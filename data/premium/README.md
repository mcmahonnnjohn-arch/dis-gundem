# Claude in Chrome oturum çıktıları

Claude in Chrome oturumu, `data/chrome_kaynaklari.csv` listesindeki kaynakları editörün kendi tarayıcısından
(premium için kendi abonelikleriyle) tarar ve her oturum sonunda buraya `YYYY-MM-DD.json` yazar;
`disgundem chrome-import data/premium/YYYY-MM-DD.json` kuyruğa alır (`premium-import` eski adıyla da çalışır).

Liste iki katmandan oluşur:
- **premium** (6): FT, Bloomberg, WSJ, Economist, Foreign Affairs, Foreign Policy — sunucuda hiç toplanmaz.
- **engelli-rss** (14): RSS'i sunucuya 403 veren kaynaklar — sunucuda gnews yedeğiyle de izlenir, Chrome doğrudan yayıncı sayfasından tamamlar.

Biçim (liste):
```json
[{"source_id":"K170","url":"https://www.ft.com/content/...","title":"...","published_at":"2026-10-19",
  "summary_tr":"Kendi cümlelerimizle 2-3 cümle.","countries":["sy","tr"],"themes":["ekonomi"],"dossiers":["yeniden-insa"],
  "frame":"notr","importance":null,"lang":"en","note":"Yayının çerçevesi: ..."}]
```
`source_id` listede yoksa kayıt reddedilir. Makale metni, 600 karakterden uzun özet veya 15 kelimeden uzun alıntı içeren kayıt da reddedilir.
