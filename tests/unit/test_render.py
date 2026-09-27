import functools
import threading
from collections.abc import Iterator
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from night_tape.evidence import manifest
from night_tape.evidence.render import render

PAGE = (
    "<html><body><div id='x'></div>"
    "<script>document.getElementById('x').textContent='rendered-by-js'</script></body></html>"
)


@pytest.fixture
def site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    monkeypatch.setenv("NIGHT_TAPE_USER_AGENT", "night-tape test")
    root = tmp_path / "site"
    root.mkdir()
    (root / "alerts.html").write_text(PAGE)
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


def test_render_archives_the_js_dom_and_a_pdf(site: str, tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    (html, _), (pdf, _) = render(
        ev,
        f"{site}/alerts.html",
        source_id="blue-ocean-service-status",
        source_class="ATS_SERVICE_ALERT",
    )
    assert (html.method, pdf.method) == ("render-html", "render-pdf")
    assert b"rendered-by-js" in (tmp_path / html.local_path).read_bytes()
    assert (tmp_path / pdf.local_path).read_bytes().startswith(b"%PDF")
    assert html.canonical_url == pdf.canonical_url == f"{site}/alerts.html"


def test_render_refuses_error_page(site: str, tmp_path: Path) -> None:
    ev = tmp_path / "evidence"
    with pytest.raises(RuntimeError, match="HTTP 404"):
        render(ev, f"{site}/missing.html", source_id="x", source_class="VENDOR_DOC")
    assert manifest.read(ev) == []
