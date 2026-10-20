"""LLM sınıflandırma. Sağlayıcıdan bağımsız: anthropic | openai | none.

`none` modunda yalnız terim filtresi çalışır (turkey_related), özet/önem üretilmez; kayıt yine kuyruğa düşer.
Prompt sürümü dosya adından gelir (classify_v1.md) ve her sınıflandırma çıktısına yazılır.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from . import glossary
from .config import PROMPTS, Settings
from .fetch import Item
from .sources import FRAMES, KNOWN_DOSSIERS, KNOWN_THEMES, Source, clean_countries, clean_ids
from .terms import Matcher

log = logging.getLogger(__name__)
PROMPT_VERSION = "classify_v3"   # v2: makale metni, sözlük, kılavuz, uyarılar; v3: kesin 3 cümle / 600 kr
AUDIT_VERSION = "denetim_v2"     # v2: yalnız yanıltıcı hatalar, her sorun özetten birebir ifadeye dayanır
AUDIT_TYPES = {"desteksiz", "ad", "unvan", "sayi", "atif", "uslup", "adlandirma"}
MAX_SUMMARY = 600
MAX_SENTENCES = 3
MODEL_WARNINGS = {"sozlukte_yok", "tek_kaynak", "dusuk_guven"}
THINKING_OFF = {"type": "disabled"}
# Bazı modeller (ör. Sonnet 5.5) düşünmeyi kapatmak için farklı değer ister; API hata mesajı bunu söyler.
THINKING_OFF_ALT = {"type": "between_tools"}
TRIAGE_VERSION = "triage_v3"  # v2: eko işareti; v3: birincil ülke ilk sırada, ikili gerilim satırı


@dataclass
class Classification:
    turkey_related: bool
    countries: list[str] = field(default_factory=list)
    importance: int | None = None
    themes: list[str] = field(default_factory=list)
    dossiers: list[str] = field(default_factory=list)
    frame: str | None = None
    summary_tr: str | None = None
    local_view_note: str | None = None
    confidence: float = 0.0
    publishable: bool = False
    warnings: list[str] = field(default_factory=list)
    audit: dict | None = None
    raw: dict = field(default_factory=dict)
    model: str = "terms"
    prompt_version: str = PROMPT_VERSION


def _with_glossary(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8").replace("{SOZLUK}", glossary.block() or "(boş)")


def _system_prompt() -> str:
    return _with_glossary(PROMPT_VERSION)


def _user_prompt(item: Item, src: Source, text: str | None = None) -> str:
    return json.dumps({
        "baslik": item.title,
        "lead": item.excerpt or "",
        "metin": text or "",
        "kaynak": src.name,
        "kaynak_ulke": src.country_id,
        "kaynak_kapsam": src.tier,
        "kaynak_dil": item.lang or (src.langs[0] if src.langs else ""),
        "kaynak_egilim": src.lean_note[:200],
        "yayin_tarihi": item.published_at.isoformat() if item.published_at else None,
    }, ensure_ascii=False)


def _norm(t: str) -> str:
    return " ".join((t or "").split()).strip(" .,;:\"'«»“”‘’").lower()


def fit_summary(text: str | None) -> str | None:
    """Kılavuz sınırı: en fazla 3 cümle ve 600 karakter; kesme cümle sınırında (kelime ortasında değil)."""
    if not text:
        return text
    text = " ".join(text.split())
    sents = re.split(r"(?<=[.!?…])\s+(?=[A-ZÇĞİÖŞÜ0-9\"'«“(])", text)
    out = ""
    for sn in sents[:MAX_SENTENCES]:
        cand = f"{out} {sn}".strip()
        if len(cand) > MAX_SUMMARY:
            break
        out = cand
    if not out:   # tek cümle bile sığmıyor: kelime sınırında kes
        out = text[:MAX_SUMMARY - 1].rsplit(" ", 1)[0] + "…"
    return out


def _parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)


class Classifier:
    def __init__(self, s: Settings, matcher: Matcher | None = None):
        self.s = s
        self.matcher = matcher or Matcher()
        self.provider = s.llm_provider
        self._client = None
        self._thinking: dict[str, dict] = {}   # model → kabul edilen "düşünme kapalı" değeri
        try:
            if self.provider == "anthropic" and s.anthropic_key:
                import anthropic
                self._client = anthropic.Anthropic(api_key=s.anthropic_key)
                self.model = s.llm_model or "claude-haiku-5-5"
                self.summary_model = s.summary_model or "claude-sonnet-5-5"
                return
            if self.provider == "openai" and s.openai_key:
                import openai
                self._client = openai.OpenAI(api_key=s.openai_key)
                self.model = s.llm_model or "gpt-5-mini"
                self.summary_model = s.summary_model or self.model
                return
        except ImportError as e:  # paket kurulu değilse hat durmaz; terim filtresine düşer
            log.error("LLM paketi yok (%s); `pip install -e './pipeline[llm]'` gerekli. Terim filtresi kullanılıyor.", e)
        self.provider = "none"
        self.model = "terms"
        self.summary_model = "terms"

    def _call(self, system: str, user: str, model: str | None = None, cache: bool = False) -> str:
        model = model or self.model
        if self.provider == "anthropic":
            # Eleme/sınıflandırma kısa, yapılandırılmış JSON: düşünme kapalı (bütçeyi yiyip yanıtı kesiyordu),
            # 40 başlıklık parti için yeterli çıktı payı. Özet/denetimde sistem promptu (kurallar + sözlük) her
            # çağrıda aynı: önbelleğe alınır.
            sys_arg = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}] if cache else system
            kw = dict(model=model, max_tokens=8000, system=sys_arg, messages=[{"role": "user", "content": user}])
            try:
                r = self._client.messages.create(thinking=self._thinking.get(model, THINKING_OFF), **kw)
            except Exception as e:
                if "between_tools" not in str(e) or self._thinking.get(model) == THINKING_OFF_ALT:
                    raise
                self._thinking[model] = THINKING_OFF_ALT
                r = self._client.messages.create(thinking=THINKING_OFF_ALT, **kw)
            # Yanıt düşünme (thinking) bloğuyla başlayabilir; yalnız metin bloklarını birleştir.
            return "".join(b.text for b in r.content if getattr(b, "type", None) == "text")
        r = self._client.chat.completions.create(model=model, messages=[
            {"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"})
        return r.choices[0].message.content

    def triage(self, batch: list[tuple[Item, dict]]) -> list[dict]:
        """Toplu ön eleme: yalnız başlık + kaynak bilgisi; dönen her öğe {"imp", "tr", "eko", "c"}.

        LLM yoksa (provider=none) terim eşleşmesine göre kaba puan: Türkiye terimi varsa 3, yoksa 1.
        Bu modda A kapsamı iç gündem değerlendirilemez; bilerek düşer.
        """
        if not batch:
            return []
        if self.provider == "none":
            out = []
            for it, src in batch:
                hit = self.matcher.hit(f"{it.title} {it.excerpt or ''}", it.lang)
                out.append({"imp": 3 if hit else 1, "tr": hit, "eko": False, "c": [src["country_id"]], "model": "terms"})
            return out
        lines = [{"i": n, "baslik": it.title[:300], "kaynak": src["name"], "ulke": src["country_id"], "kapsam": src["tier"]}
                 for n, (it, src) in enumerate(batch)]
        system = (PROMPTS / f"{TRIAGE_VERSION}.md").read_text(encoding="utf-8")
        try:
            raw = _parse(self._call(system, json.dumps(lines, ensure_ascii=False)))
            by_i = {int(x["i"]): x for x in raw.get("items", []) if "i" in x}
        except Exception as e:
            log.warning("triage hatası (%d başlık): %s; terim filtresine düşülüyor", len(batch), e)
            by_i = {}
        out = []
        for n, (it, src) in enumerate(batch):
            x = by_i.get(n)
            if x is None:  # model atladıysa güvenli taraf: terim eşleşmesi
                hit = self.matcher.hit(it.title, it.lang)
                out.append({"imp": 3 if hit else 1, "tr": hit, "eko": False, "c": [src["country_id"]], "model": "terms-fallback"})
            else:
                out.append({"imp": int(x.get("imp", 1)), "tr": bool(x.get("tr")), "eko": bool(x.get("eko")),
                            "c": clean_countries(x.get("c"), src["country_id"]),
                            "model": self.model})
        return out

    def audit(self, item: Item, text: str | None, summary: str) -> dict:
        """Özeti kaynağa karşı denetler: {"gecti", "sorunlar", "duzeltilmis_ozet"}. Hata olursa gecti=None."""
        user = json.dumps({"kaynak": {"baslik": item.title, "lead": item.excerpt or "", "metin": text or ""},
                           "ozet": summary}, ensure_ascii=False)
        try:
            raw = _parse(self._call(_with_glossary(AUDIT_VERSION), user, model=self.summary_model, cache=True))
        except Exception as e:
            log.warning("%s denetim hatası: %s", item.url, e)
            return {"gecti": None, "sorunlar": [], "duzeltilmis_ozet": None, "hata": str(e)[:200]}
        # Yalnız özette birebir geçen bir ifadeye dayanan, tanımlı türdeki sorunlar sayılır; "eksik", "sorun yok"
        # türü gözlemler ve özette olmayan alıntılar atılır (ilk denemede 32 özetin 30'u gereksiz işaretlendi).
        summ = _norm(summary)
        sorunlar, atilan = [], 0
        for x in raw.get("sorunlar") or []:
            ok = (isinstance(x, dict) and x.get("tur") in AUDIT_TYPES
                  and len(_norm(x.get("ozet_ifadesi"))) >= 3 and _norm(x.get("ozet_ifadesi")) in summ)
            if ok:
                sorunlar.append(x)
            else:
                atilan += 1
        fixed = raw.get("duzeltilmis_ozet")
        return {"gecti": not sorunlar, "sorunlar": sorunlar, "atilan": atilan,
                "duzeltilmis_ozet": fixed if sorunlar and isinstance(fixed, str) and fixed.strip() else None}

    def classify(self, item: Item, src: Source, text: str | None = None, audit: bool = True) -> Classification:
        """Kuyruk haberi için sınıflandırma + Türkçe özet. `text` makale metnidir; yalnız bu çağrıda kullanılır."""
        hit = self.matcher.hit(f"{item.title} {item.excerpt or ''}", item.lang)
        if self.provider == "none":
            return Classification(turkey_related=hit, countries=[src.country_id], publishable=hit,
                                  confidence=0.3 if hit else 0.1)
        try:
            raw = _parse(self._call(_system_prompt(), _user_prompt(item, src, text),
                                    model=self.summary_model, cache=True))
        except Exception as e:  # LLM hatası hattı durdurmaz; terim sonucu ile devam
            log.warning("%s sınıflandırma hatası: %s", item.url, e)
            return Classification(turkey_related=hit, countries=[src.country_id], publishable=False,
                                  confidence=0.0, raw={"error": str(e)})
        imp = raw.get("importance")
        conf = float(raw.get("confidence", 0.5))
        summary = raw.get("summary_tr")
        warnings = [w for w in raw.get("uyarilar") or [] if w in MODEL_WARNINGS]
        if raw.get("sozlukte_olmayanlar") and "sozlukte_yok" not in warnings:
            warnings.append("sozlukte_yok")
        if not text:
            warnings.append("metin_yok")
        if conf < 0.6 and "dusuk_guven" not in warnings:
            warnings.append("dusuk_guven")
        audit_res = None
        if audit and summary:
            summary = fit_summary(summary)
            audit_res = self.audit(item, text, summary)
            if audit_res["gecti"] is False:
                warnings.append("denetim")
                if audit_res["duzeltilmis_ozet"]:
                    audit_res["ilk_ozet"] = summary
                    summary = audit_res["duzeltilmis_ozet"]
        summary = fit_summary(summary)
        return Classification(
            turkey_related=bool(raw.get("turkey_related", hit)),
            countries=clean_countries(raw.get("countries"), src.country_id),
            importance=int(imp) if isinstance(imp, (int, float)) else None,
            themes=clean_ids(raw.get("themes"), KNOWN_THEMES),
            dossiers=clean_ids(raw.get("dossiers"), KNOWN_DOSSIERS),
            frame=raw.get("frame") if raw.get("frame") in FRAMES else None,
            summary_tr=summary,
            local_view_note=raw.get("local_view_note"),
            confidence=conf,
            publishable=bool(raw.get("publishable", False)),
            warnings=sorted(set(warnings)), audit=audit_res,
            raw=raw, model=self.summary_model,
        )
