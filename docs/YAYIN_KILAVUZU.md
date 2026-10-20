# Dış Gündem — Yayın Kılavuzu (v1.0)

**Durum:** editör onayladı · 20 Ekim 2026
Bu kılavuz, otomatik özetlerin ve editör metinlerinin dilini bağlar. Özetleme promptu (`classify_v2`) bu belgeye ve `data/sozluk/varliklar.csv` sözlüğüne göre çalışır. §4'teki adlandırma tercihleri 20 Ekim 2026'da editör tarafından onaylandı; değişiklik kılavuz sürümünü artırır.

---

## 1. Temel ilke: kaynağa sadakat

1. **Kaynakta olmayanı yazma.** Özet yalnız kaynağın söylediğini aktarır. Arka plan bilgisi eklenecekse yalnız sözlükten ya da aynı kümedeki başka bir kaynaktan gelir ve kaynağı belirtilir.
2. **Yorum ile haber ayrılır.** Kaynağın değerlendirmesi kaynağa atfedilir ("Kathimerini'ye göre…", "yazar … savunuyor"). Sitenin kendi yorumu özete girmez; o, "Analiz" katmanının işidir.
3. **Tahmin yok.** "muhtemelen", "büyük olasılıkla", "-ebilir" ile kurulan, kaynakta dayanağı olmayan cümleler yazılmaz.
4. **Süreç cümlesi yok.** "Lead kesik", "başlık yeterli bilgi vermiyor", "tam metin görülemedi" gibi ifadeler okura gösterilen metne girmez. Belirsizlik `confidence` ve `uyari` alanlarına yazılır; editör kartta görür.
5. **Kesinlik derecesi korunur.** Kaynak "iddia ediyor" diyorsa "açıkladı" yazılmaz; kaynak "kaynaklara göre" diyorsa bu atıf korunur.

## 2. Aktarma fiilleri

| Kaynaktaki durum | Kullanılacak | Kaçınılacak |
|---|---|---|
| Resmi açıklama, kayıtlı beyan | açıkladı, bildirdi, duyurdu | iddia etti |
| İsimsiz kaynak, sızıntı | "… kaynaklara göre", "… olduğu bildirildi" | açıkladı |
| Taraflı/tek taraflı iddia | öne sürdü, iddia etti, savundu | ortaya koydu, kanıtladı |
| Askerî kayıp/saldırı sayıları | "… açıklamasına göre", sayıyı kaynağa bağla | sayıyı çıplak verme |
| Görüş/analiz yazısı | savunuyor, değerlendiriyor, yorumluyor | bildiriyor |

"Ortaya koydu", "gözler önüne serdi", "itiraf etti" gibi hüküm içeren fiiller yalnız kaynak da bu hükmü veriyorsa kullanılır.

## 3. Unvan ve ad kuralları

1. **Unvanlar sözlükten gelir.** Model unvanı kendi bilgisinden yazmaz. Sözlükte olmayan kişide yalnız kaynağın verdiği unvan kullanılır; kaynak unvan vermiyorsa unvan yazılmaz ve kart `sozlukte_yok` uyarısı alır.
2. **İlk geçişte tam ad + unvan,** sonraki geçişlerde soyadı ("Dışişleri Bakanı Hakan Fidan" → "Fidan").
3. **Eski unvan/kurum kullanılmaz.** Sözlükte `not` alanında "kullanma" denen adlar (ör. Libya'da Ulusal Mutabakat Hükümeti, 2021'de sona erdi) özete girmez.
4. **Yazılış AA standardıdır.** Türkçede yerleşik yazılışı olan adlar öyle yazılır (Netanyahu, Zelenskiy, Pezeşkiyan). Yerleşik yazılışı yoksa §5'teki çeviriyazı kuralları uygulanır.
5. **Ülke adı:** metinde "Türkiye". Yabancı kaynağın başlığından aktarılan "Turkey" Türkçe metinde "Türkiye" olur.

## 4. Adlandırma tercihleri (onaylı)

Türk basınında oturmuş ama birbirinden farklı tercihler var. Son sütun geçerli kuraldır.

| Konu | Seçenekler | Kural |
|---|---|---|
| Güney Kıbrıs yönetimi | GKRY · Kıbrıs Rum Yönetimi · Kıbrıs Rum Kesimi · "Kıbrıs Cumhuriyeti" (yalnız atıfla) | **"GKRY"** kısaltma; ilk geçişte "Güney Kıbrıs Rum Yönetimi (GKRY)" |
| Hristodulidis'in unvanı | GKRY Lideri · Rum lider · "Kıbrıs Cumhurbaşkanı" (yalnız atıfla) | **"GKRY Lideri"**, ikinci geçişte "Rum lider" (AA kullanımı) |
| PKK | "terör örgütü PKK" · "PKK" | **İlk geçişte "terör örgütü PKK", sonra "PKK"**. Fesih süreci haberlerinde de bu biçim |
| YPG / SDG | "YPG/SDG" · "SDG" · "PKK/YPG" | SDG 25 Ağustos 2026'da feshini ve Suriye ordusuna katılımını açıkladı. **Geçmiş zamanla "PKK/YPG güdümlü eski SDG"**; bugünkü yapılar için kaynağın adlandırması atıfla |
| Kuzey Irak Kürt yönetimi | IKBY · Kürt Bölgesel Yönetimi | **"IKBY"**, ilk geçişte açık hali |
| Husiler | Husiler · Ensarullah | **"Husiler"** |
| Hizbullah, Hamas | çıplak ad · nitelemeli | **Çıplak ad** (kaynak nitelemesi atfedilerek aktarılabilir) |
| İsrail'in Golan/Güney Suriye varlığı | işgal · varlık · konuşlanma | **Suriye topraklarında BM kararlarına göre "işgal"**; kaynak başka terim kullanıyorsa atıfla |
| Körfez | Basra Körfezi · Fars Körfezi · Arap Körfezi | **"Basra Körfezi"**, kısaca "Körfez" |
| Ukrayna başkenti | Kiev · Kyiv | **"Kiev"** (AA) |
| ABD Savunma/Savaş Bakanlığı | Savunma Bakanı · Savaş Bakanı | **"ABD Savunma Bakanı"** (AA hâlâ böyle yazıyor; resmi ad değişikliği gerekirse not edilir) |
| AA ile Dışişleri yazımı ayrıştığında | AA · Dışişleri Bakanlığı | **AA** (ör. "Ulusal Birlik Hükümeti", "Akile Salih"; Dışişleri "Milli Birlik Hükümeti", "Agila Salih" yazıyor) |
| İran yönetimi | İran yönetimi · Tahran · "rejim" | **"İran yönetimi" / "Tahran"**; "rejim" yalnız atıfla |
| Ege adaları, kıta sahanlığı | Türk tezi terimleri · nötr | **Türk tezi terimleri** (ör. "gayri askerî statüdeki adalar"); Yunan tezi atıfla aktarılır |

## 5. Çeviriyazı (yerleşik yazılışı olmayan adlar)

- **Arapça:** Türk basını geleneği. `al-` → "el-" (güneş harflerinde ses uyumu: "eş-Şeybani", "es-Sisi"); "Mohammed" → "Muhammed"; "q" → "k"; "kh" → "h"; "dh/th" → "z/s". Kısa adlarda harfi tarif sadeleştirilir: "Ahmed eş-Şara".
- **Farsça:** "Mesud", "Abbas Arakçi"; "zh" → "j"; "kh" → "h".
- **İbranice:** İngilizce yaygın biçim Türkçe ses uyumuyla: "Yisrael Katz", "Gideon Saar".
- **Rusça/Ukraynaca:** AA biçimi ("Zelenskiy", "Umerov", "Kıslıtsya"); Ukraynalı kişilerde Ukraynaca okunuş esas.
- **Yunanca:** AA biçimi ("Miçotakis", "Gerapetritis", "Hristodulidis").
- Emin olunmayan çeviriyazı sözlüğe `belirsiz` olarak girer, editör onaylar.

## 6. Özet biçimi

- 2–3 cümle, 600 karakteri geçmez; **ilk cümle olgu**: kim, ne yaptı, nerede, ne zaman.
- İkinci cümle bağlam ya da kaynağın vurgusu; kaynağa atfedilir.
- Türkiye bağlantısı kaynakta varsa üçüncü cümlede belirtilir; yoksa uydurulmaz.
- Kaynağın yayın organı ve ülkesi özetin içinde tekrar edilmez (kartta zaten var); yalnız kaynağın çerçevesi anlatılıyorsa anılır.
- Doğrudan alıntı en fazla 15 kelime, tırnak içinde, söyleyene atfedilir.

## 7. Makale metni (20 Ekim 2026 editör kararı)

Yalnız kuyruğa giren haberlerde, özetleme sırasında makale metni okunur. Metin **saklanmaz**, veritabanına ve loglara yazılmaz; yalnız o çağrı için modele verilir. Özet kendi cümlelerimizle yazılır, telif sınırları (§6) değişmez. Ödeme duvarlı ya da erişilemeyen metinde başlık+lead ile devam edilir ve kart `metin_yok` uyarısı alır.

## 8. Uyarı etiketleri (editör kartında)

| Etiket | Anlamı |
|---|---|
| `metin_yok` | Makale metnine erişilemedi, özet başlık+lead'den |
| `sozlukte_yok` | Özette sözlükte olmayan kişi/kurum var |
| `denetim` | Denetim adımı kaynakta olmayan iddia, ad ya da sayı buldu |
| `tek_kaynak` | Taraflı ve teyitsiz tek kaynak (ör. ordu açıklaması, kayıp sayısı) |
| `dusuk_guven` | `confidence` < 0,6 |

## 9. Düzeltme döngüsü

Editörün kuyrukta yaptığı her düzeltme kaydedilir. Aynı türden düzeltme iki kez tekrarlanırsa sözlüğe ya da bu kılavuza eklenir; kılavuz sürümü artar (v0.2…).
