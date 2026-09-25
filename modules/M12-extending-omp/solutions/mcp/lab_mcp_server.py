#!/usr/bin/env python3
"""lab-fs: a minimal MCP stdio server in Python stdlib (no pip installs).

Speaks newline-delimited JSON-RPC 2.0 on stdin/stdout, which is what omp's
`stdio` transport expects (omp://mcp-protocol-transports.md, "Stdio transport
internals"). Implements the handshake omp performs
(omp://mcp-runtime-lifecycle.md, "Per-server connect pipeline"):

    initialize  ->  notifications/initialized  ->  tools/list  ->  tools/call
    ping / roots/list may arrive at any time; unknown methods get -32601.

Usage (from .omp/mcp.json):
    {"command": "python3", "args": ["solutions/mcp/lab_mcp_server.py", "data"]}

Every tool is jailed to the root directory given as argv[1] (default: cwd).

Design notes that matter for omp (omp://mcp-server-tool-authoring.md, §4):
- omp exposes each tool as `mcp__<server>_<tool>`, lowercased, non-[a-z0-9_]
  replaced by `_`. Server name `lab-fs` + tool `list_files` ->
  `mcp__lab_fs_list_files`.
- omp strips its harness-injected intent field `i` from every tool call's
  arguments before execution and shows it as the card's intent line. The
  bridge doc says a tool whose inputSchema.properties declares `i` keeps it,
  but on omp 18.3.1 the field was already gone upstream: `read_file` declares
  `i` and still reports "[no intent field delivered]". Don't depend on it.
- Optional properties sent as "" or {} are dropped before the call; validate
  the normalized payload, don't assume every field arrives.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

SERVER_NAME = "lab-fs"
SERVER_VERSION = "1.0.0"
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

TOOLS = [
    {
        "name": "list_files",
        "description": f"List files under a directory inside the jailed root ({ROOT}).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory relative to the root. Default: root."},
            },
        },
    },
    {
        "name": "read_file",
        "description": "Read a UTF-8 text file inside the jailed root. Declares `i` so omp's intent is delivered.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File relative to the root."},
                "i": {"type": "string", "description": "Caller intent (injected by omp)."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "sqlite_tables",
        "description": "List tables and row counts of a SQLite file inside the jailed root.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "SQLite file relative to the root (e.g. lab.sqlite)."},
            },
            "required": ["path"],
        },
    },
]


def jailed(rel: str) -> Path:
    p = (ROOT / rel).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError(f"path escapes root: {rel}")
    return p


def tool_list_files(args: dict) -> str:
    base = jailed(args.get("path") or ".")
    if not base.is_dir():
        raise ValueError(f"not a directory: {base}")
    rows = []
    for entry in sorted(base.iterdir()):
        kind = "dir " if entry.is_dir() else "file"
        size = "" if entry.is_dir() else f" {entry.stat().st_size}B"
        rows.append(f"{kind} {entry.relative_to(ROOT)}{size}")
    return "\n".join(rows) or "(empty)"


def tool_read_file(args: dict) -> str:
    p = jailed(args["path"])
    text = p.read_text(encoding="utf-8")
    intent = args.get("i")
    header = f"[intent received: {intent}]\n" if intent else "[no intent field delivered]\n"
    return header + text


def tool_sqlite_tables(args: dict) -> str:
    p = jailed(args["path"])
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        lines = []
        for name in names:
            (n,) = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()
            lines.append(f"{name}: {n} rows")
        return "\n".join(lines) or "(no tables)"
    finally:
        con.close()


HANDLERS = {
    "list_files": tool_list_files,
    "read_file": tool_read_file,
    "sqlite_tables": tool_sqlite_tables,
}

# One MCP *resource* so `read mcp://<resource-uri>` (and `/mcp resources`) has
# something to show. Resources are read-only data the model can pull by URI.
RESOURCE_URI = "lab-fs://listing"
RESOURCES = [
    {"uri": RESOURCE_URI, "name": "root listing", "mimeType": "text/plain",
     "description": f"Recursive listing of {ROOT}"},
]


def resource_listing() -> str:
    rows = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames.sort()
        for f in sorted(filenames):
            rows.append(str((Path(dirpath) / f).relative_to(ROOT)))
    return "\n".join(rows) or "(empty)"


def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def reply(req_id, result: dict) -> None:
    send({"jsonrpc": "2.0", "id": req_id, "result": result})


def error(req_id, code: int, message: str) -> None:
    send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def handle(msg: dict) -> None:
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}

    if req_id is None:  # notification: never answer
        return

    if method == "initialize":
        reply(req_id, {
            "protocolVersion": params.get("protocolVersion", "2025-11-25"),
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": f"lab-fs serves files under {ROOT}. Prefer list_files before read_file.",
        })
    elif method == "ping":
        reply(req_id, {})
    elif method == "tools/list":
        reply(req_id, {"tools": TOOLS})
    elif method == "resources/list":
        reply(req_id, {"resources": RESOURCES})
    elif method == "resources/read":
        uri = params.get("uri")
        if uri != RESOURCE_URI:
            error(req_id, -32002, f"Resource not found: {uri}")
            return
        reply(req_id, {"contents": [{"uri": uri, "mimeType": "text/plain", "text": resource_listing()}]})
    elif method in ("resources/templates/list", "prompts/list"):
        key = "resourceTemplates" if method == "resources/templates/list" else "prompts"
        reply(req_id, {key: []})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        fn = HANDLERS.get(name)
        if fn is None:
            error(req_id, -32602, f"unknown tool: {name}")
            return
        try:
            text = fn(args)
            reply(req_id, {"content": [{"type": "text", "text": text}], "isError": False})
        except Exception as exc:  # report tool failures in-band, per MCP
            reply(req_id, {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True})
    else:
        error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue  # omp does the same with malformed lines: skip, keep going
        try:
            handle(msg)
        except Exception as exc:  # never let one request kill the server
            if msg.get("id") is not None:
                error(msg.get("id"), -32603, f"internal error: {exc}")


if __name__ == "__main__":
    main()
