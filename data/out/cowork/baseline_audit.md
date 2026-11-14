# Baseline audit — 30 kaynaklık pilot harness
Tarih: 2026-11-15 (UTC+03 01:xx) · Dal: feat/source-universe-pilot-30-harness @ 3315d3e · Python 3.13

## Sonuçlar (gerçekten çalıştırıldı)
| Kontrol | Sonuç |
|---|---|
| pilot_30.jsonl kayıt sayısı | 30, benzersiz ID 30 |
| 28 legacy ID ↔ data/kaynak_envanteri_v3.csv | 28/28 eşleşiyor; envanterde 269 kayıt, tekrar eden ID yok |
| N001 Bellingcat / N002 ACLED envanterde mi | Hayır (ad/URL araması boş) → ikinci kez eklenmemiş |
| Pilot içi tekrar eden alan adı | Yok |
| Envanter içi tekrar eden alan adı | carnegieendowment.org ×5 (pilot dışı; pilotu etkilemez, 150'lik seçimde dikkat) |
| Orijinal 8 unit test | 8/8 OK |
| gate --mode structural | PASS (exit 0) |
| gate --mode readiness | NO_GO (exit 2), 0/30 kabul — beklenen |
| Yapısal kapı neyi denetler | Yalnız kayıt biçimi/kotalar. Gerçek URL, içerik veya kaynak doğrulaması YAPMAZ |

## Bulunan kalite-kapısı açıkları (bypass probları, bellekte)
Hiçbir gerçek kanıt olmadan, tamamen sahte bir kayıt `source_readiness` tarafından **kabul edildi**:
1. `https://example.org/...` gibi yer tutucu alan adları kanıt URL'si olarak geçiyordu.
2. `original_work_examples` tarih içermese de geçiyordu (talimat: tarihli örnek).
3. `evidence` içinde "ne görüldüğü" (observation) zorunlu değildi.
4. `signoffs.editor` herhangi bir dize olabiliyordu (model kendi adını yazabilirdi).
5. Aynı alan adı farklı yol ile ikinci kez sayılabiliyordu (yalnız host+path karşılaştırılıyordu).
6. `claims.json`: serbest metin provenance_family adlarıyla "tass-wire" + "tass-wire-reprint" iki bağımsız aile sayılıyordu; provenance_edges kullanılmıyordu.

## Düzeltmeler (eşik gevşetilmedi; yalnız sıkılaştırıldı)
- `is_url` yer tutucu/ayrılmış alan adlarını reddeder.
- Kanıt için boş olmayan `observation`; örnekler için geçerli, gelecekte olmayan `published_at`.
- Editör imzası `human:<ad>` biçiminde olmalı (model kendini insan editör ilan edemez).
- Yapısal kapıya alan adı tekilliği eklendi.
- `claim_issues(..., edges)`: `claim_id` taşıyan ve bağımlı ilişki (republishes, same_wire, same_statement, same_dataset, same_imagery, derives_from…) içeren edge'ler aileleri tek köke indirger.
- 7 yeni regresyon testi (toplam 15). Eski kodda 6'sı başarısız, yeni kodda 15/15 OK (mutasyon kanıtı).
- Mevcut testlerde `example.org` fikstürleri `news-fixture.org` yapıldı (yer tutucu reddi nedeniyle); kapı gevşemedi.

## GitHub Actions
`source-pilot.yml` doğru: PR path filtresi, py3.12, unit test + structural (zorunlu), readiness bilgilendirici. Notlar: `reports/**` path filtresinde yok (eklenecek); readiness NO_GO bilerek PR'yi kırmıyor. Actions fiilen bu oturumda çalıştırılmadı.

## Sınırlar
Yerel Python 3.13 ile test edildi; CI 3.12 kullanır, farkı beklemiyoruz ama doğrulanmadı.
