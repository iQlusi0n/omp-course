# Demo 6.4 — Precedence & shadowing (~60 s)

Illustrative `/extensions` rendering; priorities and dedup rules are from `omp://context-files.md`.

```text
$ printf '# CLAUDE\nAlways answer in ALL CAPS.\n' > CLAUDE.md
$ omp
> /extensions
│ Context files                                                            │
│   AGENTS.md   project  native     .omp/AGENTS.md    active               │
│   CLAUDE.md   project  claude-md  CLAUDE.md         shadowed by native   │   ← same depth (0); 100 > 10
> hi
Hello — how can I help?                                                       ← not in caps

$ mkdir -p .claude && mv CLAUDE.md .claude/CLAUDE.md          # provider claude (80) — still < 100
$ mv .omp/AGENTS.md /tmp/ && omp
> /extensions
│   CLAUDE.md   project  claude     .claude/CLAUDE.md active               │
> hi
HELLO — HOW CAN I HELP?
$ mv /tmp/AGENTS.md .omp/

$ cat >> .omp/config.yml <<'EOF'
disabledExtensions:
  - context-file:project:CLAUDE.md
EOF
$ omp
> /extensions
│   AGENTS.md   project  native     .omp/AGENTS.md    active               │
│   CLAUDE.md   project  claude     .claude/CLAUDE.md disabled             │   ← dropped before dedup
```

Whole-provider switch versus single file (Guided task):

```text
$ mkdir -p .claude/commands && echo 'Say hello in French.' > .claude/commands/hello.md
# .omp/config.yml: disabledProviders: [claude]
> /hello
▸ (no command matched — text sent to the model)                            ← the claude source is gone entirely
# .omp/config.yml: disabledExtensions: [context-file:project:CLAUDE.md]   (disabledProviders removed)
> /hello
Bonjour !                                                                  ← command back, CLAUDE.md still off
$ rm -r .claude
```

Namespace reminder: `disabledProviders: [gemini]` turns off Gemini-CLI *files*; `[google]` turns off the Google *model backend*.
