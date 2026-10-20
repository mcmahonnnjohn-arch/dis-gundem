-- Ülke kotası yalnız birincil ülkeyi sayar (20 Ekim 2026 editör kararı).
-- Birincil ülke: haberin asıl konusu olan ülke (sınıflandırmada ülke listesinin ilk kodu).
-- Birincil ülke Türkiye ise ülke kotası uygulanmaz; yalnız günlük toplam tavan geçerlidir.

alter table clusters add column if not exists primary_country text references countries(id);

drop view if exists queue_today;
create view queue_today as
select primary_country as country_id, count(*) as n
from clusters
where status in ('queued','approved','published')
  and primary_country is not null and primary_country <> 'tr'
  and created_at >= date_trunc('day', now() at time zone 'Europe/Istanbul')
group by 1;
