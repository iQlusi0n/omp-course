# Module 7 — Build notes

Built against `omp/18.3.1` on the build machine (Python 3 only). Verification method: `read omp://<doc>` for every claim, `omp --help` / `omp models|stats|usage|tiny-models|setup|login|config|commit --help`, and a live smoke run in an isolated profile (`PI_CODING_AGENT_DIR=/tmp/…`, `HOME=/tmp/…`) against a stdlib replica of `tools/mock-provider.py` whose contract was confirmed with the lab builder (`LabRepo`): default port 8765, `mock-1`, JSON + SSE chat completions, `--fail` → HTTP **429** with `Retry-After: 1` (not 503 as I first assumed), stderr request log, `--model` flag.

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
- The mock echoes omp's injected `<system-reminder>` block inside "You said: …". I asked LabRepo to strip it; expectations in README/exercises are hedged with `…`.

## Not verified / dropped
- `Ctrl+P` / `Alt+P` / `^` chip / `Alt+M` interactive behaviour could not be exercised in the pty (raw escape sequences were interpreted as search text by the picker); claims are limited to `omp://keybindings.md`, `omp://task-agent-discovery.md`, `omp://tools/task.md`.
- Session-title generation with a downloaded tiny model, `omp setup speech`, and Ollama discovery were not run (no weights/engine on the build machine); claims are doc-only (`omp://local-models.md`, `omp://models.md`).
- Agent Hub subagent cost display is referenced only as a pointer to Module 10 (`omp://task-agent-discovery.md` mentions per-agent usage in the Hub roster).
- `/hotkeys` and `/dump` are referenced as Module 2/5 commands; they are not documented in the files I read for this module, so no claims are made about their output beyond "lists the chord".
- The outline's `omp stats` dashboard URL `localhost:3847` is confirmed by `omp://user-facing-packages.md` and the live banner (`http://127.0.0.1:3847`).
- The first `omp` TUI launch in a fresh profile opens the setup wizard (`startup.setupWizard`, default `true`); lessons assume Module 1 already completed it.
