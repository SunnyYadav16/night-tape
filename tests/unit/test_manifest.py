import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

from night_tape.cli import main
from night_tape.evidence import fetch, manifest, verify

URL = "https://databento.com/docs/schemas-and-data-formats/tbbo"


def client_for(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def serve(*bodies: bytes) -> httpx.Client:
    it = iter(bodies)
    return client_for(
        lambda r: httpx.Response(
            200, content=next(it), headers={"content-type": "text/html; charset=utf-8"}
        )
    )


def do_fetch(ev: Path, client: httpx.Client, url: str = URL) -> tuple[manifest.Entry, bool]:
    return fetch.fetch(ev, client, url, source_id="databento-tbbo", source_class="VENDOR_DOC")


def test_fetch_archives_exact_bytes_and_one_manifest_line(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    entry, created = do_fetch(ev, serve(b"<html>v1</html>"))
    assert created
    stored = tmp_path / entry.local_path
    assert stored.read_bytes() == b"<html>v1</html>"
    assert entry.sha256 == manifest.sha256_file(stored)
    assert entry.local_path.startswith("evidence/VENDOR_DOC/databento-tbbo/")
    assert (entry.content_type, entry.method, entry.canonical_url) == ("text/html", "http", URL)
    lines = (ev / manifest.MANIFEST).read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["sha256"] == entry.sha256


def test_refetch_with_same_bytes_is_a_noop(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    first, _ = do_fetch(ev, serve(b"same"))
    second, created = do_fetch(ev, serve(b"same"))
    assert not created and second == first
    assert len(manifest.read(ev)) == 1


def test_refetch_with_changed_bytes_adds_a_snapshot_and_keeps_the_old_one(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    old, _ = do_fetch(ev, serve(b"alert v1"))
    new, created = do_fetch(ev, serve(b"alert v2"))
    assert created and old.local_path != new.local_path
    assert (tmp_path / old.local_path).read_bytes() == b"alert v1"
    assert (tmp_path / new.local_path).read_bytes() == b"alert v2"
    assert [e.sha256 for e in manifest.read(ev)] == [old.sha256, new.sha256]


def test_http_error_is_not_archived(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    with pytest.raises(httpx.HTTPStatusError):
        do_fetch(ev, client_for(lambda r: httpx.Response(404, text="not found")))
    assert manifest.read(ev) == []
    assert not ev.exists() or not any(p.is_file() for p in ev.rglob("*"))


def test_redirect_is_recorded(tmp_path: Path) -> None:
    def handler(r: httpx.Request) -> httpx.Response:
        if r.url.path == "/old":
            return httpx.Response(301, headers={"location": "https://example.org/new.pdf"})
        return httpx.Response(200, content=b"%PDF-1.7", headers={"content-type": "application/pdf"})

    entry, _ = do_fetch(tmp_path / "evidence", client_for(handler), "https://example.org/old")
    assert entry.canonical_url == "https://example.org/old"
    assert entry.notes is not None and "redirected to https://example.org/new.pdf" in entry.notes
    assert entry.local_path.endswith("new.pdf")


def test_add_file_registers_a_hand_download(tmp_path: Path) -> None:
    pdf = tmp_path / "lim-2026.pdf"
    pdf.write_bytes(b"%PDF-1.5 lim")
    entry, created = fetch.add_file(
        tmp_path / "evidence",
        pdf,
        url="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6610883",
        source_id="lim-ssrn-6610883-rev-2026-04-21",
        source_class="PAPER",
    )
    assert created and entry.method == "manual" and entry.content_type == "application/pdf"


def test_make_client_requires_a_declared_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(fetch.USER_AGENT_ENV, raising=False)
    with pytest.raises(RuntimeError, match=fetch.USER_AGENT_ENV):
        fetch.make_client()
    monkeypatch.setenv(fetch.USER_AGENT_ENV, "night-tape research test@example.org")
    seen: list[str] = []

    def handler(r: httpx.Request) -> httpx.Response:
        seen.append(r.headers["user-agent"])
        return httpx.Response(200)

    fetch.make_client(httpx.MockTransport(handler)).get("https://www.sec.gov/")
    assert seen == ["night-tape research test@example.org"]


def test_verify_clean_tampered_missing_and_orphans(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    a, _ = do_fetch(ev, serve(b"a"), "https://example.org/a.html")
    b, _ = do_fetch(ev, serve(b"b"), "https://example.org/b.html")
    assert verify.verify(ev).ok

    (tmp_path / a.local_path).write_bytes(b"tampered")
    (tmp_path / b.local_path).unlink()
    (ev / "VENDOR_DOC" / "stray.html").write_bytes(b"?")
    (ev / "VENDOR_DOC" / "half.html.part").write_bytes(b"?")
    (ev / ".DS_Store").write_bytes(b"")
    report = verify.verify(ev, required_source_ids=["databento-tbbo", "never-fetched"])
    assert report.mismatched == [a.local_path]
    assert report.missing == [b.local_path]
    assert report.orphans == [
        "evidence/VENDOR_DOC/half.html.part",
        "evidence/VENDOR_DOC/stray.html",
    ]
    assert report.unarchived_sources == ["never-fetched"]
    assert not report.ok


def test_cli_verify_exit_codes(tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    ev.mkdir()
    none = str(tmp_path / "none.yaml")
    assert main(["evidence", "--evidence-dir", str(ev), "--sources", none, "verify"]) == 0
    (ev / "stray.bin").write_bytes(b"?")
    assert main(["evidence", "--evidence-dir", str(ev), "--sources", none, "verify"]) == 1
