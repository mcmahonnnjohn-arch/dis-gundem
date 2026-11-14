# COWORK GÖREV 5 — Editoryal puanlama, birleştirme ve kalite kapısı

**Girdi:** \`data/source_universe/pilot_policy.json\` ve \`data/out/cowork/\` altındaki dört görevin bulguları. Ayrı Cowork görevi aç; mümkünse insan editör son imzayı bizzat versin.

**İşlem:** 30 ID'yi kanıt düzeyine göre sınıflandır. \`score_breakdown\` yedi bileşenden oluşur: evidence/25, originality/20, signal_noise/15, coverage/15, transparency/10, continuity/10, timeliness/5. Kanıt yetersizse sahte tam puan verme. \`RADAR\`, \`WEEKLY\`, \`EVENT\` tekil öneri üret; eski CSV'deki \`Çekirdek\` etiketi yeni RADAR değildir. EVENT için ölçülebilir olay tetikleyicisi belirt.

**Çıktı:** \`data/out/cowork/editorial.jsonl\` içinde her kaynak için puanlar, önerilen tier, özgün katkı, risk, eksik kanıt ve editörce alınacak karar. \`data/out/cowork/editorial_report.md\` içinde kapsama matrisi, tekrar eden kökenler, ret gerekçeleri, önerilen 35/65/50 büyüme ilkeleri ve GO/NO_GO yaz.

**Koordinatör aşaması:** Yalnız gerçekten doğrulanmış kanıtlar \`pilot_30.jsonl\` içine entegre edilir. \`signoffs.verifier\`, \`signoffs.red_team\` farklı bağımsız görev kimlikleri olmalı. \`signoffs.editor\` yalnız gerçek insan editörün açık kabulüyle doldurulur; model kendi adına insan imzası atamaz. \`claims.json\` içinde factual iddialar için iki farklı **kanıt ailesi** gerekir. Açık high/critical bulgu kaynak kabulünü durdurur.

**Terminal erişimi varsa:**
\`\`\`bash
python -m unittest discover -s pilot_harness/tests -v
python -m pilot_harness gate --mode structural
python -m pilot_harness report
python -m pilot_harness gate --mode readiness
\`\`\`

Terminal yoksa değişiklikleri draft PR'ye gönderip GitHub Actions test sonuçlarını incele. Test sonuçlarını çalıştırılmadan PASS diye raporlama. Hazırlanan raporda **gerçek test sonucu** ile **önerilen editoryal karar** ayrı gösterilsin. **NO_GO ise 150'ye ölçekleme ve otomatik yayın yok.**
