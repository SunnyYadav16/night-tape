import json
from pathlib import Path
from typing import Any

import pytest

from night_tape.cost import quote, save


class FakeMetadata:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_cost(self, **kw: Any) -> float:
        self.calls.append(("cost", kw))
        return 0.42

    def get_billable_size(self, **kw: Any) -> int:
        self.calls.append(("size", kw))
        return 1234

    def get_record_count(self, **kw: Any) -> int:
        self.calls.append(("count", kw))
        return 56


def make_quote(md: FakeMetadata) -> dict[str, Any]:
    return quote(
        md,
        dataset="OCEA.MEMOIR",
        schema="tbbo",
        symbols=["SPY"],
        start="2026-09-21T00:00:00Z",
        end="2026-09-21T08:00:00Z",
        sdk_version="0.0.test",
    )


def test_one_identical_request_goes_to_all_three_metadata_calls() -> None:
    md = FakeMetadata()
    q = make_quote(md)
    assert [name for name, _ in md.calls] == ["cost", "size", "count"]
    assert all(kw == q["request"] for _, kw in md.calls)
    assert q["request"]["stype_in"] == "raw_symbol"
    assert (q["cost_usd"], q["billable_bytes"], q["record_count"]) == (0.42, 1234, 56)
    assert q["sdk_version"] == "0.0.test" and q["quoted_at_utc"].endswith("Z")


def test_save_writes_json_and_never_overwrites(tmp_path: Path) -> None:
    q = make_quote(FakeMetadata())
    path = save(q, tmp_path)
    assert path.name.endswith("-OCEA.MEMOIR-tbbo.json")
    assert json.loads(path.read_text())["cost_usd"] == 0.42
    with pytest.raises(FileExistsError):
        save(q, tmp_path)
