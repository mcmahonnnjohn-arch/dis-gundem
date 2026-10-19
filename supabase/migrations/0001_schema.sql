-- Dış Gündem — temel şema (v1, 19 Ekim 2026)
-- Ülke ve dosya (dossier) birinci sınıf varlıktır; bir haber birden fazla ülkeye ve dosyaya bağlanabilir.
-- Kaynak envanteri CSV'den seed edilir (pipeline: `disgundem seed`).

create extension if not exists "pgcrypto";
create extension if not exists "vector";

-- ---------------------------------------------------------------- Sözlükler
create table regions (
  id          text primary key,            -- 'levant-irak'
  name        text not null,               -- 'Levant & Irak'
  sort_order  int  not null default 100
);

create table countries (
  id          text primary key,            -- ISO-3166 alpha-2 veya 'eu', 'kktc', 'kuresel', 'mena' gibi özel kod
  name        text not null,
  region_id   text references regions(id),
  scope       char(1) check (scope in ('A','B','R','T','P')),  -- A=iç gündem+Türkiye, B=yalnız Türkiye'ye bakış
  is_group    boolean not null default false,                  -- 'Afrika (bölgesel)' gibi ülke olmayan etiketler
  langs       text[] not null default '{}'
);

create table dossiers (                     -- ülke-üstü konu dosyaları
  id          text primary key,            -- 'dogu-akdeniz', 'karadeniz', 'kurt-meselesi'
  name        text not null,
  description text
);

create table themes (
  id          text primary key,            -- 'diplomasi', 'guvenlik', 'enerji', ...
  name        text not null,
  description text
);

-- ---------------------------------------------------------------- Kaynaklar
create type source_tier   as enum ('A','B','R','T','P');
create type source_status as enum ('cekirdek','yedek','kontrol','pasif','cikarildi');
create type fetch_method  as enum ('rss','gnews','scrape','gmail','manual');

create table sources (
  id              text primary key,        -- 'K001'
  name            text not null,
  url             text not null,
  local_url       text,
  feed_url        text,
  tier            source_tier not null,
  region_id       text references regions(id),
  country_id      text references countries(id),
  kind            text,                    -- 'Think tank', 'Ana akım', 'Devlet ajansı', ...
  reliability     char(1) check (reliability in ('A','B','C')),
  role            text,                    -- CSV 'İçerik rolü'
  langs           text[] not null default '{}',
  method          fetch_method not null default 'manual',
  status          source_status not null default 'kontrol',
  is_think_tank   boolean generated always as (kind = 'Think tank') stored,
  perspective_only boolean not null default false,   -- propaganda/düşmanca kaynak: "bakış açısı" etiketiyle gösterilir
  lean_note       text,
  editor_note     text,
  verification    jsonb not null default '{}'::jsonb, -- PR #1'in doğrulama sütunları olduğu gibi
  scan_interval   interval not null default '1 hour', -- think tank: '1 week'
  last_fetched_at timestamptz,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index on sources (status, method);
create index on sources (country_id);

-- Hattın kendisinin ölçtüğü kayan hacim; budama buradan yapılır.
create table source_metrics (
  source_id        text references sources(id) on delete cascade,
  window_start     date not null,
  window_end       date not null,
  fetched          int not null default 0,   -- pencere içinde görülen kayıt
  turkey_related   int not null default 0,   -- LLM/terim: Türkiye ile ilgili
  domestic_major   int not null default 0,   -- A kapsamı: önem >= 3
  published        int not null default 0,   -- editör onayından geçen
  computed_at      timestamptz not null default now(),
  primary key (source_id, window_start, window_end)
);

-- ---------------------------------------------------------------- İçerik
create type article_status as enum ('fetched','classified','queued','approved','rejected','published');

create table articles (
  id              uuid primary key default gen_random_uuid(),
  source_id       text not null references sources(id),
  url             text not null,
  canonical_url   text,
  title           text not null,
  lang            text,
  published_at    timestamptz,
  fetched_at      timestamptz not null default now(),
  excerpt         text,                    -- kaynaktan gelen kısa özet/lead (premium için boş)
  -- sınıflandırma (LLM)
  is_turkey_related boolean,
  importance      smallint check (importance between 1 and 5),  -- A kapsamı iç gündem ölçütü
  frame           text check (frame in ('olumlu','olumsuz','notr','karisik')), -- Türkiye çerçevelemesi (B kapsamı)
  summary_tr      text,                    -- 2-3 cümle, kendi cümlelerimizle
  summary_en      text,
  local_view_note text,                    -- "yerel medya nasıl gördü"
  classification  jsonb,                   -- modelin ham çıktısı (model, prompt sürümü, güven)
  cluster_id      uuid,
  status          article_status not null default 'fetched',
  embedding       vector(1024),
  title_hash      text generated always as (md5(lower(title))) stored,
  unique (source_id, url)
);
create index on articles (status);
create index on articles (published_at desc);
create index on articles (cluster_id);
create index on articles (title_hash);

create table article_countries (
  article_id  uuid references articles(id) on delete cascade,
  country_id  text references countries(id),
  primary key (article_id, country_id)
);
create table article_dossiers (
  article_id  uuid references articles(id) on delete cascade,
  dossier_id  text references dossiers(id),
  primary key (article_id, dossier_id)
);
create table article_themes (
  article_id  uuid references articles(id) on delete cascade,
  theme_id    text references themes(id),
  primary key (article_id, theme_id)
);

-- Aynı olayı anlatan haberler → "gelişme kümesi"
create table clusters (
  id            uuid primary key default gen_random_uuid(),
  title_tr      text,
  summary_tr    text,
  first_seen    timestamptz,
  last_seen     timestamptz,
  article_count int not null default 0,
  countries     text[] not null default '{}',
  status        article_status not null default 'fetched',
  created_at    timestamptz not null default now()
);
alter table articles add constraint articles_cluster_fk foreign key (cluster_id) references clusters(id);

-- "Analiz" içerik tipi: yerel gelişme → küresel okuma (premium, atıflı) → editörün süzgeci → kaynaklar
create table analyses (
  id             uuid primary key default gen_random_uuid(),
  cluster_id     uuid references clusters(id),
  title_tr       text not null,
  local_section  text,     -- yerel gelişme (LLM taslağı)
  global_section text,     -- küresel okuma; premium kaynaklar kendi cümlelerimizle, atıflı
  editor_section text,     -- editörün süzgeci (yalnız editör yazar)
  sources        jsonb not null default '[]'::jsonb,  -- [{title, outlet, url, date}]
  status         article_status not null default 'queued',
  author         text,
  published_at   timestamptz,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

-- Çalışma günlüğü
create table fetch_runs (
  id          uuid primary key default gen_random_uuid(),
  source_id   text references sources(id),
  started_at  timestamptz not null default now(),
  finished_at timestamptz,
  ok          boolean,
  fetched     int default 0,
  new_items   int default 0,
  error       text
);
create index on fetch_runs (source_id, started_at desc);

-- updated_at tetikleyicisi
create or replace function set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
create trigger sources_updated  before update on sources  for each row execute function set_updated_at();
create trigger analyses_updated before update on analyses for each row execute function set_updated_at();

-- ---------------------------------------------------------------- Görünümler
-- Editör kuyruğu: sınıflandırılmış, onay bekleyen
create view editorial_queue as
select a.id, a.title, a.summary_tr, a.importance, a.frame, a.is_turkey_related, a.published_at,
       s.name as source_name, s.tier, s.reliability, s.perspective_only,
       array(select country_id from article_countries ac where ac.article_id = a.id) as countries
from articles a join sources s on s.id = a.source_id
where a.status = 'queued'
order by a.importance desc nulls last, a.published_at desc;

-- Kaynak sağlığı: 7 gündür boş dönenler, hata oranı
create view source_health as
select s.id, s.name, s.status, s.method, s.last_fetched_at,
       (select count(*) from fetch_runs r where r.source_id = s.id and r.started_at > now() - interval '7 days' and r.ok = false) as errors_7d,
       (select coalesce(sum(new_items),0) from fetch_runs r where r.source_id = s.id and r.started_at > now() - interval '7 days') as new_items_7d
from sources s;

-- RLS: yayın yüzeyi yalnız yayınlanmış içeriği okur (anon); yazma servis anahtarıyla.
alter table articles enable row level security;
alter table clusters enable row level security;
alter table analyses enable row level security;
create policy "public read published articles" on articles for select using (status = 'published');
create policy "public read published clusters" on clusters for select using (status = 'published');
create policy "public read published analyses" on analyses for select using (status = 'published');
alter table sources enable row level security;
create policy "public read sources" on sources for select using (true);
