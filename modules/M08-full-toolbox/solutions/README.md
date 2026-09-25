# Module 8 — Instructor notes (solutions)

Grading is by observable artefacts: cards in the transcript (`/export notes/m8.html` if you want a file), files under `notes/`, and shell checks. Learner machines vary; the notes below say what to accept and what to look for when a step fails.

## 8.1 `read`

- **W four cards.** Accept any PDF converter output that begins with `<!-- Page 1 -->`. If the learner's card shows a `bash` call to `pdftotext`/`sqlite3`/`unzip`, the prompt did not name `read` — have them prefix the path with `read `. `Method:` for the GitHub URL should be `github-repo`; if the network is blocked the card shows `Method: failed` — accept the header structure and move on.
- **W write.** The archive write rewrites the whole zip (temp file + rename); `git status` shows `fixtures/bundle.zip` modified. The SQLite insert returns `Inserted row into users`; primary key is assigned by SQLite. Restore both with `git checkout --`.
- **G busiest month.** Reference answer: `python3 -c "import sqlite3;print(sqlite3.connect('data/lab.sqlite').execute('select substr(created_at,1,7),count(*) from orders group by 1 order by 2 desc limit 1').fetchone())"`. Accept `?q=` or a `:orders?order=…` approach as long as no `bash` card appears. A learner who used `?where=… LIMIT 1` will see `where` rejected — that is the intended lesson about the `where` validator.
- **G pinned provider.** `web/duckduckgo` and `web/startpage` are keyless. If one is bot-walled the panel shows an error and the other should still work; accept one success plus one documented failure.
- **S ssh.** `omp ssh add self --host 127.0.0.1 --user $USER`; a bare `read ssh://` lists `self`. `diff` must ignore the `[path#TAG]` hashline header on the local read — that is why the pass condition uses `:raw`.

## 8.2 `eval`

- **W retained state.** The tell-tale of a fail is a second cell that re-opens the DB. `display(await tool.read(...))` must show a dict with `text` and `details` — if the learner sees `<coroutine object …>` they forgot `await`.
- **W reset.** Nonzero exit plus `NameError` is the pass. `%reset` (the magic) also works but keeps the kernel; either is fine.
- **G plot.** Debian/Ubuntu system Python has no pip → `%pip` fails. Fix: `python3 -m venv ~/.omp/python-env && ~/.omp/python-env/bin/pip install matplotlib`, restart omp (interpreter resolution picks `~/.omp/python-env`). Verify `omp setup python --check`. The card should render the figure inline even before `savefig`; `plt.show()` is harmless under Agg.
- **G completion.** `.wait()` returns parsed data when `schema` is given; accept any month key from `by_month`. If the learner passes `model="haiku"` it fails: only `smol|default|slow` tiers are valid.
- **S %load + timeout.** Timeout text: `eval cell timed out after 30s; kernel interrupted but remains running. Reset the kernel via { reset: true } if state appears corrupted.` The function survives because the interrupt only raises `KeyboardInterrupt` inside the sleeping cell.

## 8.3 code intelligence

- **Server choice.** pyright renames across files reliably; pylsp (jedi) usually does too for this small tree but can miss the `__init__.py` re-export — if it does, accept a manual `edit` for that one file and note it. `basedpyright` and `ty` are also auto-detected. Root markers are checked in the **cwd only**: learners who start omp in `api/` get `No language servers configured`.
- **W status.** `(configured, not started)` is correct with `lsp.lazy=true`; the server starts on the first real action.
- **W rename.** Expected file set: `api/db.py`, `api/__init__.py`, `api/server.py`, `cli/commands.py`, at least one `tests/*.py`. String literals (`__all__`, docstrings, `docs/`) are not renamed — the walkthrough's step 6 covers that. Tests must pass after.
- **W/G codemod.** In hashline mode the preview pairs read `-N:print(...)` / `+N:logger.debug(...)` under a `[cli/…#TAG]` header; in a `--tools` session without `edit` it is `-N:COL`. Both are fine. Files: `cli/commands.py` (≈10 replacements) and `cli/__main__.py`. `cli/__main__.py` may lack a `logger` import → `NameError` in tests → learner adds `from cli.log import logger` with `edit`. Multi-arg `print(a, b)` becomes `logger.debug(a, b)` (format-string semantics); the lab's prints are single f-strings so tests stay green. If a learner writes `out: logger.debug(f"$$$A")` or similar, the preview will show the literal — reject and explain 1:1 substitution.
- **Apply protocol.** The model normally writes `xd://resolve` itself when asked to "apply"; if it does not, the session injects a reminder; a learner can also type `write xd://resolve with reason "…"`. `Nothing to resolve` on a second attempt is expected.
- **G find.** With `find.enabled=auto` the tool exists only when the judge resolves to `typesafe/jev-*`; without a TypeSafe key `omp config set find.enabled on` lets the fallback chain (`@tiny`, `@smol`, `@default`) judge — slower and pricier but the footer proves it ran. Expected top hit: `api/server.py` around the `/users/<id>` handler.
- **S lsp.json.** `{"servers":{"pylsp":{"disabled":true}},"idleTimeoutMs":120000}` in `<lab>/.omp/lsp.json`; `lsp reload` with `file:"*"` is required because the per-cwd config cache is not invalidated automatically. `rename_file` sends `willRenameFiles`; pyright rewrites imports, then omp moves the file and sends `didRenameFiles`. If the server returns no edits, imports must be fixed by hand — accept with a note.

## 8.4 DAP

- **Prerequisite trap #1:** the built-in adapter command is `python -m debugpy.adapter`. On systems with only `python3`, either `ln -s $(which python3) ~/.local/bin/python`, use a venv (which provides `python`), or add the `.omp/dap.json` override from the README. Symptom: `No debugger adapter available. Installed adapters: …`.
- **Prerequisite trap #2:** debugpy installed for a different interpreter than `python` → `DAP adapter exited (code 1): … No module named debugpy`.
- **W.** Card sequence and texts are in `demos/8.4-dap-debug.md`. The lab's crash is `AttributeError: 'NoneType' object has no attribute 'name'` in `display_name(user)`; the local is `user`. `evaluate` in `repl` context shows an empty `Result:` for `None` (observed on debugpy 1.8.22); `watch` shows `None`. Accept either the `variables` card or the `watch` evaluate as the "report the variable" evidence. Fix: guard in `main()` (print "no such user" and return 1) or make the lookup raise — anything that makes `python bin/crash.py` exit 0 for the default input.
- **G C.** `cc -g -O0 -o bin/crash bin/crash.c`; the binary is gitignored or should be. With gdb, `launch` stops at the beginning of `main` (`stopAtBeginningOfMainSubprogram`). `continue` then reports a signal stop (SIGSEGV) at the deref; `stack_trace` + `variables` on Locals shows the `struct user *` as `0x0`. lldb-dap behaves the same but stops on entry, not at `main`. Accept either adapter. Fix: NULL check after `find_user()`; recompile; `./bin/crash` exits 0.
- **S.** Print-debugging typically costs 2–4 `edit` cards and 2–3 reruns; the DAP path costs 0 edits before the fix. Conditional breakpoint: `set_breakpoint {file, line, condition: "user is None"}` → `verified`; `launch` with `args: ["1"]` and `continue` should end with the program terminating without a breakpoint stop.

## 8.5 gated tools

- **github.** The tool only registers if `gh` is on PATH at session start; `github.enabled` alone is not enough. `read issue://1` requires the lab to be pushed to GitHub with issues created from `docs/ISSUES.md` (instructor task before the session; issue numbers must match #1–#8). `pr_create` requires the branch to exist on the remote; if `gh` reports no upstream, have the learner `git push -u origin <branch>` first. `run_watch` gives up after 90 s with no runs — the lab has no workflow unless you add `.github/workflows/tests.yml`; accept the give-up message or add a trivial workflow.
- **security_scan.** OAuth only: API-key users get a preflight error. `start` fails with `Security scan plan is stale` if any file changed after `preflight` (including `notes/` — exclude it). The scan runs as a background job; `status` is the durable view. Findings on the lab are expected to be low-severity (stdlib HTTP server, no auth) — the pass is the `security://` reads, not the finding count. `validate` requires a nonblank `validation_summary`.
- **generate_image / tts / ida.** Optional; accept a documented failure card (`No usable model …`, `No xAI credentials …`, `ida` absent) as evidence the gate was flipped, but only if `omp config get <key>` shows the new value. Local `tts` writes WAV even when asked for `.mp3` and says so.

## Common cross-lesson failure

A learner whose session was started with `--tools …` (e.g. from Module 4 experiments) will not see `lsp`/`ast_edit`/`debug` devices in `read xd://` unless those names were included — "explicitly requested tools are top-level, everything else is absent". Restart without `--tools`.
