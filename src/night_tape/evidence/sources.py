"""The list of load-bearing sources to archive (config/monitoring.yaml) and `sync` over it.

Re-run weekly (weekly §4): unchanged bytes are a no-op, changed bytes become a new snapshot.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from playwright.sync_api import Error as PlaywrightError

from night_tape import contracts
from night_tape.config import load_yaml
from night_tape.evidence import edgar, fetch, manifest, render
from night_tape.evidence.manifest import Entry

METHODS = ("http", "render", "edgar", "manual")
# One bad source must not hide the rest. PlaywrightError covers render timeouts.
_SOURCE_ERRORS = (httpx.HTTPError, PlaywrightError, RuntimeError, OSError)
Stored = list[tuple[Entry, bool]]


@dataclass(frozen=True)
class Source:
    source_id: str
    source_class: str
    method: str
    url: str | None = None
    cik: str | None = None
    form_prefix: str | None = None
    notes: str | None = None


def _check(s: Source) -> None:
    if s.method not in METHODS:
        raise ValueError(f"{s.source_id}: method {s.method!r} not in {METHODS}")
    if s.source_class not in contracts.source_classes():
        raise ValueError(f"{s.source_id}: unknown source_class {s.source_class!r}")
    if s.method == "edgar" and not (s.cik and s.form_prefix):
        raise ValueError(f"{s.source_id}: edgar source needs cik and form_prefix")
    if s.method != "edgar" and not s.url:
        raise ValueError(f"{s.source_id}: {s.method} source needs url")


def load_sources(path: Path) -> list[Source]:
    srcs = [Source(**raw) for raw in load_yaml(path)["sources"]]  # unknown keys → TypeError
    for s in srcs:
        _check(s)
    ids = [s.source_id for s in srcs]
    if dupes := sorted({i for i in ids if ids.count(i) > 1}):
        raise ValueError(f"duplicate source_id {dupes}")
    return srcs


@dataclass
class SyncReport:
    stored: Stored = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    manual_missing: list[str] = field(default_factory=list)


def sync(
    evidence_dir: Path,
    srcs: list[Source],
    client: httpx.Client,
    *,
    render_fn: Callable[..., Stored] = render.render,
    edgar_fn: Callable[..., Stored] = edgar.archive_chain,
    sleep: Callable[[float], None] = time.sleep,
) -> SyncReport:
    report = SyncReport()
    archived = {e.source_id for e in manifest.read(evidence_dir)}
    for s in srcs:
        ids: dict[str, Any] = {"source_id": s.source_id, "source_class": s.source_class}
        try:
            if s.method == "manual":
                if s.source_id not in archived:
                    report.manual_missing.append(s.source_id)
            elif s.method == "http":
                assert s.url is not None
                sleep(edgar.MIN_INTERVAL_S)
                report.stored.append(fetch.fetch(evidence_dir, client, s.url, notes=s.notes, **ids))
            elif s.method == "render":
                report.stored.extend(render_fn(evidence_dir, s.url, notes=s.notes, **ids))
            else:
                report.stored.extend(
                    edgar_fn(
                        evidence_dir,
                        client,
                        cik=s.cik,
                        form_prefix=s.form_prefix,
                        sleep=sleep,
                        **ids,
                    )
                )
        except _SOURCE_ERRORS as exc:
            report.failed.append((s.source_id, f"{type(exc).__name__}: {exc}"))
    return report
