# Module 12 — Extending omp: Extensions, Hooks, MCP, Plugins

| | |
|---|---|
| **Level** | advanced |
| **Time** | ~2.5 h |
| **Prerequisites** | Module 6 (context files, skills, settings layering) |
| **Built against** | `omp/18.3.1` (`omp --version`); audit re-run on `omp/18.3.5` (see `BUILD-NOTES.md` § Audit) |
| **Lab checkpoint** | `git checkout module-12-start` in `omp-course-lab` |
| **Learner prerequisites** | Everything in 12.1–12.2 and 12.4–12.5 runs with omp alone (omp embeds its own TypeScript runtime). 12.3's `filesystem` server needs Node.js/`npx`; a Python-only alternative is provided. |

**Goal:** Add tools, commands, event handlers, and external servers to omp; package and share them; audit what omp silently inherits from other tools' config.

Every file referenced as `solutions/...` is in this module directory and was executed against omp 18.3.1 while building this module (see `BUILD-NOTES.md` for the evidence and the harness used).

---

## Lesson 12.1 — Extension anatomy              (~45 min)
**You will be able to:** write a one-file extension that adds a slash command, an LLM-callable tool, and an event handler; load it three different ways; find out why it did not load.
**Why this exists:** Everything you taught omp in Module 6 was *text* — context, rules, skills, prompt templates. An extension is *code* that runs inside omp's process.
It can register tools the model calls, slash commands you type, and handlers that fire on session and tool lifecycle events (including vetoing a tool call before it runs).
One TypeScript file, one default export, no build step — omp imports it with its embedded Bun runtime.
Hooks (12.2) and custom tools (12.2) are older, narrower surfaces; extensions are the superset and the recommended target for new work.
**Demo:** `demos/12-1-hello-extension.md` — `/hello Ada`, then a `word_count` card.

**Concepts:**
- **Shape.** A module whose default export is a factory: `export default function (pi: ExtensionAPI) { ... }`. The factory may return a promise.
  - During the factory ("load phase") only *registration* is legal — `pi.on`, `pi.registerTool`, `pi.registerCommand`, `pi.registerShortcut`, `pi.registerFlag`, `pi.setLabel`, renderers.
  - Calling a runtime action such as `pi.sendMessage()` or `ctx.ui.*` at load throws `ExtensionRuntimeNotInitializedError`. Do runtime work from handlers, commands, and tools.
- **Where omp looks (modules are imported at startup; the import carries an `?mtime` cache-buster so an edited file is re-imported on the next start rather than served stale — see Troubleshooting):**
  1. `<cwd>/.omp/extensions/` — project. **cwd only, no ancestor walk.** Direct `*.ts`/`*.js`, plus one-level subdirectories with `index.ts`/`index.js` or a `package.json` whose `omp.extensions` array names the entry files.
  2. `~/.omp/agent/extensions/` — user (with `omp --profile <name>`: `~/.omp/profiles/<name>/agent/extensions/`).
  3. Installed plugins' `package.json#omp.extensions` (12.4).
  4. Explicit paths: `omp -e ./ext.ts` / `--extension` (repeatable; `--hook` is an alias) and the `extensions:` array in `~/.omp/agent/config.yml` or `.omp/config.yml`.
  De-duplicated by absolute path, first seen wins. `--no-extensions` drops 1–3 and the `extensions:` setting; explicit `-e` still loads.
- **Turning one off without deleting it:** `disabledExtensions: [extension-module:<name>]` where `<name>` is the file stem (`guard.ts` → `guard`) or the directory name for `index.ts` entries.
- **`pi.registerCommand(name, { description, handler(args, ctx) })`.** `args` is everything after `/name`. Names that clash with built-ins are skipped with a log line.
  - `ctx` is an `ExtensionCommandContext`: everything a handler gets (`ctx.ui.notify/confirm/select/input/editor`, `ctx.cwd`, `ctx.hasUI`, `ctx.compact(...)`).
  - Plus session controls that only commands get: `waitForIdle`, `newSession`, `switchSession`, `branch`, `navigateTree`, `reload`.
- **`pi.registerTool({...})`.** Required: `name` (snake_case, globally unique), `label`, `description`, `parameters` (a schema built with `pi.zod`, `pi.arktype`, or the legacy `pi.typebox` shim), `execute(toolCallId, params, signal, onUpdate, ctx)` returning `{ content: [{type:"text", text}], details? }`. Optional and worth knowing:
  - `approval: "read" | "write" | "exec"` — default `"exec"`, the tier that prompts in `always-ask` and `write` modes (M4). Declare `"read"` for pure functions.
  - `loadMode: "discoverable" | "essential"` — **default `"discoverable"`**: the tool is *not* in the top-level tool list; it is advertised as an `xd://<name>` device the model dispatches by writing JSON to that URI (M8). `"essential"` puts it in the tool inventory so you get a plain `word_count` card. The solution uses `"essential"`.
  - `hidden`, `defaultInactive`, `deferrable`, `strict`, `renderCall`, `renderResult`, `onSession`.
  - `signal` is the abort signal; `onUpdate({content})` streams partial output into the card.
- **Events — `pi.on(name, async (event, ctx) => result)`.** The ones this course uses:
  | Event | Fires | Handler may return |
  |---|---|---|
  | `session_start` | session is live | — |
  | `turn_start` / `turn_end` | each user→agent turn | — |
  | `context` | before every provider request | `{ messages }` (rewrite what the model sees) |
  | `tool_call` | before any tool runs, incl. built-ins and MCP | `{ block, reason }`, `{ input }` (replace args), `{ additionalContext }` |
  | `tool_result` | after any tool | `{ content, details, isError }` |
  | `before_subagent_spawn` | parent session, once per child | `{ model, note }` or `{ block, reason }` |
  | `session_before_compact` | before compaction | `{ cancel }` or `{ compaction }` |
  | `mcp_notification` | any JSON-RPC notification from an MCP server | — |
  Full catalog: `omp://extensions.md` § "Event surface". Handler errors in most events are caught and reported; a `tool_call` handler that **throws blocks the tool** (fail-closed).
- **Status and messages.** `ctx.ui.setStatus(key, text)` writes a keyed segment into the status line (sorted by key, sanitized). `ctx.ui.notify(text, "info" | ...)`. `pi.sendMessage({ customType, content, display, attribution }, { triggerTurn, deliverAs })` records a custom message; `deliverAs` is `"steer"` (default, interrupts), `"followUp"`, `"nextTurn"`, or `"aside"`.
- **Not a sandbox.** Extensions run in-process with no isolation. A raw `setInterval`/`setTimeout` callback that throws kills the *session*; use `ctx.setInterval` / `ctx.setTimeout` (contained, auto-cleared on `session_shutdown`).
- **Failure isolation at load.** One broken module does not stop the others: omp prints `Failed to load extension <path>: <error>` on stderr and logs it. Logs (observed on disk, not documented): `~/.omp/logs/omp.<date>.<pid>.log` (profiles: `~/.omp/profiles/<name>/logs/`).
- **Reserved shortcuts** `registerShortcut` cannot take: `ctrl+c/d/z/k/p/l/o/t/g/q`, `alt+m`, `shift+tab`, `shift+ctrl+p`, `alt+enter`, `escape`, `enter`.
- **Bundled examples.** `read omp://skills/examples/hello-extension/README.md` and `.../safety-hook/README.md` describe the two canonical starters (`/hello` command; `rm -rf /` blocker). The docs bundle carries their READMEs, not their source — `solutions/hello-extension/` is a faithful, tested reconstruction.

**Try it (Walkthrough):**
1. `cd omp-course-lab && git checkout module-12-start`. Copy the solution: `mkdir -p .omp/extensions && cp -r <module-dir>/solutions/hello-extension .omp/extensions/hello-extension`. Open `index.ts` and read the three registrations (command, tool, `session_start`).
   **Expected:** `.omp/extensions/hello-extension/{index.ts,package.json}` exist; `package.json` has `"omp": { "extensions": ["./index.ts"] }`.
2. Start `omp`.
   **Expected:** an info notification `hello-extension loaded in <cwd>` at startup.
3. Type `/hello Ada`.
   **Expected:** a displayed custom message `Hello, Ada!` in the transcript, notification `Greeted Ada`, and **no** model turn (the command passes `triggerTurn: false`).
4. Prompt: `Count the words in README.md using the word_count tool and tell me the number.`
   **Expected:** a `read` card, then a `word_count` card whose expanded view (`Ctrl+O`) shows `Counting...` replaced by the count, and `details: { count: N }`.
5. Break it on purpose: `echo 'export default 42;' > .omp/extensions/broken.ts`, restart `omp`.
   **Expected:** stderr line `Failed to load extension .../broken.ts: Extension does not export a valid factory function`; `/hello` still works. Delete `broken.ts`.
6. Disable without deleting: add to `.omp/config.yml`:
   ```yaml
   disabledExtensions:
     - extension-module:hello-extension
   ```
   Restart. **Expected:** `/hello` is unknown; `word_count` gone. Remove the setting.
7. Load once from the CLI instead: move the directory out of `.omp/extensions/` and run `omp -e ./path/to/hello-extension`.
   **Expected:** identical behavior for this session only.

**Guided task:** Add a status-line token counter.
- Goal: after every turn the status line shows `ctx≈<tokens>`.
- Hints: `pi.on("turn_end", ...)`, `ctx.getContextUsage()?.tokens`, `ctx.ui.setStatus("ctx", ...)`. Guard with `ctx.hasUI`.
- Checkpoints: (a) the handler registers without touching `ctx.ui` at load; (b) the segment appears after the first turn; (c) it survives `/clear`.
- Pass: status line shows a `ctx≈` segment that changes between turns.

**Stretch:** Persist state across restarts. Goal: the extension counts `/hello` invocations and reports the total on `session_start`, surviving `/resume`. Pass: the count entries are visible in the session `.jsonl`, and after `/resume` the `session_start` notification reports the total from before the restart.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| Extension in `.omp/extensions/` never loads when omp is started in a subdirectory | project root is cwd-only, no ancestor walk | start omp at the repo root, or use `extensions:` in `~/.omp/agent/config.yml` with an absolute path |
| `ExtensionRuntimeNotInitializedError` at startup | runtime action (`pi.sendMessage`, `ctx.ui.*`) called inside the factory | move it into a handler/command/tool |
| Tool exists but the model writes to `xd://word_count` instead of calling it | default `loadMode: "discoverable"` | set `loadMode: "essential"` (or accept the `xd://` dispatch — both execute your code) |
| `/hello` silently missing, log says command conflicts with a built-in | name clash | rename the command |
| Edited `index.ts`, no change | file loaded at startup | restart omp (edits are picked up on the next start via the `?mtime` cache-buster); `/reload-plugins` refreshes skills/commands/MCP, not extension modules |
| Session dies with `uncaughtException` after adding a timer | raw `setInterval` callback threw | use `ctx.setInterval` / `ctx.setTimeout` |
| Tool prompts for approval in `write` mode | default `approval: "exec"` | declare `approval: "read"` for pure functions |

**Cheat sheet:**
| Item | Value |
|---|---|
| Project / user dirs | `<cwd>/.omp/extensions/` · `~/.omp/agent/extensions/` |
| Entry resolution | `package.json#omp.extensions` → `index.ts` → `index.js` → one-level scan |
| One-off load | `omp -e ./ext.ts` (repeatable), `--no-extensions` |
| Setting | `extensions: [path,...]`, `disabledExtensions: [extension-module:<name>]` |
| Factory | `export default function (pi: ExtensionAPI) {}` |
| Register | `pi.registerCommand`, `pi.registerTool`, `pi.on`, `pi.setLabel` |
| Tool execute | `(toolCallId, params, signal, onUpdate, ctx) → { content, details }` |
| Tool options | `approval` (exec) · `loadMode` (discoverable) · `hidden` · `renderResult` |
| Logs | `~/.omp/logs/omp.<date>.<pid>.log` |

**Source:** omp://extensions.md, omp://extension-loading.md, omp://skills/authoring-extensions.md, omp://skills/examples/hello-extension/README.md, omp://skills/examples/safety-hook/README.md, omp://cli-reference.md, omp://approval-mode.md

---

## Lesson 12.2 — Hooks (legacy) and standalone custom tools              (~30 min)
**You will be able to:** block a dangerous tool call and make the model see why; choose between an extension, a hook module, and a custom-tool module; place each where omp actually discovers it.
**Why this exists:** Before the unified extension API, omp had two narrower plug-in shapes that still work and that you will meet in other people's repos.
**Hooks** (`HookAPI`) do event interception only and are discovered under `hooks/pre|post/`, mirroring Claude Code's layout; **custom tools** (`CustomToolFactory`) provide one model-callable tool per module and are discovered under `tools/`.
Both are loaded through the same runner as extensions, so the `tool_call` / `tool_result` contracts are identical.
Knowing them lets you drop a policy file into a repo that already uses `.claude/hooks/` and lets you ship a tool without writing a command or UI.
**Demo:** `demos/12-2-tool-call-guard.md` — the model tries `git push --force`, the card goes red with your reason, the model changes course.

**Concepts:**
- **The `tool_call` contract (same in `ExtensionAPI` and `HookAPI`).** `event.toolName`, `event.input` (for `bash`: `event.input.command`), `event.toolCallId`. Return:
  - `{ block: true, reason }` — the tool never runs; **`reason` becomes the tool's error text and is exactly what the model reads next** (verified: the next provider request contains `{"role":"tool","content":"<your reason>"}`).
  - `{ input: {...} }` — replace the raw arguments (last handler wins; handlers do not see each other's revisions).
  - `{ additionalContext }` — trusted instructions delivered after the batch's tool results, only if the call ran and succeeded.
  - throw — also blocks (fail-closed). Return nothing to allow.
  - First `block` short-circuits. Eval-prelude calls (`browser.open`, `tab.run`, `computer.*` — the browser and desktop bridges of Module 14) are host bridge calls and do **not** fire `tool_call`.
- **`tool_result`** runs after execution: `{ content, details, isError }` patch what the model sees (redaction, truncation). Handlers run in order and each sees prior edits.
- **Interactive vs headless.** `ctx.hasUI` is `false` in `-p` and RPC `--no-ui` (omp's print and machine-driven modes, Module 13) and in subagents; `ctx.ui.confirm` returns `false` there. Pattern: confirm when there is a UI, hard-block when there is not.
- **Hook module.** `import type { HookAPI } from "@oh-my-pi/pi-coding-agent/extensibility/hooks"` — not re-exported from the package root. Default export `(pi: HookAPI) => void`.
  - Discovery is **only** `<cwd>/.omp/hooks/pre/*.{ts,js}` and `<cwd>/.omp/hooks/post/*.{ts,js}` (user: `~/.omp/agent/hooks/pre|post/`). A file placed directly in `.omp/hooks/` loads nothing and reports nothing (verified).
  - The `pre`/`post` split is layout inherited from `.claude/hooks/`; what a module does is decided by the events it subscribes to.
- **Custom tool module.** `import type { CustomToolFactory } from "@oh-my-pi/pi-coding-agent"`. The factory returns one tool, an array, or a promise of either.
  - It receives `CustomToolAPI`: `pi.cwd`, `pi.exec(cmd, args, {signal, cwd})`, `pi.zod`, `pi.arktype`, `pi.typebox`, `pi.ui`, `pi.hasUI`, `pi.logger`.
  - **Argument order differs from extension tools:** `execute(toolCallId, params, onUpdate, ctx, signal)`.
  - Discovery: `~/.omp/agent/tools/`, `<cwd>/.omp/tools/` (also `~/.claude/tools`, `.claude/tools`, `~/.codex/tools`, `.codex/tools`); `.ts`/`.js` plus one-level `index.ts`; `.md`/`.json` there are metadata, not tools.
  - Name conflicts with built-ins or other custom tools are rejected. Same `loadMode` default (`discoverable`) unless the name is an essential built-in.
- **Approval interaction.** A block from `tool_call` happens *before* the approval gate; a `bash.patterns` `deny` rule (M4) is a second, independent layer inside the `bash` tool's own approval decision.
- **Decision table.**
  | You need | Use |
  |---|---|
  | tools + commands + events + rendering in one module | extension |
  | pure policy/redaction, especially in a repo that already has `.claude/hooks/` | hook (or extension — preferred) |
  | one model-callable function, no UI/commands | custom tool |
  | register a provider, shortcut, CLI flag, composer shape | extension only |
  | ship via marketplace/npm | extension + `package.json#omp.extensions` |

**Try it (Walkthrough):**
1. Copy `solutions/force-push-guard` to `.omp/extensions/force-push-guard`. Read the regex: `--force` and `-f` are blocked, `--force-with-lease` is allowed.
   **Expected:** file in place; restart `omp`.
2. Prompt: `Run exactly this command with bash and report its output: git push --force origin main`.
   **Expected:** a red `bash` card with `force-push-guard: \`git push --force\` is blocked in this repository. ...`; the model's next message references the block. If you are interactive, you first get a **Force push blocked** confirm dialog — choose No.
3. Prompt: `Now run: git push --force-with-lease origin main`.
   **Expected:** the command runs (and fails on the lab's missing remote — the point is that it was *not* blocked).
4. Headless check: `omp -p --no-session "Run with bash: git push -f origin main"`.
   **Expected:** no dialog; blocked outright (the `ctx.hasUI` branch).
5. Move the same policy to a hook: `mkdir -p .omp/hooks/pre && cp solutions/hooks/pre/no-force-push.ts .omp/hooks/pre/`, remove the extension, restart, repeat step 2.
   **Expected:** blocked with `git push --force blocked (no UI to confirm)` in `-p`, or the confirm dialog interactively.
6. Prove the layout rule: `mv .omp/hooks/pre/no-force-push.ts .omp/hooks/`, restart, repeat step 2.
   **Expected:** the push is **not** blocked and nothing is logged — hooks outside `pre/`/`post/` are ignored. Move it back or delete it.
7. Custom tool: `mkdir -p .omp/tools && cp solutions/tools/repo_stats.ts .omp/tools/`, restart, prompt `How many tracked Python files are there? Use repo_stats.`
   **Expected:** a `repo_stats` card: `N tracked files match **/*.py` with `details.sample`.

**Guided task:** Redact the lab token.
- Goal: any `read` of `.env.example` shows `labtok_[REDACTED]` to the model while the file on disk is untouched.
- Hints: `pi.on("tool_result", ...)`, filter `event.toolName === "read" && !event.isError`, map `event.content` text chunks with a regex for `labtok_[A-Za-z0-9]+`, return `{ content }`. Compare with Module 6's `secrets.enabled`, which does the same thing declaratively *and* restores the value for tool execution.
- Checkpoints: (a) the `read` card's expanded output shows the placeholder; (b) `bash cat .env.example` still shows the real token (you only patched `read`).
- Pass: transcript shows `labtok_[REDACTED]` in the `read` card.

**Stretch:** Rewrite arguments instead of blocking. Goal: a `tool_call` handler that turns `git push --force` into `git push --force-with-lease` by returning `{ input: { ...event.input, command: rewritten } }`. Pass: the `bash` card shows the rewritten command.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| Hook file ignored, no error | not under `hooks/pre/` or `hooks/post/` | move it |
| `Cannot find module '@oh-my-pi/pi-coding-agent'` for `HookAPI` | wrong import path | `@oh-my-pi/pi-coding-agent/extensibility/hooks` |
| Custom tool's `signal` is `undefined` / `onUpdate` is not a function | used the extension argument order | custom tools: `(toolCallId, params, onUpdate, ctx, signal)` |
| Guard blocks nothing in a subagent | headless children have `hasUI=false` and your handler returned after a failed `confirm` | check `!ctx.hasUI` first and block |
| Block fires but the model keeps retrying variants | `reason` too terse | say what *is* allowed in the reason |
| Custom tool named like a built-in | conflict rejected | rename |

**Cheat sheet:**
| Item | Value |
|---|---|
| Hook dirs | `.omp/hooks/pre/`, `.omp/hooks/post/`, `~/.omp/agent/hooks/pre|post/` |
| Hook import | `@oh-my-pi/pi-coding-agent/extensibility/hooks` → `HookAPI` |
| Custom tool dirs | `.omp/tools/`, `~/.omp/agent/tools/` (+ `.claude/tools`, `.codex/tools`) |
| Custom tool execute | `(toolCallId, params, onUpdate, ctx, signal)` |
| Block | `return { block: true, reason }` |
| Rewrite args | `return { input }` |
| Patch output | `tool_result` → `return { content, details }` |

**Source:** omp://hooks.md, omp://skills/authoring-hooks.md, omp://custom-tools.md, omp://extensions.md, omp://approval-mode.md

---

## Lesson 12.3 — MCP servers              (~40 min)
**You will be able to:** connect a stdio MCP server from `.omp/mcp.json`, test and reload it without restarting, call its tools as `mcp__<server>_<tool>`, read its resources as `mcp://<uri>`, keep secrets out of the file, and write a server that behaves well under omp.
**Why this exists:** The Model Context Protocol is the interoperable way to hand an agent an external capability — a database, an issue tracker, a vendor API — as a process (stdio) or an endpoint (HTTP).
omp discovers server definitions from its own files *and* from Claude Code, Codex, Gemini CLI, Cursor, Windsurf, VS Code and OpenCode configs, connects in the background so startup stays fast, and exposes each server tool under a namespaced name.
You write JSON, not code.
**Demo:** `demos/12-3-mcp-filesystem.md` — `/mcp test filesystem`, a `mcp__filesystem_list_directory` card, `read mcp://lab-fs://listing`.

**Concepts:**
- **Files (first definition wins, no merging).** Project `.omp/mcp.json` → `.omp/.mcp.json` → user `~/.omp/agent/mcp.json` (profile: `~/.omp/profiles/<name>/agent/mcp.json`) → `.mcp.json` variants → other tools' configs → root `mcp.json` / `.mcp.json` fallbacks. Project config is keyed to the directory and applies under every profile; user config is per profile.
- **Shape.**
  ```json
  {
    "$schema": "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/config/mcp-schema.json",
    "mcpServers": {
      "filesystem": { "type": "stdio", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/abs/path/data"] },
      "github":     { "type": "http",  "url": "https://api.githubcopilot.com/mcp/" }
    },
    "disabledServers": [], "enabledServers": []
  }
  ```
  Field rules:
  | Field | Rule |
  |---|---|
  | `type` | omitted means `stdio`; `stdio` needs `command` (+ `args`, `env`, `cwd`); `http`/`sse` need `url` (+ `headers`); both `command` and `url` is rejected |
  | shared | `enabled`, `timeout` (ms; `0` disables), `instructions` (include the server's system-prompt instructions, default `true`), `requestIdFormat`, `auth`, `oauth` |
  | `disabledServers` / `enabledServers` | honored from the **active profile's user file** (`~/.omp/agent/mcp.json`), not from a project file |
  | relative `args` | resolve against omp's cwd (verified) |
- **Secrets.** Discovery-time `${VAR}` / `${VAR:-default}` expansion in `command`, `args`, `env`, `cwd`, `url`, `headers` (verified).
  - Pre-connect, each `env`/`headers` value is resolved: `!cmd` runs a shell command (10 s timeout, cached, omitted if empty); otherwise, if the whole value names a set environment variable, that value is used; else the literal.
  - So `"GITHUB_PERSONAL_ACCESS_TOKEN": "GITHUB_PERSONAL_ACCESS_TOKEN"` copies from your shell.
- **`/mcp` commands** (interactive): `add` (wizard or quick-add), `remove`/`rm`, `enable`/`disable`, `test <name>`, `reconnect <name>`, `reload` (rediscover all files, rebind tools live — no restart), `reauth`/`unauth <name>`, `resources`, `prompts`, `notifications`, `list` (shows which file each server came from). Writes are atomic and add `$schema` for you.
- **Tool names.** `mcp__<server>_<tool>`, lowercased, non-`[a-z0-9_]` → `_`, runs collapsed, a redundant `<server>_` prefix stripped, >64 chars hashed. `lab-fs` + `read_file` → `mcp__lab_fs_read_file` (verified). MCP tools declare the `write` approval tier, so they prompt in `write`/`always-ask` modes.
- **Resources.** `read mcp://<resource-uri>` reads a server-advertised resource (`mcp://lab-fs://listing`); `/mcp resources` lists them; `omp read mcp://<uri>` works from the shell and prints the available URIs on a miss (verified).
- **Startup timing.** Discovery returns after a 250 ms window (`mcp.startupTimeoutMs`, env `OMP_MCP_STARTUP_TIMEOUT_MS`); slow servers keep connecting in the background and their tools appear late (cached definitions become *deferred* tools immediately).
  - Request timeout: `OMP_MCP_TIMEOUT_MS` > per-server `timeout` > 30 s.
  - **Print mode** (`-p`, Module 13) additionally waits for every configured server before the first turn; on timeout it warns `MCP server "<name>" not ready after <ms>; its tools are unavailable for this run` (verified) — set `OMP_MCP_REQUIRE_READY=1` to exit 1 instead.
- **Reconnect.** Dropped transports reconnect with backoff 0.5/1/2/4 s; more than 5 attempts in 30 s trips a breaker until you `/mcp reconnect`. Tool calls retry once after a reconnect.
- **OAuth, per profile.** For `http`/`sse` servers, completing `/mcp reauth <name>` stores the credential under `mcp_oauth:profile:<profile>:<url>`; a committed, definition-only entry in a shared `.omp/mcp.json` resolves each profile's own credential automatically.
  Committed `stdio` entries run arbitrary commands — review a repo's `mcp.json` before opening it with a profile that holds credentials.
- **Silent drops.** Browser MCP servers are dropped at config load when `browser.enabled` is true (default; omp's native browser integration, Module 14) — they never reach `/mcp list`, no warning.
  - Matched by name (`playwright`, `puppeteer`, `browserbase`, `browser-tools`, `browser-use` or `browser`), by a command/args reference to a browser MCP package (e.g. `@playwright/mcp`), or by a URL pointing at browserbase.com / browser-use.com.
  - `omp read` does not apply this filter. Exa servers are filtered out too; their API keys are handed to omp's native Exa integration.
- **Settings.** `mcp.enableProjectConfig` (default `true`), `mcp.startupTimeoutMs` (`250`), `mcp.notifications` (`false`), `mcp.renderMarkdownResults` (`true`).
- **Authoring a server that plays well** (`solutions/mcp/lab_mcp_server.py`, stdlib Python, ~200 lines): newline-delimited JSON-RPC on stdio.
  - Answer `initialize` (omp speaks protocol `2025-11-25` and advertises `roots`), ignore `notifications/initialized`, answer `ping`, `tools/list`, `tools/call`, optionally `resources/list`/`resources/read`; reply `-32601` to unknown methods.
  - Report tool failures in-band with `isError: true`. Keep server and tool names unique *after sanitization* (`my-server` and `my.server` collide).
  - Optional properties sent as `""`/`{}` are dropped before your server sees them — validate the normalized payload.
  - The harness intent field `i` is **not** delivered (omp strips it and shows it as the card's intent line) — do not depend on it.

**Try it (Walkthrough):**
Prerequisite for steps 1–4: Node.js with `npx` on your machine. If you do not have it, start at step 5 (Python only).
1. Create `.omp/mcp.json` from `solutions/mcp/mcp.json`; replace `/ABSOLUTE/PATH/TO/omp-course-lab/data` with the real absolute path to the lab's `data/` directory (`pwd`). Delete the `lab-fs` entry for now.
   **Expected:** file validates in your editor against `$schema`.
2. Start `omp`, run `/mcp list`.
   **Expected:** `filesystem` listed as connected (or connecting for the first second while `npx` downloads), with source `.omp/mcp.json`.
3. `/mcp test filesystem`.
   **Expected:** success with the tool count.
4. Prompt: `Use the filesystem MCP server to list the files in data/ and tell me their sizes.`
   **Expected:** one or more `mcp__filesystem_*` cards (e.g. `mcp__filesystem_list_directory`) followed by the answer. Under `tools.approvalMode: write` you get an approval prompt first — MCP tools are `write` tier.
5. Python route: `cp solutions/mcp/lab_mcp_server.py tools/` and add the `lab-fs` entry from `solutions/mcp/mcp.json` (relative paths are fine — they resolve against the lab root). `/mcp reload` if omp is running.
   **Expected:** `/mcp list` shows both servers; `/mcp test lab-fs` succeeds with 3 tools.
6. Prompt: `Call mcp__lab_fs_sqlite_tables on lab.sqlite and summarize.`
   **Expected:** a `mcp__lab_fs_sqlite_tables` card with `orders: N rows`, `users: M rows`; expanded `details` show `serverName: lab-fs`, `mcpToolName: sqlite_tables`.
7. `read mcp://lab-fs://listing` (prompt the model, or from a shell: `omp read mcp://lab-fs://listing`).
   **Expected:** a recursive listing of `data/`. Try `omp read mcp://nope` and note the error lists available resource URIs.
8. Prove `${VAR:-default}`: `LAB_DATA_DIR=docs omp read mcp://lab-fs://listing`.
   **Expected:** the listing is now of `docs/`.

**Guided task:** Secrets and precedence.
- Goal: add the GitHub hosted MCP server with a bearer header that never appears in the file, then shadow it from the project.
- Hints: user file `~/.omp/agent/mcp.json`, `"headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }` or `"!gh auth token"`; then a project `.omp/mcp.json` entry with the same name and `"enabled": false`; `/mcp list` shows which file won. Then add the name to user-level `disabledServers` and see that it wins over everything.
- Checkpoints: `/mcp test github` passes with the env var set and fails with 401 without it; project `enabled: false` hides it; `disabledServers` hides it even if `enabledServers` lists it.
- Pass: `/mcp list` output pasted into `notes/m12.md` for each of the three states.

**Stretch:** Server-push. Goal: extend `lab_mcp_server.py` to emit a `notifications/lab/changed` notification after each `tools/call`, and write an extension with `pi.on("mcp_notification", ...)` that `ctx.ui.notify`s `event.server`/`event.method`. Pass: a notification appears after an MCP tool card; `/mcp notifications` lists the frame.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `stdio server requires "command" field` | remote server without `"type": "http"` | add `type` |
| `both "command" and "url" are set` | mixed transports | keep one |
| Server present in `.cursor/mcp.json` but absent from `/mcp list` | project-level sources off, or user `disabledServers`, or same-name shadowing by a higher-priority file | `mcp.enableProjectConfig`, check `disabledServers`, rename |
| `npx` server "connecting" for a long time | first-run package download | wait; `/mcp reconnect filesystem` |
| Tools missing in `-p` runs | print-mode barrier timed out | raise `OMP_MCP_TIMEOUT_MS`, or `OMP_MCP_REQUIRE_READY=1` to fail loudly |
| Header/env entry silently missing → 401 | `!cmd` printed nothing or timed out | run the command by hand; check it prints on stdout |
| Playwright MCP never appears | browser-MCP filter | `browser.enabled: false` (you lose the native browser prelude) |
| Two servers, one set of tools | different names but identical transport/endpoint → deduped | keep one |

**Cheat sheet:**
| Item | Value |
|---|---|
| Files | `.omp/mcp.json` (project) · `~/.omp/agent/mcp.json` (user/profile) · root `mcp.json`/`.mcp.json` |
| Transports | `stdio` (`command`,`args`,`env`,`cwd`) · `http` (`url`,`headers`) · `sse` |
| Secrets | `${VAR}` `${VAR:-x}` · env-var-name values · `!command` |
| Commands | `/mcp add|remove|enable|disable|test|reconnect|reload|reauth|unauth|resources|prompts|notifications|list` |
| Tool name | `mcp__<server>_<tool>` (sanitized) · approval tier `write` |
| Resource | `read mcp://<resource-uri>` |
| Timing | `mcp.startupTimeoutMs`=250 · `OMP_MCP_TIMEOUT_MS` · `OMP_MCP_REQUIRE_READY=1` |
| Overrides | user `disabledServers` (wins) · `enabledServers` · `mcp.enableProjectConfig` |

**Source:** omp://mcp-config.md, omp://mcp-runtime-lifecycle.md, omp://mcp-server-tool-authoring.md, omp://mcp-protocol-transports.md, omp://tools/read.md, omp://approval-mode.md

---

## Lesson 12.4 — Marketplaces & plugins              (~30 min)
**You will be able to:** package a skill, a command, and (optionally) an extension as a plugin; publish it through a two-file local marketplace; install, disable, upgrade and remove it at user or project scope; understand the Gemini manifest interop.
**Why this exists:** A team should not copy `.omp/` directories between repos by hand. A **marketplace** is a directory or Git repo with one catalog file.
A **plugin** is a directory laid out by convention (`skills/`, `commands/`, `agents/`, `hooks/pre|post/`, `tools/`, `.mcp.json`, `package.json#omp.extensions`).
omp's format is the Claude Code plugin registry format, so one repository can serve both tools.
Installing symlinks the cached plugin into a `node_modules` tree that omp's discovery already scans, so everything from 12.1–12.3 works unchanged inside a plugin.
**Demo:** `demos/12-4-marketplace.md` — `omp plugin marketplace add`, install at project scope, `/lab-tools:standup`, `read skill://lab-conventions`.

**Concepts:**
- **Catalog.** `.omp-plugin/marketplace.json` (preferred) or `.claude-plugin/marketplace.json` (fallback, Claude-compatible); ship both to serve both tools. Required: `name`, `owner.name`, `plugins[]`.
  - Each plugin: `name`, `source`, optional `description`, `version`, `category`, `tags`, `homepage`, `lspServers`, `dapAdapters` (the last two are materialized into `.lsp.json`/`.dap.json` at install — language-server and debugger configs, Module 8).
  - Optional `metadata.pluginRoot` is prepended to relative sources.
- **Sources.** Relative `"./plugins/x"` (must start with `./`, no traversal), `{ "source": "github", "repo", "ref", "sha" }`, `{ "source": "url", "url", "sha" }`, `{ "source": "git-subdir", "url", "path" }`. `npm` sources parse but installation rejects them today.
- **Naming.** Marketplace and plugin names: lowercase letters, digits, `-`, `.`; start/end alphanumeric; ≤ 64 chars; `name@marketplace` ≤ 128.
- **Two-file minimum.** `marketplace.json` + one `skills/<name>/SKILL.md`. Add `commands/<name>.md` and you have `solutions/my-marketplace/`. **Plugin commands are namespaced**: `commands/standup.md` in plugin `lab-tools` becomes `/lab-tools:standup` (verified).
- **Commands.**
  | Interactive | CLI |
  |---|---|
  | `/marketplace add <source>` · `remove <name>` · `update [name]` · `list` | `omp plugin marketplace add|remove|update|list` |
  | `/marketplace discover [mkt]` · `install [--force] [--scope user\|project] name@mkt` · `uninstall` · `installed` · `upgrade` | `omp plugin discover|install|uninstall|upgrade|list` |
  | `/plugins list` · `enable` · `disable` (`--scope`) | `omp plugin enable|disable` |
  | `/marketplace` alone: interactive browser | `omp install <spec>` = `plugin install`/`plugin link` |
  Sources: `owner/repo`, `https://…json` (catalog only; relative sources not allowed), `https://…`/`git@…` repos, `./path`, `~/path`, `/path`.
- **Scopes and disk.**
  | Scope | Install record | Plugin files |
  |---|---|---|
  | `--scope user` (default) | `~/.omp/plugins/installed_plugins.json` | `~/.omp/plugins/node_modules/<pkg>` → cache |
  | `--scope project` | `<project>/.omp/plugins/installed_plugins.json` + `omp-plugins.lock.json` (verified) | `<project>/.omp/plugins/node_modules/<pkg>` (verified) |
  Marketplace registry: `~/.omp/marketplaces.json` (with a profile: `~/.omp/profiles/<name>/marketplaces.json` — verified). An enabled project install shadows a user install of the same id.
- **After a change.** Marketplace mutations update disk but not the live session: `/reload-plugins` refreshes skills, slash commands and MCP servers; **restart** for tools, hooks, or extension modules. `marketplace.autoUpdate`: `off` | `notify` (default; writes to the debug log only) | `auto`.
- **Upgrade semantics.** `update` refreshes catalogs only; `upgrade` reinstalls; all-plugin upgrade compares only entries that declare `version` (semver must be newer). `remove` of a marketplace does not uninstall its plugins.
- **npm/link plugins** (`omp plugin install <pkg>[features]`, `omp plugin link ./dir`, `omp plugin doctor --fix`, `features`, `config --set k=v`): same runtime surfaces (`~/.omp/plugins/package.json`, `node_modules`, `omp-plugins.lock.json`).
  Manifest is `package.json#omp` (legacy `pi`); declared `extensions` are validated at install and the install rolls back if one fails to import. Project overrides: `.omp/plugin-overrides.json`.
- **Extensions inside plugins.** `package.json` `{ "omp": { "extensions": ["./index.ts"] } }` is loaded from marketplace installs too. Manifest MCP: `.mcp.json` in the plugin root, or `mcpServers` in `.omp-plugin/plugin.json` / `.claude-plugin/plugin.json` (replaces `.mcp.json`).
- **Gemini manifest interop.** `~/.gemini/extensions/<name>/gemini-extension.json` and `<cwd>/.gemini/extensions/<name>/gemini-extension.json` are discovered as *metadata* (`name`, `description`, `mcpServers`, …) into the `extensions` capability with provider `gemini`.
  - Priority 60; a native item of the same name shadows it; user beats project within Gemini.
  - The manifest is **not executed**, and a neighbouring `.ts` is not auto-run either. Gemini CLI's MCP servers come from `.gemini/settings.json` (12.5).

**Try it (Walkthrough):**
1. Copy `solutions/my-marketplace` next to the lab (`cp -r <module-dir>/solutions/my-marketplace ../my-marketplace`). Inspect: `.omp-plugin/marketplace.json`, `plugins/lab-tools/skills/lab-conventions/SKILL.md`, `plugins/lab-tools/commands/standup.md`.
   **Expected:** three files; catalog `name` is `course-marketplace`, plugin `lab-tools`, `metadata.pluginRoot` `./plugins`.
2. In `omp`: `/marketplace add ../my-marketplace` (or `omp plugin marketplace add ../my-marketplace`).
   **Expected:** `Added marketplace: …/my-marketplace`; `/marketplace list` shows `course-marketplace`.
3. `/marketplace discover course-marketplace`.
   **Expected:** `lab-tools@1.0.0` with its description.
4. `/marketplace install --scope project lab-tools@course-marketplace`.
   **Expected:** `Installed lab-tools from course-marketplace (1.0.0)`; `.omp/plugins/installed_plugins.json` lists it; `.omp/plugins/node_modules/lab-tools` is a symlink into the cache.
5. `/reload-plugins`, then `read skill://lab-conventions` (ask the model, or `omp read skill://lab-conventions`).
   **Expected:** the SKILL.md body. `/skill:lab-conventions` also exists (`skills.enableSkillCommands` is `true` by default on 18.3.1).
6. `/lab-tools:standup HEAD~2`.
   **Expected:** the command template runs with `$ARGUMENTS` = `HEAD~2`; three-line stand-up note.
7. `/plugins disable --scope project lab-tools@course-marketplace`, `/reload-plugins`, `read skill://lab-conventions`.
   **Expected:** `Unknown skill: lab-conventions`. Re-enable with `/plugins enable …`.
8. Clean up: `/marketplace uninstall --scope project lab-tools@course-marketplace`, `/marketplace remove course-marketplace`.
   **Expected:** `.omp/plugins/installed_plugins.json` has `"plugins": {}`; `/marketplace list` says none configured.

**Guided task:** Ship the guard as a plugin.
- Goal: add a second plugin `guardrails` to your marketplace that carries `solutions/force-push-guard` as an extension.
- Hints: `plugins/guardrails/package.json` with `"omp": { "extensions": ["./index.ts"] }` and `"name"`; new catalog entry with `"version": "1.0.0"`; `/marketplace update course-marketplace`; install; **restart** (extension modules need it); then repeat 12.2 step 2.
- Checkpoints: `/marketplace discover` shows two plugins; `omp plugin list` shows both; the blocked card appears after restart.
- Pass: `git push --force` blocked with the plugin installed and allowed after `/plugins disable … guardrails@course-marketplace` + restart.

**Stretch:** Version bump. Goal: change the skill text, bump `version` to `1.1.0` in the catalog, run `/marketplace update` then `/marketplace upgrade lab-tools@course-marketplace`. Pass: `read skill://lab-conventions` shows the new text; `omp plugin list` shows `1.1.0`.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `Invalid catalog` on add | missing `name`/`owner.name`/`plugins`, or invalid JSON | fix the file; per-plugin errors only skip that entry |
| Plugin listed but `source` rejected | relative source not starting with `./`, or escapes the root | `"./plugins/x"` |
| Skill installed but `skill://` unknown | live session not refreshed | `/reload-plugins` |
| Extension in plugin does nothing after install | extension modules need a restart | restart omp |
| `npm plugin sources are not yet supported` | `source.source: "npm"` | use relative/GitHub/url/git-subdir |
| Command name is `/lab-tools:standup`, not `/standup` | plugin commands are namespaced | type the prefix |
| Two scopes, `enable` refuses | plugin in both scopes | pass `--scope user\|project` |

**Cheat sheet:**
| Item | Value |
|---|---|
| Catalog | `.omp-plugin/marketplace.json` (fallback `.claude-plugin/`) |
| Plugin tree | `skills/`, `commands/`, `agents/`, `hooks/pre|post/`, `tools/`, `.mcp.json`, `package.json#omp.extensions` |
| Add / install | `/marketplace add ./dir` · `/marketplace install [--scope project] name@mkt` |
| Manage | `/plugins list|enable|disable` · `/marketplace update|upgrade|uninstall|remove` |
| CLI | `omp plugin marketplace …` · `omp plugin install|link|doctor|list|enable|disable` |
| Refresh | `/reload-plugins` (skills/commands/MCP) · restart (tools/hooks/extensions) |
| Disk | `~/.omp/marketplaces.json` · `~/.omp/plugins/…` · `<project>/.omp/plugins/…` |

**Source:** omp://marketplace.md, omp://skills/authoring-marketplaces.md, omp://skills/examples/mini-marketplace/README.md, omp://plugin-manager-installer-plumbing.md, omp://gemini-manifest-extensions.md, omp://slash-command-internals.md, omp://skills.md

---

## Lesson 12.5 — Inheriting other tools' config              (~25 min)
**You will be able to:** list exactly which files from `.claude`, `.cursor`, `.windsurf`, `.gemini`, `.codex`, `.cline`, `.github/copilot`, `.vscode` and `opencode` omp reads; audit them with `/extensions`; switch a whole source or a single file off; opt foreign *user-level* sources in.
**Why this exists:** Most repos already carry another agent's configuration. omp reads it so you do not have to migrate — but "reads it" means those files shape the system prompt, add MCP servers, tools, commands and skills, and can shadow your own. You need to know what is loaded, from where, and with which priority, and how to turn any of it off surgically.
**Demo:** `demos/12-5-extensions-audit.md` — `/extensions` listing, then `disabledExtensions` removing one file.

**Concepts:**
- **Discovery providers and priority** (higher wins on same scope/depth): `native` 100 · `omp-plugins` 90 · `claude` 80 · `agent-plugins` 75 · `agents`, `claude-plugins`, `codex` 70 · `gemini` 60 · `opencode` 55 · `cursor`, `windsurf` 50 · `cline` 40 · `github` 30 · `vscode` 20 · `agents-md`, `claude-md` 10 · `mcp-json`, `ssh-json` 5 · `builtin-defaults` 1.
- **What each foreign source contributes** (project paths are cwd-only unless noted):
  | Source | Context | Rules | MCP | Skills / commands / tools / hooks |
  |---|---|---|---|---|
  | `.claude/` | `CLAUDE.md` (user `~/.claude/CLAUDE.md`) | — | `~/.claude.json`, `~/.claude/mcp.json`, `.claude/.mcp.json`, `.claude/mcp.json` | skills (`claude` provider, priority 80), `.claude/commands/**/*.md` (a `foo/bar.md` file is also `/foo:bar`), `.claude/tools`, `~/.claude/plugins/installed_plugins.json` (marketplace plugins) |
  | `.codex/` | user `~/.codex/AGENTS.md` only | — | `~/.codex/config.toml`, `.codex/config.toml` (`[mcp_servers.*]`) | skills (`codex` provider, priority 70), `.codex/commands/*.md` (user beats project), `.codex/tools` |
  | `.gemini/` | `GEMINI.md` | — | `~/.gemini/settings.json`, `.gemini/settings.json` | `.gemini/extensions/*/gemini-extension.json` (metadata) |
  | `.cursor/` | — | `.cursor/rules/*.mdc`, `.cursorrules` | `~/.cursor/mcp.json`, `.cursor/mcp.json` | settings |
  | `.windsurf/` | — | `.windsurf/rules/*.md`, `.windsurfrules`, global rules | `~/.codeium/windsurf/mcp_config.json`, `.windsurf/mcp_config.json` | — |
  | `.cline` | — | `.clinerules` | — | — |
  | `.github/` | `copilot-instructions.md` (+ `~/.copilot/copilot-instructions.md`) | `.github/instructions/**/*.instructions.md` (`applyTo`) | — | `.github/skills` |
  | `.vscode/` | — | — | `.vscode/mcp.json` (`mcp.servers`) | — |
  | `opencode` | user `~/.config/opencode/AGENTS.md` | — | `~/.config/opencode/opencode.json`, `opencode.json` | `~/.config/opencode/commands`, `.opencode/commands` |
  | standalone | `AGENTS.md`, `CLAUDE.md` (walk up to repo root) | — | root `mcp.json`, `.mcp.json` | — |
- **Shadowing rules (M6 recap, now with the full list).** One user context file survives (native wins). One project context file per directory depth; same depth → higher priority wins; MCP servers dedupe by name (and by identical transport/endpoint) first-wins; skills/commands first-wins by name.
- **`enabledProviders` — the switch most people miss.** Default `[]`: foreign **user-level** roots (Cursor, Codex, Claude, Claude marketplace plugins, Gemini, OpenCode, Windsurf, GitHub) are **not** loaded until their id is listed (or `*`/`all`). Foreign **project** roots load by default. Native and `~/.omp/plugins` marketplace plugins are never foreign.
- **Three off-switches, coarse to fine.**
  1. `disabledProviders: [claude, github]` — the whole source, everything it contributes; path-scoped form `- path: ~/work/legacy` / `providers: [claude]`. Shares a namespace with model providers (`gemini` = Gemini CLI files, `google` = the model backend).
  2. `disabledExtensions: [context-file:<user|project>:<basename>]` — one context file; the file it used to shadow loads in its place. Also `extension-module:<name>` from 12.1. Not path-scoped; arrays replace across layers.
  3. `mcp.enableProjectConfig: false` — every project-level MCP source, letting a same-named user entry win.
- **`/extensions`** lists every discovered context file with level, source provider and state, and toggles `disabledExtensions` for you.
- **Also `--no-rules`, `--no-skills`, `--no-extensions`** for one run.

**Try it (Walkthrough):**
1. In the lab, create three foreign files: `mkdir -p .claude .cursor/rules .vscode`; `.claude/CLAUDE.md` with `Prefer tabs.`; `.cursor/rules/style.mdc` with frontmatter `alwaysApply: true` and body `Prefer spaces.`; `.vscode/mcp.json` with `{"mcp":{"servers":{"lab-fs":{"command":"python3","args":["tools/lab_mcp_server.py","data"]}}}}`.
   **Expected:** files exist. Also make sure `.omp/AGENTS.md` from Module 6 exists.
2. Start `omp`, run `/extensions`.
   **Expected:** `.omp/AGENTS.md` listed as project/native, `.claude/CLAUDE.md` listed as project/claude and marked shadowed (same depth 0, lower priority).
3. `/mcp list`.
   **Expected:** `lab-fs` with source `.vscode/mcp.json` (provider `vscode`) — unless your `.omp/mcp.json` from 12.3 still defines `lab-fs`, in which case the native one wins and the VS Code entry is shadowed. Delete the native entry and `/mcp reload` to watch it flip.
4. Ask: `Should I indent with tabs or spaces here?`
   **Expected:** the answer cites the Cursor rule (`Prefer spaces.` is always-apply; `CLAUDE.md` was shadowed).
5. Add to `.omp/config.yml`: `disabledProviders: [cursor]`; `/new`; ask again.
   **Expected:** the Cursor rule is gone.
6. Replace with `disabledExtensions: [context-file:project:AGENTS.md]`; `/new`; `/extensions`.
   **Expected:** `.omp/AGENTS.md` shows `disabled`, and `.claude/CLAUDE.md` is now the active project context (it was unshadowed, not dropped). Remove the setting afterwards.
7. Copy `.claude/CLAUDE.md` to `~/.claude/CLAUDE.md`, `/new`, `/extensions`.
   **Expected:** the user-level Claude file is **not** listed (foreign user roots are opt-in). Add `enabledProviders: [claude]` to `~/.omp/agent/config.yml`, `/new`: now listed but shadowed by `~/.omp/agent/AGENTS.md` if you have one. Clean up.

**Guided task:** Audit an inherited repo.
- Goal: for a repo of your choice that has `.claude/`, `.cursor/`, or `.vscode/mcp.json`, produce `notes/m12-audit.md` listing every file omp loads, its provider, its priority, and whether it is shadowed.
- Hints: `/extensions` for context files, `/mcp list` for servers, `omp read skill://` / `rule://<name>` for skills and rules; `disabledProviders` path-scoped entries if you want a per-repo policy.
- Checkpoints: every row has a provider id; at least one shadowing decision explained.
- Pass: the file exists and `omp -p "read notes/m12-audit.md and list any provider you cannot find in your own discovery"` reports none.

**Stretch:** Headless hygiene. Goal: a `--config ci.yml` overlay that disables your user context file (`context-file:user:AGENTS.md`), all foreign providers, and project MCP for `-p` runs. Pass: `omp -p --config ci.yml "what repo rules apply?"` mentions only `.omp/` files.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `~/.claude/CLAUDE.md` not loaded | foreign user roots are opt-in | `enabledProviders: [claude]` |
| Disabled `claude` in global config but it is back inside one repo | project `disabledProviders` array replaced the global one | list the full set in the project file |
| `.claude/CLAUDE.md` ignored in a subdirectory | claude project lookup is cwd-only | start at the repo root or use standalone `CLAUDE.md`/`.omp/AGENTS.md` |
| Disabling `gemini` had no effect on the model | wrong namespace | `google` is the model provider |
| Cursor `.mdc` rule shows up as rulebook entry, not always-apply | frontmatter lacks `alwaysApply: true` | edit the rule or accept on-demand `rule://` |

**Cheat sheet:**
| Item | Value |
|---|---|
| Audit | `/extensions` (context files) · `/mcp list` (servers + source file) |
| Whole source off | `disabledProviders: [claude, cursor, …]` (path-scoped ok) |
| One file off | `disabledExtensions: [context-file:<level>:<basename>]` |
| Foreign user roots on | `enabledProviders: [claude, …]` or `[*]` (default `[]`) |
| Project MCP off | `mcp.enableProjectConfig: false` |
| Priority | native 100 > omp-plugins 90 > claude 80 > codex/agents 70 > gemini 60 > opencode 55 > cursor/windsurf 50 > cline 40 > github 30 > vscode 20 > agents-md 10 |

**Source:** omp://context-files.md, omp://settings.md, omp://mcp-config.md, omp://custom-tools.md, omp://slash-command-internals.md, omp://skills.md, omp://gemini-manifest-extensions.md, omp://cli-reference.md

---

## Where this module goes next
- **Module 13** runs the same extensions headless (`-p`, RPC `--no-ui`): remember `ctx.hasUI` guards.
- **Module 15 (capstone)** requires one extension or MCP server in the flow — `force-push-guard` and `lab-fs` both qualify.
- Full API reference: `read omp://extensions.md`; full event list § "Event surface".
