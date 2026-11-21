"""Gate: every Hub link uses blob/<pinned tag>/ and docs/hub-pin.md is well formed."""

from __future__ import annotations

import re
from pathlib import Path

from _common import HUB_REPO_URL, main_for, pinned, read, text_files

LINK = re.compile(re.escape(HUB_REPO_URL) + r"/(blob|tree|raw)/([^/\s)>\"'`]+)/")


def scan(root: Path) -> list[str]:
    try:
        tag, _sha = pinned(root)
    except (ValueError, FileNotFoundError) as exc:
        return [f"docs/hub-pin.md: {exc}"]
    problems = []
    for rel in text_files(root):
        for n, line in enumerate(read(root, rel).splitlines(), 1):
            for m in LINK.finditer(line):
                if m.group(2) != tag:
                    problems.append(f"{rel}:{n}: Hub link uses '{m.group(2)}', pinned tag is '{tag}'")
    return problems


if __name__ == "__main__":
    main_for("check_hub_pin", scan)
