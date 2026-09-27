# Module 9 cheat sheet — Memory & Self-Authored Skills (`omp/18.3.1`)

## Gates (all off by default)

| Setting | Default | Turns on |
|---|---|---|
| `memory.backend` | `off` | `local` \| `mnemopi` \| `hindsight` \| `sharpshooter`; `/memory …`; `memory://` |
| `autolearn.enabled` | `false` | `manage_skill` (any backend) + `learn` (backend ≠ off); post-turn nudge |
| `autolearn.autoContinue` / `autolearn.minToolCalls` | `false` / `5` | auto capture turn / nudge threshold |
| `checkpoint.enabled` | `false` | `checkpoint` + `rewind` |
| `mnemopi.scoping` | `per-project` | `global` \| `per-project` \| `per-project-tagged` |
| `mnemopi.autoRecall` / `autoRetain` / `retainEveryNTurns` / `recallLimit` | `true` / `true` / `4` / `8` | first-turn `<memories>`; episode retention cadence; hits |
| `mnemopi.noEmbeddings` / `llmMode` | `false` / `smol` | FTS-only / `none` disables background LLM calls |

Check: `omp config get <key>` **from inside the repo**. Project: hand-edit `<repo>/.omp/config.yml`. Global: `omp config set <key> <v>` → `~/.omp/agent/config.yml`; undo with `omp config reset <key>`. Restart after changing gates.

## Backend → tools

| | `local` | `mnemopi` | `hindsight` |
|---|---|---|---|
| `retain` `recall` `reflect` | — | ✅ | ✅ |
| `memory_edit` | — | ✅ | — |
| `learn` (needs autolearn) | ✅ → `learned.md` | ✅ → fact 0.8 | ✅ queued |
| `memory://root[/MEMORY.md\|learned.md\|skills/<n>/SKILL.md]` | ✅ | — | — |
| `memory://<id>` | — | ✅ | pointer only |
| Storage | `~/.omp/agent/memories/<encoded-cwd>/` | `~/.omp/agent/memories/mnemopi/mnemopi.db` (+ sibling banks) | remote `hindsight.apiUrl` (default `http://localhost:8888`) |
| Injected | **Memory Guidance** block (≤ `memories.summaryInjectionTokenLimit` 5000) | `<memories>` on first turn | `<memories>` + `<mental_models>` |

`memory://` resolves only inside a session (shell `omp read memory://…` → `Unknown protocol` with the backend off, `not found in the calling session's scoped bank` with it on).

## `/memory`

`view` payload · `stats` · `diagnose` · `queue` · `sync` run consolidation now · `clear`/`reset` delete backend data (Hindsight: local state only) · `enqueue`/`rebuild` force retention + flush (+ Mnemopi consolidation of rows > 12 h) · `mm …` Hindsight mental models.

## Tool calls and result strings

| Tool | Args | Result |
|---|---|---|
| `retain` | `items:[{content, context?}]` | `N memory/memories stored.` (Mnemopi) · `… queued.` (Hindsight) |
| `recall` | `query` | `Found n relevant memory… (as of … UTC):` `- <content> (id: <id>) [<source>] (<date>) c:<score>` · `No relevant memories found.` · preview ≤ 500 chars, `…` = clipped |
| `reflect` | `query`, `context?` | Mnemopi `Based on recalled memories:` (recall + formatting) · Hindsight synthesised · `No relevant information found to reflect on.` |
| `memory_edit` | `op` update\|forget\|invalidate, `id`, `content?`, `importance?` (0..1), `replacement_id?` | `Memory <id> updated\|deleted\|invalidated in bank <b> (<store>).` · `not_found` (episodic for update/forget) · `not_editable` (fact rows) |
| `learn` | `memory`, `context?`, `skill?{action,name,description,body}` | `Lesson stored.` / `Lesson queued for retention.` [+ `Created/Updated managed skill "<n>".`] |
| `manage_skill` | `action` create\|update\|delete, `name`, `description`, `body` | `Created managed skill "<n>" (managed-skills/<n>/SKILL.md).` — refreshes skills now |
| `checkpoint` | `goal` | `Checkpoint created.` `Goal: …` `Run your investigation, then call rewind…` |
| `rewind` | `report` | `Rewind requested.` `Report captured for context replacement.` — applied at turn end |

Approval tiers: `recall` `reflect` `memory_edit` `checkpoint` `rewind` = `read` (never prompt); `retain` = `read` unless an item has `scope: "global"` (offered only under `global`/`per-project-tagged` scoping) → `write`; `manage_skill` = `write`; `learn` = `write` when `skill` given, `scope: "global"` used, or backend `local`, else `read`. Memory/checkpoint tools are *discoverable* → may render as `write xd://<tool>` under `tools.xdev`; `learn`/`manage_skill` are essential → always top-level.

## Rules worth memorising

- **Read before update:** `read memory://<id>` before any `memory_edit update` (wholesale replace; previews are clipped). Prefer `invalidate` to `forget`.
- Managed skills: `~/.omp/agent/managed-skills/<name>/SKILL.md`; name `[a-z0-9][a-z0-9-]{0,63}`; ≤ 64,000 bytes; no frontmatter in `body`; authored skill of the same name always wins (`shadowed: true`). Discovered by the `omp-managed` provider (priority 5) even when autolearn is off; read `skill://<name>`; `/skill:<name>`.
- `learn` does **not** refresh skills in the running session; `manage_skill` does. Local `learned.md`: newest-first, dedup, secret-redacted, ≤ 100 bullets, 2,000/400-char caps, injected next session.
- `local` consolidation runs at startup on sessions idle ≥ 12 h and ≤ 30 days old → `MEMORY.md`, `memory_summary.md`, `skills/`; roles `default` (extract) / `smol` (consolidate).
- Checkpoint: one active per session (`Checkpoint already active.`); yields are blocked by a `<system-warning>` until `rewind`; rewind branches the session (`branch_summary` + hidden `rewind-report`), restores **conversation only** — not files/git/artifacts. Watch `context_pct` on the status line; inspect with `/tree` → `Alt+A` → search `rewind`.
- Durability: normal exit drains 1.5 s; `/memory enqueue` is the strong boundary.
- Memory is heuristic context: repo state and the user's instruction win over a conflicting memory.

Source: omp://memory.md, omp://mnemosyne-memory-backend.md, omp://tools/{retain,recall,reflect,memory_edit,learn,manage_skill,checkpoint,rewind}.md, omp://skills.md, omp://settings.md, omp://approval-mode.md
