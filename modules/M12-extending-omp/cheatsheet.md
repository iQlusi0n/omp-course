# Module 12 cheat sheet — Extending omp (omp 18.3.1)

## Extensions (12.1)
| Item | Value |
|---|---|
| Dirs | `<cwd>/.omp/extensions/` (cwd-only) · `~/.omp/agent/extensions/` (profile: `~/.omp/profiles/<p>/agent/extensions/`) |
| Entry | `package.json#omp.extensions` → `index.ts` → `index.js` → one-level `*.ts`/`*.js` scan |
| CLI | `omp -e <path>` / `--extension` (repeatable; `--hook` alias) · `--no-extensions` |
| Settings | `extensions: [...]` · `disabledExtensions: [extension-module:<stem-or-dir>]` |
| Factory | `export default function (pi: ExtensionAPI) {}` — register only; runtime actions throw at load |
| Command | `pi.registerCommand("name", { description, handler(args, ctx) })` |
| Tool | `pi.registerTool({ name, label, description, parameters: pi.zod.object({...}), execute(id, params, signal, onUpdate, ctx) })` → `{ content:[{type:"text",text}], details }` |
| Tool opts | `approval: "read"\|"write"\|"exec"` (default exec) · `loadMode: "discoverable"` (default, via `xd://`) `\|"essential"` |
| Events | `session_start` `turn_end` `context` `tool_call` `tool_result` `before_subagent_spawn` `session_before_compact` `mcp_notification` |
| UI | `ctx.ui.notify/confirm/select/input/editor` · `ctx.ui.setStatus(key,text)` · guard with `ctx.hasUI` |
| Messages | `pi.sendMessage({customType,content,display,attribution},{triggerTurn,deliverAs})` |
| Timers | `ctx.setInterval` / `ctx.setTimeout` (raw timers that throw kill the session) |
| Logs | `~/.omp/logs/omp.<date>.<pid>.log` — `Failed to load extension <path>: …` |

## Hooks & custom tools (12.2)
| Item | Value |
|---|---|
| Block | `pi.on("tool_call", e => ({ block:true, reason }))` — reason = tool error text the model reads; throw also blocks |
| Rewrite / context | `{ input }` · `{ additionalContext }` |
| Patch output | `pi.on("tool_result", e => ({ content, details }))` |
| Hook dirs | `.omp/hooks/pre/` · `.omp/hooks/post/` · `~/.omp/agent/hooks/pre|post/` (nothing else) |
| Hook import | `import type { HookAPI } from "@oh-my-pi/pi-coding-agent/extensibility/hooks"` |
| Custom tool | `CustomToolFactory` in `.omp/tools/` or `~/.omp/agent/tools/`; `execute(id, params, onUpdate, ctx, signal)` |

## MCP (12.3)
| Item | Value |
|---|---|
| Files | `.omp/mcp.json` > `~/.omp/agent/mcp.json` > other tools' configs > root `mcp.json`/`.mcp.json` |
| stdio | `{ "command", "args", "env", "cwd" }` (`type` optional) |
| http / sse | `{ "type": "http", "url", "headers" }` |
| Shared | `enabled` `timeout` `instructions` `auth` `oauth` · user-file `disabledServers` (wins) / `enabledServers` |
| Secrets | `${VAR}` `${VAR:-default}` · value = env var name · `"!cmd"` (10 s, cached) |
| `/mcp` | `add remove enable disable test reconnect reload reauth unauth resources prompts notifications list` |
| Tools | `mcp__<server>_<tool>` sanitized · approval tier `write` |
| Resources | `read mcp://<resource-uri>` · `omp read mcp://…` |
| Timing | `mcp.startupTimeoutMs`=250 · `OMP_MCP_TIMEOUT_MS` (default 30000) · `OMP_MCP_REQUIRE_READY=1` (print mode) |
| Settings | `mcp.enableProjectConfig`=true · `mcp.notifications`=false · `mcp.renderMarkdownResults`=true |

## Marketplaces & plugins (12.4)
| Item | Value |
|---|---|
| Catalog | `.omp-plugin/marketplace.json` (fallback `.claude-plugin/`): `name`, `owner.name`, `plugins[{name, source:"./x"}]`, `metadata.pluginRoot` |
| Plugin tree | `skills/<n>/SKILL.md` `commands/*.md` (→ `/<plugin>:<cmd>`) `agents/` `hooks/pre|post/` `tools/` `.mcp.json` `package.json#omp.extensions` |
| Slash | `/marketplace add\|remove\|update\|list\|discover\|install\|uninstall\|installed\|upgrade` · `/plugins list\|enable\|disable` · `--scope user\|project` |
| CLI | `omp plugin marketplace add|remove|update|list` · `omp plugin discover|install|uninstall|upgrade|enable|disable|list|link|doctor` |
| Refresh | `/reload-plugins` (skills, commands, MCP) · restart for tools/hooks/extensions |
| Disk | `~/.omp/marketplaces.json` · `~/.omp/plugins/{installed_plugins.json,node_modules,omp-plugins.lock.json,cache/}` · `<proj>/.omp/plugins/…` |
| Setting | `marketplace.autoUpdate`: off \| notify (default) \| auto |
| Names | lowercase, digits, `-`, `.`; ≤ 64; `name@marketplace` ≤ 128 |

## Foreign config (12.5)
| Item | Value |
|---|---|
| Priority | native 100 · omp-plugins 90 · claude 80 · agent-plugins 75 · agents/claude-plugins/codex 70 · gemini 60 · opencode 55 · cursor/windsurf 50 · cline 40 · github 30 · vscode 20 · agents-md/claude-md 10 |
| Audit | `/extensions` · `/mcp list` |
| Whole source | `disabledProviders: [claude, cursor, …]` (path-scoped `- path:` / `providers:`) |
| One file | `disabledExtensions: [context-file:<user\|project>:<basename>]` |
| Foreign user roots | `enabledProviders: [claude, …]` or `[*]` — default `[]` (off) |
| Project MCP | `mcp.enableProjectConfig: false` |
| One run | `--no-rules` `--no-skills` `--no-extensions` |
