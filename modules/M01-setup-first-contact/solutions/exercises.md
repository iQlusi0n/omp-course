# Module 1 — Instructor notes (solutions)

Verified on `omp/18.3.1`. Where a step was executed on the build machine, the observed output is quoted; TUI-only steps are marked *(docs)*.

## W1 — Install, verify, authenticate, first fix

- `omp --version` → `omp/18.3.1`. The `-v` alias is documented in `cli-reference.md`.
- Login proof: `omp token <provider>` prints the credential and exits 0. When absent it prints `No active credential found for provider "<id>".` and `Configured providers: <list>`, exit 1 (observed).
- The fix prompt, run headless against a clean clone of `omp-course-lab` at `module-1-start` (audit pass, `omp/18.3.5`), produced this tool sequence (from `--mode json`): `read docs/ISSUES.md` → `read cli/format.py` → `edit cli/format.py` (`cents / 10` → `cents / 100`) → `bash python3 -m unittest discover -s tests` → `bash LAB_ISSUE=1 python3 -m unittest tests.test_issues; python3 -m cli orders --month 2026-03`. `git diff --stat`: `cli/format.py | 2 +-` / `1 file changed, 1 insertion(+), 1 deletion(-)`. Afterwards `python3 -m cli orders --month 2026-03 | tail -1` → `12 orders for 2026-03, total $1943.94`; `LAB_ISSUE=1 python3 -m unittest tests.test_issues` → `OK (skipped=18)`.
- The full suite prints `Ran 48 tests … OK (skipped=20)` on `main`; the skips are the gated issue tests. `ResourceWarning: unclosed database` lines may appear — not failures. If a learner's shell has `python` as well as `python3`, either works; the point is that a `bash` card with `OK` exists.
- If the diff has two files, the usual cause is the model "tidying" adjacent code. The prompt's "touch only the file that contains the bug" reduces this; Module 3 formalizes it.

## W2 — Terminal chord check *(docs)*

- Action IDs and defaults: `app.tools.expand` = `Ctrl+O`, `app.tools.toggleVisibility` = `Ctrl+Shift+O` (`keybindings.md`).
- A learner whose `Ctrl+Shift+O` collapses the card instead of hiding activity has a terminal that sends plain `Ctrl+O` for both. This is the expected failure mode; it is not an omp bug.

## G1 — Headless overview

Reference command:
```sh
omp -p --no-session "List the top-level directories and what each is for" > notes/m1.txt
```
Observed against the real lab: `grep -c 'api/'` → 1, `grep -c 'cli/'` → 1, `grep -cF 'Working...'` → 0 — but a bare `grep -c Working` → **1**, because the answer quotes the lab README's course title *Working with omp*. The pass command therefore matches the literal spinner `Working...` (`-F`). `Working...` is on stderr; a learner who used `2>&1` will fail checkpoint 3 — that is the teaching moment.

## G2 — Remap a chord

Reference file:
```yaml
# ~/.omp/agent/keybindings.yml
app.tools.toggleVisibility: Alt+O
```
Checks: `/hotkeys` shows `Alt+O` for the action after restart *(docs: `/hotkeys` reflects remaps loaded from disk)*. Pitfalls: writing into `config.yml` (not read from there), using an old unqualified action name (migrated, but tell them to use the namespaced IDs), forgetting to restart. In tmux: `extended-keys` first.

## G3 — Config round-trip

Observed:
```text
$ omp config set startup.showSplash true
✔ Set startup.showSplash = true
$ grep -n -A1 startup ~/.omp/agent/config.yml
15:startup:
16-  showSplash: true
$ omp config reset startup.showSplash
✔ Reset startup.showSplash to false
$ grep -c startup ~/.omp/agent/config.yml
0
```
Minimum `notes/m1-config.txt` content: `agent.db` (auth store), `config.yml` (global settings), `sessions/` (saved sessions per cwd). Bonus: `blobs/`, `history.db`, `models.db`.

## S1 — Completions

- bash: `omp completions bash | grep -c -- '--resume'` → 3 (observed). zsh → 1. fish encodes it as `-l resume` (line 89 of the script, observed), so the fish grep must look for `-l resume`.
- Wiring lines are exactly those in `omp completions --help`.

## S2 — Profile

Observed:
```text
$ omp --profile course config path
/home/user/.omp/profiles/course/agent
$ omp --profile course token anthropic
No active credential found for provider "anthropic".   (exit 1)
```
The profile directory is created on first use. Keybindings are inherited from the default profile; nothing else is (`config-usage.md` → Profiles).

## S3 — JSON event stream

Observed on the real lab: `grep -c '"edit"' notes/m1-events.json` → 21 (the string appears in `tool_execution_start`, `_update`, `_end` and in message content). Any count ≥ 1 passes. Event types present in that run: `session`, `agent_start`, `turn_start`, `message_start`, `message_update`, `message_end`, `tool_execution_start`, `tool_execution_update`, `tool_execution_end`, `turn_end`, `agent_end`. The `tool_execution_start` events carry `toolName` and `args`; the `edit` one targets `cli/format.py`.

## Grading shortcuts

```sh
# W1
omp --version && omp token "$PROVIDER" >/dev/null && git -C omp-course-lab diff --stat | grep -q 'cli/format.py' && git -C omp-course-lab diff --stat | tail -1 | grep -q '1 file changed' && (cd omp-course-lab && LAB_ISSUE=1 python3 -m unittest tests.test_issues >/dev/null 2>&1) && echo W1-PASS
# G1
f=omp-course-lab/notes/m1.txt; test -s $f && grep -q 'api/' $f && grep -q 'cli/' $f && ! grep -qF 'Working...' $f && echo G1-PASS
# G3
! grep -q showSplash "$(omp config path)/config.yml" && test -s omp-course-lab/notes/m1-config.txt && echo G3-PASS
# S2
[ "$(omp --profile course config path)" = "$HOME/.omp/profiles/course/agent" ] && ! omp --profile course token "$PROVIDER" >/dev/null 2>&1 && echo S2-PASS
```
