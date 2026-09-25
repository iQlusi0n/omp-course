---
description: CLI output must go through argparse-friendly helpers, not bare print().
astCondition: "print($$$ARGS)"
scope: "tool:edit(cli/*.py), tool:write(cli/*.py)"
interruptMode: tool-only
---
New code under `cli/` must not call `print(...)` directly.

Route output through the module's existing output helper (search `cli/` for the function that writes to `sys.stdout` and reuse it). If none exists in the file you are editing, write to `sys.stdout.write(...)` with an explicit newline so the output path stays testable.
