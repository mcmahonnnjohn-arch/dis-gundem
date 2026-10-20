"""Önem hunisi: toplanan ham akışın yalnız önemli kısmı veritabanına girer.

  ham başlıklar (kaynak başına, her çalıştırmada)
    │ 1. tekilleştirme      — daha önce görülen URL / başlık hash'i atlanır (seen_items)
    │ 2. ön filtre (ücretsiz) — A dışı kaynaklarda Türkiye terimi yoksa düşer; 3 günden eski kayıt düşer
    │ 3. toplu eleme (LLM)   — 40'lık partilerle yalnız başlık; önem 1-5 + Türkiye ilgisi
    │ 4. saklama eşiği       — önem < STORE_MIN (3) hiç saklanmaz, yalnız hash'i seen_items'a yazılır
    │ 5. kümeleme            — aynı olayı anlatan başlıklar tek kümede; kümenin önemi = en yüksek üye
    │ 6. kuyruk eşiği + tavan — önem ≥ QUEUE_MIN (4) olan kümeler; ülke başına ve günlük toplam tavanla
    ▼
  editör kuyruğu (günde ~15-30 küme hedefi)

Önem 3'ler saklanır ama kuyruğa girmez: ülke sayfasının "diğer gelişmeler" havuzu ve analiz hammaddesi;
editör isterse oradan çeker. Eşikler ve tavanlar .env / Actions vars ile değiştirilebilir.
"""
from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .fetch import Item
from .terms import Matcher


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass
class Gates:
    store_min: int = field(default_factory=lambda: _env_int("IMPORTANCE_STORE_MIN", 3))
    queue_min: int = field(default_factory=lambda: _env_int("IMPORTANCE_QUEUE_MIN", 4))
    # Ekonomik analizler (eko=True) kuyruğa daha düşük eşikle girer (20 Ekim editör kararı). Önem puanı değişmez;
    # sıralamada gerçek 4'lerin arkasında kalırlar, ülke/gün tavanı aynen uygulanır.
    econ_queue_min: int = field(default_factory=lambda: _env_int("ECON_QUEUE_MIN", 3))
    # Chrome oturumu (editör seçkisi) ayrı ve daha geniş kota kullanır; sunucunun kotasını tüketmez (20 Ekim kararı).
    chrome_per_country_daily: int = field(default_factory=lambda: _env_int("CHROME_QUEUE_PER_COUNTRY_DAILY", 8))
    chrome_total_daily: int = field(default_factory=lambda: _env_int("CHROME_QUEUE_TOTAL_DAILY", 40))

    def for_chrome(self) -> "Gates":
        from dataclasses import replace
        return replace(self, per_country_daily=self.chrome_per_country_daily, total_daily=self.chrome_total_daily)
    per_country_daily: int = field(default_factory=lambda: _env_int("QUEUE_PER_COUNTRY_DAILY", 4))
    total_daily: int = field(default_factory=lambda: _env_int("QUEUE_TOTAL_DAILY", 30))
    max_age_days: int = field(default_factory=lambda: _env_int("MAX_ITEM_AGE_DAYS", 3))
    # Çalışma başına kaynak başına en yeni N başlık LLM'e gider (maliyet tavanı; IranWire gibi 800 kayıtlık akışlar).
    # Kalanlar görülmemiş sayılır, sonraki çalışmalarda sıraları gelir.
    max_items_per_source: int = field(default_factory=lambda: _env_int("MAX_ITEMS_PER_SOURCE", 30))
    batch_size: int = 40


# ---------------------------------------------------------------- 1. tekilleştirme
_STOP = re.compile(r"[^\w\s]", re.U)


def norm_title(t: str) -> str:
    t = unicodedata.normalize("NFKC", t).casefold()
    return " ".join(_STOP.sub(" ", t).split())


def title_hash(t: str) -> str:
    return hashlib.md5(norm_title(t).encode()).hexdigest()


# ---------------------------------------------------------------- 2. ön filtre
def prefilter(items: list[Item], src: dict, matcher: Matcher, g: Gates, now: datetime | None = None) -> list[Item]:
    now = now or datetime.now(timezone.utc)
    oldest = now - timedelta(days=g.max_age_days)
    out = []
    for it in items:
        if it.published_at and it.published_at < oldest:
            continue
        if src["tier"] != "A" and not matcher.hit(f"{it.title} {it.excerpt or ''}", it.lang):
            continue  # A dışında Türkiye geçmeyen başlık LLM'e bile gitmez
        out.append(it)
    out.sort(key=lambda it: it.published_at or now, reverse=True)
    return out[:g.max_items_per_source]


# ---------------------------------------------------------------- 5. kümeleme (başlık benzerliği)
def _tokens(t: str) -> set[str]:
    return {w for w in norm_title(t).split() if len(w) > 3}


def cluster(scored: list[dict], threshold: float = 0.45, window_h: int = 48) -> list[list[dict]]:
    """Ucuz ilk sürüm: başlık token Jaccard benzerliği, 48 saat penceresi.
    Farklı dillerdeki aynı olay burada birleşmez; embedding kümelemesi gelince (sonraki PR) birleşir."""
    groups: list[list[dict]] = []
    sigs: list[set[str]] = []
    for r in sorted(scored, key=lambda x: -x["imp"]):
        tk = _tokens(r["item"].title)
        placed = False
        for gi, sig in enumerate(sigs):
            if not tk or not sig:
                continue
            j = len(tk & sig) / len(tk | sig)
            t0 = groups[gi][0]["item"].published_at
            t1 = r["item"].published_at
            near = (t0 is None or t1 is None or abs((t0 - t1).total_seconds()) < window_h * 3600)
            if j >= threshold and near:
                groups[gi].append(r)
                sigs[gi] |= tk
                placed = True
                break
        if not placed:
            groups.append([r])
            sigs.append(set(tk))
    return groups


# ---------------------------------------------------------------- 6. kuyruk tavanı
def primary_country(grp: list[dict]) -> str:
    """Kümenin birincil ülkesi: en önemli öğenin ülke listesindeki ilk kod (sınıflandırma asıl ülkeyi başa yazar).
    Ülke kotası yalnız bunu sayar; ikincil anılan ülkeler kotayı tüketmez. 'tr' ise ülke kotası uygulanmaz
    (Türkiye merceği sitenin çekirdeği), yalnız günlük toplam tavan geçerlidir."""
    top = max(grp, key=lambda x: x["imp"])
    return (top.get("c") or ["tr"])[0]



def select_for_queue(groups: list[list[dict]], g: Gates, already_today: dict[str, int] | None = None,
                     total_today: int = 0) -> tuple[list[list[dict]], list[list[dict]]]:
    """Önemi en yüksek kümelerden başlayarak ülke ve günlük tavana kadar seçer.
    Dönen: (kuyruğa, havuza). Tavan yüzünden düşen ≥4 küme havuza gider, kaybolmaz."""
    per_c = defaultdict(int, already_today or {})
    total = total_today
    queue, pool = [], []
    ranked = sorted(groups, key=lambda grp: (-max(x["imp"] for x in grp), -len(grp)))
    for grp in ranked:
        imp = max(x["imp"] for x in grp)
        primary = primary_country(grp)
        threshold = g.econ_queue_min if any(x.get("eko") for x in grp) else g.queue_min
        if imp < threshold:
            pool.append(grp)
            continue
        country_full = primary != "tr" and per_c[primary] >= g.per_country_daily
        if imp < 5 and (total >= g.total_daily or country_full):
            pool.append(grp)   # 5'ler tavanı deler: savaş/rejim değişikliği kaçırılmaz
            continue
        queue.append(grp)
        total += 1
        if primary != "tr":
            per_c[primary] += 1
    return queue, pool
