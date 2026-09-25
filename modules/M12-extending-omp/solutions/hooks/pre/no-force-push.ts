// no-force-push — Module 12 solution (Lesson 12.2), legacy HookAPI form.
//
// Same policy as solutions/force-push-guard, written against `HookAPI`.
// Shape from omp://hooks.md ("What a hook module is") and
// omp://skills/authoring-hooks.md ("Factory signature").
//
// Discovery requires the pre/ or post/ subdirectory (omp://hooks.md, "Native
// discovery location"):
//   <lab>/.omp/hooks/pre/no-force-push.ts      <- loads
//   <lab>/.omp/hooks/no-force-push.ts          <- silently ignored
//
// Note the import path: HookAPI is NOT re-exported from the package root.
import type { HookAPI } from "@oh-my-pi/pi-coding-agent/extensibility/hooks";

const FORCE_PUSH = /\bgit\s+push\b[^\n;&|]*?(?:\s--force(?!-with-lease)\b|\s-f\b)/;

export default function noForcePush(pi: HookAPI): void {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;
    const cmd = String(event.input.command ?? "");
    if (!FORCE_PUSH.test(cmd)) return;

    if (!ctx.hasUI) return { block: true, reason: "git push --force blocked (no UI to confirm)" };
    const ok = await ctx.ui.confirm("Force push", `Allow once?\n${cmd}`);
    if (!ok) return { block: true, reason: "user denied git push --force" };
  });
}
