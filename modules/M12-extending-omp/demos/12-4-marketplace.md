# Demo 12.4 — Local marketplace, project-scoped install (~60 s)

Recorded on omp 18.3.1 with `solutions/my-marketplace` via the CLI (`omp plugin …`); the `/marketplace …` slash commands are the same operations. Paths abbreviated.

```
$ omp plugin marketplace add ../my-marketplace
✔ Added marketplace: /home/user/my-marketplace

$ omp plugin marketplace list
Configured Marketplaces:

  course-marketplace  /home/user/my-marketplace

$ omp plugin discover course-marketplace
Available Plugins (course-marketplace):

  lab-tools@1.0.0
    One skill (lab conventions) and one command (/lab-tools:standup) for omp-course-lab

$ omp plugin install --scope project lab-tools@course-marketplace
✔ Installed lab-tools from course-marketplace (1.0.0)

$ omp plugin list
Marketplace Plugins:

  lab-tools@course-marketplace (1.0.0) (project)

$ find .omp/plugins -maxdepth 2
.omp/plugins
.omp/plugins/omp-plugins.lock.json
.omp/plugins/node_modules
.omp/plugins/node_modules/lab-tools        -> symlink into ~/.omp/plugins/cache/plugins/…
.omp/plugins/installed_plugins.json

$ omp read skill://lab-conventions
---
name: lab-conventions
description: Use when editing omp-course-lab. Test command, layout, and the directories that must never be edited.
---

# omp-course-lab conventions
- Run the test suite with `python3 -m unittest discover -s tests` before claiming a change works.
…
```

Inside omp the plugin contributes a namespaced command and a skill command (from the RPC `available_commands_update` frame):

```
lab-tools:standup      source: file
skill:lab-conventions  source: skill
```

Disable / enable / uninstall:

```
$ omp plugin disable --scope project lab-tools@course-marketplace
✔ Disabled lab-tools@course-marketplace
$ omp read skill://lab-conventions
Unknown skill: lab-conventions
Available: none

$ omp plugin enable --scope project lab-tools@course-marketplace
✔ Enabled lab-tools@course-marketplace

$ omp plugin uninstall --scope project lab-tools@course-marketplace
✔ Uninstalled lab-tools@course-marketplace
$ omp plugin marketplace remove course-marketplace
✔ Removed marketplace: course-marketplace
$ cat .omp/plugins/installed_plugins.json
{
  "version": 2,
  "plugins": {}
}
```

Note: under `omp --profile <name>` the marketplace registry lands in `~/.omp/profiles/<name>/marketplaces.json`, not `~/.omp/marketplaces.json`.
