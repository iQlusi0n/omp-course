# Module 9 — build notes

Built against `omp/18.3.1` on 2026-09-25. Build machine: Python 3 only, no model credentials usable for a live session run, so Walkthroughs could not be executed end-to-end (Appendix D step 4). Everything that *could* be verified without a model was verified on the binary; everything else is grounded in the bundled docs. Demos are illustrative transcripts assembled from the documented tool result strings.

## Verified on the live binary
- `omp --version` → `omp/18.3.1`.
- `omp config get memory.backend` → `off`; `autolearn.enabled` → `false`; `checkpoint.enabled` → `false`; `mnemopi.scoping` → `per-project`; `mnemopi.autoRecall`/`autoRetain` → `true`; `mnemopi.retainEveryNTurns` → `4`; `mnemopi.recallLimit` → `8`; `mnemopi.noEmbeddings` → `false`; `mnemopi.llmMode` → `smol`; `autolearn.autoContinue` → `false`; `autolearn.minToolCalls` → `5`; `memories.summaryInjectionTokenLimit` → `5000`; `tools.xdev` → `true`; `tools.approvalMode` → `yolo`.
- `omp config list` shows `memory.backend = off (off|local|hindsight|mnemopi|sharpshooter)` — the `sharpshooter` value is a real enum member with keys `sharpshooter.intervalMinutes = 5`, `sharpshooter.injectionTokenLimit = 15000`, `sharpshooter.model`.
- `statusLine.rightSegments` default `["session_name","token_total","cost","context_pct"]` — used as the observable for "context % drops" in G2. `statusLine.contextLine = embedded (off|percentage|annotated|embedded)`.
- `skills.enableSkillCommands` effective value `true` with no override in `~/.omp/agent/config.yml` → treated as default-on. Appendix C row "Skills … enableSkillCommands opt-in" disagrees; the lesson states the observed value.
- Project-layer settings: a `.omp/config.yml` containing `memory.backend: local` / `checkpoint.enabled: true` is reflected by `omp config get` **when run from inside that directory**; `omp --cwd <dir> config get …` does *not* apply it. Exercises therefore say "from inside the repo".
- Shell `omp read memory://root` → `Unknown protocol: memory://` with backend `off`, `local` and `mnemopi` (tested with a `--config` overlay). `memory://` is only resolved inside a session, so pass conditions use the in-session `read` tool or filesystem checks.
- `omp config --help`: actions `list|get|set|reset|path|init-xdg`; `omp read --help`; `omp tiny-models list` (used for the memory-model note).

## Deviations from COURSE-OUTLINE.md (doc wins)
1. **W pass condition `read memory://root shows it`** — `omp://memory.md`: "The `memory://root[/…]` rows are file-backed and only exist with `memory.backend: local` … Under `hindsight` or `mnemopi` the root is never written, so those URLs do not resolve — use `recall`/`reflect` (and `read memory://<memory-id>` on `mnemopi`) instead." The W exercise uses `read memory://<id>` instead; `memory://root` is exercised in S2 under the `local` backend.
2. **G pass condition `~/.omp/agent/skills/<managed>/SKILL.md exists`** — `omp://tools/manage_skill.md` and `omp://tools/learn.md`: managed skills are written to `<agent-dir>/managed-skills/<name>/SKILL.md` (default agent dir `~/.omp/agent`). Pass condition changed to `~/.omp/agent/managed-skills/<name>/SKILL.md`.
3. **9.3 "how they surface next session as 'Memory Guidance'"** — the Memory Guidance block is the `local` backend's injected `memory_summary.md` + `learned.md` (`omp://memory.md`). Managed skills surface through skill discovery (`omp-managed` provider, priority 5, discovered unconditionally; `omp://skills.md`), i.e. as skill metadata in the system prompt, `read skill://<name>`, and `/skill:<name>`. The lesson teaches both paths and names the distinction explicitly.
4. **9.1 `/memory view|stats|sync|clear|enqueue`** — the doc table also has `diagnose`, `queue`, `reset` (alias of `clear`), `rebuild` (alias of `enqueue`), and `mm …` (Hindsight). All listed.
5. **9.1 `sharpshooter`** — present in `omp://memory.md`'s table ("Friction-gated project decision files (architecture/product/style), consolidated in the background") and in the binary's enum, but the doc's Guide column is "—" and `omp://settings.md` omits it from the enum list. Mentioned as existing; no exercise.
6. **9.3 "`learn` tool (2000-char lessons, dedup, secret-redacted)"** — those caps and dedup are documented for the **`local`** backend's `learned.md` (`omp://memory.md`, `omp://tools/learn.md`). On `mnemopi`, `learn` stores a `fact` row (`importance 0.8`) and on `hindsight` it queues retention. Stated per backend.
7. **9.2 `reflect` (synthesize)** — on `mnemopi`, `reflect` is "local recall plus formatting. It does not implement the synthesis promised by the generic model-facing `reflect` prompt" (`omp://tools/reflect.md`). Only Hindsight synthesises. Stated explicitly.
8. **G2 "context % drops after rewind"** — rewind is applied at `turn_end`, not when the tool card appears (`omp://tools/rewind.md`). The pass condition compares the value after the prompt returns against the in-investigation peak.

## Claims dropped as unverifiable
- Exact rendering of `/memory stats` / `/memory view` / `/memory diagnose` output (docs describe them as backend-specific; no wording given). Demos use `<…>` placeholders.
- Exact file names of Mnemopi per-project bank databases ("sibling database paths under that Mnemopi directory"). Exercises check for the directory and `mnemopi.db` only.
- Whether the injected `<system-warning>` (checkpoint guard) is rendered in the TUI transcript. Lesson says it may not be visible; the observable is that the turn ends only after `rewind`.
- Whether the local embedding model (`BAAI/bge-base-en-v1.5`) is downloaded automatically on first use vs. must be pre-fetched. Exercises give `mnemopi.noEmbeddings: true` as the fallback, which the docs describe as FTS-only.
- Which secret patterns `learned.md` redaction matches (docs say "common secret/token patterns" only). Solutions tell instructors not to grade on the course's `labtok_…` value.
- `Ctrl+O` visibility of developer-role messages — removed.

## Composed paths (two doc statements joined)
- `~/.omp/agent/memories/mnemopi/mnemopi.db`: `omp://tools/retain.md` ("defaulting beneath the agent memories directory (`mnemopi/mnemopi.db`)") + `omp://tools/learn.md` ("Local backend writes `<agent-dir>/memories/<encoded-cwd>/learned.md`; the default agent directory is `~/.omp/agent`"). A `--profile` relocates the agent dir.

## Fixture dependencies (Appendix A, generic references only)
- Issue #6 (misleading error message) — G1. Issue #7 (red-herring investigation) — G2. Tag `module-9-start`. `.env.example` `labtok_…` only mentioned in solutions as a non-gradable aside. No lab file contents are assumed beyond `docs/ISSUES.md` existing.

## Appendix C coverage
- "Memory backends, `/memory`, `memory://`" — Lesson 9.1 (default `off` called out).
- "`retain`/`recall`/`reflect`/`memory_edit`" — Lesson 9.2 (default off via `memory.backend`).
- "`learn`, `manage_skill`, autolearn" — Lesson 9.3 (default `false`).
- "`checkpoint`/`rewind`" — Lesson 9.4 (default `false`); M11 cross-ref in "Where next".
- "Skills, `skill://`, `/skill:`" (shared with M6) — Lesson 9.3 read-back path.
