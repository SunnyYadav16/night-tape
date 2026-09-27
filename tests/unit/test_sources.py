from pathlib import Path
from typing import Any

import httpx
import pytest

from night_tape.evidence import manifest, sources
from night_tape.evidence.sources import Source, load_sources, sync

ROOT = Path(__file__).resolve().parents[2]


def http_client(status: int = 200) -> httpx.Client:
    return httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(status, content=b"doc", headers={"content-type": "text/html"})
        )
    )


def test_repo_source_list_loads() -> None:
    srcs = load_sources(ROOT / "config" / "monitoring.yaml")
    ids = {s.source_id for s in srcs}
    assert "boats-atsn-chain" in ids and "blue-ocean-service-status" in ids
    assert len(ids) == len(srcs)


@pytest.mark.parametrize(
    "bad, fragment",
    [
        ({"source_id": "x", "source_class": "VENDOR_DOC", "method": "http"}, "needs url"),
        ({"source_id": "x", "source_class": "VENDOR_DOC", "method": "ftp", "url": "u"}, "method"),
        ({"source_id": "x", "source_class": "BLOG", "method": "http", "url": "u"}, "source_class"),
        ({"source_id": "x", "source_class": "SEC_FORM_ATS_N", "method": "edgar"}, "needs cik"),
    ],
)
def test_bad_sources_fail_closed(tmp_path: Path, bad: dict[str, Any], fragment: str) -> None:
    import yaml

    f = tmp_path / "m.yaml"
    f.write_text(yaml.safe_dump({"sources": [bad]}))
    with pytest.raises(ValueError, match=fragment):
        load_sources(f)


def test_sync_dispatches_by_method_and_keeps_going_after_a_failure(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    calls: list[str] = []

    def fake_render(evidence_dir: Path, url: str, **kw: Any) -> list[tuple[manifest.Entry, bool]]:
        calls.append(f"render {url}")
        raise RuntimeError("render http://r: HTTP 404")

    def fake_edgar(
        evidence_dir: Path, client: httpx.Client, **kw: Any
    ) -> list[tuple[manifest.Entry, bool]]:
        calls.append(f"edgar {kw['cik']}")
        return []

    srcs = [
        Source("r", "VENDOR_DOC", "render", url="http://r"),
        Source("h", "SEC_RULE", "http", url="https://www.sec.gov/x"),
        Source("e", "SEC_FORM_ATS_N", "edgar", cik="1795131", form_prefix="ATS-N"),
        Source("m", "PAPER", "manual", url="https://papers.ssrn.com/x"),
    ]
    report = sync(
        ev, srcs, http_client(), render_fn=fake_render, edgar_fn=fake_edgar, sleep=lambda s: None
    )
    assert calls == ["render http://r", "edgar 1795131"]
    assert [e.source_id for e, _ in report.stored] == ["h"]
    assert report.failed == [("r", "RuntimeError: render http://r: HTTP 404")]
    assert report.manual_missing == ["m"]


def test_manual_source_already_archived_is_not_reported(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    manifest.store(
        ev,
        b"%PDF",
        source_id="m",
        source_class="PAPER",
        canonical_url="u",
        content_type="application/pdf",
        method="manual",
        filename="lim.pdf",
    )
    report = sync(
        ev, [Source("m", "PAPER", "manual", url="u")], http_client(), sleep=lambda s: None
    )
    assert report.manual_missing == []


def test_methods_constant_matches_loader() -> None:
    assert sources.METHODS == ("http", "render", "edgar", "manual")
