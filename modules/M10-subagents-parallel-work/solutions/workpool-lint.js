// Module 10 — Lesson 10.5: the same lint-fix pool from the JavaScript eval kernel (Bun).
// Load:  %load modules/M10-subagents-parallel-work/solutions/workpool-lint.js
// JS helpers are async and take ONE trailing options object (omp://tools/eval.md):
//   tool(fn, { name?, description?, parameters? })          fn receives one args object
//   await workpool(agentName?, { name, context, tools })     -> WorkPool { name, agent, limit, push, status, peek, close }
//   await agent(prompt, { agent, label, schema, schemaMode, isolated, apply, merge, tools })
//   await wait(handles, { timeout, raiseErrors })
//   completion(prompt, { model, system, schema })
// A name defined in BOTH kernels is an error — if you loaded workpool-lint.py, call tool.undefine("lint") there first.

import { readFileSync } from "fs";

tool(
  ({ path }) => {
    const src = readFileSync(path, "utf8");
    const out = [];
    src.split("\n").forEach((line, i) => {
      if (line !== line.trimEnd()) out.push(`${path}:${i + 1}: trailing whitespace`);
    });
    if (src.length && !src.endsWith("\n")) out.push(`${path}:${src.split("\n").length}: missing final newline`);
    return out; // [] = clean
  },
  {
    name: "lint",
    description: "Trailing-whitespace / final-newline lint. Returns 'path:line: message' rows; [] = clean.",
    parameters: { type: "object", required: ["path"], properties: { path: { type: "string", description: "project-relative file" } } },
  },
);

globalThis.runPool = async function runPool(files, name = "lintfix") {
  const pool = await workpool("sonic", {
    name,
    context:
      "omp-course-lab. One file per item. Call the `lint` tool, fix ONLY what it reports, call `lint` again until it returns []. " +
      "Touch no other file. Answer each item with yield({ key, data: { file, before, after } }).",
    tools: ["lint"],
  });
  const ids = await pool.push(...files.map((f) => `Fix lint findings in ${f}.`));
  display({ pool: pool.name, limit: pool.limit, items: ids, status: await pool.status() });
  return pool; // no pool.wait(): results auto-deliver; the aggregate job is named after the pool
};

// Single-agent variant with a typed result and a barrier:
globalThis.scoutFlagged = async function scoutFlagged(files) {
  const h = await agent("Call `lint` on each file and return only the ones with findings:\n" + files.join("\n"), {
    agent: "scout",
    tools: ["lint"],
    schema: { type: "object", required: ["files"], properties: { files: { type: "array", items: { type: "string" } } } },
  });
  const [result] = await wait([h], { timeout: 600 });
  return result.files;
};

display(tool.defined());
