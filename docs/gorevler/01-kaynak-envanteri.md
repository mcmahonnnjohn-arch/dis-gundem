# Görev 01: Kaynak havuzunu yayına hazır envantere dönüştür

Bağlam: Türkiye'nin aktif olduğu coğrafyalardaki gelişmeleri ve dünyanın Türkiye'ye bakışını derleyen "Dış Gündem" adlı bir haber/analiz sitesi kuruluyor. Önce `docs/HEDEF.md` ve `docs/KAPSAM_MODELI.md` dosyalarını oku. `data/kaynak_havuzu_v2.csv`, 259 kaynaklık bir başlangıç taslağıdır; doğrulanmadı ve eksiktir. İki ana kapsam seviyesi var: A = yakın çevre ülkeleri (kritik iç haberleri + Türkiye ile ilgili her şey), B = diğer ülkeler (yalnızca Türkiye'ye bakış). R, T ve P kaynak rolleridir (bkz. `KAPSAM_MODELI.md`). Havuzun 111'i think tank; bunlar haber değil analiz girdisi. `data/turkiye_terimleri.csv` dillere göre anahtar terimleri ve Google News edisyon kodlarını içeriyor.

## İstenen
Bu havuzu yayına hazır bir kaynak envanterine dönüştür.

- Her kaynağı doğrula: ayakta mı, çizgisi/sahipliği doğru yazılmış mı, RSS adresi ne (yoksa en iyi alternatif besleme veya scraping yolu).
- Her kaynağın son 30 gündeki Türkiye-ilgili içerik hacmini ve A kapsamı ülkelerde iç gündem hacmini ölç; pilota değmeyenleri gerekçesiyle çıkar, kaçırılan önemli kaynakları ekle. Özellikle yerel dilde yayın yapan kaynaklara dikkat et; İngilizce vitrinlerle yetinme.
- Think tank'leri ayrı değerlendir: her ülke için hangi kuruluşların Türkiye'yi düzenli yazdığını ve hangi perspektifi temsil ettiğini raporla.
- Ülke başına kısa bir "medya sahası notu" yaz: hangi yayın kime yakın, hangi perspektif eksik, nereye güvenilmez.

## Çıktı
1. Doğrulanmış envanter: aynı sütun yapısında CSV, `data/kaynak_envanteri_v3.csv`.
2. Çıkarılan ve eklenen kaynaklar listesi: `docs/envanter/degisiklikler.md` (her satırda gerekçe).
3. Ülke notları: `docs/envanter/ulke_notlari.md`.
4. Think tank raporu: `docs/envanter/think_tank_raporu.md`.
5. Önerilen çekirdek set ve gerekçesi: `docs/envanter/cekirdek_set.md`.

Kapsam, bölge sınıflandırması ve kaynak sayısı konusunda karar verme yetkisi görevi yapandadır; daha iyi bir yapı görülürse değiştirilir ve nedeni yazılır.

## Kurallar
- Doğrulanamayan her alan boş bırakılmaz, "doğrulanamadı" yazılır ve nedeni notlanır. URL, RSS ve hacim değerlerini tahmin etme, ölçemediğini ölçülmüş gibi yazma.
- Havuzda bilinen sorunlar: RSS işaretli 242 kaynaktan 202'sinin besleme URL'si boş; Gulf Research Center (K060, K207) çift kayıt; Orta Asya ve Balkanlar yok (ikinci faz, bu görevde eklenmesi serbest ama zorunlu değil).
- Hacim ölçümünde yöntemi (hangi sorgu, hangi tarih aralığı, hangi terim) `docs/envanter/yontem.md` dosyasına yaz, böylece ölçüm tekrarlanabilir olsun.
- Premium kaynaklar (FT, Bloomberg, WSJ, Economist) için yalnızca bülten/başlık erişimi doğrulanır; makale metni toplanmaz.
- Çalışma tek PR olarak açılır, merge edilmez.
