"""HTTP archive-on-fetch. Stores the bytes the server sent, never a rendering or an error page."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import httpx

from night_tape.evidence.manifest import Entry, store

USER_AGENT_ENV = "NIGHT_TAPE_USER_AGENT"
_EXT = {
    "text/html": ".html",
    "application/pdf": ".pdf",
    "application/json": ".json",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "text/plain": ".txt",
}


def user_agent() -> str:
    ua = os.environ.get(USER_AGENT_ENV, "").strip()
    if not ua:
        raise RuntimeError(
            f"set {USER_AGENT_ENV}='night-tape research <contact email>' "
            "(SEC fair access requires a declared contact)"
        )
    return ua


def make_client(transport: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": user_agent()},
        follow_redirects=True,
        timeout=60.0,
        transport=transport,
    )


def fetch_bytes(client: httpx.Client, url: str) -> httpx.Response:
    resp = client.get(url)
    resp.raise_for_status()
    return resp


def content_type(resp: httpx.Response) -> str:
    ctype: str = resp.headers.get("content-type", "application/octet-stream")
    return ctype.split(";")[0].strip()


def _filename(url: str, ctype: str) -> str:
    name = PurePosixPath(urlsplit(url).path).name
    return name if "." in name else (name or "index") + _EXT.get(ctype, ".bin")


def fetch(
    evidence_dir: Path,
    client: httpx.Client,
    url: str,
    *,
    source_id: str,
    source_class: str,
    supersedes: str | None = None,
    notes: str | None = None,
) -> tuple[Entry, bool]:
    resp = fetch_bytes(client, url)
    final = str(resp.url)
    if final != url:
        notes = f"redirected to {final}" + (f"; {notes}" if notes else "")
    ctype = content_type(resp)
    return store(
        evidence_dir,
        resp.content,
        source_id=source_id,
        source_class=source_class,
        canonical_url=url,
        content_type=ctype,
        method="http",
        filename=_filename(final, ctype),
        supersedes=supersedes,
        notes=notes,
    )


def add_file(
    evidence_dir: Path,
    path: Path,
    *,
    url: str,
    source_id: str,
    source_class: str,
    content_type: str | None = None,
    notes: str | None = None,
) -> tuple[Entry, bool]:
    ctype = content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return store(
        evidence_dir,
        path.read_bytes(),
        source_id=source_id,
        source_class=source_class,
        canonical_url=url,
        content_type=ctype,
        method="manual",
        filename=path.name,
        notes=notes,
    )
