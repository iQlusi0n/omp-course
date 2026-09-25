// sdk-readonly.ts — restricted, in-memory, read-only omp session that streams text deltas.
// Every API name below is taken from omp://sdk.md ("Explicit wiring", "Built-ins and filtering",
// "Minimal controlled embed example"). Requires Bun 1.3.14+ and `bun add @oh-my-pi/pi-coding-agent`.
//
// Run:  bun sdk-readonly.ts "Find all TODO comments in this repo and list them"
// Pass: text streams to stdout; a prompt asking for a file write is refused because
//       `write`/`edit`/`bash` are not in toolNames and restrictToolNames is true.
import {
  createAgentSession,
  discoverAuthStorage,
  ModelRegistry,
  SessionManager,
  Settings,
} from "@oh-my-pi/pi-coding-agent";

const prompt = process.argv[2] ?? "Summarize this repository in 3 bullets.";

// Own the credential/model lifecycle explicitly (sdk.md "Explicit wiring").
const authStorage = await discoverAuthStorage();
const modelRegistry = new ModelRegistry(authStorage);
await modelRegistry.refresh();

const available = modelRegistry.getAvailable();
if (available.length === 0) throw new Error("No authenticated models available");

// Isolated settings: nothing from ~/.omp/agent/config.yml leaks in (sdk.md "Minimal controlled embed").
const settings = Settings.isolated({
  "compaction.enabled": true,
  "retry.enabled": true,
});

const { session, modelFallbackMessage } = await createAgentSession({
  authStorage,
  modelRegistry,
  model: available[0],
  settings,
  sessionManager: SessionManager.inMemory(), // no .jsonl on disk; session.sessionFile === undefined
  toolNames: ["read", "grep", "glob"],       // request these...
  restrictToolNames: true,                   // ...and make it an allowlist (also disables ambient MCP/extensions/LSP)
  enableMCP: false,
  enableLsp: false,
});

if (modelFallbackMessage) process.stderr.write(`${modelFallbackMessage}\n`);
console.error(`[tools] ${session.getActiveToolNames().join(", ")}`);
console.error(`[sessionFile] ${session.sessionFile}`); // undefined for in-memory

const unsubscribe = session.subscribe((event) => {
  switch (event.type) {
    case "tool_execution_start":
      process.stderr.write(`\n[tool] ${event.toolName}\n`);
      break;
    case "message_update":
      if (event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
      }
      break;
    case "agent_end":
      // sdk.md: treat as completion only when isTerminal !== false
      if (event.isTerminal !== false) process.stderr.write("\n[agent_end] terminal\n");
      break;
  }
});

await session.prompt(prompt);
unsubscribe();
await session.dispose();
