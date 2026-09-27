# Module 3 — Instructor notes (not for learners)

Built against `omp/18.3.1`; audited against `omp/18.3.5` and the checked-in lab (2026-09-27). Fixture facts, confirmed against `omp-course-lab/docs/ISSUES.md` #3 and `tests/test_issues.py::Issue3CsvExport`: `cli/__main__.py::build_parser()` declares the `orders` subparser (today only `--month`; `--format {table,csv}`, default `table`, is added there); `cli/commands.py::cmd_orders()` renders the table and returns an exit code. The gated test asserts: exit 0; header row exactly `id,user_id,created_at,status,total_cents`; exactly 13 rows for `--month 2026-03` (12 orders + header — so **no summary line**); every `created_at` starts with `2026-03`; every `total_cents` is all digits; and `test_table_is_still_default` requires the default output to start with `id `. Gated test `LAB_ISSUE=3 python3 -m unittest tests.test_issues` → `FAILED (failures=1, skipped=18)` on `main`, `OK (skipped=18)` when fixed; full suite `python3 -m unittest discover -s tests` → `OK (skipped=20)`.

## What "good" looks like per exercise

### W — weak vs structured
- The weak run usually still produces a working flag; that is fine and *expected*. The teaching point is the transcript: zero `bash` cards, header order chosen by the model, "you can run it with…" instead of a run. If a learner's weak run happens to run tests, ask them what in the prompt caused it (nothing) — it was model discretion, which is the problem.
- Common structured-run failure: the model runs the gated test *after* editing but not before. Acceptable for the pass condition; point out that step 1 of Verification was skipped and have them add "Do not edit anything until you have shown the failing run."
- If the `@docs/ISSUES.md` mention does not expand (path does not resolve from omp's cwd), the run reads the file with a `read` card instead — equivalent outcome.
- Grading `notes/m3.md`: both sections present; Structured lists a passing `LAB_ISSUE=3` card after the edits; `git diff --stat` limited to `cli/` and `tests/`.

### 3.1 Guided (machine-checkable header)
Model acceptance line:
```
- `python3 -m cli orders --month 2026-03 --format csv | head -1` prints exactly `id,user_id,created_at,status,total_cents`
```
Pass evidence is the expanded `bash` card. If a learner writes "prints the right header", send them back — "right" is not checkable.

### 3.1 Stretch (test-first)
Prompt fragment that reliably yields two cards around the edits:
```
Verification: 1) Run `LAB_ISSUE=3 python3 -m unittest tests.test_issues` and show that it fails. Do not edit any file before this card exists. 2) Implement. 3) Run it again and show OK.
```

### 3.2 Guided (force the question)
Reliable phrasing: "Do not edit any file until you have asked me, with the ask tool, (a) which output format and (b) where the output goes." Pass is card order `read… → ask → edit…`. If the model asks in prose instead of an `ask` card, that also blocks nothing — the turn ends waiting for a reply — but the observable differs; accept prose only if the learner notes the difference (an `ask` card is a structured tool call with options; prose is a normal message). Headless `-p` sessions never have `ask` (omp://tools/ask.md).
Learner-facing README no longer names an example prompt beyond "export orders somewhere spreadsheet-friendly"; the phrasing above is the model answer if they need a nudge.

### 3.2 Stretch (budget)
`git diff --stat` summary line `N files changed, …`. Some models run `git diff --stat | tail -1`; either is fine as long as the number is in a card.

### 3.3 Guided (launch vs session level)
`omp --thinking low`, then `Shift+Tab` up to `high`. With `statusLine.compactThinkingLevel: false` the model segment reads `… · low` / `… · high` (setting description verified on the binary via `omp config get statusLine.compactThinkingLevel --json`). Remind learners to `omp config reset statusLine.compactThinkingLevel`.

### 3.3 Stretch / coursework S (`ultrathink`)
Key fact from omp://magic-keywords.md: on a fixed level, `ultrathink` adds only the hidden reasoning notice; only under `auto` does it also pick the model's highest effort for that turn. So:
- fixed level: both runs show the same level; the `ultrathink` run typically has a longer thinking block and more enumerated cases. Accept "same level, longer thinking, N vs M cases".
- `auto` (`omp --thinking auto`): the `ultrathink` turn shows a higher level (up to `max`; plain `auto` is capped at `xhigh` by `providers.autoThinkingMaxEffort`).
- A learner who reports the level changed on a fixed level either mis-read the icon or was on `auto`; check.
- Verify the keyword was live: gradient in the composer, `omp config get magicKeywords.ultrathink` → `true`, lowercase standalone word (not in backticks).

Exact task text for coursework S (learners get only the goal; hand this out if they cannot come up with a hard enough question). Send it once verbatim, then once more with `ultrathink` prepended as a standalone word:
```text
List every way the csv branch in cli/commands.py could produce a malformed row for real data in data/lab.sqlite (commas, quotes, newlines, None, unicode, float totals). For each, say whether the current code handles it and cite the line.
```
Setup for the `auto` run: `omp --thinking auto` plus `statusLine.compactThinkingLevel: false` so the level prints as text (`omp config reset statusLine.compactThinkingLevel` afterwards). Confirm the keyword is live (gradient in the composer, `omp config get magicKeywords.ultrathink` → `true`); `Ctrl+T` shows the thinking blocks.

### G1 — Esc / steer / follow-up
- Fast models may finish the narrower turn before any tool boundary; then the steer arrives as a normal next prompt. That is acceptable for checkpoint 2 only if the learner explains why (no boundary reached). The pass condition is the follow-up ordering, which is deterministic: the `Ctrl+Q` message runs after the turn's final message.
- Windows Terminal: `Ctrl+Enter` is swallowed; `Ctrl+Q` works. If a learner's `keybindings.yml` already maps `Ctrl+Q`, follow-up stays on `Ctrl+Enter` only (omp://keybindings.md).
- Double-`Esc` on an empty editor opens the rewind selector (`doubleEscapeAction: rewind`). Learners who "lost the screen" pressed it; `Esc` closes.
- `interruptMode` default `immediate`; `wait` defers steering to turn end (omp://rpc.md mode semantics; omp://settings.md Interaction). Reset with `omp config reset interruptMode`.
- Example texts for the coursework G1 checkpoints (learners get descriptions only): broad task *"For every function in cli/ and api/, read the file and write a one-line description into notes/functions.md."*; narrower *"Only cli/ …"*; steer `Now also note which functions call print()`; api turn *"Do the same for api/ into notes/functions-api.md"*; follow-up `Run git status --short and show the output` via `Ctrl+Q`.
- Example texts for the Lesson 3.4 Guided task: steer `Stop — only change the csv branch, leave table rendering alone.`; follow-up `Run LAB_ISSUE=3 python3 -m unittest tests.test_issues and show the output.` via `Ctrl+Q`.

### G2 — `/btw`
- Proof of isolation: the main session, asked "what was the last question I asked you", must not mention the side question; BTW records are not appended to the main transcript nor sent as history (omp://slash-command-internals.md §11).
- `b` promotes a completed single-turn answer to a branch only when the main session is idle and the leaf is unchanged; if a learner tries it after another main prompt, it is refused by design.
- History lives in `btw-history/` under the session artifact directory; `--no-session` keeps it in memory only; `/export` and `/share` exclude it.
- One request at a time: a second `/btw` while the first streams is refused, not queued.
- Example texts for G2: `/btw What does <function> in cli/commands.py do, and who calls it?`; isolation check to the main session: `Without using tools: what was the last question I asked you in this conversation?`

### 3.4 Stretch (`interruptMode wait`)
Steps (the learner README states only the goal and pass): `omp config set interruptMode wait`, then repeat Lesson 3.4 walkthrough step 2 (steer while cards stream); the message is acknowledged only after the turn ends. Confirm the learner ran `omp config reset interruptMode` (pass includes `omp config get interruptMode` → `immediate`).

### 3.5 Guided / Stretch
- Any sentence containing "should" is a candidate. Pass requires a new card; a refutation counts as much as a confirmation.
- Stretch: the first answer to "Did the tests pass?" is typically a hedge ("they should"). The forced run may fail if quoting was implemented sloppily — that is the ideal outcome for the lesson.
- Stretch prompts (learner README gives only the goal): first `Implement issue #3's quoting follow-up but do not run any tests; just report when done.`, then `Did the tests pass?`, then force the run with `Run LAB_ISSUE=3 python3 -m unittest tests.test_issues now and show the output.`

## Running the walkthroughs live
- Use a clean profile: `omp --profile course-build`. Keybindings inherit from the default profile; settings do not.
- A `/fresh` on an idle session prints a pruned-entries count; if a learner sees a refusal, they were still streaming — `Esc` first (omp://session-operations-export-share-fork-resume.md, Fresh).
- `/pause` resumes on `Ctrl+C`; warn learners before they try to "cancel" from the pause screen.
