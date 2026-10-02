# Module 15 — Instructor rubric (omp/18.3.1)

Grade from the learner's branch, `notes/capstone.md`, `notes/capstone.html` (the `/export`) and the two screenshots. Every row is verifiable without the learner present. Score each evidence item 0 / 1 / 2 (missing / present but weak / present and correct); **pass = ≥ 17 of 22 with no 0 in E2, E6 or E9**, plus the functional gate below.

## Functional gate (must pass before scoring)

```bash
git checkout <learner-branch>
python3 -m unittest discover -s tests            # OK; ≥ 60 tests (reference: 65, 20 skipped)
LAB_ISSUE=all python3 -m unittest tests.test_issues   # still 16 failures — no scope creep into #1–#8 (17+ or fewer both need an explanation in notes)
python3 tools/migrate.py; python3 tools/migrate.py    # 2nd run prints: already at version 2
python3 -c "import generated.schema_info as s; print(s.SCHEMA_VERSION)"   # 2
git log --oneline module-15-start..                   # ≥ 3 commits
git diff module-15-start --stat -- generated/          # only schema_info.py, and it matches a tool run (compare with capstone-solution)
```

Quick behavioural spot checks (server on a scratch DB: `DATABASE_URL=/tmp/g.sqlite python3 -m api --port 18080`):

| Check | Expect |
|---|---|
| `curl -s localhost:18080/users/9/orders?status=bogus` | `400`, error names `pending, shipped, completed, cancelled` |
| `curl -s localhost:18080/users/9999/orders` | `404` |
| `curl -s localhost:18080/users/9/orders` | `count` = number of orders, no `page` key, newest first |
| `curl -s localhost:18080/users/1` | has `"company": null` |
| `POST /signup` with `company` | `201`, body echoes `company` |
| `python3 -m cli orders --status bogus; echo $?` | argparse error, `2` |
| `python3 -m cli orders --month 2026-03 --status completed` | only `completed` rows from 2026-03 |
| `curl -s localhost:18080/ \| grep -c 'id="company"'` | `1`, between `#email` and `#submit` |
| `docs/spec.pdf` | regenerated (`git log -1 -- docs/spec.pdf` on the branch; `python3 tools/make_pdf.py` reproduces it byte-for-byte) |

## Evidence items

| # | Item | 2 (correct) | 1 (weak) | 0 |
|---|---|---|---|---|
| E1 | `.omp/AGENTS.md`, `.omp/RULES.md`, ≥ 1 rule with `condition:` | All three in the branch; `AGENTS.md` names the test command and the `generated/` rule; `omp ttsr list` (run from the lab root) shows the rule with `condition:`/`astCondition:` | Files exist but the rule has no trigger, or `AGENTS.md` is boilerplate | Missing |
| E2 | Plan with ≥ 1 annotation **before** implementation | `/export` HTML shows the plan, a note authored in the Plan Review overlay, an accepted plan, and only *then* the first `edit` card | Plan and annotation exist but edits started before acceptance, or the note is empty/trivial | No plan mode |
| E3 | Batch `task` with `outputSchema`; ≥ 1 custom agent; Agent Hub screenshot | `Spawned N background agents` card with per-item `outputSchema`; `read agent://<id>` result matches the schema; `.omp/agents/<name>.md` with `name`, `description`, `tools` (and used at least once — a `task` card with `agent: <name>`); Hub screenshot shows ≥ 2 agents | One of the three missing, or the custom agent was defined but never spawned | None |
| E4 | LSP rename **or** `ast_edit` codemod, accepted | `Applied rename:` card whose edits are consistent with `grep` (e.g. `count_orders_in_month` untouched), **or** `Staged as a proposal…` + `write xd://resolve` → `Applied N replacements`; suite green afterwards | Preview only (`apply: false` / `xd://reject`), or the change was then reverted by hand | Regex/sed instead |
| E5 | DAP session | `debug` cards: `launch` (stopped on entry) → `set_breakpoint … verified` → `continue` → `variables`/`evaluate` showing a concrete value (`version = 1` on a v1 DB, or `user = None`) → `terminate` | Launch only, or breakpoint not verified, or no variable inspected | None |
| E6 | `/review` verdict; `/annotate` notes; `omp commit` ≥ 3 commits | Review turn whose report visibly references ≥ 2 learner notes (from `/annotate code-review` → Continue with LLM review); the learner's disposition of each finding is in notes; ≥ 3 commits with generated messages, each an atomic slice (migration / API / CLI+web / docs) | Review without notes, or commits that mix slices, or exactly 3 commits only because docs were split arbitrarily | `git commit -m` by hand, or 1–2 commits |
| E7 | Browser-verified form | `eval` card: `browser.open` → `fill` ×3 (incl. `#company`) → `click("#submit")` → `waitForSelector("#banner", {visible:true})` → banner text `Welcome aboard!`; screenshot path; a DB read proving the row with the company; committed `data/lab.sqlite` **not** polluted (scratch `DATABASE_URL`) | Banner asserted but no DB proof, or the signup landed in the committed DB (`git status` shows `data/lab.sqlite` modified after the run) | `curl` only |
| E8 | Extension/hook or MCP used | Hook file under `.omp/hooks/pre/` (or `.omp/extensions/`) and a card whose error text is the hook's `reason`; **or** `.omp/mcp.json`, `/mcp list` output, and an `mcp__<server>_<tool>` card | Configured but never triggered/used | None |
| E9 | `ci/review.sh` passing | `review: N finding(s), 0 P0, verdict=pass` + `exit=0` on the v2 diff, with one sentence explaining the scope line (or why the first run failed) | Passing only on an empty diff, or exit 0 achieved by deleting the verdict check | Not run |
| E10 | `/export` HTML, `/share` link, `omp stats` | `notes/capstone.html` opens and contains the plan + review turns; a `https://my.omp.sh/s/<id>#<key>` link (or gist URL); `omp stats --summary` (or `--json`) output with the session's cost | Two of three | ≤ 1 |
| E11 | Retained memory or learned skill from a real gotcha | `Lesson stored.` (or `Created/Updated managed skill "<n>"`) card; `read memory://root/learned.md` bullet (local backend) or `recall` hit (Mnemopi/Hindsight); the lesson describes something that actually happened in *this* transcript | Lesson is generic ("run tests") or stored before any work | None |

## Stretch (bonus, +1 each, not required to pass)

- `/collab status` showing a second participant during the work.
- `.omp/WATCHDOG.md` + an `<advisory … severity="concern">` that changed a decision (quoted with the diff).
- Two `omp stats --summary` numbers (with/without `--prewalk`) and a one-line quality comparison.

## Common deductions

- **Scope creep:** fixing issues #1–#8 "while there" (except #8's validation, which the spec allows *if* it blocks the company field — it does not). `LAB_ISSUE=all` failure count ≠ 16 → −2 unless justified.
- **Hand-edited `generated/`:** `git log -p -- generated/schema_info.py` shows an edit not matching `tools/seed_db.py` output → E1 = 0 (the rule existed and was ignored) and functional-gate fail.
- **Fresh seed instead of migrated DB:** `data/lab.sqlite` schema shows `company TEXT` inside `CREATE TABLE users` (fresh seed) instead of an `ALTER TABLE`-added column. Acceptable *only if* notes say so and `tools/migrate.py` was still exercised in tests; otherwise −1 on the migration slice.
- **Unverified claims:** any "tests pass" in the transcript without a `bash` card behind it → −1 per occurrence (max −3).
- **Committed secrets or `notes/`:** `.env`, share keys, or `notes/` tracked in git → −2.

## Reference

`git checkout capstone-solution` in `omp-course-lab` (a branch): four commits — migration, API, CLI+web, docs — 65 tests, 20 skipped, `LAB_ISSUE=all` still 16 failures. `solutions/instructor-notes.md` explains the design choices and the failure modes seen while building it.
