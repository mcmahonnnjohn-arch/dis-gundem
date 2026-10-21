-- 0010: okur sitesi haritası için yer koordinatları (22 Ekim 2026)
-- places.geom bir geography sütunudur; REST'ten güvenle okunsun diye enlem/boylam düz sayı olarak sunulur.
-- security_invoker: RLS 'places' üzerinde işler (yalnız verified=true satırlar görünür).
create or replace view places_xy with (security_invoker = true) as
  select id, name_tr, country_id, kind, st_y(geom::geometry) as lat, st_x(geom::geometry) as lon
  from places;
