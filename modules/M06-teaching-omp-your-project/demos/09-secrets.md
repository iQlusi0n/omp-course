# Demo 6.9 — Secrets (~55 s)

Placeholder shapes follow `omp://secrets.md`; the exact 12-character hash differs per install (it is an HMAC under `~/.omp/agent/secret-placeholder.key`). Model replies are illustrative.

```text
$ cat .env.example
LAB_TOKEN=labtok_0123456789abcdef
DATABASE_URL=sqlite:///data/lab.sqlite
$ cp .env.example .env
$ omp config get secrets.enabled
true
$ cat .omp/secrets.yml
- type: regex
  content: "labtok_[0-9a-f]{16}"
  friendlyName: Lab Token
- type: regex
  content: "postgres://[^\\s]+"
  mode: replace
  replacement: "postgres://***"

$ omp
> Read .env and tell me: how many characters is the LAB_TOKEN value, does it
> start with "labtok_", and does it contain "$$"?
▸ read .env
   LAB_TOKEN=labtok_0123456789abcdef          ← what YOU see: display restores placeholders locally
   DATABASE_URL=sqlite:///data/lab.sqlite
The LAB_TOKEN value I received is `$$LABTOKEN_7Q2M9X4KD1PZ:L$$` — 27 characters,
it does not start with "labtok_", and it does contain "$$". That is a redaction
placeholder: the real token was withheld from me.

> Run: set -a; . ./.env; set +a; printf '%s' "$LAB_TOKEN" | wc -c; printf '%s' "$LAB_TOKEN" | cut -c1-7
▸ bash set -a; . ./.env; set +a; printf '%s' "$LAB_TOKEN" | wc -c; printf '%s' "$LAB_TOKEN" | cut -c1-7
   23
   labtok_                                   ← the shell had the real value

> Take the LAB_TOKEN value exactly as you saw it and run: printf '%s' "<value>" | cut -c1-7
▸ bash printf '%s' "$$LABTOKEN_7Q2M9X4KD1PZ:L$$" | cut -c1-7     ← what the model wrote (the card may show the restored value)
   labtok_                                   ← omp restored the real token before the shell ran it
```

What the provider received in that session: `.env` contents with `$$LABTOKEN_…:L$$` in place of the token, three times. What the shell received: `labtok_0123456789abcdef`, twice. A `mode: replace` entry would show its `replacement` to the model and stay that way in any command the model writes.
