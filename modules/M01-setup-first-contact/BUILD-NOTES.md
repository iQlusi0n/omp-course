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
| Test command `npm test` style examples elsewhere in outline | Lab is Python-only; the check is `python3 -m unittest discover -s tests` (the command `omp-course-lab/README.md` and `docs/ISSUES.md` document) | Build constraint. The first build wrote `python -m unittest …`; the Wave-2 audit aligned every occurrence with the lab's `python3` form after observing the real run. |

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
- ~~The lab repo did not yet exist when this module was built (parallel build).~~ **Wave-2 audit:** the lab exists and every fixture reference was cross-checked against `omp-course-lab/README.md` and `docs/ISSUES.md`: tag `module-1-start` (exists; all `module-N-start` tags point at `main`), issue #1 → `cli/format.py` (one line, `money()`), repro `python3 -m cli orders --month 2026-03` → `$1943.94`, gate `LAB_ISSUE=1 python3 -m unittest tests.test_issues`, `notes/` gitignored except `.gitkeep`, `.env.example` with `LAB_TOKEN=labtok_…`, `.omp/` containing only `.gitkeep`. The fix prompt and the overview prompt were re-run against a clean clone of the real lab (`/tmp/m1lab`, deleted afterwards); `demos/05-first-prompt.md`, `solutions/`, and the Lesson 1.5 expectations now show that run instead of the stand-in.
- Whether the status line shows the model name by default: `settings.md` documents `statusLine.preset`/segments but not the default segment set, so Lesson 1.5 only says a status line exists and defers to Module 2.

## Side effects on the build machine

`~/.omp/profiles/course/` was created by the S2 smoke run and removed afterwards. `startup.showSplash` was set and reset (net zero). `omp gc --wal --apply` checkpointed WAL files (benign). The stand-in lab in `/tmp/m1lab` was deleted.

## Audit (Wave 2)

Re-verified every command, flag, key, setting key, path and default in this module against `omp://` docs and `omp … --help`. The binary on the build machine had moved to **`omp/18.3.5`** (`omp --version`) by audit time; the module stays pinned to 18.3.1 course-wide and the README header notes the re-check. Differences observed between the two builds in the surface this module touches: `omp --help` describes `tiny-models` as "session titles, memory, word completion" (was "session titles + memory"); `omp config list | grep -c .` → 526 (was 524); `omp --help` COMMANDS block has 48 entries. Nothing this module teaches changed.

Fixes applied in place:

- Lesson 1.5 / W1 / S3 / demos / solutions: test command `python -m unittest …` → `python3 -m unittest …` (the lab's documented command); expected file named as `cli/format.py`; added the issue's own repro (`$1943.94`) and gate test (`LAB_ISSUE=1 …` → `OK`) to the pass conditions; unittest output quoted as `Ran 48 tests … OK (skipped=20)`.
- Lesson 1.5 Guided / G1 / solutions grading: the pass check `grep -c Working notes/m1.txt` → `0` was a **false failure on the real lab** — the answer quotes the lab README's course title *Working with omp*. Now `grep -cF 'Working...'` (the literal spinner). Observed: bare `grep -c Working` → 1, `-F 'Working...'` → 0.
- Lesson 1.6: legacy `settings.json` lives in `~/.omp/agent/` (not `~/.omp/`) and is renamed `settings.json.bak` (`settings.md`); the lab's `.omp/` is not empty — it holds `.gitkeep` and no `config.yml`.
- Lesson 1.7: `omp commit` row now lists the flags `omp commit --help` documents (`--dry-run`, `--push`, `--no-changelog`).
- `demos/03-terminal-check.md`: illustrative `read README.md` card now quotes the real lab README's first lines.

Additional claims verified by execution during the audit (all on `omp/18.3.5`): `omp config get theme` → `Unknown setting` (exit 1); `omp config get tools.approvalMode --json` output as shown in demo 06; `omp setup --check` error text; `omp gc` dry-run lines; `omp read omp://keybinding.md` "Did you mean"; `omp models anthropic` / `omp models find haiku` tables; `omp usage --provider anthropic --redact` layout; `omp token groq` failure text with `Configured providers:`; `omp --profile course config path`, `omp --profile course token anthropic` (exit 1), `PI_CODING_AGENT_DIR=/tmp/omp-alt omp config path`; `startup.showSplash` set/reset messages; `omp --help | grep -n -- "--mode=\|--print "` → exactly two lines; `sed -n '/^COMMANDS/,/^Environment/p'` → 48 command lines incl. `worktree` and `ttsr`; print-mode `OK` / `PIPED` / `@README.md` → `omp-course-lab`.

## Removed (unverifiable)

- Lesson 1.7 subcommand table, `omp commit` row: the phrase "(atomic split)". Neither `omp commit --help` nor any `omp://` doc describes an atomic-split behaviour (README-only claim per the course-wide corrections list).

No other statement had to be deleted; everything else was either confirmed or corrected in place (see above).
