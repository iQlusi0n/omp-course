# omp-course — conventions

This repository is a hands-on course on `omp` (Oh My Pi). The spec is `COURSE-OUTLINE.md`; read it before changing content. These conventions apply to anyone editing the course with omp (they were also the rules the course was built under — see README "How this course was built").

## Ground truth
- Every command, flag, keybinding, setting key, file path, and default MUST be verified by reading the bundled docs at `omp://<file>` (index: `read omp://`) or the binary (`omp --help`, `omp <cmd> --help`). Cite doc files in a `Source:` line at the end of each lesson. Verify setting defaults from a directory with no `.omp/config.yml` so project overrides do not masquerade as defaults.
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

## Verification
- Run `python3 tools/check.py` before committing content changes (structure, template fields, prose length, Appendix C coverage).
- The lab (`omp-course-lab/`) is Python-only, stdlib only. Lab changes go to its own repository; then bump the submodule pointer here. Exercises that need debuggers, LSP servers, or Chrome state the learner's prerequisites explicitly.
