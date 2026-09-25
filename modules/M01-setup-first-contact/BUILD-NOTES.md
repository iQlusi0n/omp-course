# Module 1 — Build notes

Built against `omp/18.3.1` on Linux (Debian, Python 3 only). Every command in the lessons was read in `omp://` docs or `omp … --help`; the ones marked *observed* below were also executed on the build machine, which had a working Anthropic credential, so headless (`-p`) walkthroughs were run for real. TUI-only steps could not be recorded (no pty capture tooling); `demos/` transcripts for those are marked illustrative.

## Deviations from COURSE-OUTLINE.md

| Outline says | What the module does | Why |
|---|---|---|
| 1.2: install via `curl -fsSL https://omp.sh/install \| sh`, Homebrew, Bun, Nix, Windows PowerShell, mise | Teaches `curl https://omp.sh/install \| sh` (doc form); mentions that a Homebrew formula and a Nix package exist without giving commands; **drops Bun, PowerShell, mise** | The only install commands in the bundled docs are in `macos-signing-notarization.md` (`curl https://omp.sh/install \| sh`; "Homebrew formula installs"). `PI_PACKAGE_DIR` (`omp --help`) and `nix/package.nix` (`local-models.md`) prove a Nix package exists. Nothing in `omp://` describes Bun, PowerShell or mise installs. `cli-reference.md` and `providers.md`, named as verification sources in the assignment, contain no install commands at all. |
| 1.3: per-terminal table "iTerm2/Kitty OK, Ghostty/WezTerm config snippet, Windows Terminal limits" | Table contains only terminals/hops the docs describe: Windows Terminal, VS Code integrated terminal, SSH/container hop, tmux, Warp. **iTerm2, Kitty, Ghostty, WezTerm, Alacritty rows dropped** | No bundled doc states keyboard-protocol support or config snippets for those terminals. Replaced with an observable two-key test (`Ctrl+O` vs `Ctrl+Shift+O`) and `/hotkeys` + `keybindings.yml` remap, all from `keybindings.md`. |
| 1.5: "the official quickstart prompt" | A course-authored prompt with the same three parts (find bug #1 / smallest safe fix / run the check) | No quickstart prompt text exists in `omp://`; "official" wording could not be verified. |
| 1.6: "`omp setup` wizard" | Described as "runs onboarding setup" plus `omp setup python --check` / `omp setup speech` | `omp setup --help` and the docs say only that much; wizard steps are not documented, so none are described. |
| Troubleshooting: "Alpine musl libs" | **Dropped** | Only `natives-build-release-debugging.md` (out of scope, internal build doc) mentions musl, and only for building addons — no user-facing symptom or fix is documented. |
| Test command `npm test` style examples elsewhere in outline | Lab is Python-only; the check is `python -m unittest discover -s tests` (root README convention) | Build constraint. Observed: on a machine with only `python3`, the model retried with `python3` and reported it. Lessons say so. |

## Citations to internals docs (flag for Main)

Appendix C lists these as out of scope for learner material. Each is cited for exactly one user-facing fact that appears nowhere else in `omp://`; the lessons remain correct if the sentence is cut.

- `macos-signing-notarization.md` — the install command `curl https://omp.sh/install | sh` and the existence of a Homebrew formula; also the "no Gatekeeper prompt" troubleshooting row (Lesson 1.2).
- `tui-core-renderer.md` — tmux needs `extended-keys` for modified keys and `allow-passthrough` for OSC notifications; omp queries the tmux server for the outer terminal type (Lesson 1.3).
- `natives-shell-pty-process.md` — the key parser accepts legacy sequences, xterm `modifyOtherKeys`, and the Kitty keyboard protocol (Lesson 1.3, one sentence naming the protocol the outline asked for). `bash-tool-runtime.md` (in scope) independently mentions Kitty sequences for the PTY overlay.

## Claims verified by execution (observed on the build machine)

- `omp --version` → `omp/18.3.1`.
- `omp completions bash|zsh|fish` scripts: `--resume` present (bash ×3, zsh ×1; fish encodes as `-l resume`).
- `omp update --check` → `Current version: 18.3.1` / `✔ Already up to date`.
- `omp config path` → `/home/user/.omp/agent`; `omp config get tools.approvalMode` → `yolo`; `startup.showSplash` set/reset round-trip with exact messages; `omp config list | grep -c .` → 524.
- `omp --profile course config path` → `…/profiles/course/agent`; `omp --profile course token anthropic` → exit 1 with `No active credential found…`; `PI_CODING_AGENT_DIR=/tmp/omp-alt omp config path` → `/tmp/omp-alt`.
- `omp token groq` with `<cwd>/.env` containing `GROQ_API_KEY=…` prints the value; from `/tmp` it fails and lists `Configured providers:`.
- `omp setup python --check` → `✔ Python execution is ready`; `omp setup --check` without component errors as documented.
- `omp gc` dry-run, `omp gc --wal`, `omp gc --wal --apply` outputs as shown in `demos/07-cli-surface.md`.
- `omp -p --no-session "…"`: answer on stdout, `Working...` on stderr; `echo … | omp -p` reads stdin; `omp -p @README.md "…"` attaches the file.
- Guided task prompt "List the top-level directories and what each is for" against an Appendix-A-shaped stand-in: output mentions `api/` (×2) and `cli/` (×1).
- Fix prompt in `--mode json` against the stand-in with a seeded one-line bug: tool sequence `read`, `read`, `edit`, `bash`, `bash`; `git diff --stat` → 1 file; `grep -c '"edit"'` → 23.
- `omp read omp://` index (134 files), `omp read omp://keybindings.md:1-10`, and the "Did you mean" error for a misspelled doc name.

## Not verified / not executed

- `/login`, `/logout` picker rendering and `omp login` interactive flow (would have required creating or removing real credentials). Described strictly from `providers.md` and `omp login --help`.
- TUI card rendering, `Ctrl+O` / `Ctrl+Shift+O` / `/hotkeys` behaviour (no TUI capture on the build machine). Described from `keybindings.md`; transcripts marked illustrative.
- The lab repo did not yet exist when this module was built (parallel build). All fixture references use Appendix A names: tag `module-1-start`, `docs/ISSUES.md` issue #1, `notes/` (gitignored), `.env.example` with a `labtok_…` token, directories `api/`, `cli/`. The quickstart demo used a stand-in with the same layout and a representative one-line bug; the real issue #1 will differ in file and content but not in shape.
- Whether the status line shows the model name by default: `settings.md` documents `statusLine.preset`/segments but not the default segment set, so Lesson 1.5 only says a status line exists and defers to Module 2.

## Side effects on the build machine

`~/.omp/profiles/course/` was created by the S2 smoke run and removed afterwards. `startup.showSplash` was set and reset (net zero). `omp gc --wal --apply` checkpointed WAL files (benign). The stand-in lab in `/tmp/m1lab` was deleted.
