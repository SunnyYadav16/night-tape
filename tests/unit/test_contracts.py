from typing import Any

import pytest

from night_tape import contracts

INT64_MAX = 2**63 - 1
NAMES = ["trade", "quote", "claim_registry", "event_registry", "tracker_entry"]


def trade(**over: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "trade_id": "OCEA.MEMOIR:S1:SPY:1:7:0",
        "symbol": "SPY",
        "venue": "BOATS",
        "instrument_id": 1,
        "ts_event": 1_790_000_000_000_000_000,
        "ts_recv": 1_790_000_000_000_000_100,
        "sequence": 7,
        "record_idx": 0,
        "price_int": 500_010_000_000,
        "size": 100,
        "side_raw": "B",
        "aggressor_direction": 1,
        "bid_px_pre_int": 500_000_000_000,
        "ask_px_pre_int": 500_020_000_000,
        "wall_clock_execution_date": "2026-09-21",
        "venue_trade_date": "2026-09-21",
        "finra_reporting_date": "2026-09-21",
        "nscc_clearing_business_date": "2026-09-21",
        "session_id": "S1",
        "rule_version": "BOATS_POST_2026_09_10",
        "source_dataset": "OCEA.MEMOIR",
        "source_schema": "tbbo",
        "manifest_id": "m1",
    }
    row.update(over)
    return row


def quote(**over: Any) -> dict[str, Any]:
    q: dict[str, Any] = {
        "symbol": "SPY",
        "venue": "BOATS",
        "instrument_id": 1,
        "ts_event": 1_790_000_000_000_000_000,
        "ts_recv": 1_790_000_000_000_000_100,
        "sequence": 7,
        "record_idx": 0,
        "bid_px_int": 500_000_000_000,
        "ask_px_int": 500_020_000_000,
        "bid_sz": 100,
        "ask_sz": 200,
        "midpoint_x2_int": 1_000_020_000_000,
        "quote_age_ns": None,
        "book_state": "TWO_SIDED",
        "session_id": "S1",
        "rule_version": "BOATS_POST_2026_09_10",
        "source_dataset": "OCEA.MEMOIR",
        "source_schema": "mbp-1",
        "manifest_id": "m1",
    }
    q.update(over)
    return q


def claim(**over: Any) -> dict[str, Any]:
    c: dict[str, Any] = {
        "claim_id": "C-OCEA-SHARED-SEQUENCE",
        "claim_text": "Records normalized from one native MEMOIR message share the same sequence.",
        "claim_type": "data_semantics",
        "load_bearing": True,
        "affects": ["metric_semantics"],
        "status": "UNVERIFIED",
    }
    c.update(over)
    return c


def event(**over: Any) -> dict[str, Any]:
    ev: dict[str, Any] = {
        "event_id": "E-BOATS-OOB-NONDISPLAYED-2026-07-20",
        "entity": "BOATS",
        "field": "price_band_rule",
        "value": {"aspect": "out_of_band_passive_handling", "action": "ACCEPT_NON_DISPLAYED"},
        "status": "CURRENT",
        "effective_granularity": "day",
        "effective_from": "2026-07-20",
        "effective_to": None,
        "claim_ids": ["C-BOATS-2026-07-20-OOB-NONDISPLAYED"],
        "load_bearing": True,
    }
    ev.update(over)
    return ev


def tracker(**over: Any) -> dict[str, Any]:
    t = event(
        evidence_refs=[
            {
                "source_id": "blue-ocean-service-status",
                "span_id": "s-12",
                "sha256": "a" * 64,
                "retrieved_at": "2026-09-22T12:00:00Z",
                "supports": ["value", "effective_from", "status"],
            }
        ],
        proposed_by="manual",
        provider_version=None,
        approved_by="SY",
        approved_at="2026-09-23T09:00:00Z",
    )
    t.update(over)
    return t


def events(*evs: dict[str, Any]) -> dict[str, Any]:
    return {"events": list(evs), "rule_versions": []}


@pytest.mark.parametrize("name", NAMES)
def test_every_contract_is_a_valid_2020_12_schema(name: str) -> None:
    contracts.validator(name)  # raises SchemaError if the schema itself is malformed


def test_valid_examples_pass() -> None:
    assert contracts.errors("trade", trade()) == []
    assert contracts.errors("quote", quote()) == []
    assert contracts.errors("claim_registry", {"claims": [claim()]}) == []
    assert contracts.errors("event_registry", events(event())) == []
    assert contracts.errors("tracker_entry", tracker()) == []


def test_trade_rejects_undef_price_sentinel() -> None:
    assert any("price_int" in e for e in contracts.errors("trade", trade(price_int=INT64_MAX)))


@pytest.mark.parametrize("side, direction", [("B", -1), ("A", 1), ("N", 1), ("B", None)])
def test_trade_side_and_direction_must_agree(side: str, direction: int | None) -> None:
    assert contracts.errors("trade", trade(side_raw=side, aggressor_direction=direction))


def test_trade_requires_all_four_dates_and_no_generic_date() -> None:
    row = trade()
    del row["nscc_clearing_business_date"]
    assert contracts.errors("trade", row)
    assert contracts.errors("trade", trade(date="2026-09-21"))


def test_quote_book_state_rules() -> None:
    assert contracts.errors("quote", quote(book_state="ONE_SIDED", ask_px_int=None))  # midpoint set
    ok_one_sided = quote(book_state="ONE_SIDED", ask_px_int=None, midpoint_x2_int=None)
    assert contracts.errors("quote", ok_one_sided) == []
    both_null = quote(
        book_state="ONE_SIDED", bid_px_int=None, ask_px_int=None, midpoint_x2_int=None
    )
    assert contracts.errors("quote", both_null)
    assert contracts.errors("quote", quote(book_state="EMPTY", midpoint_x2_int=None))  # prices set
    assert contracts.errors("quote", quote(midpoint_x2_int=None))  # TWO_SIDED needs a midpoint


def test_claim_rules() -> None:
    assert contracts.errors("claim_registry", {"claims": [claim(status="VERIFIED")]})
    contradictory = claim(affects=["context_only"], load_bearing=True)
    assert contracts.errors("claim_registry", {"claims": [contradictory]})
    assert contracts.errors("claim_registry", {"claims": [claim(affects=["vibes"])]})
    verified = claim(
        status="VERIFIED",
        source_class="VENDOR_DOC",
        source_id="databento-ocea-memoir",
        retrieved_at="2026-09-22T12:00:00Z",
        sha256="b" * 64,
    )
    assert contracts.errors("claim_registry", {"claims": [verified]}) == []


def test_event_rules() -> None:
    reg = "event_registry"
    assert contracts.errors(reg, events(event(effective_from="2026-07-20T00:00:00Z")))  # day gran.
    erroneous = event(status="ERRONEOUS_DISCLOSURE")  # must be granularity never, null dates
    assert contracts.errors(reg, events(erroneous))
    assert contracts.errors(reg, events(event(status="CONFLICTED")))  # needs conflicts_with
    assert contracts.errors(reg, events(event(colour="blue")))  # closed object
    assert contracts.errors(reg, events(event(entity="NYSE")))


def test_tracker_rules() -> None:
    assert contracts.errors("tracker_entry", tracker(status="PENDING_VERIFICATION"))
    no_span = tracker()
    no_span["evidence_refs"][0].pop("span_id")
    assert contracts.errors("tracker_entry", no_span)
    assert contracts.errors("tracker_entry", tracker(provider_version="v1"))  # manual → null
    assert contracts.errors("tracker_entry", tracker(colour="blue"))
    assert contracts.errors("tracker_entry", tracker(evidence_refs=[]))


def test_formats_are_enforced() -> None:
    assert contracts.errors("tracker_entry", tracker(approved_at="yesterday"))
    assert contracts.errors("trade", trade(venue_trade_date="21/09/2026"))


def test_validate_raises_with_paths() -> None:
    with pytest.raises(contracts.ContractError) as exc:
        contracts.validate("trade", trade(size=0))
    assert exc.value.name == "trade"
    assert any("size" in e for e in exc.value.errors)


def test_source_classes_come_from_the_claim_contract() -> None:
    assert "SEC_FORM_ATS_N" in contracts.source_classes()
