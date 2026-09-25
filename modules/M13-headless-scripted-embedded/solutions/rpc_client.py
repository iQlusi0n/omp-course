#!/usr/bin/env python3
"""Minimal omp RPC client written against omp://rpc.md (protocol v1/v2 wire frames).

Stdlib only. Spawns `omp --mode rpc --no-ui`, negotiates protocol v2, sends one
prompt, streams text deltas to stdout, and aborts after --abort-after seconds
(or lets the turn finish when --abort-after is 0).

Exit codes: 0 = prompt_result observed (completed or aborted as requested),
1 = something else (error status, timeout, process died).

Usage:
  python3 rpc_client.py "Summarize this repo in 3 bullets"
  python3 rpc_client.py --abort-after 2 "Write a 2000 word essay about rivers"
  python3 rpc_client.py --model claude-haiku-4-5 --tools read,grep,glob "List the tests"
"""
import argparse
import base64
import json
import subprocess
import sys
import threading
import time
from queue import Empty, Queue


class OmpRpc:
    """One NDJSON frame per line on stdin/stdout. See omp://rpc.md 'Transport and Framing'."""

    def __init__(self, extra_args):
        cmd = ["omp", "--mode", "rpc", "--no-ui", *extra_args]
        self.proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1
        )
        self.frames = Queue()
        self._seq = 0
        self._chunks = {}  # chunkId -> list of parts (v2 rpc_chunk reassembly)
        threading.Thread(target=self._reader, daemon=True).start()
        ready = self.next_frame(timeout=30)
        assert ready and ready["type"] == "ready", f"expected ready frame, got {ready}"
        self.ready = ready
        if 2 in ready.get("supportedProtocolVersions", []):
            resp = self.call("negotiate_protocol", protocolVersion=2)
            assert resp["success"], resp

    def _reader(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            frame = json.loads(line)
            if frame.get("type") == "rpc_chunk":  # v2 lossless chunking
                parts = self._chunks.setdefault(frame["chunkId"], [None] * frame["count"])
                parts[frame["index"]] = base64.b64decode(frame["data"])
                if all(p is not None for p in parts):
                    raw = b"".join(parts)
                    assert len(raw) == frame["byteLength"]
                    del self._chunks[frame["chunkId"]]
                    frame = json.loads(raw.decode("utf-8"))
                else:
                    continue
            self.frames.put(frame)
        self.frames.put(None)  # EOF

    def send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def next_frame(self, timeout=None):
        try:
            return self.frames.get(timeout=timeout)
        except Empty:
            return None

    def call(self, cmd_type, timeout=30, **fields):
        """Send a command with an id and return its matching response (buffering other frames)."""
        self._seq += 1
        rid = f"req_{self._seq}"
        self.send({"id": rid, "type": cmd_type, **fields})
        deadline = time.time() + timeout
        pending = []
        while time.time() < deadline:
            f = self.next_frame(timeout=max(0.01, deadline - time.time()))
            if f is None:
                break
            if f.get("type") == "response" and f.get("id") == rid:
                for p in pending:  # put back frames we skipped, in order
                    self.frames.put(p)
                return f
            pending.append(f)
        raise TimeoutError(f"no response for {cmd_type} ({rid})")

    def close(self):
        try:
            self.proc.stdin.close()  # EOF => omp drains, disposes session, exits 0
        except Exception:
            pass
        self.proc.wait(timeout=60)
        return self.proc.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--abort-after", type=float, default=0, help="seconds after prompt ack; 0 = never")
    ap.add_argument("--model", default=None)
    ap.add_argument("--tools", default=None, help="comma list passed as --tools")
    ap.add_argument("--timeout", type=float, default=300)
    args = ap.parse_args()

    extra = ["--no-session"]
    if args.model:
        extra += ["--model", args.model]
    if args.tools:
        extra += ["--tools", args.tools]

    rpc = OmpRpc(extra)
    print(f"[ready] protocolVersion={rpc.ready['protocolVersion']} maxFrameBytes={rpc.ready['maxFrameBytes']}", file=sys.stderr)

    state = rpc.call("get_state")["data"]
    print(f"[state] model={state['model']['provider']}/{state['model']['id']} isSettled={state['isSettled']}", file=sys.stderr)

    rpc._seq += 1
    prompt_id = f"req_{rpc._seq}"
    rpc.send({"id": prompt_id, "type": "prompt", "message": args.prompt})
    t0 = time.time()
    aborted_sent = False
    result = None
    deadline = t0 + args.timeout

    while time.time() < deadline:
        f = rpc.next_frame(timeout=0.2)
        if args.abort_after and not aborted_sent and time.time() - t0 >= args.abort_after:
            ack = rpc.call("abort")
            print(f"\n[abort] success={ack['success']}", file=sys.stderr)
            aborted_sent = True
        if f is None:
            continue
        t = f.get("type")
        if t == "response" and f.get("id") == prompt_id:
            print(f"[ack] prompt accepted agentInvoked={f.get('data', {}).get('agentInvoked')}", file=sys.stderr)
            if f.get("data", {}).get("agentInvoked") is False:
                result = {"status": "completed", "agentInvoked": False}
                break
        elif t == "message_update":
            ev = f["assistantMessageEvent"]
            if ev["type"] == "text_delta":
                sys.stdout.write(ev["delta"])
                sys.stdout.flush()
        elif t == "tool_execution_start":
            print(f"\n[tool] {f.get('toolName')}", file=sys.stderr)
        elif t == "prompt_result" and f.get("id") == prompt_id:
            result = f
            print(f"\n[prompt_result] status={f['status']} sessionSettled={f['sessionSettled']}", file=sys.stderr)
            if f["sessionSettled"]:
                break
        elif t == "session_settled":
            print("[session_settled]", file=sys.stderr)
            if result:
                break

    code = rpc.close()
    print(f"[exit] omp exited {code}", file=sys.stderr)
    if result is None:
        return 1
    if aborted_sent:
        return 0 if result["status"] == "aborted" else 1
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
