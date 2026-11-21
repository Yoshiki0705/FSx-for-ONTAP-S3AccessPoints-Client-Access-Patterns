"""Negative and positive tests for every gate. Each gate must fail on a bad input."""

from __future__ import annotations

import unittest

from helpers import PB_SHA, PLAYBOOK, SP, TAG, tree

import check_pins
import check_pins_exist
import check_make_targets
import check_markdown
import check_matrix
import check_naming
import check_parity
import check_public_safety

# Bad inputs are assembled from pieces so this file does not trip the gates itself.
FSXN = "FS" + "xN"
BARE = "FS" + "x ONTAP"
S3AP = "S3" + " AP"
WF = "Workload" + " Factory"
BX = "Blue" + "XP"


class Pins(unittest.TestCase):
    def test_good(self):
        r = tree({"a.md": f"{SP}/blob/{TAG}/docs/x.md\n{PLAYBOOK}/blob/{PB_SHA}/docs/y.md\n"})
        self.assertEqual(check_pins.scan(r), [])

    def test_serverless_blob_main_fails(self):
        r = tree({"a.md": f"{SP}/blob/main/docs/x.md\n"})
        self.assertTrue(check_pins.scan(r))

    def test_serverless_other_tag_fails(self):
        r = tree({"a.md": f"{SP}/blob/v9.9.9/docs/x.md\n"})
        self.assertTrue(check_pins.scan(r))

    def test_playbook_blob_main_fails(self):
        r = tree({"a.md": f"{PLAYBOOK}/blob/main/README.md\n"})
        self.assertTrue(check_pins.scan(r))

    def test_playbook_other_sha_fails(self):
        r = tree({"a.md": f"{PLAYBOOK}/blob/{'c' * 40}/README.md\n"})
        self.assertTrue(check_pins.scan(r))

    def test_playbook_short_sha_fails(self):
        r = tree({"a.md": f"{PLAYBOOK}/blob/{PB_SHA[:12]}/README.md\n"})
        self.assertTrue(check_pins.scan(r))

    def test_tag_on_wrong_repo_fails(self):
        r = tree({"a.md": f"{PLAYBOOK}/blob/{TAG}/README.md\n"})
        self.assertTrue(check_pins.scan(r))

    def test_malformed_pin_fails(self):
        r = tree({"docs/reference-pins.md": "Pinned tag: v1\n"}, with_pin=False)
        self.assertTrue(check_pins.scan(r))

    def test_missing_playbook_pin_fails(self):
        body = f"Serverless-Patterns pinned tag: `{TAG}`\nServerless-Patterns pinned commit: `{'a' * 40}`\n"
        r = tree({"docs/reference-pins.md": body}, with_pin=False)
        self.assertTrue(check_pins.scan(r))

    def test_missing_pin_fails(self):
        self.assertTrue(check_pins.scan(tree({"a.md": "x\n"}, with_pin=False)))

    def test_link_in_yaml_is_scanned(self):
        r = tree({".github/workflows/x.yml": f"# {PLAYBOOK}/blob/main/a\n"})
        self.assertTrue(check_pins.scan(r))

    def test_issue_link_is_not_a_pinned_ref(self):
        r = tree({"a.md": f"{PLAYBOOK}/issues/new?template=cross-repo-finding.yml\n"})
        self.assertEqual(check_pins.scan(r), [])


class Naming(unittest.TestCase):
    def test_each_forbidden_term_fails(self):
        for bad in (FSXN, BARE, f"{S3AP}s", WF, BX, "NetApp" + " Console", "Amazon FS" + "x"):
            with self.subTest(bad=bad):
                self.assertTrue(check_naming.scan(tree({"a.md": f"text {bad} text\n"})))

    def test_good_forms_pass(self):
        ok = "Amazon FSx for NetApp ONTAP, FSx for ONTAP, S3 Access Points, FSx-for-ONTAP-S3AccessPoints\n"
        self.assertEqual(check_naming.scan(tree({"a.md": ok})), [])

    def test_allow_marker(self):
        r = tree({"a.md": f"title {FSXN} <!-- allow:naming -->\n"})
        self.assertEqual(check_naming.scan(r), [])


class PublicSafety(unittest.TestCase):
    def bad(self, text):
        return check_public_safety.scan(tree({"a.md": text + "\n"}))

    def test_bad_inputs_fail(self):
        # Assembled at run time so that the source holds no literal that looks like a real identifier.
        samples = [
            "account " + "1234" + "5678" + "9013",
            "ip " + ".".join(["192", "168", "1", "5"]),
            "ip " + ".".join(["8", "8", "8", "8"]),
            "mail someone" + "@" + "corp.test",
            "id fs-" + "0a1b2c3d" + "4e5f60718",
            "alias real-bucket-ext-" + "s3alias",
            "case " + "123" + "4567",
            "path /" + "Users" + "/somebody/x",
        ]
        for s in samples:
            with self.subTest(s=s):
                self.assertTrue(self.bad(s))

    def test_placeholders_pass(self):
        ok = " ".join(
            [
                "123456" + "789012",
                "1" * 12,
                "1111" + "2222" + "3333",
                "987654" + "321098",
                ".".join(["203", "0", "113", "9"]),
                ".".join(["198", "51", "100", "2"]),
                "10.0.1.0/24",
                "10.0.0.0/16",
                "user" + "@" + "example.com",
                "fs-" + "0123456789" + "abcdef0",
                "example-ap-ext-" + "s3alias",
                "127.0.0.1",
            ]
        )
        self.assertEqual(self.bad(ok), [])

    def test_allow_marker(self):
        self.assertEqual(self.bad(".".join(["8"] * 4) + " allow:safety"), [])


class Parity(unittest.TestCase):
    def test_pair_ok(self):
        r = tree(
            {
                "docs/a.md": "# T\n\n## A\n\n| x | y |\n|---|---|\n",
                "docs/a.en.md": "# T\n\n## A\n\n| x | y |\n|---|---|\n",
            }
        )
        self.assertEqual(check_parity.scan(r), [])

    def test_missing_pair_fails(self):
        self.assertTrue(check_parity.scan(tree({"docs/a.md": "# T\n"})))
        self.assertTrue(check_parity.scan(tree({"docs/a.en.md": "# T\n"})))

    def test_heading_count_fails(self):
        r = tree({"docs/a.md": "# T\n## A\n", "docs/a.en.md": "# T\n"})
        self.assertTrue(check_parity.scan(r))

    def test_table_columns_fail(self):
        r = tree(
            {
                "docs/a.md": "# T\n\n| x | y |\n|---|---|\n",
                "docs/a.en.md": "# T\n\n| x | y | z |\n|---|---|---|\n",
            }
        )
        self.assertTrue(check_parity.scan(r))

    def test_note_count_fails(self):
        r = tree({"docs/a.md": "# T\n\n> note\n", "docs/a.en.md": "# T\n"})
        self.assertTrue(check_parity.scan(r))

    def test_exempt_needs_no_pair(self):
        self.assertEqual(check_parity.scan(tree({"AGENTS.md": "# A\n", "docs/agent/x.md": "# A\n"})), [])


MATRIX_HEAD = "| Tool | List | Get | Put | Multipart | Delete | Mount | Date | Pinned Playbook commit | Source |\n|---|---|---|---|---|---|---|---|---|---|\n"


def row(cells):
    return "| t | " + " | ".join(cells) + " | - | - | - |\n"


class Matrix(unittest.TestCase):
    def run_text(self, body):
        return check_matrix.scan_text("m.md", MATRIX_HEAD + body, PB_SHA[:12])

    def test_all_candidate_ok(self):
        p, stale, rows = self.run_text(row(["C"] * 6))
        self.assertEqual((p, stale, rows), ([], 0, 1))

    def test_candidate_with_number_fails(self):
        p, _, _ = self.run_text(row(["C 5 GiB"] + ["C"] * 5))
        self.assertTrue(p)

    def test_measured_without_link_fails(self):
        p, _, _ = self.run_text(row(["M"] + ["C"] * 5))
        self.assertTrue(p)

    def test_documented_without_url_fails(self):
        p, _, _ = self.run_text(row(["D 2026-01-01"] + ["C"] * 5))
        self.assertTrue(p)

    def test_documented_ok_and_stale_count(self):
        cells = ["D https://example.com/doc 2026-01-01"] + ["C"] * 5
        p, stale, _ = self.run_text(row(cells))
        self.assertEqual((p, stale), ([], 1))

    def test_unknown_cell_fails(self):
        p, _, _ = self.run_text(row(["maybe"] + ["C"] * 5))
        self.assertTrue(p)


class MakeTargets(unittest.TestCase):
    MK = ".PHONY: a b\na:\n\ttrue\nb:\n\ttrue\n"

    def test_ok(self):
        r = tree({"Makefile": self.MK, "AGENTS.md": "`make a`\n```\nmake b\n```\n"})
        self.assertEqual(check_make_targets.scan(r), [])

    def test_missing_target_fails(self):
        r = tree({"Makefile": self.MK, "AGENTS.md": "run `make nope`\n"})
        self.assertTrue(check_make_targets.scan(r))

    def test_missing_target_in_fence_fails(self):
        r = tree({"Makefile": self.MK, "AGENTS.md": "```\nmake nope\n```\n"})
        self.assertTrue(check_make_targets.scan(r))

    def test_not_phony_fails(self):
        r = tree({"Makefile": ".PHONY: a\na:\n\ttrue\nb:\n\ttrue\n"})
        self.assertTrue(check_make_targets.scan(r))

    def test_prose_make_is_ignored(self):
        r = tree({"Makefile": self.MK, "AGENTS.md": "make sure to read\n"})
        self.assertEqual(check_make_targets.scan(r), [])


class Markdown(unittest.TestCase):
    def test_unbalanced_fence_fails(self):
        self.assertTrue(check_markdown.scan(tree({"a.md": "```\nx\n"})))

    def test_no_final_newline_fails(self):
        self.assertTrue(check_markdown.scan(tree({"a.md": "x"})))

    def test_ja_verb_heading_fails(self):
        self.assertTrue(check_markdown.scan(tree({"a.md": "# 題\n\n## 設定を確認する\n"})))

    def test_ja_noun_heading_ok(self):
        self.assertEqual(check_markdown.scan(tree({"a.md": "# 題\n\n## 設定の確認手順\n"})), [])

    def test_en_heading_not_checked(self):
        self.assertEqual(check_markdown.scan(tree({"a.en.md": "# T\n\n## Check the setting\n"})), [])


class PinsExist(unittest.TestCase):
    def test_peeled_wins(self):
        out = "1111\trefs/tags/t\n2222\trefs/tags/t^{}\n"
        self.assertEqual(check_pins_exist.resolve(out, "t"), "2222")

    def test_missing_is_none(self):
        self.assertIsNone(check_pins_exist.resolve("1111\trefs/tags/other\n", "t"))


if __name__ == "__main__":
    unittest.main()
