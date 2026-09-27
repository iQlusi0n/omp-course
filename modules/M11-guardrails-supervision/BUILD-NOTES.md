# Module 11 — Build notes

Built against `omp/18.3.1` (`/home/user/.local/bin/omp`). Build machine: Python 3 only, no model
credentials usable for live sessions, no recordings. All TUI demos are reconstructions labelled as
such; the CLI portions of `demos/11.1-ttsr-interrupt.md` are captured verbatim.

**Wave 2 audit (2026-09-27):** the binary on PATH reported `omp/18.3.5` at audit time; the course-wide
header still says 18.3.1 (orchestrator's call). Every `omp ttsr` capture and `omp config get` default in
this module was re-run on that binary against the real `omp-course-lab` tree.

## Sources read this session

`omp://` index, `omp://rulebook-matching-pipeline.md`, `omp://ttsr-injection-lifecycle.md`,
`omp://advisor-watchdog.md`, `omp://prewalk.md`, `omp://compaction.md`, `omp://tools/context-notes.md`,
`omp://tools/new-context.md`, `omp://settings.md` (models/advisor/extended-context sections),
`omp://cli-reference.md` (prewalk/advisor flags), `omp://task-agent-discovery.md`, `omp://tools/todo.md`,
`omp://extensions.md`, `omp://hooks.md`, `omp://agent-hub.md`, `omp://session.md`,
`omp://blob-artifact-architecture.md`, `omp://handoff-generation-pipeline.md`, `omp://tools/checkpoint.md`,
`omp://tools/rewind.md`, `omp://models.md`; `omp --help`, `omp ttsr --help`, `omp config list`,
`omp config get <key>` for every default quoted. UI notice strings (`Injecting rule:`, `Prewalk: …`,
`Advisor enabled.`, `Usage: /advisor …`, `Usage: /prewalk [restart]`, `Usage: /extended-context …`,
`Usage: /omfg <complaint>`, `<advisory … guidance="weigh, don't blindly obey">`, the `context_notes`
result/error strings, `── 📷 compacted · ctrl+o ──`) were extracted from the binary.

## Deviations from the outline (doc wins)

1. **Outline 11.1: "amber 'Injecting rule' card".** The card text `Injecting rule: <name>` is verified;
   the *colour* is not documented anywhere. Lessons say "`Injecting rule: <name>` card" without a colour.
2. **Outline 11.1: "survives compaction".** Docs say the fired-rule *suppression state* is persisted
   (`ttsr_injection` entries, restored on resume); the rule file is re-read at session start. Worded
   that way rather than as a property of the rule itself.
3. **Outline 11.3 coursework: "`/prewalk` status shows fired".** `/prewalk` has no `status` subcommand
   (`Usage: /prewalk [restart]` verified). Pass condition rewritten to the `Prewalk: switched to …
   after first edit call.` notice and the model-chip change.
4. **Outline 11.2: "per-subagent `advisor:` in frontmatter".** Covered, plus the `task.agentAdvisor`
   override documented in `task-agent-discovery.md` (not in the outline).
5. **Outline 11.5: notes-backed tools and restart.** `settings.md`/tool docs say toggling adds the tools
   to the running session; `compaction.md` says restart to refresh the roster. Lesson says both and
   tells the learner to `/restart` if `/tools` lacks them.
6. **Outline 11.1 coursework W: `condition: "console\\.log"` only.** Solution rule adds
   `scope: "text, tool:edit(web/*.js), tool:write(web/*.js)"` so the walkthrough's negative test
   (`--path api/server.py`) demonstrates scope; the `condition` and `interruptMode: always` are as specified.

## Claims dropped as unverifiable

- Colour of any TUI card (amber/red) — not documented.
- Exact rendering of the advisor status table and the `/extended-context status` value — not documented;
  demos mark those lines illustrative (`Extended context enabled.`/`disabled.` and `Usage:` are verbatim).

## Removed (unverifiable)

Wave 2 audit. Each item was in the module and is now gone or rewritten:

- **`omp ttsr test` exit codes (0 triggered / 1 not) and `echo exit=$?` steps.** On the audit binary a
  no-trigger `test` exits 0 when project rules are loaded and 1 only in isolated `-r` mode; `scan` exits
  0 either way. Lesson, cheat sheet, 11-W1 and demo now say "grep the output, not `$?`".
- **`ctrl+o` on the `Injecting rule` card shows the rule body.** `Ctrl+O` is documented as "toggle
  tool-output expansion" (`keybindings.md`); nothing documents it acting on the TTSR notification card.
- **`read history://current` to find the `ttsr_injection` entry.** `tools/read.md`: bare
  `history://current` names an ordinary agent called `current`. Replaced by grepping the session
  journal (`~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<sessionId>.jsonl`, `session.md`) or `/export`.
- **`omp config set modelRoles.advisor …` / `omp config get modelRoles.advisor` / `omp config set
  modelRoles.smol …`.** `modelRoles` is a record; `omp config get modelRoles.advisor` prints
  `Unknown setting`. Replaced by the `/model` Roles view or `modelRoles:` in `config.yml` (Module 7 convention).
- **`Warning: prewalk disabled …` "on stderr".** The string is verified; the stream is not.
- **"`/advisor status` in the parent shows no active advisor" (11-S3).** Not documented; pass now keys on
  the artifact files (`<SubId>/__advisor.jsonl` present, no top-level `__advisor.jsonl`).
- **"Builtin TS/Go/Rust rules fire in a Python repo".** All 27 builtins are scoped to `*.go`/`*.rs`/`*.ts(x)`
  edits (`omp ttsr list`); row rewritten as "clutter list/scan output".
- **Byte-limit error text** `Context notes are N UTF-8 bytes. Shorten …` — corrected to the binary's
  `Context notes are N bytes; the limit is 16384 UTF-8 bytes. Shorten the notebook and use history://current/full to recover raw detail.`

## Lab alignment (Wave 2)

- Issue #8 is `POST /signup` (`api/server.py::_signup`): 500 on duplicate email, 201 on `not-an-email`;
  the temptation is a catch-all `except Exception` → 400, which the gated test rejects (it patches
  `create_user` to raise and expects 500). All references to `api/orders.py` / "except: pass" /
  "malformed rows" were rewritten; `solutions/WATCHDOG.md` and `WATCHDOG.yml` now describe that contract.
- Paths: `web/signup.js` → `web/app.js` (no `console.log` seeded); `cli/main.py` → `cli/__main__.py`;
  the only seeded `print()` calls are in `cli/commands.py`; `cli/log.py` provides the `logger` replacement.
- The CLI has `users`, `orders`, `health` — there is no `orders list`; the prewalk task now targets the
  `orders` subcommand. Test suite on `main`: `Ran 48 tests … OK (skipped=20)`.
- Rule counts in expected output: 27 builtins + project rules (`evaluated 28` with one rule installed,
  `evaluated 30` with all three; `scan` reports `rules=29` because the `question:` rule is skipped;
  from inside `cli/` both path-scoped rules drop out → `rules=27`).

## Observed on the live binary (not in docs)

- `omp ttsr test` exit code is **not** a trigger signal: 0 on trigger; on no-trigger it is 0 with project
  rules loaded and 1 only in `-r` isolated mode. `omp ttsr scan` exits 0 either way; `scan -r <question rule>`
  alone prints `Rule registered but produced no TTSR entry.` and exits 1.
- `omp ttsr scan` header reports `rules=29` when `list` reports 30 — question rules are skipped
  (consistent with `ttsr-injection-lifecycle.md` §10).
- Scope path globs are resolved relative to the `test`/`scan` root: running `scan` from inside `cli/`
  yields `no-relevant-rules` for a `tool:edit(cli/*.py)` rule. Lesson and 11-W2 step 4 teach this.
- `omp config list` on this machine shows 27 `builtin-defaults` TTSR rules (Go/Rust/TS only).

## Features covered vs Appendix C

| Row | Status |
|---|---|
| TTSR rules, `/omfg`, `omp ttsr` | covered (11.1) |
| Advisor/watchdog (default off) | covered (11.2); `advisor.enabled` default `false` called out |
| Prewalk (default off) | covered (11.3); `prewalk.enabled` default `false` called out |
| Notes-backed context, `/extended-context` (off, experimental) | covered (11.5); both defaults `false` called out |
| `checkpoint`/`rewind` (also in M9) | referenced in 11.5 decision table with `checkpoint.enabled` default `false` |
| Extension `tool_call` block (M12 row) | previewed in 11.4 only; build is M12 |

## Not exercised on this machine

- No live model session: TTSR interrupt, advisor notes, prewalk hand-off, and `new_context` rollover
  were not observed end-to-end here. Walkthroughs are written from the documented lifecycle and the
  verbatim notice strings; Appendix D step 4 (run every walkthrough in `--profile course-build`) must be
  done by the orchestrator/instructor on a machine with credentials.
- Lab fixtures were read during the Wave 2 audit (`web/app.js`, `cli/__main__.py`, `cli/commands.py`,
  `api/server.py`, `docs/ISSUES.md` #8, `tests/test_issues.py`); every path, prompt and expected output
  in the module now matches the seeded tree.
