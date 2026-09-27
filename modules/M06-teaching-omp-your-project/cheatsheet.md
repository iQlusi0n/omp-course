# Module 6 cheat sheet — Teaching omp your project (omp/18.3.1)

`~/.omp/agent` = active agent dir (`omp config path`); a profile moves it to `~/.omp/profiles/<name>/agent`.

## Files and where omp looks

| File | Project | Walk-up? | User | Loaded |
|---|---|---|---|---|
| `AGENTS.md` | nearest non-empty `.omp/` | yes | `~/.omp/agent/AGENTS.md` | once, `<repo-rules>` |
| `RULES.md` | same dir as above | yes | `~/.omp/agent/RULES.md` (**shadows** project) | every request |
| `rules/*.md` | `<cwd>/.omp/rules/` | no | `~/.omp/agent/rules/` | rulebook / always-apply |
| `commands/*.md` | `<cwd>/.omp/commands/` (beats user) | no | `~/.omp/agent/commands/` | `/name` |
| `skills/<n>/SKILL.md` | every ancestor `.omp/skills/` | yes | `~/.omp/agent/skills/` | `skill://`, `/skill:` |
| `config.yml` | `<cwd>/.omp/config.yml` | no | `~/.omp/agent/config.yml` | settings layer |
| `secrets.yml` | `<cwd>/.omp/secrets.yml` | no | `~/.omp/agent/secrets.yml` | needs `secrets.enabled` |
| `SYSTEM.md` (`APPEND_SYSTEM.md`: keep it in the same `.omp/`; walk-up documented only for `SYSTEM.md`) | nearest non-empty `.omp/` | yes | `~/.omp/agent/` | prompt replace / append |
| `PERSONALITY.md`, `TITLE_SYSTEM.md` | — / `<cwd>/.omp/` | no | `~/.omp/agent/` | tone / titles |

Foreign files also load: `.claude/CLAUDE.md`, `.gemini/GEMINI.md`, `.github/copilot-instructions.md` (cwd only); standalone `AGENTS.md`/`CLAUDE.md`, `.agent[s]/` (walk-up); `~/.codex/AGENTS.md`, `~/.config/opencode/AGENTS.md` (user). Cursor/Windsurf/Cline/`.github/instructions` → rules.

## Precedence (context files, rules, commands, skills)

`native` 100 > `omp-plugins` 90 > `claude` 80 > `agent-plugins` 75 > `agents`/`claude-plugins`/`codex` 70 > `gemini` 60 > `opencode` 55 > `cursor`/`windsurf` 50 > `cline` 40 > `github` 30 > `vscode` 20 > `agents-md`/`claude-md` 10 > `builtin-defaults` 1.
One user context file total; one project file per depth (higher priority wins a depth); dedup of rules/commands/skills by **name**, first wins.

| Setting | Effect |
|---|---|
| `disabledProviders: [claude, google, …]` | whole discovery source *or* model backend; path-scoped entries allowed |
| `disabledExtensions: [context-file:project:CLAUDE.md, skill:x]` | one item; shadowed file loads instead |
| `enabledProviders: [claude, cursor]` | opt in foreign **user-level** roots (default none) |
| `/extensions` | list/toggle context files, rules, commands |

## Rule frontmatter

`description:` → rulebook (body via `rule://<name>`) · `alwaysApply: true` → injected · `globs: [..]` → hint · `agents: main|sub|[glob…]` → scope · `condition/astCondition/question` → TTSR (M11). `RULES.md` = rule `RULES`, always sticky; re-read on `/clear`, `/new`. `rule://` works only inside a session. `--no-rules`.

## Commands and skills

Command: `.omp/commands/<name>.md`, `description:` frontmatter, `$1 $2 $@[2] $@[2:3] $ARGUMENTS|$@`; refresh with `/reload-plugins`; unknown `/x` goes to the model as text.
Skill: `.omp/skills/<name>/SKILL.md` (one level), `name` + **required** `description`, `hide`/`disableModelInvocation`; `skill://<name>[/asset]` (`omp read skill://…` from shell); `/skill:<name> [args]` (`skills.enableSkillCommands`, default **true**); filters `skills.ignoredSkills`, `skills.includeSkills`, `skills.customDirectories`, `--no-skills`, `--skills a,b`.

## Settings

`defaults < ~/.omp/agent/config.yml < <cwd>/.omp/config.yml < PI_CONFIG_FILES, --config f (repeatable) < runtime flags < declared env var`. Objects merge, **arrays/scalars replace**.

| Command | Note |
|---|---|
| `omp config list\|get k\|set k v\|reset k\|path [--json]` | `set`/`reset`/`/settings` write **global** only; `set --json` → `overriddenBy` |
| `omp --config f.yml` | launch/`acp`/`models` only; use `PI_CONFIG_FILES=f.yml omp config get k` in a shell |
| `omp --profile n` / `OMP_PROFILE=n` | isolated `~/.omp/profiles/n/agent` (keybindings inherited) |
| `omp --profile n --alias cmd` | writes `cmd() { command omp --profile=n "$@"; }` to your rc |

## System prompt

`APPEND_SYSTEM.md`/`--append-system-prompt` keep everything · `SYSTEM.md`/`--system-prompt` replace instruction block (context/skills/rules/footer stay) · `SYSTEM_TEMPLATE.md`/`--system-prompt-template` Handlebars · `PERSONALITY.md` + `personality: default|friendly|pragmatic|none` · flags beat files; literal beats template; task subagents get no append text.

## Secrets (default **off**)

`secrets.enabled: true`. Sources: env vars named `*KEY*|SECRET|TOKEN|PASSWORD|PASS|AUTH|CREDENTIAL|PRIVATE|OAUTH*` (≥ 8 chars), `secrets.yml` array of `{type: plain|regex, content, mode: obfuscate|replace, replacement, flags, friendlyName}`, built-in credential regexes, URL passwords. Provider sees `$$[NAME_]HASH[:U|L|C|M]$$`; obfuscate-mode values restored in model-authored tool args before execution; replace is one-way; TUI display restores locally.

Lab fixture: `.env.example` → `LAB_TOKEN=labtok_0123456789abcdef` → regex `labtok_[0-9a-f]{16}`.
