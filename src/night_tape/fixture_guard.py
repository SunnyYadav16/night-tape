"""Reject any tests/fixtures file whose first line is not `synthetic: true`.

Real BOATS/Databento messages must never enter the repository (licensing, weekly W1).
Runs as a pre-commit hook and, via tests/unit/test_fixture_guard.py, in CI.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

HEADER = "synthetic: true"


def is_synthetic(path: Path) -> bool:
    try:
        with path.open(encoding="utf-8") as f:
            return f.readline().rstrip("\r\n") == HEADER
    except UnicodeDecodeError:
        return False  # binary files (e.g. .dbn.zst) can never carry the header


def main(argv: Sequence[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else list(argv)
    bad = [p for p in paths if not is_synthetic(Path(p))]
    for p in bad:
        print(
            f"{p}: first line must be '{HEADER}' (tests/fixtures is synthetic-only)",
            file=sys.stderr,
        )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
