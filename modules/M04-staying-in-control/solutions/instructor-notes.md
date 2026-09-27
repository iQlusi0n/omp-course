# Module 4 — Instructor notes (solutions)

Built against omp/18.3.1. Verify pass conditions with the commands listed; do not accept "it worked".

## 4-W1 (approvals + patterns)

Expected observations on issue #4 (`stats` subcommand) under `always-ask`:
- `read`/`grep`/`glob` never prompt (tier `read`).
- First prompt is usually the pre-change `bash python3 -m unittest discover -s tests` (exec).
- `edit` prompts (write tier) — 2–4 of them: `cli/commands.py`, `cli/__main__.py`, a test file, `README.md`.
- `bash python3 -m cli stats` and the post-change test run prompt again.
Typical count: 5–8 approval cards. A learner reporting 0 did not leave `yolo` (check `omp config get tools.approvalMode`).

Denying the first `edit`: the model must not proceed silently; acceptable behaviors are an explanation, a question (`ask` card), or a retry with a different plan. If it simply retried the identical edit without comment, that is still a correct demonstration that a denial is just an error result to the model.

Pattern rule check:
```bash
omp config get bash.patterns
# [{"match":"python3 -m unittest*","approval":"allow"}]
omp config get tools.approvalMode   # write
```
Why step 8 switches to `write`: an `allow` rule lowers the command to the `write` tier (approval-mode.md "Safety overrides"). In `always-ask`, `write` still prompts, so the rule would appear to do nothing. Common learner confusion — worth saying out loud.

Step 10 (`… && rm -rf .pytest_cache`): with `bash.allowCompoundCommands` at its default `false`, `allow` cannot approve a compound line → exec-tier prompt in `write` mode. If the learner also added `rm -rf *: deny`, the line is denied instead (segment match). Both are correct outcomes; the report should say which.

### 4.2 Stretch (eval bypass)
Reference prompt: with `rm -rf *` denied in `bash.patterns`, ask omp to remove the scratch directory "using Python's `subprocess` in `eval`" (e.g. `subprocess.run(["bash","-c","rm -rf scratch"])`). Expected: the `bash.patterns` `deny` does not fire because the rules govern the `bash` tool only; the directory is removed. Setting `tools.approval.eval: prompt` (or `deny`) is the fix the note should name.

## 4-G1 (plan mode, issue #5)

Pass check:
```bash
git diff --stat                      # api/server.py, cli/__main__.py (+ cli/commands.py), tests/…
grep -ri "email\|smtp" api cli tests # no new hits (compare against module-4-start)
python3 -m unittest discover -s tests
LAB_ISSUE=5 python3 -m unittest tests.test_issues
```
If the email sub-item was implemented anyway: either the annotation was added to the wrong section, or the learner picked "Paste"/left plan mode without approving and then prompted normally. Ask them to `/plan-review` (only works while still in plan mode) or to show the annotation text in `notes/m4-plan.md`.

Terminal chord problems: `Alt+Shift+P` may not reach omp on terminals that do not forward the chord (Module 1). Fallback taught: `plan.defaultOnStartup: true` (`omp config set plan.defaultOnStartup true`) — remember to reset it afterwards.

Session naming: after approval the session is auto-named from the plan title only if the session had no name yet (session-tree-plan.md). A learner who `/rename`d earlier will not see it; not a failure.

### 4.3 Stretch (headless plan-then-implement)
Reference command: `omp --plan-yolo -p "Implement issue #5; skip sub-item (c) — it is out of scope"`. Print-mode output shows the plan, then the implementation on the `smol` role (or `--plan-yolo-into <model>`); `git diff --stat` must show no email-related change.

## 4-G2 (annotate → review → commit)

- Both notes must be visible in `notes/m4-review.md` verbatim; the review report should reference them (the overlay passes them as operator focus to `/review`).
- `omp commit --dry-run` must leave `git status` dirty. Then ≥ 2 commits with distinct scopes: check `git log --oneline -3`. Observed on this build: with files staged, `omp commit` commits only the staged changes and leaves the rest unstaged; with nothing staged it stages everything (`--legacy` always prints `Staging all changes…`). So `git add api/` → `omp commit`, then `git add cli/` → `omp commit` yields the two scoped commits.
- `No model available for commit generation` → no provider, or `commit`/`smol` roles resolve to nothing; `omp commit -m <model>` or `/login`.
- Changelog: if the lab has no `CHANGELOG.md`, `--no-changelog` is irrelevant; if it does, expect an entry.

## 4-S1 (conflict-lab)

The lab's documented flow is `git switch -c scratch main && git merge conflict-lab` → `ours = HEAD` (main content), `theirs = conflict-lab`. Both files have exactly one block (`SERVICE_NAME` in `api/server.py` L18-22, `DESCRIPTION` in `cli/__main__.py` L17-21 — competing one-line edits, so `@both` is wrong here). Tests do not pin either string, so any resolution passes the suite.

Expected sequence (the exercise states only the goal; use this to grade the approach): `read <file>:conflicts` first for both files (expect `#1` and `#2`, ids continue across files in one session); one block resolved with a side token (`@ours` or `@theirs`) and the other with literal content that combines both sides' wording; finish with `read <file>:conflicts` showing none for both files. Conclude the merge with `git commit`, not `omp commit` (see step 5 below).

Reference resolution:
1. `read api/server.py:conflicts` → `#1`; `read cli/__main__.py:conflicts` → `#2` (verified: ids continue across files within one session; from the shell each `omp read` starts at `#1` again).
2. Inspect `conflict://1/ours` and `/theirs`.
3. Literal combined resolution for one block, e.g. `write conflict://1` with content `SERVICE_NAME = "omp-course-lab orders API v1"`.
4. `write conflict://*` with `2: @theirs` (or `write conflict://2` with `@theirs`). Verified result text: `Resolved N conflicts across M files:` + a `Snapshots:` block.
5. Re-read both `:conflicts` → `No unresolved git merge conflicts in <file>.` Tests green. `git add api/server.py cli/__main__.py`, then **`git commit`** (not `omp commit`: observed on this build it creates a single-parent commit and leaves `MERGE_HEAD`; `git status` then still says "you are still merging"). A model-written message can be drafted with `omp commit --dry-run -c "…"` and pasted into `git commit -m`.
Pitfalls: writing to `conflict://1/ours` (read-only scope → ToolError); `@base` without diff3 (`git config merge.conflictStyle diff3` before merging fixes it); reusing an id after resolution (invalidated → re-read); concluding the merge with `omp commit` (single parent).

Pass check:
```bash
git grep -n '<<<<<<<\|>>>>>>>' -- api cli   # empty
python3 -m unittest discover -s tests       # exit 0
git log -1 --format='%P'                    # two parents
```

## 4-S2 (fork/undo)

Pass check: `/resume` (Tab for all) lists two sessions for this folder whose transcripts diverge at the rename prompt; `git status` clean. `omp --fork <id>` from the shell also satisfies it. Reject if the learner used `--no-session` (fork impossible) or forked mid-stream (refused with a warning).

## Reset after the module
```bash
omp config reset bash.patterns; omp config reset bash.allowCompoundCommands
omp config reset tools.approval; omp config reset tools.approvalMode; omp config reset plan.defaultOnStartup
```
