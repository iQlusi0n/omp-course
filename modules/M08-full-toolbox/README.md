# Module 8 — The Full Toolbox

| | |
|---|---|
| **Level** | intermediate |
| **Time** | ~2.5 h (8.1 ≈ 30 min · 8.2 ≈ 30 min · 8.3 ≈ 40 min · 8.4 ≈ 30 min · 8.5 ≈ 20 min) |
| **Prerequisite** | Module 2 (you can read tool cards, expand them with `Ctrl+O`, and know what `read`/`grep`/`edit`/`bash` do) |
| **Built against** | `omp --version` → `omp/18.3.1` |
| **Practice repo** | `omp-course-lab` — `git checkout module-8-start` |

**Goal.** Know the capabilities worth asking for *by name*. Most of omp's power tools are never touched by learners because they never ask for them: structured reads of databases and archives, a persistent Python kernel, language-server renames, AST codemods, a real debugger, and a handful of setting-gated integrations. Each lesson below is self-contained.

Two conventions for this module:

- **"Type in the composer"** means a normal chat prompt; the *model* decides to call the tool. Every prompt in this module names the tool explicitly so the model does not improvise.
- **`omp read …` from a shell** (verified: `omp read --help`) shows *exactly* what the `read` tool would return for a path — use it to check your pass conditions without spending model tokens.

Every setting mentioned is shown with its default from `omp config list` on 18.3.1. Settings that are **off by default** are marked ⚠ and given their enable key.

---

## Lesson 8.1 — `read` beyond text              (~30 min)

**You will be able to:** read a PDF, a SQLite table, a member of a zip file, a notebook, and a GitHub URL through the single `read` tool; write a row into SQLite or a file into an archive; run a one-shot web search from the shell with a pinned provider.

**Why this exists:** `read` takes one `path` string and dispatches on what the string looks like: a local file, a directory, `archive.zip:member`, `db.sqlite:table?where=…`, `https://…`, or an internal URL like `pr://42`. Because the model already knows `read`, teaching *you* the selector grammar is the whole lesson — once you can spell `data/lab.sqlite:orders?limit=5`, so can the prompt you write, and omp stops shelling out to `sqlite3`/`unzip`/`pdftotext` (which it may not even have).

**Demo:** `demos/8.1-read-formats.md` — live `omp read` output for each selector below, captured on 18.3.1.

**Concepts:**

- *Selector grammar (local files).* Suffix on the path: `:50-100` inclusive range, `:50` open-ended (default limit `read.defaultLimit = 300`), `:50+20` count, `:5-16,960-973` multiple ranges, `:raw` verbatim (no summary, no line prefixes), `:conflicts` (index unresolved merge markers as `conflict://N`), `:img` (rasterize a local `.svg`/`.svgz` as an image). Parseable code files of ≥ `read.summarize.minTotalLines = 100` lines read without a selector come back as a *structural summary* (declarations kept, bodies elided) with a footer naming the elided ranges — re-read those ranges, never guess. Prose (`.md`, `.txt`) is never summarized unless `read.summarize.prose = true`.
- *Directories.* `read api/` renders a tree (depth 2, 12 children per directory).
- *Documents.* `.pdf .doc .docx .ppt .pptx .xls .xlsx .rtf .epub` are converted to text; line selectors apply to the converted text (`docs/spec.pdf:1-40`). Each PDF page is marked `<!-- Page N -->`; embedded images become `read <pdf>:<id>.png` handles.
- *Archives.* `fixtures/bundle.zip` lists members; `fixtures/bundle.zip:README.md` reads one; `fixtures/bundle.zip:config` lists a folder; `:README.md:1-5` slices. Containers: tar family, zip family (`.zip .jar .war .apk .whl .vsix …`), `.7z .rar .iso .deb .rpm .asar`, single-stream `.gz .xz .zst`.
- *SQLite* (`.sqlite .sqlite3 .db .db3`, must have the SQLite header):
  - `data/lab.sqlite` → tables with row counts
  - `data/lab.sqlite:orders` → `CREATE TABLE …` plus 5 sample rows
  - `data/lab.sqlite:users:3` → one row by primary key
  - `data/lab.sqlite:orders?limit=5&offset=0&order=amount:desc&where=amount>150` → filtered query (`limit` default 20, max 500; `where` rejects `;`, comments, `LIMIT`/`UNION`/`ATTACH`/`PRAGMA`)
  - `data/lab.sqlite?q=SELECT …` → raw SQL, ≤ 1000 rows, no other params allowed
- *Notebooks.* `.ipynb` renders as editable `# %% [code] cell:N` text; `:raw` gives the JSON.
- *Images.* Any image path is sent inline to a vision-capable model; `read shot.png?q=what is selected?` asks the `vision` role a question (`images.questionTimeoutMs = 300000`).
- *URLs.* `https://…` or `www.…` are fetched and rendered reader-style; known sites get special handlers (the demo shows `Method: github-repo` for a GitHub repo URL). `:raw` returns the raw HTML; `:1-40` pages the cached render without refetching. A host:port URL needs a trailing slash before a selector (`https://example.com/:80`). Output shown to the model is capped at 300 lines / 50 KiB; the full render is spilled to `artifact://`.
- *Internal URLs* handled by `read`: `agent:// artifact:// attachment:// cfg:// conflict:// history:// issue:// local:// mcp:// memory:// omp:// pr:// proc:// rule:// security:// skill:// ssh:// vault:// xd://`.
  - `pr://42`, `issue://7` (short form resolves the repo from the checkout), `pr://owner/repo/42`, `pr://42/diff`, `pr://42/diff/all`, `?comments=0`; bare `issue://?state=open&limit=10` lists. These are served by the `gh` CLI (must be installed and logged in).
  - `ssh://host/path/file` reads a remote UTF-8 file or directory (≤ 1 MiB, POSIX remote shell); bare `ssh://` lists configured hosts; `omp ssh add <name> --host … --user …` registers one; percent-encode `:` `?` `#` in the path.
  - `xd://` lists the tool devices mounted in this session (Lesson 8.3).
- *`write` to the same targets.* `write data/lab.sqlite:users` with a JSON5 object inserts a row; `write data/lab.sqlite:users:42` updates; empty content deletes; `write fixtures/bundle.zip:notes/todo.txt` rewrites the archive atomically with the new member (zip family, `.tar`, `.tar.gz`, `.tar.zst`, `.asar` are writable; `.7z`/`.rar` are read-only). Writing `@ours`/`@theirs`/`@base`/`@both` to `conflict://N` resolves a marker block registered by `:conflicts`.
- *`web_search`* (default on: `web_search.enabled = true`). One `query` plus optional `recency` (`day|week|month|year`), `limit`, `num_search_results`. Google-style operators (`site:`, `-site:`, `after:`, `before:`, `inurl:`, `intitle:`, `filetype:`, quotes, `OR`) are parsed and mapped per provider. Provider choice is the `web` **model role**: `modelRoles.web` is the primary, `retry.fallbackChains.web` the fallbacks; unset, omp walks its built-in chain (`web/parallel` first — always available without credentials — then credentialed engines, then keyless scrapers such as `web/duckduckgo`). Per-provider hard timeout `providers.webSearchTimeoutSeconds = 60`. From the shell: `omp q --model web/duckduckgo -l 3 "query"` (`omp q` = `omp search` = `omp web-search`; the in-session tool has no per-call provider override).

**Try it (Walkthrough):**

1. In `omp-course-lab`, start `omp` and type: `read docs/spec.pdf:1-40`
   **Expected:** one `read` card whose body begins `<!-- Page 1 -->`; header `[docs/spec.pdf#XXXX]`; if the doc is longer than 40 lines the footer says `Use :41 to continue`.
2. Type: `read data/lab.sqlite:orders?limit=5`
   **Expected:** a Markdown table with 5 rows and a footer like `[N more rows; append :orders?limit=5&offset=5 to the database path to continue]`.
3. Type: `read fixtures/bundle.zip:README.md`
   **Expected:** the text of `README.md` from inside the zip; no `unzip` bash card.
4. Type: `read https://github.com/can1357/oh-my-pi`
   **Expected:** a header block `URL: … / Content-Type: text/markdown / Method: github-repo`, then `# can1357/oh-my-pi` with stars/forks/language.
5. Verify from a second terminal without a model: `omp read data/lab.sqlite:users:1`
   **Expected:** `id: 1` and the other columns of user 1, one per line.
6. Type: `Using the write tool, insert a row into data/lab.sqlite:users with name "Grace" and email "grace@lab.test", then read it back with a where= filter.`
   **Expected:** a `write` card `Inserted row into users`, then a `read` card for `data/lab.sqlite:users?where=name='Grace'` showing the new row. (`git checkout -- data/lab.sqlite` afterwards if you want the seed data back.)
7. In a shell: `omp q --model web/duckduckgo -l 3 "oh-my-pi coding agent"`
   **Expected:** a boxed `⌕ Web Search: DuckDuckGo 3 sources` panel with three numbered sources and URLs.

**Guided task:** Answer "which month had the most orders?" without any `bash` card.
- Hints: `?q=` accepts a raw `SELECT … GROUP BY substr(created_at,1,7)`; you may also ask for `:orders?order=created_at:desc&limit=…`.
- Checkpoints: (a) `read data/lab.sqlite` shows the tables; (b) one `read` card contains the aggregated table.
- Pass: the transcript has zero `bash` cards and one `read` card whose path starts with `data/lab.sqlite?q=`.

**Stretch:** Register your own machine as an SSH host (`omp ssh add self --host 127.0.0.1 --user $USER`) and read the lab's `README.md` through `ssh://self/…`. Pass: the `read` card's source is an `ssh://` URL and the content matches `read README.md`. (Needs `sshd` reachable on localhost.)

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `read data/lab.sqlite:orders` returns a "binary file" notice | file extension matches but header is not SQLite (empty/corrupt DB) | regenerate with `python3 tools/seed_db.py`; detection needs both extension and magic bytes |
| `Unknown query parameter` / `where` rejected | `where` contains `;`, `--`, `LIMIT`, `UNION`, `ATTACH`, `PRAGMA` | move the logic into `?q=SELECT …` |
| `[Cannot read .pdf file: …]` | document conversion failed | try `:raw`; check the file is a real PDF (`head -c 8 docs/spec.pdf` → `%PDF-1.`) |
| URL read returns `Method: failed` | HTTP status not OK (403/404, bot wall) | read the `Notes:` line; retry with `:raw`; use `web_search` to find an alternate page |
| `issue://1` fails | `gh` not installed or not authenticated | install GitHub CLI and run `gh auth login` |
| `ssh://host/...` errors | host not in `ssh.json` and not an OpenSSH alias, or remote shell not POSIX | `omp ssh add …`; verify `ssh host true` works from the shell |
| `omp q` prints `Error: No web search model configured.` | every candidate unavailable (offline) or `web_search.enabled` false | check network; `omp config get web_search.enabled` |
| Web search card shows `Note: no results matched …` | a `site:`/date constraint eliminated all results and was relaxed | loosen the operator or change provider with `modelRoles.web` |

**Cheat sheet:**

| Want | Path string |
|---|---|
| lines 50–100 / raw / conflicts | `file:50-100` · `file:raw` · `file:conflicts` |
| PDF page text | `docs/spec.pdf:1-40` |
| archive listing / member | `fixtures/bundle.zip` · `fixtures/bundle.zip:README.md` |
| DB tables / schema+5 rows / row by PK | `data/lab.sqlite` · `:orders` · `:users:3` |
| DB query / raw SQL | `:orders?limit=5&order=amount:desc&where=amount>150` · `data/lab.sqlite?q=SELECT …` |
| notebook cells | `docs/analysis.ipynb` (`:raw` for JSON) |
| GitHub PR / issue / diff | `pr://42` · `issue://7` · `pr://42/diff/all` |
| remote file | `ssh://host/etc/hostname` |
| insert / update / delete DB row | `write data/lab.sqlite:users` · `:users:42` (empty content = delete) |
| add file to zip | `write fixtures/bundle.zip:notes/todo.txt` |
| shell search with pinned engine | `omp q --model web/duckduckgo -l 3 "…"` |

**Source:** omp://tools/read.md, omp://tools/write.md, omp://tools/web_search.md, omp://settings.md (`modelRoles.web`, `retry.fallbackChains.web`), omp://cli-reference.md, `omp read --help`, `omp search --help`, `omp ssh --help`

---

## Lesson 8.2 — `eval` kernels              (~30 min)

**You will be able to:** run Python (and JavaScript) in a kernel that keeps state across tool calls; install a package inside it; call omp tools from inside a cell; make a one-shot structured model call with `completion()`; decide when `eval` beats `bash`.

**Why this exists:** `bash` forgets everything between calls and returns text. `eval` runs one cell per tool call in a *retained* runtime (Python subprocess or Bun worker), so a DataFrame loaded in call 1 is still there in call 5, `display()` returns structured JSON/images instead of stdout soup, and cells can call omp's own tools (`await tool.read(...)`). The model-facing prompt literally forbids `python -c` through bash for ad-hoc code — ask for `eval` by name and you get the retained kernel.

**Demo:** `demos/8.2-eval-kernel.md` — three consecutive `eval` cards: build `by_month`, reuse it without reloading, then call `tool.read` from inside the kernel (captured live on 18.3.1).

**Concepts:**

- *One call = one cell.* Inputs: `language` (`py` | `js`), `code`, `title`, `timeout` (seconds, default 30, `0` disables, max 3600), `reset` (recreate this language's runtime). State is per language; resetting Python leaves JS untouched.
- *Defaults:* `eval.py = true`, `eval.js = true`, `eval.tools.enabled = true`, `python.kernelMode = session` (`per-call` spawns a fresh interpreter every call), `python.interpreter = ""` (auto: active venv → `<cwd>/.venv` → `~/.omp/python-env` → `python`/`python3` on PATH). `PI_PY`/`PI_JS` env override the backend switches. ⚠ `eval.autoBackground.enabled = false`: when on, a cell running longer than `eval.autoBackground.thresholdMs = 60000` becomes a background job instead of blocking the turn.
- *Prelude helpers (both languages):* `display(value)` (JSON-compatible structures, images, markdown), `print`, `read(path, offset?, limit?)`, `write(path, content)`, `env(...)`, `log(message)`, `phase(title)`, `tool.<name>(args)` — a real session tool call; **a coroutine in Python** (`await tool.read({'path': 'data/lab.sqlite'})`), `completion(...)`, `agent(...)`, `wait(...)`, `workpool(...)`, `@tool`. (`agent`/`workpool`/`@tool` are Module 10; `browser`/`computer` preludes are Module 14.)
- *Magics (Python):* `%pip install <pkg>` (runs `python -m pip` for the kernel's interpreter, pauses the watchdog), `%load ./script.py` (executes a file in the retained namespace; re-run to reload), `%cd`, `%pwd`, `%env`, `%time`, `%who`, `%reset`, `%%bash`, `%%writefile`, `!cmd`. JS: `%bun add <pkg>`, `%environment project|managed`. Percent commands are standalone cells.
- *Rich output:* pandas/PIL/plotly objects and every open matplotlib figure are emitted as images after the cell (`MPLBACKEND=Agg` is set for you); `application/json` values render as a JSON tree; each JSON display value shown to the model is capped at 8000 chars (full value stays in `details.jsonOutputs`).
- *`completion()`* — stateless, tool-free one-shot model call: Python `completion(prompt, model="smol"|"default"|"slow", system=..., schema={...JSON Schema...})` returns a handle; `.wait()` returns the text, or parsed data when `schema` is given. Time spent waiting does not consume the cell timeout.
- *Limits:* interactive `input()` is rejected; output window 50 KiB with the rest spilled to `artifact://`; top-level `await` works (one persistent event loop) but `asyncio.run(...)` fails.
- *When `eval` beats `bash`:* multi-step data work (load once, iterate), anything returning structure (`display(dict)`), charts, calling other tools programmatically, small scripts you would otherwise write to a temp file. `bash` still wins for running the project's own commands (`python -m unittest`), services, and anything that must be a real shell.

**Try it (Walkthrough):**

1. Type: `Using eval (language py): open data/lab.sqlite with sqlite3, count orders per month by created_at[:7] into a dict called by_month, and display(by_month). Do not write files.`
   **Expected:** one `eval` card labelled `py`; the body ends with a `display[1]:` JSON block mapping `YYYY-MM` → count.
2. Type: `In a second eval cell, display(sum(by_month.values())) — reuse the variable, do not reload.`
   **Expected:** a second `eval` card whose code is exactly one line and whose output is the total order count (no `sqlite3.connect` in the code).
3. Type: `In eval, display(await tool.read({'path': 'data/lab.sqlite'})) to prove the tool bridge works.`
   **Expected:** the card shows a JSON object with `text: "orders (N rows)\nusers (M rows)"` and `details.resolvedPath`.
4. Type: `In eval, run %pip install matplotlib` (requires `pip` in the kernel interpreter).
   **Expected:** a standalone `%pip` cell streaming pip output; no `bash` card.
5. Type: `In eval, plot by_month as a bar chart with matplotlib and savefig('notes/orders.png'); do not call show().`
   **Expected:** the card renders the figure inline (auto-captured) and `ls notes/orders.png` in a shell succeeds.
6. Type: `In eval, call completion("Return the busiest month from this dict: " + str(by_month), model="smol", schema={"type":"object","properties":{"month":{"type":"string"}},"required":["month"]}).wait() and display the result.`
   **Expected:** the card shows a parsed object like `{"month": "2026-03"}` — structured, not prose.
7. Type: `Reset the Python kernel (reset: true) and display(by_month).`
   **Expected:** a `NameError: name 'by_month' is not defined` traceback with nonzero exit — proof that `reset` wipes state.

**Guided task:** "In eval, load `data/lab.sqlite` via `tool.read` (the `?q=` raw-SQL form), compute orders per month, plot to `notes/orders.png`."
- Hints: `await tool.read({'path': "data/lab.sqlite?q=SELECT substr(created_at,1,7) m, count(*) n FROM orders GROUP BY 1"})` returns a Markdown table in `['text']`; parse the rows or just run the SQL with `sqlite3` — either is fine, but the bridge call must appear. Keep the parsed data in a variable.
- Checkpoints: (a) first cell calls `tool.read`; (b) a later cell plots from the retained variable with no reload; (c) `notes/orders.png` exists.
- Pass: `ls -l notes/orders.png` succeeds **and** the plotting cell's code contains neither `sqlite3.connect` nor `tool.read`.

**Stretch:** Put the loader into `notes/orders_lib.py`, `%load` it, and reuse `by_month()` across two cells; then break a cell with `time.sleep(40)` and observe the timeout message. Pass: the timeout card reads `eval cell timed out after 30s; kernel interrupted but remains running…` and the next cell still sees your function.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `Python backend not available` | no Python ≥ 3.10 resolvable, or `eval.py` false / `PI_PY=0` | `omp setup python --check`; install Python or set `python.interpreter` |
| `%pip` fails with `No module named pip` | kernel interpreter has no pip (Debian system Python) | create `~/.omp/python-env` venv with pip, or point `python.interpreter` at a venv |
| `ModuleNotFoundError: PIL` after `%pip install pillow` | distribution vs import name confusion is fine here — but check you installed into the *kernel's* interpreter | use `%pip`, not `bash pip` |
| `Kernel requested stdin; interactive input is not supported` | `input()` in the cell | pass data programmatically |
| `asyncio.run` raises | kernel already owns the event loop | use top-level `await` |
| Output ends with `artifact://…` | > 50 KiB output | `read artifact://<id>:1-200` |
| Variables vanished | `reset: true`, `python.kernelMode = per-call`, or the kernel was killed after a stuck interrupt | check the card notice; re-run setup or `%load` your script |
| `Backgrounded as job …` mid-cell | `eval.autoBackground.enabled` true and cell exceeded threshold | wait for the follow-up delivery; do not poll |

**Cheat sheet:**

| Item | Value |
|---|---|
| tool | `eval` — `language: py\|js`, `code`, `title`, `timeout` (30 s default, 0 = none), `reset` |
| enable keys | `eval.py = true`, `eval.js = true`, `eval.tools.enabled = true`; env `PI_PY`, `PI_JS` |
| kernel mode | `python.kernelMode = session` (default) or `per-call`; `python.interpreter = ""` |
| helpers | `display()`, `read()`, `write()`, `env()`, `log()`, `phase()`, `await tool.<name>({...})`, `completion(prompt, model=, system=, schema=).wait()` |
| magics | `%pip install x`, `%load file.py`, `%cd`, `%env`, `%time`, `%reset`, `%%bash`, `!cmd`; JS `%bun add x`, `%environment project` |
| auto-background ⚠ | `eval.autoBackground.enabled = false`, `thresholdMs = 60000` |
| charts | matplotlib figures auto-captured (`MPLBACKEND=Agg`); `savefig()` for a file |

**Source:** omp://tools/eval.md, omp://python-repl.md, omp://settings.md, `omp config list`

---

## Lesson 8.3 — Code intelligence: `lsp`, `ast_grep`, `ast_edit`, `find`, `xd://`              (~40 min)

**You will be able to:** rename a symbol across a package with the language server instead of search-and-replace; write an AST pattern with `$X` / `$$$ARGS` metavariables, preview a codemod, and accept it through `xd://resolve`; run a semantic `find`; list the `xd://` devices in a session and pin the tool set with `--tools`.

**Why this exists:** Text tools (`grep`, `edit`) do not know that `get_user` in `api/__init__.py` is the same symbol as the one in `api/db.py`, or that `print(x)` inside a string is not a call. Language servers and tree-sitter do. omp wraps both: `lsp` speaks to whatever server your project already uses, and `ast_grep`/`ast_edit` run native ast-grep with a preview-then-accept protocol so a bad pattern never touches disk. `find` is the opposite end: describe *behaviour* in plain language and get ranked line ranges back.

**Demo:** `demos/8.3-code-intel.md` — `read xd://` listing, an `lsp status` card, an `ast_grep` card with `meta:` captures, an `ast_edit` preview, the `write xd://resolve` apply, and a `find` run (all captured live except the rename, which shows the documented output shape).

**Concepts:**

*LSP*
- Tool `lsp` (default on: `lsp.enabled = true`; `--no-lsp` disables tools, formatting and diagnostics for one run). Actions: `diagnostics`, `definition`, `references`, `hover`, `symbols`, `rename`, `rename_file`, `code_actions`, `type_definition`, `implementation`, `status`, `reload`, `capabilities`, `request`. Fields: `file`, `line` (1-indexed), `symbol` (substring on that line; `name#2` = second occurrence; **required with `line` for `definition`/`references`/`rename`**), `query`, `new_name`, `apply`, `timeout` (20 s default, 5–300).
- `rename` sends `textDocument/rename` and **applies by default** (`apply: false` previews `Rename preview:`). `rename_file` is the *file move* variant: it sends `workspace/willRenameFiles` / `didRenameFiles` to every matching server so imports follow the move. `diagnostics` with `file: "*"` runs the project checker (`pyright` for Python; `cargo check`, `tsc`, `go build` for others). `code_actions` lists (`N code action(s): index: [kind] title`) and applies with `apply: true, query: <index|title substring>`.
- Read-only actions need read approval; `rename`, `rename_file`, `code_actions`, `reload`, `request` need write approval.
- *Auto-detection* (no config needed): a built-in server is used when (1) the cwd contains one of its `rootMarkers` **and** (2) its binary resolves in project-local bins (`node_modules/.bin`, a Python venv) or `$PATH`. Detection is cwd-only — it does not look at parent directories. Python servers in `defaults.json`: `pyright` (`pyright-langserver`), `basedpyright`, `pylsp`, `ty`, plus the `ruff` linter. Their root markers (from the embedded `defaults.json` in the 18.3.1 binary): pyright → `pyproject.toml pyrightconfig.json setup.py setup.cfg requirements.txt Pipfile`; pylsp → `pyproject.toml setup.py setup.cfg requirements.txt Pipfile`. The lab ships a root `pyproject.toml`, so **install either `pyright` (`npm i -g pyright`) or `pylsp` (`pip install python-lsp-server`) and omp picks it up** — for the rename exercise pyright is the safer choice (project-aware cross-file rename).
- `lsp.lazy = true`: servers cold-start on first `lsp` call or first edit/write of a matching file; the welcome screen shows discovered servers as a gray dot. `lsp.diagnosticsOnWrite = true` attaches diagnostics to `write`/`edit` results. `lsp.formatOnWrite = false` ⚠. `lsp.shared = true` shares one server per project across omp processes.
- *Config files* (lowest → highest): `~/lsp.json`, plugin configs, `~/.omp/agent/lsp.json` (user), `<cwd>/.omp/lsp.json` (project), `<cwd>/lsp.json`. JSON or YAML; `{ "servers": { … }, "idleTimeoutMs": 300000 }` or a flat map. Override a built-in by name with only the fields you change (`"pylsp": { "disabled": true }`); a *new* server needs `command`, `fileTypes`, `rootMarkers`. Any config that contributes a server map switches off pure auto-detect (overrides are merged onto defaults, then filtered by root marker + binary). Workspace `reload` (`file: "*"`) re-reads config.

*AST tools*
- Pattern grammar (shared): `$NAME` one node, `$_` one unbound node, `$$$NAME` zero-or-more nodes, `$$$` unbound; names uppercase; a pattern must parse as one valid node in the target language (Python, TS, Go, Rust, C… 50+ languages inferred from extension).
- `ast_grep` ⚠ **off by default** (`astGrep.enabled = false`): `pat`, `path` (file/dir/glob, `;`-separated list, internal URLs), `skip`. Output groups matches by file as `*LINE:text` with a `meta: A=[...]` line when metavariables captured; 50-match page.
- `ast_edit` (default on: `astEdit.enabled = true`): `ops: [{pat, out}]` (empty `out` deletes the node; duplicate `pat`s rejected), `paths: [...]`. It **always previews**: the card starts `Staged as a proposal — files NOT modified yet…` and shows `-LINE… / +LINE…` pairs. Files are written only when the model (or you, via a prompt) **writes a one-sentence reason to `xd://resolve`**; `xd://reject` discards. While a proposal is pending omp reminds the model to resolve or reject it. Apply re-runs the rewrite and refuses if the file changed since the preview (`stalePreview`). Files with syntax errors are skipped whole; overlapping matches abort. `PI_MAX_AST_FILES` (default 1000) caps files touched.
- Substitution is 1:1: `print($$$A)` → `logger.debug($$$A)` copies the argument list verbatim, so `print("total", n)` becomes `logger.debug("total", n)` — which `logging` interprets as a format string plus args. Single-argument prints (the lab's `cli/` uses f-strings) are safe; multi-arg prints need a different `out` or a follow-up edit. Always run the tests after a codemod.

*Semantic find*
- Tool `find` (`query`, `grep_keywords: []`, `path`) and CLI `omp find "<query>" [path] [-k kw] [--hidden] [--json] [-q]`. Cascade: lexical scan → filename ranking → passage scoring → verification; hits print as `path:start-end  p  snippet` with a cost/time footer.
- Prerequisite: the **`judge` model role** (`modelRoles.judge`, default `typesafe/jev-latest`, fallback chain `typesafe/jev-preview`, `@tiny`, `@smol`, `@default`). `find.enabled = auto` enables the tool **only when the judge resolves to a TypeSafe jev model** (`TYPESAFE_API_KEY` or `/login`); set `find.enabled on` to allow any judge model (slower, prompted), `off` to hide it.

*Discoverable tools and `xd://`*
- Tools are either *essential* (always in the model's tool list: `read`, `write`, `edit`, `bash`, `grep`, `glob`…) or *discoverable*. With `tools.xdev = true` (default) discoverable tools such as `lsp`, `ast_edit`, `debug`, `checkpoint`, `retain` are *mounted as devices*: `read xd://` lists them, `read xd://lsp` prints the device's input schema, and `write xd://lsp` with a JSON body calls it. The demo shows a stock session with exactly `xd://ast_edit`, `xd://debug`, `xd://lsp` mounted. `tools.xdevDocs = catalog` controls how much of that documentation goes into the system prompt.
- `omp --tools read,write,ast_edit,grep` pins the built-in tool set for a run (explicitly requested tools are top-level, not devices); `--no-tools` disables all built-ins. Per-tool switches: `bash.enabled`, `grep.enabled`, `glob.enabled`, `astGrep.enabled`, `astEdit.enabled`, `debug.enabled`, `lsp.enabled`, `web_search.enabled`, `find.enabled`.

**Try it (Walkthrough):** (needs `pyright-langserver` or `pylsp` on PATH; check with `which pyright-langserver pylsp`)

1. Type: `read xd://`
   **Expected:** `xd:// N mounted tool devices.` listing at least `xd://ast_edit`, `xd://debug`, `xd://lsp`.
2. Type: `Call lsp with action=status.`
   **Expected:** `Language servers: pyright (configured, not started)` (or `pylsp …`). If you see `No language servers configured for this project`, jump to Troubleshooting.
3. Type: `Call lsp references for symbol get_user in api/db.py (the def line).`
   **Expected:** `Found N reference(s):` including `api/__init__.py`, `api/server.py`, `cli/commands.py`, and `tests/…`.
4. Type: `Call lsp rename with apply=false: file api/db.py, the def line of get_user, symbol get_user, new_name fetch_user.`
   **Expected:** `Rename preview:` listing every file from step 3. No files changed (`git status` clean).
5. Type: `Now apply the same rename (apply default).`
   **Expected:** `Applied rename:` with per-file change lines; `grep -rn get_user api cli tests` returns nothing except string literals (e.g. an `__all__` entry — LSP renames identifiers, not strings).
6. Type: `Fix any remaining get_user string occurrences with edit, then run python3 -m unittest discover -s tests.`
   **Expected:** a `bash` card ending `OK`.
7. Enable structural search for this run: quit, write `notes/astgrep.yml` containing `astGrep:` / `  enabled: true`, then `omp --config notes/astgrep.yml` (or persist it with `omp config set astGrep.enabled true`). Type: `Use ast_grep with pattern print($$$A) on path cli.`
   **Expected:** matches grouped under `# cli/`, each with a `meta: A=[…]` line; the count equals `grep -c "print(" cli/*.py` summed.
8. Type: `Use ast_edit with op pat=print($$$A) out=logger.debug($$$A) on paths ["cli"]. Do not apply yet.`
   **Expected:** a card beginning `Staged as a proposal — files NOT modified yet.` with `-N: print(...)` / `+N: logger.debug(...)` pairs; `git status` still clean.
9. Type: `Apply the staged proposal by writing a one-sentence reason to xd://resolve.`
   **Expected:** a `write` card to `xd://resolve` returning `Applied N replacements in M files.` (hashline mode also prints fresh `[path#TAG]` headers).
10. Type: `grep for print( in cli, then run the tests; if logger is undefined in a file, add from cli.log import logger with edit and rerun.`
    **Expected:** `grep` card `No matches found`; final `bash` card `OK`.
11. (If `find` is available — `omp config get find.enabled`, and the judge resolves) in a shell: `omp find -q "where are orders grouped by month" .`
    **Expected:** `N hit(s) for "…" · τ 0.20 · strongest first`, top hit in `api/`, footer with tokens/cost. If the tool is hidden: `omp config set find.enabled on` and retry (any chat model can judge, slower).

**Guided task:** Rename `get_user` → `fetch_user` across the `api/` package (re-exported from `api/__init__.py`), then replace `print($$$A)` with `logger.debug($$$A)` in `cli/` via `ast_edit`, accepting the proposal.
- Hints: do the rename first (LSP needs a clean tree to index), then the codemod; `cli/log.py` already exposes `logger`; ask for `apply: false` first if you want to see the preview.
- Checkpoints: (a) `lsp references` lists ≥ 4 files; (b) `Applied rename:`; (c) `Staged as a proposal`; (d) `write xd://resolve` → `Applied …`.
- Pass: `grep -rn "print(" cli/` prints nothing; `python3 -m unittest discover -s tests` passes; `api/__init__.py` imports `fetch_user`.

**Stretch:** Write `.omp/lsp.json` that disables `pylsp` and raises `idleTimeoutMs` to 120000, then `lsp reload` (`file: "*"`) and confirm with `lsp status`. Then move `api/db.py` to `api/storage/db.py` with `lsp rename_file` and make the tests pass. Pass: `lsp status` no longer lists `pylsp`; `git status` shows the move plus updated imports; tests `OK`.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `No language servers configured for this project` | no root marker in cwd (need `pyproject.toml`/`setup.py`/`setup.cfg`/`requirements.txt`/`Pipfile`) or server binary not on PATH / project venv | `git checkout module-8-start` (ships `pyproject.toml`); `npm i -g pyright` or `pip install python-lsp-server`; then `lsp reload` |
| `✘ api/db.py: No language server found` on diagnostics | as above, or you started omp in a subdirectory (detection is cwd-only) | start omp at the repo root |
| `LSP error: symbol required…` | `line` given without `symbol` for `definition`/`references`/`rename` | add `symbol: get_user` |
| Rename touched only one file | server is not project-aware (some pylsp setups) or project not fully loaded | use pyright; retry after `lsp reload`; check `references` first |
| Server hangs / `timed out after 20s` | cold start on a big tree | raise `timeout` (≤ 300) or wait and retry; `lsp status` shows live state |
| `ast_grep` not in the tool list | `astGrep.enabled = false` ⚠ | `omp config set astGrep.enabled true` (or `--config` overlay) |
| `No replacements made` + parse issues | pattern not a valid node for that language, or file has syntax errors (skipped whole) | test the pattern with `ast_grep` first; fix syntax; narrow `paths` |
| `Overlapping replacements detected` | two ops match nested nodes | split into two `ast_edit` calls |
| `xd://resolve` → `Nothing to resolve` / error | proposal already applied or preview went stale | re-run `ast_edit` to stage again |
| `find` missing from tools | `find.enabled = auto` and judge is not a TypeSafe jev model | `TYPESAFE_API_KEY=…` or `omp config set find.enabled on` |
| `omp find` exits 1: every judgment failed | no judge credentials at all | configure `modelRoles.judge` / `retry.fallbackChains.judge` |

**Cheat sheet:**

| Item | Value |
|---|---|
| lsp actions | `diagnostics` (`file:"*"` = whole project), `definition`, `references`, `hover`, `symbols`, `rename` (applies unless `apply:false`), `rename_file`, `code_actions`, `status`, `reload`, `capabilities`, `request` |
| lsp config | `<cwd>/.omp/lsp.json` (project) · `~/.omp/agent/lsp.json` (user) · `{"servers":{"pylsp":{"disabled":true}},"idleTimeoutMs":300000}` |
| lsp settings | `lsp.enabled=true`, `lsp.lazy=true`, `lsp.shared=true`, `lsp.diagnosticsOnWrite=true`, `lsp.formatOnWrite=false` ⚠, flag `--no-lsp` |
| Python servers auto-detected | `pyright-langserver`, `basedpyright-langserver`, `pylsp`, `ty`, `ruff` — root marker in cwd + binary on PATH/venv |
| pattern grammar | `$X` one node · `$$$ARGS` many · `$_`/`$$$` unbound · uppercase names |
| ast_grep ⚠ | `astGrep.enabled=false` → `omp config set astGrep.enabled true`; `pat`, `path`, `skip` |
| ast_edit | `astEdit.enabled=true`; `ops:[{pat,out}]`, `paths:[…]`; preview → `write xd://resolve "<reason>"` / `xd://reject`; `PI_MAX_AST_FILES=1000` |
| find | tool `find {query, grep_keywords, path}` · `omp find "<q>" [path] -k kw --json`; `find.enabled=auto\|on\|off`; judge role `modelRoles.judge` (`typesafe/jev-latest`) |
| devices | `tools.xdev=true`; `read xd://` list · `read xd://<tool>` schema · `write xd://<tool>` JSON call; `omp --tools a,b,c` pins built-ins; `--no-tools` |

**Source:** omp://tools/lsp.md, omp://lsp-config.md, omp://tools/ast-grep.md, omp://tools/ast-edit.md, omp://resolve-tool-runtime.md, omp://tools/find.md, omp://tools/read.md (`xd://`), omp://tools/write.md (`xd://` dispatch), omp://settings.md, omp://cli-reference.md (`--tools`, `--no-lsp`), `omp find --help`, `omp config list`, embedded `lsp/defaults.json` in the 18.3.1 binary (Python root markers)

---

## Lesson 8.4 — Real debugging (DAP)              (~30 min)

**You will be able to:** launch a program under a real debugger from a prompt, stop at a breakpoint, inspect the stack, scopes and variables, evaluate an expression, fix the bug, and re-run — in Python (debugpy) and C (gdb / lldb-dap).

**Why this exists:** Print-debugging is what an agent does when it has nothing better: it edits your source, reruns, reads stdout, edits again. The `debug` tool drives a Debug Adapter Protocol session instead — breakpoints, stepping, `variables`, `evaluate`, memory — with no source edits and no guessing. The workflow to teach the agent (and yourself) is *reproduce → breakpoint → inspect → fix → re-run*.

**Demo:** `demos/8.4-dap-debug.md` — a full debugpy session on a `None` deref captured live on 18.3.1: `launch` (stopped on entry), `set_breakpoint` (`verified`), `continue` (stopped at breakpoint), `stack_trace`, `scopes`, `variables` (`profile = None (NoneType)`), `evaluate`, `terminate`.

**Concepts:**

- Tool `debug` (default on: `debug.enabled = true`; discoverable → `xd://debug` in a stock session). One active root session at a time; `terminate` before launching another. `timeout` per request 30 s (5–300).
- Actions: `launch` (`program`, `args`, `adapter`, `cwd`), `attach` (`pid` or `port`/`host`), `set_breakpoint` / `remove_breakpoint` (`file`+`line`, or `function`; optional `condition`), `set_data_breakpoint` (`data_breakpoint_info` first — adapter must support it), `set_instruction_breakpoint`, `continue`, `step_over`, `step_in`, `step_out`, `pause`, `stack_trace` (`levels`), `threads`, `scopes` (`frame_id`; defaults to the stopped frame), `variables` (`variable_ref` or `scope_id`), `evaluate` (`expression`, `context` default `repl`, `frame_id`), `disassemble`, `read_memory` / `write_memory` (`memory_reference`, `count`, `data`), `modules`, `loaded_sources`, `custom_request`, `output` (captured stdout/stderr, 128 KiB ring), `terminate`, `sessions`.
- Approval: `output`, `threads`, `stack_trace`, `scopes`, `variables`, `disassemble`, `read_memory`, `loaded_sources`, `modules`, `sessions` are read-tier; everything else is exec-tier.
- *Built-in adapters* (`dap/defaults.json`): `gdb` (`gdb -i dap`), `lldb-dap`, `codelldb`, `debugpy` (`python -m debugpy.adapter`), `dlv`, `js-debug-adapter`, `netcoredbg`, `kotlin-debug-adapter`, `rdbg`, `php-debug-adapter`, `bash-debug-adapter`, `dart-debug-adapter`, `flutter-debug-adapter`, `elixir-ls-debugger`. Auto-selection only considers adapters whose command resolves; `launch` ranks by file extension, then root markers, then native preference (`gdb`, `lldb-dap`) for extensionless binaries; `attach` with `port` prefers `debugpy`. Pass `adapter: "gdb"` to force one.
- `debugpy` and `gdb`/`lldb-dap` launch with `stopOnEntry: true`, so a fresh `launch` card reads `Status: stopped / Stop reason: entry`. gdb additionally sets `stopAtBeginningOfMainSubprogram`.
- **Learner prerequisites** (not on the build machine): Python — `pip install debugpy` into the interpreter that `python` on PATH resolves to (the adapter command is literally `python`, not `python3`). C — a compiler plus `gdb` or `lldb-dap`; compile the fixture with `cc -g -O0 -o bin/crash bin/crash.c` (comment at the top of `bin/crash.c`).
- *Custom adapters:* `.omp/dap.json` (also `dap.yaml`, `.dap.json`; user-level `~/.omp/agent/dap.json`), shape `{ "adapters": { "<id>": { command, args, languages, fileTypes, rootMarkers, launchDefaults, attachDefaults, connectMode: "stdio"|"socket"|"tcp", acceptsDirectoryProgram } } }`. Use it when your Python is only `python3`:

  ```json
  { "adapters": { "debugpy": {
      "command": "python3", "args": ["-m", "debugpy.adapter"],
      "languages": ["python"], "fileTypes": [".py"],
      "rootMarkers": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"],
      "launchDefaults": { "request": "launch", "justMyCode": false, "stopOnEntry": true },
      "attachDefaults": { "request": "attach", "justMyCode": false } } } }
  ```
- Observed gotcha (see demo): with debugpy, `evaluate` in the default `repl` context printed `Result:` (empty) for a `None` value; `context: "watch"` returned `Result: None / Type: NoneType`. `variables` on the Locals scope always shows the value.

**Try it (Walkthrough):** (Python; `python -c "import debugpy"` must succeed)

1. Reproduce: in a shell, `python bin/crash.py; echo exit=$?`
   **Expected:** a traceback ending `AttributeError: 'NoneType' object has no attribute 'name'` inside `display_name`, `exit=1`. Note the line number of the failing statement — call it `L`.
2. Type: `Use the debug tool: launch bin/crash.py with the debugpy adapter. Do not edit files.`
   **Expected:** a `debug` card `Session debug-1 / Adapter: debugpy / Status: stopped / Stop reason: entry / Location: …/bin/crash.py:1:1`.
3. Type: `Set a source breakpoint at bin/crash.py line L, then continue.`
   **Expected:** `Breakpoints for …/bin/crash.py: - line L: verified`, then `Stop reason: breakpoint / Frame: display_name / Location: …:L:1`.
4. Type: `Run stack_trace, then scopes, then variables for the Locals scope, then evaluate the offending variable with context watch.`
   **Expected:** `Stack trace:` with `display_name` on top and `main` below; `Scopes: - Locals: ref=N …`; `Variables: - user = None (NoneType)`; `Result: None / Type: NoneType`.
5. Type: `Terminate the session, then fix the root cause in bin/crash.py (make the caller handle a missing user instead of dereferencing None), and run python bin/crash.py.`
   **Expected:** `Debug session terminated.`; an `edit` card; a `bash` card with `exit 0` and no traceback.

**Guided task:** `bin/crash.py` (seeded `None` deref) and `bin/crash.c` (seeded bad pointer): ask omp to attach a debugger, break at the failing line, report the offending variable, fix.
- Hints (C): `cc -g -O0 -o bin/crash bin/crash.c`; `launch program=bin/crash` — omp auto-picks `gdb`/`lldb-dap` for an extensionless binary, or say `adapter: gdb`; with gdb you stop at `main` first; either set a breakpoint at the deref line or just `continue` and read the `Stop reason` (a SIGSEGV stop) then `stack_trace` + `variables` — the `struct user *` is `0x0`.
- Checkpoints: (a) two separate debug sessions (Python, then C — `terminate` between them); (b) each shows a `variables` or `evaluate` card with the null value; (c) both programs re-run.
- Pass: transcript shows `debug` cards with `scopes`/`variables` for **both** programs; `python bin/crash.py` and `./bin/crash` exit 0.

**Stretch:** Reproduce the same Python bug with **print-debugging only** (`--tools read,edit,bash`) in a fresh session and compare: number of `edit` cards, number of reruns, whether the fix is the same. Then add a `condition` to the breakpoint (`user is None`) and show it is only hit on the failing input. Pass: `notes/m8-debug.md` lists both tool sequences; the conditional breakpoint card shows `verified` and the run with a valid id (`python bin/crash.py 1`) never stops.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `No debugger adapter available. Installed adapters: …` | no adapter command resolves | `pip install debugpy`; ensure `python` (not only `python3`) is on PATH, or add the `.omp/dap.json` above |
| `DAP adapter exited (code N): … No module named debugpy` | debugpy installed for a different interpreter | install into the one `python` resolves to; or set `command` in `dap.json` to that interpreter |
| `launch program resolves to a directory` | pointed at `bin/` | give the file; only `dlv` accepts directories |
| Breakpoint listed but not `verified` | line has no code (blank/comment) or file path differs from the loaded one | pick a statement line; use the same relative path you launched with |
| `continue` returns `state: running`, `timedOut: true` | program did not hit a breakpoint within `timeout` (waiting on input / long loop) | `pause`, or raise `timeout`; check `output` |
| `Debug session <id> is still active` | previous session not terminated | `terminate` (or `sessions` to see it) |
| `evaluate` shows empty `Result:` | debugpy `repl` context suppresses `None` | use `context: "watch"` or read `variables` |
| C: `Stop reason: entry` then nothing | gdb stops at `main`; you must `continue` or set a breakpoint | set `file`+`line` breakpoint, `continue` |
| `debug` tool not offered | `debug.enabled` false, or session started with `--tools` without it | `omp config get debug.enabled`; add `debug` to `--tools` |

**Cheat sheet:**

| Item | Value |
|---|---|
| enable | `debug.enabled = true` (default) · device `xd://debug` |
| flow | `launch {program, adapter?}` → `set_breakpoint {file,line\|function, condition?}` → `continue` → `stack_trace` → `scopes` → `variables {scope_id}` → `evaluate {expression, context:"watch"}` → `terminate` |
| attach | `attach {pid}` or `{port, host}` (port ⇒ debugpy) |
| adapters | `debugpy` (`python -m debugpy.adapter`), `gdb` (`gdb -i dap`), `lldb-dap`, `codelldb`, `dlv`, `js-debug-adapter`, … |
| custom | `.omp/dap.json` / `~/.omp/agent/dap.json` — `{"adapters":{"<id>":{command,args,fileTypes,rootMarkers,launchDefaults,attachDefaults,connectMode}}}` |
| C fixture | `cc -g -O0 -o bin/crash bin/crash.c` then `launch program=bin/crash adapter=gdb` |
| limits | one root session; request timeout 30 s (5–300); output ring 128 KiB; idle cleanup 10 min |

**Source:** omp://tools/debug.md, `omp config list` (`debug.enabled`), embedded `dap/defaults.json` in the 18.3.1 binary (adapter commands, `stopOnEntry`), live capture in `demos/8.4-dap-debug.md`

---

## Lesson 8.5 — Optional tools (setting-gated)              (~20 min)

**You will be able to:** turn on `github`, `security_scan`, `generate_image`, `tts`, and `ida`; know the one prompt that exercises each; read the results (`artifact://`, `security://`, temp image paths, a `.wav`).

**Why this exists:** These five tools are hidden until you flip a setting (or, for `ida`, until IDA Pro is found) because each pulls in an external dependency — the `gh` CLI, a ChatGPT OAuth login, an image model, a local speech model, a reverse-engineering suite. Hidden tools cost nothing; knowing the key means you can enable exactly what your project needs. Toggle with `omp config set <key> true`, or in the `/settings` panel (Settings → Tools). `generate_image` and `tts` are registered/removed in the running session when toggled; for the others, start a new session after changing the key.

**Demo:** `demos/8.5-gated-tools.md` — the `omp config get` values before/after enabling, plus the documented card shapes for each tool.

**Concepts:**

| Tool | Enable key (default) | Extra prerequisite | Approval |
|---|---|---|---|
| `github` | ⚠ `github.enabled = false` | `gh` on PATH, `gh auth login` | read for views/search/`run_watch`; exec for `pr_create`, `pr_checkout`, `pr_push` |
| `security_scan` | ⚠ `security.enabled = false` | git repo; **OAuth** credential for the active model's provider (API keys are refused); cloud actions need `openai-codex` ChatGPT OAuth | exec |
| `generate_image` | ⚠ `generate_image.enabled = false` | an image-kind model reachable via `modelRoles.image` / `retry.fallbackChains.image` (`omp models --kind image`) | — |
| `tts` | ⚠ `speechgen.enabled = false` | local Kokoro-82M downloaded on first use (`omp setup speech`), or xAI / DeepInfra credentials | write |
| `ida` | `ida.enabled = true` but appears only when an IDA install with idalib is found (`ida.installDir`, `$IDADIR`, `/opt/ida*`, `~/ida*`, `/Applications/IDA*.app`) | `ida.python` interpreter that imports `ida_domain` + `idapro` | `list` read, `exec` exec, edits write |

- **`github`** — ops: `repo_view`, `file_read` (`path`, `branch`), `pr_create` (`title`/`body` or `fill`, `base`, `head`, `draft`, `reviewer[]`, `label[]`), `pr_checkout` (`pr` number/branch/URL or a list → worktree `~/.omp/wt/<n>-<hash>` on branch `pr-<n>`), `pr_push`, `search_issues`/`search_prs`/`search_code`/`search_commits`/`search_repos` (`query`, `limit` ≤ 50, `since`/`until` like `3d`, `2w`, `2026-01-01`), `run_watch` (`run` id/URL or current branch; polls Actions every 3 s then 15 s; failed-job logs tail inline with the full log at `artifact://<id>`). Single issues/PRs are **not** ops — read `issue://N` / `pr://N` (shared `~/.omp/cache/github-cache.db`). One prompt: *"Enable-key set? Read `issue://1`, then create a draft PR from the current branch titled 'Fix #1' with body 'Closes #1' and watch its Actions run."*
- **`security_scan`** — actions: `preflight` (`target_kind: repository | scoped_path | ref_diff | working_tree`, `include_paths`, `exclude_paths`, `base_revision`/`head_revision`) → `Security plan <id> is ready…`; `start {plan_id}` → `Security scan <scan-id> started as <operation-id>` (background job, phases `queued → preparing → reviewing → publishing → completed`); `status {operation_id}`; `cancel`; `validate {scan_id, finding_id, validation_status, validation_summary}`; `cloud_scans`/`cloud_start`/`cloud_status`/`cloud_pull` (Codex Security cloud, explicit only). Read results with `security://scans`, `security://scans/<id>`, `…/findings`, `…/findings/<fid>`, `…/report`, `…/sarif`, `…/coverage`. Output dir holds `scan.json findings.json report.md results.sarif provenance.json` (mode 0700/0600). One prompt: *"Run security_scan preflight on this repository excluding `generated` and `notes`, start it, poll status until completed, then read `security://scans/<id>/findings`."*
- **`generate_image`** — fields `subject` (required), `action`, `scene`, `composition`, `lighting`, `style`, `text`, `changes[]` + `input[]` (edit mode; `path` or base64 `data` + `mime_type`, ≤ 35 MiB), `aspect_ratio` (`1:1 3:4 4:3 9:16 16:9 3:2 2:3`), `image_size` (`1024x1024 1536x1024 1024x1536`), `model` (pin one, e.g. `xai/grok-imagine-image`). Output files land in the OS temp dir as `omp-image-<snowflake>.<ext>`; the card lists `imagePaths`. 3-minute timeout. One prompt: *"Use generate_image: subject 'flat vector logo for a CLI tool named lab', style 'minimal, two colours', aspect_ratio 1:1; then read the returned path."*
- **`tts`** — fields `text` (1–15000 chars), `output_path` (required; `.wav` ⇒ WAV, anything else ⇒ MP3 which only the cloud backends emit — the local backend then writes a sibling `.wav` and says so), `voice_id`, `language`, `sample_rate`, `bit_rate` (xAI only). Local voice comes from `tts.localVoice = af_heart` (also `af_bella … bm_fable`), model `kokoro`. Card: `Saved <bytes> bytes to <path> (voice=…, codec=…, backend=…)`. Shell twin: `omp say "text" [--voice id]`. One prompt: *"Use tts to write notes/hello.wav saying 'Module eight complete.'"*
- **`ida`** — actions `list`, `open {db: bin/crash}`, `save`, `close`, `exec {code}` (persistent Python namespace with `db`, `functions()`, `strings()`, `xrefs_to()`, `pseudocode()`…), `rename`, `comment`, `set_type`, `make_function`; `db` may be a binary, an `.i64`/`.idb`, or an open id; each DB runs in an `omp.ida.<id>` daemon (`omp ps` lists it); `ida.maxOpen = 4`, `ida.idleCloseSec = 900`. One prompt: *"Use ida to open bin/crash, list functions matching 'user', and show pseudocode for main."*

**Try it (Walkthrough):** (needs `gh` installed and `gh auth login` done; the lab must be pushed to a GitHub repo you can write to)

1. `omp config get github.enabled` → `false`. Then `omp config set github.enabled true` and start `omp`.
   **Expected:** the second `get` prints `true`; inside the session `read xd://` now lists `xd://github` (or the tool appears top-level if you passed `--tools github`).
2. Type: `read issue://1`
   **Expected:** the rendered issue #1 ("obvious one-line bug") with its body; no `gh` bash card.
3. Type: `Use github pr_create (draft) from the current branch: title "M8 toolbox exercises", body "Closes #1". Then run_watch the resulting run.`
   **Expected:** an approval prompt if you are not in `yolo` mode, then `# Created Pull Request …` with a URL; a live `run_watch` card that settles with the run status (or `no runs` after 90 s if the repo has no workflow).
4. Type: `read pr://<number>/diff`
   **Expected:** the list of changed files from the PR you just created.

**Guided task:** enable `github.enabled`; `read issue://1`; create a PR from the current branch. Pass: a PR URL appears in the transcript **and** `gh pr view --json url` in a shell prints the same URL.

**Stretch:** `security_scan` preflight + start on the lab; read findings via `security://`. Pass: `read security://scans` lists a scan whose status is `completed` (or `partial`), and `read security://scans/<id>/report` returns a Markdown report. (Needs `security.enabled true` and an OAuth login for your active provider.)

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `github` never appears even after enabling | `gh` not on PATH — tool is created only when found | install GitHub CLI; restart the session |
| `GitHub CLI is not authenticated` | no `gh` login | `gh auth login` |
| `GitHub repository context is unavailable` | cwd is not a GitHub checkout | pass `repo: owner/name` |
| `run_watch` gives up after 90 s | no workflow runs for that commit | add a workflow or pass a `run` id/URL |
| `Security is disabled…` | `security.enabled = false` | `omp config set security.enabled true` |
| `preflight` rejects credentials | API-key auth; only stored OAuth is accepted | `/login <provider>` with OAuth; pass `credential_id` if several |
| `Security scan plan is stale` | tree changed after preflight | run `preflight` again |
| `generate_image` aggregate error listing skipped candidates | no image model with credentials | `omp models --kind image`; set `modelRoles.image` or pass `model` |
| `tts` wrote `.wav` though you asked `.mp3` | local backend cannot encode MP3 | accept WAV, or configure xAI/DeepInfra credentials |
| `No xAI credentials…` | cloud backend selected without login | `/login` xAI or `XAI_API_KEY`; or use a `.wav` path for local |
| `ida` tool absent | no IDA install found or interpreter lacks `ida_domain` | set `ida.installDir`, `ida.python` |

**Cheat sheet:**

| Tool | Enable | One prompt |
|---|---|---|
| `github` | `omp config set github.enabled true` + `gh auth login` | "read issue://1, then github pr_create draft title … and run_watch" |
| `security_scan` | `omp config set security.enabled true` + OAuth login | "security_scan preflight repository excluding generated; start; status; read security://scans/<id>/findings" |
| `generate_image` | `omp config set generate_image.enabled true` + image model | "generate_image subject … aspect_ratio 1:1; read the returned path" |
| `tts` | `omp config set speechgen.enabled true` (+ `omp setup speech`) | "tts text … output_path notes/hello.wav" |
| `ida` | `ida.enabled=true` (default) + IDA install (`ida.installDir`) | "ida open bin/crash; exec functions('user')" |

**Source:** omp://tools/github.md, omp://tools/security_scan.md, omp://tools/generate_image.md, omp://tools/tts.md, omp://tools/ida.md, omp://tools/read.md (`issue://`, `pr://`, `security://`), omp://local-models.md (`omp setup speech`), `omp config list`, `omp say --help`, `omp setup --help`

---

## Module wrap-up

You now have five things to ask for by name:

| Ask for… | when |
|---|---|
| `read <path with selector>` | data in a DB, archive, PDF, notebook, URL, PR |
| `eval` | multi-step data work, charts, structured results, calling tools from code |
| `lsp rename` / `ast_edit` + `xd://resolve` | refactors that must be semantic, previewed, atomic |
| `debug` | any crash you would otherwise print-debug |
| `github` / `security_scan` / `generate_image` / `tts` / `ida` | after flipping the key in `cheatsheet.md` |

Next: Module 10 builds on `eval` (`agent()`, `workpool()`, `@tool`) and Module 14 on the `browser`/`computer` preludes.
