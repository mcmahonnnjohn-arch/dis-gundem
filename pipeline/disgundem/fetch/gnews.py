"""Google News RSS toplayıcı: RSS'i olmayan kaynaklar için `site:domain` + yerel dil Türkiye terimleri.

Google yönlendirme linki yayıncı kanonik URL'si değildir; `extra["gnews"]=True` ile işaretlenir, tekilleştirme
başlık hash'i üzerinden de yapılır.
"""
from __future__ import annotations

from urllib.parse import quote, urlsplit

import httpx

from ..terms import Matcher
from . import Item
from .rss import fetch_feed


def _domain(url: str) -> str:
    host = urlsplit(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def fetch_gnews(client: httpx.Client, matcher: Matcher, source_id: str, site_url: str, lang: str,
                days: int = 7, turkey_only: bool = True) -> list[Item]:
    dom = _domain(site_url)
    lt = matcher.terms.get(lang) or matcher.terms["en"]
    if turkey_only:
        q = f"site:{dom} (" + " OR ".join(f'"{t}"' for t in lt.terms[:4]) + f") when:{days}d"
    else:
        q = f"site:{dom} when:{days}d"
    items: list[Item] = []
    seen: set[str] = set()
    for gl, hl in (lt.editions or [("US", "en")]):
        url = f"https://news.google.com/rss/search?q={quote(q)}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
        try:
            got = fetch_feed(client, source_id, url, lang=lang)
        except Exception:
            continue
        for it in got:
            key = it.title.casefold()
            if key in seen:
                continue
            seen.add(key)
            it.extra["gnews"] = True
            it.extra["edition"] = f"{gl}:{hl}"
            items.append(it)
    return items
