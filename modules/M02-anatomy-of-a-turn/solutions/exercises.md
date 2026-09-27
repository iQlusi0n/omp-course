# Module 2 — Instructor notes and solutions

Not for learners. Covers `exercises.md` (W1, G1, G2, S1) and the per-lesson Stretch items in `README.md`.

## W1 — Read a turn

Typical transcript for `Explain how api/ handles a request. Read only; do not edit anything.`:

1. `glob api/**/*.py` (inline) — sometimes skipped if the model reads `api` as a directory first (`• Read api` shows the tree). The lab's `api/` holds `__init__.py`, `__main__.py`, `db.py`, `server.py`.
2. `read api/__main__.py` or `read api/server.py` (boxed; `server.py` is 177 lines, so it comes back as a structural summary with `…` and a `[…NNln elided…]` footer — files ≥ 100 lines).
3. `grep do_GET|do_POST|BaseHTTPRequestHandler` (inline; hits `api/server.py`).
4. `read api/server.py:<range>` for the `_get` dispatcher / `_list_orders` body (boxed).
5. Possibly `read api/db.py` (130 lines — also summarized).

Grading: the three rows must match *their* transcript, not this list. Common mistake: listing `• Read api` (directory) as a `glob`. Directory reads are `read` cards; `glob` is always the inline `🔍 Glob:` line.

Stretch (`-p --mode json`): the count of `tool_execution_start` events equals the number of cards in the interactive run only if the model took the same path; accept ±2 and ask the learner to explain the difference (models vary turn to turn). `ask` cannot appear in `-p`.

## G1 — Two-file fix

Issue #2 files per `docs/ISSUES.md`: `api/server.py` (`_list_orders` computes `offset = page * db.PAGE_SIZE`; page 1 must start at offset 0) and `api/db.py` (`list_orders` binds `args += [offset, limit]` against `LIMIT ? OFFSET ?` — the two are swapped). Fixing only one file leaves the gated test red. Verify with `git diff --stat` (both files) and `LAB_ISSUE=2 python3 -m unittest tests.test_issues` (exit 0); the normal suite `python3 -m unittest discover -s tests` must stay green (`Ran 48 tests … OK (skipped=20)`).

Grading the tool sequence: it must contain, in order, at least `read docs/ISSUES.md` → (`grep` or `read` that reaches the second file) → `edit` × 2 → `bash LAB_ISSUE=2 python3 -m unittest …`. `todo` cards are optional unless the learner's prompt asked for a plan; if absent, the learner should have asked for one (the checkpoint says so).

Artifact recovery: the id is session-local; if the learner reports `Artifact N not found. Available: …` they read it from a different session — that is acceptable evidence that they understand ids are per-session. The `• Read artifact://N` card must show *no* `#TAG` (immutable) — ask the learner why.

Forcing a spill on a small repo: `python3 -m unittest discover -s tests -v` is well under 50 KB, and `data/lab.sqlite` (12 users, 72 orders) dumps small too. The reliable trigger is `python3 -c "for i in range(3000): print(i, 'x' * 40)"` (≈ 140 KB). Any > 50 KB output works.

Stretch (deliberate stale tag): `git checkout -- <file>` between edits reverts the model's first edit, so the second edit's tag no longer matches. Two valid outcomes: recovery with a `Warnings:` block (when the region the model targets is unchanged) or a refusal followed by a re-read. Either is a pass; what matters is that the learner saw the transcript pattern and did not get a silently wrong edit.

## G2 — Named service

Correct call: `{"command":"python3 -m api","name":"api","ready":{"port":8080}}`. Readiness footer `⟦Service: api | State: ready | Ready: yes | PID: <n>⟧`. The server's first log line is `omp-course-lab API v1 1.0 listening on http://127.0.0.1:8080 (db: …)`.

Failure modes and what to tell the learner:
- `State: failed — process exited before readiness` → port 8080 in use (a previous run). `omp ps` from another terminal, `omp ps kill api`, or `!fuser -k 8080/tcp`.
- Readiness times out at 30 s but the server is up → the lab server binds `127.0.0.1:8080` (`api/__main__.py` defaults); `ready.host` defaults to `127.0.0.1`, so this should not happen unless they changed the port. Check `read proc://api` for the actual bind line.
- The model used `async: true` instead of `name` → it's a job, not a service; `read proc://` shows `1 jobs · 0 services`. Ask them to re-prompt with "as a service named api".
- `name` parameter refused → `launch.enabled` false or a non-launch-capable session; `omp config get launch.enabled`.

Kill evidence: `⏹ Proc kill api exited · pid <n> · ran <t>` then `read proc://` → `0 jobs · 0 services`. `omp ps --plain` in another terminal must agree (the broker is project-scoped and outlives the session).

Stretch: `write proc://api` with empty content sends Enter; the http.server ignores stdin so logs don't change — that's the expected observation. `write proc://api/mode` with `session` makes the service die with the session; `persist` (default shown as `persistent` in the listing) keeps it; `detached` restarts it without a PTY and persists beyond the broker.

## S1 — Vim `ciw`

`tui.vimMode: true` → Insert on entry. `Esc` → Normal; border colour changes; with `tui.vimModeDisplay: text` the mode name is shown. `b`/`w` reach the word; `ciw` deletes inside-word and enters Insert; `Esc`; `Enter` submits from Normal. `omp config get tui.vimMode` → `true`.

Common confusion: pressing `Esc` once from Insert while a turn runs does *not* interrupt — it switches to Normal. Second `Esc` interrupts. `Up` in Normal is `k`, not history.

## Per-lesson Stretch answers (README)

- **2.1** Remap: `~/.omp/agent/keybindings.yml` → `app.tools.expand: Ctrl+E`. `/hotkeys` reflects it after restart. Remind them to delete the line.
- **2.2** Grep page boundary: `def ` only matches in 14 of the lab's files, so it will *not* cross the 20-file page. Use `.` (any non-empty line) over the whole repo — 36 tracked text files. The first card's text ends `Use skip=20 for the next page`; the follow-up call has `skip: 20`.
- **2.3** Block edit: the receipt (expanded card) includes a block-resolution line; the model's payload uses `PUT N*:` anchored at the `def` line. If the model used an explicit range instead, that is not a failure of the learner — ask them to request "as a single block anchored at the def line" once more.
- **2.4** PTY: the `Console` overlay appears only in the TUI with `PI_NO_PTY` unset. `Esc` kills the PTY; the resulting card shows the captured output. Under `--no-pty` the card carries `pty requested but unavailable in this environment; ran without a terminal` — accept that as the pass.
- **2.5** Cancelling `ask` with `Esc` aborts the tool context and the turn; the card is marked cancelled and no further cards follow until the next prompt.
- **2.6** Vim `V` + `d` deletes the line; `u` undoes; `ciw` as above. `omp config get tui.vimMode` → `true`.

## Time and model notes

Whole module fits 90 min with a fast model; `ask`/`todo` usage is model-dependent — Sonnet-class models use `ask` when told to; smaller models may answer in prose. The phrasing "use the ask tool" in the prompt is deliberate. All settings this module changes (`tui.vimMode`, `bashInterceptor.enabled`, `ask.timeout`, `ask.notify`) should be reset with `omp config reset <key>` at the end.
