# Mimari (v0.1, 19 Ekim 2026)

```
kaynak envanteri (data/kaynak_envanteri_v3.csv)
        │  disgundem seed
        ▼
   Supabase ── sources / countries / regions / dossiers / themes
        │
        │  disgundem fetch   (3 saatte bir, GitHub Actions) — önem hunisi:
        │    tekrar → ön filtre (B/R/T'de Türkiye terimi) → toplu LLM elemesi (yalnız başlık, 40'lık parti)
        │    → önem<3 saklanmaz · 3 havuz · ≥4 kuyruk → kümeleme → ülke/gün ve toplam/gün tavanı
        │    rss → feedparser · gnews → Google News RSS (yerel dil edisyonu) · scrape → liste sayfası
        │  Chrome listesi (data/chrome_kaynaklari.csv: premium + RSS'i sunucuya kapalı 14 kaynak): editörün Claude in Chrome oturumu → data/premium/*.json → disgundem chrome-import
        ▼
   clusters + articles (status=queued | pool)   ← yalnız başlık, link, tarih, kısa lead; gövde yok
        │
        │  disgundem classify  (yalnız kuyruktakiler: 2-3 cümle Türkçe özet, tema, dosya, çerçeve)
        ▼
   editorial_queue görünümü (küme bazlı; günde ~15-30 küme hedefi)
        │
        │  editör onayı (yayın yüzeyi/arayüz; bu PR'de yok)
        ▼
   articles (approved → published)  ·  clusters (gelişme kümesi)  ·  analyses (Analiz içerik tipi)
        │
        │  disgundem measure  (haftalık) → source_metrics + budama raporu
        ▼
   kaynak budama kararı (editör)
```

## Neden böyle

- **Ülke ve dosya birinci sınıf.** `countries.scope` (A/B/R/T/P) kaynak değil ülke özelliği; yeni ülke eklemek = `sources.COUNTRIES`'e bir satır + CSV'ye kaynak. Bir haber `article_countries` ve `article_dossiers` ile birden fazla yere bağlanır; Doğu Akdeniz gibi dosyalar ülke sayfasına sığmayan konuları toplar.
- **Hacim ölçümü hatta gömülü.** PR #1 elle ölçümün sürdürülemez olduğunu gösterdi. `source_metrics` her hafta kayan 30 günlük pencereyi yazar; `measure --report` pasif/çekirdek adaylarını listeler. Karar editörün.
- **Telif.** Hiçbir toplayıcı makale gövdesi almaz. Premium (P) kaynaklar sunucuda hiç toplanmaz: editör kendi abonelikleriyle Claude in Chrome'da okur, çıktı yalnız başlık+link+tarih+kendi cümleleriyle özet olarak `premium-import` ile girer; özet 600 karakteri, alıntı 15 kelimeyi aşarsa kayıt reddedilir. Chrome listesi premium ile RSS'i sunucuya 403 veren kaynaklardan oluşur (`data/chrome_kaynaklari.csv`); bu ikinci gruptakiler sunucuda gnews yedeğiyle de izlenir. Diğer her şey sunucu tarafında.
- **Editör onayı kodda.** `articles.status` akışı `fetched → classified/queued → approved → published`; `published` dışında hiçbir satır anon okumasına açık değil (RLS).
- **Sağlayıcıdan bağımsız LLM.** `LLM_PROVIDER=anthropic|openai|openrouter|none` (`openrouter`: DeepSeek, GLM vb. tek anahtarla; `FALLBACK_MODELS` ve `OPENROUTER_ZDR` ayarlanabilir; model karşılaştırması için `disgundem eval --saglayici openrouter --ozet-modeli <model> --hakem-modeli <sabit model> --etiket <not>`); `none` modunda terim filtresi çalışır, hat yine akar. Prompt sürümü (`prompts/classify_v1.md`) her kayda yazılır; prompt değişince karşılaştırılabilir.
- **Önem hunisi.** Ham akış (çekirdek 134 kaynaktan günde birkaç bin başlık) veritabanına girmez; yalnız önem ≥ 3 saklanır, ≥ 4 kuyruğa girer, aynı olay tek küme. LLM maliyeti iki kademeli: ucuz toplu eleme (yalnız başlık) herkese, özet yalnız kuyruğa girenlere. `LLM_PROVIDER=none` modunda yalnız Türkiye terimi geçenler havuza düşer, kuyruk boş kalır; kuyruğun dolması için LLM gerekir.
- **DRY_RUN varsayılan.** Supabase anahtarı yoksa her komut `data/out/*.jsonl`'e yazar; CI'da artifact olur. Böylece hat, veritabanı kurulmadan test edilir.

## Toplama yöntemi seçimi (seed sırasında)

| Durum | method |
| --- | --- |
| CSV'de çalışan RSS var | `rss` |
| Premium (P) | `manual` — sunucuda toplanmaz; Claude in Chrome oturumu + `chrome-import` |
| Engelli RSS (Chrome listesinde) | sunucuda `rss` → gnews yedeği; ek olarak Chrome oturumu + `chrome-import` |
| Scraping/sitemap alternatifi notlanmış | `scrape` (liste sayfası, yalnız başlık+link) |
| Diğer | `gnews` — `site:domain` + yerel dil Türkiye terimleri, ülke edisyonu |

A kapsamı kaynaklarda `gnews` Türkiye filtresi uygulamaz (iç gündem de gerekli); B'de uygular.

## Kurulum (dev)

1. Supabase'de **dev** projesi aç; `supabase/migrations/0001_schema.sql`'i SQL editöründe çalıştır (vector eklentisi açık olmalı).
2. Repo secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`; isteğe bağlı `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` veya `OPENROUTER_API_KEY` + vars `LLM_PROVIDER`, `LLM_MODEL` (OpenRouter için ayrıca `JUDGE_MODEL`, `FALLBACK_MODELS`, `OPENROUTER_ZDR`).
3. Actions → pipeline → Run workflow → `seed`, sonra `check-feeds` (RSS adreslerinin gerçek durumu), sonra saatlik `fetch` kendiliğinden.
4. Yerelde: `cp .env.example .env`, `pip install -e ./pipeline`, `disgundem check-feeds --core`.

## Bu PR'de olmayanlar (sonraki görevler)

- Kümeleme (`articles.embedding` sütunu hazır; embedding üretimi ve küme oluşturma yok)
- Analiz taslağı üretimi (`analyses` tablosu hazır; LLM akışı yok)
- Editör arayüzü ve yayın yüzeyi (Astro/Next; `published` RLS politikası hazır)
- Chrome tarama oturumunun standart talimatı: `docs/CHROME_OTURUMU.md`
- Kaynak özel scraper seçicileri (`fetch/scrape.py: SELECTORS`)
