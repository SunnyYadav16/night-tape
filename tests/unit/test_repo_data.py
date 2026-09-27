from pathlib import Path

from night_tape.config import load_yaml
from night_tape.evidence.sources import load_sources
from night_tape.registry.load import load

ROOT = Path(__file__).resolve().parents[2]
CELL = {"PENDING", "ALLOWED", "ALLOWED_WITH_ATTRIBUTION", "PROHIBITED", "NOT_APPLICABLE"}


def test_repo_registry_is_valid() -> None:
    reg = load(ROOT / "registry" / "claims.yaml", ROOT / "registry" / "events.yaml")
    assert len(reg.claims) >= 30 and len(reg.events) >= 20 and len(reg.rule_versions) == 5


def test_every_claim_source_is_a_configured_source() -> None:
    configured = {s.source_id for s in load_sources(ROOT / "config" / "monitoring.yaml")}
    reg = load(ROOT / "registry" / "claims.yaml", ROOT / "registry" / "events.yaml")
    unknown = sorted(
        c["source_id"]
        for c in reg.claims.values()
        if c.get("source_id") and c["source_id"] not in configured
    )
    assert unknown == []


def test_licensing_matrix_cells_are_known_values() -> None:
    doc = load_yaml(ROOT / "config" / "licensing.yaml")
    cells = {v for row in doc["permissions"] for k, v in row.items() if k != "output_type"}
    assert cells <= CELL


def test_spend_cap_is_set() -> None:
    doc = load_yaml(ROOT / "config" / "datasets.yaml")
    assert doc["spend_cap_usd"] > 0
