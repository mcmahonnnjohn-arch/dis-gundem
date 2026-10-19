# Önerilen çekirdek set

**125 benzersiz editoryal aday; erişimi doğrulanmış 113 başlangıç kaynağı ve 12 koşullu aday.** CSV’de yalnız ilk grup `Çekirdek`tir. Doğrulanamayan hiçbir kayıt bu etiketi almaz. 113 kaynağın her biri otomatik toplanabilir demek değildir: çalışan RSS ile doğrulanmış ana sayfa/sitemap üzerinden manuel takip ayrı tutulur. Uygulama/scraper bu PR’nin konusu değildir.

Bu büyüklük, tüm 269 kaynağı aynı sıklıkla izleme yükünü azaltır; A ülkelerinde yerel haber + resmî pozisyon + analiz + eksik perspektif ihtiyacını, B ülkelerinde Türkiye bağlantılı birkaç yayın/programı korur. Ülke tablolarındaki ortak bölgesel kaynaklar toplamda yalnız bir kez sayılır. Düşünce kuruluşları haftalık analiz girdisi; günlük ajans/yerel haber akışından ayrı takvimle izlenir. Premium altı kaynak başlık/bülten için koşullu analiz katmanıdır ve 113 kaynağa otomatik eklenmez.

## Önce Suriye pilotu

K001 Enab Baladi Arapça yerel haber katmanı, K003 SANA resmî beyan katmanı, K004 Syria Direct açık saha/insan hakları gazeteciliği, K007 Omran yönetişim/güvenlik analizi için seçildi. K005 North Press kuzeydoğu yedeğidir. K001’in bulunan RSS’si İngilizce ürüne aittir; Arapça ana sayfası ayrı takip edilir. K004’ün sayısal hacmi yalnız İngilizce edisyonun tam arşivine aittir. SANA’daki beyan bağımsız teyit değildir; aktörler arası çatışma iddialarında başka bir kurumsal aileden ve mümkünse doğrudan kanıt gerekir. [Enab](https://www.enabbaladi.net/about-us/) · [Syria Direct](https://syriadirect.org/about-us/) · [Omran](https://omrandirasat.org/en/about-us.html).

Pilot, dört temel kaynağı işleterek başlar. Diğer ülkeleri aynı gün açmak yerine aşağıdaki hazır takip setiyle ülke ülke genişlemek önerilir. Haftalık analiz taraması ve editör onayı sürdürülebildikçe yedeklerden ekleme yapılır. Hacmi `ölçülemedi` olan kaynağın düşük getirili olduğu varsayılmaz.

## Dağılım ve iş yükü

| Bölge | Envanter | Erişimi doğrulanmış çekirdek | Çekirdekte TT | Çekirdekte güncel RSS |
| --- | --- | --- | --- | --- |
| Levant & Irak | 25 | 12 | 3 | 5 |
| Doğu Akdeniz | 39 | 20 | 5 | 9 |
| Körfez & İran | 30 | 11 | 3 | 5 |
| Kafkasya | 24 | 12 | 3 | 6 |
| Karadeniz & Rusya | 26 | 12 | 3 | 6 |
| Avrupa | 33 | 16 | 9 | 7 |
| Kuzey Amerika | 22 | 3 | 2 | 2 |
| Asya | 23 | 11 | 4 | 4 |
| Afrika | 17 | 10 | 3 | 7 |
| Türkiye | 20 | 4 | 3 | 0 |
| Küresel | 10 | 2 | 1 | 1 |

| Kapsam | Çekirdek |
| --- | --- |
| A | 51 |
| B | 46 |
| R | 12 |
| T | 4 |
| P | 0 |

A ülkeleri için başlangıç modelindeki 4–7 haber + ajans + think tank hedefi bir yön göstericidir. Bu çekirdekte pilot yükünü sınırlamak ve aynı kurumsal aileyi iki bağımsız ses sanmamak için çoğu ülkede 3–4 tamamlayıcı giriş seçildi; daha geniş havuz CSV’de yedek kalır. Küçük ülke setlerindeki boşluklar kaynak sayısı artırılarak kapanmış varsayılmaz.

## Ülke ve ortak havuz başına gerekçe

### Suriye

- Başlangıç: K001 Enab Baladi; K003 SANA; K004 Syria Direct; K007 Omran Center for Strategic Studies.
- Gerekçe ve sınır: Çekirdek: K001 Arapça yerel haber, K003 resmi pozisyon, K004 saha/insan hakları ve ölçülebilir açık arşiv, K007 yönetişim analizi. Kuzeydoğu ve farklı etno-dini yerel perspektifler halen eksik temsil riski taşır.

### Irak

- Başlangıç: K009 Rudaw; K012 Al-Mada; K013 INA (Iraqi News Agency); K188 Al-Bayan Center.
- Gerekçe ve sınır: Çekirdek: K009 Kürtçe/Erbil haberleri, K012 Arapça Bağdat gündemi, K013 resmi ajans, K188 Irak merkezli enerji/su/dış politika araştırması. K010 aynı mülkiyet-siyaset çevresindeki yedek olarak tutulur.

### Lübnan

- Başlangıç: K017 Al-Modon; K018 L'Orient Today; K261 National News Agency (NNA); K192 Malcolm H. Kerr Carnegie Middle East Center.
- Gerekçe ve sınır: Çekirdek: K017 Arapça haber, K018 İngilizce özgün haber, yeni NNA resmi açıklama, K192 Beyrut merkezli bölgesel analiz. K017/K018 A; Carnegie R olarak kalır.

### İsrail

- Başlangıç: K022 Ynet; K020 Haaretz; K024 INSS; K195 Moshe Dayan Center (Tel Aviv Üni.).
- Gerekçe ve sınır: Çekirdek: K022 İbranice gündem, K020 Haaretz karşılaştırmalı haber perspektifi, K024 Türkiye başlıklı güvenlik analizi, K195 tarihli Turkeyscope dizisi. Ödeme/oturum engeli olan haberlerde erişilen başlık kapsamı açıkça tutulur.

### Yunanistan

- Başlangıç: K027 To Vima; K029 Naftemporiki; K030 ERT News; K031 ELIAMEP.
- Gerekçe ve sınır: Çekirdek: K027 Yunanca genel haber, K029 ekonomi/denizcilik, K030 kamu yayıncılığı, K031 Türkiye araştırması. Emek/sol ve bölgesel yerel perspektifler sınırlı; Ege ihtilafında resmi iddialar tek başına doğrulama değildir.

### GKRY

- Başlangıç: K034 Philenews; K035 Politis; K036 CNA (Cyprus News Agency); K200 PRIO Cyprus Centre.
- Gerekçe ve sınır: Çekirdek: K034 geniş Yunanca haber, K035 ikinci yerel yayın, K036 resmi ajans, K200 iki toplumlu araştırma. K037 dil yedeği; KKTC çekirdeğiyle birlikte değerlendirme gerekir.

### KKTC

- Başlangıç: K038 Kıbrıs Postası; K260 Yenidüzen.
- Gerekçe ve sınır: Çekirdek: K038 genel haber akışı ve yeni Yenidüzen sol/federasyon perspektifi; farklı çözüm tezleri ile Türkiye ilişkileri tartışmaları için PRIO ortak analitik havuzdan okunur.

### Mısır

- Başlangıç: K041 Al-Masry Al-Youm; K040 Ahram Online; K201 Al-Ahram Center for Political & Strategic Studies.
- Koşullu: K039 Mada Masr — HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı.
- Gerekçe ve sınır: Çekirdek: K039 Arapça eleştirel haber, K041 yerel ana akım, K040 resmi kurum çevresinin haberleri, K201 Türkiye konulu kurumsal araştırma. İslamcı muhalefet ve kırsal/toplumsal gündem eksikleri ayrıca aranmalı.

### Libya

- Başlangıç: K045 Libya Observer; K262 Al-Wasat; K046 Libya Herald.
- Gerekçe ve sınır: Çekirdek: K045 Arapça haber, yeni Al-Wasat ikinci Arapça perspektif, K046 İngilizce yedek. Libya A'ya genişletilmiyorsa tek ülke kaynakları B olur; Türkiye bağlantısız iç gündem toplanmaz.

### İran

- Başlangıç: K047 IRNA; K052 Shargh; K051 IranWire; K203 IPIS (Dışişleri).
- Gerekçe ve sınır: Çekirdek: K047 resmi Farsça gündem, K052 yerel gazete, K051 sürgün/insan hakları bakışı, K203 diplomatik araştırma. Devlet ve sürgün kaynaklarının güvenlik iddiaları bağımsız kanıtla karşılaştırılmalı; etnik azınlıklar sınırlı temsil edilir.

### Suudi Arabistan

- Başlangıç: K055 Asharq Al-Awsat; K058 SPA; K060 Gulf Research Center.
- Koşullu: K059 Okaz — HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı.
- Gerekçe ve sınır: Çekirdek: K055 Arapça bölge haberleri, K058 resmi ajans, K059 Arapça yerel gündem, K060 Körfez–Türkiye araştırması. K207 mükerrer GRC kaydı K060'a birleştirilir.

### Katar

- Başlangıç: K061 Al Jazeera (Arapça); K208 Al Jazeera Centre for Studies.
- Gerekçe ve sınır: Çekirdek: K061 bölgesel Arapça haber ve K208 Türkiye temalı uzun analiz; ikisi R rolünde. Katar iç siyasetinin eleştirel yerel perspektifi eksiktir; Arapça koşulunun sağlanması iç gündemin kapsamlı izlendiği anlamına gelmez.

### BAE

- Başlangıç: K062 The National (BAE); K263 Emirates News Agency (WAM).
- Koşullu: K211 Emirates Policy Center — HTTP 429; istek oranı sınırı.
- Gerekçe ve sınır: Çekirdek: K062 bölgesel haber, yeni WAM Arapça resmi Türkiye–BAE açıklamaları, K211 bölgesel politika analizi. K210 Türkiye ofisi nedeniyle yedek araştırma adayıdır; engel/JS durumu teknik doğrulamaya bağlıdır.

### Azerbaycan

- Başlangıç: K067 APA; K070 AZERTAC; K214 Topchubashov Center; K264 Abzas Media.
- Gerekçe ve sınır: Çekirdek gerekçesi: APA hızlı yerel akış; AZERTAC resmi beyan; Topchubashov analiz; Abzas kamusal hesap verebilirlik.

### Ermenistan

- Başlangıç: K073 CivilNet; K074 Armenpress; K077 Hetq; K217 Regional Studies Center.
- Gerekçe ve sınır: Çekirdek: CivilNet yerel haber; Armenpress resmi beyan; Hetq araştırmacı denge; RSC Türkiye normalleşme uzmanlığı. Çatışma iddiaları tek ulusal kaynaktan kesinleştirilmemeli.

### Gürcistan

- Başlangıç: K079 JAMnews; K080 OC Media; K219 Georgian Institute of Politics.
- Gerekçe ve sınır: Çekirdek bölgesel seçim: JAMnews yerel dil/toplum, OC Media bölgesel haber, GIP bağlamsal araştırma; Gürcistan resmi günlük ajans perspektifi bu sette eksik.

### Rusya

- Başlangıç: K083 TASS; K085 Kommersant; K086 Meduza; K220 RIAC.
- Gerekçe ve sınır: Çekirdek: TASS beyan; Kommersant ekonomik aktörler; Meduza sürgün gazetecilik; RIAC Türkiye ilişkileri. Carnegie Berlin ve Riddle derin analiz için yedek.

### Ukrayna

- Başlangıç: K092 Ukrainska Pravda; K093 European Pravda; K095 Suspilne; K225 Ukrainian Prism.
- Gerekçe ve sınır: Çekirdek: Pravda iç gündem; European Pravda diplomasi/AB; Suspilne kamu hizmeti; Prism Türkiye/Karadeniz analizi.

### Romanya

- Başlangıç: K098 Romania Insider; K265 AGERPRES.
- Gerekçe ve sınır: Romence muhalif/araştırmacı perspektif çekirdek ikilide eksik; ajans haberleri hükümet denetimi için tek dayanak yapılmaz. Kapsam B, genel Balkan genişlemesi değildir.

### Çin

- Başlangıç: K132 Xinhua; K250 CIIS.
- Koşullu: K133 SCMP — HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı.
- Gerekçe ve sınır: Çekirdek: Xinhua Çince resmî çerçeve; SCMP Hong Kong/şirket ve dış politika seçkisi; CIIS diplomatik analiz. Caixin ekonomi için erişim doğrulanırsa yedek.

### Hindistan

- Başlangıç: K138 The Hindu; K142 ORF; K252 MP-IDSA.
- Koşullu: K140 The Print — bot koruması / CAPTCHA ekranı.
- Gerekçe ve sınır: Çekirdek: The Hindu genel haber, ThePrint Hintçe+siyasi analiz, ORF jeopolitik, MP-IDSA savunma. Hintçe tüm Hindistan dilleri adına temsil iddiası değildir.

### Pakistan

- Başlangıç: K144 Dawn; K268 Dawn News Urdu; K255 ISSI.
- Gerekçe ve sınır: Çekirdek: Dawn İngilizce haber; ayrı yeni kayıt Dawn News Urdu yerel dil; ISSI stratejik pozisyon. Dawn/Dawn News tek mülkiyet grubu sayılır. Eyaletler ve sivil haklarda farklı Urduca mülkiyet perspektifi eksik.

### Japonya

- Başlangıç: K145 Nikkei Asia; K266 Asahi Shimbun.
- Gerekçe ve sınır: Çekirdek ikili: Nikkei Asia iş/sermaye perspektifi, Asahi genel/diplomatik Japonca haber. Ücretli gövdeler alınmaz, başlık ve erişim kanıtıyla yetinilir.

### Somali

- Başlangıç: K151 Hiiraan Online; K152 Garowe Online; K258 Heritage Institute (Somali).
- Gerekçe ve sınır: Çekirdek: Hiiraan haber akışı, Garowe farklı bölgesel bakış, Heritage yardım/devlet kapasitesi analizi. Türkiye yardımı hakkındaki 2016 raporu güncel etki ölçümü değildir. https://heritageinstitute.org/turkeys-assistance-model-in-somalia-achieving-much-with-little/

### Etiyopya

- Başlangıç: K259 Rift Valley Institute; K149 ISS Africa.
- Koşullu: K153 Addis Standard — HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı.
- Gerekçe ve sınır: Çekirdek aday: Addis Standard yerel aktörler; RVI Boynuz Afrika bağlamı; ISS güvenlik/Ankara bağlantısı. İki bölgesel think tank yerel Amharca haberin yerine geçmez.

### Sudan

- Başlangıç: K154 Sudan Tribune; K259 Rift Valley Institute; K149 ISS Africa.
- Gerekçe ve sınır: Çekirdek: Sudan Tribune yerel Arapça gündem; RVI saha/siyasal ekonomi; ISS dış aktör ve güvenlik analizi.

### Nijerya

- Başlangıç: K155 Premium Times; K149 ISS Africa.
- Gerekçe ve sınır: Çekirdek: Premium Times İngilizce/Hausa araştırma ve yerel haber; ISS Türkiye-Afrika güvenlik çerçevesi için paylaşılan bölgesel destek.

### Cezayir

- Başlangıç: K156 TSA (Tout sur l'Algérie).
- Koşullu: K267 Algérie Presse Service (APS) — HTTP 500.
- Gerekçe ve sınır: Çekirdek: TSA özel yayın çerçevesi, APS devlet perspektifi. APS’nin resmî rolü haberlerde taraf atfıyla görünür olmalı.

### Senegal

- Başlangıç: K157 Seneweb; K148 Jeune Afrique; K149 ISS Africa.
- Gerekçe ve sınır: Çekirdek: Seneweb yerel gündem; Jeune Afrique Frankofon bölge çerçevesi; ISS Türkiye-Batı Afrika güvenlik bağlantısı. https://issafrica.org/iss-today/west-africa-and-turkey-forge-new-security-relations

### Afrika (bölgesel)

- Başlangıç: K148 Jeune Afrique; K149 ISS Africa; K259 Rift Valley Institute.
- Gerekçe ve sınır: Çekirdek: Jeune Afrique Frankofon haber ağı; ISS güvenlik; RVI Afrika Boynuzu saha/siyasal ekonomi. Ülke yerel dillerinin yerine geçmezler.

### Kafkasya (bölgesel)

- Başlangıç: K079 JAMnews; K080 OC Media; K082 Eurasianet.
- Gerekçe ve sınır: Çekirdek gerekçesi: JAMnews dil/yerel anlatı; OC Media güncel bölgesel haber; Eurasianet Kafkasya-Orta Asya bağlantısı. Tam sahiplik/finansman dökümü bu taramada bütün üç yayın için teyit edilmedi.

### Karadeniz (bölgesel)

- Başlangıç: K099 Black Sea News / Monitor; K227 CEPA (Center for European Policy Analysis).
- Gerekçe ve sınır: Çekirdek iki kaynak farklı işlev taşır; deniz olayları mümkün olduğunda resmî liman/denizcilik kayıtlarıyla desteklenmeli. Romanya/Bulgaristan ortak tek kaynak iddiası kaldırıldı.

### Asya-Pasifik (bölgesel)

- Başlangıç: K136 The Diplomat.
- Gerekçe ve sınır: Tek kaynak önerisi bölgesel ek katmandır; ayrı ülke kapsamı veya yeterli dil çeşitliliği iddiası değildir.

### AB

- Başlangıç: K105 Avrupa Komisyonu — Press Corner; K106 ECFR; K269 European External Action Service (EEAS).
- Koşullu: K100 Politico Europe — HTTP 402; ödeme/abonelik erişim yanıtı; K101 Euractiv — HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı.
- Gerekçe ve sınır: Çekirdek: K100 + K101 Brüksel günlük haber; K105 resmî karar/duyuru; K106 dış politika analizi. Parlamento K104 ve yeni EEAS gerektiğinde olayın birincil kaynağıdır.
- K269 EEAS, K105 Komisyonun dışındaki diplomatik birincil beyanı ayırmak için eklendi; Brüksel haberlerinin erişim boşluğu resmî beyanla kapanmış sayılmaz.

### Almanya

- Başlangıç: K110 Der Spiegel; K112 SWP.
- Koşullu: K109 Deutsche Welle (DW) — başlıksız HTML; ikinci web kanalında ana sayfa ve dil yolu açılamadı.
- Gerekçe ve sınır: Çekirdek: K109 iki dil arasında erişim; K110 Almanca ulusal haber; K112 kalıcı Türkiye uzmanlığı. FAZ ve siyasi vakıflar konuya göre karşı okuma sağlar.

### Fransa

- Başlangıç: K113 Le Monde; K114 IFRI.
- Gerekçe ve sınır: Çekirdek: K113 ulusal Fransızca olay haberi, K114 kalıcı Türkiye/Ortadoğu uzmanlığı. K237 ekonomi ve politika başlıklarında seçici tamamlayıcı.

### Birleşik Krallık

- Başlangıç: K115 The Guardian; K117 BBC Türkçe; K116 Chatham House; K238 RUSI.
- Gerekçe ve sınır: Çekirdek: K115 İngilizce haber, K117 Türkçe kamu yayınına erişim, K116 kalıcı Türkiye ilişkileri programı, K238 savunma/güvenlik tamamlayıcısı.

### İtalya

- Başlangıç: K232 IAI (Istituto Affari Internazionali); K233 ISPI; K271 ANSA.
- Gerekçe ve sınır: K232 IAI ve K233 ISPI yerel dilde Türkiye/Akdeniz analizlerini, K271 ANSA günlük İtalyanca haber ayağını sağlar; üç kaynak erişim kontrolünden geçti.
- K271 ANSA, iki araştırma kurumuna günlük İtalyanca ajans katmanı ekler.

### ABD

- Başlangıç: K123 CRS Reports (Kongre); K124 Atlantic Council — Turkey Program; K244 FDD.
- Koşullu: K120 Politico — HTTP 402; ödeme/abonelik erişim yanıtı.
- Gerekçe ve sınır: NYT gibi erişim engelli sayfalarda başlık veya arama sonucu görünmesi canlı yayın erişimini kanıtlamaz; teknik doğrulanamayan çekirdek adayı etkinleştirilmez.

### Türkiye

- Başlangıç: K159 Dışişleri Bakanlığı; K162 ORSAM; K164 EDAM; K179 İKV (İktisadi Kalkınma Vakfı).
- Gerekçe ve sınır: Çekirdek: K159 resmî dış politika belgesi, K162 Ortadoğu uzmanlığı, K164 ekonomi/güvenlik analizi, K179 Türkiye-AB uzmanlığı. Diğer bölge uzmanları ve Global Panorama konuya göre eklenir.

### Hollanda

- Başlangıç: K230 Clingendael.
- Gerekçe ve sınır: Çekirdek K230 tek araştırma tamamlayıcısıdır; 2–4 kaynak önerisi bu tek kayıtlı ülkede yapay yeni kayıt ekleyerek doldurulmadı.

### Belçika

- Başlangıç: K231 Egmont Institute.
- Gerekçe ve sınır: Çekirdek K231 yalnız Avrupa/Türkiye politika araştırması tamamlayıcısı; güncel Türkiye yayın düzenliliği ve yerel dil haber ayağı doğrulanana kadar ülkeyi temsil eden tam çekirdek sayılmamalı.

### Küresel

- Başlangıç: K169 Associated Press (AP); K176 International Crisis Group.
- Koşullu: K168 Reuters — HTTP 401; kimlik doğrulama gerekli.
- Gerekçe ve sınır: Çekirdek önerisi K168 Reuters ve K169 AP olay çapraz kontrolü, K176 ICG çatışma bağlamıdır. AFP teknik doğrulama sonrası üçüncü ajans olarak seçici eklenebilir.

## Kurumsal aile ve tekrar denetimi

K034/K037 Phileleftheros; K055/K056 SRMG; K009/K189 Rudaw; K163/K246 SETA; K146/K148 Jeune Afrique Media Group aynı aile içindeki ürünlerdir. Carnegie K089/K107/K192/K242/K253 ayrı coğrafi merkez/program akışlarıdır. Kaynak ID’si ayrı olsa da aynı haber URL’si veya aynı çeviri tekrar haber üretmemelidir. Bu PR toplama/tekilleştirme kodu yazmaz; editoryal bağımsız ses hesabının kuralını kaydeder.

## Erişimi doğrulanmış 113 kaynağın kesin listesi

| ID | Kaynak | Ülke | Rol | Toplama kanıtı |
| --- | --- | --- | --- | --- |
| K001 | Enab Baladi | Suriye | A | https://english.enabbaladi.net/feed/ |
| K003 | SANA | Suriye | A | yok; scraping: https://sana.sy/sitemap_index.xml |
| K004 | Syria Direct | Suriye | A | https://syriadirect.org/feed/ |
| K007 | Omran Center for Strategic Studies | Suriye | A | doğrulanamadı: XML açılıyor fakat son kayıt 2024-05-27T12:14:00+00:00; ölçüm döneminde güncelleme kanıtı yok |
| K009 | Rudaw | Irak | A | yok; scraping: https://www.rudaw.net/sorani |
| K012 | Al-Mada | Irak | A | https://almadapaper.net/feed/ |
| K013 | INA (Iraqi News Agency) | Irak | A | doğrulanamadı: XML açılıyor fakat son kayıt 2026-05-07T01:28:00+03:00; ölçüm döneminde güncelleme kanıtı yok |
| K017 | Al-Modon | Lübnan | A | https://www.almodon.com/rss |
| K018 | L'Orient Today | Lübnan | A | yok; scraping: https://today.lorientlejour.com/sitemap.xml |
| K020 | Haaretz | İsrail | A | https://www.haaretz.com/srv/haaretz-latest-headlines |
| K022 | Ynet | İsrail | A | yok; scraping: https://www.ynet.co.il/iphone/json/api/20m/google_site_map/8-2-3-6-538-1208-550-544-4003 |
| K024 | INSS | İsrail | A | doğrulanamadı: XML açılıyor fakat son kayıt 2017-01-19T10:15:28+00:00; ölçüm döneminde güncelleme kanıtı yok |
| K027 | To Vima | Yunanistan | A | https://www.tovima.gr/feed/ |
| K029 | Naftemporiki | Yunanistan | A | https://www.naftemporiki.gr/feed/ |
| K030 | ERT News | Yunanistan | A | https://www.ertnews.gr/feed/ |
| K031 | ELIAMEP | Yunanistan | A | https://www.eliamep.gr/feed/ |
| K034 | Philenews | GKRY | A | https://www.philenews.com/feed/ |
| K035 | Politis | GKRY | A | doğrulanamadı: XML açılıyor fakat boş; güncel yayın akışı doğrulanamadı |
| K036 | CNA (Cyprus News Agency) | GKRY | A | yok; scraping: https://www.cna.org.cy |
| K038 | Kıbrıs Postası | KKTC | A | yok; scraping: https://www.kibrispostasi.com/sitemap.xml |
| K040 | Ahram Online | Mısır | A | yok; scraping: https://English.ahram.org.eg/ui/front/sitemapindex.aspx |
| K041 | Al-Masry Al-Youm | Mısır | A | doğrulanamadı: HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı; besleme isteği |
| K045 | Libya Observer | Libya | B | https://ar.libyaobserver.ly/rss.xml |
| K046 | Libya Herald | Libya | B | https://libyaherald.com/rss.xml |
| K047 | IRNA | İran | A | https://www.irna.ir/rss |
| K051 | IranWire | İran | A | https://iranwire.com/fa/feed/ |
| K052 | Shargh | İran | A | yok; scraping: https://www.sharghdaily.com/sitemap.xml |
| K055 | Asharq Al-Awsat | Suudi Arabistan | A | https://english.aawsat.com/feed |
| K058 | SPA | Suudi Arabistan | A | yok; scraping: https://www.spa.gov.sa/sitemap.xml |
| K060 | Gulf Research Center | Suudi Arabistan | A | yok; scraping: https://www.grc.net/sitemap.xml |
| K061 | Al Jazeera (Arapça) | Katar | R | https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9 |
| K062 | The National (BAE) | BAE | R | yok; scraping: https://www.thenationalnews.com/arc/outboundfeeds/sitemap/?outputType=xml |
| K067 | APA | Azerbaycan | A | https://apa.az/rss |
| K070 | AZERTAC | Azerbaycan | A | https://azertag.az/rss |
| K073 | CivilNet | Ermenistan | A | yok; scraping: https://civilnet.am/sitemap.xml |
| K074 | Armenpress | Ermenistan | A | yok; scraping: https://armenpress.am/hy |
| K077 | Hetq | Ermenistan | A | https://hetq.am/hy/rss |
| K079 | JAMnews | Kafkasya (bölgesel) | R | https://jam-news.net/feed/ |
| K080 | OC Media | Kafkasya (bölgesel) | R | https://oc-media.org/feed/ |
| K082 | Eurasianet | Kafkasya (bölgesel) | R | doğrulanamadı: XML açılıyor fakat yayın tarihleri yok/ayrıştırılamadı; güncellik doğrulanamadı |
| K083 | TASS | Rusya | A | https://tass.com/rss/v2.xml |
| K085 | Kommersant | Rusya | A | yok; scraping: https://www.kommersant.ru/sitemaps/all_docs_sitemap.xml |
| K086 | Meduza | Rusya | A | https://meduza.io/rss/all |
| K092 | Ukrainska Pravda | Ukrayna | A | https://www.pravda.com.ua/rss |
| K093 | European Pravda | Ukrayna | A | yok; scraping: https://www.eurointegration.com.ua/sitemap/sitemap.xml |
| K095 | Suspilne | Ukrayna | A | https://suspilne.media/rss/all.rss |
| K098 | Romania Insider | Romanya | B | https://www.romania-insider.com/feed.xml |
| K099 | Black Sea News / Monitor | Karadeniz (bölgesel) | R | yok; scraping: https://www.blackseanews.net |
| K105 | Avrupa Komisyonu — Press Corner | AB | B | yok; scraping: https://ec.europa.eu/sitemap.xml |
| K106 | ECFR | AB | B | doğrulanamadı: HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı; besleme isteği |
| K110 | Der Spiegel | Almanya | B | https://www.spiegel.de/schlagzeilen/index.rss |
| K112 | SWP | Almanya | B | https://www.swp-berlin.org/rss.xml |
| K113 | Le Monde | Fransa | B | https://www.lemonde.fr/rss/une.xml |
| K114 | IFRI | Fransa | B | doğrulanamadı: XML açılıyor fakat son kayıt 2023-03-23T09:06:55+00:00; ölçüm döneminde güncelleme kanıtı yok |
| K115 | The Guardian | Birleşik Krallık | B | https://www.theguardian.com/world/turkey/rss |
| K116 | Chatham House | Birleşik Krallık | B | yok; scraping: https://www.chathamhouse.org/sitemap.xml |
| K117 | BBC Türkçe | Birleşik Krallık | B | https://feeds.bbci.co.uk/turkce/rss.xml |
| K123 | CRS Reports (Kongre) | ABD | B | yok; scraping: https://www.congress.gov/sitemap/index.xml |
| K124 | Atlantic Council — Turkey Program | ABD | B | https://www.atlanticcouncil.org/feed/ |
| K132 | Xinhua | Çin | B | doğrulanamadı: HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı; besleme isteği |
| K136 | The Diplomat | Asya-Pasifik (bölgesel) | B | https://thediplomat.com/feed/ |
| K138 | The Hindu | Hindistan | B | https://www.thehindu.com/news/international/feeder/default.rss |
| K142 | ORF | Hindistan | B | yok; scraping: https://www.orfonline.org/sitemap.xml |
| K144 | Dawn | Pakistan | B | https://www.dawn.com/feeds/home |
| K145 | Nikkei Asia | Japonya | B | yok; scraping: https://asia.nikkei.com/sitemap.xml |
| K148 | Jeune Afrique | Afrika (bölgesel) | B | https://www.jeuneafrique.com/feed/ |
| K149 | ISS Africa | Afrika (bölgesel) | B | yok; scraping: https://issafrica.org |
| K151 | Hiiraan Online | Somali | B | https://hiiraan.com/news.xml |
| K152 | Garowe Online | Somali | B | yok; scraping: https://www.garoweonline.com/en |
| K154 | Sudan Tribune | Sudan | B | https://sudantribune.com/feed |
| K155 | Premium Times | Nijerya | B | https://www.premiumtimesng.com/feed |
| K156 | TSA (Tout sur l'Algérie) | Cezayir | B | https://www.tsa-algerie.com/feed/ |
| K157 | Seneweb | Senegal | B | https://www.seneweb.com/feed |
| K159 | Dışişleri Bakanlığı | Türkiye | T | doğrulanamadı: yalnız Other Papers and Links; genel açıklama akışı değil |
| K162 | ORSAM | Türkiye | T | doğrulanamadı: XML açılıyor fakat boş; güncel yayın akışı doğrulanamadı |
| K164 | EDAM | Türkiye | T | yok; scraping: https://edam.org.tr/sitemap.xml |
| K169 | Associated Press (AP) | Küresel | R | doğrulanamadı: HTTP 401; kimlik doğrulama gerekli; besleme isteği |
| K176 | International Crisis Group | Küresel | R | https://www.crisisgroup.org/rss.xml |
| K179 | İKV (İktisadi Kalkınma Vakfı) | Türkiye | T | yok; scraping: https://www.ikv.org.tr |
| K188 | Al-Bayan Center | Irak | A | https://www.bayancenter.org/feed/ |
| K192 | Malcolm H. Kerr Carnegie Middle East Center | Lübnan | R | yok; scraping: https://carnegieendowment.org/sitemap.xml |
| K195 | Moshe Dayan Center (Tel Aviv Üni.) | İsrail | A | yok; scraping: https://dayan.org/sitemap.xml |
| K200 | PRIO Cyprus Centre | GKRY | A | yok; scraping: https://cyprus.prio.org |
| K201 | Al-Ahram Center for Political & Strategic Studies | Mısır | A | yok; scraping: https://acpss.ahram.org.eg/ui/front/sitemap.xml |
| K203 | IPIS (Dışişleri) | İran | A | yok; scraping: https://ipis.ir/ |
| K208 | Al Jazeera Centre for Studies | Katar | R | https://studies.aljazeera.net/en/rss.xml |
| K214 | Topchubashov Center | Azerbaycan | A | yok; scraping: https://top-center.org/en |
| K217 | Regional Studies Center | Ermenistan | A | doğrulanamadı: XML açılıyor fakat son kayıt 2026-08-25T18:21:01+04:00; ölçüm döneminde güncelleme kanıtı yok |
| K219 | Georgian Institute of Politics | Gürcistan | R | doğrulanamadı: XML açılıyor fakat son kayıt 2025-05-30T14:24:10+00:00; ölçüm döneminde güncelleme kanıtı yok |
| K220 | RIAC | Rusya | A | yok; scraping: https://russiancouncil.ru |
| K225 | Ukrainian Prism | Ukrayna | A | yok; scraping: https://prismua.org/sitemap_index.xml |
| K227 | CEPA (Center for European Policy Analysis) | Karadeniz (bölgesel) | R | https://cepa.org/feed/ |
| K230 | Clingendael | Hollanda | B | https://www.clingendael.org/rss.xml |
| K231 | Egmont Institute | Belçika | B | yok; scraping: https://egmontinstitute.be/sitemap_index.xml |
| K232 | IAI (Istituto Affari Internazionali) | İtalya | B | doğrulanamadı: aggregator akışının kuruma ait araştırma kapsamı doğrulanamadı |
| K233 | ISPI | İtalya | B | doğrulanamadı: XML açılıyor fakat son kayıt 2024-11-29T17:30:07+00:00; ölçüm döneminde güncelleme kanıtı yok |
| K238 | RUSI | Birleşik Krallık | B | doğrulanamadı: yalnız yaklaşan etkinlik akışı; yayınlar değil |
| K244 | FDD | ABD | B | https://www.fdd.org/feed/ |
| K250 | CIIS | Çin | B | yok; scraping: https://www.ciis.org.cn |
| K252 | MP-IDSA | Hindistan | B | doğrulanamadı: XML açılıyor fakat son kayıt 2024-02-28T08:02:02+00:00; ölçüm döneminde güncelleme kanıtı yok |
| K255 | ISSI | Pakistan | B | https://issi.org.pk/feed/ |
| K258 | Heritage Institute (Somali) | Somali | B | https://heritageinstitute.org/feed/ |
| K259 | Rift Valley Institute | Afrika (bölgesel) | B | doğrulanamadı: XML açılıyor fakat boş; güncel yayın akışı doğrulanamadı |
| K260 | Yenidüzen | KKTC | A | https://www.yeniduzen.com/rss/ |
| K261 | National News Agency (NNA) | Lübnan | A | yok; scraping: https://nna-leb.gov.lb/sitemap.xml |
| K262 | Al-Wasat | Libya | B | yok; scraping: https://www.alwasat.ly/sitemap.xml |
| K263 | Emirates News Agency (WAM) | BAE | B | yok; scraping: https://www.wam.ae/ar/sitemap/news.xml |
| K264 | Abzas Media | Azerbaycan | A | https://abzas.org/rss.xml |
| K265 | AGERPRES | Romanya | B | doğrulanamadı: üçüncü taraf allorigins/bazqux proxy; yayıncı beslemesi değil |
| K266 | Asahi Shimbun | Japonya | B | doğrulanamadı: HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı; besleme isteği |
| K268 | Dawn News Urdu | Pakistan | B | yok; scraping: https://www.dawnnews.tv/feeds/sitemap |
| K269 | European External Action Service (EEAS) | AB | B | yok; scraping: https://www.eeas.europa.eu/sitemap.xml |
| K271 | ANSA | İtalya | B | https://www.ansa.it/rss.xml |

## 12 koşullu editoryal aday

| ID | Kaynak | Neden koşullu |
| --- | --- | --- |
| K039 | Mada Masr | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K059 | Okaz | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K100 | Politico Europe | HTTP 402; ödeme/abonelik erişim yanıtı |
| K101 | Euractiv | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K109 | Deutsche Welle (DW) | başlıksız HTML; ikinci web kanalında ana sayfa ve dil yolu açılamadı |
| K120 | Politico | HTTP 402; ödeme/abonelik erişim yanıtı |
| K133 | SCMP | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K140 | The Print | bot koruması / CAPTCHA ekranı |
| K153 | Addis Standard | HTTP 403; erişim reddedildi; nedenin bot olduğu ayrıca kanıtlanmadı |
| K168 | Reuters | HTTP 401; kimlik doğrulama gerekli |
| K211 | Emirates Policy Center | HTTP 429; istek oranı sınırı |
| K267 | Algérie Presse Service (APS) | HTTP 500 |

Bu 12 ID erişim yeniden doğrulanmadan CSV çekirdeğine veya yayın kuyruğuna alınmaz. Premium K170–K175 bu 12 adayın içinde değildir; ayrı P katmanında yalnız başlık/bülten erişim durumu ve sınırlamalarla tutulur.
