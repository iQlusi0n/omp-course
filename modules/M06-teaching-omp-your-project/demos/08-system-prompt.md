# Demo 6.8 — System prompt customization (~35 s)

Illustrative session output; precedence rules from `omp://system-prompt-customization.md`.

```text
$ cat .omp/APPEND_SYSTEM.md
When you finish a task in this repository, end your reply with a two-line footer:
`Verified: <command> (exit <code>)` and `Untested: <what you could not run, or "nothing">`.

$ omp
> Rename nothing; just run the test suite and report.
▸ bash python3 -m unittest discover -s tests
   Ran 48 tests in 0.71s
   OK (skipped=20)
All 48 tests pass (20 gated issue tests skipped).
Verified: python3 -m unittest discover -s tests (exit 0)
Untested: nothing

$ omp --append-system-prompt "Reply in exactly one sentence."      # flag beats APPEND_SYSTEM.md
> Rename nothing; just run the test suite and report.
▸ bash python3 -m unittest discover -s tests
All 48 tests pass with exit status 0.                                 # no footer: the file's text was replaced
> What tools do you have? List names only.
read, bash, edit, write, grep, glob, lsp, task, todo, ask, web_search, …   # default instructions intact
```

`SYSTEM.md` (Guided task) — the instruction block is replaced, generated sections stay:

```text
$ printf 'You are a code reviewer. Never edit files. Cite paths in backticks.\n' > .omp/SYSTEM.md
$ omp
> What is the test command? Answer from context.
`python3 -m unittest discover -s tests`   ← context files still injected
> Fix the failing test.
I am configured as a reviewer and do not edit files. The failure is in `api/server.py` …
$ rm .omp/SYSTEM.md                        ← do not leave this in the lab repo
```

Blast radius, smallest to largest: `PERSONALITY.md` (tone) < `APPEND_SYSTEM.md` (adds) < `SYSTEM.md` (replaces instructions) < `SYSTEM_TEMPLATE.md` (Handlebars, you own everything you reference).
