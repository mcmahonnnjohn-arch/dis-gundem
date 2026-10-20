"""RSS/Atom toplayıcı. feedparser + httpx; tarihi olmayan kayıt alınmaz (ölçüm penceresi tarihe bağlı)."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import feedparser
import httpx
from dateutil import parser as dtparse

from ..config import Settings
from . import Item

log = logging.getLogger(__name__)
TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}


def canonical(url: str) -> str:
    p = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k not in TRACKING]
    return urlunsplit((p.scheme, p.netloc.lower(), p.path.rstrip("/") or "/", urlencode(q), ""))


def _date(entry) -> datetime | None:
    for key in ("published", "updated", "created"):
        v = entry.get(key)
        if v:
            try:
                d = dtparse.parse(v)
                return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
            except (ValueError, OverflowError):
                pass
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def _strip(html: str, limit: int = 400) -> str:
    try:
        from selectolax.lexbor import LexborHTMLParser as HTMLParser
        text = HTMLParser(html).text(separator=" ")
    except Exception:
        text = html
    text = " ".join(unescape(text).split())
    return text[:limit]


BROWSER_HEADERS = {
    # Bazı yayıncılar (Cloudflare/WAF) bilinmeyen bot UA'larını ya da veri merkezi IP'lerini 403 ile reddeder.
    # Herkese açık RSS için tek seferlik ikinci deneme standart tarayıcı başlıklarıyla yapılır; CAPTCHA/çerez
    # meydan okuması aşılmaz, o durumda kaynak gnews yedeğine düşer.
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/128.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.5",
    "Accept-Language": "en-US,en;q=0.8,tr;q=0.6",
}
RETRY_STATUS = {401, 403, 406, 429}
_BAD_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_BARE_AMP = re.compile(rb"&(?!(?:[a-zA-Z][a-zA-Z0-9]{1,31}|#[0-9]{1,7}|#x[0-9a-fA-F]{1,6});)")


def _get(client: httpx.Client, url: str) -> tuple[httpx.Response, bool]:
    r = client.get(url)
    if r.status_code in RETRY_STATUS or r.is_redirect:
        r2 = client.get(url, headers=BROWSER_HEADERS)
        if r2.status_code < 300:
            return r2, True
        r = r2
    r.raise_for_status()
    return r, False


def _parse(content: bytes):
    parsed = feedparser.parse(content)
    if parsed.bozo and not parsed.entries:
        # Kaçışsız & ve kontrol karakterleri (ör. Okaz) — temizleyip bir kez daha dene
        cleaned = _BARE_AMP.sub(b"&amp;", content)
        cleaned = _BAD_XML.sub("", cleaned.decode("utf-8", errors="replace")).encode("utf-8")
        parsed2 = feedparser.parse(cleaned)
        if parsed2.entries:
            return parsed2
        raise ValueError(f"besleme ayrıştırılamadı: {parsed.bozo_exception}")
    return parsed


def fetch_feed(client: httpx.Client, source_id: str, feed_url: str, lang: str | None = None) -> list[Item]:
    r, browser_ua = _get(client, feed_url)
    parsed = _parse(r.content)
    if not parsed.entries:
        ctype = r.headers.get("content-type", "?").split(";")[0]
        raise ValueError(f"besleme boş (HTTP {r.status_code}, {ctype}, {len(r.content)} bayt)")
    items: list[Item] = []
    undated = 0
    for e in parsed.entries:
        link = e.get("link")
        title = (e.get("title") or "").strip()
        if not link or not title:
            continue
        d = _date(e)
        if d is None:
            undated += 1
            continue
        summary = e.get("summary") or (e.get("content") or [{}])[0].get("value", "")
        it = Item(
            source_id=source_id, url=canonical(link), title=unescape(title), published_at=d,
            lang=lang or (parsed.feed.get("language") or "")[:2] or None,
            excerpt=_strip(summary) if summary else None,
        )
        if browser_ua:
            it.extra["browser_ua"] = True
        items.append(it)
    if not items and undated:
        raise ValueError(f"{undated} kayıt var ama hiçbirinde tarih yok")
    return items


def make_client(s: Settings) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": s.user_agent, "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8"},
        timeout=s.http_timeout, follow_redirects=True,
    )
