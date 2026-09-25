#!/usr/bin/env python3
"""E6 solution: expose a host-owned tool over RPC (omp://rpc.md "Host Tool Sub-Protocol").

Registers `lab_issue(number)` which returns the matching `## #N` section of docs/ISSUES.md
from THIS process, then prompts the agent to use it.

Usage: python3 rpc_host_tool.py [--issues docs/ISSUES.md] [--model <id>] [--number 1]
Pass:  stderr shows a host_tool_call for lab_issue and an accepted host_tool_result;
       stdout is the agent's one-line summary.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rpc_client import OmpRpc  # noqa: E402


def issue_text(path: str, number: int) -> str:
    text = Path(path).read_text(encoding="utf-8")
    # Section headed by "#N" (e.g. "## #1 ..." or "### Issue #1"); ends at the next heading.
    m = re.search(rf"^#+[^\n]*#{number}\b[^\n]*\n(.*?)(?=^#+ |\Z)", text, re.M | re.S)
    return m.group(0).strip() if m else f"issue #{number} not found in {path}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issues", default="docs/ISSUES.md")
    ap.add_argument("--model", default=None)
    ap.add_argument("--number", type=int, default=1)
    args = ap.parse_args()

    extra = ["--no-session", "--no-tools"]  # the ONLY tool the model gets is ours
    if args.model:
        extra += ["--model", args.model]
    rpc = OmpRpc(extra)

    resp = rpc.call(
        "set_host_tools",
        tools=[
            {
                "name": "lab_issue",
                "label": "Lab issue",
                "description": "Return the text of issue #<number> from the lab's docs/ISSUES.md",
                "parameters": {
                    "type": "object",
                    "properties": {"number": {"type": "integer"}},
                    "required": ["number"],
                    "additionalProperties": False,
                },
            }
        ],
    )
    print(f"[set_host_tools] {resp['data']}", file=sys.stderr)

    rpc._seq += 1
    pid = f"req_{rpc._seq}"
    rpc.send({"id": pid, "type": "prompt", "message": f"Use lab_issue to read issue #{args.number} and summarize the bug in one line."})

    while True:
        f = rpc.next_frame(timeout=300)
        if f is None:
            break
        t = f.get("type")
        if t == "host_tool_call":
            print(f"[host_tool_call] id={f['id']} tool={f['toolName']} args={f['arguments']}", file=sys.stderr)
            body = issue_text(args.issues, int(f["arguments"]["number"]))
            rpc.send({"type": "host_tool_result", "id": f["id"], "result": {"content": [{"type": "text", "text": body}]}})
        elif t == "host_tool_cancel":
            print(f"[host_tool_cancel] target={f['targetId']}", file=sys.stderr)
        elif t == "message_update" and f["assistantMessageEvent"]["type"] == "text_delta":
            sys.stdout.write(f["assistantMessageEvent"]["delta"])
            sys.stdout.flush()
        elif t == "prompt_result" and f.get("id") == pid:
            print(f"\n[prompt_result] status={f['status']}", file=sys.stderr)
            if f["sessionSettled"]:
                break
        elif t == "session_settled":
            break
    rpc.close()


if __name__ == "__main__":
    main()
