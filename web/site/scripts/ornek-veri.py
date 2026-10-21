#!/usr/bin/env python3
"""Örnek veri üretici: data/test_seti/ozet_test_seti.jsonl (editörün referans özetleri) +
data/kaynak_envanteri_v3.csv -> src/data/ornek.json. Yalnız Supabase anahtarı yokken kullanılır;
site bu durumda "örnek veri" şeridi gösterir. Uydurma içerik üretmez: özetler editör referans özetleridir."""
import csv, json, re, pathlib
kok = pathlib.Path(__file__).resolve().parents[3]
src = {r["ID"]: r for r in csv.DictReader(open(kok / "data/kaynak_envanteri_v3.csv", encoding="utf-8"))}
out = []
for l in open(kok / "data/test_seti/ozet_test_seti.jsonl", encoding="utf-8"):
    r = json.loads(l)
    s = src.get(r["source_id"])
    if not s or not r.get("referans_ozet"):
        continue
    ozet = r["referans_ozet"].strip()
    ilk = re.split(r"(?<=[.!?])\s", ozet)[0]
    if len(ilk) <= 110:
        baslik = ilk
    else:
        kes = ilk[:110].rfind(", ")
        baslik = ilk[:kes] if kes > 50 else ilk[:107].rsplit(" ", 1)[0] + "…"
    out.append({
        "id": r["article_id"],
        "baslik": baslik.rstrip("."),
        "ozet": ozet,
        "bakis_farki": None,
        "tarih": None,
        "turkiye_mercegi": bool(re.search(r"Türkiye|Ankara|Fidan|Erdoğan|Güler|TBMM|Türk", ozet)),
        "bolge": s["Bölge"],
        "ulkeler": [s["Ülke"]],
        "kaynaklar": [{"ad": s["Kaynak"], "ulke": s["Ülke"], "dil": r["lang"], "url": r["url"], "ozgun_baslik": r["baslik"]}],
    })
(kok / "web/site/src/data/ornek.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "örnek olay yazıldı")
