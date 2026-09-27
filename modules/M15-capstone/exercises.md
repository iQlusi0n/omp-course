# Module 15 — Capstone exercises (omp/18.3.1)

One project, five phases. Work in `omp-course-lab` on a branch cut from `module-15-start`:

```bash
cd omp-course-lab && git checkout module-15-start && git switch -c v2
python3 -m unittest discover -s tests          # green before you start (48 tests, 20 skipped)
LAB_ISSUE=all python3 -m unittest tests.test_issues   # 16 failures — issues #1–#8 are NOT your job
```

Keep a running `notes/capstone.md` (gitignored) with the evidence numbers **E1–E11** from the README checklist. Every phase ends with a pass condition you can check without an instructor.

Time budget: Phase 0 — 15 min · Phase 1 — 35 min · Phase 2 — 60 min · Phase 3 — 40 min · Phase 4 — 30 min.

Tiering: each phase has a **Walkthrough** (exact prompts), a **Guided** variant (goal + hints + checkpoints + pass) and a **Stretch** (goal + pass; instructor notes in `solutions/`). Do the walkthrough if you want the safe path, the guided variant if you finished the module's own guided tasks comfortably.

---

## Phase 0 — Inform the session (15 min) → E1

**Walkthrough**

1. Create `.omp/AGENTS.md` (M6 §6.1). Minimum content: the test command (`python3 -m unittest discover -s tests`), the four packages, "never edit `generated/`; regenerate with `python3 tools/seed_db.py`", "issues #1–#8 in `docs/ISSUES.md` are out of scope for v2 unless they block an item", and "run the suite in a `bash` card before claiming anything passes".
2. Create `.omp/RULES.md` (M6 §6.2): three lines, hard rules only — no edits under `generated/`; no `pip`/network; the spec `docs/V2-SPEC.md` wins over any memory.
3. Create `.omp/rules/no-hand-edit-generated.md` with a TTSR trigger (M11 §11.1):
   ```md
   ---
   description: generated/ is machine-written; regenerate it with tools/seed_db.py
   condition: "SCHEMA_VERSION|STATUSES|TABLES|GENERATED"
   scope: "tool:edit(generated/*), tool:write(generated/*)"
   interruptMode: always
   ---
   Never edit files under `generated/`. Run `python3 tools/seed_db.py --db /tmp/scratch.sqlite` to regenerate `generated/schema_info.py` without touching `data/lab.sqlite`.
   ```
4. From the lab root: `omp ttsr list`, then three dry-runs (verified on 18.3.1):
   ```
   omp ttsr test --source tool --tool edit --path generated/schema_info.py 'SCHEMA_VERSION = 2'
   omp ttsr test --source tool --tool edit --path tools/seed_db.py 'SCHEMA_VERSION = 2'
   omp ttsr test --source text 'SCHEMA_VERSION = 2'
   ```
   **Expected:**
   - `omp ttsr list` shows the rule with `condition: SCHEMA_VERSION|STATUSES|TABLES|GENERATED`.
   - Run 1 prints `Triggered (1)` / `✓ no-hand-edit-generated  condition: /SCHEMA_VERSION|STATUSES|TABLES|GENERATED/`, exit 0.
   - Runs 2 and 3 print `No rules triggered. (evaluated 1)`, exit 1 — the `scope` globs limit it to edits/writes under `generated/`, so editing the seeder or talking about the constant is fine.
5. Start `omp` in the lab; `/extensions`.
   **Expected:** `AGENTS.md` and `RULES.md` listed as project context files; the rule listed.

**Guided:**
- *Goal:* the same three files, but the rule uses an `astCondition:` instead of a `condition:` regex.
- *Hints:* the pattern is `SCHEMA_VERSION = $V`; `omp ttsr test` takes the same `--source`/`--tool`/`--path` flags as the walkthrough.
- *Checkpoints:* (a) `omp ttsr list` shows the rule with `astCondition:`; (b) the edit-under-`generated/` dry-run triggers, the `--source text` dry-run does not.
- *Pass:* the two dry-run outputs pasted in `notes/capstone.md`; E1 below.

**Stretch:**
- *Goal:* add a second rule with `question:` that the judge asks only when the reply claims tests pass (M11 §11.1 stretch), with `ttsr.judge: on` for the session.
- *Pass:* `omp ttsr list` shows two rules; `omp config get ttsr.judge` prints `on`; one transcript excerpt where the judge question fired is pasted in `notes/capstone.md`.

**Pass (E1):** the three files exist in your branch; `omp ttsr list` shows ≥ 1 rule with `condition:` (or `astCondition:`); a screenshot or paste of `/extensions` in `notes/capstone.md`.

---

## Phase 1 — Scout, plan, annotate (35 min) → E2, E3

**Walkthrough**

1. Fan out three read-only scouts in one batch (M10 §10.1). Prompt:

   ```text
   Read docs/V2-SPEC.md. Spawn ONE batch task with context "omp-course-lab v2, see docs/V2-SPEC.md; read-only" and three scout items:
   (1) migration — which files define the schema, where SCHEMA_VERSION is written, how tests build a temp DB;
   (2) API — how routes are matched in api/server.py, how db.list_orders is shaped, which tests cover /orders;
   (3) CLI+web — where argparse lives, how cli/commands.py renders, what web/app.js posts.
   Each item uses outputSchema {"type":"object","properties":{"files":{"type":"array","items":{"type":"string"}},"tests_to_add":{"type":"array","items":{"type":"string"}},"risks":{"type":"array","items":{"type":"string"}}},"required":["files","tests_to_add","risks"]}.
   ```

   **Expected:** ``Spawned 3 background agents using scout`` then three delivered results; `read agent://<id>` (or `read agent://<id>/risks/0`) shows the typed fields. Press `Alt+A` while they run and take the Agent Hub screenshot (E3).
2. Define a custom agent `.omp/agents/test-writer.md` (M10 §10.3). A reference is `modules/M10-subagents-parallel-work/solutions/test-writer.md`: `name`, `description`, `tools: read, grep, glob, edit, write, bash`, `model: "@smol"`, `output:` schema. You will use it in Phase 2.
3. Enter plan mode: `Alt+Shift+P`. Prompt:

   ```text
   Plan v2 per docs/V2-SPEC.md in three slices that each end with a green suite and a commit:
   (A) migration + seed + generated + data + tests,
   (B) GET /users/<id>/orders + company on GET /users/<id> + tests,
   (C) CLI --status + web company + POST /signup company + tests,
   then (D) docs (spec.md, spec.pdf, README).
   Include, per slice, the exact test command and the files touched. Do not include fixes for issues #1–#8.
   ```

   **Expected:** a plan with sections A–D; the Plan Review overlay opens.
4. In the overlay, put the cursor on the migration section, press `a`, write: `Regenerate generated/ through tools/seed_db.py --db /tmp/scratch.sqlite so data/lab.sqlite stays the migrated one, not a fresh seed.` `Enter`. Add a second note wherever the plan mentions issue #8 validation: `Out of scope unless it blocks the company field.` Accept the plan.
   **Expected:** the notes appear in the transcript before any `edit` card (E2). `/plan-review` re-opens the overlay if you need to check.

**Guided:**
- *Goal:* the same outcome with a fourth batch item — a `reviewer` that reads `docs/spec.md` and lists the sections that will need updating in slice D.
- *Hints:* write the scouts' `outputSchema` yourself from `omp://tools/task.md`; the reviewer item needs its own schema (a list of section names is enough).
- *Checkpoints:* (a) four `agent://` results; (b) the reviewer's list matches what you later change in Phase 4.
- *Pass:* the four `agent://<id>` ids and the reviewer's section list in `notes/capstone.md`; E2/E3 below.

**Stretch:**
- *Goal:* run the scouts with `isolated: true` and inspect `read history://<id>` for one of them.
- *Pass:* one scout's `read history://<id>` output (first lines) pasted in `notes/capstone.md`.

**Pass (E2, E3):** `notes/capstone.md` has the three `agent://<id>` ids and one pasted typed result; `.omp/agents/test-writer.md` exists; the Agent Hub screenshot is saved (e.g. `notes/hub.png`); the transcript shows a plan annotation followed by an accepted plan and only then the first `edit`.

---

## Phase 2 — Implement in slices (60 min) → E4 (and the ≥ 3 commits of E6)

Slice order is the spec's natural split: **A migration → B API → C CLI+web → D docs**. After every slice: suite in a `bash` card, then commit (Phase 4 explains `omp commit`; you may commit as you go — that is the point).

**Walkthrough**

1. Optional but recommended: restart with `omp --approval-mode write` so every `bash` call prompts (M4 §4.1) and you see each command before it runs; add `bash.patterns: [{match: "python3 -m unittest*", approval: allow}]` in `.omp/config.yml` so the suite never prompts.
2. Slice A prompt:

   ```text
   Implement slice A of the accepted plan. tools/migrate.py must be idempotent and print `already at version 2` on the second run.
   Bump SCHEMA_VERSION in tools/seed_db.py to 2 and add the nullable company column to its CREATE TABLE.
   Run `python3 tools/migrate.py` on data/lab.sqlite, then `python3 tools/seed_db.py --db /tmp/scratch.sqlite` to regenerate generated/.
   Add tests/test_migrate.py that builds a v1 database by hand and checks: column added, version 2, second run prints the no-op line, seeded DB already at 2.
   Run the suite and show the output.
   ```

   **Expected:**
   - `write` cards for `tools/migrate.py` and `tests/test_migrate.py`; `edit` card on `tools/seed_db.py`.
   - Two `bash` cards for migrate (second prints `already at version 2`); a `bash` card for the seed run; suite `OK`.
   - **No** `edit` card on `generated/` — if the model tries, your TTSR rule or `edit.blockAutoGenerated` refuses it (paste the refusal into notes: bonus E8-style evidence, but not E8).
3. Slice B prompt (the LSP/`ast_edit` requirement lives here — E4):

   ```text
   Implement slice B. Extend db.list_orders with optional status and user_id filters that AND together (do not touch the LIMIT/OFFSET line).
   Add GET /users/<id>/orders per the spec (400 naming STATUSES for a bad status, 404 for a missing user, no pagination, count = len(orders)).
   Add company to get_user.
   Before adding the route, use the lsp tool to rename db.count_orders to count_live_orders across api/ (apply the rename) so it is not confused with count_orders_in_month;
   if no LSP server is available, instead use ast_edit to change every print($$$A) in cli/ to logger.info($$$A) and apply the proposal via write xd://resolve.
   Add tests. Run the suite.
   ```

   **Expected (E4):**
   - LSP path: an `lsp` card `Applied rename:` listing `api/db.py` (and `api/server.py` if referenced) — note that `count_orders_in_month` was **not** renamed.
   - Codemod path: an `ast_edit` card `Staged as a proposal — files NOT modified yet` followed by a `write xd://resolve` card `Applied N replacements in 1 files.`
   - Either way: suite `OK`; new tests for 200/400/404 present.
4. Slice C prompt:

   ```text
   Implement slice C. cli orders gains --status with argparse choices from generated.schema_info.STATUSES (exit 2 on an invalid value), combined with --month by AND; keep the table output unchanged when --status is absent.
   web/index.html gets <input id="company" name="company"> between email and the button; web/app.js sends company only when non-empty; POST /signup stores company (blank → null) and echoes it in the 201 body.
   Spawn the test-writer agent from .omp/agents to add the CLI tests for --status while you write the API/web tests yourself. Run the suite.
   ```

   **Expected:** a `task` card spawning `test-writer`; its typed result (`result: pass`, `tests_added`); `edit` cards on `cli/__main__.py`, `cli/commands.py`, `web/index.html`, `web/app.js`, `api/server.py`, `api/db.py`; suite `OK`.
5. Slice D prompt:

   ```text
   Update docs/spec.md for v2 (schema version 2 + migrate.py, the new endpoint with an example, company on /users/<id> and /signup, the CLI flag), regenerate docs/spec.pdf with python3 tools/make_pdf.py, and add the new command/flag to README.md. Do not edit docs/spec.pdf by hand.
   ```

   **Expected:** `edit` cards on `docs/spec.md` and `README.md`; a `bash` card `wrote …/docs/spec.pdf (… 3 pages)`.

**Guided:**
- *Goal:* the same four slices, with prompts you write yourself, and slice A tried two ways in forked sessions before you keep one.
- *Hints:* use the M3 prompt shape (outcome, acceptance, scope, verification, receipt); `/fork` before slice A and compare `PRAGMA table_info` against `try/except OperationalError` as the idempotency check.
- *Checkpoints:* (a) `git diff --stat` per slice touches only that slice's files; (b) `LAB_ISSUE=all python3 -m unittest tests.test_issues` still reports **16** failures at the end — you fixed nothing you were not asked to.
- *Pass:* both checkpoint outputs pasted in `notes/capstone.md`, plus one sentence on which idempotency approach you kept and why; E4 + commits below.

**Stretch:**
- *Goal:* run slice C's CLI and web halves as two `isolated: true` subagents in one batch and merge their patches.
- *Pass:* one batch card with both subagents' results; after the merge the suite prints `OK` and `git diff --stat` shows both halves' files.

**Pass (E4 + commits):** the suite prints `OK` after each slice; `git log --oneline module-15-start..` shows ≥ 3 commits (one per slice at least); E4 card is pasted in notes; `grep -rn "count_orders(" api/` shows only the renamed symbol (LSP path) **or** `grep -rn "print(" cli/` is empty (codemod path).

---

## Phase 3 — Verify like a skeptic (40 min) → E5, E7, E9

**Walkthrough**

1. **DAP (E5).** Build a v1 database to debug against — the pre-migration blob is still in git: `git show module-15-start:data/lab.sqlite > /tmp/v1.sqlite` (verified: `schema_version` = 1). Prompt (M8 §8.4; needs `python -c "import debugpy"` to succeed):

   ```text
   Use the debug tool: launch tools/migrate.py with args ["--db", "/tmp/v1.sqlite"] using the debugpy adapter.
   Set a breakpoint on the line that executes the UPDATE of schema_version, continue, run stack_trace, scopes, and variables for Locals, evaluate `version` with context watch, then terminate. Do not edit files.
   ```

   **Expected:** `debug` cards: `Status: stopped / Stop reason: entry`, `Breakpoints for …/tools/migrate.py: - line N: verified`, `Stop reason: breakpoint`, `Variables: - version = 1 (int)`, `Result: 1 / Type: int`, `Debug session terminated.`
   Alternative accepted for E5: the seeded `bin/crash.py` session exactly as in M8 §8.4 (`user = None (NoneType)`).
2. **Browser (E7).** Start the API as a service on a scratch DB, then drive the form (M14 §14.1; M2 services):

   ```text
   Copy data/lab.sqlite to /tmp/v2-browser.sqlite. Run `DATABASE_URL=/tmp/v2-browser.sqlite python3 -m api` as a bash service named lab-api with ready port 8080.
   Then in a JS eval cell: open http://127.0.0.1:8080/ as tab "signup", fill #name "Cap Stone", #email "cap@example.com", #company "ACME", click #submit, waitForSelector("#banner", {visible: true, timeout: 5000}), display the banner text, take a screenshot, close the tab.
   Finally read /tmp/v2-browser.sqlite?q=SELECT name, company FROM users WHERE email='cap@example.com'.
   ```

   **Expected:** a `bash` card `lab-api: ready`; an `eval` card printing `Welcome aboard!` and a screenshot path; a `read` card with one row `Cap Stone | ACME`. `write proc://lab-api/kill` when done.
3. **Headless review (E9).** Copy your Module 13 `ci/review.sh` + `ci/ci.yml` into the lab's `ci/` (the lab ships `ci/` empty for this). Add one scope sentence to its `/review` prompt so pre-existing bugs do not fail the gate:

   ```text
   Scope: only lines added or changed by this diff count. Pre-existing bugs documented in docs/ISSUES.md (issues #1–#8) are known and out of scope: do not list them and do not let them affect the verdict.
   ```

   Run it from a shell **with the v2 diff in the working tree** (e.g. on a scratch clone: `git reset --mixed module-15-start` so the four commits become one unstaged diff): `./ci/review.sh --max-time 4m; echo exit=$?`.
   **Expected:** `review: N finding(s), 0 P0, verdict=pass` and `exit=0`. See `demos/15.2-ci-review-v2.md` for both the failing (no scope line: the reviewer lists issues #1, #2, #6, #7, #8 as P1 and votes `fail`) and the passing run on the reference solution.

**Guided:**
- *Goal:* harden each of the three checks with one negative or conditional case: a breakpoint that is skipped on an already-migrated DB, a failed signup, and the review gate wired into your git flow.
- *Hints:* (a) make the DAP breakpoint conditional on `version == 1` and run it against a migrated DB; (b) submit the form with an existing email — issue #8 makes this a `500`, and the banner still says `Signup failed: …` with class `error`; (c) call `ci/review.sh` from a `git` pre-push hook or a `make review` target.
- *Checkpoints:* (a) the migrated-DB `debug` transcript has no `Stop reason: breakpoint` line; (b) the `eval` card shows the banner's class `error` and its `Signup failed: …` text; (c) the hook or target prints the script's `review: … verdict=…` line.
- *Pass:* the three checkpoint outputs pasted in `notes/capstone.md`; E5/E7/E9 below.

**Stretch:**
- *Goal:* run `ci/review.sh` with `OMP_REVIEW_TARGET=pr://…` against a real PR of your fork.
- *Pass:* the PR URL, the script's `review: … verdict=…` line and its exit code pasted in `notes/capstone.md`.

**Pass (E5, E7, E9):** the three expected outputs pasted in `notes/capstone.md`; the screenshot file exists; `exit=0` from `ci/review.sh`.

---

## Phase 4 — Ship (30 min) → E6, E8, E10, E11

**Walkthrough**

1. **Annotate + review (E6).** With the v2 changes in the working tree (or `git diff module-15-start` as the base-branch diff kind): `/annotate code-review` → pick the local diff → put `a` notes on at least two lines (e.g. the `status` validation, the `company.strip() or None` line) → **Continue with LLM review** (M4 §4.4).
   **Expected:** a `/review` turn whose report references your notes; `read`/`grep` cards behind it. Fix anything real in a fresh prompt; ignore pre-existing issues (say so in notes).
2. **Commit (E6).** If you committed per slice in Phase 2 you are done — verify `git log --oneline module-15-start..` ≥ 3. Otherwise commit now, one slice at a time: `git add tools/migrate.py tools/seed_db.py generated/ data/lab.sqlite tests/test_migrate.py` → `omp commit --dry-run` → `omp commit -c "v2 slice A: migration"`; repeat for B, C, D.
   **Expected:** each `omp commit` prints its generated message and `git log -1` shows it; ≥ 3 commits total.
3. **Extension/hook or MCP (E8).** Pick one and *use* it in this flow:
   - Hook: `.omp/hooks/pre/guard-db.ts` that blocks any `bash` command containing `data/lab.sqlite` unless it starts with `python3 tools/migrate.py` or `git` (M12 §12.2 shape: `pi.on("tool_call", …) → { block: true, reason }`). Restart omp, ask it to `rm data/lab.sqlite`, capture the blocked card.
   - MCP: `.omp/mcp.json` with the M12 `lab-fs` server; `/mcp list`; ask omp to read a file through the `mcp__lab-fs_…` tool.
   **Expected:** a blocked-tool card whose text is your `reason`, or an `mcp__…` tool card.
4. **Export / share / cost (E10).** `/export notes/capstone.html` → path printed and opened; `/share` → `https://my.omp.sh/s/<id>#<key>` (secrets redacted by default, `share.redactSecrets: true`); in a shell `omp stats --summary`.
   **Expected:** the HTML file exists; the share URL and the stats summary (total cost, per-model) pasted in notes.
5. **Learn (E11).** Enable memory once: `omp config set memory.backend local && omp config set autolearn.enabled true`, restart. Prompt with the gotcha you actually hit (typical: "regenerating `generated/` with a full seed silently replaces the migrated DB", or "`money()` shows 10× because issue #1 is unfixed — not a v2 bug"):

   ```text
   learn: store this lesson for omp-course-lab: <your one-sentence gotcha>. If it is a repeatable procedure, also create a managed skill "lab-regenerate-generated" whose body is the exact command sequence.
   ```

   **Expected:** `Lesson stored.` (and `Created managed skill "lab-regenerate-generated".` if you asked); `read memory://root/learned.md` shows the bullet; the skill file is at `~/.omp/agent/managed-skills/lab-regenerate-generated/SKILL.md`.

**Guided:**
- *Goal:* a review by the bundled `reviewer` **and** `security-reviewer` agents, reconciled with your own `/annotate` notes, then commits pushed to your fork.
- *Hints:* spawn both agents in one batch (M10 §10.7) targeting `git diff module-15-start`; commit with `omp commit --push`.
- *Checkpoints:* (a) both reports arrive in one batch card, readable via `read agent://<id>`; (b) your reconciliation note says which findings you kept, dropped, or already had as `/annotate` notes.
- *Pass:* the two `agent://<id>` reports and the reconciliation note in `notes/capstone.md`; the commits are visible on your fork's branch; E6/E8/E10/E11 below.

**Stretch:**
- *Goal:* `/collab` while committing (guest can watch but only the host runs `omp commit`); `.omp/WATCHDOG.md` + `advisor.enabled: true` for the review turn; `omp --prewalk` for a repeat of slice C and compare `omp stats --summary`.
- *Pass:* as the README Lesson 15.1 Stretch (a)–(c): `/collab status` shows a second participant; the advisory text is quoted in `notes/capstone.md` with the diff it changed; two `omp stats --summary` numbers and one sentence on the `@smol` hand-off.

**Pass (E6, E8, E10, E11):** review report + your notes visible in the transcript; ≥ 3 commits; blocked-card or `mcp__` card; `notes/capstone.html`, a share URL, a stats summary; `Lesson stored.` card and the `learned.md` bullet.

---

## Hand-in

`notes/capstone.md` with E1–E11 (paths, pasted card text, command outputs), `notes/capstone.html`, the Agent Hub screenshot, the browser screenshot, and your branch name. The instructor grades with `rubric.md` and compares against the `capstone-solution` tag.
