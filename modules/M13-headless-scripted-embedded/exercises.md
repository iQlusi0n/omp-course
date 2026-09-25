# Module 13 — Exercises

Work in `omp-course-lab` at `git checkout module-13-start`. Put your outputs in `notes/` (gitignored) and `ci/`. A configured model is required for everything except E5; `omp models` must list at least one. Time per exercise is in the header.

Solutions and instructor checks: `solutions/`.

---

## E1 (W, 10 min) — Print only the answer

**Goal:** a one-liner that asks omp headless "list the failing tests" and prints only the final answer.

1. Run the tests once so you know the truth: `python -m pytest -q 2>&1 | tail -3`.
   Expected: the summary line (the lab seeds at least one failing test in the module-13 checkpoint; if it is green, plant a failure by editing any assertion).
2. `omp -p --no-session --mode json --tools read,grep,glob,bash "Run python -m pytest -q and list only the failing test ids, one per line." 2>/dev/null > notes/e1.jsonl`
   Expected: `notes/e1.jsonl` has one JSON object per line; `jq -r .type notes/e1.jsonl | sort | uniq -c` shows `tool_execution_start` ≥ 1 (bash ran).
3. `jq -rs '[.[] | select(.type=="message_end" and .message.role=="assistant")] | last | .message.content[] | select(.type=="text") | .text' notes/e1.jsonl`
   Expected: only the failing test ids.
4. Fold 2+3 into `notes/failing.sh` (script body: the omp command piped into the jq filter). `bash notes/failing.sh`
   Expected: only the test ids on stdout, nothing on stderr (add `2>/dev/null`).

**Pass:** `bash notes/failing.sh | wc -l` equals the number of failing tests in step 1 and `bash notes/failing.sh 2>&1 >/dev/null | wc -c` is `0`.

---

## E2 (G, 20 min) — `ci/review.sh`: read-only review, exit 1 on P0

**Goal:** `ci/review.sh` reviews the working diff with a read-only omp, using `--config ci/ci.yml` for approval and tool pinning, and exits non-zero on a P0 finding.

Hints:
- Start from `solutions/ci-review.sh` and `solutions/ci.yml` if stuck, but write your own first: the pieces are `omp -p --mode json --no-session --config ci/ci.yml --tools read,grep,glob --max-time 5m "/review <ask for JSON>"`, then a parser for the last assistant `message_end`.
- `ci.yml` needs `tools.approvalMode: always-ask` and a `tools.approval` deny list — keys in `omp://settings.md`.
- Models sometimes fence JSON in ```` ``` ```` even when told not to; strip it.
- omp exits `0` when it refuses a tool; your exit code must come from the parsed verdict. Fail closed on unparseable output.

Checkpoints:
1. Clean tree → `bash ci/review.sh; echo $?` → `0` and a line saying 0 P0.
2. Plant a P0 (e.g. `os.system("rm -rf " + input())` in `cli/__init__.py`) → exit `1` with the finding row.
3. `jq -r 'select(.type=="tool_execution_start") | .toolName'` over the raw stream shows only `read`/`grep`/`glob`.
4. `bash ci/review.sh --max-time 1` (or hard-code it) → exit `1`, "failing closed" message, no tree changes.
5. `git status --porcelain` is empty after every run except your planted P0.

**Pass:** exit code observed both ways (checkpoints 1 and 2), and checkpoint 3.

---

## E3 (G, 20 min) — Python RPC client: prompt, stream, abort

**Goal:** a Python script that spawns `omp --mode rpc`, sends a prompt, streams `text_delta`s to stdout, and sends `abort` after N seconds.

Hints:
- Wire protocol: `omp://rpc.md`. First stdout line is `ready`; you may optionally `negotiate_protocol` v2.
- Use an `id` on every command; the ack for `prompt` arrives *immediately*; the real completion is `prompt_result` with the same `id`.
- Abort: `{"id":"a1","type":"abort"}` → response `success:true` → then `prompt_result … "status":"aborted"`.
- Close stdin when done and keep reading stdout to EOF, else omp may not exit.
- Bundled reference implementation: `solutions/rpc_client.py` (stdlib only). If you have the `omp-rpc` Python package from the omp source tree, `RpcClient(...).prompt_and_wait()` wraps most of this — but write the raw version once.

Checkpoints:
1. `python3 notes/rpc.py "Reply with exactly the word: hello"` → prints `hello`, and the script logs `status=completed`.
2. `python3 notes/rpc.py --abort-after 2 "Write a 1500 word essay about rivers"` → partial text, then the abort response `success:true`, then `prompt_result` with `status=aborted`.
3. The omp child exits with code `0` after you close stdin.

**Pass:** checkpoint 2 — the `abort` is acknowledged (`success:true`) **and** the same prompt's `prompt_result.status == "aborted"`.

---

## E4 (G, 15 min, Bun required) — SDK read-only session streaming `text_delta`

**Goal:** a Bun script that creates an in-memory, tool-restricted session and prints streamed text.

Prerequisites: Bun ≥ 1.3.14, `bun add @oh-my-pi/pi-coding-agent`, provider credentials visible to `discoverAuthStorage()` (same as the CLI).

Hints:
- `omp://sdk.md` "Explicit wiring" + "Built-ins and filtering" + "Minimal controlled embed example". Reference: `solutions/sdk-readonly.ts`.
- `toolNames: ["read","grep","glob"]` **and** `restrictToolNames: true`; `sessionManager: SessionManager.inMemory()`.
- Subscribe before `prompt()`; print `event.assistantMessageEvent.delta` for `text_delta`; `await session.dispose()` at the end.

Checkpoints:
1. `bun notes/sdk.ts "List the top-level directories in one line"` streams an answer; the script prints `session.sessionFile` → `undefined`.
2. `bun notes/sdk.ts "Create notes/sdk.txt containing done"` → the model says it cannot write; `notes/sdk.txt` does not exist.
3. `session.getActiveToolNames()` printed → exactly `read, grep, glob`.

**Pass:** checkpoint 1 output plus checkpoint 2 (write attempt rejected, no file).

---

## E5 (S, 15 min, ACP editor required) — `omp acp` in Zed (or any ACP client); approve one write

**Goal:** host omp inside your editor via ACP and observe the permission gate.

Steps (goal only): register `omp acp` as an agent server in the editor; open `omp-course-lab`; ask for a read-only question (no dialog expected); ask for an edit to `cli/__init__.py` — reject once, then approve once.

**Pass:** one rejected `edit` leaves `git diff --stat` empty; one approved `edit` shows `cli/__init__.py` in `git diff --stat`. Bonus: relaunch as `omp acp --yolo` and show the dialog no longer appears.

---

## E6 (S, 20 min) — RPC host tool

**Goal:** from Python, register a host tool `lab_issue(number:int)` returning the matching section of `docs/ISSUES.md`, then prompt the agent to use it.

**Pass:** a `host_tool_call` frame with `toolName:"lab_issue"` is logged; your `host_tool_result` is accepted (no error response); the final assistant text summarizes issue #1's bug. Instructor notes in `solutions/README.md`.

---

## Self-check

| # | Evidence to keep in `notes/` |
|---|---|
| E1 | `failing.sh` + its output |
| E2 | `ci/review.sh`, `ci/ci.yml`, two terminal captures with `echo $?` |
| E3 | `rpc.py` + capture showing `abort` ack and `status=aborted` |
| E4 | `sdk.ts` + capture with `sessionFile undefined` and refused write |
| E5 | screenshot/transcript of the rejected and approved permission dialogs |
| E6 | capture of the `host_tool_call` / `host_tool_result` pair |
