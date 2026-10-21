"""Yerel editör onay görünümü: `disgundem editor` → http://127.0.0.1:8787

Servis anahtarı yalnız bu süreçte kalır; sayfa tarayıcıda yalnız bu yerel sunucuyla konuşur.
Birim = küme (okur ekranındaki olay kartı). Eylemler: kaydet · yayınla · reddet.
Her metin düzeltmesi `editor_corrections` günlüğüne yazılır (Yayın Kılavuzu §9).
"""
from __future__ import annotations

import json
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .editor_ui import SAYFA

ALANLAR = {"title_tr": 160, "summary_tr": 600, "bakis_farki": 400}   # alan → azami karakter (kılavuz §6, §10)
EYLEMLER = {"kaydet", "yayinla", "reddet"}
KIMLIK = re.compile(r"^[0-9a-fA-F-]{8,64}$")
AZAMI_GOVDE = 64 * 1024


class EditorHata(Exception):
    def __init__(self, mesaj: str, kod: int = 400):
        super().__init__(mesaj)
        self.mesaj, self.kod = mesaj, kod


def _temiz(v) -> str | None:
    if v is None:
        return None
    if not isinstance(v, str):
        raise EditorHata("Alanlar metin olmalı")
    v = re.sub(r"[ \t]+", " ", v).strip()
    return v or None


def uygula(store, cid: str, eylem: str, alanlar: dict | None) -> dict:
    """Bir küme için editör eylemini uygular. Yalnız `queued` kümeler işlenir."""
    if eylem not in EYLEMLER:
        raise EditorHata("Bilinmeyen eylem")
    if not KIMLIK.match(cid or ""):
        raise EditorHata("Geçersiz küme kimliği")
    mevcut = store.editor_cluster(cid)
    if mevcut is None:
        raise EditorHata("Küme bulunamadı", 404)
    if mevcut["status"] != "queued":
        raise EditorHata(f"Bu küme artık kuyrukta değil ({mevcut['status']})", 409)

    yeni, duzeltmeler = {}, []
    if eylem != "reddet":
        for alan, azami in ALANLAR.items():
            if alanlar is None or alan not in alanlar:
                continue
            v = _temiz(alanlar[alan])
            if v and len(v) > azami:
                raise EditorHata(f"{alan} en fazla {azami} karakter olabilir ({len(v)})")
            eski = _temiz(mevcut.get(alan))
            if v != eski:
                yeni[alan] = v
                duzeltmeler.append({"alan": alan, "onceki": eski, "yeni": v})
        if eylem == "yayinla":
            son = {**mevcut, **yeni}
            if not _temiz(son.get("title_tr")) or not _temiz(son.get("summary_tr")):
                raise EditorHata("Yayınlamak için başlık ve özet gerekli")
        if yeni:
            store.editor_save(cid, yeni, duzeltmeler)
    if eylem == "yayinla":
        store.editor_set_status(cid, "published")
    elif eylem == "reddet":
        store.editor_set_status(cid, "rejected")
    return {"ok": True, "duzeltme": len(duzeltmeler)}


class DemoStore:
    """Veritabanı olmadan arayüzü denemek için bellek içi kuyruk (web/site/src/data/ornek.json)."""
    def __init__(self, yol: Path):
        veri = json.loads(Path(yol).read_text(encoding="utf-8"))[:12]
        self.kumeler, self.gunluk = {}, []
        for i, o in enumerate(veri):
            cid = f"00000000-0000-0000-0000-{i:012d}"
            k = o["kaynaklar"][0]
            self.kumeler[cid] = {
                "id": cid, "status": "queued", "title_tr": o["baslik"], "summary_tr": o["ozet"], "bakis_farki": None,
                "importance": 5 - (i % 3), "primary_country": None, "countries": o["ulkeler"], "article_count": 1,
                "first_seen": None, "last_seen": None, "origin": "server",
                "makaleler": [{"id": cid, "title": k.get("ozgun_baslik"), "url": k["url"], "lang": k["dil"], "frame": None,
                               "summary_tr": o["ozet"], "uyarilar": ["tek_kaynak"] if i % 4 == 0 else [],
                               "kaynak_adi": k["ad"], "kaynak_ulke": k["ulke"], "published_at": None}],
            }

    def editor_queue(self, limit: int = 60) -> list[dict]:
        return [k for k in self.kumeler.values() if k["status"] == "queued"][:limit]

    def editor_cluster(self, cid):
        return self.kumeler.get(cid)

    def editor_save(self, cid, fields, corrections):
        self.kumeler[cid].update(fields)
        self.gunluk += [{"cluster_id": cid, **c} for c in corrections]

    def editor_set_status(self, cid, status):
        self.kumeler[cid]["status"] = status


def sunucu_kur(store, port: int = 8787, demo: bool = False) -> ThreadingHTTPServer:
    token = secrets.token_urlsafe(24)

    class H(BaseHTTPRequestHandler):
        server_version = "DisGundemEditor"

        def log_message(self, *a):   # sessiz
            pass

        def _host_ok(self) -> bool:
            p = self.server.server_address[1]
            return self.headers.get("Host", "") in (f"127.0.0.1:{p}", f"localhost:{p}")

        def _yanit(self, kod: int, govde: bytes, tur: str):
            self.send_response(kod)
            self.send_header("Content-Type", tur)
            self.send_header("Content-Length", str(len(govde)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(govde)

        def _json(self, kod: int, obj):
            self._yanit(kod, json.dumps(obj, ensure_ascii=False, default=str).encode(), "application/json; charset=utf-8")

        def _yetki(self) -> bool:
            if not self._host_ok():
                self._json(403, {"hata": "Geçersiz Host"})
                return False
            if not secrets.compare_digest(self.headers.get("X-Editor-Token", ""), token):
                self._json(403, {"hata": "Geçersiz oturum anahtarı; sayfayı yenileyin"})
                return False
            return True

        def do_GET(self):
            if not self._host_ok():
                return self._json(403, {"hata": "Geçersiz Host"})
            if self.path == "/":
                html = SAYFA.replace("__TOKEN__", token).replace("__DEMO__", "1" if demo else "0")
                return self._yanit(200, html.encode(), "text/html; charset=utf-8")
            if self.path == "/api/kuyruk":
                if not self._yetki():
                    return
                return self._json(200, {"kumeler": store.editor_queue(), "demo": demo})
            self._json(404, {"hata": "Yok"})

        def do_POST(self):
            m = re.match(r"^/api/kume/([^/]+)$", self.path)
            if not m:
                return self._json(404, {"hata": "Yok"})
            if not self._yetki():
                return
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if n <= 0 or n > AZAMI_GOVDE:
                    raise EditorHata("Geçersiz gövde boyutu")
                govde = json.loads(self.rfile.read(n))
                if not isinstance(govde, dict):
                    raise EditorHata("Geçersiz gövde")
                alanlar = govde.get("alanlar")
                if alanlar is not None and not isinstance(alanlar, dict):
                    raise EditorHata("Geçersiz alanlar")
                self._json(200, uygula(store, m.group(1), govde.get("eylem", ""), alanlar))
            except EditorHata as e:
                self._json(e.kod, {"hata": e.mesaj})
            except (ValueError, UnicodeDecodeError):
                self._json(400, {"hata": "Geçersiz JSON"})

    return ThreadingHTTPServer(("127.0.0.1", port), H)
