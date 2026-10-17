# Doğrulama ve ölçüm yöntemi

## Ne ölçüldü, ne ölçülmedi?

Bu çalışma kaynak/edisyon kimliği, açık ana sayfa erişimi, RSS/Atom/sitemap yolu, gözlenen metadata ve kaynaklı editoryal bağlam envanteridir. **269 kaynağın tümü için aylık içerik hacmi ölçülmüş değildir.** CSV’de 268 Türkiye hacmi hücresi ve 116 A iç gündem hücresi, nedenleriyle `ölçülemedi` kalır. K004’ün seçili İngilizce edisyonunda tam arşiv ve altı açık makale incelemesi 1 Türkiye bağlantılı, 3 kritik iç gündem sonucunu destekler. Bu örnek, başlık filtresindeki 0 eşleşmenin gerçek ilgide 0 anlamına gelmediğini gösterir.

Ana hacim, dönem içindeki ayrı yayınlarda somut Türkiye bağlantısının içerik incelemesiyle doğrulanmış sayısıdır. Kişinin geçmişte İstanbul’da bulunması veya eski bir fotoğrafın Türkiye’de çekilmiş olması tek başına yeterli görülmez. A iç gündemi, ilgili ülkenin politik/güvenlik/ekonomi/enerji/karar gündeminde `KAPSAM_MODELI.md` önem eşiği ≥3 olan içerik sayısıdır; bütün haberlerin veya sırf ülke adını anan başlıkların sayısı değildir. K004 puanları editoryal sınıflamadır; yayın onayı yerine geçmez.

## Sabit tarih penceresi

- Yerel: **18 Eylül 2026 00:00:00 +03:00 dahil → 18 Ekim 2026 00:00:00 +03:00 hariç**; 30 tamamlanmış gün.
- UTC: **2026-09-17T21:00:00Z ≤ ilk yayın tarihi < 2026-10-17T21:00:00Z**.
- HTTP taramaları 17 Ekim 2026 UTC akşamı yapıldı; nihai değerlendirmede kullanılan isteklerin gerçek zamanı kanıt JSONL’sindedir. Tarama saatini yayın tarihinin yerine kullanma. Pencere bittikten sonra gelen 18 Ekim yerel haberleri sayma.
- RSS: `pubDate`, Atom `published`, RSS 1.0 `dc:date`. Sadece `updated`, sitemap `lastmod`, arama motoru tarama tarihi veya ay adı ilk yayın tarihi sayılmaz. Saat dilimi olmayan bir feed tarihi geçici olarak UTC kabul edildi; bu belirsizlik tam aylık sayımı onaylamaya yeterli değildir. WordPress’te `date_gmt` kullanıldı; tarihi olmayan veri ölçüme alınmadı.
- K004’te 17 Eylül’de ilk yayımlanıp 21 Eylül’de güncellenmiş kayıt doğru biçimde dışlandı. Arapça edisyonun farklı tarihli yayınları İngilizce sayıma eklenmedi.

## Girdiler ve araçlar

Başlangıç: `data/kaynak_havuzu_v2.csv` (259 satır), `data/turkiye_terimleri.csv` (16 dil), yukarıda belirtilen üç hedef/kapsam/görev belgesi. Kaynak CSV’si ilk 15 sütun sırası korunarak işlendi. Çıktı 29 sütundur; yeni sütunlar eski tüketiciler için ayrıca değerlendirilmelidir, bu PR uygulama tüketicisini değiştirmez.

Teknik araç: Python 3.12 standart kütüphane (`urllib.request`, `xml.etree.ElementTree`, `html.parser`, `csv`, `json`, `hashlib`, `datetime`, `email.utils`, `concurrent.futures`). Yayıncı ana sayfalarının doğrudan web açılışları ve kurumsal/sahiplik araştırmaları için Search Service `system1_search_query`, `system2_search_query`, `open`, `find`, `click` kullanıldı. Bot/oturum duvarı çözülmedi. Son CSV, artifact-tool Workbook hücre matrisi üzerinden yazılıp `Workbook.fromCSV` ile yeniden okunarak bütün hücreleri karşılaştırıldı; formül veya yeniden hesaplanabilir sayfa üretilmedi.

Araştırma sorguları kurum adına göre “<kurum> Turkey/Türkiye program publications”, “<kurum> about funding donors annual report ownership” ve yerel dilde eşdeğer konu/kurum adlarıdır. Genel arama sonucu sayısı bir aylık hacim ölçümü değildir. Think tank satırlarındaki `evidence_urls` hangi kurumsal program, bağış, künye veya yayın sayfasının iddiayı desteklediğini gösterir; tarihsel belge güncel bütçe diye sunulmaz.

## Canlılık ve besleme kontrolü

1. V2 URL’sine normal GET yapıldı; son URL, HTTP durum, içerik türü, UTC zamanı, yanıt uzunluğu ve SHA-256 tutuldu. HTTP 200 tek başına yeterli değil: `Site Unavailable`, RunCloud karşılama, giriş veya challenge ekranı gerçek yayın ana sayfası sayılmadı. K118, K109 ve K135 gibi sınır durumları bağımsız web kontrolüyle de incelendi. K135’in ikinci web kanalında görülen başlıkları, ana HTTP yolundaki hatayı gizlemek için `Canlı`ya çevrilmedi.
2. Önce mevcut RSS URL’si; sonra HTML’deki RSS/Atom linkleri; sonra uygun açık standart adaylar `/feed/`, `/rss.xml`, `/rss` denendi. Kaynak başına en fazla 7 besleme adayı. URL tahmini yalnız bir istek adayıdır; XML ve yayın kayıtları okunmadan çalışan URL diye yazılmadı. Premiumlarda açık bülten/başlık bağlantıları dışında makale yolu izlenmedi.
3. RSS/Atom/RDF kökü ve item/entry yapısı ayrıştırıldı; yalnız başlık, URL ve ilk yayın metadata’sı kullanıldı. Boş/tarihsiz veya son kaydı pencere öncesinde kalan akış otomatik çekirdekte genel yayın RSS’si diye onaylanmadı. RAND podcast’i, RUSI etkinliği, MFA’nın Other Papers bölümü, ORDAF sayfa akışı, AVİM Facebook akışı, AGERPRES üçüncü taraf proxy’si ve AFP kurum haberleri ayrıca kapsam nedeniyle elendi.
4. Uygun RSS bulunamazsa `robots.txt` içinde ilan edilen ilk sitemap ve gerekirse `/sitemap.xml` denendi; XML kökü `urlset`/`sitemapindex` olmalı. Sitemap’in çalışması tarih/kapsam/öğe erişim izni kanıtı değildir. Scraping alternatifi yalnız kamuya açık başlık/liste yoludur; yazılmış veya denenmiş bir içerik scraper’ı yoktur.
5. Bir origin’de HTTP 401/403/429 veya belirgin CAPTCHA/challenge görülünce o taramadaki sonraki origin adayları durduruldu. HTTP 402, 5xx, timeout ve tamamlanamayan yönlendirmeler somut nedenle tutuldu. 403’ün nedenini kanıt olmadan belirli bot sistemi diye teşhis etmedik. Bu hatalar `Ölü` kanıtı değildir; kesin kapanışı doğrulanmış kaynak bulunmadığı için `Ölü=0`.
6. Aynı kurumun doğrulanmış güncel alan adı/kimliği için `Taşındı` kullanıldı. Edisyon seçimi, aynı alan adı içindeki normal yönlendirme veya yalnız tahmin edilen yeni adres tek başına taşınma değildir. K006/K007/K107/K123/K166/K190/K192/K196/K210/K212/K253 eski ve yeni adres/kurumsal kanıtlarıyla bu gruptadır.

GET sınırları: User-Agent `DisGundemInventory/3.0 (public metadata verification; no article crawling)`; istek zaman aşımı 10 saniye; normal yanıt en fazla 2.000.000 bayt; ana/besleme taraması 10, API ve Google News 8 eşzamanlı iş. Boyut kesilmesi kayda geçti; kesilmiş XML tam veri sayılmadı. Başarısızlığı aşmak için kimlik bilgisi, farklı IP/proxy, CAPTCHA çözümü veya gizli uç nokta kullanılmadı. HTML’de ilan edilmiş herkese açık K014 besleme parametresi özel kimlik bilgisi değildir; standart parametresiz adres ayrıca XML vermedi. K208’in parametresiz RSS’si doğrudan doğrulanıp seçildi.

## Türkiye terimleri ve eşleşme

Teknik sözlüğün kaynağı `data/turkiye_terimleri.csv`dir; dosya değiştirilmedi. Seçili dil kodları dosyadaki dil satırlarına eşlenir. `Türkiye`, `Ankara`, `Erdoğan`, `Türk (sıfat)` hücreleri `/` üzerinden alternatiflere bölünür, boşluklar temizlenir, aynı terimler tekilleştirilir. İngilizcede Turkey/Türkiye birlikte alınır. Başlıklar Unicode NFKC + casefold ile normalleşir; Çince terimler alt dize, diğer terimler Unicode kelime sınırıyla eşleşir. Çekim/stemming/transliterasyon genişletmesi yapılmadı; olası kaçırmalar bu yüzden vardır. Eşleşme içerik ilgisi onayı değildir; İngilizce turkey hayvan anlamında da geçebilir.

Sözlükte **Gürcüce, Romence, Japonca, Urduca, İtalyanca, Hollandaca, Amharca, Oromoca ve Hausa** satırları yok. Seçili akış bu dilleri içeriyorsa aday sütunundaki 0 yalnız mevcut sözlük gözlemidir; Türkiye ilgisi yok anlamına gelmez. Uygun dil satırı bulunmayan Google News keşfinde İngilizce terimler kullanıldı ve kapsam eksiği kayda geçirildi. K140 Hintçe girişindeki CAPTCHA, K153 Amharca 403, K267 APS 500 gibi açıklar dil başarısı diye sayılmadı. T kaynaklarında önerilen ters filtre otomatik olarak uygulanmadı; yalnız ülke adını dışlamak dış politika yazılarını da kaybettirebilir. T hacmi, iç gündem/hedef ülke ayrımı tamamlanmadığı için ölçülemedi.

## WordPress başlık metadata’sını tekrarlama

48 kaynağın uygun görünen kamuya açık API’si incelendi. **42’sinde seçili türlerin sayfalaması tamam; bu, kurumun bütün yayınlarının tamam olduğu anlamına gelmez.** WordPress tür keşfi `GET /wp-json/wp/v2/types?context=view`. Kullanılan beyaz liste: `post, research, publication, publications, article, articles, analysis, analyses, report, reports, news, perspective_post, perspective, makale, yayin, yazi`. `page`, `attachment`, yazar profili, ortak, şablon ve açık `event` türü seçilmedi. `post` türünün kendisi de etkinlik/duyuru içerebilir.

Her türün ilan edilen `rest_namespace/rest_base` değerine aşağıdaki istek yapıldı:

```text
GET {base}/wp-json/{rest_namespace}/{rest_base}
?context=view
&after=2026-09-16T00:00:00
&before=2026-10-20T00:00:00
&per_page=100&page={1..N}
&orderby=date&order=desc
&_fields=id,date,date_gmt,link,title,type
```

Tarih sorgusundaki geniş pay, site saat dilimi farkında sınır kayıt kaybetmemek içindir; asıl 30 günlük filtre her kaydın `date_gmt` değeri üzerinde UTC aralığıyla uygulanır. `content`, `excerpt`, makale HTML’si istenmedi. Her sayfada `X-WP-Total` / `X-WP-TotalPages`, alınan kayıt ve ID/URL tekilliği kontrol edildi. 20 sayfa/2.000 kayıt sınırında duruldu. K034’te en eski alınan kayıt 2 Ekim, K029’da 7 Ekim, K030’da 9 Ekim olduğu için üçünde de başlangıca ulaşılamadı. API sıfır sonucu bütün kurum için sıfır üretim değildir.

Somut kapsam açıkları: ISPI K233 `pubblicazioni/pubblicazione/informarsi_mondo`, K190 `opinion/magazine/forum`, TRENDS K210 `observatory-pub/observatory-mag` gibi başka yayın türleri kullanıyor. K124 API/RSS kurumsal genel akıştır; Türkiye programının özgün çıktısı sanılmamalı. API taramasındaki `base` eski/İngilizce bir edisyonsa sonraki yerel dil URL düzeltmesinin hacmi diye okunmaz; bu adres CSV ölçüm kapsamına ve kanıta yazılmıştır. İlk keşif denemelerindeki hatalı/eksik tür seçimleri nihai metadata sayısına alınmadı.

Resmî API tanımları: [Posts ve tarih alanları](https://developer.wordpress.org/rest-api/reference/posts/) · [Pagination](https://developer.wordpress.org/rest-api/using-the-rest-api/pagination/) · [_fields](https://developer.wordpress.org/rest-api/using-the-rest-api/global-parameters/) · [Post types](https://developer.wordpress.org/rest-api/reference/post-types/).

## Google News keşif sorgusunu tekrarlama

153 kaynak için yayıncı RSS’si yetersiz/uygunsuz olduğunda alternatif arama RSS’si açıldı. Kullanılan kalıp:

```text
site:{www öneki çıkarılmış domain} ("terim1" OR "terim2" OR ...)
after:2026-09-16 before:2026-10-20
https://news.google.com/rss/search?q={URL-encoded sorgu}&hl=en-US&gl=US&ceid=US:en
```

Her kaynakta tam sorgu, kullanılan terimler, gerçek URL, UTC istek zamanı, XML yanıt hash’i ve gözlenen örneklem bilgisi kanıtlarda saklanır. Bu teknik tarama **bilinçli olarak US:en edisyonunu sabit kullandı**; terim dosyasındaki ülke/dil edisyonlarının tamamı sorgulanmadı. Dolayısıyla yerel dil indeks kapsamı ve ülke bazlı tamlık iddia edilmez. Google News sonuçları indeks/cap/sıralama/saat farkından etkilenebilir; birçok sorgu 100 kayıtta kalır. 0 sonuç yayın yok demek değildir; sonuç sayısı kaynak geneli aylık hacim değildir.

Bu sorgular sabit geçmiş pencere içindir; üretimde kayan son 30 günlük besleme yerine kullanılmamalı. `pubDate` üzerinden asıl UTC pencere tekrar uygulanır. Google yönlendirme URL’si yayıncı kanonik URL’siyle her zaman aynı değildir; GNews ve yayıncı akışları çapraz toplanıp tek aylık toplam yapılmadı. Kaynağın kendisi engelliyse GNews sonucu `Doğrulanamadı` durumunu kaldırmadı.

## K004 tam içerik pilotini tekrarlama

Seçili edisyon `https://syriadirect.org/` İngilizce; [latest](https://syriadirect.org/latest/), [reports](https://syriadirect.org/reports/) ve [multimedia](https://syriadirect.org/multimedia/) dönem arşivleri kontrol edilir. Latest’te altı dönem kaydından sonra 17 Eylül ve öncesine geçilir; reports beş ve multimedia bir kayıtla aynı altı URL’yi tamamlar. Diğer özel bölümler ve API türleri, dönem içinde kaçmış bir İngilizce yayın görünmediğini destekler. RSS ve tam sayfalanmış API’deki URL kümesi arşivle birebir karşılaştırılır.

Altı açık makalenin tamamı web aracında okunur; gövdeler/alıntılar repoya kaydedilmez. Türkiye bağlantısı, A iç gündemi, önem puanı ve bir cümle gerekçe her URL için [pilot kanıtında](kanitlar/suriye_direct_pilot.json) bulunur. Başlıkta 0 eşleşme; gövde/fotoğraf altında 3 terim adayı; somut içerik bağlantısında 1 kabul; önem≥3 iç gündemde 3 kabul. Türkiye bağlantısı olan kitap değerlendirmesinin iç gündem puanı 2 olabilir; iki sütun birbirine otomatik eşitlenmez. Bu, kaynakların tüm dilleri için toplam değildir.

## Kanıtların yapısı ve yeniden üretim

`kanitlar/mena.jsonl`, `eurasia_africa.jsonl`, `west_turkey.jsonl`: her satır bir özgün/güncel kaynak ID’sinin kontrol sonucudur. 269 mevcut kayıt ve iki birleşme izi dahil 271 ID bulunur. Her kayıtta eski/güncel URL istekleri, erişim nedenleri, besleme sonucu, varsa sitemap, kurum bağlamı bağlantıları, ölçüm penceresi/terimleri ve API/GNews sorguları vardır. K187/K207 `superseded_by` ile yönlendirilir. [202 RSS sonuç tablosu](rss_202_sonuclari.md) özellikle başlangıçta boş olan satırları incelemeyi kolaylaştırır.

Makale başlıklarının/metinlerinin büyük bir kopyası üretilmedi. Metadata özetinde tam evrenin kayıt sayısı, pencere içi adet, en eski/en yeni tarih ve normalleşmiş metadata SHA-256 bulunur; başlıklar `title_sha256` ile temsil edilir. Her kaynağın en fazla 10 başlık adayı, RSS’de en fazla 5, GNews’te en fazla 2 örnek URL tutulur. K004’ün altı kayıtlık evreni tam tutulur; yine gövde ve başlık alıntısı yoktur. Örneklerin sayısı toplamın kendisi değildir. Diğer kayıtlar için tekrar ölçüm, kaydedilmiş sorguların ve sayfalamanın yeniden çalıştırılmasıyla yapılır.

Kanonik tekilleştirme, aynı kaynakta URL fragmentini ve `utm_*`, `fbclid`, `gclid` izleme parametrelerini çıkarıp URL’yi eşler; farklı dil çevirileri otomatik birleştirilmedi. Metadata listesi hash’i UTF-8, `ensure_ascii=False, sort_keys=True, separators=(',', ':')` JSON serileştirmesinin SHA-256 değeridir. HTTP body hash’i kontrol anındaki en fazla 2 MB’lık yanıtı tanımlar; sayfa dinamikse yeni çalıştırmada aynı hash beklenmez. Kanıt, tarihli bir gözlemdir; gelecek erişilebilirlik garantisi değildir.

Tekrar çalıştıran kişi (1) aynı v2/terim girdisini alır, (2) kaynak ID’sinin kaydedilmiş GET/RSS/API/GNews URL’lerini sırayla uygular, (3) aynı UTC pencere/terim/tekilleştirme kuralını uygular, (4) tamlık sağlanamazsa ana hacmi yine `ölçülemedi` tutar, (5) sayısal hacim için arşiv tamlığını ve bütün içeriklerin anlamsal kararlarını ayrıca kaydeder. Çıktıların dinamik web nedeniyle birebir aynı kalacağı iddia edilmez; yöntem ve sorgular tekrarlanabilir.

## Premium, engeller ve dış metin talimatları

K170 FT, K171 Bloomberg, K172 WSJ, K173 Economist, K174 Foreign Affairs, K175 Foreign Policy için yalnız açık ana sayfa/başlık/bülten işaretleri ve varsa açık RSS metadata’sı kontrol edildi. Makale bağlantısı açılmadı; makale metni toplanıp repoya konmadı. Hesaba/bülten kutusuna giriş yapılmadığından e-posta teslimi ve abonelik hakkı doğrulanmış sayılmaz. Beş premium kaynak erişim hatasıyla `Doğrulanamadı`; K174’te açık ana sayfa başlık erişimi `Canlı`, aylık başlık arşivi hacmi ölçülemedi. Diğer ücretli kaynaklarda da başlık erişimi tam metin lisansı değildir.

Erişilen HTML’de görev değiştirmeye yönelik talimat kalıpları ve araştırma sırasında görülen metinler kontrol edildi; görevi değiştirmeye yönelik uygulanmış bir dış talimat veya kaydedilmiş prompt injection bulgusu yok. Bu beyan yalnız bu taramada erişilen metinler içindir; bütün sitenin güvenlik denetimi değildir. Böyle bir metin sonraki kontrolde görülürse uygulanmamalı ve PR’ye URL/gözlem notu eklenmelidir.

## Son doğrulama ve sınırlar

CSV UTF-8 ve standart CSV quoting ile yeniden okundu; ilk 15 sütun, 269 benzersiz ID, 12 ekleme/2 birleşme, 202/202 RSS sonucu, 117 A iç gündem alanı, durum enumları, ölçülemeyen gerekçeleri ve çekirdek üyeliği denetlendi. 109 TT + K166 rapor kapsamı, ülke notlarının 10 satır sınırı, yerel dil açıkları, bilinen yanlış RSS kapsamları ve premium gövde dışlaması ayrıca incelendi. [Sayısal özet](kanitlar/ozet.json) ve [doğrulama sonuçları](kanitlar/kabul_kontrolu.json) makinece okunabilir.

Örneklem kontrolleri istatistiksel hata payı tahmini değildir: adı değişen/yerel dil edisyonu düzeltilen bütün URL’ler yeniden denendi; 7 şüpheli ana sayfa bağımsız web kanalında kontrol edildi; K004’ün altı dönem makalesinin tümü okundu. 34 doğrulanamayan kaynak, 75 doğrulanamayan besleme ve ana hacimdeki 268 eksik bu PR’nin açık sınırlarıdır. Bu satırlar otomatik yayın veya tamamlanmış ölçüm gibi kullanılmamalıdır.

### Girdi bütünlüğü

| Girdi | SHA-256 (UTF-8, LF normalleştirilmiş yerel kopya) |
| --- | --- |
| kaynak_havuzu_v2.csv | 992d9781fb34d6d74b01dcb91fc06ef7cbaae772e5906320ae966996aecfc9f7 |
| turkiye_terimleri.csv | 1a6b238bf7ce66e4d76a4313d63322776ec5cc60482a4ecb31cec8ccf1c566d4 |

Başlangıç Git commit: `ebdccc59af1013f86ba7420dc4ce9b6a9bbab911`. Hash kontrolünde CRLF varsa önce LFye dönüştür; v2 girdisinin Git dosyası bu PR ile değişmez. Araştırma betikleri geçici çalışma ortamında çalıştı; tekrar için gereken protokol ve gerçek sorgular bu doküman/kanıt dosyalarındadır. Repoya uygulama veya toplama kodu eklenmedi.
