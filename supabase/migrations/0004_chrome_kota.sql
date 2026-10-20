-- Chrome oturumu kayıtları için ayrı kuyruk kotası (20 Ekim 2026 editör kararı: "ayrı kota, bu kaynaklar öncelikli").
-- clusters.origin: 'server' (zamanlanmış toplama) | 'chrome' (editörün Claude in Chrome oturumu, chrome-import).
-- Her köken kendi günlük tavanını kullanır; biri diğerinin kotasını tüketmez.

alter table clusters add column if not exists origin text not null default 'server'
  check (origin in ('server', 'chrome'));

update clusters set origin = 'chrome'
where id in (select cluster_id from articles where classification->>'model' = 'editor-chrome' and cluster_id is not null);

-- Önceki görünüm birincil ülkesi 'tr' olan kümeleri hiç saymıyordu; toplam tavan eksik sayılıyordu.
-- Artık her (köken, birincil ülke) satırı döner; ülke kotası 'tr' dışı satırlardan, toplam tümünden hesaplanır.
drop view if exists queue_today;
create view queue_today as
select origin, primary_country as country_id, count(*) as n
from clusters
where status in ('queued','approved','published')
  and created_at >= date_trunc('day', now() at time zone 'Europe/Istanbul')
group by 1, 2;
