// force-push-guard — Module 12 solution (Lesson 12.1 / 12.2, Guided task)
//
// Blocks `git push --force` / `git push -f` before the bash tool runs and tells
// the model why. Contract from omp://extensions.md ("Tool lifecycle") and
// omp://skills/authoring-hooks.md ("Pre-tool blocking contract"):
//
//   return { block: true, reason: "..." }  -> tool never executes; `reason`
//                                            becomes the tool error text the
//                                            model sees.
//   throw                                   -> also blocks (fail-closed).
//   return undefined                        -> execution continues.
//
// Install: cp -r solutions/force-push-guard <lab>/.omp/extensions/force-push-guard
//      or: omp -e ./solutions/force-push-guard
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// `git push` followed (on the same simple command) by --force or -f.
// `--force-with-lease` is deliberately allowed: it is the safe variant.
const FORCE_PUSH = /\bgit\s+push\b[^\n;&|]*?(?:\s--force(?!-with-lease)\b|\s-f\b)/;

export default function forcePushGuard(pi: ExtensionAPI) {
  pi.setLabel("Force-push guard");

  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;

    const command = String(event.input.command ?? "");
    if (!FORCE_PUSH.test(command)) return;

    // Interactive session: let a human override once. Headless: hard block.
    if (ctx.hasUI) {
      const allow = await ctx.ui.confirm(
        "Force push blocked",
        `The agent wants to run:\n${command}\n\nAllow this one time?`,
      );
      if (allow) return;
    }

    return {
      block: true,
      reason:
        "force-push-guard: `git push --force` is blocked in this repository. " +
        "Use `git push --force-with-lease` only if the user explicitly asked, " +
        "otherwise push normally or ask the user.",
    };
  });
}
