# Slash commands (grouped)

Only commands documented in omp:// docs or used in modules M01–M14 are listed; the doc column names where the command appears. Custom commands come from `.omp/commands/<name>.md` (`/name`), skills from `/skill:<name>`, plugins from `/<plugin>:<cmd>`, extensions from `pi.registerCommand`. An unknown `/word` is sent to the model as text. `/help` lists what your build registers.

## Session

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/new` | empty conversation, new session id | session-operations-export-share-fork-resume.md | M5 |
| `/resume [id \| @claude \| @codex]` | picker (`Tab` = all projects) / switch / import foreign transcript | session-switching-and-recent-listing.md | M5 |
| `/rename [title]` | set title, or generate one with the tiny title model | session.md | M5 |
| `/move <path>` | relocate the session to another directory (refused while a `/btw` runs) | slash-command-internals.md | M5 |
| `/wt` | move the session into a new git worktree (`/worktree` alias seen in M5 only) | slash-command-internals.md | M5 |
| `/fresh` | reset provider stream state; transcript/context kept; idle only | session-operations-export-share-fork-resume.md | M3, M5 |
| `/clear` | drop model context (`reset_boundary`), history stays on disk; re-reads `RULES.md` | session-operations-export-share-fork-resume.md | M5, M6 |
| `/delete` | delete current session + artifacts (best-effort), start a new id | session-operations-export-share-fork-resume.md | M5 |
| `/restart` | relaunch with the original flags and resume in place | session-operations-export-share-fork-resume.md | M5, M11 |
| `/tree` | branch navigator; leaf moves inside the same file | tree.md, session-tree-plan.md | M5 |
| `/branch` | rewind selector → new file for a user target (`doubleEscapeAction: tree` makes it behave like `/tree`) | tree.md | M5 |
| `/fork` | full copy into a new session (`parentSession`); not while streaming, needs persistence | session-operations-export-share-fork-resume.md | M4, M5 |
| `/export [--themes] [path]` | HTML export (`Cannot export in-memory session` under `--no-session`) | session-operations-export-share-fork-resume.md | M5 |
| `/dump` | copy transcript JSON to clipboard | session-operations-export-share-fork-resume.md | M5 |
| `/share` | encrypted share link (`share.redactSecrets`, `share.store`) | session-operations-export-share-fork-resume.md | M5 |
| `/record` | toggle `.ompcast` recording (`● REC`) → `<tmpdir>/omp-recordings/` | stream.md | M5, M14 |
| `/copy` `/open` `/help` `/hotkeys` `/theme` `/exit` `/quit` | local UI commands (also allowed to collab guests) | collab.md, keybindings.md | M1, M14 |
| `/pause` | park main agent, subagents and advisor at their next safe boundary; resume `Esc`/`Enter`/`Space`/`Ctrl+C`; TUI only | slash-command-internals.md | M3 |
| `/btw <question>` · `/btw` | independent side question · history panel; stored under `btw-history/` | slash-command-internals.md | M3 |

## Context

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/compact [instructions]` | summarize old history in place | compaction.md | M5, M11 |
| `/handoff [focus]` | handoff-style compaction (in-place entry) | compaction.md, handoff-generation-pipeline.md | M5, M11 |
| `/shake` | shake compaction method | compaction.md | M5 |
| `/extended-context on \| off` | select the model's `maxContextWindow` / restore normal (`extendedContext` setting) | models.md | M11 |
| `/todo expand` · `/todo collapse` · `/todo` | todo HUD visibility / historical state | tools/todo.md | M2 |
| `/extensions` | list/toggle discovered context files, rules, commands, skills; shows shadowing | context-files.md | M6, M12 |
| `/reload-plugins` | refresh skills, commands, MCP (not extensions/hooks/tools) | slash-command-internals.md, marketplace.md | M6, M12 |
| `/skill:<name> [args]` | run a skill as a command (`skills.enableSkillCommands`, default `true`) | skills.md | M6, M9 |
| `/memory view \| stats \| diagnose \| queue \| sync \| clear \| reset \| enqueue \| rebuild \| mm …` | memory backend inspection and maintenance (`memory.backend ≠ off`) | memory.md | M9 |
| `/omfg <complaint>` | generate a TTSR rule from a complaint | ttsr-injection-lifecycle.md | M11 |

## Model

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/model` | model picker; assign roles (same as `Alt+M`) | models.md | M7 |
| `/login [provider \| redirect-url]` · `/logout` | authenticate a provider (or Stencil for stream/clip) · sign out | providers.md | M1, M7, M14 |
| `/settings` | settings panel (writes global `config.yml`); e.g. Interaction → Input, Magic Keywords, Context → Compaction | keybindings.md, compaction.md, magic-keywords.md | M1–M3 |

## Agents

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/agents` | agent-definition hub: per-agent prewalk / advisor strips (`task.agentPrewalk`, `task.agentAdvisor`) | task-agent-discovery.md, advisor-watchdog.md | M10, M11 |
| `/jobs` | snapshot of background jobs and services (Agent Hub companion) | agent-hub.md | M10 |
| `/vibe [first directive]` | enter vibe mode (director + `vibe_*` workers); `/vibe` again exits and kills workers | vibe-mode.md | M10 |
| `/advisor [on \| off \| status \| dump [raw] \| configure]` | second-model watchdog (`modelRoles.advisor`, `advisor.enabled`) | advisor-watchdog.md | M11 |
| `/prewalk` · `/prewalk restart` | arm prewalk / back to `@default` and re-arm (no `status` subcommand) | prewalk.md | M11 |
| `/computer` · `/computer on \| off \| status` | toggle the desktop prelude for this session only | computer-use.md | M14 |

## Review & plan

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/review [focus]` | single-target code review (what `/annotate` submits after "Continue with LLM review"; CI bot prompt in M13) | slash-command-internals.md | M4, M10, M13 |
| `/annotate [code-review [pr://owner/repo/N] [focus] \| last \| session \| <path> \| "text"]` | annotate a diff or text; diff notes → `/review`, text notes → composer | slash-command-internals.md | M4 |
| `/plan-review` | reopen the Plan Review overlay (plan mode only) | slash-command-internals.md | M4 |

## Config, plugins, MCP

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/mcp add \| remove \| enable \| disable \| test \| reconnect \| reload \| reauth \| unauth \| resources \| prompts \| notifications \| list` | manage MCP servers | mcp-config.md | M12 |
| `/marketplace add \| remove \| update \| list \| discover \| install \| uninstall \| installed \| upgrade` | marketplace catalogs and plugins (`--scope user \| project`) | marketplace.md | M12 |
| `/plugins list \| enable \| disable` | toggle installed plugins | marketplace.md | M12 |

## Collab & live

| Command | Effect | Doc | Module |
|---|---|---|---|
| `/collab` · `/collab view` · `/collab <relay>` · `/collab status` · `/collab stop` | host a room (control / view-only / custom relay) | collab.md | M14 |
| `/join <link>` · `/leave` | join / leave a room (`omp join "<link>"` from a shell) | collab.md | M14 |
| `/live` | live voice mode (same as `Ctrl+L`, `app.live.toggle`) | keybindings.md | M14 |

## Shell mirrors of slash commands

`omp login` ↔ `/login` · `omp share` ↔ `/share` · `omp join` ↔ `/join` · `omp commit` (no slash form) · `omp worktree` ↔ `/wt` · `omp ttsr` ↔ `/omfg` (generate) · `omp plugin …` ↔ `/marketplace`, `/plugins` · `omp agents unpack` ↔ `/agents` templates · `omp collab list|link` ↔ `/collab status`.

Not in omp:// docs (README-only claims elsewhere, do not rely on): `/review` P0–P3 verdict format, `omp commit` atomic split.

Source: omp://slash-command-internals.md · omp://session-operations-export-share-fork-resume.md · omp://session.md · omp://tree.md · omp://compaction.md · omp://models.md · omp://providers.md · omp://memory.md · omp://tools/todo.md · omp://context-files.md · omp://skills.md · omp://marketplace.md · omp://mcp-config.md · omp://agent-hub.md · omp://vibe-mode.md · omp://advisor-watchdog.md · omp://prewalk.md · omp://computer-use.md · omp://collab.md · omp://stream.md · omp://keybindings.md · omp://ttsr-injection-lifecycle.md · modules M01–M14 cheat sheets
