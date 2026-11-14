# Pilot 30 — Puanlar ve katman önerileri

_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._


**Yöntem:** Puan, yalnız kayıtlı kanıta dayanan **alt sınırdır** (kanıt yoksa 0). `signal_noise` hiçbir kaynak için ölçülmedi (editör 20 maddelik örneklem yapmalı); bu yüzden hiçbir kaynağın 7 bileşenli tam puanı yoktur ve `pilot_30.jsonl` içinde `score_breakdown=null`'dır. Alt sınır, kanıt erişilebilirliğini ölçer, editoryal değeri değil: devlet ajansları erişilebildikleri için paywall'lı Haaretz'den yüksek görünür.

Bileşenler: kanıt/25 (=5×geçen zorunlu kontrol), özgünlük/20, sinyal-gürültü/15 (ölçülmedi), tamamlayıcılık/15, şeffaflık/10, süreklilik/10, zamanlılık/5.

| ID | Kaynak | Kanıt | Özgün | S/G | Kapsam | Şeffaf. | Sürekl. | Zaman. | Alt sınır | Mümkün üst | Öneri | Gerekçe |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K001 | Enab Baladi | 10 | 0 | — | 10 | 3 | 6 | 3 | 32 | 100 | **HOLD** | eksik zorunlu kontrol: canonical_url, originality, provenance |
| K003 | SANA | 20 | 3 | — | 10 | 10 | 10 | 3 | 56 | 100 | **HOLD** | resmî/devlet kanalı: özgünlük kapısı yapısal olarak geçilemez; yalnız atıflı resmî pozisyon izleme rolü için editör kararı gerekir |
| K004 | Syria Direct | 20 | 16 | — | 5 | 3 | 10 | 3 | 57 | 100 | **HOLD** | eksik zorunlu kontrol: identity |
| K007 | Omran Center for Strategic Studies | 5 | 0 | — | 10 | 3 | 4 | 0 | 22 | 100 | **HOLD** | eksik zorunlu kontrol: identity, activity, originality, provenance |
| K020 | Haaretz | 0 | 0 | — | 5 | 3 | 0 | 0 | 8 | 100 | **HOLD** | eksik zorunlu kontrol: identity, canonical_url, activity, originality, provenance |
| K029 | Naftemporiki | 20 | 0 | — | 10 | 3 | 10 | 3 | 46 | 100 | **HOLD** | eksik zorunlu kontrol: originality |
| K031 | ELIAMEP | 20 | 16 | — | 10 | 3 | 10 | 5 | 64 | 100 | **HOLD** | eksik zorunlu kontrol: provenance |
| K039 | Mada Masr | 0 | 0 | — | 10 | 3 | 0 | 0 | 13 | 100 | **HOLD** | eksik zorunlu kontrol: identity, canonical_url, activity, originality, provenance; mahkeme kapatma kararı 27 Ekim 2026 (RT-006) |
| K047 | IRNA | 0 | 0 | — | 10 | 3 | 0 | 0 | 13 | 100 | **HOLD** | resmî/devlet kanalı; kanıt eksik |
| K051 | IranWire | 0 | 0 | — | 10 | 3 | 0 | 0 | 13 | 100 | **HOLD** | eksik zorunlu kontrol: identity, canonical_url, activity, originality, provenance |
| K065 | Al-Monitor | 15 | 0 | — | 5 | 3 | 6 | 3 | 32 | 100 | **HOLD** | eksik zorunlu kontrol: originality, provenance |
| K070 | AZERTAC | 20 | 3 | — | 13 | 10 | 6 | 3 | 55 | 100 | **HOLD** | resmî/devlet kanalı: özgünlük kapısı yapısal olarak geçilemez; yalnız atıflı resmî pozisyon izleme rolü için editör kararı gerekir |
| K077 | Hetq | 15 | 0 | — | 13 | 7 | 6 | 3 | 44 | 100 | **HOLD** | eksik zorunlu kontrol: originality, provenance |
| K080 | OC Media | 20 | 0 | — | 13 | 3 | 6 | 3 | 45 | 100 | **HOLD** | eksik zorunlu kontrol: originality |
| K083 | TASS | 15 | 3 | — | 13 | 6 | 6 | 3 | 46 | 100 | **HOLD** | resmî/devlet kanalı: özgünlük kapısı yapısal olarak geçilemez; yalnız atıflı resmî pozisyon izleme rolü için editör kararı gerekir |
| K086 | Meduza | 20 | 0 | — | 13 | 10 | 6 | 3 | 52 | 100 | **HOLD** | eksik zorunlu kontrol: originality |
| K225 | Ukrainian Prism | 5 | 0 | — | 13 | 7 | 0 | 0 | 25 | 100 | **HOLD** | eksik zorunlu kontrol: identity, activity, originality, provenance |
| K105 | Avrupa Komisyonu — Press Corner | 10 | 3 | — | 5 | 10 | 4 | 0 | 32 | 100 | **HOLD** | resmî/devlet kanalı: özgünlük kapısı yapısal olarak geçilemez; yalnız atıflı resmî pozisyon izleme rolü için editör kararı gerekir |
| K112 | SWP | 25 | 16 | — | 10 | 10 | 6 | 5 | 72 | 100 | **WEEKLY** | 5/5 zorunlu kontrol; imzalar/puan/insan editör eksik; signal_noise ölçülmedi |
| K238 | RUSI | 25 | 16 | — | 5 | 7 | 6 | 5 | 64 | 100 | **WEEKLY** | 5/5 zorunlu kontrol; imzalar/puan/insan editör eksik; signal_noise ölçülmedi |
| K123 | CRS Reports (Kongre) | 5 | 16 | — | 5 | 3 | 0 | 0 | 29 | 100 | **HOLD** | resmî/devlet kanalı; kanıt eksik |
| K244 | FDD | 0 | 0 | — | 5 | 3 | 4 | 0 | 12 | 100 | **HOLD** | eksik zorunlu kontrol: identity, canonical_url, activity, originality, provenance |
| K132 | Xinhua | 15 | 3 | — | 13 | 0 | 10 | 3 | 44 | 100 | **HOLD** | resmî/devlet kanalı: özgünlük kapısı yapısal olarak geçilemez; yalnız atıflı resmî pozisyon izleme rolü için editör kararı gerekir |
| K138 | The Hindu | 0 | 0 | — | 8 | 3 | 0 | 0 | 11 | 100 | **HOLD** | eksik zorunlu kontrol: identity, canonical_url, activity, originality, provenance |
| K153 | Addis Standard | 5 | 0 | — | 13 | 7 | 0 | 0 | 25 | 100 | **HOLD** | eksik zorunlu kontrol: canonical_url, activity, originality, provenance |
| K154 | Sudan Tribune | 5 | 0 | — | 13 | 3 | 0 | 0 | 21 | 100 | **HOLD** | eksik zorunlu kontrol: canonical_url, activity, originality, provenance |
| K159 | Dışişleri Bakanlığı | 20 | 3 | — | 10 | 10 | 10 | 3 | 56 | 100 | **HOLD** | resmî/devlet kanalı: özgünlük kapısı yapısal olarak geçilemez; yalnız atıflı resmî pozisyon izleme rolü için editör kararı gerekir |
| K168 | Reuters | 20 | 16 | — | 5 | 3 | 6 | 3 | 53 | 100 | **HOLD** | eksik zorunlu kontrol: canonical_url |
| N001 | Bellingcat | 25 | 20 | — | 5 | 3 | 10 | 5 | 68 | 100 | **EVENT** | 5/5 zorunlu kontrol; imzalar/puan/insan editör eksik; signal_noise ölçülmedi |
| N002 | ACLED | 15 | 16 | — | 5 | 7 | 4 | 0 | 47 | 100 | **HOLD** | eksik zorunlu kontrol: activity, provenance |

Katman eşikleri (politika): RADAR≥75, WEEKLY≥65, EVENT≥60. Hiçbir kaynak 7 bileşenli tam puanla bu eşiklerde doğrulanmadı; öneriler rol/kanıt gerekçeli ve **editör kararı bekler**.
Eski CSV'deki `Çekirdek` etiketi ve önceki `proposed_tier` kanıt sayılmadı.

N001 için önerilen EVENT tetikleyicisi: Somut bir saldırı/hasar/askerî hareket iddiasında görüntü-video jeolokasyonu veya doğrulaması gerektiğinde ve en az iki bağımsız ham görüntü ailesi bulunduğunda (öneri; editör onayı gerekir)
