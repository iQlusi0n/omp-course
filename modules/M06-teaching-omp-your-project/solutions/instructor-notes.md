# Module 6 — Instructor notes (solutions)

`solutions/dot-omp/` is a complete `.omp/` tree for `omp-course-lab`. Install it with:

```bash
cd omp-course-lab && git checkout module-6-start
cp -r ../modules/M06-teaching-omp-your-project/solutions/dot-omp/. .omp/
cp .env.example .env
```

| File | Lesson | Purpose |
|---|---|---|
| `AGENTS.md` | 6.1 | layout, commands, conventions, `@../docs/spec.md` import (relative to `.omp/`) |
| `RULES.md` | 6.2 | three sticky prohibitions |
| `rules/sqlite-migrations.md` | 6.3 | rulebook rule (`description` + `globs`) |
| `rules/no-print-in-api.md` | 6.3 | always-apply rule scoped `agents: main` |
| `commands/changelog.md` | 6.5 | `$1` + `$ARGUMENTS` |
| `skills/release-checklist/SKILL.md`, `report.md` | 6.6 | skill + asset via `skill://release-checklist/report.md` |
| `config.yml` | 6.7, 6.9 | `tools.approvalMode: write`, `theme.dark`, `secrets.enabled: true` |
| `APPEND_SYSTEM.md` | 6.8 | `Verified:`/`Untested:` footer |
| `secrets.yml` | 6.9 | `labtok_[0-9a-f]{16}` (obfuscate) + a `replace` example |

## Verified on the build machine (omp/18.3.1, no model)

- `omp config get tools.approvalMode` → `write` in the repo root, `yolo` outside and in `api/` (no ancestor walk for settings).
- `omp config get secrets.enabled` → `true` inside, `false` outside.
- `omp config set tools.approvalMode yolo --json` → `{"key":"tools.approvalMode","value":"yolo","overriddenBy":"project"}`; `omp config reset tools.approvalMode` → `✔ Reset tools.approvalMode to write`.
- `PI_CONFIG_FILES=/tmp/ci.yml omp config get tools.approvalMode` → overlay value; `omp config get … --config f` → `Unknown option '--config'`.
- `omp read skill://release-checklist`, `…/report.md` resolve from the root **and** from `api/`; a missing asset → `File not found: <abs path>`.
- `omp read rule://sqlite-migrations` from the shell → `Unknown rule … Available: none` (rule snapshot is per session; must be read inside omp).
- `OMP_PROFILE=x omp config path` → `~/.omp/profiles/x/agent`; `omp config set` under the profile writes that profile's `config.yml`; `agent.db` is created there.
- `SHELL=/bin/bash omp --profile course --alias omp-course` appends a `omp-course()` function block to `~/.bashrc`; with an unsupported `$SHELL` it errors `Unsupported shell. Supported shells: bash, zsh, fish, PowerShell.`
- `skills.enableSkillCommands` default is `true` (schema default; not set in the global config).

Model-dependent steps (refusals, rulebook reads, skill invocation, placeholder reporting) were not run here — the demos mark them as illustrative. Run them once in `omp --profile course-build` before teaching and paste real transcripts over the illustrative ones.

## Exercise solutions

### 6-W
Files: `dot-omp/AGENTS.md`, `dot-omp/RULES.md`. Common failure: learner writes `@docs/spec.md` (does not expand — path is relative to `.omp/`) or leaves an empty `.omp/AGENTS.md` from an earlier module (empty files contribute nothing). If `generated/` still gets edited, check `~/.omp/agent/RULES.md` (shadows the project file) and whether the prompt itself authorised the edit — `RULES.md` says "unless the user explicitly asks", so a prompt like "edit generated/x anyway" is a legitimate override; the graded prompt does not say that.

### 6-G1
Files: `dot-omp/commands/changelog.md`, `dot-omp/skills/release-checklist/`. Acceptable variations: any placeholder set that yields the version; a skill without an asset (then checkpoint 5 is skipped). Failure modes: skill nested one directory too deep; missing `description` (native skills require it); expecting the command to appear without `/reload-plugins`.

### 6-G2
File: `dot-omp/config.yml`. Learners often run `omp config set tools.approvalMode write` and see it apply everywhere — that is the global file. The `--json` `overriddenBy` output is the fastest way to show the layer. For the array optional part, expected `omp config get disabledProviders --json` values: inside `["groq"]`, outside `["ollama","groq"]`.

### 6-G3
File: `dot-omp/secrets.yml` + `secrets.enabled` in `config.yml`. The token is 23 chars; a friendly-named placeholder is 27 (`$$LABTOKEN_` + 12 + `:L$$`). Learners who judge by the `read` card conclude "it didn't work" — the TUI restores placeholders for display; the model's own description is the evidence. If the learner exported `LAB_TOKEN` in their shell, automatic env-var collection already covers it even without `secrets.yml` (name contains `TOKEN`, value ≥ 8 chars) — that is the Stretch, not a failure.

### 6-S
```bash
omp --profile course            # /login inside, then /exit
omp --profile course config path          # ~/.omp/profiles/course/agent
omp --profile course --alias omp-course   # writes function to rc file
. ~/.bashrc && omp-course --version
omp-course config set theme.dark dark && omp-course config get theme.dark && omp config get theme.dark
ls ~/.omp/profiles/course/agent/          # agent.db  config.yml  (sessions/ after first session)
```
Isolation proof: the default profile's `~/.omp/agent/config.yml` is unchanged (`cmp` against a copy taken before). Keybindings are the documented exception (profile inherits them).

## Grading rubric (suggested)

| Item | Points |
|---|---|
| 6-W pass condition (no `generated/` change, no commit, both files in `/extensions`) | 25 |
| 6-G1 (command expands `$1`; `skill://` resolves; `/skill:` invocation observed) | 25 |
| 6-G2 (inside/outside values differ; `overriddenBy: project` shown) | 15 |
| 6-G3 (model reports placeholder; shell card shows `labtok_`) | 25 |
| 6-S (profile dir + alias + isolation) | 10 |
