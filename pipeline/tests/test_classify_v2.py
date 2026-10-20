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
    audit = {"gecti": False, "sorunlar": [{"tur": "unvan", "aciklama": "UMH 2021'de sona erdi"}],
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
    monkeypatch.setattr(cli, "fetch_text", lambda c, u, ua: ("GİZLİ METİN " * 50, "ok"))
    s = Settings(article_text=True, audit=True)
    cli.cmd_classify(s, SimpleNamespace(limit=10, yeniden=True))
    assert rec and "GİZLİ" not in json.dumps(rec, ensure_ascii=False)
    assert rec[0]["classification"]["onceki"]["summary_tr"] == "eski"
    assert rec[0]["classification"]["metin"] == "ok"
