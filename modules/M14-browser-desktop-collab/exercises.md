# Module 14 — Exercises

Verified against `omp/18.3.1`. Start from `cd omp-course-lab && git checkout module-14-start`.
Tiers: **W** walkthrough (exact prompts/keys), **G** guided (goal + hints + checkpoints), **S** stretch (goal + pass condition; instructor notes in `solutions/`).
Each exercise has an observable pass condition — a card, a file, a JSON field, or a `read` of an internal URI.

Prerequisites per exercise are stated up front; nothing here needs Node, a C toolchain, or a system Chrome (omp manages headless Chromium). 14.2 needs a real desktop session; 14.3 needs a second terminal; 14.4 S needs a stencil.so login.

---

## 14.1-W — Signup smoke test through the browser prelude (~15 min)

**Prereqs:** `omp config get browser.enabled` → `true` (default); `eval.js` → `true`. Lab root.

1. Start the lab API as a service. Prompt: *"Start `python3 -m api` as a bash service named `lab-api`, ready when port 8080 answers."*
   **Expected:** bash card with `name: "lab-api"`, `ready: {port: 8080}`; result `lab-api: ready pid=<n>`.
2. Prompt: *"eval JS: open `http://127.0.0.1:8080/` in a browser tab named `signup` (wait_until load) and `console.log(JSON.stringify(await tab.observe()))`."*
   **Expected:** `Opened tab "signup" on headless browser (hidden, shared)` · `Title: omp-course-lab signup` · elements `[{id:1, role:"textbox", name:"Name "}, {id:2, role:"textbox", name:"Email "}, {id:3, role:"button", name:"Sign up"}]` (ids may differ — that is the point of observing).
3. Prompt: *"In one eval cell: reopen the same tab, `observe()`, fill Name and a fresh unique Email (e.g. `m14-${Date.now()}@example.com` — `ada@example.com` and the other seeded users already exist and a duplicate makes `POST /signup` return 500, lab issue #8) via `tab.id(...)`, click the Sign up button, then `tab.run` a function that `waitForSelector('#banner', {visible:true, timeout:5000})`, reads its text with `tab.evaluate`, throws unless it is exactly `Welcome aboard!`, and returns it. Print the text, then `tab.screenshot({silent:true})` and print the path, then `tab.close()`."*
   **Expected:** `banner: Welcome aboard!` · `screenshot: /tmp/omp-sshots-<hex>.webp` (or under `browser.screenshotDir`) · `Released managed tab "signup"`.
4. Prompt: *"read <that path>"*. **Expected:** the image renders; the banner text is visible.
5. Prompt: *"Copy the screenshot to `notes/14-1-signup.webp`."* **Expected:** file exists (`ls notes/`).

**Pass:** the eval card contains `banner: Welcome aboard!` **and** `notes/14-1-signup.webp` exists.

Deliberate failures (do each once): rerun step 3 with `timeout: 5` in `waitForSelector`. **Expected:** `timed out after 5ms` — the unit is milliseconds. Rerun step 3 with `ada@example.com`. **Expected:** the cell throws `banner was "Signup failed: internal error"` — the seeded user already exists.

---

## 14.1-G — Same check as a background `agent()` job (~10 min)

**Goal:** run the signup check as a background subagent from an eval cell while you keep working in the main session, and receive its result as a delivery.

**Hints:**
- `const h = await agent("Open http://127.0.0.1:8080/ in a browser tab named 'signup-bg'. Fill Name and Email (use a fresh email), click Sign up, wait for #banner, and reply with the exact banner text and the tab.screenshot() path. Close the tab.", { label: "ui-check" });` then `console.log(h.handle, h.status)` — **do not** `await h.wait()`.
- Python: `h = await agent("...", label="ui-check"); print(h.handle, h.status)`.
- The child has its own eval executor; use a **different tab name** than any tab the parent holds.
- Meanwhile ask omp something unrelated (*"how many routes does `api/` define?"*).
- Watch progress with `Alt+A` (Agent Hub); `read agent://<id>` after it finishes.

**Checkpoints:** (1) the cell returns immediately and prints `agent://<id>` + `running`; (2) Hub shows `ui-check`; (3) a delivery card arrives later without you asking; (4) `read agent://<id>` returns the child's final output.

**Pass:** the delivered result contains `Welcome aboard!` and a screenshot path that `read <path>` renders.

---

## 14.2-G — Screenshot the terminal, walk the AX tree, press the Tk button (~20 min)

**VM or dedicated user account strongly recommended.**
**Prereqs:** desktop session; `python3 -c "import tkinter"` succeeds; OS permissions — macOS: Screen Recording + Accessibility for your terminal app, then restart it; Linux X11: RandR/XTEST + AT-SPI; Wayland: expect `capture: false` (no screenshots) and no `raise()`; Windows: none documented. Put `tools: { approvalMode: write }` in the lab's `.omp/config.yml` so input calls prompt.

**Goal:** with `python3 bin/gui-demo.py` running (window **Lab GUI Demo**, button **Click me**, label **Ready**), from one omp session: (a) screenshot the terminal window omp runs in, (b) print the Tk window's AX tree, (c) find its button by role and `press()` it via AX, (d) prove the label now reads **Clicked!**.

**Hints:**
- `/computer on` first (session-only). `display(await computer.capabilities())` before anything else.
- `computer.windows({ app: "<terminal app>" })` — substring, case-insensitive; if several match, pick by `id`.
- `const win = await computer.window({ title: "Lab GUI Demo" }); await win.ax({ maxDepth: 6 })`.
- `const b = await win.find({ role: "button" }); await b[0].press();` — expect an approval prompt (`exec`).
- Proof: `(await win.ax()).includes("Clicked!")` or `await win.screenshot()`.
- No button in the tree? Use the pixel path: `await win.screenshot()` then `await win.click(x, y)` with coordinates **from that screenshot**.

**Checkpoints:** (1) capabilities show `capture`/`ax` available and permission granted; (2) two screenshots (terminal, Tk) as inline images, no prompts (read tier); (3) one approval prompt showing `press` and the resolved JS; (4) the label changed.

**Pass:** a fresh `win.ax()` or screenshot shows **Clicked!** (app state changed), and the transcript shows exactly one `exec` approval for the press.

---

## 14.3-G — Host, join, steer a subagent from the guest's Hub (~20 min)

**Prereqs:** two terminals (a partner on another machine is better); relay reachable (`collab.relayUrl` = `wss://my.omp.sh` default).

**Goal:** host shares full control; partner joins; host spawns a subagent; partner steers it from **their** Agent Hub; `omp collab list --json` shows two participants.

**Hints:**
- Host: `/collab` → paste the `omp join "…"` line to the partner (it is a secret).
- Partner: `omp join "<link>"` (any directory) or `/join <link>` inside omp.
- Host prompt: *"Use a `task` subagent to audit `api/` for unhandled exceptions; report a list."*
- Partner: `Alt+A` → select the host's subagent → transcript viewer → type *"also audit `cli/`"* + Enter. Guests get the full-screen viewer, and the input line only when the agent is messageable.
- Third shell on the host machine: `omp collab list --json`.
- Host `/collab status` also lists participants.

**Checkpoints:** (1) partner's transcript shows host's cards natively (not a screen mirror); (2) partner's prompts appear on both sides with the partner's name badge; (3) Hub on the partner lists the host's subagent with live progress; (4) the steering message appears in the subagent's transcript on both sides.

**Pass:** `omp collab list --json` → `hosts[0]` has a participant count of **2** while the partner is connected, and the subagent's transcript contains the partner's steering text.

---

## 14.4-S — Stream it, record it, clip it (~20 min)

**Prereqs:** stencil.so account (`/login` → Stencil), or `STENCIL_API_KEY`.

**Goal:** (1) `omp stream --title "M14"` from the lab root and attach a new omp session; (2) prove redaction: `read .env.example` in the streamed session and confirm the viewer page shows `LAB_TOKEN=••••••` (a `NAME=value` row with a `*_TOKEN` name) while `DATABASE_URL=…` is untouched; (3) `/record` a short run of 14.1-W, stop it, `omp play` it, then `omp clip -t "Signup smoke" -d "M14"`.

**Pass:** the viewer page shows the session pane with the token masked, `omp play` replays the recording, and `omp clip` prints a `live.omp.sh/c/<id>` URL whose page plays it.

---

## 14.4-G (optional, offline) — Push-to-talk dictation (~10 min)

**Prereqs:** microphone; ~700 MB download.

**Goal:** dictate a prompt with the space bar.

**Hints:** `omp setup speech` (choose the default dictation model; wait for download) → `omp config set stt.enabled true` → new session → hold **Space** on an empty composer, speak, release. `stt.submitTrigger` is `never` by default: press Enter to send.

**Checkpoints:** `omp setup speech --check` shows the STT model installed; transcription appears in the composer.

**Pass:** the transcribed text lands in the composer and, after Enter, omp responds to it.

---

## Cleanup

`write proc://lab-api/kill` (or ask omp to stop the `lab-api` service). `git checkout -- data/lab.sqlite` (or `python3 tools/seed_db.py`) — every successful signup added a row to the tracked seed DB. `/computer off`. `/collab stop`. `omp config set browser.relay false` if you enabled it in the 14.1 stretch. Delete `notes/14-1-signup.webp` if you don't want it (`notes/` is gitignored anyway).
