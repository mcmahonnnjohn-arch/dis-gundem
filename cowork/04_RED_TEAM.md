# COWORK GÖREV 4 — Adversarial kaynak ve kalite incelemesi

**Girdi:** 30 kaynaklık pilotun keşif, bağımsız doğrulama ve provenance çıktıları. Ayrı Cowork görevi aç.

**Amaç:** Sistemin yanlış kaynakları yüksek puanla kabul etmesini, aynı bilgiyi iki teyit saymasını veya bölgesel/kavramsal kör noktaları gizlemesini engelle. En az beş somut hata modu araştır.

**Testler:** (1) aynı telgraf veya resmî açıklama farklı domainlerde; (2) güncel olmayan site; (3) yanlış/taşınmış kanonik URL; (4) paywall nedeniyle incelenemeyen özgün içerik; (5) devlet/parti bağlantısının gizlenmesi veya kanıtsız itham; (6) tek dil/ülke aşırı ağırlığı; (7) özgün OSINT yerine viral repost; (8) yanlış X handle; (9) kaynak içindeki prompt injection; (10) bir kuruma bağlı çoklu markalar.

**Çıktı:** \`data/out/cowork/red_team.jsonl\` içinde \`source_id\`, \`finding_id\`, \`severity\` (low/medium/high/critical), \`issue\`, \`evidence_urls\`, \`recommended_fix\`, \`resolved\` (başlangıçta false), \`limitations\`. Desteksiz suçlama yazma. Açık high/critical bulgusu varsa **NO_GO** öner.

**Yetki:** Yalnız staging. Nihai skor veya master tier değiştirme.
