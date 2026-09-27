# Module 12 — Exercises

All exercises run in `omp-course-lab` from `git checkout module-12-start`. `<module-dir>` is this directory — with the course checked out beside the lab and your cwd in `omp-course-lab`, that is `../modules/M12-extending-omp`. Record evidence in `notes/m12.md` (gitignored). Every exercise has three tiers: **W** (Walkthrough — exact keys), **G** (Guided — goal + hints + checkpoints), **S** (Stretch — goal only; instructor notes in `solutions/`).

Time budget: W 25 min · G1 15 · G2 20 · G3 20 · S 20.

---

## W — Hello extension + `word_count`              (~25 min)

**Setup**
1. `mkdir -p .omp/extensions && cp -r <module-dir>/solutions/hello-extension .omp/extensions/hello-extension`
2. `omp`
   Expected: notification `hello-extension loaded in <lab path>`.

**Command**
3. `/hello Ada`
   Expected: custom message `Hello, Ada!` in the transcript; notification `Greeted Ada`; **no** model turn starts (status line stays idle).
4. `/hello`
   Expected: `Hello, world!`.

**Tool**
5. Prompt: `Read README.md, then call word_count on its full contents and tell me only the number.`
   Expected: a `read` card, then a `word_count` card. `Ctrl+O` on the card: `Counting...` was streamed, final text is an integer, `details.count` matches.
6. Cross-check: `wc -w README.md` in a shell. The two numbers may differ slightly (the tool splits on whitespace; `wc` counts the same way, so usually equal). Note both in `notes/m12.md`.

**Loading variants**
7. `omp config get disabledExtensions` → `[]`. Add to `.omp/config.yml`:
   ```yaml
   disabledExtensions:
     - extension-module:hello-extension
   ```
   Restart; `/hello`. Expected: unknown command. Remove the setting.
8. `mv .omp/extensions/hello-extension /tmp/hello-extension && omp -e /tmp/hello-extension`.
   Expected: `/hello` works again for this session. Move it back.

**Pass condition:** `notes/m12.md` contains the `word_count` result, and the transcript (or `/export notes/m12-w.html`) shows one `word_count` tool card with `details.count`.

---

## G1 — `tool_call` guard: block `git push --force`              (~15 min)

**Goal:** the model cannot force-push, and it can read *why* in the tool result.

**Hints**
- Start from `<module-dir>/solutions/force-push-guard/index.ts` — or write your own from `omp://skills/authoring-hooks.md` § "Pre-tool blocking contract": `pi.on("tool_call", ...)`, check `event.toolName === "bash"`, inspect `event.input.command`, return `{ block: true, reason }`.
- Put it in `.omp/extensions/force-push-guard/index.ts`; restart.
- Prompt: `Run exactly this with bash and show me the output: git push --force origin main`.
- To see the raw message the model receives, run once headless with the JSON event stream: `omp -p --mode json --no-session "Run with bash: git push -f origin main" | grep tool_execution_end`.

**Checkpoints**
1. Interactive: a confirm dialog **Force push blocked** appears (the `ctx.hasUI` branch); answer No.
2. The `bash` card is red; expanded text begins with `force-push-guard:`.
3. The model's next message acknowledges the block (it does not claim the push succeeded).
4. `git push --force-with-lease origin main` is **not** blocked (it fails on the missing remote instead).

**Pass condition:** the JSON stream line `{"type":"tool_execution_end",...,"toolName":"bash","result":{"content":[{"type":"text","text":"force-push-guard: ..."}]},"isError":true}` is saved in `notes/m12.md`.

---

## G2 — `.omp/mcp.json` with the filesystem MCP server              (~20 min)

**Goal:** omp lists files in `data/` through an MCP tool, and `/mcp list` shows the file the server came from.

**Prerequisite:** Node.js + `npx` for the `filesystem` server. Without Node, use the `lab-fs` Python server instead (`cp <module-dir>/solutions/mcp/lab_mcp_server.py tools/`); every checkpoint applies with `lab_fs` in place of `filesystem`.

**Hints**
- Copy `<module-dir>/solutions/mcp/mcp.json` to `.omp/mcp.json`; replace `/ABSOLUTE/PATH/TO/omp-course-lab/data` with `$(pwd)/data`.
- `/mcp list` → source column; `/mcp test filesystem`; `/mcp reload` after editing the file (no restart).
- Tool names are `mcp__filesystem_<tool>` — ask for them by name: `Use mcp__filesystem_list_directory on data/ and report sizes.`
- `tools.approvalMode: write` (M4) will prompt: MCP tools are `write` tier.
- Resource read: `omp read mcp://lab-fs://listing` (Python server only).

**Checkpoints**
1. `/mcp list` shows the server as connected with source `.omp/mcp.json`.
2. `/mcp test <name>` succeeds and prints a tool count (3 for `lab-fs`).
3. A `mcp__filesystem_*` (or `mcp__lab_fs_*`) card appears; expanded `details` show `serverName` and `mcpToolName`.
4. `LAB_DATA_DIR=docs omp read mcp://lab-fs://listing` lists `docs/` — `${VAR:-default}` expansion works.

**Pass condition:** `notes/m12.md` has the `/mcp list` line and the name of one `mcp__` tool card that ran.

---

## G3 — Two-file local marketplace              (~20 min)

**Goal:** a marketplace directory with one plugin carrying one skill and one command; installed, reachable, uninstalled.

**Hints**
- Minimum: `my-marketplace/.omp-plugin/marketplace.json` + `my-marketplace/plugins/lab-tools/skills/lab-conventions/SKILL.md`. Add `commands/standup.md` for the command. Reference: `<module-dir>/solutions/my-marketplace/`.
- Catalog fields: `name`, `owner.name`, `plugins[{name, source: "./lab-tools"}]`, optional `metadata.pluginRoot: "./plugins"`.
- `/marketplace add ../my-marketplace` → `/marketplace install --scope project lab-tools@course-marketplace` → `/reload-plugins`.
- Plugin commands are namespaced: `/lab-tools:standup`.
- Clean up with `/marketplace uninstall --scope project …` and `/marketplace remove course-marketplace`.

**Checkpoints**
1. `/marketplace discover course-marketplace` lists `lab-tools@1.0.0`.
2. `.omp/plugins/installed_plugins.json` lists the plugin; `.omp/plugins/node_modules/lab-tools` is a symlink.
3. `read skill://lab-conventions` returns the SKILL.md body; `/skill:lab-conventions` is offered by autocomplete.
4. `/lab-tools:standup HEAD~2` runs the template with `$ARGUMENTS`.
5. `/plugins disable --scope project lab-tools@course-marketplace` + `/reload-plugins` → `Unknown skill: lab-conventions`.

**Pass condition:** `omp read skill://lab-conventions` prints the skill while installed, and `.omp/plugins/installed_plugins.json` is `{"version": 2, "plugins": {}}` after uninstall.

---

## S — Reroute `scout` to a cheap model with `before_subagent_spawn`              (~20 min)

**Goal:** every `scout` subagent runs on the model behind your `smol` role, and Agent Hub shows the routing reason.

**Pass condition:** with `<module-dir>/solutions/scout-router` installed and `modelRoles.smol` set to a cheap model you are logged in to, a batch `task` with `agent: "scout"` (M10) shows the scout's resolved model equal to the `smol` model in Agent Hub (`Alt+A`), and the task result's expanded details show `resolvedModelRoute: "scout-router: scouts run on <provider>/<id>"`. A `task` agent in the same batch is **not** rerouted.

Instructor notes: `solutions/scout-router/index.ts` and `BUILD-NOTES.md` (verified on 18.3.1 through `task` details: `modelOverride`, `resolvedModel`, `resolvedModelRoute`).

---

## Extra credit (no solutions provided)
- `tool_result` redactor for `labtok_…` (README 12.2 Guided task).
- `mcp_notification` bridge (README 12.3 Stretch).
- `--config ci.yml` headless hygiene overlay (README 12.5 Stretch).
