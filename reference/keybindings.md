# Keybindings — default chords and action IDs

Verified against `omp://keybindings.md`, `omp://agent-hub.md`, `omp://tree.md` and module cheat sheets (course pinned to omp 18.3.1). `/hotkeys` inside a session is always the authority for *your* build: it shows remaps and extension-added bindings.

## Remapping

| Fact | Value |
|---|---|
| File | `~/.omp/agent/keybindings.yml` (a `keybindings.json` / `keybindings.yaml` is accepted and migrated). **Not** inside `config.yml`; there is no nested `keybindings` object. |
| Shape | `action.id: Chord` or `action.id: [Chord, Chord]`; chord names are case-insensitive (`Ctrl+P`, `Alt+Shift+P`, `Shift+Enter`, `Ctrl+Backspace`) |
| Disable | `action.id: []` |
| Profiles | default profile's `keybindings.yml` loads first; the active profile's file overrides per action (the only user file profiles inherit) |
| Old names | unqualified legacy action names are migrated on load; write namespaced IDs |
| Live view | `/hotkeys` |

Example:

```yaml
app.model.cycleForward: Ctrl+P
app.plan.toggle: Alt+Shift+P
app.history.search: []
```

## Action IDs (defaults)

| Action ID | Default chord | Does | Module |
|---|---|---|---|
| `app.model.cycleForward` | `Ctrl+P` | cycle role models forward (`cycleOrder`, default `smol, default, slow`) | M7 |
| `app.model.cycleBackward` | `Shift+Ctrl+P` | cycle role models backward | M7 |
| `app.model.selectTemporary` | `Alt+P` | pick a temporary model; roles untouched | M7 |
| `app.model.select` | `Alt+M` | model selector, assign roles (same as `/model`) | M7 |
| `app.plan.toggle` | `Alt+Shift+P` | toggle plan mode | M4 |
| `app.history.search` | `Ctrl+R` | search prompt history | M2 |
| `app.tools.expand` | `Ctrl+O` | expand/collapse tool cards | M1, M2 |
| `app.tools.toggleVisibility` | `Ctrl+Shift+O` | hide/show tool activity (`display.hideToolActivity`) | M1, M2 |
| `app.thinking.toggle` | `Ctrl+T` | show/hide thinking blocks (`hideThinkingBlock`) | M2, M3 |
| `app.thinking.cycle` | `Shift+Tab` | cycle thinking level for the session | M3 |
| `app.editor.external` | `Ctrl+G` | edit the draft in `$VISUAL` / `$EDITOR` | M2 |
| `app.message.followUp` | `Ctrl+Q`, `Ctrl+Enter` | queue a follow-up (`followUpMode`); `Ctrl+Q` exists because Windows Terminal swallows `Ctrl+Enter` | M2, M3 |
| `app.message.dequeue` | `Alt+Up`, `Shift+Up` | pull a queued message back into the editor | M2, M3 |
| `app.retry` | `Alt+R` | retry the last failed assistant turn | M2, M3 |
| `app.display.reset` | `Alt+L` | redraw a garbled terminal | M1, M2 |
| `app.clipboard.copyLine` | `Alt+Shift+L` | copy current line | M2 |
| `app.clipboard.copyPrompt` | `Alt+Shift+C` | copy whole prompt | M2 |
| `app.clipboard.pasteTextRaw` | `Ctrl+Shift+V`, `Alt+Shift+V` | paste text without collapsing it | M2 |
| `app.clipboard.pasteImage` | Linux `Ctrl+V`; macOS `Ctrl+V`, `Cmd+V`; Windows `Ctrl+V`, `Alt+V` | paste clipboard (image preferred, text fallback) | M1, M2 |
| `app.stt.toggle` | unbound (hold `Space` = push-to-talk) | toggle dictation (`stt.enabled`, default `false`) | M14 |
| `app.live.toggle` | `Ctrl+L` | start/stop live voice (same as `/live`) | M14 |
| `app.agents.hub` | `Alt+A` | open/close the Agent Hub | M10 |
| `app.session.observe` | `Ctrl+S` | legacy action, also opens the Agent Hub | M10 |

## Fixed keys (not remappable action IDs)

| Key | Context | Does |
|---|---|---|
| `Esc` | turn streaming | abort the turn (`interruptMode: immediate`, default) |
| `Esc Esc` | empty editor | rewind selector (`doubleEscapeAction: rewind`; `tree` opens `/tree`; `none` disables) |
| `Esc` | focused subagent (Hub) | return to main session — never interrupts the child |
| `Ctrl+C` | draft present | clear draft; `Up` recalls it (`composer.recallClearedDrafts: true`) |
| `Ctrl+C Ctrl+C` | any | exit omp |
| `Enter` while streaming | composer | steer (`steeringMode: one-at-a-time` / `all`) |
| `Up` / `Down` | composer | prompt history (Insert mode only under Vim mode) |
| `!cmd` / `$code` | composer prefix | run shell / Python locally, no model turn |
| `@path` | composer | attach file (fuzzy autocomplete) |
| `^` | composer | tag a model → pseudonym `m1`, `m2` usable as `agent` |
| `/pause` screen | any | resume with `Esc`, `Enter`, `Space`, or `Ctrl+C` |
| Double-tap `←` | empty main editor | open Agent Hub (gesture, not an action ID) |

## Overlay keys

| Overlay | Keys |
|---|---|
| `/tree` | `↑↓` move · `Alt+↑↓` prev/next turn · `PgUp/PgDn` `←→` page · `Home/End` · `Enter` select · `Shift+Enter` summarize+select · type = search · `Esc` · `Shift+L` label · `Ctrl+O` / `Shift+Ctrl+O` filter cycle · `Alt+D/T/U/L/A` filter (`default`, `no-tools`, `user-only`, `labeled-only`, `all`) |
| `/resume` picker | type = search · `Tab` current folder ↔ all projects · `Enter` · `Del` / `⌫` delete (empty search) · `Esc` |
| Agent Hub | `j`/`k` select · `Enter` focus · `t` tree · `Tab` inspector · `PgUp`/`PgDn` · `r` revive parked · `x` kill · `Esc` close |
| Plan review / `/annotate` | `a` annotate line/section · `A` whole file/text · `e` edit · `u` undo · `Enter` save · `Shift+Enter` newline · `Escape` discard |
| `/btw` panel | `Esc` cancel/close · `c` copy · `f` follow-up · `b` branch; history: `Up`/`Down`, `Tab`, `Enter`/`f` |
| `/model` picker | `→` models · `Alt+←/→` model kind · `Enter` assign · `Esc` |

## Vim editing mode (`tui.vimMode: true`, default `false`)

Insert `i a I A o O` → `Escape` → Normal; `v` / `V` visual; `h j k l 0 ^ $ w b e gg G`, counts, `d y c` + motion/text object (`iw aw i" a( ip …`), `dd yy cc x D C p P u`. `Escape` falls through to the app interrupt only when Vim has nothing pending. `Ctrl` chords, `Enter`, `Tab` keep app meaning in every mode.

## Terminal gotchas

| Symptom | Fix |
|---|---|
| `Ctrl+Shift+O` acts like `Ctrl+O`, `Alt+…` types a letter, `Shift+Tab` dead | terminal lacks modifier encoding (Kitty keyboard protocol); enable it or remap the action |
| chords die only inside tmux | tmux `extended-keys` on |
| `Ctrl+Enter` / `Ctrl+V` swallowed on Windows Terminal | `Ctrl+Q` / `Alt+V` |
| odd SSH hop mangles Backspace | `PI_TUI_RAW_BACKSPACE_IS_CTRL=1` |

Source: omp://keybindings.md · omp://agent-hub.md · omp://tree.md · omp://slash-command-internals.md · modules M01–M14 cheat sheets
