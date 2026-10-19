# Premium tarama çıktıları

Claude in Chrome oturumu (editörün kendi FT/Bloomberg/WSJ/Economist/FA/FP abonelikleri) her tarama sonunda buraya
`YYYY-MM-DD.json` yazar; `disgundem premium-import data/premium/YYYY-MM-DD.json` kuyruğa alır.

Biçim (liste):
```json
[{"source_id":"K170","url":"https://www.ft.com/content/...","title":"...","published_at":"2026-10-19",
  "summary_tr":"Kendi cümlelerimizle 2-3 cümle.","countries":["sy","tr"],"themes":["ekonomi"],"dossiers":["yeniden-insa"],
  "frame":"notr","importance":null,"note":"FT'nin çerçevesi: ..."}]
```
Makale metni, 600 karakterden uzun özet veya 15 kelimeden uzun alıntı içeren kayıt reddedilir.
