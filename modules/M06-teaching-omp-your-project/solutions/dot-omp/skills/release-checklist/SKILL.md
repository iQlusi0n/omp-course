---
name: release-checklist
description: Step-by-step checklist for cutting an omp-course-lab release (clean tree, tests, version bump, changelog, generated files, tag). Use when asked to "release", "cut a version", or "tag".
---
# Release checklist

Work through every step in order; report each as PASS/FAIL with the command output.

1. **Clean tree** — `git status --porcelain` prints nothing.
2. **Tests** — `python3 -m pytest -q` exits 0.
3. **Version** — bump `VERSION` (one semver line). It must be greater than `git describe --tags --abbrev=0`.
4. **Changelog** — `CHANGELOG.md` has a section for the new version. If it is missing, tell the user to run `/changelog <version>`.
5. **Generated files** — regenerate, then `git diff --stat generated/` prints nothing. Never hand-edit `generated/`.
6. **Tag** — propose `git tag -a v<version> -m "v<version>"`; do **not** run it unless the user confirms.

Fill in the report template at `skill://release-checklist/report.md` and paste it as your final message.
