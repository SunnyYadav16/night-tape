"""Archive JS-rendered pages: the DOM after load (HTML) plus a printed PDF.

Use only when the raw HTTP bytes don't contain what a reader sees (e.g. the Blue Ocean
service-status page). page.pdf() is Chromium-only.
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from night_tape.evidence.fetch import user_agent
from night_tape.evidence.manifest import Entry, store


def render(
    evidence_dir: Path, url: str, *, source_id: str, source_class: str, notes: str | None = None
) -> list[tuple[Entry, bool]]:
    ua = user_agent()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=ua)
            resp = page.goto(url, wait_until="networkidle", timeout=60_000)
            if resp is None or not resp.ok:
                raise RuntimeError(f"render {url}: HTTP {resp.status if resp else 'no response'}")
            html = page.content().encode("utf-8")
            pdf = page.pdf(format="Letter", print_background=True)
        finally:
            browser.close()
    return [
        store(
            evidence_dir,
            html,
            source_id=source_id,
            source_class=source_class,
            canonical_url=url,
            content_type="text/html",
            method="render-html",
            filename="render.html",
            notes=notes,
        ),
        store(
            evidence_dir,
            pdf,
            source_id=source_id,
            source_class=source_class,
            canonical_url=url,
            content_type="application/pdf",
            method="render-pdf",
            filename="render.pdf",
            notes=notes,
        ),
    ]
