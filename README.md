# Dış Gündem

Türkiye'nin aktif olduğu coğrafyalardaki gelişmeleri ve dünyanın Türkiye'ye bakışını derleyen Türkçe haber/analiz sitesi. Otomatik toplama + LLM sınıflandırma + editör onayı.

- Hedef ve kurallar: [`docs/HEDEF.md`](docs/HEDEF.md)
- Kapsam modeli (A/B/R/T/P, önem ölçütü, temalar): [`docs/KAPSAM_MODELI.md`](docs/KAPSAM_MODELI.md)
- Mimari ve kurulum: [`docs/MIMARI.md`](docs/MIMARI.md)
- Kaynak envanteri (269 kaynak, doğrulanmış): [`data/kaynak_envanteri_v3.csv`](data/kaynak_envanteri_v3.csv) · raporlar [`docs/envanter/`](docs/envanter/)

## Hızlı başlangıç

```bash
pip install -e ./pipeline
cp .env.example .env            # DRY_RUN=1 ile veritabanı gerekmez
disgundem seed                  # envanteri yükle (dry-run: data/out/)
disgundem check-feeds --core    # çekirdek RSS adreslerini dene
disgundem fetch                 # çekirdek kaynakları topla (premium hariç)
disgundem premium-import data/premium/2026-10-19.json   # Claude in Chrome premium oturumu çıktısı
disgundem classify              # sınıflandır, kuyruğa al
disgundem measure --report      # 30 günlük hacim + budama raporu
```

Şema: [`supabase/migrations/0001_schema.sql`](supabase/migrations/0001_schema.sql). CI: [`.github/workflows/pipeline.yml`](.github/workflows/pipeline.yml) (saatlik fetch, haftalık measure).

## Çalışma biçimi

Her başlık ayrı branch ve PR; PR açıklamasında ne değişti, nasıl test edildi, riskler. Supabase'e yalnız dev projesi üzerinden. Merge kararı editörün.
