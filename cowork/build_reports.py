"""Builds reports/pilot_30_*.md from the staging outputs and the repo's real gate runs (2026-11-15)."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/out/cowork"
REP = ROOT / "reports"
REP.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT))
from pilot_harness.__main__ import audit, materialize, read_json, POLICY  # noqa: E402

jl = lambda n: [json.loads(x) for x in (OUT / n).read_text(encoding="utf-8").splitlines() if x.strip()]
pilot = {r["id"]: r for r in (json.loads(x) for x in (ROOT / "data/source_universe/pilot_30.jsonl").read_text(encoding="utf-8").splitlines() if x.strip())}
mat = {r["id"]: r for r in materialize()}
ver = {r["source_id"]: r for r in jl("verification.jsonl")}
disc = {r["source_id"]: r for r in jl("discovery.jsonl")}
edu = {r["source_id"]: r for r in jl("editorial.jsonl")}
rt = jl("red_team.jsonl")
spot = jl("red_team_spotchecks.jsonl")
edges = jl("provenance.jsonl")
fam = json.loads((OUT / "provenance_families.json").read_text(encoding="utf-8"))
ids = list(pilot)
cell = lambda s, n=140: str(s).replace("|", "/").replace("\n", " ")[:n]
HDR = "_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._\n\n"


def w(name, text):
    (REP / name).write_text(text, encoding="utf-8")


# 1 matrix
L = ["# Pilot 30 — Kaynak matrisi\n", HDR,
     "Durum anahtarı: P=PASS, F=FAIL, ?=UNKNOWN (BLOCKED dahil). Kontroller: kimlik / kanonik URL / aktiflik / özgünlük / köken / sahiplik / bakış.\n",
     "| ID | Kaynak | Bölge | Dil | Tür | Kontroller (K·U·A·Ö·P·S·B) | Köken ailesi | Karar |", "|---|---|---|---|---|---|---|---|"]
sym = {"PASS": "P", "FAIL": "F", "UNKNOWN": "?"}
for i in ids:
    m, p = mat[i], pilot[i]
    ch = " ".join(sym[p["checks"][k]] for k in ["identity", "canonical_url", "activity", "originality", "provenance", "ownership", "perspective"])
    L.append(f"| {i} | {m['canonical_name']} | {m['region']} | {'/'.join(m['languages'])} | {m['source_type']} | {ch} | {cell(p['provenance_family'], 60)} | {edu[i]['decision']}{' (resmî rol)' if p.get('monitoring_role') else ''} |")
c = Counter(edu[i]["decision"] for i in ids)
L += ["", f"Karar dağılımı (öneri): {dict(c)}. REJECT: 0 (hiçbir kaynak için ret kanıtı yok; kanıtsız ret uydurulmadı).",
      f"Bölge sayısı: {len({mat[i]['region'] for i in ids})}; kaynak türü: " + str(dict(Counter(mat[i]['source_type'] for i in ids)))]
w("pilot_30_source_matrix.md", "\n".join(L) + "\n")

# 2 evidence
L = ["# Pilot 30 — Kaynak bazında kanıt\n", HDR,
     "**Önemli sınırlama (RT-001):** Doğrulayıcı `observed_at` değerleri toplu yazım zamanıdır (kanıt kayıtlarında `observed_at_precision=batch_write_time`). "
     "Tazelik 45 günlük eşik için günler düzeyinde doğrudur (hepsi 2026-11-14/15) ama sayfa-bazlı erişim saati değildir. Kırmızı takım 26 PASS'i yeniden çekip 17 'evet', 8 'kısmi', 1 'hayır' buldu; kısmi/hayır olanlar PASS'ten UNKNOWN'a indirildi.\n"]
for i in ids:
    p, v = pilot[i], ver[i]
    L += [f"## {i} — {mat[i]['canonical_name']}", f"- Doğrulayıcı: {p['signoffs']['verifier']}; keşif: {p['discoverer']}",
          f"- Erişim notu: {cell(v.get('paywall_or_access_notes', ''), 220)}"]
    for k, c_ in v["checks"].items():
        st = p["checks"][k]
        note = p["verification_notes"].get(k, "")
        L.append(f"- **{k}**: {st}{' — ' + cell(note, 200) if note else ''}\n  - kanıt: {c_['evidence_url']} (gözlem: {cell(c_['observation'], 240)})")
    for e in p["original_work_examples"]:
        L.append(f"- Özgün çalışma (doğrulanmış): {e['url']} ({e['published_at']})")
    for e in p["original_work_examples_unverified"]:
        L.append(f"- Özgün çalışma adayı (DOĞRULANMADI): {e['url']} ({e.get('published_at')})")
    L.append("")
w("pilot_30_evidence.md", "\n".join(L))

# 3 provenance
claim_e = [e for e in edges if e["level"] == "claim"]
src_e = [e for e in edges if e["level"] == "source"]
L = ["# Pilot 30 — Köken ve bağımsız teyit\n", HDR,
     f"Denetçi: cowork-provenance-01. {len(edges)} edge ({len(claim_e)} iddia düzeyi, {len(src_e)} kaynak düzeyi). `EXT:` ile başlayan uçlar 30'luk küme dışındaki kökenlerdir (AFP, Axios, MOFCOM, Glasnaya…).\n",
     "**Sonuç:** Pilot kaynaklar arasında gerçekten bağımsız teyit bulunamadı (`independent_corroboration` edge sayısı: "
     f"{sum(e['relationship']=='independent_corroboration' for e in edges)}). Resmî açıklama yalnız açıklamanın yapıldığını kanıtlar.\n",
     "## Sahte bağımsız teyit örnekleri (iddia düzeyi)", "| Kimden → Kime | İlişki | Kapsam | Kanıt | Güven |", "|---|---|---|---|---|"]
for e in claim_e:
    L.append(f"| {e['from_source_id']} → {e['to_source_id']} | {e['relationship']} | {cell(e['claim_or_topic_scope'], 170)} | {e['evidence_url']} | {e['confidence']} |")
L += ["", "## Kaynak düzeyi kurumsal ilişkiler (iddia bağımlılığıyla karıştırılmamalı)", "| Kimden → Kime | İlişki | Kapsam | Kanıt | Güven |", "|---|---|---|---|---|"]
for e in src_e:
    L.append(f"| {e['from_source_id']} → {e['to_source_id']} | {e['relationship']} | {cell(e['claim_or_topic_scope'], 170)} | {e['evidence_url']} | {e['confidence']} |")
L += ["", "## Köken aileleri ve çözülmemiş bağımlılıklar", "| ID | Aile (öneri) | Çözülmemiş |", "|---|---|---|"]
for i in ids:
    f = fam[i]
    L.append(f"| {i} | {cell(f['provenance_family'], 90)} | {cell('; '.join(f.get('unresolved_dependencies', [])), 200)} |")
L += ["", "Sınırlar: edge `observed_at` değerleri toplu yazım zamanıdır; sayfalar bazen araç özetiyle okundu; birkaç yukarı akış orijinali (Reuters, Axios) açılamadı."]
w("pilot_30_provenance.md", "\n".join(L) + "\n")

# 4 red team
L = ["# Pilot 30 — Red-team bulguları\n", HDR,
     f"Denetçi: cowork-redteam-01. {len(rt)} bulgu: " + str(dict(Counter(r['severity'] for r in rt))) + ". Hepsi **çözülmedi**; açık yüksek bulgu olduğu için kabul engellidir.\n",
     "Koordinatör notu: RT-004 (kapı mantığı) ve RT-003'ün kod tarafı bu turda düzeltildi (aşağıda 'Çözüm durumu'); diğer bulgular açık.\n",
     "| ID | Kaynak | Önem | Sorun | Düzeltme önerisi | Durum |", "|---|---|---|---|---|---|"]
fixed = {"RT-004": "KOD DÜZELTİLDİ (kısmen): UNKNOWN-önekli aile reddi, EXT/ortaklık edge birleşmesi; singleton aile riski sürüyor",
         "RT-003": "KOD DÜZELTİLDİ: edge'ler artık doldurulup iddia bağımlılığı sayılıyor; claims.json boş olduğundan sınanacak gerçek iddia yok"}
for r in rt:
    L.append(f"| {r['finding_id']} | {r['source_id']} | {r['severity']} | {cell(r['issue'], 330)} | {cell(r['recommended_fix'], 260)} | {fixed.get(r['finding_id'], 'AÇIK')} |")
L += ["", "## Yeniden çekme (spot-check) sonuçları", "| Kaynak | Kontrol | Destekliyor mu | Not |", "|---|---|---|---|"]
for s in spot:
    L.append(f"| {s['source_id']} | {s['check']} | {s['supports']} | {cell(s.get('note', ''), 200)} |")
L += ["", "## Kanıt URL'leri", ""] + [f"- {r['finding_id']}: " + ", ".join(r.get("evidence_urls", [])[:4]) for r in rt if r.get("evidence_urls")]
w("pilot_30_red_team.md", "\n".join(L) + "\n")

# 5 tiers
L = ["# Pilot 30 — Puanlar ve katman önerileri\n", HDR,
     "**Yöntem:** Puan, yalnız kayıtlı kanıta dayanan **alt sınırdır** (kanıt yoksa 0). `signal_noise` hiçbir kaynak için ölçülmedi (editör 20 maddelik örneklem yapmalı); bu yüzden hiçbir kaynağın 7 bileşenli tam puanı yoktur ve `pilot_30.jsonl` içinde `score_breakdown=null`'dır. "
     "Alt sınır, kanıt erişilebilirliğini ölçer, editoryal değeri değil: devlet ajansları erişilebildikleri için paywall'lı Haaretz'den yüksek görünür.\n",
     "Bileşenler: kanıt/25 (=5×geçen zorunlu kontrol), özgünlük/20, sinyal-gürültü/15 (ölçülmedi), tamamlayıcılık/15, şeffaflık/10, süreklilik/10, zamanlılık/5.\n",
     "| ID | Kaynak | Kanıt | Özgün | S/G | Kapsam | Şeffaf. | Sürekl. | Zaman. | Alt sınır | Mümkün üst | Öneri | Gerekçe |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i in ids:
    e = edu[i]; sc = e["score_components"]
    L.append(f"| {i} | {mat[i]['canonical_name']} | {sc['evidence']} | {sc['originality']} | {'—' if sc['signal_noise'] is None else sc['signal_noise']} | {sc['coverage']} | {sc['transparency']} | {sc['continuity']} | {sc['timeliness']} | {e['score_lower_bound']} | {e['score_known_max']} | **{e['decision']}** | {cell(e['reason'], 150)} |")
L += ["", "Katman eşikleri (politika): RADAR≥75, WEEKLY≥65, EVENT≥60. Hiçbir kaynak 7 bileşenli tam puanla bu eşiklerde doğrulanmadı; öneriler rol/kanıt gerekçeli ve **editör kararı bekler**.",
      "Eski CSV'deki `Çekirdek` etiketi ve önceki `proposed_tier` kanıt sayılmadı.",
      "", "N001 için önerilen EVENT tetikleyicisi: " + pilot["N001"]["activation_trigger"]]
w("pilot_30_tier_recommendations.md", "\n".join(L) + "\n")

# 6 quality gate (real runs)
cmds = [["python", "-m", "unittest", "discover", "-s", "pilot_harness/tests", "-v"], ["python", "-m", "pilot_harness", "gate", "--mode", "structural"],
        ["python", "-m", "pilot_harness", "materialize"], ["python", "-m", "pilot_harness", "report"], ["python", "-m", "pilot_harness", "gate", "--mode", "readiness"]]
L = ["# Pilot 30 — Kalite kapısı (gerçek çalıştırma)\n", HDR]
for cmd in cmds:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    L += [f"## `{' '.join(cmd[1:])}` → exit {r.returncode}", "```", out[-2500:], "```", ""]
res = audit(); pol = read_json(POLICY)["acceptance"]
chk = res["check_counts"]
rows = [("Tam 30 benzersiz kaynak", "30", res["pilot_count"] == 30), ("≥9 bölge", "9", len({mat[i]['region'] for i in ids}) >= 9),
        ("≥5 dil", "5", len({l for i in ids for l in mat[i]['languages']}) >= 5), ("≥2 OSINT/veri", "2", sum(mat[i]['source_type'] in {'OSINT', 'Conflict data'} for i in ids) >= 2),
        (f"≥{pol['min_accepted']} kabul", len(res["accepted"]), len(res["accepted"]) >= pol["min_accepted"]),
        ("30 kimlik teyidi", chk.get("identity", 0), chk.get("identity", 0) >= 30), ("≥29 kanonik URL", chk.get("canonical_url", 0), chk.get("canonical_url", 0) >= 29),
        ("≥27 özgünlük", chk.get("originality", 0), chk.get("originality", 0) >= 27), ("≥27 provenance", chk.get("provenance", 0), chk.get("provenance", 0) >= 27),
        ("Açık yüksek/kritik red-team yok", len(res["set_blockers"]) + sum(len(p["red_team_findings"]) > 0 and any(f["severity"] in {"high", "critical"} for f in p["red_team_findings"]) for p in pilot.values()), False),
        ("İnsan editör onayı", 0, False)]
L += ["## Kriter tablosu", "| Kriter | Ölçülen | Sonuç |", "|---|---|---|"]
for n, val, ok in rows:
    L.append(f"| {n} | {val} | {'GEÇTİ' if ok else 'GEÇMEDİ'} |")
L += ["", "**Kapının kapsamı:** `structural` yalnız kayıt biçimini ve kotaları denetler; gerçek URL/içerik doğrulaması yapmaz. Bu turda gerçek doğrulama web araçlarıyla ajanlarca yapıldı ve kapı bu kayıtların biçimini/tutarlılığını denetledi. Yapısal PASS editoryal teyit değildir.",
      f"**Hazırlık sonucu: {res['go_no_go']}.** Kabul: {len(res['accepted'])}/30.",
      "Bu turda kod değişiklikleri (eşik gevşetilmeden): yer tutucu alan adı reddi, observation zorunluluğu, tarihli özgün örnek, `human:` editör imzası, alan adı tekilliği, iddia düzeyi bağımlılık birleştirme (EXT/ortaklık), UNKNOWN-önekli aile reddi, set genelinde açık yüksek bulgu engeli; `official_position_monitor` rolü (özgünlük aranmaz, olgusal kanıt sayılmaz, eşik anahtarı kapalı); test sayısı 8 → 26.",
      "GitHub Actions bu oturumda çalıştırılmadı; PR'ye push sonrası sonucu izlenmeli."]
w("pilot_30_quality_gate.md", "\n".join(L) + "\n")

# 7 decision
langs = Counter(l for i in ids for l in mat[i]["languages"])
regs = Counter(mat[i]["region"] for i in ids)
full = [i for i in ids if edu[i]["decision"] in {"RADAR", "WEEKLY", "EVENT"}]
L = ["# Pilot 30 — Editoryal karar\n", HDR,
     "## KARAR: **NO-GO**\n",
     "Teknik/araştırma kapıları geçilmedi (PENDING değil). 150 kaynağa ölçekleme ve otomatik yayın **açılmaz**. İnsan editör imzası bu turda atılmadı.\n",
     "## Sayılar",
     f"- Gerçekten incelenen kaynak: 30/30 (keşif + kör doğrulama + provenance + red-team).",
     f"- 5/5 zorunlu kontrolü geçen (editör incelemesine hazır, kabul DEĞİL): {len(full)} — {', '.join(full)}.",
     "- Reddedilen: 0 (kanıtlı ret yok). Bekleyen/HOLD: 27. Kabul edilen: 0.",
     f"- Kapı sayıları: kimlik {chk.get('identity',0)}/30, kanonik URL {chk.get('canonical_url',0)}/29, özgünlük {chk.get('originality',0)}/27, köken {chk.get('provenance',0)}/27.",
     "", "## En değerli özgün kaynaklar (kanıtla)",
     "- N001 Bellingcat: tarihli özgün OSINT (jeolokasyon/görüntü doğrulama); görüntü kökenleri iddia başına etiketlenmeli (RT-022).",
     "- K112 SWP, K238 RUSI: özgün analiz, tarihli çalışmalar; finansman/çıkar bağlamı UNKNOWN veya kısmi (RT-014, RT-015).",
     "- N002 ACLED: özgün kodlanmış veri katmanı, fakat girdileri medya/kurum raporları; metodoloji ve bağışçı listesi doğrulanamadı (RT-021).",
     "", "## En önemli provenance/bağımsızlık sorunları",
     "- Sıfır bağımsız teyit çifti: TASS/Naftemporiki/Reuters (Peşkov), Xinhua/TASS (Nasser Hastanesi), SANA/MFA (219), Xinhua/Al-Monitor (Hürmüz) aynı kökene dayanıyor.",
     "- TASS–Xinhua 2026-2030 içerik paylaşımı: Rusya-Çin konularında tek aile sayılmalı.",
     "- Meduza'nın bir 'özgün' örneği Glasnaya yeniden yayımı; Al-Monitor Axios/AFP aktarıyor.",
     "", "## Kapsama boşlukları",
     f"- Bölgeler ({len(regs)}): {dict(regs)}. Diller: {dict(langs)}; 28/30 kaynak İngilizce içeriyor, 11'i yalnız İngilizce (RT-020).",
     "- Türkiye yalnız Dışişleri Bakanlığı ile temsil ediliyor; Türkçe basın yok. Afrika, Güney/Doğu Asya, Latin Amerika, Rusya (bağımsız) ve Orta Doğu (Arapça pan-bölgesel) zayıf.",
     "- Kırmızı takımın **yalnız öneri** olarak andığı yerel dil adayları (kayıt defterine EKLENMEDİ): Kan/Ynet/Maariv, BBC Persian/Radio Farda, Medyascope/bianet/T24, Ukrainska Pravda/Suspilne, Novaya Gazeta Europe/Mediazona, Al-Araby Al-Jadeed, Dabanga, Jeune Afrique, Folha/Infobae, Caixin, Dawn/Scroll.",
     "", "## Editörün karar vermesi gereken açık konular",
     "1. **Resmî/devlet kanalları (SANA, IRNA, AZERTAC, TASS, Xinhua, Dışişleri, AB Press Corner) — KARAR VERİLDİ (kullanıcı, 2026-11-15):** 'atıflı resmî pozisyon izleme' rolünde izlenecek. Uygulama ilkeleri: yalnız `attributed_statement` olarak kaydedilir; olgunun doğruluğunu teyit saymaz ve iki-aile kuralında bağımsız kanıt olarak sayılmaz; özgünlük kapısı gevşetilmedi (bu kaynaklar 'özgün üretim' sayımına girmez); ROL KODA İŞLENDİ (`monitoring_role=official_position_monitor`, `attribution_only=true`, politika `official_monitor`): rol kaynaklarında özgünlük kontrolü aranmaz ama kimlik, URL, aktiflik ve köken (state-statement/state-media/institution) PASS olmalı; olgusal iddiada kanıt sayılmazlar. **Aritmetik uyarı:** 7 rol kaynağı özgünlükte PASS olamayacağı için ≥27 özgünlük eşiği (en çok 23) varsayılan olarak ulaşılamaz kalır; `adjust_originality_threshold` anahtarı bilerek kapalı bırakıldı, yalnız editör açabilir. Nihai kaynak kabulü bekliyor (`signoffs.editor` boş).",
     "2. **Mada Masr (K039):** izlenmemesinin nedeni reddedilmesi değil, HOLD'da olmasıdır: 7 kontrolün hepsi UNKNOWN (sayfalar açılmadı, ana sayfa eski/tarihsiz), 27 Ekim 2026'da mahkeme kapatma ve ekipman müsaderesi kararı verdi, haber odası kapatıldı; site 2017'den beri Mısır içinde engelli. 2026-11-15'te yapılan ek aramada kapatma kararının temyiz duruşması 25 Kasım olarak görüldü (Drop Site News; Attalah'ın kendi yazısı gibi görünüyor, ikincil okuma); 11 Kasım'daki duruşma ayrı davadır. İzleme için gereken: kanonik alan adında veya birinci elden kanıtlı bir aynada/kanalda son tarihli özgün makale.",
     "3. **Erişilemeyen kaynaklar (Haaretz, The Hindu, Reuters, CRS, IRNA, IranWire):** robots/paywall/engelden BLOCKED. Yasal erişim yolu (abonelik, API, lisanslı akış) gerekir; ücretli hizmet için sizin onayınız gerekir, kullanılmadı.",
     "4. **signal_noise ölçümü:** her aday için 20 maddelik örneklem; ölçülmeden tam puan ve katman yok.",
     "5. **Gözlem zamanı kesinliği (RT-001):** kayıtlar toplu yazım zamanını taşıyor; bağımsız bir turda sayfa-bazlı zaman damgasıyla yeniden doğrulama istenir mi?",
     "6. **İnsan editör imzası:** `signoffs.editor` yalnız `human:<ad>` biçiminde, gerçek insan tarafından doldurulur.",
     "7. Son kabul, 150'ye genişleme ve yayın için açık onayınız gerekir; hiçbiri verilmedi.",
     "", "## 150 kaynağa genişleme koşulları (hepsi birlikte)",
     "- Hazırlık kapısı GO: ≥27 kabul, 30 kimlik, ≥29 URL, ≥27 özgünlük, ≥27 köken, ≥2 OSINT/veri kabulü.",
     "- Set genelindeki açık yüksek bulguların (RT-001, 002, 003, 004, 005, 020) kapatılması ve yeniden red-team.",
     "- Kaynak başına tam 7 bileşenli puan, üç farklı imza, insan editör onayı.",
     "- Gerçek iddia testi: `claims.json`'da en az bir iddianın iki gerçekten bağımsız kökenle teyidi.",
     "- Yerel dil/bölge boşlukları için yeni adaylar aynı keşif→kör doğrulama→provenance→red-team zincirinden geçmeli.",
     "", "Nihai ilke: daha fazla kaynak değil, daha fazla bağımsız teyit."]
w("pilot_30_editorial_decision.md", "\n".join(L) + "\n")
print("reports written")
