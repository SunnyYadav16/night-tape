"""Load-bearing claims that would block the freeze (r2.1 §6.2 freeze rule)."""

from __future__ import annotations

from night_tape.registry.load import Registry

OK_STATUSES = {"VERIFIED", "CONTINGENCY"}


def load_bearing_gaps(reg: Registry, archived_sha256: set[str]) -> list[str]:
    gaps: list[str] = []
    for cid, c in sorted(reg.claims.items()):
        if not c["load_bearing"]:
            continue
        if c["status"] not in OK_STATUSES:
            gaps.append(f"{cid}: status {c['status']}")
        elif c["status"] == "VERIFIED" and c["sha256"] not in archived_sha256:
            gaps.append(
                f"{cid}: VERIFIED but sha256 {c['sha256'][:12]}... not in evidence manifest"
            )
    return gaps
