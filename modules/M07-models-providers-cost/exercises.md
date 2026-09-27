# Module 7 — Exercises

Built against `omp/18.3.1`. Start from `git -C omp-course-lab checkout module-7-start`. All exercises are run from the `omp-course-lab` directory unless a step says otherwise. Every exercise ends with an observable **Pass** check.

Prerequisites on the learner machine:
- Python 3 (for `tools/mock-provider.py` — stdlib only).
- One real provider logged in (Module 1). Referred to below as `<real>/<model>`.
- Optional: Ollama (or LM Studio / llama.cpp). Every step that mentions Ollama has a mock-only alternative.

Cleanup reminder: exercises 7-W1, 7-G2, 7-G3 and 7-S1 edit `~/.omp/agent/config.yml` and `~/.omp/agent/models.yml`. The last section restores them.

---

## 7-W1 — Roles: `smol` cheap, `slow` strong, cycle through them              (~10 min, Walkthrough)

1. `omp models` → note two selectors from the tables: a cheap one (`<real>/<cheap>`) and a strong one (`<real>/<strong>`).
   Expected: both appear as rows under a `<real> (N)` table.
2. `omp` → `/model` → Enter.
   Expected: the **Models** panel with `✦ Roles` / `⬢ All models` on the left and a `Kind:` filter row on the right.
3. Press `→`, move to `<cheap>`, Enter, move the bottom bar to `smol`, Enter.
   Expected: bottom bar shows `<cheap> → [ … ]  smol ✔ …`; the status-line chip does not change.
4. Move to `<strong>`, Enter, choose `slow`, Enter. Esc.
5. Type `Which model are you? One line.` Enter. Press `Ctrl+P`, ask again. `Ctrl+P` again, ask again.
   Expected: chip cycles `smol → default → slow` (`cycleOrder` default `["smol","default","slow"]`); answers name three (or two, if `default` equals one of them) different models.
6. Quit. In a shell: `omp config get modelRoles`.

**Pass:** `omp config get modelRoles` prints a JSON object containing `"smol":"<real>/<cheap>"` and `"slow":"<real>/<strong>"`, and `grep -A3 '^modelRoles:' "$(omp config path)/config.yml"` shows the same two lines.

---

## 7-G1 — Local engine as the `commit` model              (~15 min, Guided)

**Goal:** a local (or discovered) model is assigned to `commit`, and `omp commit` resolves it.

Hints:
- With Ollama: `ollama pull <small-model>` then `omp models ollama` — the discovered row is what you assign. Ollama is found at `OLLAMA_BASE_URL` → `OLLAMA_HOST` → `http://127.0.0.1:11434` with no config.
- Without Ollama: `python3 tools/mock-provider.py --port 8765` and export `LM_STUDIO_BASE_URL=http://127.0.0.1:8765/v1`; `omp models lm-studio` then lists `mock-1` (context `128K`, max-out `33K` — discovery defaults).
- Assign from `/model` (row → Enter → `commit` → Enter) or set `modelRoles.commit: ollama/<model>` (or `lm-studio/mock-1`) in `~/.omp/agent/config.yml`.
- Stage a change: `echo "# module 7" >> README.md && git add README.md`.
- `omp commit --dry-run` never commits.

Checkpoints:
- `/model` shows the engine's provider row with `●` (available) and its model listed.
- `omp config get modelRoles` contains `"commit":"ollama/…"` (or `"lm-studio/mock-1"`).

**Pass:** the first two lines of `omp commit --dry-run` are `● Resolving model...` and `  └─ <the local model's display name>`. With Ollama, a commit message follows; with the mock the run ends in `Commit generated using fallback due to agent failure` plus a generated fallback message — that still passes (the model was resolved). Then `git restore --staged README.md && git checkout README.md`.

---

## 7-G2 — Custom provider from `models.yml`              (~15 min, Guided)

**Goal:** the lab's mock endpoint is a first-class provider named `mock`, and omp can chat with it.

Hints:
- Start it: `python3 tools/mock-provider.py --port 8765` (stdout prints one banner line `mock-provider serving model 'mock-1' on http://127.0.0.1:8765/v1 in normal mode`; every request is logged to stderr).
- `~/.omp/agent/models.yml` root key is `providers:`. A provider with `models:` needs `baseUrl`, `api`, and either `apiKey` or `auth: none`. The mock is keyless and speaks `/v1/chat/completions`, i.e. `api: openai-completions`.
- Model fields worth setting: `id: mock-1`, `name`, `contextWindow`, `maxTokens`, and `cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0}` (a flat override — see 7.6).
- Validate with `omp models mock`. A malformed file prints `Warning: models.yml validation failed — custom providers disabled` and the reason.
- Chat once: `omp -p --model mock/mock-1 "say hi"`.

Checkpoints:
- `omp models mock` prints a `mock (1)` table whose row starts `│ mock-1 │     33K │    4.1K │`.
- `omp models find mock` returns the same row; `omp models --json` includes `{"provider":"mock","id":"mock-1",…}`.

**Pass:** `omp -p --model mock/mock-1 "say hi"` prints exactly `Hello from mock-1. You said: say hi` (the mock strips omp's injected `<system-reminder>` block and echoes the first 80 characters of what remains), and the mock's stderr shows `[mock-provider] POST /v1/chat/completions -> "POST /v1/chat/completions HTTP/1.1" 200 -`.

---

## 7-G3 — Fallback chain, proven with `--fail`              (~15 min, Guided)

**Goal:** `retry.fallbackChains.default` has two entries and a failing primary hands the turn to the first entry.

Hints:
- You need two mocks: primary in failure mode `python3 tools/mock-provider.py --port 8765 --fail` and a healthy backup `python3 tools/mock-provider.py --port 8766`. `--fail` answers every chat request with HTTP `429` + `Retry-After: 1`, which omp classifies as retryable.
- Add a second provider `mock-backup` (same block as 7-G2 with `baseUrl: http://127.0.0.1:8766/v1`, `name: Mock 1 (backup)`).
- In `~/.omp/agent/config.yml`:
  ```yaml
  modelRoles:
    default: mock/mock-1
  retry:
    fallbackChains:
      default:
        - mock-backup/mock-1
        - <real>/<model>
  ```
- Defaults you are relying on: `retry.enabled: true`, `retry.modelFallback: true`, `retry.maxRetries: 10`. Check with `omp config get retry.modelFallback`.
- TUI: `omp` then `say hi` — a fallback warning `mock/mock-1 → mock-backup/mock-1` with the 429 reason appears, then the answer; the chip reads `Mock 1 (backup)`. Headless proof: `omp -p --mode json --no-session "say hi" | grep -E 'retry_fallback_(applied|succeeded)'`.
- Startup prints `Warning: Fallback chain for role 'default' references unknown model: …` if an entry is misspelled.

Checkpoints:
- `omp config get retry.fallbackChains` → `{"default":["mock-backup/mock-1","<real>/<model>"]}`.
- Primary mock stderr shows `"POST /v1/chat/completions HTTP/1.1" 429`; backup shows `… 200`.

**Pass:** the JSON run prints exactly these two event lines (reason abbreviated):
```
{"type":"retry_fallback_applied","from":"mock/mock-1","to":"mock-backup/mock-1","role":"default","reason":"Request failed: 429 rate limited (mock --fail) …"}
{"type":"retry_fallback_succeeded","model":"mock-backup/mock-1","role":"default"}
```
Expect ~10–30 s: the `Retry-After: 1` hint and jittered backoff are honoured before the switch.

---

## 7-S1 — Path-scope a model set to the lab only              (~15 min, Stretch)

**Goal:** inside `omp-course-lab` only `mock/mock-1` is selectable; every other directory keeps the full catalog. Verify from a sibling directory.

Constraints: use a path-scoped `enabledModels` entry in the **global** config (no bare string entries), keep `modelRoles.default` on `<real>/<model>`, and do not touch `omp-course-lab/.omp/config.yml`.

**Pass:** all three hold —
1. `omp config get enabledModels` prints `["mock/mock-1"]` inside the lab and `[]` from `../` (a sibling directory).
2. Inside the lab, `omp -p --mode json --no-session "say hi" | grep -c '"provider":"mock"'` is ≥ 1 even though `modelRoles.default` is the real model (the first scoped model becomes the initial model).
3. From the sibling directory the same command prints `0` and the answer comes from `<real>/<model>`.

Bonus (no pass check): repeat with `disabledProviders: [{path: <sibling>, providers: [mock]}]` and confirm `omp models` from the sibling has no `mock (1)` table.

---

## 7-S2 — Cost attribution per role              (~10 min, Stretch)

**Goal:** the same prompt run through `@smol` and `@slow` appears as two rows in `omp stats`.

**Pass:** `omp stats --summary` prints a `By Model:` section listing both model ids with a request count and `$` value each, and `omp stats --json | sed -n '/^{/,$p' | python3 -c 'import json,sys; print(sorted(m["model"] for m in json.load(sys.stdin)["byModel"]))'` lists both ids (`byModel` is a list of objects with `model`, `totalCost`, `totalOutputTokens`). State which one cost more.

---

## Cleanup

```bash
# stop the mocks (Ctrl+C in their terminals)
omp config reset retry.fallbackChains
omp config reset enabledModels
omp config reset disabledProviders
# then edit ~/.omp/agent/config.yml: set modelRoles.default back to <real>/<model>;
# keep or delete the mock / mock-backup blocks in ~/.omp/agent/models.yml
unset LM_STUDIO_BASE_URL
rm -f omp-course-lab/.env
omp models      # should list your real provider again
```
