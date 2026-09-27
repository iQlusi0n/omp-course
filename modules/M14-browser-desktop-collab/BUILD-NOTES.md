# Module 14 — build notes

Built against `omp/18.3.1` on Linux x64 (Python 3 only; no system Chrome, no desktop, no second participant, no Stencil account). Sources: `omp://tools/browser.md`, `omp://tools/computer.md`, `omp://computer-use.md`, `omp://collab.md`, `omp://stream.md`, `omp://keybindings.md`, `omp://user-facing-packages.md`, `omp://settings.md`, `omp://approval-mode.md`, `omp://tools/eval.md`, `omp://tools/bash.md`, `omp://agent-hub.md`, `omp://local-models.md`, `omp://providers.md`; `omp --help`, `omp collab --help`, `omp stream --help`, `omp join --help`, `omp browser-relay --help`, `omp play --help`, `omp clip --help`, `omp setup --help`, `omp config list --json`.

## Deviations from COURSE-OUTLINE.md (doc/binary wins)

1. **`browser.enabled` default is `true`, not off.** Appendix C row "Browser prelude, browser-relay | 14 | off". On a machine whose `~/.omp/agent/config.yml` and project `.omp/config.yml` do not set it, `omp config get browser.enabled` → `true` (`omp config list --json` value `true`). `browser.relay` is `false` (off), so the *relay* half of the row is opt-in as the outline says. Lesson header and cheat sheet state the real defaults.
2. **Coursework wording "start the lab web app as a service"**: LabRepo confirmed `python3 -m api` (port 8080) serves both the JSON API and `web/` statics, so the module uses one service `lab-api` and `http://127.0.0.1:8080/` for the form rather than a separate static server.
3. Outline 14.1 mentions `tab.type()`; kept, but the walkthrough prefers `fill()` (sets the value) and shows `type()` once. Both are documented direct helpers.

## Observed-but-undocumented behaviour (stated as "observed" in the lessons)

- `tab.waitForSelector(..., { timeout })` takes **milliseconds** (`timeout: 5` → `timed out after 5ms`). `browser.md` does not state the unit; `browser.open` `timeout` is documented as seconds.
- Inside `tab.run`, `document` is not defined (runs in the worker) — `RuntimeError: document is not defined`. Consistent with the doc ("Runs use the shared JavaScript runtime"), but the lesson calls it out explicitly because every learner hits it.
- Python `tab.evaluate("() => …")` returns `{}`; an expression string (`"document.querySelector('#banner').textContent"`) returns the value. Doc says `evaluate(fnOrSource, ...args)` without specifying how Python strings are interpreted.
- `tab.screenshot()` wrote `/tmp/omp-sshots-<hex>.webp` on this build (doc says only "full-resolution image" + returns the path). Lessons say "a path like …webp (observed)".
- `browser.open` with an existing name prints `Reused tab "<name>" …` and navigates to the new URL.
- Headless Chromium was available through omp on a machine with no system Chrome; the doc calls it "project-shared headless Chromium" without describing provisioning. The lesson says "managed by omp; first open may be slow".

## Not executed on the build machine (doc-grounded only)

- **14.2 computer**: no desktop/X11. All API, approval-tier, permission, and error-code facts come from `tools/computer.md`, `computer-use.md`, `approval-mode.md`, `settings.md`. Demo `demos/14.2-computer-ax.md` uses placeholder values and says so. Whether Tk widgets appear in the AX tree on each platform is **not** claimed either way; the lesson provides a pixel fallback and grades on the label change.
- **14.3 collab**: only the empty-registry CLI paths were run (`omp collab list` → `No active Collab hosts.`, `--json` → `{"version":1,"hosts":[]}`, `omp collab link 99999` → error exit 1). `/collab` output block in the demo is the example text from `collab.md`. The exact JSON key name for the participant count is **not** pinned (doc lists "participant count" prose only); exercises say "participant count field".
- **14.4 stream/clip/voice**: `omp stream` without login → `stream: a stencil.so account is required …` (exit 1) observed; `omp play` non-TTY error and `omp clip` missing-file error observed; `omp setup speech --check` output observed. The `omp stream` success banner is the doc's example.
- **14.1-G `agent()`**: the handle surface and auto-delivery semantics are from `tools/eval.md`; not spawned here (cost). Verified that the child would need its own tab name (children do not share the caller's eval executor; headless browser is project-shared).

## Claims dropped as unverifiable

- Outline 14.4 "push-to-talk STT" beyond what `keybindings.md` says: kept only "`app.stt.toggle` unbound; hold Space to record, release to transcribe; `stt.enabled`, `stt.language`, `stt.submitTrigger`, roles `dictation`/`speech`, `omp setup speech`". No claim about which mic/device is used or latency.
- `/live` voice mode: the only documentation is the `app.live.toggle` row (`Ctrl+L`, "same as `/live`") and the `live.voice` setting ("Codex-backed realtime voice sessions", default `sol`). No `/live` sub-commands, provider requirements beyond "Codex-backed", or transcript behaviour are claimed. There is no `live.enabled` key (`omp config get live.enabled` → `Unknown setting`).
- Slash-command output strings for `/computer status`, `/collab status`, `/record` stop, and approval-prompt chrome are not documented verbatim; demos describe them in parentheses instead of quoting.
- QR codes: `collab.md` states `/collab` renders QR codes for both links; their exact placement is not described — demo shows `[QR: …]` placeholders.
- `omp collab list` human-readable row layout is not shown in the docs; only the field list is. Not fabricated.

## Coverage (Appendix C rows for M14)

- "Browser prelude, browser-relay" — Lesson 14.1 (`browser.open`, `observe`, `tab.id`, `tab.run`, screenshots, modes, `omp browser-relay install`, `browser.relay`).
- "Computer use" — Lesson 14.2 (`computer.enabled`, `/computer`, `window`, `screenshot`, `ax`, `find`, `press`, `computer.run`, permissions, approval tiers).
- "`/collab`, `/join`, `omp collab`, `omp stream`, `/live` voice" — Lessons 14.3, 14.4.
- "`/export`, `/dump`, `/share`, `/record`, `omp play|clip`" (5, 14) — Lesson 14.4 covers `/record`, `omp play`, `omp clip`; `/dump`/`/export` appear in 14.3 as the guest-side allowlist. `/share` is Module 5's.

## Fixture references (from LabRepo, cwd lab root)

- `python3 -m api` → :8080, serves `/` = `web/index.html`; form `#signup-form` with `#name`, `#email`, `#submit` ("Sign up"); `#banner` gets text `Welcome aboard!` and loses `hidden` on 201, or `Signup failed: <error>` with class `error` otherwise (`web/app.js`); page title `omp-course-lab signup`.
- `data/lab.sqlite` (tracked) is seeded with 12 users whose emails are `<first>@example.com` — including `ada@example.com`. `api/server.py::_signup` inserts straight into it and a duplicate email raises `sqlite3.IntegrityError` → HTTP 500 (`docs/ISSUES.md` #8). All 14.1 cells therefore use a fresh `m14-<timestamp>@example.com`, and the cleanup step reseeds with `git checkout -- data/lab.sqlite` / `python3 tools/seed_db.py`.
- `bin/gui-demo.py`: window "Lab GUI Demo", `ttk.Button` "Click me", `ttk.Label` "Ready" → "Clicked!"; without tkinter prints `tkinter is not available: …` and exits 1.
- `.env.example`: `LAB_TOKEN=labtok_0123456789abcdef`, `DATABASE_URL=sqlite:///data/lab.sqlite`.

## Wave-2 audit (2026-09-27, omp 18.3.1)

Re-verified every command, flag, key, setting key/default, path and URI in this module against `omp://tools/browser.md`, `omp://tools/computer.md`, `omp://computer-use.md`, `omp://collab.md`, `omp://stream.md`, `omp://keybindings.md`, `omp://user-facing-packages.md`, `omp://settings.md`, `omp://approval-mode.md`, `omp://tools/eval.md`, `omp://tools/bash.md`, `omp://bash-tool-runtime.md`, `omp://agent-hub.md`, `omp://local-models.md`, `omp config list --json`, and `omp {stream,play,clip,collab,join,browser-relay,setup} --help`; fixtures against `omp-course-lab/web/index.html`, `web/app.js`, `bin/gui-demo.py`, `.env.example`, `data/lab.sqlite`, `docs/ISSUES.md`.

### Fixed

1. **Duplicate-email fixture bug (14.1 W/G, demo §3–4, solutions).** The reference cells signed up `ada@example.com`, which is seeded user #1; against the real API the banner reads `Signup failed: internal error` and the assert throws. Reproduced with `curl` (500, `IntegrityError`) and then the corrected cell was run end-to-end through `omp -p` with headless Chromium against `python3 -m api` on a DB copy: `banner: Welcome aboard!`, row 13 inserted. The original demo was captured against a stand-in page with no seeded table, which is why it passed; its header now says so. Added a troubleshooting row, a deliberate-failure step, and the `data/lab.sqlite` reseed to cleanup.
2. **14.1 step 1 claimed a `!` bang command could start the supervised service.** `bash-tool-runtime.md`: the bang surface goes through `AgentSession.executeBash()` and only the tool-call path handles named services. Reworded to "ask omp".

### Removed (unverifiable)

- none this pass.
