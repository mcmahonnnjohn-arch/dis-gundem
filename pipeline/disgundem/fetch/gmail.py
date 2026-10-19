"""Premium bültenler (FT, Bloomberg, WSJ, Economist, FA, FP) — Gmail etiketinden başlık + link toplar.

Telif kuralı (docs/HEDEF.md): makale metni saklanmaz. Bültenden yalnız başlık, yayın tarihi ve kaynak linki alınır;
2-3 cümlelik özet ve analiz daha sonra kendi cümlelerimizle üretilir.

Gereksinim: `pip install google-api-python-client google-auth` ve GMAIL_TOKEN_PATH'te OAuth token JSON'u.
Token yoksa toplayıcı boş liste döndürür ve bunu loglar (hat durmaz).
"""
from __future__ import annotations

import base64
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from selectolax.lexbor import LexborHTMLParser as HTMLParser

from ..config import Settings
from . import Item
from .rss import canonical

log = logging.getLogger(__name__)

SENDER_TO_SOURCE = {   # gönderen alan adı → kaynak ID (v3 envanteri)
    "ft.com": "K170", "bloomberg.com": "K171", "wsj.com": "K172", "economist.com": "K173",
    "foreignaffairs.com": "K174", "foreignpolicy.com": "K175",
}
SKIP_LINK = re.compile(r"(unsubscribe|manage|preferences|privacy|account|login|signup|mailto:)", re.I)


def _service(s: Settings):
    if not s.gmail_token_path or not Path(s.gmail_token_path).exists():
        log.warning("GMAIL_TOKEN_PATH yok; premium bültenler atlandı")
        return None
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(s.gmail_token_path, ["https://www.googleapis.com/auth/gmail.readonly"])
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _html_of(payload) -> str:
    if payload.get("mimeType") == "text/html" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "replace")
    for part in payload.get("parts", []) or []:
        h = _html_of(part)
        if h:
            return h
    return ""


def fetch_gmail(s: Settings, since_days: int = 2) -> list[Item]:
    svc = _service(s)
    if svc is None:
        return []
    q = f"label:{s.gmail_label} newer_than:{since_days}d"
    resp = svc.users().messages().list(userId="me", q=q, maxResults=100).execute()
    items: list[Item] = []
    for m in resp.get("messages", []):
        msg = svc.users().messages().get(userId="me", id=m["id"], format="full").execute()
        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        sender = headers.get("from", "")
        dom = next((d for d in SENDER_TO_SOURCE if d in sender), None)
        if not dom:
            continue
        try:
            sent = parsedate_to_datetime(headers.get("date", ""))
        except Exception:
            sent = datetime.now(timezone.utc)
        html = _html_of(msg["payload"])
        if not html:
            continue
        tree = HTMLParser(html)
        seen: set[str] = set()
        for a in tree.css("a[href]"):
            href = a.attributes.get("href", "")
            text = " ".join(a.text(separator=" ").split())
            if dom not in href or SKIP_LINK.search(href) or len(text) < 20:
                continue
            url = canonical(href)
            if url in seen:
                continue
            seen.add(url)
            items.append(Item(source_id=SENDER_TO_SOURCE[dom], url=url, title=text, published_at=sent, lang="en",
                              extra={"newsletter": headers.get("subject", ""), "gmail_id": m["id"]}))
    return items
