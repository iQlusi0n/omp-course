# omp-course — build conventions

This repository builds a hands-on course on `omp` (Oh My Pi). The spec is `COURSE-OUTLINE.md`. Read it before doing anything.

## Ground truth
- Every command, flag, keybinding, setting key, file path, and default MUST be verified by reading the bundled docs at `omp://<file>` (index: `read omp://`) or the binary (`omp --help`, `omp <cmd> --help`). Cite doc files in a `Source:` line at the end of each lesson.
- Third-party guides are not sources. Do not copy benchmark claims.
- If a doc contradicts the outline, the doc wins; note the deviation in the module's `BUILD-NOTES.md`.
- Record `omp --version` in each module README header.

## Layout
- Modules: `modules/MNN-<slug>/` containing `README.md` (lessons), `exercises.md`, `cheatsheet.md`, `demos/` (fenced transcripts), `solutions/` (instructor notes), `BUILD-NOTES.md` (deviations, gaps, unverifiable claims).
- Practice repo: `omp-course-lab/` per COURSE-OUTLINE.md Appendix A.
- Reference sheets: `reference/`.

## Lesson format
Use the lesson template in COURSE-OUTLINE.md §1 verbatim. Every exercise has an observable pass condition. Three tiers: Walkthrough (W), Guided (G), Stretch (S).

## Style
- Assume a developer who has used chat AI a little. Explain *why* in one paragraph, then *how* with exact keys/commands.
- Call out every setting that is off by default and the key to enable it.
- Fixture references use the numbers in `omp-course-lab/docs/ISSUES.md` / Appendix A.

## Environment for building
- Python 3 available; no node/bun/C compiler/debuggers on the build machine. The lab is Python-only. Exercises that need debuggers, LSP servers, or Chrome describe the learner's prerequisites explicitly.
