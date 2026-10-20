"""Makale metni: yalnız kuyruğa giren haberin özetlenmesi sırasında okunur, SAKLANMAZ.

Yayın kılavuzu §7 (20 Ekim 2026 editör kararı): metin veritabanına, dosyaya ya da loga yazılmaz; yalnız o
özetleme çağrısında modele verilir. Bu modül metni döndürür, kalıcı hiçbir yere yazmaz.

Sıra: robots.txt izni → sayfa (bot UA, reddedilirse tarayıcı başlığı) → JSON-LD articleBody → <p> yoğunluğu
en yüksek kapsayıcı. Ödeme duvarı/çerez duvarı/aşırı kısa metin = metin yok; özet başlık+lead ile yazılır.
"""
from __future__ import annotations

import json
import logging
from urllib import robotparser
from urllib.parse import urlsplit

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from .rss import BROWSER_HEADERS, RETRY_STATUS

log = logging.getLogger(__name__)

MIN_CHARS = 400       # bunun altı: duvar, özet kartı ya da çıkarım hatası
MAX_CHARS = 15000     # modele giden üst sınır (uzun analizlerde ilk ~2.500 kelime)
SKIP_HOSTS = ("news.google.com",)   # gnews yedeği yönlendirmesi JS ile çözülüyor; okunamaz
PAYWALL_HINTS = ("subscribe to continue", "subscribe to read", "this article is for subscribers",
                 "already a subscriber", "مشتركين فقط", "μόνο για συνδρομητές", "только для подписчиков")
_DROP = "script,style,noscript,nav,header,footer,aside,form,figure,iframe,svg,button"

_robots: dict[str, robotparser.RobotFileParser | None] = {}


def _allowed(client: httpx.Client, url: str, ua: str) -> bool:
    parts = urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        rp = robotparser.RobotFileParser()
        try:
            r = client.get(f"{base}/robots.txt", timeout=8)
            if r.status_code >= 400:
                rp = None          # robots yok/erişilemez: kısıt yok sayılır (standart davranış)
            else:
                rp.parse(r.text.splitlines())
        except httpx.HTTPError:
            rp = None
        _robots[base] = rp
    rp = _robots[base]
    return True if rp is None else rp.can_fetch(ua, url)


def _from_jsonld(tree: HTMLParser) -> str | None:
    for node in tree.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(node.text() or "")
        except ValueError:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            d = stack.pop()
            if isinstance(d, dict):
                body = d.get("articleBody")
                if isinstance(body, str) and len(body) >= MIN_CHARS:
                    return body
                stack.extend(v for v in d.values() if isinstance(v, (dict, list)))
            elif isinstance(d, list):
                stack.extend(d)
    return None


def _from_paragraphs(tree: HTMLParser) -> str | None:
    for n in tree.css(_DROP):
        n.decompose()
    scores: dict[int, tuple[object, int]] = {}
    for p in tree.css("p"):
        t = " ".join(p.text(separator=" ").split())
        if len(t) < 40 or p.parent is None:
            continue
        key = p.parent.mem_id
        node, sc = scores.get(key, (p.parent, 0))
        scores[key] = (node, sc + len(t))
    if not scores:
        return None
    best = max(scores.values(), key=lambda x: x[1])[0]
    paras = [" ".join(p.text(separator=" ").split()) for p in best.css("p")]
    return "\n".join(t for t in paras if len(t) >= 40) or None


def extract(html: str) -> str | None:
    tree = HTMLParser(html)
    text = _from_jsonld(tree) or _from_paragraphs(tree)
    if not text:
        return None
    text = text.strip()
    low = text[:3000].lower()
    if len(text) < MIN_CHARS or (len(text) < 1500 and any(h in low for h in PAYWALL_HINTS)):
        return None
    return text[:MAX_CHARS]


def fetch_text(client: httpx.Client, url: str, ua: str) -> tuple[str | None, str]:
    """(metin, durum) döndürür. durum: ok | atlandi | robots | http-<kod> | hata | bos."""
    if any(h in urlsplit(url).netloc for h in SKIP_HOSTS):
        return None, "atlandi"
    try:
        if not _allowed(client, url, ua):
            return None, "robots"
        r = client.get(url, headers={"Accept": "text/html"})
        if r.status_code in RETRY_STATUS:
            r = client.get(url, headers={**BROWSER_HEADERS, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"})
        if r.status_code >= 400:
            return None, f"http-{r.status_code}"
        text = extract(r.text)
        return (text, "ok") if text else (None, "bos")
    except httpx.HTTPError as e:
        log.info("metin alınamadı %s: %s", url, type(e).__name__)
        return None, "hata"
