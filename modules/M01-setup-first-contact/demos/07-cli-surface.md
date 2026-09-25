# Demo 1.7 — Help, docs, and housekeeping from the shell (~45 s)

All real output, `omp/18.3.1`.

## Help is per-command

```text
$ omp models --help
List, search, and refresh available models

USAGE
  $ omp models [ACTION] [PATTERN] [FLAGS]

ARGUMENTS
  ACTION    ls (default) | find | refresh | <provider>
  PATTERN   Filter/search substring, or provider name (required for find)

FLAGS
      --json               Output JSON
      --kind=<value>       Catalog kind to list
  …
EXAMPLES
  # List available chat models, grouped by provider
    omp models
  # List one provider's models (any provider name works)
    omp models openai-codex
  # Find models by substring
    omp models find minimax
  # Force a fresh catalog fetch (replaces rm -rf ~/.omp/models.db)
    omp models refresh

$ omp models find haiku
anthropic (3)
┌───────────────────────────┬─────────┬─────────┬───────────────────────────────┬────────┐
│ model                     │ context │ max-out │ thinking                      │ images │
├───────────────────────────┼─────────┼─────────┼───────────────────────────────┼────────┤
│ claude-3-haiku-20240307   │    200K │    4.1K │ -                             │ yes    │
│ claude-haiku-4-5          │    200K │     64K │ minimal,low,medium,high,xhigh │ yes    │
│ claude-haiku-4-5-20251001 │    200K │     64K │ minimal,low,medium,high,xhigh │ yes    │
└───────────────────────────┴─────────┴─────────┴───────────────────────────────┴────────┘
```

## The bundled docs, without a session

```text
$ omp read omp:// | head -8
# Documentation

134 files available:

- [ERRATA-GPT5-HARMONY.md](omp://ERRATA-GPT5-HARMONY.md)
- [adding-a-provider.md](omp://adding-a-provider.md)
- [advisor-watchdog.md](omp://advisor-watchdog.md)
- [agent-hub.md](omp://agent-hub.md)

$ omp read omp://keybindings.md:1-3
# Keybindings

Run `/hotkeys` inside an `omp` session to see the active chords for your current build. …

$ omp read omp://keybinding.md
Documentation file not found: keybinding.md
Did you mean: keybindings.md
```

## Housekeeping

```text
$ omp update --check
Current version: 18.3.1
✔ Already up to date

$ omp gc                                   ← dry-run by default
GC dry-run (/home/user/.omp/agent)
blobs: 0/2 files, 20.0KB, 28 refs
sessions: 0/11 archived, 0 history rows and 0 stats rows removed
sessions skipped active: 3
wal: checkpoint dry-run, 165.0KB across 2 dbs

$ omp gc --wal                             ← a flag narrows the sweep
GC dry-run (/home/user/.omp/agent)
wal: checkpoint dry-run, 430.5KB across 2 dbs

$ omp gc --wal --apply
GC applied (/home/user/.omp/agent)
wal: checkpointed, 0B across 2 dbs
```

## Routing rule, demonstrated

```text
$ omp models          → runs the `models` subcommand (table above)
$ omp "models"        → opens the TUI with the message "models" (Ctrl+C twice to leave)
$ omp -- --help       → opens the TUI with the message "--help": `--` ends flag parsing
```
