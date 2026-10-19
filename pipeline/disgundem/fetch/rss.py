"""RSS/Atom toplayıcı. feedparser + httpx; tarihi olmayan kayıt alınmaz (ölçüm penceresi tarihe bağlı)."""
from __future__ import annotations

import logging
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


def fetch_feed(client: httpx.Client, source_id: str, feed_url: str, lang: str | None = None) -> list[Item]:
    r = client.get(feed_url)
    r.raise_for_status()
    parsed = feedparser.parse(r.content)
    if parsed.bozo and not parsed.entries:
        raise ValueError(f"besleme ayrıştırılamadı: {parsed.bozo_exception}")
    items: list[Item] = []
    for e in parsed.entries:
        link = e.get("link")
        title = (e.get("title") or "").strip()
        if not link or not title:
            continue
        d = _date(e)
        if d is None:
            continue
        summary = e.get("summary") or (e.get("content") or [{}])[0].get("value", "")
        items.append(Item(
            source_id=source_id, url=canonical(link), title=unescape(title), published_at=d,
            lang=lang or (parsed.feed.get("language") or "")[:2] or None,
            excerpt=_strip(summary) if summary else None,
        ))
    return items


def make_client(s: Settings) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": s.user_agent, "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8"},
        timeout=s.http_timeout, follow_redirects=True,
    )
