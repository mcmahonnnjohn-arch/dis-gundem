# Pilot 30 — Kaynak matrisi

_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._


Durum anahtarı: P=PASS, F=FAIL, ?=UNKNOWN (BLOCKED dahil). Kontroller: kimlik / kanonik URL / aktiflik / özgünlük / köken / sahiplik / bakış.

| ID | Kaynak | Bölge | Dil | Tür | Kontroller (K·U·A·Ö·P·S·B) | Köken ailesi | Karar |
|---|---|---|---|---|---|---|---|
| K001 | Enab Baladi | Levant & Irak | ar/en | Bağımsız | P ? P ? ? ? ? | UNKNOWN | HOLD |
| K003 | SANA | Levant & Irak | ar/en/tr | Devlet ajansı | P P P F P P P | state-statement:syria | HOLD |
| K004 | Syria Direct | Levant & Irak | en | Bağımsız | ? P P P P ? ? | own-field-reporting:K004 (one SANA-derived figure) | HOLD |
| K007 | Omran Center for Strategic Studies | Levant & Irak | ar/en | Think tank | ? P ? ? ? ? ? | UNKNOWN (öneri, doğrulanmadı: own-dataset:K007) | HOLD |
| K020 | Haaretz | Doğu Akdeniz | en | Ana akım | ? ? ? ? ? ? ? | UNKNOWN (öneri, doğrulanmadı: own-reporting:haaretz (anonymo | HOLD |
| K029 | Naftemporiki | Doğu Akdeniz | el | Ekonomi | P P P ? P ? ? | wire:ΑΠΕ-ΜΠΕ+Reuters (for sampled foreign item) | HOLD |
| K031 | ELIAMEP | Doğu Akdeniz | el/en | Think tank | P P P P ? ? ? | UNKNOWN (öneri, doğrulanmadı: own-analysis:K031) | HOLD |
| K039 | Mada Masr | Doğu Akdeniz | ar/en | Bağımsız | ? ? ? ? ? ? ? | UNKNOWN | HOLD |
| K047 | IRNA | Körfez & İran | fa | Devlet ajansı | ? ? ? ? ? ? ? | UNKNOWN (öneri, doğrulanmadı: state-statement:iran (IRNA con | HOLD |
| K051 | IranWire | Körfez & İran | fa/en | Bağımsız | ? ? ? ? ? ? ? | UNKNOWN | HOLD |
| K065 | Al-Monitor | Körfez & İran | en | Uzman yayın | P P P ? ? ? ? | UNKNOWN (öneri, doğrulanmadı: mixed:AFP-wire + Axios-relay + | HOLD |
| K070 | AZERTAC | Kafkasya | az/en/tr | Devlet ajansı | P P P F P P P | state-statement:azerbaijan | HOLD |
| K077 | Hetq | Kafkasya | hy/en | Bağımsız | P P P ? ? P ? | UNKNOWN | HOLD |
| K080 | OC Media | Kafkasya | en/ru | Bağımsız | P P P ? P ? ? | own-field-reporting:K080 | HOLD |
| K083 | TASS | Karadeniz & Rusya | ru/en | Devlet ajansı | ? P P F P ? P | state-statement:russia (TASS) + feed-share with Xinhua | HOLD |
| K086 | Meduza | Karadeniz & Rusya | ru/en | Bağımsız | P P P ? P P P | mixed:own+partner-republication(Glasnaya) | HOLD |
| K225 | Ukrainian Prism | Karadeniz & Rusya | uk/en | Think tank | ? P ? ? ? P ? | UNKNOWN | HOLD |
| K105 | Avrupa Komisyonu — Press Corner | Avrupa | en | Resmi kurum | P P ? F ? P P | UNKNOWN (öneri, doğrulanmadı: institution:eu-commission (pri | HOLD |
| K112 | SWP | Avrupa | de/en | Think tank | P P P P P P P | own-research:K112 | WEEKLY |
| K238 | RUSI | Avrupa | en | Think tank | P P P P P P ? | own-research:K238 (convened taskforce) | WEEKLY |
| K123 | CRS Reports (Kongre) | Kuzey Amerika | en | Resmi kurum | ? ? ? P ? ? ? | UNKNOWN (öneri, doğrulanmadı: institution:us-congress-crs (p | HOLD |
| K244 | FDD | Kuzey Amerika | en | Think tank | ? ? ? ? ? ? ? | UNKNOWN (öneri, doğrulanmadı: own-analysis:fdd (advocacy; re | HOLD |
| K132 | Xinhua | Asya | zh/en | Devlet ajansı | ? P P F P ? ? | state-statement:prc (Xinhua) + feed-share with TASS | HOLD |
| K138 | The Hindu | Asya | en | Ana akım | ? ? ? ? ? ? ? | UNKNOWN | HOLD |
| K153 | Addis Standard | Afrika | en/am/om | Bağımsız | P ? ? ? ? P ? | UNKNOWN | HOLD |
| K154 | Sudan Tribune | Afrika | en/ar | Bağımsız | P ? ? ? ? ? ? | UNKNOWN | HOLD |
| K159 | Dışişleri Bakanlığı | Türkiye | tr/en | Resmi kurum | P P P F P P P | state-statement:turkiye (primary) | HOLD |
| K168 | Reuters | Küresel | en | Ajans | P ? P P P ? ? | wire:reuters | HOLD |
| N001 | Bellingcat | Küresel | en | OSINT | P P P P P ? ? | own-osint:bellingcat (shared imagery with Planet/WaPo, Tasni | EVENT |
| N002 | ACLED | Küresel | en | Conflict data | P P ? P ? P ? | UNKNOWN (öneri, doğrulanmadı: dataset:acled (own coded event | HOLD |

Karar dağılımı (öneri): {'HOLD': 27, 'WEEKLY': 2, 'EVENT': 1}. REJECT: 0 (hiçbir kaynak için ret kanıtı yok; kanıtsız ret uydurulmadı).
Bölge sayısı: 11; kaynak türü: {'Bağımsız': 9, 'Devlet ajansı': 5, 'Think tank': 6, 'Ana akım': 2, 'Ekonomi': 1, 'Uzman yayın': 1, 'Resmi kurum': 3, 'Ajans': 1, 'OSINT': 1, 'Conflict data': 1}
