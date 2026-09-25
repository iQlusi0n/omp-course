# omp-course-lab — project context

Small Python (stdlib-only) HTTP service + CLI used by the omp course. No third-party packages.

## Layout
- `api/` — HTTP service on `http.server`, SQLite-backed (`data/lab.sqlite`). `api/__init__.py` re-exports the public functions.
- `cli/` — argparse client for the API.
- `web/` — static signup form (HTML + small JS).
- `generated/` — build output. **Never edit by hand**; change the generator input and regenerate.
- `tests/` — test suite. `notes/` — learner scratch output, gitignored.

## Commands
- Test: `python3 -m pytest -q` (if pytest is missing: `python3 -m unittest discover -s tests`)
- Lint: `python3 -m compileall -q api cli`
- Run API: `python3 -m api --port 8080`

## Conventions
- Python 3.10+, stdlib only. Ask before adding any dependency.
- Public functions live in `api/` and are re-exported from `api/__init__.py`; update the re-export when you rename.
- Every behavior change ships with a test. Run the suite before reporting done and show the command output.
- Keep diffs small; one concern per change. Do not reformat files you did not otherwise touch.

## Review expectations
- State what changed, which command verified it, and the exit status.
- If a request would touch `generated/`, stop and ask which generator input to change instead.

Architecture notes (expanded inline by omp at session start): @../docs/spec.md
