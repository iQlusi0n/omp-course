# Demo 6.5 — Custom slash commands (~40 s)

```text
$ cat .omp/commands/changelog.md
---
description: Draft a CHANGELOG.md entry for a version from git history
---
Draft a `CHANGELOG.md` entry for version **$1** (all arguments: `$ARGUMENTS`).

1. Run `git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD` …
2. Group them under `### Added`, `### Changed`, `### Fixed`. …
3. Show the proposed entry as a fenced markdown block. Do **not** write to `CHANGELOG.md` until I reply "apply".

(omp already running — commands are not watched)
> /reload-plugins
> /chan▌
  /changelog   Draft a CHANGELOG.md entry for a version from git history      ← completion from frontmatter

> /changelog 1.2.0 "since last week"
▸ bash git log --oneline module-6-start..HEAD
   a1b2c3d fix(api): return 404 for unknown order id
   d4e5f6a feat(cli): add --json flag
Proposed entry for **1.2.0** (arguments: `1.2.0 since last week`):
  ## 1.2.0
  ### Added
  - CLI `--json` output flag
  ### Fixed
  - API returns 404 for unknown order ids
Reply "apply" to write it to CHANGELOG.md.

$ git status --porcelain CHANGELOG.md
                                          ← nothing written
```

Expansion recap: `$1` → `1.2.0`; `$ARGUMENTS` (and `$@`) → `1.2.0 since last week` (quotes stripped); `$@[2]` would be `since last week`. An unknown `/typo` is not an error — it reaches the model as literal text.
