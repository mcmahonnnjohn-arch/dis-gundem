# Pilot 30 — Editoryal karar

_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._


## KARAR: **NO-GO**

Teknik/araştırma kapıları geçilmedi (PENDING değil). 150 kaynağa ölçekleme ve otomatik yayın **açılmaz**. İnsan editör imzası bu turda atılmadı.

## Sayılar
- Gerçekten incelenen kaynak: 30/30 (keşif + kör doğrulama + provenance + red-team).
- 5/5 zorunlu kontrolü geçen (editör incelemesine hazır, kabul DEĞİL): 3 — K112, K238, N001.
- Reddedilen: 0 (kanıtlı ret yok). Bekleyen/HOLD: 27. Kabul edilen: 0.
- Kapı sayıları: kimlik 18/30, kanonik URL 19/29, özgünlük 8/27, köken 13/27.

## En değerli özgün kaynaklar (kanıtla)
- N001 Bellingcat: tarihli özgün OSINT (jeolokasyon/görüntü doğrulama); görüntü kökenleri iddia başına etiketlenmeli (RT-022).
- K112 SWP, K238 RUSI: özgün analiz, tarihli çalışmalar; finansman/çıkar bağlamı UNKNOWN veya kısmi (RT-014, RT-015).
- N002 ACLED: özgün kodlanmış veri katmanı, fakat girdileri medya/kurum raporları; metodoloji ve bağışçı listesi doğrulanamadı (RT-021).

## En önemli provenance/bağımsızlık sorunları
- Sıfır bağımsız teyit çifti: TASS/Naftemporiki/Reuters (Peşkov), Xinhua/TASS (Nasser Hastanesi), SANA/MFA (219), Xinhua/Al-Monitor (Hürmüz) aynı kökene dayanıyor.
- TASS–Xinhua 2026-2030 içerik paylaşımı: Rusya-Çin konularında tek aile sayılmalı.
- Meduza'nın bir 'özgün' örneği Glasnaya yeniden yayımı; Al-Monitor Axios/AFP aktarıyor.

## Kapsama boşlukları
- Bölgeler (11): {'Levant & Irak': 4, 'Doğu Akdeniz': 4, 'Körfez & İran': 3, 'Kafkasya': 3, 'Karadeniz & Rusya': 3, 'Avrupa': 3, 'Kuzey Amerika': 2, 'Asya': 2, 'Afrika': 2, 'Türkiye': 1, 'Küresel': 3}. Diller: {'ar': 5, 'en': 28, 'tr': 3, 'el': 2, 'fa': 2, 'az': 1, 'hy': 1, 'ru': 3, 'uk': 1, 'de': 1, 'zh': 1, 'am': 1, 'om': 1}; 28/30 kaynak İngilizce içeriyor, 11'i yalnız İngilizce (RT-020).
- Türkiye yalnız Dışişleri Bakanlığı ile temsil ediliyor; Türkçe basın yok. Afrika, Güney/Doğu Asya, Latin Amerika, Rusya (bağımsız) ve Orta Doğu (Arapça pan-bölgesel) zayıf.
- Kırmızı takımın **yalnız öneri** olarak andığı yerel dil adayları (kayıt defterine EKLENMEDİ): Kan/Ynet/Maariv, BBC Persian/Radio Farda, Medyascope/bianet/T24, Ukrainska Pravda/Suspilne, Novaya Gazeta Europe/Mediazona, Al-Araby Al-Jadeed, Dabanga, Jeune Afrique, Folha/Infobae, Caixin, Dawn/Scroll.

## Editörün karar vermesi gereken açık konular
1. **Resmî/devlet kanalları (SANA, IRNA, AZERTAC, TASS, Xinhua, Dışişleri, AB Press Corner):** özgünlük kapısını yapısal olarak geçemez (6 FAIL). Yalnız 'atıflı resmî pozisyon' rolü için ayrı bir rol/kapı tanımlanacak mı? Bu kapıyı gevşetmeyi bu tur yapmadım; karar sizin.
2. **Mada Masr (K039):** mahkeme kapatma kararı (27 Ekim 2026); izlenecek mi, HOLD mu, ayna/alternatif erişim var mı?
3. **Erişilemeyen kaynaklar (Haaretz, The Hindu, Reuters, CRS, IRNA, IranWire):** robots/paywall/engelden BLOCKED. Yasal erişim yolu (abonelik, API, lisanslı akış) gerekir; ücretli hizmet için sizin onayınız gerekir, kullanılmadı.
4. **signal_noise ölçümü:** her aday için 20 maddelik örneklem; ölçülmeden tam puan ve katman yok.
5. **Gözlem zamanı kesinliği (RT-001):** kayıtlar toplu yazım zamanını taşıyor; bağımsız bir turda sayfa-bazlı zaman damgasıyla yeniden doğrulama istenir mi?
6. **İnsan editör imzası:** `signoffs.editor` yalnız `human:<ad>` biçiminde, gerçek insan tarafından doldurulur.
7. Son kabul, 150'ye genişleme ve yayın için açık onayınız gerekir; hiçbiri verilmedi.

## 150 kaynağa genişleme koşulları (hepsi birlikte)
- Hazırlık kapısı GO: ≥27 kabul, 30 kimlik, ≥29 URL, ≥27 özgünlük, ≥27 köken, ≥2 OSINT/veri kabulü.
- Set genelindeki açık yüksek bulguların (RT-001, 002, 003, 004, 005, 020) kapatılması ve yeniden red-team.
- Kaynak başına tam 7 bileşenli puan, üç farklı imza, insan editör onayı.
- Gerçek iddia testi: `claims.json`'da en az bir iddianın iki gerçekten bağımsız kökenle teyidi.
- Yerel dil/bölge boşlukları için yeni adaylar aynı keşif→kör doğrulama→provenance→red-team zincirinden geçmeli.

Nihai ilke: daha fazla kaynak değil, daha fazla bağımsız teyit.
