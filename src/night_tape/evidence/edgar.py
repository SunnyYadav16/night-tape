"""Archive every file of every filing in one form family for one CIK (e.g. all BOATS ATS-N).

Archive the accession folders, not only the XSL-rendered view (weekly W1 "Watch out for").
The submissions listing is archived too, so "the full chain" is itself evidenced.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from night_tape.evidence.fetch import content_type, fetch_bytes
from night_tape.evidence.manifest import Entry, store

SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
FOLDER = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/"
# ponytail: fixed sleep keeps one client under SEC's 10 req/s; token bucket if we ever parallelize
MIN_INTERVAL_S = 0.12


@dataclass(frozen=True)
class Filing:
    accession: str
    form: str
    filing_date: str


class PaginatedSubmissions(RuntimeError):
    """Older filings live in extra submission files; archiving only `recent` would be partial."""


def parse_filings(submissions: dict[str, Any], form_prefix: str) -> list[Filing]:
    filings = submissions["filings"]
    if filings.get("files"):
        names = [f["name"] for f in filings["files"]]
        raise PaginatedSubmissions(
            f"older filings in {names}; extend edgar.py before trusting the chain"
        )
    recent = filings["recent"]
    rows = zip(recent["accessionNumber"], recent["form"], recent["filingDate"], strict=True)
    found = [Filing(a, f, d) for a, f, d in rows if f.startswith(form_prefix)]
    return sorted(found, key=lambda f: (f.filing_date, f.accession))


def archive_chain(
    evidence_dir: Path,
    client: httpx.Client,
    *,
    cik: str,
    form_prefix: str,
    source_id: str,
    source_class: str,
    sleep: Callable[[float], None] = time.sleep,
) -> list[tuple[Entry, bool]]:
    def get(url: str) -> httpx.Response:
        sleep(MIN_INTERVAL_S)
        return fetch_bytes(client, url)

    listing_url = SUBMISSIONS.format(cik=cik.zfill(10))
    listing = get(listing_url)
    filings = parse_filings(listing.json(), form_prefix)  # fail closed before storing anything
    results = [
        store(
            evidence_dir,
            listing.content,
            source_id=source_id,
            source_class=source_class,
            canonical_url=listing_url,
            content_type="application/json",
            method="edgar",
            filename=f"CIK{cik.zfill(10)}.json",
            notes=f"{len(filings)} {form_prefix}* filings listed",
        )
    ]
    for filing in filings:
        base = FOLDER.format(cik=int(cik), acc=filing.accession.replace("-", ""))
        names = sorted(
            item["name"] for item in get(base + "index.json").json()["directory"]["item"]
        )
        for name in names:
            resp = get(base + name)
            results.append(
                store(
                    evidence_dir,
                    resp.content,
                    source_id=source_id,
                    source_class=source_class,
                    canonical_url=base + name,
                    content_type=content_type(resp),
                    method="edgar",
                    filename=name,
                    subdir=filing.accession,
                    edgar_accession=filing.accession,
                    published_or_filed_at=filing.filing_date,
                    notes=filing.form,
                )
            )
    return results
