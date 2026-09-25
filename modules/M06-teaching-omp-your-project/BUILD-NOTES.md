# Module 6 — Build notes

Built against `omp/18.3.1` on the course build machine (Python 3 only, no model credentials). Sources read this session: `omp://context-files.md`, `omp://rulebook-matching-pipeline.md`, `omp://skills.md`, `omp://slash-command-internals.md`, `omp://settings.md`, `omp://config-usage.md`, `omp://system-prompt-customization.md`, `omp://secrets.md`, `omp://cli-reference.md` (flags table), `omp://environment-variables.md` (profile/config env vars), `omp --help`, `omp config --help`, `omp read --help`, `omp config list --json`.

## Deviations from COURSE-OUTLINE.md (doc/binary wins)

1. **`/skill:<name>` does not need enabling.** Outline 6.6 and Appendix C say `skills.enableSkillCommands` is opt-in. In 18.3.1 the schema default is `true` (`omp config list --json`; the build machine's global config does not set it). Lesson 6.6 tells learners to verify with `omp config get skills.enableSkillCommands` and set it only if their config turned it off.
2. **Secrets pass condition reworded.** Outline G says "transcript shows placeholder". `omp://secrets.md`: "Session context restores placeholders for local display/resume", so the on-screen `read` card is not reliable evidence. The exercise instead asks the model to describe the value it received (length / `$$` / prefix) and uses a model-authored `printf` of the placeholder to show restoration in the `bash` card.
3. **`rule://` is session-scoped.** `omp read rule://<name>` from a shell returns `Unknown rule … Available: none` (verified). Lessons say to ask omp to read `rule://` inside a session; `skill://` does work from the shell via `omp read`.
4. **`--config` is not accepted by `omp config`** (verified error; docs list launch/`acp`/`models`). Exercise 6-G2 uses `PI_CONFIG_FILES` for shell checks and `--config` only on a launch.
5. **Fixture detail from the lab builder:** `.env.example` = `LAB_TOKEN=labtok_0123456789abcdef` + `DATABASE_URL=sqlite:///data/lab.sqlite` (per `LabRepo`, this session). Regex used: `labtok_[0-9a-f]{16}`. If the lab changes the shape, update `solutions/dot-omp/secrets.yml`, Lesson 6.9 and Exercise 6-G3 together.
6. **Skills walk up, settings/commands/rules do not.** Not in the outline; documented in `omp://config-usage.md` ("Directory admission rules") and verified (`omp read skill://…` from `api/` works; `omp config get` from `api/` returns the global value). Surfaced as the module's opening table because it explains most "it doesn't load" reports.
7. **Task subagents do not inherit `AGENTS.md`** (`omp://system-prompt-customization.md`, "Inputs by session type"). Mentioned in 6.1 as a one-line forward pointer to Module 10 because it changes what learners put in `RULES.md`/rules vs `AGENTS.md`.

## Claims dropped or hedged as unverifiable here

- Exact `/extensions` rendering (column layout, the literal words `active` / `shadowed` / `disabled`). Docs state it lists level, source and state and shows disabled/shadowed entries; the demos draw an illustrative panel. Instructor should replace with a real capture.
- Whether the TUI transcript shows the expanded command template or the typed `/changelog 1.2.0`. Lesson 6.5 pass conditions rely on the reply and `git status`, not on transcript rendering.
- Whether the `bash` card shows the restored token or the placeholder for a model-authored command (demo 6.9 annotates "may show the restored value").
- All model behaviour (refusals, rule reads, footer compliance) is illustrative — no provider credentials on the build machine. Appendix D step 4 (run every Walkthrough in `omp --profile course-build`) is still owed for the model-dependent steps; the shell-only steps were run and their outputs are pasted verbatim in `demos/07-settings.md` and `solutions/instructor-notes.md`.
- `AGENTS.md` refresh on `/new`: docs guarantee re-discovery on `/clear`/`/new` only for `RULES.md`; the module tells learners to restart omp after editing `AGENTS.md`.
- Outline 6.4 lists the priority chain as "native > omp-plugins > claude > codex > gemini > …"; the doc table also has `agent-plugins` (75) and `agents`/`claude-plugins` (70, tied with `codex`). The lesson uses the full doc table.

## Verification performed (no model)

Scratch repo `/tmp/m06lab` with the shipped `solutions/dot-omp/` copied to `.omp/`:

- `omp config get tools.approvalMode` → `write` (root), `yolo` (`/tmp`, `api/`); `secrets.enabled` → `true`/`false`; `theme.dark` → `titanium`.
- `omp config set tools.approvalMode yolo --json` → `overriddenBy: project`; `omp config reset` → `Reset … to write`.
- `PI_CONFIG_FILES=/tmp/m06overlay.yml omp config get tools.approvalMode` → `always-ask`.
- `omp read skill://release-checklist[/report.md]` → file contents; `…/nope.md` → `File not found`.
- `omp read rule://sqlite-migrations` → `Unknown rule`, `Available: none` (expected outside a session).
- `OMP_PROFILE=m06smoke omp config path|set|reset` → profile dir `~/.omp/profiles/m06smoke/agent` with `config.yml` + `agent.db`.
- `SHELL=/bin/bash HOME=/tmp/fakehome omp --profile course --alias omp-course` → function block appended to `.bashrc`; unsupported `$SHELL` → error listing bash/zsh/fish/PowerShell.
- Frontmatter delimiters and `secrets.yml` list shape checked with a throwaway Python script; regex matches the lab token.
- Cleanup: scratch repo `/tmp/m06lab`, `/tmp/fakehome`, the overlay file and `~/.omp/profiles/m06smoke` were deleted after verification.

## Coverage (Appendix C rows for Module 6)

| Row | Where |
|---|---|
| `AGENTS.md` family, `@imports`, `RULES.md` | 6.1, 6.2 |
| `.omp/rules` (alwaysApply / rulebook / `rule://`) | 6.3 |
| Discovery precedence, `/extensions`, `disabledProviders/Extensions` | 6.4 |
| Custom slash commands (`$ARGUMENTS`) | 6.5 |
| Skills, `skill://`, `/skill:` (default noted) | 6.6 |
| Settings layering, `omp config`, `/settings`, `--config`, profiles | 6.7 |
| `SYSTEM.md` / `APPEND_SYSTEM.md` / `PERSONALITY.md` / template | 6.8 |
| Secrets obfuscation (default off) | 6.9 |
