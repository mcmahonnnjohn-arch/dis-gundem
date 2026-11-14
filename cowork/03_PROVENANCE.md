# COWORK GÖREV 3 — Köken ve bağımsız teyit denetimi

**Girdi:** \`data/out/cowork/verification.jsonl\`, pilot ID listesi ve gerekliyse doğrulanmış haber/çalışma URL'leri. Ayrı Cowork görevi aç.

**Amaç:** Aynı orijinal muhabir, telgraf ajansı, devlet açıklaması, görüntü, uydu kaydı, sosyal paylaşım, veri seti veya sızdırılmış belgeye dayanan kaynakları ayrı bağımsız teyit gibi sayma. Sahiplik ilişkisi ile **tekil iddianın kanıt bağımlılığını** ayrı kaydet.

**Çıktı:** \`data/out/cowork/provenance.jsonl\`: \`from_source_id\`, \`to_source_id\`, \`relationship\`, \`evidence_url\`, \`observed_at\`, \`claim_or_topic_scope\`, \`confidence\`, \`limitations\`. Ayrıca her kaynak için kanıtla desteklenebiliyorsa \`provenance_family\` öner; bilinmiyorsa UNKNOWN. Varsayımsal bağlantı uydurma.

**Kritik test:** İki farklı outlet aynı Reuters haberini aktarıyorsa **tek aile**; resmî açıklama tek başına açıklamadaki olgunun doğruluğu değildir. Açık veri setinden türetilen iki grafik, veri seti bağımsız değilse iki teyit değildir.

**Yetki:** Yalnız staging dosyası. Kaynak evreninin master kayıtlarını değiştirme. Çözülmemiş bağımlılıkları özellikle listele.
