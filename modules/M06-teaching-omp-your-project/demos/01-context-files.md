# Demo 6.1 — Context files (~50 s)

Fenced transcript (no recording on the build machine). Shell lines are verified against `omp/18.3.1`; model replies are illustrative.

```text
$ cd omp-course-lab && git checkout -q module-6-start
$ mkdir -p .omp && cp ../modules/M06-teaching-omp-your-project/solutions/dot-omp/AGENTS.md .omp/
$ tail -1 .omp/AGENTS.md
Architecture notes (expanded inline by omp at session start): @../docs/spec.md

$ omp
> /extensions
┌ Extensions ─────────────────────────────────────────────────────────┐
│ Context files                                                       │
│   AGENTS.md        project   native   .omp/AGENTS.md        active  │
│ Rules                                                               │
│   (none)                                                            │
└─────────────────────────────────────────────────────────────────────┘

> What is the test command for this repo, and which directory must you never
> edit? Answer from your context only, do not read files.

The test command is `python3 -m pytest -q`. The `generated/` directory is
build output and must never be edited by hand.

> Quote the first heading of the architecture notes you were given.

"# omp-course-lab specification"          ← came from docs/spec.md via @../docs/spec.md
```

Then, from a subdirectory with its own non-empty `.omp/`:

```text
$ mkdir -p api/.omp && echo "# api-local notes" > api/.omp/AGENTS.md
$ cd api && omp
> /extensions
│ Context files                                                       │
│   AGENTS.md        project   native   api/.omp/AGENTS.md    active  │   ← root .omp/AGENTS.md NOT loaded:
                                                                          nearest non-empty .omp/ wins
$ cd .. && rm -r api/.omp
```

What to notice: no `read` card — the facts came from the injected `<repo-rules>` block; the `@` import resolved relative to `.omp/`, not the repo root; a nearer `.omp/` stops the walk.
