// Veri katmanı: Supabase (anon, RLS yalnız published satırları açar) ya da örnek veri.
import ornek from "../data/ornek.json";

export interface Kaynak { ad: string; ulke: string; dil: string; url: string; ozgun_baslik?: string }
export interface Yer { ad: string; lat: number; lon: number; birincil: boolean }
export interface Olay {
  id: string; baslik: string; ozet: string; bakis_farki: string | null; tarih: string | null;
  turkiye_mercegi: boolean; bolge: string; ulkeler: string[]; kaynaklar: Kaynak[];
  ulke_kodlari: string[]; birincil_ulke: string | null;
  olay_turu: string | null; turkiye_anlami: string | null; olay_tarihi: string | null;
  yerler: Yer[]; aktorler: { ad: string; tur: string }[];
}
export interface Analiz {
  id: string; baslik: string; yerel: string | null; kuresel: string | null; editor: string | null;
  yazar: string | null; tarih: string | null;
  kaynaklar: { yayin: string; baslik: string; yazar: string; tarih: string; url: string }[];
}
export interface Ulke { id: string; ad: string; bolge: string }
export interface Yayin {
  olaylar: Olay[]; ornek: boolean; bolgeler: string[]; analizler: Analiz[]; ulkeler: Record<string, Ulke>;
  haritaNotu: { baslik: string; govde: string; tarih: string } | null;
}

const URL = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;
const KEY = import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string | undefined;

async function rest<T>(yol: string): Promise<T> {
  const r = await fetch(`${URL}/rest/v1/${yol}`, { headers: { apikey: KEY!, Authorization: `Bearer ${KEY}` } });
  if (!r.ok) throw new Error(`Supabase ${r.status}: ${yol}`);
  return r.json() as Promise<T>;
}
/** Tablosu henüz yok / boş ise sayfa düşmesin (ör. migration uygulanmadı). */
async function restOpsiyonel<T>(yol: string, yedek: T): Promise<T> {
  try { return await rest<T>(yol); } catch { return yedek; }
}

// Bölge sırası: Yayın Kılavuzu / proje kararı (bölgesel kategorizasyon)
const SIRA = ["Levant & Irak", "Doğu Akdeniz", "Körfez & İran", "Kafkasya", "Asya", "Karadeniz & Rusya", "Avrupa", "Balkanlar", "Afrika"];

export const OLAY_TURU: Record<string, string> = {
  catisma: "Çatışma", saldiri: "Saldırı", diplomasi: "Diplomasi", anlasma: "Anlaşma", ekonomi: "Ekonomi", enerji: "Enerji",
  secim: "Seçim", protesto: "Protesto", askeri_hareket: "Askerî hareket", insani: "İnsani", yargi_guvenlik: "Yargı & güvenlik", siyasi: "Siyasi",
};

export function slug(s: string): string {
  return s.toLocaleLowerCase("tr").replace(/ç/g, "c").replace(/ğ/g, "g").replace(/ı/g, "i").replace(/ö/g, "o").replace(/ş/g, "s").replace(/ü/g, "u")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

async function yukle(): Promise<Yayin> {
  if (!(URL && KEY)) {
    const olaylar = (ornek as any[]).map((o) => ({
      ulke_kodlari: o.ulkeler.map(slug), birincil_ulke: o.ulkeler[0] ? slug(o.ulkeler[0]) : null,
      olay_turu: null, turkiye_anlami: null, olay_tarihi: o.tarih ?? null, yerler: [], aktorler: [], ...o,
    })) as Olay[];
    const ulkeler: Record<string, Ulke> = {};
    for (const o of olaylar) o.ulkeler.forEach((ad, i) => { ulkeler[slug(ad)] ??= { id: slug(ad), ad, bolge: o.bolge }; });
    return { olaylar, ornek: true, bolgeler: SIRA.filter((b) => olaylar.some((o) => o.bolge === b)), analizler: [], ulkeler, haritaNotu: null };
  }
  const [kumeler, ulkeSatir, yerler, kYer, aktorler, kAktor, analizSatir, notlar] = await Promise.all([
    rest<any[]>(
      "clusters?status=eq.published&merged_into=is.null&order=last_seen.desc&limit=200" +
      "&select=id,title_tr,summary_tr,bakis_farki,last_seen,event_at,event_type,turkey_stake,primary_country,countries," +
      "articles(id,title,url,lang,frame,is_turkey_related,source:sources(name,tier,country:countries(name,region:regions(name))))"
    ),
    rest<any[]>("countries?select=id,name,region:regions(name)"),
    restOpsiyonel<any[]>("places_xy?select=id,name_tr,lat,lon", []),
    restOpsiyonel<any[]>("cluster_places?select=cluster_id,place_id,is_primary", []),
    restOpsiyonel<any[]>("actors?select=id,name_tr,kind", []),
    restOpsiyonel<any[]>("cluster_actors?select=cluster_id,actor_id", []),
    restOpsiyonel<any[]>("analyses?status=eq.published&order=published_at.desc&select=id,title_tr,local_section,global_section,editor_section,sources,author,published_at", []),
    restOpsiyonel<any[]>("map_notes?status=eq.published&order=week_start.desc&limit=1&select=title_tr,body_md,week_start", []),
  ]);
  const ulkeler: Record<string, Ulke> = {};
  for (const u of ulkeSatir) ulkeler[u.id] = { id: u.id, ad: u.name, bolge: u.region?.name ?? "" };
  const yerMap = new Map(yerler.map((y) => [y.id, y]));
  const aktorMap = new Map(aktorler.map((a) => [a.id, a]));
  const olaylar: Olay[] = kumeler.map((k) => {
    const ar = (k.articles ?? []) as any[];
    const kaynaklar: Kaynak[] = ar.map((a) => ({
      ad: a.source?.name ?? "", ulke: a.source?.country?.name ?? "", dil: a.lang ?? "", url: a.url, ozgun_baslik: a.title,
    }));
    const bolge = ar.find((a) => a.source?.country?.region?.name)?.source.country.region.name ?? "";
    return {
      id: k.id, baslik: k.title_tr ?? "", ozet: k.summary_tr ?? "", bakis_farki: k.bakis_farki ?? null,
      tarih: k.last_seen ?? null,
      turkiye_mercegi: ar.some((a) => a.source?.tier === "B" || a.is_turkey_related === true),
      bolge, ulkeler: [...new Set(kaynaklar.map((s) => s.ulke).filter(Boolean))], kaynaklar,
      ulke_kodlari: (k.countries ?? []) as string[], birincil_ulke: k.primary_country ?? null,
      olay_turu: k.event_type ?? null, turkiye_anlami: k.turkey_stake ?? null, olay_tarihi: k.event_at ?? k.last_seen ?? null,
      yerler: kYer.filter((c) => c.cluster_id === k.id && yerMap.has(c.place_id))
        .map((c) => ({ ad: yerMap.get(c.place_id).name_tr, lat: yerMap.get(c.place_id).lat, lon: yerMap.get(c.place_id).lon, birincil: !!c.is_primary })),
      aktorler: kAktor.filter((c) => c.cluster_id === k.id && aktorMap.has(c.actor_id))
        .map((c) => ({ ad: aktorMap.get(c.actor_id).name_tr, tur: aktorMap.get(c.actor_id).kind })),
    } as Olay;
  }).filter((o) => o.baslik && o.ozet);
  const analizler: Analiz[] = analizSatir.map((a) => ({
    id: a.id, baslik: a.title_tr, yerel: a.local_section ?? null, kuresel: a.global_section ?? null, editor: a.editor_section ?? null,
    yazar: a.author ?? null, tarih: a.published_at ?? null,
    kaynaklar: ((a.sources ?? []) as any[]).map((s) => ({ yayin: s.outlet ?? "", baslik: s.title ?? "", yazar: s.author ?? "", tarih: s.date ?? "", url: s.url ?? "" })),
  }));
  const n = notlar[0];
  return {
    olaylar, ornek: false, bolgeler: SIRA.filter((b) => olaylar.some((o) => o.bolge === b)), analizler, ulkeler,
    haritaNotu: n ? { baslik: n.title_tr, govde: n.body_md, tarih: n.week_start } : null,
  };
}

let _onbellek: Promise<Yayin> | null = null;
/** Derleme sırasında tüm sayfalar aynı veriyi paylaşır (tek istek). */
export function yayinCek(): Promise<Yayin> { return (_onbellek ??= yukle()); }

/** Bir ülke masasına düşen olaylar: birincil ülke ya da kümedeki ülke etiketi. */
export function ulkeOlaylari(y: Yayin, id: string): Olay[] {
  return y.olaylar.filter((o) => o.birincil_ulke === id || o.ulke_kodlari.includes(id));
}
export function ulkeIdleri(y: Yayin): string[] {
  return Object.keys(y.ulkeler).filter((id) => ulkeOlaylari(y, id).length > 0);
}
