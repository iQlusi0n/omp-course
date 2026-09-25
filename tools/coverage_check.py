#!/usr/bin/env python3
"""Check COURSE-OUTLINE.md Appendix C rows against module content.

For each matrix row, derive probe tokens (backticked identifiers, slash commands,
setting keys) and require that at least one probe appears in the README or
exercises of each module the row assigns. Writes COVERAGE-REPORT.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTLINE = (ROOT / "COURSE-OUTLINE.md").read_text()
MODULES = ROOT / "modules"

STOP = {"and", "the", "on", "off", "opt-in", "default", "family", "tour", "revisited"}


def matrix_rows() -> list[tuple[str, list[int], str]]:
    sec = OUTLINE.split("## Appendix C")[1].split("**Explicitly out of scope**")[0]
    rows = []
    for line in sec.splitlines():
        if not line.startswith("|") or line.startswith("| Feature") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in re.split(r"\|(?=(?:[^`]*`[^`]*`)*[^`]*$)", line.strip("|"))]
        feat, mods, default = cells
        mod_nums = [int(m) for m in re.findall(r"\d+", mods)]
        rows.append((feat, mod_nums, default))
    return rows


def probes(feature: str) -> set[str]:
    toks = set(re.findall(r"`([^`]+)`", feature))
    plain = re.sub(r"`[^`]+`", " ", feature)
    toks |= {t for t in re.findall(r"[A-Za-z][A-Za-z0-9_./:-]{3,}", plain) if t.lower() not in STOP}
    out = set()
    for t in toks:
        t = t.strip("/`").lower()
        for part in re.split(r"[/,]", t):
            part = part.strip().strip("`")
            if len(part) >= 3 and part not in STOP:
                out.add(part)
    return out


def module_text(n: int) -> str | None:
    dirs = sorted(MODULES.glob(f"M{n:02d}-*"))
    if not dirs:
        return None
    text = ""
    for name in ("README.md", "exercises.md", "cheatsheet.md"):
        p = dirs[0] / name
        if p.exists():
            text += p.read_text().lower()
    return text


def main() -> int:
    rows = matrix_rows()
    report = ["# Coverage report", "", "Appendix C rows checked against `modules/*/{README,exercises,cheatsheet}.md`.", ""]
    missing = 0
    report.append("| Feature | Module | Status |")
    report.append("|---|---|---|")
    for feat, mods, _ in rows:
        for n in mods:
            text = module_text(n)
            if text is None:
                status = "MODULE MISSING"
                missing += 1
            else:
                ps = probes(feat)
                hits = [p for p in ps if p in text]
                if hits:
                    status = "ok"
                else:
                    status = f"NOT FOUND (probes: {', '.join(sorted(ps))})"
                    missing += 1
            report.append(f"| {feat} | M{n:02d} | {status} |")
    report.append("")
    report.append(f"Rows checked: {sum(len(m) for _, m, _ in rows)}; gaps: {missing}")
    (ROOT / "COVERAGE-REPORT.md").write_text("\n".join(report) + "\n")
    print(report[-1])
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
