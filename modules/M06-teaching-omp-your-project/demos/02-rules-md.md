# Demo 6.2 — `RULES.md` (~40 s)

Model replies are illustrative; file semantics are from `omp://context-files.md`.

```text
$ cat > .omp/RULES.md <<'EOF'
- Never run `git commit`, `git push`, or rewrite history unless the user explicitly asks in the current message.
- Never edit files under `generated/`; change the generator input instead and say so.
- Never add a third-party dependency without asking first.
EOF

(omp is already running)
> /new                                   ← RULES.md is re-discovered on /new and /clear

> read rule://RULES and quote it back verbatim
▸ read rule://RULES
- Never run `git commit`, `git push`, or rewrite history unless …
- Never edit files under `generated/`; …
- Never add a third-party dependency without asking first.

> Add a comment line to the top of the first file you find under generated/
> and commit it.

I can't do either part: this repository's rules forbid editing `generated/`
(it is build output) and committing unless you explicitly ask for a commit.
If you want the comment in the generated file, tell me which generator input
should change and I'll edit that instead — and say "commit it" if you want a commit.

$ git status --porcelain generated/ ; git log -1 --format=%s
                                          ← empty
module-6-start
```

Shadowing gotcha (Guided task):

```text
$ echo 'Always start replies with the word RULE-USER.' > ~/.omp/agent/RULES.md
> /new
> hi
RULE-USER Hello! …
> read rule://RULES
▸ read rule://RULES
Always start replies with the word RULE-USER.      ← project RULES.md is gone: same rule name, user wins
$ rm ~/.omp/agent/RULES.md
```
