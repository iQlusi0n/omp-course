# Module 1 — Exercises

Built against `omp/18.3.1`. All work happens in `omp-course-lab` at tag `module-1-start`. `notes/` is gitignored — put every output file there. Each exercise ends with a **Pass** line that is a command or an observation, never a feeling.

Tiers: **W** = Walkthrough (exact keys/commands, expected output shown) · **G** = Guided (goal + hints + checkpoints) · **S** = Stretch (goal + pass condition; instructor notes in `solutions/`).

Time: W ≈ 20 min · G ≈ 15 min · S ≈ 10 min each.

---

## W1 — Install, verify, authenticate, first fix (~20 min)

Prerequisite: a provider account (OAuth: Anthropic, OpenAI Codex, GitHub Copilot, …) **or** an API key for a key-based provider.

1. Install:
   ```sh
   curl https://omp.sh/install | sh
   ```
   Open a new shell.
   **Expected:** `which omp` prints a path.
2. Verify:
   ```sh
   omp --version
   ```
   **Expected:** `omp/18.3.1` (newer is fine; write the number in `notes/m1-version.txt`).
3. Authenticate — pick **one**:
   - OAuth from the shell: `omp login anthropic` (or `omp login openai-codex`, `omp login github-copilot`). Follow the URL it prints/opens.
   - OAuth from a session: `omp` → `/login` → choose a provider → `Ctrl+C` `Ctrl+C` to exit.
   - API key: `export ANTHROPIC_API_KEY=…` (or `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, …) in your shell rc.
   **Expected:** `omp token <provider> | cut -c1-6` prints six characters and exits 0.
4. Check the catalog is live:
   ```sh
   omp models <provider> | head -5
   ```
   **Expected:** `<provider> (N)` followed by a table header `model │ context │ max-out │ thinking │ images`.
5. Enter the lab and start omp:
   ```sh
   cd omp-course-lab && git checkout module-1-start && git status --short && omp
   ```
   **Expected:** nothing from `git status --short`; the TUI opens with an empty composer.
6. Paste this prompt and press `Enter`:
   ```text
   Read `docs/ISSUES.md` and locate issue #1. Inspect the code it points at for one small bug. Make the smallest safe fix — touch only the file that contains the bug. Then run `python3 -m unittest discover -s tests` and show me the result.
   ```

   **Expected:** in order: a `read` card (`docs/ISSUES.md`), a `read` card for `cli/format.py` (issue #1 names that file; more `read`/`grep`/`glob` cards are fine), one `edit` card, one `bash` card containing `unittest`, then a final message reporting the tests pass.
7. Press `Ctrl+O`.
   **Expected:** tool output expands; the `bash` card shows `Ran 48 tests … OK (skipped=20)` (the skips are the `LAB_ISSUE`-gated tests).
8. Exit with `Ctrl+C` `Ctrl+C`, then:
   ```sh
   git diff --stat
   ```
   **Expected:** `cli/format.py | 2 +-` and `1 file changed`.
9. Confirm the fix against the issue's own repro:
   ```sh
   python3 -m cli orders --month 2026-03 | tail -1
   LAB_ISSUE=1 python3 -m unittest tests.test_issues
   ```
   **Expected:** `12 orders for 2026-03, total $1943.94`, then `OK (skipped=18)` (was `FAILED (failures=2, skipped=18)` before the fix — the 18 skips are the other issues' gated tests).

**Pass:** `omp --version` printed a version; `omp token <provider>` exits 0; `git diff --stat | tail -1` says `1 file changed` and the file is `cli/format.py`; `LAB_ISSUE=1 python3 -m unittest tests.test_issues` finishes with `OK (skipped=18)`.

If the diff touches more than one file: `git checkout -- <extra file>` and read Lesson 1.5's troubleshooting — the prompt's "touch only the file that contains the bug" is doing real work.

---

## W2 — Terminal chord check (~5 min)

1. In `omp-course-lab`, run `omp`, then send: `read README.md and summarize it in one line`.
   **Expected:** one `read` card and a one-line answer.
2. Press `Ctrl+O` twice.
   **Expected:** the card expands, then collapses.
3. Press `Ctrl+Shift+O` twice.
   **Expected:** tool activity hides, then returns.
4. Send `/hotkeys`.
   **Expected:** a list including `app.tools.expand  Ctrl+O` and `app.tools.toggleVisibility  Ctrl+Shift+O`.
5. Exit (`Ctrl+C` `Ctrl+C`).

**Pass:** both chords behaved as expected **or** you recorded which one failed in `notes/m1-terminal.txt` together with the terminal name (you will fix it in G2).

---

## G1 — Headless repo overview to a file (~10 min)

**Goal:** Produce `notes/m1.txt` containing omp's answer to *"List the top-level directories and what each is for"* — and nothing else.

**Hints:**
- Print mode is `-p`; the answer goes to stdout and the progress spinner (`Working...`) goes to stderr.
- `>` redirects only stdout. `2>&1` would drag `Working...` into the file.
- Match the spinner with its three dots (`grep -F 'Working...'`): the lab README names the course *Working with omp*, so the answer legitimately contains the word `Working`.
- `--no-session` keeps this throwaway run out of your session list.
- The lab's `notes/` directory exists and is gitignored.

**Checkpoints:**
1. The command returns to the prompt with exit 0 (`echo $?`).
2. `wc -l notes/m1.txt` is greater than 5.
3. `grep -cF 'Working...' notes/m1.txt` prints `0`.

**Pass:**
```sh
test -s notes/m1.txt && grep -q 'api/' notes/m1.txt && grep -q 'cli/' notes/m1.txt && ! grep -qF 'Working...' notes/m1.txt && echo PASS
```
prints `PASS`.

---

## G2 — Make a chord work on your terminal (~10 min)

**Goal:** Every chord that failed in W2 (or, if none failed, `app.tools.toggleVisibility`) is reachable from your keyboard.

**Hints:**
- `/hotkeys` gives you the exact action ID.
- Remaps go in `~/.omp/agent/keybindings.yml` — a flat YAML mapping `action.id: Chord` (or a list of chords). This file is **not** `config.yml`.
- Chord notation is what the UI shows: `Ctrl+P`, `Alt+Shift+P`, `Ctrl+Backspace`. Case-insensitive.
- Restart omp after editing.
- If you are in tmux and chords with modifiers die only there, tmux `extended-keys` is the first thing to enable.

**Checkpoints:**
1. `cat ~/.omp/agent/keybindings.yml` shows your line.
2. `/hotkeys` in a fresh session lists the new chord next to the action ID.
3. Pressing it performs the action.

**Pass:** `/hotkeys` shows your chord for the action **and** pressing it toggles the tool-activity block (or whichever action you remapped).

---

## G3 — Config root and one setting round-trip (~10 min)

**Goal:** Prove you know where settings live and that `omp config set` writes exactly there.

**Hints:**
- `omp config path` prints the agent directory.
- `startup.showSplash` is a harmless boolean (default `false`).
- `omp config set` writes the **global** file, never the project's `.omp/config.yml`.
- `grep -n showSplash "$(omp config path)/config.yml"` shows whether the key is on disk.

**Checkpoints:**
1. `omp config get startup.showSplash` → `false`.
2. After `omp config set startup.showSplash true`, the `grep` above finds the key.
3. After `omp config reset startup.showSplash`, the `grep` finds nothing and `get` prints `false` again.

**Pass:** checkpoint 3 holds, and `notes/m1-config.txt` lists the entries of `$(omp config path)` with a one-phrase purpose each (at least `agent.db`, `config.yml`, `sessions/`).

---

## S1 — Shell completions (~10 min)

**Goal:** `omp --res<Tab>` completes `--resume` in your everyday shell.

**Pass:** typing `omp --res` then `Tab` yields `--resume` (or `--resume=`), and `omp completions <yourshell> | grep -c -e '--resume' -e '-l resume'` is ≥ 1 (bash/zsh scripts spell the flag `--resume`; fish uses `-l resume`). Record the rc line you added in `notes/m1-completions.txt`.

## S2 — Isolated profile (~10 min)

**Goal:** A profile named `course` with its own agent directory and no inherited logins.

**Pass:** `omp --profile course config path` ends in `/profiles/course/agent`, and `omp --profile course token <provider>` exits non-zero while `omp token <provider>` exits 0.

## S3 — Headless fix with an event stream (~15 min)

**Goal:** Re-run the W1 fix prompt from a clean checkout in print mode with `--mode json`, saving events to `notes/m1-events.json`, and locate the `edit` tool call in the stream.

**Pass:** after `git checkout -- . && git checkout module-1-start` and the run, `git diff --stat | tail -1` says `1 file changed` (the file is `cli/format.py`) **and** `grep -c '"edit"' notes/m1-events.json` ≥ 1.

---

## Reset between attempts

```sh
git checkout -- . && git checkout module-1-start     # repo
omp config reset startup.showSplash                    # G3
rm -f ~/.omp/agent/keybindings.yml                     # G2 (only if you created it here)
```
