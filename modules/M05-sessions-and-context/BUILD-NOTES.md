# Module 5 — Build notes

Built against `omp/18.3.1` (Linux x64) on 2026-09-25. Build machine: Python 3 only, one Anthropic model logged in; TUI exercised in a pty (120×40) against a throwaway repo (`/tmp/m5lab`) with `--session-dir`, not against `omp-course-lab` (built in parallel).

## Verified live (binary / TUI)

- `omp --help`, `omp worktree --help`, `omp play --help`, `omp clip --help`, `omp share --help`, `omp gc --help`, `omp config --help`.
- `omp config get` defaults: `share.redactSecrets=true`, `share.store=blob`, `share.serverUrl=https://my.omp.sh/s`, `branchSummary.enabled=false`, `branchSummary.reserveTokens=16384`, `treeFilterMode=default`, `doubleEscapeAction=rewind` (enum `rewind|tree|none`), `compaction.handoffSaveToDisk=false`, `compaction.methodOrder=[remote,snapcompact,handoff,shake,soft]`, `compaction.thresholdPercent=-1`, `compaction.asyncEnabled=true`, `compaction.keepRecentTokens=20000`, `compaction.idleEnabled=false`, `compaction.midTurnEnabled=true`, `compaction.autoContinue=true`, `contextPromotion.enabled=false`, `autoResume=false`, `stream.serverUrl=https://live.omp.sh`, `stream.redactPatterns=[]`, `worktree.clone=true`, `worktree.cleanSource=false`, `worktree.base` unset, `statusLine.rightSegments=[session_name,token_total,cost,context_pct]`, `statusLine.contextLine=embedded`.
- `-p` runs: `--session-dir`, `-c`, `--resume <prefix>`, `--fork <prefix>` (header `parentSession` + `providerPromptCacheKey` = source id), `--export <jsonl> <out>`, `omp share <jsonl>`.
- JSONL layout: 256-byte title slot, header v3, entries with `id`/`parentId`; entry types seen: `model_change`, `thinking_level_change`, `message` (user/assistant/toolResult), `credential_pin`, `custom` (`tool_execution_start`, `session_exit`), `title_change`, `label`, `branch_summary`, `reset_boundary`.
- TUI: `/tree` (overlay header, hint line, search, `Shift+L` label → `[milestone]`, `Navigated to selected point`, `Already at this point`), `Summarize branch?` chooser with `branchSummary.enabled=true`, `⑂ branch · ctrl+o` divider, `/rename`, `/fork` message, `/branch` rewind selector footer and `Rewound to selected point`, `/resume` picker layout and footer, `Resumed session`, `/compact`/`/handoff`/`/shake` small-session guard messages, `/record` start/stop messages and `● REC` segment, `/export`, `/dump`, `/share`, `/fresh` (`2 provider states pruned`), `/clear` (`Context reset — 25 messages dropped; session continues.`), terminal breadcrumb file contents, welcome-screen recent sessions.

## Deviations from the outline / docs

1. **`/branch` did not create a new file on our run.** omp://tree.md says a user-message target of `/branch` "branches into a new session file". In the smoke run (`doubleEscapeAction: rewind`, `←` then Enter in the rewind selector) the new prompt was appended as a sibling in the *same* file and no third `.jsonl` appeared. Possible causes: the rewind cursor may have been on a non-user row when Enter fired, or the rewind selector's in-place semantics differ from the documented `/branch` flow. Lessons state the documented behaviour as **[doc]** and tell learners to count files; W1 accepts 2 or 3.
2. **Auto-compaction not exercised.** The only available model has a 1M window; the reserve-based threshold (~850k tokens) is unreachable on a small repo. Lesson 5.5 and G1 lower `compaction.thresholdTokens` (documented: positive value wins) instead of relying on defaults. Divider text `── 📷 compacted · ctrl+o ──` and the `Generating handoff… (esc to cancel)` loader are quoted from omp://compaction.md / omp://handoff-generation-pipeline.md, not observed.
3. **Status-line auto-compact icon** ("pulses while a speculation runs") is doc-only (omp://compaction.md); the outline's "observe icon" step is phrased as "watch the `context_pct` segment and the divider".
4. `/move`, `/wt`, `/delete`, `/restart` were not executed (they change cwd / delete / relaunch the pty process). Usage string `Usage: /move <path>` and the `/delete` / `/restart` descriptions were read from the binary; `/wt` alias `/worktree` and its behaviour come from the binary's changelog strings and the `worktree.cleanSource` setting description. `omp worktree` CLI verified via `--help`.
5. `/resume @claude` / `@codex` and `--from-claude` / `--from-codex`: no foreign sessions on the build machine; documented in omp://session-switching-and-recent-listing.md and `omp --help`, marked Stretch.
6. `omp clip` and `omp stream` need a Stencil login — not attempted; help output verified.
7. `/tree` **[doc]** items not pressed: `Alt+Up/Down`, `Ctrl+O` filter cycle, `Alt+D/T/U/L/A`, `Shift+Enter`. Keys are from omp://tree.md and the overlay's own hint line.
8. The outline lists `/handoff` under "compaction" with `handoffSaveToDisk` — the doc clarifies it applies to **automatic** handoffs only; lesson says so.
9. Outline says `/export` HTML "incl. subagents" — confirmed in doc (`collectSubSessions`); not observed because no `task` ran in the smoke session.
10. `contextPromotionTarget` is a `models.yml` model field, gated by `contextPromotion.enabled=false`; mentioned only, full treatment deferred to Module 7 per outline.

## Dropped as unverifiable

- `/wt` argument syntax was originally dropped; the wave-2 audit read the handler from the binary (`inlineHint: "[<branch>]"`, default `wt/<YYYYMMDD-HHMMSS>`, `Branch '…' already exists` / `Cannot create a worktree while streaming.` / `Moved to worktree … on branch …` strings) and the lesson now states it as **[observed in binary]**. Still not exercised live.
- Exact `/move` semantics beyond "relocates the session, refuses during `/btw`" — from omp://slash-command-internals.md only.
- Keybinding action ids for `/tree` / `/fork` (`app.session.tree`, `app.session.fork`) appear in omp://tree.md and omp://session-tree-plan.md but not in omp://keybindings.md's common table; only `app.session.tree` is mentioned in the README, attributed to tree.md.

## Lab fixture references used

`module-5-start` tag, `notes/`, `api/`, `cli/__main__.py`, `tests/`, `docs/spec.md`, `data/lab.sqlite`, `fixtures/bundle.zip`, `.env.example` `labtok_…`, issue #7 (red-herring investigation) — all per Appendix A / `omp-course-lab/README.md`; no other lab details assumed.

## Wave-2 audit (2026-09-27)

Binary on PATH at audit time: `omp/18.3.5` (README header keeps the 18.3.1 build line and notes the re-audit). Every command, flag, key, setting key, default, path and message in this module was re-checked against `omp://` docs (session.md, session-switching-and-recent-listing.md, session-operations-export-share-fork-resume.md, tree.md, session-tree-plan.md, compaction.md, handoff-generation-pipeline.md, stream.md, settings.md, cli-reference.md, slash-command-internals.md, keybindings.md, environment-variables.md, models.md), `omp --help`, `omp worktree|gc|play|clip|share|tiny-models|config --help`, `omp config get/list` (all 33 setting defaults quoted in the module), UI strings extracted from the binary, and one `-p --session-dir` smoke run (title slot / header v3 / entry types confirmed on 18.3.5).

Fixed in place:

- `cli/main.py` → `cli/__main__.py` (README 5.4 step 1, exercises W1) — the lab has no `cli/main.py`.
- `/wt` now documented as `/wt [<branch>]` with the generated-branch pattern and refusal messages (README 5.1, cheat sheet, exercises S2, solutions S2); `/move` refusal while streaming added.
- `worktree.clone` scope corrected to the binary's description (`/wt`, `github pr_checkout`, bash `git worktree add`; falls back to plain checkout).
- Terminal-id env fallback list corrected to the documented set/order (`ZELLIJ_PANE_ID`, `TMUX_PANE`, `CMUX_SURFACE_ID`, `KITTY_WINDOW_ID`, `WEZTERM_PANE`, `TERM_SESSION_ID`, `WT_SESSION`).
- 5.2 step 2 expectation: breadcrumb has *at least* two lines (a third bookkeeping line was observed).
- `statusLine.contextLine` described per its schema description (how the composer border line reflects context usage; enum `off|percentage|annotated|embedded`).
- `omp config set` always writes the global config (settings.md); project scoping needs a hand-edited `.omp/config.yml` (README 5.5 step 1, exercises G1).
- 5.3 Stretch pass condition: status line shows the session *title*, not an id.
- 5.5 troubleshooting: manual `/compact` "session too small" is not fixed by lowering `thresholdTokens` (thresholds govern automatic maintenance).
- Compaction divider: the documented divider is `── 📷 compacted · ctrl+o ──` regardless of method (compaction.md "Display transcript"); method identification now relies on the expanded summary (README 5.5, exercises G1/S3, solutions G1).
- `/tree` compaction rows: `compaction` is not among the entry types the `default` filter hides (tree.md), so the "hidden by default, press Alt+A" claim was replaced by "search `compact`; `Alt+A` shows everything".
- 5.6 guided hint rewritten from doc: export embeds entries + current leaf; pre-`/clear` history retained; compactions rendered chronologically.
- `doubleEscapeAction` enum: omp://settings.md lists only `rewind|none`; `omp config list` shows `rewind|tree|none` and omp://session-tree-plan.md documents the `tree` behaviour — binary wins, lesson unchanged.

### Removed (unverifiable)

- "or a plain `compacted` divider when a text method ran" / "the divider text differs (`📷 compacted` for image frames)" — no doc or binary string supports a method-specific divider.
- "compaction entries are hidden by the default `/tree` filter" — not in tree.md's hidden list.
- "`Ctrl+O`-style expansion exists in the HTML for compactions and branch summaries" — HTML export behaviour for expandable dividers is not documented.
- "`/wt` needs a clean way to name the branch — read its prompt" — `/wt` takes an inline optional branch; no prompt exists in the handler.
