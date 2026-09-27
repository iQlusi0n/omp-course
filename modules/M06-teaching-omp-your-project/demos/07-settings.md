# Demo 6.7 — Settings layering & profiles (~60 s)

Every line below was run on the build machine with `omp/18.3.1` (paths shortened).

```text
$ cat .omp/config.yml
tools:
  approvalMode: write
theme:
  dark: titanium
secrets:
  enabled: true

$ omp config get tools.approvalMode            # inside the repo root
write
$ (cd .. && omp config get tools.approvalMode) # outside
yolo
$ (cd api && omp config get tools.approvalMode) # subdirectory: no ancestor walk for settings
yolo

$ omp config set tools.approvalMode yolo --json  # writes the GLOBAL file, but…
{"key":"tools.approvalMode","value":"yolo","overriddenBy":"project"}
$ omp config reset tools.approvalMode
✔ Reset tools.approvalMode to write              # effective value is still the project's

$ printf 'tools:\n  approvalMode: always-ask\n' > /tmp/ci.yml
$ PI_CONFIG_FILES=/tmp/ci.yml omp config get tools.approvalMode
always-ask                                       # overlay > project
$ omp config get tools.approvalMode --config /tmp/ci.yml
error: Unknown option '--config'. …              # --config is for launch / acp / models only

$ OMP_PROFILE=m06smoke omp config path
/home/you/.omp/profiles/m06smoke/agent
$ OMP_PROFILE=m06smoke omp config set compaction.enabled false
✔ Set compaction.enabled = false
$ cat ~/.omp/profiles/m06smoke/agent/config.yml
compaction:
  enabled: false
$ ls ~/.omp/profiles/m06smoke/agent/
agent.db  agent.db-shm  agent.db-wal  config.yml

$ SHELL=/bin/bash omp --profile course --alias omp-course
Created omp-course for profile course in /home/you/.bashrc
Restart your shell or run: . '/home/you/.bashrc'
Then use: omp-course update, omp-course --version, or omp-course
$ tail -4 ~/.bashrc
# >>> omp profile alias: omp-course >>>
omp-course() {
    command omp --profile=course "$@"
}
# <<< omp profile alias: omp-course <<<
```

Merge rule in one picture: `tools:` (object) merged key-by-key across layers; `disabledProviders:` (array) replaced wholesale by whichever layer sets it last.
