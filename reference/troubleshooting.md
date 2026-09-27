# Troubleshooting index

Aggregated and deduplicated from the **Troubleshooting** sidebars of modules M01–M14 (502 rows → the recurring ones). Symptom → cause → fix; the module column points at the lesson with the full context.

## Install, launch, CLI

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `omp: command not found` after install | PATH not refreshed | new shell; check the install script's final message | M1 |
| `omp update` / `--check` fails with a GitHub rate-limit message | anonymous API quota | `GITHUB_TOKEN=… omp update` | M1 |
| `omp <word>` opened the TUI instead of running a command | `<word>` is not a subcommand → it became the prompt | check `omp --help` COMMANDS | M1 |
| omp starts in `/tmp/…` instead of the repo | launched from `~` | `cd` into the repo, or `--allow-home` | M1 |
| Piped prompt hangs / waits | `-` argument or missing `-p` | `echo "…" \| omp -p` | M1, M13 |
| Output file contains `Working...` | you captured stderr | `2>/dev/null` (stdout is clean) | M1, M13 |
| Prompt starting with `-` parsed as a flag | flag parsing | `omp -p -- "-x …"` | M13 |
| Exit 1 with empty output in CI | `Deadline exceeded` | raise `--max-time`, narrow the prompt | M13 |
| Run hangs at start (CI / `-p`) | slow or dead MCP server in project config | `OMP_MCP_REQUIRE_READY=1` to fail fast; raise `OMP_MCP_TIMEOUT_MS`; remove MCP in the bot profile | M12, M13 |

## Keys and terminal

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `Ctrl+Shift+O` acts like `Ctrl+O`; `Alt+A` types `a`; `Shift+Tab` / `Alt+Shift+P` / `Ctrl+P` dead | terminal lacks modifier encoding (Kitty keyboard protocol) or tmux/shell swallows the chord | enable the protocol; tmux `extended-keys`; remap the action in `~/.omp/agent/keybindings.yml`; `/hotkeys` shows what omp sees | M1–M4, M7, M10 |
| `Ctrl+Enter` does nothing (Windows Terminal) | terminal swallows it | `Ctrl+Q` (same action `app.message.followUp`) | M1–M3 |
| `Ctrl+Q` does something else | your `keybindings.yml` already binds it | bind `app.message.followUp` explicitly | M2, M3 |
| `Ctrl+V` image paste does nothing (Windows Terminal) | terminal paste intercepts | `Alt+V`, or paste a single image-file path | M1, M2 |
| A remapped chord is ignored | wrong file / wrong action ID / not restarted | must be `~/.omp/agent/keybindings.yml` (not `config.yml`); copy the ID from `/hotkeys` | M1 |
| Screen garbled after resize | renderer/terminal desync | `Alt+L`; Warp: `PI_TUI_RESIZE_IN_PLACE=0`/`1` | M1, M2 |
| `Esc` doesn't stop the turn | `interruptMode: wait`, or Vim Insert→Normal consumed it | `omp config get interruptMode`; press `Esc` again | M2 |
| Double `Esc` opened a full-screen picker | rewind selector (`doubleEscapeAction: rewind`) | `Esc` to close; `omp config set doubleEscapeAction none` | M2, M3 |
| Cards vanished and stay gone | `display.hideToolActivity: true` persisted | `Ctrl+Shift+O` or reset the setting | M2, M3 |
| No thinking block ever appears | level `off`/`minimal`, `hideThinkingBlock: true`, or `--hide-thinking` | `Shift+Tab` raise level; `Ctrl+T`; check the setting | M2, M3 |

## Auth, models, providers

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `No active credential found for provider "<id>"` / "no credentials" on first turn | provider not authenticated | `/login <provider>` or export its env var; `omp token <provider>` lists configured providers | M1, M7, M13 |
| Browser never opens during `/login` | headless/remote box | `omp login <provider>` prints the URL; paste the callback as `/login <redirect-url>` | M1 |
| Model missing from `/model` / `omp models`, provider shows `○` | in `disabledProviders`, or no credentials, or filtered by `enabledModels` | `omp config get disabledProviders`; available = not disabled **and** (keyless or credentialed) | M1, M7 |
| Wrong/stale key used | higher-precedence source (`--api-key` › `models.yml apiKey` › stored OAuth › `/login` key › env/`.env`) | walk the list; `unset` the shell var; check the four `.env` files | M1, M7 |
| `omp config set modelRoles …` wiped other roles | record is replaced whole | pass the complete object or edit `config.yml` | M7 |
| `Warning: models.yml validation failed — custom providers disabled` | schema error (missing `baseUrl`/`api`, `apiKey` without `auth: none`) | read the reason under the warning; `omp models` again | M7 |
| Retry loader spins, no fallback | `retry.modelFallback: false`, no chain, or all candidates cooling down | add a `default` chain in `retry.fallbackChains`; `omp models` lists the fallback | M7 |
| `disabledProviders: [gemini]` didn't touch Google models | `gemini` is a discovery-source id | model provider is `google` | M6, M7, M12 |
| `Total Cost: $0.0000` for real work | unpriced discovered/gateway model | add a `cost` block in `models.yml`; `omp usage` for plan providers | M7 |

## Settings and config files

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `omp config set` says another source overrides | env var, project file, overlay, or runtime override wins | `--json` shows `overriddenBy`; fix that layer | M1, M6, M7 |
| `Unknown setting` | not a full schema path | `omp config list`; copy the key | M1 |
| Project `.omp/config.yml` ignored | launched from a parent/sibling dir (no ancestor walk), `.omp/` empty, or YAML top level not a mapping | `cd` to the dir holding `.omp/`; `omp config get <key>` there | M1, M6, M9 |
| `omp config set` "changed the wrong file" | it always writes global | edit `<repo>/.omp/config.yml` by hand | M6, M9 |
| Global array vanished in a project (e.g. `disabledProviders`) | arrays replace per layer | repeat the full array in the project file | M6, M7, M12 |
| Profile does not see your logins / sessions | profiles have their own agent dir | `omp --profile <n> login …`; same `--profile`/`OMP_PROFILE` | M1, M5 |
| Tools missing after enabling a gate | roster not refreshed | `/restart` or a new session | M9, M11, M14 |

## Context files, rules, skills, commands

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `/extensions` shows no project context file | `.omp/` or `AGENTS.md` empty | empty files/dirs are skipped | M6 |
| Loads from repo root but not from a subdirectory | nearer non-empty `.omp/` without `AGENTS.md` stops the walk; `.claude/`, `.omp/rules`, `.omp/commands`, `.omp/extensions`, `.omp/agents` are cwd-only | launch from the root; add the file to the nearer `.omp/` | M6, M10, M12 |
| Edited `AGENTS.md`/`RULES.md`, nothing changed | discovered at session start / reset | restart, `/new`, or `/clear` | M6 |
| Project `RULES.md` ignored | user `~/.omp/agent/RULES.md` shadows it (same rule name) | merge or delete the user one | M6 |
| Rule not listed anywhere | no `description` and no `alwaysApply` | add one | M6 |
| `omp read rule://…` / `memory://…` fails in the shell | per-session URIs | ask omp to read them in-session | M6, M9 |
| "omp ignores my CLAUDE.md" | shadowed by a same-depth higher-priority file | `/extensions`; move guidance to `.omp/AGENTS.md` | M6, M12 |
| Disabled `claude` and lost MCP/commands | `disabledProviders` removes the whole source | `disabledExtensions: [context-file:…]` | M6 |
| `~/.claude/CLAUDE.md` / `~/.cursor/rules` never load | foreign user roots are opt-in | `enabledProviders: [claude, cursor]` | M6, M12 |
| New command absent from completion | no file watcher | `/reload-plugins` or restart | M6, M12 |
| `/skill:name` not offered | `skills.enableSkillCommands: false` | set it back to `true` | M6 |
| Agent stopped using `todo`/delegation conventions | `SYSTEM.md` replaced the instruction block | use `APPEND_SYSTEM.md` | M6 |

## Turns, tools, output

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| Final message says "tests pass" but no `bash` card | model reported from memory | "Run `<cmd>` now and show the output" | M1, M3 |
| `read` shows `…` and `[…N ln elided…]` | structural summary (≥ 100 lines) | ask for the ranges, or `read.summarize.enabled: false` | M2 |
| `Artifact N not found` / `No session - artifacts unavailable` | wrong session, or `--no-session` | ids are per session; drop `--no-session` | M2, M3 |
| `Edit` refused "outside recorded seen-line ranges" | model read a summary, not the lines | `read path:A-B` first | M2 |
| Edits fail after your own git revert / editor format-on-save | stale hashline tags | tell omp to re-read | M2, M4 |
| `Edit` refused on `generated/…` | `edit.blockAutoGenerated: true` | intended; set `false` only deliberately | M2 |
| Service `State: failed — process exited before readiness` / never ready at 30 s | port in use, crash, wrong `ready.port`/`host` | `read proc://<name>`; `write proc://<name>/kill` stale instance | M2 |
| `Async bash execution is disabled` / `name` not available / `pty requested but unavailable` | `async.enabled` false / `launch.enabled` false or non-TUI / `--no-pty` or headless | enable; use the TUI | M2 |
| `Ask tool requires interactive mode` / no `ask` in `-p` | TUI-only tool | use the TUI | M2, M3 |
| Model never uses `ask` | prefers prose, or `ask.enabled: false`, or instruction was conditional | "use the ask tool"; make it unconditional | M2, M3 |
| `web_search` error, `provider: none` | no search provider for the `web` role | set a key or `modelRoles.web` | M2, M8 |
| `ultrathink` has no gradient / gradient but no effect | not lowercase standalone prose / `magicKeywords.*` false | fix the word; `omp config get magicKeywords.enabled` | M3, M10 |

## Approvals, plan mode, review, git

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| Nothing ever prompts | default `tools.approvalMode: yolo` | `--approval-mode write` or `omp config set tools.approvalMode write` | M4, M14 |
| `edit` prompts even in `write` mode | `tools.approval.edit: prompt` override or tool declared `exec` | `omp config get tools.approval`; reset | M4, M12 |
| Subagent errors with a rejected tool call | `tools.approval.<tool>: prompt` cannot be answered headless | `allow`/`deny` instead | M4 |
| Allow rule matches but still prompts | compound command / redirection / `cd` | simple commands, or `bash.allowCompoundCommands: true` | M4 |
| `bash.patterns` rule never matches | only `*` is a wildcard | `python3 -m unittest*` | M4 |
| `/plan-review` says nothing to review | not in plan mode or no plan yet | toggle plan mode; ask for a plan | M4 |
| `/annotate path` missing file | resolved against live session cwd | relative to session cwd or `./` prefix | M4 |
| `read pr://…` / `issue://` fails | not a GitHub checkout, `gh` missing/unauthenticated | `gh auth status`; `pr://owner/repo/N` | M4, M8, M13 |
| `No model available for commit generation` | no provider / `commit`+`smol` roles unresolved | `/login` or `omp commit -m <model>` | M4 |
| `Conflict #1 not found` | ids are session-scoped, invalidated on resolve | `read <file>:conflicts` again | M4 |
| Write to `conflict://1/ours` rejected | side scopes are read-only | write `conflict://1` | M4 |

## Sessions and context

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| No `.jsonl` after starting | created lazily on the first assistant message | finish one turn | M5 |
| `omp -c` opens the wrong session; after `/new` `-c` opens the old one | breadcrumb belongs to another pane/cwd; new file not materialized | `omp --resume` and pick; run one turn first | M5 |
| `--resume abc` picks an unexpected session | prefix matched several; newest wins | more characters / full filename | M5 |
| `/clear`, `/fresh`, `/fork` refused; `/fork` "requires persistence" | streaming or `!` running; `--no-session` | `Esc` then retry; run persisted | M3–M5 |
| `/tree` → `Already at this point` | selected the current leaf | move the cursor | M5 |
| Enter never asks about summaries | `branchSummary.enabled: false` | enable, or `Shift+Enter` | M5 |
| `Nothing to compact (session too small)` / `Nothing to hand off` | under the recent-tokens floor / already compacted | do more work; lower `compaction.thresholdTokens` | M5 |
| `Context overflow recovery failed` | no runnable method | add `snapcompact`/`shake` to `methodOrder`, or `/clear` | M5 |
| `Cannot export in-memory session to HTML` | `--no-session` | `/share` or `/dump`, or run persisted | M5 |
| `Context notes are N UTF-8 bytes…` | > 16,384 bytes | keep the notebook short; `history://current/full` for detail | M11 |
| `/extended-context on` no effect | model has no `maxContextWindow` | add it in `models.yml` | M11 |

## Toolbox (eval, LSP, AST, debug, gated tools)

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `Python backend not available` | no Python ≥ 3.10, `eval.py` false, `PI_PY=0` | `omp setup python --check`; `python.interpreter` | M8 |
| `%pip` → `No module named pip` | kernel interpreter lacks pip | venv with pip; point `python.interpreter` at it | M8 |
| `No language servers configured for this project` / `No language server found` | no root marker in **cwd** or binary not on PATH; started in a subdirectory | ship `pyproject.toml`; install `pyright`/`pylsp`; start at the root; `lsp reload` | M8 |
| `ast_grep` not in the tool list | `astGrep.enabled: false` | `omp config set astGrep.enabled true` | M8 |
| `find` missing | `find.enabled: auto` and judge is not a TypeSafe jev model | `find.enabled: on` or `TYPESAFE_API_KEY` | M8 |
| `No debugger adapter available` / `No module named debugpy` | adapter not resolvable; debugpy in another interpreter | `pip install debugpy` into the `python` on PATH; `.omp/dap.json` | M8 |
| `github` never appears after enabling | `gh` not on PATH | install GitHub CLI; restart | M8 |
| `Security is disabled…` / `preflight` rejects credentials | `security.enabled: false` / API-key auth | enable; `/login` with OAuth | M8 |
| `generate_image` skipped all candidates / `No xAI credentials` | no image / TTS model with credentials | `omp models --kind image`; `modelRoles.image`; local Kokoro for `.wav` | M8 |

## Memory, skills, checkpoints

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `Mnemopi backend is not initialised` | DB / embedding / LLM init failed | `/memory diagnose`; `mnemopi.noEmbeddings: true`, `mnemopi.llmMode: none`; restart | M9 |
| `read memory://root` fails under `mnemopi` | root exists only with `memory.backend: local` | `recall`/`reflect`, or `memory://<id>` | M9 |
| No `MEMORY.md` under `local` | consolidation runs at next startup for sessions idle ≥ 12 h | `/memory sync` now; `/memory enqueue` | M9 |
| `learn` missing | needs `autolearn.enabled` **and** `memory.backend ≠ off` | `manage_skill` alone works with `off` | M9 |
| `No relevant memories found.` right after retaining | different bank (cwd changed; `per-project` scoping) | stay in the same directory | M9 |
| `memory_edit` → `not_editable` / `not_found` | fact row / episodic row | read `memory://<id>`; use `invalidate` | M9 |
| No `checkpoint` tool / `No active checkpoint…` | `checkpoint.enabled: false`, subagent, or `rewind` first | enable; add to agent `tools:`; ask for the checkpoint | M9 |
| Files still changed after `rewind` | rewind restores conversation only | git revert | M9 |

## Subagents, guardrails, extensions

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `Unknown agent "Scout"` | names exact, case-sensitive; only nearest `.omp/agents` | `scout`; `read history://` | M10 |
| Call rejected: missing `context` / `effort` or `isolated` "not a valid parameter" | batch shape needs `context`; `task.enableEffort` off; `task.isolation.enabled` false or plan mode on | add `context`; enable the gate; leave plan mode | M10 |
| Results never arrive; turn ended | async delivery | keep working; `read proc://`; `wait` only when blocked | M10 |
| `Subagent exited without calling yield tool` | weak model | stronger agent / smaller task; output still in `agent://<id>` | M10 |
| Child edited files unexpectedly | subagents run `yolo` | `scout`, or `isolated: true` | M10 |
| `r` has no effect / `write agent://` fails for an isolated child | only `parked` agents revive; isolated agents have no reviver | message idle agents; spawn anew | M10 |
| `Isolated task execution requires a git repository.` / patch not applied | not a git repo / patch conflict | `git init`; `git apply --3way <path>` | M10 |
| `/vibe` refused; `/new` `/fork` `/move` `/handoff` refused | plan/goal mode active; vibe active | exit the other mode first | M10 |
| `omp ttsr list` doesn't show your rule / never fires on prose | wrong path/extension/shadowed; default scope excludes `thinking` | `.omp/rules/<name>.md`; `scope: "text, thinking"`; `omp ttsr test` | M11 |
| `Advisor setting enabled, but no model is assigned to the 'advisor' role.` | `modelRoles.advisor` unset | `omp config set modelRoles.advisor <provider/id>` | M11 |
| `Warning: prewalk disabled — no API key for …` / armed but never switches | target lacks credentials / no `todo` or edits went through `bash` | `--prewalk-into`; ask for a plan first | M11 |
| Hook file ignored | not under `hooks/pre/` or `hooks/post/` | move it | M11, M12 |
| `browser.open(...)` / `computer` not intercepted by hooks | prelude bridge calls are not `AgentTool` calls | documented; use TTSR or approval policy | M11 |
| `ExtensionRuntimeNotInitializedError` | runtime action inside the factory | move into a handler | M12 |
| Model writes to `xd://word_count` instead of calling the tool | `loadMode: "discoverable"` (default) | `loadMode: "essential"` (both execute) | M12 |
| `stdio server requires "command" field` / `both "command" and "url"` | remote without `"type": "http"`; mixed transports | add `type`; keep one | M12 |
| Server absent from `/mcp list` | `mcp.enableProjectConfig` off, `disabledServers`, or same-name shadowing | check each; rename | M12 |

## Headless, embedded, browser, desktop, collab

| Symptom | Cause | Fix | Mod |
|---|---|---|---|
| `Model "x" not found` … exit 1 | no credential / bad fuzzy id | `omp models`; env key or `--api-key` | M13 |
| RPC client blocks after last frame / `prompt` `success:false` mid-turn | stdin not closed or stdout not drained; second prompt without `streamingBehavior` | close stdin, drain stdout; `"streamingBehavior":"steer"` | M13 |
| ACP: every write asks although config says yolo | default-config ACP keeps the client gate | `tools.approvalMode: yolo` explicitly or `--yolo` | M13 |
| Review bot edits files | a fence is missing | `--tools`, deny list in `ci.yml`, `--no-extensions`, no `--yolo` (flags beat overlays) | M13 |
| `browser` / `computer` global missing in a cell | `browser.enabled` / `computer.enabled` off, or eval off | set them; `/computer on` for one session; new session | M14 |
| `document is not defined` inside `tab.run` | runs in the worker, not the page | `tab.evaluate` / `page.$eval` | M14 |
| macOS blank capture / `PermissionDenied` | Screen Recording / Accessibility not granted | grant to the terminal app, restart it | M14 |
| `BackgroundUnavailable` / `InvalidCoordinateFrame` / `StaleRef` | background input refused / old screenshot / AX generation moved | AX `press()` or `delivery: "foreground"`; re-screenshot; `win.ax()` again | M14 |
| Guest can read but prompt is refused | view-only link | ask for the full `/collab` link | M14 |
| Space doesn't record / dictation never submits | `stt.enabled: false`; `stt.submitTrigger: never` | enable + `omp setup speech`; `release` / `say-submit` | M14 |

Source: Troubleshooting tables in `modules/M01`–`M14/README.md` (each row verified there against omp:// docs by its module builder)
