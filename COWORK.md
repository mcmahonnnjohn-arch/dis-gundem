# Claude Cowork — 30 kaynaklık pilot

**Başlangıç:** \`cowork/00_RUNBOOK.md\`. Bu dosya Cowork için giriş noktasıdır; \`.claude/agents/\` Claude Code subagent tanımlarıdır ve Cowork'te otomatik çalıştıkları varsayılmamalıdır.

## Hedef
30 kaynaklık pilotu bağımsız araştırma, doğrulama, provenance, red-team ve editoryal kapıdan geçir. 150 kaynaklık hedef: **35 RADAR / 65 WEEKLY / 50 EVENT**. Mevcut \`data/kaynak_envanteri_v3.csv\` 269 adaydan oluşur; pilot yalnız 28 eski + 2 yeni kaynağı kapsar.

## Cowork'te yapılacaklar
1. GitHub PR #37'nin \`feat/source-universe-pilot-30-harness\` dalını yerel klasöre indir veya klonla; Cowork'e bu klasöre erişim ver.
2. \`cowork/01_DISCOVERY.md\` talimatlarını **Görev 1** olarak çalıştır.
3. **Yeni, bağımsız Cowork görevi** aç. Yalnız \`cowork/verification_brief_30.csv\` ve \`cowork/02_VERIFICATION.md\` ile başla; scout notlarını verme.
4. \`cowork/03_PROVENANCE.md\`, \`cowork/04_RED_TEAM.md\` ve \`cowork/05_EDITORIAL_GATE.md\` için ayrı görevler aç.
5. Koordinatör kanıt dosyalarını birleştirir; Python testleri ve CI'ı çalıştırır. \`gate --mode readiness\` GO vermezse **150'ye genişletme**.

**Sınırlar:** Cowork'in web, terminal, GitHub ve dosya erişimi kurulum/izinlere bağlıdır. Erişilemeyen kanıt için UNKNOWN/BLOCKED yaz; araştırılmış gibi gösterme. Kod çalıştırılamıyorsa testler GitHub Actions üzerinde yürütülür. Cowork çıktısı kendiliğinden editoryal onay değildir.

**Asıl uygulama notu:** \`docs/SOURCE_UNIVERSE_PILOT.md\`
