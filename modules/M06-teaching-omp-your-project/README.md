# Module 6 — Teaching omp Your Project

| | |
|---|---|
| **Level** | intermediate |
| **Time** | ~2 h (9 lessons, 10–20 min each) |
| **Built against** | `omp --version` → `omp/18.3.1` |
| **Prerequisites** | Modules 1–5 (you can run omp in `omp-course-lab`, read cards, `/new`, `/clear`) |
| **Start state** | `cd omp-course-lab && git checkout module-6-start` (`.omp/` may hold what you added in Module 4) |
| **Files** | `README.md` (lessons) · `exercises.md` (module coursework) · `cheatsheet.md` · `demos/` · `solutions/dot-omp/` (copy-pasteable `.omp/` tree) · `BUILD-NOTES.md` |

**Goal:** Encode repo conventions so every session starts informed; layer settings correctly.

The nine lessons build one `.omp/` directory in `omp-course-lab`. By the end it looks like this (a finished copy is in `solutions/dot-omp/`):

```text
omp-course-lab/.omp/
  AGENTS.md                      # 6.1  project context (loaded once per session)
  RULES.md                       # 6.2  sticky rules (carried on every request)
  rules/sqlite-migrations.md     # 6.3  rulebook rule (listed; body via rule://)
  rules/no-print-in-api.md       # 6.3  always-apply rule scoped to the main agent
  commands/changelog.md          # 6.5  /changelog <version>
  skills/release-checklist/      # 6.6  skill://release-checklist, /skill:release-checklist
  config.yml                     # 6.7  project settings layer
  APPEND_SYSTEM.md               # 6.8  extra system-prompt text
  secrets.yml                    # 6.9  secret patterns (needs secrets.enabled)
```

Two facts govern everything in this module. First, **the native `.omp/` provider has the highest discovery priority (100)**, so anything you put there beats `CLAUDE.md`, `GEMINI.md`, Cursor rules, etc. at the same scope. Second, **each file kind has its own lookup rule** — some walk up from cwd, some do not:

| Kind | Project location | Walks up from cwd? | User location |
|---|---|---|---|
| `AGENTS.md`, `RULES.md`, `SYSTEM.md` | *nearest non-empty* `.omp/` toward repo root | yes (stops at first non-empty `.omp/`) | `~/.omp/agent/` |
| `rules/*.md`, `commands/*.md`, `config.yml` | `<cwd>/.omp/` only (must be non-empty) | **no** | `~/.omp/agent/` |
| `skills/<name>/SKILL.md` | every ancestor `.omp/skills/` up to repo root | yes | `~/.omp/agent/skills/` |
| `secrets.yml` | `<cwd>/.omp/secrets.yml` | no | `~/.omp/agent/secrets.yml` |

`~/.omp/agent` means the *active* agent directory: `omp config path` prints it; a named profile (Lesson 6.7) moves it to `~/.omp/profiles/<name>/agent`.

---

## Lesson 6.1 — Context files              (~20 min)
**You will be able to:** write a `.omp/AGENTS.md` that omp loads automatically; predict which of several `AGENTS.md`/`CLAUDE.md` files load; use `@path` imports.
**Why this exists:** Every new session starts with a blank model. Without a context file you re-explain the test command, the directory layout and the review bar in every prompt — and forget half of it. omp discovers Markdown instruction files before the first turn and injects them into the opening project context (a `<repo-rules>` block containing one `<file path="…">` element per file), so the agent already knows the build, the conventions and the no-go zones. You never need to tell it to "read AGENTS.md".
**Demo:** `demos/01-context-files.md`
**Concepts:**
- Native files (recommended): `<repo>/.omp/AGENTS.md` (project) and `~/.omp/agent/AGENTS.md` (user). Project discovery walks from cwd toward the repo root and stops at the **nearest non-empty `.omp/`**; `AGENTS.md` is read from that directory only. A nearer `.omp/` without `AGENTS.md` blocks farther ones. Empty directories and empty files contribute nothing.
- Foreign conventions still load (no migration needed): `.claude/CLAUDE.md` and `.gemini/GEMINI.md` (cwd only, no walk-up), `.github/copilot-instructions.md` (cwd only; plus user `~/.copilot/copilot-instructions.md`), `~/.codex/AGENTS.md` and `~/.config/opencode/AGENTS.md` (user only), `.agent/AGENTS.md` / `.agents/AGENTS.md` (walk-up), standalone `AGENTS.md` and `CLAUDE.md` (walk-up to repo root). Cursor `.cursor/rules/*.mdc`, Windsurf `.windsurf/rules/*.md`, Cline `.clinerules` and `.github/instructions/**/*.instructions.md` are discovered as **rules** (Lesson 6.3), not context files.
- `AGENTS.md` files *below* the cwd are not injected; they are listed in a `<dir-context>` block that tells the agent to read them before editing those directories.
- `@path` imports expand inline before injection: **relative paths resolve from the importing file's directory** (so inside `.omp/AGENTS.md`, `@../docs/spec.md` reaches `<repo>/docs/spec.md`), `~/` is home, up to five hops, cycles skipped, missing targets left as literal text. A token only counts when `@` starts a line or follows a space/tab; tokens in code spans and fenced blocks are left alone; trailing `. , ; : ! ? ) ] } " '` is trimmed.
- What belongs in it: layout, build/test/lint commands, conventions, review expectations, pointers to deeper docs via `@`. What does not: secrets (Lesson 6.9), hard "never" rules that must survive long sessions (Lesson 6.2), per-task instructions (that is the prompt), long design docs (import them instead — the file costs context once per session).
- Task subagents (Module 10) do **not** inherit `AGENTS.md`; rules (6.2, 6.3) do reach them.
**Try it (Walkthrough):**
1. `cd omp-course-lab && git checkout module-6-start && mkdir -p .omp`.
   Expected: `.omp/` exists (it may already contain files from Module 4).
2. Create `.omp/AGENTS.md` — copy `solutions/dot-omp/AGENTS.md` or write your own with: the layout, `python3 -m pytest -q` as the test command, a lint command, and the sentence "`generated/` is build output; never edit it by hand".
   Expected: `cat .omp/AGENTS.md` shows your text; the last line is `@../docs/spec.md`.
3. Start `omp` in the repo root and type `/extensions`.
   Expected: the dashboard lists `AGENTS.md` with level `project`, source native, state active.
4. Ask: `What is the test command for this repo, and which directory must you never edit? Answer from your context only, do not read files.`
   Expected: the reply names `python3 -m pytest -q` and `generated/` without any `read` card.
5. Ask: `Quote the first heading of the architecture notes you were given.`
   Expected: the reply quotes the first heading of `docs/spec.md` — proof that `@../docs/spec.md` expanded.
**Guided task:** Goal: prove the nearest-non-empty rule. Hints: `mkdir -p api/.omp && echo "# api-local" > api/.omp/AGENTS.md`, then start omp in `api/` and ask the same question as step 4. Checkpoints: (a) `/extensions` from `api/` shows only the `api/.omp/AGENTS.md`; (b) the answer no longer knows the test command; (c) `rm -r api/.omp` restores it. Pass condition: the two `/extensions` listings differ exactly in which `AGENTS.md` is active.
**Stretch:** Goal: make a user-level `~/.omp/agent/AGENTS.md` with one personal preference (e.g. "reply in British English") and confirm it loads *in addition to* the project file (different scopes both survive). Pass: `/extensions` shows one `user` and one `project` context file.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| `/extensions` shows no project context file | `.omp/` empty, or `AGENTS.md` empty | Put content in the file; empty files/dirs are skipped |
| File loads from repo root but not from a subdirectory | A nearer non-empty `.omp/` (without `AGENTS.md`) stops the walk | Remove the nearer `.omp/` or add an `AGENTS.md` to it |
| `.claude/CLAUDE.md` in the repo root is ignored from a subdirectory | `.claude/` is cwd-only (no walk-up) | Use `.omp/AGENTS.md` or a standalone `AGENTS.md`; or launch from the root |
| `@docs/x.md` did not expand | Path is relative to `.omp/`, not the repo root; or it sits inside backticks | Use `@../docs/x.md`; move it out of code spans |
| Edited `AGENTS.md`, session unchanged | Context files are discovered at session start | Restart omp (or open a new session) |
**Cheat sheet:**

| Item | Value |
|---|---|
| Project file | `<nearest non-empty .omp>/AGENTS.md` |
| User file | `~/.omp/agent/AGENTS.md` (shadows every other user-level file) |
| Inspect | `/extensions` |
| Import | `@relative/from/this/file.md`, `@~/notes.md`; 5 hops; not in code spans |
| Injected as | `<repo-rules><file path="…">…</file></repo-rules>` |
**Source:** omp://context-files.md, omp://system-prompt-customization.md (session-type table)

---

## Lesson 6.2 — `RULES.md`: sticky rules              (~10 min)
**You will be able to:** decide what goes in `RULES.md` versus `AGENTS.md`; explain why a user `RULES.md` can silently replace the project one.
**Why this exists:** Context files are injected once, at the top of the conversation. After an hour of tool output they are far up the transcript and the model's grip on "never commit" weakens. `RULES.md` is converted into an **always-apply rule** whose full body travels with **every request**, so a handful of hard requirements keep their hold no matter how long the session runs.
**Demo:** `demos/02-rules-md.md`
**Concepts:**
- Locations: `~/.omp/agent/RULES.md` (user) and `RULES.md` in the **nearest non-empty project `.omp/`** (same walk as `AGENTS.md`). Nowhere else is recognised.
- Loaded as a rule named `RULES`, forced `alwaysApply: true`; frontmatter cannot make it non-sticky. Readable in-session as `rule://RULES`.
- Rule dedup is by name, first wins. Both files synthesize the same name, and the user one is appended first → **a user `RULES.md` shadows the project `RULES.md`; they are not concatenated.** Never name a regular rule file `rules/RULES.md`: it loads earlier and shadows both.
- Re-read from disk at session start and on `/clear` and `/new` — create or edit it while omp is running and it applies at the next reset.
- Keep it short: every line is re-sent on every request. Background belongs in `AGENTS.md`.
**Try it (Walkthrough):**
1. Create `.omp/RULES.md` with three lines: never commit/push unless asked, never edit `generated/`, never add a dependency without asking (see `solutions/dot-omp/RULES.md`).
   Expected: file exists, no frontmatter.
2. In the running omp session type `/new`.
   Expected: a fresh conversation; the status line resets.
3. Ask: `read rule://RULES and quote it back verbatim`.
   Expected: a `read` card for `rule://RULES` followed by your three lines.
4. Ask: `Add a comment line to the top of the first file you find under generated/ and commit it.`
   Expected: omp declines both parts (or asks) and cites the rule; `git status` shows no change under `generated/` and `git log -1` is unchanged.
**Guided task:** Goal: demonstrate user-shadows-project. Hints: write `~/.omp/agent/RULES.md` containing only `Always start replies with the word RULE-USER.`; `/new`; ask anything; then ask omp to read `rule://RULES`. Checkpoint: replies begin with `RULE-USER` **and** `rule://RULES` no longer mentions `generated/`. Pass condition: after deleting the user file and `/new`, `rule://RULES` shows the project text again.
**Stretch:** Goal: find the length limit that matters to you. Put a 60-line essay in `RULES.md`, watch the context % in the status line across five short turns, then shrink it back to three lines and compare. Pass: you can state the per-turn context cost difference you observed.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Project `RULES.md` ignored | A user `~/.omp/agent/RULES.md` exists (same rule name) | Merge into one file or delete the user one |
| `RULES.md` in repo root ignored | Only native locations count | Move it to `.omp/RULES.md` |
| Edited the file, nothing changed | Applied at next reset | `/new` or `/clear` |
| `rule://RULES` "Unknown rule" | File empty, or a `rules/RULES.md` shadows it | Add content; rename the regular rule |
**Cheat sheet:**

| Item | Value |
|---|---|
| Files | `.omp/RULES.md` (project), `~/.omp/agent/RULES.md` (user; wins) |
| Semantics | always-apply rule `RULES`, body on every request |
| Refresh | session start, `/clear`, `/new` |
| Read back | `rule://RULES` (inside a session) |
**Source:** omp://context-files.md ("Sticky rules vs normal context"), omp://rulebook-matching-pipeline.md

---

## Lesson 6.3 — The rules directory              (~15 min)
**You will be able to:** write a rulebook rule (listed, read on demand) and an always-apply rule; scope a rule to specific agents; read a rule with `rule://`.
**Why this exists:** Some guidance is only relevant sometimes — how to write a DB migration matters only when the schema changes. Putting it in `AGENTS.md` wastes context on every session; leaving it out means the agent guesses. A rule with a `description` is listed in the system prompt by name and description only (the **rulebook**), and the model reads the body with `rule://<name>` when the task matches. A rule with `alwaysApply: true` is injected in full, like `RULES.md` but as a separate, nameable, agent-scopable file.
**Demo:** `demos/03-rules-dir.md`
**Concepts:**
- Locations: `<cwd>/.omp/rules/*.{md,mdc}` (only when the cwd's `.omp/` is non-empty — **no walk-up**) and `~/.omp/agent/rules/*.{md,mdc}`. Rule name = filename without extension.
- Frontmatter fields that matter now: `description:` → rulebook entry; `alwaysApply: true` → full body in the system prompt; `globs:` → shown inline in the rulebook line as a hint (advisory — omp does not auto-select rules by path); `agents:` → restrict to agent names/globs (`main` = top-level session, `sub` = unnamed subagent, `[scout, "foreman-*"]`). `condition:`, `astCondition:`, `question:` make a rule a TTSR rule — Module 11.
- Bucketing order: TTSR fields win, then `alwaysApply`, then `description`. A rule with both `alwaysApply` and `description` is always-apply only. A rule with **neither** is invisible: not listed, not injected, not addressable.
- `rule://<name>` resolves against rulebook + always-apply + TTSR rules of the **current session**. It is session state, so `omp read rule://x` from a plain shell reports `Unknown rule … Available: none` (verified) — ask omp to read it instead.
- Rules are deduplicated by name across providers (native first). `--no-rules` disables rules discovery for a run.
- Foreign rule sources: `.cursor/rules/*.mdc`, `.windsurf/rules/*.md`, `.clinerules`, `.github/instructions/**/*.instructions.md` (`applyTo: '**'` → always-apply; other globs → rulebook), plus `.agent[s]/rules/`.
**Try it (Walkthrough):**
1. `mkdir -p .omp/rules` and add `solutions/dot-omp/rules/sqlite-migrations.md` (has `description` + `globs`) and `solutions/dot-omp/rules/no-print-in-api.md` (has `alwaysApply: true` and `agents: main`).
   Expected: two files; both start with `---` frontmatter.
2. Restart omp in the repo root; `/extensions`.
   Expected: both rules listed; `no-print-in-api` is labelled as always-applied.
3. Ask: `Which rules are available to you, by name? Do not read any files.`
   Expected: the reply names `sqlite-migrations` (with its description) and `RULES`; it may not list `no-print-in-api` by name because its body is injected rather than listed.
4. Ask: `I need to add a created_at column to the orders table. Before doing anything, tell me the procedure you must follow.`
   Expected: a `read` card for `rule://sqlite-migrations`, then the five-step procedure from the rule.
5. Ask: `Add a debugging print() to api/__init__.py.`
   Expected: omp proposes `logging` instead, citing the always-apply rule.
**Guided task:** Goal: make a rule invisible on purpose and then visible again. Hints: create `.omp/rules/ghost.md` with a body but no frontmatter; restart; ask omp to read `rule://ghost`. Checkpoint: "Unknown rule" with the list of available names. Then add `description: Ghost rule` and restart. Pass condition: `rule://ghost` returns the body.
**Stretch:** Goal: scope `no-print-in-api` to subagents only (`agents: sub`) and show that the main session no longer sees it while a `task` subagent does (`read agent://<id>` after asking a subagent to list its rules — Module 10 covers `task`; a one-line "spawn a scout that reports which always-apply rules it has" is enough). Pass: main session does not cite the rule; the subagent's transcript does.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Rule not listed anywhere | No `description` and no `alwaysApply` | Add one of them |
| Rules load from repo root, not from `api/` | `.omp/rules` is cwd-only | Launch from the root, or add `api/.omp/rules/` |
| `omp read rule://name` fails in the shell | `rule://` is per-session state | Ask omp to `read rule://name` |
| Frontmatter values dropped | Invalid YAML → fallback line parser; multi-line arrays lost | Use flow arrays: `globs: ["a", "b"]` |
| Rule applies to subagents unexpectedly | No `agents:` field = every agent | Add `agents: main` |
**Cheat sheet:**

| Frontmatter | Effect |
|---|---|
| `description: …` | rulebook entry; body via `rule://<name>` |
| `alwaysApply: true` | full body in system prompt |
| `globs: [..]` | hint shown in rulebook line |
| `agents: main` / `[scout, "x-*"]` | restrict to agents |
| `condition:` / `astCondition:` / `question:` | TTSR (Module 11) |
**Source:** omp://rulebook-matching-pipeline.md, omp://context-files.md

---

## Lesson 6.4 — Precedence & shadowing              (~15 min)
**You will be able to:** predict which context file wins when several conventions coexist; turn a provider or a single file off; opt foreign user-level sources in.
**Why this exists:** Real repos accumulate `CLAUDE.md`, `.cursor/rules`, `copilot-instructions.md` and an `AGENTS.md` from four tools. omp loads all of them by a fixed priority table and a per-scope dedup. If you do not know the table you will edit a file that is silently shadowed and conclude "omp ignores my instructions".
**Demo:** `demos/04-precedence.md`
**Concepts:**
- Provider priorities: `native` 100 > `omp-plugins` 90 > `claude` 80 > `agent-plugins` 75 > `agents`/`claude-plugins`/`codex` 70 > `gemini` 60 > `opencode` 55 > `cursor`/`windsurf` 50 > `cline` 40 > `github` 30 > `vscode` 20 > `agents-md`/`claude-md` 10 > `mcp-json`/`ssh-json` 5 > `builtin-defaults` 1.
- Dedup: **one user context file** overall (native wins → `~/.omp/agent/AGENTS.md` shadows `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, …). **One project file per directory depth** (cwd = depth 0; `.claude/`, `.github/` of an ancestor count as that ancestor's depth); at equal depth the higher priority wins; across depths all survive; byte-identical copies collapse. Injection order: farther ancestors → nearer → user file last (most prominent).
- Worked example (from the docs): `repo/AGENTS.md` + `repo/packages/api/AGENTS.md` + `repo/packages/api/.github/copilot-instructions.md`, cwd `packages/api`: root file kept (depth 2); at depth 0 `github` (30) beats `agents-md` (10) so the Copilot file wins; add `packages/api/.omp/AGENTS.md` and native wins depth 0 outright.
- `/extensions` shows every discovered context file with level, source and state (active / shadowed / disabled) and toggles `disabledExtensions`. It also shows active and shadowed slash commands and rules.
- `disabledProviders: [claude, github]` removes the **whole source** (its MCP servers, commands, skills, hooks too). One shared id namespace with model providers: `gemini` = Gemini CLI files, `google` = the Google model backend. Supports path-scoped entries (`- path: ~/work/legacy` / `providers: [claude]`).
- `disabledExtensions: [context-file:<level>:<basename>]` drops one file (`context-file:project:CLAUDE.md`; a project id applies at every depth). Disabling ≠ shadowing: the dropped file leaves before dedup, so whatever it shadowed loads instead. Also accepts `skill:<name>`.
- `enabledProviders` (default `[]`): foreign **user-level** roots (`~/.claude`, `~/.codex`, `~/.cursor`, `~/.gemini`, `~/.config/opencode`, Windsurf, Copilot) do not load until listed (or `*`/`all`); project roots load regardless; native roots need no entry.
- All three are arrays: a higher settings layer **replaces** the whole list (Lesson 6.7).
**Try it (Walkthrough):**
1. In the repo root: `printf '# CLAUDE\nAlways answer in ALL CAPS.\n' > CLAUDE.md` and restart omp.
   Expected: `/extensions` shows `CLAUDE.md` (source claude-md) as **shadowed** and `.omp/AGENTS.md` active — same depth, native wins. Replies are not in caps.
2. `mkdir -p .claude && mv CLAUDE.md .claude/CLAUDE.md`; restart.
   Expected: still shadowed (claude 80 < native 100).
3. Temporarily `mv .omp/AGENTS.md /tmp/`; restart.
   Expected: `.claude/CLAUDE.md` is now active; the next reply is in caps. Move `AGENTS.md` back.
4. Add to `.omp/config.yml`: `disabledExtensions: [context-file:project:CLAUDE.md]`; restart.
   Expected: `/extensions` shows `CLAUDE.md` as disabled, `AGENTS.md` active. `rm -r .claude` when done.
**Guided task:** Goal: disable a whole provider and observe the blast radius. Hints: put `disabledProviders: [claude]` in `.omp/config.yml` while a `.claude/commands/hello.md` and a `.claude/CLAUDE.md` exist. Checkpoints: (a) `/extensions` lists neither; (b) `/hello` is sent to the model as plain text (unknown slash input is not rejected). Pass condition: replacing `disabledProviders` with `disabledExtensions: [context-file:project:CLAUDE.md]` brings `/hello` back while `CLAUDE.md` stays off.
**Stretch:** Goal: reproduce the docs' depth example inside `omp-course-lab` (root `AGENTS.md`, `api/AGENTS.md`, `api/.github/copilot-instructions.md`, cwd `api/`) and write down, before starting omp, which two files will load and in what order. Pass: `/extensions` agrees with your prediction.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| "omp ignores my CLAUDE.md" | Shadowed by a same-depth higher-priority file | `/extensions` → move guidance into `.omp/AGENTS.md` |
| Disabled `claude` and lost MCP servers/commands | `disabledProviders` removes the whole source | Use `disabledExtensions: [context-file:…]` |
| `~/.cursor/rules` never load | Foreign user roots are opt-in | `enabledProviders: [cursor]` |
| Project `disabledProviders` re-enabled a globally disabled one | Arrays replace per layer | Repeat the full list in the project file |
| Disabled `google` but Gemini CLI files still load | Wrong namespace | Discovery id is `gemini` |
**Cheat sheet:**

| Setting | Meaning |
|---|---|
| `disabledProviders: [id…]` | whole discovery source or model backend; path-scoped allowed |
| `disabledExtensions: [context-file:user\|project:<basename>, skill:<name>]` | single item |
| `enabledProviders: [claude, cursor, …]` | opt in foreign user-level roots |
| `/extensions` | list + toggle |
**Source:** omp://context-files.md ("Load order and shadowing", "Disabling…"), omp://settings.md ("Provider and source disabling"), omp://slash-command-internals.md

---

## Lesson 6.5 — Custom slash commands              (~10 min)
**You will be able to:** create a Markdown slash command with arguments; know why it did not show up; predict the collision winner.
**Why this exists:** Some prompts you type weekly: "draft the changelog", "summarise the failing tests", "review this PR against our checklist". A file in `.omp/commands/` turns each into `/name args` with tab completion — versioned with the repo, shared with the team, no extension code.
**Demo:** `demos/05-commands.md`
**Concepts:**
- Files: `<cwd>/.omp/commands/<name>.md` (project) and `~/.omp/agent/commands/<name>.md` (user). File name = command name. **Project beats user** on a collision. Non-recursive; hidden files skipped; the scan honours `.gitignore` — an ignored `.omp/` yields no commands.
- Frontmatter `description:` is the completion text; without it the first non-empty body line (≤ 60 chars) is used. Body = prompt template.
- Placeholders: `$1`, `$2`… positional; `$@[start]` / `$@[start:length]` 1-based slices; `$ARGUMENTS` or `$@` everything. Args are split quote-aware (`'…'`/`"…"`, no backslash escapes). If the template uses no placeholder, the arguments are appended.
- Built-in names are reserved and dispatched first; then extension commands, custom/MCP prompt commands, then file commands. Unknown `/foo` is **not rejected** — it goes to the model as literal text.
- Discovered at start, after `/move`, and on `/reload-plugins`. There is no file watcher: after adding a file, `/reload-plugins` or restart.
- Foreign sources: `.claude/commands/**/*.md` (recursive; `foo/bar.md` also as `foo:bar`), `.codex/commands/*.md`, `.opencode/commands/*.md`. `commands.enableClaudeProject` default `true`; `commands.enableClaudeUser` default `false`.
**Try it (Walkthrough):**
1. `mkdir -p .omp/commands` and copy `solutions/dot-omp/commands/changelog.md` (uses `$1` and `$ARGUMENTS`).
   Expected: file present; frontmatter has `description`.
2. In omp: `/reload-plugins`, then type `/chan` and pause.
   Expected: the completion shows `/changelog — Draft a CHANGELOG.md entry…`.
3. Run `/changelog 1.2.0`.
   Expected: omp runs the expanded template — the reply refers to version `1.2.0` (from `$1`), a `bash` card runs `git log …`, the answer is a fenced changelog block, and `git status` shows no `CHANGELOG.md` change.
4. Run `/changelog 1.2.0 "since last week"`.
   Expected: the reply echoes the full argument string `1.2.0 since last week` (quotes stripped — `$ARGUMENTS`) while still treating `1.2.0` as the version (`$1`).
**Guided task:** Goal: build `/failing-tests` that runs the suite and summarises only failures. Hints: template with no placeholder; instruct "run `python3 -m pytest -q`, then list each failing test with a one-line cause; if all pass say PASS". Checkpoint: `/failing-tests` after `git checkout module-6-start` produces a card with the pytest run. Pass condition: the reply contains either `PASS` or a bullet per failing test, and `/extensions` lists the command as active.
**Stretch:** Goal: create the same `changelog.md` under `~/.omp/agent/commands/` with a different description and show that `/extensions` marks the user copy as shadowed. Pass: completion text is the project description.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| New command absent from completion | No file watcher | `/reload-plugins` or restart |
| `.omp/commands` present but nothing loads | `.omp/` gitignored, or hidden filename | Un-ignore; rename |
| `/name` reached the model as text | Name typo, or collides with a built-in | Check `/extensions`; rename |
| Arguments glued together | Spaces need quotes | `/cmd "two words"` |
| Command exists in `.claude/commands` only from the repo root | cwd-only provider | Launch from the root or use `.omp/commands` |
**Cheat sheet:**

| Item | Value |
|---|---|
| Location | `.omp/commands/<name>.md` (project > user) |
| Placeholders | `$1`, `$2`, `$@[2]`, `$@[2:3]`, `$ARGUMENTS`/`$@` |
| Refresh | `/reload-plugins` |
| Collisions | built-ins > extension > custom > file; native > claude > … |
**Source:** omp://slash-command-internals.md

---

## Lesson 6.6 — Skills              (~15 min)
**You will be able to:** author a `SKILL.md` with assets; reach it via `skill://` and `/skill:`; choose between skill, command, rule and context file.
**Why this exists:** A command is something *you* trigger; a rule is something the agent must *obey*. A **skill** is knowledge the agent can *choose* to load — a workflow, a checklist, reference tables — advertised in the system prompt by name and description only, and read on demand with the `read` tool. It keeps long procedures out of every prompt while making them discoverable, and any helper files live next to it.
**Demo:** `demos/06-skills.md`
**Concepts:**
- Layout: `<root>/skills/<name>/SKILL.md`, exactly one level deep (`skills/team/x/SKILL.md` is **not** found). Native roots: every ancestor's `.omp/skills/` from cwd to the repo root (walk-up, verified) plus `~/.omp/agent/skills/`. `skills.customDirectories: [path…]` adds roots (same one-level scan; a custom-dir skill overrides a same-named provider skill).
- Frontmatter: `name` (defaults to the directory name), `description` (**required** for native skills — no description, no skill), `hide: true` / `disableModelInvocation: true` (omit from the system-prompt list; still reachable via `skill://` and `/skill:`), `globs`, `alwaysApply` accepted.
- `skill://<name>` → the `SKILL.md`; `skill://<name>/<relative>` → an asset in the skill directory. Absolute paths, `..` and escapes are rejected; a missing asset is `File not found`. Works from the shell too: `omp read skill://<name>` (verified).
- `/skill:<name> [args]` injects the body (frontmatter stripped, base dir appended, args as `User: …`). Enabled by `skills.enableSkillCommands` — **default `true` in 18.3.1** (check with `omp config get skills.enableSkillCommands`; set it to `true` if your config says otherwise). Delivery while streaming: `Enter` steers, `Ctrl+Enter` queues a follow-up; the token also works mid-sentence ("run /skill:release-checklist for 1.2.0").
- Filters: `skills.ignoredSkills` (glob, exclude), `skills.includeSkills` (glob allowlist; empty = all), `disabledExtensions: [skill:<name>]`, `--no-skills`, `--skills git-*,docker`, `skills.enabled`.
- Precedence: `native` 100 > `omp-plugins` 90 > `claude` 80 > `claude-plugins`/`agents`/`codex` 70 > `opencode` 55 > `github` 30 (`.github/skills/`) > `omp-managed` 5 (auto-learned, Module 9). Dedup by name, first wins.
- Decision table:

| You want… | Use | Loaded |
|---|---|---|
| Facts every session needs (layout, commands) | `AGENTS.md` | once, at start |
| A prohibition that must hold all session | `RULES.md` / `alwaysApply` rule | every request |
| A procedure only relevant to some tasks, model-selected | rule with `description` **or** skill | on demand via `rule://`/`skill://` |
| A procedure with helper files (templates, scripts) | skill | on demand |
| A prompt *you* fire with arguments | command | on `/name` |
**Try it (Walkthrough):**
1. `mkdir -p .omp/skills/release-checklist` and copy `SKILL.md` + `report.md` from `solutions/dot-omp/skills/release-checklist/`.
   Expected: `omp read skill://release-checklist` in your shell prints the file; `omp read skill://release-checklist/report.md` prints the table.
2. Restart omp; ask: `Which skills do you have available? Names and descriptions only.`
   Expected: `release-checklist` with its description, no `read` card.
3. Ask: `Cut release 0.2.0 — follow your release skill.`
   Expected: a `read` card for `skill://release-checklist`, then bash cards for `git status --porcelain` and the tests; no `git tag` executed.
4. Type `/skill:release-checklist 0.2.0`.
   Expected: the injected message names the skill and `[Skill directory: …/.omp/skills/release-checklist]`, then the same workflow.
5. Ask: `read skill://release-checklist/report.md and fill it in for the run you just did`.
   Expected: the filled table.
**Guided task:** Goal: add `hide: true` and prove "hidden ≠ disabled". Hints: restart, repeat step 2 (skill absent from the list), then step 4 and step 1's shell command. Checkpoint: `/skill:release-checklist` still works. Pass condition: the skill is missing from the model's list but `skill://release-checklist` still resolves.
**Stretch:** Goal: put a second copy of the skill in `~/.omp/agent/skills/release-checklist/` with a different description and show which wins (native project vs native user are the same provider — first scanned wins; check `/extensions` and the model's list). Then exclude it with `skills.ignoredSkills: ["release-*"]` and confirm both copies disappear. Pass: `omp read skill://release-checklist` fails after the ignore.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Skill not discovered | Nested more than one level, or missing `description` | Flatten; add `description` |
| `/skill:name` not offered | `skills.enableSkillCommands` false | `omp config set skills.enableSkillCommands true` |
| `skill://name/../x` rejected | Traversal guard | Keep assets inside the skill dir |
| Two skills, only one loads | Same name; first provider wins | Rename or `ignoredSkills` |
| Skill loads but the model never uses it | Weak description | Say *when* to use it in `description` |
**Cheat sheet:**

| Item | Value |
|---|---|
| Layout | `.omp/skills/<name>/SKILL.md` (+ assets) |
| Read | `skill://<name>`, `skill://<name>/<asset>`; `omp read skill://…` |
| Invoke | `/skill:<name> [args]` (`skills.enableSkillCommands`, default true) |
| Filter | `skills.ignoredSkills`, `skills.includeSkills`, `skills.customDirectories`, `--no-skills`, `--skills` |
**Source:** omp://skills.md, omp://config-usage.md ("Directory admission rules")

---

## Lesson 6.7 — Settings layering & profiles              (~20 min)
**You will be able to:** predict the effective value of any setting; put repo-specific settings in `.omp/config.yml`; use one-shot overlays; keep a separate profile.
**Why this exists:** You want `yolo` at home, `write` in the client repo, `always-ask` in CI, and none of those choices should overwrite each other. omp resolves every key through six layers with two merge rules. Once you know the layers and that **arrays replace, objects merge**, every "why is this setting not applying?" has a 30-second answer: `omp config get <key>` from the right directory.
**Demo:** `demos/07-settings.md`
**Concepts:**
- Precedence, low → high: built-in defaults < `~/.omp/agent/config.yml` (global) < `<cwd>/.omp/config.yml` (project; also legacy `.omp/settings.json`) < overlays (`PI_CONFIG_FILES` list, then each `--config <file>` in order) < runtime overrides (`--model`, `--approval-mode`, `--yolo`, …) < a setting's declared env var (`PI_PY`, `OMP_AUTH_BROKER_URL`, …).
- Merge: objects deep-merge key by key; **scalars and arrays are replaced wholesale** by the higher layer (`disabledProviders`, `enabledModels`, `cycleOrder`, `extensions`, …).
- Project settings are read only from the **process cwd's** `.omp/` (non-empty) — no ancestor walk (verified: `write` at the root, `yolo` in `api/`). Other tools' project files (Claude, Codex, Gemini, Cursor, OpenCode) can contribute settings too.
- `omp config list [--json]` · `get <key> [--json]` · `set <key> <value>` · `reset <key>` · `path`. `set`/`reset` and `/settings` **always write the global file**; when another layer still wins, `set` tells you (`--json` → `"overriddenBy": "project"`, verified). To change a project value, edit `.omp/config.yml` by hand (exception: `modelRoleStorage: project` stores model-role picks there).
- Value parsing for `set`: booleans `true/false/yes/no/on/off/1/0`; arrays and records as JSON strings (`'["anthropic"]'`, `'{"bash":"prompt"}'`); keys must be exact schema paths (`theme.dark`, not `theme`).
- Overlays: `--config` is accepted by the launch command, `acp` and `models` — **not** by `omp config` (verified error). From a shell use `PI_CONFIG_FILES=./ci.yml omp config get …` (verified). A missing/invalid overlay is a hard error, never a silent fallback.
- Profiles: `omp --profile <name>` or `OMP_PROFILE=<name>` (legacy `PI_PROFILE`) relocates the whole agent dir to `~/.omp/profiles/<name>/agent` — its own `config.yml`, `agent.db` (logins), sessions, skills, commands, `AGENTS.md`/`RULES.md`. Keybindings are the one thing inherited from the default profile. `omp --profile <name> --alias <cmd>` writes a shell function `<cmd>() { command omp --profile=<name> "$@"; }` into your rc file and exits (verified: bash → `~/.bashrc`; supported shells bash, zsh, fish, PowerShell). `PI_CODING_AGENT_DIR` relocates only the default profile.
- `/settings` inside a session edits the same global file, showing only keys with UI metadata; `omp config list` is the full schema.
**Try it (Walkthrough):**
1. Copy `solutions/dot-omp/config.yml` to `.omp/config.yml` (sets `tools.approvalMode: write`, `theme.dark: titanium`, `secrets.enabled: true`).
   Expected: `omp config get tools.approvalMode` in the repo root prints `write`.
2. `cd .. && omp config get tools.approvalMode && cd -`.
   Expected: `yolo` (the global default) outside the repo.
3. `omp config set tools.approvalMode yolo --json` from the repo root.
   Expected: `{"key":"tools.approvalMode","value":"yolo","overriddenBy":"project"}` — written globally, still shadowed here. Then `omp config reset tools.approvalMode`.
   Expected: `✔ Reset tools.approvalMode to write` (the effective value is the project's).
4. `printf 'tools:\n  approvalMode: always-ask\n' > /tmp/ci.yml && PI_CONFIG_FILES=/tmp/ci.yml omp config get tools.approvalMode`.
   Expected: `always-ask` — overlay beats project.
5. `omp --config /tmp/ci.yml` in the repo, ask for any file edit.
   Expected: an approval prompt card (always-ask), unlike a plain `omp` launch (write).
**Guided task:** Goal: demonstrate array replacement. Hints: `omp config set disabledProviders '["ollama","groq"]'` (global), then add `disabledProviders: [groq]` to `.omp/config.yml`. Checkpoints: `omp config get disabledProviders --json` inside prints only `groq`; outside prints both. Pass condition: you can state which list is effective in each directory, then `omp config reset disabledProviders` and remove the project key.
**Stretch:** Goal: `omp --profile course` with its own login (`/login` inside it), confirm `~/.omp/profiles/course/agent/agent.db` and `config.yml` exist and `omp --profile course config path` prints that directory; create `omp-course` with `--alias` and run `omp-course --version`. Pass: `ls ~/.omp/profiles/course/agent/` lists `agent.db` and `config.yml`; the alias function is in your rc file.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Project setting ignored | Started omp in a subdirectory, or `.omp/` empty, or YAML top level not a mapping | Launch from the dir holding `.omp/`; check `omp config get` |
| `omp config set` "changed the wrong file" | It always writes global | Edit `.omp/config.yml`; read `overriddenBy` |
| Global array vanished in a project | Arrays replace | Repeat the full array in the project layer |
| `--config` "Unknown option" on `omp config` | Overlays only on launch/`acp`/`models` | Use `PI_CONFIG_FILES` |
| Startup fails after adding an overlay | Missing file / invalid YAML / top-level list | Fix the file; overlays never fall back |
| Env var beats config | Declared env vars are the top layer | Unset it (`omp config set --json` names it) |
**Cheat sheet:**

| Command | Purpose |
|---|---|
| `omp config get k [--json]` | effective value (+ provenance hints) |
| `omp config set k v` / `reset k` | write/delete in **global** file |
| `omp config path` | active agent dir |
| `--config f.yml` (repeatable), `PI_CONFIG_FILES=a:b` | one-shot overlays |
| `--profile n`, `OMP_PROFILE=n`, `--alias cmd` | isolated profile at `~/.omp/profiles/n/agent` |
**Source:** omp://settings.md, omp://config-usage.md, omp://cli-reference.md, omp://environment-variables.md

---

## Lesson 6.8 — System prompt customization (overview)              (~10 min)
**You will be able to:** add text to the default system prompt without losing it; know what `SYSTEM.md` throws away; name the template and title/personality files.
**Why this exists:** Context files speak about *the repo*; sometimes you need to change how *the agent* behaves — reporting format, language, delegation policy. omp exposes four files for that, each with a different blast radius. Most teams only ever need `APPEND_SYSTEM.md`.
**Demo:** `demos/08-system-prompt.md`
**Concepts:**

| File / flag | Effect | Keeps default instructions? |
|---|---|---|
| `APPEND_SYSTEM.md` / `--append-system-prompt <text-or-file>` | appends plain text after the default prompt and project content | yes |
| `SYSTEM.md` / `--system-prompt <text-or-file>` | replaces the default instruction block; context files, skills, rules, secrets guidance and the project/environment footer are still generated | **no** — tool policy, workflow rules, internal-URL catalog are gone |
| `SYSTEM_TEMPLATE.md` / `--system-prompt-template <path>` | Handlebars template replacing the instruction block with live data (`{{toolInventory}}`, `{{xdevDocs}}`, …) | only what the template references (named here only) |
| `PERSONALITY.md` (user agent dir only) | replaces the text of the preset chosen by `personality` (`default`, `friendly`, `pragmatic`, `none`) | yes |
| `TITLE_SYSTEM.md` | replaces the prompt used to auto-title sessions | n/a |

- Discovery: project first, then user; within a scope a literal beats a template (`SYSTEM.md` > `SYSTEM_TEMPLATE.md`). Native `.omp/SYSTEM.md` walks up to the nearest non-empty `.omp/`; `.claude`/`.codex`/`.gemini` bases resolve at the launch cwd and home. An explicit flag wins over discovered files; `--system-prompt` and `--system-prompt-template` are mutually exclusive.
- Single-line flag values are tried as a file path first, then used literally; multi-line values are literal.
- Plain files are inserted verbatim — `{{cwd}}` in `SYSTEM.md` reaches the model as those characters. Only the template route compiles Handlebars.
- Task subagents do not receive `APPEND_SYSTEM.md`/`--append-system-prompt` and always run with personality `none`.
- Templates are read once at launch; restart after editing.
**Try it (Walkthrough):**
1. Copy `solutions/dot-omp/APPEND_SYSTEM.md` to `.omp/APPEND_SYSTEM.md` (asks for a `Verified:`/`Untested:` footer). Restart omp.
   Expected: no visible change at start.
2. Ask: `Rename nothing; just run the test suite and report.`
   Expected: the reply ends with `Verified: python3 -m pytest -q (exit 0)` and an `Untested:` line.
3. Start a second terminal: `omp --append-system-prompt "Reply in exactly one sentence."` and ask the same.
   Expected: one sentence; the flag replaced the file's text (flag wins over `APPEND_SYSTEM.md`).
4. Ask in the same session: `What tools do you have? List names only.`
   Expected: the full tool list — the default instructions are intact under append.
**Guided task:** Goal: see what `SYSTEM.md` removes. Hints: `printf 'You are a code reviewer. Never edit files. Cite paths in backticks.\n' > .omp/SYSTEM.md`; restart; ask step 4's question and then ask for the test command from context. Checkpoints: tools still exist (schemas are still sent) but the reply no longer follows the default workflow rules; `AGENTS.md` facts still answered (context files survive). Pass condition: after `rm .omp/SYSTEM.md` and restart, the default behaviour is back. Do not leave `SYSTEM.md` in the lab repo.
**Stretch:** Goal: `~/.omp/agent/PERSONALITY.md` with one sentence of style guidance, plus `omp config set personality pragmatic` to compare presets. Pass: two sessions with visibly different tone; `omp config reset personality` afterwards.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Agent stopped using `todo`/delegation conventions | `SYSTEM.md` replaced the instruction block | Use `APPEND_SYSTEM.md` instead |
| `--append-system-prompt notes.md` sent the literal string | File not found → literal | Check the path |
| Template edits not applied | Read once at launch | Restart omp |
| `PERSONALITY.md` in `.omp/` ignored | User agent dir only | Move to `~/.omp/agent/` |
| Subagents ignore the append text | Not inherited by task subagents | Put it in a rule instead |
**Cheat sheet:**

| Goal | Use |
|---|---|
| Add instructions, keep everything | `APPEND_SYSTEM.md` / `--append-system-prompt` |
| Replace instruction block (plain) | `SYSTEM.md` / `--system-prompt` |
| Replace with live-data template | `SYSTEM_TEMPLATE.md` / `--system-prompt-template` |
| Tone only | `PERSONALITY.md` + `personality` setting |
| Session titles | `TITLE_SYSTEM.md` |
**Source:** omp://system-prompt-customization.md, omp://config-usage.md (`TITLE_SYSTEM.md`), omp://settings.md (`personality`)

---

## Lesson 6.9 — Secrets              (~15 min)
**You will be able to:** turn on secret obfuscation; add a project pattern; explain what the provider sees versus what a tool executes.
**Why this exists:** The agent reads `.env` files, config dumps and logs — and every byte it reads is sent to a model provider. Secret obfuscation swaps configured and credential-shaped values for deterministic placeholders **before** text leaves the process, then restores the real values inside model-authored tool arguments so `curl -H "Authorization: $TOKEN"` still works. The model reasons about `$$LABTOKEN_3P8W5JH1TK2Q:L$$`; your shell gets the token.
**Demo:** `demos/09-secrets.md`
**Concepts:**
- **Off by default.** Enable with `secrets.enabled: true` (in `.omp/config.yml` for the repo, `omp config set secrets.enabled true` globally, or `/settings`).
- Sources collected at session start: (1) environment variables whose names contain `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PASS`, `AUTH`, `CREDENTIAL`, `PRIVATE`, `OAUTH` with values ≥ 8 chars; (2) `secrets.yml` entries — global `~/.omp/agent/secrets.yml`, project `<cwd>/.omp/secrets.yml` (project overrides global on identical `content`); (3) built-in regexes for GitHub/GitLab/OpenAI/Anthropic tokens, AWS keys, Google API keys, Slack, npm, Stripe, Hugging Face, SendGrid, JWTs, `Bearer` headers, PEM blocks; (4) passwords inside `scheme://user:password@host` env values.
- `secrets.yml` is a YAML **array** of `{type: plain|regex, content, mode?: obfuscate|replace, replacement?, flags?, friendlyName?}`. `obfuscate` (default) is reversible; matches shorter than 8 chars are ignored. `replace` is one-way (fixed `replacement` or a same-length value) and can handle short values. Regexes always run globally; `/pattern/flags` literal syntax is accepted. Invalid entries are skipped with a warning; a non-array file is ignored with a warning.
- Placeholders: `$$<12-char HMAC>$$` with a case hint (`:U`, `:L`, `:C`, `:M`) and an optional `FRIENDLYNAME_` prefix. The HMAC key is per install (`~/.omp/agent/secret-placeholder.key`) and never sent, so a transcript reader cannot brute-force placeholders back.
- What sees what: provider-visible text (your messages, tool results, replayed history) carries placeholders; model-authored tool arguments are deep-walked and **restored before execution**; the local TUI/session file restores placeholders for display and resume and re-obfuscates on replay. Replace-mode values are never restored.
- The system prompt gains secret-redaction guidance when enabled, so the model knows a `$$…$$` token is a placeholder, not a value.
- Lab fixture: `.env.example` holds `LAB_TOKEN=labtok_0123456789abcdef` (`labtok_` + 16 lowercase hex) and `DATABASE_URL=sqlite:///data/lab.sqlite`.
**Try it (Walkthrough):**
1. Ensure `.omp/config.yml` has `secrets.enabled: true` (Lesson 6.7) and copy `solutions/dot-omp/secrets.yml` to `.omp/secrets.yml` (`labtok_[0-9a-f]{16}` with `friendlyName: Lab Token`).
   Expected: `omp config get secrets.enabled` in the repo prints `true`.
2. `cp .env.example .env` (gitignored) and restart omp.
   Expected: a normal start; no warning about `secrets.yml`.
3. Ask: `Read .env and tell me: how many characters is the LAB_TOKEN value, does it start with "labtok_", and does it contain "$$"?`
   Expected: the model reports a value that starts with `$$`, contains `LABTOKEN`, is not 23 characters, and says it is a redaction placeholder — it cannot see the real token. (The `read` card on your screen may still display the real value: local display restores placeholders.)
4. Ask: `Run: set -a; . ./.env; set +a; printf '%s' "$LAB_TOKEN" | wc -c; printf '%s' "$LAB_TOKEN" | cut -c1-7`.
   Expected: the bash card prints `23` and `labtok_` — the shell had the real value.
5. Ask: `Echo the LAB_TOKEN value you read in step 3 into a bash command: printf '%s\n' "<that value>" | cut -c1-7`.
   Expected: the model writes the placeholder into the command, omp restores it before execution, and the card prints `labtok_`. This is the restore path in action.
**Guided task:** Goal: compare `obfuscate` with `replace`. Hints: add a second entry `{type: plain, content: sqlite:///data/lab.sqlite, mode: replace, replacement: "<DB-URL>"}`; restart; ask omp to read `.env` and then to run `printf '%s' "$DATABASE_URL"` after sourcing `.env`. Checkpoints: the model reports `<DB-URL>` for the URL; the shell still prints the real URL (it never left the process); asking the model to *echo the URL it saw* prints `<DB-URL>` literally — replace mode is not restored. Pass condition: you can state which of the two entries is reversible and show one card for each.
**Stretch:** Goal: rely on automatic env-var collection only. Hints: remove the regex entry, `export LAB_TOKEN=labtok_0123456789abcdef` in your shell before launching, repeat step 3. Pass: still a placeholder (name matches `TOKEN`, value ≥ 8 chars). Then rename the variable to `LAB_THING` and show it leaks — which is why the project regex exists.
**Troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| Nothing is obfuscated | `secrets.enabled` still `false` in the effective layer | `omp config get secrets.enabled` from the repo root |
| `secrets.yml` ignored with a warning | Top level not an array, or bad regex | Start the file with `- type: …` |
| A short password is not hidden | `obfuscate` skips matches < 8 chars | Use `mode: replace` |
| Model quotes the real value in its reply | Display restores placeholders locally | Ask for length/prefix instead of the literal value |
| Tool got the placeholder, not the value | `replace` mode is one-way | Use `obfuscate` for values tools must use |
**Cheat sheet:**

| Item | Value |
|---|---|
| Enable | `secrets.enabled: true` (default off) |
| Files | `~/.omp/agent/secrets.yml`, `<cwd>/.omp/secrets.yml` |
| Entry | `- type: regex|plain`, `content`, `mode: obfuscate|replace`, `replacement`, `flags`, `friendlyName` |
| Placeholder | `$$[FRIENDLY_]HASH[:U|L|C|M]$$` |
| Restore | in model-authored tool args before execution (obfuscate only) |
**Source:** omp://secrets.md, omp://settings.md (`secrets.enabled`)

---

## Module wrap-up

You now have a `.omp/` tree that makes every session in `omp-course-lab` start informed, holds hard rules on every request, offers `/changelog` and a release skill, prompts before non-workspace actions in this repo only, and hides the lab token from the provider. `exercises.md` consolidates the graded coursework; `cheatsheet.md` is the one-page reference. Module 7 builds on `config.yml` (model roles, providers); Module 9 revisits skills as something the agent writes for itself; Module 11 adds `condition:` to the rules you wrote here; Module 12 uses the same discovery pipeline for extensions and MCP.
