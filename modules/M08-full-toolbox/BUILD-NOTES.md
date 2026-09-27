# Module 8 — Build notes

Built against `omp/18.3.1` on a Linux x64 build machine with Python 3.13 only (no node, cc, gdb, lldb, pyright, pylsp, gh, IDA). Every command/flag/setting/default was read this session from `omp://` docs, `omp --help`, `omp <cmd> --help`, or `omp config list`/`get`; Python-server root markers and DAP adapter defaults were extracted from the `lsp/defaults.json` and `dap/defaults.json` blobs embedded in the 18.3.1 binary because `omp://lsp-config.md` names the servers but not their markers.

## Verified live (smoke runs on a throwaway copy of the lab layout under `/tmp`)

- `omp read` for: SQLite list / `:table` / `:table:key` / `?limit&order&where` / `?q=`; zip list / member / folder; PDF (`:1-4`, page markers, 1+3 context lines); `.ipynb` cell rendering; `:conflicts` → `conflict://1`; `https://github.com/can1357/oh-my-pi` (`Method: github-repo`); `xd://resolve` hint; bare `ssh://`; `omp://…:1-3`.
- `omp q --model web/duckduckgo -l 3 …` (boxed panel); `omp find -q "…" .` (hit + footer; judge resolved to TypeSafe on this machine).
- `eval` py: three cells with retained state and `await tool.read({...})` bridge (`omp -p --mode json`).
- `read xd://` in a stock session → exactly `xd://ast_edit`, `xd://debug`, `xd://lsp`; `write xd://lsp {"action":"status"}` → `No language servers configured for this project` (no server installed here).
- `ast_grep` (via `--config` overlay `astGrep.enabled: true`) with `print($$$A)` on `cli` → 4 matches with `meta:`; `ast_edit` preview → `write xd://resolve` → `Applied 4 replacements in 1 file.` → `grep` empty. File contents changed on disk as previewed.
- `debug` with debugpy 1.8.22 (wheel unpacked by hand + `python` shim): `launch` (entry stop) → `set_breakpoint` (`verified`) → `continue` (breakpoint stop) → `stack_trace` → `scopes` → `variables` (`profile = None (NoneType)`) → `evaluate` (`repl` empty, `watch` → `None`) → `terminate`.
- Defaults confirmed with `omp config get/list`: `tools.xdev=true`, `tools.xdevDocs=catalog`, `astGrep.enabled=false`, `astEdit.enabled=true`, `find.enabled=auto`, `debug.enabled=true`, `lsp.enabled/lazy/shared/diagnosticsOnWrite=true`, `lsp.formatOnWrite=false`, `eval.py/js=true`, `eval.tools.enabled=true`, `eval.autoBackground.enabled=false` (`thresholdMs=60000`), `python.kernelMode=session`, `web_search.enabled=true`, `providers.webSearchTimeoutSeconds=60`, `github.enabled=false`, `security.enabled=false`, `generate_image.enabled=false`, `speechgen.enabled=false`, `ida.enabled=true` (+`maxOpen=4`, `idleCloseSec=900`), `tts.localVoice=af_heart`, `read.defaultLimit=300`, `read.summarize.minTotalLines=100`, `images.questionTimeoutMs=300000`.

## Not verified live (documented shape only, flagged in the demos)

- LSP `rename` / `rename_file` output — no language server installable offline here (pip wheel download failed: network unreachable mid-build). Demo 8.3 §3 is explicitly marked "documented output shape, NOT a live capture".
- C debugging with gdb/lldb-dap, `github`, `security_scan`, `generate_image`, `tts`, `ida` cards — demo 8.5 states this; card bodies follow `omp://tools/*.md`.

## Deviations from the outline

- Outline 8.1 lists "security DBs NVD/OSV/KEV" under `web_search`. No `omp://` doc mentions NVD, OSV or KEV (grep over all docs: no match). **Dropped.**
- Outline 8.3 writes `--tools` "pinning" and `xd://` "discoverable devices" as if `tools.xdev` were a documented setting. `settings.md` does not list `tools.xdev`; it exists in `omp config list` (`tools.xdev=true`, `tools.xdevDocs`, `tools.xdevInlineDevices`) and is referenced in `tools/checkpoint.md`, `tools/memory_edit.md`, `system-prompt-customization.md`. Taught from those sources plus the live `read xd://` output.
- Outline 8.3 "`find` semantic search (judge-model prerequisite)": confirmed; added the nuance from `tools/find.md` that `find.enabled=auto` only enables the tool for a TypeSafe jev judge and that `on` allows any judge.
- Outline says `omp q --model web/<provider>`: `omp q --help` prints the `omp search` help (alias confirmed); `settings.md` also names `omp web-search`. All three listed.
- Outline 8.5 says toggling a gate takes effect "in the running session". Only `generate_image.md` and `tts.md` document live registration on toggle; `github.md` says the tool is created when `gh` is found; `security_scan.md` rechecks `security.enabled` per action. README says: image/tts live, others start a new session. `security_scan` is taught with "Settings → Tools → Security" per its doc.
- `/settings` panel: not documented in `tui.md`/`slash-command-internals.md`, but referenced by `keybindings.md`, `magic-keywords.md`, `memory.md`, `compaction.md` ("in `/settings`"), and `tools/github.md` ("Settings → Tools"). Mentioned once, with `omp config set` as the primary path.
- Lab detail: `debugpy` adapter command is literally `python -m debugpy.adapter` (from embedded `dap/defaults.json`); on `python3`-only systems the README supplies a `.omp/dap.json` override. Flagged as a prerequisite, not assumed.
- Lab detail: Python LSP auto-detect needs a root marker in the cwd. Requested (and LabRepo confirmed) a root `pyproject.toml` in `omp-course-lab`; README states the marker list from the binary.
- Lab facts (confirmed on disk during the wave-2 audit): `get_user` defined at `api/db.py:48`, re-exported by `api/__init__.py` (also in its `__all__` string list), used in `api/server.py`, `cli/commands.py`, `tests/test_db.py`, `tests/test_issues.py`; **all 10** `print(` calls are in `cli/commands.py` (`cli/__main__.py` has none; `cli/log.py` mentions `print(` only in its docstring) — `ast_grep print($$$A)` on `cli` returns 10 matches, verified with a live `omp -p --tools ast_grep` run; `cli/commands.py` does not import `logger`; `bin/crash.py` fails with `AttributeError: 'NoneType' object has no attribute 'name'` at line 39 in `display_name(user)`, called from `main()` line 45 over `WANTED_IDS = [1, 2, 99, 3]`, takes no argv, and its docstring requires a report line for every id plus exit 0; `bin/crash.c` derefs NULL `u` in `main()` line 45, compile `cc -g -O0 -o bin/crash bin/crash.c` (comment in the file), `bin/crash` gitignored; root `pyproject.toml` present; `data/lab.sqlite` tables `orders` (72), `schema_version` (1), `users` (12), `orders` columns `id user_id created_at status total_cents`; `fixtures/bundle.zip` members `README.md`, `data/sample.csv`, `config.json`; `docs/spec.pdf` 3 pages / 118 converted lines; no `.ipynb` in the lab; `python3 -m unittest discover -s tests` → `OK (skipped=20)` on `main`.

## Observed behaviour worth knowing (recorded in the lesson)

- debugpy `evaluate` with the default `repl` context returned an empty `Result:` for a `None` value; `context: "watch"` returned `Result: None / Type: NoneType`. Documented as a gotcha in 8.4.
- `ast_edit` preview pairs render as `-LINE:COL` in a `--tools` session without `edit` (no hashline anchors), and as `-LINE:text` under `[path#TAG]` in a normal session — both shapes described in demo 8.3.
- `read docs/spec.pdf` (no selector) returns the converted text with a hashline header; a bounded `:1-4` adds 1 leading + 3 trailing context lines (matches `tools/read.md`).

## Wave-2 audit (omp 18.3.1)

Every command, flag, key, setting, path, scheme and default in README/exercises/cheatsheet/solutions was re-checked against `omp://` docs, `omp --help` / `omp <cmd> --help`, `omp config get`, and the lab on disk. Live checks this pass: `omp read` on the real lab (`data/lab.sqlite`, `:orders`, `:users:1`, `?limit`/`order`/`where`, `?q=`, `where … LIMIT` rejection text, `fixtures/bundle.zip`, `:README.md`, `:data`, `docs/spec.pdf:1-40` footer, `xd://` from the CLI, bare `ssh://`, `https://github.com/can1357/oh-my-pi` → `Method: github-repo`), `omp find -q … api` (header `· τ 0.20 · strongest first`, footer `judged N`), `omp -p --tools ast_grep` with an `astGrep.enabled` overlay (10 matches in `cli/commands.py`), `omp models --kind judge`, and the embedded `lsp/defaults.json` / `dap/defaults.json` blobs in the binary (pyright/pylsp root markers, debugpy `python -m debugpy.adapter`, gdb `stopAtBeginningOfMainSubprogram`).

### Fixed (wrong or lab-misaligned)

- 8.1: `fixtures/bundle.zip:config` is a file, not a folder → `:data`; `orders` has `total_cents`, not `amount` (concept list, cheat sheet, demo note); table list includes `schema_version`; `docs/spec.pdf:1-40` footer is `Use :44 to continue` (bounded range adds 3 trailing context lines), not `:41`.
- 8.2: bridge `text` is three tables (`orders (72 rows)\nschema_version (1 rows)\nusers (12 rows)`).
- 8.3: `ast_grep` count is 10 in `cli/commands.py` (was "sum of `grep -c` over `cli/*.py`", which would count the two docstring mentions in `cli/log.py`); apply message `Applied 10 replacements in 1 file.`; the missing `logger` import is in `cli/commands.py` (not `cli/__main__.py`); judge chain now quotes the built-in chain from `omp://environment-variables.md` (`typesafe/jev-latest`, `openrouter/~typesafe/jev-latest`, `tiny`, `smol`, `default`, active model) instead of the example YAML in `settings.md`.
- 8.4: failing line is 39, local `user`, caller `main()` line 45; the fix must keep exit 0 and print a line for id 99 (fixture docstring), so the instructor note "return 1" was wrong; C deref is in `main()` line 45 with local `u`; the stretch's conditional breakpoint now uses the fixture's own loop (`user_id = 99` first stop) because `bin/crash.py` ignores argv.
- Demos 8.1–8.4 carry a "Lab values" paragraph mapping the throwaway-copy captures to the real fixture values.

### Removed (unverifiable)

- "`python bin/crash.py 1` (a valid id) never stops" — `bin/crash.py` takes no arguments; there is no valid-input run to compare. Replaced by the in-loop comparison.
- `retry.fallbackChains.judge` default "`typesafe/jev-preview`, `@tiny`, `@smol`, `@default`" — that list is the *example* config in `omp://settings.md`, not a documented default; `omp config get modelRoles.judge` reports `Unknown setting`. Replaced by the built-in chain documented in `omp://environment-variables.md`.
- `docs/analysis.ipynb` as a lab notebook fixture — the lab ships no notebook; cheat sheet now says so.
- "`cli/__main__.py` may lack a `logger` import" / prints in `cli/__main__.py` — the file has no `print` calls.
- `fixtures/bundle.zip:config` "lists a folder" — no such folder in the lab archive.

### Verified unchanged (spot list)

`omp q` = `omp search` = `omp web-search` (`cli-reference.md`, `settings.md`, `omp q --help`); `-l/--limit`, `--model`, `--recency` on `omp search`; `omp read`, `omp ssh add --host --user`, `omp find -k --hidden --json -q`, `omp say --voice/--out`, `omp setup python|speech --check`, `omp models --kind image`; flags `--tools`, `--no-tools`, `--no-lsp`, `--config`, `-p`, `--no-session`, `--mode json`; `Ctrl+O` (`app.tools.expand`); `/export [path]`; all 37 setting defaults listed under "Defaults confirmed" plus `tools.approvalMode=yolo`, `read.summarize.prose=false`; every tool field/action/output string quoted in 8.1–8.5 against `omp://tools/{read,write,web_search,eval,lsp,ast-grep,ast-edit,find,debug,github,security_scan,generate_image,tts,ida}.md`, `python-repl.md`, `lsp-config.md`, `resolve-tool-runtime.md`, `local-models.md`, `keybindings.md`. Fixture references: all exercises point at files that exist in `omp-course-lab` (`data/lab.sqlite`, `fixtures/bundle.zip`, `docs/spec.pdf`, `api/db.py`, `api/__init__.py`, `cli/commands.py`, `cli/log.py`, `bin/crash.py`, `bin/crash.c`, `pyproject.toml`, `notes/`) or at seeded issue #1 (`docs/ISSUES.md`), and each has an observable pass condition.

## Appendix C rows covered

`read` multi-format, `ssh://`, `pr://`, `issue://`, URLs (8.1) · `web_search` providers, `omp q` (8.1) · `eval` kernels, `%pip`, tool bridge, `completion()` (8.2) · LSP tool + `lsp.json` (8.3) · `ast_grep`, `ast_edit` + `xd://resolve` (8.3) · `find` semantic search (8.3) · `xd://` devices, `--tools` (8.3) · `debug` (DAP), `.omp/dap.json` (8.4) · `github`, `security_scan`, `generate_image`, `tts`, `ida` (8.5). `write` to archives/SQLite rows and `conflict://` writes covered in 8.1.
