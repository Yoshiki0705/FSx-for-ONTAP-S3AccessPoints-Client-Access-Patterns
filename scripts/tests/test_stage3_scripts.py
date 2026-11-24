"""Stage 3 scripts: a dry run must assemble the real commands, and --execute must refuse unsafe states.

The dry run is the only thing CI can check. A script that only echoed a label would print no
`aws ...` / `mount-s3 ...` line, so assert_real_commands() fails on it (see test_stub_is_caught).
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import SCRIPTS

BENCH = SCRIPTS.parent / "benchmarks"
SCRIPT_DIR = BENCH / "scripts"


# Every test runs with stub cloud CLIs first on PATH. A test that reached a real `aws` once created a
# bucket in a real account, so any call that escapes the dry run now fails and leaves a marker.
STUB_DIR = Path(tempfile.mkdtemp())
CALLED = STUB_DIR / "called"
for tool in ("aws", "s5cmd", "rclone", "mount-s3", "umount", "openssl"):
    stub = STUB_DIR / tool
    stub.write_text(f'#!/bin/sh\necho "{tool} $*" >> "{CALLED}"\nexit 99\n', encoding="utf-8")
    stub.chmod(0o755)


def sh(script: str, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    e = {**os.environ, "PATH": f"{STUB_DIR}:{os.environ['PATH']}", **(env or {})}
    return subprocess.run(
        ["bash", str(SCRIPT_DIR / script), *args],
        capture_output=True,
        text=True,
        env=e,
        timeout=60,
        check=False,
    )


def assert_real_commands(case: unittest.TestCase, output: str, needles: tuple[str, ...]) -> None:
    for needle in needles:
        case.assertIn(needle, output, f"dry run did not assemble a real command containing {needle!r}")


SETUP = (
    "aws s3api create-bucket",
    "aws fsx create-volume",
    "aws fsx create-and-attach-s3-access-point",
    "aws iam create-role",
    "aws iam create-instance-profile",
    "aws ec2 run-instances",
    "Key=Project\\,Value=client-access-patterns",
)
MEASURE = (
    "aws s3api list-objects-v2",
    "aws s3 cp",
    "s5cmd --log debug cp",
    "rclone --config",
    "mount-s3",
    "aws s3api copy-object",
    "--dump headers",
)
TEARDOWN = (
    "aws fsx detach-and-delete-s3-access-point",
    "aws fsx delete-volume",
    "aws ec2 terminate-instances",
    "aws iam delete-role",
    "aws s3api delete-bucket",
    "aws resourcegroupstaggingapi get-resources",
)


class DryRun(unittest.TestCase):
    def test_setup_builds_real_commands(self):
        r = sh("stage3-setup.sh")
        self.assertEqual(r.returncode, 0, r.stderr)
        assert_real_commands(self, r.stdout, SETUP)

    def test_measure_builds_real_commands_for_every_case(self):
        r = sh("stage3-measure.sh", "--case", "all")
        self.assertEqual(r.returncode, 0, r.stderr)
        assert_real_commands(self, r.stdout, MEASURE)

    def test_teardown_builds_real_commands(self):
        r = sh("stage3-teardown.sh")
        self.assertEqual(r.returncode, 0, r.stderr)
        assert_real_commands(self, r.stdout, TEARDOWN)

    def test_export_builds_real_commands(self):
        r = sh("stage3-export-evidence.sh")
        self.assertEqual(r.returncode, 0, r.stderr)
        assert_real_commands(self, r.stdout, ("aws s3 cp", "aws fsx describe-volumes"))

    def test_stub_is_caught(self):
        stub = "echo 'would create the bucket'\necho 'would create the volume'\n"
        with self.assertRaises(AssertionError):
            assert_real_commands(self, stub, SETUP)

    def test_dry_run_never_writes_state(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "state.env"
            sh("stage3-setup.sh", env={"STAGE3_STATE": str(state)})
            self.assertFalse(state.exists())


class NoRealCalls(unittest.TestCase):
    def test_dry_runs_never_call_a_cloud_cli(self):
        CALLED.unlink(missing_ok=True)
        for script, args in (
            ("stage3-setup.sh", ()),
            ("stage3-measure.sh", ("--case", "all")),
            ("stage3-export-evidence.sh", ()),
            ("stage3-teardown.sh", ()),
        ):
            sh(script, *args)
        self.assertFalse(CALLED.exists(), CALLED.read_text(encoding="utf-8") if CALLED.exists() else "")


class Refusals(unittest.TestCase):
    def test_execute_needs_a_config_file(self):
        with tempfile.TemporaryDirectory() as d:
            r = sh("stage3-setup.sh", "--execute", env={"STAGE3_CONFIG": str(Path(d) / "missing.env")})
            self.assertEqual(r.returncode, 2)
            self.assertIn("no config file", r.stderr)

    def test_step_skips_what_the_state_file_records_as_done(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "s.env"
            state.write_text("FOO_DONE=1\n", encoding="utf-8")
            script = (
                f'. "{SCRIPT_DIR}/stage3-lib.sh"; DRY_RUN=0; STATE_FILE="{state}"; '
                "step FOO echo MUST-NOT-RUN; step BAR echo RAN-BAR"
            )
            env = {**os.environ, "PATH": f"{STUB_DIR}:{os.environ['PATH']}"}
            r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env, check=False)
            self.assertIn("skip FOO", r.stdout)
            self.assertNotIn("MUST-NOT-RUN\n", r.stdout.replace("+ echo MUST-NOT-RUN", ""))
            self.assertIn("RAN-BAR", r.stdout)
            self.assertIn("BAR_DONE=1", state.read_text(encoding="utf-8"))

    def test_teardown_refuses_without_exported_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            cfg, state = Path(d) / "c.env", Path(d) / "s.env"
            cfg.write_text("RUN_ID=unit-test-no-evidence\n", encoding="utf-8")
            state.write_text("VOLUME_ID=x\nINSTANCE_ID=x\nROLE_NAME=x\nPROFILE_NAME=x\n", encoding="utf-8")
            r = sh(
                "stage3-teardown.sh", "--execute", env={"STAGE3_CONFIG": str(cfg), "STAGE3_STATE": str(state)}
            )
            self.assertEqual(r.returncode, 2)
            self.assertIn("no exported evidence", r.stderr)


if __name__ == "__main__":
    unittest.main()
