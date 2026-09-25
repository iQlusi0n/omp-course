# Module 2 — Coursework

All exercises run in `omp-course-lab`. Start from the checkpoint:

```sh
cd omp-course-lab && git checkout module-2-start && mkdir -p notes && omp
```

`notes/` is gitignored; that is where your evidence goes. Time box per exercise is in the heading. Each lesson in [`README.md`](README.md) also has its own short Walkthrough/Guided/Stretch; the four below are the module's graded coursework from the course outline.

Prerequisites: omp 18.3.1 logged in to one provider (Module 1); a terminal that passes `Ctrl+O` and `Ctrl+Shift+O` (check with `/hotkeys`); Python 3 on PATH (`python -m api` and `python -m unittest` are the only commands the lab needs).

---

## W1 — Read a turn (Walkthrough, ~15 min)

Goal: run one read-only turn, expand every card, and identify one `read`, one `grep`, and one `glob` card by shape.

1. Prompt exactly: `Explain how api/ handles a request. Read only; do not edit anything.`
   Expected: a spinner in the status line, then a mix of inline `🔍 Glob:` / `🔍 Grep:` lines and boxed `• Read …` cards, then prose. (If the model used only `read` cards, follow up with `Also show me where the word "month" is used in api/ and list the files under tests/` to force a `grep` and a `glob`.)
2. Press `Ctrl+O`.
   Expected: boxed cards expand to their full content; `… N more matches` folds under grep open.
3. Press `Ctrl+O` again, then `Ctrl+Shift+O` twice.
   Expected: cards collapse; then vanish; then return.
4. Write `notes/m2.md` with a section `## W1` containing three lines, one per card type, in this format:

   ```
   glob  | api/**/*.py            | inline | 5 files
   grep  | month in api           | inline | 7 matches · 3 files
   read  | api/server.py:14-60    | boxed  | 47 lines
   ```

**Pass condition:** `notes/m2.md` has a `## W1` section with a `glob`, a `grep`, and a `read` row whose arguments match the cards in your transcript (check by expanding the card with `Ctrl+O`).

**Guided variant (if the walkthrough felt easy):** add the *order* of every card in the turn and mark which ones the model called in parallel (they appear in the same assistant message, one after another with no prose between). Pass: the section lists every card in order.

**Stretch:** run the same prompt headless with `omp -p --mode json "Explain how api/ handles a request. Read only." > notes/m2-turn.json` and confirm each card you listed corresponds to a `tool_execution_start` event in the JSON (Module 13 explains the format; here you only need `grep -c tool_execution_start notes/m2-turn.json` and compare the count with your list — `-p` has no UI, so `ask` never appears and no PTY is possible).

---

## G1 — Two-file fix with full accounting (Guided, ~25 min)

Goal: fix lab issue #2 (the bug that spans two files), recover any truncated output, watch the todo panel, and account for every tool call.

Hints:
- Read `docs/ISSUES.md` yourself first (`!cat docs/ISSUES.md` from the composer, or `omp read docs/ISSUES.md` outside) so you know the repro command.
- A prompt shape that works: outcome + acceptance + verification — *"Fix issue #2 from docs/ISSUES.md. Smallest safe change in the two files involved; add or update the regression test; run `python -m unittest discover -s tests` and show me the result. Ask before touching anything outside api/, cli/, tests/."*
- If the model plans, a `☑ Todo` card appears and the HUD above the composer tracks it; `/todo expand` to see all of it.
- Expand the `bash` test card (`Ctrl+O`) before believing "tests pass"; a failing run has `| Exit: 1` in its footer.
- To *force* a spill so you can practise recovery: after the fix, prompt `Run the suite with -v twice and also dump data/lab.sqlite as CSV in the same command` — anything > 50 KB of output. The card gets a truncation warning naming `artifact://<N>`.
- Then: `Read artifact://<N>:1-30 and tell me the first table name.`

Checkpoints:
- [ ] a `• Read docs/ISSUES.md…` card
- [ ] at least one `🔍 Grep:` card that lands in the *second* file
- [ ] two `✎ Edit:` cards (one per file) with `⟦+a/-r⟧` counts
- [ ] a `$ python -m unittest …` card whose footer has **no** `Exit:` entry
- [ ] a `☑ Todo` card and the HUD (if the model planned; if not, ask it to `todo init` a two-phase plan first and rerun)
- [ ] one `artifact://<N>` id from a truncated card, and a `• Read artifact://<N>…` card that shows plain numbers with no `#TAG`

**Pass condition:**
1. `git diff --stat` lists both files named in issue #2 (plus the test file).
2. `python -m unittest discover -s tests` exits 0 (`!python -m unittest discover -s tests; echo exit=$?` from the composer).
3. `notes/m2.md` has a `## G1` section listing the tool sequence in order, one line per card: tool name, one-line argument summary, and for edits the `+a/-r` count; plus the artifact id you read back.

**Stretch:** make one edit fail on purpose. Between the model's two edits, run `git checkout -- <first file>` from another terminal and continue. Pass: the transcript shows either a `✘ Edit` → `• Read` → `✎ Edit` sequence or an edit receipt with a `Warnings:` block, and `notes/m2.md` records which one you got.

---

## G2 — Named service through `proc://` (Guided, ~15 min)

Goal: start the lab API as a supervised service named `api`, prove readiness, inspect it through `proc://`, hit it, kill it, and prove the listing is empty.

Hints:
- The exact prompt from the outline works: `run the API as a service named api, ready on port 8080`. The model's call is `bash` with `{"command":"python -m api","name":"api","ready":{"port":8080}}`.
- `read proc://` and `read proc://api` are `read` calls — type them as prompts, or say "read proc://api".
- Stopping is a `write` to `proc://api/kill`; "stop the api service" is enough.
- The service outlives the turn, and even the session: `omp ps` in another terminal shows it; `omp ps stop api` also works.
- Both `launch.enabled` and `async.enabled` are `true` by default — if the `name` parameter is refused, run `omp config get launch.enabled`.

Checkpoints:
- [ ] `$ python -m api` card with footer `⟦Service: api | State: ready | Ready: yes | PID: <n>⟧`
- [ ] `ⓘ Proc jobs & services 0 jobs · 1 services` from `read proc://`
- [ ] `ⓘ Proc api ready · pid <n> · up <t>` with at least one server log line from `read proc://api`
- [ ] `!curl -s localhost:8080/users/1` returns JSON (or `python -c "import urllib.request as u;print(u.urlopen('http://localhost:8080/users/1').read())"` if curl is missing)
- [ ] `⏹ Proc kill api exited …`

**Pass condition:** the transcript contains the readiness card *and* a `read proc://` card after the kill that reports `0 services`; `omp ps --plain` in another terminal lists no `api`. Copy the readiness footer line into `notes/m2.md` under `## G2`.

**Stretch:** start it again, then prompt `Send a blank line to the api service's stdin, then read its logs` — a `write proc://api` with empty content sends Enter; `read proc://api` shows nothing changed (the server ignores stdin). Then `write proc://api/mode` with `session` so the service dies with the session; restart omp and confirm `omp ps` no longer lists it. Pass: `notes/m2.md` names the mode you set and the observed lifetime.

---

## S1 — Vim mode `ciw` (Stretch, ~10 min)

Goal: enable Vim editing mode and change one word of a draft with `ciw`.

Steps (no hints beyond these):
1. `omp config set tui.vimMode true` (or `/settings` → Interaction → Input → Vim Editing Mode). Restart omp.
2. Type a draft containing the word `users`; press `Esc`; navigate with `b`/`w`; `ciw`; type `orders`; `Esc`; `Enter`.

**Pass condition:** `omp config get tui.vimMode` prints `true`; the submitted prompt in the transcript contains `orders` where you typed `users`; and `notes/m2.md` under `## S1` notes what changed visually on `Esc` (border colour / mode text).

Reset afterwards unless you like it: `omp config reset tui.vimMode`.

---

## Module pass checklist

| Item | Evidence |
|---|---|
| W1 | `## W1` in `notes/m2.md` with glob/grep/read rows matching the transcript |
| G1 | both #2 files in `git diff --stat`; suite exits 0; tool sequence + artifact id in `## G1` |
| G2 | readiness footer copied to `## G2`; `read proc://` shows `0 services` after kill; `omp ps --plain` agrees |
| S1 (optional) | `tui.vimMode` = `true`; `ciw` replacement visible in a submitted prompt |

Stop the API service and `omp config reset tui.vimMode` before moving on. Module 3 starts from `module-3-start`, so leave your fix uncommitted or on a scratch branch — the orchestrator's checkpoint tag is what the next module expects.
