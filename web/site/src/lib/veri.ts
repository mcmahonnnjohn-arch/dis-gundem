// Veri katmanı: Supabase (anon, RLS yalnız published satırları açar) ya da örnek veri.
import ornek from "../data/ornek.json";

export interface Kaynak { ad: string; ulke: string; dil: string; url: string; ozgun_baslik?: string }
export interface Olay {
  id: string; baslik: string; ozet: string; bakis_farki: string | null; tarih: string | null;
  turkiye_mercegi: boolean; bolge: string; ulkeler: string[]; kaynaklar: Kaynak[];
}
export interface Yayin { olaylar: Olay[]; ornek: boolean; bolgeler: string[] }

const URL = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;
const KEY = import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string | undefined;

async function rest<T>(yol: string): Promise<T> {
  const r = await fetch(`${URL}/rest/v1/${yol}`, { headers: { apikey: KEY!, Authorization: `Bearer ${KEY}` } });
  if (!r.ok) throw new Error(`Supabase ${r.status}: ${yol}`);
  return r.json() as Promise<T>;
}

// Bölge sırası: Yayın Kılavuzu / proje kararı (bölgesel kategorizasyon)
const SIRA = ["Levant & Irak", "Doğu Akdeniz", "Körfez & İran", "Kafkasya", "Asya", "Karadeniz & Rusya", "Avrupa", "Balkanlar", "Afrika"];

export async function yayinCek(): Promise<Yayin> {
  let olaylar: Olay[]; let isOrnek = false;
  if (URL && KEY) {
    const kumeler = await rest<any[]>(
      "clusters?status=eq.published&merged_into=is.null&order=last_seen.desc&limit=80" +
      "&select=id,title_tr,summary_tr,bakis_farki,last_seen,countries," +
      "articles(id,title,url,lang,frame,is_turkey_related,source:sources(name,tier,country:countries(name,region:regions(name))))"
    );
    olaylar = kumeler.map((k) => {
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
      } as Olay;
    }).filter((o) => o.baslik && o.ozet);
  } else {
    olaylar = ornek as Olay[]; isOrnek = true;
  }
  const bolgeler = SIRA.filter((b) => olaylar.some((o) => o.bolge === b));
  return { olaylar, ornek: isOrnek, bolgeler };
}
