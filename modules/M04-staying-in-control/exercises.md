# Module 4 — Coursework

All exercises run in `omp-course-lab`. Start: `git checkout module-4-start` (or continue from your Module 3 state). Learner outputs go to `notes/` (gitignored). Test command: `python3 -m unittest discover -s tests`. Verified against `omp/18.3.1`.

Every exercise has an observable pass condition — a config value, a git state, or a card in the transcript. "You should understand X" is never a pass condition.

| # | Tier | Lesson | Time |
|---|---|---|---|
| 4-W1 | Walkthrough | 4.1 + 4.2 | 25 min |
| 4-G1 | Guided | 4.3 | 25 min |
| 4-G2 | Guided | 4.4 + 4.5 | 25 min |
| 4-S1 | Stretch | 4.5 | 20 min |
| 4-S2 | Stretch | 4.6 | 10 min |

---

## 4-W1 — Walkthrough: `always-ask`, approve/deny, then a `bash.patterns` allow rule

Goal: feel the prompt gate on a real task (issue #4, the `stats` CLI subcommand), then remove one specific prompt with a pattern rule.

1. Confirm the default: `omp config get tools.approvalMode`
   **Expected:** `yolo`.
2. Persist the strictest mode for this module: `omp config set tools.approvalMode always-ask`
   **Expected:** `✔ Set tools.approvalMode = always-ask`.
3. `omp`, then prompt:
   ```
   Fix issue #4 from docs/ISSUES.md (add the stats subcommand).
   Acceptance: `python3 -m cli stats` prints orders per month; `python3 -m unittest discover -s tests` passes.
   Run the tests before and after; do not touch generated/.
   ```
   **Expected:** the first `bash` card (`python3 -m unittest …`) stops on an approval card reading `Allow tool: bash` with the command. Approve it.
4. When the first `edit` card asks, **deny** it.
   **Expected:** the model receives the denial and either explains or proposes a different edit; it does not silently continue.
5. Approve subsequent `edit`/`bash` cards until the turn ends.
   **Expected:** final `bash` card shows the unittest run passing; `git diff --stat` lists `cli/` files and a test file.
6. Count how many approval cards you answered; write the number and the tool names in `notes/m4-approvals.md`.
7. Now stop the test-run prompts only:
   ```bash
   omp config set bash.patterns '[{"match":"python3 -m unittest*","approval":"allow"}]'
   omp config get bash.patterns
   ```
   **Expected:** `[{"match":"python3 -m unittest*","approval":"allow"}]`.
8. Switch to `write` mode so the allow rule can take effect (`always-ask` still prompts for `write`-tier calls, and an `allow` rule lowers a command *to* the `write` tier):
   `omp config set tools.approvalMode write`
9. `omp`, prompt: `Run the test suite and report the counts.`
   **Expected:** the `python3 -m unittest discover -s tests` `bash` card runs **with no approval card** before it.
10. Prompt: `Run the test suite, then delete .pytest_cache with rm -rf, as one && command.`
    **Expected:** the command is not auto-approved (compound line; `allow` cannot approve it) — you get a prompt for `exec`. Deny it.

**Pass condition:** `omp config get bash.patterns` shows the rule; `omp config get tools.approvalMode` → `write`; your transcript from step 9 has a `bash` test-run card with no approval card preceding it; `notes/m4-approvals.md` exists with the count from step 6.

> Deviation from the outline: the outline's example rule is `npm test`; the lab is Python-only, so the rule targets `python3 -m unittest*`. Same mechanism.

---

## 4-G1 — Guided: plan mode on issue #5, annotate one section out of scope

Goal: get a plan for issue #5 (order cancellation: `DELETE /orders/<id>`, `python3 -m cli cancel <id>`, and sub-item (c) "email the customer"), mark sub-item (c) out of scope, approve, and confirm the implementation omits it.

Hints:
- Toggle plan mode with `Alt+Shift+P` before the first prompt; if the chord does nothing, set `plan.defaultOnStartup: true` and restart.
- Ask for "one section per sub-item" so the Contents sidebar maps 1:1 to sub-items.
- In the sidebar: `a` = annotate selected section, `e` = edit, `u` = undo, `Enter` saves. `/plan-review` reopens the overlay if you closed it.
- Approve with the option that keeps your context unless the session is already large.

Checkpoints:
1. During planning, the transcript contains only `read`/`grep`/`glob` (and possibly `web_search`/`task`) cards — no `edit`, no `write` to repo paths (the plan's own `write local://<slug>-plan.md` and `write xd://propose` are expected).
2. The overlay shows ≥ 3 sections; sub-item (c) carries your annotation text.
3. After approval, the session is auto-named from the plan title (terminal title and editor border colour refresh; only if the session had no name yet).
4. `git diff --stat` touches `api/` and `cli/` (and tests) but nothing email-related; `grep -ri "email" cli/ api/` shows no new hits.

**Pass condition:** implementation omits the annotated item (checkpoint 4) and `python3 -m unittest discover -s tests` passes. Write the section titles and your annotation to `notes/m4-plan.md`.

---

## 4-G2 — Guided: annotate the working diff, LLM review, then `omp commit`

Goal: put two line notes on the issue #5 diff, run the review with those notes as focus, apply fixes, and commit.

Hints:
- `/annotate code-review` → choose the working-copy diff. `a` adds a line note; `A` a whole-file note.
- Choose **Continue with LLM review** (not "Paste annotations") to launch `/review` with your notes as focus.
- After fixes, `omp commit --dry-run` first; then `omp commit -c "<one line of context>"`. If the model refuses (`No model available for commit generation`), log in or pass `-m <model>`.
- For a second, separately scoped commit, stage only what belongs to it: `git add api/` → `omp commit -c "api only"`, then `git add cli/` → `omp commit -c "cli only"`. Observed on this build: with files staged, `omp commit` commits only the staged changes; with nothing staged it stages everything (`--legacy` always prints `Staging all changes…`). Check `--dry-run` output for what it intends to include.

Checkpoints:
1. Overlay shows two notes on two different lines (or one line + one file-level).
2. The `/review` turn's report references your notes' subject matter.
3. `omp commit --dry-run` prints a message and changes nothing (`git status` still dirty).
4. `git log --oneline -3` shows ≥ 2 new commits whose subjects name different scopes (e.g. `api:` vs `cli:`).

**Pass condition:** ≥ 2 commits with distinct scopes in `git log`; `notes/m4-review.md` contains the two notes verbatim and the review's summary.

---

## 4-S1 — Stretch: resolve `conflict-lab` via `conflict://*`

Goal: `git switch -c scratch main && git merge conflict-lab` (the lab's documented flow) conflicts in `api/server.py` and `cli/__main__.py` — one marker block each, around the `SERVICE_NAME` / `DESCRIPTION` strings. Resolve both with `conflict://` writes — never by editing markers by hand — and get the tests green.

Constraints: use `read <file>:conflicts` first for both files (expect `#1` and `#2`, ids continue across files in one session); resolve one block with a side token (`@ours` or `@theirs`) and the other with literal content that combines both sides' wording; finish with `read <file>:conflicts` showing none for both files.

**Pass condition:** `git grep -n '<<<<<<<\|>>>>>>>' -- api cli` prints nothing; `python3 -m unittest discover -s tests` exits 0; `git log -1 --format=%P` shows two parents — conclude the merge with `git commit` (observed on this build: `omp commit` makes a single-parent commit and leaves `MERGE_HEAD`; draft the message with `omp commit --dry-run -c "…"` if you want a model-written one).

---

## 4-S2 — Stretch: fork before risk, undo with git

Goal: `/fork`, run a deliberately over-broad refactor prompt, revert with git, resume the original session.

**Pass condition:** two session files for this cwd (see `/resume`, Tab toggles folder/all); `git status` clean; `notes/m4-undo.md` names the fork session id and the git command you used to revert.

---

## Cleanup before Module 5

```bash
omp config reset bash.patterns
omp config reset bash.allowCompoundCommands
omp config reset tools.approval
# keep tools.approvalMode = write if you prefer prompts for exec; reset to restore the default:
omp config reset tools.approvalMode     # → yolo
```
