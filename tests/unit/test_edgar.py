from pathlib import Path
from typing import Any

import httpx
import pytest

from night_tape.evidence import edgar, manifest

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK0001795131.json"
BASE = "https://www.sec.gov/Archives/edgar/data/1795131/"
FOLDERS = {
    BASE + "000090266426003296/index.json": ["primary_doc.xml", "ex3redline.pdf"],
    BASE + "000179513124000022/index.json": ["primary_doc.xml"],
}


def submissions(files: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "cik": "1795131",
        "filings": {
            "recent": {
                "accessionNumber": [
                    "0000902664-26-003296",
                    "0001795131-24-000022",
                    "0000000000-25-000001",
                ],
                "form": ["ATS-N/MA", "ATS-N/CA", "D"],
                "filingDate": ["2026-05-01", "2024-03-01", "2025-01-01"],
            },
            "files": files or [],
        },
    }


def edgar_client(subs: dict[str, Any]) -> httpx.Client:
    def handler(r: httpx.Request) -> httpx.Response:
        url = str(r.url)
        if url == SUBMISSIONS_URL:
            return httpx.Response(200, json=subs)
        if url in FOLDERS:
            items = [{"name": n, "type": "text.gif"} for n in FOLDERS[url]]
            return httpx.Response(200, json={"directory": {"item": items}})
        if url.startswith(BASE):
            return httpx.Response(
                200, content=f"bytes of {url}".encode(), headers={"content-type": "application/xml"}
            )
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def run(ev: Path, client: httpx.Client, sleeps: list[float]) -> list[tuple[manifest.Entry, bool]]:
    return edgar.archive_chain(
        ev,
        client,
        cik="1795131",
        form_prefix="ATS-N",
        source_id="boats-atsn-chain",
        source_class="SEC_FORM_ATS_N",
        sleep=sleeps.append,
    )


def test_parse_filings_keeps_the_form_family_oldest_first() -> None:
    filings = edgar.parse_filings(submissions(), "ATS-N")
    assert [(f.form, f.filing_date) for f in filings] == [
        ("ATS-N/CA", "2024-03-01"),
        ("ATS-N/MA", "2026-05-01"),
    ]


def test_archive_chain_stores_the_listing_and_every_file(tmp_path: Path) -> None:
    sleeps: list[float] = []
    results = run(tmp_path / "evidence", edgar_client(submissions()), sleeps)
    entries = [e for e, created in results if created]
    assert len(entries) == 4  # submissions JSON + 3 filing files
    assert entries[0].canonical_url == SUBMISSIONS_URL and entries[0].edgar_accession is None
    files = entries[1:]
    assert {e.edgar_accession for e in files} == {"0000902664-26-003296", "0001795131-24-000022"}
    assert all(e.method == "edgar" and e.source_id == "boats-atsn-chain" for e in files)
    assert all(f"/{e.edgar_accession}/" in e.local_path for e in files)
    assert len(sleeps) == 6 and set(sleeps) == {edgar.MIN_INTERVAL_S}  # one sleep per request


def test_second_run_is_a_noop(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    run(ev, edgar_client(submissions()), [])
    assert not any(created for _, created in run(ev, edgar_client(submissions()), []))


def test_paginated_submissions_fail_closed(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    subs = submissions(files=[{"name": "CIK0001795131-submissions-001.json"}])
    with pytest.raises(edgar.PaginatedSubmissions):
        run(ev, edgar_client(subs), [])
    assert manifest.read(ev) == []
