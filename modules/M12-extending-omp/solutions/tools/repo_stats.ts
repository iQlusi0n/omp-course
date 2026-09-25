// repo_stats — Module 12 solution (Lesson 12.2), standalone custom tool.
//
// A CustomToolFactory module: the model can call it, but it registers no
// commands or event handlers. Shape from omp://custom-tools.md ("Module
// contract"). Note the execute argument order differs from extension tools:
//
//   custom tool : execute(toolCallId, params, onUpdate, ctx, signal)
//   extension   : execute(toolCallId, params, signal, onUpdate, ctx)
//
// Discovery: <lab>/.omp/tools/repo_stats.ts or ~/.omp/agent/tools/repo_stats.ts
// (omp://custom-tools.md, "Discovery locations"). Restart omp after adding.
import type { CustomToolFactory } from "@oh-my-pi/pi-coding-agent";

const factory: CustomToolFactory = (pi) => ({
  name: "repo_stats",
  label: "Repo Stats",
  description: "Count git-tracked files matching a glob (default: all Python files)",
  parameters: pi.zod.object({
    glob: pi.zod.string().optional().describe("git ls-files pathspec, e.g. '**/*.py'"),
  }),
  approval: "read",
  loadMode: "essential", // default for a non-built-in name is "discoverable" (xd://repo_stats)

  async execute(_toolCallId, params, onUpdate, _ctx, signal) {
    onUpdate?.({ content: [{ type: "text", text: "Scanning..." }], details: { phase: "scan" } });

    const result = await pi.exec("git", ["ls-files", params.glob ?? "**/*.py"], { signal, cwd: pi.cwd });
    if (result.killed) throw new Error("Scan was cancelled");
    if (result.code !== 0) throw new Error(result.stderr || "git ls-files failed");

    const files = result.stdout.split("\n").filter(Boolean);
    return {
      content: [{ type: "text", text: `${files.length} tracked files match ${params.glob ?? "**/*.py"}` }],
      details: { count: files.length, sample: files.slice(0, 10) },
    };
  },
});

export default factory;
