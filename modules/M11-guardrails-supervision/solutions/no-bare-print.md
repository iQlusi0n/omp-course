---
description: CLI output must go through argparse-friendly helpers, not bare print().
astCondition: "print($$$ARGS)"
scope: "tool:edit(cli/*.py), tool:write(cli/*.py)"
interruptMode: tool-only
---
New code under `cli/` must not call `print(...)` directly.

Route output through `cli/log.py`'s `logger` (`from cli.log import logger` → `logger.debug(msg)`); it writes bare messages to stdout, so the CLI tests stay green. For error text keep using `sys.stderr.write(...)` as `cli/__main__.py` does.
