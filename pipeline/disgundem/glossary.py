"""Varlık sözlüğü (data/sozluk/varliklar.csv) → özetleme promptuna giden başvuru bloğu.

Kaynak başlıkları Arapça, Yunanca, İbranice, Farsça… geldiği için Latin harfli anahtarla eşleştirme güvenilir değil.
Sözlük küçükken (≤ FULL_LIMIT satır) tamamı sistem promptuna eklenir ve önbelleğe alınır; büyüyünce yalnız
haber metninde geçen satırlar seçilir.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache

from .config import ROOT

PATH = ROOT / "data" / "sozluk" / "varliklar.csv"
FULL_LIMIT = 400


@dataclass(frozen=True)
class Entry:
    id: str
    tur: str
    ozgun: str
    tr: str
    unvan_tr: str
    ulke: str
    not_: str
    durum: str
    aciklama: str = ""

    def line(self) -> str:
        head = f"{self.tr}" + (f" — {self.unvan_tr}" if self.unvan_tr else "")
        alt = f" [özgün: {self.ozgun}]" if self.ozgun and self.ozgun != self.tr else ""
        flag = " (UNVAN DOĞRULANMADI: kaynakta yoksa unvan yazma)" if self.durum == "belirsiz" else ""
        note = f" · {self.not_}" if self.not_ else ""
        desc = f" · AÇIKLAMA (ilk geçişte parantez içinde ver): {self.aciklama}" if self.aciklama else ""
        return f"- {head}{alt}{flag}{desc}{note}"


@lru_cache(maxsize=1)
def load() -> tuple[Entry, ...]:
    if not PATH.exists():
        return ()
    with PATH.open(encoding="utf-8") as f:
        return tuple(Entry(r["id"], r["tur"], r["ozgun"], r["tr"], r["unvan_tr"], r["ulke"], r["not"], r["durum"],
                           r.get("kisa_aciklama") or "")
                     for r in csv.DictReader(f) if r.get("durum") != "eski")


def _matches(e: Entry, text: str) -> bool:
    low = text.lower()
    keys = {e.tr, e.ozgun, *e.tr.split(" / ")}
    return any(k and len(k) >= 4 and k.lower() in low for k in keys)


def block(text: str = "") -> str:
    """Prompta eklenecek sözlük metni. Boş metinle çağrılırsa (veya sözlük küçükse) tamamı."""
    rows = load()
    if len(rows) > FULL_LIMIT and text:
        rows = tuple(e for e in rows if _matches(e, text))
    if not rows:
        return ""
    groups = {"kisi": "Kişiler", "kurum": "Kurumlar", "orgut": "Örgütler", "belge": "Belgeler",
              "yer": "Yerler", "terim": "Terimler"}
    out = []
    for key, title in groups.items():
        lines = [e.line() for e in rows if e.tur == key]
        if lines:
            out.append(f"### {title}\n" + "\n".join(lines))
    return "\n\n".join(out)
