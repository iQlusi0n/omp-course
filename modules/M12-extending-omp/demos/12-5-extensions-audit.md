# Demo 12.5 — Auditing inherited config (~45 s)

This demo is composed from the documented behavior of `/extensions`, `/mcp list`, `disabledProviders`, and `disabledExtensions` (omp://context-files.md, omp://mcp-config.md). The exact column layout of `/extensions` was not captured on the build machine (no interactive TUI); the *facts* — which file wins and why — are what the docs specify. Verify the layout live in your own session.

Repo state:

```
omp-course-lab/
  .omp/AGENTS.md              native   (priority 100)  depth 0
  .claude/CLAUDE.md           claude   (priority 80)   depth 0   ← same depth, lower priority
  .cursor/rules/style.mdc     cursor   (priority 50)   rule, alwaysApply: true
  .vscode/mcp.json            vscode   (priority 20)   MCP server "lab-fs"
```

```
> /extensions
  context-file  project  .omp/AGENTS.md          native      active
  context-file  project  .claude/CLAUDE.md       claude      shadowed by native
  (~/.claude/CLAUDE.md is absent from this list: foreign user roots load only with enabledProviders)

> /mcp list
  lab-fs   stdio  python3 tools/lab_mcp_server.py data   connected   .vscode/mcp.json (VS Code)
```

Add `disabledProviders: [cursor]` to `.omp/config.yml`, then `/new`: the always-apply rule from `style.mdc` no longer appears in the rulebook / system prompt.

Replace with `disabledExtensions: [context-file:project:AGENTS.md]`, then `/new`:

```
> /extensions
  context-file  project  .omp/AGENTS.md          native      disabled
  context-file  project  .claude/CLAUDE.md       claude      active     ← unshadowed, not dropped
```

Opt a foreign *user* root in (`~/.omp/agent/config.yml`):

```yaml
enabledProviders:
  - claude
```

```
> /extensions
  context-file  user     ~/.omp/agent/AGENTS.md  native      active
  context-file  user     ~/.claude/CLAUDE.md     claude      shadowed by native   (one user file survives)
```
