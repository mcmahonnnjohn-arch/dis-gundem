"""Türkiye terim sözlüğü (data/turkiye_terimleri.csv) → dil başına derlenmiş desenler ve Google News edisyonları.

Terim eşleşmesi ucuz ön filtredir; nihai "Türkiye ile ilgili mi" kararı LLM'de (classify) verilir.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .config import DATA

TERMS_PATH = DATA / "turkiye_terimleri.csv"

LANG_CODE = {
    "Arapça": "ar", "İbranice": "he", "Yunanca": "el", "Farsça": "fa", "Azerice": "az", "Ermenice": "hy",
    "Rusça": "ru", "Ukraynaca": "uk", "İngilizce": "en", "Almanca": "de", "Fransızca": "fr", "Çince": "zh",
    "Hintçe": "hi", "Somalice": "so", "Kürtçe (Kurmancî)": "ku", "Türkçe": "tr",
}


@dataclass
class LangTerms:
    lang: str
    terms: list[str]
    editions: list[tuple[str, str]]   # (gl, hl)
    pattern: re.Pattern


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).casefold()


def _split(cell: str) -> list[str]:
    out = []
    for part in re.split(r"\s*/\s*", cell.strip()):
        part = part.strip()
        if part and not part.startswith("—"):
            out.append(part)
    return out


def _editions(cell: str) -> list[tuple[str, str]]:
    eds = []
    for m in re.finditer(r"\b([A-Z]{2}):([a-z]{2}(?:-[A-Za-z]+)?)\b", cell):
        eds.append((m.group(1), m.group(2)))
    return eds


def load_terms(path: Path = TERMS_PATH) -> dict[str, LangTerms]:
    out: dict[str, LangTerms] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            lang = LANG_CODE.get(row["Dil"].strip())
            if not lang:
                continue
            terms: list[str] = []
            for col in ("Türkiye", "Ankara", "Erdoğan", "Türk (sıfat)"):
                terms += _split(row.get(col, ""))
            terms = list(dict.fromkeys(t for t in terms if t))
            if lang == "zh":
                pat = "|".join(re.escape(_norm(t)) for t in terms)
            else:
                pat = r"(?<!\w)(?:" + "|".join(re.escape(_norm(t)) for t in terms) + r")(?!\w)"
            out[lang] = LangTerms(
                lang=lang, terms=terms, editions=_editions(row.get("Google News edisyonu (gl/hl/ceid)", "")),
                pattern=re.compile(pat),
            )
    return out


class Matcher:
    def __init__(self, terms: dict[str, LangTerms] | None = None):
        self.terms = terms or load_terms()
        self._all = re.compile("|".join(f"(?:{t.pattern.pattern})" for t in self.terms.values()))

    def hit(self, text: str, lang: str | None = None) -> bool:
        if not text:
            return False
        n = _norm(text)
        if lang and lang in self.terms:
            return bool(self.terms[lang].pattern.search(n))
        return bool(self._all.search(n))

    def gnews_query(self, lang: str, extra: str = "", days: int = 7) -> list[str]:
        """Dil edisyonu başına Google News RSS arama URL'leri."""
        lt = self.terms.get(lang) or self.terms["en"]
        q = " OR ".join(f'"{t}"' for t in lt.terms[:4])
        if extra:
            q = f"({q}) {extra}"
        q += f" when:{days}d"
        from urllib.parse import quote
        urls = []
        for gl, hl in lt.editions or [("US", "en")]:
            urls.append(f"https://news.google.com/rss/search?q={quote(q)}&hl={hl}&gl={gl}&ceid={gl}:{hl}")
        return urls
