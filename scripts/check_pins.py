"""Gate: every pinned link uses the pinned ref, and docs/reference-pins.md is well formed.

Playbook links must use blob/<pinned commit SHA>/ (the Playbook publishes no release tags).
Serverless-Patterns links must use blob/<pinned release tag>/. `blob/main/` is never allowed.
"""

from __future__ import annotations

import re
from pathlib import Path

from _common import PINS_FILE, PLAYBOOK_REPO_URL, SERVERLESS_REPO_URL, main_for, pinned, read, text_files


def link_pattern(repo_url: str) -> re.Pattern[str]:
    return re.compile(re.escape(repo_url) + r"/(blob|tree|raw)/([^/\s)>\"'`]+)/")


PLAYBOOK_LINK = link_pattern(PLAYBOOK_REPO_URL)
SERVERLESS_LINK = link_pattern(SERVERLESS_REPO_URL)


def scan(root: Path) -> list[str]:
    try:
        pins = pinned(root)
    except (ValueError, FileNotFoundError) as exc:
        return [f"{PINS_FILE}: {exc}"]
    expected = (
        ("Playbook", PLAYBOOK_LINK, pins.playbook_sha),
        ("Serverless-Patterns", SERVERLESS_LINK, pins.serverless_tag),
    )
    problems = []
    for rel in text_files(root):
        for n, line in enumerate(read(root, rel).splitlines(), 1):
            for name, pattern, ref in expected:
                for m in pattern.finditer(line):
                    if m.group(2) != ref:
                        problems.append(f"{rel}:{n}: {name} link uses '{m.group(2)}', pinned ref is '{ref}'")
    return problems


if __name__ == "__main__":
    main_for("check_pins", scan)
