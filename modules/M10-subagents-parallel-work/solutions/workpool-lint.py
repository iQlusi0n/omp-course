# Module 10 — Lesson 10.5 / exercise G3: lint-fix pass with a kernel @tool + workpool().
# Load into the Python eval kernel:   %load modules/M10-subagents-parallel-work/solutions/workpool-lint.py
# then run:                            run_pool(lab_files())
#
# API shapes copied from omp://tools/eval.md and omp://python-repl.md (omp 18.3.1):
#   @tool / @tool(name=..., description=...)           -> kernel-defined tool for subagents (eval.tools.enabled)
#   workpool(agent=None, *, name=None, context=None, tools=None)
#   pool.push(*items) -> ["<pool>#<seq>", ...]; pool.status(); pool.peek(); pool.close()
#   agent(prompt, *, agent=None, label=None, schema=None, schema_mode=None, isolated=None, apply=None, merge=None, tools=None)
#   wait(handles, timeout=None, raise_errors=True)
#   completion(prompt, *, model="default", system=None, schema=None)
# Stdlib only. Never pushes files under generated/ (RULES.md fixture).

import ast
from pathlib import Path
from typing import Annotated


@tool(description="Stdlib lint: unused imports, trailing whitespace, missing final newline. Returns 'path:line: message' rows; empty list = clean.")
def lint(path: Annotated[str, "project-relative .py file"]) -> list[str]:
    p = Path(path)
    src = p.read_text(encoding="utf-8")
    findings: list[str] = []
    try:
        tree = ast.parse(src, filename=str(p))
    except SyntaxError as e:  # report, don't raise: a raising tool errors the caller, not the kernel
        return [f"{path}:{e.lineno}: syntax error: {e.msg}"]
    imported: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    imported[a.asname or a.name] = node.lineno
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.value.id for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
    }
    exported = set()
    for node in tree.body:  # `__all__ = [...]` re-exports (api/__init__.py fixture)
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                exported |= {c.value for c in node.value.elts if isinstance(c, ast.Constant)}
    for name, line in sorted(imported.items(), key=lambda kv: kv[1]):
        if name not in used and name not in exported and not p.name == "__init__.py":
            findings.append(f"{path}:{line}: unused import '{name}'")
    for i, line in enumerate(src.splitlines(), 1):
        if line != line.rstrip():
            findings.append(f"{path}:{i}: trailing whitespace")
    if src and not src.endswith("\n"):
        findings.append(f"{path}:{len(src.splitlines())}: missing final newline")
    return findings


def lab_files(roots=("api", "cli", "tests")) -> list[str]:
    """Python files eligible for the lint-fix pass (never generated/)."""
    out: list[str] = []
    for r in roots:
        out += sorted(str(p) for p in Path(r).rglob("*.py"))
    return out


def baseline(files: list[str]) -> dict[str, int]:
    return {f: len(lint(f)) for f in files}


def run_pool(files: list[str], name: str = "lintfix"):
    """One keep-alive pool of `sonic` workers; each item = one file. Results auto-deliver;
    the aggregate job is named after the pool. No pool.wait() exists — end the cell and let
    results arrive, or call the zero-argument `wait` tool only when nothing else is left to do."""
    pool = workpool(
        "sonic",
        name=name,
        context=(
            "omp-course-lab, Python 3 stdlib. You fix ONE file per item. Call the `lint` tool on the file, "
            "fix ONLY what it reports (remove unused imports, strip trailing whitespace, add a final newline), "
            "call `lint` again until it returns []. Touch no other file. Do not reformat, rename, or reorder. "
            "Answer each item with yield({key, data: {file, before, after}})."
        ),
        tools=["lint"],
    )
    before = baseline(files)
    ids = pool.push(*[f"Fix lint findings in {f} (currently {before[f]} findings)." for f in files])
    display({"pool": pool.name, "items": ids, "status": pool.status()})
    return pool, before


def report(files: list[str], before: dict[str, int]) -> str:
    """Markdown table for notes/m10.md after the pool drained."""
    rows = ["| file | lint before | lint after |", "|---|---|---|"]
    for f in files:
        rows.append(f"| {f} | {before[f]} | {len(lint(f))} |")
    return "\n".join(rows)


# Optional two-phase variant (Lesson 10.5 guided task): scout first, then a fresh pool.
def two_phase(files: list[str]):
    h = agent(
        "For each listed file call the `lint` tool and return only files with >0 findings.\n" + "\n".join(files),
        agent="scout",
        tools=["lint"],
        schema={"type": "object", "required": ["files"], "properties": {"files": {"type": "array", "items": {"type": "string"}}}},
    )
    flagged = wait([h])[0]["files"]  # parsed because a schema was given
    verdicts = {}
    for f in flagged:
        c = completion(
            f"Findings for {f}:\n" + "\n".join(lint(f)) + "\nIs fixing these trivial (whitespace/imports only) or does it need review?",
            model="smol",
            schema={"type": "object", "required": ["verdict"], "properties": {"verdict": {"enum": ["trivial", "needs review"]}}},
        )
        verdicts[f] = c.wait()["verdict"]
    display({"flagged": flagged, "verdicts": verdicts})
    return run_pool(flagged, name="lintfix2")
