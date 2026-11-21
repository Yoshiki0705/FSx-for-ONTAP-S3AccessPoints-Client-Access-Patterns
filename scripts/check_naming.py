"""Gate: forbidden product names and abbreviations (Playbook naming rule)."""

from __future__ import annotations

import re
from pathlib import Path

from _common import main_for, read, text_files

# Patterns are written so that this file does not match itself.
RULES = [
    (re.compile(r"\bFSxN\b"), "use 'FSx for ONTAP'"),
    (re.compile(r"\bFSx\b(?!\s+for\b|-for-)"), "bare abbreviation: write 'FSx for ONTAP'"),
    (re.compile(r"\bS3 APs?\b"), "write 'S3 Access Points' in full"),
    (re.compile(r"Workload\s+Factory"), "forbidden product name"),
    (re.compile(r"NetApp\s+Console"), "forbidden product name"),
    (re.compile(r"Blue[X]P"), "forbidden product name"),
]
ALLOW = "allow:naming"


def scan(root: Path) -> list[str]:
    problems = []
    for rel in text_files(root):
        for n, line in enumerate(read(root, rel).splitlines(), 1):
            if ALLOW in line:
                continue
            for rx, why in RULES:
                if rx.search(line):
                    problems.append(f"{rel}:{n}: {why}")
    return problems


if __name__ == "__main__":
    main_for("check_naming", scan)
