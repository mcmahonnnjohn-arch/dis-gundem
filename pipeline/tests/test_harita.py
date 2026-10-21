"""harita: yer sözlüğü eşleştirme, model çıktısının doğrulanması, cmd_harita akışı."""
import csv
import json
from types import SimpleNamespace

import pytest

from disgundem import cli, harita
from disgundem.config import Settings


class FakeClf:
    provider, model, summary_model = "anthropic", "h", "s"
    def __init__(self, replies): self.replies = list(replies); self.calls = []
    def _call(self, system, user, model=None, cache=False):
        self.calls.append((system, user)); return json.dumps(self.replies.pop(0))


# ---------------------------------------------------------------- sözlük
def test_gazetteer_loads_and_is_consistent():
    pl = harita.places()
    assert len(pl) >= 100 and "sy-tel-rifat" in pl and "sy" in pl
    for p in pl.values():
        assert p.id.startswith(p.country_id) and -90 <= p.lat <= 90 and -180 <= p.lon <= 180
        assert p.kind in {"sehir", "ilce", "bolge", "sinir_kapisi", "liman", "us", "tesis", "deniz_alani", "ulke"}


def _base(name: str) -> str:
    return name.split(" (")[0].strip()


def test_gazetteer_covers_every_glossary_place():
    """varliklar.csv'deki her yer (Suriye ve diğerleri) yer sözlüğünde aynı Türkçe yazılışla ya da takma adla bulunmalı
    (Dera, Kuneytra, Banyas, Ovda, Hürmüz…). Bir satırda iki yer olabilir: 'Trablus (Libya) / Trablusşam (Lübnan)'."""
    with (harita.SOZLUK / "varliklar.csv").open(encoding="utf-8") as f:
        yer = [r for r in csv.DictReader(f) if r["tur"] == "yer"]
    have = {harita.norm(n) for p in harita.places().values() for n in (p.name_tr, *p.aliases)}
    missing = [part for r in yer for part in map(_base, r["tr"].split(" / ")) if harita.norm(part) not in have]
    assert yer and not missing, missing


def test_every_country_has_a_country_level_record():
    from disgundem.sources import COUNTRIES
    codes = {v[0] for v in COUNTRIES.values() if not v[3]}          # grup etiketleri (levant, korfez…) hariç
    country_level = {p.id for p in harita.places().values() if p.precision == "ulke"}
    assert codes <= country_level, sorted(codes - country_level)
    assert all(harita.places()[c].country_id == c for c in country_level)


def test_place_countries_are_known_to_the_countries_table():
    """places.country_id yabancı anahtarı: sözlükte olmayan ülke kodu seed'i düşürür."""
    from disgundem.sources import dictionaries
    known = {c["id"] for c in dictionaries()["countries"]}
    assert {p.country_id for p in harita.places().values()} <= known


def test_actor_countries_exist():
    from disgundem.sources import dictionaries
    known = {c["id"] for c in dictionaries()["countries"]}
    assert all(a.country_id in known for a in harita.actors().values() if a.country_id)


@pytest.mark.parametrize("raw,expected", [
    ("Tal Rifaat", "sy-tel-rifat"), ("Tel Rıfat", "sy-tel-rifat"), ("tell rifaat", "sy-tel-rifat"),
    ("Al-Bab", "sy-el-bab"), ("al Bab", "sy-el-bab"), ("Kobani", "sy-ayn-el-arab"), ("Deir ez-Zor", "sy-deyrizor"),
    ("İdlib", "sy-idlib"), ("IDLIB", "sy-idlib"), ("حلب", "sy-halep"), ("Qamishli", "sy-kamisli"),
])
def test_resolve_aliases_syria(raw, expected):
    assert harita.resolve(raw, "sy") == expected


@pytest.mark.parametrize("raw,country,expected", [
    ("Irak", "iq", "iq"), ("Lübnan", "lb", "lb"), ("Turkey", "tr", "tr"), ("Libya", "ly", "ly"),
    ("Ovda Hava Üssü", "il", "il-ovda"), ("Uvda", "il", "il-ovda"), ("Kyiv", "ua", "ua-kiev"),
    ("Tripoli", "ly", "ly-trablus"), ("Tripoli", "lb", "lb-trablussam"),      # aynı ad, ülke ayırır
    ("Strait of Hormuz", "ir", "kuresel-hurmuz-bogazi"), ("Hormuz", "om", "kuresel-hurmuz-bogazi"),   # deniz alanı: ülke yanlışsa da
    ("Persian Gulf", "sa", "kuresel-basra-korfezi"), ("Bab el-Mandeb", "ye", "kuresel-babulmendep"),
])
def test_resolve_countries_and_seas(raw, country, expected):
    assert harita.resolve(raw, country) == expected


def test_resolve_ambiguous_without_country():
    assert harita.resolve("Tripoli", None) is None          # Libya mı Lübnan mı: belirsizse eşleşmez


def test_resolve_unknown_and_wrong_country():
    assert harita.resolve("Atlantis", "sy") is None
    assert harita.resolve("Aleppo", "iq") is None          # ülke verildiyse başka ülkede aranmaz
    assert harita.resolve("Aleppo", None) == "sy-halep"     # ülke yoksa tek eşleşme kabul


# ---------------------------------------------------------------- doğrulama
def test_clean_picks_single_primary_and_resolves_names():
    L = harita.clean({"tur": "saldiri", "yerler": [{"id": "sy-sam"}, {"ad": "Kisweh", "ulke": "sy", "birincil": True},
                                                  {"ad": "Nowhere", "ulke": "sy"}],
                      "aktorler": [{"id": "il", "rol": "fail"}, {"id": "sy", "rol": "hedef"}, {"id": "uydurma"}],
                      "turkiye": "  Türkiye saldırıyı kınadı.  "}, "sy")
    assert L.event_type == "saldiri"
    assert L.places == [("sy-sam", False), ("sy-kisve", True)]
    assert L.unresolved == [("Nowhere", "sy")]
    assert L.actors == [("il", "fail"), ("sy", "hedef")]
    assert L.turkey_stake == "Türkiye saldırıyı kınadı."


def test_clean_defaults():
    L = harita.clean({"tur": "bilinmeyen", "yerler": [{"id": "sy-halep"}, {"id": "sy-halep"}], "turkiye": None}, "sy")
    assert L.event_type is None and L.places == [("sy-halep", True)] and L.turkey_stake is None
    L = harita.clean({"tur": "diplomasi", "yerler": []}, "sy")      # yer yok → ülke merkezi birincil
    assert L.places == [("sy", True)]
    L = harita.clean({"tur": "diplomasi", "yerler": []}, "gr")      # her ülkenin ülke kaydı var
    assert L.places == [("gr", True)]
    L = harita.clean({"tur": "diplomasi", "yerler": []}, "xx")      # sözlükte olmayan kod → yersiz
    assert L.places == []
    assert harita.clean({"tur": "yargi_guvenlik"}, None).event_type == "yargi_guvenlik"
    assert harita.clean({"tur": "siyasi"}, None).event_type == "siyasi"


def test_extract_batches_and_maps_indices(monkeypatch):
    monkeypatch.setattr(harita, "BATCH", 2)
    ev = [{"k": f"c{i}", "baslik": "b", "ozet": "o", "ulke": "sy"} for i in range(3)]
    clf = FakeClf([{"olaylar": [{"i": 1, "tur": "ekonomi", "yerler": [{"id": "sy-halep", "birincil": True}]},
                                {"i": 9, "tur": "ekonomi"}]},
                   {"olaylar": [{"i": 0, "tur": "insani", "yerler": []}]}])
    out = harita.extract(clf, ev)
    assert set(out) == {"c1", "c2"} and out["c2"].places == [("sy", True)]
    assert len(clf.calls) == 2 and "sy-tel-rifat: Tel Rıfat" in clf.calls[0][0] and "eski-sdg" in clf.calls[0][0]


# ---------------------------------------------------------------- komut
def test_cmd_harita_writes_links_and_unresolved(monkeypatch):
    rec = SimpleNamespace(links=[], unres=None)

    class FakeStore:
        def __init__(self, s): pass
        def map_candidates(self, hours, redo):
            return ([{"id": "k1", "primary_country": "sy", "title_tr": None, "summary_tr": None},
                     {"id": "k2", "primary_country": "sy", "title_tr": "T", "summary_tr": None}],
                    [{"cluster_id": "k1", "title": "Strike near Tal Rifaat", "summary_tr": "Tel Rıfat'ta saldırı."}])
        def set_map_links(self, cid, fields, places, actors): rec.links.append((cid, fields, places, actors))
        def note_unresolved(self, names): rec.unres = names

    reply = {"olaylar": [{"i": 0, "tur": "saldiri", "yerler": [{"ad": "Tal Rifaat", "ulke": "sy", "birincil": True},
                                                              {"ad": "Köy X", "ulke": "xx"}],
                          "aktorler": [{"id": "tr", "rol": "taraf"}], "turkiye": None}]}
    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "Classifier", lambda s: FakeClf([reply]))
    cli.cmd_harita(Settings(), SimpleNamespace(saat=72, yeniden=False))
    (cid, fields, places, actors), = rec.links            # k2 özetsiz: atlandı
    assert cid == "k1" and fields["event_type"] == "saldiri" and fields["map_meta"]["cozulemeyen"] == ["Köy X"]
    assert places == [("sy-tel-rifat", True)] and actors == [("tr", "taraf")]
    assert rec.unres == [("Köy X", None)]                 # bilinmeyen ülke kodu FK'ye gitmez


def test_cmd_harita_skips_without_migration(monkeypatch, capsys):
    class FakeStore:
        def __init__(self, s): pass
        def map_candidates(self, hours, redo): raise RuntimeError("column clusters.event_type does not exist")
    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "Classifier", lambda s: FakeClf([]))
    cli.cmd_harita(Settings(), SimpleNamespace(saat=72, yeniden=False))
    assert "atlandı" in capsys.readouterr().out
