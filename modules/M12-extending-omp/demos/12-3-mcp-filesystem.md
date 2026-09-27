# Demo 12.3 — MCP server from `.omp/mcp.json` (~60 s)

Recorded on omp 18.3.1 with the Python `lab-fs` server (`solutions/mcp/lab_mcp_server.py`, no Node required) against a scratch `data/` and `docs/` (hence the `README.md` and two-file `docs/` listing below); in `omp-course-lab`, `data/` holds only `lab.sqlite` and `docs/` has four files. The `npx` `filesystem` server behaves the same way with `mcp__filesystem_*` tool names; it was not runnable on the build machine (no Node) and is shown only in the config.

`.omp/mcp.json`:

```json
{
  "mcpServers": {
    "lab-fs": { "type": "stdio", "command": "python3", "args": ["tools/lab_mcp_server.py", "${LAB_DATA_DIR:-data}"] }
  }
}
```

Resource read from the shell — omp spawns the server, does the `initialize` handshake, `resources/list`, `resources/read`:

```
$ omp read mcp://lab-fs://listing
README.md
lab.sqlite

$ LAB_DATA_DIR=docs omp read mcp://lab-fs://listing        # ${VAR:-default} expanded at discovery
spec.md
spec.pdf

$ omp read mcp://nope
No MCP server has resource "nope".

Available resources:
  lab-fs://listing (lab-fs)
```

Tool calls, rendered from the `--mode json` stream (scripted model):

```
> Read README via MCP.

  ▸ mcp__lab_fs_list_files  Listing lab data
      path: "."
    file README.md 25B
    file lab.sqlite 12288B

  ▸ mcp__lab_fs_read_file  Reading the lab readme
      path: "README.md"
    [no intent field delivered]
    hello world from the lab
    details: { "serverName": "lab-fs", "mcpToolName": "read_file", "provider": "native", "providerName": "OMP" }
```

Raw event for the second call:

```
{"type":"tool_execution_end","toolCallId":"call_2","toolName":"mcp__lab_fs_read_file","result":{"content":[{"type":"text","text":"[no intent field delivered]\nhello world from the lab\n"}],"details":{"serverName":"lab-fs","mcpToolName":"read_file","isError":false,"provider":"native","providerName":"OMP"}},"isError":false}
```

Print-mode barrier when a configured server cannot start (here a deliberately broken entry, `OMP_MCP_TIMEOUT_MS=5000`):

```
Warning: MCP server "bad" not ready after 5000ms; its tools are unavailable for this run.
```

`enabled: false` on the entry → the resource disappears:

```
$ omp read mcp://lab-fs://listing
No MCP server has resource "lab-fs://listing".

Available resources:
  (none)
```
