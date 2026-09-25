# Module 10 cheat sheet — Subagents & Parallel Work (`omp/18.3.1`)

## `task` (batch shape, `task.batch: true`)
| | |
|---|---|
| Call | `{ "context": "<shared, required>", "tasks": [ { "name?", "agent?", "task", "outputSchema?", "schemaMode?": "permissive\|strict", "isolated?", "effort?": "lo\|med\|hi" } ] }` |
| Bundled agents | `scout` (read-only, `@smol`) · `reviewer` (`@slow`, spawns `scout`) · `security-reviewer` (read-only) · `task` (`@task`, spawns `*`) · `sonic` (`@smol`, mechanical) |
| Async return | ``Spawned N background agents using <types>.`` → results auto-deliver; ``<id> is now idle — message it via `write agent://<id>` …`` |
| Read results | `read agent://<id>` · `read agent://<id>/key/0` · nested `agent://<id>.<child>` · `read history://<id>` · bare `read history://` |
| Children run with | `tools.approvalMode` **forced `yolo`**, no advisor, no conversation history; inherit `AGENTS.md`, skills, `local://`, approved plan |
| `^` chip | pick a model in the composer → pseudonym `m1`, `m2` usable as `agent` |
| Templates | `omp agents unpack [--project] [--dir D] [--force] [--json]` |

## Agent Hub & steering
| Key / URI | Action |
|---|---|
| `Alt+A` (`app.agents.hub`) · `Ctrl+S` · double-`←` on empty editor | open Hub |
| `j`/`k` · `Enter` · `t` · `Tab` · `PgUp`/`PgDn` · `r` · `x` · `Esc` | select · focus · tree · inspector · scroll · revive **parked** · kill · close |
| Focused child: type + `Enter` · `Esc` / double-`←` | steer or prompt · back to main (never interrupts) |
| `write agent://<id>` (content) · `write agent://all` · `write proc://<id>/kill` | message/steer/revive · broadcast · cancel |
| `read proc://` · `read proc://<id>` · `/jobs` · `wait` (no args) | jobs+services · inspect w/o consuming · snapshot · block for next delivery (30 min cap) |
| Statuses | `running` → `idle` → `parked` (after `task.agentIdleTtlMs` 7 min) · `aborted` (terminal) |
| `/agents` | definition hub: per-agent prewalk / advisor strips (`task.agentPrewalk`, `task.agentAdvisor`) |

## Custom agents
| | |
|---|---|
| Files | `.omp/agents/<name>.md` (project) · `~/.omp/agent/agents/<name>.md` (user); `.claude/agents` etc. skipped |
| Frontmatter | `name`*, `description`*, `tools` (CSV/list, `yield` auto), `spawns` (`*`/CSV), `model` (`@role`/list), `thinkingLevel`, `output`, `blocking`, `autoloadSkills`, `read-summarize`, `prewalk`, `advisor` |
| Precedence | project → user → extension roots → Claude plugins → bundled; first-wins, exact case-sensitive name |
| Model | `task.agentModelOverrides[name]` → frontmatter `model` → parent model; aliases via `modelRoles` |
| Gate | `task.disabledAgents` · parent `spawns` policy · `task.maxRecursionDepth` (2) · `task.enableLsp` (off) |

## Isolation
| | |
|---|---|
| Enable | `task.isolation.enabled` (**true**) + `isolated: true` per item; needs a git repo; rejected in plan mode |
| Backend | `isolation.backend`: `auto` · `apfs` · `btrfs` · `zfs` · `reflink` · `overlayfs` · `projfs` · `block-clone` · `rcopy` (PAL fallback) |
| Integrate | `task.isolation.merge`: `patch` (default, `<id>.patch`) · `branch` (`omp/task/<id>`, cherry-pick, stash) · `task.isolation.apply` (true) · `task.isolation.commits` |
| Lifecycle | isolated agent → `parked`, **not revivable**; transcript via `history://<id>` |
| Worktrees | `omp worktree [list\|clear\|add]` (`--dry-run`, `--all`, `--json`, `-b`, `--detach`); base `~/.omp/wt` (`worktree.base`, `OMP_WORKTREE_DIR`) |

## Orchestration from `eval`
| Python | JS |
|---|---|
| `h = agent(prompt, agent=, label=, schema=, schema_mode=, isolated=, apply=, merge=, tools=)` | `const h = await agent(prompt, { agent, label, schema, schemaMode, isolated, apply, merge, tools })` |
| `.id .agent .handle .status .done() .wait(timeout) .send(msg) .cancel() .output()` | same; `await h.wait()` |
| `wait(handles, timeout=None, raise_errors=True)` | `await wait(handles, { timeout, raiseErrors })` |
| `p = workpool("sonic", name=, context=, tools=)`; `p.push(*items)` `.status()` `.peek()` `.close()` | `const p = await workpool("sonic", { name, context, tools })` |
| `completion(prompt, model="smol\|default\|slow", system=, schema=).wait()` | `completion(prompt, { model, system, schema })` |
| `@tool` / `@tool(name=, description=)`; `tool.defined()`; `tool.undefine(n)` | `tool(fn, { name, description, parameters })` |
| Rules | pool name = aggregate job id; first drain closes it; no `pool.wait()`; children never share your kernel; `eval.tools.enabled` (on); `eval.workpool.freshAgents` (off) |
| Keywords | `orchestrate` · `workflowz` (needs `eval`+`task`; key `magicKeywords.workflow`) · `jevify` (needs `eval`) · lowercase standalone prose only |

## Vibe mode
| | |
|---|---|
| Toggle | `/vibe` · `/vibe <first directive>` · `/vibe` again = exit (**kills all workers**); excluded with plan/goal modes |
| Tiers | `fast` → `sonic` (`@smol`) · `good` → `task` (`@task`); override `task.agentModelOverrides.sonic/.task` |
| Tools | `vibe_spawn {cli, prompt, name?}` · `vibe_send {session, message}` · `vibe_wait {sessions?, timeout?=30}` · `vibe_kill {session}` · `vibe_list {}` |

## Parallel review
| | |
|---|---|
| Pattern | one batch, `agent: reviewer` per target (`git diff`, `git show <sha>`, `git diff main...branch`, `gh pr diff N`) |
| Output | `overall_correctness` · `explanation` · `confidence` · `findings[] {title, body, priority 0-3, confidence, file_path, line_start, line_end}` |
| Security | `agent: security-reviewer` → `coverage_summary`, `findings[]` · single target: `/review`, `/annotate code-review` |
