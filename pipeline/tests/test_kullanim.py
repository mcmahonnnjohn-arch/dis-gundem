"""Token ve maliyet kaydı: OpenRouter gerçek maliyeti, Claude tahmini maliyeti, hakem/hat ayrımı, eval raporu."""
import json
import sys
from types import SimpleNamespace

import pytest

from disgundem import evaluate
from disgundem.classify import Classifier, estimate_cost
from disgundem.config import Settings


def _usage(prompt=0, completion=0, cached=0, cost=None):
    return SimpleNamespace(prompt_tokens=prompt, completion_tokens=completion, cost=cost,
                           prompt_tokens_details=SimpleNamespace(cached_tokens=cached, cache_write_tokens=0))


class FakeOpenAI:
    """Her çağrıda sıradaki (içerik, kullanım) ikilisini döndürür."""
    def __init__(self, **kw):
        self.queue = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        content, usage = self.queue.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))], usage=usage)


@pytest.fixture
def openrouter_clf(monkeypatch):
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    return Classifier(Settings(llm_provider="openrouter", openrouter_key="k",
                               summary_model="z-ai/glm-5.2", judge_model="judge/model"))


def test_openrouter_reported_cost_and_tokens_accumulate(openrouter_clf):
    c = openrouter_clf
    c._client.queue = [("{}", _usage(1000, 200, cached=400, cost=0.002)), ("{}", _usage(500, 100, cost=0.001))]
    c._call("s", "u", model="z-ai/glm-5.2")
    c._call("s", "u", model="z-ai/glm-5.2")
    u = c.usage_report()["hat"]["z-ai/glm-5.2"]
    assert (u["cagri"], u["girdi"], u["onbellek"], u["cikti"]) == (2, 1100, 400, 300)   # girdi = prompt - önbellek
    assert u["maliyet"] == pytest.approx(0.003) and u["tahmini"] is False


def test_missing_usage_is_tolerated(openrouter_clf):
    openrouter_clf._client.queue = [("{}", None)]
    assert openrouter_clf._call("s", "u") == "{}"
    assert openrouter_clf.usage_report() == {}


def test_estimate_cost_from_price_table():
    # Haiku 5.5: 0,10 / 0,50 / önbellek 0,01 ($ / 1M token)
    assert estimate_cost("claude-haiku-5-5", 1_000_000, 1_000_000) == pytest.approx(0.60)
    assert estimate_cost("claude-haiku-5-5", 0, 0, onbellek=1_000_000) == pytest.approx(0.01)
    assert estimate_cost("bilinmeyen/model", 1000, 1000) is None


def test_anthropic_usage_is_estimated_and_flagged():
    clf = Classifier(Settings())
    clf.provider = "anthropic"
    reply = SimpleNamespace(content=[SimpleNamespace(type="text", text="{}")],
                            usage=SimpleNamespace(input_tokens=1_000_000, output_tokens=1_000_000,
                                                  cache_read_input_tokens=0, cache_creation_input_tokens=0))
    clf._client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: reply))
    clf._call("s", "u", model="claude-haiku-5-5")
    u = clf.usage_report()["hat"]["claude-haiku-5-5"]
    assert u["maliyet"] == pytest.approx(0.60) and u["tahmini"] is True


def test_unpriced_model_makes_total_unknown(openrouter_clf):
    c = openrouter_clf
    c.provider = "openai"            # doğrudan OpenAI yolu: yanıtta maliyet beklenmez, tabloda da yok
    c._client.queue = [("{}", _usage(100, 10))]
    c._call("s", "u", model="gpt-5-mini")
    k = evaluate.usage_summary(c, 5)
    assert k["hat_usd"] is None and k["hat_usd_haber"] is None


def test_judge_cost_is_separated_from_pipeline_cost(openrouter_clf):
    c = openrouter_clf
    verdict = json.dumps({"dogruluk": 4, "kapsam": 4, "atif": 5, "hatalar": []})
    c._client.queue = [("{}", _usage(1000, 100, cost=0.004)), (verdict, _usage(2000, 50, cost=0.010))]
    c._call("s", "u", model=c.summary_model)                                   # hat
    evaluate.judge(c, {"baslik": "b", "referans_ozet": "r", "source_id": "yok"}, "aday")   # hakem
    k = evaluate.usage_summary(c, 2)
    assert k["hat_usd"] == pytest.approx(0.004) and k["hakem_usd"] == pytest.approx(0.010)
    assert k["hat_usd_haber"] == pytest.approx(0.002)
    assert "judge/model" in k["ayrinti"]["hakem"] and "z-ai/glm-5.2" in k["ayrinti"]["hat"]
    assert c.rol == "hat"            # hakem sonrası rol geri alınır


def test_report_includes_usage_section(openrouter_clf):
    c = openrouter_clf
    c._client.queue = [("{}", _usage(1000, 100, cost=0.004))]
    c._call("s", "u", model=c.summary_model)
    agg = {"n": 0, "olmali_oran": None, "ihlal_orani": 0, "bicim_ok": 0, "surec_orani": 0, "dogruluk": None,
           "kapsam": None, "atif": None, "dil": {}, "kullanim": evaluate.usage_summary(c, 1)}
    md = evaluate.report_md({"prompt": "p", "denetim": "d", "model": "m"}, agg, [])
    assert "## Kullanım ve maliyet" in md and "z-ai/glm-5.2" in md and "$0.0040" in md
