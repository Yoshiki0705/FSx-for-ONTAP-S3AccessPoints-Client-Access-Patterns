"""Gate: compatibility matrix cells follow the confirmation levels (C / D / M).

C (candidate): bare 'C', no numbers.  D (documented): official URL and a date.
M (measured): a Markdown link to the record.  '-' means not applicable.
Rows whose Hub tag differs from the pin are counted as stale (a warning, not a failure).
"""

from __future__ import annotations

import re

from _common import lines_outside_fences, pinned, read, text_files

MATRIX_GLOB_PREFIX = "docs/compatibility-matrix"
LEVEL_COLS = range(1, 7)  # list, get, put, multipart, delete, mount
TAG_COL = 8


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def scan_text(rel: str, text: str, tag: str) -> tuple[list[str], int, int]:
    problems, stale, rows = [], 0, 0
    in_matrix = False
    for n, line in lines_outside_fences(text):
        if not line.lstrip().startswith("|"):
            in_matrix = False
            continue
        c = cells(line)
        if c and c[0] in ("Tool", "ツール"):
            in_matrix = True
            continue
        if not in_matrix or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        rows += 1
        used = False
        for i in LEVEL_COLS:
            v = c[i] if i < len(c) else ""
            if v == "-":
                continue
            kind = v[:1]
            if kind == "C":
                if v != "C":
                    problems.append(f"{rel}:{n}: candidate cell must be exactly 'C' (got '{v}')")
            elif kind == "D":
                used = True
                if not (re.search(r"https?://", v) and re.search(r"\d{4}-\d{2}-\d{2}", v)):
                    problems.append(f"{rel}:{n}: documented cell needs an official URL and a date")
            elif kind == "M":
                used = True
                if not re.search(r"\]\([^)]+\)", v):
                    problems.append(f"{rel}:{n}: measured cell needs a link to its record")
            else:
                problems.append(f"{rel}:{n}: cell must start with C, D, M or be '-' (got '{v}')")
        if used and (len(c) <= TAG_COL or c[TAG_COL] != tag):
            stale += 1
    return problems, stale, rows


def main() -> int:
    from _common import ROOT

    tag, _ = pinned(ROOT)
    problems, stale, rows = [], 0, 0
    for rel in text_files(ROOT):
        if rel.startswith(MATRIX_GLOB_PREFIX) and rel.endswith(".md"):
            p, s, r = scan_text(rel, read(ROOT, rel), tag)
            problems += p
            stale += s
            rows += r
    if rows == 0:
        problems.append("no matrix rows found (header 'Tool' / 'ツール' missing?)")
    print(f"check_matrix: {rows} row(s), {stale} stale")
    for p in problems:
        print(f"  {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
