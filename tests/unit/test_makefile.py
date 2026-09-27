"""The freeze checklist is code (weekly W1 task 2). Stubs must fail loudly."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# r2.1 §13.1 and §13.2, in order. Dropping a step from the Makefile must fail this test.
R21_FREEZE = [
    "evidence-load-bearing",
    "source-archive-verify",
    "test",
    "pilot-report",
    "break-report",
    "power-report",
    "universe-verify",
    "xnas-cost-decision",
    "manifest-verify",
    "qc-report",
    "replication-diagnostic",
    "preevent-report",
    "prereg-check",
    "freeze-archive",
]
R21_RELEASE = [
    "permissions-check",
    "attribution-check",
    "public-data-scan",
    "release-docs",
    "release-bundle",
]


def make_var(name: str) -> list[str]:
    """Read a Makefile variable by feeding make a one-line helper rule on stdin."""
    result = subprocess.run(
        ["make", "-s", "--no-print-directory", "-f", "Makefile", "-f", "-", f"print-{name}"],
        input="print-%:\n\t@echo $($*)\n",
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=True,
    )
    return result.stdout.split()


def test_freeze_and_release_steps_match_r21() -> None:
    assert make_var("FREEZE_STEPS") == R21_FREEZE
    assert make_var("RELEASE_STEPS") == R21_RELEASE


@pytest.mark.parametrize(
    "target", R21_FREEZE + R21_RELEASE + ["freeze-required", "release-required"]
)
def test_every_target_exists(target: str) -> None:
    dry = subprocess.run(
        ["make", "-n", "--no-print-directory", target], cwd=ROOT, capture_output=True
    )
    assert dry.returncode == 0, dry.stderr


def test_stubs_fail_loudly() -> None:
    stubs = make_var("STUBS")
    assert stubs and "test" not in stubs
    for target in stubs:
        result = subprocess.run(
            ["make", "--no-print-directory", target], cwd=ROOT, capture_output=True, text=True
        )
        assert result.returncode != 0, target
        assert f"NOT IMPLEMENTED: {target}" in result.stderr
