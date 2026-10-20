-- 0007: aynı olayın haberleri tek kartta (21 Ekim 2026 editör kararı)
alter table clusters add column if not exists merged_into uuid references clusters(id);  -- birleşen küme → hedef
alter table clusters add column if not exists bakis_farki text;   -- kaynaklar olayı farklı çerçeveliyorsa kim nasıl
create index if not exists clusters_merged_into_idx on clusters (merged_into);
