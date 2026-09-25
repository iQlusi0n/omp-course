# Demo 1.1 — `omp --help` (real output, `omp/18.3.1`, ~45 s)

What to notice: one binary, three things in it — launch **flags**, **subcommands**, and the **tool list** the model can call. `-p` and `--mode` are the entry-point switches; `acp` is the fourth entry point.

```text
$ omp --help
omp v18.3.1

USAGE
  $ omp [COMMAND]

ARGUMENTS
  MESSAGES   Messages to send (prefix files with @)

FLAGS
      --model=<value>                   Model to use (fuzzy match: "opus", "gpt-5.2", or "openai/gpt-5.2")
      --smol=<value>                    Smol/fast model for lightweight tasks (or PI_SMOL_MODEL env)
      --slow=<value>                    Slow/reasoning model for thorough analysis (or PI_SLOW_MODEL env)
      …
      --mode=<value>                    Output mode: text (default), json, rpc, or rpc-ui
      --config=<value>                  Load an extra config.yml-style overlay for this run (repeatable)
      --add-dir=<value>                 Add a workspace directory beyond the working directory (repeatable)
  -p, --print                           Non-interactive mode: process prompt and exit
  -c, --continue                        Continue previous session
      …

EXAMPLES
  # Interactive mode
    omp
  # Interactive mode with initial prompt
    omp "List all .ts files in src/"
  # Include files in initial message
    omp @prompt.md @image.png "What color is the sky?"
  # Non-interactive mode (process and exit)
    omp -p "List all .ts files in src/"
  # Continue previous session
    omp --continue "What did we discuss?"
  # Create a shell shortcut for a work profile
    omp --profile work --alias omp-work
  …

COMMANDS
  acp            Run omp as an ACP (Agent Client Protocol) server over stdio
  agents         Manage bundled task agents
  …
  commit         Generate a commit message and update changelogs
  completions    Print a shell completion script (bash, zsh, or fish)
  config         Manage configuration settings
  find           Semantic search: describe a behavior, get the files and line ranges that implement it
  gc             Run storage garbage collection
  git            Interactive fullscreen git UI: split diff viewer, staging sidebar, and commit composer
  login          Log in to a model provider (terminal counterpart of /login)
  models         List, search, and refresh available models
  plugin         Manage plugins (install, uninstall, list, etc.)
  read           Show what the read tool will return for a path, URL, or internal URI
  setup          Run onboarding setup or install dependencies for optional features
  share          Share a saved session via an encrypted link (same as /share)
  stats          View usage statistics
  tiny-models    Download tiny local models (session titles + memory)
  token          Get the API key or OAuth token for a provider
  ttsr           Inspect and test Time-Traveling Stream Rules (TTSR)
  update         Check for and install updates
  usage          Show provider usage limits for every authenticated account
  worktree       Add, list, or clear git worktrees (clone-first when enabled)
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

The `…` marks lines cut for length; nothing was reordered. `omp --help` on your machine is the authority — if it differs, your version differs.

The one `--mode` value the short help omits:

```text
$ omp read omp://cli-reference.md | grep -n '^| `acp`'
…| `acp` | Agent Client Protocol server over stdio. Equivalent to the `acp` subcommand …
```
