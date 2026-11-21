"""Gate: nothing that identifies a real account, resource, person, or network."""

from __future__ import annotations

import re
from pathlib import Path

from _common import main_for, read, text_files

ALLOW = "allow:safety"
ACCOUNT = re.compile(r"(?<!\d)\d{12}(?!\d)")
IPV4 = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?![\d]|\.\d)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
RES_ID = re.compile(r"\b(?:fs|fsvol|vol|svm|vpc|subnet|sg|fsap|eni|i)-([0-9a-f]{8,17})\b")
ALIAS = re.compile(r"\b[a-z0-9][a-z0-9-]*-ext-s3alias\b")
CASE = re.compile(r"(?i)\bcase[ #]?\d{5,}|\bDB-I-\d+")
HOME = re.compile(r"/(?:Users|home)/[A-Za-z][\w.-]*")
SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net")
PLACEHOLDER_HEX = "0123456789abcdef0"


def account_ok(s: str) -> bool:
    if len(set(s)) == 1:
        return True
    groups = [s[i : i + 4] for i in range(0, 12, 4)]
    if all(len(set(g)) == 1 for g in groups):
        return True
    d = [int(c) for c in s]
    steps = {(d[i + 1] - d[i]) % 10 for i in range(11)}
    return steps in ({1}, {9})


def ip_ok(ip: str) -> bool:
    o = [int(x) for x in ip.split(".")]
    if any(x > 255 for x in o):
        return True  # not an address (version string etc.)
    return (
        o[:3] in ([203, 0, 113], [198, 51, 100])
        or o[:2] == [10, 0]
        or o[0] in (127, 255)
        or o == [0, 0, 0, 0]
    )


def scan_line(line: str) -> list[str]:
    out = []
    for m in ACCOUNT.finditer(line):
        if not account_ok(m.group()):
            out.append(f"12-digit number outside allowed placeholder shapes: {m.group()}")
    for m in IPV4.finditer(line):
        if not ip_ok(m.group(1)):
            out.append(f"IPv4 address outside placeholder ranges: {m.group(1)}")
    for m in EMAIL.finditer(line):
        if not m.group().lower().endswith(SAFE_EMAIL_DOMAINS):
            out.append(f"email address: {m.group()}")
    for m in RES_ID.finditer(line):
        if m.group(1) != PLACEHOLDER_HEX:
            out.append(f"resource ID that is not the placeholder: {m.group()}")
    for m in ALIAS.finditer(line):
        if not re.search(r"example|placeholder|xxxx", m.group()):
            out.append(f"access point alias: {m.group()}")
    if CASE.search(line):
        out.append("support case or vendor ticket number")
    if HOME.search(line):
        out.append("personal home path")
    return out


def scan(root: Path) -> list[str]:
    problems = []
    for rel in text_files(root):
        for n, line in enumerate(read(root, rel).splitlines(), 1):
            if ALLOW in line:
                continue
            problems += [f"{rel}:{n}: {p}" for p in scan_line(line)]
    return problems


if __name__ == "__main__":
    main_for("check_public_safety", scan)
