-- 0006: özet test seti ölçümleri (disgundem eval). Makale metni saklanmaz; yalnız üretilen özet ve puanlar.
create table if not exists eval_runs (
  id         uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  etiket     text,
  meta       jsonb not null,      -- prompt, denetim, hakem, model sürümleri
  ozet       jsonb not null,      -- set geneli ve dil kırılımı oranlar/puanlar
  sonuclar   jsonb not null       -- haber başına özet, uyarılar, kural ve hakem puanları
);
alter table eval_runs enable row level security;   -- yalnız service_role
create index if not exists eval_runs_created_idx on eval_runs (created_at desc);
