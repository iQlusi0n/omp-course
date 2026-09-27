# Module 10 — Subagents & Parallel Work (~2 h, advanced)

| | |
|---|---|
| **Built against** | `omp/18.3.5` (`omp --version`) |
| **Prerequisites** | Module 8 (eval kernels, `local://`, `artifact://`). Module 4 for `/review`. |
| **Practice repo** | `omp-course-lab` — `git checkout module-10-start` |
| **Goal** | Fan work out, watch it, steer it, and get typed results back. |
| **Lessons** | 10.1 `task` · 10.2 Hub & steering · 10.3 Custom agents · 10.4 Isolation · 10.5 Orchestration from code · 10.6 Vibe mode · 10.7 Parallel review |

**Default-off / default-on settings you will touch in this module** (verified with `omp config get` on 18.3.5 from a directory with no `.omp/config.yml` — a project or user override shadows these; `omp config get <key>` in your repo shows the effective value):

| Key | Default | Meaning |
|---|---|---|
| `async.enabled` | `true` | Spawns return immediately as background jobs; results auto-deliver. |
| `task.batch` | `true` | `task` takes `{ context, tasks[] }` (one subagent per item). |
| `task.maxConcurrency` | `32` | Session-wide cap on simultaneously running subagents. |
| `task.maxRecursionDepth` | `2` | How deep subagents may spawn subagents. |
| `task.enableEffort` | `false` | **Off.** Exposes per-item `effort` (`lo`/`med`/`hi`). |
| `task.enableLsp` | `false` | **Off.** Subagents get no `lsp` tool unless enabled. |
| `task.isolation.enabled` | `false` | **Off.** Enable with `task.isolation.enabled: true` in `.omp/config.yml` (or `omp config set`) so items accept `isolated: true` (Lesson 10.4). |
| `task.isolation.merge` | `patch` | Integrate isolated changes as a patch (`branch` = commit to `omp/task/<id>`). |
| `task.isolation.apply` | `true` | Apply successful isolated changes to the parent checkout automatically. |
| `task.agentIdleTtlMs` | `420000` | Idle subagents are parked to disk after 7 min; `0` keeps them live. |
| `eval.tools.enabled` | `true` | Kernel `@tool` / `tool(fn)` functions are exposed to subagents. |
| `eval.workpool.freshAgents` | `false` | Reuse idle workpool workers (true = fresh agent per item). |
| `display.pinnedAgents` | `collapsed` | Pinned `Subagents` jump list above the editor (`off`/`collapsed`/`full`). |
| `tui.mouse` | `false` | **Off.** Click live agent cards / jump-list rows to focus. |
| `magicKeywords.enabled` | `true` | `orchestrate`, `workflowz`, `jevify`, `ultrathink` notices. |

> Safety note that changes how you delegate: every subagent runs with `tools.approvalMode` forced to `yolo` (headless children have no UI to answer approval prompts) and with the advisor off unless the agent opts in. Your approval mode does **not** protect you inside a subagent — scope the task text, choose read-only agents, or use isolation. (Source: `omp://tools/task.md` §Flow step 12.)

---

## Lesson 10.1 — The `task` tool              (~25 min)
**You will be able to:** spawn one or many subagents from a single `task` call with the batch shape; pick the right bundled agent; get schema-validated JSON back and read it with `agent://<id>/<path>`.
**Why this exists:** A single agent session has one context window and one pair of hands. Mapping three directories, reviewing three commits, or fixing ten files serially burns your main context on details you will never need again. `task` spawns child sessions that start blank (they do **not** inherit your conversation), do bounded work, and hand back a compact result — optionally validated against a JSON Schema so the parent can read fields instead of prose. With `async.enabled` (default on) every spawn is a background job, so the parent keeps working and results arrive when they arrive.
**Demo:** `demos/10.1-batch-scouts.md`
**Concepts:**
- **Batch shape** (`task.batch: true`, default): one call = `{ "context": "<shared background>", "tasks": [ item, item, … ] }`. `context` is **required** and is rendered into every child's system prompt (`CONTEXT` section). Each item: `{ name?, agent?, task, solutionSpace, outputSchema?, schemaMode?, isolated?, effort? }`. `solutionSpace` is a one-line statement of how open-ended the child's problem is (e.g. `one fix: rename, names given`); it feeds the child's `auto` thinking classifier. The schema marks it required, but a call that omits it still spawns (the `task` text is classified instead). Names must be unique within the call (case-insensitive); omitted names become generated *AdjectiveNoun* ids.
- **Flat shape** (`task.batch: false`): one spawn per call, `{ agent?, task, … }`; share background by writing it once to a `local://ctx.md` file that each task text references (children share the parent's `local://` root).
- **Bundled agents** (`omp agents unpack --dir /tmp/agents` dumps their definitions):

  | Agent | Model role | Tools | Use for |
  |---|---|---|---|
  | `scout` | `@smol`, thinking `medium` | `read find grep glob web_search` (+`yield`) — **read-only** | Investigation, mapping, "where is X" |
  | `reviewer` | `@slow` | `read find grep glob bash lsp web_search ast_grep`; `spawns: scout` | Bug-finding review of a diff (Lesson 10.7) |
  | `security-reviewer` | *(session model)* | `read find grep glob lsp ast_grep` — read-only | Evidence-backed vulnerability sweep |
  | `task` | `@task`, thinking `auto`, `spawns: "*"` | full toolset | General multi-step work that edits files |
  | `sonic` | `@smol`, thinking `medium` | full toolset | Strictly mechanical edits / data collection |

  The model-facing prompt tags `scout`/`sonic` as low-reasoning and warns against offloading *thinking* to them. Give them lookups and mechanical edits; give `task` judgment calls.
- **Execution mode:** `async.enabled: true` (default) → the call returns ``Spawned N background agents using scout, task.`` with one ``- `<id>` (job `<jobId>`)`` line per item; each final result is injected into your conversation later as an async-result message ending with ``<id> is now idle — message it via `write agent://<id>` to follow up; transcript at history://<id>``. `async.enabled: false` → the call blocks and returns a summary (preview capped at 5 000 chars; full output at `agent://<id>`).
- **Results and where they live:** every child writes `<id>.md` (full output) and `<id>.jsonl` (its session) under your session's artifacts dir. `read agent://<id>` → full output. `read agent://<id>/modules/0/path` → JSON extraction from a structured result (slash path = extraction; a nested child is dot-qualified: `agent://<id>.<child>`). Output is capped at 500 000 bytes / 5 000 lines (`PI_TASK_MAX_OUTPUT_BYTES` / `PI_TASK_MAX_OUTPUT_LINES`).
- **`outputSchema`** (per item, JSON Schema): the child must finish through the hidden `yield` tool; its payload is validated. Precedence: per-item `outputSchema` → agent frontmatter `output` → parent session schema. `schemaMode` is `permissive` (default; warns after retries) or `strict` (fails). `scout`, `reviewer` and `security-reviewer` already ship an `output` schema, so their results are JSON even without `outputSchema`.
- **`effort`** (`"lo" | "med" | "hi"`): exists only when `task.enableEffort: true` (default **off**). Maps to the resolved model's lowest/middle/highest effort, clamped by `task.maxEffort` (default `max`). Overrides the agent's `thinkingLevel`, including `auto`.
- **Limits:** `task.maxConcurrency` (32) is a session-wide semaphore — a 40-item batch queues 8. `task.maxRecursionDepth` (2) hides `task` from children at the limit. `task.softRequestBudget` (200 requests) injects a wrap-up notice, force-stops at 1.5×. `task.maxRuntimeMs` (0 = off) is a hard wall clock. `task.agentIdleTtlMs` (7 min) parks idle children to disk.
- **Plan mode** (M4): children get a read-only tool subset (`read grep glob web_search`, +`ast_grep` if declared), no spawns, and `isolated` is rejected.
- **What children inherit:** workspace tree, skills, `AGENTS.md`/context files, the shared `local://` root, the approved-plan reference when one exists, `async.enabled`. **Not** your conversation. Write task text as if for a new hire with no chat history.
- **Model chips:** type `^` in the composer, pick a model; the chip becomes a session-local pseudonym `m1`, `m2`, … that `task`, eval `agent()` and `workpool()` accept as `agent` (bundled `task` template pinned to that model).

**Try it (Walkthrough):**
1. `cd omp-course-lab && git checkout module-10-start && omp`. Ask: *"Read `omp://tools/task.md` §Inputs and tell me the two required top-level fields of a batch call."*
   **Expected:** the answer names `context` and `tasks`; the card shows one `read` of `omp://tools/task.md`.
2. Prompt (copy verbatim):
   ```
   Use ONE task call with three scout items named ApiScout, CliScout, WebScout. context: "omp-course-lab: Python stdlib HTTP API in api/, argparse CLI in cli/, static signup form in web/. Report structure only; do not propose changes." Each task: map its directory (api/, cli/, web/) — every module, its purpose, public entry points. Use this outputSchema on every item:
   {"type":"object","required":["modules"],"properties":{"modules":{"type":"array","items":{"type":"object","required":["path","purpose"],"properties":{"path":{"type":"string"},"purpose":{"type":"string"},"entrypoints":{"type":"array","items":{"type":"string"}}}}},"risks":{"type":"array","items":{"type":"string"}}}}
   Do not wait; tell me when the spawn call returns.
   ```
   **Expected:** a `task` card whose result text starts ``Spawned 3 background agents using scout.`` followed by three ``- `ApiScout` (job …)``-style lines. Your turn ends immediately; within ~1 min three async-result messages arrive, each ending with ``… is now idle — message it via `write agent://ApiScout` …``.
3. Prompt: *"read agent://ApiScout/modules/0 and agent://CliScout/modules"*.
   **Expected:** two `read` cards returning a discrete JSON object / array (no line numbers — extraction bypasses pagination). If the read fails with *invalid JSON for extraction*, the child returned prose: re-run with `"schemaMode":"strict"`.
4. Prompt: *"read history://ApiScout"*.
   **Expected:** a concise transcript: the child's tool calls (`glob`, `read`, `grep`) and its final `yield`.
5. `omp config get task.maxConcurrency` in a second terminal.
   **Expected:** `32` (unless your project or user config overrides it — the printed value is the effective one).

**Guided task:** From the lab root, dispatch **one** batch call that mixes agent types: a `scout` that lists every place `cli/` calls `print()` (with `outputSchema` `{ "type":"object","required":["callsites"],"properties":{"callsites":{"type":"array","items":{"type":"string"}}}}`) and a `sonic` that appends a line `# M10 marker` to `notes/m10.md` (create the file if missing). *Hints:* give both items distinct `name`s; put the repo description in `context`, not in each `task`; `sonic` has full tools so its task text must say exactly one file to touch. *Checkpoints:* (a) the spawn text says ``using scout, sonic`` (deduped agent types); (b) `read agent://<ScoutName>/callsites` returns an array; (c) `git status` shows only `notes/m10.md` changed (gitignored, so `git status --ignored`). **Pass:** both async results arrive; the callsites array is non-empty; only `notes/m10.md` changed.

**Stretch:** Enable `task.enableEffort` (`omp config set task.enableEffort true`, then `/restart`), spawn the same `scout` twice with `effort: "lo"` and `effort: "hi"`, and compare `requests`/`tokens` in Agent Hub (`Alt+A`, Lesson 10.2). **Pass:** the `effort` field is accepted (no *Unknown parameter* error) and the Hub shows two rows with different token counts; `omp config set task.enableEffort false` afterwards.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| ``Unknown agent "Scout". Available: …`` | Agent names are exact and case-sensitive | Use `scout`; the error's `Available:` list names every discoverable agent |
| Call rejected: missing `context` | Batch shape requires shared `context` | Add a non-empty `context` string; or set `task.batch false` for the flat shape |
| Item rejected: duplicate name | Names are unique per call, case-insensitive | Rename (`ApiScout`, `ApiScout2`) or omit names |
| Results never arrive; turn ended | Normal with `async.enabled` — delivery is asynchronous | Keep working; `read proc://` to inspect; use the `wait` tool only when blocked |
| `SYSTEM WARNING: Subagent exited without calling yield tool after 3 reminders.` | Child ended without `yield` (often a weak model) | Re-run with a stronger agent (`task`) or a smaller task; the raw output is still in `agent://<id>` |
| `effort` "not a valid parameter" | `task.enableEffort` is off (default) | `omp config set task.enableEffort true`, restart the session |
| Child edited files you did not expect | Subagents run in `yolo` approval regardless of your mode | Use `scout` (read-only) for investigation; `isolated: true` (Lesson 10.4) for edits |
| 33rd item sits at `queued` | `task.maxConcurrency` = 32 semaphore | Wait, or raise `task.maxConcurrency` (live setting; affects queued spawns) |

**Cheat sheet:**

| Thing | Value |
|---|---|
| Batch call | `{ "context": "...", "tasks": [ { "name", "agent", "task", "solutionSpace", "outputSchema", "schemaMode", "isolated" } ] }` |
| Bundled agents | `scout` (RO) · `reviewer` · `security-reviewer` (RO) · `task` · `sonic` |
| Read output | `read agent://<id>` · `read agent://<id>/key/0` · `read agent://<id>.<child>` |
| Transcript | `read history://<id>` · bare `read history://` lists agents |
| Dump bundled definitions | `omp agents unpack [--project] [--dir DIR] [--force] [--json]` |
| Settings | `async.enabled` · `task.batch` · `task.maxConcurrency` · `task.maxRecursionDepth` · `task.enableEffort` · `task.maxEffort` · `task.softRequestBudget` · `task.maxRuntimeMs` · `task.agentIdleTtlMs` |

**Source:** omp://tools/task.md, omp://task-agent-discovery.md, omp://tools/read.md, `omp agents --help`, `omp config list`

---

## Lesson 10.2 — Watching and steering              (~20 min)
**You will be able to:** open Agent Hub, read per-agent status/cost, focus a child and steer it by typing, kill or revive one, and do the same from the composer with `agent://`, `history://`, `proc://` and `wait`.
**Why this exists:** Background spawns return in a second; the work happens out of view. Without a roster you are guessing whether a child is stuck, over budget, or editing the wrong file. Agent Hub is the human surface (roster, inspector, transcript, steer, revive, kill); the internal URIs are the same controls exposed to the model — so the agent can supervise its own children, and so can you, from either side.
**Demo:** `demos/10.2-hub-steer.md`
**Concepts:**
- **Open the Hub:** `Alt+A` (action `app.agents.hub`) — opens even when empty. `Ctrl+S` (legacy `app.session.observe`) opens the same Hub. Double-tap `←` from an **empty** main editor opens it when the session has an agent to show. `/hotkeys` shows the live chords; remap in `~/.omp/agent/keybindings.yml` (`app.agents.hub: Alt+A`).
- **Roster rows:** status (`running` / `idle` / `parked` / `aborted`), agent id, parent, unread IRC count · model role + resolved model + age · assigned task or current activity · cost, active time, request count, tool-call count, tokens. Header aggregates status and usage. Missing metrics show `usage —`, never an estimate. The main agent is not listed.
- **Roster keys:** `j`/`k`, `↑`/`↓`, wheel = select · `Enter`/click = open · `t` = flat ↔ parent/child tree · `Tab` = toggle inspector (narrow terminals) · `PageUp`/`PageDown` = scroll inspector · `r` = revive selected **parked** agent · `x` = abort if needed, then kill and release · `Esc` = close inspector, then Hub.
- **Inspector** (beside roster on wide terminals): current tool + arguments, last intent, retry state, context-window use, lineage, output/patch paths, isolated-worktree branch metadata.
- **Focus & steer:** `Enter` focuses the main TUI on that child's session (Hub closes). Type a message + `Enter` → steers a running turn or prompts an idle one; the exchange is written to the child's persisted history. `Esc` with an empty editor (or double-`←`) returns to the main session — `Esc` does **not** interrupt the child. Focusing a parked agent revives it.
- **Pinned `Subagents` block** above the editor while children run: `display.pinnedAgents` = `collapsed` (default; few rows + expander) / `full` / `off`. With `tui.mouse: true` (default **off**) you can click live task cards and jump-list rows to focus that agent directly; while on, text selection is `Shift+drag` and wheel is `Shift+wheel`.
- **`/jobs`** prints a snapshot of running/recent async jobs. **`/agents`** is a different surface: a hub of agent *definitions* where `Enter` on an agent opens its property strip (prewalk / advisor on-off-model) — it writes `task.agentPrewalk` / `task.agentAdvisor` (Module 11).
- **URIs (model side, and yours via prompts):**
  - `read agent://<id>` final output · `read agent://<id>/path/0` JSON field · `read history://` list registered agents · `read history://<id>` concise transcript (live or parked).
  - `read proc://` jobs + services · `read proc://<id>` status/output **without** consuming the delivery.
  - `write proc://<id>/kill` (no content) cancels a job or owned subagent.
  - `write agent://<id>` with content = send a message: steers a running child, prompts an idle one, **revives** a parked one. `write agent://all` broadcasts to visible live peers. Read-approved; allowed in plan mode.
  - **Peer (IRC) messaging** between siblings: children whose tool list includes `write` get a roster in their system prompt and can `write agent://<sibling>`; `agent://all` broadcasts. Availability is derived (caller has `write` + someone to message), not a setting.
  - **`wait` tool** (no arguments): blocks until the first settled owned job or incoming peer message; consumes that delivery; 30-minute safety cap; returns *"Nothing to wait for"* immediately if nothing can wake it. Results auto-deliver anyway — polling is wasted turns.
- **Lifecycle:** success or failure → `idle` (session attached) → parked after `task.agentIdleTtlMs` (session file kept) → revived by a message or Hub. Hard abort / timeout / `x` → `aborted` (terminal). Isolated runs → `parked` without a reviver (transcript still readable). `Main` is never parked. The Hub also lists parked children from a resumed session's artifacts; advisor rows (`__advisor*.jsonl`) are read-only: no message/revive/kill.

**Try it (Walkthrough):**
1. In the lab session, prompt: *"Spawn one `task` agent named Slowpoke: read every file under api/ one at a time, then summarise each in two sentences. Return the summaries."* Immediately press `Alt+A`.
   **Expected:** Hub opens; one row `running · Slowpoke · Main · … task · @task …` with cost/tokens ticking. Header shows `1 running`.
2. Press `Enter` on Slowpoke. Type: `Stop after api/__init__.py — do not read the rest.` and press `Enter`. Press `Esc`.
   **Expected:** the transcript view shows your message injected into the child's turn; back in the main session the later async result is a **short** summary (one file). `read history://Slowpoke` shows your steer message.
3. Prompt: *"Spawn a `scout` named Doomed that counts lines in every file under web/."* Open `Alt+A`, select `Doomed` with `j`/`k`, press `x`.
   **Expected:** the row flips to `aborted`; the async result delivered to the main session reports the abort (no summary).
4. Prompt: *"write agent://Slowpoke — content: Also list the HTTP routes you saw."*
   **Expected:** a `write` card with a delivery receipt; Slowpoke (idle) runs a follow-up turn using its **existing** context — no re-reading of files it already saw; a new async result arrives.
5. Wait > 7 minutes (or set `omp config set task.agentIdleTtlMs 30000` and `/restart` before step 1), open `Alt+A`, select Slowpoke, press `r`.
   **Expected:** status `parked` → `idle`; `read history://Slowpoke` still returns the full transcript.

**Guided task:** Spawn two `task` children on independent files with the same `context` and instruct them: *"Before editing, `write agent://<other name>` with the list of symbols you intend to rename; after editing, `write agent://all` with 'done'."* Watch the Hub's unread-IRC count column. *Hints:* both children need `write` — bundled `task` has full tools; use explicit `name`s so the roster ids are predictable; `read history://<id>` shows delivered peer messages. *Checkpoints:* (a) each child's transcript contains a delivered message from the other; (b) the Hub roster shows a non-zero unread count while a message is pending. **Pass:** `read history://<A>` shows a peer message from `<B>` and vice-versa.

**Stretch:** Turn on `tui.mouse` and `display.pinnedAgents: full`; with three children running, click a pinned row to focus one without opening the Hub, then return with double-`←`. **Pass:** the transcript, status line and editor switch to the child (its id in the status line) and back; `omp config set tui.mouse false` afterwards.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `Alt+A` does nothing / types `a` | Terminal did not deliver Alt as a modifier (keyboard protocol, M1) | Use `Ctrl+S`, or remap `app.agents.hub` in `keybindings.yml`; check `/hotkeys` |
| `r` has no effect | Only `parked` agents can be revived | Idle agents are already live — just message them; aborted agents are terminal |
| Esc in the child "didn't stop it" | `Esc` only returns focus; it never interrupts a child | Use Hub `x`, or `write proc://<id>/kill` |
| `write agent://<id>` → *no such agent* | id is case-sensitive and session-scoped (`Task`, `Task-2`) | `read history://` for exact ids |
| `wait` returns "Nothing to wait for" | No owned running job / live peer / owned service | Nothing is pending; results already delivered |
| Roster shows `usage —` | No progress or persisted usage data for that row | Not an error; cost appears once the child has made requests |
| Clicking a card does nothing | `tui.mouse` is off (default), or the row scrolled into terminal scrollback | `omp config set tui.mouse true`; only viewport rows are clickable |

**Cheat sheet:**

| Key / URI | Action |
|---|---|
| `Alt+A` / `Ctrl+S` / double-`←` (empty editor) | Open Agent Hub |
| `j` `k` · `Enter` · `t` · `Tab` · `r` · `x` · `Esc` | select · focus · tree · inspector · revive parked · kill · close |
| Focused child: type + `Enter`; `Esc` / double-`←` | steer / prompt; return to main |
| `read agent://<id>[/path]` · `read history://[<id>]` · `read proc://[<id>]` | output · transcript/list · jobs |
| `write agent://<id>` · `write agent://all` · `write proc://<id>/kill` | message/steer/revive · broadcast · cancel |
| `wait` (tool, no args) · `/jobs` · `/agents` | block until next delivery · job snapshot · definition property hub |
| `display.pinnedAgents` (`collapsed`) · `tui.mouse` (`false`) | pinned jump list · click-to-focus |

**Source:** omp://agent-hub.md, omp://tools/wait.md, omp://tools/task.md, omp://tools/read.md, omp://tools/write.md, omp://keybindings.md, omp://settings.md

---

## Lesson 10.3 — Custom agents              (~20 min)
**You will be able to:** write a project agent in `.omp/agents/<name>.md` with the right frontmatter, dispatch it by name, and predict which definition wins when names collide.
**Why this exists:** Bundled agents are generic. Your repo has recurring specialist jobs — "write tests for this package", "port this module", "audit this endpoint" — that need a fixed tool set, a cheap model and a stable output shape. A custom agent is a markdown file: frontmatter for policy, body for the system prompt. Because dispatch is by name, you can swap models by editing one role mapping instead of rewriting prompts.
**Demo:** `demos/10.3-custom-agent.md`
**Concepts:**
- **Where:** project `.omp/agents/<name>.md` (only the nearest `.omp` from cwd); user `~/.omp/agent/agents/<name>.md`. `.claude/agents`, `.codex/agents`, `.gemini/agents` are deliberately **skipped** (different frontmatter contract). `omp agents unpack --project` copies the five bundled definitions into `.omp/agents/` as templates.
- **Precedence (first-wins by exact, case-sensitive name):** project `.omp/agents` → user agents → OMP extension `agents/` roots (CLI `--extension`, project `extensions:`, user `extensions:`, installed plugins) → Claude marketplace plugin agents (project before user) → bundled. A project `scout.md` silently replaces bundled `scout`. Within one directory, files load in lexicographic order.
- **Frontmatter fields** (`name` and `description` required; a file missing either is skipped with a warning, other files still load):

  | Field | Accepts | Notes |
  |---|---|---|
  | `tools` | CSV or list | `yield` is auto-added. If omitted → full toolset. `task` is auto-added when `spawns` is set and depth allows. `wait` is injected when async/peers/services exist. `write` in the list enables peer messaging. `lsp` also needs `task.enableLsp`. |
  | `spawns` | `"*"`, CSV, list | Which agents this one may spawn; omitted `agent` in the child's call defaults to the first listed. Legacy: `tools` containing `task` ⇒ `spawns: "*"`. |
  | `model` | selector, CSV, list | Tried in order; `@role` aliases expand through `modelRoles` (e.g. `@smol`, `@task`, `@slow`, your own `@review`). |
  | `thinkingLevel` / `thinking-level` | level | Effort; a per-item `effort` (when enabled) overrides it. |
  | `output` | schema | Structured result contract (bundled files use `properties` / `optionalProperties` / `elements` / `metadata` keys — copy that shape). Beaten by per-item `outputSchema`. |
  | `blocking` | bool | `true` makes the parent wait inline even with `async.enabled`. No bundled agent sets it. |
  | `autoloadSkills` | list | Parent-session skill names injected before the first prompt; unknown names ignored. |
  | `read-summarize` | bool | `false` ⇒ verbatim `read` instead of structural summaries. The discovery doc says `scout` ships with it disabled; the unpacked 18.3.5 `scout.md` does not carry the key, so set it explicitly in your own file. |
  | `prewalk` | `true` / selector | Start on `model`, hand off to `@smol` (or the given selector) at first edit/write. Module 11. |
  | `advisor` | `true` / selector | Pair the child with an advisor. Module 11. |
- **Settings that override frontmatter:** `task.agentModelOverrides` (`{ "test-writer": "@smol" }`) beats `model`; `task.disabledAgents` (`["sonic"]`) makes a name fail preflight with the enabled alternatives listed; `task.agentPrewalk` / `task.agentAdvisor` (set from `/agents`) beat `prewalk` / `advisor`; `task.agentCompactionThresholdOverrides`, `task.agentServiceTierOverrides` are per-agent exact-name records.
- **Model precedence for a dispatch:** `task.agentModelOverrides[name]` → frontmatter `model` list → parent's active model, then its configured/default fallback. Role aliases resolve in the first two.
- **Live reload:** task/eval preflight reloads settings and rediscovers agents from disk before each spawn, so a file you add mid-session works on the next call — no restart. (The tool *description* the model sees is memoized per cwd, so the model may not "know" the agent exists until you name it.)
- **Ad-hoc agents with `^`:** type `^` in the composer, pick a model from the `Alt+P` picker scope; the chip becomes a session-local pseudonym (`m1`, `m2`, …) usable as `agent` in `task`, eval `agent()` and `workpool()`. They use the bundled `task` template pinned to that model; pseudonyms survive `/resume`; a same-named discovered agent wins.
- **Spawn policy of the parent:** `"*"` (default) allow any; `""` deny all; CSV allow-list. Denied ⇒ ``Cannot spawn '...'. Allowed: ...``.

**Try it (Walkthrough):**
1. In the lab root: `omp agents unpack --project` and `ls .omp/agents/`.
   **Expected:** `reviewer.md scout.md security-reviewer.md sonic.md task.md` — these now *shadow* the bundled copies (identical content, so behaviour is unchanged). Delete them after this lesson or keep as templates.
2. Create `.omp/agents/test-writer.md` from `solutions/test-writer.md` (or write your own with `name`, `description`, `tools: read, grep, glob, edit, write, bash`, `model: "@smol"`, an `output` block, and a body that says which test command to run).
   **Expected:** file exists; `read history://` still lists nothing new (definitions are not agents until dispatched).
3. Prompt: *"Use task with one item: agent test-writer, name TwApi, task: add one unittest for the smallest public function in api/. Run the tests."*
   **Expected:** ``Spawned 1 background agents using test-writer.``; the async result is JSON matching the `output` schema (`files_changed`, `tests_added`, `test_command`, `result`). `read agent://TwApi/result` returns `"pass"` (or `"fail"` with a reason).
4. `omp config set task.agentModelOverrides '{"test-writer":"@task"}'`, then re-dispatch as `TwApi2`. Open `Alt+A`.
   **Expected:** TwApi2's roster row shows the `@task` role / a different resolved model than TwApi. Reset: `omp config reset task.agentModelOverrides`.
5. `omp config set task.disabledAgents '["test-writer"]'`; dispatch again.
   **Expected:** the tool returns a preflight error naming the disabled agent and listing enabled alternatives; no subagent runs. Reset with `omp config reset task.disabledAgents`.

**Guided task:** Create `.omp/agents/scout.md` that copies the bundled `scout` (from `omp agents unpack --dir /tmp/agents`) but adds a `read-summarize: false` line and changes `description` to start with `PROJECT OVERRIDE:`. Dispatch a `scout`. *Hints:* the tool description is memoized per cwd — dispatch by name anyway; `read history://<id>` shows the system prompt is the project copy (its first lines). *Checkpoints:* discovery is first-wins by exact name; `Scout.md` (capital S) would **not** override. **Pass:** `read history://<id>` shows the `PROJECT OVERRIDE:` description; delete the file and re-dispatch → bundled behaviour returns.

**Stretch:** Define `.omp/agents/lead.md` with `spawns: test-writer, scout` and `tools: read, grep, glob, write` (no `edit`, no `bash`) and dispatch it with the task *"delegate: one test-writer per package (api/, cli/), then summarise their results"*. **Pass:** `read history://Lead` shows a `task` call whose items are `test-writer`; `agent://Lead.TwApi`-style nested ids resolve; `Lead` itself never called `edit` (it had none).

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Agent file ignored, warning in log | Missing `name` or `description`, or bad YAML | Both fields are required; frontmatter falls back to a `key: value` parser — keep it simple |
| ``Unknown agent "test-writer"`` from another directory | Only the **nearest** `.omp/agents` from cwd is read | Start `omp` in the repo root that holds `.omp/` |
| Custom agent cannot `lsp` | `task.enableLsp` default off | `omp config set task.enableLsp true` |
| Child cannot spawn | `spawns` omitted/empty, or `task.maxRecursionDepth` reached | Add `spawns:`; depth default 2 |
| Agent uses the wrong model | `task.agentModelOverrides` beats frontmatter | `omp config get task.agentModelOverrides` |
| `.claude/agents/*.md` not found | Cross-harness roots are skipped by design | Move/convert the file to `.omp/agents/` |
| `^` chip agent "unknown" | Pseudonyms are per session branch; rewinding before first mention frees it | Re-tag the model in a new message |

**Cheat sheet:**

| Thing | Value |
|---|---|
| Project / user agent | `.omp/agents/<name>.md` · `~/.omp/agent/agents/<name>.md` |
| Required frontmatter | `name`, `description` |
| Optional | `tools`, `spawns`, `model`, `thinkingLevel`, `output`, `blocking`, `autoloadSkills`, `read-summarize`, `prewalk`, `advisor` |
| Precedence | project → user → extension roots → Claude plugins → bundled (first wins, exact name) |
| Model precedence | `task.agentModelOverrides[name]` → frontmatter `model` → parent model |
| Disable / override | `task.disabledAgents` · `task.agentModelOverrides` · `task.agentPrewalk` · `task.agentAdvisor` |
| Templates | `omp agents unpack --project [--force]` |

**Source:** omp://task-agent-discovery.md, omp://tools/task.md, omp://settings.md, `omp agents --help`

---

## Lesson 10.4 — Isolation              (~15 min)
**You will be able to:** run editing subagents in an isolated copy of the checkout, choose patch vs branch integration, recover a patch when auto-apply fails, and manage agent worktrees with `omp worktree`.
**Why this exists:** Two subagents editing the same working tree race each other — one's `edit` sees the other's half-finished file, tests run against a mixture, and `git status` becomes noise. Isolation gives each child its own materialised workspace (copy-on-write clone or overlay where the filesystem supports it, recursive copy as a last resort), captures its changes, and integrates them into your checkout as a patch or a branch — atomically, after the child finishes.
**Demo:** `demos/10.4-isolation.md`
**Concepts:**
- **Enable:** `task.isolation.enabled` (default **`false`**). Turn it on for the lab by adding `task.isolation.enabled: true` to `omp-course-lab/.omp/config.yml` (the lab ships an empty `.omp/` — create the file; or `omp config set task.isolation.enabled true` for your user config), then start `omp` from the lab root: the `isolated` item field is part of the `task` tool schema, which is built when the session starts. When true **and plan mode is off**, every task item accepts `isolated: true`. Isolation requires a git repository (``Isolated task execution requires a git repository.``).
- **Backend:** `isolation.backend` = `auto` (default) | `apfs` | `btrfs` | `zfs` | `reflink` | `overlayfs` | `projfs` | `block-clone` | `rcopy`. `auto` walks the candidate list and falls back (Linux: kernel overlay → `fuse-overlayfs` → clones → recursive copy); the result reports `fellBack` / `fallbackReason`. Legacy values `worktree`, `fuse-overlay`, `fuse-projfs` migrate to `rcopy`, `overlayfs`, `projfs`.
- **Integration:** `task.isolation.merge` = `patch` (default): the child's root diff is captured to `<id>.patch` in the session artifacts and applied to your checkout only if it applies cleanly; otherwise the `.patch` is left for manual handling. `branch`: the child's work is committed on `omp/task/<id>` in a temporary worktree and cherry-picked into your checkout; your dirty tree is stashed first — a stash-pop conflict does **not** undo the cherry-picks (reported as `stashConflict`). Nested git repos are diffed and merged separately.
- **`task.isolation.apply`** (default `true`): set `false` to keep the patch/branch artifacts without touching your checkout — the review-before-merge workflow. `task.isolation.commits` = `generic` | `ai` (commit message style for nested-repo changes).
- **Lifecycle:** isolated agents are torn down at completion → status `parked` **without a reviver** (workspace merged and cleaned). You can still `read history://<id>` and `read agent://<id>`, but you cannot message them. Hub inspector shows `patchPath`, `branchName`, `branchBaseSha`.
- **Result fields:** `patchPath`, `branchName`, `branchBaseSha`, `nestedPatches` on the `SingleResult`.
- **eval side:** `agent(prompt, isolated=True, apply=..., merge=...)` — `merge=False` forces patch mode for that call; `apply=False` keeps artifacts.
- **`omp worktree` (alias `omp wt`):** `list` (default) · `clear [--dry-run] [--all]` · `add [-b BRANCH | -B BRANCH] [--detach] [-C DIR] PATH [COMMIT]` · `--json`. Agent-managed worktrees live under `~/.omp/wt` (override: `worktree.base` setting or `OMP_WORKTREE_DIR`, absolute or `~`-relative). `worktree.clone: true` (default) makes new worktrees start as a copy-on-write clone so ignored build artefacts carry over; `worktree.cleanSource` resets the original checkout after `/wt` carries changes over (Module 5).
- **Plan mode** rejects `isolated`, `apply`, `merge` per spawn.

**Try it (Walkthrough):**
1. Add `task.isolation.enabled: true` to `omp-course-lab/.omp/config.yml` (create the file if missing), then `omp config get task.isolation.enabled` and `omp config get task.isolation.merge` from the lab root.
   **Expected:** `true` and `patch` (from another directory the first prints `false` — the default).
2. In the lab (clean tree, on `main`), prompt: *"One batch, two `sonic` items, both `isolated: true`: IsoA appends `# iso A` to `api/__init__.py`; IsoB appends `# iso B` to `cli/__init__.py`."*
   **Expected:** ``Spawned 2 background agents using sonic.``; when both results arrive, `git status` shows both files modified in **your** checkout, `git diff` shows one line each. `Alt+A` → inspector for IsoA shows a `patch` path and status `parked`.
3. `omp config set task.isolation.apply false`, `git checkout -- .`, repeat step 2 with names IsoC/IsoD.
   **Expected:** your tree stays clean; each result mentions its `.patch` artifact; `read agent://IsoC` shows the child's summary. Apply one by hand: `git apply <patchPath from the inspector>`. Reset: `omp config set task.isolation.apply true`.
4. `omp config set task.isolation.merge branch`, repeat with names IsoE/IsoF.
   **Expected:** `git log --oneline -3` shows two cherry-picked commits on your branch; `git branch --list 'omp/task/*'` shows the task branches (or their cleanup, depending on the run). Reset: `omp config set task.isolation.merge patch`.
5. `omp worktree list` then `omp worktree clear --dry-run`.
   **Expected:** a (possibly empty) list under `~/.omp/wt`; dry-run prints what would be removed without touching the filesystem.

**Guided task:** Make two isolated `sonic` agents edit the **same** line of `api/__init__.py` with different text. *Hints:* patch mode applies each root patch only if it applies cleanly; the second one will not. *Checkpoints:* the first result applied; the second result reports a failed apply and leaves its `.patch`; `git apply --3way <patch>` (or `git apply --reject`) surfaces the conflict, which you can resolve with `read api/__init__.py:conflicts` + `conflict://<N>` (Module 4). **Pass:** both patches exist in the artifacts dir; final `api/__init__.py` contains your chosen resolution; tree is clean after `git checkout` or commit.

**Stretch:** Set `isolation.backend: rcopy` (`omp config set isolation.backend rcopy`), re-run step 2, and compare wall time in the Hub against `auto`. Then try `overlayfs`. **Pass:** each run completes; the result/inspector reports the backend actually used (and `fellBack` when `overlayfs` is unavailable); reset to `auto`.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `isolated` "not a valid parameter" | `task.isolation.enabled` is off (default `false`), or plan mode is on | `task.isolation.enabled: true` in `.omp/config.yml` / `omp config set task.isolation.enabled true`; leave plan mode |
| `Isolated task execution requires a git repository.` | cwd is not inside a git repo | `git init` or run from the lab root |
| Patch not applied, `.patch` left | Patch did not apply cleanly against your current tree | `git apply --3way <path>`; resolve; or re-run after committing your own edits |
| Child `parked`, `write agent://` fails | Isolated agents have no reviver | Spawn a new agent; `history://<id>` still works |
| `stashConflict` in the result (branch mode) | Your dirty tree conflicted on stash pop | Cherry-picks are already on HEAD; `git stash list` + `git stash pop` and resolve |
| Backend errors on Linux (`fusermount` missing) | overlay backends need kernel overlay or `fuse-overlayfs` | `isolation.backend: rcopy` (slow but universal), or `auto` |
| Worktree dirs pile up in `~/.omp/wt` | Task copies / PR checkouts not cleaned | `omp worktree clear` (`--all` includes live PR checkouts) |

**Cheat sheet:**

| Thing | Value |
|---|---|
| Per item | `"isolated": true` (batch or flat shape); eval: `agent(..., isolated=True, apply=?, merge=?)` |
| Settings | `task.isolation.enabled` (**false**; set true in `.omp/config.yml`) · `isolation.backend` (auto) · `task.isolation.merge` (patch\|branch) · `task.isolation.apply` (true) · `task.isolation.commits` (generic\|ai) |
| Artifacts | `<id>.patch` (patch mode) · branch `omp/task/<id>` (branch mode) · `patchPath`/`branchName` in result & Hub inspector |
| Worktrees | `omp worktree [list\|clear\|add]`, `--dry-run`, `--all`, `--json`; base `~/.omp/wt` (`worktree.base`, `OMP_WORKTREE_DIR`) |

**Source:** omp://tools/task.md, omp://settings.md, omp://environment-variables.md, omp://cli-reference.md, `omp worktree --help`, `omp config list`

---

## Lesson 10.5 — Orchestration from code              (~25 min)
**You will be able to:** launch and await subagents from an `eval` cell with `agent()`/`wait()`, run a keep-alive `workpool()` over many items, use `completion()` for cheap one-shot judgments, expose a kernel function to children with `@tool`, and trigger the `orchestrate`/`workflowz`/`jevify` contracts.
**Why this exists:** `task` is a fire-and-forget fan-out. Real pipelines have shape: research → plan → N workers → review → merge, with results feeding the next stage and per-item retries. The persistent `eval` kernel already holds state, so it is the natural place for orchestration logic: handles are values, `wait()` is a barrier, a `workpool()` amortises worker context across items, and `@tool` lets children call **your** Python (a linter, a fixture generator, a validator) instead of reinventing it — every call runs inside your kernel.
**Demo:** `demos/10.5-workpool.md`
**Concepts:**
- **`agent()`** — registers one background subagent job and returns a handle immediately.
  - Python: `agent(prompt, *, agent=None, label=None, schema=None, schema_mode=None, isolated=None, apply=None, merge=None, tools=None)`.
  - JS: `await agent(prompt, { agent, label, schema, schemaMode, isolated, apply, merge, tools })`.
  - Handle: `.id`, `.agent`, `.handle` (`agent://<id>`), `.status`, `.done()`, `.wait(timeout=None)`, `.send(message)`, `.cancel()`, `.output()`; Python handles are awaitable. Preflight errors (unknown agent, spawn policy, depth, unknown `tools` names) fail the call synchronously; execution errors surface from `.wait()`. No per-call `model` — pick an agent (or a `^` pseudonym). Eval children are keep-alive and **do not share your eval kernel** (`shareEvalSession=false`).
- **`wait(handles, timeout=None, raise_errors=True)`** (JS `wait(handles, { timeout, raiseErrors })`): barrier over agent/completion handles, results in input order; `TimeoutError` if still running after `timeout`; with `raise_errors=False` a failed handle is returned in its slot as the error object. Time spent in `wait()` **pauses** the cell watchdog (default 30 s timeout is not the problem; compute is).
- **`workpool(agent=None, *, name=None, context=None, tools=None)`** (JS: `workpool(agentName?, { name, context, tools })`): keep-alive pool bounded by live `task.maxConcurrency`.
  - `.push(*items)` → item ids `<pool>#<seq>`. An item goes to the idle worker with the lowest context usage, spawns a new worker while the pool has room, else is queued round-robin and handed over as one batch when that worker's turn ends. `eval.workpool.freshAgents: true` = new context per item, no batching.
  - Workers answer each batch item with `yield({ key: <1-based>, data: {...} })` or `yield({ key, error })`; the last key ends the turn.
  - The pool **name is the aggregate async-job id**; its first full drain settles and closes the pool (new phase = new named pool). The aggregate result auto-delivers once. There is **no** `pool.wait()` — leave eval and call the zero-argument `wait` tool only when truly blocked; this keeps the kernel free to serve `@tool` calls.
  - `.status()` worker/item counts + context usage; `.peek()` non-consuming `{ batches, pending }`; `.close()` drops queued items. After a restart, workers remain parked keep-alive agents (`write agent://<id>`).
- **`completion(prompt, *, model="default", system=None, schema=None)`** (JS `completion(prompt, { model, system, schema })`): stateless, tool-free one-shot model call → `CompletionHandle` (`.wait()`, `.done()`, `.cancel()`). `model` is a tier: `"smol"`, `"default"`, `"slow"`. `schema` → parsed data from `.wait()`. Handles evicted 30 min after settling.
- **Kernel-defined tools** (`eval.tools.enabled`, default on): Python `@tool` / `@tool(name=..., description=...)` — JSON Schema inferred from type hints (`str int float bool list[...] dict[...] Literal Optional Annotated[T, "desc"]`) and defaults; positional-only params rejected; async functions awaited. JS `tool(fn, { name?, description?, parameters? })`. `tool.defined()` lists, `tool.undefine(name)` removes, redefining replaces. Consumers: `task` items' `tools`, `agent(tools=[...])`, `workpool(tools=[...])`. Calls run on a dedicated runner thread (py) so a cell blocked in `wait()` still serves them; a raising tool reports the error to the caller and the kernel keeps running; a name defined in both kernels is an error; plan mode rejects `tools`.
- **Limits:** `task.maxRecursionDepth` (2) and `task.maxConcurrency` govern eval fan-out too. Owner teardown (`reset: true`, session end) cancels children's jobs, releases completion handles, and closes pools.
- **Magic keywords** (lowercase, standalone prose; not inside code spans/fences; `orchestrate,` matches, `orchestrated` / `orchestrate()` do not; applies to that turn only):
  - `orchestrate` — multi-agent contract: scope, delegate substantial independent work in parallel, verify each phase, continue to completion.
  - `workflowz` — deterministic multi-subagent workflow built on the eval kernel's `agent()`, `completion()`, handles, `wait()`, `workpool()`; injected only when **both** `eval` and `task` are active. Setting key: `magicKeywords.workflow`.
  - `jevify` — bulk-classification contract for the kernel's `judge()` helper (freeze question/rubric/threshold, judge everything in one batch, read only what is flagged); needs `eval`.
  - Global switch `magicKeywords.enabled`; per-keyword `magicKeywords.ultrathink|orchestrate|workflow|jevify` (all default `true`).

**Try it (Walkthrough):**
1. Prompt: *"In a Python eval cell, define `@tool def lint(path: str) -> list[str]` using only `ast` and `pathlib`: report unused imports and trailing whitespace as `path:line: message`. Then `display(tool.defined())`."* (Solution: `solutions/workpool-lint.py`.)
   **Expected:** the eval card prints `["lint"]`.
2. Prompt: *"Same kernel: `h = agent('Run the lint tool on cli/__init__.py and report the raw list; do not edit.', agent='sonic', tools=['lint']); display(h.handle)`."*
   **Expected:** the cell prints `agent://<id>` immediately (no blocking). Shortly after, an async result arrives; `Alt+A` shows a `sonic` row.
3. Prompt: *"Same kernel: `display(h.wait())`."*
   **Expected:** the child's output (the lint list). Because the child ran `lint`, your kernel served a call while the cell was in `wait()`.
4. Prompt: *"Same kernel: create `pool = workpool('sonic', name='lintfix', context='omp-course-lab; fix ONLY what lint reports; run lint again until empty; touch no other file', tools=['lint'])`, push one item per Python file under api/, cli/ and tests/ (15 files; never `generated/`), then `display(pool.status())`."*
   **Expected:** `status()` shows ≤ `task.maxConcurrency` workers and N items; the pinned `Subagents` block and `Alt+A` list the pool's workers. Ending your turn lets results flow; the aggregate `lintfix` result arrives once when the pool drains.
5. Prompt: *"`display(read('agent://lintfix'))` then `git diff --stat`."*
   **Expected:** the aggregate output; `git diff --stat` shows only the pushed files changed.

**Guided task:** Rewrite step 4 as a two-phase pipeline: phase 1 a `scout` `agent()` with `schema={"type":"object","required":["files"],"properties":{"files":{"type":"array","items":{"type":"string"}}}}` that lists files with lint findings; phase 2 a fresh named pool that fixes only those. Use `completion(prompt, model="smol", schema=...)` to decide, per file, whether the diff is "trivial" or "needs review". *Hints:* `wait([h])[0]` returns parsed data when a schema was given; a settled pool cannot be reused — name phase 2 `lintfix2`; `display()` JSON so the parent can read it. *Checkpoints:* (a) scout result parsed; (b) `pool.status()` shows only flagged files; (c) completion verdicts listed. **Pass:** `notes/m10.md` contains a table `file | lint findings before | after | verdict`; every "after" is `0`.

**Stretch:** Put the word `workflowz` in a prompt asking for the same pipeline with adversarial review (second pool of `reviewer`s over the diffs). **Pass:** the reply's visible plan names `agent()`/`workpool()`/`wait()` phases and `read history://<reviewer id>` shows real reviewer runs; compare the cost in `Alt+A` header to your manual version.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `agent()` raises `Unknown tools: lint` | `@tool` not defined in *this* kernel, or `eval.tools.enabled` off | Define it in the same language kernel; `omp config get eval.tools.enabled` |
| Cell times out at 30 s during compute | Watchdog counts compute, not `wait()` | `timeout: 0` or larger; `wait()` already pauses it |
| `pool.push` after drain "pool closed" | First full drain settles the pool | Create a new named pool |
| `asyncio.run()` error | Kernel already runs an event loop | Use top-level `await` |
| Children cannot see kernel variables | Eval children never share your kernel | Pass data in the prompt or via `local://` files; expose functions via `@tool` |
| `workflowz` did nothing extra | Needs both `eval` and `task` active, exact lowercase, not in a code span | Check `/settings` → Interaction → Magic Keywords; `omp config get magicKeywords.workflow` |
| Tool name clash error | Same name defined in py **and** js kernels | `tool.undefine()` in one kernel |
| Python `agent` is not callable (`TypeError: ... is not a callable object`) | A cell rebound the prelude name (`agent = Path(...)`) | `del agent` in that kernel, or `reset: true` for the language |

**Cheat sheet:**

| Helper | Python | JS |
|---|---|---|
| spawn | `h = agent(prompt, agent=, label=, schema=, schema_mode=, isolated=, apply=, merge=, tools=)` | `const h = await agent(prompt, { agent, label, schema, schemaMode, isolated, apply, merge, tools })` |
| handle | `.id .agent .handle .status .done() .wait(timeout) .send(msg) .cancel() .output()` · awaitable | same, `await h.wait()` |
| barrier | `wait(handles, timeout=None, raise_errors=True)` | `await wait(handles, { timeout, raiseErrors })` |
| pool | `p = workpool(agent, name=, context=, tools=)`; `p.push(*items)` `.status()` `.peek()` `.close()` | `const p = await workpool(agentName, { name, context, tools })` |
| one-shot | `completion(prompt, model="smol"\|"default"\|"slow", system=, schema=)` | `completion(prompt, { model, system, schema })` |
| kernel tool | `@tool` / `@tool(name=, description=)`; `tool.defined()`; `tool.undefine(n)` | `tool(fn, { name, description, parameters })` |
| keywords | `orchestrate` · `workflowz` (eval+task) · `jevify` (eval) · `magicKeywords.*` | |

**Source:** omp://tools/eval.md, omp://python-repl.md, omp://magic-keywords.md, omp://tools/wait.md, omp://settings.md, live kernel introspection (`inspect.signature`, `Function.prototype.toString`)

---

## Lesson 10.6 — Vibe mode              (~15 min)
**You will be able to:** enter `/vibe`, spawn `fast` and `good` workers, steer and wait on them, and know when a director beats a `task` fan-out.
**Why this exists:** `task` children are disposable; each new job starts blank. Some work is better done by a **persistent** worker that accumulates context over several turns — "keep fixing the flaky test until green", "iterate on this migration". Vibe mode demotes your top-level session to a director with read-only tools plus five worker controls, and keeps two tiers of long-lived workers running. You direct; they edit; you verify by reading the files they touched.
**Demo:** `demos/10.6-vibe.md`
**Concepts:**
- **Toggle:** `/vibe` enters; `/vibe <prompt>` enters and submits the first directive; `/vibe` again **exits** — exit cancels in-flight turns, **kills every worker** in the scope, and persists terminal lifecycle records. Status line shows `Vibe`. TUI-only command; mutually exclusive with active *and paused* plan/goal modes; `/new`, `/fork`, `/move`, `/handoff` are rejected while active.
- **Director toolset:** `read`, optional parent-owned `todo`, and `vibe_spawn` / `vibe_send` / `vibe_wait` / `vibe_kill` / `vibe_list`. No `edit`, no `bash` — the director cannot fix things itself.
- **Tiers:** `fast` → bundled `sonic` (`@smol`); `good` → bundled `task` (`@task`). The tier always picks the **bundled** definition, never a same-named project agent. `task.agentModelOverrides.sonic` / `.task` win over the bundled model; keep aliases there and concrete selectors in `modelRoles` (e.g. `task.agentModelOverrides: { sonic: "@fast_worker", task: "@good_worker" }`).
- **Tools:** `vibe_spawn { cli: "fast"|"good", prompt, name? }` (blank worker, self-contained brief; name ≤ 48 chars) · `vibe_send { session, message }` (steers a streaming turn; queues if unsteerable; starts a turn if idle/parked) · `vibe_wait { sessions?, timeout? }` (first watched turn to settle; all in-flight when omitted; default 30 s; acknowledges results so they are not delivered twice) · `vibe_kill { session }` (cancel, clear queue, release; transcript stays at `history://<id>`) · `vibe_list {}` (tier, state, turn/queue counts, model, recent activity).
- **Delivery:** spawn/send return immediately; each worker-turn result self-delivers into the director conversation (preview-capped; full output at `agent://<id>`). Workers are real keep-alive task-executor subagents with their own persisted child transcripts — they appear in `Alt+A`.
- **Resume:** a session whose mode is `vibe` rehydrates completed workers as idle/parked; a turn cut by a process restart is not resumed. Killed / mode-exit workers stay terminal.
- **When vs `task`:** `task`/`workpool` for many independent, bounded jobs with typed results; `/vibe` for a few long-running workstreams that need iteration and a human director in the loop. Routing rule from the doc: draft with `fast`, escalate to `good` when mechanical execution stalls or judgment is needed.

**Try it (Walkthrough):**
1. In the lab, type `/vibe`.
   **Expected:** status line shows `Vibe`; the next assistant turn lists only `read`, `todo` and `vibe_*` tools when asked *"what tools do you have?"*.
2. Prompt: *"Spawn a fast worker named Fixer: add a docstring to every function in cli/ that lacks one. Spawn a good worker named Judge: read cli/ and list functions whose behaviour is unclear from the code, do not edit."*
   **Expected:** two `vibe_spawn` cards returning immediately; `Alt+A` shows `Fixer` (`sonic`) and `Judge` (`task`) running.
3. Prompt: *"vibe_wait with timeout 60."*
   **Expected:** a `vibe_wait` card that returns when the first worker settles; its result is delivered once (not duplicated later).
4. Prompt: *"vibe_send Fixer: also add a module docstring to cli/__init__.py."*
   **Expected:** the message steers the running turn or starts Fixer's next turn; a new result arrives; `git diff --stat` shows only `cli/` changes.
5. Type `/vibe`.
   **Expected:** mode exits; `vibe_list` no longer exists; `Alt+A` shows both workers `aborted`; `read history://Fixer` still works.

**Guided task:** Use `/vibe` to make a `fast` worker implement the seeded bug fix for issue #1 (from `docs/ISSUES.md`: `cli/format.py`, `money(1234)` must return `$12.34`) while a `good` worker writes a regression test for it; then `vibe_send` the good worker the fast worker's diff (paste from `read agent://<id>`) for review. *Hints:* workers never see the director's conversation — every brief must name files and acceptance criteria; the director verifies by `read`ing touched files. *Checkpoints:* `vibe_list` shows both `idle` after their turns; the new test fails before the fix and passes after. **Pass:** `python3 -m unittest discover -s tests` and `LAB_ISSUE=1 python3 -m unittest tests.test_issues` both exit 0; `git diff --stat` touches only `cli/format.py` and one test file.

**Stretch:** Route tiers through roles: set `task.agentModelOverrides` to `{ "sonic": "@fast_worker", "task": "@good_worker" }` and add both roles in `modelRoles`; re-enter `/vibe`, spawn one of each, and confirm the resolved models in `vibe_list`. **Pass:** `vibe_list` shows the two role-backed models; reset the overrides afterwards.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `/vibe` refused | Plan or goal mode is active or paused | Exit plan/goal mode first |
| `/new`, `/fork`, `/move`, `/handoff` refused | Not allowed while vibe mode is active | `/vibe` to exit first |
| Worker "unknown" in `vibe_send` | Worker ids are scoped to the owning agent + parent session | `vibe_list` for live ids |
| Worker `dead` | Its child session can no longer be resolved | Spawn a replacement |
| Workers vanished after exit | Exit kills the whole scope by design | Collect outputs (`agent://<id>`) before `/vibe` |
| Director "cannot edit" | Director toolset is read-only | That is the point — `vibe_send` the worker |
| Interrupted turn not resumed after restart | Documented behaviour | `vibe_send` the worker again |

**Cheat sheet:**

| Thing | Value |
|---|---|
| Enter / exit | `/vibe` · `/vibe <first directive>` · `/vibe` again = exit (kills workers) |
| Tiers | `fast` → `sonic` (`@smol`) · `good` → `task` (`@task`) · override via `task.agentModelOverrides.sonic/.task` |
| Tools | `vibe_spawn {cli, prompt, name?}` · `vibe_send {session, message}` · `vibe_wait {sessions?, timeout?=30s}` · `vibe_kill {session}` · `vibe_list {}` |
| Outputs | `agent://<id>` · `history://<id>` · `Alt+A` |

**Source:** omp://vibe-mode.md, omp://task-agent-discovery.md, omp://agent-hub.md

---

## Lesson 10.7 — `/review` revisited: parallel review with reviewer subagents              (~15 min)
**You will be able to:** sweep uncommitted work, a commit and a branch in parallel with `reviewer` subagents, read their structured findings from `agent://`, and add a `security-reviewer` pass.
**Why this exists:** In Module 4 `/review` gave you one LLM review of one diff (base-branch, working copy, commit, or a GitHub PR — the same diff kinds `/annotate code-review` offers). Before a release you often have three things to review at once and a bug-finder's output that you want as **data**: priority, file, line range, confidence. The bundled `reviewer` agent is exactly that: a read-only-ish specialist (git read commands only) with a fixed output schema that streams findings as incremental `yield` sections. Three reviewers in one batch call cost the same wall time as one.
**Demo:** `demos/10.7-parallel-review.md`
**Concepts:**
- **`reviewer` definition** (from `omp agents unpack`): model `@slow`; tools `read find grep glob bash lsp web_search ast_grep` (+`yield`); `spawns: scout`; bash restricted by its prompt to `git diff`, `git log`, `git show`, `jj diff --git`, `gh pr diff` — never edits or builds. Procedure: get the patch → read modified files in full → one incremental `yield` per finding under `type: ["findings"]` → verdict sections `overall_correctness` (`correct`|`incorrect`), `explanation`, `confidence`. Criteria: provable impact, actionable, unintentional, **introduced in the patch**, no unstated assumptions, proportionate rigor. Priorities P0 (blocks release) … P3 (nice to have).
- **Output schema** (frontmatter `output`): `overall_correctness`, `explanation`, `confidence` required; `findings[]` of `{ title, body, priority 0-3, confidence, file_path, line_start, line_end }` (≤ 10-line ranges, must overlap the diff). Read with `read agent://<id>/findings/0/title`, `read agent://<id>/overall_correctness`.
- **`security-reviewer`:** read-only (`read find grep glob lsp ast_grep`), output `coverage_summary` + optional `findings[]` with `rule_id`, `title`, … — use it for a vulnerability sweep of the repo state, not a diff.
- **Targets you can name in task text:** working copy (`git diff`), staged (`git diff --cached`), a commit (`git show <sha>`), a branch (`git diff main...conflict-lab`), a PR (`gh pr diff N`, needs `gh`). Put the target in each item's `task`; put repo conventions in `context`.
- **`/review` vs. reviewer subagents:** `/review` is the one-target bundled command (Module 4; its diff resolver is shared with `/annotate code-review`). For parallel sweeps, dispatch `reviewer` items yourself. The Hub shows each reviewer's cost so you can compare `@slow` runs.
- **Reading results:** async results carry a preview; the full JSON is `agent://<id>`. `history://<id>` shows every `git show`/`read` the reviewer made — useful to check that a P0 is patch-anchored.

**Try it (Walkthrough):**
1. In the lab on `main` (clean tree): apply a deliberate change — prompt *"In cli/, change one `print()` call to print a different variable name that does not exist; do not run anything."* Commit nothing.
   **Expected:** `git diff --stat` shows one file in `cli/`.
2. Prompt (one batch call):
   ```
   context: "omp-course-lab (Python stdlib). Review only what the target diff introduces."
   tasks:
     - name: RevWorking, agent: reviewer, task: "Target: `git diff` (uncommitted working copy)."
     - name: RevCommit,  agent: reviewer, task: "Target: `git show HEAD` (the most recent commit)."
     - name: RevBranch,  agent: reviewer, task: "Target: `git diff main...conflict-lab` (the conflict-lab branch vs main)."
   ```
   **Expected:** ``Spawned 3 background agents using reviewer.``; `Alt+A` shows three `@slow` rows; results arrive independently.
3. Prompt: *"read agent://RevWorking/overall_correctness and agent://RevWorking/findings/0"*.
   **Expected:** `"incorrect"` and a finding object whose `file_path` is your `cli/` file with `line_start`/`line_end` on the changed line and `priority` 0 or 1.
4. Prompt: *"read agent://RevCommit/overall_correctness"*.
   **Expected:** most likely `"correct"` with an empty/absent `findings` (the tagged start state is intended to be clean) — or real findings, which is the point.
5. `git checkout -- cli/`.
   **Expected:** clean tree.

**Guided task:** Add a fourth item `agent: security-reviewer`, name `Sec`, task *"Sweep api/ for input-handling and SQL-construction risks; cite file:line."*; then ask the parent to *"combine the four results into `notes/m10-review.md`: one table sorted by priority, columns target | priority | title | file:line | confidence"*. *Hints:* `read agent://Sec/findings` returns the array; the parent can `read` each `agent://` and write the note — no re-review needed. *Checkpoints:* four async results; the note lists every finding once. **Pass:** `notes/m10-review.md` exists with ≥ 1 row from `RevWorking` and the `Sec` coverage summary quoted.

**Stretch:** Create `.omp/agents/reviewer.md` (project override) that copies the bundled reviewer but restricts `tools` to `read, grep, glob, bash` and sets `model: "@smol"`; re-run step 2 and compare cost and findings quality in the Hub. **Pass:** the Hub rows show the `@smol` role; you can articulate one finding the cheap reviewer missed (or confirm parity); delete the override.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Reviewer result is prose, extraction fails | Weak model ignored the `yield` sections | Use `schemaMode: "strict"` or leave `model` at `@slow` |
| `findings/0` "missing" | No findings — `findings` is optional in the schema | Read `overall_correctness` / `explanation` |
| Reviewer edited a file | Reviewer prompt forbids it, but `bash` is in its tool list | Use `isolated: true`, or the read-only `security-reviewer` |
| `gh pr diff` fails | `gh` not installed/authenticated | Review locally: `git fetch` + `git diff main...branch` |
| Branch diff empty | Wrong range syntax | `main...conflict-lab` (three dots) |
| Three reviewers took as long as one | That is the win — each ran concurrently | Compare `active time` per row in the Hub |

**Cheat sheet:**

| Thing | Value |
|---|---|
| Parallel review | one batch, `agent: reviewer` per target; target named in each `task` |
| Reviewer output | `overall_correctness` · `explanation` · `confidence` · `findings[] {title, body, priority, confidence, file_path, line_start, line_end}` |
| Read | `read agent://<id>/findings/0` · `read agent://<id>/overall_correctness` · `read history://<id>` |
| Security sweep | `agent: security-reviewer` → `coverage_summary`, `findings[] {rule_id, title, …}` |
| Single target | `/review` (Module 4) · `/annotate code-review [focus]` |

**Source:** omp://tools/task.md, omp://slash-command-internals.md, omp://agent-hub.md, `omp agents unpack` (bundled `reviewer.md`, `security-reviewer.md`)

---

## Module checkpoint
You are done with Module 10 when `exercises.md` W + all four G tasks pass. Continue to Module 11 (guardrails: prewalk, advisor, TTSR) which builds on `task.agentPrewalk` / `task.agentAdvisor` from Lesson 10.3, or Module 14 (browser/desktop), which uses `agent()` fan-out from Lesson 10.5.
