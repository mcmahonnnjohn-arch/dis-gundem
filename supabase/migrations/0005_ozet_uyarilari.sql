-- 0005: özet uyarı etiketleri (Yayın Kılavuzu §8) — editör kartında filtrelenir.
-- metin_yok · sozlukte_yok · denetim · tek_kaynak · dusuk_guven
alter table articles add column if not exists uyarilar text[] not null default '{}';
create index if not exists articles_uyarilar_idx on articles using gin (uyarilar);
