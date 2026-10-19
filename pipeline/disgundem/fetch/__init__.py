"""Toplayıcılar. Her toplayıcı Item listesi döndürür; makale gövdesi toplanmaz (başlık, link, tarih, kısa lead)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Item:
    source_id: str
    url: str
    title: str
    published_at: datetime | None = None
    lang: str | None = None
    excerpt: str | None = None
    extra: dict = field(default_factory=dict)
