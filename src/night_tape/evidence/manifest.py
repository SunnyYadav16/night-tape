"""Append-only evidence manifest. One JSON object per line in evidence/manifest.jsonl.

Every capture path (HTTP, EDGAR, render, manual) writes through store(). A snapshot file is
never overwritten; a changed source becomes a new file and a new line.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

MANIFEST = "manifest.jsonl"
METHODS = ("http", "edgar", "render-html", "render-pdf", "manual")


@dataclass(frozen=True)
class Entry:
    source_id: str
    source_class: str
    canonical_url: str
    retrieved_at_utc: str
    local_path: str  # relative to evidence_dir.parent, e.g. "evidence/VENDOR_DOC/x/..."
    sha256: str
    content_type: str
    method: str
    published_or_filed_at: str | None = None
    edgar_accession: str | None = None
    supersedes: str | None = None
    notes: str | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(evidence_dir: Path) -> list[Entry]:
    path = evidence_dir / MANIFEST
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [Entry(**json.loads(line)) for line in lines if line.strip()]


def store(
    evidence_dir: Path,
    data: bytes,
    *,
    source_id: str,
    source_class: str,
    canonical_url: str,
    content_type: str,
    method: str,
    filename: str,
    subdir: str | None = None,
    edgar_accession: str | None = None,
    published_or_filed_at: str | None = None,
    supersedes: str | None = None,
    notes: str | None = None,
) -> tuple[Entry, bool]:
    """Write `data` as a new snapshot. Returns (entry, created); created=False if unchanged."""
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}")
    digest = hashlib.sha256(data).hexdigest()
    previous = [
        e for e in read(evidence_dir) if (e.canonical_url, e.method) == (canonical_url, method)
    ]
    if previous and previous[-1].sha256 == digest:
        return previous[-1], False

    now = datetime.now(UTC)
    folder = evidence_dir / source_class / source_id
    if subdir:
        folder = folder / subdir
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    target = folder / f"{now:%Y%m%dT%H%M%SZ}-{digest[:12]}-{safe_name}"
    if target.exists():
        raise FileExistsError(target)  # never overwrite evidence
    folder.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    part.write_bytes(data)
    part.replace(target)  # the manifest line is written only after the file is complete

    entry = Entry(
        source_id=source_id,
        source_class=source_class,
        canonical_url=canonical_url,
        retrieved_at_utc=now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        local_path=str(target.relative_to(evidence_dir.parent)),
        sha256=digest,
        content_type=content_type,
        method=method,
        published_or_filed_at=published_or_filed_at,
        edgar_accession=edgar_accession,
        supersedes=supersedes,
        notes=notes,
    )
    with (evidence_dir / MANIFEST).open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
    return entry, True
