"""Manual gate (network): the pinned refs exist remotely and match the recorded values.

Not part of `make drift`; run with `make drift-pins` (see docs/reference-pins.md).
Serverless-Patterns: the release tag must still point at the recorded commit.
Playbook: the recorded commit must exist (the Playbook publishes no release tags).
"""

from __future__ import annotations

import subprocess
import sys
import urllib.error
import urllib.request

from _common import PLAYBOOK_REPO_URL, ROOT, SERVERLESS_REPO_URL, pinned


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


def commit_url(repo_url: str, sha: str) -> str:
    return f"https://{repo_url}/commit/{sha}"


def commit_exists(repo_url: str, sha: str) -> bool:
    req = urllib.request.Request(commit_url(repo_url, sha), method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310  (fixed https URL)
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise


def main() -> int:
    pins = pinned(ROOT)
    out = subprocess.run(
        ["git", "ls-remote", "--tags", f"https://{SERVERLESS_REPO_URL}.git", f"refs/tags/{pins.serverless_tag}*"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        print(f"check_pins_exist: git ls-remote failed: {out.stderr.strip()}")
        return 1
    remote = resolve(out.stdout, pins.serverless_tag)
    if remote is None:
        print(f"check_pins_exist: tag {pins.serverless_tag} not found on the Serverless-Patterns remote")
        return 1
    if remote != pins.serverless_sha:
        print(f"check_pins_exist: tag {pins.serverless_tag} now points at {remote}, recorded {pins.serverless_sha}")
        return 1
    try:
        found = commit_exists(PLAYBOOK_REPO_URL, pins.playbook_sha)
    except OSError as exc:
        print(f"check_pins_exist: could not reach the Playbook remote: {exc}")
        return 1
    if not found:
        print(f"check_pins_exist: Playbook commit {pins.playbook_sha} not found")
        return 1
    print(f"check_pins_exist: ok (Serverless-Patterns {pins.serverless_tag} -> {pins.serverless_sha}; Playbook {pins.playbook_sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
