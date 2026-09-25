# Demo 6.3 — Rules directory (~55 s)

The shell part is verified; the in-session part is illustrative.

```text
$ ls .omp/rules
no-print-in-api.md  sqlite-migrations.md
$ head -4 .omp/rules/sqlite-migrations.md
---
description: How to change the SQLite schema behind data/lab.sqlite (migrations, seeding, tests). Read before touching api/db.py or any CREATE TABLE.
globs: ["api/db.py", "api/migrations/**"]
---
$ head -4 .omp/rules/no-print-in-api.md
---
alwaysApply: true
agents: main
---

$ omp read rule://sqlite-migrations            ← rule:// is per-session state; the shell has none
Unknown rule: sqlite-migrations
Available: none

$ omp
> Which rules are available to you, by name? Do not read any files.

From the rulebook: `sqlite-migrations` — "How to change the SQLite schema behind
data/lab.sqlite …" (globs api/db.py, api/migrations/**). Always-applied content is
also present (repository RULES and a logging rule for `api/`).

> I need to add a created_at column to the orders table. Before doing anything,
> tell me the procedure you must follow.
▸ read rule://sqlite-migrations
1. Never ALTER TABLE in place — add api/migrations/NNN_<slug>.sql
2. Idempotent statements only …
3. Update the seed script …
4. Add a fresh-DB test …
5. Run `python3 -m pytest -q tests/test_db.py` and show the output.

> Add a debugging print() to api/__init__.py.

The always-apply rule for `api/` forbids `print()` there; I'll add
`logging.getLogger(__name__).debug(...)` instead. Proceed?
```

Invisible rule (Guided task):

```text
$ printf 'Body without frontmatter.\n' > .omp/rules/ghost.md      # no description, no alwaysApply
(restart omp)
> read rule://ghost
▸ read rule://ghost
Unknown rule: ghost
Available: sqlite-migrations, no-print-in-api, RULES
```
