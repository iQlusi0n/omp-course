# Module 5 — Coursework

Start point: `cd omp-course-lab && git checkout module-5-start`. All outputs go to `notes/` (gitignored). Time per exercise is in brackets. Every exercise has an observable pass condition — collect the evidence in `notes/m5.md`.

Prerequisites: a logged-in model (Module 1). A vision-capable model is needed only for the `snapcompact` comparison in G2. No LSP (language-server code intelligence, Module 8), debugger, or browser required except to *open* the exported HTML / share link.

Conventions: keys are shown as `Ctrl+O`; slash commands are typed in the composer and submitted with Enter; `!cmd` runs a shell command from the composer.

---

## W1 — Tree, label, branch, fork  [20 min]  *(Walkthrough)*

Goal: run three turns, navigate the tree, label, jump back with a summary, then `/branch` and `/fork` from the same point, and identify all three in `/resume`.

1. `omp` → `/rename m5-w1`.
   Expected: `Session renamed to "m5-w1".`
2. Turn 1: `Read cli/__main__.py and summarize its subcommands in one line. No edits.`
   Turn 2: `Which of those subcommands reads data/lab.sqlite? One line, no edits.`
   Turn 3: `List the files under tests/. Filenames only, no edits.`
   Expected: three answers, at least two `read` cards.
3. `omp config set branchSummary.enabled true` from a second shell (or `!omp config set branchSummary.enabled true`).
   Expected: `✔ Set branchSummary.enabled = true`.
4. `/tree`. Press `Up` until the cursor `›` is on `user: Which of those subcommands…` (turn 2). `Shift+L`, type `turn2`, Enter.
   Expected: the row reads `[turn2] user: Which of those…`.
5. Press `Enter` on that row → chooser `Summarize branch?` → `Summarize`.
   Expected: loader, then `⑂ branch · ctrl+o` divider and `Navigated to selected point`; the composer holds turn 2's text.
6. Replace the composer text with `Instead: which subcommand has the most CLI arguments? One line, no edits.` and submit.
   Expected: an answer. `/tree` now shows turn 3 hanging off a side branch and your new prompt on the bulleted path, with the `[turn2]` label still on the old user row.
7. `/fork`.
   Expected: `✔ Session forked to <timestamp>_<id>.jsonl`.
8. `/branch` → `Left` (previous user turn) → `Enter`.
   Expected: `Rewound to selected point`; the prompt is back in the composer. Press `Ctrl+C` to clear it, then submit `Say BRANCHED.`
9. `/resume`.
   Expected: the picker lists the original `m5-w1` and the fork (marked `⑂ fork`, `current`). Note whether a third file exists: `!ls ~/.omp/agent/sessions/-*omp-course-lab*/ | grep -c jsonl`.
10. `omp config set branchSummary.enabled false` to restore the default.

**Pass:** `notes/m5.md` contains (a) the count of `.jsonl` files from step 9, (b) one sentence each on the scope of `/tree` (same file, leaf move), `/branch` (rewind selector; user target may create a new file), `/fork` (whole copy, new id, `parentSession`), and (c) the label name you set.

---

## W2 — The five resets  [10 min]  *(Walkthrough)*

1. In any session: `Remember the word PINEAPPLE. Reply OK.` → `OK`.
2. `/fresh` → `Fresh provider session started (N provider states pruned).` Then `What word did I ask you to remember?` → `PINEAPPLE`.
3. `/clear` → `✔ Context reset — N messages dropped; session continues.` Same question → the model does not know.
4. `!grep -c reset_boundary "$(ls -t ~/.omp/agent/sessions/-*omp-course-lab*/*.jsonl | head -1)"` → `1`.
5. `/new`, one turn, then `!ls -t ~/.omp/agent/sessions/-*omp-course-lab*/*.jsonl | head -2` → two files.
6. `/delete` → the newer file from step 5 is gone; you are in a new empty session.

**Pass:** step 4 prints `1`; step 6's file no longer exists; `notes/m5.md` has one line per command stating what survived (file / transcript / model context).

---

## G1 — Force auto-compaction, then hand off  [15 min]  *(Guided)*

Goal: drive context past the threshold with large reads, watch auto-compaction, then `/handoff "focus on the API refactor"`, and find the compaction entries in `/tree`.

Hints:
- Default thresholds on large-window models are far away; set a fixed trigger: `omp config set compaction.thresholdTokens 30000` (writes the global config; for a lab-only override edit `omp-course-lab/.omp/config.yml` by hand). Check with `omp config get compaction.thresholdTokens`.
- Big input: one prompt that asks omp to read `docs/spec.md` and every file under `api/` and `cli/` in full, and tells it not to summarize (exact wording in `solutions/`).
- The divider looks like `── 📷 compacted · ctrl+o ──` and sits where compaction fired. `Ctrl+O` on it expands the summary.
- `/handoff` refuses while streaming and prints `Nothing to hand off (already compacted)` if the kept tail is all that is left — do a turn or two of work between the auto-compaction and the handoff.
- In `/tree`, type `compact` to find the `compaction` entries on the active path (`Alt+A` shows every bookkeeping entry as well).

Checkpoints:
- `context_pct` on the composer border rises above the threshold during the read turn, then drops after the divider appears.
- `/handoff "focus on the API refactor"` prints `Context handed off and compacted in place`.
- `/tree` shows two compaction rows on the bulleted path.

**Pass:** `notes/m5.md` records the `context_pct` value before and after each compaction and the first heading of the handoff document (from `Ctrl+O`). Restore the default: `omp config reset compaction.thresholdTokens`.

---

## G2 — Export vs share  [10 min]  *(Guided)*

Goal: `/export` to `notes/m5-session.html`, then `/share`, and compare.

Hints:
- `/export notes/m5-session.html` (no spaces in the path). Open the file in a browser.
- `/share` prints `Share URL: https://my.omp.sh/s/<id>#<key>`; the fragment after `#` is the decryption key — never paste the full URL into `notes/`.
- If you printed `.env.example` earlier, search both outputs for `labtok_` — `share.redactSecrets` (default `true`) redacts only what the secrets config knows; `/export` is never redacted.
- `omp --export <path-to-jsonl> notes/m5-cli.html` produces the same HTML without a running session.

Checkpoints:
- `!ls -la notes/m5-session.html` shows a non-trivial size.
- The share page renders the same turns after decrypting in the browser.

**Pass:** HTML opens in a browser; the share link resolves; `notes/m5.md` lists two differences you observed (e.g. redaction, size cap, local vs remote).

---

## G3 — Prove `-c` is per terminal  [10 min]  *(Guided)*

Goal: show that `omp -c` follows the terminal breadcrumb, not "newest file".

Hints:
- Two tmux/terminal panes in `omp-course-lab`.
- Run a one-line turn in pane A that identifies pane A; then in pane B start `omp`, run a one-line turn that identifies pane B, `/exit`.
- In pane A `/exit` then `omp -c`.

Checkpoints: `ls ~/.omp/agent/terminal-sessions/` shows two breadcrumbs; `cat` each — second lines differ.

**Pass:** pane A's `omp -c` shows pane A's transcript although session B is newer. Paste both breadcrumb contents into `notes/m5.md`.

---

## S1 — Record and replay  [5 min]  *(Stretch)*

Goal: capture a short session as an `.ompcast` recording and replay it from the shell.

**Pass:** the status line showed `● REC`; `/record` printed `Saved …s recording to …ompcast`; `omp play -s 2` replays it (`Space` pauses, `q` quits). Optional: `omp clip -t "M5"` prints a `live.omp.sh/c/<id>` URL (needs Stencil login).

## S2 — Worktree session  [10 min]  *(Stretch)*

Goal: move the current session into a new git worktree and prove omp knows about it.

**Pass:** `omp worktree list` shows the path; `/resume` (Tab → all projects) shows the session under that path; `omp worktree clear --dry-run` lists it for removal.

## S3 — Method comparison  [15 min]  *(Stretch)*

Goal: find out which compaction method actually runs under two different `compaction.methodOrder` settings, `["shake","soft"]` and `["snapcompact","soft"]` (vision model required).

**Pass:** `notes/m5.md` names the method that ran each time (from what `Ctrl+O` on the divider reveals: `artifact://` refs vs image frames vs prose) and the resulting `context_pct`. Restore with `omp config reset compaction.methodOrder`.
