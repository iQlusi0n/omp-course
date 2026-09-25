# Module 12 — Instructor notes and solutions

Every file here was executed against omp 18.3.1 during the build (evidence in `../BUILD-NOTES.md`). Learners can copy them verbatim; instructors should read the notes below before grading.

| Exercise | Solution | Verified how |
|---|---|---|
| W — hello + `word_count` | `hello-extension/{index.ts,package.json}` | Loaded via `.omp/extensions/`, `-e <dir>`, and `extensions:` setting; `/hello` in `available_commands_update`; `word_count` executed with `details.count`; disabled via `disabledExtensions`. |
| G1 — force-push guard | `force-push-guard/index.ts` (ExtensionAPI) · `hooks/pre/no-force-push.ts` (HookAPI) | `git push --force` → blocked, reason delivered as the `tool` message to the next provider request; `--force-with-lease` allowed; hook ignored outside `pre/`. |
| 12.2 custom tool | `tools/repo_stats.ts` | Discovered from `.omp/tools/`; card `2 tracked files match *.py`, `details.sample`. |
| G2 — MCP | `mcp/mcp.json` · `mcp/lab_mcp_server.py` | `omp read mcp://lab-fs://listing`; `${VAR:-default}`; `enabled:false`; `mcp__lab_fs_read_file` and `mcp__lab_fs_list_files` calls; relative `args`/script paths resolve against cwd. `filesystem` (npx) entry not run on the build machine (no Node). |
| G3 — marketplace | `my-marketplace/` | `omp plugin marketplace add/list/discover/install --scope project/disable/enable/uninstall/remove`; `skill://lab-conventions`; `/lab-tools:standup` and `/skill:lab-conventions` registered. |
| S — scout router | `scout-router/index.ts` | `before_subagent_spawn` fired (a `block:true` variant produced `Task execution failed: scout-router TEST BLOCK`); real variant produced task details `modelOverride: ["local-fake/fake-model"]`, `resolvedModel`, `resolvedModelRoute: "scout-router: scouts run on local-fake/fake-model"`. |

## Grading notes

- **W:** accept either a `word_count` card or an `xd://word_count` write card — both execute the tool. The shipped solution sets `loadMode: "essential"` so the plain card appears; a learner who copied the docs example (no `loadMode`) will see `xd://` dispatch. That is correct behavior, not a failure.
- **G1:** the pass evidence is the `tool_execution_end` line with `isError: true` and the learner's reason text. If the learner's regex also blocks `--force-with-lease`, point out the negative lookahead in the solution; not a failure.
- **G2:** `/mcp list` must show the source file. In `tools.approvalMode: write` there will be an approval prompt because MCP tools are `write` tier — expected. The harness intent field `i` does **not** reach the server (see BUILD-NOTES); do not penalize a server that declares `i` and never receives it.
- **G3:** the command is `/lab-tools:standup`, namespaced. `/reload-plugins` is required after install before `skill://` resolves in the running session; `omp read skill://…` from a new shell works immediately.
- **S:** Agent Hub was not capturable on the build machine; grade on the task result's expanded `details` (`resolvedModel` = the `smol` model, `resolvedModelRoute` = the note) or the Hub row's model column.

## Throwaway harness used for verification (not shipped)

- A scripted OpenAI-compatible mock (`/v1/chat/completions`, streaming) registered in `models.yml` under profile `m12build` so real tool calls could be driven without credentials.
- `omp --mode rpc --no-ui --no-session` with `get_state` (`dumpTools`) and `get_available_commands` to prove registration.
- `omp -p --mode json` to capture `tool_execution_*` events and the mock's request log to see what the model received.
