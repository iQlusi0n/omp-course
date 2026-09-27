# Module 7 — Instructor notes and solutions

Verified on `omp/18.3.1` in an isolated profile (`PI_CODING_AGENT_DIR=<tmp>`) against the lab's `tools/mock-provider.py` (default port 8765, `GET /v1/models` → `mock-1`, `POST /v1/chat/completions` JSON + SSE, `--fail` → HTTP 429 with `Retry-After: 1`, requests logged to stderr as `[mock-provider] <METHOD> <path> -> "<request line>" <status> -`). **Fixture defect at audit time:** the checked-in script omits `import sys` (and imports `json` twice), so its `log_message` raises `NameError` on every request and omp gets empty responses; the audit ran a copy with `import sys` added. Until the lab owner fixes it, no exercise in this module passes with the shipped file.

## Reference `models.yml`

```yaml
providers:
  mock:
    baseUrl: http://127.0.0.1:8765/v1
    api: openai-completions
    auth: none
    models:
      - id: mock-1
        name: Mock 1 (omp-course-lab)
        reasoning: false
        input: [text]
        contextWindow: 32768
        maxTokens: 4096
        cost:
          input: 0
          output: 0
          cacheRead: 0
          cacheWrite: 0
  mock-backup:
    baseUrl: http://127.0.0.1:8766/v1
    api: openai-completions
    auth: none
    models:
      - id: mock-1
        name: Mock 1 (backup)
        contextWindow: 32768
        maxTokens: 4096
```

Verified output: `omp models mock` → `mock (1)` table, row `│ mock-1 │     33K │    4.1K │ -        │ no     │`. Common learner errors and the exact messages:
- missing `baseUrl` → `Provider mock: "baseUrl" is required when defining custom models.`
- missing `api` → validation error naming `api` (provider-level or per model)
- missing `auth: none` and `apiKey` → validation error requiring `apiKey`
- a root key other than `providers` → schema error. In all cases the banner is `Warning: models.yml validation failed — custom providers disabled` and built-ins keep working.

## 7-W1 (roles + cycle)

`omp config set modelRoles '{"default":"<real>/<model>","smol":"<real>/<cheap>","slow":"<real>/<strong>"}'` is the shell equivalent of the picker. Verified that `set` on a record replaces the whole object — learners who `set` twice lose the first role; that is the point of the troubleshooting row. `cycleOrder` default confirmed: `["smol","default","slow"]`.

Grading: accept any two distinct real selectors; the `:high` suffix on `slow` is optional. Pass evidence is the `omp config get modelRoles` line.

## 7-G1 (local `commit` model)

Verified with `modelRoles.commit: mock-backup/mock-1` and one staged file:

```
● Resolving model...
  └─ Mock 1 (backup)
…
● Agent did not provide proposal, using fallback...
Warnings:
- Commit generated using fallback due to agent failure
Generated commit message:
docs: updated documentation for a.txt
```

The mock cannot follow the commit agent's protocol, so the fallback message is expected; grade on the `Resolving model` card. With Ollama, `ollama/<model>` produces a real proposal. Discovery path for the mock-only variant: `LM_STUDIO_BASE_URL=http://127.0.0.1:8765/v1` → `lm-studio (1)` with `mock-1` (`128K`/`33K` synthesized).

`omp commit --dry-run` never writes; `-m/--model` on `omp commit` overrides the role for one run if a learner wants to compare.

## 7-G2 (custom provider)

Pass line observed: `Hello from mock-1. You said: say hi`. omp prepends a `<system-reminder>` block to the user message; the mock strips it from the echo (and cuts the echo at 80 characters). Grade on `Hello from mock-1` and the `200` in the mock's stderr.

## 7-G3 (fallback chain)

Config used:

```yaml
modelRoles:
  default: mock/mock-1
retry:
  fallbackChains:
    default:
      - mock-backup/mock-1
      - <real>/<model>
```

Observed JSON events (in order): `retry_fallback_applied` (`from: mock/mock-1`, `to: mock-backup/mock-1`, `role: default`, `reason: Request failed: 429 rate limited (mock --fail) retry-after-ms=1000 …`), `auto_retry_start` (`attempt: 1`, `maxAttempts: 10`, `delayMs: 0`), `retry_fallback_succeeded`, `auto_retry_end` (`success: true`). Wall time ≈ 12 s end to end. Learners who see `Retrying (1/10) in Ns…` for a long time usually have `retry.modelFallback: false` or a misspelled chain entry (startup prints `Warning: Fallback chain for role 'default' references unknown model: …`).

A second chain entry that is *not* available (no credentials) is fine — only the first resolvable candidate is used; unknown entries only produce the startup warning.

## 7-S1 (path-scoped `enabledModels`)

Global `config.yml` used:

```yaml
modelRoles:
  default: mock/mock-1        # in the lab use <real>/<model>
  smol: mock-backup/mock-1
enabledModels:
  - path: /tmp/m07-smoke/proj
    models:
      - mock-backup/mock-1
```

Observed: `omp config get enabledModels` → `["mock-backup/mock-1"]` inside `proj`, `[]` elsewhere; `omp -p --mode json` inside `proj` answered from `mock-backup/mock-1` although `default` pointed at `mock/mock-1` (first scoped model becomes the initial model); from `elsewhere` it answered from `mock/mock-1`. Companion `disabledProviders: [{path: …/private, providers: [mock]}]` removed the `mock (1)` table only under `private`.

Grading pitfalls: `~` must be expanded by omp (it is), but a relative `path:` is resolved against the process cwd — require an absolute or `~/` path. A project `.omp/config.yml` that also sets `enabledModels` replaces the global array wholesale and hides the scoped entry.

## 7-S2 (cost per role)

Grade on the `By Model:` section of `omp stats --summary` listing both ids. The mock contributes `mock-1: N reqs, $0.0000`; explain `unpricedRequests` in `--json` if a learner asks why gateway sessions are "free".

## 7.2 guided (`^` chip) and stretch (rebind)

Not reproducible on the build machine (no interactive completion capture). Doc-backed: `^` uses the same scope/ranking as `Alt+P`; pseudonyms `m1…` appear as `<model agent="m1" name="…"/>` in the user message and survive `/resume`. Keybinding ids verified in `omp://keybindings.md`: `app.model.cycleForward` (`Ctrl+P`), `app.model.cycleBackward` (`Shift+Ctrl+P`), `app.model.selectTemporary` (`Alt+P`), `app.model.select` (`Alt+M`); an empty array disables an action.

## 7.4 stretch (tiny titles)

Not run here (no weights download on the build machine). Doc-backed: `omp tiny-models download lfm2.5-230m`; worker socket `~/.omp/run/tiny/<model>-<backend>.sock`, idle exit after 15 min; `modelRoles.tiny` unset ⇒ titles use the online path (no automatic download).

## Cleanup for a shared machine

`omp config reset retry.fallbackChains && omp config reset enabledModels && omp config reset disabledProviders`; restore `modelRoles.default`; delete the `mock*` blocks or leave them (harmless when the server is down — the provider simply reports connection errors if selected).
