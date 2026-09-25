# Demo 1.4 — Authenticate one provider and prove it (~60 s)

`omp login`, `omp token`, `omp models`, `omp usage` output is real (`omp/18.3.1`), with the account identity and secret redacted. The in-session `/login` picker is illustrative.

## From the shell

```text
$ omp login anthropic
  (prints the authorization URL and opens it in your browser;
   complete consent there — if the flow asks you to paste a callback URL back,
   paste it at the prompt)

$ omp token anthropic | cut -c1-6
sk-ant

$ omp models anthropic | head -6
anthropic (26)
┌────────────────────────────┬─────────┬─────────┬───────────────────────────────┬────────┐
│ model                      │ context │ max-out │ thinking                      │ images │
├────────────────────────────┼─────────┼─────────┼───────────────────────────────┼────────┤
│ claude-3-5-sonnet-20240620 │    200K │    8.2K │ -                             │ yes    │
│ claude-3-5-sonnet-20241022 │    200K │    8.2K │ -                             │ yes    │

$ omp usage --provider anthropic --redact
Usage · fetched 5.5s ago

Anthropic — 1 account
  ● mb* · mb*'*
      ● Claude 5 Hour         █████████████████░░░░░░░░░░░  62.0% used · resets in 4h51m
      ● Claude 7 Day          ██░░░░░░░░░░░░░░░░░░░░░░░░░░  8.0% used · resets in 6d21h
  capacity: 5h → 0.62/1 account used (0.38× quota left) · 7d → 0.08/1 account used …
```

## What "not logged in" looks like

```text
$ omp token groq
No active credential found for provider "groq".
Configured providers: anthropic
$ echo $?
1
```

## The `.env` route (API-key providers, no login)

```text
$ cd omp-course-lab
$ printf 'GROQ_API_KEY=gsk_fake123\n' > .env        # <cwd>/.env — gitignored in the lab
$ omp token groq
gsk_fake123                                          ← <cwd>/.env beat "nothing"
$ cd /tmp && omp token groq
No active credential found for provider "groq".      ← project .env does not follow you
Configured providers: anthropic
```

(The key above is fake — `omp token` only reports what would be used; the first real request would fail.)

## In a session (illustrative picker)

```text
$ omp
› /login
  Select a provider
  › anthropic          (OAuth)
    openai-codex       (OAuth)
    github-copilot     (OAuth)
    google-gemini-cli  (OAuth)
    openai             (API key)
    …
  [Enter] → browser opens → back in omp: "Logged in to anthropic"

› /logout
  Select a provider to log out
  › anthropic
  [Enter] → credentials for anthropic removed from ~/.omp/agent/agent.db
```

`/login <provider>` skips the picker. `/login <redirect-url>` finishes an OAuth flow whose callback could not reach omp. Logins are provider-scoped: logging in to `anthropic` does not touch `openai-codex`.
