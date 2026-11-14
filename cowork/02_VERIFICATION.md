# COWORK GÖREV 2 — Kör/bağımsız kaynak doğrulaması

Bu görevi **Görev 1'den ayrı, yeni Cowork konuşmasında** başlat. Yalnız \`cowork/verification_brief_30.csv\` dosyasını ve bu talimatı ver. Scout raporlarını, eski CSV'deki \`Doğrulama\` ve \`Durum\` alanlarını, önerilen tier ve puanları gösterme.

**Rol:** Bağımsız doğrulayıcısın. Her ID için şu kontrolleri sıfırdan yap: \`identity\`, \`canonical_url\`, \`activity\`, \`originality\`, \`provenance\`, \`ownership\`, \`perspective\`.

**Çıktı:** \`data/out/cowork/verification.jsonl\`: 30 kaynak için yedi kontrolün her birine \`PASS|FAIL|UNKNOWN\`, \`evidence_url\`, \`observed_at\` (UTC), \`reviewer\`, \`observation\`, \`limitations\`; ayrıca \`original_work_examples\` (URL, tarih, özgünlüğün nedeni), \`provenance_family_candidate\`, \`paywall_or_access_notes\`.

**Kanıt standardı:** Güncel faaliyet için tarihlenmiş yayın; özgünlük için somut özgün haber/araştırma/veri; kimlik için kurumun kendisi; sahiplik/fonlama için açık, kanıtlanabilir belgeler. HTTP 200, arama sonucu snippet'i veya bir sitenin kendi iddiası tek başına tüm kontrolleri PASS yapmaz. URL çalışmıyorsa FAIL/UNKNOWN ve gerekçe yaz. X handle uydurma. Aynı wire haberi tekrar eden yayınları bağımsız kaynak sayma.

**Temiz oda:** Keşif ajanının değerlendirmesini isteme veya kullanma. Kanıtın URL'sini ve gözlem tarihini yaz; web erişimin yoksa \`BLOCKED\` ve \`UNKNOWN\` de. **Bu görev nihai tier veya score vermez**; kanıtlar ayrı incelemeye gidecek.
