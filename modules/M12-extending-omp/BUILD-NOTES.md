# Module 12 — Build notes

Built against `omp/18.3.1` on a Python-3-only Linux build machine (no Node/Bun outside omp's embedded runtime, no Chrome, no interactive TTY for the TUI). All omp facts were read from `omp://` docs or the binary this session; cited per lesson.

## Verification method

No model credentials on the build machine, so a **throwaway scripted OpenAI-compatible mock** (`/v1/chat/completions`, streaming + non-streaming, scripted tool calls) was registered in `~/.omp/profiles/m12build/agent/models.yml` and every solution was driven through the real omp binary:

- `omp --mode rpc --no-ui --no-session -e …` → `get_state.dumpTools` and `get_available_commands` prove tool/command registration.
- `omp -p --mode json --no-session …` → `tool_execution_start/update/end` events; the mock's request log shows exactly what the model received (`{"role":"tool","content":…}`).
- `omp read mcp://…`, `omp read skill://…`, `omp plugin …` from the shell.

Observed evidence (all on 18.3.1):

| Claim in lessons | Evidence |
|---|---|
| `.omp/extensions/<dir>/index.ts` + `package.json#omp.extensions` auto-discovered; `-e <dir>`; `extensions:` setting | `hello` present in `available_commands_update` in all three modes; absent with `--no-extensions` (settings path) |
| `disabledExtensions: [extension-module:hello-extension]` disables a directory entry by directory name | `hello` absent, `word_count` absent |
| Default `loadMode: "discoverable"` → tool advertised as `xd://word_count` in the system prompt, not in the tool inventory; `"essential"` → in inventory | system prompt text `- xd://word_count — Count the words in a string of text`; `dumpTools` gains `word_count` only with `essential` |
| Broken module isolated | stderr `Failed to load extension …/broken.ts: Extension does not export a valid factory function`; log entry `"level":"error","message":"Failed to load extension"`; `hello` still loads |
| `tool_call` `{block, reason}` → reason is the tool result the model reads | `tool_execution_end … "text":"force-push-guard: …" … "isError":true`; next provider request contains `{"role":"tool","content":"force-push-guard: …"}` |
| Hook only discovered under `hooks/pre|post/` | `.omp/hooks/pre/no-force-push.ts` blocks; `.omp/hooks/no-force-push.ts` does nothing, no log |
| Custom tool in `.omp/tools/` | `repo_stats` in `dumpTools`; executed: `2 tracked files match *.py` |
| `.omp/mcp.json` stdio server, resource read, `${VAR:-default}`, `enabled:false`, relative paths vs cwd | `omp read mcp://lab-fs://listing` → listing; `LAB_DATA_DIR=…` changes it; `enabled:false` → `(none)`; `args: ["lab_mcp_server.py","data"]` without `cwd` works |
| `mcp__<server>_<tool>` sanitization | `lab-fs`/`read_file` → `mcp__lab_fs_read_file`; details `serverName`, `mcpToolName`, `provider: native` |
| Print-mode MCP barrier message | `Warning: MCP server "bad" not ready after 5000ms; its tools are unavailable for this run.` |
| Marketplace add/discover/install/enable/disable/uninstall/remove; project scope layout; `skill://`; namespaced command | CLI output in `demos/12-4-marketplace.md`; `available_commands_update` shows `lab-tools:standup` (file) and `skill:lab-conventions` (skill) |
| Profile-scoped marketplace registry | `~/.omp/profiles/m12build/marketplaces.json` updated, `~/.omp/marketplaces.json` untouched |
| `before_subagent_spawn` fires once per child; `model`/`note` applied | with `async.enabled: false`, a `block:true` variant yielded `Task execution failed: scout-router TEST BLOCK`; the real router yielded task details `modelOverride:["local-fake/fake-model"]`, `resolvedModel:"local-fake/fake-model"`, `resolvedModelRoute:"scout-router: scouts run on local-fake/fake-model"` |
| Defaults | `omp config list`: `marketplace.autoUpdate = notify`, `enabledProviders = []`, `disabledExtensions = []`, `skills.enableSkillCommands = true`, `tools.xdev = true`, `mcp.enableProjectConfig = true`, `mcp.startupTimeoutMs = 250`, `mcp.notifications = false`, `mcp.renderMarkdownResults = true` |

## Deviations from the outline / docs

1. **Outline 12.1 lists `hello-extension` / `safety-hook` as "bundled examples".** The `omp://` bundle contains only their `README.md` files (`omp://skills/examples/*/README.md`), not `index.ts`/`package.json`. Lesson 12.1 says so and ships a tested reconstruction in `solutions/hello-extension/`. The walkthrough copies from `solutions/`, not from `omp://`.
2. **Outline 12.1: "`/reload-plugins`" as an extension-loading control.** Per omp://marketplace.md, `/reload-plugins` refreshes skills, slash commands and MCP servers; extension modules, tools and hooks need a restart. Taught as such. `/reload-plugins` is referenced in omp://marketplace.md and omp://slash-command-internals.md but has no dedicated doc section; its exact console output was not captured (no TUI on the build machine).
3. **Outline 12.1 event list includes `session_before_compact`, `mcp_notification`, `before_subagent_spawn`** — all present in omp://extensions.md and covered. `ctx.ui.setStatus` covered (omp://hooks.md "Status line behavior", omp://skills/authoring-extensions.md).
4. **Outline 12.3: "declare `i`" as an MCP-server authoring tip.** omp://mcp-server-tool-authoring.md §4 says `i` is stripped *unless* the tool's `inputSchema.properties` declares it. **Observed on 18.3.1: a tool that declares `i` still does not receive it** — the intent is stripped upstream and surfaces only as `tool_execution_start.intent`. The lesson states this as observed and tells authors not to depend on it; the outline's tip is dropped as unverifiable in practice.
5. **`skills.enableSkillCommands` default.** Outline Appendix C marks `/skill:` as "enableSkillCommands opt-in"; on 18.3.1 `omp config get skills.enableSkillCommands` returns `true`. Lesson 12.4 states the observed default.
6. **Filesystem MCP server (`npx @modelcontextprotocol/server-filesystem`)** could not be launched on the build machine (no Node). The config in `solutions/mcp/mcp.json` is copied from omp://mcp-config.md; the walkthrough states the Node prerequisite and provides the Python `lab-fs` server as the verified alternative. Tool names for the filesystem server (`mcp__filesystem_list_directory`) are [INFERENCE] from the documented sanitization rule plus the server's published tool name; not observed.
7. **Agent Hub column for the routing `note`** (outline Stretch: "verify in Agent Hub"). omp://extensions.md says the task UI shows the note "on live, async, and settled rows"; omp://agent-hub.md lists "model role, resolved model". Not observable without a TTY; the exercise's pass condition uses the task result's `resolvedModelRoute` / `resolvedModel` details, which were observed, and points to the Hub's model column as the interactive check.
8. **`/extensions` output layout** in `demos/12-5-extensions-audit.md` is composed from omp://context-files.md ("lists every discovered context file with its level, source, and current state"), not captured. Marked as such in the demo.
9. **`/mcp list` source column**: documented ("`/mcp list` to see which config file a server came from"); exact format not captured (no TUI).
10. **Lab fixture references.** The lab was built in parallel; this module uses only `data/lab.sqlite`, `docs/`, `README.md`, `tools/`, `notes/`, `.env.example` (`labtok_…`) and `generated/` as fixed by Appendix A. `solutions/mcp/mcp.json` expects `tools/lab_mcp_server.py` to be copied in by the learner (walkthrough step 5); the lab repo is not modified by this module.
11. **Gemini manifest interop** is covered as documented (metadata only, not executed); no `.gemini/extensions` fixture was created because the doc states it produces no runtime behavior.

## Not covered / gaps

- `registerShortcut`, `registerFlag`, `registerProvider`, `registerComposerShape`, `registerFileWriteFallback`/`DeleteFallback`, `runEphemeralTurn`: named in 12.1 concepts as existing; no exercise (out of the outline's scope).
- `/marketplace` interactive browser (TUI) and Smithery flows: not exercised.
- OAuth `/mcp reauth` against a real remote server: described from docs only (no network credentials).
- `--trusted-extension` and `--plugin-dir` flags: listed in cheat sheet source (omp://cli-reference.md) but not exercised.

## Cleanup performed on the build machine

Throwaway artifacts (`/tmp/m12ext/*`, temp project dir, mock provider, `m12build` profile's `models.yml`/`config.yml`, marketplace registrations, project-scoped plugin install) were removed or uninstalled; nothing outside `modules/M12-extending-omp/` was written in the course repo.

## Audit (wave 2, `omp/18.3.5` on PATH)

Every omp command, flag, key, setting, path, URI scheme and default in `README.md`, `exercises.md`, `cheatsheet.md`, `demos/` and `solutions/README.md` was re-checked against `omp://` (extensions.md, extension-loading.md, hooks.md, custom-tools.md, mcp-config.md, mcp-runtime-lifecycle.md, mcp-server-tool-authoring.md, approval-mode.md, marketplace.md, skills/authoring-marketplaces.md, plugin-manager-installer-plumbing.md, gemini-manifest-extensions.md, context-files.md, settings.md, skills.md, slash-command-internals.md, cli-reference.md, rpc.md, keybindings.md, tools/read.md, session-operations-export-share-fork-resume.md, skills/examples/*), `omp plugin --help`, `omp install --help`, and `omp config get`. The binary on PATH during the audit was **18.3.5**, not 18.3.1; the README header records both.

Re-executed during the audit (no model calls):

- `python3 -c 'import ast; ast.parse(open("solutions/mcp/lab_mcp_server.py").read())'` — parses; `json.load` on `solutions/my-marketplace/.omp-plugin/marketplace.json`, `solutions/mcp/mcp.json`, `solutions/hello-extension/package.json` — valid.
- `lab_mcp_server.py` piped JSON-RPC: `initialize` → `2025-11-25`; `tools/call sqlite_tables` on the lab's `data/lab.sqlite` → `orders: 72 rows / schema_version: 1 rows / users: 12 rows`; unknown method → `-32601`.
- Scratch project with `.omp/mcp.json` from `solutions/mcp/mcp.json` (lab-fs entry): `omp read mcp://lab-fs://listing` → `lab.sqlite`; `LAB_DATA_DIR=docs …` → the four `docs/` files; `omp read mcp://nope` → `No MCP server has resource "nope"` + available list.
- `omp --mode rpc --no-ui --no-session` with `solutions/hello-extension` in `.omp/extensions/` plus `broken.ts`: `available_commands_update` contains `hello`; stderr `Failed to load extension …/broken.ts: Extension does not export a valid factory function`.
- `omp plugin marketplace add/discover/install --scope project/uninstall/marketplace remove` on `solutions/my-marketplace` under a throwaway profile: same output as `demos/12-4-marketplace.md`; `omp read skill://lab-conventions` printed the skill; `installed_plugins.json` ended as `{"version": 2, "plugins": {}}`; registry landed in `~/.omp/profiles/<name>/marketplaces.json`.

### Fixed

1. 12.1 `ExtensionCommandContext`: `compact` is on every handler's `ExtensionContext` (omp://extensions.md § 2), not command-only; moved out of the command-only list.
2. 12.1 "Where omp looks" header claimed edits need no restart while the troubleshooting row said they do; reworded to the documented fact (`?mtime` cache-buster on import; modules are imported at startup).
3. 12.2 `bash.patterns` sentence: dropped the "covers `bash` but not `eval`" clause (not in omp://approval-mode.md).
4. 12.3 browser-MCP filter: listed the exact names omp://mcp-config.md gives (`playwright`, `puppeteer`, `browserbase`, `browser-tools`, `browser-use`, `browser`, package/URL references) instead of `browser*`; Exa wording now matches omp://mcp-runtime-lifecycle.md (filtered, keys extracted for the native Exa integration).
5. 12.3 shape: noted that `disabledServers`/`enabledServers` are read from the active profile's **user** file (omp://mcp-config.md "User-level enable and disable overrides"); cheatsheet "file-level" → "user-file".
6. 12.5 foreign-source table: `.claude/` now lists `.claude/commands/**/*.md` (+ `foo:bar` alias) and `.codex/commands/*.md` (user beats project) per omp://slash-command-internals.md; skills are attributed to the provider rather than to an undocumented path.
7. 12.1 log path marked "observed on disk, not documented".
8. Lab fixture: `solutions/my-marketplace/.../SKILL.md` and `demos/12-4-marketplace.md` said `python -m unittest …`; the lab README's command is `python3 -m unittest discover -s tests`.
9. Demo 12.3 now says its `data/`/`docs/` listings come from a scratch directory, not the lab's.

### Removed (unverifiable)

- 12.5 table: `.claude/skills`, `.claude/hooks/pre|post`, `.codex/skills` as concrete discovery paths. omp://skills.md lists the `claude`/`codex` providers as skill sources but names no directory; omp://hooks.md only says the native `pre|post` layout "mirrors" `.claude/hooks/`, and omp://extension-loading.md says hook factories are discovered from native roots only.
- 12.2: "`bash.patterns` … covers commands the model runs through `bash` but not through `eval`".
- 12.3: "Exa servers are folded into the native `web_search` integration" (doc says keys are extracted for the native Exa integration; no `web_search` claim).

### Version note

`omp --version` on the audit machine is `18.3.5`; all facts above were re-read on that build. Behaviours observed by the builder on 18.3.1 that were re-run here matched.
