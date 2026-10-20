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
