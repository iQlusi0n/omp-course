---
alwaysApply: true
agents: main
---
In `api/`, never use `print()` for diagnostics; use `logging.getLogger(__name__)`. `print()` is acceptable only in `cli/`.
