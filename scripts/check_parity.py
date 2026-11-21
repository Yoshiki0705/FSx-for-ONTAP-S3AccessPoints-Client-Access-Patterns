"""Gate: ja/en document pairs (X.md and X.en.md) have the same structure."""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path

from _common import lines_outside_fences, main_for, read, text_files

# Markdown files that have no ja/en pair by design. Anything else without a pair fails,
# so a new unpaired document forces a decision here.
EXEMPT = (
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "docs/hub-pin.md",
    "docs/agent/*",
    "drafts/*",
    ".kiro/*",
    ".github/*",
)


def exempt(rel: str) -> bool:
    return any(fnmatch(rel, pat) for pat in EXEMPT)


def pair_of(rel: str) -> str:
    return rel[:-6] + ".md" if rel.endswith(".en.md") else rel[:-3] + ".en.md"


def shape(text: str) -> dict:
    headings, tables, notes = [], [], 0
    in_table = in_note = False
    for _n, line in lines_outside_fences(text):
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            headings.append(len(m.group(1)))
        if line.lstrip().startswith("|"):
            if not in_table:
                tables.append(line.count("|") - 1)
            in_table = True
        else:
            in_table = False
        if line.startswith(">"):
            if not in_note:
                notes += 1
            in_note = True
        else:
            in_note = False
    fences = sum(1 for ln in text.splitlines() if re.match(r"^\s*(```|~~~)", ln)) // 2
    return {"heading levels": headings, "table columns": tables, "notes": notes, "code blocks": fences}


def scan(root: Path) -> list[str]:
    files = {f for f in text_files(root) if f.endswith(".md") and not exempt(f)}
    problems = []
    for rel in sorted(files):
        other = pair_of(rel)
        if other not in files:
            problems.append(f"{rel}: no pair {other}")
            continue
        if rel.endswith(".en.md"):
            continue
        a, b = shape(read(root, rel)), shape(read(root, other))
        for key in a:
            if a[key] != b[key]:
                problems.append(f"{rel} vs {other}: {key} differ: {a[key]} / {b[key]}")
    return problems


if __name__ == "__main__":
    main_for("check_parity", scan)
