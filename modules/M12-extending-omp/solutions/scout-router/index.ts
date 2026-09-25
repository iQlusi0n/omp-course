// scout-router — Module 12 solution (Stretch)
//
// Reroute every `scout` subagent to a cheap model, without touching
// `task.agentModelOverrides`. Contract from omp://extensions.md
// ("Subagent lifecycle"):
//
//   before_subagent_spawn -> { model?: string | string[]; block?: boolean; reason?: string; note?: string }
//
// - fires in the PARENT session once per spawned child (task, eval agent(),
//   workpool workers), before the child resolves its model
// - event carries `agent`, `invocationKind`, `modelRole`, `patterns`, `spawnKey`
// - a returned `model` replaces the spawn's attempt-ordered patterns; extra
//   entries become the child's retry fallback chain
// - `note` is shown by the task UI / Agent Hub as the spawn's routing reason
// - `block: true` refuses the spawn with `reason`
//
// Install: cp -r solutions/scout-router <lab>/.omp/extensions/scout-router
// Adjust CHEAP to a model you are logged in to (`omp models`).
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Role alias or provider/id. "@smol" follows whatever modelRoles.smol points at.
const CHEAP = ["@smol"];

export default function scoutRouter(pi: ExtensionAPI) {
  pi.setLabel("Scout router");

  pi.on("before_subagent_spawn", async (event, ctx) => {
    if (event.agent !== "scout") return;

    // Sanity: resolve the target the same way --model would; skip if unknown.
    const resolved = ctx.models.resolve(CHEAP[0]);
    if (!resolved) {
      pi.logger.warn(`scout-router: cannot resolve ${CHEAP[0]}; leaving spawn untouched`);
      return;
    }

    return {
      model: CHEAP,
      note: `scout-router: scouts run on ${resolved.provider}/${resolved.id}`,
    };
  });
}
