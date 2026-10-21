-- 0009: yerel editör onay görünümü (21 Ekim 2026) — düzeltme günlüğü (Yayın Kılavuzu §9)
-- Editörün kuyrukta yaptığı her düzeltme kaydedilir; aynı türden düzeltme iki kez tekrarlanırsa
-- sözlüğe ya da kılavuza eklenir. Yazma yalnız servis anahtarıyla (RLS açık, politika yok → anon göremez).
create table if not exists editor_corrections (
  id          uuid primary key default gen_random_uuid(),
  cluster_id  uuid not null references clusters(id) on delete cascade,
  alan        text not null check (alan in ('title_tr', 'summary_tr', 'bakis_farki')),
  onceki      text,
  yeni        text,
  created_at  timestamptz not null default now()
);
create index if not exists editor_corrections_cluster_idx on editor_corrections (cluster_id, created_at desc);
alter table editor_corrections enable row level security;
