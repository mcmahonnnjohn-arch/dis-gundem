"""Kaynak envanteri CSV'sini (data/kaynak_envanteri_v3.csv) şema kayıtlarına çevirir.

Ülke ve bölge sözlükleri burada tanımlıdır; CSV'de geçen her 'Ülke' değeri bir koda eşlenmek zorundadır
(eşlenmeyen değer seed'i durdurur, sessizce atlanmaz).
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import DATA

CSV_PATH = DATA / "kaynak_envanteri_v3.csv"

# (id, ad, sıra)
REGIONS = [
    ("levant-irak", "Levant & Irak", 10),
    ("dogu-akdeniz", "Doğu Akdeniz", 20),
    ("korfez-iran", "Körfez & İran", 30),
    ("kafkasya", "Kafkasya", 40),
    ("karadeniz-rusya", "Karadeniz & Rusya", 50),
    ("avrupa", "Avrupa", 60),
    ("kuzey-amerika", "Kuzey Amerika", 70),
    ("asya", "Asya", 80),
    ("afrika", "Afrika", 90),
    ("turkiye", "Türkiye", 95),
    ("kuresel", "Küresel", 99),
]
REGION_BY_NAME = {name: rid for rid, name, _ in REGIONS}

# CSV 'Ülke' → (kod, bölge, kapsam, grup mu, diller)
COUNTRIES: dict[str, tuple[str, str, str, bool, list[str]]] = {
    "Suriye": ("sy", "levant-irak", "A", False, ["ar"]),
    "Irak": ("iq", "levant-irak", "A", False, ["ar", "ku"]),
    "Lübnan": ("lb", "levant-irak", "A", False, ["ar", "fr"]),
    "Levant": ("levant", "levant-irak", "R", True, ["ar"]),
    "İsrail": ("il", "dogu-akdeniz", "A", False, ["he"]),
    "Yunanistan": ("gr", "dogu-akdeniz", "A", False, ["el"]),
    "GKRY": ("cy", "dogu-akdeniz", "A", False, ["el"]),
    "KKTC": ("kktc", "dogu-akdeniz", "T", False, ["tr"]),
    "Mısır": ("eg", "dogu-akdeniz", "A", False, ["ar"]),
    "Libya": ("ly", "dogu-akdeniz", "B", False, ["ar"]),
    "İran": ("ir", "korfez-iran", "A", False, ["fa"]),
    "Suudi Arabistan": ("sa", "korfez-iran", "A", False, ["ar"]),
    "Katar": ("qa", "korfez-iran", "B", False, ["ar"]),
    "BAE": ("ae", "korfez-iran", "B", False, ["ar"]),
    "Körfez": ("korfez", "korfez-iran", "R", True, ["ar"]),
    "MENA": ("mena", "korfez-iran", "R", True, ["ar", "en"]),
    "Azerbaycan": ("az", "kafkasya", "A", False, ["az", "ru"]),
    "Ermenistan": ("am", "kafkasya", "A", False, ["hy"]),
    "Gürcistan": ("ge", "kafkasya", "B", False, ["ka"]),
    "Kafkasya (bölgesel)": ("kafkasya", "kafkasya", "R", True, ["en", "ru"]),
    "Rusya": ("ru", "karadeniz-rusya", "A", False, ["ru"]),
    "Ukrayna": ("ua", "karadeniz-rusya", "A", False, ["uk"]),
    "Romanya": ("ro", "karadeniz-rusya", "B", False, ["ro"]),
    "Karadeniz (bölgesel)": ("karadeniz", "karadeniz-rusya", "R", True, ["en"]),
    "AB": ("eu", "avrupa", "B", False, ["en"]),
    "Almanya": ("de", "avrupa", "B", False, ["de"]),
    "Fransa": ("fr", "avrupa", "B", False, ["fr"]),
    "Birleşik Krallık": ("gb", "avrupa", "B", False, ["en"]),
    "İtalya": ("it", "avrupa", "B", False, ["it"]),
    "Hollanda": ("nl", "avrupa", "B", False, ["nl", "en"]),
    "Belçika": ("be", "avrupa", "B", False, ["en", "fr"]),
    "ABD": ("us", "kuzey-amerika", "B", False, ["en"]),
    "Çin": ("cn", "asya", "B", False, ["zh"]),
    "Hindistan": ("in", "asya", "B", False, ["en", "hi"]),
    "Pakistan": ("pk", "asya", "B", False, ["en", "ur"]),
    "Japonya": ("jp", "asya", "B", False, ["ja"]),
    "Asya-Pasifik (bölgesel)": ("asya-pasifik", "asya", "R", True, ["en"]),
    "Afrika (bölgesel)": ("afrika", "afrika", "R", True, ["en", "fr"]),
    "Somali": ("so", "afrika", "B", False, ["so", "en"]),
    "Etiyopya": ("et", "afrika", "B", False, ["am", "en"]),
    "Sudan": ("sd", "afrika", "B", False, ["ar", "en"]),
    "Nijerya": ("ng", "afrika", "B", False, ["en"]),
    "Cezayir": ("dz", "afrika", "B", False, ["ar", "fr"]),
    "Senegal": ("sn", "afrika", "B", False, ["fr"]),
    "Türkiye": ("tr", "turkiye", "T", False, ["tr"]),
    "Küresel": ("kuresel", "kuresel", "P", True, ["en"]),
}

DOSSIERS = [
    ("dogu-akdeniz", "Doğu Akdeniz", "Yunanistan, GKRY, Libya, Mısır, İsrail: deniz yetki alanları, enerji, askeri"),
    ("karadeniz", "Karadeniz", "Rusya, Ukrayna, Romanya, Bulgaristan: Boğazlar, tahıl, deniz güvenliği"),
    ("kurt-meselesi", "Kürt meselesi", "Suriye, Irak, İran: PKK/YPG/SDG, Erbil, sınır ötesi"),
    ("turk-devletleri", "Türk Devletleri Teşkilatı", "Azerbaycan, Orta Asya: TDT, Orta Koridor"),
    ("ab-turkiye", "AB–Türkiye", "Gümrük birliği, vize, genişleme, SAFE/savunma"),
    ("savunma-ihracati", "Savunma ihracatı", "SİHA, KAAN, deniz platformları; alıcı ülkeler"),
    ("yeniden-insa", "Suriye'nin yeniden inşası", "İhaleler, enerji, ulaştırma, Körfez sermayesi, Türk şirketleri"),
    ("goc", "Göç ve geri dönüş", "Suriyeliler, gönüllü geri dönüş, Avrupa sınır politikası"),
]

THEMES = [
    ("diplomasi", "Diplomasi", "Ziyaretler, anlaşmalar, forumlar, krizler"),
    ("guvenlik", "Güvenlik & savunma", "Operasyonlar, savunma ihracatı, NATO, PKK/YPG, askeri"),
    ("enerji", "Enerji", "Boru hatları, LNG, nükleer, elektrik, Doğu Akdeniz gazı"),
    ("ekonomi", "Ekonomi & yatırım", "Ticaret, müteahhitlik, yeniden inşa, finans"),
    ("goc", "Göç & diaspora", "Mülteciler, geri dönüş, vize, diaspora"),
    ("ic-gundem", "İç gündem", "A kapsamı: seçim, iktidar, kriz, protesto, yargı"),
    ("turkiye-bakis", "Türkiye'ye bakış", "Yabancı basında Türkiye çerçevelemesi"),
    ("yumusak-guc", "Yumuşak güç", "TİKA, Maarif, Diyanet, YTB, diziler, THY"),
    ("bolgesel-rekabet", "Bölgesel rekabet", "ABD, Rusya, Çin, İran, Körfez etkileşimi"),
]

STATUS_MAP = {"Çekirdek": "cekirdek", "Yedek": "yedek", "Kontrol et": "kontrol", "Pasif": "pasif", "Çıkarıldı": "cikarildi"}

# CSV 'Toplama' → fetch_method
def _method(row: dict) -> str:
    t = row.get("Toplama", "")
    feed = row.get("RSS / Besleme URL", "")
    if row.get("Kapsam") == "P":
        return "manual"   # premium: Claude in Chrome oturumuyla okunur, `disgundem premium-import` ile girilir
    if feed.startswith("http"):
        return "rss"
    if "scraping" in row.get("Besleme kapsamı / durumu", "").lower() or "sitemap" in row.get("Alternatif erişim", "").lower():
        return "scrape"
    return "gnews"  # yerel dil edisyonuyla Google News RSS; en ucuz yedek


PERSPECTIVE_HINTS = ("bakış açısı", "propaganda", "düşmanca")

VERIFICATION_COLS = [
    "Doğrulama", "Son 30 gün Türkiye hacmi", "Son 30 gün iç gündem hacmi", "Doğrulama tarihi (UTC)",
    "Doğrulama notu", "Besleme kapsamı / durumu", "Edisyon / besleme dili", "Alternatif erişim",
    "Yerel dil doğrulaması", "Bağlam kanıtı", "Gözlenen Türkiye başlık adayı", "Gözlenen dönem metadata kaydı",
    "Ölçüm kapsamı / kanıt",
]


@dataclass
class Source:
    id: str
    name: str
    url: str
    local_url: str | None
    feed_url: str | None
    tier: str
    region_id: str
    country_id: str
    kind: str
    reliability: str
    role: str
    langs: list[str]
    method: str
    status: str
    perspective_only: bool
    lean_note: str
    editor_note: str
    scan_interval: str
    verification: dict = field(default_factory=dict)

    def as_row(self) -> dict:
        d = self.__dict__.copy()
        return d


def _langs(s: str) -> list[str]:
    parts = re.split(r"[/,+ ]+", s.strip())
    return [p for p in parts if re.fullmatch(r"[a-z]{2,3}", p)]


KNOWN_COUNTRIES = {v[0] for v in COUNTRIES.values()}


def clean_countries(codes, fallback: str | None = None) -> list[str]:
    """LLM ya da oturum dosyasından gelen ülke kodlarını sözlükteki kodlara indirger (sıra korunur: ilk kod birincil).
    Sözlükte olmayan kod (ör. LLM'in 'jo', 'ye' döndürmesi) atılır; hiç kalmazsa kaynağın ülkesine düşülür.
    clusters.primary_country ve article_countries yabancı anahtarları bilinmeyen kodu reddeder."""
    out: list[str] = []
    for c in codes or []:
        c = str(c).strip().lower()
        if c in KNOWN_COUNTRIES and c not in out:
            out.append(c)
    if not out and fallback:
        out = [fallback]
    return out


KNOWN_THEMES = {t[0] for t in THEMES}
KNOWN_DOSSIERS = {d[0] for d in DOSSIERS}
FRAMES = {"olumlu", "olumsuz", "notr", "karisik"}


def clean_ids(values, known: set[str]) -> list[str]:
    """Tema/dosya kodlarını sözlüğe indirger (bilinmeyenler atılır; yabancı anahtar hatasını önler)."""
    out: list[str] = []
    for v in values or []:
        v = str(v).strip().lower()
        if v in known and v not in out:
            out.append(v)
    return out


def load_sources(path: Path = CSV_PATH) -> list[Source]:
    out: list[Source] = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            country = row["Ülke"]
            if country not in COUNTRIES:
                raise ValueError(f"{row['ID']}: eşlenmemiş ülke değeri {country!r} — sources.COUNTRIES'e ekle")
            code, region, _, _, _ = COUNTRIES[country]
            region_csv = REGION_BY_NAME.get(row["Bölge"])
            if region_csv and region_csv != region:
                region = region_csv  # CSV'deki bölge kazanır (ör. Libya Doğu Akdeniz)
            feed = row.get("RSS / Besleme URL", "").strip()
            local = row.get("Yerel dil URL", "").strip()
            note_blob = " ".join([row.get("Not", ""), row.get("Eğilim / Bağlam", "")]).lower()
            out.append(Source(
                id=row["ID"],
                name=row["Kaynak"],
                url=row["URL"],
                local_url=local if local.startswith("http") else None,
                feed_url=feed if feed.startswith("http") else None,
                tier=row["Kapsam"],
                region_id=region,
                country_id=code,
                kind=row.get("Tür", ""),
                reliability=row.get("Güv.", "B") or "B",
                role=row.get("İçerik rolü", ""),
                langs=_langs(row.get("Dil", "")),
                method=_method(row),
                status=STATUS_MAP.get(row.get("Durum", "Kontrol et"), "kontrol"),
                perspective_only=row.get("Güv.") == "C" and any(h in note_blob for h in PERSPECTIVE_HINTS),
                lean_note=row.get("Eğilim / Bağlam", ""),
                editor_note=row.get("Not", ""),
                scan_interval="1 week" if row.get("Tür") == "Think tank" else "1 hour",
                verification={k: row.get(k, "") for k in VERIFICATION_COLS},
            ))
    return out


def dictionaries() -> dict[str, list[dict]]:
    regions = [{"id": r, "name": n, "sort_order": o} for r, n, o in REGIONS]
    countries = [
        {"id": code, "name": name, "region_id": region, "scope": scope, "is_group": grp, "langs": langs}
        for name, (code, region, scope, grp, langs) in COUNTRIES.items()
    ]
    dossiers = [{"id": i, "name": n, "description": d} for i, n, d in DOSSIERS]
    themes = [{"id": i, "name": n, "description": d} for i, n, d in THEMES]
    return {"regions": regions, "countries": countries, "dossiers": dossiers, "themes": themes}
