# Module 7 cheat sheet — Models, Providers & Cost (`omp/18.3.1`)

## Roles (`config.yml` → `modelRoles`)
| Role | Drives | Unset → |
|---|---|---|
| `default` | the conversation | initial-model selection |
| `smol` / `slow` | cheap chores / deep reasoning; `Ctrl+P` cycle | — |
| `plan` `commit` `task` `advisor` `vision` | plan mode, `omp commit`, subagents, advisor, image questions | `default` |
| `tiny` → `memory` | session titles → memory (M9) | `@smol` → `@tiny` |
| `image` `web` `speech` `dictation` `judge` | model-kind runners | built-in priority lists |

- Selector: `provider/id[:minimal|low|medium|high|xhigh|max]` (chat roles only); alias `"@slow"` (quote it); `*` = `@default`.
- One run: `--model <id|role>`, `--smol`, `--slow`, `--plan`; env `PI_SMOL_MODEL`, `PI_SLOW_MODEL`, `PI_PLAN_MODEL` (flag beats env).
- `omp config get modelRoles` · `omp config set modelRoles '{…}'` (replaces whole record) · `modelRoleStorage: global|project` (default `global`).

## Switching in-session
| Key / cmd | Effect |
|---|---|
| `Ctrl+P` / `Shift+Ctrl+P` | cycle `cycleOrder` (default `smol, default, slow`) |
| `Alt+P` | temporary model, roles untouched |
| `Alt+M` or `/model` | picker; `→` models, `Alt+←/→` kind, Enter assign, Esc |
| `^` in composer | tag a model → chip → pseudonym `m1`, `m2` (usable as `agent` in `task`/`agent()`) |
| `omp --models a,b,c` | scope the cycle; first entry = initial model |
| keybindings.yml ids | `app.model.cycleForward/cycleBackward/selectTemporary/select` |

`omp models [<provider>]` · `omp models find <s>` · `omp models refresh` · `--kind chat|tiny|image|tts|stt|search|judge|embedding|rerank|video|all` · `--json` · `--config <overlay>`

## Providers & credentials
- Available = not in `disabledProviders` **and** (keyless **or** credentials resolve).
- Key precedence: `--api-key` → `models.yml apiKey` → stored OAuth (accounts rotated) → `/login` key → env/`.env` → other stored → custom resolver.
- `.env` order: process env → `<cwd>/.env` → `~/.omp/agent/.env` → `~/.omp/.env` → `~/.env` (first wins; `OMP_*` mirrored to `PI_*`).
- `/login [provider|redirect-url]`, `/logout`, `omp login [provider]`; store `~/.omp/agent/agent.db`.
- `disabledProviders: [id…]` — arrays **replace** across layers; ids are shared with discovery sources (`google` ≠ `gemini`). `enabledProviders` = foreign config sources, not models.

## `models.yml` (`~/.omp/agent/models.yml`)
```yaml
providers:
  mock:                      # id used in selectors: mock/mock-1
    baseUrl: http://127.0.0.1:8765/v1
    api: openai-completions  # or openai-responses, anthropic-messages, …
    auth: none               # else apiKey: ENV_NAME | literal | "!cmd"
    models:
      - id: mock-1
        name: Mock 1 (omp-course-lab)
        contextWindow: 32768
        maxTokens: 4096
        cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0}
```
- Override a built-in: provider block without `models` + `baseUrl`/`headers`/`modelOverrides`/`discovery`/….
- `discovery.type`: `ollama` `llama.cpp` `lm-studio` `openai-models-list` `proxy` `litellm`.
- Implicit local engines (keyless, no file): `ollama` (`OLLAMA_BASE_URL`/`OLLAMA_HOST`/`:11434`), `llama.cpp` (`LLAMA_CPP_BASE_URL`/`:8080`), `lm-studio` (`LM_STUDIO_BASE_URL`/`:1234/v1` — any OpenAI-compatible server).
- Tiny/speech: `omp tiny-models list|download <id>|download all`, `omp setup speech`, `modelRoles.tiny: local/lfm2.5-230m`.
- Broken file → `Warning: models.yml validation failed — custom providers disabled` (built-ins keep working). Cache: `<agent dir>/models.db`.

## Resilience
| Setting | Default |
|---|---|
| `retry.enabled` / `maxRetries` / `baseDelayMs` / `maxDelayMs` | `true` / `10` / `500` / `300000` |
| `retry.modelFallback` / `fallbackRevertPolicy` | `true` / `cooldown-expiry` (`never`) |
| `retry.fallbackChains` | `{}` — keys: role, `provider/model`, `provider/*`; `[]` = none |
| `contextPromotion.enabled` | `false` (+ `contextPromotionTarget` in `modelOverrides`) |
| `retry.usageAwareFallback` | `false` |

- Chain lookup: exact model → `provider/*` → role → `default` (model-kind roles never use `default`).
- Backoff 500·2ⁿ ms capped 8 s, jittered; `Esc` cancels; events `auto_retry_start/end`, `retry_fallback_applied/succeeded`.
- Path scope (`enabledModels`, `disabledProviders`, `enabledProviders`): `- {path: ~/repo, models: [...]}`; check with `omp config get <key>` from that cwd.

## Cost
- Status line `cost` segment (↑/↓ only for scheduled pricing); discovered/gateway models are unpriced (`$0`).
- `omp stats` → `http://localhost:3847` (`--port`, `--host`); `--summary`; `--json` (`overall`, `byModel`, `byFolder`, …). Data: `~/.omp/agent/sessions/` → `~/.omp/stats.db`.
- `omp usage [--provider id] [--json] [--redact] [--history --days N]`, `omp usage clients --days N`, `omp usage invalidate`.
