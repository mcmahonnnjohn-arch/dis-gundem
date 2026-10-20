# Varlık sözlüğü

`varliklar.csv` — kişi, kurum, örgüt, yer ve terimlerin sitede kullanılacak tek doğru biçimi. Özetleme promptu, haberde geçen adların satırlarını modele verir; model unvanı kendi bilgisinden yazmaz (`docs/YAYIN_KILAVUZU.md` §3).

| Sütun | Anlamı |
|---|---|
| `id` | Kalıcı kimlik (A01, B07…). Satır silinmez, `durum=eski` yapılır |
| `tur` | kisi · kurum · orgut · yer · belge · terim |
| `ozgun` | Kaynaklarda geçen özgün/İngilizce biçim (eşleştirme anahtarı) |
| `tr` | Sitede kullanılacak Türkçe yazılış |
| `unvan_tr` | Güncel Türkçe unvan (yalnız kişiler) |
| `ulke` | ISO-2 kod |
| `not` | Kaçınılacak eski unvan/ad, ayrım, editoryal uyarı |
| `kaynak_url` | Güncel unvanı/durumu doğrulayan kaynak |
| `durum` | dogrulandi · belirsiz · karar (kılavuz kararı bekliyor) · eski |
| `dogrulama` | Son doğrulama tarihi |

Unvanlar değişir: `dogrulama` tarihi 60 günden eski kişi satırları haftalık raporda yeniden doğrulamaya düşer.
