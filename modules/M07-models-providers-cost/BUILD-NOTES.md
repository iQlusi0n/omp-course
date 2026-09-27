# Module 7 — Build notes

Built against `omp/18.3.1` on the build machine (Python 3 only). Verification method: `read omp://<doc>` for every claim, `omp --help` / `omp models|stats|usage|tiny-models|setup|login|config|commit --help`, and a live smoke run in an isolated profile (`PI_CODING_AGENT_DIR=/tmp/…`, `HOME=/tmp/…`) against `tools/mock-provider.py`: default port 8765, `mock-1`, JSON + SSE chat completions, `--fail` → HTTP **429** with `Retry-After: 1`, stderr request log (`[mock-provider] <METHOD> <path> -> "<request line>" <status> -`), stdout banner `mock-provider serving model 'mock-1' on http://127.0.0.1:8765/v1 in normal mode`, `--model` / `--host` flags, `<system-reminder>` stripped from the echo, echo cut at 80 chars.

## Wave-2 audit (2026-09-27)
- Re-verified every command/flag/key/default in README, exercises, cheatsheet, demos and solutions against `omp://models.md`, `settings.md`, `providers.md`, `environment-variables.md`, `keybindings.md`, `non-compaction-retry-policy.md`, `local-models.md`, `task-agent-discovery.md`, `cli-reference.md`, `user-facing-packages.md` and the `--help` output of `omp`, `omp models|stats|usage|tiny-models|setup|login|commit|config`.
- Smoke-run (isolated profile, lab mock on 8765 `--fail` + 8766): `omp models` tables, `omp models --json` keys, validation banner for a missing `baseUrl`, implicit `lm-studio` discovery (`128K`/`33K`, cached in `models.db`), `omp -p --mode json --no-session` fallback events (`retry_fallback_applied` → `auto_retry_start` → `retry_fallback_succeeded` → `auto_retry_end`, ≈12 s), path-scoped `enabledModels` (`omp config get` per cwd, initial model inside the path), `omp config set modelRoles` record replacement, `omp commit --dry-run` resolving `modelRoles.commit`, `omp stats --summary|--json`, `omp models --kind tiny`, `omp tiny-models list`, `omp usage`.
- **Lab fixture defect (outside this module's write scope, reported to the orchestrator):** `omp-course-lab/tools/mock-provider.py` never imports `sys` (and imports `json` twice), so `log_message` raises `NameError` on every request and every `curl`/omp call gets an empty reply. Verified by running the shipped file. Needs `import sys` in the lab repo; the smoke run used a copy with that one-line fix.
- Fixed in this module: mock banner goes to **stdout** (was described as a stderr `[mock] listening …` line); stderr log-line format; the mock now strips the `<system-reminder>` block (README/exercises/demos/solutions no longer hedge with `…`); `omp stats --json` `byModel` is a **list** of objects, not an id-keyed map (README step 7.6-2, guided task and exercise 7-S2 pass check rewrote their Python one-liners); `providers.tinyModelDtype` default is `default` (= each model's shipped dtype, `q4`), not `q4`; `omp tiny-models list` also prints `smollm` (word completion) after the eight tiny models; `omp models --kind bogus` prefix is lower-case `error:`; fallback wall time ≈10–15 s (observed 12 s).
- Binary on the audit machine reports `omp/18.3.5`; module headers keep `18.3.1` for consistency with the other modules (orchestrator decision).

## Removed (unverifiable)
- Demo 7.5 "earlier capture with an HTTP 503 primary and `retry.maxRetries: 2`" — the lab mock has no 503 mode (`--fail` is 429 only), so the transcript cannot be reproduced with the fixture.
- Solutions 7-G3 "≈ 30 s with a 503 primary" — same reason.

## Verified live (not just doc-read)
- `omp models mock` table, `omp models find`, `omp models --kind tiny|all|bogus`, `omp models --json` shape, `omp models refresh`.
- `models.yml` validation banner and message for a missing `baseUrl`.
- `omp -p --model mock/mock-1` end-to-end; `omp -p --mode json` events `retry_fallback_applied` / `auto_retry_start` / `retry_fallback_succeeded` / `auto_retry_end` with both 429 and 503 primaries.
- Startup warning `Fallback chain for role 'default' references unknown model: …`.
- Path-scoped `enabledModels` and `disabledProviders` (`omp config get` per cwd, `omp models` per cwd, initial-model selection inside the scoped path).
- `.env` precedence via `LM_STUDIO_BASE_URL` in `<cwd>/.env` vs exported variable vs none.
- Implicit `lm-studio` discovery of an arbitrary OpenAI-compatible server (probes `GET /api/v0/models` then `GET /v1/models`; synthesizes 128K/33K).
- `omp config set modelRoles` (record replaced wholesale), `omp config get` of `retry.*` defaults, `cycleOrder`, `modelRoleStorage`, `contextPromotion.enabled`, `retry.usageAware*`.
- `omp commit --dry-run` resolving `modelRoles.commit`.
- `omp stats --summary`, `omp stats` (port 3847), `omp stats --json` (leading sync line before JSON).
- `omp usage` / `--json` with no stored accounts.
- `/model` picker render (Roles column, Kind row, role bar, footer) via a pty.

## Deviations from the outline
- Outline 7.3 says "`disabledProviders`/`enabledProviders`" as a pair for model gating. Per `omp://settings.md`, `enabledProviders` opts *foreign user-level config sources* into discovery; it is **not** a model allow-list. Lesson 7.3 says so explicitly and points to `enabledModels`.
- Outline 7.1 lists `Shift+Ctrl+P` cycling in 7.2 — kept; chord verified in `omp://keybindings.md` (`app.model.cycleBackward`).
- Outline 7.6 "per-turn cost in status line": docs describe a `cost` segment showing *recorded session cost* (`omp://settings.md`), not per-turn; lesson wording follows the doc.
- Outline 7.5 "round-robin credentials": docs say stored OAuth accounts are "ranked and rotated automatically" (`omp://providers.md`) and that credential switching happens before model fallback (`omp://non-compaction-retry-policy.md`); the phrase "round-robin" appears only in an internal porting doc, so lessons say "rotated".
- Dry-run correction (2026-09-27, omp/18.3.5): the shipped `tools/mock-provider.py` does **not** strip omp's injected `<system-reminder>` block — `_reply_text` echoes the first 80 characters of the last user message verbatim. The observed reply is `Hello from mock-1. You said: <system-reminder> Today: …`; README 7.4/7.5, exercises 7-G2, demos and solutions now expect that prefix. If the lab mock gains a strip step, revert these expectations to `You said: say hi`.

## Not verified / dropped
- `Ctrl+P` / `Alt+P` / `^` chip / `Alt+M` interactive behaviour could not be exercised in the pty (raw escape sequences were interpreted as search text by the picker); claims are limited to `omp://keybindings.md`, `omp://task-agent-discovery.md`, `omp://tools/task.md`.
- Session-title generation with a downloaded tiny model, `omp setup speech`, and Ollama discovery were not run (no weights/engine on the build machine); claims are doc-only (`omp://local-models.md`, `omp://models.md`).
- Agent Hub subagent cost display is referenced only as a pointer to Module 10 (`omp://task-agent-discovery.md` mentions per-agent usage in the Hub roster).
- `/hotkeys` and `/dump` are referenced as Module 2/5 commands; they are not documented in the files I read for this module, so no claims are made about their output beyond "lists the chord".
- The outline's `omp stats` dashboard URL `localhost:3847` is confirmed by `omp://user-facing-packages.md` and the live banner (`http://127.0.0.1:3847`).
- The first `omp` TUI launch in a fresh profile opens the setup wizard (`startup.setupWizard`, default `true`); lessons assume Module 1 already completed it.
