"""Manual gate (network): the pinned Hub tag exists remotely and points at the recorded commit.

Not part of `make drift`; run with `make drift-hub` (see docs/hub-pin.md).
"""

from __future__ import annotations

import subprocess
import sys

from _common import HUB_REPO_URL, ROOT, pinned


def resolve(ls_remote_output: str, tag: str) -> str | None:
    """Commit SHA for the tag from `git ls-remote --tags` output (peeled entry wins)."""
    direct = peeled = None
    for line in ls_remote_output.splitlines():
        sha, _, ref = line.partition("\t")
        if ref == f"refs/tags/{tag}":
            direct = sha
        elif ref == f"refs/tags/{tag}^{{}}":
            peeled = sha
    return peeled or direct


def main() -> int:
    tag, sha = pinned(ROOT)
    out = subprocess.run(
        ["git", "ls-remote", "--tags", f"https://{HUB_REPO_URL}.git", f"refs/tags/{tag}*"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        print(f"check_hub_tag_exists: git ls-remote failed: {out.stderr.strip()}")
        return 1
    remote = resolve(out.stdout, tag)
    if remote is None:
        print(f"check_hub_tag_exists: tag {tag} not found on the Hub remote")
        return 1
    if remote != sha:
        print(f"check_hub_tag_exists: tag {tag} now points at {remote}, recorded {sha}")
        return 1
    print(f"check_hub_tag_exists: ok ({tag} -> {sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
