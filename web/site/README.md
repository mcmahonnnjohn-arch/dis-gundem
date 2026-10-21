# Dış Gündem — okur sitesi (Astro, statik)

Ana sayfa ve olay kartı akışı. Tasarım kaynağı: `../tasarim/ana-sayfa-revize` (Stitch); düzen Yayın Kılavuzu §13'e göre sadeleştirildi.

```
npm install
npm run dev        # http://localhost:4321
npm run build      # dist/ (statik)
```

## Veri

- `PUBLIC_SUPABASE_URL` + `PUBLIC_SUPABASE_ANON_KEY` varsa derleme sırasında `clusters` (status=published, `merged_into` boş) ve bağlı `articles/sources/countries/regions` okunur. Yalnız **anon** anahtar; RLS yalnız yayımlanmış satırları açar. Bu yol henüz gerçek bir Supabase'e karşı denenmedi.
- Anahtar yoksa `src/data/ornek.json` kullanılır ve sayfa üstünde "Örnek veri" şeridi çıkar. `npm run ornek`, `data/test_seti/ozet_test_seti.jsonl` (editör referans özetleri) ve kaynak envanterinden üretir. Örnekte başlık, özetin ilk cümlesinden türetilir; gerçek veride `clusters.title_tr` kullanılır.

## Karar ve sınırlar

- Okur ekranında yalnız: bölge/ülke künyesi, başlık, özet, varsa **Bakış farkı**, kaynaklar (yayın · ülke · dil; özgün başlık kendi yazı yönünde). Kaynak kodu, önem puanı, uyarı etiketleri yok (§13.2).
- Tasarımdaki uydurma bölümler (algı barometresi, piyasa kutuları, "Seviye" matrisi, son dakika şeridi, uydurma künyeler) taşınmadı; bkz. `../tasarim/README.md`.
- "Dışarıdan Türkiye" bölümü: kümede B kapsamlı (yalnız Türkiye'ye bakış) kaynak ya da `is_turkey_related` haber varsa. Bu ölçüt ilk tahmindir; editörle gözden geçirilmeli.
- Yok: olay detay sayfası, ülke masası, harita, arama, editör görünümü, `kisa_aciklama` (§11) ile terim açıklaması. Özetler zaten ilk geçişte açıklamayı taşımalıdır (özetleme prompt'unun işi).
- Yazı tipleri Google Fonts'tan gelir (Playfair Display, Merriweather, IBM Plex Sans).
