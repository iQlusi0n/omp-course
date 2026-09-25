# Module 1 cheat sheet — Setup & First Contact (`omp/18.3.1`)

## Install / verify / update
| Want | Command |
|---|---|
| Install | `curl https://omp.sh/install \| sh` |
| Version | `omp --version` (`-v`) |
| Completions | `eval "$(omp completions zsh)"` · `eval "$(omp completions bash)"` · `omp completions fish > ~/.config/fish/completions/omp.fish` |
| Update / check only | `omp update` · `omp update --check` · `--canary` / `--stable` |
| Garbage collect | `omp gc` (dry-run) → `omp gc --apply` (`--wal`, `--blobs`, `--archive` select steps) |

## Launch forms
| Form | Effect |
|---|---|
| `omp` | interactive TUI |
| `omp "text"` | TUI with first message |
| `omp @file.md @img.png "q"` | attach files/images to first message |
| `omp -p "text"` | headless; answer → stdout, `Working...` → stderr |
| `echo "text" \| omp -p` | non-TTY stdin is the prompt (no `-`) |
| `omp -p --mode json "…"` | structured event stream |
| `--no-session` · `-- "…"` · `--allow-home` | ephemeral · literal text after flags · allow starting in `~` |

## Keys (defaults; `/hotkeys` shows yours)
| Key | Action ID | Does |
|---|---|---|
| `Ctrl+O` | `app.tools.expand` | expand/collapse tool output |
| `Ctrl+Shift+O` | `app.tools.toggleVisibility` | hide/show tool activity |
| `Esc` | — | abort running turn / clear draft |
| `Ctrl+C` ×2 | — | exit omp (`Ctrl+C` once clears draft; `Up` recalls it) |
| `Alt+L` | `app.display.reset` | reset garbled display |
| `Ctrl+Q` / `Ctrl+Enter` | `app.message.followUp` | queue follow-up (`Ctrl+Q` exists because Windows Terminal eats `Ctrl+Enter`) |
| `Alt+V` (Windows) | `app.clipboard.pasteImage` | paste when terminal intercepts `Ctrl+V` |
Remap: `~/.omp/agent/keybindings.yml` → `action.id: Chord` or `[]`. tmux: enable `extended-keys`. Odd SSH hops: `PI_TUI_RAW_BACKSPACE_IS_CTRL=1`.

## Auth
| Want | Command |
|---|---|
| Log in | `/login [provider]` · `omp login [provider]` · `/login <redirect-url>` to finish a pasted callback |
| Log out | `/logout` |
| Prove it | `omp token <provider>` (exit 0) · `omp models <provider>` · `omp usage [--provider p]` |
| Env key | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` (`google`), `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `COPILOT_GITHUB_TOKEN`, … |
| `.env` order | shell env › `<cwd>/.env` › `~/.omp/agent/.env` › `~/.omp/.env` › `~/.env` |
| Key precedence | `--api-key` › `models.yml apiKey` › stored OAuth › `/login` key › env/.env › other stored › `models.yml` fallback |
| Store | `~/.omp/agent/agent.db` (profile: `~/.omp/profiles/<name>/agent/agent.db`) |
| Selectable model | not in `disabledProviders` **and** (keyless **or** credentialed) |

## Config root (`omp config path` → `~/.omp/agent`)
| Entry | Purpose |
|---|---|
| `config.yml` | global settings (written by `/settings`, `omp config set/reset`) |
| `models.yml` | custom providers/models (M7) |
| `agent.db` · `.env` · `keybindings.yml` | credentials · env file · chord remaps |
| `sessions/<encoded-cwd>/*.jsonl` | saved sessions (M5) |
| `skills/` · `extensions/` · `agents/` | user-level skills (M6/9) · extensions (M12) · custom agents (M10) |
| `AGENTS.md` · `RULES.md` · `SYSTEM.md` | user-level context / sticky rules / system prompt (M6) |
| `blobs/` · `history.db` · `models.db` | artifacts · prompt history · catalog cache |

## `omp config`
`list [--json]` · `get <key>` · `set <key> <value>` (global file only) · `reset <key>` · `path` · `init-xdg`. In-session: `/settings`.
Layering: env-on-definition › runtime › `--config` overlays / `PI_CONFIG_FILES` › `<cwd>/.omp/config.yml` (dir must be non-empty; no ancestor walk) › `~/.omp/agent/config.yml` › default.
Defaults to know: `tools.approvalMode: yolo` · `startup.showSplash: false`.
Profiles: `omp --profile NAME` · `OMP_PROFILE=NAME` · `omp --profile NAME --alias CMD`. Relocate: `PI_CODING_AGENT_DIR=/path`.
Setup: `omp setup` (onboarding) · `omp setup python --check` · `omp setup speech`.

## Help & docs
`omp --help` · `omp <cmd> --help` · `omp read omp://` (index) · `omp read omp://cli-reference.md[:N-M]`.
Routing: first non-flag arg that is a subcommand runs it; anything else is the prompt (`omp models` ≠ `omp "models"`).

## Subcommands you will meet
`models` `config` `login` `token` `usage` `setup` `completions` `update` `gc` `read` (M1) · `commit` `git` (M4) · `worktree` `share` `play` `clip` (M5) · `stats` `tiny-models` (M7) · `find` `search`/`q` (M8) · `agents` (M10) · `ttsr` (M11) · `plugin` `install` (M12) · `acp` (M13) · `collab` `join` `stream` (M14)
