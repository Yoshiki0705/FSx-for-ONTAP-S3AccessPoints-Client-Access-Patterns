"""Coverage tests: the gates see every file, and documents name only real make targets.

A gate that silently skips part of the tree passes while checking nothing, so these tests
enumerate the tree a second way (git) and compare.
"""

from __future__ import annotations

import subprocess
import unittest

from helpers import SCRIPTS  # noqa: F401  (puts scripts/ on sys.path)

import _common
import check_make_targets
import check_parity


class Coverage(unittest.TestCase):
    def test_no_file_type_is_silently_skipped(self):
        self.assertEqual(_common.unknown_files(), [], "add the suffix to TEXT_SUFFIXES or BINARY_SUFFIXES")

    def test_gate_file_list_matches_git(self):
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=_common.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if out.returncode != 0:
            self.skipTest("not a git work tree")
        git_text = {f for f in out.stdout.splitlines() if _common.is_text(f) and (_common.ROOT / f).exists()}
        self.assertEqual(set(_common.text_files()), git_text)

    def test_every_markdown_file_is_paired_or_exempt(self):
        self.assertEqual(check_parity.scan(_common.ROOT), [])

    def test_matrix_documents_exist_for_both_languages(self):
        names = _common.text_files()
        self.assertIn("docs/compatibility-matrix.md", names)
        self.assertIn("docs/compatibility-matrix.en.md", names)

    def test_makefile_declares_documented_targets(self):
        self.assertEqual(check_make_targets.scan(_common.ROOT), [])


if __name__ == "__main__":
    unittest.main()
