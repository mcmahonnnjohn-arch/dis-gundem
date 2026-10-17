# Yapısal kararlar

Bu PR yalnız veri ve dokümantasyon üretir. v2 dosyası ve uygulama kodu değişmez. `data/kaynak_envanteri_v3.csv` ilk 15 sütunu aynı ad ve sırayla korur; doğrulama, hacim, dil, kapsam ve kanıt bilgileri sona eklenir. Bu ekler CSV araştırma alanlarıdır; uygulama/veritabanı şeması veya Supabase işlemi değildir.

1. **259 başlangıç satırından 269 envanter kaydı:** 12 yeni gerçek kaynak eklendi, 2 mükerrer birleştirildi. Erişim hatası veya ölçülemeyen aylık hacim bir kaynağı otomatik silme gerekçesi yapılmadı. Yeni kimlikler K260–K271; K187 ve K207 tekrar kullanılmaz.
2. **Tek kurum, tek aynı akış:** K207 Gulf Research Center → K060; K187 GMF Ankara → K128. K187’nin adındaki Carnegie gerçek bir ikinci kurum kaydı değildi. Carnegie ülke merkezleri, Rudaw haber/araştırma ürünleri ve SETA/SETA DC ayrı yayın akışları olarak korunur; aynı kurumsal aileden iki ürün bağımsız teyit çifti sayılmaz.
3. **P kodu yalnız altı premium yayına ayrıldı:** K170–K175. Reuters K168, AP K169 ve International Crisis Group K176 R olur. K246 SETA DC, Türk perspektifi için T olur; Washington adresi tek başına bağımsız ABD perspektifi sayılmaz. A/B/R/T/P tanımları korunur, hatalı atamalar düzeltilir.
4. **KKTC ve Lübnan iç gündemi A:** K038 Kıbrıs Postası T→A; K017 Al-Modon ve K018 L’Orient Today R→A. K260 Yenidüzen ve K261 NNA A ekleridir. Bu, Türkiye iç gündemini kapsama almaz. Libya’daki tek ülke yayınları K045/K046 R→B olur; Libya’nın genel iç gündemi yeni bir A alanı yapılmaz.
5. **Ülke/bölge açıklığı:** Katar, BAE ve Lübnan belirli yayın/kurumlarda soyut Körfez/Levant yerine görünür. K098 Romanya B; K145 yalnız Japonya; K136 Asya-Pasifik bölgesel; K137 MERICS Almanya/Avrupa; K219 Gürcistan; K230 Hollanda; K231 Belçika; K258 Somali. İngiltere adı Birleşik Krallık olarak normalleşir. Kafkasya/Karadeniz ortak yayınlarında `(bölgesel)` açık yazılır. Kalan MENA/Levant/Körfez etiketleri gerçekten ortak havuzdur; ülke diye sayılmaz.
6. **Yerel dil, ürün kimliğine göre:** K022 İbranice Ynet, K027 Yunanca To Vima, K045 Arapça Libya Observer, K047 Farsça IRNA, K061 Arapça Al Jazeera, K132 Çince Xinhua adreslerine geçer. Haaretz.com, eKathimerini, Ahram Online, L’Orient Today, Caixin Global gibi seçili İngilizce ürünler bütün yerel dil ürününü temsil ediyormuş gibi etiketlenmez. K004’te sayım birimi İngilizce edisyondur; Arapça ayrı kalır.
7. **Karışık adlar ayrıştırıldı:** K038 Kıbrıs Postası/Yenidüzen, K052 Etemad/Shargh, K063 Al-Araby/New Arab, K098 Romania Insider/Novinite, K105 EEAS/Komisyon, K169 AP/AFP, K199 Kathimerini/LSE ve K223 Re:Russia/Riddle adları seçili gerçek URL’nin ürününe indirgenir. Ayrı kaynak olarak eklenen Yenidüzen, EEAS ve AFP yeni ID alır. V2 adının içinde geçen fakat bağımsız satırı olmayan isimler ek bir çıkarılmış kayıt olarak sayılmaz.
8. **K166 yanlış kurum adı ve adresi düzeltildi:** Global Panorama (Global Akademi/UİK) akademik portalıdır; Koç/Dış Politika Enstitüsü karışımı kaldırılır. [Güncel künye](https://www.globalpanorama.org/biz-kimiz/). Yer değiştirme ve yeniden adlandırmaların tek tek kanıtları aşağıda ve `kanitlar/` içindedir.
9. **Çekirdek yeniden hesaplandı:** 125 benzersiz editoryal adayın 113’ü erişim kanıtıyla `Çekirdek`, 12’si koşullu listededir. Envanter genelinde doğrulanamayan 34 kayıt `Kontrol et`, erişilebilir diğer 122 kayıt `Yedek` olur. Çekirdek etiketi kurulu bir scraper, otomatik yayın veya metin telif lisansı anlamına gelmez.
10. **Belirsizlik görünür:** `Güv.` A/B/C eski editoryal başlangıç sınıfıdır; sahiplik bağı bir doğruluk puanı değildir. Bağımsız kanıtı olmayan eski çizgi/sahiplik notları `doğrulanamadı: v2 ön notu` ile işaretlendi. Düşünce kuruluşlarının finansmanında kurum özbeyanı, tarihsel belge ve güncel donor listesi ayrıldı; bilinmeyene kesin ilişki yazılmadı.
11. **Hacim ölçütü daraltılmadı:** Başlık eşleşmesi ve eksik RSS/API/GNews kayıt adedi aylık Türkiye hacmine dönüştürülmez. Yalnız tam kapsamı ve içeriği denetlenen K004 İngilizce pilotunda 1 Türkiye bağlantılı ve 3 önem≥3 iç gündem yazısı sayılır; diğer ana hücrelerde kaynak özelinde `ölçülemedi` nedeni bulunur. Gözlenen başlık adayları ve metadata adetleri ayrı sütunlardır.
12. **Besleme gerçekten kullanılabilir olmalı:** Boş, tarihi eski, tarihsiz, podcast/etkinlik veya üçüncü taraf sosyal/proxy akışları genel yayın RSS’si olarak onaylanmadı. `yok; scraping:` yalnız kontrol edilen adaylarda uygun RSS bulunmadığını ve açık liste yolunu ifade eder; sitenin tüm olası uç noktalarında RSS olmadığı iddiası değildir.

## Orta Asya ve Balkanlar

Yeni bir Orta Asya veya genel Balkan ülke grubu eklenmedi. Romanya zaten Karadeniz satırında bulunuyordu: K098 tek ülkeye normalleştirildi ve Romence AGERPRES K265 eklendi. Bu sınırlı Romanya iyileştirmesi genel Balkan kapsaması gibi sunulmaz; v2 adındaki Bulgar Novinite bağımsız kayıt olmadığı için Bulgaristan kapsanmış sayılmaz. Japonya/Kore birleşik etiketi de Kore kaynağı varmış izlenimi vermeyecek biçimde düzeltildi.

## Sayılar

| Ölçüt | Sonuç |
| --- | --- |
| v2 → v3 | 259 → 269 |
| Eklenen / birleştirilerek çıkarılan | 12 / 2 |
| Canlı / Taşındı / Ölü / Doğrulanamadı | 224 / 11 / 0 / 34 |
| Güncel, kullanılabilir yayıncı RSS/Atom | 114 |
| Scraping/liste alternatifi / beslemesi doğrulanamayan | 80 / 75 |
| Başlangıçtaki 202 boş RSS kaydının sonuç kapsamı | 202/202 |
| Ana Türkiye hacmi sayısal / ölçülemedi | 1 / 268 |
| A kapsamı iç gündem sayısal / ölçülemedi | 1 / 116 |
| Kapsam A / B / R / T / P | 117 / 100 / 25 / 21 / 6 |
| Think tank / ek akademik portal | 109 / 1 |
| Önerilen çekirdek / erişimi doğrulanmış / koşullu | 125 / 113 / 12 |

## Birleştirilerek çıkarılan kayıtlar

| Çıkarılan ID | Korunan ID | Tek satır gerekçe | Kanıt |
| --- | --- | --- | --- |
| K207 | K060 | Gulf Research Center aynı grc.net kurumu ve yayın akışı iki kez listelenmişti; tüm notlar K060 altında toplandı. | [GRC](https://www.grc.net/) |
| K187 | K128 | GMF Ankara zaten K128 kurumunun ofisi; Carnegie/GMF birleşik adı bağımsız ikinci kurum/akış kanıtı sağlamıyor. | [GMF Ankara](https://www.gmfus.org/our-offices/ankara) |

## Eklenen kayıtlar

| Yeni ID | Ülke | Kaynak | Tek satır gerekçe | Kanıt |
| --- | --- | --- | --- | --- |
| K260 | KKTC | Yenidüzen | K038'de yanlışlıkla aynı kaynakmış gibi yazılan gerçek ikinci gazeteyi ayrılaştırır; CTP kökenli, federasyon ve barış yanlısı perspektifi ekler. | [1](https://www.yeniduzen.com/kunye-4s.htm) · [2](https://www.yeniduzen.com/yeniduzen-gazetesi-tarihcesi-13s.htm) |
| K261 | Lübnan | National News Agency (NNA) | Lübnan'a Arapça resmi açıklama/ajans katmanı; haber iddialarının bağımsız teyidi sayılmaz. | [1](https://www.nna-leb.gov.lb/index.htm) · [2](https://nna-leb.gov.lb/ar/info/privacy-policy) · [3](https://mail.ministryinfo.gov.lb/518) |
| K262 | Libya | Al-Wasat | Arapça Libya haber katmanını ve farklı yerel perspektifi genişletir; son teknik kontrolde ana sayfa ve sitemap HTTP 200 ile doğrulandı. | [1](https://www.alwasat.ly/about-us-ar) · [2](https://www.alwasat.ly) |
| K263 | BAE | Emirates News Agency (WAM) | The National'ın İngilizce gündemini Arapça resmi ülke açıklamalarıyla tamamlar; Türkiye–BAE ilişkileri başlıkları için. JS içerik çıkarma sınırlılığı ayrıca kaydedilmeli. | [1](https://www.wam.ae/ar) · [2](https://www.wam.ae/ar/article/hszrhacj-الإمارات-وتركيا-علاقات-متنامية-نحو-شراكة-شاملة) |
| K264 | Azerbaycan | Abzas Media | Yerel dilde yolsuzluk ve kamusal hesap verebilirlik araştırması; Turan faaliyeti belirsizliği ve ağırlıklı resmi/ana akım havuzun eksik perspektifini tamamlar. Çalışanlarının tutukluluğu ve erişim kısıtları nedeniyle teknik erişim başarısı ayrıca kaydedilmeli. | [1](https://abzas.org/az/about) · [2](https://rsf.org/en/azerbaijan-foreign-media-muzzled-llham-aliyevs-regime) |
| K265 | Romanya | AGERPRES | K098’in yalnız İngilizce Romanya yayını olduğu düzeltildikten sonra Romence ülke kaynağı açığını kapatır; Karadeniz ve Türkiye diplomasi başlıkları için birincil ajans akışı. | [1](https://agerpres.ro/national) · [2](https://www.agerpres.ro/english/corporate/contact) |
| K266 | Japonya | Asahi Shimbun | Nikkei Asia İngilizce ekonomi seçkisinin yanına Japonca genel haber perspektifi ekler; Türkiye konu ve seri sayfaları var, ücretli gövdeler alınmadan başlık/erişim doğrulaması yapılmalı. | [1](https://globe.asahi.com/series/11024396) · [2](https://globe.asahi.com/tag/11029931) · [3](https://www.asahi.com/international/) |
| K267 | Cezayir | Algérie Presse Service (APS) | TSA eski Arapça adresi Fransızcaya yönlendiği için Arapça resmî ulusal ajans adayı eklendi; son iki teknik kontrolde HTTP 500 alındı, yerel dil açığı kapanmış sayılmadı. | [1](https://www.aps.dz/) · [2](https://www.aps.dz/a-propos-de-l-aps) · [3](https://www.aps.dz/fr/tags/algerie-turquie) |
| K268 | Pakistan | Dawn News Urdu | Dawn gazetesinin İngilizce ürününe Urduca kardeş yayın ekler; ana sayfa ve sitemap HTTP 200 ile doğrulandı. Aynı mülkiyet grubu bağımsız ikinci perspektif sayılmaz; Urduca terim kapsamı henüz yok. | [1](https://www.dawn.com/) · [2](https://live.dawnnews.tv/) · [3](https://live.dawnnews.tv/world/middle-east) |
| K269 | AB | European External Action Service (EEAS) | K105te Komisyonla karışan dış politika/diplomasi açıklamaları ayrı bir kaynak kimliği gerektiriyor. Resmî Türkçe basın odası da mevcut. | [1](https://www.eeas.europa.eu/eeas/bas%C4%B1n-odas%C4%B1_tr) · [2](https://www.eeas.europa.eu/) |
| K270 | Küresel | Agence France-Presse (AFP) | K169daki AP / AFP birleşik adında temsil edilmeyen ayrı ajans. Fransızca/İngilizce başlık ve basın ürünleri; lisanslı ajans metni izinsiz toplanmamalı. | [1](https://www.afp.com/en/about-us) · [2](https://factcheck.afp.com/about-afp) |
| K271 | İtalya | ANSA | İtalya mevcut seti yalnız düşünce kuruluşlarından oluşuyor; İtalyanca olay haberi için ulusal ajans eklenerek IAI/ISPI analizi tamamlanır. | [1](https://www.ansa.it/corporate/it/) · [2](https://www.ansa.it/ansa_verified/info/chi_siamo.html) |

## Mevcut kayıtlarda araştırmaya dayalı düzeltmeler

Toplu RSS, doğrulama, hacim, eski doğrulanmamış bağlam ve `Durum` güncellemeleri yukarıdaki kararlar kapsamındadır. Aşağıdaki tablo kurum/edisyon/sahiplik/kapsam düzeltmelerini tek tek izler.

| ID | Değişen alanlar | Gerekçe | Kanıt |
| --- | --- | --- | --- |
| K002 | Eğilim / Bağlam | Belirsiz 'Katar destekli' ifadesi yerine doğrulanmış şirket bağı ve güncel ofis bilgisi. | [1](https://www.fadaatmedia.com/en/our-companies) · [2](https://www.fadaatmedia.com/about-us) |
| K004 | Eğilim / Bağlam | Amman güncel merkez gibi yazılmış; 10 Ağustos 2026 güncellenmiş resmi hakkında sayfası Almanya kaydını belirtiyor. | [1](https://syriadirect.org/about-us/) |
| K006 | URL, Dil, Eğilim / Bağlam | Eski jusoor.co İngilizce hakkında URL'si jusoor.sy/ar adresine yönleniyor; mevcut hedef Arapça, tarihsel İngilizce/Türkçe sürüm bugün aynı URL'de doğrulanmadı. | [1](https://jusoor.co/en/about-us) · [2](https://jusoor.sy/ar) |
| K007 | URL, Kaynak, Eğilim / Bağlam | Yeni resmi site, kurum adı ve kayıt/iletişim bilgisi doğrulandı; 14 Ekim 2026 tarihli güncel yayın var. | [1](https://omrandirasat.org/en/about/) · [2](https://omrandirasat.org/en/contact/) · [3](https://omrandirasat.org/en/) |
| K017 | Ülke, Kapsam, İçerik rolü, Tür, Güv., Eğilim / Bağlam | Lübnan'ın soyut Levant etiketi altında kaybolması giderilir; sahiplik bağlantısı bulunan yayına koşulsuz bağımsız etiketi verilmez. | [1](https://www.almodon.com) · [2](https://lebanon.mom-gmr.org/en/owners/companies/detail/company/company/show/rainbow-media-co-sal-3/) |
| K018 | Ülke, Kapsam, İçerik rolü, Dil, Eğilim / Bağlam | L'Orient Today İngilizcedir; Fransızca L'Orient-Le Jour ayrı ürün ve URL'dir. Lübnan ülke kapsamı görünür kılınır. | [1](https://www.lorientlejour.com/qui-sommes-nous) · [2](https://today.lorientlejour.com) |
| K020 | Dil | Mevcut haaretz.com URL'si İngilizce edisyondur; İbranice marka ailesi alanın kendisinde doğrulanmış gibi gösterilmez. | [1](https://www.haaretz.com) · [2](https://www.haaretz.co.il) |
| K022 | URL, Dil, Eğilim / Bağlam | İbranice yayın yerine İngilizce ynetnews URL'si verilmişti; 'en yüksek tiraj' ölçülmemiş üstünlük iddiası kaldırılır. | [1](https://www.ynet.co.il/home/0,7340,L-8,00.html) |
| K026 | Dil, Eğilim / Bağlam | eKathimerini URL'sinin dili İngilizce; Yunanca kardeş yayın kathimerini.gr'dedir. | [1](https://www.ekathimerini.com) · [2](https://www.kathimerini.gr/aboutus/) |
| K027 | URL, Dil, Eğilim / Bağlam | Yerel Yunanca edisyon hedeflenir; tovima.com İngilizce edisyondur. | [1](https://www.tovima.gr) · [2](https://www.tovima.com/about/) · [3](https://www.tovima.com/finance/evangelos-marinakis-each-new-summit-we-conquer-allows-us-to-see-further-still/) |
| K037 | Kaynak, Eğilim / Bağlam | Dil servisi gerçek ayrı ürün olduğu için otomatik silinmez; aynı mülkiyetin bağımsız perspektif sayılması önlenir. | [1](https://phileleftherosgroup.com/our-brands/websites/in-cyprus/) |
| K038 | Kaynak, Kapsam, İçerik rolü, Eğilim / Bağlam | Birbirinden ayrı Kıbrıs Postası ve Yenidüzen tek URL'de birleştirilmişti; kayıt URL'deki yayına daraltılır. A önerisi yerel siyasi gündemi Ankara resmi pozisyonu saymamak içindir. | [1](https://www.kibrispostasi.com) · [2](https://www.yeniduzen.com/kunye-4s.htm) |
| K039 | Eğilim / Bağlam | 'Tek bağımsız' mutlak ve ölçülmemiş iddiası kaldırılır; kurum kendisini bağımsız seslerden biri olarak tanımlıyor. | [1](https://www.madamasr.com/en/about-us/) |
| K040 | Dil | Ahram Online'ın verilen english.ahram.org.eg adresi İngilizcedir; Arapça ana kuruluş ayrı URL'dedir. | [1](https://english.ahram.org.eg) · [2](https://gate.ahram.org.eg) |
| K045 | URL, Dil, Kapsam, İçerik rolü | Mevcut İngilizce vitrin yerel Arapça sürümle değiştirilir; Libya v2'de A dışı tutulduğu için tek ülke kaynağına R yerine B önerilir. | [1](https://ar.libyaobserver.ly/1586) · [2](https://ar.libyaobserver.ly/politics?page=3&qt-libya_weather=1&qt-sidebar_tabs=2) |
| K046 | Kapsam, İçerik rolü | Tek ülke yayınıdır; Libya'yı A'ya genişletmeden bölgesel rolün yanlış kullanımını giderir. | [1](https://libyaherald.com) |
| K047 | URL, Dil, Eğilim / Bağlam | Yerel Farsça gündemi İngilizce vitrin üzerinden temsil etmekten kaçınılır; eski Türkçe dil iddiası ayrıca doğrulanmadı. | [1](https://www.irna.ir) · [2](https://en.irna.ir) |
| K050 | Eğilim / Bağlam | Suudi bağlantısı ile devlet finansmanı eşitlenmez; mülkiyet açıklaması tarih ve atıfla sınırlandırılır. | [1](https://www.iranintl.com/en/privacyen) · [2](https://www.iranintl.com/en/202210266792) |
| K052 | Kaynak, Eğilim / Bağlam | Etemad ve Shargh farklı gazeteler; URL yalnız Shargh'a aittir. Etemad yeni kaynak sayılacaksa ayrıca ID ve doğrulama gerekir. | [1](https://www.sharghdaily.com) |
| K055 | Eğilim / Bağlam | Zamansız 'Türkiye'ye mesafeli' genellemesi yerine doğrulanmış sahiplik bağı yazılır. | [1](https://english.aawsat.com/about-us) · [2](https://www.srmg.com/en/our-brands/news) |
| K056 | Eğilim / Bağlam | Ortak şirket mülkiyeti çekirdek sette perspektif çeşitliliğini olduğundan fazla göstermemeli. | [1](https://www.srmg.com/en/our-brands/news) |
| K061 | Ülke, Kaynak, URL, Dil, Eğilim / Bağlam | Bölgesel R rolü korunur; gerçek ülke ve yerel Arapça URL görünür yapılır. İngilizce kardeş edisyon aljazeera.com'dadır. | [1](https://www.aljazeera.net) |
| K062 | Ülke, Eğilim / Bağlam | Bölgesel rol korunurken ülke merkezi somutlaştırılır; sahiplik resmi About sayfasıyla yazılır. | [1](https://www.thenationalnews.com/about-us/) |
| K063 | Kaynak, Dil, Eğilim / Bağlam | İki dil ürünü tek URL'de varmış gibi gösterilmez; verilen alaraby.co.uk Arapça kaydı korunur. | [1](https://www.fadaatmedia.com/en/our-companies) · [2](https://www.fadaatmedia.com/about-us) |
| K189 | URL, Eğilim / Bağlam | Bağımsız gerçek araştırma merkezi mevcuttur; /english/analysis yanlış URL'dir. K009 ile silerek birleştirilmemeli, kurumsal bağı belirtilmeli. | [1](https://rudawrc.net/en/about-us) · [2](https://rudawrc.net/en/region/turkey) |
| K190 | Kaynak, URL, Dil, Eğilim / Bağlam | harmoon.org doğrudan damascusinstitute.org'a yönleniyor; güncel Arapça kurum adı değişmiş. Eski İngilizce sayfa güncel mali kontrol kanıtı değildir. | [1](https://www.harmoon.org) · [2](https://damascusinstitute.org/من-نحن/) · [3](https://damascusinstitute.org/en/about-us/) |
| K191 | Eğilim / Bağlam | Eski seri güncel haftalık yayına ilişkin kesin taahhüt gibi tutulmaz; kuruluşun şirket niteliği açık yazılır. | [1](https://www.coar-global.org/about-us) · [2](https://coar-global.org/publications/recent-tensions-highlight-the-enduring-syrian-refugees-crisis) |
| K192 | Kaynak, URL, Ülke, Eğilim / Bağlam | Eski carnegie-mec alanının kurumsal merkez sayfası yenilenir ve gerçek ülke görünür olur. | [1](https://carnegieendowment.org/middle-east) · [2](https://carnegieendowment.org/middle-east/about-the-malcolm-h-kerr-carnegie-middle-east-center?center=middle-east) |
| K196 | Kaynak, URL, Eğilim / Bağlam | Güncel kurum adı ve alan adı; 'sağ' kısaltması somut kurumsal misyonla desteklenir. | [1](https://jcfa.org/2013/04/page/2/) · [2](https://jcfa.org/israel-and-turkey-compete-for-regional-hegemony/) |
| K199 | Kaynak, Eğilim / Bağlam | Kathimerini analiz ile LSE merkezi tek kayıtta karıştırılmış; URL'deki gerçek merkeze daraltılır. | [1](https://www.lse.ac.uk/Hellenic-Observatory/About-us/centre) |
| K202 | URL, Dil, Eğilim / Bağlam | Eski İngilizce alt alan yerine erişilen resmi Arapça merkez seçilir; geçici teknik arızadan dönüş duyurusu mevcut. | [1](https://eipss-eg.org/about-us/) · [2](https://eipss-eg.org/en/tiehome-2/) |
| K208 | Ülke | Bölgesel rol R korunur; Doha merkezi gerçek ülke etiketiyle görünür olur. | [1](https://studies.aljazeera.net/en/dossiers) |
| K210 | Ülke, Güv., Eğilim / Bağlam, URL | Kanıtlanmamış doğrudan devlet/propaganda C sınıfı yerine bağlam ve finansman belirsizliği belirtilir; nihai sınıf kararı editöre açık. | [1](https://trendsgroup.org/external-office/turkiye/) · [2](https://trendsresearch.org/news/an-analytical-study-by-trends-on-artificial-intelligence-and-its-enormous-challenges-and-opportunities/) |
| K211 | Ülke | Abu Dabi merkezli kuruluşun bölgesel rolü korunarak ülke etiketi belirginleştirilir. | [1](https://epc.ae/en) |
| K212 | Kaynak, URL, Dil, Eğilim / Bağlam | Güncel marka ve yeni alan adı resmi About/Support sayfalarıyla teyit edildi. | [1](https://agsi.org/about/) · [2](https://agsi.org/support/) |
| K069 | Durum, Eğilim / Bağlam | V2 çekirdek etiketi otomatik sürdürülmemeli: faaliyet durdurma haberi ile arşiv sitesinin erişilebilirliği ayrı şeylerdir. Kesin Ölü kararı güncel teknik/kurumsal kanıt gerektirir. | [1](https://eurasianet.org/financial-pressures-force-azerbaijans-last-bastion-of-independent-media-to-suspend-operations) · [2](https://rsf.org/en/azerbaijan-foreign-media-muzzled-llham-aliyevs-regime) |
| K073 | Eğilim / Bağlam | Boş bağlam yerine bağımsız medya sahiplik araştırması ile doğrulanan yayıncı bilgisi eklendi. | [1](https://armenia.mom-gmr.org/en/media/online/outlet/civilnet-114983/) |
| K078 | Eğilim / Bağlam | Bağımsız yayıncı ifadesi kamu finansmanını gizlememeli; finansman editoryal doğruluk puanı değildir. | [1](https://pressroom.rferl.org/about-rfe-rl/) |
| K079 | Dil, Yerel dil URL | V2 yalnız İngilizce/Rusça yazmış; yayın ayrıca Gürcüce, Ermenice, Azerbaycanca çalışıyor. Edisyon yolları toplama öncesinde ayrıca doğrulanmalı. | [1](https://directory.globalprojectoasis.org/jamnews/) |
| K083 | Yerel dil URL | tass.com İngilizce giriş; Rusça ana yayın ayrı işaretlenmeli. Bu URL teknik test gerektiren bilinen yerel edisyondur. | [1](https://tass.com) · [2](https://tass.ru) |
| K086 | Yerel dil URL, Eğilim / Bağlam | Rusça tam akış ile İngilizce seçki özdeş değildir; yerel dil ana sayfası önceliklendirilir. | [1](https://amp.meduza.io/en/pages/about) |
| K092 | Eğilim / Bağlam | Sahiplik ve editoryal güvence kaynaklandırıldı; 2021 işlem tarihi güncel hisse dökümü sanılmamalı. | [1](https://www.pravda.com.ua/news/2021/05/26/7294947/) · [2](https://dragon-capital.com/media/press-releases/olena-prytula-and-tomas-fiala-announce-ownership-change-at-ukrayinska-pravda/) |
| K098 | Kaynak, Ülke, Kapsam, İçerik rolü, Eğilim / Bağlam | Tek URL iki bağımsız yayını temsil edemez; hayali Bulgaristan kapsamı çıkarıldı. Romanya Karadeniz bölgesinde B olarak tutulur. | [1](https://www.romania-insider.com/about-us) · [2](https://cdn.romania-insider.com/terms-and-conditions) |
| K131 | Dil, Eğilim / Bağlam | Verilen URL İngilizce Global Times ürünüdür; aynı URL üzerinden Çince kapsama iddiası kaldırıldı. | [1](https://www.globaltimes.cn/about-us/index.html) |
| K132 | URL, Yerel dil URL, Dil | Xinhua kaydı yalnız İngilizce vitrine bağlanıyordu; canlı Çince ana sayfa temel URL yapıldı. İngilizce edisyon english.news.cn olarak kaynak notunda korunabilir. | [1](https://www.news.cn/) · [2](https://english.news.cn/) |
| K133 | Eğilim / Bağlam | Görece bağımsız gibi derecesi belirsiz hüküm yerine somut sahiplik ve beyan ayrımı. | [1](https://www.scmp.com/policies-and-standards) · [2](https://corp.scmp.com/our-company) |
| K136 | Ülke, Eğilim / Bağlam | Çin altında yerel perspektif olarak sayılması hatalıydı. B Türkiye filtresi korunur; bölgesel ülke etiketi kullanılır. | [1](https://thediplomat.com/?page=aboutUs) |
| K137 | Ülke, Bölge, Dil, Eğilim / Bağlam | MERICS Çin içinde kurulu yerel think tank değildir; merkez ülkesi düzeltildi, Çin uzmanlığı bağlamda kaldı. | [1](https://merics.org/en/about) · [2](https://merics.org/en/transparency) |
| K140 | Dil, Yerel dil URL, Eğilim / Bağlam | Aynı markanın Hintçe akışı doğrulandı; yeni ID ile mükerrer üretmeden İngilizce vitrin açığı kapatılabilir. | [1](https://hindi.theprint.in/) · [2](https://theprint.in/terms-of-use/) · [3](https://india.mom-gmr.org/en/media/detail/outlet/the-print/) |
| K143 | Eğilim / Bağlam | Türkiye’ye sert çerçeve genellemesi sistematik örneklemle ölçülmemiştir; yerine kanıtlı kurumsal bağlam. | [1](https://www.linkedin.com/company/wionews/) |
| K144 | Eğilim / Bağlam | Resmi Dawn ana sayfası Dawn News Urduya bağlantı veriyor; ayrı yayın ürünü olduğu için aynı ID altında dil/hacim birleştirmek yerine yeni kayıt önerildi. | [1](https://www.dawn.com/) · [2](https://live.dawnnews.tv/) |
| K145 | Ülke, Eğilim / Bağlam | Nikkei Asia Japonca veya Korece yerel yayın değildir; Japonya/Kore birleşik etiketi Japonya olarak düzeltildi. Kore yeni ülke kapsamı yapılmadı. | [1](https://asia.nikkei.com/) |
| K146 | Dil, Eğilim / Bağlam | Fransızca Jeune Afrique ayrı ürün ve zaten K148; The Africa Report satırında aynı grubu iki bağımsız perspektif gibi sayma. | [1](https://in.linkedin.com/company/the-africa-report) |
| K152 | Eğilim / Bağlam | Coğrafi perspektif ve yayıncı ilişkisi kurumsal about sayfasıyla açıklandı; siyasi kamp aidiyeti çıkarılmadı. | [1](https://www.garoweonline.com/index.php/en/about-us) |
| K153 | Dil, Yerel dil URL, Eğilim / Bağlam | Kurumsal üç dil doğrulandı; Amharca URL resmi kanalca veriliyor ancak bu oturumda doğrudan erişimi doğrulanamadı. | [1](https://addisstandard.com/about-us/) · [2](https://t.me/s/addisstandardamh) · [3](https://addisstandard.com/Amharic/) |
| K154 | Yerel dil URL | Sudan Tribune Arapça sitesi .net alanında; .com İngilizce giriş tek başına yerel dil kanıtı değildir. | [1](https://sudantribune.net/) · [2](https://sudantribune.com/) |
| K155 | Dil, Yerel dil URL, Eğilim / Bağlam | Aynı markanın canlı Hausa edisyonu saptandı; yeni kaynak ID gerekmez. | [1](https://hausa.premiumtimesng.com/) · [2](https://www.premiumtimesng.com/about) |
| K156 | Eğilim / Bağlam | 2017 Arapça açılış duyurusu bugünkü aktif Arapça servis kanıtı değil. APS eklemesi yerel dil boşluğunu kapatır. | [1](https://www.tsa-algerie.com/contact/) · [2](https://www.tsa-algerie.com/bienvenue-a-tsa-en-arabe/) · [3](https://www.tsa-algerie.com/ar/) |
| K157 | Eğilim / Bağlam | Fransızca yerel çalışma dilidir fakat yerli dil ihtiyacını tek başına kapatmaz; görsel/ses içeriği metin RSS sanılmadı. | [1](https://www.seneweb.com/) |
| K213 | Eğilim / Bağlam | Devlete yakın ifadesi yerine kuruluşun belgeli hukuki ilişkisi. | [1](https://think-tanks.az/eng/center-for-the-analysis-of-international-relations) · [2](https://aircenter.az/en/mission) |
| K214 | Eğilim / Bağlam | Bağımsızlık beyanı ile ulusal perspektif birbirini dışlamaz; kurumsal misyon korundu. | [1](https://top-center.org/en/page/1/about-us) |
| K216 | Eğilim / Bağlam | Kurucu diaspora vakfı bağı görünür kılındı. | [1](https://apri.institute/who-we-are/) |
| K218 | Eğilim / Bağlam | Devlete yakın belirsizliği yerine doğrudan kamu kurumu ilişkisi kaynaklandırıldı. | [1](https://www.orbeli.am/en/about_us) · [2](https://iprc.am/orbeli-center/?lang=en) |
| K219 | Ülke, Eğilim / Bağlam | Kafkasya ülke değildir; merkezi Gürcistan olduğu açıklandı, R bölgesel rolü korunur. | [1](https://gip.ge/about-us/about/) |
| K220 | Eğilim / Bağlam | Dışişleri yakın ifadesi kurucu listesi ve Türkiye programıyla somutlaştırıldı. | [1](https://russiancouncil.ru/en/about/founders/) · [2](https://russiancouncil.ru/en/projects/bilaterial/russia-turkey/) |
| K221 | Eğilim / Bağlam | Kremlin yakın kısaltması yerine somut kurucu ilişkileri; güncel bütçe kaynağı ayrıca doğrulanmadı. | [1](https://valdaiclub.com/about/valdai) · [2](https://valdaiclub.com/about/founders) |
| K222 | Eğilim / Bağlam | Akademi ifadesi kamu bütçeli kurum bilgisiyle tamamlandı. | [1](https://www.imemo.ru/index.php?page_id=2435) |
| K223 | Kaynak, Eğilim / Bağlam | Re:Russia ve Riddle aynı kuruluş değil; ridl.io yalnız Riddle kaydı olarak düzeltildi. Re:Russia yeni kaynak gibi icat edilmedi. | [1](https://ridl.io/about-riddle-2/) · [2](https://ridl.io/ru/podderzhat/) |
| K249 | Eğilim / Bağlam | Bağımsız sıfatı veya otomatik propaganda hükmü yerine doğrulanabilir kurucu bağlamı ve finansman belirsizliği. | [1](https://uom.ac.mu/confucius/index.php/en/component/content/article/welcoming-of-a-delegation-from-charhar-institute-shangyi-county-hebei-province-18th-april-2017?Itemid=220&catid=47) |
| K250 | Eğilim / Bağlam | Bağlılık doğrudan resmi kurum sayfasından teyit edildi. | [1](https://www.ciis.org.cn/english/AboutUs/) |
| K251 | Eğilim / Bağlam | Boş bağlam kurumun kendi tanımıyla dolduruldu; bütçe payları doğrulanamadı. | [1](https://www.siis.org.cn/updates/cms/old/UploadFiles/file/20200214/SIIS%20Report%20.pdf) |
| K252 | Eğilim / Bağlam | Finansman ile idari bağlılık birbirinden ayrıldı. | [1](https://idsa.in/about) |
| K253 | URL, Eğilim / Bağlam | Güncel Carnegie India kurumsal merkez adresi HTTP 200 ve kurum kimliğiyle doğrulandı; eski alan adı/merkez geçişi Taşındı olarak işlendi. | [1](https://carnegieendowment.org/india?center=india) |
| K255 | Eğilim / Bağlam | Yalnız İslamabad coğrafyası yerine belgeli bakanlık ilişkisi. | [1](https://issi.org.pk/wp-content/uploads/2022/Annual_Report_2023/Annual_Report_2022.pdf) |
| K258 | Ülke, Eğilim / Bağlam | Somali think tank’i Afrika bölgesel toplamasında kaybolmamalı; ülke Somali olarak netleştirildi. | [1](https://heritageinstitute.org/about-heritage-institute/) |
| K105 | Kaynak, Eğilim / Bağlam | Tek URL Komisyon Press Cornerı temsil ediyor; birleşik EEAS / Komisyon adı düzeltildi, EEAS ayrı yeni kayıt olarak önerildi. | [1](https://ec.europa.eu/commission/presscorner) · [2](https://www.eeas.europa.eu/eeas/bas%C4%B1n-odas%C4%B1_tr) |
| K107 | URL, Eğilim / Bağlam | Carnegie Europe güncel ana kurum alanındaki Avrupa programına taşınmış; K242 üst kurum kaydıyla ortak aile/URL tekrarı makale düzeyinde ele alınmalı. | [1](https://carnegieendowment.org/europe) · [2](https://carnegieendowment.org/programs/europe) |
| K109 | Kaynak, Dil, Eğilim / Bağlam | DWnin yalnız TR/EN etiketi Almanca yerel yayını görünmez kılıyordu; dil alanı ve kamu yayıncılığı bağlamı netleştirildi. | [1](https://static.dw.com/downloads/68393580/dw-factsheeten.pdf) · [2](https://www.dw.com/downloads/36383966/dwgesetzen.pdf) |
| K123 | URL | CRS ürünleri güncel Congress.gov koleksiyon adresine yönleniyor; kongre araştırması resmî belge olarak korunur. | [1](https://www.congress.gov/crs-products) |
| K124 | URL, Eğilim / Bağlam | Türkiye programının güncel resmî yolu doğrulandı; eski atlantic-council-in-turkey yolu yerine kullanılır. | [1](https://www.atlanticcouncil.org/programs/atlantic-council-turkey-program/) · [2](https://www.atlanticcouncil.org/in-depth-research-reports/report/2025-honor-roll-of-contributors/) |
| K125 | Eğilim / Bağlam | V2deki İsrail yakınlığı etiketi bu taramada somut kontrol/finansman kanıtıyla doğrulanamadı; kurumun açık misyonu ve bağış politikasıyla değiştirildi. | [1](https://www.washingtoninstitute.org/policy-analysis/turkey) · [2](https://www.washingtoninstitute.org/support/donor-eligibility) |
| K128 | Kaynak, URL, Eğilim / Bağlam | K187 GMF Ankara mükerreri burada birleştirilir; genel ana sayfa yerine kalıcı Türkiye/Ankara ofisi akışı seçildi. | [1](https://www.gmfus.org/our-offices/ankara) · [2](https://www.gmfus.org/about) |
| K129 | Eğilim / Bağlam | V2deki genelleyici Türkiye eleştirel etiketi, Türkiye arşivindeki farklı savunma analizlerini kapsamadığından daha somut bağlamla değiştirildi. | [1](https://www.hudson.org/turkey) · [2](https://www.hudson.org/institutional-integrity-transparency) |
| K161 | Kaynak, Dil, Eğilim / Bağlam | URL yalnız TRT Worldü gösteriyor; TRT Haber ayrı ürün. Ayrı TRT Haber eklenmeden birleşik ad ve tr dili çıkarıldı. | [1](https://www.trtworld.com/) |
| K166 | Kaynak, URL, Dil, Eğilim / Bağlam | Eski uikpanorama ana sayfası servis varsayılanı; yeni Global Panorama künyesi ve yayınları doğrulandı. Koç Üniversitesi / Türkiye Dış Politika Enstitüsü atfı yanlış birleşimdi. | [1](https://www.globalpanorama.org/biz-kimiz/) · [2](https://www.globalpanorama.org/) |
| K168 | Kapsam | Reuters uluslararası ajanstır; P yalnız kullanıcının belirttiği altı premium yayın için tutulur. | [1](https://www.reuters.com/) |
| K169 | Kapsam, Kaynak, Dil, Eğilim / Bağlam | AP / AFP birleşik adı tek apnews.com URLsiyle iki ajansı varmış gibi gösteriyordu; AP kaydı korunur, AFP yeni ID ile eklenir. | [1](https://apnews.com/) · [2](https://www.afp.com/en/about-us) |
| K176 | Kapsam | International Crisis Group küresel çatışma araştırma kuruluşudur; altı premium yayın sınıfından çıkarılarak R yapılır. | [1](https://www.crisisgroup.org/sites/default/files/2023-02/267-isis-in-turkey.pdf) |
| K186 | Kaynak | Resmî künyeye göre Araştırmacıları yerine Araştırmacılar adı düzeltildi. | [1](https://ordaf.org/hakkimizda/) |
| K228 | Eğilim / Bağlam | EUISSnin özel bağımsız think tank değil özerk AB ajansı olduğu finansman/yakınlık bağlamında açıklaştırıldı. | [1](https://www.iss.europa.eu/about-us) |
| K230 | Ülke, Eğilim / Bağlam | Ulusal araştırma enstitüsü AB kurumlarıyla aynı ülke hücresinde tutulmamalı; Avrupa bölgesi korunarak Hollanda ülkesine taşındı. | [1](https://www.careers.clingendael.org/over-ons/why-work-at-clingendael/) · [2](https://www.clingendael.org/sites/default/files/2024-10/Clingendael_rapport_Turkse_diasporabeleid_in_Nederland.pdf) |
| K231 | Ülke, Eğilim / Bağlam | Egmont ulusal merkezli kuruluş olarak Belçikaya ayrıldı; AB bölgesel kurumsal kaynaklarıyla karıştırılmamalı. | [1](https://egmontinstitute.be/about-the-institute/) |
| K235 | Eğilim / Bağlam | Parti yakınlığı resmî kurum açıklamasıyla somutlaştırıldı; finansman doğrulanmadan kamu payı yazılmadı. | [1](https://www.kas.de/de/web/tuerkei/ueber-uns) |
| K236 | Eğilim / Bağlam | Kurumun açık değerleri ile perspektif somutlaştırıldı; doğrulanmamış bağışçı veya parti kontrolü iddiası eklenmedi. | [1](https://www.fes.de/en/about-us/about-fes) · [2](https://turkey.fes.de/en/topics/democracy-and-human-rights.html) |
| K244 | Eğilim / Bağlam | Genelleyici lobi etiketi yerine resmî Türkiye programının somut politika çerçevesi yazıldı. | [1](https://www.fdd.org/projects/turkey-program/) |
| K245 | Güv., Eğilim / Bağlam | MEF devlet yayını değildir; C yerine görüş/savunuculuk kaynağı B sınıfı önerildi. Güven kategorisi ölçülmüş hata oranı değildir. | [1](https://www.meforum.org/the-architecture-of-turkeys-anti-americanism-organization-dossiers) · [2](https://www.meforum.org/topics/strategic-alliances) |
| K246 | Kapsam, Eğilim / Bağlam | ABDde faaliyet gösterse de Ankara perspektifini taşıyan SETA ofisi yabancı kaynak çeşitliliği sayılmamalı; ülke ABD korunup kapsam T yapıldı. | [1](https://setadc.org/seta-dc/) · [2](https://www.setav.org/hakkimizda/) |
| K115 | Ülke | İngiltere yerine devlet adı Birleşik Krallık kullanılarak ülke sınıflandırması normalleştirildi; Avrupa bölgesi ve mevcut kapsam korunur. | [1](https://www.theguardian.com) |
| K116 | Ülke | İngiltere yerine devlet adı Birleşik Krallık kullanılarak ülke sınıflandırması normalleştirildi; Avrupa bölgesi ve mevcut kapsam korunur. | [1](https://www.chathamhouse.org) |
| K117 | Ülke | İngiltere yerine devlet adı Birleşik Krallık kullanılarak ülke sınıflandırması normalleştirildi; Avrupa bölgesi ve mevcut kapsam korunur. | [1](https://www.bbc.com/turkce) |
| K238 | Ülke | İngiltere yerine devlet adı Birleşik Krallık kullanılarak ülke sınıflandırması normalleştirildi; Avrupa bölgesi ve mevcut kapsam korunur. | [1](https://rusi.org) |
| K239 | Ülke | İngiltere yerine devlet adı Birleşik Krallık kullanılarak ülke sınıflandırması normalleştirildi; Avrupa bölgesi ve mevcut kapsam korunur. | [1](https://www.iiss.org) |

## Boş RSS kayıtları ve erişim engelleri

Başlangıçta RSS işaretli olup adresi boş olan 202 kaydın tamamının sonucu [RSS 202 sonuç tablosunda](rss_202_sonuclari.md) bulunur. 86 kayıtta doğrudan güncel RSS, 63 kayıtta liste/scraping alternatifi, 51 kayıtta doğrulanamadı sonucu ve 2 kayıtta birleşme izi vardır (202 toplam). K187’nin korunan GMF beslemesine bağlanması da sayıldığında 87 başlangıç kaydı güncel bir yayıncı beslemesine bağlanır; diğerlerinde alternatif veya somut doğrulanamama nedeni vardır. Birleştirilen iki ID de iz kaybı olmadan korunan IDnin sonucuna bağlanır.

| Doğrulanamayan ID | Kaynak | Somut neden |
| --- | --- | --- |
| K008 | SOHR | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K023 | Israel Hayom | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K026 | eKathimerini | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K032 | Greek City Times | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K039 | Mada Masr | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K048 | Tasnim | HTTP 502 |
| K054 | Amwaj.media | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K057 | Al Arabiya | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K059 | Okaz | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K069 | Turan | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K088 | RBC | HTTP 401; kimlik doğrulama gerekli |
| K100 | Politico Europe | HTTP 402; ödeme/abonelik erişim yanıtı |
| K101 | Euractiv | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K109 | Deutsche Welle (DW) | başlıksız HTML; ikinci web kanalında ana sayfa ve dil yolu açılamadı |
| K118 | New York Times | HTTP 200 içinde Site Unavailable; yayın ana sayfası görülmedi; ikinci web kontrolü de başarısız |
| K120 | Politico | HTTP 402; ödeme/abonelik erişim yanıtı |
| K122 | Dışişleri Bakanlığı brifingleri | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K133 | SCMP | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K135 | Caixin | HTTP 200 içinde Site Unavailable; ikinci web kanalında başlıklar görüldü fakat bu HTTP toplama yolu doğrulanamadı |
| K140 | The Print | bot koruması / CAPTCHA ekranı |
| K153 | Addis Standard | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K160 | MSB | HTTP 302 yönlendirme tamamlanamadı; yayın ana sayfası doğrulanamadı |
| K168 | Reuters | HTTP 401; kimlik doğrulama gerekli |
| K170 | Financial Times | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K171 | Bloomberg | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K172 | Wall Street Journal | HTTP 401; kimlik doğrulama gerekli |
| K173 | The Economist | HTTP 402; ödeme/abonelik erişim yanıtı |
| K175 | Foreign Policy | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K180 | SAM (Dışişleri Stratejik Araştırmalar Merkezi) | HTTP 502 |
| K211 | Emirates Policy Center | HTTP 429; istek oranı sınırı |
| K226 | Ukrainian Institute for the Future | HTTP 429; istek oranı sınırı |
| K237 | Institut Montaigne | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K254 | Gateway House | HTTP 307 yönlendirme tamamlanamadı; RSS çalışsa da ana sayfa doğrulanamadı |
| K267 | Algérie Presse Service (APS) | HTTP 500 |
