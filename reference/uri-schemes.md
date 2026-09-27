# Internal URI schemes

Built-in registry per `omp://tools/read.md` ("Internal URLs"): `agent://`, `artifact://`, `attachment://`, `cfg://`, `conflict://`, `history://`, `issue://`, `local://`, `mcp://`, `memory://`, `omp://`, `pr://`, `proc://`, `rule://`, `security://`, `skill://`, `ssh://`, `vault://`, `xd://`. MCP servers may advertise more. Every scheme resolves through `read`; a scheme is writable only if its handler exposes `write` — read-only schemes are refused at the approval gate with `<scheme>:// URLs are read-only`, and `edit`/`ast_edit` never target URLs. Unknown `scheme://` targets are refused instead of becoming local filenames (prefix `./` on purpose).

`omp read <uri>` from a shell shows exactly what the model would see, but session-scoped schemes (`local://`, `memory://`, `rule://`, `xd://`, `agent://`, `artifact://`) only resolve inside a session.

| Scheme | Read | Write | Example | Notes / gate | Module |
|---|---|---|---|---|---|
| `agent://` | `agent://<id>` subagent output; `agent://<id>/key/0` JSON path (discrete value, no pagination, no line selector); nested `agent://<id>.<child>` | `agent://<id>` message a peer (revives parked); `agent://all` broadcast (write-only) | `read agent://Scout-1/findings/0` · `write agent://Scout-1` + content | messaging is read-approved, allowed in plan mode | M10 |
| `artifact://` | `artifact://<id>[:1-200 \| :raw:1-3000]`; `grep` works; whole-resource read > 8 MiB refused, unbounded `:raw` > 50 KiB refused | no | `read artifact://12:1-200` | spilled tool output (`tools.artifactSpillThreshold` 50 KB); ids are per session; needs a session (`--no-session` → `No session - artifacts unavailable`) | M2 |
| `attachment://` | current image attachments; `?q=<question>` asks the vision role | no | `read <uri from the error list>?q=what is shown` | grammar is only exposed via the error `Available attachment URIs: …`; not covered by a module | — |
| `cfg://` | bare = effective config tree as commented YAML; `cfg://<key>` = value, `type`, `default`, `source`, `values`, `description` | handler write hook (settings-panel plumbing per `omp://config-usage.md`); content grammar undocumented | `read cfg://tools.approvalMode` | works from the shell: `omp read cfg://<key>` is the fastest way to see a default | M1, M6 |
| `conflict://` | `conflict://<N>` one registered marker block; `/ours` `/theirs` `/base` `/both` sides (read-only scopes) | `conflict://<N>` with `@ours` \| `@theirs` \| `@base` \| `@both` \| literal lines; `conflict://*` all, or per-id `1: @ours⏎2: @theirs` | `read f.py:conflicts` → `write conflict://1` content `@theirs` | ids registered by `<file>:conflicts`, session-scoped, invalidated on resolve; `@base` needs diff3 | M4 |
| `history://` | bare = registered agents + persisted subagents; `history://<id>` transcript; `history://current/full[:raw:1-200]` raw branch (needs `compaction.experimentalContextManagement`) | no | `read history://` · `read history://Scout-1` | `history://current/full` rejects queries/fragments/extra paths | M10, M11 |
| `issue://` | `issue://<N>` · `issue://<owner>/<repo>/<N>` · `?comments=0` · bare `issue://?state=open&limit=5&author=&label=` | no (mutations via `github` tool) | `read issue://1` | needs `gh` authenticated; `github.enabled` for the tool, not the read | M8 |
| `local://` | session-local artifact sandbox file; globs `local://*.md`; hashline anchors kept | yes (plain-file path; snapshot header returned) | `write local://ctx.md` → `read local://ctx.md` | shared with subagents (flat-shape `task` context convention); `No session - local:// unavailable` from a shell | M10 |
| `mcp://` | `mcp://<resource-uri>` MCP server resource | not documented | `read mcp://docs/readme` · `/mcp resources` | server must be connected; `omp read mcp://…` works from a shell | M12 |
| `memory://` | `memory://root[/MEMORY.md \| learned.md \| skills/<n>/SKILL.md]` (only `memory.backend: local`; bare root = `memory_summary.md`; globs ok) · `memory://<id>` full Mnemopi row (`memory.backend: mnemopi`) | no (use `memory_edit`) | `read memory://root/MEMORY.md` · `read memory://<id>` before `memory_edit update` | in-session only (`Unknown protocol: memory://` from a shell); hindsight ids return a pointer only | M9 |
| `omp://` | bare = doc index (134 files); `omp://<file>[:N-M]`; `grep` walks every doc | no | `omp read omp://cli-reference.md:1-40` · `grep approvalMode omp://` | works everywhere | M1 |
| `pr://` | `pr://<N>` · `pr://<owner>/<repo>/<N>` · `pr://<N>/diff` · `/diff/<i>` · `/diff/all` · `?comments=0` · bare list with `?state=&limit=&author=&label=`; GHE host prefix accepted | no | `read pr://42/diff` | same SQLite cache as the `github` tool; needs `gh` | M4, M13 |
| `proc://` | bare = background jobs + services; `proc://<id>` status + output without consuming delivery; `grep re proc://<name>` searches service logs | `proc://<id>` stdin (Enter appended; empty = Enter); `proc://<id>/kill` cancel job / stop service / abort owned subagent (no content); `proc://<id>/mode` `persist` \| `session` \| `detached` | `read proc://api` · `write proc://api/kill` | proc writes are `exec` tier; `omp ps` is the shell mirror | M2, M10 |
| `rule://` | `rule://<name>` body of a rulebook / always-apply / registered TTSR rule (frontmatter stripped) | no | `read rule://no-print-in-api` · `rule://RULES` | exact name; rules with no `description`, no `alwaysApply`, no accepted TTSR condition are not addressable; in-session only | M6, M11 |
| `security://` | `security://` index · `scans` · `scans/<id>` · `/manifest` `/findings[/<fid>]` `/coverage` `/report` `/sarif` `/provenance` | no (mutations via `security_scan`) | `read security://scans/<id>/findings` | `security.enabled: true` (default `false`) else `security:// is disabled` | M8 |
| `skill://` | `skill://<name>[/asset]` full SKILL.md or asset (unbounded — no default line cap); `grep re skill://<name>` searches the skill dir | no | `omp read skill://release-checklist` | traversal (`..`) rejected; works from a shell | M6, M9 |
| `ssh://` | `ssh://<host>/<path>` remote UTF-8 file or dir (≤ 1 MiB, POSIX shell); bare `ssh://` lists hosts; percent-encode `:` `?` `#` | not documented in `omp://tools/write.md` | `read ssh://build/etc/hostname` | hosts from `omp ssh add <name> --host … --user …` (`--scope project\|user`) or OpenSSH aliases; read tier is `exec`, so `glob` refuses it and `grep` cannot list a remote dir | M8 |
| `vault://` | Obsidian vault content (file-backed) | yes (plain-file path) | `read vault://Notes/todo.md` | `vault.enabled: true` (default `false`) else `vault:// is disabled`; not covered by a module | — |
| `xd://` | bare = mounted tool devices; `xd://<tool>` input documentation | `xd://<tool>` with a JSON argument object = dispatch the tool (its own approval tier, result, errors); `xd://resolve` / `xd://reject` apply or discard a staged `ast_edit` proposal (body = reason) | `read xd://ast_edit` → `write xd://ast_edit {"ops":…}` | `tools.xdev: true` (default) presents *discoverable* tools this way; `tools.xdevDocs` `inline\|builtins\|catalog`; `xd:// is not mounted` from a shell | M8, M9, M12 |

## Selectors that apply to file-backed schemes

`local://`, `artifact://`, `agent://`, `skill://`, `memory://root/…`, `vault://` are located to a real file, so `:N`, `:A-B`, `:A+C`, `:5-10,20-30`, `:raw`, `:img` behave like filesystem reads. Virtual schemes (`omp://`, `history://`, `proc://`, `cfg://`, `xd://`, `rule://`, `security://`) paginate in memory and reject `:img`. A trailing line selector on a **write** target (`local://notes.md:5`) is refused rather than dropped.

## Shell mirrors

| Want | Command |
|---|---|
| exact model view | `omp read <uri>` |
| search docs | in-session `grep` tool with `path: omp://` (the `omp grep` CLI only takes filesystem paths) |
| services | `omp ps [list\|info\|logs\|stop\|kill\|restart] <name>` |
| SSH hosts | `omp ssh add\|remove\|list` |

Source: omp://tools/read.md · omp://tools/write.md · omp://tools/grep.md · omp://tools/glob.md · omp://tools/task.md · omp://tools/security_scan.md · omp://rulebook-matching-pipeline.md · omp://config-usage.md · `omp read cfg://` · `omp read vault://` · `omp ssh --help` · modules M02, M04, M06, M08–M13 cheat sheets
