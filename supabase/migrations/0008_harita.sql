-- 0008: Jeopolitik Harita (21 Ekim 2026 taslak)
-- İlke: harita ayrı bir veri hattı değil; mevcut clusters (olaylar) konumlandırılarak haritaya düşer.
-- Statik katmanlar (kontrol bölgeleri, üsler, boru hatları) elle derlenir ve tarihlidir; zaman kaydırıcısı bunları süzer.
-- Sıcak noktalar mevcut dossiers tablosunun genişletilmesidir (ayrı tablo yok).
-- Yer ve aktör sözlükleri data/sozluk/yerler_*.csv ve aktorler.csv'den `disgundem seed` ile yüklenir;
-- olaylara bağlama `disgundem harita` adımıdır (prompts/harita_v1.md).

create extension if not exists postgis;

-- ---------------------------------------------------------------- Yer sözlüğü (gazetteer)
-- LLM serbest yer adı üretir ("Tel Rıfat", "Tal Rifaat"); burada tek kimliğe bağlanır.
-- varliklar.csv mantığıyla elle doğrulanır; bulunamayan adlar place_unresolved'a düşer.
create table places (
  id          text primary key,                 -- 'sy-tel-rifat'
  name_tr     text not null,                    -- yayın adı: 'Tel Rıfat'
  aliases     text[] not null default '{}',     -- 'Tal Rifaat', 'تل رفعت'
  country_id  text not null references countries(id),
  kind        text not null check (kind in ('sehir','ilce','bolge','sinir_kapisi','liman','us','tesis','deniz_alani','ulke')),
  geom        geography(Point, 4326) not null,
  precision   text not null default 'sehir' check (precision in ('nokta','sehir','bolge','ulke')),
  verified    boolean not null default false,
  source_url  text
);
create index places_geom_idx on places using gist (geom);
create index places_aliases_idx on places using gin (aliases);

-- ---------------------------------------------------------------- Olayların haritaya düşmesi
-- Her küme (olay) 0..n yere bağlanır; biri birincil konumdur (işaretçi oraya konur).
create type event_type as enum ('catisma','saldiri','diplomasi','anlasma','ekonomi','enerji','secim','protesto','askeri_hareket','insani');

alter table clusters add column if not exists event_type  event_type;
alter table clusters add column if not exists turkey_stake text;   -- popup'taki "Türkiye için anlamı" (tek cümle)
alter table clusters add column if not exists event_at    timestamptz;   -- olayın gerçekleştiği an (first_seen yayın anıdır)
alter table clusters add column if not exists map_meta    jsonb;         -- harita çıkarımının ham çıktısı (prompt sürümü, çözülemeyen adlar)
-- İşaretçi boyutu mevcut clusters.importance'tan (huni ölçeği 1-5) türetilir: 3→1, 4→2, 5→3 (map_events.marker).

create table cluster_places (
  cluster_id  uuid references clusters(id) on delete cascade,
  place_id    text references places(id),
  is_primary  boolean not null default false,
  primary key (cluster_id, place_id)
);
create unique index cluster_places_one_primary on cluster_places (cluster_id) where is_primary;

-- Sözlükte bulunamayan yer adları: editör eşler veya yeni yer ekler.
create table place_unresolved (
  raw_name    text primary key,
  country_id  text references countries(id),
  seen_count  int not null default 1,
  last_seen   timestamptz not null default now(),
  resolved_to text references places(id)
);

-- Olayda rol alan aktörler (Rakipler & Ortaklar katmanı ve aktör filtresi için)
create table actors (
  id          text primary key,                 -- 'ru', 'ir', 'il', 'deas', 'eski-sdg'
  name_tr     text not null,
  kind        text not null check (kind in ('devlet','silahli_grup','orgut','sirket','ittifak')),
  country_id  text references countries(id),
  aliases     text[] not null default '{}',
  active      boolean not null default true    -- feshedilmiş yapılar (eski SDG, HTŞ) geçmiş olaylar için kalır
);
create table cluster_actors (
  cluster_id  uuid references clusters(id) on delete cascade,
  actor_id    text references actors(id),
  role        text check (role in ('fail','hedef','arabulucu','taraf')),
  primary key (cluster_id, actor_id)
);

-- ---------------------------------------------------------------- Statik katmanlar
create type map_layer as enum ('turkiye_varligi','kontrol_alani','enerji_altyapi','rakip_ortak');

create table map_features (
  id           uuid primary key default gen_random_uuid(),
  layer        map_layer not null,
  subtype      text not null,                   -- 'us','tika_projesi','muteahhitlik','boru_hatti','koridor','ruhsat_sahasi','meb_iddiasi','kontrol_bolgesi'
  name_tr      text not null,
  actor_id     text references actors(id),      -- kontrol bölgesinin sahibi, üssün sahibi
  country_id   text references countries(id),
  geom         geography(Geometry, 4326) not null,   -- nokta, çizgi (boru hattı) veya poligon (kontrol bölgesi)
  description  text,
  status       text check (status in ('aktif','insa','planlanan','tartismali','sona_erdi')),
  valid_from   date not null,                   -- zaman kaydırıcısı: bu tarihte haritada mı?
  valid_to     date,                            -- null = hâlâ geçerli
  source_url   text not null,                   -- her statik özellik kaynaklı (Kaynak & Yöntem sayfası buradan)
  confidence   char(1) not null default 'B' check (confidence in ('A','B','C')),
  updated_by   text,
  updated_at   timestamptz not null default now()
);
create index map_features_geom_idx  on map_features using gist (geom);
create index map_features_layer_idx on map_features (layer, valid_from, valid_to);
create trigger map_features_updated before update on map_features for each row execute function set_updated_at();

-- ---------------------------------------------------------------- Sıcak noktalar (dossiers genişlemesi)
alter table dossiers add column if not exists is_hotspot   boolean not null default false;
alter table dossiers add column if not exists area         geography(Polygon, 4326);   -- haritadaki vurgulu alan; olaylar buna düşerse otomatik etiketlenir
alter table dossiers add column if not exists center       geography(Point, 4326);
alter table dossiers add column if not exists default_zoom smallint;
alter table dossiers add column if not exists sort_order   int not null default 100;

-- Dosya sayfasının sekmeleri: Arka Plan, Aktörler, Türkiye'nin Çıkarı, Senaryolar, İzlenecek Göstergeler
create table dossier_sections (
  dossier_id  text references dossiers(id) on delete cascade,
  section     text check (section in ('arka_plan','turkiye_cikari','senaryolar','gostergeler')),
  body_md     text not null,
  updated_at  timestamptz not null default now(),
  primary key (dossier_id, section)
);
create table dossier_actors (                  -- Aktörler sekmesi: her aktörün güncel tutumu
  dossier_id  text references dossiers(id) on delete cascade,
  actor_id    text references actors(id),
  posture_tr  text not null,                   -- tek satır
  updated_at  timestamptz not null default now(),
  primary key (dossier_id, actor_id)
);
-- Zaman Çizelgesi sekmesi ayrı tablo istemez: article_dossiers + clusters'tan türetilir; editör "kilometre taşı" işaretler.
alter table clusters add column if not exists is_milestone boolean not null default false;

-- ---------------------------------------------------------------- Harita Notu (haftalık editoryal)
create table map_notes (
  id           uuid primary key default gen_random_uuid(),
  week_start   date not null unique,
  title_tr     text not null,
  body_md      text not null,
  author       text,
  cluster_ids  uuid[] not null default '{}',   -- notta anılan olaylar haritada vurgulanır
  status       article_status not null default 'queued',
  published_at timestamptz
);

-- ---------------------------------------------------------------- Görünümler (yayın yüzeyi bunları okur)
-- Olay katmanı: yayınlanmış, birleşmemiş kümeler, birincil konumuyla
create or replace view map_events as
select c.id, c.title_tr, c.summary_tr, c.turkey_stake, c.event_type, c.importance,
       least(greatest(coalesce(c.importance, 3) - 2, 1), 3) as marker,
       coalesce(c.event_at, c.first_seen) as event_at, c.primary_country, c.is_milestone,
       p.id as place_id, p.name_tr as place_name, p.precision, p.geom,
       array(select dossier_id from article_dossiers ad join articles a on a.id = ad.article_id
             where a.cluster_id = c.id group by dossier_id) as dossiers,
       array(select actor_id from cluster_actors ca where ca.cluster_id = c.id) as actors
from clusters c
join cluster_places cp on cp.cluster_id = c.id and cp.is_primary
join places p on p.id = cp.place_id
where c.status = 'published' and c.merged_into is null;

-- Sıcak nokta özeti: sağ sütundaki trend okları ve sparkline
create or replace view hotspot_trend as
select d.id, d.name,
       count(*) filter (where e.event_at > now() - interval '7 days')                                         as events_7d,
       count(*) filter (where e.event_at between now() - interval '14 days' and now() - interval '7 days')    as events_prev_7d,
       coalesce(sum(e.marker) filter (where e.event_at > now() - interval '7 days'), 0)                    as weight_7d
from dossiers d
left join map_events e on d.id = any(e.dossiers)
where d.is_hotspot
group by d.id, d.name;

-- Algı katmanı: ülke başına haftalık Türkiye çerçevelemesi (articles.frame zaten var)
create or replace view perception_weekly as
select s.country_id,
       date_trunc('week', a.published_at)::date as week_start,
       count(*)                                          as n,
       count(*) filter (where a.frame = 'olumlu')        as olumlu,
       count(*) filter (where a.frame = 'notr')          as notr,
       count(*) filter (where a.frame = 'olumsuz')       as olumsuz,
       count(*) filter (where a.frame = 'karisik')       as karisik,
       round(avg(case a.frame when 'olumlu' then 1 when 'olumsuz' then -1 else 0 end)::numeric, 2) as ton_skoru
from articles a join sources s on s.id = a.source_id
where a.is_turkey_related and a.frame is not null and a.status in ('approved','published')
group by 1, 2;

-- RLS
alter table places enable row level security;        create policy "public read places"       on places        for select using (verified);
alter table map_features enable row level security;  create policy "public read features"     on map_features  for select using (true);
alter table map_notes enable row level security;     create policy "public read map notes"    on map_notes     for select using (status = 'published');
alter table actors enable row level security;        create policy "public read actors"       on actors        for select using (true);
alter table dossier_sections enable row level security; create policy "public read sections"  on dossier_sections for select using (true);
alter table dossier_actors enable row level security;   create policy "public read d_actors"  on dossier_actors   for select using (true);
alter table cluster_places enable row level security;   create policy "public read c_places"  on cluster_places   for select using (true);
alter table cluster_actors enable row level security;   create policy "public read c_actors"  on cluster_actors   for select using (true);
