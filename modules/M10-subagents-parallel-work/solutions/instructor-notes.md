# Module 10 — instructor notes (solutions)

Built against `omp/18.3.5`. Everything below was checked against `omp://tools/task.md`, `omp://task-agent-discovery.md`, `omp://agent-hub.md`, `omp://tools/eval.md`, `omp://python-repl.md`, `omp://tools/wait.md`, `omp://vibe-mode.md`, `omp://magic-keywords.md`, `omp config list`, `omp agents unpack`, and live kernel introspection. The helper snippets (`workpool-lint.py`, `workpool-lint.js`) had their non-agent parts executed on the build machine; the agent-spawning parts follow the documented API verbatim.

## W — three scouts with `outputSchema`

Exact `task` call the learner's prompt should produce (they may see it in the card's arguments):

```json
{
  "context": "omp-course-lab: Python stdlib HTTP API in api/, argparse CLI in cli/, static signup form in web/. Report structure only; do not propose changes.",
  "tasks": [
    { "name": "ApiScout", "agent": "scout", "task": "Map api/: every module, its purpose, public entry points.", "outputSchema": { "type": "object", "required": ["modules"], "properties": { "modules": { "type": "array", "items": { "type": "object", "required": ["path", "purpose"], "properties": { "path": { "type": "string" }, "purpose": { "type": "string" }, "entrypoints": { "type": "array", "items": { "type": "string" } } } } }, "risks": { "type": "array", "items": { "type": "string" } } } } },
    { "name": "CliScout", "agent": "scout", "task": "Map cli/: …", "outputSchema": { "…": "same" } },
    { "name": "WebScout", "agent": "scout", "task": "Map web/: …", "outputSchema": { "…": "same" } }
  ]
}
```

Pass evidence: three async-result messages; `read agent://ApiScout/modules/0` returns an object with `path` and `purpose` (lab modules: `api/__init__.py`, `api/db.py`, `api/server.py`, `api/__main__.py`; `cli/__init__.py`, `cli/__main__.py`, `cli/commands.py`, `cli/format.py`, `cli/log.py`). Hub (`Alt+A`) rows show `cost` per agent once requests were made; `usage —` before the first request is normal.

Common failure: learner omits `context` → tool returns a validation error text with empty results. Second: learner writes `Scout` — names are case-sensitive.

Why `scout`'s own `output` schema does not interfere: per-item `outputSchema` has top precedence (`omp://tools/task.md` §Inputs).

## G1 — `test-writer` on two packages, isolated

Ship `solutions/test-writer.md` to `omp-course-lab/.omp/agents/test-writer.md`. Note the tool list adds `glob` and `write` to the outline's `read/grep/edit/bash`: `write` is required to create a new `tests/test_*.py`; `edit` only patches existing files. `yield` is auto-added.

Dispatch:

```json
{
  "context": "omp-course-lab. Test command: python3 -m unittest discover -s tests. Stdlib only.",
  "tasks": [
    { "name": "TwApi", "agent": "test-writer", "isolated": true, "task": "Package: api/. Add one unittest for the smallest untested public function." },
    { "name": "TwCli", "agent": "test-writer", "isolated": true, "task": "Package: cli/. Add one unittest for the smallest untested public function." }
  ]
}
```

- Default integration is **patch** (`task.isolation.merge: patch`, `task.isolation.apply: true`): both root patches apply to the learner's checkout after each child finishes. Two patches that create *different* `tests/test_api_*.py` / `tests/test_cli_*.py` files apply cleanly. If both children append to the same existing test file at the same anchor, the second patch fails to apply and stays at `<id>.patch` (Hub inspector → patch path) — `git apply --3way <path>` resolves.
- For the "two branches" reading of the pass condition: `omp config set task.isolation.merge branch` before dispatch → commits are cherry-picked onto the learner's branch; `omp/task/<id>` branches are the task branches. Either satisfies "two branches/patches".
- Pass: `python3 -m unittest discover -s tests` exits 0 after integration; `git status` shows only files under `tests/` (plus nothing else — the agent body forbids production edits).
- Isolated children land `parked` without a reviver: `write agent://TwApi` will fail; that is expected (README 10.4).
- `@smol` resolves through `modelRoles.smol`; if the learner's smol model is too weak to `yield` JSON, `schemaMode: "strict"` makes the failure explicit instead of a permissive warning.

## G2 — steer via `write agent://<id>`, kill from Hub

Spawn two `task` children with generous scope (e.g. "summarise every file under api/" and "summarise every file under cli/"). Then:

1. `write agent://<A>` with content `Change of scope: only api/server.py; stop after that.` — the receipt text confirms delivery. `read history://<A>` shows the message as a user-attributed entry in A's transcript and the subsequent shorter turn.
2. `Alt+A`, `j`/`k` to `<B>`, `x`. Row becomes `aborted`; the parent receives a failed/aborted delivery (doc: "aborted variant points at the transcript only"). `read history://<B>` still works; `write agent://<B>` does not (aborted is terminal).

Pass evidence: transcript of A contains the steer text; B's Hub status is `aborted`.

Equivalent from the composer without the Hub: `write proc://<B>/kill` (no content).

## G3 — `workpool()` lint pass vs. separate spawns (`notes/m10.md`)

Files at `module-10-start`: `api/**/*.py` (4) + `cli/**/*.py` (5) + `tests/**/*.py` (6, including `support.py` and `test_issues.py`) = 15 ≥ 10; **never** `generated/` (RULES fixture) and not `tools/` (mock provider must keep working). `lab_files()` globs at run time, so the count follows the checkout.

Run A (pool): `%load` `solutions/workpool-lint.py`, `pool, before = run_pool(lab_files())`, end the turn, wait for the `lintfix` aggregate delivery, then `write('notes/m10.md', report(lab_files(), before))`.

Run B (separate spawns): `git checkout -- api cli tests`, then one batch `task` call with 15 `sonic` items (one file each, `context` = the same pool context, and *no* `lint` tool unless the learner passes `tools: ["lint"]` per item — `task` items accept `tools` too, per `omp://tools/eval.md` §Kernel-defined tools).

Measurement:
- Wall time: Hub header / per-row `active time`, or the learner's stopwatch between spawn and last delivery.
- Cost: `omp stats --summary` before and after each run — take the delta of `Total Cost` and `Requests` (stats are per model/folder, not per agent; the Hub shows per-agent cost while rows are live). `omp stats --json` gives the same numbers machine-readably.

Expected shape of the table (numbers vary by model):

| approach | agents | requests | wall time | cost |
|---|---|---|---|---|
| `workpool('sonic')` 15 items | ≤ `task.maxConcurrency` workers, batched follow-ups | lower | similar | lower |
| 15 `sonic` task items | 15 | higher (15 fresh contexts) | similar (both bounded by `task.maxConcurrency`=32) | higher |

The pool wins on requests/cost because idle workers take follow-up batches with their context warm; with `eval.workpool.freshAgents: true` the two runs converge — a good discussion point.

Pass: `notes/m10.md` has the table with both rows filled and every file's "lint after" is 0.

## S — `/vibe`

`/vibe` → `vibe_spawn {cli:"fast", name:"Fixer", prompt:"…"}` and `{cli:"good", name:"Judge", prompt:"…"}` → `vibe_wait {timeout: 60}` → `/vibe` exits and kills both. Evidence: `Alt+A` shows both workers `aborted` after exit and `read history://Fixer` still renders. If the learner had plan mode paused, `/vibe` is refused — exit plan mode first.

## 10.3 Guided / Stretch

Project override of `scout`: file must be exactly `.omp/agents/scout.md` (case-sensitive name inside frontmatter, first-wins). The `lead` agent stretch: `spawns: test-writer, scout` auto-adds `task`; children are dot-qualified (`Lead.TwApi`) in `agent://`. Depth: `Lead` is depth 1, its children depth 2 — the default `task.maxRecursionDepth` (2) means the grandchildren get no `task` tool.

## 10.7 Guided

`notes/m10-review.md` is produced by the **parent** reading `agent://RevWorking/findings`, `agent://RevCommit/…`, `agent://RevBranch/…`, `agent://Sec/findings` and `agent://Sec/coverage_summary`. A reviewer with zero findings has no `findings` key (optional) — the parent must handle a missing path (read error → treat as empty).
