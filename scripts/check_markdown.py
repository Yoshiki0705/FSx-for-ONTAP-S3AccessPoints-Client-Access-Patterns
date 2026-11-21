"""Gate: basic Markdown structure (balanced fences, final newline, Japanese heading form)."""

from __future__ import annotations

import re
from pathlib import Path

from _common import lines_outside_fences, main_for, read, text_files

KANA = re.compile(r"[\u3040-\u30ff]")
BAD_END = re.compile(r"(ます|ません|です|でした|ください|か|[うくぐすずつぬふぶむるれ])$")
OK_END = re.compile(r"(問い|項目|手順|範囲|一覧|理由|条件|場合|点|扱い|こと|もの|形|型|流れ)$")


def scan(root: Path) -> list[str]:
    problems = []
    for rel in text_files(root):
        if not rel.endswith(".md"):
            continue
        text = read(root, rel)
        if text and not text.endswith("\n"):
            problems.append(f"{rel}: no newline at end of file")
        if sum(1 for ln in text.splitlines() if re.match(r"^\s*(```|~~~)", ln)) % 2:
            problems.append(f"{rel}: unbalanced code fence")
        if rel.endswith(".en.md"):
            continue
        for n, line in lines_outside_fences(text):
            m = re.match(r"^#{2,6}\s+(.*\S)\s*$", line)
            if m and KANA.search(m.group(1)) and BAD_END.search(m.group(1)) and not OK_END.search(m.group(1)):
                problems.append(f"{rel}:{n}: Japanese heading should be a noun phrase: {m.group(1)}")
    return problems


if __name__ == "__main__":
    main_for("check_markdown", scan)
