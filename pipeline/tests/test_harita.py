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


def test_gazetteer_names_match_glossary():
    """varliklar.csv'deki Suriye yerleri yer sözlüğüyle aynı Türkçe yazılışta olmalı (Dera, Kuneytra, Banyas)."""
    with (harita.SOZLUK / "varliklar.csv").open(encoding="utf-8") as f:
        sy = [r for r in csv.DictReader(f) if r["tur"] == "yer" and r["ulke"] == "sy"]
    names = {p.name_tr for p in harita.places().values()}
    assert sy and all(r["tr"] in names for r in sy)


def test_actor_countries_exist():
    from disgundem.sources import dictionaries
    known = {c["id"] for c in dictionaries()["countries"]}
    assert all(a.country_id in known for a in harita.actors().values() if a.country_id)


@pytest.mark.parametrize("raw,expected", [
    ("Tal Rifaat", "sy-tel-rifat"), ("Tel Rıfat", "sy-tel-rifat"), ("tell rifaat", "sy-tel-rifat"),
    ("Al-Bab", "sy-el-bab"), ("al Bab", "sy-el-bab"), ("Kobani", "sy-ayn-el-arab"), ("Deir ez-Zor", "sy-deyrizor"),
    ("İdlib", "sy-idlib"), ("IDLIB", "sy-idlib"), ("حلب", "sy-halep"), ("Qamishli", "sy-kamisli"),
])
def test_resolve_aliases(raw, expected):
    assert harita.resolve(raw, "sy") == expected


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
    L = harita.clean({"tur": "diplomasi", "yerler": []}, "gr")      # sözlüğü olmayan ülke → yersiz
    assert L.places == []


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
