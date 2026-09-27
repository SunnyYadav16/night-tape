"""Re-hash every manifest entry and find files the manifest does not know about."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from night_tape.evidence.manifest import MANIFEST, read, sha256_file

_IGNORED = {MANIFEST, ".DS_Store"}


@dataclass(frozen=True)
class Report:
    missing: list[str]
    mismatched: list[str]
    orphans: list[str]
    unarchived_sources: list[str]

    @property
    def ok(self) -> bool:
        return not (self.missing or self.mismatched or self.orphans or self.unarchived_sources)


def verify(evidence_dir: Path, required_source_ids: Iterable[str] = ()) -> Report:
    root = evidence_dir.parent
    entries = read(evidence_dir)
    known: set[Path] = set()
    missing: list[str] = []
    mismatched: list[str] = []
    for e in entries:
        path = root / e.local_path
        known.add(path.resolve())
        if not path.is_file():
            missing.append(e.local_path)
        elif sha256_file(path) != e.sha256:
            mismatched.append(e.local_path)
    files = evidence_dir.rglob("*") if evidence_dir.exists() else iter(())
    orphans = sorted(
        str(p.relative_to(root))
        for p in files
        if p.is_file() and p.name not in _IGNORED and p.resolve() not in known
    )
    archived = {e.source_id for e in entries}
    unarchived = sorted(set(required_source_ids) - archived)
    return Report(missing, mismatched, orphans, unarchived)
