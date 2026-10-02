#!/usr/bin/env python3
"""Structural checks for the course content. Exit 1 on any failure.

- every module has README.md, exercises.md, cheatsheet.md, BUILD-NOTES.md, demos/, solutions/
- every lesson in a README carries the §1 template fields
- no prose line in README.md/exercises.md exceeds 400 characters (code fences and tables exempt)
- Appendix C coverage matrix is fully covered (delegates to coverage_check.py)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "modules"
REQUIRED_FILES = ("README.md", "exercises.md", "cheatsheet.md", "BUILD-NOTES.md")
REQUIRED_DIRS = ("demos", "solutions")
FIELDS = (
    "**You will be able to:**",
    "**Why this exists:**",
    "**Try it (Walkthrough):**",
    "**Guided task:**",
    "**Stretch:**",
    "**Troubleshooting:**",
    "**Cheat sheet:**",
    "**Source:**",
)
MAX_PROSE = 400


def long_prose_lines(text: str) -> int:
    count = 0
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith("|"):
            continue
        if len(line) > MAX_PROSE:
            count += 1
    return count


def main() -> int:
    problems: list[str] = []
    mods = sorted(p for p in MODULES.iterdir() if p.is_dir() and re.match(r"M\d\d-", p.name))
    if len(mods) != 15:
        problems.append(f"expected 15 modules, found {len(mods)}")
    for d in mods:
        for f in REQUIRED_FILES:
            if not (d / f).is_file():
                problems.append(f"{d.name}: missing {f}")
        for sub in REQUIRED_DIRS:
            if not any((d / sub).glob("*")):
                problems.append(f"{d.name}: empty or missing {sub}/")
        readme = d / "README.md"
        if readme.is_file():
            text = readme.read_text()
            lessons = len(re.findall(r"^## Lesson", text, re.M))
            if lessons == 0:
                problems.append(f"{d.name}: no '## Lesson' headings")
            for field in FIELDS:
                if text.count(field) < lessons:
                    problems.append(f"{d.name}: '{field}' appears {text.count(field)}x for {lessons} lessons")
            if "You will be able:" in text:
                problems.append(f"{d.name}: malformed field 'You will be able:'")
        for f in ("README.md", "exercises.md"):
            p = d / f
            if p.is_file():
                n = long_prose_lines(p.read_text())
                if n:
                    problems.append(f"{d.name}/{f}: {n} prose line(s) > {MAX_PROSE} chars")

    cov = subprocess.run([sys.executable, str(ROOT / "tools" / "coverage_check.py")], capture_output=True, text=True)
    print(cov.stdout.strip())
    if cov.returncode != 0:
        problems.append("coverage_check.py reported gaps (see COVERAGE-REPORT.md)")

    for p in problems:
        print("FAIL:", p)
    print(f"{len(mods)} modules checked; {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
