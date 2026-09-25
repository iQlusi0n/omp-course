// hello-extension — Module 12 solution (Lesson 12.1)
//
// Shapes copied from omp://skills/authoring-extensions.md ("Full example") and
// omp://extensions.md ("Quick start", "Tool authoring details").
//
// Install (pick one):
//   cp -r solutions/hello-extension  <lab>/.omp/extensions/hello-extension   # project
//   cp -r solutions/hello-extension  ~/.omp/agent/extensions/hello-extension  # user
//   omp -e ./solutions/hello-extension                                         # once
//
// Then: /hello Ada   and   "Count the words in README.md using word_count."
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

export default function helloExtension(pi: ExtensionAPI) {
  const z = pi.zod;

  // Registration-only during load. Runtime actions (pi.sendMessage, ctx.ui.*)
  // are only legal inside handlers/commands/tools — calling them here throws
  // ExtensionRuntimeNotInitializedError.
  pi.setLabel("Hello + Word Count");

  // 1) Lifecycle event: fires once the session is live.
  pi.on("session_start", async (_event, ctx) => {
    if (!ctx.hasUI) return; // headless (-p, subagents): ui methods are no-ops anyway
    ctx.ui.notify(`hello-extension loaded in ${ctx.cwd}`, "info");
  });

  // 2) Slash command: /hello [name]
  pi.registerCommand("hello", {
    description: "Send a greeting into the conversation",
    handler: async (args, ctx) => {
      const name = args.trim() || "world";
      pi.sendMessage(
        {
          customType: "course.hello.greeting", // namespace your customType
          content: `Hello, ${name}!`,
          display: true,
          attribution: "user",
        },
        { triggerTurn: false }, // just record + display; don't start a model turn
      );
      ctx.ui.notify(`Greeted ${name}`, "info");
    },
  });

  // 3) LLM-callable tool: word_count
  pi.registerTool({
    name: "word_count", // snake_case, globally unique
    label: "Word Count",
    description: "Count the words in a string of text",
    parameters: z.object({
      text: z.string().describe("Text to count"),
    }),
    approval: "read", // pure function: never needs a prompt even in always-ask
    // Default loadMode is "discoverable": the tool is advertised as an xd://word_count
    // device and the model dispatches it by writing JSON to that URI. "essential"
    // lists it in the top-level tool inventory so you get a plain `word_count` card.
    loadMode: "essential",
    async execute(_toolCallId, params, signal, onUpdate, _ctx) {
      if (signal?.aborted) {
        return { content: [{ type: "text", text: "Cancelled" }] };
      }
      onUpdate?.({ content: [{ type: "text", text: "Counting..." }] });
      const count = params.text.split(/\s+/).filter(Boolean).length;
      return {
        content: [{ type: "text", text: String(count) }],
        details: { count }, // structured, reconstructible from history
      };
    },
  });
}
