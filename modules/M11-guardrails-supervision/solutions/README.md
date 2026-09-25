# Module 11 — Instructor notes (solutions)

Files in this directory:

| File | Install as | Used by |
|---|---|---|
| `no-console-log.md` | `<repo>/.omp/rules/no-console-log.md` | 11-W1, 11-W3, Lesson 11.1 walkthrough |
| `no-bare-print.md` | `<repo>/.omp/rules/no-bare-print.md` | 11-W2, Lesson 11.1 guided task |
| `no-unverified-tests.md` | `<repo>/.omp/rules/no-unverified-tests.md` | 11-S2, Lesson 11.1 stretch |
| `WATCHDOG.md` | `<repo>/WATCHDOG.md` (or `<repo>/.omp/WATCHDOG.md`) | 11-G1, Lesson 11.2 walkthrough |
| `WATCHDOG.yml` | `<repo>/WATCHDOG.yml` | 11-G2 |

All three rule files were verified on `omp/18.3.1` with `omp ttsr test -r …` and `omp ttsr scan -r …`
(see `demos/11.1-ttsr-interrupt.md` Part A for the captured output). Verified outcomes:

- `no-console-log`: triggers on `--source text`, and on `--source tool --tool edit --path web/x.js`; does **not** trigger on `--path api/x.py` or `--source thinking`.
- `no-bare-print`: triggers on `print("hi", x)` under `cli/*.py`; does not trigger on `sys.stdout.write(...)`.
- `no-unverified-tests`: `omp ttsr test` never triggers (judge not called); `-v` prints the question; `omp ttsr scan` skips it.

## Stretch answers

**11-S1 (notes-backed windows).** `compaction.experimentalContextManagement: true`, restart if
`/tools` lacks the two tools. Fastest way to force a rollover without a huge task: ask the model to
write notes, then explicitly call `new_context`. The divider appears at the next safe tool-loop
boundary, so the model must make at least one more tool call. Evidence: `read history://current/full:1-40`
shows entries from before the divider; a `context_notes` read after it returns the latest revision.
If no divider appears, the four required tools (`context_notes`, `new_context`, `read`, `grep`) are not
all active — check `/tools` and any `--tools` restriction.

**11-S2 (judged rule).** `no-unverified-tests.md` is the answer. Key teaching points: `question:`
never interrupts; the `condition:` is only a prefilter; `ttsr.judge: auto` will not judge unless a
native judge model resolves — set `ttsr.judge on` for the exercise and warn that the chat model is
billed for it. Delivery is an aside after `message_end`, rendered from `ttsr-warning.md`.

**11-S3 (advised subagent).** Add `advisor: true` to the agent's frontmatter, or set it from the
`/agents` hub (Enter → advisor strip → on). The child's log is
`<session-artifacts>/<SubId>/__advisor.jsonl`. `/advisor status` in the parent only reports the
parent's advisors, so "main session unadvised" is shown by `/advisor status` reporting nothing active.

**11-S4 (guardrail plan).** Expected predicates (any three equivalent ones pass):

| `event.toolName` | `event.input` field | predicate |
|---|---|---|
| `edit` / `write` | `path` | starts with `generated/` |
| `bash` | `command` | contains `rm` **and** `data/lab.sqlite` |
| `bash` | `command` | contains `push --force` or `push -f` |

Paragraph must state: TTSR aborts the stream and retries with `<system-interrupt>`; the hook lets
the call reach dispatch and returns a tool error whose text is `reason`.

## Lesson 11.3 stretch (`--prewalk-into` cost comparison)

Any target lacking credentials produces
`Warning: prewalk disabled — no API key for <provider>/<id>` on stderr at startup and the session
runs unarmed — that is the required captured line. Costs come from `omp stats`; the exact figures
vary by provider, so grade on the presence of three rows with a cost and a tests-pass column.

## Grading shortcuts

- TTSR exercises can be graded offline: run the learner's `omp ttsr test` commands yourself.
- Advisor exercises: ask for `ls` of the session artifact directory (`__advisor*.jsonl` present) and the `/advisor status` output.
- Prewalk: ask the learner to quote the `Prewalk: switched to … after first edit call.` line and name the preceding edit card.
