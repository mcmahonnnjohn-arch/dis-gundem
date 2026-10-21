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

## Harita sözlükleri (0008_harita.sql)

`yerler_<ülke>.csv` — olayların haritaya düştüğü yerler; ülke başına bir dosya (ilk sürüm: `yerler_sy.csv`, 118 kayıt). `disgundem seed` ile `places` tablosuna yüklenir; `disgundem harita` LLM'in yazdığı yer adını buradaki `id`ye ya da takma adlara (`aliases`, `|` ile ayrılmış Türkçe/İngilizce/Arapça yazımlar) eşler. Eşlenemeyen adlar `place_unresolved` tablosuna düşer: editör ya `resolved_to` ile mevcut yere bağlar ya da yeni satır ekler.

| Sütun | Anlamı |
|---|---|
| `id` | `<ülke>-<ad>` (ör. `sy-tel-rifat`); vilayetler `sy-v-…`, ülke kaydı yalnız kod (`sy`) |
| `name_tr` | Yayın adı; `varliklar.csv` ile aynı yazılış (test bunu denetler) |
| `kind` | sehir · ilce · bolge · sinir_kapisi · liman · us · tesis · deniz_alani · ulke |
| `precision` | nokta · sehir · bolge · ulke (vilayet ve ülke kayıtları yaklaşık merkezdir) |
| `lat`, `lon` | WGS84 ondalık |
| `verified` | `false` olan yer sitede görünmez (RLS); olay en yakın doğrulanmış şehre bağlanmalı |
| `koordinat_kaynagi` | GeoNames / Wikipedia bağlantısı ya da `elle` |

Şehir koordinatları GeoNames'ten, sınır kapısı/üs/tesis koordinatları Wikipedia'dan doğrulandı (21 Ekim 2026). Doğrulanamayan 5 kayıt `verified=false`: Bab es-Selame, Cedide Yabus, Tartus Limanı, Humus Rafinerisi, Conoco sahası.

`aktorler.csv` — olaylarda rol alan devlet, örgüt ve silahlı gruplar (`cluster_actors`). Adlar Yayın Kılavuzu §4'e uyar; feshedilmiş yapılar (`aktif=0`: HTŞ) geçmiş olaylar için kalır. Eski SDG kılavuz gereği "PKK/YPG güdümlü eski SDG" adıyla tutulur.
