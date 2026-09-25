# Demo 1.3 — The two-key terminal check (~50 s)

TUI rendering below is **illustrative** (no recording could be made on the build machine): card glyphs, borders and colors depend on theme, `symbolPreset` and terminal. The chords, action IDs and the `/hotkeys` names are from `keybindings.md` and are exact.

`›` = what you type into the composer. `[Key]` = a key press.

```text
$ cd omp-course-lab && omp

› read README.md and summarize it in one line

  ▸ read README.md                                  ← collapsed tool card
  omp-course-lab is a small Python practice repo with an API, a CLI and seeded issues.

[Ctrl+O]
  ▾ read README.md
  │ 1: # omp-course-lab
  │ 2: Python-only practice repo.                    ← card expanded: file lines visible
  │ …
[Ctrl+O]
  ▸ read README.md                                  ← collapsed again

[Ctrl+Shift+O]
  omp-course-lab is a small Python practice repo …  ← tool activity hidden; only prose remains
[Ctrl+Shift+O]
  ▸ read README.md                                  ← tool activity back

› /hotkeys
  app.model.cycleForward       Ctrl+P
  app.model.cycleBackward      Shift+Ctrl+P
  app.model.selectTemporary    Alt+P
  app.model.select             Alt+M
  app.plan.toggle              Alt+Shift+P
  app.history.search           Ctrl+R
  app.tools.expand             Ctrl+O
  app.tools.toggleVisibility   Ctrl+Shift+O
  app.thinking.toggle          Ctrl+T
  app.thinking.cycle           Shift+Tab
  app.editor.external          Ctrl+G
  app.message.followUp         Ctrl+Q, Ctrl+Enter
  app.message.dequeue          Alt+Up, Shift+Up
  app.retry                    Alt+R
  app.display.reset            Alt+L
  …

[Ctrl+C] [Ctrl+C]
$
```

## What a broken chord looks like

Same session, a terminal that does not encode `Shift` on `Ctrl` chords:

```text
[Ctrl+O]
  ▾ read README.md            ← works
[Ctrl+Shift+O]
  ▸ read README.md            ← WRONG: it collapsed the card (omp received plain Ctrl+O)
```

Fix without changing terminals — remap the action to a chord that arrives intact, then restart omp:

```text
$ cat > ~/.omp/agent/keybindings.yml <<'EOF'
app.tools.toggleVisibility: Alt+O
EOF
$ omp
› /hotkeys
  …
  app.tools.toggleVisibility   Alt+O
  …
[Alt+O]
  (tool activity hidden)
```

Inside tmux, before remapping, enable modified-key reporting in `~/.tmux.conf` and re-test. The option names (`extended-keys`, `allow-passthrough`) are the ones omp's docs reference; the `set` syntax is tmux's — confirm against `man tmux` for your version:

```text
set -s extended-keys on
set -g allow-passthrough on     # for OSC notifications, not keys
```
