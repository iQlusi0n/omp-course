# Module 10 — Coursework

Built against `omp/18.3.5`. Start state: `cd omp-course-lab && git checkout module-10-start`. All outputs the learner writes go under `notes/` (gitignored). Test command for the lab: `python3 -m unittest discover -s tests`.

Prerequisites on the learner machine: git, Python 3, a configured `smol` role model (`omp config get modelRoles` shows the map) because `scout`, `sonic` and the custom `test-writer` resolve `@smol`; a `slow` role model for 10.7 reviewers (`@slow`). Nothing else.

Tiers: **W** exact steps · **G** goal + hints + checkpoints · **S** goal only (notes in `solutions/instructor-notes.md`). Every exercise names an observable pass condition.

---

## Exercise 1 (W, ~15 min) — One batch, three scouts, typed results

1. In the lab session prompt, verbatim:
   ```
   Use ONE task call with three scout items named ApiScout, CliScout, WebScout.
   context: "omp-course-lab: Python stdlib HTTP API in api/, argparse CLI in cli/, static signup form in web/. Report structure only; do not propose changes."
   Each task: map its directory (api/, cli/, web/) — every module, its purpose, public entry points.
   outputSchema for every item:
   {"type":"object","required":["modules"],"properties":{"modules":{"type":"array","items":{"type":"object","required":["path","purpose"],"properties":{"path":{"type":"string"},"purpose":{"type":"string"},"entrypoints":{"type":"array","items":{"type":"string"}}}}},"risks":{"type":"array","items":{"type":"string"}}}}
   Do not wait for results.
   ```
   **Expected:** one `task` card: ``Spawned 3 background agents using scout.`` + three ``- `<name>` (job …)`` lines.
2. Press `Alt+A` while they run.
   **Expected:** three rows `running`, parent `Main`, role `@smol`; header `3 running`. Press `t` to see the tree; `Esc` to close.
3. Wait for the three async-result messages (each ends ``… is now idle — message it via `write agent://<name>` …``).
   **Expected:** each preview is JSON with a `modules` array.
4. Prompt: `read agent://ApiScout/modules/0` then `read agent://WebScout/modules`.
   **Expected:** a single object `{ "path": "api/…", "purpose": "…" … }`; then an array. No line numbers (discrete-value extraction).
5. Open `Alt+A` again.
   **Expected:** the three rows are `idle` and each shows a **cost** and token count (no `usage —`).

**Pass:** three structured results readable via `agent://<name>/modules/0`; the Hub shows a cost per agent.

---

## Exercise 2 (G, ~25 min) — `test-writer` on two packages, isolated, merged

**Goal:** define `.omp/agents/test-writer.md` (`tools: read, grep, glob, edit, write, bash`; `model: "@smol"`; an `output` schema with `result`, `test_command`, `files_changed`, `tests_added`), dispatch it on `api/` and `cli/` in the **same** batch call with `isolated: true` on both items, and end with a passing test suite in your checkout.

**Hints:**
- `omp agents unpack --dir /tmp/agents` shows the frontmatter style (`output` uses `properties` / `optionalProperties` / `elements`); a ready file is in `solutions/test-writer.md`.
- `task.isolation.enabled` is **off** by default: put `task.isolation.enabled: true` in `omp-course-lab/.omp/config.yml` (or `omp config set task.isolation.enabled true`) before dispatching; `isolated` then appears per item as long as plan mode is off. Default merge is `patch` with auto-apply; set `task.isolation.merge branch` if you want `omp/task/<id>` branches instead.
- Put the test command in `context`; put the package in each `task`.
- Isolated agents finish `parked` with no reviver — collect everything from `agent://<id>` and the Hub inspector (`patchPath` / `branchName`).

**Checkpoints:**
1. `read history://` lists `test-writer`-based agents after dispatch (definitions alone are not listed).
2. Both async results are JSON with `"result": "pass"` and a non-empty `tests_added`.
3. `Alt+A` → inspector for each shows a patch path (patch mode) or branch name + base SHA (branch mode).
4. `git status` shows only new/changed files under `tests/`.

**Pass:** two patches (`<id>.patch` in the session artifacts) or two `omp/task/<id>` branches exist; after integration `python3 -m unittest discover -s tests` exits 0.

**If a patch fails to apply** (both agents touched the same test file): the `.patch` is retained — `git apply --3way <patchPath>`; resolve with `read <file>:conflicts` + `conflict://<N>` (Module 4).

---

## Exercise 3 (G, ~15 min) — Steer one, kill another

**Goal:** with two `task` children running long, deliberately over-scoped jobs, change one child's scope mid-flight from the composer via `write agent://<id>`, and kill the other from the Hub.

**Hints:**
- Give both children explicit `name`s so ids are predictable (`Alpha`, `Beta`).
- `write agent://Alpha` needs non-empty `content`; the tool returns a delivery receipt. It steers a running turn or prompts an idle one.
- Hub: `Alt+A`, `j`/`k` to `Beta`, `x` kills immediately (abort → release). `Esc` in a focused child only returns to the main session.
- Alternative kill without the Hub: `write proc://Beta/kill` (no content).

**Checkpoints:**
1. Receipt text for the `write agent://Alpha` call.
2. `read history://Alpha` shows your steer message and a shorter subsequent turn.
3. Hub row for `Beta` reads `aborted`; the delivered result for Beta reports the abort and points at `history://Beta`.
4. `write agent://Beta` now fails (aborted is terminal) while `read history://Beta` still works.

**Pass:** Alpha's transcript contains the steer text and its final output reflects the reduced scope; Beta's status in the Hub is `aborted`.

---

## Exercise 4 (G, ~30 min) — `workpool()` lint-fix over 15 files vs. separate spawns

**Goal:** from a Python eval cell, define a stdlib `@tool lint(path)` (unused imports, trailing whitespace, missing final newline), run a `workpool('sonic', name='lintfix', tools=['lint'])` over every `*.py` under `api/`, `cli/`, `tests/` (15 files at `module-10-start`: 4 + 5 + 6; **never** `generated/`), then repeat the job as one batch `task` call with 15 `sonic` items, and compare wall time and cost. Write the comparison to `notes/m10.md`.

**Hints:**
- `%load ../modules/M10-subagents-parallel-work/solutions/workpool-lint.py` (path relative to the lab root, where your session runs) gives you `lint`, `lab_files()`, `run_pool()`, `report()`.
- `pool.push(*items)` returns `lintfix#1 …`; there is no `pool.wait()` — end the cell, let results auto-deliver; the aggregate job is named `lintfix`. Only call the zero-argument `wait` tool if you have nothing else to do.
- The pool is bounded by `task.maxConcurrency` (default 32); `pool.status()` shows workers and context usage. A drained pool is closed — use a new name for a second run.
- Cost: `omp stats --summary` before/after each run, delta of `Total Cost` and `Requests`. Wall time: Hub header / per-row `active time`. Per-agent cost: Hub rows while live.
- Reset between runs: `git checkout -- api cli tests`.
- `task` items also accept `tools: ["lint"]` (kernel-defined tools are exposed to `task`, `agent()`, `workpool()` while `eval.tools.enabled` is on).

**Checkpoints:**
1. `display(tool.defined())` → `["lint"]`.
2. `run_pool(lab_files())` prints `{"pool": "lintfix", "items": [...15 ids], "status": {...}}`.
3. Aggregate `lintfix` delivery arrives once; `report(...)` shows `lint after` = 0 for every file.
4. Second run (batch `task`, 15 items) completes; `omp stats --summary` deltas recorded.

**Pass:** `notes/m10.md` contains a table with two rows (`workpool`, `15 task items`) and columns `agents | requests | wall time | cost`, plus the per-file before/after table with all "after" values `0`.

---

## Exercise 5 (S, ~15 min) — Vibe mode round trip

**Goal:** enter `/vibe`, spawn one `fast` and one `good` worker on independent workstreams in `cli/` and `api/`, `vibe_wait` for the first to settle, `vibe_send` a follow-up to the other, then exit the mode.

**Pass:** while in the mode the status line shows `Vibe`; after `/vibe` again, `Alt+A` shows both workers `aborted`; `read history://<worker>` still renders; `git diff --stat` shows only the files the briefs named.

---

## Exercise 6 (G, ~15 min) — Parallel review sweep (Lesson 10.7)

**Goal:** one batch call with three `reviewer` items — working copy (`git diff`), `HEAD` (`git show HEAD`), and `git diff main...conflict-lab` — plus one `security-reviewer` over `api/`; have the parent merge all findings into `notes/m10-review.md` sorted by priority.

**Hints:** name the target inside each `task`; `read agent://<id>/findings` is an array or missing (optional); `overall_correctness` is always present. Seed a real bug in the working copy first (Lesson 10.7 step 1) so `RevWorking` has something to find.

**Checkpoints:** four async deliveries; `read agent://RevWorking/overall_correctness` → `"incorrect"`; `read agent://Sec/coverage_summary` → a string.

**Pass:** `notes/m10-review.md` has one row per finding with `target | priority | title | file:line | confidence`, and quotes the security coverage summary.

---

## Self-check before Module 11

| Question | Where to verify |
|---|---|
| Which two top-level fields does a batch `task` call require? | `omp://tools/task.md` §Inputs — `context`, `tasks` |
| What approval mode do subagents run in, regardless of yours? | `yolo` (task.md §Flow 12) |
| Which Hub key revives, and what status must the agent have? | `r`, `parked` |
| Which file wins: `.omp/agents/scout.md` or bundled `scout`? | project (first-wins by exact name) |
| What is the default `task.isolation.merge`? | `patch` |
| Why is there no `pool.wait()`? | keeps the kernel free to serve `@tool` calls; results auto-deliver |
| Which two tools must be active for `workflowz` to inject? | `eval` and `task` |
| What happens to vibe workers on `/vibe` exit? | all killed |
