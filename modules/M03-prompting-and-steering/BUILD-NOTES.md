# Module 3 — Build notes

Built 2026-09-25 against `omp/18.3.1` (`omp --version`). All facts verified against `omp://` docs, `omp --help`, `omp config --help`, `omp config get/list` on the build machine.

## Verified on the live binary
- Defaults via `omp config get`: `magicKeywords.enabled=true`, `magicKeywords.ultrathink=true`, `defaultThinkingLevel=high`, `steeringMode=one-at-a-time`, `followUpMode=one-at-a-time`, `interruptMode=immediate`, `doubleEscapeAction=rewind`, `hideThinkingBlock=false`.
- `omp config list` shows the per-keyword key is `magicKeywords.workflow` (not `workflowz`) — matches omp://magic-keywords.md; the lesson says so explicitly.
- `statusLine.compactThinkingLevel` (default `true`, "Show the thinking level as a single icon on the model name instead of a separate ` · <level>` suffix") is **not in omp://settings.md**; verified only via `omp config get statusLine.compactThinkingLevel --json`. Cited as such in Lesson 3.3.
- `doubleEscapeAction` enum on the binary is `rewind|tree|none`; omp://settings.md lists only `rewind, none`. Lessons mention `rewind` (default) and `none` only.
- `omp -p --no-session --thinking off "Reply with exactly: OK"` returned `OK` — a model is reachable, but the lab repo (`omp-course-lab/`) did not exist on disk during this build (built in parallel), so no walkthrough was run end-to-end against the fixture. Demos are therefore representative fenced transcripts, labelled as such.
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
- Lab issue #3 specifics (title, files, header, gated test command) come from the lab builder's message during the parallel build, not from a checked-in `docs/ISSUES.md`; instructor notes tell the teacher to confirm against the lab before class.

## Feature-matrix rows covered (Appendix C)
- "Thinking level, `ultrathink`, magic-keyword toggles" (3, default on) — Lesson 3.3, cheatsheet, coursework S.
- "`/pause`, `/btw`, `/fresh`" (3) — Lesson 3.4, demos 3.4b/3.4c, coursework G2.
- Also touched (owned by other modules): `Esc`/`Ctrl+O`/`Ctrl+Shift+O`/`Ctrl+T` (2), `Ctrl+Q` queue/dequeue and draft recall (2), `ask` (2), `artifact://` (2), `!cmd` (2), `/hotkeys` (2).

## Not covered here by design
- `orchestrate`, `workflowz`, `jevify` semantics — named as existing, deferred to Module 10.
- `/review`, `/annotate`, approval modes, plan mode — Module 4.
- `/clear`, `/new`, `/delete`, compaction — Module 5.
