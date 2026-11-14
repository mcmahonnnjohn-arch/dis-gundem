# Kaynak evreni: 30 kaynak pilotu ve Claude Code harness

## Mimari karar

Mevcut \`data/kaynak_envanteri_v3.csv\` **269 kaynaklık tarihsel keşif/doğrulama havuzudur**. Nihai hedef, bundan ve yeni adaylardan seçilecek **150 benzersiz kaynak**: 35 RADAR, 65 WEEKLY, 50 EVENT. Eski \`Durum=Çekirdek\` ile yeni \`RADAR\` **aynı alan değildir**. A/B/R/T/P ülke/ürün kapsam kodları da editoryal izleme katmanı değildir.

Bu pilot, **28 mevcut K-ID + 2 yeni OSINT/veri adayı** ile toplam 30 kaynak seçer. Yeni N001 Bellingcat (özgün açık kaynak araştırmaları) ve N002 ACLED (çatışma olay verisi) mevcut CSV'ye doğrudan eklenmez; kaynak evreni overlay'inde adaydır. Kanonik URL ve ilk keşif bağlantısı kaynakların pilot kalite kapılarını geçtiği anlamına gelmez. Diğer 28 kayıt da güncel, bağımsız doğrulamayı sıfırdan geçer.

\`pilot_30.jsonl\` her kaynağı yalnız bir kez sayar. Mevcut K-ID'ler CSV'den okunur; aynı kimlik iki kez kopyalanmaz. Kaynakların mevcut otomatik toplama yöntemleri, RSS listeleri, ülke sınıflandırmaları, veritabanı ve yayın hattı değişmez.

## Çalıştırma

Repo kökünde Python 3.11+:

\`\`\`bash
python -m unittest discover -s pilot_harness/tests -v
python -m pilot_harness gate --mode structural
python -m pilot_harness materialize
python -m pilot_harness report
python -m pilot_harness gate --mode readiness
\`\`\`

- \`materialize\` → \`data/out/source_universe_pilot.jsonl\` (30 birleşik kayıt).
- \`report\` → \`data/out/pilot_quality_report.md\` (kaynak matrisi, kalite ve GO/NO_GO).
- \`gate --mode structural\` → ID, URL biçimi, envanter eşleşmesi, tekillik, bölge/dil/OSINT kapsamı. Başarısızsa exit 1.
- \`gate --mode readiness\` → bağımsız güncel kanıt, özgünlük, provenance, puan, imza ve nihai karar. Başlangıçta **NO_GO / exit 2** beklenir.
- CI: \`.github/workflows/source-pilot.yml\` yapısal kapıyı ve regresyon testlerini çalıştırır; readiness NO_GO durumunu rapora yazar ama PR'yi kırmaz. **Bu, kaynakların teyit edildiği anlamına gelmez.**

## Veri sözleşmesi

Kaynak başına \`checks\`: \`identity\`, \`canonical_url\`, \`activity\`, \`originality\`, \`provenance\`, \`ownership\`, \`perspective\`. Değerler \`PASS | FAIL | UNKNOWN | NA\`. İlk beşi kabul için zorunlu PASS'tir. \`ownership\` ve \`perspective\` için UNKNOWN ancak \`unknowns\` içinde açık gerekçeyle tutulabilir; özellikle RADAR kararı insan editörce yeniden değerlendirilmeli.

Her PASS için \`evidence\` dizisine şu şemada bir öğe eklenir (yalnız **örnek format**, gerçek teyit değil):

\`\`\`json
{"check":"originality","url":"https://publisher.example/original-report","observed_at":"2026-11-14T10:00:00Z","reviewer":"verifier-01"}
\`\`\`

Ayrıca \`original_work_examples\`: \`[{"url":"https://publisher.example/original-report","published_at":"2026-11-10"}]\`; \`provenance_family\`: belirlenmiş köken; \`score_breakdown\`: yedi tam sayı; \`signoffs\`: verifier/red_team/editor üç farklı kimlik; \`red_team_findings\`: \`[{"severity":"high","resolved":false,"reason":"..."}]\`; \`assigned_tier\`: tek bir RADAR/WEEKLY/EVENT. Verifier keşifçiden farklı olmalıdır. URL'ler HTTPS ve gözlemler en fazla 45 günlük olmalıdır.

**Puanlama:** evidence 25, originality 20, signal_noise 15, coverage 15, transparency 10, continuity 10, timeliness 5. Editör eşikleri: RADAR 75, WEEKLY 65, EVENT 60; **puan tek başına kabul sağlamaz**. EVENT için somut aktivasyon tetikleyicisi gerekir. Red-team'in çözülmemiş high/critical bulgusu kabulü durdurur.

## GO / NO_GO

Yapısal kapı: tam 30 benzersiz kaynak, en az 9 bölge, en az 5 dil, en az 2 OSINT/veri kaynağı, geçerli HTTPS kanonik adresleri ve mevcut envanter ID eşleşmesi.

Operasyonel kapı: en az 27 kabul, 30 kimlik teyidi, 29 güncel URL teyidi, 27 özgün üretim teyidi, 27 provenance teyidi ve **iki OSINT/veri adayının kabulü**. Her kabul edilen kaynakta özgün iş örneği, geçerli 100 puanlık döküm, bağımsız verifier, ayrı red-team, ayrı editör ve tekil tier olmalı. Sayılar \`pilot_policy.json\` üzerinden sürümlenir.

\`claims.json\` içine girilen \`kind=factual\` iddiaları en az **iki ayrı provenance_family** gerektirir. \`kind=attributed_statement\` ise tek birincil kaynaktan atıflı beyan olarak kaydedilebilir; beyanın içeriğinin doğruluğunu teyit etmez. \`provenance_edges.json\` kanıt URL'si olmayan ilişkiyi kabul etmez. İki ayrı medya kuruluşu aynı Reuters haberi veya aynı uydu görüntüsünü kopyalıyorsa iki teyit sayılmaz.

## Pilot iş dağıtımı

1. \`source-scout\`: 30 kaynağı bölgelere ve dillere göre bölüştür; özgün üretim örneklerini topla. Eski CSV'deki ideolojik eğilim notlarını kanıtlanmış kabul etme.
2. \`independent-verifier\`: scout'tan bağımsız kontrol; tarih, kanıt URL'si, edisyon, etkinlik ve özgün üretim.
3. \`provenance-auditor\`: haber ajansı kopyaları, devlet açıklamaları, ortak görüntü/dataset, aynı kurumsal aile ve fon ilişkileri.
4. \`red-team\`: en az beş özgül hata modu; yüksek/kritik bulguları kapatmadan PASS verme.
5. \`tier-editor\`: kaynak bazında kullanım değeri, 100 puan, önerilen katman, aktivasyon tetikleyicisi ve açık kapsam boşlukları.
6. Orchestrator: yalnız doğrulanmış kayıtları JSONL'ye işler, testleri çalıştırır, raporu üretir; **nihai editör onayı olmadan katman ataması yapmaz**.

## Kırmızı çizgiler

- Yeni kaynak eklemek, otomatik olarak günlük haber akışını genişletmez.
- X hesapları ancak kurumun ilk elden sayfası kanıtlıyorsa eklenir; tahmini hesap yazılmaz.
- HTTP 200 özgünlük veya güncellik kanıtı değildir.
- Paywall ve CAPTCHA atlatılmaz; premium makale metni depolanmaz.
- \`data/out/\` çıktı klasörüdür; orijinal CSV ve üretim Supabase'i bu pilot tarafından değiştirilmez.
- Pilot **NO_GO** ise 150'ye ölçekleme ve yayın yetkisi açılmaz.
