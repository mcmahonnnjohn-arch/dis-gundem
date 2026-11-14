# COWORK GÖREV 1 — Kaynak keşfi

Bu dosyanın içeriğini **yeni Cowork görevine** ver.

**Rol:** 30 kaynaklık jeopolitik pilot için keşif araştırmacısısın. Mevcut \`data/source_universe/pilot_30.jsonl\` ve \`data/kaynak_envanteri_v3.csv\` kayıtlarını oku. Eski \`Çekirdek\`/ \`Canlı\` alanları editoryal teyit değildir. Yeni N001 Bellingcat ve N002 ACLED'yi de araştır.

**Çıktı:** \`data/out/cowork/discovery.jsonl\` içinde **her 30 ID için bir satır**: \`source_id\`, \`canonical_url_candidate\`, \`region\`, \`languages\`, \`original_work_candidates\` (tarihli özgün URL), \`methodology_or_about_urls\`, \`ownership_or_funding_candidate_urls\`, \`editorial_use_case\`, \`risk_flags\`, \`unknowns\`. Ayrıca \`data/out/cowork/discovery_notes.md\` içinde bölgesel ve dilsel kapsama boşluklarını yaz.

**Yöntem:** Yerel dilde özgün haber, belge, araştırma, uydu/OSINT veya veri arayın. Ajans kopyası ve basın açıklamasını özgün saha araştırması olarak sınıflandırmayın. X handle ancak birinci elden kanıtlıysa önerin. Sayfa açılamıyorsa \`BLOCKED\` kaydedin; PASS veya uydurma bağlantı yazmayın. Her iddiayı URL ile destekleyin.

**Yetki:** Yalnız staging çıktılarını yaz. \`pilot_30.jsonl\`, \`claims.json\`, \`provenance_edges.json\`, ana CSV ve üretim sistemlerini değiştirme. Kendi keşfini bağımsız teyit olarak sayma. Tamamlanınca 30/30 kapsam sayısını ve açık kalanları raporla.
