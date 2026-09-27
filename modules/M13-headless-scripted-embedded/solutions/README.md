# Module 13 — instructor notes (solutions/)

All scripts here were executed on the build machine (omp 18.3.1, `anthropic/claude-haiku-4-5`) in a scratch git repo; the transcripts in `../demos/` are their real output.

| File | Exercise | What it proves |
|---|---|---|
| `ci.yml` | E2 | `tools.approvalMode: always-ask` + per-tool `deny` overlay |
| `ci-review.sh` | E2 | `omp -p --mode json --config ci.yml --tools read,grep,glob --max-time`, `/review` with a JSON verdict, exit 1 on P0 / `verdict: fail` / deadline / unparseable |
| `rpc_client.py` | E3 | raw NDJSON client: ready → `negotiate_protocol` v2 → `get_state` → `prompt` → stream → `abort` → `prompt_result{status:"aborted"}` → stdin EOF → exit 0 |
| `rpc_host_tool.py` | E6 | `set_host_tools` → `host_tool_call` → `host_tool_result` round trip with `--no-tools` |
| `sdk-readonly.ts` | E4 | restricted in-memory session; every identifier from omp://sdk.md (not runnable here: no Bun) |

## E1 — notes/failing.sh

```bash
#!/usr/bin/env bash
omp -p --no-session --mode json --tools read,grep,glob,bash \
  "Run LAB_ISSUE=all python3 -m unittest tests.test_issues and list only the failing test ids, one per line." 2>/dev/null \
| jq -rs '[.[] | select(.type=="message_end" and .message.role=="assistant")] | last
          | .message.content[] | select(.type=="text") | .text'
```
Grading: `bash notes/failing.sh 2>&1 >/dev/null | wc -c` must be `0` — students often forget `2>/dev/null` and get `Working...` in the pipe. If `bash` is not in `--tools` the model cannot run the tests and will guess; that is the teaching moment for "tool pinning changes the answer". The lab's `main` is green; only `LAB_ISSUE=all` (or `=<n>`) makes the seeded `tests/test_issues.py` tests run and fail — a prompt without the variable yields an empty list.

## E2 — ci/review.sh

Use `ci-review.sh` verbatim as the reference. Observed evidence (demo 13.5, 18.3.1): planted P0 → `EXIT=1` with two `P0` rows; clean diff → `EXIT=0`; `--max-time 1` → "failing closed", `EXIT=1`. Audit run (18.3.5, lab with the planted P0 in `cli/__init__.py`): the reviewer answered with prose *and* a fenced JSON block listing the lab's seeded issues as `P1` with `verdict: "fail"` and did not name the planted line — the script now extracts the JSON object from prose/fences and exits `1` on `verdict: "fail"` as well as on a `P0` row, so the pipeline still went red.

Common student mistakes:
- Putting `--yolo` on the command line "to be safe": runtime flags beat `--config`, so the overlay's `always-ask` is overridden (verified: `--config ask.yml --yolo` created the file).
- Deriving pass/fail from `$?` of omp — it is `0` after a refused write.
- Not extracting the JSON: haiku fenced it in every run despite "no code fence", and on the audit run also prefixed a sentence of prose. Search for the fenced block or the outer `{…}` instead of `json.loads` on the whole reply.
- Forgetting `--no-extensions`: a developer's global extension could contribute a tool. The `tools.approval` deny list in `ci.yml` is the backstop.

`/review` is a bundled command; its prompt is built from the working diff in the session cwd (`omp://slash-command-internals.md` §"Code review" mentions `bundled/review/diff.ts`). No native JSON output is documented — hence the prompt-defined schema.

## E3 — RPC abort

Wire sequence to look for in the student's log (from demo 13.2): `response prompt success:true` → text deltas → `response abort success:true` → `agent_end` → `prompt_result … status:"aborted" sessionSettled:true` → `session_settled`.
Guided-task variant (steer instead of abort) was verified: `steer` ack `success:true`, original `prompt_result.status == "completed"`, final text `STEERED`.

Note the `prompt` ack's `data` omits `agentInvoked` when a turn *is* started; only the local-completion case carries `agentInvoked:false`. Students who wait for `data.agentInvoked === true` will hang.

## E4 — SDK

Cannot be graded on the Python-only lab box. On a Bun machine check: `[sessionFile] undefined`, `[tools] read, grep, glob`, and that the write prompt produces no file. If a student's script writes files, the usual cause is `toolNames` without `restrictToolNames: true` (sdk.md: "by itself it is **not** an allowlist").

## E5 — ACP

No ACP client on the build machine; nothing was executed. Grade from the student's editor transcript: one rejected `edit` (tree unchanged), one approved (`git diff --stat` lists the file), and — bonus — no dialog after relaunching with `omp acp --yolo`. If the student reports "yolo in config but still prompted": approval-mode.md says a *default*-config ACP session keeps the client gate; yolo must be set explicitly.

## E6 — host tool

`rpc_host_tool.py` output on the build machine:

```
[set_host_tools] {'toolNames': ['lab_issue']}
[host_tool_call] id=158db42e4e94636d tool=lab_issue args={'number': 1}
Tax is added twice for the last line item when calculating order totals in `api/orders.py`.
[prompt_result] status=completed
```
(The issue text was a stand-in `docs/ISSUES.md` at build time; in the lab, issue #1 is "CLI shows money 10× too large" — the summary must name that `cli/format.py` money-formatting bug.) The `--no-tools` launch flag makes the host tool the only tool, which keeps the grading unambiguous.
