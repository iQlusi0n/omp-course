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

**omp version.** Modules were written against `omp/18.3.1` and every command, key, setting and default was re-audited on `omp/18.3.5` (the binary updated mid-build). Where a demo says "captured on 18.3.1" that is literal; no behavioral difference was found between the two. Each module's `BUILD-NOTES.md` lists what was verified live, what is doc-derived, and what was removed as unverifiable.

**Known limits of the build machine** (see per-module `BUILD-NOTES.md`): no desktop, Chrome relay, LSP server, C compiler, debugger, or second collaborator was available, so 8.4 (C/DAP), 14.2 (computer use), 14.3 (collab) and interactive TUI overlays are documented from `omp://` docs and binary strings rather than live captures. Everything shell- or `omp -p`-reachable was executed.
