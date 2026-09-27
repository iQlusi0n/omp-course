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
  "Run LAB_ISSUE=all python3 -m unittest tests.test_issues and list only the failing test ids, one per line. No header, no other text." 2>/dev/null \
| jq -rs '[.[] | select(.type=="message_end" and .message.role=="assistant")] | last
          | .message.content[] | select(.type=="text") | .text'
```
Grading: `bash notes/failing.sh 2>&1 >/dev/null | wc -c` must be `0` — students often forget `2>/dev/null` and get `Working...` in the pipe. Count ids with `grep -c '^tests\.test_issues\.'` rather than `wc -l`: on the 18.3.5 dry run the model prepended `16 of 20 tests failed:` before the ids until the prompt said "No header, no other text". If `bash` is not in `--tools` the model cannot run the tests and will guess; that is the teaching moment for "tool pinning changes the answer". The lab's `main` is green; only `LAB_ISSUE=all` (or `=<n>`) makes the seeded `tests/test_issues.py` tests run and fail — a prompt without the variable yields an empty list.

## E2 — ci/review.sh

Use `ci-review.sh` verbatim as the reference. Observed evidence, by run:
- Demo 13.5 (18.3.1, scratch repo): planted P0 → `EXIT=1` with two `P0` rows; clean diff → `EXIT=0`; `--max-time 1` → "failing closed", `EXIT=1`.
- Audit run (18.3.5, lab with the planted P0 in `cli/__init__.py`): the reviewer answered with prose *and* a fenced JSON block listing the lab's seeded issues as `P1` with `verdict: "fail"` and did not name the planted line. The script now extracts the JSON object from prose/fences and exits `1` on `verdict: "fail"` as well as on a `P0` row, so the pipeline still went red.
- Dry run (18.3.5, lab at `module-13-start`): with the original prompt a **clean** tree also came back `8 finding(s), 0 P0, verdict=fail` (the seeded issues again) → `EXIT=1`. The prompt now says "Review ONLY the lines changed in the working diff … If the diff is empty, answer pass"; with that, clean → `0 finding(s), 0 P0, verdict=pass`/`EXIT=0`, planted P0 → `P0 cli/__init__.py:4 …`/`EXIT=1` in two of three runs (one run answered `pass`). Grade checkpoint 2 on a rerun if the first attempt misses.

Lesson 13.5 Stretch (real CI) — the steps withheld from the learner: create `.github/workflows/review.yml` (or the CI's equivalent) from the "Pipeline skeleton" in the lesson; install omp; export the provider key from the CI secret store as an env var; run `ci/review.sh --max-time 5m`; post the finding rows as a PR comment. Grade on one red run (P0 branch), one green run (after the fix), and `grep -r labtok_ $CI_LOG` finding nothing.

Lesson 13.5 Guided (PR target) — the learner runs `OMP_REVIEW_TARGET=pr://<N> bash ci/review.sh` after confirming `omp read pr://<N>/diff/all` works.

Common student mistakes:
- Putting `--yolo` on the command line "to be safe": runtime flags beat `--config`, so the overlay's `always-ask` is overridden (verified: `--config ask.yml --yolo` created the file).
- Deriving pass/fail from `$?` of omp — it is `0` after a refused write.
- Not extracting the JSON: haiku fenced it in every run despite "no code fence", and on the audit run also prefixed a sentence of prose. Search for the fenced block or the outer `{…}` instead of `json.loads` on the whole reply.
- Forgetting `--no-extensions`: a developer's global extension could contribute a tool. The `tools.approval` deny list in `ci.yml` is the backstop.

`/review` is a bundled command; its prompt is built from the working diff in the session cwd (`omp://slash-command-internals.md` §"Code review" mentions `bundled/review/diff.ts`). No native JSON output is documented — hence the prompt-defined schema.

## E3 — RPC abort

Wire sequence to look for in the student's log (from demo 13.2): `response prompt success:true` → text deltas → `response abort success:true` → `agent_end` → `prompt_result … status:"aborted" sessionSettled:true` → `session_settled`.
Guided-task variant (steer instead of abort) was verified with the frame `{"type":"steer","message":"Stop and instead reply with only the word STEERED"}` sent after N seconds: `steer` ack `success:true`, original `prompt_result.status == "completed"`, final text `STEERED`. The lesson leaves the steer wording to the learner; accept any message whose effect is unmistakable in the final text.

Note the `prompt` ack's `data` omits `agentInvoked` when a turn *is* started; only the local-completion case carries `agentInvoked:false`. Students who wait for `data.agentInvoked === true` will hang.

## E4 — SDK

Cannot be graded on the Python-only lab box. On a Bun machine check: `[sessionFile] undefined`, `[tools] read, grep, glob`, and that the write prompt produces no file. If a student's script writes files, the usual cause is `toolNames` without `restrictToolNames: true` (sdk.md: "by itself it is **not** an allowlist").

Lesson 13.3 Guided (`notes/sdk-count.ts`) — reference prompt for checkpoint (b): "grep for TODO across the repo and summarize"; the table must show `grep ≥ 1` and never a `write`/`edit` row.

Lesson 13.3 Stretch (persist and resume) — the recipe withheld from the learner: `SessionManager.create(process.cwd())`, print `session.sessionFile`; in a second run resume with `SessionManager.continueRecent(process.cwd())` and ask "what did I ask you last time?". Pass when the answer references the first prompt and `omp --resume <id>` opens the same session in the TUI.

## E5 — ACP

No ACP client on the build machine; nothing was executed. Grade from the student's editor transcript: one rejected `edit` (tree unchanged), one approved (`git diff --stat` lists the file), and — bonus — no dialog after relaunching with `omp acp --yolo`. If the student reports "yolo in config but still prompted": approval-mode.md says a *default*-config ACP session keeps the client gate; yolo must be set explicitly.

E5 steps (withheld from the learner): register `omp acp` as an agent server in the editor; open `omp-course-lab`; ask a read-only question (no dialog expected); ask for an edit to `cli/__init__.py` — reject once, then approve once.

Lesson 13.4 Stretch (ACP vs print) — the command withheld from the learner: `omp -p --no-session --config notes/acp-yolo.yml "run python3 -m unittest discover -s tests and report the summary line"` with the overlay set to yolo + `tools.approval.bash: prompt`. Expected: the bash call is refused under `-p` (no UI to satisfy a `prompt` policy) but prompted in ACP; the note must cite approval-mode.md.

## E6 — host tool

`rpc_host_tool.py` output on the build machine:

```
[set_host_tools] {'toolNames': ['lab_issue']}
[host_tool_call] id=158db42e4e94636d tool=lab_issue args={'number': 1}
Tax is added twice for the last line item when calculating order totals in `api/orders.py`.
[prompt_result] status=completed
```
(The issue text was a stand-in `docs/ISSUES.md` at build time; in the lab, issue #1 is "CLI shows money 10× too large" — the summary must name that `cli/format.py` money-formatting bug.) The `--no-tools` launch flag makes the host tool the only tool, which keeps the grading unambiguous.

Lesson 13.2 Stretch — reference prompt from the lesson's earlier wording: "Use lab_issue to read issue #1 and summarize it in one line" (`rpc_host_tool.py` sends the near-identical "Use lab_issue to read issue #1 and summarize the bug in one line.").
