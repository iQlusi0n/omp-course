# Module 10 — build notes

Built against `omp/18.3.1` on Linux (Python 3 only; no node/bun on PATH outside omp's own eval kernel). Every command/key/setting was checked against `omp://` docs, `omp --help` / `omp <cmd> --help`, `omp config list`, `omp agents unpack`, and live eval-kernel introspection.

## Deviations from the outline (doc/binary wins)

| Outline claim | Observed | Action |
|---|---|---|
| Appendix C: "Isolation/worktrees — off" | `omp config list` on 18.3.1: `task.isolation.enabled = true`, `isolation.backend = auto`, `task.isolation.merge = patch`, `task.isolation.apply = true` — with no `task.*` keys in `~/.omp/agent/config.yml` | README header table and Lesson 10.4 state **default true**; learners are told to verify with `omp config get`. |
| 10.1 "`task.maxConcurrency`" (no default given) | Default `16` (`omp config list`); `omp://tools/eval.md` says "default 32" for helper fan-out | Course uses the binary's `16`; noted the doc discrepancy here. |
| 10.3 "`~/.omp/agent/agents/`" | Confirmed by `omp agents --help` (`--user` writes there) and `omp://task-agent-discovery.md` | None. |
| 10.3 "`^` model chips as ad-hoc agents" | Verified in `omp://task-agent-discovery.md` §User-tagged model agents | None. |
| 10.4 "backends (APFS/btrfs/ZFS/overlayfs/reflink)" | Full enum is `auto apfs btrfs zfs reflink overlayfs projfs block-clone rcopy` | Listed the full enum. |
| 10.4 "`omp worktree`" | `omp worktree [list\|clear\|add]` with `--dry-run`, `--all`, `--json`, `-b/-B`, `--detach`, `-C` (`omp worktree --help`); alias `wt` | Documented the real surface. |
| G exercise: `test-writer` "tools: read/grep/edit/bash" | `edit` cannot create files; a new `tests/test_*.py` needs `write` | Shipped definition uses `read, grep, glob, edit, write, bash`; noted in instructor notes. |
| G exercise: "workpool over 10 files" | Lab has 9 `.py` under `api/`+`cli/` (per LabRepo agent) | Scope widened to `api/`, `cli/`, `tests/` = 13 files; `generated/` excluded (RULES fixture). |
| G exercise: "cost from `omp stats`" | `omp stats --summary` / `--json` report per model / per folder, **not per agent** | Exercise measures deltas before/after each run; per-agent cost comes from Agent Hub rows. |
| 10.2 "pinned-agents block (`display.pinnedAgents`, `tui.mouse`)" | Both verified (`omp://agent-hub.md`, `omp://settings.md`; defaults `collapsed`, `false`) | None. |

## Claims dropped as unverifiable

- **`/review` sweeping branches/commits "in parallel" as a built-in behaviour (outline 10.7).** No `omp://` doc describes `/review` spawning multiple reviewer subagents. The only `/review` documentation found is `omp://slash-command-internals.md` §12 (it shares a diff resolver with `/annotate code-review` and has base-branch / working-copy / commit / PR targets). Lesson 10.7 therefore teaches the parallel sweep as an explicit batch `task` call with `agent: reviewer` items (fully documented in `omp://tools/task.md` + the bundled `reviewer.md` schema), and presents `/review` as the single-target command from Module 4.
- **Exact wording of the disabled-agent preflight error and of the abort delivery text.** Docs say the message "lists enabled alternatives" / "aborted variant points at the transcript only"; no verbatim string. Demos mark these lines as paraphrased.
- **Exact keys inside `workpool().status()`.** Doc: "worker/item counts and context usage". Demo 10.5 marks the dict layout as illustrative.
- **`/agents` as a definition hub** is documented only indirectly (`omp://advisor-watchdog.md`, `omp://settings.md`: "configured from the `/agents` hub; Enter on an agent opens its property strip"). Described at that level of detail only.
- **`judge()` / `jevify`**: `omp://magic-keywords.md` documents the keyword and setting; the `judge` helper docs live at `xd://eval/judge` inside a kernel and were not expanded here (Module 8 owns eval basics). Mentioned only as a pointer.

## Verification performed on the build machine

- `omp config list` / `omp config get` for every setting in the README header table.
- `omp agents unpack --dir /tmp/m10-agents --json` → read all five bundled definitions (tools, model roles, `output` schemas, `spawns`) quoted in 10.1 / 10.7.
- `omp worktree --help`, `omp stats --help`, `omp agents --help`, `omp cleanse --help`.
- Python eval kernel: `inspect.signature` on `workpool`, `wait`, `completion`, `tool`; `AgentHandle` / `WorkPool` method lists; `@tool` with `Annotated` hints registered and undefined successfully.
- JS eval kernel: `Function.prototype.toString` on `agent`, `workpool`, `wait`; `tool(fn, {name, description, parameters})` registered and undefined successfully.
- `solutions/workpool-lint.py`: non-agent parts (`lint`, `lab_files`, `baseline`, `report`) executed against synthetic files with a stubbed `@tool`; findings correct (unused import, trailing whitespace, missing newline; `__all__` re-exports not flagged).
- **Not run:** any real subagent spawn (`task`, `agent()`, `workpool()`, `/vibe`), Agent Hub interaction, isolation merges. These need a model budget and an interactive TUI; the demo transcripts are fenced reconstructions from the documented output shapes and are labelled as such.

## Fixture dependencies (Appendix A / LabRepo)

- Tag `module-10-start`; branch `conflict-lab` (10.7 branch review target); `docs/ISSUES.md` issue #1 (10.6 guided).
- Test command `python3 -m unittest discover -s tests` (confirmed with LabRepo agent).
- `notes/` gitignored (learner outputs `notes/m10.md`, `notes/m10-review.md`).
- `generated/` must never be pushed to the lint pool (RULES fixture).

## Learner prerequisites stated in the module

- `modelRoles.smol` resolves (scout/sonic/test-writer use `@smol`); `modelRoles.slow` for `reviewer`.
- Git repo (isolation requirement). Linux overlay backends may need `fuse-overlayfs`; `rcopy` always works.
- `gh` only for the optional PR-diff target.
