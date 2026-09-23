from pathlib import Path

import pytest

from night_tape.fixture_guard import is_synthetic, main

ROOT = Path(__file__).resolve().parents[2]


def test_header_on_first_line_is_accepted(tmp_path: Path) -> None:
    f = tmp_path / "f01.yaml"
    f.write_text("synthetic: true\ntrades: []\n")
    assert is_synthetic(f)


def test_header_anywhere_else_is_rejected(tmp_path: Path) -> None:
    f = tmp_path / "real.yaml"
    f.write_text("trades: []\nsynthetic: true\n")
    assert not is_synthetic(f)


def test_empty_and_binary_files_are_rejected(tmp_path: Path) -> None:
    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    raw = tmp_path / "raw.dbn.zst"
    raw.write_bytes(b"\x28\xb5\x2f\xfd\x00\xff")  # zstd magic: real market data never passes
    assert not is_synthetic(empty)
    assert not is_synthetic(raw)


def test_main_reports_every_bad_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = tmp_path / "good.yaml"
    good.write_text("synthetic: true\n")
    bad = tmp_path / "bad.yaml"
    bad.write_text("x: 1\n")
    assert main([str(good), str(bad)]) == 1
    err = capsys.readouterr().err
    assert "bad.yaml" in err and "good.yaml" not in err


def test_repo_fixture_tree_is_synthetic() -> None:
    fixtures = ROOT / "tests" / "fixtures"
    files = [p for p in fixtures.rglob("*") if p.is_file()] if fixtures.exists() else []
    assert [str(p) for p in files if not is_synthetic(p)] == []
