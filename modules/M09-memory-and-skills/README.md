# Module 9 — Memory & Self-Authored Skills (~1 h, intermediate)

| | |
|---|---|
| **Built against** | `omp --version` → `omp/18.3.1` |
| **Prerequisite** | Module 6 (settings layering, skills, `skill://`) |
| **Practice repo** | `omp-course-lab` at `git checkout module-9-start` |
| **Fixtures used** | issue #6 (`"database is locked"` when `DATABASE_URL` uses the `sqlite:///` form — a misleading error; fix in `api/db.py`), issue #7 (`order_count` includes cancelled orders — an investigation with seeded red herrings; fix in `api/db.py`) — see `omp-course-lab/docs/ISSUES.md`. Gated tests: `LAB_ISSUE=6` / `LAB_ISSUE=7 python3 -m unittest tests.test_issues`. |
| **Coursework** | `exercises.md` · answers in `solutions/` · one-page `cheatsheet.md` |

**Goal:** Make omp remember across sessions and turn lessons into reusable skills.

**Everything in this module is off by default.** Three settings gate every feature below and ship as off/false on omp 18.3.1 (verified with `omp config get`); a fourth, already on, is listed because Module 6 flagged it:

| Setting | Default | Unlocks |
|---|---|---|
| `memory.backend` | `off` | a memory backend (`local`, `mnemopi`, `hindsight`, `sharpshooter`); `/memory …`; `memory://` reads |
| `autolearn.enabled` | `false` | `manage_skill` tool (always) and `learn` tool (only when a backend is active) |
| `checkpoint.enabled` | `false` | `checkpoint` + `rewind` tools |
| `skills.enableSkillCommands` | `true` (observed) | `/skill:<name>` slash commands — already on; listed because Module 6 flagged it |

Which tools you get depends on **which backend** you choose, not just on turning memory on:

| Tool | `off` | `local` | `mnemopi` | `hindsight` | Extra gate |
|---|---|---|---|---|---|
| `retain` | — | — | ✅ | ✅ | — |
| `recall` | — | — | ✅ | ✅ | — |
| `reflect` | — | — | ✅ (recall + formatting, no synthesis model) | ✅ (server-side synthesis) | — |
| `memory_edit` | — | — | ✅ | — | — |
| `learn` | — | ✅ | ✅ | ✅ | `autolearn.enabled` |
| `manage_skill` | ✅ | ✅ | ✅ | ✅ | `autolearn.enabled` (independent of backend) |
| `checkpoint` / `rewind` | ✅ | ✅ | ✅ | ✅ | `checkpoint.enabled` (independent of backend) |
| `read memory://root[/…]` | — | ✅ | — | — | file-backed root only exists under `local` |
| `read memory://<memory-id>` | — | — | ✅ | — (returns a corrective pointer) | — |

Source: omp://memory.md, omp://mnemosyne-memory-backend.md, omp://tools/retain.md, omp://tools/recall.md, omp://tools/reflect.md, omp://tools/memory_edit.md, omp://tools/learn.md, omp://tools/manage_skill.md, omp://tools/checkpoint.md, omp://tools/rewind.md, omp://tools/read.md.

---

## Lesson 9.1 — Backends              (~15 min)
**You will be able to:** pick a memory backend and state which tools, files, and `memory://` URLs it gives you; enable it project-locally or globally; inspect it with `/memory`.
**Why this exists:** A fresh omp session knows nothing about yesterday. Module 6 fixed the *stable* facts (`AGENTS.md`, rules, skills), but the things you discover while working — "the tests copy the DB and set `DATABASE_URL` themselves", "that `database is locked` message is a lie" — evaporate at `/new`. A memory backend gives omp a place to keep that residue. omp ships several, and they differ in *where* data lives (files, local SQLite, a remote server) and in *which tools* the model gets. Choosing wrong means asking for `recall` and getting nothing, so this lesson is about the decision table first and the switch second.
**Demo:** `demos/9.1-backends.md` — enabling `mnemopi` in the lab repo, then `/memory stats` and `/memory view`.
**Concepts:**
- `memory.backend` — enum `off | local | hindsight | mnemopi | sharpshooter`, default **`off`** (`omp config get memory.backend` → `off`). Three ways to select:
  - `/settings` panel inside a session (writes the global file);
  - `omp config set memory.backend <value>` — writes the **global** `~/.omp/agent/config.yml`; `omp config reset memory.backend` removes it;
  - by hand in `<repo>/.omp/config.yml` — the only way to scope it to one project (settings commands never write arbitrary project keys). `omp config get` run *from inside the repo* reports the merged value.
  The backend is opened and the memory tools registered when a session starts; after changing the setting, start a new `omp` process (this module's exercises assume a restart, not just `/new`).
- **Decision guide** — pick by what you need *today*:

  | You want… | Pick | Because |
  |---|---|---|
  | "Remember X" / "what do you remember?" working in the same afternoon, no server | `mnemopi` | explicit tools (`retain`/`recall`/`reflect`/`memory_edit`), local SQLite, immediate |
  | A curated `MEMORY.md` you can read and edit like a doc, built from past sessions overnight | `local` | file artifacts, startup consolidation, `memory://root/…` readable; no explicit tools |
  | Team-shared memory on a server, with mental models | `hindsight` | remote bank; `recall`/`retain`/`reflect`; no `memory_edit` |
  | Nothing stored anywhere | `off` (default) | — |

- **`local`** — a background pipeline runs at **startup**, reads *past* persisted sessions of this project, and writes into `~/.omp/agent/memories/<encoded-cwd>/`:
  - `MEMORY.md` — curated long-term document;
  - `memory_summary.md` — the compact text injected at session start (this is what `memory://root` returns);
  - `skills/<name>/SKILL.md` — generated procedural playbooks (stale ones are pruned on the next run);
  - `learned.md` — written by `learn` (Lesson 9.3), *never overwritten* by consolidation.

  Phase 1 extracts per session with the `default` model role; Phase 2 consolidates with `smol` (falls back to `default`, then the active model). Output is secret-redacted before writing. Sessions are skipped when too recent, too old, active, or a subagent/non-persisted session. **No `retain`/`recall`/`reflect`/`memory_edit`** on this backend. Timing knobs that decide whether you will ever see output:

  | Key | Default | Effect |
  |---|---|---|
  | `memories.minRolloutIdleHours` | `12` | sessions active more recently are skipped → today's work shows up tomorrow |
  | `memories.maxRolloutAgeDays` | `30` | older sessions are ignored |
  | `memories.maxRolloutsPerStartup` | `64` | cap per startup |
  | `memories.threadScanLimit` | `300` | recent session records scanned |
  | `memories.summaryInjectionTokenLimit` | `5000` | shared cap for summary + lessons injected |

- **`mnemopi`** — local SQLite under the agent memories directory: `~/.omp/agent/memories/mnemopi/mnemopi.db`, with project banks as sibling database files. Exposes `recall`, `retain`, `reflect`, `memory_edit` (+ `learn` with autolearn).
  - `mnemopi.scoping` default **`per-project`** (bank derived from the cwd basename + a stable hash of its absolute path — so `omp-course-lab/` and `omp-course-lab/api/` are *different* banks); `global` = one shared bank; `per-project-tagged` = write project-local, recall project + global (duplicates merged).
  - `mnemopi.autoRecall: true` → the first model turn gets a `<memories>` block (query composed from up to `mnemopi.recallContextTurns` = 3 prior turns, ≤ `mnemopi.recallMaxQueryChars` = 4000 chars, ≤ `mnemopi.recallLimit` = 8 hits, ≤ `mnemopi.injectionTokenLimit` = 5000 tokens).
  - `mnemopi.autoRetain: true` → completed turns are stored as *episodes* no more often than every `mnemopi.retainEveryNTurns` (4) user turns.
  - LLM work (fact extraction, consolidation) uses `mnemopi.llmMode: smol` — resolves the `tiny` role, then `smol`; `remote` uses `mnemopi.llmBaseUrl/llmApiKey/llmModel`; `none` disables LLM calls. If no model or credential resolves, Mnemopi continues without LLM-backed work.
  - Embeddings default to the local `BAAI/bge-base-en-v1.5` (`mnemopi.embeddingVariant: en`); `mnemopi.noEmbeddings: true` forces FTS-only recall; `mnemopi.embeddingModel/embeddingApiUrl/embeddingApiKey` select an OpenAI-compatible endpoint instead.
  - Startup is best-effort: if the DB or models fail to initialise, the session continues with Mnemopi inert and the tools report `Mnemopi backend is not initialised for this session.`
- **`hindsight`** — remote server (default `hindsight.apiUrl: http://localhost:8888`, `hindsight.apiToken`; `HINDSIGHT_*` env vars override). Exposes `recall`, `retain`, `reflect`; **no `memory_edit`** (upstream memories are not edited through this backend). Default scoping `per-project-tagged` (project label = lowercased basename of the repository's primary checkout root, so every worktree of one repo shares a scope). `/memory clear` drains pending retains and clears only local state — the server-side bank survives. Also `/memory mm …` mental-model maintenance. Not exercised in this course (needs a server).
- **`sharpshooter`** — listed in `omp://memory.md` as "friction-gated project decision files (architecture/product/style), consolidated in the background"; tuning keys `sharpshooter.intervalMinutes` (5), `sharpshooter.injectionTokenLimit` (15000), `sharpshooter.model`. No further guide is bundled; not covered here.
- **What gets injected.** `local`: a **Memory Guidance** block (summary + learned lessons, shared cap `memories.summaryInjectionTokenLimit` = 5000 tokens). `mnemopi`/`hindsight`: a `<memories>` block on the first turn, refreshed by auto-recall; recalled memory is also offered as extra context during compaction (M5). In every case the docs are explicit: memory is **heuristic** context — prefer repo state and the user's instruction when they conflict; treat conflicting memory as stale; cite the memory artifact when it changes the plan and pair it with current-repo evidence.
- **`memory://` URLs** for the `read` tool:

  | URL | Backend | Returns |
  |---|---|---|
  | `memory://root` | `local` | `memory_summary.md` (the startup injection) |
  | `memory://root/MEMORY.md` | `local` | full long-term document |
  | `memory://root/learned.md` | `local` | lessons captured by `learn` |
  | `memory://root/skills/<name>/SKILL.md` | `local` | a generated playbook (`memory://root/...` also works as a `glob` pattern) |
  | `memory://<memory-id>` | `mnemopi` | the full row — working or episodic — behind YAML frontmatter (`id`, `bank`, `store`, `memory_type`, `source`, timestamps, `importance`, `veracity`, `session_id`, `metadata`); only the calling session's scoped banks |

  Under `mnemopi` the `root` form does not resolve; under `hindsight` the id form returns a corrective pointer. These URLs are session-side: the shell `omp read memory://…` reports `Unknown protocol: memory://`.
- **`/memory` subcommands:** `view` (current injection payload) · `stats` (backend statistics) · `diagnose` · `queue` (pending deltas awaiting consolidation) · `sync` (run consolidation now) · `clear`/`reset` (delete active backend data; Mnemopi: every scoped DB + WAL/SHM) · `enqueue`/`rebuild` (force consolidation/retention; Mnemopi: retains the current session, flushes extraction, runs sleep/consolidation for rows older than 12 h; local: marks work for the next startup) · `mm …` (Hindsight only; unsupported in ACP mode).
- **How the tools render.** `retain`/`recall`/`reflect`/`memory_edit` are *discoverable* tools. With `tools.xdev` (observed `true` on 18.3.1) they may be presented as devices — the card can read `write xd://recall` instead of a top-level `recall` card, and `read xd://` lists the mounted devices. Passing `--tools=recall,retain,reflect` keeps them top-level. Either rendering is the same tool.
- **Approval.** `recall`, `reflect` and `memory_edit` declare `approval = "read"`, so they never prompt in any approval mode (Module 4), even though `memory_edit` writes to disk. `retain` is `read` too, except a call with a `scope: "global"` item is `write` (that option is only offered under `global`/`per-project-tagged` scoping — never under the default `per-project`).
- **Subagents (M10 preview).** They alias the parent's memory state for explicit `recall`/`retain`/`reflect` calls but run no auto-recall/auto-retain loops of their own; the `local` pipeline skips them entirely.

**Try it (Walkthrough):**
1. In a shell, from `omp-course-lab/`: `omp config get memory.backend`, `omp config get mnemopi.scoping`.
   Expected: `off` and `per-project`.
2. Create `omp-course-lab/.omp/config.yml` (or append to it) with:
   ```yaml
   memory:
     backend: mnemopi
   mnemopi:
     scoping: per-project
   ```
   Then re-run `omp config get memory.backend` from inside the repo.
   Expected: `mnemopi`. (Alternative, global: `omp config set memory.backend mnemopi` — this writes `~/.omp/agent/config.yml` and applies to every project.)
3. Start `omp` in the repo and type `/memory stats`.
   Expected: Mnemopi bank statistics (bank name derived from `omp-course-lab` + hash). If instead you see that the backend is not initialised, see Troubleshooting.
4. `/memory view`.
   Expected: the current injection payload — empty or near-empty on a first run, because nothing has been retained yet.
5. Ask: `read xd:// and tell me which memory-related devices are mounted` (or, if `tools.xdev` is off, simply `which memory tools do you have?`).
   Expected: the answer names `recall`, `retain`, `reflect`, `memory_edit`. If `learn` is missing, that is correct — it needs `autolearn.enabled` (Lesson 9.3).
6. `ls ~/.omp/agent/memories/`.
   Expected: a `mnemopi/` directory holding `mnemopi.db` (the backend opens its SQLite databases when a session starts with it active; project banks are sibling files).

**Guided task:** *Goal:* prove the backend/tool matrix to yourself. *Hints:* flip `memory.backend` between `local` and `mnemopi` in the project `.omp/config.yml`, restart omp each time, and ask omp "which of retain, recall, reflect, memory_edit can you call right now?". Also ask it to `read memory://root` under each. *Checkpoints:* (a) under `local` the four tools are absent and `memory://root` either reads `memory_summary.md` or reports that no summary exists yet; (b) under `mnemopi` the four tools are present and `memory://root` does not resolve. *Pass condition:* your notes for (a) and (b) match the table at the top of this README.

**Stretch:** *Goal:* switch `mnemopi.scoping` to `per-project-tagged` and explain in one sentence what changes for `recall` versus `retain`. *Pass condition:* your sentence says writes stay in the project bank while recall also reads the shared global bank (compare `omp://mnemosyne-memory-backend.md` § Scoping).

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `omp config get memory.backend` still prints `off` after editing `.omp/config.yml` | You ran it outside the repo, or the file is not under `<repo>/.omp/` | `cd omp-course-lab` first; the project layer loads only when the cwd has a non-empty `.omp/` |
| Memory tool says `Mnemopi backend is not initialised for this session.` | Backend startup failed (DB or embedding/LLM model init) and the session continued inert | `/memory diagnose`; try `mnemopi.noEmbeddings: true` (FTS-only) and/or `mnemopi.llmMode: none`; restart |
| `read memory://root` fails under `mnemopi` | The file-backed root exists only with `memory.backend: local` | Use `recall`/`reflect`, or `read memory://<id>` for a specific row |
| Shell `omp read memory://root` → `Unknown protocol: memory://` | `memory://` is resolved inside a session, not by the CLI reader | Ask omp to `read memory://…` in-session |
| I set `memory.backend: local` but no `MEMORY.md` ever appears | Consolidation only processes sessions idle ≥ 12 h and ≤ 30 days old, at the *next* startup | Come back tomorrow; `/memory enqueue` marks work for the next startup, `/memory sync` runs it now |
| `learn` is missing even though memory is on | `learn` also needs `autolearn.enabled: true` | Lesson 9.3 |

**Cheat sheet:**

| Item | Value |
|---|---|
| Check | `omp config get memory.backend` (from inside the repo) |
| Enable (project) | `<repo>/.omp/config.yml` → `memory:\n  backend: mnemopi` |
| Enable (global) | `omp config set memory.backend mnemopi` → `~/.omp/agent/config.yml` |
| Revert (global) | `omp config reset memory.backend` |
| Inspect | `/memory view` · `/memory stats` · `/memory diagnose` · `/memory queue` |
| Force work | `/memory enqueue` (Mnemopi: retain now + flush + consolidate rows > 12 h) · `/memory sync` |
| Wipe | `/memory clear` (Mnemopi: deletes every scoped DB) |
| Files | local: `~/.omp/agent/memories/<encoded-cwd>/{MEMORY.md,memory_summary.md,learned.md,skills/}` · mnemopi: `~/.omp/agent/memories/mnemopi/mnemopi.db` |

**Source:** omp://memory.md, omp://mnemosyne-memory-backend.md, omp://settings.md, omp://config-usage.md, omp://tools/read.md, omp://tools/retain.md, omp://approval-mode.md

---

## Lesson 9.2 — Explicit memory tools              (~15 min)
**You will be able to:** make omp store a fact with `retain`, find it again with `recall`, answer from memory with `reflect`, and correct or retire it with `memory_edit` — and read each card correctly.
**Why this exists:** Auto-retain stores whole conversation turns as low-importance *episodes* every few turns. That is a safety net, not a knowledge base: it fires late, it keeps chatter, and it never knows which one sentence mattered. The four explicit tools let you (through the model) write *facts* on purpose, query them, and fix them when they go stale. The failure mode this prevents is the confident-but-wrong memory: a recalled preview is clipped at 500 characters, and `memory_edit update` replaces content wholesale, so the docs require a full-row read before any update. Knowing that rule is most of what this lesson teaches.
**Demo:** `demos/9.2-memory-tools.md` — retain → `/new` → recall → reflect → memory_edit.
**Concepts:** (all require `memory.backend: mnemopi` or `hindsight`; `memory_edit` is `mnemopi` only)
- **`retain({ items: [{ content, context? }] })`** — one or more self-contained memories. Mnemopi result text: `1 memory stored.` / `N memories stored.` (stored as `memoryType: fact`, `importance: 0.75`, `source: coding-agent-retain`; exact duplicate content in the same session updates the existing row). Hindsight: `N memories queued.` — the write happens on a later flush. Neither response is a per-item durability receipt.
- **`recall({ query })`** — natural-language search; result `Found <n> relevant memory/memories (as of YYYY-MM-DD HH:MM UTC):` then Mnemopi bullets `- <content> (id: <id>) [<source>] (<YYYY-MM-DD>) c:<score>`; or `No relevant memories found.` Content is a **preview capped at 500 chars**; a clipped preview ends in `…`. Explicit `recall` does not refresh the `<memories>` block that auto-recall injected. At most `mnemopi.recallLimit` (8) hits.
- **`reflect({ query, context? })`** — Mnemopi: a scoped recall, formatted as `Based on recalled memories:` + context — *no synthesis model runs*, so the answer can be raw recalled context. Hindsight: the server synthesises text. Either way, `No relevant information found to reflect on.` when nothing matches.
- **`memory_edit({ op, id, content?, importance?, replacement_id? })`** — `op` ∈ `update | forget | invalidate`; `id` comes from a `recall` bullet. `update` replaces text and/or importance (clamped 0..1) **wholesale**; `forget` hard-deletes a working-memory row; `invalidate` soft-supersedes a working *or* episodic row (optionally recording `replacement_id`). Fact-table rows are read-only → `not_editable`; `update`/`forget` on an episodic id → `not_found`. Result: `Memory <id> updated|deleted|invalidated in bank <bank> (<store>).`
- **Rule: read before update.** `read memory://<id>` returns the full row behind YAML frontmatter. Do it before every `update`; copying a clipped preview into `content` deletes the unseen tail. Prefer `invalidate` over `forget` when history may still be useful.
- **Prompt phrasing that tends to trigger each tool** (the model chooses; these are the natural cues, not guarantees):

  | You say | Tool the model reaches for | What you get back |
  |---|---|---|
  | "Remember that …", "Store this for future sessions: …", "Keep a note that …" | `retain` | `1 memory stored.` / `N memories stored.` |
  | "What do you remember about …?", "Have we hit this before?", "Search your memory for …" | `recall` | bullet list with ids |
  | "Based on what you remember about this repo, how should I …?" (needs an *answer*, not a list) | `reflect` | `Based on recalled memories:` + context |
  | "That memory is wrong — update it to say …" | `read memory://<id>` then `memory_edit update` | `Memory <id> updated …` |
  | "Mark the memory about X as outdated; Y replaces it" | `memory_edit invalidate` (+ `replacement_id`) | `Memory <id> invalidated …` |
  | "Forget the memory about …" | `memory_edit forget` | `Memory <id> deleted …` |

- **Where a memory comes from decides what it is.** Three writers feed the same scoped bank with different metadata, and `memory_edit`'s rules depend on the *store* a row sits in:

  | Writer | `memory_type` | `importance` | `veracity` | `source` |
  |---|---|---|---|---|
  | `retain` tool | `fact` | `0.75` | `tool` | `coding-agent-retain` |
  | `learn` tool (Lesson 9.3) | `fact` | `0.8` | `tool` | `coding-agent-learn` |
  | auto-retain (every 4 user turns) | `episode` | `0.65` | `unknown` | `coding-agent-transcript` |

  New rows land in the **working** store. Mnemopi's sleep/consolidation (run by `/memory enqueue`, and only for unconsolidated working rows older than half the 24-hour working-memory TTL = 12 h) promotes eligible rows; normal shutdown never does. Every row reports its store — `working`, `episodic`, or `fact` — in `memory://<id>` frontmatter and in `memory_edit` results. `update`/`forget` work on working rows only; `invalidate` works on working *and* episodic rows; fact-table rows are read-only. This is why an id that `recall` showed you yesterday may answer `not_found` to `update` today — use `invalidate`.
- **Auto vs explicit.** `mnemopi.autoRecall` (first turn, `<memories>` block) and `mnemopi.autoRetain` (episodes) run without you asking. Explicit tool calls are per-session work on the same scoped bank; an explicit `recall` does not rewrite the injected `<memories>` block. Subagents alias the parent state for explicit calls but run no auto loops of their own.
- **Durability.** Normal exit gives the retain/flush drain 1.5 s and does not promote fresh rows; already-written working rows are durable. `/memory enqueue` is the strong boundary: forces retention of the current session, flushes pending extraction, consolidates rows older than 12 h.
- **Approval:** `recall`/`reflect`/`memory_edit` are `approval = "read"`; `retain` is `read` unless an item carries `scope: "global"` (then `write`). Under `per-project` scoping nothing here ever prompts.

**Try it (Walkthrough):** (backend `mnemopi` from Lesson 9.1; cwd `omp-course-lab/`)
1. `remember that this repo's tests copy data/lab.sqlite to a temp file and point DATABASE_URL at the copy (tests/support.py, class TempDB)`
   Expected: a `retain` card (or `write xd://retain`) whose result reads `1 memory stored.`
2. `/new`
   Expected: an empty conversation, same project, same bank.
3. `how do the tests in this repo pick their database?`
   Expected: a `recall` and/or `reflect` card; the result bullet contains `DATABASE_URL` and an `(id: …)`; the answer repeats the fact. Note the id.
4. `read memory://<that id>`
   Expected: a `read` card with YAML frontmatter (`id`, `bank`, `store`, `memory_type: fact`, `importance: 0.75`, `source: coding-agent-retain`) and the full content.
5. `that memory should also say that the sqlite:/// URL form from .env.example only works once issue #6 is fixed in api/db.py — before that, only a plain path works. Update it.`
   Expected: the model re-reads `memory://<id>` (or uses the full row it already has), then a `memory_edit` card with `op: update` and result `Memory <id> updated in bank <bank> (working).`
6. `/memory stats`
   Expected: bank statistics reflecting at least one stored memory.

**Guided task:** *Goal:* store three facts about the lab in one `retain` call, then answer a question that needs two of them via `reflect`. *Hints:* phrase the ask as "remember these three things: …" so the model sends one `items` array; then `/new`; then a question whose answer needs two facts. *Checkpoints:* result `3 memories stored.`; the `reflect` result starts with `Based on recalled memories:`; both needed facts appear in it. *Pass condition:* the assistant's final answer states both facts and cites memory as the source.

**Stretch:** *Goal:* retire a fact the right way. Retain a deliberately wrong fact, then have omp `invalidate` it and record the corrected memory as its replacement. *Pass condition:* `memory_edit` result reads `… invalidated …`, and a subsequent `recall` for the topic surfaces the correct memory (compare the ids).

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `No relevant memories found.` right after retaining | Different bank: cwd changed (per-project scoping hashes the absolute cwd) or scoping changed | Stay in the same directory; check `omp config get mnemopi.scoping` |
| Recall works but the answer ignores it | Recalled memory is background context; the model prefers current repo evidence | Ask explicitly: "use your memory of …" |
| The card says `write xd://retain` instead of `retain` | `tools.xdev` presents discoverable tools as devices | Same tool; or start with `--tools=recall,retain,reflect,memory_edit` |
| `memory_edit` returns `not_editable` | The id is a fact-table row (read-only) | Read it with `memory://<id>`; retain a new corrected fact instead |
| `memory_edit update` returns `not_found` for an id `recall` just showed | The row is episodic; `update`/`forget` only support working memory | Use `invalidate` (works on episodic rows) |
| `memory_edit update requires content or importance.` | Empty update | Supply `content` and/or `importance` |
| Memory vanished after restarting | Normal exit only gets a 1.5 s drain; heavy write in flight was cut | Run `/memory enqueue` before quitting |
| Nothing found although the text matches exactly | Embedding path not initialised | `mnemopi.noEmbeddings: true` → FTS-only; restart |

**Cheat sheet:**

| Tool | Input | Result text (Mnemopi) |
|---|---|---|
| `retain` | `items:[{content, context?}]` | `N memory/memories stored.` |
| `recall` | `query` | `Found n relevant memory… \n- <content> (id: <id>) [<source>] (<date>) c:<score>` / `No relevant memories found.` |
| `reflect` | `query`, `context?` | `Based on recalled memories:\n\n…` / `No relevant information found to reflect on.` |
| `memory_edit` | `op` update/forget/invalidate, `id`, `content?`, `importance?`, `replacement_id?` | `Memory <id> updated/deleted/invalidated in bank <bank> (<store>).` |
| `read memory://<id>` | — | full row + YAML frontmatter; **required before `update`** |

**Source:** omp://tools/retain.md, omp://tools/recall.md, omp://tools/reflect.md, omp://tools/memory_edit.md, omp://mnemosyne-memory-backend.md, omp://tools/read.md

---

## Lesson 9.3 — Learn & managed skills              (~15 min)
**You will be able to:** enable autolearn; capture a lesson with `learn`; promote a repeatable procedure to a managed skill with `learn.skill` or `manage_skill`; find it again next session via `skill://` and `/skill:`.
**Why this exists:** Memory stores *facts*; a skill stores a *procedure*. When you finally understand why a misleading error appears and what the three-step fix is, you want both: a one-line lesson so the model never falls for it again, and a playbook it can read on demand. omp separates the two on purpose. Lessons go to memory (any backend). Procedures go to *managed skills* — an isolated directory the model may write to, ranked dead-last in skill discovery so it can never shadow a skill you authored. That isolation is the point: the model may teach itself, but it cannot overwrite your instructions.
**Demo:** `demos/9.3-learn-skill.md` — solving fixture #6, then `learn` + managed skill, then reading it in a new session.
**Concepts:**
- **`autolearn.enabled`** (default `false`). Turning it on registers **`manage_skill`** regardless of backend, and **`learn`** only when `memory.backend` is `local`, `mnemopi`, or `hindsight`. Both are `loadMode = "essential"` — always top-level, never `xd://`. It also arms a *nudge*: after a turn that used ≥ `autolearn.minToolCalls` (5) tools, omp reminds the model to capture lessons. With `autolearn.autoContinue: false` (default) the reminder rides your next turn; `true` spends tokens on an extra capture turn at stop.
- **`learn({ memory, context?, skill? })`** — stores the lesson **first**, then optionally writes a skill. Per backend: `local` → normalises and appends to `~/.omp/agent/memories/<encoded-cwd>/learned.md` (newest-first, deduplicated, secret-redacted, ≤ 100 bullets, `memory` ≤ 2,000 chars, `context` ≤ 400) — injected starting with the **next** session, so the current prompt-cache prefix is untouched; `mnemopi` → a `fact` row, `importance 0.8`, `source: coding-agent-learn`; `hindsight` → queued. Result: `Lesson stored.` / `Lesson queued for retention.`, plus `Created managed skill "<name>".` when `skill` is given. `skill = { action: create|update, name, description, body }` (body is Markdown **without** frontmatter). Approval is dynamic: `write` if `skill` is present, if an item has `scope: "global"` (Mnemopi `global`/`per-project-tagged` scoping only), or if the backend is `local`; otherwise `read`.
- **`manage_skill({ action, name, description?, body? })`** — `create` (exclusive; fails if it exists), `update` (must exist), `delete`. `approval = "write"`. Unlike `learn`, it **refreshes the active skill list immediately**, so the running session can use the skill.
- **Where managed skills live:** `~/.omp/agent/managed-skills/<name>/SKILL.md` (default agent dir; a `--profile` moves it). Name is trimmed, lowercased, must match `[a-z0-9][a-z0-9-]{0,63}`; description collapsed to one line; whole file ≤ 64,000 bytes; frontmatter (`name`, `description`) is generated for you.

  What the tool writes (you supply `name`, `description`, `body`; the frontmatter is generated):

  ```markdown
  ---
  name: lab-issue-6-misleading-error
  description: Diagnose the misleading 'database is locked' error in omp-course-lab
  ---
  ## When python3 -m cli says 'database is locked'
  1. Do not look for locks, WAL files or a running server.
  2. Print DATABASE_URL; a sqlite:/// prefix or a missing file is the cause.
  3. Fix api/db.py db_path()/connect(); re-run LAB_ISSUE=6 python3 -m unittest tests.test_issues.
  ```

  Rejections you can hit: `Invalid skill name "…"`, `Managed skill "<name>" needs a non-empty description.`, `… needs a non-empty body.`, `Managed skill is <bytes> bytes; the limit is 64000.`, plus symlink/hard-link safety errors on `update`.
- **The autolearn nudge, end to end.** Turn ends → if it used ≥ `autolearn.minToolCalls` tools, omp queues a reminder → with `autoContinue: false` the reminder rides your *next* prompt (no extra tokens until you send one); with `true`, omp runs one capture turn immediately → the model decides whether anything is worth a `learn` (memory-only) or `learn` + `skill` / `manage_skill` (procedure) → skills land in `managed-skills/`, lessons in the backend. You stay in control: with `autoContinue` off, nothing is written until you send another turn, and you can say "don't capture anything".
- **How they surface next session:** skill discovery runs the `omp-managed` provider (priority 5, dead-last) **unconditionally** — even with autolearn off — so the skill appears in the system prompt's skill list, is readable with `read skill://<name>`, and gets a `/skill:<name>` command when `skills.enableSkillCommands` is on. A same-named *authored* skill (`<repo>/.omp/skills/<name>/SKILL.md`, `~/.omp/agent/skills/<name>/SKILL.md`, plugin skills, or any other higher-priority provider) always wins; `learn`/`manage_skill create` against such a name returns an error with `shadowed: true` and writes nothing. Note the two user-level directories: `~/.omp/agent/skills/` is *yours* (authored, native provider, priority 100); `~/.omp/agent/managed-skills/` is the *model's* (managed, priority 5).
- **Do not confuse with "Memory Guidance".** That block is the `local` backend's injected `memory_summary.md` + `learned.md` lessons. Managed skills are not part of it; they arrive through skill discovery. With `mnemopi`, lessons arrive through `<memories>`/recall instead.
- **When to use which:** fact → `learn` without `skill` (or plain `retain`); repeatable multi-step procedure → `learn` with `skill` (lesson + playbook in one call) or `manage_skill` when you want it usable *now*. Docs: use `learn` sparingly — one precise lesson beats several vague ones.

**Try it (Walkthrough):** (backend `mnemopi` from 9.1; cwd `omp-course-lab/`)
1. Add to `omp-course-lab/.omp/config.yml`:
   ```yaml
   autolearn:
     enabled: true
   ```
   Restart omp; `omp config get autolearn.enabled` from the repo → `true`.
   Expected: on the next prompt the model can call `learn` and `manage_skill` (ask "which learning/skill tools do you have?" if unsure).
2. Reproduce issue #6: `DATABASE_URL=sqlite:///data/lab.sqlite python3 -m cli users 1` → `error: database is locked (is another process using data/lab.sqlite?)` (exit 2). Then work it with omp until the root cause is clear: nothing is locked — `api/db.py::db_path()` hands the whole `sqlite:///…` string to `sqlite3.connect`, and `connect()` swallows the real `OperationalError` and raises the invented "locked" message.
   Expected: a fix in `api/db.py` (`db_path`, `connect`) so that `LAB_ISSUE=6 python3 -m unittest tests.test_issues` passes, plus a one-sentence explanation of why the message misleads.
3. `learn this as one durable lesson: in omp-course-lab, "database is locked" from python3 -m cli is invented by api/db.py connect(); the real cause is DATABASE_URL being passed to sqlite3.connect unchanged, so check the DATABASE_URL value (sqlite:/// prefix, missing file) before hunting for locks.`
   Expected: a `learn` card with `memory` filled and no `skill`; result `Lesson stored.`
4. `now turn the diagnosis steps into a managed skill named lab-misleading-error with a one-line description and a numbered procedure`
   Expected: a `manage_skill` card (`action: create`) with result `Created managed skill "lab-misleading-error" (managed-skills/lab-misleading-error/SKILL.md).`
5. Shell: `cat ~/.omp/agent/managed-skills/lab-misleading-error/SKILL.md`
   Expected: generated frontmatter with `name:` and `description:` followed by the body you asked for.
6. `/new`, then `read skill://lab-misleading-error and summarise it in one line`.
   Expected: the `read` card returns the SKILL.md body; the summary matches. Try typing `/skill:lab-` — autocomplete offers the managed skill.

**Guided task:** *Goal:* do the same with a single `learn` call that carries `skill.action: create`. *Hints:* say "learn the lesson and, in the same call, create a managed skill called …"; because `learn` does not refresh skills, you must `/new` (or restart) before `skill://` sees it. *Checkpoints:* result text contains both `Lesson stored.` and `Created managed skill`; the file exists on disk immediately; `read skill://<name>` works only after `/new`. *Pass condition:* `~/.omp/agent/managed-skills/<name>/SKILL.md` exists and a fresh session reads it.

**Stretch:** *Goal:* observe shadowing. Create an authored skill `omp-course-lab/.omp/skills/lab-misleading-error/SKILL.md` (with `description` frontmatter), restart, and ask omp to `manage_skill create` the same name. *Pass condition:* the tool result is an error with `shadowed: true`; `read skill://lab-misleading-error` returns the *authored* file; deleting the authored copy and restarting brings the managed one back.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| No `learn` tool although autolearn is on | `memory.backend` is `off` | `learn` needs `local`/`mnemopi`/`hindsight`; `manage_skill` alone works with `off` |
| `Invalid skill name "…"` | After trim + lowercase the name still contains characters outside `[a-z0-9-]` (e.g. `_`, spaces), starts with `-`, or is > 64 chars | Use `[a-z0-9][a-z0-9-]{0,63}` (uppercase is folded, not rejected) |
| `Managed skill "<name>" needs a non-empty body.` | Body trimmed to empty | Provide Markdown body without frontmatter |
| Created via `learn`, but `skill://<name>` says not found in the same session | `learn` writes for a later discovery refresh | `/new` or restart; or use `manage_skill` (refreshes immediately) |
| `create` fails: file already exists | Exclusive-create semantics | Use `update` |
| Lesson stored but skill error `… could not be written: …` | Skill validation/size failed after the lesson persisted | Fix the name/body and `manage_skill create`; do not re-learn (dedup on `local`, duplicate row on `mnemopi`) |
| The nudge never appears | Turn used fewer than `autolearn.minToolCalls` (5) tools | Lower the setting or ask for `learn` explicitly |
| `learn` asks for approval in `write` mode when others didn't | `learn` is `approval = "write"` with `skill` or on `local` | Expected; approve it |

**Cheat sheet:**

| Item | Value |
|---|---|
| Enable | `autolearn.enabled: true` (+ a backend for `learn`) |
| Nudge knobs | `autolearn.autoContinue` (false) · `autolearn.minToolCalls` (5) |
| `learn` | `memory`, `context?`, `skill?{action,name,description,body}` → `Lesson stored.` [+ `Created managed skill "…"`] |
| `manage_skill` | `action` create/update/delete, `name`, `description`, `body` → `Created managed skill "<n>" (managed-skills/<n>/SKILL.md).` |
| Path | `~/.omp/agent/managed-skills/<name>/SKILL.md` |
| Read back | `read skill://<name>` · `/skill:<name>` |
| Local lessons | `~/.omp/agent/memories/<encoded-cwd>/learned.md` · `read memory://root/learned.md` |
| Precedence | authored skill > managed skill (always) |

**Source:** omp://tools/learn.md, omp://tools/manage_skill.md, omp://skills.md, omp://memory.md, omp://settings.md

---

## Lesson 9.4 — Scoped exploration pruning: checkpoint & rewind              (~15 min)
**You will be able to:** enable `checkpoint.enabled`; ask omp to fence a long investigation with `checkpoint({goal})`; read the `rewind({report})` card; confirm that context usage dropped while the report stayed.
**Why this exists:** A deep investigation reads dozens of files, runs tests, and chases dead ends — and every byte of that stays in context afterwards, crowding out the work you actually wanted. Module 5's compaction fixes this reactively and globally: when the window fills, *everything old* is summarised by a model. `checkpoint`/`rewind` is the surgical version: the model marks a boundary before it starts digging, and when it is done it replaces the whole excursion with a report *it wrote itself*. The transcript branches at the boundary; the exploration stays on disk but leaves the active branch; the next provider call sees only the report. This is a session-tree operation only — no git, no file, no artifact restore.
**Demo:** `demos/9.4-checkpoint-rewind.md` — issue #7 investigation with checkpoint → rewind, before/after `context_pct`.
**Concepts:**
- **`checkpoint.enabled`** (default `false`) registers both tools for the top-level session. Subagents get them only through an explicit `tools:` list, and requesting either name auto-includes the other. Both are `approval = "read"`, `loadMode = "discoverable"` (may render as `xd://checkpoint` under `tools.xdev`).
- **`checkpoint({ goal })`** → text `Checkpoint created.` / `Goal: <goal>` / `Run your investigation, then call rewind with a concise report.`; `details: { goal, startedAt }`. No id, no restore token. Only one active checkpoint per session: a second call throws `Checkpoint already active.` Despite its summary string mentioning git, it **does not touch git or the filesystem** — it records the current message count and the last persisted session-entry id.
- **The guard.** While a checkpoint is active and no rewind report is pending, an attempt to end the turn injects a developer-role `<system-warning>` ("You are in an active checkpoint. You MUST call rewind …") and schedules another turn.
- **`rewind({ report })`** → text `Rewind requested.` / `Report captured for context replacement.`; `details: { report, rewound: true }`. Empty report → `Report cannot be empty.`; no checkpoint → `No active checkpoint. Create a checkpoint before calling rewind.`; already done → `Checkpoint already completed; continue from the retained rewind report instead of calling rewind again.`
- **What actually happens (at `turn_end`, not when the card appears):** the session branches at the checkpoint entry with a `branch_summary` (the report), appends a hidden `rewind-report` custom message (developer-role guidance + the report for the next turn), rebuilds the in-memory messages from the new branch, resets advisor state (cost preserved), resyncs todos, and closes provider sessions whose history was rewritten. The abandoned entries remain in the `.jsonl` file; if the checkpoint entry cannot be found the rewind branches from root and logs a warning.
- **Observing it:** the status line's `context_pct` segment (in the default `statusLine.rightSegments`) drops after the turn ends; `/tree` shows the branch point, and with `Alt+A` (all entries) you can search `rewind` to find the `custom` bookkeeping entry; the `branch_summary` renders as a `<summary>` block in compaction context.
- **Resume-safe.** On `/resume`, session switch, or `/tree` navigation, an unfinished checkpoint (successful `checkpoint` result with no later report on the active branch) is rehydrated, so `rewind` still works after a restart.
- **What the session tree looks like** before and after — the abandoned entries stay in the `.jsonl` and remain visible in `/tree`; only the *active branch* changes:

  ```mermaid
  graph TD
    U1[user: investigate #7 with a checkpoint] --> C[assistant: checkpoint ✓  ← branch point]
    C --> X1[read/grep/bash …]
    X1 --> X2[… dozens of exploratory cards …]
    X2 --> R[assistant: rewind ✓]
    C --> BS[branch_summary: the report]
    BS --> RR[custom: rewind-report]
    RR --> U2[user: what was the red herring?]
    style X1 fill:#eee,stroke:#999,color:#666
    style X2 fill:#eee,stroke:#999,color:#666
    style R fill:#eee,stroke:#999,color:#666
  ```

  After `turn_end` the leaf sits at `rewind-report`; the next provider call is built from `U1 → C → BS → RR`, not from the shaded exploratory path.
- **Versus the other ways to shrink context** (M5):

  | | Compaction (`/compact`, auto) | `checkpoint` → `rewind` | `/tree` → `Summarize` |
  |---|---|---|---|
  | Who decides *when* | thresholds (`compaction.thresholdPercent/Tokens`, reserve) or you (`/compact`) | the agent, at a boundary it declared before exploring | you, by hand |
  | What is summarised | everything older than `keepRecentTokens`, across the whole conversation | exactly the entries after the checkpoint | the abandoned branch between old and new leaf |
  | Who writes the summary | a model, via `compaction.methodOrder` (`remote, snapcompact, handoff, shake, soft`) | the working agent, in `report` | a model (`branchSummary.enabled` prompt) |
  | Persisted as | `compaction` entry | `branch_summary` + hidden `rewind-report` custom message | `branch_summary` |
  | Needs a setting | on by default | `checkpoint.enabled: true` | `branchSummary.enabled` for the prompt; `Shift+Enter` works regardless |

  They compose: a rewind's `branch_summary` is a message-bearing entry that later compaction retains and renders as a `<summary>` block.
- **Prompt phrasing:** "Set a checkpoint with the goal '…', investigate, and when you know the answer rewind with a report containing X, Y, Z." Being explicit about what the report must contain is what makes the retained context useful.

**Try it (Walkthrough):** (cwd `omp-course-lab/`; memory backend irrelevant)
1. Add to `omp-course-lab/.omp/config.yml`:
   ```yaml
   checkpoint:
     enabled: true
   ```
   Restart omp; `omp config get checkpoint.enabled` from the repo → `true`.
   Expected: `true`.
2. Note the `context_pct` value on the status line (right side) before you begin.
   Expected: a small number on a fresh session.
3. `Set a checkpoint with the goal "find the real cause of issue #7 in docs/ISSUES.md (order_count includes cancelled orders)". Investigate thoroughly — read the code and run the tests. When you know the answer, rewind with a report that names the real cause, the red herring(s) you ruled out, and the file:line to change. Do not fix anything yet.`
   Expected: a `checkpoint` card first (`Checkpoint created.` / `Goal: …`), then many `read`/`grep`/`bash` cards, then a `rewind` card (`Rewind requested.` / `Report captured for context replacement.`), then the turn ends. The lab seeds three red herrings — the "default to 0" comment in `cli/commands.py`, the "check the seed" note in `api/server.py`, and `tools/seed_db.py` — while the real cause is one function in `api/db.py` (`count_orders`).
4. Look at `context_pct` again.
   Expected: lower than during the investigation — the exploration left the active branch.
5. `What did the investigation conclude? Quote the report.`
   Expected: the answer reproduces the report (it is in the retained `rewind-report` message); no `rewind` is called again. The report points at `api/db.py`, not at any of the three seeded red herrings. Shell check that nothing was fixed: `LAB_ISSUE=7 python3 -m unittest tests.test_issues` still fails and `git status` is clean.
6. `/tree`, press `Alt+A`, type `rewind`.
   Expected: the bookkeeping entries (`branch_summary` / `custom` `rewind-report`) at the branch point; the abandoned investigation branch is visible alongside. `Esc` to close without moving.

**Guided task:** *Goal:* trigger the guard. *Hints:* ask for a checkpoint but tell omp to "stop and report back to me in chat" instead of rewinding. *Checkpoints:* the model tries to end the turn; the session injects a developer-role `<system-warning>` about the active checkpoint (it is a message to the model, so it may not be rendered in the transcript) and schedules another turn; the model then calls `rewind`. *Pass condition:* the turn only ends after a `rewind` card — you never get a final answer without one.

**Stretch:** *Goal:* try to nest. With a checkpoint active, ask for a second checkpoint. *Pass condition:* the second call errors with `Checkpoint already active.`; a later `rewind` still succeeds and refers to the first goal.

**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| No `checkpoint` tool | `checkpoint.enabled` is `false`, or you are in a subagent | Enable; for subagents add `checkpoint` (or `rewind`) to the agent's `tools:` list |
| `No active checkpoint. Create a checkpoint before calling rewind.` | Rewind called first | Ask for the checkpoint explicitly |
| `Checkpoint already completed; continue from the retained rewind report …` | The model called `rewind` twice | Expected; continue from the report |
| Context % did not drop | Rewind is applied at `turn_end`; you looked mid-turn — or the investigation was tiny | Wait for the turn to end; use a bigger investigation |
| Files the investigation changed are still changed | Rewind restores conversation context only | Use git (`omp git`, M4) to revert files |
| `Checkpoint already active.` | One checkpoint per session | Finish it with `rewind` first |

**Cheat sheet:**

| Item | Value |
|---|---|
| Enable | `checkpoint.enabled: true` (project `.omp/config.yml` or `omp config set checkpoint.enabled true`) |
| `checkpoint` | `{ goal }` → `Checkpoint created. / Goal: … / Run your investigation, then call rewind …` |
| `rewind` | `{ report }` → `Rewind requested. / Report captured for context replacement.` (applied at turn end) |
| Persisted | `branch_summary` at the checkpoint + hidden `rewind-report` custom message; old branch stays in `.jsonl` |
| Observe | status line `context_pct` · `/tree` → `Alt+A` → search `rewind` |
| Not restored | files, git, artifacts, blobs, prompt history |
| Errors | `Checkpoint already active.` · `No active checkpoint…` · `Report cannot be empty.` · `Checkpoint already completed…` |

**Source:** omp://tools/checkpoint.md, omp://tools/rewind.md, omp://tree.md, omp://compaction.md, omp://settings.md

---

## Where next
- **Module 11** reuses `checkpoint`/`rewind` inside guardrail workflows and adds advisors on top.
- **Module 10** notes: subagents alias the parent's memory state for explicit `recall`/`retain`/`reflect` and only get `checkpoint`/`rewind`/`learn`/`manage_skill` through an explicit tools list.
