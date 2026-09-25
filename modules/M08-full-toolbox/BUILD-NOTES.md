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
- Lab facts used from LabRepo's message (not yet on disk when this module was written): `get_user` defined in `api/db.py`, re-exported by `api/__init__.py`, used in `api/server.py`, `cli/commands.py`, `tests/`; prints in `cli/commands.py` and `cli/__main__.py`; `cli/log.py` exports `logger`; `bin/crash.py` fails with `AttributeError: 'NoneType' object has no attribute 'name'` in `display_name(user)`; `bin/crash.c` NULL `struct user*` deref, compile `cc -g -O0 -o bin/crash bin/crash.c`; tests `python3 -m unittest discover -s tests`. If the lab diverges, update README 8.3 step 3/5, 8.4 step 1/4, and `solutions/README.md`.

## Observed behaviour worth knowing (recorded in the lesson)

- debugpy `evaluate` with the default `repl` context returned an empty `Result:` for a `None` value; `context: "watch"` returned `Result: None / Type: NoneType`. Documented as a gotcha in 8.4.
- `ast_edit` preview pairs render as `-LINE:COL` in a `--tools` session without `edit` (no hashline anchors), and as `-LINE:text` under `[path#TAG]` in a normal session — both shapes described in demo 8.3.
- `read docs/spec.pdf` (no selector) returns the converted text with a hashline header; a bounded `:1-4` adds 1 leading + 3 trailing context lines (matches `tools/read.md`).

## Appendix C rows covered

`read` multi-format, `ssh://`, `pr://`, `issue://`, URLs (8.1) · `web_search` providers, `omp q` (8.1) · `eval` kernels, `%pip`, tool bridge, `completion()` (8.2) · LSP tool + `lsp.json` (8.3) · `ast_grep`, `ast_edit` + `xd://resolve` (8.3) · `find` semantic search (8.3) · `xd://` devices, `--tools` (8.3) · `debug` (DAP), `.omp/dap.json` (8.4) · `github`, `security_scan`, `generate_image`, `tts`, `ida` (8.5). `write` to archives/SQLite rows and `conflict://` writes covered in 8.1.
