# Module 11 — Coursework

Built against `omp/18.3.1`. Work in `omp-course-lab` from `git checkout module-11-start`.
Every exercise ends with an observable pass condition. Tiers: **W** walkthrough (exact keys),
**G** guided (goal + hints + checkpoints), **S** stretch (goal + pass only; notes in `solutions/README.md`).

Prerequisites per exercise are listed; the CLI-only exercises (11-W1, 11-W2) need no model.

| # | Tier | Lesson | Time | Needs |
|---|---|---|---|---|
| 11-W1 | W | 11.1 | 10 min | `omp` only |
| 11-W2 | W | 11.1 | 10 min | `omp` only |
| 11-W3 | W | 11.1 | 10 min | a chat model |
| 11-G1 | G | 11.2 | 20 min | a second model for `modelRoles.advisor` |
| 11-G2 | G | 11.2 | 15 min | same |
| 11-G3 | G | 11.3 | 15 min | `modelRoles.smol` ≠ `modelRoles.default` |
| 11-G4 | G | 11.1 | 10 min | a chat model |
| 11-S1 | S | 11.5 | 25 min | a chat model |
| 11-S2 | S | 11.1 | 15 min | a judge model (`ttsr.judge: on`) |
| 11-S3 | S | 11.2 + 10 | 20 min | custom agent from Module 10 |
| 11-S4 | S | 11.4 | 10 min | none (paper) |

---

## 11-W1 — Test a TTSR rule without a model (W, 11.1)

1. Create `.omp/rules/no-console-log.md` in the lab repo with the exact contents of
   `modules/M11-guardrails-supervision/solutions/no-console-log.md`.
   **Expected:** `omp ttsr list | grep -A1 no-console-log` prints the rule as `[native]` with
   `condition: console\.log` and `scope: text, tool:edit(web/*.js), tool:write(web/*.js)`.
2. From the repo root:
   `omp ttsr test --source tool --tool edit --path web/app.js 'console.log("x")'`
   **Expected:** `Triggered (1)` … `✓ no-console-log  condition: /console\.log/ [native]`.
3. `omp ttsr test --source tool --tool edit --path api/server.py 'console.log("x")'`
   **Expected:** `No rules triggered. (evaluated 28)` (scope glob excluded the path; 28 = your rule + 27 builtins). Do not grade on exit codes — see the cheat sheet.
4. `omp ttsr test --source thinking 'maybe console.log here'`
   **Expected:** not triggered — `thinking` is outside the rule's `scope`.
5. `omp ttsr test --json --source text 'console.log(1)'`
   **Expected:** JSON with `"triggered":[{"name":"no-console-log", … "matched":{"regex":["console\\.log"] …`.

**Pass:** steps 2–5 produce exactly the trigger/no-trigger outcomes above.

## 11-W2 — Scan the repo for existing violations (W, 11.1)

1. Add `.omp/rules/no-bare-print.md` from `solutions/no-bare-print.md` (an `astCondition` rule scoped to `cli/*.py`).
2. From the repo root: `omp ttsr scan -v cli/`
   **Expected:** header `TTSR scan — directory=…/cli files=5 scanned=5 rules=29 …`, then
   `Found violations/matches: (1 matches across 1 files)` and
   `cli/commands.py` / `✓ no-bare-print  astCondition: print($$$ARGS) [native]` (the only seeded
   `print()` sites are in `cli/commands.py`; `cli/__main__.py` uses `sys.stderr.write`).
3. `omp ttsr scan -v web/`
   **Expected:** `No rule matches found. (evaluated 29 rules on 1/2 files)` — the seeded `web/app.js`
   contains no `console.log`; `index.html` is skipped as `no-relevant-rules=1`.
4. `cd cli && omp ttsr scan -v .`
   **Expected:** `scanned=0 rules=27` and `no-relevant-rules=5`, no matches — the `cli/*.py` scope
   glob no longer matches the paths as seen from inside `cli/`, so both project rules drop out.
   This is why you scan from the repo root.

**Pass:** step 2 lists `cli/commands.py`; step 4 lists no matches.

## 11-W3 — Watch a rule abort a live edit (W, 11.1)

Prereq: 11-W1 done; a chat model logged in.

1. `omp` in the lab repo. Prompt:
   *"In web/app.js, log the form payload to the console right before the fetch so I can debug submissions."*
   **Expected:** the streaming edit is cut off; an `Injecting rule: no-console-log` card appears.
   The retried edit adds a `DEBUG`-guarded `debug()` helper.
2. `!grep -n "console.log" web/app.js`
   **Expected:** no output — the seeded file has no `console.log` and the rule kept it that way.
3. Ask for the same change again.
   **Expected:** no card (`ttsr.repeatMode: once`).
4. `!grep -l ttsr_injection ~/.omp/agent/sessions/*/*.jsonl` (the session journal), or `/export`
   and search the HTML (it embeds the session entries). `read history://current` is **not** the
   session — that URL names an agent called `current`.
   **Expected:** the journal holds one hidden `custom_message` with `customType: "ttsr-injection"`
   and a `ttsr_injection` entry listing `no-console-log`.

**Pass:** the card in step 1 and the `ttsr_injection` entry in step 4.

## 11-G1 — Advisor with WATCHDOG.md on issue #8 (G, 11.2)

*Goal:* a second model catches the catch-all-exception temptation in issue #8 (`POST /signup`) before you do.

*Hints:*
- Assign the `advisor` role in `/model` (Roles view) or under `modelRoles:` in `~/.omp/agent/config.yml`
  (`modelRoles` is a record; `omp config set modelRoles.advisor` is not a key); leave `advisor.enabled` alone and use `/advisor on`.
- Put `solutions/WATCHDOG.md` at `<repo>/WATCHDOG.md` ("watch for catch-all exception handling").
- Prompt for the #8 fix with *"keep the change minimal"* — that phrasing tempts wrapping `_signup` in
  `except Exception:` → 400, which also hides genuine crashes. `docs/ISSUES.md` #8 wants: missing field
  or no `@` → 400, `sqlite3.IntegrityError` → 409, anything else still 500.
- If nothing lands, `/advisor dump` and read what the advisor actually said; a `nit` is delivered as a
  quiet aside at the next step boundary, not as an interrupt.

*Checkpoints:*
1. `/advisor status` → one advisor, your model, `running`/`idle`, zero cost before the first turn.
2. After the turn: an `<advisory severity="…">` card in the transcript (or a `nit` aside).
3. `/advisor status` → non-zero tokens and cost.

*Pass:* an `<advisory …>` note is visible in the transcript **and** `/advisor status` shows the
model id you configured **and** `LAB_ISSUE=8 python3 -m unittest tests.test_issues` passes (a catch-all
fails its 500 test). Bonus evidence: `ls <session-dir>/__advisor.jsonl`.

## 11-G2 — Roster with WATCHDOG.yml (G, 11.2)

*Goal:* two named specialists review the same task; a third stays paused.

*Hints:*
- Copy `solutions/WATCHDOG.yml` to `<repo>/WATCHDOG.yml`. Leave `Fixer.enabled: false`.
- `/advisor configure` opens the TUI editor and shows any validation warnings.
- Intentionally break one entry (e.g. `tools: [readd]`) and watch the warning; fix it.
- Re-run the 11-G1 prompt.

*Checkpoints:*
1. `/advisor status` lists `ErrorHandling`, `ApiContract` (active) and `Fixer` (paused).
2. Advisory cards now carry `advisor="ErrorHandling"` (or `ApiContract`).
3. Session artifacts contain `__advisor.errorhandling.jsonl` and `__advisor.apicontract.jsonl`.

*Pass:* both named JSONL files exist and `omp stats` for the session attributes advisor cost.

## 11-G3 — Prewalk hand-off (G, 11.3)

*Goal:* the expensive model plans, `@smol` implements; you can point at the hand-off line.

*Hints:*
- `omp config get modelRoles` — `smol` must differ from `default`.
- Start with `omp --prewalk` (or `/prewalk` inside a session).
- Ask for a feature that needs a plan: a `--json` flag on the CLI `orders` subcommand (`python3 -m cli orders --month 2026-03 --json`), *"plan first, then implement, then run the tests"*.
- The gate is `todo` call → first completed `edit`/`write`. Files written through `bash` never trigger it.

*Checkpoints:*
1. Startup notice `Prewalk: armed for <provider>/<id> — will switch at the first edit/write once the todo list exists.`
2. A todo card appears before the first edit.
3. Immediately after the first edit card: `Prewalk: switched to <provider>/<id> after first edit call.`
4. The model chip in the status line now names the `smol` model.
5. `/prewalk restart` → `Prewalk restarted: using @default (…) … (todo-gated).`

*Pass:* you can quote the `Prewalk: switched to …` notice and name the edit card it followed; the
model chip changed. (`/prewalk` has no `status` subcommand — the notice is the status.)

## 11-G4 — Generate a rule with /omfg (G, 11.1)

*Goal:* turn a complaint into a saved TTSR rule without hand-writing regex.

*Hints:*
- Provoke a behaviour first: ask the agent to "quickly add a debug print to cli/__main__.py".
- Then `/omfg stop adding bare print() calls to the CLI` — omp drafts a rule (regex or ast-grep),
  validates it against the recent outputs, and offers to save it.
- Inspect with `omp ttsr list` and `omp ttsr test -v -r .omp/rules/<generated>.md --source tool --tool edit --path cli/x.py 'print("x")'`.

*Checkpoints:* the generated file has frontmatter with `condition:` or `astCondition:`; `omp ttsr test` triggers on the snippet.

*Pass:* `omp ttsr list` shows the generated rule as `[native]` and the `test` call prints `Triggered (1)`.

## 11-S1 — Notes-backed context windows (S, 11.5)

*Goal:* enable `compaction.experimentalContextManagement`, run a long task, and observe a `new_context`
rollover and the `context_notes` content that survived it.

*Pass:* (1) `/tools` lists `context_notes` and `new_context`; (2) the transcript contains a
`New context window requested.` card followed by a compaction divider; (3) a `context_notes` read
after the divider returns a notebook that still names the task; (4) `read history://current/full:1-40`
returns raw entries with IDs from before the divider.

## 11-S2 — Judged rule (S, 11.1)

*Goal:* a `question:` rule that warns when the reply claims tests pass without a visible test run,
prefiltered by a `condition:` so the judge is asked only when the reply contains "pass"/"verified".

*Pass:* `omp ttsr list` shows both `condition:` and `question:` on the rule; `omp ttsr test -v` prints
`question (judged at runtime, not tested)`; with `ttsr.judge: on`, a live turn that claims success
without running tests receives a warning injection after the message ends (never mid-stream).

## 11-S3 — Advised subagent (S, 11.2)

*Goal:* attach an advisor to a Module 10 custom agent only (main session unadvised), spawn it on a
small `api/` change, and locate its review log.

*Pass:* Agent Hub shows an `advisor`-kind row under the subagent with ≥ 1 review turn, at
`<session>/<SubId>/__advisor.jsonl`; the parent's artifact dir has no top-level `__advisor.jsonl`
(`advisor.enabled` off, `/advisor on` never run in the main session).

## 11-S4 — Guardrail plan for Module 12 (S, 11.4)

*Goal:* in `notes/guardrail-plan.md`, specify three `tool_call` block predicates for the lab repo and
explain in one paragraph how a `tool_call` block differs, from the model's point of view, from a TTSR
rule on the same string.

*Pass:* three predicates each naming `event.toolName` and the `event.input` field; the paragraph
states that TTSR aborts and retries with `<system-interrupt>` while the hook returns a tool error
carrying `reason`.
