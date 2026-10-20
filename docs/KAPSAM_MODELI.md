# Kapsam Modeli (Kaynak Havuzu v2, 18 Ekim 2026)

Havuz, Claude'un genel bilgisine dayanan bir **başlangıç taslağıdır**. URL, RSS ve aktiflik doğrulanmadan hatta alınmamalıdır. Veri dosyaları: `data/kaynak_havuzu_v2.csv` (259 kaynak), `data/turkiye_terimleri.csv`, `data/Dis_Gundem_Kaynak_Havuzu_v2.xlsx` (kaynak: Kapsam Modeli, Özet, Tema Matrisi sayfaları).

## Kapsam seviyeleri (CSV `Kapsam` sütunu)
| Kod | Ad | Tanım |
|---|---|---|
| A | Yakın çevre | Ülkenin kritik/önemli **iç haberleri** (iktidar/seçim, güvenlik ve çatışma, ekonomi/kriz, dış politika kararları, enerji) + Türkiye ile ilgili her şey. Kaynak: ülkenin 4-7 ana ulusal yayını + ajans + 1 think tank. |
| B | Türkiye'ye bakış | Yalnızca Türkiye'yi konu alan içerik: anahtar kelime filtresi (`turkiye_terimleri.csv`) + LLM doğrulama. Kaynak: ülkenin 2-4 ağırlıklı yayını + Türkiye programı olan think tank'ler + Google News ülke/dil filtresi. |
| R | Bölgesel | Birden fazla ülkeye hizmet eden yayınlar (Al-Monitor, Eurasianet, JAMnews...). Hem A hem B rolünde çalışır; ülke etiketi makale bazında atanır. |
| T | Türk perspektifi | Resmi Türk pozisyonu ve Türk think tank'leri. Her ülke sayfasında "Ankara ne dedi" kutusunu besler. |
| P | Premium | FT, Bloomberg, WSJ, Economist, Foreign Affairs, Foreign Policy. Gmail bültenleri. Kendi analizinle süzülerek "Analiz" içerik tipinde kullanılır, haber kartı olmaz. |

Not: Türkiye'nin kendi iç gündemi kapsam dışıdır. T ve P kayıtları kaynak rolüdür, kapsam genişletmesi değildir.

## Think tank katmanı
Her bölge için yerel think tank'ler ve Türk think tank'leri (ORSAM, SETA, EDAM, TEPAV, İRAM, AVİM, İKV...). `Tür = Think tank` filtresiyle görünür (111 kayıt). Rolü haber değil, "Analiz" içerik tipinin hammaddesidir. Haftalık tarama yeterlidir, saatlik değil.

## Sütun anlamları
- **İçerik rolü:** İç gündem + Türkiye = A; Türkiye'ye bakış = B; Bölgesel; Türk perspektifi; Premium bağlam.
- **Güvenilirlik (Güv.):** A = bağımsız/kurumsal. B = ana akım ama devlet/sermaye/siyasi eksene yakın. C = devlet ajansı/propaganda; "resmi pozisyon" etiketiyle gösterilir, haber olarak değil.
- **Durum:** Çekirdek = ilk günden takip. Kontrol et = doğrulanmadı. Pasif/Çıkarıldı.

## Bölgeler (site navigasyonu)
Levant & Irak · Doğu Akdeniz · Körfez & İran · Kafkasya · Karadeniz & Rusya · Avrupa · Kuzey Amerika · Asya · Afrika. **Orta Asya ve Balkanlar bu sürümde yok**, ikinci fazda eklenir (`HEDEF.md`'deki ülke listesinde yer alırlar).

## Önem ölçeği ve huni (20 Ekim 2026'dan itibaren tüm başlıklara uygulanır)
Önem artık yalnız A iç gündemine değil, her başlığa tek ölçekle verilir (`pipeline/prompts/triage_v2.md`):

| Puan | A kapsamı iç gündem | Türkiye ile ilgili (tüm kapsamlar) |
|---|---|---|
| 5 | Savaş/ateşkes/barış kararı, rejim veya iktidar değişikliği, büyük saldırı | Türkiye'yi doğrudan hedef alan kriz |
| 4 | Seçim sonucu, hükümet krizi, büyük ekonomik şok | Somut karar, anlaşma, üst düzey ziyaret, askeri hamle, büyük ihale |
| 3 | Kabine değişikliği, önemli yargı kararı, enerji/altyapı anlaşması | Kayda değer yorum veya analiz |
| 2 | Rutin siyaset, açıklama tekrarı | Türkiye'nin geçerken anıldığı haber |
| 1 | Magazin, spor, kültür, yerel | Türkiye adı tesadüfi |

**Huni:** önem < 3 hiç saklanmaz (yalnız tekrar kontrolü için hash'i tutulur) · 3 saklanır ama kuyruğa girmez ("havuz": ülke sayfası ve analiz hammaddesi) · ≥ 4 editör kuyruğuna girer · aynı olayı anlatan başlıklar tek küme olarak bir kez görünür · ülke başına günde 4, toplam günde 30 küme tavanı; önem 5 tavanı deler. B/R/T kaynaklarında Türkiye terimi geçmeyen başlık LLM'e hiç gönderilmez. Eşikler `IMPORTANCE_*` / `QUEUE_*` değişkenleriyle ayarlanır.

**Ekonomik analiz önceliği (20 Ekim editör kararı):** ekonomi, enerji, finans, ticaret, yatırım, yaptırım veya altyapı üzerine *analiz/rapor* (rutin ekonomik haber değil) `eko` işareti alır ve kuyruğa önem **3**'ten girer (`ECON_QUEUE_MIN`, varsayılan 3). Önem puanı değişmez; sıralamada gerçek 4'lerin arkasında kalır, ülke/gün tavanı aynen uygulanır — yani kuyruk doluysa haber 4'leri önce girer.

## Tema matrisi
| Tema | Kapsam | Ağır olduğu ülkeler |
|---|---|---|
| Diplomasi | Ziyaretler, anlaşmalar, forumlar, krizler | Tümü |
| Güvenlik & savunma | Operasyonlar, savunma ihracatı (SİHA, KAAN), NATO, PKK/YPG, Doğu Akdeniz askeri | Suriye, Irak, Yunanistan, İsrail, Ukrayna, Azerbaycan, AB |
| Enerji | Boru hatları, LNG, nükleer, elektrik ihracı, Doğu Akdeniz gazı | Rusya, İran, Irak, Azerbaycan, İsrail, GKRY, Mısır |
| Ekonomi & yatırım | Ticaret, müteahhitlik, yeniden inşa, finans, Körfez sermayesi | Suudi, BAE, Irak, Suriye, Rusya, Afrika |
| Göç & diaspora | Mülteciler, geri dönüş, vize, Avrupa'daki Türkler | Suriye, AB, Almanya, Yunanistan |
| İç gündem (A) | Seçim, iktidar, kriz, protesto, yargı | Tüm A ülkeleri |
| Türkiye'ye bakış (B) | Yabancı basında Türkiye çerçevelemesi (olumlu/olumsuz/nötr) | Tüm B ülkeleri |
| Yumuşak güç | TİKA, Maarif, Diyanet, YTB, diziler, THY | Afrika, Balkanlar, Orta Asya, Kafkasya |
| Bölgesel rekabet | ABD, Rusya, Çin, İran, Körfez'in Türkiye'yle etkileşimi | Çapraz |

## Havuzun bilinen durumu (v2, ham sayımlar)
- 259 kaynak: A 112, B 90, R 26, T 22, P 9. Çekirdek 114, Kontrol et 145.
- Think tank 111 (çekirdek 38).
- Toplama yöntemi RSS işaretli 242 kaynaktan **202'sinin besleme URL'si boş**.
- `https://www.grc.net` iki kez geçiyor (Gulf Research Center: K060 ve K207). Birleştirilmeli.
- Orta Asya ve Balkanlar yok.
