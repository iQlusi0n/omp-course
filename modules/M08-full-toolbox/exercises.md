# Module 8 — Exercises

Start state: `cd omp-course-lab && git checkout module-8-start`. Learner outputs go in `notes/` (gitignored). Every exercise names its tier (**W** walkthrough, **G** guided, **S** stretch), an estimated time, prerequisites beyond omp 18.3.1 + Python 3, and an observable pass condition. Instructor notes: `solutions/README.md`.

Prerequisite summary for the whole module (install what you need before starting):

| Lesson | Needs |
|---|---|
| 8.1 | network for the URL and web-search steps; `sshd` on localhost only for 8.1-S |
| 8.2 | Python ≥ 3.10 resolvable by omp (`omp setup python --check`); `pip` in that interpreter for `%pip`; matplotlib installable |
| 8.3 | `pyright-langserver` (`npm i -g pyright`) **or** `pylsp` (`pip install python-lsp-server`) on PATH; a judge model for `find` (`TYPESAFE_API_KEY`, or `find.enabled on`) |
| 8.4 | `pip install debugpy` into the interpreter `python` resolves to; for C: a compiler and `gdb` or `lldb-dap` |
| 8.5 | `gh` + `gh auth login` and push access to a GitHub copy of the lab; OAuth login for `security_scan`; image/speech backends optional |

---

## 8.1 — `read` beyond text

### 8.1-W  Four formats, four cards (10 min)
Type, one at a time: `read docs/spec.pdf:1-40` · `read data/lab.sqlite:orders?limit=5` · `read fixtures/bundle.zip:README.md` · `read https://github.com/can1357/oh-my-pi`.
**Pass:** four `read` cards with structured output: `<!-- Page 1 -->` in the first, a 5-row Markdown table with a `[N more rows; …offset=5…]` footer in the second, the README text in the third, `Method: github-repo` in the fourth. No `bash` cards. Save the four card bodies to `notes/m8-read.md`.

### 8.1-W  Write to a database row and an archive member (5 min)
Prompt:

```text
Insert a user named Grace (email grace@lab.test) with the write tool into data/lab.sqlite:users, read it back with ?where=, then add a file notes/todo.txt containing 'hello' inside fixtures/bundle.zip and read it back.
```

**Pass:** cards `Inserted row into users`, a `read` with a `?where=` clause (`name='Grace'` or `email='grace@lab.test'`) showing the new row, `Successfully wrote 5 bytes to fixtures/bundle.zip:notes/todo.txt`, and `read fixtures/bundle.zip:notes/todo.txt` → `hello`. Then `git checkout -- data/lab.sqlite fixtures/bundle.zip`.

### 8.1-G  Busiest month, no shell (10 min)
Goal: find the month with the most orders.
Hints: `?q=SELECT … GROUP BY substr(created_at,1,7)`; `order=` and `limit=` also exist on the table form.
Checkpoints: (a) `read data/lab.sqlite` lists `orders`; (b) one `read` card holds the aggregate.
**Pass:** zero `bash` cards; a `read` card whose path starts with `data/lab.sqlite?q=`; the answer written to `notes/m8-busiest.txt` matches `python3 -c "import sqlite3;print(sqlite3.connect('data/lab.sqlite').execute('select substr(created_at,1,7),count(*) from orders group by 1 order by 2 desc limit 1').fetchone())"`.

### 8.1-G  Pinned search provider (5 min)
Goal: run the same query through two engines from the shell and note the difference in `Method`/sources.
Hints: `omp q --model web/duckduckgo "…"`, `omp q --model web/startpage "…"`; `-l 3` limits results.
**Pass:** `notes/m8-search.md` contains both boxed outputs and names the two providers shown in the panel headers.

### 8.1-S  Read yourself over SSH (10 min; needs local `sshd`)
Goal: read the lab's `README.md` through omp's SSH transport, pointed at your own machine.
**Pass:** the `read` card's source is an `ssh://self/…` URL and `diff <(omp read ssh://self/…/README.md) <(omp read README.md:raw)` is empty (ignoring the hashline header).

---

## 8.2 — `eval` kernels

### 8.2-W  Retained state and the tool bridge (10 min)
Three prompts, three cells: build `by_month` from `data/lab.sqlite` and `display()` it; `display(sum(by_month.values()))` in a new cell without reloading; `display(await tool.read({'path':'data/lab.sqlite'}))`.
**Pass:** three `eval` cards; the second cell's code has no `sqlite3.connect`; the third shows `"text": "orders (72 rows)\nschema_version (1 rows)\nusers (12 rows)"` under `display[1]:`.

### 8.2-W  `reset` wipes state (3 min)
Prompt:

```text
Reset the Python kernel and display(by_month).
```

**Pass:** the card shows `NameError: name 'by_month' is not defined` and `Command exited with code 1`.

### 8.2-G  Orders per month, plotted (15 min)
Goal: load `data/lab.sqlite` from inside `eval` through the tool bridge (`tool.read` with the `?q=` raw-SQL form), compute orders per month, and plot the result to `notes/orders.png`.
Hints: `%pip install matplotlib` first (standalone cell); keep the parsed rows in a variable; `plt.savefig('notes/orders.png')`; the figure is also auto-captured inline.
Checkpoints: (a) cell 1 contains `await tool.read`; (b) plotting cell contains neither `tool.read` nor `sqlite3`; (c) inline image appears in the card.
**Pass:** `test -s notes/orders.png` succeeds **and** the plotting cell reuses the variable (no reload).

### 8.2-G  Structured one-shot call (5 min)
Goal: use `completion()` with a JSON schema to extract `{"month": "..."}` for the busiest month from `by_month`.
Hints: `completion(prompt, model="smol", schema={...}).wait()`; the wait does not count against the 30 s cell timeout.
**Pass:** the card's `display[1]:` is an object with a single `month` key whose value is one of `by_month`'s keys.

### 8.2-S  `%load` and the watchdog (10 min)
Goal: prove that a `%load`-ed helper survives a kernel timeout.
**Pass:** the sleeping cell's card contains `eval cell timed out after 30s; kernel interrupted but remains running`, and the following cell still calls `by_month()` successfully.

---

## 8.3 — Code intelligence

### 8.3-W  Devices and server status (5 min)
Prompts: `read xd://` · `Call lsp with action=status`.
**Pass:** the first card lists `xd://ast_edit`, `xd://debug`, `xd://lsp`; the second reads `Language servers: pyright (configured, not started)` (or `pylsp …`) — **not** `No language servers configured for this project`.

### 8.3-W  Preview, then apply a rename (10 min)
Prompts: `lsp references` for `get_user` on its `def` line in `api/db.py`; `lsp rename` with `apply: false` to `fetch_user`; then the same rename applied.
**Pass:** the preview lists `api/__init__.py`, `api/server.py`, `cli/commands.py` and a test file; after apply, `git diff --stat` touches those files and `python3 -m unittest discover -s tests` prints `OK` (fix any string-literal `get_user` — e.g. an `__all__` entry — with `edit` first).

### 8.3-W  Codemod with preview and `xd://resolve` (10 min)
Start omp with `astGrep.enabled` on (`omp config set astGrep.enabled true` or a `--config` overlay). Prompts: `ast_grep` pattern `print($$$A)` on `cli`; `ast_edit` `print($$$A)` → `logger.debug($$$A)` on `["cli"]`; *"apply the staged proposal by writing a reason to xd://resolve"*; then grep and tests.
**Pass:** `Staged as a proposal — files NOT modified yet` card, then `Applied 10 replacements in 1 file.` (all 10 `print(` calls live in `cli/commands.py`; the docstring mentions in `cli/log.py` are not matched).
Afterwards `grep -rn "print(" cli/commands.py` is empty (`grep -rn "print(" cli/` still shows the two docstring lines in `cli/log.py`), and tests are `OK` after adding `from cli.log import logger` to `cli/commands.py`.

### 8.3-G  Rename + codemod end to end (15 min)
Goal: LSP rename `get_user` → `fetch_user` across `api/` (re-exported from `api/__init__.py`); then `ast_edit` `print($$$A)` → `logger.debug($$$A)` in `cli/`, accepting the proposal.
Hints: rename first; `lsp references` before `rename`; `cli/log.py` already exports `logger`; multi-argument prints need a second look after the codemod.
Checkpoints: (a) references ≥ 4 files; (b) `Applied rename:`; (c) `Staged as a proposal`; (d) `write xd://resolve` → `Applied …`.
**Pass:** `grep -rn "print(" cli/commands.py` prints nothing; tests pass; `grep -n fetch_user api/__init__.py` shows the re-export.

### 8.3-G  Semantic find (5 min; needs a judge)
Goal: locate "where the HTTP handler looks up a user by id" without knowing file names.
Hints: `omp find -q "…" .` or the `find` tool; add `-k get_user` style keywords if the lexical pass is thin; `omp config set find.enabled on` if the tool is hidden.
**Pass:** top hit is under `api/` with a range that contains the handler; the footer shows `judged N` > 0.

### 8.3-S  Project LSP override and file move (15 min)
Goal: disable `pylsp` for this project only, then move `api/db.py` to `api/storage/db.py` with a server-driven file move so the imports follow, and make the tests pass.
**Pass:** `lsp status` no longer lists `pylsp`; `git status` shows the rename plus updated imports; tests `OK`.

---

## 8.4 — Real debugging (DAP)

### 8.4-W  Break, inspect, fix (15 min; needs debugpy)
Reproduce `python bin/crash.py` (exit 1). Prompts: launch under debugpy; breakpoint at the failing line; continue; `stack_trace`, `scopes`, `variables`, `evaluate … context watch`; terminate; fix; rerun.
**Pass:** cards `Stop reason: entry` → `line 39: verified` → `Stop reason: breakpoint` (frame `display_name`) → `Variables: - user = None (NoneType)` → `Debug session terminated.`; final `bash` card runs `python bin/crash.py` with exit 0 and prints a line for every id in `WANTED_IDS` (99 marked unknown).

### 8.4-G  Python and C, same workflow (20 min; C needs `cc` + `gdb`/`lldb-dap`)
Goal: for `bin/crash.py` and `bin/crash.c`, attach a debugger, break at the failing line, report the offending variable, fix.
Hints: `cc -g -O0 -o bin/crash bin/crash.c`; `launch program=bin/crash adapter=gdb` (stops at `main`; `continue` to the fault or set a breakpoint); `terminate` between sessions (one root session at a time).
Checkpoints: (a) two sessions; (b) a `variables`/`evaluate` card per program showing `user = None` (Python, in `display_name`) / `u = 0x0` (C, in `main` at `bin/crash.c:45`); (c) both fixed.
**Pass:** transcript shows `debug` cards with `scopes`/`variables` for **both** programs; `python bin/crash.py; echo $?` and `./bin/crash; echo $?` both print `0`.

### 8.4-S  Print-debug vs DAP, plus a conditional breakpoint (15 min)
Goal: fix the same Python crash twice — once by print-debugging only in a fresh session without `debug`, once with `debug` and a *conditional* breakpoint that skips the good ids — and compare the cost of each approach.
**Pass:** `notes/m8-debug.md` lists both tool sequences with counts; the conditional-breakpoint card says `verified`; the first `variables` card after `continue` shows `user_id = 99` and `user = None` (an unconditional breakpoint on the same line stops first at `user_id = 1`).

---

## 8.5 — Setting-gated tools

### 8.5-W  Turn on `github` and read an issue (5 min; needs `gh`)
`omp config get github.enabled` (→ `false`), `omp config set github.enabled true`, new session, `read issue://1`.
**Pass:** the second `get` prints `true`; `read xd://` lists `xd://github`; the issue card shows issue #1's title and body with no `gh` bash card.

### 8.5-G  PR from the current branch (10 min)
Goal: enable `github.enabled`; `read issue://1`; create a (draft) PR from the current branch; then `read pr://<n>/diff`.
Hints: `pr_create` needs `title` or `fill: true`; it asks for exec approval outside `yolo`; push the branch first if `gh` complains.
**Pass:** a PR URL in the transcript that matches `gh pr view --json url -q .url`; the diff listing names your changed files.

### 8.5-G  One prompt each (10 min; optional backends)
For each tool you can enable, run its one-line prompt from `cheatsheet.md` and record the card's first line in `notes/m8-gated.md`.
**Pass:** `notes/m8-gated.md` has one line per enabled tool, each line copied from a real card (`Saved … bytes to notes/hello.wav …`, `omp-image-…`, `Opened …`).

### 8.5-S  Security scan (20 min; OAuth login required)
Goal: run a security scan on the lab and read its findings.
**Pass:** `read security://scans` lists the scan as `completed` or `partial`; `read security://scans/<id>/report` returns Markdown; one finding (if any) is `validate`d with a summary and the finding card shows the new status.
