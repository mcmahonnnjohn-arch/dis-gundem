# Dış Gündem: Hedef ve Kapsam

## Hedef
Türkiye'nin aktif olduğu coğrafyalardaki gelişmeleri ve o ülkelerdeki Türkiye ile ilgili haberleri derleyen, Türkçe bir haber/analiz sitesi.

## İki mercek
- **Mercek 1: Türkiye'yi dışarıdan nasıl görüyorlar.** Yabancı basın, düşünce kuruluşları ve hükümetlerin Türkiye'ye bakışı.
- **Mercek 2: Rakipler ve dostlar neyle meşgul.** Ülkelerin ekonomik, siyasi ve askeri gündemi.

Türkiye iç gündemi kapsam dışıdır.

Not: Mercekler editoryal bakıştır. Kaynak havuzundaki A/B/R/T/P kodları ise ülke kapsam seviyeleridir (A = yakın çevre: kritik iç haberler + Türkiye'yle ilgili her şey; B = yalnızca Türkiye'ye bakış). Ayrıntı: `docs/KAPSAM_MODELI.md`.

## Kapsam ülkeleri
Suriye, Irak, İran, Suudi Arabistan, Mısır, GKRY, Yunanistan, İsrail, Lübnan, Ermenistan, Azerbaycan, Orta Asya cumhuriyetleri, Balkanlar, Ukrayna/Karadeniz kıyıları, Afrika. AB de eklenebilir.
Kaynak havuzu v2'de Orta Asya ve Balkanlar yoktur; ikinci faz.

**Pilot ülke: Suriye.** Yeni ülke eklemek kod değişikliği değil, yapılandırma (veri girişi) ile mümkün olmalı.

## Editoryal akış
topla → özetle → analiz et → editör onayı → yayınla.
"Kendi süzgecimden geçirme" adımı, kodda bir onay kuyruğudur. Onaylanmamış hiçbir içerik yayınlanmaz.

## Kaynak ve telif kuralları
- FT, Foreign Affairs, Foreign Policy, Bloomberg gibi premium yayınların makale metni siteye konmaz, veritabanında saklanmaz. Saklanacaklar: başlık, yayın tarihi, kaynak linki, kendi cümlelerle en fazla 3 cümlelik özet ve üretilen analiz.
- Alıntı en fazla 15 kelime, kaynak başına en fazla bir alıntı.
- Birincil kaynaklar (resmi açıklamalar, bakanlıklar, uluslararası kuruluşlar, ajanslar) öncelikli.
- Doğrulanamayan bilgi yayın kuyruğuna girmez; "doğrulanamadı" etiketiyle ayrı listelenir.

## Çalışma biçimi
Supabase'e yalnızca geliştirme (dev) branch'i üzerinden bağlanılır. Her başlık ayrı branch ve ayrı PR. Her PR'da: ne değişti, nasıl test edildi, riskler. Merge edilmez, editör (repo sahibi) inceler.

## Veri ve görevler
- `data/kaynak_havuzu_v2.csv`: 259 kaynaklık doğrulanmamış başlangıç havuzu (xlsx sürümü ve `turkiye_terimleri.csv` yanında).
- `docs/KAPSAM_MODELI.md`: kapsam seviyeleri, önem ölçütü, tema matrisi.
- `docs/gorevler/01-kaynak-envanteri.md`: ilk görev, havuzu doğrulanmış envantere çevirmek.
