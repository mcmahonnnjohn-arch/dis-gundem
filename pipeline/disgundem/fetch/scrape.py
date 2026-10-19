"""Liste sayfası scraper'ı (RSS'siz kaynaklar): yalnızca başlık + link toplar, makale gövdesine girmez.

Genel sezgisel: ana sayfadaki aynı alan adına giden, 25+ karakterlik bağlantı metinleri. Kaynak başına
özel seçici gerekirse `SELECTORS[source_id]` içine CSS seçici yazılır. Tarih sayfadan güvenilir alınamazsa
`published_at=None` kalır ve kayıt ölçüm penceresine girmez (yalnız kuyruğa düşer).
"""
from __future__ import annotations

from urllib.parse import urljoin, urlsplit

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from . import Item
from .rss import canonical

SELECTORS: dict[str, str] = {
    # "K122": "div.collection-result a",   # örnek: state.gov press briefings
}


def fetch_listing(client: httpx.Client, source_id: str, page_url: str, lang: str | None = None,
                  min_len: int = 25, limit: int = 60) -> list[Item]:
    r = client.get(page_url, headers={"Accept": "text/html"})
    r.raise_for_status()
    tree = HTMLParser(r.text)
    host = urlsplit(page_url).netloc.lower()
    nodes = tree.css(SELECTORS[source_id]) if source_id in SELECTORS else tree.css("a[href]")
    items: list[Item] = []
    seen: set[str] = set()
    for a in nodes:
        href = a.attributes.get("href")
        text = " ".join(a.text(separator=" ").split())
        if not href or len(text) < min_len:
            continue
        url = urljoin(page_url, href)
        if urlsplit(url).netloc.lower() != host:
            continue
        url = canonical(url)
        if url in seen:
            continue
        seen.add(url)
        items.append(Item(source_id=source_id, url=url, title=text, lang=lang, extra={"scraped": True}))
        if len(items) >= limit:
            break
    return items
