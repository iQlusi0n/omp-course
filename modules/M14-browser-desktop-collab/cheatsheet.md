# Module 14 cheat sheet — browser · computer · collab · stream/voice (omp 18.3.1)

## Defaults that matter (`omp config get <key>`)
| Key | Default | Note |
|---|---|---|
| `browser.enabled` | `true` | prelude also needs `eval.js`/`eval.py` (both `true`) |
| `browser.relay` | `false` | adopt your own Chrome via `omp browser-relay install`; `PI_BROWSER_RELAY=0|1` overrides |
| `browser.headless` / `browser.screenshotDir` | `true` / unset | unset → screenshots in OS temp dir |
| `computer.enabled` | `false` | `/computer`, `/computer on|off|status` = session only; config edit needs new session |
| `computer.display` / `maxWidth` / `maxHeight` | `all` / `3840` / `2400` | no `computer.backend` key |
| `tools.approvalMode` | `yolo` | use `write` for computer use; `tools.approval.computer|eval: allow|prompt|deny` |
| `collab.relayUrl` / `collab.autoStart` | `wss://my.omp.sh` / `off` | `autoStart: view|control` hosts every session |
| `stream.serverUrl` / `stream.redactPatterns` | `https://live.omp.sh` / `[]` | |
| `stt.enabled` / `stt.submitTrigger` | `false` / `never` | `release`, `release-complete`, `say-submit` |
| `live.voice` | `sol` | Codex-backed live voice |

## Browser (eval prelude)
| Do | JS | Python |
|---|---|---|
| open / reuse | `await browser.open({name,url,wait_until:"load",timeout})` | `await browser.open(name=…, url=…)` |
| existing handle | `browser.tab("main")` | same (sync) |
| inspect | `await tab.observe()` → `tab.id(n)`; `await tab.ariaSnapshot()` → `tab.ref("e5")`; `tab.extract("text")` | same |
| act | `fill(sel,v)` `type(sel,t)` `click(sel)` `press(key)` `select(sel,…)` `uploadFile(sel,…)` | same |
| wait | `waitForSelector(sel,{visible:true,timeout:5000})` (ms) · `waitForUrl` | same, kwargs |
| page JS | `tab.evaluate(fn|src, ...args)`; inside `run`: `page.$eval(sel, fn)` | `tab.evaluate("<expr>")` |
| multi-step | `tab.run(async ({tab,page,wait,assert}, ...args)=>{…}, {args, timeout})` | `tab.run("<js>", timeout=…)` string only |
| screenshot | `tab.screenshot({selector?, fullPage?, silent?})` → path | same |
| close | `tab.close()` · `browser.close({all:true})` · `kill:true` for spawned | same |
| modes | `app:{path}` spawned · `app:{cdp_url}` connected · `app:{relay:true, target:"substr"}` · else headless | |
| relay | `omp browser-relay install` → Load unpacked `~/.omp/browser-relay/extension` → `omp config set browser.relay true`; flags `-p --token --no-group -v` | |

## Computer (eval prelude)
| Do | Call |
|---|---|
| discover | `computer.capabilities()` · `displays()` · `windows({app,title})` · `window(id|{app,title})` · `focusedWindow()` |
| capture / input | `win.screenshot({silent})` · `click(x,y,{button,count,modifiers,delivery})` · `doubleClick` · `move` · `drag([[x,y],…])` · `scroll` · `type(text)` · `press("cmd+shift+p")` · `raise()` / py `raise_()` |
| AX | `win.ax({all,maxDepth})` → `[ref=eN]` · `win.find({role,title,value,limit})` · `win.ref("e5")` · `computer.elementAt(x,y)` · `focusedElement()` |
| element | reads `value() bounds() attributes() actions() parent() children()`; mutations `setValue perform press() click() focus()` |
| clipboard | `computer.clipboard.read()` · `.write(text)` |
| multi-step | `computer.run(fn|code, {args, read_only, timeout≤300})` → `{desktop, wait, assert}`; `wait(ms)` / `wait(pred,{timeout,interval})` |
| approval | inspection = `read`; input/`raise`/`setValue`/`perform`/`press`/`click`/`focus`/`clipboard.write` = `exec`; `run` read only with `read_only:true` |
| rules | pixel coords ⇐ latest screenshot of same target; AX bounds = global coords; prefer AX; `BackgroundUnavailable` → AX or `delivery:"foreground"` |
| permissions | macOS Screen Recording + Accessibility (restart terminal) · X11 RandR/XTEST + AT-SPI · Wayland portal/`LIBEI_SOCKET`, `capture:false` in release builds · Windows UIA |

## Collab
| Do | Command |
|---|---|
| host | `/collab` (control) · `/collab view` · `/collab <relay>` · `/collab status` · `/collab stop` · `/leave` |
| guest | `/join <link>` · `omp join "<link>"` · `/leave` · browser `https://my.omp.sh/#<link>` |
| registry | `omp collab list [--json]` · `omp collab link <instanceId|pid> [--view] [--json]` |
| link | `<roomId>.<key>`; full = 48-byte secret (prompt/interrupt/Hub), view = 32-byte key; AES-256-GCM E2E |
| guest can | prompt · `Esc` interrupt · Hub chat/kill/revive · answer select/editor; local `/dump /export /copy /open /help /hotkeys /theme /settings /leave /collab /exit /quit` |
| host only | `/model /compact /resume /branch`, `!`, `$`, skills — rooms follow the session (`/new`,`/resume`,`/fork` rotate them) |

## Stream, record, voice
| Do | Command |
|---|---|
| login | `/login` → Stencil (stencil.so) · `STENCIL_API_KEY` |
| stream | `omp stream [--title t] [--server url] [--no-tui]`; footer `● LIVE n`; console `/title`, `/quit`; only sessions started after, same dir |
| record | `/record` toggle (`● REC`) → `<tmpdir>/omp-recordings/<utc>-<session>.ompcast` |
| play / clip | `omp play [file] -s 2 -i 1` (Space pause, q quit) · `omp clip [file] -t "…" -d "…"` → `live.omp.sh/c/<id>` |
| voice | `Ctrl+L` = `app.live.toggle` = `/live` |
| dictation | hold Space (`app.stt.toggle` unbound) · `stt.enabled: true` · `omp setup speech [--check]` · roles `dictation` (`local/parakeet-tdt-0.6b-v3`), `speech` (`local/kokoro`) |
