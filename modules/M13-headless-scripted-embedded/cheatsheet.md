# Module 13 cheat sheet — headless omp (omp 18.3.1)

## Print mode
| Task | Command |
|---|---|
| one prompt, text out | `omp -p "…"` · `echo "…" \| omp -p` · `omp -p @file.md "…"` · `omp -p -- "-starts-with-dash"` |
| event stream | `omp -p --mode json "…"` (one JSON object per line; stderr has `Working...`) |
| final answer only | `… 2>/dev/null \| jq -rs '[.[]\|select(.type=="message_end" and .message.role=="assistant")]\|last\|.message.content[]\|select(.type=="text")\|.text'` |
| thinking in text | `--print-thoughts` |
| budget | `--max-time 10m` → stderr `Deadline exceeded`, exit `1` |
| hygiene | `--no-session` `--no-title` `--no-extensions` `--no-skills` `--no-rules` `--profile ci-bot` |
| tools | `--tools read,grep,glob` · `--no-tools` · `--no-lsp` |
| approval | `--approval-mode always-ask\|write\|yolo` (default `yolo`); `--yolo`/`--auto-approve` |
| overlay | `--config ci.yml` (repeatable; flags > overlays > project > global) |
| model | `--model haiku` · `--model slow` (role) |
| exit codes | `0` completed (even if a tool was refused) · `1` startup failure / deadline |

## JSON event types (`--mode json`)
`session` → `agent_start` → `turn_start` → `message_start/…/message_end` (roles `user`, `assistant`, `toolResult`) → `tool_execution_start/end` → `turn_end` → `agent_end`.
`message_update.assistantMessageEvent.type`: `thinking_start|delta|end`, `text_start|delta|end`, `toolcall_start|delta|end`.

## RPC (`omp --mode rpc --no-ui`)
| Do | Frame |
|---|---|
| first line out | `{"type":"ready","protocolVersion":1,"supportedProtocolVersions":[1,2],"maxFrameBytes":1048576,…}` |
| v2 (lossless chunks) | `{"id":"p","type":"negotiate_protocol","protocolVersion":2}` → `rpc_chunk{chunkId,index,count,byteLength,data}` |
| prompt | `{"id":"r1","type":"prompt","message":"…"}` → ack → events → `{"type":"prompt_result","id":"r1","status":"completed\|aborted\|error","sessionSettled"}` → `session_settled` |
| during a turn | `steer` · `follow_up` · `abort` · `abort_and_prompt` · `prompt{streamingBehavior:"steer"\|"followUp"}` |
| state | `get_state` (`isStreaming`, `isSettled`, `hasPendingAsyncWork`, `model`, `contextUsage`) |
| model / thinking | `set_model{provider,modelId}` · `cycle_model` · `set_thinking_level{level}` |
| session | `new_session` · `open_session{sessionDir}` · `switch_session{sessionPath}` · `get_messages_page{cursor,limit}` · `export_html` |
| shell | `bash{command}` / `abort_bash` (concurrent; match on `id`) |
| filter | `set_event_filter{events:[…]\|null}` |
| host tools | `set_host_tools{tools:[{name,description,parameters}]}` → `host_tool_call{id,toolName,arguments}` → `host_tool_result{id,result:{content:[{type:"text",text}]},isError?}` |
| host URIs | `set_host_uri_schemes{schemes:[{scheme,writable}]}` → `host_uri_request{id,operation,url,content?}` → `host_uri_result{id,content?}` |
| subagents | `set_subagent_subscription{level:"off"\|"progress"\|"events"}` (default off) |
| errors | `{"type":"response","success":false,"error","code?"}`; bad JSON → `command:"parse"`, loop continues |
| exit | close stdin, read stdout to EOF → exit `0` |
| libraries | TS `RpcClient` · Python `from omp_rpc import RpcClient` (`prompt_and_wait`, `require_assistant_text`) |

## SDK (Bun ≥ 1.3.14, `bun add @oh-my-pi/pi-coding-agent`)
| Need | API |
|---|---|
| session | `const { session, modelFallbackMessage } = await createAgentSession({...})` |
| auth/models | `discoverAuthStorage()` · `new ModelRegistry(auth)` · `await registry.refresh()` · `registry.getAvailable()` |
| ephemeral | `sessionManager: SessionManager.inMemory()` (`session.sessionFile === undefined`) |
| persistent | `SessionManager.create(cwd)` · `continueRecent(cwd)` · `list(cwd)` · `open(path)` |
| config | `settings: Settings.isolated({...})` |
| allowlist | `toolNames:[…]` **+** `restrictToolNames:true` (`enableMCP:false`, `enableLsp:false`) |
| events | `session.subscribe(e => …)`; `text_delta` in `e.assistantMessageEvent`; done = `agent_end` with `isTerminal !== false` |
| control | `session.prompt(text,{streamingBehavior?})` · `steer` · `followUp` · `abort` · `await session.dispose()` |

## ACP (editors)
| Do | How |
|---|---|
| serve | `omp acp` (= `omp --mode acp`) |
| default | client permission gate stays on for `bash`, `edit`, `delete`, `move` (`session/request_permission`) |
| unattended | `omp acp --yolo` · `--auto-approve` · `--approval-mode yolo` · `--config acp-yolo.yml` · explicit `tools.approvalMode: yolo` |
| keep one gate | `tools.approval.bash: prompt` (or `deny`) survives yolo |

## CI review bot
`omp -p --mode json --no-session --no-extensions --no-skills --config ci.yml --tools read,grep,glob --max-time 10m "/review <JSON verdict spec>"` → parse last assistant `message_end` (extract the `{…}` from any fence/prose) → exit 1 on P0 or `verdict: fail`.
`ci.yml`: `tools.approvalMode: always-ask` + `tools.approval: {write: deny, edit: deny, bash: deny, eval: deny, task: deny}`.
PRs: `pr://N` · `pr://N/diff` · `pr://N/diff/<i>` · `pr://N/diff/all` · `pr://owner/repo/N` · `omp read pr://N`. Keys via env (`ANTHROPIC_API_KEY`, …). Bigger: `robomp serve`.
