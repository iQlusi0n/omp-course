# Module 11 — Build notes

Built against `omp/18.3.1` (`/home/user/.local/bin/omp`). Build machine: Python 3 only, no model
credentials usable for live sessions, no recordings. All TUI demos are reconstructions labelled as
such; the CLI portions of `demos/11.1-ttsr-interrupt.md` are captured verbatim.

## Sources read this session

`omp://` index, `omp://rulebook-matching-pipeline.md`, `omp://ttsr-injection-lifecycle.md`,
`omp://advisor-watchdog.md`, `omp://prewalk.md`, `omp://compaction.md`, `omp://tools/context-notes.md`,
`omp://tools/new-context.md`, `omp://settings.md` (models/advisor/extended-context sections),
`omp://cli-reference.md` (prewalk/advisor flags), `omp://task-agent-discovery.md`, `omp://tools/todo.md`,
`omp://extensions.md`, `omp://hooks.md`, `omp://agent-hub.md`, `omp://session.md`,
`omp://blob-artifact-architecture.md`, `omp://handoff-generation-pipeline.md`, `omp://tools/checkpoint.md`,
`omp://tools/rewind.md`, `omp://models.md`; `omp --help`, `omp ttsr --help`, `omp config list`,
`omp config get <key>` for every default quoted. UI notice strings (`Injecting rule:`, `Prewalk: …`,
`Advisor enabled.`, `Usage: /advisor …`, `Usage: /prewalk [restart]`, `Usage: /extended-context …`,
`Usage: /omfg <complaint>`, `<advisory … guidance="weigh, don't blindly obey">`, the `context_notes`
result/error strings, `── 📷 compacted · ctrl+o ──`) were extracted from the binary.

## Deviations from the outline (doc wins)

1. **Outline 11.1: "amber 'Injecting rule' card".** The card text `Injecting rule: <name>` is verified;
   the *colour* is not documented anywhere. Lessons say "`Injecting rule: <name>` card" without a colour.
2. **Outline 11.1: "survives compaction".** Docs say the fired-rule *suppression state* is persisted
   (`ttsr_injection` entries, restored on resume); the rule file is re-read at session start. Worded
   that way rather than as a property of the rule itself.
3. **Outline 11.3 coursework: "`/prewalk` status shows fired".** `/prewalk` has no `status` subcommand
   (`Usage: /prewalk [restart]` verified). Pass condition rewritten to the `Prewalk: switched to …
   after first edit call.` notice and the model-chip change.
4. **Outline 11.2: "per-subagent `advisor:` in frontmatter".** Covered, plus the `task.agentAdvisor`
   override documented in `task-agent-discovery.md` (not in the outline).
5. **Outline 11.5: notes-backed tools and restart.** `settings.md`/tool docs say toggling adds the tools
   to the running session; `compaction.md` says restart to refresh the roster. Lesson says both and
   tells the learner to `/restart` if `/tools` lacks them.
6. **Outline 11.1 coursework W: `condition: "console\\.log"` only.** Solution rule adds
   `scope: "text, tool:edit(web/*.js), tool:write(web/*.js)"` so the walkthrough's negative test
   (`--path api/server.py`) demonstrates scope; the `condition` and `interruptMode: always` are as specified.

## Claims dropped as unverifiable

- Colour of any TUI card (amber/red) — not documented.
- Exact rendering of the advisor status table and `/extended-context status` line — not documented;
  demos mark those lines illustrative.
- Whether `omp ttsr scan` returns a non-zero exit on matches — observed **0 both ways** on 18.3.1, so
  the lesson tells learners to grep the output in CI rather than rely on exit codes.

## Observed on the live binary (not in docs)

- `omp ttsr test` exit code: 0 when a rule triggered, 1 when none.
- `omp ttsr scan` header reports `rules=29` when `list` reports 30 — question rules are skipped
  (consistent with `ttsr-injection-lifecycle.md` §10).
- Scope path globs are resolved relative to the `test`/`scan` root: running `scan` from inside `cli/`
  yields `no-relevant-rules` for a `tool:edit(cli/*.py)` rule. Lesson and 11-W2 step 4 teach this.
- `omp config list` on this machine shows 27 `builtin-defaults` TTSR rules (Go/Rust/TS only).

## Features covered vs Appendix C

| Row | Status |
|---|---|
| TTSR rules, `/omfg`, `omp ttsr` | covered (11.1) |
| Advisor/watchdog (default off) | covered (11.2); `advisor.enabled` default `false` called out |
| Prewalk (default off) | covered (11.3); `prewalk.enabled` default `false` called out |
| Notes-backed context, `/extended-context` (off, experimental) | covered (11.5); both defaults `false` called out |
| `checkpoint`/`rewind` (also in M9) | referenced in 11.5 decision table with `checkpoint.enabled` default `false` |
| Extension `tool_call` block (M12 row) | previewed in 11.4 only; build is M12 |

## Not exercised on this machine

- No live model session: TTSR interrupt, advisor notes, prewalk hand-off, and `new_context` rollover
  were not observed end-to-end here. Walkthroughs are written from the documented lifecycle and the
  verbatim notice strings; Appendix D step 4 (run every walkthrough in `--profile course-build`) must be
  done by the orchestrator/instructor on a machine with credentials.
- Lab fixtures (`web/signup.js`, `cli/main.py`, issue #8 contents) were referenced by Appendix A paths
  and generic descriptions; the exact seeded lines were not read (lab built in parallel).
