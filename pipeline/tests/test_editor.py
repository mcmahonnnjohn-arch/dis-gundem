"""Editör onay görünümü: eylem mantığı ve yerel sunucunun güvenlik kontrolleri."""
import json
import threading
import urllib.error
import urllib.request

import pytest

from disgundem.config import ROOT
from disgundem.editor import DemoStore, EditorHata, sunucu_kur, uygula

ORNEK = ROOT / "web" / "site" / "src" / "data" / "ornek.json"


@pytest.fixture
def store():
    return DemoStore(ORNEK)


def _ilk(store):
    cid = next(iter(store.kumeler))
    return cid, store.kumeler[cid]


def test_yayinla_duzeltmeyi_gunluge_yazar(store):
    cid, k = _ilk(store)
    eski = k["title_tr"]
    r = uygula(store, cid, "yayinla", {"title_tr": "  Yeni   başlık ", "summary_tr": k["summary_tr"]})
    assert r["duzeltme"] == 1 and k["status"] == "published" and k["title_tr"] == "Yeni başlık"
    assert store.gunluk == [{"cluster_id": cid, "alan": "title_tr", "onceki": eski, "yeni": "Yeni başlık"}]


def test_degisiklik_yoksa_gunluk_bos(store):
    cid, k = _ilk(store)
    assert uygula(store, cid, "kaydet", {"title_tr": k["title_tr"]})["duzeltme"] == 0 and store.gunluk == []


def test_reddet_metne_dokunmaz(store):
    cid, k = _ilk(store)
    uygula(store, cid, "reddet", {"title_tr": "yok sayılır"})
    assert k["status"] == "rejected" and k["title_tr"] != "yok sayılır" and store.gunluk == []


def test_bos_baslik_yayinlanamaz(store):
    cid, _ = _ilk(store)
    with pytest.raises(EditorHata):
        uygula(store, cid, "yayinla", {"title_tr": "   "})
    assert store.kumeler[cid]["status"] == "queued"


def test_ozet_600_karakteri_asamaz(store):
    cid, _ = _ilk(store)
    with pytest.raises(EditorHata):
        uygula(store, cid, "kaydet", {"summary_tr": "a" * 601})


def test_kuyrukta_olmayan_kume_yeniden_islenmez(store):
    cid, _ = _ilk(store)
    uygula(store, cid, "reddet", None)
    with pytest.raises(EditorHata) as e:
        uygula(store, cid, "yayinla", None)
    assert e.value.kod == 409


def test_gecersiz_kimlik_ve_eylem(store):
    with pytest.raises(EditorHata):
        uygula(store, "../etc", "yayinla", None)
    with pytest.raises(EditorHata):
        uygula(store, next(iter(store.kumeler)), "sil", None)


def _istek(port, yol, token=None, host=None, gov=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["X-Editor-Token"] = token
    if host:
        h["Host"] = host
    rq = urllib.request.Request(f"http://127.0.0.1:{port}{yol}", headers=h, method="POST" if gov is not None else "GET",
                                data=json.dumps(gov).encode() if gov is not None else None)
    try:
        with urllib.request.urlopen(rq) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_sunucu_token_ve_host_denetimi(store):
    srv = sunucu_kur(store, 0, demo=True)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        st, html = _istek(port, "/")
        assert st == 200
        token = html.split('data-token="')[1].split('"')[0]
        assert _istek(port, "/api/kuyruk")[0] == 403                          # token yok
        assert _istek(port, "/api/kuyruk", token="yanlis")[0] == 403
        assert _istek(port, "/api/kuyruk", token=token, host="evil.example")[0] == 403   # DNS rebinding
        st, govde = _istek(port, "/api/kuyruk", token=token)
        kume = json.loads(govde)["kumeler"][0]
        assert st == 200 and kume["makaleler"]
        assert _istek(port, f"/api/kume/{kume['id']}", token=token, gov={"eylem": "yayinla"})[0] == 200
        assert _istek(port, f"/api/kume/{kume['id']}", token=token, gov={"eylem": "yayinla"})[0] == 409
        assert _istek(port, f"/api/kume/{kume['id']}", token=token, gov=[1])[0] == 400
    finally:
        srv.shutdown()
