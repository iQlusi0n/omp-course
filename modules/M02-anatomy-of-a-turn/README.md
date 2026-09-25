# Module 2 — Anatomy of a Turn

| | |
|---|---|
| **Level** | basic |
| **Time** | ~1.5 h (6 lessons + coursework) |
| **Built against** | `omp --version` → `omp/18.3.1` |
| **Prerequisite** | Module 1 (installed, logged in, ran one prompt in `omp-course-lab`) |
| **Start state** | `cd omp-course-lab && git checkout module-2-start` |
| **Goal** | Read the TUI fluently; know what each built-in tool does and how to inspect what it did. |

Every card shape in this module was rendered with `omp gallery --plain` (the binary's deterministic renderer preview) and the model-facing `read` text with `omp read`; the content inside the cards was then rewritten to match the lab repo. Nothing here is a screenshot of a third-party guide.

Lessons:

- [2.1 TUI layout](#lesson-21--tui-layout-15-min)
- [2.2 The core tool set](#lesson-22--the-core-tool-set-25-min)
- [2.3 Why edits are reliable: hashline](#lesson-23--why-edits-are-reliable-hashline-10-min)
- [2.4 `bash` behaviors you'll notice](#lesson-24--bash-behaviors-youll-notice-20-min)
- [2.5 `ask` and `todo`](#lesson-25--ask-and-todo-10-min)
- [2.6 Composer skills](#lesson-26--composer-skills-10-min)

Coursework is in [`exercises.md`](exercises.md); the one-page reference is [`cheatsheet.md`](cheatsheet.md).

---

## Lesson 2.1 — TUI layout              (~15 min)
**You will be able to:** name the five regions of the omp screen; expand, hide, and re-show tool output; stop a turn; find any chord with `/hotkeys`.
**Why this exists:** A terminal agent does most of its work *between* your prompts — reading, searching, editing, running. Chat UIs hide that; omp puts every step on screen as a *card* so you can audit it. If you can't read the cards you are trusting the model's summary of its own work, which is the one thing the course tells you never to do. Learn the layout once and every later module gets faster.
**Demo:** [`demos/2.1-tui-layout.md`](demos/2.1-tui-layout.md) — one prompt, the resulting transcript, and the status band, with each region labelled.
**Concepts:**
- **Transcript** (top, scrolls into terminal history): your prompts, assistant prose, thinking blocks, and tool cards in the order they happened. Tool cards come in two shapes: *inline one-liners* (`🔍 Grep: …`, `🔍 Glob: …`, `ⓘ Proc …`) and *boxed cards* (`╭─── • Read … ╮`, `✎ Edit`, `$ cmd` with an `Output` section, `☑ Todo`, `✔ Ask`, `⌕ Web Search`). Boxed cards are collapsed by default to a short preview (bash: 10 visual lines; write: 6 lines; todo: 8 items) and show `⟦Ctrl+O: Expand⟧` when there is more.
- **Composer** (bottom): the editor you type into. Its border/band carries the status line. The default composer shape is `band` ("Status Band"); `composer.shape` selects others (`box`, `claude`, `pi`, `borderless`, `rule`, `field`, `rail` — preview them with `omp gallery --surface composer`).
- **Status line** segments (default preset `statusLine.preset: default`): `π` idle / `⠹ 1m` spinner + elapsed while a turn runs; `⬢ <model> · ◒ <thinking level>`; a mode chip when active (`🗺 Plan`, `🏃 Prewalk`, `👥 Vibe`); `⑂ <branch> *3 +2 ?1` git state; `◫ 62.0%/200K ⟲` context usage over the window. The trailing `⟲` is the **auto-compact icon**: it pulses while omp speculatively summarizes in the background and holds accent colour when a summary is armed and waiting for the threshold (Module 5 covers compaction). `statusLine.contextLine` (`embedded` by default) controls where the context gauge lives.
- **Todo HUD**: a sticky panel that appears above the composer once the model calls the `todo` tool. `/todo expand` shows every phase and task; `/todo collapse` restores the bounded preview. Closed items fade after `tasks.todoClearDelay` (default `60` s; display-only).
- **Pinned `Subagents` block**: appears above the editor while subagents run (Module 10). `display.pinnedAgents` is `collapsed` by default (`full` lists all, `off` hides).
- **Keys you use every minute** (all default chords; action IDs in parentheses are what you remap in `~/.omp/agent/keybindings.yml`):

  | Key | Action | Notes |
  |---|---|---|
  | `Esc` | Interrupt the running turn | `interruptMode` default `immediate` (`wait` defers until the current tool finishes). With an **empty** editor, a double `Esc` opens the rewind selector (`doubleEscapeAction: rewind`; set `none` to disable). |
  | `Ctrl+O` | Toggle tool-output expansion (`app.tools.expand`) | Expands the boxed cards to everything the tool returned inline. |
  | `Ctrl+Shift+O` | Show/hide tool activity (`app.tools.toggleVisibility`) | Same as `display.hideToolActivity` (default `false`). Hidden ≠ gone: the cards are still in the session. |
  | `Ctrl+T` | Toggle thinking-block visibility (`app.thinking.toggle`) | Display only. `hideThinkingBlock` (default `false`) and `--hide-thinking` set the same thing. |
  | `Ctrl+C` | Clear the draft; press twice to exit | Cleared drafts are recoverable — see 2.6. |
  | `/hotkeys` | List the active chords for your build, including remaps and extension bindings | The authoritative answer when a key "does nothing". |

**Try it (Walkthrough):**
1. `cd omp-course-lab && git checkout module-2-start && omp`.
   Expected: empty transcript; status line shows `π`, your model, `⑂ main` (or the tag name), and `◫ <low>%/<window>`.
2. Type `/hotkeys` and press Enter.
   Expected: a list of action IDs with chords. Find `app.tools.expand` → `Ctrl+O` and `app.thinking.toggle` → `Ctrl+T`.
3. Prompt: `Explain how api/ handles a request. Read only; do not edit anything.`
   Expected: the status `π` becomes a spinner with elapsed time; inline `🔍 Glob:` and `🔍 Grep:` lines and boxed `• Read api/…` cards appear; then assistant prose.
4. Press `Ctrl+O`.
   Expected: every boxed card expands to its full content (line-numbered file text in `Read` cards). Press `Ctrl+O` again to collapse.
5. Press `Ctrl+Shift+O`.
   Expected: all tool cards disappear; only prose remains. Press again to bring them back.
6. Press `Ctrl+T`.
   Expected: thinking blocks toggle (if your model emitted any; with `defaultThinkingLevel: high` most do).
7. Ask a longer question (`Walk every file in cli/ and summarize each function`), then press `Esc` mid-turn.
   Expected: the streaming stops; the partial assistant message stays in the transcript; the status line returns to `π`.

**Guided task:** Goal — capture the anatomy of one turn in writing. Hints — use the prompt from step 3; the inline vs boxed distinction; `Ctrl+O` before you write. Checkpoints — (a) you can point at the first tool the model called; (b) you know which cards were inline and which were boxed. Pass condition — `notes/m2.md` exists and lists, in order, every tool card from that turn with its shape (`inline`/`boxed`) and one line of what it did.
**Stretch:** Goal — remap `app.tools.expand` to `Ctrl+E` in `~/.omp/agent/keybindings.yml`, restart omp, confirm with `/hotkeys`. Pass condition — `/hotkeys` shows `app.tools.expand: Ctrl+E`; `Ctrl+O` no longer expands cards. (Remove the remap afterwards; the rest of the course assumes defaults.)
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `Ctrl+O` / `Ctrl+Shift+O` do nothing | Terminal lacks the kitty keyboard protocol, or another program (tmux, shell) swallows the chord | Module 1.3 terminal table; run `/hotkeys` to confirm what omp thinks the chord is |
| `Esc` doesn't stop the turn immediately | `interruptMode: wait` | `omp config get interruptMode`; set `immediate` |
| Double `Esc` opened a full-screen list | That's the rewind selector (`doubleEscapeAction: rewind`) | `Esc` again to close; set `doubleEscapeAction: none` if you keep hitting it |
| No thinking block ever appears | Thinking level `off`/`minimal`, or `hideThinkingBlock: true`, or `--hide-thinking` | `Shift+Tab` cycles the level (Module 3); check the setting |
| Cards vanished and stay gone | `display.hideToolActivity: true` persisted | `Ctrl+Shift+O` or `omp config set display.hideToolActivity false` |

**Cheat sheet:**

| Item | Value |
|---|---|
| Expand cards | `Ctrl+O` (`app.tools.expand`) |
| Hide/show tool activity | `Ctrl+Shift+O` (`app.tools.toggleVisibility`, `display.hideToolActivity`) |
| Thinking visibility | `Ctrl+T` (`app.thinking.toggle`, `hideThinkingBlock`) |
| Stop a turn | `Esc` (`interruptMode: immediate`) |
| Rewind picker | `Esc Esc` on an empty editor (`doubleEscapeAction`) |
| All chords | `/hotkeys`; remap in `~/.omp/agent/keybindings.yml` |
| Todo HUD | `/todo expand`, `/todo collapse`, `tasks.todoClearDelay` |
| Composer/status preview | `omp gallery --surface composer`, `omp gallery --surface segment` |

**Source:** omp://keybindings.md, omp://settings.md, omp://compaction.md, omp://tools/todo.md, omp://agent-hub.md, omp://tree.md, omp://bash-tool-runtime.md, `omp gallery --help`, `omp config list`

---

## Lesson 2.2 — The core tool set              (~25 min)
**You will be able to:** recognise each of the nine core tools by its card; read the arguments the model passed; know each tool's limits well enough to predict when output will be truncated; recover full output from `artifact://N`.
**Why this exists:** The model does not "see your repo". It sees only what tools return, under hard caps (300 lines per open-ended read, 50 KB per tool result, 20 files per grep page). Knowing the caps tells you *why* omp re-read a file in three chunks, why it asked for `skip=20`, and why a test run's output ends in `Read artifact://7 for full output`. Once you can read the card you can also tell the model exactly what to do next ("read artifact://7:raw:1-200").
**Demo:** [`demos/2.2-core-tools.md`](demos/2.2-core-tools.md) — one turn on the lab repo that uses `glob`, `grep`, `read` (range + directory), `edit`, `write`, `bash` (with an artifact spill), `todo`, `ask`, and `web_search`, followed by the learner asking omp to read the artifact.
**Concepts:**

*What each tool takes and what its card shows.* (Field names are the tool's real parameter names — you will see them in expanded cards and in `--mode json` output later.)

| Tool | Arguments | Card | Limits that shape behaviour |
|---|---|---|---|
| `read` | `path` — a file, directory, URL, internal URI, with optional trailing selector | Boxed `• Read <path>[:sel]`; line-numbered body | Open-ended read: `read.defaultLimit` = 300 lines. Bounded range `:A-B` adds 1 line of context before and 3 after. Directories: depth 2, 12 entries per dir, sorted by recency with sizes/ages. Code files ≥ 100 lines with no selector come back as a **structural summary** (declarations kept, bodies elided, footer `[…NNln elided; re-read needed ranges, e.g. path:5-16,40-80]`); `read.summarize.enabled` is `true` by default and prose (`.md`/`.txt`) is never summarized unless `read.summarize.prose: true`. |
| `grep` | `pattern` (regex), `path` (file/dir/glob, or `a; b` list, or `file:50-100`), `case` (default `true`), `gitignore` (default `true`), `skip` | Inline `🔍 Grep: <pattern> N matches · M files · in <scope>` with a folded tree | 20 files per page (`Use skip=<N> for the next page`), 20 matches per file in multi-file scope, 200 in a single file; context 1 before / 3 after (`grep.contextBefore`/`grep.contextAfter`); 512-char line cap; 30 s timeout; engine is Rust regex → PCRE2 (lookaround/backrefs) → literal fallback. |
| `glob` | `path` (glob/dir/file, or `a; b` list), `hidden` (default `true`), `gitignore` (default `true`), `limit` (≤ 200) | Inline `🔍 Glob: <pattern> N files · in <base>` | Bare `*.py` is made recursive (`**/*.py`); `src/*.py` stays non-recursive. Newest mtime first. 5 s timeout returns a partial result. |
| `edit` | `input` — one or more `[PATH#TAG]` sections of hashline ops (2.3) | Boxed `✎ Edit: <file> ⟦+a/-r⟧` with a unified diff | Existing files only; tag must come from a prior `read`/`grep`/`edit`/`write`. |
| `write` | `path`, `content` | Boxed `✎ Write: <file> · N lines`, first 6 lines + `… N more lines ⟦Ctrl+O: Expand⟧` | Creates or wholly overwrites; parent dirs created. Refuses generated-looking files (`edit.blockAutoGenerated`, default `true`). Also writes archive entries, SQLite rows, `proc://` stdin, `agent://` messages (Modules 8/10). |
| `bash` | `command`; `timeout` (s, default 300, `0` = none, clamped 1–3600); `cwd`; `pty`; `async`; `name`+`ready`+`env` for services | Boxed `$ <command>` / `Output` / footer `⟦Wall: 0.18s \| Timeout: 300s⟧`; failed adds `\| Exit: N` and a red frame | stdout+stderr merged; empty output prints `(no output)`; non-zero exit ends with `Command exited with code N` and the card is marked failed. |
| `todo` | one op: `init`/`start`/`done`/`drop`/`block`/`unblock`/`rm`/`append`/`view` with `list`/`items`/`task`/`phase` | Boxed `☑ Todo N tasks` tree, and the sticky HUD | Exactly one task `in_progress` at a time; tasks are addressed by exact content string. |
| `ask` | `questions[]` — each `{id, question, options[{label, description}], multi?, recommended?}` | Boxed `Ask N questions` with radio (`◉/○`) or checkbox (`☑/☐`) groups; `✔ Ask` when answered | Interactive only; runs alone (no other tool in the same batch). |
| `web_search` | `query`, `recency` (`day`/`week`/`month`/`year`), `limit`, `num_search_results` | Boxed `⌕ Web Search: <Provider> N sources` with `Query`/`Answer`/`Sources`/`Metadata` | Provider chain comes from `modelRoles.web` (Module 7/8); `web_search.enabled` is `true` by default; per-provider timeout `providers.webSearchTimeoutSeconds` (60). |

*Reading the arguments.* The collapsed header already contains the arguments that matter: the path and selector for `read`, the pattern/scope/counts for `grep`, the command for `bash`. `Ctrl+O` shows the rest.

*Truncation and `artifact://`.* Every tool result is bounded before the model sees it. The shared limits are 3 000 lines / 50 KB (`tools.artifactSpillThreshold` = 50 KB). When `bash` (or any streaming tool) crosses the threshold the full sanitized output is mirrored to a file in the session's artifact directory (`~/.omp/agent/sessions/<cwd>/<timestamp>_<id>/<N>.bash.log`) and the model-facing result keeps a head (`tools.artifactHeadBytes`, 20 KB) and a tail (`tools.artifactTailBytes` 20 KB / `tools.artifactTailLines` 500) with an elision marker between them. Over-wide lines are cut at `tools.outputMaxColumns` (768 bytes). The card shows a warning line naming the reason and `artifact://<id>`, and the model-facing text ends with `Read artifact://<id> for full output`. Artifact IDs are session-local integers; `read artifact://7`, `read artifact://7:1-200`, `read artifact://7:raw:1-3000` all work, and `grep <pattern> artifact://7` searches it. A whole-artifact read above 8 MiB is refused — page it. Artifacts survive `/resume` and are copied on `/fork`.

*How to ask omp to read one.* Plain English works: `Read artifact://7 and list every failing test name.` The model calls `read` with `path: artifact://7` (immutable, so no hashline header — you can't `edit` an artifact).

*Two CLI mirrors that need no model.* `omp read <path-or-uri>` prints exactly what the `read` tool would return (selectors included). `omp grep <pattern> [path]` runs the same native search engine and prints match counts and `file:line:` hits in its own diagnostic layout (not the model-facing `[PATH#TAG]` layout) — handy for checking what a pattern would match. Use them whenever you want to predict what the model will see.

**Try it (Walkthrough):**
1. Outside omp: `omp read api` then `omp read api/__init__.py`.
   Expected: a recency-sorted tree with sizes/ages; then a `[api/__init__.py#XXXX]` header followed by `N:text` lines — that header is a hashline tag (2.3).
2. `omp read docs/ISSUES.md:1-20`.
   Expected: lines 1–20 plus up to 3 trailing context lines and a `[Showing lines … of …]` footer — the same bounded-range behaviour the model gets.
3. Inside omp (`git checkout module-2-start`), prompt: `Find every place cli/ prints to stdout and list file:line. Read-only.`
   Expected: a `🔍 Grep: print\(` inline card with a folded `# cli/` tree, `*LINE│` match rows, and a `… N more matches` fold. Press `Ctrl+O` to see them all.
4. Prompt: `Run the test suite and show me the output.`
   Expected: a `$ python -m unittest discover -s tests` card with an `Output` section and a footer `⟦Wall: …s | Timeout: 300s⟧`. If a test fails the footer ends `| Exit: 1` and the last line is `Command exited with code 1`.
5. Prompt: `Print the first 4000 lines of the SQLite schema and data with sqlite3 or python, whichever exists.` (Anything that produces > 50 KB works.)
   Expected: the bash card's output is cut, a warning line names the truncation and an `artifact://<N>` id.
6. Prompt: `Read artifact://<N>:1-40 and tell me what the first table is.`
   Expected: a `• Read artifact://<N>:1-40` card with plain numbered lines (no `#TAG` — artifacts are immutable) and a correct answer.
7. Prompt: `Create notes/m2-scratch.txt containing the word hello.`
   Expected: `✎ Write: notes/m2-scratch.txt · 1 lines`; `git status` shows nothing (`notes/` is gitignored).

**Guided task:** Goal — fix lab issue #2 (the bug that spans two files) and account for every tool call. Hints — read `docs/ISSUES.md` first; ask for the smallest fix plus the relevant test; watch the Todo HUD if the model creates a plan; expand the `bash` test card before believing "tests pass". Checkpoints — (a) a `read` of `docs/ISSUES.md`; (b) at least one `grep` that finds the second file; (c) two `✎ Edit` cards; (d) a `$ python -m unittest …` card whose footer has no `Exit:`. Pass condition — both files appear in `git diff --stat`; `notes/m2.md` lists the tool sequence (tool name + one-line argument summary, in order); any truncated output was recovered via `read artifact://N` and the id is written in the notes.
**Stretch:** Goal — force a grep page boundary. Prompt for a pattern that matches in more than 20 files (e.g. `def ` across the whole repo) and ask omp to continue to the next page. Pass condition — the first inline card ends with `Use skip=<N> for the next page` and the second `🔍 Grep:` card's expanded args show `skip: <N>`.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `read` of a source file shows `…` and a `[…NNln elided…]` footer | Structural summary for files ≥ 100 lines | Ask for the ranges the footer suggests, or `read.summarize.enabled: false` |
| `read` returned only 300 lines | `read.defaultLimit` | Ask for `path:301-` or a specific range; raise the setting if you must |
| `Read artifact://N` says `Artifact N not found. Available: …` | Wrong session, or the id is from a subagent | Use one of the listed ids; artifact ids are per session |
| `No session - artifacts unavailable` | Running with `--no-session` | Drop `--no-session`; artifacts need a session directory |
| Grep says `Grep timed out after 30s` | Scope too wide | Narrow `path` or `glob` first |
| `No files found matching pattern` for a hidden or ignored file | `gitignore: true` default | Ask for `gitignore:false` explicitly (`hidden` is already `true`) |
| `web_search` returns `Error: …` and `provider: none` | No search provider available for the `web` role | Module 7/8 — set a provider key or `modelRoles.web` |

**Cheat sheet:**

| Item | Value |
|---|---|
| Read selectors | `:50`, `:50-100`, `:50+20`, `:5-16,40-80`, `:raw`, `:conflicts`, `:img` |
| Read caps | 300 lines open-ended (`read.defaultLimit`); +1/+3 context on ranges; dir depth 2 × 12 |
| Grep caps | 20 files/page (`skip`), 20/200 matches per file, 1/3 context, 30 s |
| Glob caps | `limit` ≤ 200, mtime-desc, 5 s |
| Bash footer | `⟦Wall \| Timeout \| Exit⟧`; default timeout 300 s |
| Spill threshold | `tools.artifactSpillThreshold` 50 KB; head/tail 20 KB; `tools.outputMaxColumns` 768 |
| Recover full output | `read artifact://N`, `read artifact://N:raw:1-3000`, `grep <re> artifact://N` |
| Predict a read without a model | `omp read <path>` (exact); `omp grep <pattern> [path]` (engine only) |

**Source:** omp://tools/read.md, omp://tools/grep.md, omp://tools/glob.md, omp://tools/edit.md, omp://tools/write.md, omp://tools/bash.md, omp://tools/todo.md, omp://tools/ask.md, omp://tools/web_search.md, omp://bash-tool-runtime.md, omp://blob-artifact-architecture.md, omp://settings.md, `omp read --help`, `omp grep --help`

---

## Lesson 2.3 — Why edits are reliable: hashline              (~10 min)
**You will be able to:** read a `[path#TAG]` header; explain why an edit was rejected as stale; recognise the "re-read, then edit" pattern in a transcript.
**Why this exists:** The classic agent failure is editing a file it last saw ten minutes ago: the search string no longer matches, or worse, it matches in the wrong place. omp's default `edit` mode, **hashline**, makes every edit carry proof of what the model saw. Each `read`, `grep`, successful `edit`, and `write` returns a four-hex **snapshot tag** computed from the whole normalized file. An `edit` must quote that tag and refer to line numbers from that snapshot. If the file changed underneath (you saved in your editor, a formatter ran, another tool wrote it), the tag no longer matches and the edit is refused — and the model re-reads instead of guessing. You never have to think about it, but you will *see* it in the transcript, and you should know that a refused edit is the system working.
**Demo:** [`demos/2.3-hashline.md`](demos/2.3-hashline.md) — the model-facing text of a read, the edit payload, the success receipt, then a stale-tag rejection after the learner edits the file by hand, and the automatic recovery.
**Concepts:**
- **Header**: `[api/users.py#1F2A]` then `12:def get_user(conn, user_id):`. The tag is four uppercase hex characters derived from the file's normalized content and recorded in the session **snapshot store** (256 paths × 4 versions, files ≤ 4 MiB). `grep` mints the same tags (`[PATH#TAG]` + `*12:` match rows), so the model can edit straight from a search hit.
- **Patch language** (you read it; the model writes it): one `[PATH#TAG]` section per file, then ops — `PUT 4.=4:` replace line 4 (`+TEXT` body rows are the final content), `PUT 10.=14:` replace a range, `PUT <1:` / `PUT >N:` insert before/after, `PUT >$:` append, `PUT N*:` replace the syntactic block starting at N (tree-sitter), `CUT N.=M` delete, `REM` delete file, `MV dest` rename. All numbers refer to the **original** snapshot, never to earlier hunks in the same call.
- **What gets rejected**: unknown/absent tag; lines the model has not been shown (`re-read elided or undisplayed ranges before editing them`); a stale tag when the snapshot chain can't prove a unique safe result; overlapping ops; a byte-identical no-op (three repeats trip the loop guard). A stale tag *can* be recovered silently when the store proves the edit still lands uniquely — you'll see a `Warnings:` block on the receipt.
- **Transcript signature of a stale edit**: `✘ Edit: <file>` (red) → `• Read <file>:<range>` → `✎ Edit: <file> ⟦+1/-1⟧`. That middle read is the point.
- **No tag, no edit**: `:raw` reads, `artifact://`, `skill://`, `agent://` and other immutable resources deliberately omit the header. If you want the model to edit a file, don't have it read it `:raw`.
- **Receipts**: a successful edit returns a fresh `[path#TAG]`, a short post-edit preview, and (in the card) a unified diff with `⟦+added/-removed⟧`. `write` also returns a fresh header so the next edit needs no re-read.
- **Mention only**: `edit.mode` selects the wire contract — `hashline` (default), `apply_patch`, `patch`, `replace`; `PI_EDIT_VARIANT` overrides per process. Leave it alone. `edit.blockAutoGenerated` (default `true`) refuses files that look generated — the lab's `generated/` directory will trip it, which is what Module 6 uses.

**Try it (Walkthrough):**
1. Outside omp: `omp read cli/log.py` and note the `[cli/log.py#TAG]` header.
   Expected: four hex characters after `#`.
2. Append a blank line to `cli/log.py` in your editor, save, and run `omp read cli/log.py` again.
   Expected: a different tag. (Same content → same tag; any change → new tag.)
3. Inside omp, prompt: `In cli/log.py, rename the logger variable's level constant to DEBUG_LEVEL. Small edit only.`
   Expected: `• Read cli/log.py` → `✎ Edit: cli/log.py ⟦+n/-n⟧`. Press `Ctrl+O` on the edit card: a unified diff.
4. Without leaving omp, edit `cli/log.py` in another terminal (change any unrelated line) and save. Then prompt: `Now also rename it in the docstring of the same file.`
   Expected (one of two): either a `✘ Edit` card followed by a fresh `• Read cli/log.py` and a successful `✎ Edit`, or a successful edit whose expanded receipt contains a `Warnings:` block mentioning recovery. Both are correct.
5. Prompt: `Read cli/log.py:raw and then change line 1.`
   Expected: the model re-reads without `:raw` before editing (a `:raw` read has no tag) — or explains it needs to.

**Guided task:** Goal — produce and explain one stale-tag event on purpose. Hints — the snapshot store is per session; `git checkout -- <file>` between two edits is the fastest way to change a file behind omp's back. Checkpoints — (a) you identified the tag in a `read` header; (b) you changed the file externally; (c) the next edit either re-read or warned. Pass condition — `notes/m2.md` contains the two tags (before/after) and one sentence on what the transcript showed between the refusal and the successful edit.
**Stretch:** Goal — observe a block edit. Ask omp to replace an entire function in `api/` "as one block". Pass condition — the expanded edit receipt shows a block-resolution line (the op was `PUT N*:`), and `git diff` shows only that function changed.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Model loops on the same edit three times | Byte-identical no-op → loop guard escalates | `Esc`, then tell it the exact current content or ask it to re-read |
| `Edit` refused: "outside recorded seen-line ranges" | The model read a summary, not the lines it wants to touch | Ask it to `read path:A-B` for that range first |
| `Edit` refused on `generated/…` | `edit.blockAutoGenerated: true` | Intended for the lab; in real projects, set `false` only if you mean it |
| Edits succeed but land at wrong lines | Someone set `edit.mode: replace` / `PI_EDIT_VARIANT` | `omp config get edit.mode`; reset to `hashline` |
| Format-on-save in your editor keeps changing tags | External writes invalidate snapshots | Expected; omp re-reads. Turn off format-on-save while pairing, or let omp run the formatter |

**Cheat sheet:**

| Item | Value |
|---|---|
| Header | `[path#TAG]` (4 hex), then `LINE:TEXT`; grep rows `*LINE:` |
| Who mints tags | `read` (not `:raw`), `grep`, successful `edit`, `write` |
| Ops | `PUT N.=M:` `PUT <N:` `PUT >N:` `PUT >$:` `PUT N*:` `CUT N.=M` `REM` `MV` |
| Store | 256 paths × 4 versions, ≤ 4 MiB per file |
| Mode | `edit.mode: hashline` (default; also `apply_patch`, `patch`, `replace`) |
| Generated guard | `edit.blockAutoGenerated: true` |

**Source:** omp://tools/edit.md, omp://tools/read.md, omp://tools/grep.md, omp://tools/write.md, omp://settings.md

---

## Lesson 2.4 — `bash` behaviors you'll notice              (~20 min)
**You will be able to:** run your own shell commands from the composer with `!`; explain why a long command "backgrounded itself"; start, inspect, and stop a named service through `proc://`; predict when a command gets a PTY; know what the bash interceptor does and that it is off by default.
**Why this exists:** `bash` is the tool that touches the world, so its quirks are the ones you'll trip over first: output caps, a persistent shell (so `cd` and `export` stick), an automatic background hand-off after 60 s, and a supervised **service** mode for dev servers. omp also exposes the same shell to *you* without a model turn (`!cmd`), which is the fastest way to check what it just did.
**Demo:** [`demos/2.4-bash-services.md`](demos/2.4-bash-services.md) — `!git status` from the composer; a test run that auto-backgrounds and delivers later; the lab API started as service `api` with a port-readiness check; `read proc://`, `read proc://api`, `write proc://api/kill`.
**Concepts:**
- **Two surfaces, one executor.** The model's `bash` tool and your `!cmd` both run through `executeBash()`. Only the tool path gets interception, approval, auto-background, and the boxed card renderer; your `!` commands render in a dedicated block that keeps the last 20 lines collapsed. `bash.enabled: false` removes the *model's* tool but not your `!`. (`$` runs Python locally the same way; Module 8.)
- **Persistent shell session.** Non-PTY tool calls reuse a native `Shell` keyed by session, so state persists across calls; the environment is hardened non-interactive (`PAGER=cat`, `GIT_EDITOR=true`, `TERM=dumb`, `NO_COLOR=1`, `CI=true`…). Concurrent calls never share one shell — extras run one-shot. A leading `cd <dir> && …` is rewritten into the structured `cwd` argument.
- **In-process coreutils.** The native shell bundles a uutils-style command set (`jq` is the vendored `jaq`; `PI_DISABLE_UUTILS_BUILTINS` falls back to system binaries) and resolves `scheme://` paths — `cat artifact://7 | wc -l` works, `realpath local://x` prints the backing file. External programs never see virtual paths.
- **Timeouts.** Default 300 s; `timeout: 0` disables; positive values clamp to 1–3600 and to `tools.maxTimeout` if set. A timeout returns a failed card with `details.timedOut`.
- **Auto-background** (`bash.autoBackground.enabled: true`, `thresholdMs: 60000`): a foreground command that outlives the window becomes a managed job. The card ends `Backgrounded as job <id>; result will be delivered automatically.` and the result arrives later as its own update. Explicit `async: true` does the same immediately (`async.enabled: true`, `async.maxJobs: 100`). `read proc://` lists jobs; `read proc://<id>` inspects without consuming delivery; `write proc://<id>/kill` cancels; the `wait` tool blocks until the next result (the model should keep working instead).
- **Named services** (`launch.enabled: true`): `bash` with `name` (≤ 48 chars, unique per project) and optional `ready: {port, log, host, timeout}` and `env`. Incompatible with `async`/`timeout`. Readiness waits on every condition (default 30 s). Reusing a live name restarts it. `read proc://<name>` → status + log tail; `grep <re> proc://<name>` searches logs; `write proc://<name>` sends stdin (Enter appended); `write proc://<name>/kill` stops; `write proc://<name>/mode` with `persist`/`session`/`detached`. Services live in a project-scoped launch broker, outside the session; from any terminal `omp ps` lists them and `omp ps logs <name> --follow`, `omp ps stop <name>`, `omp ps kill <name>`, `omp ps restart <name>` control them.
- **PTY** (`pty: true`): only in the interactive TUI with `PI_NO_PTY` unset (`--no-pty` sets it). Opens a `Console` overlay, forwards your keystrokes, real `TERM=xterm-256color`, inherits your environment (no hardening). `Esc` in the overlay kills the process. Asked for where unavailable, the call runs without a terminal and appends `pty requested but unavailable in this environment; ran without a terminal`.
- **Interceptor** (`bashInterceptor.enabled`, **default `false`** — enable it): regex rules that return `Blocked: <message>` instead of running, steering the model to a dedicated tool. Default rule set routes `cat|head|tail|less|more` → `read`, `grep|rg|ripgrep|ag|ack` → `grep`, `find|fd|locate` with name/type flags → `glob`, `sed -i`/`perl -i`/`awk -i inplace` → `edit`, `echo|printf|cat <<` with redirection → `write`. A rule fires only if its target tool is available; piped stdin stages (`… | grep x`) are never intercepted. It is routing, not security — `bash.patterns` (Module 4) is the allow/prompt/deny policy.
- **Cache note:** a `gh issue`/`gh pr` mutating command invalidates the `issue://`/`pr://` cache so later reads are fresh (Module 8).

**Try it (Walkthrough):**
1. In the composer type `!git status --short` and Enter.
   Expected: a shell block (not a tool card) with the output; no model turn, no token cost.
2. `!cd api && pwd` then `!pwd`.
   Expected: the first prints `…/omp-course-lab/api`; the second prints the same — the shell session persists.
3. Prompt: `Run the API as a service named api, ready on port 8080.`
   Expected: a `$ python -m api` card whose footer reads `⟦Service: api | State: ready | Ready: yes | PID: <n>⟧`.
4. Prompt: `read proc://` (yes, literally).
   Expected: `ⓘ Proc jobs & services 0 jobs · 1 services` with `└─ ⟦service⟧ api ⟦ready⟧ pid <n> · up <t> · persistent`.
5. Prompt: `read proc://api`.
   Expected: `ⓘ Proc api ready · pid <n> · up <t>` followed by the server's log lines (a `Serving …8080` line).
6. `!curl -s localhost:8080/users/1`.
   Expected: JSON for user 1 — the service is really up.
7. Prompt: `Stop the api service.`
   Expected: `⏹ Proc kill api exited · pid <n> · ran <t>`; a following `read proc://` shows `0 services`.
8. Prompt: `Run: python -c "import time; time.sleep(70); print('done')"`.
   Expected: after ~60 s the card ends `Backgrounded as job <id>; result will be delivered automatically.`; the `done` output arrives later as a separate delivery.
9. `omp config set bashInterceptor.enabled true`, restart omp, prompt: `Use cat to show api/__init__.py.`
   Expected: a failed `$ cat api/__init__.py` card with `Blocked: Use the \`read\` tool instead of cat/head/tail…`, then a `• Read api/__init__.py` card. Set it back to `false` (or leave it on — many people do).

**Guided task:** Goal — the outline's service exercise, end to end. Start the lab API as service `api` ready on port 8080, prove readiness, read its logs, hit it once, kill it. Hints — the `ready.port` check is what makes the card say `Ready: yes`; `read proc://api` is a read, not a bash call; killing is a `write` to `proc://api/kill`. Checkpoints — service card with `State: ready`; `ⓘ Proc api …` card; `⏹ Proc kill api`. Pass condition — the transcript contains a service card showing readiness, and `read proc://` after the kill no longer lists `api` (`0 services`); `omp ps` in another terminal agrees.
**Stretch:** Goal — see a PTY. Prompt: `Open python3 interactively with a PTY and wait for me.` Type `1+1`, Enter, then `Esc`. Pass condition — a `Console` overlay appeared, echoed `2`, and the card shows the session ended on `Esc` (exit code recorded as a kill). If you are on `--no-pty`, the card instead contains `pty requested but unavailable` — record that instead.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Service card says `State: failed — process exited before readiness` | Port already in use, or the app crashed | `!lsof -i :8080` / read the log tail in the card; `write proc://api/kill` any stale instance |
| Service card never becomes ready, times out at 30 s | Wrong port in `ready`, or app binds another host | Match `ready.port`/`host` to the app; `read proc://api` shows what it printed |
| `Async bash execution is disabled` | `async.enabled: false` | `omp config set async.enabled true` |
| `name` parameter "not available" | `launch.enabled: false` or non-launch-capable session (print/RPC) | Enable the setting; use the TUI |
| `pty requested but unavailable…` | `PI_NO_PTY=1` / `--no-pty`, or no UI (`-p`, RPC) | Run interactively without `--no-pty` |
| `Blocked: Use the read tool…` | Interceptor on (you enabled it) and the target tool exists | That's the point; the model should switch tools. Disable only if a rule misfires |
| `!` command shows only 20 lines | Collapsed preview of the bang block | `Ctrl+O` to expand; output above 50 KB spills to `artifact://` too |
| Command hung on a pager or editor | You used `pty: true` (no hardening) | Non-PTY runs set `PAGER=cat`, `GIT_EDITOR=true`; drop `pty` |

**Cheat sheet:**

| Item | Value |
|---|---|
| Your shell, no model | `!cmd` (`$` = local Python) |
| Timeout | default 300 s; `0` = none; clamp 1–3600; `tools.maxTimeout` ceiling |
| Auto-background | `bash.autoBackground.enabled` (on), `thresholdMs` 60000; `async.enabled` (on) |
| Jobs | `read proc://`, `read proc://<id>`, `write proc://<id>/kill`, `wait` |
| Services | `bash {name, ready:{port,log,host,timeout}, env}`; needs `launch.enabled` (on); `omp ps` |
| Service control | `read proc://<name>`, `grep <re> proc://<name>`, `write proc://<name>` (stdin), `…/kill`, `…/mode` |
| PTY | `pty: true`; TUI only; `PI_NO_PTY` / `--no-pty` disables; `Esc` kills |
| Interceptor | `bashInterceptor.enabled` **off by default**; `bashInterceptor.patterns` regex rules |
| Model tool off, `!` still on | `bash.enabled: false` |

**Source:** omp://tools/bash.md, omp://bash-tool-runtime.md, omp://tools/wait.md, omp://tools/write.md, omp://tools/read.md, omp://settings.md, `omp --help`, `omp config list`

---

## Lesson 2.5 — `ask` and `todo`              (~10 min)
**You will be able to:** answer an `ask` picker (single, multi, "Other", multi-question navigation); set `ask.timeout`/`ask.notify`; read the todo HUD and use `/todo expand|collapse`.
**Why this exists:** Two tools exist purely to keep *you* in the loop. `ask` turns "the model guessed" into "the model asked", with a keyboard picker instead of a free-text negotiation. `todo` makes a multi-step plan visible while it runs, so you can see the model drift before it finishes. Both are on by default and cost nothing to use; the only setting most people touch is `ask.timeout`, and only when running unattended.
**Demo:** [`demos/2.5-ask-todo.md`](demos/2.5-ask-todo.md) — a two-question `ask` (radio + checkbox), the answered card, then a `todo` init/start/done sequence with the HUD.
**Concepts:**
- **`ask`** is registered only when the session has a UI (never in `-p`/RPC). One call, one or more questions. Each option has a `label` and optional `description` (shown as `↳ …`). Single-select renders `○`/`◉`; `multi: true` renders `☐`/`☑`. The runtime appends its own controls — `Other (type your own)` opens a text editor; multi-select gets `Done selecting`; in a multi-question form ←/→ move between questions and prior answers are kept; the rich dialog also offers `Chat about this` (returns control to the composer without answering). `recommended` marks a default `(Recommended)`.
- **Timeout & notify.** `ask.timeout` (seconds, default `0` = wait forever) auto-selects the recommended (else first) option and marks the result `(auto-selected after timeout)`; it is always disabled in plan mode. `ask.notify` (`on` by default) sends a terminal notification `Waiting for input` — set `off` if your terminal bells annoy you. If `speech.enabled` is on, the question is also spoken.
- **Cancel** (`Esc` in the picker) aborts the tool *and the turn*: the transcript shows the call as cancelled and the model stops.
- **`todo`**: phases → tasks; statuses `pending` `in_progress` `completed` `abandoned` `blocked`. Exactly one task is `in_progress` (normalization auto-promotes the first pending one). The card is a tree (`☑ Todo N tasks`, `☐`/`☑` rows, `I. Phase  0/2`), and the same state is mirrored in the sticky HUD above the composer.
- **`/todo`**: `/todo expand` shows every phase/task in the HUD, `/todo collapse` restores the preview (both display-only). Manual edits through `/todo` are persisted as `user_todo_edit` entries and the model is told via a `<system-reminder>`. On `/resume`, completed/abandoned tasks are dropped from the live list. Subagents don't get `todo`; the parent owns the list. `todo.enabled: true`; `tasks.todoClearDelay` 60 s fades closed items in the HUD.

**Try it (Walkthrough):**
1. Prompt: `Before touching anything, ask me which of these you should do for issue #2: fix only the bug, fix and add a regression test, or fix and refactor the module. Use the ask tool with a recommended option.`
   Expected: a boxed `Ask 1 questions` card with three `○` rows and one `(Recommended)`; the composer is replaced by the picker.
2. Use ↑/↓ and Enter to pick the second option.
   Expected: the card becomes `✔ Ask …` with `◉` on your pick; the model continues with that choice.
3. Prompt: `Ask me two questions at once: which files I want touched (multi-select from the files in api/), and whether to run tests after (yes/no).`
   Expected: a two-group card; the first group toggles `☐/☑` rows, ←/→ moves between questions, `Done selecting` submits the multi group.
4. On any picker choose `Other (type your own)` and type a sentence.
   Expected: the result card shows your text as the answer.
5. Prompt: `Plan issue #2 as a todo list with two phases before you start.`
   Expected: a `☑ Todo` card and the HUD appear; the first task is marked in-progress. `/todo expand`, then `/todo collapse`.
6. Let the turn finish.
   Expected: tasks flip to `☑` in the HUD as the model calls `todo done`; closed items fade after ~60 s.

**Guided task:** Goal — make `ask` unattended-safe. Hints — `omp config set ask.timeout 20` and `ask.notify off`; ask a question with `recommended`; walk away. Checkpoints — the picker appears without a bell; after 20 s it resolves by itself. Pass condition — the answered card's text ends with `(auto-selected after timeout)` and `omp config get ask.timeout` prints `20`. Reset both settings afterwards.
**Stretch:** Goal — cancel an `ask` with `Esc` and observe that the turn stops, then resume with a normal prompt. Pass condition — the `Ask` card is marked cancelled/aborted and no further tool cards appear until your next prompt.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Model never uses `ask` even when you say "ask me" | Some models prefer prose questions; or `ask.enabled: false` | Say "use the ask tool"; check the setting |
| `Ask tool requires interactive mode` | Running `-p`/RPC | `ask` is TUI-only by design |
| Picker resolves instantly | `ask.timeout` set low from a previous experiment | `omp config reset ask.timeout` |
| Todo HUD stale / `Todo update failed…` | The model sent an invalid op (unknown task string) | It gets a reminder next turn; `/todo expand` to see the real state |
| Done tasks vanished after `/resume` | Resume strips completed/abandoned tasks | `/todo` shows historical state from the transcript |

**Cheat sheet:**

| Item | Value |
|---|---|
| Ask keys | ↑/↓ move, Enter pick, ←/→ question nav, `Esc` cancel turn |
| Reserved rows | `Other (type your own)`, `Done selecting`, `Chat about this` |
| Timeout | `ask.timeout` (s; `0` = none; ignored in plan mode) |
| Notify | `ask.notify: on\|off` |
| Todo ops | `init` `start` `done` `drop` `block` `unblock` `rm` `append` `view` |
| HUD | `/todo expand`, `/todo collapse`; `tasks.todoClearDelay` |

**Source:** omp://tools/ask.md, omp://tools/todo.md, omp://settings.md, `omp config list`

---

## Lesson 2.6 — Composer skills              (~10 min)
**You will be able to:** attach files/images to a prompt; search history; edit a long prompt in `$EDITOR`; queue and dequeue follow-ups while a turn runs; recover a cleared draft; retry a failed turn; repair a garbled display; turn on Vim mode.
**Why this exists:** You will spend more time in the composer than anywhere else in omp. Every chord below removes a restart: queueing a follow-up instead of waiting, recovering a draft you cleared by reflex, retrying a provider hiccup with one key. None of them are discoverable by accident.
**Demo:** [`demos/2.6-composer.md`](demos/2.6-composer.md) — `@`-mention, a queued follow-up delivered after the turn, `Ctrl+C` + `Up`, and Vim `ciw`.
**Concepts:**

| Chord (action ID) | What it does | Details |
|---|---|---|
| `@<path>` | Attach a file or image | Works on the command line (`omp @docs/spec.md "summarize"`) and in the composer, where `@` opens a fuzzy path autocomplete; the mention is inlined into the message as a `fileMention` entry. Images attach as `[Image #N]`. |
| `Ctrl+V` (`app.clipboard.pasteImage`) | Paste from clipboard, image preferred, text fallback | Linux `Ctrl+V`; macOS also `Cmd+V`; Windows also `Alt+V` (Windows Terminal may eat `Ctrl+V`). Large text pastes collapse to `[Paste #N, +M lines]`; `Ctrl+Shift+V`/`Alt+Shift+V` (`app.clipboard.pasteTextRaw`) pastes without collapsing. |
| `Ctrl+R` (`app.history.search`) | Search prompt history | Persistent across sessions. |
| `Ctrl+G` (`app.editor.external`) | Edit the draft in `$VISUAL`/`$EDITOR` | Save and quit to return. |
| `Ctrl+Q`, `Ctrl+Enter` (`app.message.followUp`) | Queue a follow-up while a turn runs | Delivered after the current turn (`followUpMode: one-at-a-time` by default; `all` sends every queued message together). Both chords are bound because Windows Terminal swallows `Ctrl+Enter`. A queued message can also nudge a still-running command into the background early. |
| `Alt+Up`, `Shift+Up` (`app.message.dequeue`) | Pull the queued message back into the editor | Edit or discard it. |
| `Ctrl+C` then `Up` | Recall a cleared draft | `composer.recallClearedDrafts: true` by default; 100-entry in-memory history; not in `Ctrl+R`; lost on exit. Double `Ctrl+C` still exits. |
| `Alt+R` (`app.retry`) | Retry the last failed assistant turn | Use after a provider error; Module 3 covers `/fresh` for a wedged stream. |
| `Alt+L` (`app.display.reset`) | Reset the terminal display | Garbled rendering after a resize or a stray control sequence. |
| `Alt+Shift+L` / `Alt+Shift+C` | Copy current line / whole prompt | Clipboard helpers. |
| `Shift+Tab` (`app.thinking.cycle`) | Cycle thinking level | Module 3. |

- **Vim mode** — `tui.vimMode` is **off by default**; enable with `omp config set tui.vimMode true` or `/settings` → Interaction → Input → *Vim Editing Mode*. Starts in Insert; `Esc` → Normal (border colour changes; `tui.vimModeDisplay: text|icon|none` shows the mode). Motions `h j k l w b e 0 ^ $ gg G`, counts, operators `d y c` with motions and text objects (`iw aw i" a( ip …`), `x D C dd yy cc p P u`, Visual `v`/`V`. `Ctrl` chords, `Enter`, and `Tab` keep their app meaning in every mode, so `Enter` still submits from Normal. `Esc` only reaches the app interrupt when Vim has nothing pending — in Insert it just switches modes, so stopping a turn from Insert is `Esc` `Esc`.

**Try it (Walkthrough):**
1. Type `@` and a few letters of `ISSUES`.
   Expected: an autocomplete list of matching paths; Enter inserts `@docs/ISSUES.md`.
2. Finish the prompt `— summarize issue #2 in two lines` and send.
   Expected: the file content is inlined for the model (no `read` card needed); the answer references #2.
3. Start a longer prompt (`Summarize every function in api/`), and while it streams type `Now do the same for cli/` and press `Ctrl+Q`.
   Expected: a queued-message indicator; after the first turn ends, the second prompt is sent automatically.
4. Queue another follow-up, then press `Alt+Up`.
   Expected: the text returns to the editor; nothing was sent.
5. Type a sentence, press `Ctrl+C` once, then `Up`.
   Expected: the sentence is back, editable, unsent.
6. Press `Ctrl+G`.
   Expected: your `$EDITOR` opens with the draft; save/quit returns it to the composer.
7. `omp config set tui.vimMode true`, restart, type `fix the users endpoint`, press `Esc`, move to `users` with `b`/`w`, type `ciw` `orders` `Esc`, then `Enter`.
   Expected: border colour changed on `Esc`; the word was replaced; `Enter` submitted from Normal mode.

**Guided task:** Goal — drive one whole turn without touching the mouse or restarting. Hints — combine `@`, `Ctrl+Q`, `Alt+Up`, `Ctrl+R`. Checkpoints — a follow-up delivered after the turn; a dequeued message edited and re-sent; a previous prompt recalled with `Ctrl+R`. Pass condition — the transcript shows two consecutive user messages where the second was queued (sent with no idle gap), and `notes/m2.md` names the three chords you used.
**Stretch:** Goal — Vim mode. With `tui.vimMode: true`, compose a three-line prompt, use `V` + `d` to delete a line and `u` to undo it, then `ciw` on one word. Pass condition — `omp config get tui.vimMode` prints `true` and the submitted prompt contains the `ciw` replacement.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `Ctrl+V` pastes nothing (Windows Terminal) | Terminal handles paste first | `Alt+V`; or paste a single image-file path |
| `Ctrl+Enter` does nothing | Windows Terminal swallows it | `Ctrl+Q` (same action) |
| `Ctrl+Q` does something else | Your `keybindings.yml` already binds `Ctrl+Q` | Remap `app.message.followUp` explicitly |
| Draft not recalled after `Ctrl+C` | `composer.recallClearedDrafts: false`, or you exited omp | Re-enable; recall history is in-memory only |
| `Up` in Vim Normal mode moves the cursor, not history | By design (`k`) | Switch to Insert for history, or use `Ctrl+R` |
| `Esc` doesn't stop the turn in Vim mode | Insert → Normal consumed it | Press `Esc` again |
| Screen garbage after resize | Renderer/terminal desync | `Alt+L` |

**Cheat sheet:**

| Item | Value |
|---|---|
| Attach | `@path` (autocomplete), `omp @file "prompt"`, `Ctrl+V` image |
| History | `Ctrl+R`; drafts `Ctrl+C` → `Up` |
| External editor | `Ctrl+G` |
| Queue / dequeue | `Ctrl+Q` or `Ctrl+Enter` / `Alt+Up` or `Shift+Up`; `followUpMode` |
| Retry / redraw | `Alt+R` / `Alt+L` |
| Raw paste | `Ctrl+Shift+V` / `Alt+Shift+V` |
| Vim | `tui.vimMode: true` (off by default); `tui.vimModeDisplay` |

**Source:** omp://keybindings.md, omp://cli-reference.md, omp://settings.md, omp://session.md, omp://fs-scan-cache-architecture.md, omp://bash-tool-runtime.md, `omp config list`

---

## Where this module leaves you

You can now look at any turn and answer: which tools ran, in what order, with what arguments, what they returned, what was cut off, and whether an edit was proven against a fresh snapshot. Module 3 uses exactly that skill to compare a vague prompt with a structured one; Module 8 extends `read`/`bash` with the rest of the toolbox.

Further reading (not sources): none required. Everything above is in `omp://` — `read omp://tools/bash.md` inside omp is a fine way to practise reading a long card.
