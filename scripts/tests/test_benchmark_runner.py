"""The benchmark runner must stay a dry run: --execute is refused and nothing connects."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from helpers import SCRIPTS

sys.path.insert(0, str(SCRIPTS.parent / "benchmarks" / "scripts"))

import run_benchmark  # noqa: E402


class Runner(unittest.TestCase):
    def test_default_is_dry_run(self):
        self.assertEqual(run_benchmark.main([]), 0)

    def test_execute_is_refused(self):
        self.assertEqual(run_benchmark.main(["--execute"]), 2)

    def test_runner_imports_no_network_or_cloud_libraries(self):
        src = Path(run_benchmark.__file__).read_text(encoding="utf-8")
        for banned in ("import boto3", "import socket", "import urllib", "import requests", "subprocess"):
            self.assertNotIn(banned, src)


if __name__ == "__main__":
    unittest.main()
