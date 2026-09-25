---
description: Draft a CHANGELOG.md entry for a version from git history
---
Draft a `CHANGELOG.md` entry for version **$1** (all arguments: `$ARGUMENTS`).

1. Run `git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD` and read the commits since the last tag.
2. Group them under `### Added`, `### Changed`, `### Fixed`. Drop merge commits and pure chores.
3. Show the proposed entry as a fenced markdown block. Do **not** write to `CHANGELOG.md` until I reply "apply".
