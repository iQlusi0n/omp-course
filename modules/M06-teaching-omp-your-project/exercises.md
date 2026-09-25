# Module 6 — Coursework

Built against `omp/18.3.1`. All work happens in `omp-course-lab`; start from `git checkout module-6-start`. Each lesson in `README.md` has its own Walkthrough / Guided / Stretch; the five exercises below are the module's graded set and reuse the files you create there. Record evidence in `notes/m6.md` (gitignored) unless a pass condition names another artefact. A finished `.omp/` tree is in `solutions/dot-omp/` — use it to unblock yourself, not to skip the typing.

Prerequisites: a logged-in provider (Module 1); a terminal that delivers `Ctrl+Enter` (Module 1.3) for the skill follow-up variant; nothing else. All lab code is Python stdlib.

---

## Exercise 6-W — Context + sticky rules              (Walkthrough, ~15 min)

**Goal:** omp knows the test/lint commands and refuses to touch `generated/` without being told in the prompt.

1. `cd omp-course-lab && git checkout module-6-start && mkdir -p .omp`
2. Write `.omp/AGENTS.md` containing at least:
   - Test: `python3 -m pytest -q`
   - Lint: `python3 -m compileall -q api cli`
   - "`generated/` is build output — never edit it by hand."
   - Last line: `@../docs/spec.md` (relative to `.omp/`, not the repo root)
3. Write `.omp/RULES.md` with one line: `Never run git commit or git push unless the user explicitly asks in the current message.`
4. Start `omp` in the repo root. Type `/extensions`.
   Expected: `AGENTS.md` (project, native) listed as a context file; `RULES` listed among rules as always-applied.
5. Type `/new` (forces re-discovery of `RULES.md`; `AGENTS.md` was read at start).
6. Prompt: `Append a comment "# reviewed" to the first file under generated/ and commit it.`
   Expected: omp declines or asks before touching `generated/`, and does not commit. It cites the context file or the rule.
7. Prompt: `What is the test command? Answer from context, no tool calls.`
   Expected: `python3 -m pytest -q`, no `read` card.

**Pass condition (all three):**
- `git status --porcelain generated/` prints nothing and `git log -1 --format=%s` is unchanged from `module-6-start`.
- `/extensions` lists `AGENTS.md` and `RULES`.
- `notes/m6.md` contains the reply from step 6 (copy with `/copy` or by hand).

**If it edited `generated/` anyway:** check `/extensions` — an empty `.omp/AGENTS.md`, a nearer non-empty `.omp/` in a subdirectory, or a user-level `~/.omp/agent/RULES.md` (which shadows the project one) are the usual causes (Lessons 6.1–6.2).

---

## Exercise 6-G1 — A command and a skill              (Guided, ~20 min)

**Goal:** `/changelog <version>` drafts a changelog entry from git history; `/skill:release-checklist` walks a release checklist; both are discoverable without restarting for the command.

Hints:
- Command file: `.omp/commands/changelog.md`, frontmatter `description:`, body uses `$1` for the version and `$ARGUMENTS` for everything. Instruct it to run `git log --oneline <last-tag>..HEAD`, group into Added/Changed/Fixed, and **show** the entry without writing it.
- Skill: `.omp/skills/release-checklist/SKILL.md` with `name:` and `description:` (description is mandatory for native skills; say *when* the skill applies). Put a report template in `.omp/skills/release-checklist/report.md` and reference it as `skill://release-checklist/report.md` in the body.
- Commands need `/reload-plugins` (or a restart) to appear; skills are discovered at session start — restart after creating the skill.
- `skills.enableSkillCommands` defaults to `true` in 18.3.1; confirm with `omp config get skills.enableSkillCommands`.

Checkpoints:
1. `omp read skill://release-checklist` in your shell prints the skill; `omp read skill://release-checklist/report.md` prints the template. (Shell check — no model needed.)
2. Inside omp, `/chan<Tab>` completes to `/changelog` with your description.
3. `/changelog 1.2.0` → a `bash` card with `git log`, a fenced entry mentioning `1.2.0`, no change to `CHANGELOG.md` (`git status`).
4. `/skill:release-checklist 1.2.0` → the injected message names the skill and its directory; bash cards for `git status --porcelain` and the test run follow; no `git tag` is executed.
5. Prompt: `read skill://release-checklist/report.md and fill it in` → a completed table.

**Pass condition:** checkpoints 1, 3 and 4 all observed; `notes/m6.md` lists the tool cards produced by `/changelog 1.2.0` and by `/skill:release-checklist 1.2.0`, in order.

Variant (if streaming): type `/skill:release-checklist` while a turn is running — `Enter` steers immediately, `Ctrl+Enter` queues it as a follow-up.

---

## Exercise 6-G2 — Project settings layer              (Guided, ~10 min)

**Goal:** the lab repo runs in `write` approval mode with a chosen dark theme while every other directory keeps your global settings.

Hints:
- Project settings live in `<cwd>/.omp/config.yml` and are read only when omp starts **in that directory** (no ancestor walk). Nested YAML: `tools: {approvalMode: write}`, `theme: {dark: <name>}`.
- `omp config set` writes the **global** file; for the project layer edit the file by hand.
- `omp config get <key> --json` and `omp config set … --json` (`overriddenBy`) show which layer is winning.

Checkpoints:
1. In the repo root: `omp config get tools.approvalMode` → `write`; `omp config get theme.dark` → your value.
2. `cd ..` (or any other directory): the same two commands print your global values (`yolo` and `titanium` unless you changed them).
3. In `omp-course-lab/api/`: `omp config get tools.approvalMode` → global value again (proves no walk-up).
4. From the repo root: `omp config set tools.approvalMode yolo --json` → `"overriddenBy":"project"`; then `omp config reset tools.approvalMode` → `Reset tools.approvalMode to write`.
5. Start `omp` in the repo and ask for a trivial edit outside the workspace (e.g. `create /tmp/m6-probe.txt`) → an approval prompt appears; the same prompt in `/tmp` runs without asking (yolo).

**Pass condition:** the outputs of checkpoints 1–3 pasted into `notes/m6.md` show different values inside vs outside the repo; `git diff --stat` shows only `.omp/config.yml` added.

Optional: add `disabledProviders: [groq]` to the project file after `omp config set disabledProviders '["ollama","groq"]'` and observe array replacement with `omp config get disabledProviders --json` inside vs outside; clean up with `omp config reset disabledProviders`.

---

## Exercise 6-G3 — Secrets              (Guided, ~15 min)

**Goal:** the lab token never reaches the provider, yet shell commands still receive it.

Fixture: `.env.example` contains `LAB_TOKEN=labtok_0123456789abcdef` (`labtok_` + 16 lowercase hex = 23 characters) and `DATABASE_URL=sqlite:///data/lab.sqlite`.

Hints:
- `secrets.enabled` is **off by default**; put `secrets: {enabled: true}` in `.omp/config.yml` (project-only) or `omp config set secrets.enabled true` (global).
- `.omp/secrets.yml` is a YAML array. A regex entry: `- type: regex`, `content: "labtok_[0-9a-f]{16}"`, optional `friendlyName: Lab Token`. Obfuscate mode is the default and reversible.
- `cp .env.example .env` (`.env` is gitignored). Restart omp after editing `secrets.yml`.
- The TUI restores placeholders for local display, so do not judge by what *you* see in the `read` card — ask the model what *it* sees.

Checkpoints:
1. `omp config get secrets.enabled` in the repo root → `true`; startup shows no `secrets.yml` warning.
2. Prompt: `Read .env. Tell me the exact length of the LAB_TOKEN value, whether it starts with "labtok_", and whether it contains "$$".` → the model reports a `$$…$$` placeholder (contains `LABTOKEN` if you set `friendlyName`), not a 23-character `labtok_…` value, and says it is redacted.
3. Prompt: `Run: set -a; . ./.env; set +a; printf '%s' "$LAB_TOKEN" | wc -c; printf '%s' "$LAB_TOKEN" | cut -c1-7` → bash card prints `23` and `labtok_` (the shell reads the file itself; nothing to restore).
4. Prompt: `Take the LAB_TOKEN value exactly as you saw it and run: printf '%s' "<value>" | cut -c1-7` → the model writes the placeholder into the command; the card prints `labtok_` — omp restored the real value before execution.

**Pass condition:** checkpoint 2's reply (placeholder, wrong length) and checkpoint 4's card output (`labtok_`) are both recorded in `notes/m6.md`; `.omp/secrets.yml` is committed-safe (contains the pattern, not the token).

Stretch inside this exercise: add `- type: plain, content: sqlite:///data/lab.sqlite, mode: replace, replacement: "<DB-URL>"` and show that the model sees `<DB-URL>`, that a command it writes containing `<DB-URL>` is **not** restored, and that `printf '%s' "$DATABASE_URL"` after sourcing `.env` still prints the real URL.

---

## Exercise 6-S — An isolated profile              (Stretch, ~15 min)

**Goal:** a `course` profile with its own login, settings and sessions, launchable as `omp-course`.

Steps (goal only; see `solutions/instructor-notes.md` for a worked run):
- `omp --profile course` → `/login` a provider inside it → `/exit`.
- `omp --profile course config path` and `omp config path` must differ.
- `omp --profile course --alias omp-course`, then `. ~/.bashrc` (or your shell's rc) and `omp-course --version`.
- Prove isolation: `omp-course config get theme.dark` vs `omp config get theme.dark` after `omp-course config set theme.dark <other>`.

**Pass condition:** `ls ~/.omp/profiles/course/agent/` lists `agent.db` and `config.yml`; `type omp-course` in your shell prints a function that runs `command omp --profile=course "$@"`; the two `theme.dark` values differ; the default profile's `config.yml` is byte-identical to before (`git`-style check: copy it first and `cmp`).

Cleanup: `omp config reset theme.dark` is not needed in the default profile; remove the alias block from your rc file when done if you do not want to keep the profile.

---

## Submission checklist

- [ ] `notes/m6.md` with evidence for 6-W, 6-G1, 6-G2, 6-G3 (and 6-S if attempted)
- [ ] `.omp/AGENTS.md`, `.omp/RULES.md`, `.omp/commands/changelog.md`, `.omp/skills/release-checklist/SKILL.md`, `.omp/config.yml`, `.omp/secrets.yml` present in the working tree (commit them yourself — `omp commit` from Module 4 — or leave them uncommitted; Module 7 starts from its own tag either way)
- [ ] no `CLAUDE.md`, `.claude/`, or `.omp/SYSTEM.md` left over from the README experiments
- [ ] `git status --porcelain generated/` empty
