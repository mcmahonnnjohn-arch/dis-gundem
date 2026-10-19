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
from .sources import Source
from .terms import Matcher

log = logging.getLogger(__name__)
PROMPT_VERSION = "classify_v1"


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
        if self.provider == "anthropic" and s.anthropic_key:
            import anthropic
            self._client = anthropic.Anthropic(api_key=s.anthropic_key)
            self.model = s.llm_model or "claude-haiku-5-5"
        elif self.provider == "openai" and s.openai_key:
            import openai
            self._client = openai.OpenAI(api_key=s.openai_key)
            self.model = s.llm_model or "gpt-5-mini"
        else:
            self.provider = "none"
            self.model = "terms"

    def _call(self, system: str, user: str) -> str:
        if self.provider == "anthropic":
            r = self._client.messages.create(model=self.model, max_tokens=600, system=system,
                                             messages=[{"role": "user", "content": user}])
            return r.content[0].text
        r = self._client.chat.completions.create(model=self.model, messages=[
            {"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"})
        return r.choices[0].message.content

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
            countries=[c for c in raw.get("countries", []) if isinstance(c, str)] or [src.country_id],
            importance=int(imp) if isinstance(imp, (int, float)) else None,
            themes=raw.get("themes", []) or [],
            dossiers=raw.get("dossiers", []) or [],
            frame=raw.get("frame"),
            summary_tr=raw.get("summary_tr"),
            local_view_note=raw.get("local_view_note"),
            confidence=float(raw.get("confidence", 0.5)),
            publishable=bool(raw.get("publishable", False)),
            raw=raw, model=self.model,
        )
