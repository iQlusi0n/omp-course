---
description: Summarize what changed in the lab since a git ref (default HEAD~3)
---

Write a three-line stand-up note for omp-course-lab:

1. Run `git log --oneline $ARGUMENTS..HEAD` (if `$ARGUMENTS` is empty, use `HEAD~3`) and `git diff --stat $ARGUMENTS..HEAD`.
2. Line 1: what shipped. Line 2: what is in progress (uncommitted changes from `git status --short`). Line 3: blockers, or "none".
3. Do not edit any files.
