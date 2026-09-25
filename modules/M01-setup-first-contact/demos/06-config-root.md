# Demo 1.6 — The config root (~50 s)

Real output from the build machine (`omp/18.3.1`, Linux). Entries you have not created yet (`models.yml`, `skills/`, `extensions/`, `agents/`, `keybindings.yml`, `.env`) simply do not exist until you create them.

```text
$ omp config path
/home/user/.omp/agent

$ ls -1p ~/.omp/agent/
agent.db                ← auth store: OAuth sessions + /login-saved keys (Lesson 1.4)
agent.db-shm
agent.db-wal
blobs/                  ← large tool outputs, content-addressed (artifact://, Module 2)
cache/
config.yml              ← global settings: /settings, omp config set/reset write here
custom-session-files/
history.db              ← prompt history (Ctrl+R search)
last-changelog-version
models.db               ← cached model catalog (omp models refresh)
sessions/               ← one bucket per working directory (Module 5)
terminal-sessions/

$ ls ~/.omp/agent/sessions/ | head -3
-
-Downloads
-Downloads-omp-course-lab          ← <encoded-cwd>: "-" + path under $HOME with "/" → "-"

$ ls -1p ~/.omp/
agent/        ← the agent directory above
cache/
logs/
plugins/      ← installed plugins (Module 12)
profiles/     ← one agent/ tree per --profile
stats.db      ← omp stats (Module 7)
…
```

## One setting, round-trip

```text
$ omp config get tools.approvalMode
yolo
$ omp config get tools.approvalMode --json
{
  "key": "tools.approvalMode",
  "value": "yolo",
  "type": "enum",
  "description": "Default approval behavior for tool calls. 'Always ask' auto-approves read-only tools only. 'Write' auto-approves read and workspace-write tools. 'Yolo' auto-approves all tiers; user policy may still prompt or block."
}

$ omp config get startup.showSplash
false
$ omp config set startup.showSplash true
✔ Set startup.showSplash = true
$ grep -n -A1 startup ~/.omp/agent/config.yml
15:startup:
16-  showSplash: true
$ omp config reset startup.showSplash
✔ Reset startup.showSplash to false
$ grep -c startup ~/.omp/agent/config.yml
0

$ omp config list | grep -c .
524                                       ← every key; use `get` for one
```

## Profiles and relocation

```text
$ omp --profile course config path
/home/user/.omp/profiles/course/agent
$ omp --profile course token anthropic
No active credential found for provider "anthropic".      ← profiles do not share agent.db
$ PI_CODING_AGENT_DIR=/tmp/omp-alt omp config path
/tmp/omp-alt
```

## Setup checks

```text
$ omp setup python --check
Python: /usr/bin/python3

✔ Python execution is ready

$ omp setup --check
error: setup --check/--json requires a COMPONENT (python|speech)
```
