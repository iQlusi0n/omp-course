---
name: lab-conventions
description: Use when editing omp-course-lab. Test command, layout, and the directories that must never be edited.
---

# omp-course-lab conventions

- Run the test suite with `python -m unittest discover -s tests` before claiming a change works.
- `api/` is a stdlib `http.server` service backed by `data/lab.sqlite`; `api/__init__.py` re-exports the public functions.
- `cli/` is an argparse client. Keep `print()` calls there — Module 8 uses them as a codemod fixture.
- Never edit anything under `generated/`.
- Seeded issues are numbered in `docs/ISSUES.md`; refer to them as "issue #N" in commit messages.
