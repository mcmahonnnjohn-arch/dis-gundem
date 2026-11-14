# Cowork operasyon kılavuzu — Dış Gündem kaynak evreni pilotu

## 1. Tek kaynak evreni, ayrılmış görevler

Mevcut kaynak envanteri: \`data/kaynak_envanteri_v3.csv\` (269 kayıt).
Pilot overlay: \`data/source_universe/pilot_30.jsonl\` (28 K-ID + N001 Bellingcat + N002 ACLED).
Pilot kalite politikası: \`data/source_universe/pilot_policy.json\`.
Nihai evren: **150 benzersiz kaynak = RADAR 35 + WEEKLY 65 + EVENT 50**.
Eski CSV'deki \`Çekirdek\` etiketi **yeni RADAR'a eşit değildir**.

Her görevi **ayrı Cowork konuşması/görevi** olarak başlatın. Ayrı görevler gerçek istatistiksel veya kurumsal bağımsızlık garantisi değildir; ancak önceki ajan çıktısının sonraki doğrulamayı yönlendirmesini azaltır. Verifier'a scout'un değerlendirmelerini göstermeyin. Web/terminal/dosya araçlarının kullanılabilirliği değişebilir; kullanılamayan araçlar için dürüstçe BLOCKED kaydedin.

## 2. Girdi ve çıktı sözleşmesi

- Görev 1 keşif: \`cowork/01_DISCOVERY.md\` → \`data/out/cowork/discovery.jsonl\`
- Görev 2 bağımsız teyit: \`cowork/02_VERIFICATION.md\` + yalnız \`cowork/verification_brief_30.csv\` → \`data/out/cowork/verification.jsonl\`
- Görev 3 köken/bağımsızlık: \`cowork/03_PROVENANCE.md\` + teyit çıktısı → \`data/out/cowork/provenance.jsonl\`
- Görev 4 adversarial inceleme: \`cowork/04_RED_TEAM.md\` + teyit ve köken çıktıları → \`data/out/cowork/red_team.jsonl\`
- Görev 5 editoryal ve entegrasyon: \`cowork/05_EDITORIAL_GATE.md\` + tüm çıktılar → \`data/out/cowork/editorial.jsonl\` ve rapor.

**Sadece koordinatör** \`pilot_30.jsonl\`, \`claims.json\`, \`provenance_edges.json\` dosyalarını günceller. Görev ajanları staging çıktısı üretir. \`data/kaynak_envanteri_v3.csv\`, mevcut \`pipeline/\`, Supabase, secrets ve yayın iş akışı değiştirilmez.

## 3. Kanıt politikası

Kayıt başına yedi kontrol: identity, canonical_url, activity, originality, provenance, ownership, perspective. \`PASS\` yazılan her kontrol için birinci elden veya yeterince güvenilir kanıtın **tam URL'si**, **UTC gözlem zamanı**, **verifier kimliği** ve **ne görüldüğü** gerekir. Ana sayfanın açılması, özgün gazetecilik kanıtı değildir. Kaynağın eski CSV'de \`Canlı\` görünmesi yeni teyit sayılmaz.

Örnek (yalnız şema; gerçek bulgu değildir):
\`\`\`json
{"source_id":"K001","check":"originality","status":"PASS","url":"https://publisher.example/original-report","observed_at":"2026-11-14T10:00:00Z","reviewer":"cowork-verifier-01","observation":"Tarihli özgün saha haberi ve byline incelendi","limitations":[]}
\`\`\`

Sahiplik, fonlama, ideolojik bakış ve X hesabı için kanıt bulunmazsa UNKNOWN. Haber kuruluşu ve kanıtın kökeni farklı kavramlardır: aynı ajans haberi iki mecrada yayımlanmışsa iki bağımsız teyit değildir. Resmî açıklama, yalnız açıklamanın yapıldığını doğrular; içeriğinin doğru olduğunu değil.

## 4. Bağımsız inceleme

Verifier, keşif dosyasını ve eski \`Durum\`/\`Doğrulama\` alanlarını görmemeli. Verifier yalnız kimlik, başlangıç URL'si, bölge ve dilden oluşan \`verification_brief_30.csv\` ile başlar. Bir başka görev provenance bağımlılıklarını araştırır. Red-team yüksek/kritik riskleri açık bırakırsa kaynak kabul edilmez. Editör rolündeki model yalnız **öneri** verir; gerçek insan editörün kabulü olmadan \`signoffs.editor\` doldurulmaz.

## 5. Kalite kapısı

\`\`\`bash
python -m unittest discover -s pilot_harness/tests -v
python -m pilot_harness gate --mode structural
python -m pilot_harness materialize
python -m pilot_harness report
python -m pilot_harness gate --mode readiness
\`\`\`

Son komut başlangıçta **NO_GO (exit 2)** vermelidir; bu bir hata değil, kanıtların henüz toplanmadığını gösterir. Gerçek zamanlı URL, makale ve sahiplik doğrulaması Python harness tarafından yapılmaz; bu testler **kanıt kayıtlarının yapısını ve editoryal kabul kurallarını** denetler. Web'deki gerçekleri bağımsız insan/araştırmacı doğrulaması ile değerlendirmek gerekir.

**GO koşulları:** tam 30 benzersiz kaynak, ≥9 bölge, ≥5 dil, ≥2 OSINT/veri; ≥27 kabul, 30 kimlik teyidi, ≥29 güncel URL, ≥27 özgünlük, ≥27 provenance teyidi, iki OSINT/veri kaynağının kabulü; üç farklı imza, 100 puanlık alt skorlar ve yüksek/kritik açık risk olmaması. Detaylar \`pilot_policy.json\` dosyasında sürümlenir.

## 6. Editoryal son çıktı

- Kaynak bazında: kimlik, ülke/dil, özgünlük, 2 özgün iş örneği tercih edilir, fonlama ve perspektif, köken, puan, tier, risk, belirsizlik, kanıt URL'leri.
- Bölge/dil/OSINT boşlukları; aynı kanıta bağımlı görünen kurum kümeleri.
- Reddedilen veya bekleyen kaynaklar ve net gerekçe.
- Tarihli GO/NO_GO raporu.
- GO olmadan 150 kaynaklık evrene otomatik genişleme ve bülten yayını yapılmaz.
