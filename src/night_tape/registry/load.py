"""Load registry/claims.yaml and registry/events.yaml, validate both, check cross-references."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from night_tape import contracts
from night_tape.config import load_yaml

Record = dict[str, Any]


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class Registry:
    claims: dict[str, Record]
    events: dict[str, Record]
    rule_versions: dict[str, Record]


def _index(items: list[Record], key: str, problems: list[str]) -> dict[str, Record]:
    out: dict[str, Record] = {}
    for item in items:
        if item[key] in out:
            problems.append(f"duplicate {key} {item[key]}")
        out[item[key]] = item
    return out


def load(claims_path: Path, events_path: Path) -> Registry:
    claims_doc = load_yaml(claims_path)
    events_doc = load_yaml(events_path)
    contracts.validate("claim_registry", claims_doc)
    contracts.validate("event_registry", events_doc)

    problems: list[str] = []
    claims = _index(claims_doc["claims"], "claim_id", problems)
    events = _index(events_doc["events"], "event_id", problems)
    rule_versions = _index(events_doc["rule_versions"], "rule_version", problems)

    for eid, ev in events.items():
        problems += [f"{eid}: unknown claim {c}" for c in ev["claim_ids"] if c not in claims]
        for key in ("supersedes", "correction_of"):
            if ev.get(key) and ev[key] not in events:
                problems.append(f"{eid}: {key} -> unknown event {ev[key]}")
        problems += [
            f"{eid}: conflicts_with -> unknown event {x}"
            for x in ev.get("conflicts_with") or []
            if x not in events
        ]
    for rv, r in rule_versions.items():
        problems += [
            f"{rv}: unknown basis event {x}" for x in r["basis_event_ids"] if x not in events
        ]

    if problems:
        raise RegistryError("; ".join(problems))
    return Registry(claims, events, rule_versions)
