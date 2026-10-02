# Working with omp — a hands-on course

A 15-module, ~22-hour course on driving `omp` (Oh My Pi, https://omp.sh), the terminal coding agent. Written for developers who have used AI assistants a little and want to run an autonomous agent well.

- **Spec:** `COURSE-OUTLINE.md` — audience, design rules, per-module scope, coverage matrix.
- **Modules:** `modules/M01-…` through `modules/M15-…`. Each has `README.md` (lessons), `exercises.md`, `cheatsheet.md`, `demos/`, `solutions/` (instructor), `BUILD-NOTES.md` (deviations from spec, unverifiable claims dropped).
- **Practice repo:** `omp-course-lab/` — a git submodule (its own repository, so it can carry the `module-N-start` tags and the `conflict-lab` / `capstone-solution` branches). Python-only lab with seeded issues (`docs/ISSUES.md`) and fixtures.
- **Reference sheets:** `reference/`.
- **Coverage:** `COVERAGE-REPORT.md` — Appendix C rows vs. what modules actually cover.

## Learner quick start

```sh
git clone --recurse-submodules <course repo url>
cd omp-course/omp-course-lab
git checkout module-1-start
python3 -m unittest discover -s tests     # expect: OK (skipped=20)
cd .. && open modules/M01-setup-first-contact/README.md
```

Already cloned without submodules? `git submodule update --init`.

## Repository layout and checks

| Path | Purpose |
|---|---|
| `modules/`, `reference/` | Learner-facing content and instructor solutions |
| `omp-course-lab/` | Submodule → sibling repo `omp-course-lab` |
| `tools/check.py` | CI: module structure, lesson template fields, prose line length, Appendix C coverage |
| `tools/coverage_check.py` | Regenerates `COVERAGE-REPORT.md` (CI fails if it is stale) |
| `.omp/` | omp project config for contributors: conventions (`AGENTS.md`, `RULES.md`) and the `course-builder` / `course-verifier` agent definitions used to build the course. Build-time setting overrides were removed before publishing. |
| `.github/workflows/check.yml` | Runs the above plus the lab suite on every push/PR |

Contributing a fix: edit the module, run `python3 tools/check.py`, and if you changed a fact about omp cite the `omp://` doc in the lesson's `Source:` line and note it in that module's `BUILD-NOTES.md`. Lab changes go to the `omp-course-lab` repo; after merging there, bump the submodule pointer here. The `module-N-start` tags must keep pointing at the lab's `main` HEAD (`for t in $(git tag -l 'module-*'); do git tag -f $t main; done`).

## How this course was built

Built with omp itself: one orchestrating session, one `course-builder` subagent per module in isolated worktrees, then a `course-verifier` pass that re-checked every command, key, and setting against the bundled `omp://` docs and the binary. See `.omp/agents/` and `COURSE-OUTLINE.md` Appendix D.

**omp version.** Modules were written against `omp/18.3.1` and every command, key, setting and default was re-audited on `omp/18.3.5` (the binary updated mid-build). Where a demo says "captured on 18.3.1" that is literal; no behavioral difference was found between the two. Each module's `BUILD-NOTES.md` lists what was verified live, what is doc-derived, and what was removed as unverifiable.

**Known limits of the build machine** (see per-module `BUILD-NOTES.md`): no desktop, Chrome relay, LSP server, C compiler, debugger, or second collaborator was available, so 8.4 (C/DAP), 14.2 (computer use), 14.3 (collab) and interactive TUI overlays are documented from `omp://` docs and binary strings rather than live captures. Everything shell- or `omp -p`-reachable was executed.
