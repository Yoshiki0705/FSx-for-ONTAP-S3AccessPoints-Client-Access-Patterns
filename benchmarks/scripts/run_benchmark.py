"""Benchmark runner scaffold. Dry run by default; it never connects to a file system.

Real execution can cost money and needs the owner's approval first (see benchmarks/README.md).
It is deliberately not implemented here: --execute only explains what is missing.
"""

from __future__ import annotations

import argparse
import sys

ENV_FIELDS = (
    "benchmark_run_id",
    "measured_on (JST)",
    "region",
    "FSx for ONTAP layout and throughput capacity",
    "ONTAP version",
    "S3 Access Points settings (no alias)",
    "client host and network bandwidth",
    "tool and version",
    "object size",
    "parallelism",
    "repetitions and aggregation",
    "measurement class (sample / production estimate)",
    "result with units",
    "reproduction command",
    "cleanup performed",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tool", default="<tool>")
    ap.add_argument("--scenario", default="<scenario>")
    ap.add_argument("--dry-run", action="store_true", default=True, help="print the plan only (default)")
    ap.add_argument("--execute", action="store_true", help="opt in to a real run (not implemented)")
    args = ap.parse_args(argv)
    if args.execute:
        print("Real execution is not implemented here. Get the owner approval first.", file=sys.stderr)
        return 2
    print(f"DRY RUN: would measure tool={args.tool} scenario={args.scenario}. No connection is made.")
    print("A record must fill every environment field before it is published:")
    for field in ENV_FIELDS:
        print(f"  - {field}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
