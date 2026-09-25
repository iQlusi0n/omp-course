# Module 5 cheat sheet — Sessions & Context (omp 18.3.1)

## Where things live
| Item | Path / key |
|---|---|
| Session file | `~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<id>.jsonl` (256-byte title slot, header, entries with `id`/`parentId`) |
| Artifacts | `<same dir>/<timestamp>_<id>/` (subagents, `btw-history/`, auto `handoff-*.md`) |
| Blobs | `~/.omp/agent/blobs/<sha256>` |
| Terminal breadcrumb | `~/.omp/agent/terminal-sessions/<terminal-id>` (cwd, session path, optional `fresh`) |
| Agent dir | `omp config path` (`PI_CODING_AGENT_DIR`, `--profile`) |

## CLI flags
| Flag | Meaning |
|---|---|
| `-c` / `--continue` | breadcrumb session for this terminal, else newest in cwd, else new |
| `-r` / `--resume [id\|path]` | picker (no value) or direct open; prefix match, newest wins |
| `--fork <id\|path>` | copy into a new session in current cwd |
| `--export <jsonl> [out.html]` | HTML and exit |
| `--session-dir <dir>` · `--no-session` | custom store · ephemeral |
| `--from-claude` · `--from-codex` | import foreign transcripts |
| `omp share <id\|path> [--gist]` · `omp play [file] -s N -i S` · `omp clip [file] -t -d` | share / replay / publish |
| `omp worktree [list\|add\|clear]` · `omp gc [--apply]` | worktrees · storage GC |

## Slash commands
| Command | Effect | File |
|---|---|---|
| `/resume [id\|@claude\|@codex]` | picker / switch / import | switch |
| `/rename [title]` | set or auto-generate title | same |
| `/move <path>` · `/wt` (`/worktree`) | relocate session to dir / new worktree | same, moved |
| `/fresh` | new provider stream state; transcript + context kept | same |
| `/clear` | drop model context; append `reset_boundary`; history stays on disk | same |
| `/new` | empty conversation, new id | new |
| `/delete` | delete current session + artifacts (best-effort), new id | new |
| `/restart` | relaunch with original flags, resume in place | same |
| `/tree` | leaf move inside file | same |
| `/branch` | rewind selector; user target → new file (`doubleEscapeAction: tree` → same as `/tree`) | usually new |
| `/fork` | full copy, `parentSession`, cache key inherited | new |
| `/compact [instructions]` · `/handoff [focus]` · `/shake` | summarize old history in place | same |
| `/export [--themes] [path]` · `/dump` · `/share` · `/record` | HTML · clipboard+JSON · encrypted link · `.ompcast` | — |

## `/tree` keys
`↑↓` move · `Alt+↑↓` prev/next turn · `PgUp/PgDn` `←→` page · `Home/End` · `Enter` select · `Shift+Enter` summarize+select · type = search · `Esc` clear search/close · `Shift+L` label · `Ctrl+O` / `Shift+Ctrl+O` filter cycle · `Alt+D/T/U/L/A` filter (`default`, `no-tools`, `user-only`, `labeled-only`, `all`)

Selecting a **user** row → leaf = its parent, text prefilled (empty composer only). Other rows → leaf = row. Leaf itself → `Already at this point`.

## `/resume` picker keys
type = search · `Tab` current folder ↔ all projects · `Enter` · `Del` / `⌫` (empty search) delete · `Esc`

## Settings (default)
| Key | Default | Note |
|---|---|---|
| `branchSummary.enabled` | `false` | **opt-in** summarize prompt when leaving a branch; `branchSummary.reserveTokens` 16384 |
| `treeFilterMode` | `default` | initial `/tree` filter |
| `doubleEscapeAction` | `rewind` | `rewind` / `tree` / `none` |
| `autoResume` | `false` | plain `omp` acts like `-c` |
| `compaction.enabled` | `true` | |
| `compaction.methodOrder` | `[remote, snapcompact, handoff, shake, soft]` | first runnable wins |
| `compaction.thresholdTokens` / `thresholdPercent` | `-1` / `-1` | reserve-based: max(16384, 15 %) |
| `compaction.keepRecentTokens` | `20000` | verbatim tail |
| `compaction.asyncEnabled` / `midTurnEnabled` / `autoContinue` | `true` | speculative · mid-turn · continue after |
| `compaction.idleEnabled` | `false` | idle compaction |
| `compaction.handoffSaveToDisk` | `false` | auto handoffs → `handoff-*.md` |
| `contextPromotion.enabled` | `false` | model `contextPromotionTarget` before compacting |
| `share.redactSecrets` / `share.store` / `share.serverUrl` | `true` / `blob` / `https://my.omp.sh/s` | |
| `stream.redactPatterns` | `[]` | extra regexes for `/record` and `omp stream` |
| `worktree.base` / `worktree.clone` / `worktree.cleanSource` | unset (`~/.omp/wt`) / `true` / `false` | |
| `statusLine.rightSegments` | `[session_name, token_total, cost, context_pct]` | where the % lives |
