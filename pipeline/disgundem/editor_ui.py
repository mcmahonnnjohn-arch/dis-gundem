"""Editör görünümü: tek dosyalık sayfa. İç bilgi (puan, uyarı, üye özetleri) yalnız burada ve varsayılan kapalıdır."""

SAYFA = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>Dış Gündem · Editör</title>
<style>
:root{--zemin:#fcf9f8;--yuzey:#fff;--metin:#1c1b1b;--ikincil:#564242;--cizgi:#dcc0c0;--vurgu:#5b0617;--onay:#1b5e3b;--uyari:#ba1a1a;--alan:#f6f3f2}
@media(prefers-color-scheme:dark){:root{--zemin:#141313;--yuzey:#1c1b1b;--metin:#ece8e7;--ikincil:#c9bcbc;--cizgi:#4a3d3e;--vurgu:#ffb3b5;--onay:#7ddba3;--uyari:#ffb4ab;--alan:#242222}}
*{box-sizing:border-box}body{margin:0;background:var(--zemin);color:var(--metin);font:16px/1.55 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--zemin);border-bottom:1px solid var(--cizgi);padding:.75rem 1rem;z-index:3;display:flex;gap:1rem;align-items:baseline;flex-wrap:wrap}
header h1{margin:0;font:700 1.1rem Georgia,serif;color:var(--vurgu)}header span{color:var(--ikincil);font-size:.9rem}
.demo{background:var(--alan);border-bottom:1px solid var(--cizgi);text-align:center;font-size:.85rem;color:var(--ikincil);padding:.4rem}
main{max-width:56rem;margin:0 auto;padding:1rem}
.kume{background:var(--yuzey);border:1px solid var(--cizgi);border-radius:6px;padding:1.25rem;margin:0 0 1.5rem}
.kunye{font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ikincil);margin:0 0 .75rem}
label{display:block;font-size:.8rem;font-weight:600;color:var(--ikincil);margin:.9rem 0 .25rem}
input,textarea{width:100%;font:inherit;color:inherit;background:var(--alan);border:1px solid var(--cizgi);border-radius:4px;padding:.55rem .7rem}
input.b{font:700 1.15rem Georgia,serif}textarea{line-height:1.6;resize:vertical}
.say{float:right;font-weight:400}.say.asim{color:var(--uyari);font-weight:600}
ul.k{list-style:none;margin:1rem 0 0;padding:0;font-size:.9rem;color:var(--ikincil)}ul.k li{padding:.2rem 0}ul.k a{color:inherit}
details{margin-top:1rem;font-size:.9rem;color:var(--ikincil)}summary{cursor:pointer}
details .m{border-top:1px solid var(--cizgi);padding:.6rem 0}.rozet{display:inline-block;border:1px solid var(--uyari);color:var(--uyari);border-radius:3px;padding:0 .4rem;font-size:.75rem;margin-right:.3rem}
.eylem{display:flex;gap:.6rem;margin-top:1.25rem;flex-wrap:wrap;align-items:center}
button{font:600 .9rem system-ui;padding:.6rem 1.1rem;border-radius:4px;border:1px solid var(--cizgi);background:transparent;color:var(--metin);cursor:pointer}
button.ana{background:var(--onay);border-color:var(--onay);color:#fff}button.red{color:var(--uyari);border-color:var(--uyari);margin-left:auto}
button:disabled{opacity:.5;cursor:wait}.ileti{font-size:.85rem;color:var(--uyari)}
.bos{text-align:center;color:var(--ikincil);padding:3rem 0}
</style></head><body data-token="__TOKEN__" data-demo="__DEMO__">
<header><h1>DIŞ GÜNDEM · Editör</h1><span id="sayac">Yükleniyor…</span></header>
<div class="demo" id="demo" hidden>Demo: bellek içi örnek kuyruk; hiçbir şey veritabanına yazılmaz.</div>
<main id="liste"></main>
<script>
const T=document.body.dataset.token;
const el=(t,o={},...c)=>{const e=document.createElement(t);for(const[k,v]of Object.entries(o)){if(k==="class")e.className=v;else if(k==="text")e.textContent=v;else e.setAttribute(k,v)}c.flat().forEach(x=>e.append(x));return e};
const guvenli=u=>/^https?:\/\//i.test(u||"")?u:"#";
const LIM={title_tr:160,summary_tr:600,bakis_farki:400};
async function api(yol,gov){const r=await fetch(yol,{method:gov?"POST":"GET",headers:{"X-Editor-Token":T,"Content-Type":"application/json"},body:gov?JSON.stringify(gov):undefined});
 const j=await r.json().catch(()=>({hata:"Geçersiz yanıt"}));if(!r.ok)throw new Error(j.hata||r.status);return j}
function alan(ad,etiket,deger,satir){
 const g=satir?el("input",{class:"b",type:"text"}):el("textarea",{rows:ad==="summary_tr"?5:3});g.value=deger||"";g.dataset.alan=ad;
 const s=el("span",{class:"say"});const hesap=()=>{const n=g.value.trim().length;s.textContent=n+"/"+LIM[ad];s.classList.toggle("asim",n>LIM[ad])};g.addEventListener("input",hesap);hesap();
 return el("div",{},el("label",{},etiket,s),g)}
function kart(k){
 const kunye=el("p",{class:"kunye",text:[ (k.countries||[]).join(", "), k.article_count+" haber" ].filter(Boolean).join(" · ")});
 const ilet=el("span",{class:"ileti"});
 const kaynaklar=el("ul",{class:"k"},(k.makaleler||[]).map(a=>el("li",{},el("a",{href:guvenli(a.url),target:"_blank",rel:"noopener noreferrer",text:a.kaynak_adi||a.source_id}),
   " · "+(a.kaynak_ulke||"")+" · "+(a.lang||""),a.title?el("div",{text:a.title,dir:"auto",style:"font-size:.8rem"}):"")));
 const uy=(k.makaleler||[]).flatMap(a=>a.uyarilar||[]);
 const detay=el("details",{},el("summary",{text:"Ayrıntılar"+(uy.length?" ("+uy.length+" uyarı)":"")}),
   el("div",{class:"m",text:"Önem: "+(k.importance??"—")+" · köken: "+(k.origin||"—")}),
   (k.makaleler||[]).map(a=>el("div",{class:"m"},(a.uyarilar||[]).map(u=>el("span",{class:"rozet",text:u})),
     el("div",{text:(a.kaynak_adi||"")+": "+(a.summary_tr||"(özet yok)")}),a.frame?el("div",{text:"Türkiye çerçevesi: "+a.frame}):"")));
 const kutu=el("section",{class:"kume"},kunye,alan("title_tr","Olay başlığı",k.title_tr,true),alan("summary_tr","Özet (2–3 cümle)",k.summary_tr),
   alan("bakis_farki","Bakış farkı (kaynaklar olayı farklı çerçeveliyorsa; yoksa boş bırak)",k.bakis_farki),kaynaklar,detay);
 const topla=()=>{const o={};kutu.querySelectorAll("[data-alan]").forEach(g=>o[g.dataset.alan]=g.value);return o};
 const dugmeler=[];
 const calistir=async(eylem,onay)=>{if(onay&&!confirm(onay))return;dugmeler.forEach(d=>d.disabled=true);ilet.textContent="";
   try{await api("/api/kume/"+k.id,{eylem,alanlar:eylem==="reddet"?undefined:topla()});
     if(eylem==="kaydet"){ilet.style.color="var(--onay)";ilet.textContent="Kaydedildi";dugmeler.forEach(d=>d.disabled=false)}
     else{kutu.remove();sayac()}}catch(e){ilet.style.color="var(--uyari)";ilet.textContent=e.message;dugmeler.forEach(d=>d.disabled=false)}};
 const y=el("button",{class:"ana",text:"Yayınla"}),s=el("button",{text:"Kaydet"}),r=el("button",{class:"red",text:"Reddet"});
 y.onclick=()=>calistir("yayinla");s.onclick=()=>calistir("kaydet");r.onclick=()=>calistir("reddet","Bu olay reddedilsin mi?");
 dugmeler.push(y,s,r);kutu.append(el("div",{class:"eylem"},y,s,ilet,r));return kutu}
function sayac(){const n=document.querySelectorAll(".kume").length;document.getElementById("sayac").textContent=n?n+" olay onay bekliyor":"";
 if(!n&&!document.querySelector(".bos"))document.getElementById("liste").append(el("p",{class:"bos",text:"Onay bekleyen olay yok."}))}
(async()=>{if(document.body.dataset.demo==="1")document.getElementById("demo").hidden=false;
 try{const j=await api("/api/kuyruk");const L=document.getElementById("liste");j.kumeler.forEach(k=>L.append(kart(k)));sayac()}
 catch(e){document.getElementById("sayac").textContent="Hata: "+e.message}})();
</script></body></html>
"""
