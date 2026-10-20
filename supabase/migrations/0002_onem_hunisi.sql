-- Önem hunisi (20 Ekim 2026): eşik altı kayıtlar saklanmaz, yalnız hash'i tutulur.

-- Görülmüş ama elenmiş başlıklar: tekrar LLM'e gitmesin diye. 14 günden eskiler silinebilir.
create table seen_items (
  source_id   text not null references sources(id) on delete cascade,
  url_hash    text not null,
  title_hash  text not null,
  importance  smallint,
  seen_at     timestamptz not null default now(),
  primary key (source_id, url_hash)
);
create index on seen_items (title_hash);
create index on seen_items (seen_at);

-- Önem 3: saklanır, kuyruğa girmez; ülke sayfası "diğer gelişmeler" ve analiz hammaddesi.
alter type article_status add value if not exists 'pool' after 'classified';

alter table clusters add column if not exists importance smallint;
alter table articles add column if not exists triage jsonb;   -- ön eleme çıktısı (model, prompt, ham puan)

-- Kuyruk artık küme bazlı: her olay bir kez görünür.
-- Sütun yapısı 0001'dekinden farklı; `create or replace` sütun düşüremediği için önce kaldırılır.
drop view if exists editorial_queue;
create view editorial_queue as
select c.id as cluster_id, c.importance, c.title_tr, c.article_count, c.countries, c.first_seen, c.last_seen,
       (select json_agg(json_build_object('id', a.id, 'title', a.title, 'url', a.url, 'source', s.name,
                                          'reliability', s.reliability, 'perspective_only', s.perspective_only,
                                          'summary_tr', a.summary_tr) order by s.reliability, a.published_at)
          from articles a join sources s on s.id = a.source_id where a.cluster_id = c.id) as articles
from clusters c
where c.status = 'queued'
order by c.importance desc, c.last_seen desc;

-- Bugün kuyruğa giren küme sayısı (ülke başına tavan için)
create or replace view queue_today as
select unnest(countries) as country_id, count(*) as n
from clusters
where status in ('queued','approved','published') and created_at >= date_trunc('day', now() at time zone 'Europe/Istanbul')
group by 1;

-- Temizlik: 14 günden eski seen_items
create or replace function prune_seen_items() returns void language sql as $$
  delete from seen_items where seen_at < now() - interval '14 days';
$$;
