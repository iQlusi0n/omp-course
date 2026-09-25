# Module 9 — Coursework

Built against `omp/18.3.1`. All work happens in `omp-course-lab/` (`git checkout module-9-start`). Every setting below is **off by default**; you enable it in `omp-course-lab/.omp/config.yml` (project-local, hand-edited — `omp config set` writes the global file instead) and restart omp so the tool roster is rebuilt.

**Prerequisites**
- A working model (Module 1) — `learn`, `reflect`, and the checkpoint investigation all need real turns.
- Mnemopi's local embedding model (`BAAI/bge-base-en-v1.5`) needs to be available on first use. If the backend reports "not initialised", set `mnemopi.noEmbeddings: true` (FTS-only) and retry; all exercises pass in FTS-only mode.
- Optional cost control: `mnemopi.llmMode: none` turns off Mnemopi's own extraction/consolidation LLM calls (they otherwise use your `tiny`/`smol` role). Retain/recall still work.

**Clean-up at the end** (so later modules start from a known state): remove the `memory:`, `mnemopi:`, `autolearn:`, and `checkpoint:` blocks from `.omp/config.yml`, or keep them if you like the features. `/memory clear` wipes the Mnemopi databases for this project; `rm -r ~/.omp/agent/managed-skills/<name>` removes a managed skill.

Config used by the whole module (add incrementally as each exercise instructs):

```yaml
# omp-course-lab/.omp/config.yml
memory:
  backend: mnemopi
mnemopi:
  scoping: per-project
  # noEmbeddings: true      # fallback: FTS-only
  # llmMode: none           # optional: no background LLM calls
autolearn:
  enabled: true
checkpoint:
  enabled: true
```

---

## W0 — Confirm the defaults (5 min, Walkthrough)

1. From `omp-course-lab/`: `omp config get memory.backend && omp config get autolearn.enabled && omp config get checkpoint.enabled`.
   Expected: `off`, `false`, `false`.
2. Start `omp`, ask: `which of these tools can you call right now: retain, recall, reflect, memory_edit, learn, manage_skill, checkpoint, rewind?`
   Expected: none of them.
3. `/memory stats`.
   Expected: no backend statistics (backend is `off`).

**Pass:** step 1 prints exactly `off` / `false` / `false`, and omp confirms none of the eight tools is available.

---

## W1 — Retain a fact, recall it in a new session (15 min, Walkthrough)

Lesson 9.1 + 9.2. Enable **only** the `memory:`/`mnemopi:` block from the config above; restart omp inside `omp-course-lab/`.

1. `omp config get memory.backend` (from the repo) → `mnemopi`.
2. In omp: `/memory stats`.
   Expected: Mnemopi bank statistics (the bank is derived from the directory name `omp-course-lab` plus a hash of its absolute path).
3. `remember that this repo's integration tests need DATABASE_URL set`
   Expected: a `retain` card (it may render as `write xd://retain`); result `1 memory stored.`
4. `/new`
   Expected: an empty conversation in the same project.
5. `how do I run integration tests here?`
   Expected: a `recall` or `reflect` card whose result contains `DATABASE_URL` and an `(id: …)`; the answer repeats the fact. Copy the id.
6. `read memory://<id>`
   Expected: a `read` card showing YAML frontmatter (`id`, `bank`, `store`, `memory_type: fact`, `importance: 0.75`, `source: coding-agent-retain`) and the full content.
7. Shell: `ls ~/.omp/agent/memories/mnemopi/`
   Expected: `mnemopi.db` and sibling bank database files.

**Pass:** (a) a `recall`/`reflect` card in the *new* session cites the `DATABASE_URL` fact, and (b) `read memory://<id>` returns the row with frontmatter. (`read memory://root` is *not* the check here — that URL is file-backed and only exists under `memory.backend: local`.)

---

## G1 — Learn a lesson from issue #6 and promote it to a skill (20 min, Guided)

Lesson 9.3. Add the `autolearn:` block; restart omp.

**Goal.** Solve the misleading-error gotcha in `docs/ISSUES.md` #6, then make omp (1) store a one-sentence lesson and (2) create a managed skill with the diagnosis procedure, and (3) prove the skill is discoverable in a fresh session.

**Hints.**
- `omp config get autolearn.enabled` from the repo must print `true` before you start; `learn` also needs the `mnemopi` backend from W1 to still be on.
- Work #6 as in Module 3: reproduce, read the error, find the *actual* cause (the fixture's error text points at the wrong place).
- Ask for the lesson first, without a skill: "learn this as one durable lesson: the error says X, the real cause is Y, check Z first."
- Then either `manage_skill create` (usable immediately) or a second `learn` with `skill.action: create` (usable after `/new`). Pick a kebab-case name, e.g. `lab-issue-6-misleading-error`.
- After creating the skill, `/new` and `read skill://<name>`.

**Checkpoints.**
1. `learn` card result: `Lesson stored.` (Mnemopi stores it as a `fact` with `importance 0.8`.)
2. Skill creation result: `Created managed skill "<name>" (managed-skills/<name>/SKILL.md).` — or, via `learn`, `Lesson stored. Created managed skill "<name>".`
3. Shell: `cat ~/.omp/agent/managed-skills/<name>/SKILL.md` shows generated `name:`/`description:` frontmatter and your body.
4. In a fresh session, `read skill://<name>` returns that body; typing `/skill:` offers `<name>`.

**Pass:** `~/.omp/agent/managed-skills/<name>/SKILL.md` exists **and** a fresh session's `read skill://<name>` returns it. (The outline's `~/.omp/agent/skills/…` path is not where managed skills go — see `BUILD-NOTES.md`.)

---

## G2 — Checkpoint a red-herring investigation, watch the rewind (15 min, Guided)

Lesson 9.4. Add the `checkpoint:` block; restart omp. Memory backend does not matter here.

**Goal.** Investigate `docs/ISSUES.md` #7 (a bug whose obvious suspect is innocent) inside a checkpoint, get a `rewind` report, and show that context usage fell while the report survived.

**Hints.**
- Read `context_pct` on the right of the status line before you begin and again after the turn ends.
- Prompt shape: "Set a checkpoint with goal '…'. Investigate #7 thoroughly — read code, run tests. When done, rewind with a report naming: the real cause, the red herring you ruled out, the file:line to change. Don't fix anything."
- The rewind is applied at *turn end*, not when the `rewind` card appears — wait for the prompt to return.
- Then ask a question that can only be answered from the report, e.g. "What was the red herring?"
- `/tree`, `Alt+A`, search `rewind` to see the `branch_summary` and hidden `rewind-report` entries at the branch point; `Esc` to leave without moving.

**Checkpoints.**
1. First card: `checkpoint` — `Checkpoint created.` / `Goal: …`.
2. Many `read`/`grep`/`bash` cards (the investigation).
3. `rewind` card — `Rewind requested.` / `Report captured for context replacement.`
4. After the prompt returns, `context_pct` is lower than at its peak during the investigation.
5. The follow-up question is answered from the report without re-investigating and without another `rewind`.

**Pass:** `context_pct` after the turn < `context_pct` during the investigation, **and** the follow-up answer reproduces the report's three items.

---

## S1 — Correct a retained fact with `memory_edit`, then `/memory stats` (10 min, Stretch)

Lesson 9.2. Backend `mnemopi` still on.

**Goal.** The W1 fact is incomplete: integration tests need `DATABASE_URL` *pointing at a scratch database*. Make omp correct the stored memory in place — the safe way — and confirm with statistics.

**Pass:** the transcript shows, in order, (1) a `read memory://<id>` card for the row, (2) a `memory_edit` card with `op: update` and result `Memory <id> updated in bank <bank> (working).`, (3) a `recall` in a new session whose bullet contains "scratch", and (4) `/memory stats` rendering Mnemopi statistics.

Bonus: repeat with `op: invalidate` and a `replacement_id` instead of `update`, and explain in one line when you would prefer it (answer in `solutions/S1.md`).

---

## S2 — The `local` backend's `learned.md` (10 min, Stretch, optional)

Lessons 9.1 + 9.3. Switch `memory.backend` to `local` (keep `autolearn.enabled: true`); restart.

**Goal.** Show that `learn` on the `local` backend writes a file you can read through `memory://root/learned.md` in the *next* session, and that the four Mnemopi tools are gone.

**Pass:** (a) omp confirms `retain`/`recall`/`reflect`/`memory_edit` are unavailable; (b) `learn` returns `Lesson stored.`; (c) `cat ~/.omp/agent/memories/*/learned.md` shows your lesson as the newest bullet; (d) after `/new`, `read memory://root/learned.md` returns it. Restore `memory.backend: mnemopi` (or remove the block) afterwards.
