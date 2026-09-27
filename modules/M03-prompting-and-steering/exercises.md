# Module 3 — Coursework

Built against `omp/18.3.1`. Work in `omp-course-lab`; start from `git checkout module-3-start`. Every result goes in `notes/m3.md` (the `notes/` directory is gitignored). Each exercise names its **pass condition**; check it before moving on. Time: ~50 min total.

Fixture: `docs/ISSUES.md` **#3** — *CLI: `orders` has no `--format csv` (export for spreadsheets)* (`cli/__main__.py`, `cli/commands.py`). Repro today: `python3 -m cli orders --month 2026-03 --format csv` → `error: unrecognized arguments: --format csv`, exit 2. Expected: `--format {table,csv}` (default `table`); CSV via the `csv` module with header `id,user_id,created_at,status,total_cents`, one row per order, integer `total_cents`, no summary line; table output unchanged. Gated test: `LAB_ISSUE=3 python3 -m unittest tests.test_issues` (`FAILED (failures=1, skipped=18)` before, `OK (skipped=18)` after). Full suite: `python3 -m unittest discover -s tests` (`OK (skipped=20)`).

Prerequisite keys from Module 2: `Ctrl+O` (expand card), `Ctrl+Shift+O` (hide/show cards), `!cmd`, `@path`.

---

## W — Weak prompt, then structured prompt, on issue #3   (~20 min)

**Goal:** Drive the same task twice and compare the transcripts, not the diffs.

Steps (exact):
1. `git checkout module-3-start && omp`
2. Send exactly: `add csv output to the orders command`. If it asks a question, answer in one word. Wait for the turn to end.
3. Count and record under `## Weak` in `notes/m3.md`:
   - number of tool cards (`Ctrl+Shift+O` twice if they are hidden);
   - number of `bash` cards, and whether any ran a test command;
   - `!git diff --stat` output;
   - `!LAB_ISSUE=3 python3 -m unittest tests.test_issues` → `OK` or `FAILED`.
4. `!git stash push -u -m m3-weak`; quit (`Ctrl+C` twice); `omp`.
5. Send the structured prompt from `README.md` Lesson 3.1 **Concepts** (paste it, or save it as `notes/prompt-issue3.md` and send `@notes/prompt-issue3.md`).
6. Record the same four items under `## Structured`, plus the order of `bash` cards (which command, exit 0 or not).

**Expected shape (structured):** an error-marked test card *before* any `edit`, then `edit` cards in `cli/`, then passing test cards, then the repro command with `id,user_id,created_at,status,total_cents` as its first output line, then a per-file receipt.

**Pass:** `notes/m3.md` has both sections; the Structured section shows ≥ 1 `bash` card running `LAB_ISSUE=3 python3 -m unittest tests.test_issues` with exit 0 *after* the edits, and `!git diff --stat` lists only `cli/` and `tests/` paths.

---

## G1 — Interrupt with `Esc`, redirect scope, queue a follow-up with `Ctrl+Q`   (~15 min)

**Goal:** Correct a running turn without restarting, then queue work for after it.

Hints:
- Use a task with many tool calls so there are boundaries to steer at: e.g. *"For every function in cli/ and api/, read the file and write a one-line description into notes/functions.md."*
- Steer = type + `Enter` while it runs (`interruptMode: immediate` is the default; check with `omp config get interruptMode`).
- Follow-up = type + `Ctrl+Q` (or `Ctrl+Enter`; Windows Terminal needs `Ctrl+Q`). `Alt+Up` pulls it back.
- `Esc` once aborts; `Esc` twice on an empty editor opens the rewind selector — close it with `Esc`.

Checkpoints:
1. Start the task. While `read` cards are appearing, press `Esc`. The turn stops; the partial transcript stays.
2. Send a narrower version (*"Only cli/ …"*). While it runs, type `Now also note which functions call print()` and press `Enter` → it is delivered at a tool boundary and acknowledged before the turn ends.
3. Start one more turn (*"Do the same for api/ into notes/functions-api.md"*). While it runs, type `Run git status --short and show the output` and press `Ctrl+Q`. A queued indicator appears; the turn is not interrupted.

**Pass:** after the api/ turn ends, the follow-up runs on its own: a `bash` card with `git status --short` appears *after* the api/ turn's final message, and its output lists `notes/functions.md` and `notes/functions-api.md` as untracked. Record the card order in `notes/m3.md` under `## G1`.

---

## G2 — `/btw` without polluting the main thread   (~10 min)

**Goal:** Ask "what does this function do?" and prove the main transcript did not change.

Hints:
- Pick any function in `cli/commands.py`. Send `/btw What does <function> in cli/commands.py do, and who calls it?`
- The answer opens in a panel: `c` copies, `Esc` closes. Bare `/btw` opens history.
- Proof that the main thread is untouched: the next main prompt must not "know" about the side question. Ask the main session: `Without using tools: what was the last question I asked you in this conversation?`

Checkpoints:
1. The `/btw` panel shows an answer that references the current session (it can see your issue #3 work).
2. `/btw` (bare) lists your question; `Esc` closes history.
3. The main-session answer names your last *main* prompt, not the side question.

**Pass:** the main transcript contains no user message with your `/btw` question, and the main session's answer to "last question I asked" is a main-thread prompt. Paste both the side answer (copied with `c`) and the main answer into `notes/m3.md` under `## G2`.

---

## S — With and without `ultrathink`   (~15 min)

**Goal:** Run one hard analysis twice and record how thinking changed.

Task text (use verbatim, then once more with the word `ultrathink` prepended as a standalone word):

> `List every way the csv branch in cli/commands.py could produce a malformed row for real data in data/lab.sqlite (commas, quotes, newlines, None, unicode, float totals). For each, say whether the current code handles it and cite the line.`

Setup notes:
- On a fixed level (the default `high`), `ultrathink` adds the reasoning notice only. To also see the *level* move, start a session with `omp --thinking auto` and set `statusLine.compactThinkingLevel: false` so the status line prints the level as text (`omp config reset statusLine.compactThinkingLevel` afterwards).
- Confirm the keyword is live: the word must show a gradient in the composer; `omp config get magicKeywords.ultrathink` → `true`.
- `Ctrl+T` shows the thinking blocks.

**Pass:** `notes/m3.md` has a `## S` table with, for each run: level shown in the status line during the turn, approximate thinking-block length (lines), number of distinct failure modes listed, and whether each was backed by a cited line. On `auto` the `ultrathink` run shows a higher level than the plain run; on a fixed level the two show the same level and you say so.

---

## Turn-in

`notes/m3.md` with sections `## Weak`, `## Structured`, `## G1`, `## G2`, `## S`. Leave the working tree with the structured issue #3 change in place (Module 4 starts from `module-4-start`, so nothing here needs committing).
