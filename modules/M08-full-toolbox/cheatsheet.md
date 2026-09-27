# Module 8 cheat sheet — The Full Toolbox (omp/18.3.1)

## `read` selectors (also `omp read <path>` from a shell)
| Target | Path string |
|---|---|
| line ranges / raw / conflicts / SVG as image | `f:50-100` · `f:50+20` · `f:5-16,40-80` · `f:raw` · `f:conflicts` · `f.svg:img` |
| document (pdf docx pptx xlsx rtf epub) | `docs/spec.pdf:1-40` |
| archive list / member / folder | `x.zip` · `x.zip:README.md` · `x.zip:dir` (tar, zip family, 7z, rar, iso, deb, rpm, asar, gz…) — lab: `fixtures/bundle.zip` = `README.md`, `data/sample.csv`, `config.json` |
| SQLite tables / schema+5 rows / row by PK | `db.sqlite` · `db.sqlite:t` · `db.sqlite:t:42` — lab tables `users`, `orders`, `schema_version` |
| SQLite query / raw SQL | `db.sqlite:t?limit=20&offset=0&order=c:desc&where=…` · `db.sqlite?q=SELECT …` (≤1000 rows) — lab: `data/lab.sqlite:orders?order=total_cents:desc&limit=5` |
| notebook | `nb.ipynb` (cells as `# %% [code] cell:N`) · `:raw` |
| image question | `shot.png?q=…` (vision role) |
| URL | `https://…` (site handlers, e.g. `Method: github-repo`) · `:raw` · `:1-40` pages cache |
| GitHub | `pr://N` · `issue://N` · `pr://owner/repo/N` · `pr://N/diff` · `/diff/all` · `?comments=0` · bare `issue://?state=open` |
| remote | `ssh://host/path` · bare `ssh://` lists · `omp ssh add <name> --host … --user …` |
| devices | `xd://` list · `xd://<tool>` schema · `write xd://<tool>` JSON call |

## `write` targets
`db.sqlite:t` (insert JSON5) · `db.sqlite:t:42` (update; empty = delete) · `x.zip:inner/file` (atomic rewrite; zip/tar/tgz/tar.zst/asar) · `conflict://N` with `@ours|@theirs|@base|@both` · `xd://resolve` / `xd://reject` (body = reason)

## `web_search`
`web_search.enabled=true` · role `modelRoles.web` + `retry.fallbackChains.web` (unset → built-in chain, `web/parallel` first) · `providers.webSearchTimeoutSeconds=60` · shell: `omp q --model web/duckduckgo -l 3 "…"` (`omp q` = `omp search` = `omp web-search`)

## `eval`
| | |
|---|---|
| call | `language: py\|js`, `code`, `title`, `timeout` (30 s; 0 = none; ≤ 3600), `reset` |
| keys | `eval.py=true` `eval.js=true` `eval.tools.enabled=true` `python.kernelMode=session\|per-call` `python.interpreter=""` · env `PI_PY` `PI_JS` |
| ⚠ off | `eval.autoBackground.enabled=false` (`thresholdMs=60000`) |
| helpers | `display()` `read()` `write()` `env()` `log()` `phase()` · `await tool.<name>({…})` · `completion(prompt, model="smol", system=, schema=).wait()` |
| magics | `%pip install x` · `%load f.py` · `%cd` `%env` `%time` `%reset` `%%bash` `!cmd` · JS `%bun add x` `%environment project` |
| gotchas | no `input()`; top-level `await` ok, `asyncio.run` not; >50 KiB → `artifact://`; figures auto-captured |

## `lsp`
| | |
|---|---|
| actions | `diagnostics` (`file:"*"` = project checker) · `definition` `references` `hover` `symbols` `type_definition` `implementation` · `rename` (applies unless `apply:false`) · `rename_file` · `code_actions` (`apply:true, query:idx\|title`) · `status` `reload` `capabilities` `request` |
| fields | `file` `line` (1-based) `symbol` (`name#2`; required with `line` for definition/references/rename) `new_name` `apply` `timeout` (20 s, 5–300) |
| keys/flags | `lsp.enabled=true` `lsp.lazy=true` `lsp.shared=true` `lsp.diagnosticsOnWrite=true` ⚠ `lsp.formatOnWrite=false` · `--no-lsp` |
| auto-detect | root marker in **cwd** + binary on PATH/venv. Python: `pyright-langserver` `basedpyright-langserver` `pylsp` `ty` `ruff`; markers `pyproject.toml setup.py setup.cfg requirements.txt Pipfile` (+`pyrightconfig.json` for pyright) |
| config | `<cwd>/.omp/lsp.json` › `~/.omp/agent/lsp.json` · `{"servers":{"pylsp":{"disabled":true}},"idleTimeoutMs":300000}` · new server needs `command` `fileTypes` `rootMarkers` |

## `ast_grep` / `ast_edit` / `find` / devices
| | |
|---|---|
| pattern | `$X` one node · `$$$ARGS` many · `$_` `$$$` unbound · UPPERCASE · must parse as one node |
| ⚠ `ast_grep` | `astGrep.enabled=false` → `omp config set astGrep.enabled true` · `pat` `path` (`a; b`, globs, URLs) `skip` · 50/page |
| `ast_edit` | `astEdit.enabled=true` · `ops:[{pat,out}]` `paths:[…]` · always previews (`Staged as a proposal…`) · apply: `write xd://resolve "<reason>"` · discard: `xd://reject` · stale preview refused · `PI_MAX_AST_FILES=1000` |
| `find` | `find {query, grep_keywords:[], path}` · `omp find "<q>" [path] -k kw --json -q` · `find.enabled=auto\|on\|off` · judge role `modelRoles.judge`; built-in chain `typesafe/jev-latest`, `openrouter/~typesafe/jev-latest`, `tiny`, `smol`, `default`, active model; `auto` needs a TypeSafe jev judge |
| devices | `tools.xdev=true` `tools.xdevDocs=catalog` · stock session mounts `xd://ast_edit xd://debug xd://lsp` · `omp --tools a,b,c` pins · `--no-tools` |

## `debug` (DAP)
`debug.enabled=true` · `launch {program, adapter?, args?, cwd?}` (stops on entry) → `set_breakpoint {file,line | function, condition?}` → `continue` → `stack_trace` → `scopes {frame_id?}` → `variables {variable_ref|scope_id}` → `evaluate {expression, context:"watch"}` → `terminate` · `attach {pid}` / `{port,host}` · one root session · timeout 30 s (5–300)
Adapters: `debugpy` (`python -m debugpy.adapter` — needs `python` on PATH), `gdb` (`gdb -i dap`), `lldb-dap`, `codelldb`, `dlv`, `js-debug-adapter`… · custom: `.omp/dap.json` `{"adapters":{"<id>":{command,args,fileTypes,rootMarkers,launchDefaults,attachDefaults,connectMode}}}` · lab fixtures: `bin/crash.py` (`AttributeError` on `user.name` in `display_name`, line 39) · `cc -g -O0 -o bin/crash bin/crash.c` (NULL `u` in `main`, line 45)

## Setting-gated tools
| Tool | Enable | Needs | One prompt |
|---|---|---|---|
| `github` | ⚠ `github.enabled=false` → `true` | `gh` + `gh auth login` | "read issue://1; github pr_create draft title …; run_watch" |
| `security_scan` | ⚠ `security.enabled=false` → `true` | git + OAuth credential | "preflight repository exclude generated; start; status; read security://scans/<id>/findings" |
| `generate_image` | ⚠ `generate_image.enabled=false` → `true` | image model (`omp models --kind image`, `modelRoles.image`) | "generate_image subject … aspect_ratio 1:1; read the returned path" |
| `tts` | ⚠ `speechgen.enabled=false` → `true` | local Kokoro (`omp setup speech`) or xAI/DeepInfra | "tts text … output_path notes/hello.wav" (`omp say` from shell; `tts.localVoice=af_heart`) |
| `ida` | `ida.enabled=true` + IDA install (`ida.installDir`, `$IDADIR`) | interpreter importing `ida_domain` (`ida.python`) | "ida open bin/crash; exec functions('user')" |

Results: `artifact://<id>` (run_watch logs) · `security://scans[/<id>[/findings|/report|/sarif|/coverage]]` · `/tmp/omp-image-<id>.<ext>` · `notes/hello.wav`
