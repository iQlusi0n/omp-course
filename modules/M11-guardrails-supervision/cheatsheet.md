# Module 11 cheat sheet — Guardrails & Supervision (`omp/18.3.1`)

## TTSR (on by default; rules opt-in per file)
| What | Where / value |
|---|---|
| Rule files | `<cwd>/.omp/rules/*.md` · `~/.omp/agent/rules/*.md` · name = filename |
| Regex trigger | `condition: "console\\.log"` (list = any; `(?i)` ok; glob-looking values become edit/write scope) |
| AST trigger | `astCondition: "print($$$ARGS)"` — edit/write streams only, language from path |
| Judged trigger | `question: "…yes/no…"` — judge role after output; never interrupts; `ttsr.judge auto\|on\|off` |
| Scope | `scope: "text, thinking, tool, tool:edit(web/*.js)"` — default `text`+`tool` |
| Extra gates | `globs: [...]` (path) · `agents: [main, scout, "foreman-*"]` |
| Interrupt | `interruptMode: always \| prose-only \| tool-only \| never` (rule overrides `ttsr.interruptMode`) |
| Injection | `<system-interrupt reason="rule_violation" rule= path=>` (abort + retry) · `<system-reminder …>` (prepended to tool result) |
| TUI | `Injecting rule: <name>` card, `ctrl+o` expands |
| Persisted | `custom_message` `customType: "ttsr-injection"` · `ttsr_injection` entry (restored on resume) |
| Settings (defaults) | `ttsr.enabled=true` · `interruptMode=always` · `contextMode=discard` · `repeatMode=once` · `repeatGap=10` · `builtinRules=true` · `disabledRules=[]` · `judge=auto` |
| Generate | `/omfg <complaint>` |
| CLI | `omp ttsr list` · `omp ttsr test [-r rule.md] [--source text\|thinking\|tool] [--tool edit] [--path p] [--agent a] [--file -] [-v] [--json] '<snippet>'` · `omp ttsr scan [dir] [-r rule.md] [-v] [--no-gitignore] [--max-bytes n]` |
| Exit codes | unreliable for CI: `scan` exits 0 either way; `test` exits 0 on no-trigger with project rules loaded (only `-r` mode exits 1) — grep for `Triggered (` / `Found violations/matches`; run from repo root (scope globs are root-relative) |

## Advisor / watchdog (off by default)
| What | Where / value |
|---|---|
| Enable | `modelRoles.advisor: <provider/id[:level]>` (config.yml or `/model` Roles view; `modelRoles` is a record — `omp config set modelRoles.advisor` is not a key) + `advisor.enabled: true` · session: `/advisor on` · headless: `omp -p --advisor` |
| Commands | `/advisor [on\|off\|status\|dump [raw]\|configure]` |
| Default tools | `read`, `grep`, `glob` (isolated `-advisor` tool session; approvals still apply) |
| Severities | `nit` aside · `concern` steer (card if after terminal answer) · `blocker` steer |
| Transcript marker | `<advisory advisor="Name" severity="concern" guidance="weigh, don't blindly obey">` |
| `WATCHDOG.md` | advisor-only priorities; `~/.omp/agent/WATCHDOG.md`, `<dir>/WATCHDOG.md`, `<dir>/.omp/WATCHDOG.md` up to repo root — all load; `@` imports |
| `WATCHDOG.yml` | `instructions`, `maxNotesPerUpdate`, `advisors[]: name, enabled, model, tools, instructions` |
| Tuning (defaults) | `advisor.immuneTurns=3` · `advisor.maxNotesPerUpdate=4` · `advisor.syncBacklog=off\|1\|3\|5` · `tier.advisor=none` · `retry.fallbackChains.advisor` |
| Subagents | frontmatter `advisor: true\|"model"` · `task.agentAdvisor: {agent: on\|off\|pattern}` · `/agents` hub |
| Logs | `<session>/__advisor.jsonl` · `__advisor.<slug>.jsonl` · `<SubId>/__advisor*.jsonl` · Agent Hub `advisor` rows · `omp stats` |

## Prewalk (off by default)
| What | Where / value |
|---|---|
| Enable | `prewalk.enabled: true` · `--prewalk` · `--prewalk-into <model\|@role>` · `--no-prewalk` |
| Gate | plan nudge → successful `todo` → first completed `edit`/`write` → switch to `@smol` (one-shot) |
| In session | `/prewalk` (arm) · `/prewalk restart` (back to `@default`, re-arm) — no `status` subcommand |
| Notices | `Prewalk: armed for …` · `Prewalk: injected deep-plan nudge.` · `Prewalk: switched to … after first edit call.` · status-line `prewalk active` |
| Subagents | frontmatter `prewalk: true\|"@smol"` · `task.prewalk` (bundled `task`, default false) · `task.agentPrewalk` |

## Extension guardrail (preview → Module 12)
| What | Where / value |
|---|---|
| Handler | `pi.on("tool_call", async (event, ctx) => ({ block: true, reason: "…" }))` — throw = blocked |
| Extras | `input` rewrite (non-blocking, last-wins) · `additionalContext` |
| Files | `<cwd>/.omp/hooks/pre/*.ts` · `.omp/hooks/post/*.ts` · `~/.omp/agent/hooks/pre\|post/` · `--hook`/`-e <file>` |
| Events | `ttsr_triggered` · `before_subagent_spawn` (`block`) · `session_stop` (`decision: "block"`) |

## Long-running context
| What | Where / value |
|---|---|
| Notes-backed windows | `compaction.experimentalContextManagement: true` (default false) · `/settings` → Context → Compaction |
| `context_notes` | read (no `text`) · replace (`text`) · clear (`text: ""`) · ≤ 16,384 bytes · latest revision injected |
| `new_context` | `{}` → `New context window requested.` → rollover at next safe boundary, no summariser |
| Raw history | `history://current/full[:1-200 \| :raw:1-200]` via `read`/`grep` |
| Extended window | `/extended-context [on\|off\|status]` · `extendedContext=false` · `maxContextWindow` in `models.yml` |
| Alternatives | `/compact [focus]` · `/handoff [focus]` (in-place compaction entry) · `checkpoint`/`rewind` (`checkpoint.enabled`) |
| Compaction defaults | `methodOrder=[remote, snapcompact, handoff, shake, soft]` · `keepRecentTokens=20000` · `handoffSaveToDisk=false` |
