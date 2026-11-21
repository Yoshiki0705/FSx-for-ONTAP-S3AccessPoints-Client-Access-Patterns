"""Gate: every `make <target>` named in documents exists, and every Makefile target is .PHONY."""

from __future__ import annotations

import re
from pathlib import Path

from _common import main_for, read, text_files

TARGET_DEF = re.compile(r"^([A-Za-z0-9_-]+):(?!=)")
INLINE = re.compile(r"`make\s+(?:-\S+\s+)*([A-Za-z][A-Za-z0-9_-]*)")
FENCED = re.compile(r"^\s*(?:\$\s*)?make\s+(?:-\S+\s+)*([A-Za-z][A-Za-z0-9_-]*)")


def makefile_targets(text: str) -> tuple[set[str], set[str]]:
    targets, phony = set(), set()
    for line in text.splitlines():
        if line.startswith(".PHONY:"):
            phony |= set(line.split(":", 1)[1].split())
        else:
            m = TARGET_DEF.match(line)
            if m:
                targets.add(m.group(1))
    return targets, phony


def referenced(text: str) -> set[str]:
    refs = set(INLINE.findall(text))
    fence = False
    for line in text.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
        elif fence:
            m = FENCED.match(line)
            if m:
                refs.add(m.group(1))
    return refs


def scan(root: Path) -> list[str]:
    if not (root / "Makefile").exists():
        return ["Makefile is missing"]
    targets, phony = makefile_targets(read(root, "Makefile"))
    problems = [f"Makefile: target '{t}' is not in .PHONY" for t in sorted(targets - phony)]
    for rel in text_files(root):
        if rel.endswith(".md"):
            for t in sorted(referenced(read(root, rel)) - targets):
                problems.append(f"{rel}: names `make {t}` but the Makefile has no such target")
    return problems


if __name__ == "__main__":
    main_for("check_make_targets", scan)
