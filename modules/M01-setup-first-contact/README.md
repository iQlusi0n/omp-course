# Module 1 — Setup & First Contact

| | |
|---|---|
| **Built against** | `omp --version` → `omp/18.3.1` |
| **Level / time** | basic · ~1 h (seven lessons, 5–12 min each) |
| **Goal** | From zero to a verified, model-backed `omp` answering one question in the practice repo. |
| **Prerequisites** | A terminal, `git`, Python 3. The practice repo `omp-course-lab` checked out at tag `module-1-start`. |
| **Files** | `exercises.md` (coursework W/G/S), `cheatsheet.md`, `demos/` (fenced transcripts), `solutions/` (instructor), `BUILD-NOTES.md` (what was dropped and why). |

Every command, flag, key, setting and path in this module was read in the bundled docs (`omp read omp://<file>`) or in `omp --help` / `omp <cmd> --help` for the version above. Each lesson ends with a `Source:` line naming the docs.

How to read the transcripts: `$` lines are your shell, `›` lines are what you type into the omp composer, everything else is output. TUI renderings in `demos/` are illustrative — glyphs and colors vary with theme and terminal; the words on the cards do not.

---

## Lesson 1.1 — What omp is (and isn't)              (~5 min)
**You will be able to:** (1) describe the omp loop in one sentence; (2) say how a terminal agent differs from chat and from autocomplete; (3) name the four entry points and pick the right one for "I'm sitting at the keyboard".

**Why this exists:** A chat assistant answers; an autocompleter guesses the next token. omp *acts*: given a prompt it reads files, searches, edits, and runs commands in your repo, and every one of those actions is rendered as a card you can expand and audit. The unit of work is a **turn**: prompt → model → zero or more tool calls → a final message. You are the reviewer of the cards, not the typist of the code. Everything else in this course is about steering that loop and reading its output.

**Demo:** `demos/01-help.md` — the `omp --help` sections that matter today. Excerpt:

```text
$ omp --help
omp v18.3.1

USAGE
  $ omp [COMMAND]

ARGUMENTS
  MESSAGES   Messages to send (prefix files with @)
…
  -p, --print                           Non-interactive mode: process prompt and exit
…
      --mode=<value>                    Output mode: text (default), json, rpc, or rpc-ui
…
Available Tools (default-enabled unless noted):
  read          - Read file contents
  bash          - Execute bash commands
  edit          - Edit files with find/replace
  write         - Write files (creates/overwrites)
  grep          - Search file contents
  glob          - Find files by glob pattern
  lsp           - Language server protocol (code intelligence)
  python        - Execute Python code (requires: omp setup python)
  notebook      - Edit Jupyter notebooks
  browser       - Browser automation (Puppeteer)
  computer      - Native host desktop capture and input (disabled by default)
  task          - Launch sub-agents for parallel tasks
  todo          - Manage todo/task lists
  web_search    - Search the web
  ask           - Ask user questions (interactive mode only)
```

**Concepts:**
- **The loop.** You type a prompt. The model decides which tools to call (`read`, `grep`, `glob`, `edit`, `write`, `bash`, …). Each call and its result appears as a **card** in the transcript. When the model stops calling tools it writes a final message. You review the cards and the diff, then steer with the next prompt. Module 2 dissects each card; Module 3 teaches steering.
- **Agent vs chat vs autocomplete.** Chat: you paste context in, copy code out. Autocomplete: inline, one line at a time, no execution. Agent: the model has the repo and a shell; it verifies its own work (or you tell it to — Module 3). The risk profile is different, which is why Module 4 covers approval modes before you let it loose on real work.
- **Four entry points, one engine** (`omp --help`, `--mode`):
  | Entry point | How | Used in |
  |---|---|---|
  | **TUI** (interactive) | `omp` | this module, Modules 1–12 |
  | **Print mode** (headless) | `omp -p "…"` / `--mode json` | 1.5 today; Module 13 |
  | **RPC** (host an omp in your own program) | `omp --mode rpc` | Module 13 |
  | **ACP** (editor-embedded) | `omp acp` / `--mode acp` | Module 13 |
- **Tools are default-on** except `computer` (and `python` needs `omp setup python`) — read it straight from `omp --help`'s "Available Tools" section. Module 8 covers the setting-gated ones.

**Try it (Walkthrough):**
1. Run `omp --help | grep -n "Available Tools" -A 16`.
   **Expected:** fifteen tool lines; `ask` is marked "interactive mode only", `computer` "disabled by default".
2. Run `omp --help | grep -n -- "--mode=\|--print "` (note the trailing space after `--print`, which excludes `--print-thoughts`).
   **Expected:** exactly two lines: `--mode=<value>` listing `text`, `json`, `rpc`, `rpc-ui`, and `-p, --print`.
3. Run `omp --help | grep -n "^  acp"`.
   **Expected:** `acp            Run omp as an ACP (Agent Client Protocol) server over stdio`.

**Guided task:** Goal: write the four entry points and the flag/command that starts each into `notes/m1-entrypoints.txt` in the lab repo (`notes/` is gitignored). Hints: everything is in `omp --help`; `--mode` has one value the short help doesn't list — `omp read omp://cli-reference.md` and search "Output modes". Checkpoints: (a) you found `-p`; (b) you found the `acp` subcommand; (c) you found the fifth `--mode` value in the doc. Pass: `grep -c -e "-p" -e rpc -e acp notes/m1-entrypoints.txt` prints `3` or more.

**Stretch:** Goal: from `omp --help` alone, list the tools a *headless* run cannot use meaningfully. Pass: your list names `ask` and you can point at the phrase in `--help` that justifies it.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `omp: command not found` | not installed / not on PATH yet | Lesson 1.2 |
| `omp --help` shows a different tool list than above | different version | `omp --version`; this module is pinned to 18.3.1 — re-read `--help`, it is ground truth for *your* build |

**Cheat sheet:**
| Want | Command |
|---|---|
| Interactive session | `omp` |
| Headless answer, exit | `omp -p "…"` |
| Machine-readable events | `omp -p --mode json "…"` |
| Full flag list | `omp --help` |

**Source:** omp://cli-reference.md, `omp --help`

---

## Lesson 1.2 — Install              (~10 min)
**You will be able to:** (1) install omp with the documented script; (2) confirm the install with `omp --version`; (3) enable shell completions for bash, zsh, or fish; (4) check for and apply updates.

**Why this exists:** omp ships as a single binary plus native add-ons; the install script places it and keeps it upgradeable through `omp update`. Completions matter more here than for most CLIs because the launch surface has ~60 flags and ~50 subcommands — `omp --res<Tab>` beats scrolling `--help`.

**Demo:** `demos/02-install-version.md`. Excerpt:

```text
$ omp --version
omp/18.3.1
$ eval "$(omp completions zsh)"
$ omp update --check
Current version: 18.3.1
✔ Already up to date
```

**Concepts:**
- **Install script.** `curl https://omp.sh/install | sh` (the form documented in the bundled docs; adding `-fsSL` is ordinary curl hardening and changes nothing about omp). A Homebrew formula also exists; the docs mention it but not its name, so use the script if in doubt. A Nix package exists (`PI_PACKAGE_DIR` in `omp --help` is there for Nix/Guix store paths). Bun, Windows PowerShell and mise install paths are **not** described in the bundled docs and are therefore not taught here — see `BUILD-NOTES.md`.
- **Verify:** `omp --version` (also `-v`) prints `omp/<version>` and exits.
- **Completions:** `omp completions SHELL` prints a script (`bash|zsh|fish`). Documented wiring (`omp completions --help`):
  - zsh: `eval "$(omp completions zsh)"` in `~/.zshrc`, or write it to a file in `$fpath`
  - bash: `eval "$(omp completions bash)"` in `~/.bashrc`
  - fish: `omp completions fish > ~/.config/fish/completions/omp.fish`
- **Updates:** `omp update` installs; `omp update --check` only reports; `--canary` / `--stable` switch release channel; `-f/--force`; `-l/--plugins` updates installed plugins. If GitHub rate-limits release metadata, set `GITHUB_TOKEN` or `GH_TOKEN` (`omp update --help`).
- **Version pin for this course:** everything here was verified on 18.3.1. If `omp update` moves you forward and something differs, `omp <cmd> --help` and `omp read omp://<doc>` are the arbiters, not this text.

**Try it (Walkthrough):**
1. `curl https://omp.sh/install | sh`, then open a new shell (or re-source your rc file).
   **Expected:** `which omp` prints a path.
2. `omp --version`
   **Expected:** `omp/18.3.1` (or newer — note the difference in `notes/`).
3. Add the completion line for your shell to its rc file, then start a new shell.
   **Expected:** no error on shell start.
4. Type `omp --res` and press `Tab`.
   **Expected:** the shell completes `--resume` (bash/zsh may show `--resume=`; fish shows a description column).
5. `omp update --check`
   **Expected:** `Current version: 18.3.1` and either `✔ Already up to date` or a newer version offered. Do not install mid-module unless you want to re-verify.

**Guided task:** Goal: prove the completion script contains every launch flag you will use today without opening it in an editor. Hints: the script is plain text on stdout; `grep -c` counts. Checkpoints: (a) `omp completions bash | grep -c -- '--resume'` ≥ 1; (b) the same for `--print`; (c) the same for `--profile`. Pass: all three counts are non-zero.

**Stretch:** Goal: in a *second* shell you don't normally use (e.g. bash if you live in zsh), wire completions the documented way and verify `omp mod<Tab>` completes `models`. Pass: `models` completes.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `command not found` after install | PATH not refreshed | open a new shell; check the install script's final message for the directory it used |
| `omp update` fails with a GitHub rate-limit message | anonymous API quota | `GITHUB_TOKEN=… omp update` (documented in `omp update --help`) |
| Completions "work" but `--res<Tab>` shows nothing | rc line added to the wrong shell's file, or shell not restarted | confirm `echo $SHELL`; `eval "$(omp completions $(basename $SHELL))"` in the *current* shell to test |
| macOS: install worked but you expected a Gatekeeper prompt | `curl … | sh` sets no quarantine bit, so Gatekeeper is not consulted | nothing to fix — this is documented behavior |

**Cheat sheet:**
| Want | Command |
|---|---|
| Install | `curl https://omp.sh/install \| sh` |
| Version | `omp --version` |
| Completions | `eval "$(omp completions zsh)"` · `eval "$(omp completions bash)"` · `omp completions fish > ~/.config/fish/completions/omp.fish` |
| Update / check only | `omp update` · `omp update --check` |
| Channel | `omp update --canary` · `omp update --stable` |

**Source:** omp://cli-reference.md (`completions`, `update`), omp://macos-signing-notarization.md (install script and Homebrew formula mention — internals doc; see BUILD-NOTES), `omp completions --help`, `omp update --help`

---

## Lesson 1.3 — Terminal requirements              (~8 min)
**You will be able to:** (1) explain why some omp chords need a terminal that encodes modifier keys; (2) run a two-key test that tells you whether *your* terminal delivers them; (3) look up what omp expects with `/hotkeys` and remap in `keybindings.yml` when it doesn't.

**Why this exists:** A classic terminal sends `Ctrl+O` and `Ctrl+Shift+O` as the *same* byte, and `Alt+Shift+P` may arrive as an Escape followed by `P`. omp's key parser understands the legacy encodings and the modern ones (xterm `modifyOtherKeys`, the Kitty keyboard protocol), but it can only distinguish chords the terminal actually encodes. When a chord "does nothing", the fix is on the terminal side or a remap — not in omp. Find out now, before Module 2 asks you to use `Ctrl+O` and `Ctrl+Shift+O` back to back.

**Demo:** `demos/03-terminal-check.md`. Excerpt:

```text
$ cd omp-course-lab && omp
› read README.md and summarize it in one line
  ▸ read README.md                       ← tool card (collapsed)
  omp-course-lab is a small Python practice repo …
  [Ctrl+O]   → card expands and shows the file lines
  [Ctrl+O]   → card collapses again
  [Ctrl+Shift+O] → the tool activity block hides entirely
  [Ctrl+Shift+O] → it comes back
› /hotkeys
  app.tools.expand            Ctrl+O
  app.tools.toggleVisibility  Ctrl+Shift+O
  …
```

**Concepts:**
- **What omp needs from the terminal.** The chords omp binds by default (`keybindings.md`): `Ctrl+O` expand card, `Ctrl+Shift+O` hide tool activity, `Ctrl+T` thinking, `Shift+Tab` thinking level, `Ctrl+P` / `Shift+Ctrl+P` cycle models, `Alt+P`, `Alt+M`, `Alt+Shift+P` plan mode, `Ctrl+R`, `Ctrl+G`, `Ctrl+Q` / `Ctrl+Enter` follow-up, `Alt+Up` / `Shift+Up` dequeue, `Alt+R`, `Alt+L`, `Alt+Shift+L`, `Alt+Shift+C`, `Ctrl+Shift+V` / `Alt+Shift+V`, `Ctrl+V`, `Ctrl+L`, `Alt+A`. Anything with `Shift+` on top of `Ctrl`/`Alt`, or `Ctrl+Enter`, requires the terminal to encode modifiers.
- **The two-key test.** `Ctrl+O` works in every terminal. `Ctrl+Shift+O` only works if the terminal encodes Shift alongside Ctrl. If `Ctrl+O` toggles a card but `Ctrl+Shift+O` either does nothing or *also* toggles the card, your terminal is collapsing the chord.
- **`/hotkeys`** prints the active chords for your build, including remaps and extension-added bindings — it is what omp *expects*, so compare it against what you *pressed*.
- **Remapping** lives in `~/.omp/agent/keybindings.yml`: a mapping of action ID → chord (or list of chords; `[]` disables). Chord names are case-insensitive, same notation as the UI. Not read from `config.yml`.
  ```yaml
  # ~/.omp/agent/keybindings.yml
  app.tools.toggleVisibility: Alt+O      # if Ctrl+Shift+O never arrives
  app.message.followUp: [Ctrl+Q]         # drop Ctrl+Enter if the terminal eats it
  ```
- **Per-terminal notes — only what the bundled docs state.** Terminals not listed are not "unsupported"; they are simply not described in the docs, so run the two-key test.
  | Terminal / hop | Documented behavior | What to do |
  |---|---|---|
  | Windows Terminal | May handle `Ctrl+V` before omp sees it; swallows `Ctrl+Enter`. | Image paste: use `Alt+V` (bound on Windows). Follow-up: `Ctrl+Q` is bound for exactly this reason. |
  | VS Code integrated terminal | Delivers `Ctrl+V` to omp only when configured to forward it. | `app.clipboard.pasteImage` pastes text when the clipboard holds no image, so text paste still works. |
  | SSH / container hop that hides a Windows Terminal client | Raw `0x08` may arrive for `Ctrl+Backspace`. | `PI_TUI_RAW_BACKSPACE_IS_CTRL=1` interprets raw `0x08` as `Ctrl+Backspace`. |
  | tmux | Modified keys need tmux `extended-keys`; OSC notifications need `allow-passthrough`. omp asks the tmux server for the outer terminal type. | Enable both in `.tmux.conf`; re-run the two-key test inside the pane. |
  | Warp | Re-reports size on alt-screen toggles; omp repaints in place there by default. | If resize garbles the display: `Alt+L` (reset display), or `PI_TUI_RESIZE_IN_PLACE=0/1` to force a path. |
- **Display, not keys:** `Alt+L` resets the terminal display when output looks corrupted. Double `Ctrl+C` exits omp.

**Try it (Walkthrough):**
1. `cd omp-course-lab && git checkout module-1-start && omp` (if you have not authenticated yet, do Lesson 1.4 first — you need a working model for a tool call).
   **Expected:** the composer appears at the bottom.
2. Type `read README.md and summarize it in one line` and press `Enter`.
   **Expected:** one `read` card followed by a one-line answer.
3. Press `Ctrl+O`.
   **Expected:** the `read` card expands to show file content. Press again: it collapses.
4. Press `Ctrl+Shift+O`.
   **Expected:** the tool activity block disappears. Press again: it returns. If instead the card expands/collapses or nothing happens → your terminal collapsed the chord; go to Troubleshooting.
5. Type `/hotkeys` and press `Enter`.
   **Expected:** a list of action IDs with chords; `app.tools.expand` is `Ctrl+O`, `app.tools.toggleVisibility` is `Ctrl+Shift+O`.
6. Press `Ctrl+C` twice to exit.
   **Expected:** back at the shell.

**Guided task:** Goal: make one chord that your terminal cannot deliver work anyway. Hints: pick the action ID from `/hotkeys`; the file is `~/.omp/agent/keybindings.yml`; restart omp after editing. Checkpoints: (a) `/hotkeys` shows the new chord for the action; (b) the new chord performs the action. Pass: `/hotkeys` lists your remapped chord and pressing it toggles the corresponding UI element. (If every default chord already works, remap `app.tools.toggleVisibility` to `Alt+O` and verify anyway — you will need this skill on the next machine.)

**Stretch:** Goal: run the same two-key test inside tmux and outside it, on the same terminal. Pass: `notes/m1-terminal.txt` records which chords worked in each context and which tmux option (if any) you had to enable.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `Ctrl+O` does nothing at all | you are not in the composer, or no turn has produced a card yet | click/focus the terminal; send a prompt that triggers a `read`; then retry |
| `Ctrl+O` works, `Ctrl+Shift+O` acts like `Ctrl+O` | terminal drops Shift on Ctrl-chords (no modifier encoding) | enable Kitty keyboard protocol / modified-key reporting in the terminal if it offers it; otherwise remap `app.tools.toggleVisibility` in `keybindings.yml` |
| `Ctrl+Enter` does nothing (Windows Terminal) | terminal swallows it | use `Ctrl+Q` (already bound to `app.message.followUp`) |
| `Ctrl+V` image paste does nothing (Windows Terminal) | terminal paste command intercepts it | `Alt+V` |
| Chords stop working inside tmux only | `extended-keys` off | enable `extended-keys` in tmux; `allow-passthrough` for notifications |
| Screen looks garbled after resize | terminal/mux resize handling | `Alt+L`; on Warp try `PI_TUI_RESIZE_IN_PLACE=0` or `=1` |
| A chord you remapped is ignored | wrong file, wrong action ID, or omp not restarted | file must be `~/.omp/agent/keybindings.yml` (not `config.yml`); copy the ID from `/hotkeys` |

**Cheat sheet:**
| Want | Key / command |
|---|---|
| See active chords | `/hotkeys` |
| Expand/collapse a card | `Ctrl+O` |
| Hide/show tool activity | `Ctrl+Shift+O` |
| Reset display | `Alt+L` |
| Exit omp | `Ctrl+C` twice |
| Remap file | `~/.omp/agent/keybindings.yml` (`action.id: Chord` / `[]` to disable) |
| Ctrl+Backspace over odd hops | `PI_TUI_RAW_BACKSPACE_IS_CTRL=1` |

**Source:** omp://keybindings.md, omp://environment-variables.md (`PI_TUI_RAW_BACKSPACE_IS_CTRL`, `PI_TUI_RESIZE_IN_PLACE`), omp://tui-core-renderer.md (tmux `extended-keys` / `allow-passthrough` — internals doc; see BUILD-NOTES), omp://natives-shell-pty-process.md (key parser: legacy, `modifyOtherKeys`, Kitty — internals doc; see BUILD-NOTES)

---

## Lesson 1.4 — Authenticate              (~10 min)
**You will be able to:** (1) log in to one provider with `/login` or `omp login`; (2) prove the credential is stored with `omp token <provider>`; (3) explain where credentials live and in which order omp resolves a key, including the four `.env` files; (4) log out.

**Why this exists:** Nothing happens without a model. omp separates the *provider* (the account: `anthropic`, `openai`, `google`, `ollama`, …) from the *model* (`anthropic/claude-…`), and each provider is authenticated independently. Most providers use OAuth through `/login`; API-key providers work from an environment variable or `.env` with no login at all. You pick **one** provider now. Routing several models and providers is Module 7.

**Demo:** `demos/04-login.md`. Excerpt:

```text
$ omp login anthropic
  (prints the auth URL, opens your browser; paste back if prompted)
$ omp token anthropic | cut -c1-6
sk-ant
$ omp models anthropic | head -3
anthropic (26)
┌────────────────────────────┬─────────┬─────────┬───────────────────────────────┬────────┐
│ model                      │ context │ max-out │ thinking                      │ images │
```

**Concepts:**
- **In a session:** `/login` opens the provider selector (OAuth or key); `/login <provider>` jumps to one (`/login anthropic`); if an OAuth flow gives you a callback URL to paste, run `/login <redirect-url>` to finish it. `/logout` opens the selector to remove stored credentials. Logins are **provider-scoped** — authenticating `anthropic` says nothing about `openai`.
- **From the terminal:** `omp login [PROVIDER]` does the same: prints the auth URL (and opens it), reads any prompts from stdin, saves to the same store. Without an argument it shows a numbered picker. Examples in `omp login --help`: `omp login`, `omp login anthropic`; provider IDs include `anthropic`, `openai-codex`, `github-copilot`, `google-gemini-cli`, `cursor`, …
- **Where it lives:** `~/.omp/agent/agent.db` (the auth store), or the auth-broker snapshot in broker mode (out of scope). `PI_CODING_AGENT_DIR` relocates `~/.omp/agent` and the store moves with it; a `--profile` gets its own `~/.omp/profiles/<name>/agent/agent.db`.
- **Env-var alternative (API-key providers).** Set the provider's variable and skip `/login`: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` (provider `google`), `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `XAI_API_KEY`, `COPILOT_GITHUB_TOKEN`… The full map is in `providers.md`; `omp --help` prints the core ones under "Environment Variables".
- **`.env` lookup order** (first definition wins; an already-set process variable is never overwritten):
  1. process environment (your shell)
  2. `<cwd>/.env`
  3. `~/.omp/agent/.env`
  4. `~/.omp/.env`
  5. `~/.env`
  Parsing is minimal: `#` comments, shell-identifier names only, optional quotes. An `OMP_*` key is mirrored to `PI_*`.
- **Credential precedence when a model needs a key** (first match wins): `--api-key` on the command line → `apiKey` pinned in `models.yml` → stored OAuth → key saved by `/login` → provider env var incl. `.env` → other stored key → `models.yml` fallback. You only need to remember: *an explicit flag beats a file beats a login beats the environment*.
- **Availability rule:** a model is selectable only if its provider is **not** in `disabledProviders` **and** (it is keyless **or** has credentials). Local engines (`ollama`, `llama.cpp`, `lm-studio`) are keyless and appear as soon as they answer — Module 7.
- **Proving it:** `omp token <provider>` prints the stored key/OAuth token (exit 0) or fails; `omp models <provider>` lists that provider's models; `omp usage` shows limits for every authenticated account. `omp token … --list` lists OAuth accounts when you have more than one.

**Try it (Walkthrough):**
1. Choose one provider. OAuth (recommended): `omp login anthropic` (or `omp login openai-codex`, `omp login github-copilot`). API key: `export ANTHROPIC_API_KEY=…` (or the variable for your provider) and skip to step 3.
   **Expected:** the browser opens (or a URL is printed); after consent the command returns without error.
2. `omp token <provider> | cut -c1-6`
   **Expected:** the first six characters of a credential, exit code 0. (`omp token` prints the whole secret — never paste its output anywhere.)
3. `omp models <provider>`
   **Expected:** a table of models with `context`, `max-out`, `thinking`, `images` columns.
4. `omp usage --provider <provider>`
   **Expected:** a usage/limits report for your account (API-key providers may show no quota windows — that is fine).
5. Start `omp` in the lab, type `/logout`, pick your provider, confirm; then `omp token <provider>`.
   **Expected:** `omp token` now fails (non-zero exit). Log back in with `/login <provider>` or `omp login <provider>` before Lesson 1.5.

**Guided task:** Goal: make the lab repo use a key from a project `.env` while your shell has none, then prove which source won. Needs an API-key provider (e.g. `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`); OAuth-only learners use any key-based provider you have access to — the key does not need to be valid for `omp token` to report it. Hints: `.env.example` in the lab shows the file shape (its `labtok_…` token is fake — do not use it as a real key); `<cwd>/.env` outranks `~/.env`; `omp token <provider>` prints what will be used, and from a directory with no `.env` prints `No active credential found for provider "<id>".` plus `Configured providers: …`; `git status` must not show `.env` (it is gitignored). Checkpoints: (a) `env | grep -c _API_KEY` is `0` in your shell; (b) `omp token <provider>` from inside `omp-course-lab` prints the `.env` value; (c) from `cd /tmp` it exits non-zero. Pass: (b) and (c) both hold and `git status --short` does not list `.env`.

**Stretch:** Goal: log in to a *second* provider and show both are stored independently. Pass: `omp token <a>` and `omp token <b>` both exit 0 and `omp usage` lists both accounts.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| Browser never opens during `/login` | headless/remote box or blocked handler | `omp login <provider>` prints the URL — open it elsewhere; if the flow hands you a callback URL, paste it as `/login <redirect-url>` |
| `No active credential found for provider "<id>".` (`omp token`), or omp tells you to run `/login` / set the provider's environment variable | provider not authenticated | `/login <provider>` or export the env var from the `providers.md` map; the `omp token` message also lists `Configured providers:` so you can see which ones *are* set up |
| Model is missing from `/model` or `omp models` | provider disabled, or no credentials | `omp config get disabledProviders`; remember: not disabled **and** (keyless or credentialed) |
| Wrong/stale key is used | a higher-precedence source wins (`--api-key`, `models.yml`, stored OAuth, exported shell var, `<cwd>/.env`) | walk the precedence list; `unset` the shell var or remove the file entry |
| `/login` for `google` does nothing useful | `google` is the Gemini *API* (key) provider; OAuth Google is `google-gemini-cli` / `google-antigravity` | `omp login google-gemini-cli`, or `export GEMINI_API_KEY=…` |
| Logged in, but a different account/org is picked | multiple OAuth accounts rotate | `omp token <provider> --list`; `--account N` to pick |

**Cheat sheet:**
| Want | Command |
|---|---|
| Log in (session / shell) | `/login [provider]` · `omp login [provider]` |
| Finish a pasted OAuth callback | `/login <redirect-url>` |
| Log out | `/logout` |
| Prove credential | `omp token <provider>` |
| List provider models | `omp models <provider>` |
| Account limits | `omp usage [--provider p]` |
| Key by env | `export ANTHROPIC_API_KEY=…` (or `OPENAI_API_KEY`, `GEMINI_API_KEY`, …) |
| `.env` order | shell env › `<cwd>/.env` › `~/.omp/agent/.env` › `~/.omp/.env` › `~/.env` |
| Store | `~/.omp/agent/agent.db` |

**Source:** omp://providers.md, omp://environment-variables.md, `omp login --help`, `omp token --help`, `omp usage --help`, `omp models --help`

---

## Lesson 1.5 — First prompt              (~12 min)
**You will be able to:** (1) start omp in the practice repo and run a bug-fix prompt that ends in one changed file; (2) read the cards well enough to confirm the check ran; (3) use the three other launch forms — initial-prompt argument, `@file` attachment, and stdin/`-p` — and know which one to reach for.

**Why this exists:** The first prompt teaches the shape of every later one: an *outcome* ("fix issue #1"), a *constraint* ("smallest safe fix") and a *verification* ("run the tests"). You get to watch the loop from Lesson 1.1 happen for real, and you get the observable that this whole module is graded on: `git diff --stat` shows exactly one file.

**Demo:** `demos/05-first-prompt.md`. Excerpt (headless form, real output from the build machine):

```text
$ omp -p --no-session "List the top-level directories and what each is for"
Working...                                   ← stderr; stdout is only the answer
The repo is a small Python practice lab …
| `api/` | An HTTP service built on the standard library's `http.server`, storing data in SQLite | …
| `cli/` | A command-line client built with `argparse` | …
| `generated/` | Machine-generated output that should not be hand-edited | …
```

**Concepts:**
- **Launch forms** (`omp --help`, `cli-reference.md`). When the first non-flag argument is not a subcommand it becomes the initial prompt:
  | Form | What happens |
  |---|---|
  | `omp` | interactive TUI, empty composer |
  | `omp "text"` | interactive TUI, `text` sent as first message |
  | `omp @docs/ISSUES.md @shot.png "question"` | `@path` attaches files/images to the first message |
  | `omp -p "text"` | print mode: answer on stdout, exit; progress (`Working...`) on stderr |
  | `echo "text" \| omp -p` | non-TTY stdin is read as the prompt automatically — no `-` marker |
  | `omp -- "--looks-like-a-flag"` | `--` ends flag parsing; the rest is literal message text |
- **Sessions are saved** under `~/.omp/agent/sessions/<encoded-cwd>/<timestamp>_<sessionId>.jsonl` — one bucket per working directory. `--no-session` makes a run ephemeral. Module 5 covers resume/fork.
- **Starting in `~`** auto-switches omp to a temp dir; `--allow-home` overrides. Always start in the repo.
- **During a turn:** `Esc` aborts the running turn (and clears the draft when nothing is running); `Ctrl+C` clears the composer, `Up` recalls the cleared draft; `Ctrl+C` twice exits.
- **Reading the result:** every tool call is a card. For this prompt expect `read`/`grep` cards (investigation), an `edit` card (the fix), and a `bash` card running the test command. The final message is only as trustworthy as the cards above it — if there is no `bash` card, the check did not run (Module 3.5 makes a habit of this).
- **The prompt you will use** (course-authored, modeled on the outline's quickstart):
  > Read `docs/ISSUES.md` and locate issue #1. Inspect the code it points at for one small bug. Make the smallest safe fix — touch only the file that contains the bug. Then run `python -m unittest discover -s tests` and show me the result.

**Try it (Walkthrough):**
1. `cd omp-course-lab && git checkout module-1-start && git status --short`
   **Expected:** `HEAD` at `module-1-start`, clean tree (nothing printed by `--short`).
2. `omp`
   **Expected:** the TUI with an empty composer and a status line at the bottom (`statusLine.preset` controls its segments; Module 2 reads it in detail).
3. Paste the prompt above and press `Enter`. Watch the cards.
   **Expected:** a `read` card for `docs/ISSUES.md`, one or more `read`/`grep` cards, one `edit` card, one `bash` card whose command contains `unittest`, then a final message saying the tests pass.
4. Press `Ctrl+O` to expand tool output and look at the `bash` card.
   **Expected:** the expanded card shows `OK` from unittest (or `Ran N tests … OK`).
5. `Ctrl+C` twice to exit, then `git diff --stat`.
   **Expected:** exactly one file with a small `+/-` count. This is the module's pass condition.
6. Try the attachment form: `omp @docs/ISSUES.md "Which of these issues is the smallest? One line."`
   **Expected:** the TUI opens with the attachment shown in your first message; the answer names an issue. A `read` card is unnecessary because the file content travelled with the message (the model may still read for context). Exit.
7. Try print mode: `omp -p --no-session "Reply with exactly the word OK"`
   **Expected:** stdout `OK`, stderr `Working...`, exit 0.
8. Try stdin: `echo "Reply with exactly the word PIPED" | omp -p --no-session`
   **Expected:** `PIPED`.

**Guided task:** Goal: capture a headless repo overview to `notes/m1.txt` with only the answer in the file. Hints: print mode writes the answer to stdout and progress to stderr; `>` redirects stdout only; `--no-session` keeps the session list clean. Checkpoints: (a) `notes/m1.txt` exists; (b) it does not contain `Working...`; (c) it mentions both `api/` and `cli/`. Pass: `grep -c 'api/' notes/m1.txt` and `grep -c 'cli/' notes/m1.txt` are both ≥ 1 and `grep -c Working notes/m1.txt` is `0`.

**Stretch:** Goal: run the fix prompt again from a clean checkout in print mode with `--mode json` and find the `edit` tool call in the event stream. Pass: `git checkout -- . && git checkout module-1-start` first; afterwards `git diff --stat` shows one file **and** `grep -c '"edit"' notes/m1-events.json` ≥ 1.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| omp starts in `/tmp/…` instead of the repo | you launched from `~` | `cd omp-course-lab` first, or `--allow-home` if you really meant `~` |
| "no credentials" / model error on the first turn | Lesson 1.4 not done | `/login <provider>` |
| Final message says "fixed" but no `bash` card | the model skipped the check | reply: "You did not run the tests. Run `python -m unittest discover -s tests` and show the output." |
| `git diff --stat` shows two or more files | the model widened scope | `git checkout -- <extra file>`; next time keep "touch only the file that contains the bug" in the prompt (Module 3) |
| Piped prompt does nothing and omp waits | you added a `-` argument or forgot `-p` | `echo "…" \| omp -p` — no `-`; without `-p` a non-TTY stdin still becomes the prompt but omp tries to open the TUI |
| Print run's file contains `Working...` | you redirected `2>&1` | redirect stdout only (`> file`) or add `2>/dev/null` |

**Cheat sheet:**
| Want | Command / key |
|---|---|
| Start in repo | `cd repo && omp` |
| Initial prompt | `omp "…"` |
| Attach file/image | `omp @path "…"` |
| Headless | `omp -p "…"` · `echo "…" \| omp -p` |
| Ephemeral | `--no-session` |
| Literal text after flags | `omp -- "…"` |
| Abort turn | `Esc` |
| Exit | `Ctrl+C` `Ctrl+C` |
| Module pass check | `git diff --stat` → one file |

**Source:** omp://cli-reference.md, omp://session.md (on-disk layout), omp://keybindings.md (`Esc`, `Ctrl+C`, draft recall), `omp --help`

---

## Lesson 1.6 — The config root              (~8 min)
**You will be able to:** (1) print the active agent directory and name what each entry in it is for; (2) read and write one setting with `omp config`; (3) explain profiles in one sentence; (4) run `omp setup` checks.

**Why this exists:** Every later module writes something under `~/.omp/agent/` — settings, custom providers, skills, agents, extensions — or under the repo's `.omp/`. Knowing the map now means Modules 6–12 are "put the file here" instead of "where does this go?". Settings have a strict layering; today you only need the two ends of it: the global file and the project file.

**Demo:** `demos/06-config-root.md`. Excerpt (real listing from the build machine):

```text
$ omp config path
/home/user/.omp/agent
$ ls -1p ~/.omp/agent/
agent.db          ← credentials (Lesson 1.4)
blobs/            ← large tool outputs (artifact://, Module 2)
cache/
config.yml        ← global settings
history.db        ← prompt history (Ctrl+R)
models.db         ← cached model catalog (omp models refresh)
sessions/         ← one bucket per cwd (Module 5)
terminal-sessions/
$ omp config get tools.approvalMode
yolo
$ omp config get startup.showSplash
false
```

**Concepts:**
- **`omp config path`** prints the active agent directory (honors `PI_CODING_AGENT_DIR`). Default `~/.omp/agent`; with `--profile <name>` / `OMP_PROFILE`, `~/.omp/profiles/<name>/agent`.
- **Tour of `~/.omp/agent/`** (files you create appear when you create them):
  | Entry | Purpose | Module |
  |---|---|---|
  | `config.yml` | global settings; canonical write target of `/settings`, `omp config set/reset` | 6 |
  | `models.yml` | custom providers/models (`models.yaml` also accepted) | 7 |
  | `agent.db` | auth store (OAuth + login-saved keys) | 1 |
  | `.env` | agent-level env file (3rd in the `.env` order) | 1 |
  | `keybindings.yml` | chord remaps by action ID | 1 |
  | `sessions/<encoded-cwd>/*.jsonl` | saved sessions | 5 |
  | `skills/<name>/SKILL.md` | user-level skills | 6, 9 |
  | `extensions/` | user-level extensions/hooks | 12 |
  | `agents/*.md` | user-level custom task agents | 10 |
  | `AGENTS.md`, `RULES.md`, `SYSTEM.md` | user-level context/rules/prompt | 6 |
  | `blobs/`, `history.db`, `models.db`, `cache/` | runtime state (artifacts, prompt history, model catalog cache) | 2, 7 |
- **Sibling `~/.omp/`** holds `profiles/`, `plugins/`, `logs/`, `stats.db`, `.env` (4th in order), `wt/` (agent worktrees). Legacy `settings.json` is migrated into `config.yml` once and renamed `.bak`.
- **`omp config`** (`omp config --help`; `settings.md`):
  | Command | Effect |
  |---|---|
  | `omp config list [--json]` | every setting, grouped, with effective value and type — the authoritative key list |
  | `omp config get <key>` | one effective value; unknown key exits non-zero |
  | `omp config set <key> <value>` | parse against schema, write **global** `config.yml`; warns if another layer still overrides |
  | `omp config reset <key>` | delete from global file so lower layers/default apply |
  | `omp config path` | active agent directory |
  | `omp config init-xdg` | create XDG data/state/cache dirs (Linux/macOS) |
  `/settings` inside a session edits the same global file through a panel. Keys must be full schema paths (`theme.dark`, not `theme`).
- **Layering (preview; full treatment in Module 6.7):** env var on the definition › runtime override › `--config` overlays / `PI_CONFIG_FILES` › project `<cwd>/.omp/config.yml` (+ `settings.json`) › global `~/.omp/agent/config.yml` › default. Project settings are read only when `<cwd>/.omp/` is **non-empty** — the lab's `.omp/` is empty at `module-1-start` on purpose. `omp config set` never writes the project file; edit `<repo>/.omp/config.yml` by hand.
- **Two defaults to know now:** `tools.approvalMode` is `yolo` (auto-approve everything — Module 4 changes this); `startup.showSplash` is `false`.
- **Profiles:** `omp --profile work` isolates auth, sessions, settings and caches under `~/.omp/profiles/work/agent/`; `OMP_PROFILE=work` does the same; `omp --profile work --alias omp-work` creates a shell shortcut. Keybindings are the one thing a profile inherits from the default profile.
- **`omp setup`:** with no component it runs onboarding setup; `omp setup python --check` reports the interpreter used by the Python eval backend; `omp setup speech` selects and downloads local speech/dictation models (Module 7). `--check`/`--json` require a component.

**Try it (Walkthrough):**
1. `omp config path`
   **Expected:** `/home/<you>/.omp/agent` (macOS: `/Users/<you>/.omp/agent`).
2. `ls -1p "$(omp config path)"`
   **Expected:** at least `agent.db`, `config.yml`, `sessions/`.
3. `omp config get tools.approvalMode`
   **Expected:** `yolo`.
4. `omp config set startup.showSplash true && omp config get startup.showSplash`
   **Expected:** `✔ Set startup.showSplash = true` then `true`; `grep -n -A1 startup "$(omp config path)/config.yml"` shows a `startup:` block with `showSplash: true`.
5. `omp config reset startup.showSplash && omp config get startup.showSplash`
   **Expected:** `✔ Reset startup.showSplash to false` then `false`; the `grep` above finds nothing.
6. `omp setup python --check`
   **Expected:** `Python: /usr/bin/python3` (or your path) and `✔ Python execution is ready`.
7. `omp config list | grep -c .`
   **Expected:** a number in the hundreds — this is why you use `get`.

**Guided task:** Goal: create an isolated profile called `course`, confirm it has its own agent directory and its own (empty) auth store, then go back. Hints: `--profile` accepts any subcommand that reads config; `omp --profile course config path`; `omp --profile course token <provider>` should fail. Checkpoints: (a) `omp --profile course config path` ends in `/profiles/course/agent`; (b) that directory exists after the first run; (c) `omp --profile course token <provider>` exits non-zero. Pass: (a) and (c).

**Stretch:** Goal: relocate the whole agent directory for one command with `PI_CODING_AGENT_DIR`, and show `omp config path` follows it. Pass: `PI_CODING_AGENT_DIR=/tmp/omp-alt omp config path` prints `/tmp/omp-alt`.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `omp config set` says another source overrides the value | env var, project file, `--config` overlay, or runtime override wins | the message names it (`overriddenBy` in `--json`); fix that layer |
| `Unknown setting` on `set` | not a full schema path | `omp config list` and copy the exact key |
| Project `.omp/config.yml` is ignored | not valid YAML / top level not a mapping, or you launched from a parent or sibling directory — settings discovery does **not** walk ancestors | `cd` into the directory that contains `.omp/`; validate the YAML; `omp config get <key>` from there |
| Startup fails naming a `.broken-…` file | invalid global/project YAML was quarantined | fix the original, delete the backup |
| Profile does not see your logins | profiles have separate `agent.db` by design | `omp --profile <name> login <provider>` |

**Cheat sheet:**
| Want | Command |
|---|---|
| Agent dir | `omp config path` |
| Read / write / reset a key | `omp config get k` · `omp config set k v` · `omp config reset k` |
| All keys | `omp config list [--json]` |
| In-session panel | `/settings` |
| Isolated profile | `omp --profile NAME …` · `OMP_PROFILE=NAME` · `--alias CMD` |
| Relocate agent dir | `PI_CODING_AGENT_DIR=/path` |
| Onboarding / checks | `omp setup` · `omp setup python --check` · `omp setup speech` |

**Source:** omp://settings.md, omp://config-usage.md, omp://providers.md (`agent.db`, `.env`), omp://models.md (`models.yml`), omp://session.md, omp://keybindings.md, omp://task-agent-discovery.md (`agents/`), omp://skills/authoring-extensions.md (`extensions/`), omp://python-repl.md (`omp setup python --check`), omp://local-models.md (`omp setup speech`), `omp config --help`, `omp setup --help`

---

## Lesson 1.7 — The CLI surface              (~7 min)
**You will be able to:** (1) find any flag or subcommand with `omp --help` / `omp <cmd> --help` and the bundled docs via `omp read omp://…`; (2) recognize the subcommands the course will use and say which module teaches each; (3) run the two housekeeping commands safely.

**Why this exists:** omp is one binary with a large surface. The habit that keeps you productive is not memorizing it — it is knowing that `--help` and `omp read omp://` are always one command away and always match your build. This lesson names the subcommands once so later modules can use them without re-introduction.

**Demo:** `demos/07-cli-surface.md`. Excerpt:

```text
$ omp gc
GC dry-run (/home/user/.omp/agent)
blobs: 0/2 files, 20.0KB, 28 refs
sessions: 0/11 archived, 0 history rows and 0 stats rows removed
sessions skipped active: 3
wal: checkpoint dry-run, 165.0KB across 2 dbs
$ omp read omp://keybindings.md:1-3
# Keybindings

Run `/hotkeys` inside an `omp` session to see the active chords for your current build. …
```

**Concepts:**
- **Routing rule.** `omp [command] [flags] [messages…]`. If the first non-flag argument is a registered subcommand, that runs; otherwise `omp` runs the default `launch` command and the arguments are the prompt. So `omp models` lists models; `omp "models"` asks the model about models.
- **Help everywhere.** `omp --help` (launch flags + subcommand list), `omp <cmd> --help` (that command's flags and examples), `omp config` with no action lists settings. `omp read omp://` prints the doc index; `omp read omp://<file>[:N-M]` prints a doc or a line range — the same text this course was verified against.
- **Subcommands the course uses** (from `omp --help` COMMANDS; one line each, taught where listed):
  | Command | Purpose | Module |
  |---|---|---|
  | `omp models [ls\|find\|refresh\|<provider>]` | list/search/refresh the model catalog; `--kind`, `--json` | 1, 7 |
  | `omp config list\|get\|set\|reset\|path` | settings | 1, 6 |
  | `omp login [provider]` · `omp token <provider>` · `omp usage` | auth and account limits | 1, 7 |
  | `omp setup [python\|speech] [--check]` | onboarding / optional deps | 1, 7, 8 |
  | `omp completions bash\|zsh\|fish` | shell completion script | 1 |
  | `omp update [--check\|--canary\|--stable]` | upgrade | 1 |
  | `omp gc [--apply]` | storage garbage collection (dry-run by default) | 1 |
  | `omp read <path\|url\|uri>` | what the `read` tool would return | 1, 8 |
  | `omp commit` | generate commit message, update changelogs (atomic split) | 4 |
  | `omp git` | fullscreen git UI: split diff, staging, commit composer | 4 |
  | `omp worktree` (`wt`) | add/list/clear agent-managed worktrees | 5, 10 |
  | `omp stats` · `omp usage` | usage statistics / provider limits | 7 |
  | `omp tiny-models list\|download` | tiny local models (titles, memory) | 7 |
  | `omp plugin …` · `omp install` | plugins, marketplaces | 12 |
  | `omp agents unpack [--project]` | export bundled subagent definitions | 10 |
  | `omp share` · `omp collab` · `omp join` · `omp stream` · `omp play` · `omp clip` | sharing, live collaboration, recordings | 5, 14 |
  | `omp ttsr` | inspect/test Time-Traveling Stream Rules | 11 |
  | `omp search` / `omp q` / `omp web-search` | test web-search providers | 8 |
  | `omp find "<query>"` | semantic search: behavior → files and line ranges | 8 |
  | `omp acp` | ACP server over stdio | 13 |
  | `omp ps` | daemon-supervised background processes | 2 |
- **Housekeeping.**
  - `omp update` — see 1.2. `omp update --check` never installs.
  - `omp gc` is a **dry-run by default**; `omp gc --apply` applies. Options: `--blobs` (sweep unreferenced blobs), `--archive` (archive cold sessions), `--wal` (checkpoint DB WAL files), `--cold-archive-after-days N`, `--retain-newest-global N`, `--retain-newest-per-cwd N`, `--agent-dir`, `--json`. Run the dry-run and read it before `--apply`.

**Try it (Walkthrough):**
1. `omp models --help`
   **Expected:** ACTION `ls (default) | find | refresh | <provider>`, and the example `omp models find minimax`.
2. `omp gc`
   **Expected:** `GC dry-run (<agent dir>)` followed by `blobs:`, `sessions:`, `wal:` lines. Nothing is changed.
3. `omp read omp:// | head -20`
   **Expected:** `# Documentation`, `134 files available:` and the first entries of the index.
4. `omp read omp://cli-reference.md | grep -n "^| \`" | head -5`
   **Expected:** table rows starting with backticked flags/commands — you have found the flag tables.
5. `omp "models"` — *do not* press Enter on anything; just observe, then `Ctrl+C` twice.
   **Expected:** the TUI opens with `models` as the first message: an argument that is not a subcommand is a prompt.

**Guided task:** Goal: build your own one-page index of the subcommands with their one-line purposes, straight from the binary. Hints: `omp --help` has a `COMMANDS` block; `sed -n '/^COMMANDS/,/^Environment/p'` isolates it; save to `notes/m1-commands.txt`. Checkpoints: (a) the file has ≥ 40 command lines; (b) it contains `worktree` and `ttsr`. Pass: `grep -c -e '^  worktree' -e '^  ttsr' notes/m1-commands.txt` prints `2`.

**Stretch:** Goal: run `omp gc --wal --apply` (WAL checkpoint only — safe; `--wal` restricts the sweep to that step) and compare its output with `omp gc --wal`. Pass: the applied run prints `GC applied (<agent dir>)` and `wal: checkpointed, …` instead of `GC dry-run` / `checkpoint dry-run`, and `omp` still starts afterwards.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `omp <word>` opened the TUI instead of running a command | `<word>` is not a registered subcommand | check spelling against `omp --help` COMMANDS |
| `omp gc` "did nothing" | it is a dry-run | `omp gc --apply` after reading the dry-run |
| `omp read omp://x.md` says file not found | wrong name | `omp read omp://` lists all 134 files; the error also suggests close matches |
| `omp update --check` errors with rate limit | GitHub API quota | `GITHUB_TOKEN=… omp update --check` |

**Cheat sheet:**
| Want | Command |
|---|---|
| Launch flags + commands | `omp --help` |
| One command's flags | `omp <cmd> --help` |
| Docs index / one doc / range | `omp read omp://` · `omp read omp://cli-reference.md` · `omp read omp://keybindings.md:1-40` |
| Upgrade | `omp update` (`--check` to look only) |
| Garbage collect | `omp gc` (dry-run) → `omp gc --apply` |
| Model catalog | `omp models` · `omp models find <substr>` · `omp models refresh` |

**Source:** omp://cli-reference.md, `omp --help`, `omp gc --help`, `omp update --help`, `omp models --help`, `omp read --help`

---

## Module pass conditions (summary)

| Tier | Task | Observable |
|---|---|---|
| W | install → `omp --version` → `/login` → fix issue #1 → check | `omp --version` prints a version; `omp token <provider>` exits 0; `git diff --stat` shows exactly one file |
| G | `omp -p "List the top-level directories and what each is for" > notes/m1.txt` | file exists, mentions `api/` and `cli/`, no `Working...` line |
| S | shell completions | `omp --res<Tab>` → `--resume` |

Full coursework with hints and pass commands: `exercises.md`. Instructor notes: `solutions/`.

Next: **Module 2 — Anatomy of a Turn** (`Ctrl+O`, `Ctrl+Shift+O`, `Ctrl+T`, `/hotkeys`, and every default tool's card).
