# Yeniden kontrol — 19 Ekim 2026

PR #1'in `Doğrulanamadı` bıraktığı 34 kaynak, tarayıcı benzeri bir istemciyle (sayfayı render eden, normal User-Agent kullanan araç) yeniden denendi. PR #1'in HTTP istemcisi `DisGundemInventory/3.0` UA'sıyla 403 aldığı için çoğu kayıt sahte negatifti.

## Sonuç

| Sonuç | Adet | Kaynaklar |
| --- | --- | --- |
| Canlı (yeniden doğrulandı) | 19 | SOHR, Israel Hayom, Greek City Times, Mada Masr, Tasnim, Amwaj, Al Arabiya, Okaz, Turan, RBC, SCMP, Caixin, ThePrint, Addis Standard, SAM, UIF, Institut Montaigne, Gateway House, APS |
| Canlı (editör teyidi) | 7 | eKathimerini, Politico Europe, Euractiv, DW, NYT, Politico, Reuters — doğrulama aracı bu yayınlara politika gereği erişmiyor; yayında oldukları bilinen büyük yayınlar, editör onayıyla canlı sayıldı |
| Hâlâ doğrulanamadı | 8 | Dışişleri (ABD) brifingleri (fetch hatası), MSB ve Emirates Policy Center (robots.txt araç erişimini engelliyor), FT, Bloomberg, WSJ, Economist, Foreign Policy (premium; erişim Gmail bülteni üzerinden, ana sayfa doğrulaması gerekmiyor) |

Yeni bulunan besleme adresleri: Okaz `https://www.okaz.com.sa/rss`, RBC `https://rssexport.rbc.ru/rbcnews/news/30/full.rss`, Caixin `https://gateway.caixin.com/api/data/global/feedlyRss.xml`, Gateway House `https://www.gatewayhouse.in/rss`. XML ayrıştırması hattın ilk çalıştırmasında doğrulanacak.

## Çekirdek değişikliği

Yeniden doğrulanan kaynaklardan 21'i `Çekirdek`e alındı (PR #1'in koşullu listesindeki K039, K059, K100, K101, K109, K120, K133, K140, K153, K168, K267 dahil; ayrıca Yunanistan çapası eKathimerini K026). Çekirdek 113 → 134.

Çekirdeğe alınmayanlar ve nedeni: Greek City Times (bakış açısı kaynağı), Amwaj (makale listesi JS ile yükleniyor, önce scraping denenmeli), SAM (yayın seyrek), UIF (JS uygulaması, headless gerekir), SOHR (rakam doğrulama yükü).

## Hacim ölçümü

PR #1 269 kaynaktan yalnızca 1'inde sayısal hacim üretebildi. Bu çalışmada hacim elle ölçülmedi; ölçüm hattın kendisine gömüldü (`pipeline` → `measure` komutu): her kaynak için kayan 30 günlük Türkiye-ilgili ve iç gündem sayımı `sources` tablosunda tutulur, 2 haftalık toplama sonunda budama raporu üretilir. Bkz. `docs/MIMARI.md`.
