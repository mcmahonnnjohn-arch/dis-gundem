"""LLM sınıflandırma. Sağlayıcıdan bağımsız: anthropic | openai | none.

`none` modunda yalnız terim filtresi çalışır (turkey_related), özet/önem üretilmez; kayıt yine kuyruğa düşer.
Prompt sürümü dosya adından gelir (classify_v1.md) ve her sınıflandırma çıktısına yazılır.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from .config import PROMPTS, Settings
from .fetch import Item
from .sources import FRAMES, KNOWN_DOSSIERS, KNOWN_THEMES, Source, clean_countries, clean_ids
from .terms import Matcher

log = logging.getLogger(__name__)
PROMPT_VERSION = "classify_v1"
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
    raw: dict = field(default_factory=dict)
    model: str = "terms"
    prompt_version: str = PROMPT_VERSION


def _system_prompt() -> str:
    return (PROMPTS / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")


def _user_prompt(item: Item, src: Source) -> str:
    return json.dumps({
        "baslik": item.title,
        "lead": item.excerpt or "",
        "kaynak": src.name,
        "kaynak_ulke": src.country_id,
        "kaynak_kapsam": src.tier,
        "kaynak_dil": item.lang or (src.langs[0] if src.langs else ""),
        "kaynak_egilim": src.lean_note[:200],
        "yayin_tarihi": item.published_at.isoformat() if item.published_at else None,
    }, ensure_ascii=False)


def _parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0) if m else text)


class Classifier:
    def __init__(self, s: Settings, matcher: Matcher | None = None):
        self.s = s
        self.matcher = matcher or Matcher()
        self.provider = s.llm_provider
        self._client = None
        try:
            if self.provider == "anthropic" and s.anthropic_key:
                import anthropic
                self._client = anthropic.Anthropic(api_key=s.anthropic_key)
                self.model = s.llm_model or "claude-haiku-5-5"
                return
            if self.provider == "openai" and s.openai_key:
                import openai
                self._client = openai.OpenAI(api_key=s.openai_key)
                self.model = s.llm_model or "gpt-5-mini"
                return
        except ImportError as e:  # paket kurulu değilse hat durmaz; terim filtresine düşer
            log.error("LLM paketi yok (%s); `pip install -e './pipeline[llm]'` gerekli. Terim filtresi kullanılıyor.", e)
        self.provider = "none"
        self.model = "terms"

    def _call(self, system: str, user: str) -> str:
        if self.provider == "anthropic":
            # Eleme/sınıflandırma kısa, yapılandırılmış JSON: düşünme kapalı (bütçeyi yiyip yanıtı kesiyordu),
            # 40 başlıklık parti için yeterli çıktı payı.
            r = self._client.messages.create(model=self.model, max_tokens=8000, system=system,
                                             thinking={"type": "disabled"},
                                             messages=[{"role": "user", "content": user}])
            # Yanıt düşünme (thinking) bloğuyla başlayabilir; yalnız metin bloklarını birleştir.
            return "".join(b.text for b in r.content if getattr(b, "type", None) == "text")
        r = self._client.chat.completions.create(model=self.model, messages=[
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

    def classify(self, item: Item, src: Source) -> Classification:
        hit = self.matcher.hit(f"{item.title} {item.excerpt or ''}", item.lang)
        if self.provider == "none":
            return Classification(turkey_related=hit, countries=[src.country_id], publishable=hit,
                                  confidence=0.3 if hit else 0.1)
        try:
            raw = _parse(self._call(_system_prompt(), _user_prompt(item, src)))
        except Exception as e:  # LLM hatası hattı durdurmaz; terim sonucu ile devam
            log.warning("%s sınıflandırma hatası: %s", item.url, e)
            return Classification(turkey_related=hit, countries=[src.country_id], publishable=False,
                                  confidence=0.0, raw={"error": str(e)})
        imp = raw.get("importance")
        return Classification(
            turkey_related=bool(raw.get("turkey_related", hit)),
            countries=clean_countries(raw.get("countries"), src.country_id),
            importance=int(imp) if isinstance(imp, (int, float)) else None,
            themes=clean_ids(raw.get("themes"), KNOWN_THEMES),
            dossiers=clean_ids(raw.get("dossiers"), KNOWN_DOSSIERS),
            frame=raw.get("frame") if raw.get("frame") in FRAMES else None,
            summary_tr=raw.get("summary_tr"),
            local_view_note=raw.get("local_view_note"),
            confidence=float(raw.get("confidence", 0.5)),
            publishable=bool(raw.get("publishable", False)),
            raw=raw, model=self.model,
        )
