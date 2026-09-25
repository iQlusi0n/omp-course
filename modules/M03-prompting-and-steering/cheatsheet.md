# Module 3 cheat sheet — Prompting & Steering (omp/18.3.1)

## Prompt shape
| Part | Write it as |
|---|---|
| Outcome | end state in repo terms (command, flag, file, behavior) |
| Acceptance | `<command>` → expected exit/output; what must stay unchanged |
| Scope | "Not in scope: …", "Do not modify `<path>`", "If `<X>` is unclear, ask; otherwise state your assumption and proceed." |
| Verification | numbered: check before → implement → check after; "fix and re-run; never report done with a failing run" |
| Receipt | "Finish with: files changed (one line each) and the exact commands you ran." |
| Attach | `@path` in the composer; `omp @file "…"` from the shell |

## Reading a result
| Signal | Meaning |
|---|---|
| `bash` card, error-marked, ends `Command exited with code <n>` | the command failed, whatever the prose says |
| No `bash` card behind "tests pass" | unverified → "Run `<cmd>` now and show the output." |
| Card footer `[raw output: artifact://<id>]` | output cut → "Read artifact://<id> …" |
| `Ctrl+O` / `Ctrl+Shift+O` | expand card / hide-show all cards |
| `!git diff --stat`, `!git status --short` | your own cross-check, no model tokens |

## Thinking
| Action | Key / flag / setting |
|---|---|
| Cycle level (session) | `Shift+Tab` (`app.thinking.cycle`) |
| Show/hide blocks (display only) | `Ctrl+T` (`app.thinking.toggle`); `--hide-thinking`; `hideThinkingBlock: false` |
| Level for a run | `--thinking off\|minimal\|low\|medium\|high\|xhigh\|max\|auto`; `--model <sel>:<level>` |
| Default level | `defaultThinkingLevel: high` |
| Level as text in status line | `statusLine.compactThinkingLevel: false` (default `true` = icon) |
| Budgets | `thinkingBudgets.minimal 1024 · low 2048 · medium 8192 · high 16384 · xhigh 32768 · max 32768` |
| `auto` ceiling | `providers.autoThinkingMaxEffort: xhigh` (only `ultrathink` reaches `max`) |

## Magic keywords (all on by default)
| Word | Effect this turn | Toggle |
|---|---|---|
| `ultrathink` | careful multi-step notice; on `auto`, top effort for the turn | `magicKeywords.ultrathink` |
| `orchestrate` `workflowz` `jevify` | multi-agent / bulk-judgment contracts (Module 10) | `.orchestrate` `.workflow` `.jevify` |
| global | | `magicKeywords.enabled` |
Rules: exact lowercase, standalone prose word; punctuation may touch it; not inside code fences/inline code/HTML. Gradient in composer = recognized (gradient persists even when disabled).

## Steering
| Action | Key / command |
|---|---|
| Abort turn | `Esc` (twice on empty editor → rewind selector; `doubleEscapeAction: rewind` default) |
| Steer (interrupt path) | type + `Enter` while streaming; `interruptMode: immediate` (default) / `wait`; `steeringMode: one-at-a-time` / `all` |
| Follow-up (after turn) | `Ctrl+Q` / `Ctrl+Enter` (`app.message.followUp`); `followUpMode` |
| Dequeue | `Alt+Up` / `Shift+Up` (`app.message.dequeue`) |
| Clear / recall draft | `Ctrl+C` / `Up` (`composer.recallClearedDrafts: true`); `Ctrl+C` ×2 exits |
| Retry failed turn | `Alt+R` (`app.retry`) |
| Pause everything | `/pause` (TUI only); resume `Esc` `Enter` `Space` `Ctrl+C` |
| Side question | `/btw <q>`; panel: `Esc` cancel/close, `c` copy, `f` follow-up, `b` branch; bare `/btw` = history (`Up`/`Down`, `Tab`, `Enter`/`f`) |
| Reset provider stream | `/fresh` (idle only; keeps transcript/session file) |
| `ask` tool | interactive only; `ask.timeout: 0`, `ask.notify: on` |

## Config one-liners
```bash
omp config get defaultThinkingLevel        # high
omp config get magicKeywords.ultrathink    # true
omp config set interruptMode wait          # experiment; then:
omp config reset interruptMode
omp config set doubleEscapeAction none     # if double-Esc keeps opening the rewind picker
/hotkeys                                   # live chords in-session
/settings → Interaction → Magic Keywords
```

Sources: omp://magic-keywords.md · omp://keybindings.md · omp://slash-command-internals.md · omp://session-operations-export-share-fork-resume.md · omp://settings.md · omp://tools/bash.md · omp://tools/ask.md · omp://rpc.md · omp://tree.md
