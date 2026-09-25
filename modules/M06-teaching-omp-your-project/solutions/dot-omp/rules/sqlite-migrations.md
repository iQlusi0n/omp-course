---
description: How to change the SQLite schema behind data/lab.sqlite (migrations, seeding, tests). Read before touching api/db.py or any CREATE TABLE.
globs: ["api/db.py", "api/migrations/**"]
---
# SQLite schema changes

1. Never `ALTER TABLE` in place. Add a numbered file under `api/migrations/NNN_<slug>.sql`.
2. Every migration must be idempotent (`CREATE TABLE IF NOT EXISTS`, `INSERT OR IGNORE`).
3. Update the seed script so `data/lab.sqlite` can be rebuilt from scratch.
4. Add a test that opens a fresh in-memory DB, applies all migrations, and asserts the new column/table exists.
5. Run `python3 -m pytest -q tests/test_db.py` and show the output.
