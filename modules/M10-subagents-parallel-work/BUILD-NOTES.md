# Module 10 — build notes

Built against `omp/18.3.1` (wave 1) and re-audited against `omp/18.3.5` (wave 2 audit; `omp --version` on the build machine now reports 18.3.5 — module headers updated). Every command/key/setting was checked against `omp://` docs, `omp --help` / `omp <cmd> --help`, `omp config list` / `omp config list --json` (setting descriptions), `omp agents unpack`, and live eval-kernel introspection.

## Deviations from the outline (doc/binary wins)

| Outline claim | Observed | Action |
|---|---|---|
| Appendix C: "Isolation/worktrees — off" | Real default `task.isolation.enabled = false` (`omp config get` from `/tmp`, 18.3.5). Wave 1 saw `true` because this build repo's own `.omp/config.yml` sets `task.isolation.enabled: true` (project override, reported as the effective value inside the repo). `isolation.backend = auto`, `task.isolation.merge = patch`, `task.isolation.apply = true` are real defaults. | README header, 10.4, cheat sheet, exercises and demo 10.4 now state **default false** and tell the learner to add `task.isolation.enabled: true` to `omp-course-lab/.omp/config.yml` before the isolation exercises (the lab ships an empty `.omp/`). |
| 10.1 "`task.maxConcurrency`" (no default given) | Real default `32` (`omp config get` from `/tmp`, matching `omp://tools/eval.md` "default 32"). Wave 1's `16` was this build repo's `.omp/config.yml` override (`task.maxConcurrency: 16`). | Course states `32`; every `16` in README 10.1/10.5, exercises Ex 4, demo 10.5 and instructor notes corrected. |
| 10.3 "`~/.omp/agent/agents/`" | Confirmed by `omp agents --help` (`--user` writes there) and `omp://task-agent-discovery.md` | None. |
| 10.3 "`^` model chips as ad-hoc agents" | Verified in `omp://task-agent-discovery.md` §User-tagged model agents | None. |
| 10.4 "backends (APFS/btrfs/ZFS/overlayfs/reflink)" | Full enum is `auto apfs btrfs zfs reflink overlayfs projfs block-clone rcopy` | Listed the full enum. |
| 10.4 "`omp worktree`" | `omp worktree [list\|clear\|add]` with `--dry-run`, `--all`, `--json`, `-b/-B`, `--detach`, `-C` (`omp worktree --help`); alias `wt` | Documented the real surface. |
| G exercise: `test-writer` "tools: read/grep/edit/bash" | `edit` cannot create files; a new `tests/test_*.py` needs `write` | Shipped definition uses `read, grep, glob, edit, write, bash`; noted in instructor notes. |
| G exercise: "workpool over 10 files" | Lab at `module-10-start` has 4 `.py` under `api/`, 5 under `cli/`, 6 under `tests/` (`__init__`, `support`, `test_api`, `test_cli`, `test_db`, `test_issues`) — checked with `git ls-tree module-10-start` | Scope widened to `api/`, `cli/`, `tests/` = 15 files (wave 1 said 13; corrected in README 10.5, exercises Ex 4, instructor notes, demo 10.5); `generated/` excluded (RULES fixture). |
| G exercise: "cost from `omp stats`" | `omp stats --summary` / `--json` report per model / per folder, **not per agent** | Exercise measures deltas before/after each run; per-agent cost comes from Agent Hub rows. |
| 10.2 "pinned-agents block (`display.pinnedAgents`, `tui.mouse`)" | Both verified (`omp://agent-hub.md`, `omp://settings.md`; defaults `collapsed`, `false`) | None. |
| 10.1 task item fields | `omp://tools/task.md` §Inputs lists `solutionSpace` as a required item field (lenient validation still spawns without it) | Added to the item shape in README 10.1 and both cheat sheets. |
| 10.3 `read-summarize` on `scout` | `omp://task-agent-discovery.md` says `scout` ships with it disabled, but the unpacked 18.3.5 `scout.md` frontmatter has no such key | Removed the claim from the 10.1 agent table; 10.3 field row states both facts; the 10.3 guided task now *adds* `read-summarize: false` instead of "deleting the line". |
| Exercises prerequisites: `omp config get modelRoles.smol` | `omp config get modelRoles.smol` → `Unknown setting`; `omp config get modelRoles` prints the role map | Exercise header now uses `omp config get modelRoles`. |
| 10.6 guided pass condition | `docs/ISSUES.md` #1 ships a gated test (`LAB_ISSUE=1 python3 -m unittest tests.test_issues`) and names `cli/format.py` | Pass condition now cites the fixture's command and file. |
| Module checkpoint "all three G tasks" | `exercises.md` has four G exercises (2, 3, 4, 6) | Corrected to "all four". |
| `%load modules/M10-…/solutions/workpool-lint.py` | Sessions run from the `omp-course-lab` root, where that path does not exist | Paths changed to `../modules/M10-…` in exercises, demo 10.5 and both helper headers. |
| `solutions/workpool-lint.py` flagged `from __future__ import annotations` as unused (5 lab files) | Run against the real `module-10-start` checkout during the audit | `lint` now skips `__future__` imports; on the untouched checkout only `tests/test_issues.py` has findings (2 unused imports) — demo 10.5 shows those real values. |

## Removed (unverifiable)

- **`/review` sweeping branches/commits "in parallel" as a built-in behaviour (outline 10.7).** No `omp://` doc describes `/review` spawning multiple reviewer subagents. The only `/review` documentation found is `omp://slash-command-internals.md` §12 (it shares a diff resolver with `/annotate code-review` and has base-branch / working-copy / commit / PR targets). Lesson 10.7 therefore teaches the parallel sweep as an explicit batch `task` call with `agent: reviewer` items (fully documented in `omp://tools/task.md` + the bundled `reviewer.md` schema), and presents `/review` as the single-target command from Module 4.
- **`xd://eval/judge` as the location of the `judge()` helper docs (README 10.5).** `omp read xd://eval/judge` on 18.3.5 answers `Tool 'eval' has no doc topics`, and `omp://magic-keywords.md` only names `judge()`; the pointer was removed. `jevify` itself stays (documented in `omp://magic-keywords.md`).
- **`read-summarize: false` as part of the bundled `scout` definition (README 10.1 table, 10.3 guided task).** Not present in the unpacked 18.3.5 `scout.md`; see the deviations table.
- **Exact wording of the disabled-agent preflight error and of the abort delivery text.** Docs say the message "lists enabled alternatives" / "aborted variant points at the transcript only"; no verbatim string. Demos mark these lines as paraphrased.
- **Exact keys inside `workpool().status()`.** Doc: "worker/item counts and context usage". Demo 10.5 marks the dict layout as illustrative.
- **`/agents` as a definition hub** is documented only indirectly (`omp://advisor-watchdog.md`, `omp://settings.md`: "configured from the `/agents` hub; Enter on an agent opens its property strip"). Described at that level of detail only.

## Verification performed on the build machine

- `omp config get` for every setting in the README header table, run from `/tmp` (no project `.omp/config.yml`) so project overrides do not masquerade as defaults; `omp config list --json` for the descriptions of `task.enableLsp`, `worktree.clone`, `worktree.cleanSource`, `worktree.base`. Inside this build repo, `omp config get task.isolation.enabled` / `task.maxConcurrency` print the overridden `true` / `16` — that is the effective value, not the default.
- `omp config set task.agentModelOverrides '{"test-writer":"@task"}'` / `omp config set task.disabledAgents '["test-writer"]'` and `omp config reset <key>` executed and reverted (JSON values accepted as written in Lesson 10.3).
- `omp agents unpack --dir /tmp/m10-agents --json` → read all five bundled definitions (tools, model roles, `output` schemas, `spawns`, reviewer bash allow-list and priority table) quoted in 10.1 / 10.7.
- `omp worktree --help`, `omp worktree list`, `omp worktree clear --dry-run` (real output text in demo 10.4), `omp stats --help`, `omp stats --summary` (`Requests`, `Total Cost` labels), `omp agents --help`, `omp config --help`.
- Python eval kernel (one `omp -p --no-session --tools eval` run on 18.3.5): `inspect.signature` → `agent(prompt, *, agent=None, label=None, schema=None, schema_mode=None, isolated=None, apply=None, merge=None, tools=None)`, `workpool(agent=None, *, name=None, context=None, tools=None)`, `wait(handles, timeout=None, *, raise_errors=True)`, `completion(prompt, *, model='default', system=None, schema=None)`, `tool(fn=None, /, *, name=None, description=None)`.
- JS eval kernel (one run): `String(fn)` → `agent(prompt, opts)`, `workpool(agentName, opts)` (a bare options object is also accepted), `wait(handles, { timeout, raiseErrors = true })`, `completion(prompt, opts)`.
- `solutions/workpool-lint.py`: non-agent parts (`lint`, `lab_files`, `baseline`, `report`) executed against synthetic files with a stubbed `@tool`; findings correct (unused import, trailing whitespace, missing newline; `__all__` re-exports not flagged).
- `solutions/test-writer.md` frontmatter keys (`name`, `description`, `tools`, `model`, `thinkingLevel`, `output`) all appear in the `AgentDefinition` list in `omp://task-agent-discovery.md`; `thinkingLevel` is the spelling the bundled files use.
- **Not run:** any real subagent spawn (`task`, `agent()`, `workpool()`, `/vibe`), Agent Hub interaction, isolation merges. These need a model budget and an interactive TUI; the demo transcripts are fenced reconstructions from the documented output shapes and are labelled as such.

## Fixture dependencies (Appendix A / LabRepo)

- Tag `module-10-start`; branch `conflict-lab` (10.7 branch review target) — both present in `omp-course-lab`; `docs/ISSUES.md` issue #1 (`cli/format.py`, gated test `LAB_ISSUE=1 python3 -m unittest tests.test_issues`) for the 10.6 guided task.
- Test command `python3 -m unittest discover -s tests` (from `omp-course-lab/docs/ISSUES.md`).
- `notes/` gitignored (learner outputs `notes/m10.md`, `notes/m10-review.md`).
- `generated/` must never be pushed to the lint pool (RULES fixture).

## Learner prerequisites stated in the module

- `modelRoles.smol` resolves (scout/sonic/test-writer use `@smol`); `modelRoles.slow` for `reviewer`.
- Git repo (isolation requirement). Linux overlay backends may need `fuse-overlayfs`; `rcopy` always works.
- `gh` only for the optional PR-diff target.
