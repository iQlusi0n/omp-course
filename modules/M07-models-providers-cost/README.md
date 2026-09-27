# Module 7 — Models, Providers & Cost (~1.5 h, intermediate)

| | |
|---|---|
| **Built against** | `omp/18.3.1` (`omp --version`) |
| **Prerequisites** | Module 6 (settings layering, `omp config`, `<repo>/.omp/config.yml`). One provider logged in from Module 1. |
| **Practice repo** | `omp-course-lab` — `git checkout module-7-start` |
| **Learner machine** | Python 3 (for `tools/mock-provider.py`). Ollama / LM Studio / llama.cpp optional — every local-engine exercise has a mock-only path. |
| **Goal** | Route the right model to the right job; add local/custom providers; survive provider failures; watch spend. |

Off-by-default settings you will meet in this module (each is called out where it matters):
`modelRoleStorage: project`, `contextPromotion.enabled`, `retry.usageAwareFallback`, `statusLine.preset: custom`, and every `retry.fallbackChains.*` entry (empty by default).

Lessons: [7.1 Roles](#lesson-71--roles-one-model-per-job-15-min) · [7.2 Switching in-session](#lesson-72--switching-models-in-session-15-min) · [7.3 Providers & credentials](#lesson-73--providers-credentials-and-env-15-min) · [7.4 Custom & local providers](#lesson-74--custom-and-local-providers-20-min) · [7.5 Resilience](#lesson-75--resilience-retry-fallback-chains-scoping-15-min) · [7.6 Cost visibility](#lesson-76--cost-visibility-10-min)

Coursework for the whole module is in [`exercises.md`](exercises.md); the one-page reference is [`cheatsheet.md`](cheatsheet.md).

---

## Lesson 7.1 — Roles: one model per job              (~15 min)
**You will be able to:** name the built-in model roles and what each drives; assign a role from `/model` or `config.yml`; override a role for one run from the CLI or environment.
**Why this exists:** A coding session is not one workload. Session titles, commit messages, planning, subagent fan-out, image questions and web grounding all have different cost/quality needs. Instead of switching the active model by hand before each job, omp routes each workload through a named **role**. Roles live in `config.yml` under `modelRoles` (never in `models.yml`, which only defines providers and model metadata). Pick a good default once, a cheap `smol`, a strong `slow`, and everything else inherits sensibly.
**Demo:** [`demos/7.1-roles-picker.md`](demos/7.1-roles-picker.md) — the `/model` picker with the Roles column and the role-assignment bar, then `omp config get modelRoles`.
**Concepts:**
- **Chat roles** (accept ordinary chat models): `default`, `smol`, `slow`, `vision`, `plan`, `commit`, `tiny`, `memory`, `task`, `advisor`. `tiny` and `memory` also accept `tiny`-kind catalog models.
- **Model-kind roles** (select a runner of a different catalog kind): `image` (generate_image), `web` (search / grounded chat), `speech` (TTS), `dictation` (STT), `judge` (typed judgments, auto-thinking, unexpected-stop detection, AI-assisted staging). `judge` also accepts tiny and chat models.
- **Inheritance when unset:** `tiny` resolves through `@smol`; `memory` resolves through `@tiny`. Model-kind roles use their own built-in priority lists.
- **Selector syntax:** exact `provider/modelId` (unambiguous), bare id (provider inferred by `modelProviderOrder`, then catalog priority, then recent use), fuzzy substring. Chat roles may append a thinking suffix: `anthropic/claude-opus-4-5:high`; allowed levels `minimal|low|medium|high|xhigh|max`. Model-kind roles take no suffix. Role aliases (`"@slow"`) must be quoted in YAML; `*` means `@default`.
- **`vision` ≠ `image`:** `vision` is the chat model used for `read screenshot.png?q=...`; `image` is the `generate_image` model. Assigning `vision` does not give a model image input — the model must also be able to send images to its provider.
- **Where assignments land:** `/model` → Roles view writes `modelRoles.<role>` to the global `~/.omp/agent/config.yml`. With `modelRoleStorage: project` (**default `global`**) role assignments from the picker go to `<cwd>/.omp/config.yml` instead; missing project roles still fall back to global ones. This is the *only* settings write that ever targets the project file.
- **Assigning vs switching:** assigning a non-`default` role in the picker saves the selector but does **not** switch the active conversation model; assigning `plan` does not enter plan mode. Assigning `default` also switches the live model (unless a higher-precedence layer overrides it). The session-only picker (`Alt+P`, lesson 7.2) changes the active model without touching roles.
- **One-run overrides (never persisted):** `--model <id-or-role>` (`--model slow`, `--model @slow`, `--model opus`), `--smol <id>`, `--slow <id>`, `--plan <id>`; env `PI_SMOL_MODEL`, `PI_SLOW_MODEL`, `PI_PLAN_MODEL` (the CLI flag wins over the env var). Only these three roles have per-role flags/env.
- **Initial model on a fresh session**, in order: explicit CLI model → first scoped model (`enabledModels` / `--models`) → saved `default` → known provider defaults among available models → first available model.
- **Shell view:** `omp config get modelRoles` prints the merged record; `omp config set modelRoles '{"smol":"…","slow":"…"}'` writes the **whole record** (record type = JSON object) to the global file. `omp config list` shows every key with its effective value.
- Custom roles (`review`, `fast`, …) can be created from the Roles view or via `modelTags`; Module 10 uses them for agent model overrides.

**Try it (Walkthrough):**
1. In `omp-course-lab`, run `omp`, then type `/model` and press Enter.
   Expected: a two-column **Models** panel. Left column: `✦ Roles`, `⬢ All models`, then one row per provider (`●` = available, `○` = no credentials). Right column: the model list with a `Kind:` filter row, a `🔍` search box, and a footer `Enter assign roles · ↑/↓ providers · → models · type to search · Alt+←/→ kind · Esc close`.
2. Move right into the model list and put the cursor on a cheap chat model (the one you logged into in Module 1 is fine). Press Enter.
   Expected: the bottom bar becomes `<model> → [ ● default ✔ ]  smol   slow   vision   plan   commit   tiny   memory   task   advisor   judge   fallbacks…`. Move to `smol` and press Enter.
3. Repeat for a stronger model → `slow`. Press Esc to close the picker.
   Expected: no change to the conversation model (you assigned non-`default` roles).
4. In a second terminal: `omp config get modelRoles`.
   Expected: a JSON object containing your `smol` and `slow` selectors, e.g. `{"smol":"openai/gpt-4.1-mini","slow":"anthropic/claude-opus-4-5"}`. `cat "$(omp config path)/config.yml"` shows the same under `modelRoles:`.
5. Launch with a one-run override: `PI_SLOW_MODEL=<other-model> omp -p "which model role is slow?"` — then `omp config get modelRoles` again.
   Expected: the persisted `slow` value is unchanged; env/CLI overrides are runtime-only.

**Guided task:** Give `plan` a thinking suffix. Goal: `modelRoles.plan` = your `slow` model with `:high`. Hints: edit `~/.omp/agent/config.yml` by hand or use `omp config set modelRoles '<full JSON record>'` (it replaces the record, so include `smol`/`slow` again). Checkpoint: `omp config get modelRoles` shows `"plan":"<provider>/<id>:high"`. Pass condition: `omp --plan @slow -p "say ok"` runs without a "model not found" error and `omp config get modelRoles` still shows the `:high` suffix.
**Stretch:** Make role assignments repo-local. Goal: set `modelRoleStorage: project` globally, assign `smol` from `/model` inside `omp-course-lab`, and prove the write landed in `omp-course-lab/.omp/config.yml` (only `modelRoles` appears there) while `omp config get modelRoles` from `~` still shows the global value. Pass condition: `git -C omp-course-lab diff --stat -- .omp/config.yml` lists the file and it contains only a `modelRoles:` block.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `/model` shows the provider with `○` and its models cannot be selected | No credentials for that provider, or it is in `disabledProviders` | `/login <provider>` or set its env var (7.3); `omp config get disabledProviders` |
| `omp config set modelRoles …` wiped my other roles | `modelRoles` is a record; `set` replaces the whole value | Pass the complete JSON object, or edit `config.yml` |
| Set `slow` in config but a different model is used | `--slow`/`PI_SLOW_MODEL`, a `--config` overlay, or a project `.omp/config.yml` overrides it | `omp config set modelRoles …` reports `overriddenBy`; check `env | grep PI_`, `omp config get modelRoles` from the repo dir |
| Assigned `plan` in the picker but nothing changed | Roles other than `default` are used only when the workload runs | Enter plan mode (M4) — the `plan` model is applied then |
| YAML error: `@slow` "found character that cannot start any token" | Unquoted alias | `plan: "@slow"` |

**Cheat sheet:**
| Action | Command / key |
|---|---|
| Open picker | `/model` (also `Alt+M`) |
| Persisted roles | `omp config get modelRoles`, `omp config set modelRoles '{…}'` |
| One-run overrides | `--model`, `--smol`, `--slow`, `--plan`; `PI_SMOL_MODEL`, `PI_SLOW_MODEL`, `PI_PLAN_MODEL` |
| Thinking suffix | `provider/id:low|medium|high|xhigh|max|minimal` |
| Role storage | `modelRoleStorage: global` (default) / `project` |

**Source:** omp://models.md, omp://settings.md, omp://cli-reference.md, omp://environment-variables.md

---

## Lesson 7.2 — Switching models in-session              (~15 min)
**You will be able to:** cycle models with the keyboard, pick a temporary model without changing roles, tag a model inline with `^`, and inspect the catalog from the shell with `omp models`.
**Why this exists:** Mid-task you often want "the cheap one for this grep, the strong one for this design question". Re-launching omp loses context. omp exposes a small keyboard vocabulary for switching the live model while the roles you configured in 7.1 stay intact, plus a shell command that shows exactly which models are selectable on this machine, in this directory.
**Demo:** [`demos/7.2-switching.md`](demos/7.2-switching.md) — `omp models`, `omp models find`, the picker's Kind filter, and the status-line model chip.
**Concepts:**
- **Cycle roles:** `Ctrl+P` forward, `Shift+Ctrl+P` backward, through `cycleOrder` (**default** `["smol","default","slow"]`). The active model name is shown in the status line (`⬢ <model name>`).
- **Scope the cycle for one run:** `--models a,b,c` — comma-separated patterns (exact `provider/id`, bare ids, globs such as `openai/*` or `*sonnet*`, optional `:thinking` suffix). The first scoped model becomes the initial model on a fresh session. `enabledModels` in config does the same persistently (7.5 shows path scoping).
- **Temporary pick:** `Alt+P` opens a session-only picker — changes the live model, does **not** rewrite any role.
- **Roles picker:** `Alt+M` (same panel as `/model`). Inside it: `↑/↓` providers, `→` models, type to search, `Alt+←/→` to change **Kind** (`all`, `chat`, `tiny`, `image`, `tts`, `stt`, `search`, `judge`, `embedding`, `rerank`, …), Enter to assign, Esc to close. Each provider row is its own view; `All models` is the merged view.
- **Composer chip `^`:** type `^` in the composer to pick a model from the same scope as `Alt+P`; accepting inserts an atomic chip showing its display name (`Have ^<pick> review this change`). On submit each first-mentioned model gets a session-local pseudonym `m1`, `m2`, …, and the message carries `<model agent="m1" name="…"/>`. `task`, eval `agent()` and `workpool()` accept that pseudonym as their `agent` — Module 10 uses this. Pseudonyms survive `/resume`; repeating a selector reuses its number.
- **Rebind the keys** in `~/.omp/agent/keybindings.yml`: `app.model.cycleForward`, `app.model.cycleBackward`, `app.model.selectTemporary`, `app.model.select` (chord names like `Ctrl+P`, `Alt+Shift+P`).
- **Shell catalog:** `omp models` (default action `ls`) prints provider-grouped tables with `model`, `context`, `max-out`, `thinking`, `images` columns for every *available* model; `omp models <provider>` filters to one provider; `omp models find <substring>` matches provider, id or name; `omp models refresh` forces an online catalog re-fetch (ignores the cache TTL); `--kind <chat|tiny|image|tts|stt|search|judge|embedding|rerank|video|all>`; `--json` for scripts (`{"models":[{provider,id,selector,name,contextWindow,maxTokens,cost,kind,…}]}`); `--config <overlay>` to preview a settings overlay; `-e <ext>` / `--no-extensions`.
- The `images` column reports what the transport will actually send; `--json` keeps the declared `input`.
- `includeModelInPrompt` (**default `true`**) tells the model its own name in the system prompt — useful when you ask "which model are you?" during this lesson.

**Try it (Walkthrough):**
1. `omp models` in a shell.
   Expected: one table per provider you can use, e.g. `anthropic (N)` followed by rows like `│ claude-… │ 200K │ 32K │ low,medium,high │ yes │`. Providers without credentials are absent.
2. `omp models find mini` then `omp models --kind tiny`.
   Expected: only rows whose provider/id/name contain `mini`; then a `local (8)` table (`falcon-h1-90m`, `gemma-3-1b`, `lfm2-1.2b`, `lfm2.5-230m`, `lfm2.5-350m`, `llama3.2:3b`, `qwen2.5-1.5b`, `qwen3-1.7b`) — the on-device catalog from 7.4.
3. Start `omp` in the lab, ask `Which model are you?`, then press `Ctrl+P` and ask again.
   Expected: the status line chip changes from your `smol` name to `default` (cycle order `smol → default → slow`), and the second answer names a different model. `Shift+Ctrl+P` goes back.
4. Press `Alt+P`, choose any third model, ask again, then quit and run `omp config get modelRoles`.
   Expected: the answer names the temporary model; `modelRoles` is unchanged.
5. Restart with a scoped cycle: `omp --models '<smol-selector>,<slow-selector>'` and press `Ctrl+P` twice.
   Expected: only those two models alternate; the first listed one is the initial model.

**Guided task:** Tag a model inline. Goal: send one message that mentions a model with `^` and observe the pseudonym. Hints: type `Have ^`, pick a model from the completion, finish with `summarize api/__init__.py`; after submit, `/dump` (M5) or scroll the transcript to see `<model agent="m1" name="…"/>` in your user message. Checkpoint: the chip renders as the model's display name before submit. Pass condition: the transcript's user message contains `agent="m1"`.
**Stretch:** Rebind cycling. Goal: `keybindings.yml` maps `app.model.cycleForward` to `Alt+N` and disables `app.model.cycleBackward` (`[]`). Pass condition: `/hotkeys` (M2) lists `Alt+N` for "Cycle role models forward" and `Ctrl+P` no longer cycles.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `Ctrl+P` does nothing | Terminal lacks the keyboard protocol (M1.3) or the role model is unavailable | Verify with `/hotkeys`; check `omp models` lists the `smol`/`slow` models |
| Cycle skips a role | The role's model is not available here (no credentials, disabled, or filtered by `enabledModels`) | `omp models` from the same directory; 7.3 / 7.5 |
| `omp models` prints `No models available. Set API keys in environment variables.` | No provider has credentials, or `models.yml` failed validation (a `Warning:` line precedes it) | Fix the warning (7.4) or log in (7.3) |
| A model I stopped serving still appears in `omp models` | Cached discovery rows (`<agent dir>/models.db`) survive a failed re-probe | Selecting it fails with a connection error; `omp models refresh` re-fetches; restart the server or ignore |
| `^` completion never appears | Token needs whitespace boundaries (`Have ^`, not `Have^`); mentions inside `!`/`$` local-execution drafts stay literal | Add a space before `^` |

**Cheat sheet:**
| Action | Key / command |
|---|---|
| Cycle roles fwd / back | `Ctrl+P` / `Shift+Ctrl+P` (`cycleOrder`) |
| Temporary model (no role change) | `Alt+P` |
| Roles picker | `Alt+M` or `/model` |
| Scope cycle for one run | `omp --models a,b,c` |
| Inline model tag | `^` → chip → pseudonym `m1`, `m2` |
| List / find / refresh | `omp models [<provider>]`, `omp models find <s>`, `omp models refresh`, `--kind`, `--json` |

**Source:** omp://keybindings.md, omp://models.md, omp://task-agent-discovery.md, omp://cli-reference.md, omp://settings.md, `omp models --help`

---

## Lesson 7.3 — Providers, credentials, and `.env`              (~15 min)
**You will be able to:** explain when a provider is "available"; predict which credential omp will use; place keys in the right `.env`; disable providers globally or per project.
**Why this exists:** Most "model not found" and "wrong key charged" problems are precedence problems. omp merges four catalog sources, seven credential sources and five environment layers, and each has a fixed order. Once you know the order you can make a repo use a specific gateway or keep a client's code away from a given vendor without touching your global setup.
**Demo:** [`demos/7.3-credentials.md`](demos/7.3-credentials.md) — `omp usage` with no accounts, `omp config get disabledProviders` inside and outside a scoped path.
**Concepts:**
- **Provider vs model.** A provider is the account/backend namespace (`anthropic`, `openai`, `google`, `ollama`, `my-gateway`); a model is `provider/model-id`. Disabling a provider removes every model under it.
- **Catalog sources, in order:** bundled catalog → `~/.omp/agent/models.yml` → runtime discovery (local engines, discovery-enabled gateways) → extension-registered providers.
- **Available =** provider id **not** in effective `disabledProviders` **and** (provider is keyless **or** credentials resolve). `disabledProviders` is checked *before* credentials — no key can revive a disabled id.
- **Three credential shapes:** OAuth login (`/login anthropic`, `openai-codex`, `github-copilot`, `google-gemini-cli`, …), API key (env var, `.env`, `models.yml apiKey`, or an interactive `/login <provider>` key prompt), and coding-plan / subscription keys (e.g. `/login zai`, `zhipu-coding-plan`, `cline-pass`) whose quota windows `omp usage` reports (7.6).
- **Commands:** `/login` (picker), `/login <provider>`, `/login <redirect-url>` to finish a blocked OAuth callback, `/logout` (picker); from a shell `omp login [<provider>]` writes to the same store. Credentials live in `~/.omp/agent/agent.db` (`PI_CODING_AGENT_DIR` moves it; an auth broker replaces it — out of scope here). Logins are provider-scoped.
- **Credential precedence (first match wins):**
  1. runtime `--api-key`
  2. `models.yml` `providers.<id>.apiKey` (deliberately beats OAuth so a gateway key is not replaced by an upstream token)
  3. stored OAuth credential (refreshed; multiple accounts are ranked and rotated automatically — each org/workspace counts as an account)
  4. API key saved by `/login`
  5. provider env var (including `.env` values)
  6. other stored API key (e.g. broker-migrated)
  7. `models.yml` fallback resolver for custom providers
- **Core env vars:** `ANTHROPIC_OAUTH_TOKEN` then `ANTHROPIC_API_KEY`; `OPENAI_API_KEY`; `OPENAI_CODEX_OAUTH_TOKEN`; `GEMINI_API_KEY`; `GROQ_API_KEY`; `OPENROUTER_API_KEY`; `MISTRAL_API_KEY`; `XAI_API_KEY`; `COPILOT_GITHUB_TOKEN`; `AZURE_OPENAI_API_KEY`; `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`+`AWS_SECRET_ACCESS_KEY` for `amazon-bedrock`; local engines are keyless (`OLLAMA_API_KEY`, `LM_STUDIO_API_KEY`, `LLAMA_CPP_API_KEY` only for authenticated hosts).
- **`.env` order** (first definition wins; already-set process variables are never overwritten): process env → `<cwd>/.env` → `~/.omp/agent/.env` → `~/.omp/.env` → `~/.env`. Parsing: `#` comments, `KEY=value` with optional quotes, keys must be shell identifiers, and each `OMP_*` key is mirrored to `PI_*`. A project `.env` is the simplest way to give one repo its own gateway key or local endpoint (`OLLAMA_BASE_URL=…`).
- **`disabledProviders`** (`~/.omp/agent/config.yml` or `<repo>/.omp/config.yml`): exact ids; arrays are **replaced** by the higher layer, not merged — a project list must repeat the global ids it wants to keep. Works uniformly on bundled, custom, discovered, extension and implicit local providers. Does not delete stored credentials.
- **Shared id namespace gotcha:** `disabledProviders` also gates *discovery sources* (`claude`, `codex`, `gemini`, `native`, `agents`, `github`…). `google` is the Gemini API model provider; `gemini` is the `GEMINI.md` discovery source.
- **`enabledProviders` is not a model allow-list.** It opts *foreign user-level config sources* (Cursor, Codex, Claude, Gemini, OpenCode, Windsurf, GitHub) into discovery (**default empty**). To narrow models use `enabledModels` (7.5).
- Inspect the merged, path-resolved value with `omp config get disabledProviders` from the directory in question.

**Try it (Walkthrough):**
1. `omp usage`.
   Expected: one block per authenticated account with its limit windows — or `No credentials found. Run \`omp\` and use /login to add accounts.` if you only use env keys.
2. Make a repo-local `.env` drive provider discovery. This step needs the lab mock from 7.4 running: `python3 tools/mock-provider.py --port 8765`. First, from `~`, run `omp models lm-studio`.
   Expected: `No models matching "lm-studio"` (nothing answers on LM Studio's default port).
3. Create `omp-course-lab/.env`:
   ```dotenv
   # lab-local endpoint, read only when omp starts in this directory
   LM_STUDIO_BASE_URL=http://127.0.0.1:8765/v1
   ```
   Still from the lab directory, prove the process environment beats the file: `LM_STUDIO_BASE_URL=http://127.0.0.1:1 omp models lm-studio`.
   Expected: `No models matching "lm-studio"` — the exported value (a dead port) won over `.env`.
   Now plain `omp models lm-studio` from the lab.
   Expected: an `lm-studio (1)` table listing `mock-1` — the `.env` value was read because the cwd is the lab. (Order matters: once discovered, the row is cached in `<agent dir>/models.db` and keeps showing from other directories; delete the file `omp-course-lab/.env` when done.)
4. Add to `omp-course-lab/.omp/config.yml`:
   ```yaml
   disabledProviders:
     - <the provider you logged into in M1>
   ```
   Run `omp models` inside the lab and from `~`.
   Expected: the provider's table disappears inside the lab only. Remove the entry afterwards.
5. `omp config get disabledProviders` from both directories.
   Expected: `["<id>"]` inside the lab, `[]` from `~`.

**Guided task:** Prove precedence between `.env` layers. Goal: with the mock running on port 8765 and a second copy on 8766, put `LM_STUDIO_BASE_URL=http://127.0.0.1:8766/v1` in `~/.omp/agent/.env` and `LM_STUDIO_BASE_URL=http://127.0.0.1:8765/v1` in `omp-course-lab/.env`; predict, then observe, which server is discovered from each directory. Hints: `rm "$(omp config path)/models.db"*` before each `omp models lm-studio` so the cache does not mask the change; the mock's stderr shows which instance received `GET /v1/models`. Checkpoint: inside the lab the 8765 instance logs the request. Pass condition: from `~` the 8766 instance logs it, and after `export LM_STUDIO_BASE_URL=http://127.0.0.1:1` neither does and `omp models lm-studio` prints `No models matching "lm-studio"` from both directories. Clean up both files.
**Stretch:** Pin a key for a gateway without leaking it into the shell. Goal: a custom provider whose `apiKey` is `"!cat ~/.omp/lab-gateway.key"` (command-resolved secret). Pass condition: `omp models <provider>` lists the model, `env | grep -i lab-gateway` is empty, and the key file is never referenced in `config.yml`. (Build the provider block in 7.4.)

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| A provider's models are not selectable | Not `disabledProviders`-free, or no resolvable credentials | `/login <provider>` or export its env var; `omp config get disabledProviders` |
| The wrong key is used | A higher-precedence source: `--api-key`, `models.yml apiKey`, stored OAuth, or an exported shell var beating `.env` | Walk the 7-step list; `unset` the shell var; check the four `.env` files |
| Disabled a provider globally but it still shows in a repo | Project `disabledProviders` array replaced the global one | Repeat global ids in the project array |
| `disabledProviders: [gemini]` did nothing to Google models | `gemini` is a discovery source id | Use `google` |
| Two logins for one email | Each org/workspace is a separate account; rotation treats them separately | Expected — `omp usage` lists both |

**Cheat sheet:**
| Item | Value |
|---|---|
| Login / logout | `/login [provider|redirect-url]`, `/logout`, `omp login [provider]` |
| Store | `~/.omp/agent/agent.db` |
| Key precedence | `--api-key` → `models.yml apiKey` → OAuth → `/login` key → env/`.env` → other stored → custom resolver |
| `.env` order | process → `<cwd>/.env` → `~/.omp/agent/.env` → `~/.omp/.env` → `~/.env` |
| Disable | `disabledProviders: [id]` (arrays replace); inspect `omp config get disabledProviders` |

**Source:** omp://providers.md, omp://settings.md, omp://environment-variables.md, `omp login --help`, `omp usage --help`

---

## Lesson 7.4 — Custom and local providers              (~20 min)
**You will be able to:** write a valid `models.yml` provider, verify it with `omp models <provider>`, get a local engine auto-discovered, and download an on-device tiny model for background roles.
**Why this exists:** Teams front models with gateways, run local engines for privacy or cost, and want zero-cost on-device models for chores like session titles. All three are the same mechanism: a **provider** entry that omp merges into its catalog. `models.yml` declares the endpoint, wire API and (optionally) the models; local engines are discovered without any file; tiny models ship in the `local` catalog and download on first use.
**Demo:** [`demos/7.4-custom-provider.md`](demos/7.4-custom-provider.md) — starting `tools/mock-provider.py`, `omp models mock`, a broken file's warning, and `LM_STUDIO_BASE_URL` discovery of the same server.
**Concepts:**
- **File:** `~/.omp/agent/models.yml` (or `.yaml`; an old `models.json` is migrated once). Root key is `providers:` only.
- **Provider fields:** `baseUrl`, `api` (provider-level or per model), `apiKey` (env-var-name-or-literal; `!command` runs a shell command and uses trimmed stdout, 10 s timeout, resolved lazily), `auth: apiKey|none|oauth`, `authHeader: true` (inject `Authorization: Bearer <key>`), `headers`, `disableStrictTools` (Anthropic-fronted proxies), `discovery: {type, timeoutMs}`, `modelOverrides`, `models[]`.
- **Model fields:** `id` (required), `name`, `api`, `reasoning`, `input: [text, image]`, `contextWindow`, `maxContextWindow`, `maxTokens`, `cost: {input, output, cacheRead, cacheWrite}` (per-million; an explicit `cost` is a flat override; omit it to inherit catalog pricing by id), `headers`, `compat`, `thinking`, `contextPromotionTarget` (7.5), `compactionModel`.
- **Allowed `api`:** `openai-completions` (`/v1/chat/completions`), `openai-responses` (`/v1/responses`), `openai-codex-responses`, `azure-openai-responses`, `anthropic-messages`, `bedrock-converse-stream`, `google-generative-ai`, `google-gemini-cli`, `google-vertex`, plus judgment APIs `typesafe`, `openrouter-decisions`.
- **Validation:** with `models` present you need `baseUrl`, `apiKey` (unless `auth: none`), and `api` at provider or every model. A provider without `models` is an *override* of a built-in and needs at least one of `baseUrl`, `apiKey`, `auth: none`, `headers`, `compat`, `disableStrictTools`, `modelOverrides`, `discovery`, `remoteCompaction`. `discovery` needs provider-level `api` except `type: proxy`. On any error omp prints `Warning: models.yml validation failed — custom providers disabled` + the reason, and keeps built-ins.
- **Discovery types:** `ollama`, `llama.cpp`, `lm-studio`, `openai-models-list` (generic `GET {baseUrl}/models`; `injectV1: false` for gateways rooted elsewhere), `proxy` (per-model wire from `supported_endpoint_types`), `litellm`.
- **Merge order:** bundled → custom config → provider overrides applied to built-ins → `modelOverrides` → custom `models` (same `provider+id` replaces) → cached/discovered models. Same-id models under two providers stay distinct — select `provider/id`.
- **Implicit local engines** (no file needed; skipped if you define the same id in `models.yml` or disable it):
  | id | base URL (env → default) | api |
  |---|---|---|
  | `ollama` | `OLLAMA_BASE_URL` → `OLLAMA_HOST` → `http://127.0.0.1:11434` | `openai-responses`; context from `OLLAMA_CONTEXT_LENGTH` → `/api/show` → 128000 |
  | `llama.cpp` | `LLAMA_CPP_BASE_URL` → `http://127.0.0.1:8080` | `openai-responses` |
  | `lm-studio` | `LM_STUDIO_BASE_URL` → `http://127.0.0.1:1234/v1` | `openai-completions`; `GET /models` — works for *any* OpenAI-compatible local server |
  All three are keyless; their models are selectable as soon as the engine answers. `OLLAMA_CONTEXT_LENGTH` only changes omp's budget, not Ollama's `num_ctx`.
- **Discovered proxy/gateway models are priced at zero** ("local-unknown") — see 7.6.
- **The lab's mock provider:** `python3 tools/mock-provider.py --port 8765` serves `GET /v1/models` (one model, `mock-1`) and `POST /v1/chat/completions` (streaming and non-streaming; reply `Hello from mock-1. You said: <last user message>` — the echo is cut at 80 characters, and because omp prepends a `<system-reminder>` block with the date and cwd to your message, what you see is `Hello from mock-1. You said: <system-reminder> Today: …` rather than your own words), prints one banner line to stdout, logs every request to stderr as `[mock-provider] POST /v1/chat/completions -> "POST /v1/chat/completions HTTP/1.1" 200 -`, needs no key. `--fail` turns every chat request into HTTP `429` with `Retry-After: 1` (7.5). `--model <id>` renames the model; `--host` rebinds it.
- **Exact block for the mock** — append to `~/.omp/agent/models.yml`:
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
  ```
- **Verify:** `omp models mock` → a `mock (1)` table with `mock-1 │ 33K │ 4.1K │ - │ no`; `omp -p --model mock/mock-1 "say hi"` → a line starting `Hello from mock-1. You said: <system-reminder> Today:`.
- **Tiny on-device models** (catalog provider `local`, kind `tiny`): `omp models --kind tiny`; `omp tiny-models list`; `omp tiny-models download <id>` / `download all` (default download `lfm2.5-230m`, ~214 MB). Assign with `modelRoles.tiny: local/lfm2.5-230m` (titles) and `modelRoles.memory: local/lfm2-1.2b` (Module 9 memory); `judge: local/lfm2-1.2b` for on-device judgments. Weights download only when a local candidate is used or prefetched; inference runs in a per-model worker (`~/.omp/run/tiny/<model>-<backend>.sock`) that exits after 15 min idle. CPU by default; `providers.tinyModelDevice` / `PI_TINY_DEVICE` (`gpu`, `cuda`, `mlx`, …) and `providers.tinyModelDtype` / `PI_TINY_DTYPE` (setting default `default` = each model's shipped dtype, currently `q4`) are opt-outs.
- **Speech:** `omp setup speech` picks, persists and downloads `modelRoles.speech` (`local/kokoro`, ~100 MB) and `modelRoles.dictation` (`local/parakeet-tdt-0.6b-v3` default, or `local/whisper-*`); `omp models --kind tts|stt` lists them. Keep chains empty (`retry.fallbackChains.speech: []`) to stay local.
- **Cache:** discovered rows persist in `<agent dir>/models.db`; `omp models refresh` forces a re-fetch (the help text calls it the replacement for `rm -rf ~/.omp/models.db`).

**Try it (Walkthrough):**
1. In `omp-course-lab`: `python3 tools/mock-provider.py --port 8765` (leave it running).
   Expected: one banner line on stdout: `mock-provider serving model 'mock-1' on http://127.0.0.1:8765/v1 in normal mode`.
2. Append the block above to `~/.omp/agent/models.yml` (create the file with `providers:` at the top if it does not exist). Run `omp models mock`.
   Expected:
   ```
   mock (1)
   ┌────────┬─────────┬─────────┬──────────┬────────┐
   │ model  │ context │ max-out │ thinking │ images │
   ├────────┼─────────┼─────────┼──────────┼────────┤
   │ mock-1 │     33K │    4.1K │ -        │ no     │
   └────────┴─────────┴─────────┴──────────┴────────┘
   ```
3. `omp -p --model mock/mock-1 "say hi"`.
   Expected: `Working...` then a line starting `Hello from mock-1. You said: <system-reminder> Today:` (the 80-character echo is filled by the block omp prepends, so `say hi` itself is cut off); the mock's stderr shows `"POST /v1/chat/completions HTTP/1.1" 200`.
4. Break it on purpose: delete the `baseUrl:` line and run `omp models`.
   Expected: `Warning: models.yml validation failed — custom providers disabled` followed by `Provider mock: "baseUrl" is required when defining custom models.`; built-in providers still list. Restore the line.
5. Discovery without a file: comment out the whole `mock:` block, then `LM_STUDIO_BASE_URL=http://127.0.0.1:8765/v1 omp models lm-studio`.
   Expected: an `lm-studio (1)` table containing `mock-1` (context `128K`, max-out `33K` — local defaults synthesized by discovery). Uncomment the block afterwards.
6. `omp tiny-models list` then `omp models --kind tiny`.
   Expected: the eight tiny models with descriptions plus `smollm` (the word-completion model, not a chat/tiny role candidate); the second command shows the eight under `local (8)` (`qwen3-1.7b` is the only one listing thinking levels).

**Guided task:** Local engine as `commit` model. Goal: assign a local model to `modelRoles.commit` and prove `omp commit` resolves it. Hints: with Ollama running, `omp models ollama` must list a pulled model (`ollama pull <name>` first); without Ollama, use `LM_STUDIO_BASE_URL=http://127.0.0.1:8765/v1` so `lm-studio/mock-1` is discovered. Set the role (`/model` → the model → `commit`), stage a change in the lab (`echo "# note" >> README.md && git add README.md`), run `omp commit --dry-run`. Checkpoint: the first card reads `● Resolving model...` / `└─ <your local model name>`. Pass condition: that line names the local model (the mock will fail to produce a proposal and omp prints `Commit generated using fallback due to agent failure` — that is expected for the mock; a real Ollama model produces a message). `git restore --staged README.md && git checkout README.md`.
**Stretch:** Tiny titles. Goal: `omp tiny-models download lfm2.5-230m`, set `modelRoles.tiny: local/lfm2.5-230m`, start a session with a real chat model and a descriptive first message. Pass condition: `omp models --kind tiny` lists the model; the session gets a title (M5 `/resume` list or `/rename` view) and `ls ~/.omp/run/tiny/` shows a `lfm2.5-230m-*.sock` worker socket while the session is alive.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `Warning: models.yml validation failed — custom providers disabled` | Schema/validation error (missing `baseUrl`, `api`, or `apiKey` without `auth: none`; unknown root key) | Read the reason printed under the warning; `omp models` again |
| `omp models mock` prints nothing for `mock` | Server not running, wrong port, or `mock` in `disabledProviders` | `curl http://127.0.0.1:8765/v1/models`; `omp config get disabledProviders` |
| Ollama models missing from `omp models` | Engine not answering at `OLLAMA_BASE_URL`/`OLLAMA_HOST`/`127.0.0.1:11434`, id disabled, or an explicit `ollama:` entry in `models.yml` replaced discovery | `curl $OLLAMA_BASE_URL/api/tags`; remove/fix the explicit entry |
| Custom model answers but tools never get called | Wrong wire (`openai-completions` vs `openai-responses`) or the server rejects `strict`/`tool_choice` | Match `api` to the endpoint the server exposes; see `compat` keys in models.md |
| Model works from a shell but shows `no` under images | Transport strips image input for that model class (`compat.stripImageInput`) | Expected for text-only backends |
| Tiny model download fails on NixOS/non-FHS | `onnxruntime-node` needs `libstdc++.so.6` on the loader path | Set `OMP_NATIVE_LIBRARY_PATH` to the directory holding it |

**Cheat sheet:**
| Item | Value |
|---|---|
| File | `~/.omp/agent/models.yml` → `providers.<id>` |
| Minimum custom provider | `baseUrl`, `api`, `apiKey` or `auth: none`, `models[].id` |
| Secret from command | `apiKey: "!op read op://…"` |
| Verify | `omp models <provider>`, `omp -p --model <provider>/<id> "hi"` |
| Local engines | `OLLAMA_BASE_URL`/`OLLAMA_HOST`, `LLAMA_CPP_BASE_URL`, `LM_STUDIO_BASE_URL` |
| Tiny / speech | `omp tiny-models list|download <id>|download all`, `omp setup speech`, `omp models --kind tiny|tts|stt` |

**Source:** omp://models.md, omp://providers.md, omp://local-models.md, omp://environment-variables.md, `omp models --help`, `omp tiny-models --help`, `omp setup --help`, `omp commit --help`

---

## Lesson 7.5 — Resilience: retry, fallback chains, scoping              (~15 min)
**You will be able to:** read omp's retry loader, configure a fallback chain per role or per model, and restrict which models a directory may use.
**Why this exists:** Providers rate-limit, overload and go down. omp already retries transient errors with capped exponential backoff and rotates between logged-in accounts; what you configure is *where to go next* when the current model keeps failing — and, for regulated or client-specific repos, which models may never be used there at all.
**Demo:** [`demos/7.5-fallback.md`](demos/7.5-fallback.md) — a primary on `mock-provider.py --fail` and the JSON events `retry_fallback_applied` → `retry_fallback_succeeded`.
**Concepts:**
- **Retry settings (defaults):** `retry.enabled: true`, `retry.maxRetries: 10`, `retry.baseDelayMs: 500`, `retry.maxDelayMs: 300000` (5 min; `0` disables the fail-fast cap), `retry.modelFallback: true`, `retry.fallbackRevertPolicy: cooldown-expiry` (`never` stays on the fallback), `retry.fallbackChains: {}`. Opt-in: `retry.usageAwareFallback: false` (preflight on coding-plan quota reports; `retry.usageReservePct: 10`, `retry.usageReservePolicy: confirm|auto|fail-closed`).
- **What is retried:** 429 / 500 / 502 / 503 / 504, overloaded, rate/usage limits, network/socket/timeouts, provider "retry your request" wording, classifier refusals. **Not** context overflow — that goes to compaction / context promotion instead.
- **Backoff:** `min(baseDelayMs·2^(attempt−1), 8000 ms)` × 75–100 % jitter → 500, 1000, 2000, 4000, 8000… Provider `retry-after` / `x-ratelimit-reset` headers can lengthen it; a delay above `maxDelayMs` with no credential/model switch fails immediately.
- **In the TUI:** loader `Retrying (attempt/maxAttempts) in Ns… (esc to cancel)`; `Esc` cancels the retry; final failure prints `Retry failed after N attempts: <error>`. Recovered error entries are shown dimmed and are excluded from the model's context.
- **Credential rotation first:** on a usage limit omp first tries another stored account for the same provider (accounts are ranked and rotated); only then the model chain.
- **`retry.fallbackChains`** — keys are a **role** (`default`, `smol`, `judge`, …), an exact **`provider/model-id`** (applies whenever that model is live, whatever role it plays), or a **`provider/*`** wildcard (every model of that provider). Entries are selectors with optional `:thinking`; a `provider/*` *entry* keeps the failing id and swaps the provider. `[]` disables fallback for that key. Chat roles without a chain inherit `default`; model-kind roles (`web`, `speech`, `dictation`, `judge`, `image`) never use `default` — unset means their built-in list. Role aliases like `"@tiny"` are valid entries.
- **Which chain wins** for a failing model: exact `provider/model-id` key → `provider/*` key → the current role's chain → `default` (which also owns a live model belonging to no role). Candidates still cooling down are skipped; the switch applies for the rest of the turn and appends a temporary `model_change`; the primary returns when its cooldown expires (`cooldown-expiry`).
- **Events** (visible with `--mode json`, RPC, extensions): `auto_retry_start {attempt, maxAttempts, delayMs, errorMessage}`, `retry_fallback_applied {from, to, role, reason}`, `retry_fallback_succeeded {model, role}`, `auto_retry_end {success, attempt, finalError?}`. The TUI shows a bounded preview of `reason` under the source→target warning.
- **Startup validation:** unknown models/providers in a chain print `Warning: Fallback chain for role '<role>' references unknown model: <selector>` when the TUI starts.
- **Path-scoped `enabledModels` / `disabledProviders`** (also `enabledProviders`): mix bare strings (apply everywhere) with `{path|paths|pathPrefix|pathPrefixes: …, models|providers|values|items: […]}` entries that apply when the cwd *is* or is *under* the path (`~` expands). Scoping is resolved after the layer merge, so a project array that replaces the global one drops global scoped entries. `omp config get enabledModels` prints the value resolved for the current directory.
- **Effect of a scoped `enabledModels`:** inside the path, the first scoped model becomes the initial model of a fresh session even if `modelRoles.default` points elsewhere; `Ctrl+P` cycling and pickers are limited to the scope. A scoped `disabledProviders` removes the provider's tables from `omp models` inside the path.
- **Context promotion:** `contextPromotion.enabled` (**default `false`**). When on and a request fails with a context-length error, omp switches temporarily to `contextPromotionTarget` configured on the model (`models.yml` → `providers.<p>.modelOverrides.<id>.contextPromotionTarget: provider/bigger-model`) before falling back to compaction. Only the configured target is considered, and only if its credentials resolve.

**Try it (Walkthrough):**
1. Start a second mock as the backup: `python3 tools/mock-provider.py --port 8766`, and add a second provider to `models.yml`:
   ```yaml
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
   Expected: `omp models` shows both `mock (1)` and `mock-backup (1)`.
2. Restart the primary in failure mode: stop the port-8765 mock and run `python3 tools/mock-provider.py --port 8765 --fail`.
   Expected: `curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8765/v1/chat/completions -d '{}'` prints `429`.
3. Add the chain to `~/.omp/agent/config.yml` (two entries — the backup mock, then the real model you use):
   ```yaml
   modelRoles:
     default: mock/mock-1
   retry:
     fallbackChains:
       default:
         - mock-backup/mock-1
         - <your-M1-provider>/<model>
   ```
   Expected: `omp config get retry.fallbackChains` → `{"default":["mock-backup/mock-1","…"]}`.
4. In the lab: `omp` then `say hi`.
   Expected: the request fails on `mock/mock-1`, omp shows a fallback warning from `mock/mock-1` to `mock-backup/mock-1` with the `429 rate limited (mock --fail)` reason, and the answer `Hello from mock-1. You said: <system-reminder> Today: …` arrives from the backup (~10–15 s; the mock's `Retry-After: 1` is honoured first). The status line chip now reads `Mock 1 (backup)`.
5. Same thing headless, as proof you can grep: `omp -p --mode json --no-session "say hi" | grep -E 'retry_fallback_(applied|succeeded)'`.
   Expected: two JSON lines — `{"type":"retry_fallback_applied","from":"mock/mock-1","to":"mock-backup/mock-1","role":"default","reason":"Request failed: 429 rate limited (mock --fail) …"}` and `{"type":"retry_fallback_succeeded","model":"mock-backup/mock-1","role":"default"}`.
6. Restore `modelRoles.default` to your real model and stop the `--fail` mock.

**Guided task:** Scope the mock to the lab. Goal: `mock/mock-1` is selectable only inside `omp-course-lab`. Hints: global `config.yml`:
```yaml
enabledModels:
  - path: ~/path/to/omp-course-lab
    models:
      - mock/mock-1
```
(no bare entries, so other directories keep every model). Checkpoints: `omp config get enabledModels` prints `["mock/mock-1"]` inside the lab and `[]` from a sibling directory; inside the lab a fresh `omp -p "say hi"` answers from the mock even though `modelRoles.default` is your real model. Pass condition: `omp -p --mode json --no-session "say hi" | grep -o '"provider":"mock"' | head -1` prints a match inside the lab and nothing from the sibling directory.
**Stretch:** Per-provider wildcard. Goal: a `retry.fallbackChains` key `mock/*` with entry `mock-backup/*` (keep the failing id, swap provider) and *no* `default` chain; prove the swap with `--fail` on the primary. Pass condition: `retry_fallback_applied` shows `"from":"mock/mock-1","to":"mock-backup/mock-1"` with `"role":"default"` and `omp config get retry.fallbackChains` contains only the `mock/*` key.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| Retry loader spins for minutes, no fallback | `retry.modelFallback: false`, no chain owns the model, or every candidate is cooling down / unavailable | `omp config get retry.modelFallback`; add a `default` chain; check `omp models` lists the fallback |
| `Warning: Fallback chain for role 'default' references unknown model` | Typo or provider without credentials | Use exact `provider/id` from `omp models` |
| Fell back and never came back | `retry.fallbackRevertPolicy: never`, or the primary's cooldown has not expired | `omp config get retry.fallbackRevertPolicy`; `Alt+P` to switch back manually |
| `web`/`judge` ignore my `default` chain | Model-kind roles never inherit `default` | Set `retry.fallbackChains.web` / `.judge` explicitly |
| Context-length errors compact instead of promoting | `contextPromotion.enabled` is off, or no `contextPromotionTarget`/no credentials for it | `omp config set contextPromotion.enabled true`; add the target in `modelOverrides` |
| Scoped `enabledModels` ignored | Project `.omp/config.yml` array replaced the global array; or path does not match cwd (no ancestor walk for project config, but scoping uses cwd prefix) | Check `omp config get enabledModels` from that directory |

**Cheat sheet:**
| Item | Value |
|---|---|
| Retry knobs | `retry.enabled/maxRetries/baseDelayMs/maxDelayMs/modelFallback/fallbackRevertPolicy` |
| Chain keys | role · `provider/model` · `provider/*`; entry `[]` = no fallback |
| Precedence | exact model → `provider/*` → role → `default` |
| Cancel a retry | `Esc` |
| Events | `auto_retry_start/end`, `retry_fallback_applied/succeeded` |
| Scoping | `enabledModels` / `disabledProviders` `{path:, models:|providers:}`; `omp config get <key>` per cwd |
| Promotion | `contextPromotion.enabled: true` + `contextPromotionTarget` |

**Source:** omp://settings.md, omp://non-compaction-retry-policy.md, omp://models.md, omp://providers.md

---

## Lesson 7.6 — Cost visibility              (~10 min)
**You will be able to:** read the session cost in the status line, open the local usage dashboard, and check provider quota windows from a shell.
**Why this exists:** Routing decisions are only as good as your feedback loop. omp records token usage and estimated (or server-reported) cost for every assistant message in the session log; `omp stats` aggregates those logs locally, and `omp usage` asks each provider how much of your plan is left. None of this leaves your machine.
**Demo:** [`demos/7.6-stats.md`](demos/7.6-stats.md) — `omp stats --summary`, the dashboard URL, and the JSON shape.
**Concepts:**
- **Status line:** the `cost` segment shows the recorded session cost; the model chip shows the live model. With scheduled pricing (first-party `deepseek`) it appends `↑` during peak / `↓` off-peak for the *active* model, refreshing at tariff boundaries — the arrow is about the current tariff, not past spend. `statusLine.preset` (`default`, `minimal`, `compact`, `full`, `nerd`, `ascii`, `custom`); with `custom`, put `cost` in `statusLine.leftSegments` / `rightSegments`.
- **How cost is estimated:** from the selected provider/model's catalog pricing, preferring server-reported cost when the provider streams one. Completed messages keep their recorded cost — switching models, crossing a tariff boundary or reopening a session never reprices history. An explicit `cost` in `models.yml` is a flat override; discovered proxy/gateway models stay at zero ("local-unknown"), so a `$0.00` session on a gateway is *unpriced*, not free.
- **`omp stats`:** syncs `~/.omp/agent/sessions/` into `~/.omp/stats.db`, then serves the dashboard at `http://localhost:3847` (`Dashboard available at: http://127.0.0.1:3847`, stop with `Ctrl+C`). `--port <n>`, `--host <h>`. `--summary` prints the console report (Requests, Error Rate, Total/Input/Output Tokens, Cache Rate, Cache Savings, Total Cost, Premium Requests, Avg Duration/TTFT/Tokens-per-second, then **By Model** and **By Folder**). `--json` prints `{overall, byModel, byFolder, byAgentType, timeSeries, modelSeries, modelPerformanceSeries, costSeries}` after a sync line; `byModel` is a **list** of objects (`model`, `provider`, `totalRequests`, `totalInputTokens`, `totalOutputTokens`, `totalCost`, `unpricedRequests`, …), not a map keyed by id. Dashboard API: `/api/stats`, `/api/stats/models`, `/api/stats/folders`, `/api/stats/timeseries`, `/api/sync`.
- **`omp usage`:** per-account limit windows for every authenticated account (OAuth and coding-plan providers); `--provider <id>`, `--json`, `--redact` (for screenshots), `--history --days N` (hourly snapshots), `omp usage clients --days N` (token burn per machine/app), `omp usage invalidate [--provider id]` (drop cached reports). Env-key-only setups print `No credentials found`.
- **Picker hints:** `/model` rows show price per million (`free` for zero-cost entries), observed tokens/s and TTFT.
- **Subagents:** Agent Hub (`Alt+A`, Module 10) lists each task agent's model and usage, so fan-out cost is attributable per agent.
- **Cheap defaults recap:** `smol` for chores, `tiny: local/…` for titles, `commit` on a local engine, `judge` local — everything else in this module was about making the expensive model the exception.

**Try it (Walkthrough):**
1. Finish a short real-model session in the lab (`omp -p "Summarize cli/ in two sentences"`), then `omp stats --summary`.
   Expected: `Syncing session files...`, `Synced N new entries…`, then `=== AI Usage Statistics ===` with `Requests`, `Total Tokens`, `Total Cost: $…`, a `By Model:` line naming your model, and `By Folder:` naming the lab directory.
2. `omp stats --json | sed -n '/^{/,$p' | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["overall"]["totalCost"], [m["model"] for m in d["byModel"]])'`.
   Expected: the total cost and the list of model ids seen (the mock, if used, appears as `mock-1` with `totalCost` `0`).
3. `omp stats` (no flags) and open the printed URL in a browser; `Ctrl+C` to stop.
   Expected: `Dashboard available at: http://127.0.0.1:3847`; the page shows the same totals, per-model and per-folder charts.
4. `omp usage --redact`.
   Expected: per-provider account rows with their windows (or `No credentials found` for env-key setups).
5. In a live session, look at the status line after one answer.
   Expected: a `cost` value; if you are on a discovered/mock model it stays `$0.00` (unpriced).

**Guided task:** Compare two roles by cost. Goal: run the same prompt (`Explain what api/__init__.py re-exports and why`) once with `--model @smol` and once with `--model @slow`, then attribute cost per model. Hints: `omp stats --json` → `byModel` (list of objects); `omp stats --summary` → `By Model:`. Checkpoint: both models appear under `By Model:`. Pass condition: you can state the per-model cost for each and which one had more output tokens (`totalCost` and `totalOutputTokens` on the matching `byModel` entries).
**Stretch:** Put `cost` on the left. Goal: `statusLine.preset: custom` with `cost` in `statusLine.leftSegments` and the model chip on the right. Pass condition: after restart the cost value renders on the left of the status line; `omp config get statusLine.leftSegments` includes `cost`.

**Troubleshooting:**
| Symptom | Cause | Fix |
|---|---|---|
| `Total Cost: $0.0000` for real work | Model priced at zero (discovered proxy/gateway, explicit `cost: 0`) or provider reports none | Give the model a `cost` block in `models.yml`, or trust `omp usage` for plan-based providers |
| Dashboard port in use | Another `omp stats` or service on 3847 | `omp stats --port 3848` |
| `omp stats --json` is not valid JSON | A sync line precedes the object | Strip lines before the first `{` (see step 2) |
| `omp usage` says `No credentials found` | Only env-var keys; no stored accounts | Expected — usage windows come from OAuth / coding-plan accounts |
| Cost arrow `↑/↓` never shows | Only models with scheduled catalog pricing (first-party DeepSeek) show it; flat overrides suppress it | Expected |

**Cheat sheet:**
| Item | Value |
|---|---|
| Dashboard | `omp stats` → `http://localhost:3847`; `--port`, `--host` |
| Console | `omp stats --summary`, `omp stats --json` |
| Storage | reads `~/.omp/agent/sessions/`, writes `~/.omp/stats.db` |
| Quotas | `omp usage [--provider id] [--json] [--redact] [--history --days N]`, `omp usage clients --days N`, `omp usage invalidate` |
| Status line | `cost` segment; `statusLine.preset`, `statusLine.leftSegments/rightSegments` |

**Source:** omp://user-facing-packages.md, omp://settings.md, omp://models.md, omp://cli-reference.md, omp://task-agent-discovery.md, `omp stats --help`, `omp usage --help`
