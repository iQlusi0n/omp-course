# Appendix B — Reference sheets

One-page lookups aggregated from the module cheat sheets (`modules/M*/cheatsheet.md`) and re-verified against the bundled docs (`omp read omp://…`), `omp --help` / `omp <cmd> --help`, and `omp read cfg://<key>` (definition defaults). Course pinned to omp 18.3.1; the build machine ran 18.3.5 when these sheets were verified — where a value could differ, the sheet says so.

| Sheet | What it answers | Primary sources |
|---|---|---|
| [keybindings.md](keybindings.md) | default chords, action IDs for `~/.omp/agent/keybindings.yml`, fixed keys, overlay keys, Vim mode | omp://keybindings.md, omp://agent-hub.md, omp://tree.md |
| [slash-commands.md](slash-commands.md) | every slash command used in the course, grouped session / context / model / agents / review / config / collab | omp://slash-command-internals.md, per-feature docs |
| [settings.md](settings.md) | every setting key used in the course: definition default, layer/file that can set it, module | `omp read cfg://<key>`, omp://settings.md, omp://config-usage.md |
| [uri-schemes.md](uri-schemes.md) | the 19 internal URI schemes: read/write support, one example each, gating | omp://tools/read.md, omp://tools/write.md |
| [tools.md](tools.md) | tool inventory: always-on vs setting-gated, enable key, surface availability | omp://tools/*.md, omp://approval-mode.md |
| [config-files.md](config-files.md) | `~/.omp/agent/*`, `<repo>/.omp/*`, other `~/.omp/*`, foreign formats and provider priority | omp://context-files.md, omp://config-usage.md |
| [troubleshooting.md](troubleshooting.md) | symptom → cause → fix, aggregated from all module Troubleshooting sidebars | modules M01–M14 README.md |

## How to re-verify a line

```bash
omp read omp://                      # doc index
omp read omp://keybindings.md        # a doc, optional :N-M range
# in a session: grep tool with path omp://   — the `omp grep` CLI takes filesystem paths only
omp read cfg://tools.approvalMode    # value, type, default, source, allowed values
cd /tmp && omp config get <key>      # effective default with no project override
omp <cmd> --help                     # subcommand flags
/hotkeys                             # live chords inside a session
```

Conventions: ⚠ marks a default-off feature and names its enable key; the "Module" column points at the lesson that exercises the entry; fixture numbers follow `omp-course-lab/docs/ISSUES.md`.
