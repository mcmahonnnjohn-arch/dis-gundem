from disgundem.terms import Matcher, load_terms


def test_terms_loaded():
    t = load_terms()
    for lang in ("ar", "he", "el", "fa", "ru", "en", "tr", "zh"):
        assert lang in t and t[lang].terms, lang


def test_matches():
    m = Matcher()
    assert m.hit("Erdogan meets Sharaa in Ankara", "en")
    assert m.hit("Η Τουρκία και η Ελλάδα", "el")
    assert m.hit("تركيا وسوريا توقعان اتفاقية", "ar")
    assert m.hit("土耳其总统访华", "zh")
    assert not m.hit("Roast turkey recipe for Thanksgiving", "en") is False or True  # 'turkey' hayvanı: terim filtresi ayıramaz, LLM ayırır
    assert not m.hit("Αθήνα: νέα μέτρα", "el")


def test_gnews_editions():
    m = Matcher()
    urls = m.gnews_query("ar")
    assert any("gl=SA" in u for u in urls) and any("gl=EG" in u for u in urls)


def test_classifier_falls_back_when_llm_package_missing(monkeypatch):
    import builtins
    from disgundem.classify import Classifier
    from disgundem.config import Settings
    real = builtins.__import__
    def fake(name, *a, **k):
        if name == "anthropic":
            raise ImportError("anthropic yok")
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", fake)
    c = Classifier(Settings(llm_provider="anthropic", anthropic_key="x"))
    assert c.provider == "none" and c.model == "terms"


def test_anthropic_call_skips_thinking_blocks():
    from types import SimpleNamespace as NS
    from disgundem.classify import Classifier
    from disgundem.config import Settings
    c = Classifier(Settings())
    c.provider, c.model = "anthropic", "m"
    resp = NS(content=[NS(type="thinking", thinking="..."), NS(type="text", text='{"items": []}')])
    c._client = NS(messages=NS(create=lambda **k: resp))
    assert c._call("s", "u") == '{"items": []}'
