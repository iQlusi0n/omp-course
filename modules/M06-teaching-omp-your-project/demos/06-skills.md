# Demo 6.6 — Skills (~55 s)

Shell output below is verified on `omp/18.3.1`; session output is illustrative.

```text
$ find .omp/skills -type f
.omp/skills/release-checklist/SKILL.md
.omp/skills/release-checklist/report.md

$ omp read skill://release-checklist | head -4
---
name: release-checklist
description: Step-by-step checklist for cutting an omp-course-lab release (clean tree, tests, version bump, changelog, generated files, tag). Use when asked to "release", "cut a version", or "tag".
---
$ omp read skill://release-checklist/report.md | head -1
# Release <version> — checklist report
$ omp read skill://release-checklist/nope.md
File not found: /home/you/omp-course-lab/.omp/skills/release-checklist/nope.md
$ (cd api && omp read skill://release-checklist | head -2)        ← skills walk up from cwd
---
name: release-checklist

$ omp config get skills.enableSkillCommands
true

$ omp
> Which skills do you have available? Names and descriptions only.
- release-checklist — Step-by-step checklist for cutting an omp-course-lab release … Use when asked to "release", "cut a version", or "tag".

> /skill:release-checklist 1.1.0
▸ (custom message) The user invoked the skill "release-checklist" …
  [Skill directory: /home/you/omp-course-lab/.omp/skills/release-checklist]
  User: 1.1.0
▸ bash git status --porcelain
▸ bash python3 -m unittest discover -s tests
   Ran 48 tests in 0.71s
   OK (skipped=20)
▸ read skill://release-checklist/report.md
| Clean tree      | PASS | git status --porcelain (exit 0, empty) |
| Tests           | PASS | python3 -m unittest discover -s tests (exit 0) |
| Version         | FAIL | pyproject.toml version is 1.0.0; bump to 1.1.0 required |
…
| Tag (proposed)  | —    | git tag -a v1.1.0 -m "v1.1.0" (not run) |
```

Hidden ≠ disabled (Guided task): with `hide: true` the skill vanishes from the model's list, but `omp read skill://release-checklist` and `/skill:release-checklist` still work.
