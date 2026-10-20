"""rss.fetch_feed: tarayıcı başlığıyla ikinci deneme, bozuk XML temizliği, boş/tarihsiz besleme teşhisi."""
import httpx
import pytest

from disgundem.fetch.rss import BROWSER_HEADERS, fetch_feed

RSS = b"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>t</title>
<item><title>Turkey and Greece talk</title><link>https://ex.com/a</link><pubDate>Mon, 19 Oct 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def test_browser_header_retry_on_403():
    calls = []

    def h(req):
        calls.append(req.headers["user-agent"])
        if req.headers["user-agent"] != BROWSER_HEADERS["User-Agent"]:
            return httpx.Response(403)
        return httpx.Response(200, content=RSS)

    items = fetch_feed(_client(h), "K1", "https://ex.com/feed")
    assert len(items) == 1 and items[0].extra.get("browser_ua")
    assert len(calls) == 2


def test_still_403_raises():
    with pytest.raises(httpx.HTTPStatusError):
        fetch_feed(_client(lambda r: httpx.Response(403)), "K1", "https://ex.com/feed")


def test_bare_ampersand_is_repaired():
    bad = RSS.replace(b"Turkey and Greece", b"Turkey & Greece \x01")
    items = fetch_feed(_client(lambda r: httpx.Response(200, content=bad)), "K1", "https://ex.com/feed")
    assert items and "Turkey & Greece" in items[0].title


def test_empty_feed_message():
    empty = b'<?xml version="1.0"?><rss version="2.0"><channel><title>t</title></channel></rss>'
    with pytest.raises(ValueError, match="besleme boş"):
        fetch_feed(_client(lambda r: httpx.Response(200, content=empty)), "K1", "https://ex.com/feed")


def test_undated_feed_message():
    nodate = RSS.replace(b"<pubDate>Mon, 19 Oct 2026 10:00:00 GMT</pubDate>", b"")
    with pytest.raises(ValueError, match="tarih yok"):
        fetch_feed(_client(lambda r: httpx.Response(200, content=nodate)), "K1", "https://ex.com/feed")


def test_scrape_retries_with_browser_headers():
    from disgundem.fetch.scrape import fetch_listing
    html = b'<html><body><a href="/news/1">Turkey and Egypt sign a long enough headline here</a></body></html>'
    def h(req):
        if req.headers["user-agent"] != BROWSER_HEADERS["User-Agent"]:
            return httpx.Response(403)
        return httpx.Response(200, content=html, headers={"content-type": "text/html"})
    items = fetch_listing(_client(h), "K1", "https://ex.com/")
    assert len(items) == 1 and items[0].url.startswith("https://ex.com/news/1")


def test_collect_fallback_zero_is_not_error(monkeypatch):
    from disgundem import cli
    def boom(*a, **k): raise httpx.HTTPStatusError("403", request=None, response=None)
    monkeypatch.setattr(cli, "fetch_listing", boom)
    monkeypatch.setattr(cli, "fetch_gnews", lambda *a, **k: [])
    src = {"id": "K1", "method": "scrape", "url": "https://ex.com", "tier": "B", "langs": ["en"]}
    items, via = cli._collect(None, None, src)
    assert items == [] and via == "gnews-yedek-0"


def test_collect_fallback_error_raises_original(monkeypatch):
    from disgundem import cli
    def boom(*a, **k): raise ValueError("birincil")
    def gboom(*a, **k): raise RuntimeError("gnews")
    monkeypatch.setattr(cli, "fetch_feed", boom)
    monkeypatch.setattr(cli, "fetch_gnews", gboom)
    src = {"id": "K1", "method": "rss", "feed_url": "f", "url": "https://ex.com", "tier": "A", "langs": ["en"]}
    with pytest.raises(ValueError, match="birincil"):
        cli._collect(None, None, src)
