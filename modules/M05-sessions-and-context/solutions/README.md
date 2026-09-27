# Module 5 — Instructor notes

## W1 — Tree / label / branch / fork

Expected `notes/m5.md` content:
- File count after step 9: **2 or 3**. `/fork` always creates a second file. `/branch` with the default `doubleEscapeAction: rewind` *should* create a third when the rewind target is a user message (omp://tree.md), but on our verification run the rewind landed in the same file as a sibling branch (see `BUILD-NOTES.md`). Accept either count as long as the learner explains what they saw.
- Scope sentences (any wording): `/tree` = leaf move inside the same file, nothing deleted; `/branch` = rewind selector, prefilled prompt, may create a new file; `/fork` = full copy with new id, `parentSession` = old id, artifact dir copied.
- Verification for the label: `grep -c '"type":"label"' <jsonl>` ≥ 1.
- Verification for the summary: `grep -c '"type":"branch_summary"' <jsonl>` ≥ 1. If the abandoned branch had nothing summarizable the summary text is literally `No content to summarize` — still a pass; point out that a real abandoned branch (with tool calls) produces prose plus a `<files>` list.
- Common failure: learner presses Enter on the leaf → `Already at this point`. Tell them to move the cursor first.
- Common failure: composer not empty when selecting a user row → no prefill (by design).

## W2 — Resets

Check `grep -c reset_boundary` = 1 in the *original* file, and that the `/new` file is gone after `/delete`. Note `/delete` is best-effort; if the file remains, that is a documented caveat, not a learner error.

## G1 — Auto-compaction + handoff

- With `compaction.thresholdTokens: 30000`, reading `docs/spec.md` + `api/` + `cli/` (Appendix A: < 3k LOC total) may still land under 30k tokens. If so, have the learner also read `data/lab.sqlite:orders?limit=200` and `fixtures/bundle.zip` members, or lower the threshold to 20000. Do not go below `compaction.keepRecentTokens` (20000) — nothing would be summarizable.
- Which method runs depends on the model: the `remote` lane needs provider-native server compaction (OpenAI Responses compact; Anthropic compaction beta on Opus 4.6+/Sonnet 4.6+/Fable/Mythos 5 via the official endpoint); other models fall to `snapcompact` (needs image input) then `handoff`/`shake`/`soft`. The divider is the same `── 📷 compacted · ctrl+o ──` in every case; what `Ctrl+O` reveals differs (image frames vs. handoff document vs. `artifact://` references vs. prose). Any of them passes.
- `/handoff` immediately after an auto-compaction reports `Nothing to hand off (already compacted)` — the learner must do a turn or two of work first. This is expected; it is in the hints.
- `/tree` lists `compaction` entries on the active path (search `compact`; `Alt+A` shows all bookkeeping entries too).
- Pass evidence: two `"type":"compaction"` lines in the JSONL (`grep -c '"type":"compaction"'`).

## G2 — Export vs share

- HTML: local, unredacted, includes subagent transcripts, `~400 KB` for a short session.
- Share: encrypted blob ≤ 1 MB, key in URL fragment, `share.redactSecrets` applies only to configured/discovered secrets — if `secrets.enabled` was never set up (Module 6) the `labtok_` value will *not* be redacted; that is a valid observation.
- Accept any two differences from: redaction, size cap/trimming, local file vs remote store, subagent embedding, `--themes`.

## G3 — Per-terminal `-c`

Breadcrumb file names are TTY-derived (`pts-N`) or env-derived (`TMUX_PANE`, …). Two panes → two files. If the learner uses two *tabs* of a terminal that shares a TTY id (rare), fall back to tmux.

## S1 — Record

Recording path is under `<tmpdir>/omp-recordings/`; on macOS `$TMPDIR` is per-user. `omp play` with no argument plays the newest. `omp clip` needs `/login` → Stencil; skip if unavailable.

## S2 — Worktree

`/wt [<branch>]` takes an optional branch name and otherwise generates `wt/<YYYYMMDD-HHMMSS>` (handler read from the binary; not exercised on the build machine). The worktree lands under `worktree.base` / `~/.omp/wt`, so `omp worktree list` must show the entry; `omp worktree clear --dry-run` must list it without removing.

## S3 — Methods

`["shake","soft"]`: shake replaces old tool results with `artifact://N` references — `Ctrl+O` on the divider shows those references; if savings are insufficient, `soft` runs and prose appears. `["snapcompact","soft"]`: requires `model.input` to include `image`; otherwise snapcompact is skipped and `soft` runs — learners on text-only models should report exactly that.

## Grading rubric (all tiers)

| Evidence | Where |
|---|---|
| `.jsonl` count, label, branch summary | `ls`, `grep -c` on the bucket |
| `reset_boundary` present | `grep -c` |
| compaction entries | `grep -c '"type":"compaction"'` |
| HTML + share id | `notes/m5.md`, `notes/m5-session.html` |
| breadcrumbs | `notes/m5.md` |
| recording | `ls /tmp/omp-recordings` |
