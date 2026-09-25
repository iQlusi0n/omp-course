# Working with omp — a hands-on course

A 15-module, ~22-hour course on driving `omp` (Oh My Pi, https://omp.sh), the terminal coding agent. Written for developers who have used AI assistants a little and want to run an autonomous agent well.

- **Spec:** `COURSE-OUTLINE.md` — audience, design rules, per-module scope, coverage matrix.
- **Modules:** `modules/M01-…` through `modules/M15-…`. Each has `README.md` (lessons), `exercises.md`, `cheatsheet.md`, `demos/`, `solutions/` (instructor), `BUILD-NOTES.md` (deviations from spec, unverifiable claims dropped).
- **Practice repo:** `omp-course-lab/` — Python-only lab with seeded issues (`docs/ISSUES.md`), fixtures, and `module-N-start` tags.
- **Reference sheets:** `reference/`.
- **Coverage:** `COVERAGE-REPORT.md` — Appendix C rows vs. what modules actually cover.

## Learner quick start

```sh
git clone <this repo>
cd omp-course/omp-course-lab
git checkout module-1-start
python -m unittest discover -s tests     # should pass
cd .. && open modules/M01-setup-first-contact/README.md
```

## How this course was built

Built with omp itself: one orchestrating session, one `course-builder` subagent per module in isolated worktrees, then a `course-verifier` pass that re-checked every command, key, and setting against the bundled `omp://` docs and the binary. See `.omp/agents/` and `COURSE-OUTLINE.md` Appendix D.

omp version used for verification: see each module's README header.
