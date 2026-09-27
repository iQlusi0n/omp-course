# Module 3 — Build notes

Built 2026-09-25 against `omp/18.3.1` (`omp --version`). All facts verified against `omp://` docs, `omp --help`, `omp config --help`, `omp config get/list` on the build machine.

## Verified on the live binary
- Defaults via `omp config get`: `magicKeywords.enabled=true`, `magicKeywords.ultrathink=true`, `defaultThinkingLevel=high`, `steeringMode=one-at-a-time`, `followUpMode=one-at-a-time`, `interruptMode=immediate`, `doubleEscapeAction=rewind`, `hideThinkingBlock=false`.
- `omp config list` shows the per-keyword key is `magicKeywords.workflow` (not `workflowz`) — matches omp://magic-keywords.md; the lesson says so explicitly.
- `statusLine.compactThinkingLevel` (default `true`, "Show the thinking level as a single icon on the model name instead of a separate ` · <level>` suffix") is **not in omp://settings.md**; verified only via `omp config get statusLine.compactThinkingLevel --json`. Cited as such in Lesson 3.3.
- `doubleEscapeAction` enum on the binary is `rewind|tree|none`; omp://settings.md lists only `rewind, none`. Lessons mention `rewind` (default) and `none` only.
- `omp -p --no-session --thinking off "Reply with exactly: OK"` returned `OK` — a model is reachable, but the lab repo (`omp-course-lab/`) did not exist on disk during this build (built in parallel), so no walkthrough was run end-to-end against the fixture. Demos are therefore representative fenced transcripts, labelled as such. **Audit 2026-09-27:** the lab now exists and the fixture commands were run from its root on `main`: `python3 -m cli orders --month 2026-03 --format csv` → `error: unrecognized arguments: --format csv`, exit 2; `LAB_ISSUE=3 python3 -m unittest tests.test_issues` → `FAILED (failures=1, skipped=18)`; `python3 -m unittest discover -s tests` → `Ran 48 tests … OK (skipped=20)`. Demo transcripts were aligned to these strings.
- TUI smoke: launched `omp --no-session` in a PTY; the composer, status line (model, cwd, branch, context %) rendered. Sending the raw `ESC [ Z` byte sequence through the PTY was delivered as literal text rather than as `Shift+Tab` (the PTY harness does not speak the terminal keyboard protocol), so the `Shift+Tab` cycle and border-color change were **not observed** here; they are stated from omp://keybindings.md (`app.thinking.cycle`) and omp://theme.md (thinking border tokens). Flagged in the lesson's troubleshooting table (kbd protocol).

## Deviations from the outline
- Outline 3.4 lists `/btw` keys as "`f`/`c`/`b`". Doc (omp://slash-command-internals.md §11) confirms `c` copy, `f` follow-up, `b` branch-promotion (single-turn only, idle + unchanged leaf), plus `Esc` cancel/close, and history keys `Up`/`Down`/`Tab`/`Enter`/`Left`/`Right`. Doc also states "There is no … separate `x` cancellation key" — the lesson does not mention `x`.
- Outline says `ultrathink` "standalone lowercase prose only" — confirmed; lesson adds the doc's caveat that on a fixed thinking level `ultrathink` adds only the notice and changes effort only under `auto`.
- Outline 3.3 says "`Ctrl+T` to see it": `Ctrl+T` toggles thinking-*block* visibility; the *level* is read from the status line icon / border color, not from `Ctrl+T`. Lesson separates the two.
- Outline 3.4 says "`/fresh` when the provider stream wedges" — confirmed (omp://session-operations-export-share-fork-resume.md, Fresh). Added the doc's constraint that `/fresh` is rejected while streaming and the note that `/clear`/`/new`/`/delete` are Module 5.
- Coursework G "queue a follow-up with Ctrl+Q while streaming": `Ctrl+Q` and `Ctrl+Enter` both bind `app.message.followUp`; lesson lists both and the Windows Terminal caveat.

## Claims dropped as unverifiable
- Any specific cycle *order* for `Shift+Tab` (e.g. high → xhigh → max → auto …). No doc states the order or that it depends on the model; the demo shows the icon changing and tells learners to read the level rather than count presses.
- "omp resolves to the nearest level the model offers." Replaced with the documented transport behavior from omp://settings.md (`providers.autoThinkingMaxEffort` row): a model that requires explicit effort receives its lowest supported effort.
- "`Shift+Tab` levels wrap around" — not documented; removed.
- An `ask` card "lets you add a note": the rich ask dialog supports notes, the selector fallback does not (omp://tools/ask.md). Lesson now says "option picker plus `Other (type your own)`" only.
- Exact rendering of queued-message indicators, the pause screen, the `/fresh` notice text, and `/btw` panel chrome: drawn schematically in demos with a disclaimer; wording is not asserted.
- The `read` of `docs/ISSUES.md` from an `@` mention: doc says the mention inlines the file as a `fileMention` entry, so the lesson no longer predicts a `read` card for it.
- Lab issue #3 specifics (title, files, header, gated test command) originally came from the lab builder's message during the parallel build. **Audit 2026-09-27:** confirmed against the checked-in `omp-course-lab/docs/ISSUES.md` #3 and `tests/test_issues.py::Issue3CsvExport`; the full title *(export for spreadsheets)*, the `--format {table,csv}` (default `table`) contract, integer `total_cents`, and "no summary line" (the test expects exactly 13 rows) were added to the README prompt, exercises, demos, and instructor notes.

## Feature-matrix rows covered (Appendix C)
- "Thinking level, `ultrathink`, magic-keyword toggles" (3, default on) — Lesson 3.3, cheatsheet, coursework S.
- "`/pause`, `/btw`, `/fresh`" (3) — Lesson 3.4, demos 3.4b/3.4c, coursework G2.
- Also touched (owned by other modules): `Esc`/`Ctrl+O`/`Ctrl+Shift+O`/`Ctrl+T` (2), `Ctrl+Q` queue/dequeue and draft recall (2), `ask` (2), `artifact://` (2), `!cmd` (2), `/hotkeys` (2).

## Not covered here by design
- `orchestrate`, `workflowz`, `jevify` semantics — named as existing, deferred to Module 10.
- `/review`, `/annotate`, approval modes, plan mode — Module 4.
- `/clear`, `/new`, `/delete`, compaction — Module 5.

## Audit 2026-09-27 (wave 2)

Binary on PATH at audit time reported `omp/18.3.5` (module was built against `18.3.1`). Every command, flag, keybinding, setting key, path, and default in this module was re-read in `omp://` docs or `omp --help` / `omp config --help` / `omp config get`; live defaults unchanged (`defaultThinkingLevel=high`, `magicKeywords.*=true`, `interruptMode=immediate`, `steeringMode`/`followUpMode=one-at-a-time`, `doubleEscapeAction=rewind`, `hideThinkingBlock=false`, `statusLine.compactThinkingLevel=true`, `ask.timeout=0`, `ask.notify=on`, `providers.autoThinkingMaxEffort=xhigh`, `composer.recallClearedDrafts=true`).

### Fixed
- Lesson 3.3 / cheatsheet: "`hideThinkingBlock: false` hides the text" → `hideThinkingBlock: true` (default is `false`; omp://settings.md).
- Lesson 3.5 / cheatsheet: `!cmd` cross-checks "cost no model tokens" → they run without a model turn, but the run is persisted as a `bashExecution` message and is conversation input on the next prompt (omp://session.md message roles; omp://compaction.md treats `bashExecution` as a user-turn boundary).
- Cheatsheet: the `[raw output: artifact://<id>]` footer is the shell-minimizer footer; plain truncation carries an artifact id in its truncation note (omp://tools/bash.md). Row now names both forms.
- Demos 3.1/3.2/3.5: unittest result strings aligned to the real fixture (`FAILED (failures=1, skipped=18)`, `OK (skipped=18)`, `OK (skipped=20)`), `--format` does not exist on `main` (the edit adds it, not a choice), real test name `test_orders_month_table (test_cli.CliTests.test_orders_month_table)`.
- Demo 3.4b: `cmd_orders()` returns an int exit code and is called from `main()` in `cli/__main__.py` (was "returns None … called from the `orders` handler").
- Lesson 3.3 troubleshooting: "`ultrathink` glued to punctuation" listed as a non-trigger → omp://magic-keywords.md says sentence punctuation and quotes *may* touch the keyword; only letters, digits, `_`, `/`, `\`, `-`, file extensions, symbol references, and call syntax break the match. Row corrected.

### Removed (unverifiable)
- Lesson 3.1 troubleshooting: "`@` token must be preceded by a space or line start" as a cause for a literal `@docs/ISSUES.md` — no omp:// doc states the composer's mention-tokenization rule (omp://session.md only documents the resulting `fileMention` role). Row now cites only path resolution. Same phrase ("token glued to punctuation") dropped from instructor notes.
- Lesson 3.1 troubleshooting: "check the card's `cwd` line" — no doc states that the bash card renders a `cwd` line (omp://tools/bash.md documents `cwd` as a tool parameter only).
