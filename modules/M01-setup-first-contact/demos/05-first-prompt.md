# Demo 1.5 — First prompt, four ways (~60 s)

Everything below was run on the build machine with `omp/18.3.1` against a stand-in of the lab layout seeded with a one-line bug (the shape of issue #1). Card rendering in the TUI section is illustrative; the tool sequence, arguments and outputs are the real ones from the `--mode json` event stream of the same prompt.

## 1. Interactive fix (TUI)

```text
$ cd omp-course-lab && git checkout module-1-start && git status --short
$ omp

› Read `docs/ISSUES.md` and locate issue #1. Inspect the code it points at for one small bug.
  Make the smallest safe fix — touch only the file that contains the bug.
  Then run `python -m unittest discover -s tests` and show me the result.

  ▸ read docs/ISSUES.md
  ▸ read api/math.py
  ▸ edit api/math.py                                  ← one hashline edit: `return a - b` → `return a + b`
  ▸ bash python -m unittest discover -s tests          ✗ exit 127 (command not found: python)
  ▸ bash python3 -m unittest discover -s tests         ✓

  I fixed the bug from issue #1 in `api/math.py`: `add()` was subtracting (`return a - b`)
  instead of adding, so I changed it to `return a + b`. That was the only change, in the only file.

  The exact command you asked for, `python -m unittest discover -s tests`, didn't run because
  this machine has no `python` command (exit code 127). I ran the same thing with `python3`,
  and it passed:

  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.000s

  OK

[Ctrl+O]                                              ← expand: the bash card shows the same OK block
[Ctrl+C] [Ctrl+C]
$ git diff --stat
 api/math.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Read the cards, not the prose: the second `bash` card is the evidence that the check ran; the first one is the evidence that the model noticed a failure and adapted rather than claiming success.

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
$ grep -c 'api/' notes/m1.txt; grep -c 'cli/' notes/m1.txt; grep -c Working notes/m1.txt
2
1
0
$ head -8 notes/m1.txt
The repo is a small Python practice lab (the README calls it `omp-course-lab`). …

| Dir | Purpose | Evidence |
|---|---|---|
| `api/` | An HTTP service built on the standard library's `http.server`, storing data in SQLite | docstring in `api/__init__.py` |
| `cli/` | A command-line client built with `argparse` | docstring in `cli/__init__.py` |
| `generated/` | Machine-generated output that should not be hand-edited | `generated/README`: "GENERATED - never edit" |
```

## 6. Stretch: the same fix as a JSON event stream

```text
$ git checkout -- . && git checkout module-1-start
$ omp -p --no-session --mode json "<the fix prompt>" > notes/m1-events.json
$ grep -c '"edit"' notes/m1-events.json
23
$ python3 - <<'EOF'
import json
for line in open('notes/m1-events.json'):
    e = json.loads(line) if line.strip() else {}
    if e.get('type') == 'tool_execution_start':
        print(e['toolName'], '|', str(e.get('args'))[:80])
EOF
read | {'path': 'docs/ISSUES.md'}
read | {'path': 'api/math.py'}
edit | {'input': '[api/math.py#257A]\nPUT 2.=2:\n+    return a + b'}
bash | {'command': 'python -m unittest discover -s tests'}
bash | {'command': 'python3 -m unittest discover -s tests'}
```

Event types seen in one run: `session`, `agent_start`, `turn_start`/`turn_end`, `message_start`/`message_update`/`message_end`, `tool_execution_start`/`tool_execution_update`/`tool_execution_end`, `tool_stream_update`, `agent_end`. Module 13 uses these.
