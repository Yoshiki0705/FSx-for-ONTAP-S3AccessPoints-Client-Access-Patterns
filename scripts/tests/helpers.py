"""Test helpers: build a throwaway tree and put scripts/ on sys.path."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

TAG = "v1.2.3-test"
SHA = "a" * 40  # allow:safety
PB_SHA = "b" * 40  # allow:safety
PIN = (
    f"Playbook pinned commit: `{PB_SHA}`\n"
    f"Serverless-Patterns pinned tag: `{TAG}`\n"
    f"Serverless-Patterns pinned commit: `{SHA}`\n"
)
SP = "https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns"
PLAYBOOK = "https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook"


def tree(files: dict[str, str], with_pin: bool = True) -> Path:
    root = Path(tempfile.mkdtemp())
    if with_pin:
        files = {"docs/reference-pins.md": PIN, **files}
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return root
