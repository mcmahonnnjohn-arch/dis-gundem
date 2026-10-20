"""classify_v2: makale metni çıkarımı, sözlük bloğu, denetim düzeltmesi, metnin saklanmaması."""
import json
from types import SimpleNamespace

import httpx

from disgundem import cli, glossary
from disgundem.classify import Classifier
from disgundem.config import Settings
from disgundem.fetch import Item
from disgundem.fetch import article
from disgundem.fetch.article import extract, fetch_text

BODY = "Libya Temsilciler Meclisi deniz yetki alanları mutabakatını oybirliğiyle onayladı. " * 12


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def test_extract_prefers_jsonld():
    html = f'<html><script type="application/ld+json">{json.dumps({"@graph": [{"articleBody": BODY}]})}</script>' \
           '<body><p>kısa</p></body></html>'
    assert extract(html).startswith("Libya Temsilciler")


def test_extract_paragraph_density_skips_nav():
    paras = "".join(f"<p>{BODY[:200]} {i}</p>" for i in range(5))
    html = f"<html><body><nav><p>{'menü bağlantısı ' * 10}</p></nav><div class='x'>{paras}</div></body></html>"
    text = extract(html)
    assert text and "menü" not in text and text.count("\n") == 4


def test_extract_paywall_and_short_is_none():
    assert extract("<html><body><p>Subscribe to continue reading this exclusive story today.</p></body></html>") is None


def test_fetch_text_respects_robots_and_skips_gnews():
    article._robots.clear()

    def h(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /private/")
        return httpx.Response(200, text=f"<html><body><article><p>{BODY}</p></article></body></html>")

    c = _client(h)
    assert fetch_text(c, "https://ex.com/private/a", "Bot")[1] == "robots"
    text, st = fetch_text(c, "https://ex.com/news/a", "Bot")
    assert st == "ok" and "Temsilciler" in text
    assert fetch_text(c, "https://news.google.com/rss/articles/x", "Bot") == (None, "atlandi")


def test_glossary_block_flags_unverified():
    glossary.load.cache_clear()
    b = glossary.block()
    assert "Mücteba Hamaney" in b and "### Kişiler" in b
    assert "UNVAN DOĞRULANMADI" in b          # belirsiz satırlar işaretli


class FakeAnthropic:
    """İlk çağrı özet, ikinci çağrı denetim döndürür."""
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(self.replies.pop(0)))])


def _clf(replies):
    clf = Classifier(Settings())
    clf.provider, clf.model, clf.summary_model = "anthropic", "haiku", "sonnet"
    clf._client = FakeAnthropic(replies)
    return clf


SRC = SimpleNamespace(name="Al-Wasat", country_id="ly", tier="A", langs=["ar"], lean_note="")
ITEM = Item(source_id="K262", url="https://ex.com/a", title="الكوني يرحب", lang="ar")


def test_audit_failure_replaces_summary_and_flags():
    first = {"turkey_related": True, "countries": ["ly", "tr"], "summary_tr": "Ulusal Mutabakat Hükümeti memnun.",
             "uyarilar": [], "sozlukte_olmayanlar": [], "confidence": 0.8, "publishable": True}
    audit = {"gecti": False, "sorunlar": [{"tur": "unvan", "ozet_ifadesi": "Ulusal Mutabakat Hükümeti",
                                           "aciklama": "UMH 2021'de sona erdi"}],
             "duzeltilmis_ozet": "Libya Başkanlık Konseyi Başkan Yardımcısı Musa el-Koni onayı memnuniyetle karşıladı."}
    clf = _clf([first, audit])
    c = clf.classify(ITEM, SRC, text=BODY)
    assert c.summary_tr.startswith("Libya Başkanlık Konseyi")
    assert "denetim" in c.warnings and "metin_yok" not in c.warnings
    assert c.audit["ilk_ozet"].startswith("Ulusal Mutabakat")
    sent = clf._client.calls
    assert sent[0]["model"] == "sonnet" and sent[1]["model"] == "sonnet"
    assert sent[0]["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "Mücteba Hamaney" in sent[0]["system"][0]["text"]       # sözlük prompta girdi
    assert json.loads(sent[0]["messages"][0]["content"])["metin"].startswith("Libya")


def test_no_text_warns_and_long_summary_trimmed():
    first = {"turkey_related": True, "summary_tr": "a " * 400, "confidence": 0.5, "sozlukte_olmayanlar": ["X"]}
    clf = _clf([first, {"gecti": True, "sorunlar": [], "duzeltilmis_ozet": None}])
    c = clf.classify(ITEM, SRC, text=None)
    assert {"metin_yok", "dusuk_guven", "sozlukte_yok"} <= set(c.warnings)
    assert len(c.summary_tr) <= 600


def test_fit_summary_sentence_boundary():
    from disgundem.classify import fit_summary
    s = "Birinci cümle burada bitti. İkinci cümle de bitti. Üçüncü cümle tamam. Dördüncü cümle fazla."
    assert fit_summary(s) == "Birinci cümle burada bitti. İkinci cümle de bitti. Üçüncü cümle tamam."
    long = "A" * 300 + " kelime. " + "B" * 350 + " son."
    assert fit_summary(long).endswith("kelime.")            # 600'ü aşan ikinci cümle hiç alınmaz


def test_audit_drops_unanchored_and_omission_notes():
    first = {"turkey_related": True, "summary_tr": "Güler Irak'taki varlığın süreceğini söyledi.", "confidence": 0.9}
    audit = {"gecti": False, "sorunlar": [
        {"tur": "desteksiz", "ozet_ifadesi": "kaynakta olmayan bir ifade", "aciklama": "x"},
        {"tur": "eksik", "ozet_ifadesi": "Güler", "aciklama": "AFP atfı özete alınmamış"},
        {"tur": "unvan", "ozet_ifadesi": "", "aciklama": "sorun yok"},
        {"tur": "ad", "ozet_ifadesi": "Güler", "aciklama": "Sözlükle uyumlu; bu kalem hata değildir."}],
        "duzeltilmis_ozet": "Bambaşka özet."}
    c = _clf([first, audit]).classify(ITEM, SRC, text=BODY)
    assert c.audit["gecti"] is True and c.audit["atilan"] == 4
    assert "denetim" not in c.warnings and c.summary_tr.startswith("Güler")   # düzeltme uygulanmadı


def test_cmd_classify_never_persists_article_text(monkeypatch):
    rec = []
    row = {"id": "a1", "source_id": "K262", "url": "https://ex.com/a", "title": "t", "status": "queued",
           "summary_tr": "eski", "classification": {"prompt": "classify_v1", "model": "haiku"}}

    class FakeStore:
        def __init__(self, s): pass
        def queued_server(self, limit): return [row]
        def unsummarized(self, limit): return []
        def set_article_links(self, *a): pass
        def upsert_articles(self, rows): rec.extend(rows)

    class FakeClf:
        provider, model, summary_model = "anthropic", "h", "s"
        def __init__(self, s): pass
        def classify(self, item, src, text=None, audit=True):
            assert text == "GİZLİ METİN " * 50
            return SimpleNamespace(frame=None, summary_tr="yeni", local_view_note=None, model="s", prompt_version="v2",
                                   confidence=0.9, raw={}, countries=["ly"], themes=[], dossiers=[],
                                   warnings=[], audit={"gecti": True})

    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "Classifier", FakeClf)
    monkeypatch.setattr(cli, "load_sources", lambda: [SimpleNamespace(id="K262")])
    monkeypatch.setattr(cli, "make_client", lambda s: SimpleNamespace(close=lambda: None))
    monkeypatch.setattr(cli, "fetch_text", lambda c, u, ua, t="": ("GİZLİ METİN " * 50, "ok"))
    s = Settings(article_text=True, audit=True)
    cli.cmd_classify(s, SimpleNamespace(limit=10, yeniden=True))
    assert rec and "GİZLİ" not in json.dumps(rec, ensure_ascii=False)
    assert rec[0]["classification"]["onceki"]["summary_tr"] == "eski"
    assert rec[0]["classification"]["metin"] == "ok"


def test_thinking_fallback_to_between_tools():
    class Picky(FakeAnthropic):
        def create(self, **kw):
            if kw["thinking"] == {"type": "disabled"}:
                raise RuntimeError('send "thinking": {"type": "between_tools"} instead')
            return super().create(**kw)

    clf = _clf([])
    clf._client = Picky([{"items": []}, {"items": []}])
    clf._call("s", "u", model="sonnet")
    clf._call("s", "u", model="sonnet")
    modes = [c["thinking"]["type"] for c in clf._client.calls]
    assert modes == ["between_tools", "between_tools"]      # ikinci çağrıda doğrudan doğru değer


def test_cmd_classify_skips_llm_errors(monkeypatch):
    rec = []

    class FakeStore:
        def __init__(self, s): pass
        def queued_server(self, limit): return [{"id": "a1", "source_id": "K262", "url": "u", "title": "t",
                                                 "status": "queued", "summary_tr": "eski"}]
        def set_article_links(self, *a): pass
        def upsert_articles(self, rows): rec.extend(rows)

    class ErrClf:
        provider, model, summary_model = "anthropic", "h", "s"
        def __init__(self, s): pass
        def classify(self, item, src, text=None, audit=True):
            return SimpleNamespace(raw={"error": "400"}, audit=None)

    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "Classifier", ErrClf)
    monkeypatch.setattr(cli, "load_sources", lambda: [SimpleNamespace(id="K262")])
    import pytest
    with pytest.raises(SystemExit):
        cli.cmd_classify(Settings(article_text=False), SimpleNamespace(limit=10, yeniden=True))
    assert rec == []                                         # eski özetin üzerine boş yazılmadı


def test_relevance_guard_rejects_other_story():
    from disgundem.fetch.article import relevance
    other = "The GCC Secretary-General said trade with the United Kingdom reached 70 billion dollars. " * 10
    title = "Erdogan Submits Makkah Joint Defense Agreement to Parliament for Ratification - Asharq Al-Awsat"
    assert relevance(title, other) < 0.34
    good = "President Erdogan submitted the Makkah joint defense agreement to parliament for ratification. " * 5
    assert relevance(title, good) > 0.6
    # Arapça: ön ekli kelimeler alt dize olarak yakalanır
    assert relevance("تركيا تحيل اتفاقية مكة للدفاع المشترك", "أحالت تركيا اتفاقية مكة للدفاع المشترك إلى البرلمان") > 0.6


def test_jsonld_picks_body_matching_title_and_fetch_marks_mismatch():
    from disgundem.fetch import article as A
    other = "Gulf trade with Britain reached seventy billion dollars last year, officials said today. " * 8
    right = "Erdogan submitted the Makkah defense agreement to parliament for ratification today. " * 8
    html = ('<script type="application/ld+json">' + json.dumps({"@graph": [{"articleBody": other}, {"articleBody": right}]})
            + "</script>")
    assert A.extract(html, "Erdogan Submits Makkah Defense Agreement to Parliament").startswith("Erdogan")
    A._robots.clear()
    c = _client(lambda r: httpx.Response(404) if r.url.path == "/robots.txt" else
                httpx.Response(200, text=f"<html><body><article><p>{other}</p></article></body></html>"))
    assert fetch_text(c, "https://ex.com/n/1", "Bot", "Erdogan Submits Makkah Defense Agreement")[1] == "uyumsuz"


def test_relevance_inflected_languages():
    from disgundem.fetch.article import relevance
    assert relevance("Η Βουλή της Λιβύης ενέκρινε το παράνομο τουρκολιβυκό μνημόνιο",
                     "Η Βουλή των Αντιπροσώπων της Λιβύης ενέκρινε ομόφωνα το τουρκολιβυκού μνημονίου") > 0.6
    assert relevance("Украинские дроны атаковали Тамбовскую область",
                     "Беспилотники ВСУ атаковали Тамбовскую область, украинские дроны") > 0.6
