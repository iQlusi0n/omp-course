---
name: release-checklist
description: Step-by-step checklist for cutting an omp-course-lab release (clean tree, tests, version bump, changelog, generated files, tag). Use when asked to "release", "cut a version", or "tag".
---
# Release checklist

Work through every step in order; report each as PASS/FAIL with the command output.

1. **Clean tree** — `git status --porcelain` prints nothing.
2. **Tests** — `python3 -m unittest discover -s tests` exits 0.
3. **Version** — bump `version` in `pyproject.toml` (semver). It must be greater than the current value.
4. **Changelog** — `CHANGELOG.md` has a section for the new version. If the file or the section is missing, tell the user to run `/changelog <version>`.
5. **Generated files** — run `python3 tools/seed_db.py`, then `git diff --stat generated/ data/` prints nothing. Never hand-edit `generated/` (files start with `# GENERATED — do not edit`).
6. **Tag** — propose `git tag -a v<version> -m "v<version>"`; do **not** run it unless the user confirms.

Fill in the report template at `skill://release-checklist/report.md` and paste it as your final message.
