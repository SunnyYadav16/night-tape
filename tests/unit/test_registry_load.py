from pathlib import Path
from typing import Any

import pytest
import yaml

from night_tape.cli import main
from night_tape.config import load_yaml
from night_tape.contracts import ContractError
from night_tape.registry.claims import load_bearing_gaps
from night_tape.registry.load import RegistryError, load

SHA = "c" * 64


def claim(cid: str, **over: Any) -> dict[str, Any]:
    c: dict[str, Any] = {
        "claim_id": cid,
        "claim_text": "t",
        "claim_type": "schedule",
        "load_bearing": True,
        "affects": ["identification"],
        "status": "UNVERIFIED",
    }
    c.update(over)
    return c


def event(eid: str, **over: Any) -> dict[str, Any]:
    e: dict[str, Any] = {
        "event_id": eid,
        "entity": "BOATS",
        "field": "halt_rule",
        "value": "none",
        "status": "CURRENT",
        "effective_granularity": "day",
        "effective_from": "2026-09-10",
        "effective_to": None,
        "claim_ids": ["C-A"],
        "load_bearing": True,
    }
    e.update(over)
    return e


def write(
    tmp: Path,
    claims: list[dict[str, Any]],
    events: list[dict[str, Any]],
    rvs: list[dict[str, Any]] | None = None,
) -> tuple[Path, Path]:
    c, e = tmp / "claims.yaml", tmp / "events.yaml"
    c.write_text(yaml.safe_dump({"claims": claims}))
    e.write_text(yaml.safe_dump({"events": events, "rule_versions": rvs or []}))
    return c, e


def test_yaml_dates_stay_strings(tmp_path: Path) -> None:
    f = tmp_path / "d.yaml"
    f.write_text("effective_from: 2026-07-20\nat: 2026-09-22T12:00:00Z\n")
    assert load_yaml(f) == {"effective_from": "2026-07-20", "at": "2026-09-22T12:00:00Z"}


def test_unquoted_dates_validate_through_the_loader(tmp_path: Path) -> None:
    c = tmp_path / "claims.yaml"
    e = tmp_path / "events.yaml"
    e.write_text(
        "events:\n- event_id: E-X\n  entity: BOATS\n  field: halt_rule\n  value: none\n"
        "  status: CURRENT\n  effective_granularity: day\n  effective_from: 2026-09-10\n"
        "  effective_to: null\n  claim_ids: [C-A]\n  load_bearing: true\nrule_versions: []\n"
    )
    c.write_text(
        "claims:\n- {claim_id: C-A, claim_text: t, claim_type: schedule, load_bearing: true, "
        "affects: [identification], status: UNVERIFIED}\n"
    )
    assert load(c, e).events["E-X"]["effective_from"] == "2026-09-10"


def test_valid_registry_loads(tmp_path: Path) -> None:
    rv = {
        "rule_version": "BOATS_POST_2026_09_10",
        "venue": "BOATS",
        "effective_granularity": "day",
        "effective_from": "2026-09-10",
        "effective_to": None,
        "basis_event_ids": ["E-X"],
        "provisional": True,
    }
    reg = load(*write(tmp_path, [claim("C-A")], [event("E-X")], [rv]))
    assert list(reg.claims) == ["C-A"] and list(reg.events) == ["E-X"]
    assert list(reg.rule_versions) == ["BOATS_POST_2026_09_10"]


@pytest.mark.parametrize(
    "claims, events, fragment",
    [
        ([claim("C-A"), claim("C-A")], [], "duplicate claim_id C-A"),
        ([claim("C-A")], [event("E-X", claim_ids=["C-NOPE"])], "unknown claim C-NOPE"),
        (
            [claim("C-A")],
            [event("E-X", supersedes="E-GHOST")],
            "supersedes -> unknown event E-GHOST",
        ),
    ],
)
def test_cross_reference_errors(
    tmp_path: Path,
    claims: list[dict[str, Any]],
    events: list[dict[str, Any]],
    fragment: str,
) -> None:
    with pytest.raises(RegistryError, match=fragment):
        load(*write(tmp_path, claims, events))


def test_contract_violation_surfaces_the_path(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match=r"claims\[0\]"):
        load(*write(tmp_path, [claim("C-A", status="VERIFIED")], []))


def test_load_bearing_gaps(tmp_path: Path) -> None:
    claims = [
        claim("C-OPEN"),
        claim(
            "C-OK",
            status="VERIFIED",
            source_class="VENDOR_DOC",
            source_id="s",
            retrieved_at="2026-09-22T12:00:00Z",
            sha256=SHA,
        ),
        claim("C-PLAN", status="CONTINGENCY"),
        claim("C-CTX", load_bearing=False, affects=["context_only"]),
    ]
    reg = load(*write(tmp_path, claims, []))
    assert load_bearing_gaps(reg, {SHA}) == ["C-OPEN: status UNVERIFIED"]


def test_verified_claim_with_unarchived_hash_is_a_gap(tmp_path: Path) -> None:
    ok = claim(
        "C-OK",
        status="VERIFIED",
        source_class="VENDOR_DOC",
        source_id="s",
        retrieved_at="2026-09-22T12:00:00Z",
        sha256=SHA,
    )
    reg = load(*write(tmp_path, [ok], []))
    gaps = load_bearing_gaps(reg, archived_sha256=set())
    assert len(gaps) == 1 and gaps[0].startswith("C-OK: VERIFIED but sha256")


def test_cli_load_bearing_exit_code(tmp_path: Path) -> None:
    c, e = write(tmp_path, [claim("C-OPEN")], [])
    args = ["registry", "--claims", str(c), "--events", str(e)]
    assert main([*args, "check"]) == 0
    assert main([*args, "load-bearing", "--evidence-dir", str(tmp_path / "evidence")]) == 1
