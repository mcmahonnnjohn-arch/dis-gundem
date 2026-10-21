"""Jeopolitik Harita: olayları (kümeleri) yer, olay türü ve aktörlere bağlama (0008_harita.sql).

Harita ayrı bir veri hattı değildir; `olay` adımından sonra özetli kümeler tek LLM çağrısında (en fazla BATCH olay)
türe, yerlere, aktörlere ve "Türkiye için anlamı" satırına çevrilir.

Yer adları serbest metin olarak güvenilmez ("Tal Rifaat", "Tel Rıfat", "تل رفعت"). Model önce sözlükten id seçer;
seçemediği adı yerelde takma adlarla eşleştiririz; o da olmazsa ad `place_unresolved`a düşer ve editör eşler.
Sözlük: data/sozluk/yerler_*.csv (ülke başına bir dosya) ve data/sozluk/aktorler.csv.
"""
from __future__ import annotations

import csv
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

from .classify import _parse
from .config import PROMPTS, ROOT

log = logging.getLogger(__name__)

PROMPT_VERSION = "harita_v1"
SOZLUK = ROOT / "data" / "sozluk"
BATCH = 8
EVENT_TYPES = {"catisma", "saldiri", "diplomasi", "anlasma", "ekonomi", "enerji", "secim", "protesto",
               "askeri_hareket", "insani", "yargi_guvenlik", "siyasi"}
ROLES = {"fail", "hedef", "arabulucu", "taraf"}
MAX_STAKE = 160


@dataclass(frozen=True)
class Place:
    id: str
    name_tr: str
    aliases: tuple[str, ...]
    country_id: str
    kind: str
    precision: str
    lat: float
    lon: float
    verified: bool

    def row(self) -> dict:
        return {"id": self.id, "name_tr": self.name_tr, "aliases": list(self.aliases), "country_id": self.country_id,
                "kind": self.kind, "precision": self.precision, "verified": self.verified,
                "geom": f"SRID=4326;POINT({self.lon} {self.lat})"}


@dataclass(frozen=True)
class Actor:
    id: str
    name_tr: str
    kind: str
    country_id: str
    aliases: tuple[str, ...]
    active: bool

    def row(self) -> dict:
        return {"id": self.id, "name_tr": self.name_tr, "kind": self.kind, "country_id": self.country_id or None,
                "aliases": list(self.aliases), "active": self.active}


# ------------------------------------------------------------------ sözlükler
@lru_cache(maxsize=1)
def places() -> dict[str, Place]:
    out: dict[str, Place] = {}
    for path in sorted(SOZLUK.glob("yerler_*.csv")):
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                out[r["id"]] = Place(r["id"], r["name_tr"], tuple(a for a in r["aliases"].split("|") if a),
                                     r["country_id"], r["kind"], r["precision"], float(r["lat"]), float(r["lon"]),
                                     r["verified"].strip().lower() == "true")
    return out


@lru_cache(maxsize=1)
def actors() -> dict[str, Actor]:
    path = SOZLUK / "aktorler.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {r["id"]: Actor(r["id"], r["name_tr"], r["kind"], r["country_id"],
                               tuple(a for a in r["aliases"].split("|") if a), r["aktif"].strip() == "1")
                for r in csv.DictReader(f)}


_PREFIX = re.compile(r"^(al|el|es|er|ad|ed|as|ash|at|az|ar|an)[\s\-]+")
_ARABIC_AL = re.compile(r"^ال")


def norm(name: str) -> str:
    """Eşleştirme anahtarı: küçük harf, aksansız, Arapça harfi tarif ve tire/kesme yok.
    'Al-Qamishli' = 'Kamışlı' değil (farklı çeviriyazı) — onları takma ad listesi taşır; burada yalnız biçim farkı."""
    s = name.strip().replace("İ", "i").replace("I", "ı").lower()
    s = s.replace("ı", "i")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.replace("‘", "").replace("’", "").replace("'", "").replace("`", "")
    s = _ARABIC_AL.sub("", s)
    s = _PREFIX.sub("", s)
    return re.sub(r"[\s\-]+", " ", s).strip()


@lru_cache(maxsize=1)
def _index() -> dict[tuple[str, str], str]:
    """(ülke, normalize ad) → yer id. Aynı anahtar iki yere çıkarsa belirsizdir, ikisi de düşer."""
    idx: dict[tuple[str, str], str] = {}
    clash: set[tuple[str, str]] = set()
    for p in places().values():
        for n in {p.name_tr, *p.aliases}:
            k = (p.country_id, norm(n))
            if k in idx and idx[k] != p.id:
                clash.add(k)
            idx[k] = p.id
    for k in clash:
        idx.pop(k, None)
    return idx


@lru_cache(maxsize=1)
def _sea_index() -> dict[str, str]:
    """Boğaz, körfez gibi ülkeler arası deniz alanları: model ülkeyi yanlış verse de ('ir' yerine 'om') adı eşleşir."""
    return {norm(n): p.id for p in places().values() if p.kind == "deniz_alani" for n in {p.name_tr, *p.aliases}}


def resolve(name: str, country: str | None) -> str | None:
    if not name:
        return None
    idx = _index()
    if country:
        return idx.get((country, norm(name))) or _sea_index().get(norm(name))
    hits = {v for (c, n), v in idx.items() if n == norm(name)}
    return hits.pop() if len(hits) == 1 else None


def _places_block() -> str:
    by_c: dict[str, list[str]] = {}
    for p in places().values():
        by_c.setdefault(p.country_id, []).append(f"{p.id}: {p.name_tr}")
    return "\n".join(f"- {c}: " + "; ".join(v) for c, v in sorted(by_c.items())) or "(boş)"


def _actors_block() -> str:
    return "\n".join(f"- {a.id}: {a.name_tr}" + ("" if a.active else " (feshedildi; yalnız geçmiş olaylar)")
                     for a in actors().values()) or "(boş)"


def system_prompt() -> str:
    text = (PROMPTS / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")
    return text.replace("{YERLER}", _places_block()).replace("{AKTORLER}", _actors_block())


# ------------------------------------------------------------------ çıkarım
@dataclass
class MapLinks:
    event_type: str | None
    places: list[tuple[str, bool]]          # (yer id, birincil)
    unresolved: list[tuple[str, str | None]]  # (ham ad, ülke)
    actors: list[tuple[str, str | None]]    # (aktör id, rol)
    turkey_stake: str | None


def clean(raw: dict, fallback_country: str | None = None) -> MapLinks:
    """Model çıktısını doğrular. Kural: tam bir birincil yer; yoksa ilki, o da yoksa ülke kaydı."""
    t = raw.get("tur")
    etype = t if t in EVENT_TYPES else None
    known = places()
    got: list[tuple[str, bool]] = []
    unres: list[tuple[str, str | None]] = []
    for y in (raw.get("yerler") or [])[:3]:
        if not isinstance(y, dict):
            continue
        pid = y.get("id") if y.get("id") in known else None
        if not pid and (y.get("ad") or y.get("id")):
            name = y.get("ad") or y.get("id")
            pid = resolve(name, y.get("ulke") or fallback_country)
            if not pid:
                unres.append((str(name)[:120], y.get("ulke") or fallback_country))
                continue
        if pid and pid not in {g for g, _ in got}:
            got.append((pid, bool(y.get("birincil"))))
    if got:
        firsts = [i for i, (_, b) in enumerate(got) if b]
        k = firsts[0] if firsts else 0
        got = [(g, i == k) for i, (g, _) in enumerate(got)]
    elif fallback_country and fallback_country in known:
        got = [(fallback_country, True)]       # yer adı yok ya da çözülemedi: ülke merkezine
    acts = actors()
    act_out: list[tuple[str, str | None]] = []
    for a in (raw.get("aktorler") or [])[:5]:
        if isinstance(a, dict) and a.get("id") in acts and a["id"] not in {x for x, _ in act_out}:
            act_out.append((a["id"], a.get("rol") if a.get("rol") in ROLES else None))
    stake = raw.get("turkiye")
    stake = stake.strip()[:MAX_STAKE] if isinstance(stake, str) and stake.strip() else None
    return MapLinks(etype, got, unres, act_out, stake)


def extract(clf, events: list[dict]) -> dict[str, MapLinks]:
    """events: [{"k": küme id, "baslik", "ozet", "kaynak_basliklari", "ulke"}] → {küme id: MapLinks}."""
    if not events or clf.provider == "none" or not places():
        return {}
    system = system_prompt()
    out: dict[str, MapLinks] = {}
    for start in range(0, len(events), BATCH):
        chunk = events[start:start + BATCH]
        payload = [{"i": n, "baslik": e.get("baslik"), "ozet": e.get("ozet"),
                    "kaynak_basliklari": (e.get("kaynak_basliklari") or [])[:4]} for n, e in enumerate(chunk)]
        try:
            raw = _parse(clf._call(system, json.dumps(payload, ensure_ascii=False), model=clf.model, cache=True))
        except Exception as ex:
            log.warning("harita çıkarım hatası: %s", ex)
            continue
        for r in raw.get("olaylar") or []:
            try:
                e = chunk[int(r.get("i"))]
            except (TypeError, ValueError, IndexError):
                continue
            out[e["k"]] = clean(r, e.get("ulke"))
    return out
