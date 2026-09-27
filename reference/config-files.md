# Config file map

`~/.omp/agent` = the active agent directory (`omp config path`). `PI_CODING_AGENT_DIR` relocates it; a named profile (`omp --profile <n>`, `OMP_PROFILE`) uses `~/.omp/profiles/<n>/agent` instead (profiles inherit only `keybindings.yml`). `<repo>/.omp` = the project directory; most project lookups are **cwd-only** (no ancestor walk) and require the directory to be non-empty — exceptions are noted.

## `~/.omp/agent/*` (user scope)

| Entry | Purpose | Written by | Module |
|---|---|---|---|
| `config.yml` | global settings (first present of `config.yml`, `config.yaml`) | `omp config set/reset`, `/settings` | M1, M6 |
| `models.yml` | custom providers / models / overrides; cache in `models.db` | hand-edit | M7 |
| `agent.db` | credentials (OAuth, `/login` keys), legacy settings | `/login`, `omp login` | M1 |
| `.env` | env file (order: shell › `<cwd>/.env` › here › `~/.omp/.env` › `~/.env`) | hand-edit | M1, M7 |
| `keybindings.yml` | chord remaps (`keybindings.json`/`.yaml` migrated) | hand-edit | M1, M2 |
| `AGENTS.md` | user context file (`<repo-rules>`) | hand-edit | M6 |
| `RULES.md` | user sticky rule — **shadows** a project `RULES.md` (same rule name) | hand-edit | M6 |
| `SYSTEM.md` · `APPEND_SYSTEM.md` · `SYSTEM_TEMPLATE.md` · `PERSONALITY.md` · `TITLE_SYSTEM.md` | replace / append / Handlebars template / tone / session-title prompt | hand-edit | M6 |
| `WATCHDOG.md` · `WATCHDOG.yml` | advisor priorities / advisor roster | hand-edit, `/advisor configure` | M11 |
| `rules/*.md` (`.mdc`) | rulebook / always-apply / TTSR rules | hand-edit | M6, M11 |
| `commands/*.md` | `/name` slash commands (project copy wins) | hand-edit | M6 |
| `skills/<name>/SKILL.md` | user skills (`skill://`, `/skill:`) | hand-edit, `omp skill` | M6 |
| `managed-skills/<name>/SKILL.md` | skills written by `manage_skill` / `learn` (provider `omp-managed`, priority 5) | the model | M9 |
| `agents/<name>.md` | custom subagents | hand-edit, `omp agents unpack` | M10 |
| `extensions/` · `hooks/pre\|post/` · `tools/` | extension modules · hook factories · custom tools | hand-edit | M11, M12 |
| `prompts/*.md` · `instructions/*.md` | prompt / instruction capability files | hand-edit | — |
| `mcp.json` (then `.mcp.json`) | MCP servers (user) | `/mcp add` | M12 |
| `lsp.json` · `secrets.yml` | language-server overrides · secret patterns (`secrets.enabled`) | hand-edit | M6, M8 |
| `sessions/<encoded-cwd>/<ts>_<id>.jsonl` (+ sibling dir) | session transcripts + artifacts, `btw-history/`, `handoff-*.md`, `__advisor*.jsonl` | omp | M5 |
| `blobs/<sha256>` · `history.db` · `terminal-sessions/<id>` | artifacts · prompt history · `-c` breadcrumbs | omp | M5 |
| `memories/<encoded-cwd>/` · `memories/mnemopi/mnemopi.db` | `local` / `mnemopi` memory stores | omp | M9 |
| `share.*` | custom share handler (no fallback if it fails) | hand-edit | M5 |

Other `~/.omp/` paths: `~/.omp/marketplaces.json`, `~/.omp/plugins/{installed_plugins.json,node_modules,omp-plugins.lock.json,cache/}` (M12) · `~/.omp/wt/` worktrees (`worktree.base`) (M5, M10) · `~/.omp/stats.db` (`omp stats`) (M7) · `~/.omp/logs/omp.<date>.<pid>.log` (M12) · `~/.omp/browser-relay/extension` (M14) · `~/.omp/run/collab-hosts` (M14) · `~/.omp/python-env` (M8) · `~/.omp/profiles/<n>/agent/` (M6). `omp config init-xdg` moves data/state/cache under `$XDG_*_HOME/omp`.

## `<repo>/.omp/*` (project scope)

| Entry | Lookup | Purpose | Module |
|---|---|---|---|
| `AGENTS.md` · `RULES.md` | **nearest non-empty `.omp/`** walking up to the repo root; missing file does not continue upward | project context · sticky rule (`rule://RULES`) | M6 |
| `SYSTEM.md` · `APPEND_SYSTEM.md` · `SYSTEM_TEMPLATE.md` · `TITLE_SYSTEM.md` | nearest non-empty `.omp/` (title: cwd) | system prompt · titles (`PERSONALITY.md` is user-only) | M6 |
| `WATCHDOG.md` | every `<dir>/WATCHDOG.md` and `<dir>/.omp/WATCHDOG.md` up to the repo root (all load) | advisor priorities | M11 |
| `config.yml` (`settings.json` first) | cwd only; layer between global and overlays; arrays replace | project settings | M6 |
| `secrets.yml` | cwd only | array of `{type, content, mode, …}` | M6 |
| `rules/*.md` | cwd only | rulebook / always-apply / TTSR | M6, M11 |
| `commands/*.md` | cwd only; beats user | `/name` with `$1 $@ $ARGUMENTS` | M6 |
| `skills/<name>/SKILL.md` | **every ancestor** `.omp/skills/` (no non-empty requirement) | `skill://<name>`, `/skill:<name>` | M6 |
| `agents/<name>.md` | nearest `.omp/agents` from cwd | custom subagents (`.claude/agents` etc. skipped) | M10 |
| `extensions/` · `hooks/pre\|post/*.ts` · `tools/` | cwd only | extensions · `tool_call`/`tool_result` guards · `CustomToolFactory` | M11, M12 |
| `mcp.json` (then `.mcp.json`) | project first, then user, then foreign, then root `mcp.json`/`.mcp.json`; `mcp.enableProjectConfig` | MCP servers | M12 |
| `lsp.json` · `dap.json` | project › user | `{"servers":{…},"idleTimeoutMs":…}` · `{"adapters":{…}}` | M8 |
| `plugins/…` | project-scope installed plugins (`--scope project`) | plugins | M12 |
| `../.omp-plugin/marketplace.json` (repo root; fallback `.claude-plugin/`) | marketplace catalog: `name`, `owner.name`, `plugins[{name, source:"./x"}]` | `/marketplace add` | M12 |

## Foreign formats omp discovers

Provider priority (higher wins a same-depth conflict; dedup by name, first wins): `native` 100 › `omp-plugins` 90 › `claude` 80 › `agent-plugins` 75 › `codex` / `agents` / `claude-plugins` 70 › `gemini` 60 › `opencode` 55 › `cursor` / `windsurf` 50 › `cline` 40 › `github` 30 › `vscode` 20 › `agents-md` / `claude-md` 10 › `mcp-json` / `ssh-json` 5 › `builtin-defaults` 1.

| Provider id | Project path | User path (all foreign user roots are **opt-in** via `enabledProviders`) | Contributes | Walk-up? |
|---|---|---|---|---|
| `claude` | `.claude/CLAUDE.md`, `.claude/commands/`, MCP | `~/.claude/CLAUDE.md` | context, commands (`commands.enableClaudeProject` true / `.enableClaudeUser` false), MCP | no |
| `claude-md` / `agents-md` | standalone `CLAUDE.md` / `AGENTS.md` (not inside a dot-dir) | — | context | yes (to repo root / home boundary) |
| `agents` | `.agent/AGENTS.md`, `.agents/AGENTS.md` | `~/.agent/`, `~/.agents/` | context, rules | yes |
| `codex` | — (project Codex context comes via `agents-md`) | `~/.codex/AGENTS.md` | context | — |
| `gemini` | `.gemini/GEMINI.md`, `extensions/<n>/gemini-extension.json` | `~/.gemini/GEMINI.md` | context, extensions | no |
| `opencode` | — | `~/.config/opencode/AGENTS.md` | context | — |
| `github` | `.github/copilot-instructions.md`; `.github/instructions/**/*.instructions.md` (rules; `applyTo` globs) | `~/.copilot/copilot-instructions.md` | context, rules | no |
| `cursor` | `.cursor/rules/*.mdc`, legacy `.cursorrules`, `.cursor/mcp.json` | `~/.cursor/rules` | rules, MCP, settings | no |
| `windsurf` | `.windsurf/rules/*.md`, `.windsurfrules` | global Windsurf rules | rules, MCP | no |
| `cline` | `.clinerules` | — | rules | no |
| `vscode` / `mcp-json` | `.vscode` MCP config; root `mcp.json` / `.mcp.json` | — | MCP | no |
| `claude-plugins` / `omp-plugins` / `agent-plugins` | marketplace-installed plugin trees (`skills/ commands/ agents/ hooks/ tools/ .mcp.json`) | `~/.omp/plugins` | skills, commands, rules, hooks, tools, MCP | — |
| `ssh-json` | `ssh.json` (`omp ssh add --scope project\|user`) | user `ssh.json` | SSH hosts | — |

Controls: `disabledProviders: [claude, cursor, …]` drops a whole source (ids shared with model providers — `google` ≠ `gemini`); `disabledExtensions: [context-file:project:CLAUDE.md, skill:x, extension-module:<stem>]` drops one item; `enabledProviders: [claude]` opts in foreign **user** roots (default none); `--no-rules --no-skills --no-extensions` for one run; `/extensions` audits what loaded; `/reload-plugins` refreshes skills/commands/MCP (extensions, hooks, tools need a restart).

Source: omp://context-files.md · omp://config-usage.md · omp://system-prompt-customization.md · omp://advisor-watchdog.md · omp://mcp-config.md · omp://marketplace.md · omp://lsp-config.md · omp://tools/debug.md · omp://keybindings.md · modules M01, M05, M06, M08–M12, M14 cheat sheets
