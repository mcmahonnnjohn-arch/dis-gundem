# Claude in Chrome tarama oturumu

Kaynak listesi: `data/chrome_kaynaklari.csv` (20 kaynak: 6 premium + 14 engelli-RSS). `Sıklık` sütunu her kaynağın
ne zaman taranacağını, `Tarama odağı` neyin alınacağını söyler.

## Oturum
1. Editörün Chrome'unda yeni sekmede listedeki kaynakları sırayla aç (günlük olanlar her gün, haftalıklar pazartesi).
2. Kapsam:
   - **A kademesi** (Suriye, İsrail, GKRY, Azerbaycan, Ukrayna…): kritik iç gündem + Türkiye ile ilgili her şey.
   - **B kademesi ve think tank'ler**: yalnız Türkiye geçen başlıklar; site içi aramada "Turkey", "Türkiye", "Erdoğan" kullan.
   - **Premium**: Türkiye ve kapsam ülkeleri; analizler öncelikli.
3. Son taramadan bu yana yayımlananları al; önemsizleri atla (önem ölçeği `docs/KAPSAM_MODELI.md`, 1–5; 3 altı alınmaz).
4. Her kayıt için yalnız başlık, link, tarih ve **kendi cümlelerimizle** 2–3 cümle özet yaz; gövde kopyalanmaz,
   alıntı 15 kelimeyi aşmaz, özet 600 karakteri aşmaz.
5. Çıktıyı `data/premium/YYYY-MM-DD.json` olarak kaydet (biçim: `data/premium/README.md`) ve
   `disgundem chrome-import data/premium/YYYY-MM-DD.json` çalıştır.

## Sınırlar
- Giriş, CAPTCHA veya ödeme duvarı aşılmaz; editörün oturumunda açılmayan sayfa atlanır ve not edilir.
- Aynı başlık sunucudaki gnews yedeğinden de gelmiş olabilir; tekilleştirme başlık hash'iyle eler.
