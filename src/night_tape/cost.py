"""Record Databento cost, billable size and record count for one request. Never downloads data.

Weekly W1 task 9 baseline; the Week 3 cost guard calls quote() before every pull.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def quote(
    metadata: Any,  # databento.Historical().metadata
    *,
    dataset: str,
    schema: str,
    symbols: list[str],
    start: str,
    end: str,
    sdk_version: str,
    stype_in: str = "raw_symbol",
) -> dict[str, Any]:
    request = {
        "dataset": dataset,
        "schema": schema,
        "symbols": symbols,
        "start": start,
        "end": end,
        "stype_in": stype_in,
    }
    return {
        "request": request,
        "sdk_version": sdk_version,
        "quoted_at_utc": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "cost_usd": float(metadata.get_cost(**request)),
        "billable_bytes": int(metadata.get_billable_size(**request)),
        "record_count": int(metadata.get_record_count(**request)),
    }


def save(doc: dict[str, Any], out_dir: Path) -> Path:
    r = doc["request"]
    path = out_dir / f"{doc['quoted_at_utc'].replace(':', '')}-{r['dataset']}-{r['schema']}.json"
    if path.exists():
        raise FileExistsError(path)
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
