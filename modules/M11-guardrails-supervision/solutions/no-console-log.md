---
description: Never add console.log to shipped web code; use a DEBUG-guarded helper.
condition: "console\\.log"
scope: "text, tool:edit(web/*.js), tool:write(web/*.js)"
interruptMode: always
---
Do not add `console.log(...)` calls to files under `web/`.

If diagnostic output is genuinely needed, define one helper at the top of the file and call that instead:

```js
const DEBUG = false;
function debug(...args) { if (DEBUG) console.warn("[signup]", ...args); }
```

Then use `debug("...")` at the call site. Do not leave any `console.log` in the retried edit.
