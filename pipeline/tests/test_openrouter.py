"""OpenRouter sağlayıcısı: istemci kurulumu, yedek model/ZDR gövdesi, sabit hakem modeli, eval CLI geçersiz kılmaları."""
import sys
from types import SimpleNamespace

import pytest

from disgundem import cli, evaluate
from disgundem.classify import Classifier
from disgundem.config import Settings


class FakeOpenAI:
    """`openai` paketinin yerine geçer (CI'da llm eklentisi kurulu değil). Son oluşturulan örneği saklar."""
    last = None

    def __init__(self, **kw):
        self.init_kw = kw
        self.calls = []
        self.reply = '{"ok": true}'
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        FakeOpenAI.last = self

    def _create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.reply))])


@pytest.fixture
def fake_openai(monkeypatch):
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    FakeOpenAI.last = None
    return FakeOpenAI


def _clf(**kw):
    return Classifier(Settings(llm_provider="openrouter", openrouter_key="sk-or-test", **kw))


def test_init_points_openai_client_at_openrouter(fake_openai):
    clf = _clf()
    assert clf.provider == "openrouter"
    assert fake_openai.last.init_kw["base_url"] == "https://openrouter.ai/api/v1"
    assert fake_openai.last.init_kw["api_key"] == "sk-or-test"
    # model verilmezse eleme varsayılanı; özet ve hakem sırayla ona düşer
    assert (clf.model, clf.summary_model, clf.judge_model) == ("deepseek/deepseek-chat",) * 3


def test_models_and_judge_are_independent(fake_openai):
    clf = _clf(llm_model="deepseek/deepseek-chat", summary_model="z-ai/glm-5.2", judge_model="anthropic/judge")
    assert (clf.model, clf.summary_model, clf.judge_model) == ("deepseek/deepseek-chat", "z-ai/glm-5.2", "anthropic/judge")


def test_missing_key_falls_back_to_terms(fake_openai):
    clf = Classifier(Settings(llm_provider="openrouter"))
    assert clf.provider == "none" and clf.judge_model == "terms"


def test_call_sends_deduped_fallbacks_and_zdr(fake_openai):
    clf = _clf(fallback_models=("z-ai/glm-5.2", "deepseek/deepseek-chat"), openrouter_zdr=True)
    out = clf._call("sistem", "kullanıcı", model="z-ai/glm-5.2")
    kw = fake_openai.last.calls[0]
    assert out == '{"ok": true}'
    assert kw["model"] == "z-ai/glm-5.2"
    assert kw["extra_body"] == {"models": ["z-ai/glm-5.2", "deepseek/deepseek-chat"], "provider": {"zdr": True}}
    assert kw["messages"][0] == {"role": "system", "content": "sistem"}


def test_call_has_no_extra_body_by_default_and_tolerates_empty_content(fake_openai):
    clf = _clf()
    fake_openai.last.reply = None
    assert clf._call("s", "u") == ""
    assert fake_openai.last.calls[0]["extra_body"] is None


def test_judge_uses_judge_model_not_candidate(monkeypatch):
    seen = {}

    def _call(system, user, model=None, cache=False):
        seen["model"] = model
        return '{"dogruluk": 4, "kapsam": 4, "atif": 5, "hatalar": []}'

    clf = SimpleNamespace(_call=_call, summary_model="z-ai/glm-5.2", judge_model="anthropic/judge")
    case = {"baslik": "b", "referans_ozet": "r", "source_id": "yok"}
    verdict = evaluate.judge(clf, case, "aday özet")
    assert seen["model"] == "anthropic/judge" and verdict["dogruluk"] == 4


def test_meta_records_openrouter_details(fake_openai):
    s = Settings(llm_provider="openrouter", openrouter_key="k", summary_model="z-ai/glm-5.2",
                 judge_model="anthropic/judge", fallback_models=("deepseek/deepseek-chat",))
    meta = evaluate.meta_for(Classifier(s), s)
    assert meta["saglayici"] == "openrouter" and meta["hakem_modeli"] == "anthropic/judge"
    assert meta["model"] == "z-ai/glm-5.2" and meta["yedekler"] == ["deepseek/deepseek-chat"]


def test_eval_cli_flags_override_settings(monkeypatch):
    got = {}
    monkeypatch.setattr(cli, "cmd_eval", lambda s, args: got.update(s=s, args=args))
    cli.main(["eval", "--saglayici", "openrouter", "--model", "a/x", "--ozet-modeli", "b/y",
              "--hakem-modeli", "c/z", "--etiket", "glm"])
    s = got["s"]
    assert (s.llm_provider, s.llm_model, s.summary_model, s.judge_model) == ("openrouter", "a/x", "b/y", "c/z")


def test_eval_cli_without_flags_keeps_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("JUDGE_MODEL", "")
    got = {}
    monkeypatch.setattr(cli, "cmd_eval", lambda s, args: got.update(s=s))
    cli.main(["eval"])
    assert got["s"].llm_provider == "anthropic" and got["s"].judge_model == ""
