"""HTTP archive-on-fetch. Stores the bytes the server sent, never a rendering or an error page."""

import email.utils
import mimetypes
import os
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
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


RETRY_STATUSES = {429, 500, 502, 503, 504}


def _retry_after(resp: httpx.Response) -> float | None:
    val = resp.headers.get("retry-after", "").strip()
    if not val:
        return None
    if val.isdigit():
        return float(val)
    try:
        dt = email.utils.parsedate_to_datetime(val)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return max(0.0, (dt - datetime.now(UTC)).total_seconds())
    except (TypeError, ValueError, OverflowError):
        return None


def fetch_bytes(
    client: httpx.Client,
    url: str,
    *,
    max_retries: int = 8,
    base_backoff: float = 1.0,
    max_backoff: float = 60.0,
    sleep: Callable[[float], None] = time.sleep,
) -> httpx.Response:
    for attempt in range(max_retries + 1):
        try:
            resp = client.get(url)
        except httpx.TransportError as exc:
            if attempt == max_retries:
                raise
            wait = min(max_backoff, base_backoff * (2**attempt))
            print(
                f"[fetch_bytes] {exc.__class__.__name__} on {url}; "
                f"retrying in {wait:.1f}s (attempt {attempt + 1}/{max_retries})",
                file=sys.stderr,
            )
            sleep(wait)
            continue

        if resp.status_code < 400:
            return resp

        if resp.status_code in RETRY_STATUSES or resp.status_code >= 500:
            if attempt == max_retries:
                resp.raise_for_status()
            retry_after = _retry_after(resp)
            resp.close()
            calc_wait = min(max_backoff, base_backoff * (2**attempt))
            wait = max(calc_wait, retry_after) if retry_after is not None else calc_wait
            print(
                f"[fetch_bytes] HTTP {resp.status_code} on {url}; "
                f"retrying in {wait:.1f}s (attempt {attempt + 1}/{max_retries})",
                file=sys.stderr,
            )
            sleep(wait)
            continue

        resp.raise_for_status()
        return resp

    raise RuntimeError(f"fetch_bytes failed after {max_retries} retries: {url}")


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
