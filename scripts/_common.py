"""Shared helpers for the repository gates (standard library only)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories that are never scanned. Mirrors .gitignore; a coverage test compares
# this walk with `git ls-files` so the two cannot drift apart silently.
EXCLUDE_DIRS = (
    ".git",
    ".kiro/specs",
    ".kiro/skills",
    ".private",
    ".venv",
    "__pycache__",
    ".ruff_cache",
)
TEXT_SUFFIXES = {
    ".md",
    ".yml",
    ".yaml",
    ".py",
    ".sh",
    ".toml",
    ".json",
    ".txt",
    ".cfg",
    ".ini",
    ".svg",
}
TEXT_NAMES = {"Makefile", "LICENSE", ".gitignore", ".gitkeep", "CODEOWNERS"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".pyc"}

HUB_REPO_URL = "github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns"


def _excluded(rel: str) -> bool:
    return any(rel == d or rel.startswith(d + "/") for d in EXCLUDE_DIRS) or any(
        part in {"__pycache__", ".ruff_cache"} for part in rel.split("/")
    )


def list_files(root: Path = ROOT) -> list[str]:
    """Every non-excluded file under root, as sorted posix relative paths."""
    out = []
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            if not _excluded(rel):
                out.append(rel)
    return sorted(out)


def is_text(rel: str) -> bool:
    p = Path(rel)
    return p.suffix in TEXT_SUFFIXES or p.name in TEXT_NAMES


def text_files(root: Path = ROOT) -> list[str]:
    return [f for f in list_files(root) if is_text(f)]


def unknown_files(root: Path = ROOT) -> list[str]:
    """Files that are neither known text nor known binary (a gate would skip them)."""
    return [f for f in list_files(root) if not is_text(f) and Path(f).suffix not in BINARY_SUFFIXES]


def read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def lines_outside_fences(text: str):
    """Yield (lineno, line) for lines that are not inside a code fence (fence lines excluded)."""
    fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
            continue
        if not fence:
            yield n, line


def pinned(root: Path = ROOT) -> tuple[str, str]:
    """Return (tag, sha) from docs/hub-pin.md, or raise ValueError."""
    text = read(root, "docs/hub-pin.md")
    tag = re.search(r"^Pinned tag: `([^`\s]+)`", text, re.M)
    sha = re.search(r"^Pinned commit: `([0-9a-f]{40})`", text, re.M)
    if not tag or not sha:
        raise ValueError("docs/hub-pin.md must contain 'Pinned tag: `<tag>`' and 'Pinned commit: `<40 hex>`'")
    return tag.group(1), sha.group(1)


def report(name: str, problems: list[str]) -> int:
    if problems:
        print(f"{name}: FAILED ({len(problems)} problem(s))")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"{name}: ok")
    return 0


def main_for(name: str, scan) -> None:
    sys.exit(report(name, scan(ROOT)))
