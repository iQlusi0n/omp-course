# Demo 1.5 — First prompt, four ways (~60 s)

Everything below was run on the build machine against a clean clone of `omp-course-lab` at `module-1-start` (audit pass on `omp/18.3.5`; the original build used `omp/18.3.1` and a stand-in repo). Card rendering in the TUI section is illustrative; the tool sequence, arguments and outputs are the real ones from the `--mode json` event stream of the same prompt.

## 1. Interactive fix (TUI)

```text
$ cd omp-course-lab && git checkout module-1-start && git status --short
$ omp

› Read `docs/ISSUES.md` and locate issue #1. Inspect the code it points at for one small bug.
  Make the smallest safe fix — touch only the file that contains the bug.
  Then run `python3 -m unittest discover -s tests` and show me the result.

  ▸ read docs/ISSUES.md
  ▸ read cli/format.py
  Bug: `money()` divides cents by 10 instead of 100.
  ▸ edit cli/format.py                                ← one hashline edit: `cents / 10` → `cents / 100`
  ▸ bash python3 -m unittest discover -s tests         ✓
  ▸ bash LAB_ISSUE=1 python3 -m unittest tests.test_issues; python3 -m cli orders --month 2026-03   ✓

  I fixed issue #1, "CLI shows money 10× too large". The bug was in `cli/format.py` at line 6:
  `money()` divided by `10` instead of `100` when turning cents into dollars. I changed it to
  `cents / 100`, and that's the only change I made.

  Result of `python3 -m unittest discover -s tests`:
  Ran 48 tests in 0.964s

  OK (skipped=20)

  I also checked the issue directly:
  - `LAB_ISSUE=1 python3 -m unittest tests.test_issues` passes (20 tests run, 18 skipped).
  - The repro `python3 -m cli orders --month 2026-03` now ends with
    `12 orders for 2026-03, total $1943.94`, which is the expected value (194394 cents).

[Ctrl+O]                                              ← expand: the bash card shows the same OK block
[Ctrl+C] [Ctrl+C]
$ git diff --stat
 cli/format.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Read the cards, not the prose: the first `bash` card is the evidence that the check you asked for ran; the second is the model going one step further and running the issue's own repro. If there were no `bash` card at all, the "OK" in the prose would be unproven.

## 2. Initial prompt + attachment

```text
$ omp @README.md "What is the first heading in the attached file? Reply with just the heading text."
  omp-course-lab
```

(Real answer from `-p`; in the TUI the same message appears with the attachment listed under it.)

## 3. Print mode — stdout vs stderr

```text
$ omp -p --no-session "Reply with exactly the word OK" > /tmp/out.txt 2> /tmp/err.txt; echo exit=$?
exit=0
$ cat /tmp/out.txt
OK
$ cat /tmp/err.txt
Working...
```

So `omp -p "…" > notes/m1.txt` captures only the answer.

## 4. Piped stdin

```text
$ echo "Reply with exactly the word PIPED" | omp -p --no-session 2>/dev/null
PIPED
```

## 5. The Guided task, for real

```text
$ omp -p --no-session "List the top-level directories and what each is for" > notes/m1.txt
$ grep -c 'api/' notes/m1.txt; grep -c 'cli/' notes/m1.txt; grep -cF 'Working...' notes/m1.txt
1
1
0
$ grep -c Working notes/m1.txt          ← why the pass command matches the dots too
1
$ head -5 notes/m1.txt
This is `omp-course-lab`, the practice repo for the *Working with omp* course. It uses only the Python 3 standard library. …

| Directory | Purpose |
|---|---|
| `api/` | JSON service built on `http.server`, started with `python3 -m api` on 127.0.0.1:8080. Endpoints are `GET /health`, `GET /users/<id>`, `GET /orders?month=&page=` and `POST /signup`. … |
```

The answer legitimately contains the word `Working` (the course title in the lab README), so the pass condition matches the literal spinner `Working...` with `grep -F`.

## 6. Stretch: the same fix as a JSON event stream

```text
$ git checkout -- . && git checkout module-1-start
$ omp -p --no-session --mode json "<the fix prompt>" > notes/m1-events.json
$ grep -c '"edit"' notes/m1-events.json
21
$ python3 - <<'EOF'
import json
for line in open('notes/m1-events.json'):
    e = json.loads(line) if line.strip() else {}
    if e.get('type') == 'tool_execution_start':
        print(e['toolName'], '|', str(e.get('args'))[:80])
EOF
read | {'path': 'docs/ISSUES.md'}
read | {'path': 'cli/format.py'}
edit | {'input': '[cli/format.py#D6EB]\nPUT 6.=6:\n+    return "$%.2f" % (cents / 100)'}
bash | {'command': 'python3 -m unittest discover -s tests'}
bash | {'command': 'LAB_ISSUE=1 python3 -m unittest tests.test_issues; python3 -m cli orders --month 2026-03'}
```

Event types seen in this run: `session`, `agent_start`, `turn_start`/`turn_end`, `message_start`/`message_update`/`message_end`, `tool_execution_start`/`tool_execution_update`/`tool_execution_end`, `agent_end`. Module 13 uses these.
