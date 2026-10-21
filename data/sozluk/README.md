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

Olayların haritaya düştüğü yerler `yerler_*.csv` dosyalarındadır: `yerler_sy.csv` (Suriye, 117 kayıt), `yerler_ulkeler.csv` (her ülke için ülke geneli kaydı, 38 kayıt), `yerler_diger.csv` (`varliklar.csv`'deki Suriye dışı yerler ve deniz alanları). Yeni ülke eklerken `yerler_<ülke>.csv` açılır. `disgundem seed` ile `places` tablosuna yüklenir; `disgundem harita` LLM'in yazdığı yer adını buradaki `id`ye ya da takma adlara (`aliases`, `|` ile ayrılmış Türkçe/İngilizce/Arapça yazımlar) eşler. Eşlenemeyen adlar `place_unresolved` tablosuna düşer: editör ya `resolved_to` ile mevcut yere bağlar ya da yeni satır ekler.

| Sütun | Anlamı |
|---|---|
| `id` | `<ülke>-<ad>` (ör. `sy-tel-rifat`); vilayetler `sy-v-…`, ülke kaydı yalnız kod (`sy`) |
| `name_tr` | Yayın adı; `varliklar.csv` ile aynı yazılış (test bunu denetler) |
| `kind` | sehir · ilce · bolge · sinir_kapisi · liman · us · tesis · deniz_alani · ulke |
| `precision` | nokta · sehir · bolge · ulke. `ulke` kayıtları (yer belirtilmeyen ulusal haberler) haritada **işaretçi olarak çizilmez**, "Ülke geneli" listesinde gösterilir (`map_events.country_level`); koordinatları yalnız çıpadır (başkent). Vilayet kayıtları yaklaşık merkezdir |
| `lat`, `lon` | WGS84 ondalık |
| `verified` | `false` olan yer sitede görünmez (RLS); olay en yakın doğrulanmış şehre bağlanmalı |
| `koordinat_kaynagi` | GeoNames / Wikipedia bağlantısı ya da `elle` |

Şehir ve başkent koordinatları GeoNames'ten, sınır kapısı/üs/tesis/deniz alanı koordinatları Wikipedia'dan doğrulandı (21 Ekim 2026). Boğaz ve körfezler (`deniz_alani`) `kuresel` ülkesi altındadır; model ülkeyi yanlış verse de adla eşleşir. Doğrulanamayan 5 kayıt `verified=false`: Bab es-Selame, Cedide Yabus, Tartus Limanı, Humus Rafinerisi, Conoco sahası.

`aktorler.csv` — olaylarda rol alan devlet, örgüt ve silahlı gruplar (`cluster_actors`). Adlar Yayın Kılavuzu §4'e uyar; feshedilmiş yapılar (`aktif=0`: HTŞ) geçmiş olaylar için kalır. Eski SDG kılavuz gereği "PKK/YPG güdümlü eski SDG" adıyla tutulur.
