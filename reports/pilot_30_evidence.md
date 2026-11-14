# Pilot 30 — Kaynak bazında kanıt

_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._


**Önemli sınırlama (RT-001):** Doğrulayıcı `observed_at` değerleri toplu yazım zamanıdır (kanıt kayıtlarında `observed_at_precision=batch_write_time`). Tazelik 45 günlük eşik için günler düzeyinde doğrudur (hepsi 2026-11-14/15) ama sayfa-bazlı erişim saati değildir. Kırmızı takım 26 PASS'i yeniden çekip 17 'evet', 8 'kısmi', 1 'hayır' buldu; kısmi/hayır olanlar PASS'ten UNKNOWN'a indirildi.

## K001 — Enab Baladi
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Root domain fetch failed; English subdomain accessible. Donation appeal, no paywall seen.
- **identity**: PASS
  - kanıt: https://english.enabbaladi.net/about-us/ (gözlem: About page states it was established 2011 by citizen journalists from Daraya, calls itself an independent Syrian nonprofit 501(c)(3) media organization, names Editor in Chief Jawad Sharbaji.)
- **canonical_url**: UNKNOWN
  - kanıt: https://www.enabbaladi.net (gözlem: Starting URL https://www.enabbaladi.net failed to fetch (client_error). English edition at english.enabbaladi.net fetched successfully.)
- **activity**: PASS
  - kanıt: https://english.enabbaladi.net/ (gözlem: English edition listing showed items dated Monday 9 November and Saturday 7 November (e.g. Aleppo Airport bus service, Hama grain authority).)
- **originality**: UNKNOWN
  - kanıt: https://english.enabbaladi.net/ (gözlem: No dated original Enab Baladi report inside the window was fetched. Search surfaced 2026 English items (Jan 2026 Aleppo Ashrafieh, July 2026 SNHR figures) but these were not opened; the SNHR item relays another body's data.)
- **provenance**: UNKNOWN
  - kanıt: https://english.enabbaladi.net/ (gözlem: Listed items mix apparent official ministry statements, UN reports and local reporting; no article opened to establish upstream.)
- **ownership**: UNKNOWN
  - kanıt: https://english.enabbaladi.net/about-us/ (gözlem: About page names partners (National Endowment for Democracy, Internews, Free Press Unlimited) without a funding breakdown; the only explicit funding attribution concerns a separate alliance (funded by Free Press Unlimited).)
- **perspective**: UNKNOWN
  - kanıt: https://english.enabbaladi.net/about-us/ (gözlem: Self-described mission: independent public-interest reporting; origin among anti-Assad Daraya activists; states it promoted peaceful resistance.)
- Özgün çalışma adayı (DOĞRULANMADI): https://english.enabbaladi.net/archives/2026/11/damascus-sdf-integration-due-by-year-end-what-remains/ (2026-11 (day UNKNOWN))
- Özgün çalışma adayı (DOĞRULANMADI): https://english.enabbaladi.net/archives/2026/11/from-factions-to-a-unified-force-what-army-is-syria-building/ (2026-11 (day UNKNOWN))

## K003 — SANA
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Open access; Arabic primary, English/Turkish/French/Spanish/Kurdish editions listed.
- **identity**: PASS
  - kanıt: https://sana.sy (gözlem: Site footer/metadata describes SANA as the official national news agency of Syria, founded 24 June 1965, affiliated with the Ministry of Information, headquartered in Damascus.)
- **canonical_url**: PASS
  - kanıt: https://sana.sy (gözlem: https://sana.sy resolved and served Arabic front page dated 14-15 Nov 2026 with language editions at /en, /tr, /fr, /es, /ku.)
- **activity**: PASS
  - kanıt: https://sana.sy/economy/syrian-economy/2635173/ (gözlem: Front page listed many items dated 14 November 2026 (e.g. Finance Ministry decision on tax files).)
- **originality**: FAIL — FAIL: Sampled items are ministerial decisions, ambassador credential ceremonies and local incident notices, i.e. official statements and agency copy; no investigative or independent reporting item ide
  - kanıt: https://sana.sy (gözlem: Sampled items are ministerial decisions, ambassador credential ceremonies and local incident notices, i.e. official statements and agency copy; no investigative or independent reporting item identified.)
- **provenance**: PASS
  - kanıt: https://sana.sy (gözlem: Content is state-agency reporting of government ministries and officials (labelled state media). Upstream = Syrian government statements.)
- **ownership**: PASS
  - kanıt: https://sana.sy (gözlem: Own site states affiliation with the Ministry of Information (Syrian state).)
- **perspective**: PASS
  - kanıt: https://sana.sy (gözlem: State media of the Syrian government; coverage foregrounds ministers and official activity (e.g. Foreign Minister al-Shaibani receiving ambassadors).)
- Özgün çalışma adayı (DOĞRULANMADI): https://sana.sy/politics/2635087/ (2026-11-14)
- Özgün çalışma adayı (DOĞRULANMADI): https://sana.sy/syria-and-the-world/2635105/ (2026-11-14)

## K004 — Syria Direct
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Open access.
- **identity**: UNKNOWN
  - kanıt: https://syriadirect.org (gözlem: Homepage describes it as an independent nonprofit journalism organization focused on Syrian stories and training Syrian journalists.)
- **canonical_url**: PASS
  - kanıt: https://syriadirect.org (gözlem: syriadirect.org resolved and listed dated articles with matching syriadirect.org URLs.)
- **activity**: PASS
  - kanıt: https://syriadirect.org/syria-reconnects-to-global-finance-but-ordinary-syrians-are-still-struggling/ (gözlem: Article page dated 23 October 2026; homepage also lists a 1 November 2026 piece by Rime Allaf and a 26 October piece.)
- **originality**: PASS
  - kanıt: https://syriadirect.org/syria-reconnects-to-global-finance-but-ordinary-syrians-are-still-struggling/ (gözlem: 23 Oct 2026 piece by Karam Alhindi is field reporting from Damascus based on the author's own interviews with a bank CEO, a financial expert, a deputy economy minister and a shop owner.)
- **provenance**: PASS
  - kanıt: https://syriadirect.org/syria-reconnects-to-global-finance-but-ordinary-syrians-are-still-struggling/ (gözlem: Own interviews plus cited published figures (UN, OCHA, World Bank, SANA).)
- **ownership**: UNKNOWN
  - kanıt: https://syriadirect.org (gözlem: Page does not state owner or governance; lists partners Asfari Foundation, DT Institute, McNulty Prize, without saying whether they fund it.)
- **perspective**: UNKNOWN
  - kanıt: https://syriadirect.org (gözlem: Self-described independent nonprofit; no documented editorial line fetched.)
- Özgün çalışma (doğrulanmış): https://syriadirect.org/syria-reconnects-to-global-finance-but-ordinary-syrians-are-still-struggling/ (2026-10-23)

## K007 — Omran Center for Strategic Studies
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Open access; PDF versions linked. Some fetches returned stale or placeholder dates.
- **identity**: UNKNOWN
  - kanıt: https://omrandirasat.org (gözlem: Fetched pages are titled Omran Center for Strategic Studies and name its executive director; no about/legal page opened (omranstudies.org about page appeared only in search results).)
- **canonical_url**: PASS
  - kanıt: https://omrandirasat.org/en/research/beyond-the-axis-israels-approach-in-syria-from-threat-management-to-reshaping-the-security-environment/ (gözlem: omrandirasat.org/en/research page loads under the Omran Center brand with Arabic and English content. Legacy domain omranstudies.org also appears in search results.)
- **activity**: UNKNOWN
  - kanıt: https://omrandirasat.org/en/ (gözlem: Latest verifiable dated item found is 2 June 2026 (web page). Search surfaced PDFs under wp-content/uploads/2026/08/ but they were not opened; one English fetch returned an item with a 1 Jan 1970 placeholder date.)
- **originality**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-016: özgünlük kanıtı 166 gün eski (>45)
  - kanıt: https://omrandirasat.org/en/research/beyond-the-axis-israels-approach-in-syria-from-threat-management-to-reshaping-the-security-environment/ (gözlem: Research item (web page 2 June 2026; Arabic study 12 May 2026) by Muhsen Al Mustafa, Sasha Al Alou, Seba Abdullatif; tracks 416 Israeli operations in Syria in 2025 with a database and maps, mixed quantitative/qualitative method.)
- **provenance**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-005: yukarı akış izlenmedi
  - kanıt: https://omrandirasat.org/en/research/beyond-the-axis-israels-approach-in-syria-from-threat-management-to-reshaping-the-security-environment/ (gözlem: Own-compiled monitoring dataset and analysis.)
- **ownership**: UNKNOWN
  - kanıt: https://omrandirasat.org/en/research/beyond-the-axis-israels-approach-in-syria-from-threat-management-to-reshaping-the-security-environment/ (gözlem: No funding or ownership information found on fetched pages.)
- **perspective**: UNKNOWN
  - kanıt: https://omrandirasat.org/en/research/beyond-the-axis-israels-approach-in-syria-from-threat-management-to-reshaping-the-security-environment/ (gözlem: Not documented on pages fetched; subject framing treats post-Assad state institutions as legitimate government.)
- Özgün çalışma adayı (DOĞRULANMADI): https://omrandirasat.org/en/research/beyond-the-axis-israels-approach-in-syria-from-threat-management-to-reshaping-the-security-environment/ (2026-06-02)
- Özgün çalışma adayı (DOĞRULANMADI): https://omrandirasat.org/wp-content/uploads/2026/08/16082026-1.pdf (2026-08-16)

## K020 — Haaretz
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Haaretz article and headline pages blocked to fetch tool (robots_disallowed); site uses a premium paywall (.premium in URLs). Nothing bypassed.
- **identity**: UNKNOWN
  - kanıt: https://www.haaretz.com (gözlem: Own about/legal page not read. Homepage fetch returned headlines only.)
- **canonical_url**: UNKNOWN
  - kanıt: https://www.haaretz.com (gözlem: Homepage fetched (headlines, no URLs or dates); article-level URL format seen in search results (haaretz.com/israel-news/...).)
- **activity**: UNKNOWN
  - kanıt: https://www.haaretz.com/israel-news/elections/2026-08-15/ty-article-static/.premium/reality-check-as-the-election-nears-haaretz-debunks-israeli-politicians-biggest-lies/0000019f-a8c0-d798-a3bf-bafea2290000 (gözlem: Search results show Haaretz URLs dated 2026-08-15 (outside window). Secondary outlets (Yeni Safak 8 Sep 2026, Washington Examiner 10 Sep 2026) describe a Haaretz investigation; no in-window Haaretz item opened.)
- **originality**: UNKNOWN
  - kanıt: https://en.yenisafak.com/world/haaretz-reveals-netanyahu-ignored-uae-warning-before-oct-7-attack-3722904 (gözlem: Secondary report (8 Sep 2026) says Haaretz revealed an alleged UAE warning to Netanyahu before 7 Oct 2023; Haaretz original URL and reporter not given in either secondary article.)
- **provenance**: UNKNOWN
  - kanıt: https://en.yenisafak.com/world/haaretz-reveals-netanyahu-ignored-uae-warning-before-oct-7-attack-3722904 (gözlem: Reported investigation appears to rest on Haaretz's own sourcing (not confirmed).)
- **ownership**: UNKNOWN
  - kanıt: https://www.arabnews.pk/node/2577706/media (gözlem: Search results associate publisher Amos Schocken and the Schocken family with Haaretz; not confirmed by an ownership document.)
- **perspective**: UNKNOWN
  - kanıt: https://www.haaretz.com/opinion/editorial/2025-12-15/ty-article-opinion/netanyahus-government-wants-a-commission-of-whitewashing-into-october-7/0000019b-23b8-d60f-a5db-6bbebacc0000 (gözlem: Search result shows Haaretz editorials critical of the Netanyahu government (Dec 2025); editorial line not documented from an own statement.)
- Özgün çalışma adayı (DOĞRULANMADI): https://en.yenisafak.com/world/haaretz-reveals-netanyahu-ignored-uae-warning-before-oct-7-attack-3722904 (2026-09-08)

## K029 — Naftemporiki
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Some items under Premium (e-edition, archive); sampled item free. Greek only.
- **identity**: PASS
  - kanıt: https://naftemporiki.gr/about (gözlem: About page lists owner 'Η ΝΑΥΤΕΜΠΟΡΙΚΗ', legal form branch of foreign company, GEMI 159656107001, chairman Giorgos Melissanidis, general manager Spyros Ktenas.)
- **canonical_url**: PASS
  - kanıt: https://www.naftemporiki.gr (gözlem: naftemporiki.gr resolved and served a live feed dated 14 Nov 2026 with matching URLs.)
- **activity**: PASS
  - kanıt: https://www.naftemporiki.gr/kosmos/2189099/to-kremlino-epivevaiose-tis-synomilies-ton-proedron-poytin-si-kai-tramp-stin-kina-stis-19-noemvrioy/ (gözlem: Article dated Saturday 14 Nov 2026 17:36 Athens time.)
- **originality**: UNKNOWN
  - kanıt: https://www.naftemporiki.gr (gözlem: The only article opened is wire copy (ΑΠΕ-ΜΠΕ with Reuters). No concrete original Naftemporiki investigation or dataset was checked.)
- **provenance**: PASS
  - kanıt: https://www.naftemporiki.gr/kosmos/2189099/to-kremlino-epivevaiose-tis-synomilies-ton-proedron-poytin-si-kai-tramp-stin-kina-stis-19-noemvrioy/ (gözlem: Sampled item credited to ΑΠΕ-ΜΠΕ with information from Reuters, plus RIA for a detail.)
- **ownership**: UNKNOWN
  - kanıt: https://naftemporiki.gr/about (gözlem: Owner entity named; no shareholder list. Domain holder ZOFRANK HOLDINGS CO LIMITED-NAFTEMPORIKI; Greece 2.0 / NextGenerationEU SME digital banner noted.)
- **perspective**: UNKNOWN
  - kanıt: https://naftemporiki.gr/about (gözlem: No editorial policy statement read; economic/business daily by profile.)

## K031 — ELIAMEP
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Open access; Greek and English.
- **identity**: PASS
  - kanıt: https://www.eliamep.gr/en/about-us/ (gözlem: About page: private, independent, nonprofit think tank in Athens founded 1988; publishes annual reports.)
- **canonical_url**: PASS
  - kanıt: https://www.eliamep.gr (gözlem: eliamep.gr resolved with dated listings and matching URLs.)
- **activity**: PASS
  - kanıt: https://www.eliamep.gr/eliamep-explainer-oi-endiameses-ekloges-stis-ipa-to-2026-ti-allazei-stin-ouasigkton/ (gözlem: Explainer dated 11 Nov 2026; homepage also lists a policy brief dated 14 Nov 2026.)
- **originality**: PASS
  - kanıt: https://www.eliamep.gr/eliamep-explainer-oi-endiameses-ekloges-stis-ipa-to-2026-ti-allazei-stin-ouasigkton/ (gözlem: ELIAMEP Explainer on the 3 Nov 2026 US midterms by Dimitris Tsarouchas and Athina Fatsea; own analysis.)
- **provenance**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-005/spot-check no: açıklayıcı metin kaynak göstermiyor
  - kanıt: https://www.eliamep.gr/eliamep-explainer-oi-endiameses-ekloges-stis-ipa-to-2026-ti-allazei-stin-ouasigkton/ (gözlem: Own authored policy analysis by named staff.)
- **ownership**: UNKNOWN
  - kanıt: https://www.eliamep.gr/en/about-us/ (gözlem: No donor breakdown; page mentions EU-linked grants (ERC, FP7) and named grant-funded chairs (Kontelli programme, A. G. Leventis Foundation chair); annual reports said to include fundraising summary.)
- **perspective**: UNKNOWN
  - kanıt: https://www.eliamep.gr/en/about-us/ (gözlem: Describes itself as fully independent; research areas incl. Turkey, Mediterranean, EU. No documented political/ideological stance read.)
- Özgün çalışma (doğrulanmış): https://www.eliamep.gr/eliamep-explainer-oi-endiameses-ekloges-stis-ipa-to-2026-ti-allazei-stin-ouasigkton/ (2026-11-11)

## K039 — Mada Masr
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: Blocked inside Egypt since 2017 per Al Jazeera; court ordered closure and equipment confiscation 27 Oct 2026 (Tuesday ruling); article fetches returned client_error. Continuity risk is high.
- **identity**: UNKNOWN
  - kanıt: https://www.madamasr.com/en/ (gözlem: No about/legal page opened. Al Jazeera describes it as one of Egypt's last prominent independent outlets, founded 2013, editor-in-chief Lina Attalah.)
- **canonical_url**: UNKNOWN
  - kanıt: https://www.madamasr.com/en/ (gözlem: https://www.madamasr.com/en/ fetched without error but returned undated, apparently stale headlines (some referencing 2014 events). Al Jazeera reports a court ordered the outlet's closure on a Tuesday (article 27 Oct 2026) and that it has b)
- **activity**: UNKNOWN
  - kanıt: https://www.madamasr.com/en/2026/10/27/news/u/lina-attalah-in-custody-after-court-issues-le3-mn-fine-orders-mada-masrs-closure/ (gözlem: Search results list Mada Masr URLs dated 2026/10/26 and 2026/10/27, but fetching those pages failed (client_error).)
- **originality**: UNKNOWN
  - kanıt: https://www.madamasr.com/en/ (gözlem: No dated original Mada Masr report was opened.)
- **provenance**: UNKNOWN
  - kanıt: https://www.madamasr.com/en/ (gözlem: Not established; outlet known to report on Egypt but no article opened.)
- **ownership**: UNKNOWN
  - kanıt: https://aljazeera.com/news/2026/10/27/egypt-orders-closure-of-leading-independent-news-site-mada-masr (gözlem: Al Jazeera article does not state ownership.)
- **perspective**: UNKNOWN
  - kanıt: https://aljazeera.com/news/2026/10/27/egypt-orders-closure-of-leading-independent-news-site-mada-masr (gözlem: Described as independent; faces licensing prosecution (Article 105, 2018 media law) and a 3 million EGP fine on its editor.)

## K047 — IRNA
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: BLOCKED: irna.ir and en.irna.ir return robots_disallowed to the fetch tool; no bypass attempted. Persian primary.
- **identity**: UNKNOWN
  - kanıt: https://www.irna.ir (gözlem: irna.ir fetch returned robots_disallowed; no about page read. Search results (not opened) list en.irna.ir and third-party descriptions of IRNA as a state agency.)
- **canonical_url**: UNKNOWN
  - kanıt: https://en.irna.ir/ (gözlem: Search results list en.irna.ir pages; starting URL not fetchable.)
- **activity**: UNKNOWN
  - kanıt: https://en.irna.ir/news/86321045/Russia-and-China-urge-immediate-end-to-war-against-Iran-stress (gözlem: Search results show IRNA English items with no dates; pages blocked to the fetch tool.)
- **originality**: UNKNOWN
  - kanıt: https://en.irna.ir/ (gözlem: State agencies carry official statements only; no item reviewed.)
- **provenance**: UNKNOWN
  - kanıt: https://en.irna.ir/ (gözlem: Search titles (e.g. Army statements on Hormuz, SNSC statements) suggest official-statement relay; not read.)
- **ownership**: UNKNOWN
  - kanıt: https://statemediamonitor.com/2023/08/islamic-republic-news-agency-irna/ (gözlem: Third-party monitor entry exists in search results; not opened.)
- **perspective**: UNKNOWN
  - kanıt: https://en.irna.ir/ (gözlem: Not read. Treated as state media candidate, unverified.)

## K051 — IranWire
- Doğrulayıcı: cowork-verifier-A; keşif: cowork-discovery-A
- Erişim notu: BLOCKED: all iranwire.com fetches returned client_error; evidence limited to search result titles/URLs.
- **identity**: UNKNOWN
  - kanıt: https://iranwire.com (gözlem: iranwire.com fetch failed (client_error); no about page read.)
- **canonical_url**: UNKNOWN
  - kanıt: https://iranwire.com/en/ (gözlem: Search results list iranwire.com/en/ article URLs; direct fetches failed.)
- **activity**: UNKNOWN
  - kanıt: https://iranwire.com/en/news/160174-brussels-says-iran-may-be-behind-cyberattacks-on-supermarket-refrigeration-systems/ (gözlem: Search results list article URLs with sequential IDs up to about 160181, no dates visible; fetches failed.)
- **originality**: UNKNOWN
  - kanıt: https://iranwire.com/en/features/156066-gallows-by-the-numbers-an-iranwire-investigation-into-irans-execution-waves/ (gözlem: Search results show titled IranWire investigations and features (execution waves, IRGC cyber unit, surrogacy market); none opened or dated.)
- **provenance**: UNKNOWN
  - kanıt: https://iranwire.com/en/news/160174-brussels-says-iran-may-be-behind-cyberattacks-on-supermarket-refrigeration-systems/ (gözlem: At least some items relay other bodies' findings (US Senate report, Brussels statement) per titles.)
- **ownership**: UNKNOWN
  - kanıt: https://iranwire.com (gözlem: Not read.)
- **perspective**: UNKNOWN
  - kanıt: https://iranwire.com (gözlem: Not read; exile-run outlet status unverified here.)

## K065 — Al-Monitor
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: Metered paywall on originals observed (paywall text); content not fully read.
- **identity**: PASS
  - kanıt: https://www.al-monitor.com/about (gözlem: About page states Al-Monitor was founded in 2012 by Jamal Daniel; footer of homepage names AL-MONITOR, LLC as copyright holder.)
- **canonical_url**: PASS
  - kanıt: https://www.al-monitor.com (gözlem: Homepage loads with current November 2026 originals, newsletters and podcast under the same host.)
- **activity**: PASS
  - kanıt: https://www.al-monitor.com/newsletter/2026-11-12/china-seizes-diplomatic-opening-middle-east (gözlem: Newsletter dated Nov 12, 2026 (author Rosaleen Carroll) and other newsletters dated Nov 11, 2026 listed on homepage.)
- **originality**: UNKNOWN
  - kanıt: https://www.al-monitor.com/originals/2026/11/mossad-chief-visits-us-fears-grow-netanyahu-could-strike-iran-block-eisenkot (gözlem: Ben Caspit piece cites 'Israeli political sources told Al-Monitor' (own sourcing) and relays an Axios report; page shows no explicit publication date (URL says 2026/11).)
- **provenance**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-018/spot-check partial: paywall; içerik kısmen AFP/Axios aktarımı
  - kanıt: https://www.al-monitor.com/originals/2026/11/mossad-chief-visits-us-fears-grow-netanyahu-could-strike-iran-block-eisenkot (gözlem: Mixed upstream: own anonymous Israeli sources plus attribution to Axios (itself citing three sources) for the Mossad visit detail.)
- **ownership**: UNKNOWN
  - kanıt: https://www.al-monitor.com/about (gözlem: Founder named; LLC named; no ownership or funding documents seen.)
- **perspective**: UNKNOWN
  - kanıt: https://www.al-monitor.com/about (gözlem: Only self-description as independent; no evidenced editorial or ideological stance documented.)
- Özgün çalışma adayı (DOĞRULANMADI): https://www.al-monitor.com/originals/2026/11/mossad-chief-visits-us-fears-grow-netanyahu-could-strike-iran-block-eisenkot (2026-11 (day not shown on page))
- Özgün çalışma adayı (DOĞRULANMADI): https://www.al-monitor.com/originals/2026/11/why-carton-eggs-luxury-gaza (2026-11-14)
- Özgün çalışma adayı (DOĞRULANMADI): https://www.al-monitor.com/originals/2026/11/how-war-us-reshaping-nuclear-doctrine-post-khamenei-iran (2026-11 (exact day not shown))

## K070 — AZERTAC
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen. Languages per about page: az, en, ru, fr, de, ar, zh, es.
- **identity**: PASS
  - kanıt: https://azertag.az/en/about (gözlem: About page: AZERTAC founded 1 March 1920 by Government of the Azerbaijan Democratic Republic; since 24 Nov 2016 a public legal entity, statute approved Dec 2017; described as 'sole source of official government news'.)
- **canonical_url**: PASS
  - kanıt: https://azertag.az/en/xeber/top_stories_update-4494357 (gözlem: English edition is at azertag.az/en (root azertag.az is the Azerbaijani edition); item URLs resolve under that host.)
- **activity**: PASS
  - kanıt: https://azertag.az/en/xeber/top_stories_update-4494357 (gözlem: Item dated 4 Nov 2026 12:01; sidebar lists items stamped 14.11.2026 and 15.11.2026 00:11.)
- **originality**: FAIL — FAIL: Sampled item is a headline digest of reports; state agency carries official statements and wire-style copy, no original investigation/data observed.
  - kanıt: https://azertag.az/en/xeber/top_stories_update-4494357 (gözlem: Sampled item is a headline digest of reports; state agency carries official statements and wire-style copy, no original investigation/data observed.)
- **provenance**: PASS
  - kanıt: https://azertag.az/en/about (gözlem: State news agency: content relies on government statements and ministries; must be labelled state media.)
- **ownership**: PASS
  - kanıt: https://azertag.az/en/about (gözlem: Government-founded public legal entity reorganized from a state body (explicit on its about page).)
- **perspective**: PASS
  - kanıt: https://azertag.az/en/about (gözlem: Self-described sole source of official government news; Azerbaijani state perspective (state media).)
- Özgün çalışma adayı (DOĞRULANMADI): https://azertag.az/en/xeber/top_stories_update-4494357 (2026-11-04)

## K077 — Hetq
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen.
- **identity**: PASS
  - kanıt: https://hetq.am/en/about (gözlem: About page: Hetq published in Yerevan since 2001 by the Association of Investigative Journalists NGO (re-registered 2004 as Investigative Journalists NGO); Hetq LLC manager listed.)
- **canonical_url**: PASS
  - kanıt: https://hetq.am/en (gözlem: English edition canonical at hetq.am/en; hy default and ru available.)
- **activity**: PASS
  - kanıt: https://hetq.am/hy/article/185453 (gözlem: Feed items stamped 2026-11-14 and 2026-11-13; article 185453 dated 14 Nov 2026 12:30.)
- **originality**: UNKNOWN
  - kanıt: https://hetq.am/hy/article/185453 (gözlem: Inspected article is a retrospective overview with no cited sources or new documents; no verified investigative piece opened.)
- **provenance**: UNKNOWN
  - kanıt: https://hetq.am/hy/article/185453 (gözlem: Upstream material for sampled items not identifiable (no citations).)
- **ownership**: PASS
  - kanıt: https://hetq.am/en/about (gözlem: NGO publisher explicit; Calouste Gulbenkian Foundation support disclosed.)
- **perspective**: UNKNOWN
  - kanıt: https://hetq.am/en/about (gözlem: Investigative/anti-corruption mission only; no documented ideological stance seen.)
- Özgün çalışma adayı (DOĞRULANMADI): https://hetq.am/en/article/180949 (2026-04-23)
- Özgün çalışma adayı (DOĞRULANMADI): https://hetq.am/en/article/185365 (2026-11-12)

## K080 — OC Media
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen; members-only Daily Brief exists.
- **identity**: PASS
  - kanıt: https://oc-media.org/about-us/ (gözlem: About page names founders Mariam Nikuradze, Dominik K Cagara, Caroline Sutcliffe; registered as an NGO; EIC Robin Fabbro.)
- **canonical_url**: PASS
  - kanıt: https://oc-media.org (gözlem: Homepage with 2026 articles; English edition.)
- **activity**: PASS
  - kanıt: https://oc-media.org/georgias-prison-director-resigns-amid-investigation-into-alleged-inmate-beating/ (gözlem: Homepage top stories dated 26 Oct 2026 (author Lana Kokaia).)
- **originality**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-024/spot-check partial: örnek kısmen özgün
  - kanıt: https://oc-media.org/how-the-armenian-government-built-a-sham-exhibit-at-the-national-gallery/ (gözlem: Ani Ghulinyan article dated 24 Oct 2026: author visited the gallery 14 Oct, took photos, quoted staff, Investigative Committee written statement, defence lawyers.)
- **provenance**: PASS
  - kanıt: https://oc-media.org/how-the-armenian-government-built-a-sham-exhibit-at-the-national-gallery/ (gözlem: Primarily own field observation and interviews, supplemented by other outlets' coverage and official videos.)
- **ownership**: UNKNOWN
  - kanıt: https://oc-media.org/about-us/ (gözlem: Funding described as institutional donors plus readers; donors not named.)
- **perspective**: UNKNOWN
  - kanıt: https://oc-media.org/about-us/ (gözlem: Self-declared political independence; no documented stance evidenced.)
- Özgün çalışma adayı (DOĞRULANMADI): https://oc-media.org/how-the-armenian-government-built-a-sham-exhibit-at-the-national-gallery/ (2026-10-24)
- Özgün çalışma adayı (DOĞRULANMADI): https://oc-media.org/georgias-prison-director-resigns-amid-investigation-into-alleged-inmate-beating/ (2026-10-26)
- Özgün çalışma adayı (DOĞRULANMADI): https://oc-media.org/outcry-after-tehran-invites-azerbaijani-girls-facing-hijab-ban-to-study-in-iran/ (2026-10-26)

## K083 — TASS
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen. State media; sanctions/access restrictions not tested.
- **identity**: UNKNOWN
  - kanıt: https://tass.com (gözlem: Homepage footer shows media registration certificate No. 03247 (2 Apr 1999) and menu links to management/contacts; tass.com/about fetch failed (client_error).)
- **canonical_url**: PASS
  - kanıt: https://tass.com (gözlem: Homepage resolves with items dated 13-14 Nov 2026.)
- **activity**: PASS
  - kanıt: https://tass.com/world/2218193 (gözlem: Item datelined SOFIA, November 14 (year inferred 2026 from homepage context).)
- **originality**: FAIL — FAIL: Sampled item relays a Facebook post by Bulgarian PM Radev; homepage items attributed to Russian MFA statements. No original investigation seen.
  - kanıt: https://tass.com/world/2218193 (gözlem: Sampled item relays a Facebook post by Bulgarian PM Radev; homepage items attributed to Russian MFA statements. No original investigation seen.)
- **provenance**: PASS
  - kanıt: https://tass.com/world/2218193 (gözlem: Upstream is a foreign politician's social post; other headlines rest on Russian MFA/'top brass' statements. Russian state news agency.)
- **ownership**: UNKNOWN
  - kanıt: https://tass.com (gözlem: Own site does not state owner in text read; only secondary source (Wikipedia) cites state ownership.)
- **perspective**: PASS
  - kanıt: https://tass.com (gözlem: Homepage carries headlines framed as Russian MFA positions (e.g. EU gas, EANA expelling TASS); state-media perspective.)
- Özgün çalışma adayı (DOĞRULANMADI): https://tass.com/defense/2218169 (2026-11-14)
- Özgün çalışma adayı (DOĞRULANMADI): https://tass.com/politics/2217939 (2026-11-13)

## K086 — Meduza
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: Blocked in Russia (exile outlet); reachable from outside. Russian-language default.
- **identity**: PASS
  - kanıt: https://meduza.io/en/pages/about (gözlem: About page: registered company SIA 'Medusa Project', Riga, Latvia; CEO Galina Timchenko; EIC Ivan Kolpakov; foreign agent 2021, undesirable org Jan 2023.)
- **canonical_url**: PASS
  - kanıt: https://meduza.io (gözlem: Homepage (Russian) with items dated 12-14 Nov 2026; English via EN link.)
- **activity**: PASS
  - kanıt: https://meduza.io/news/2026/11/14/belyy-dom-ob-yavil-chto-vstrecha-trampa-putina-i-si-proydet-19-noyabrya-v-kitae-oni-obsudyat-yadernoe-oruzhie-no-ne-voynu-v-ukraine (gözlem: Many items dated 12-14.11.2026 (dates from URLs).)
- **originality**: UNKNOWN
  - kanıt: https://meduza.io/feature/2026/11/14/ranshe-vrachi-privivali-sebe-chumu-ya-privila-sebe-tyurmu (gözlem: Inspected feature (14 Nov 2026) is a full republication of Glasnaya's 13 Nov original reporting; Meduza's own originals (e.g. Kolpakov interview with Pivovarov 13 Nov) only seen as headlines.)
- **provenance**: PASS
  - kanıt: https://meduza.io/feature/2026/11/14/ranshe-vrachi-privivali-sebe-chumu-ya-privila-sebe-tyurmu (gözlem: Mixed: republished partner outlet (Glasnaya) reporting, own interviews/podcasts, daily news likely rewrites; not clean own-reporting.)
- **ownership**: PASS
  - kanıt: https://meduza.io/en/pages/about (gözlem: SIA Medusa Project (Riga); funding mainly reader donations (12,000+ monthly donors), book sales; ad revenue lost after 2021 designation.)
- **perspective**: PASS
  - kanıt: https://meduza.io/en/pages/about (gözlem: Exile outlet outlawed in Russia: foreign agent (Apr 2021), undesirable (Jan 2023).)
- Özgün çalışma adayı (DOĞRULANMADI): https://meduza.io/feature/2026/11/14/ranshe-vrachi-privivali-sebe-chumu-ya-privila-sebe-tyurmu (2026-11-14)
- Özgün çalışma adayı (DOĞRULANMADI): https://meduza.io/video/2026/11/13/politik-andrey-pivovarov-okazalsya-v-emigratsii-posle-istoricheskogo-obmena-on-rasskazal-glavredu-meduzy-ivanu-kolpakovu-kakoy-uvidel-oppozitsiyu-v-izgnanii (2026-11-13)
- Özgün çalışma adayı (DOĞRULANMADI): https://meduza.io/feature/2026/11/14/ranshe-vrachi-privivali-sebe-chumu-ya-privila-sebe-tyurmu (2026-11-14)

## K225 — Ukrainian Prism
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen. Mixed uk/en.
- **identity**: UNKNOWN
  - kanıt: https://prismua.org/en/ (gözlem: Homepage self-describes as network-based non-governmental analytical centre (Foreign Policy Council 'Ukrainian Prism'); about page (/en/pro-radu/) and /en/about-us/ not readable.)
- **canonical_url**: PASS
  - kanıt: https://prismua.org/en/ (gözlem: English edition loads with 2026 dated publications; Ukrainian items served at http://prismua.org.)
- **activity**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): spot-check partial; RT-017: örnek başka kurumun brifinden türetilmiş
  - kanıt: https://prismua.org/en/2408675468-2/ (gözlem: Publications dated 10/11/2026 and 27/10/2026 on English listing.)
- **originality**: UNKNOWN
  - kanıt: https://prismua.org/en/2408675468-2/ (gözlem: Listing shows named-author analytical papers dated 10 Nov 2026 (e.g. Kraiev) but no paper was opened.)
- **provenance**: UNKNOWN
  - kanıt: https://prismua.org/en/ (gözlem: Upstream material for papers not examined.)
- **ownership**: PASS
  - kanıt: https://prismua.org/en/ (gözlem: Site developed with support of Public Affairs Section of the US Embassy in Ukraine (disclaimer on page).)
- **perspective**: UNKNOWN
  - kanıt: https://policycommons.net/orgs/the-foreign-policy-council-ukrainian-prism/ (gözlem: Aggregator states goal to support Ukrainian authorities' foreign policy; stance not independently evidenced.)
- Özgün çalışma adayı (DOĞRULANMADI): https://prismua.org/en/2408675468-2/ (2026-11-10)
- Özgün çalışma adayı (DOĞRULANMADI): https://prismua.org/russian-unmanned-systems-current-state-prospects-of-production-and-application/ (2024-08-13)

## K105 — Avrupa Komisyonu — Press Corner
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: Press items are JS-rendered; not fetchable as static text.
- **identity**: PASS
  - kanıt: https://commission.europa.eu/document/97384f52-5a62-4258-a570-d15ab2ae44fa_en (gözlem: Press Corner linked from commission.europa.eu, which states it is managed by the Directorate-General for Communication.)
- **canonical_url**: PASS
  - kanıt: https://ec.europa.eu/commission/presscorner/home/en (gözlem: Page metadata gives canonical https://ec.europa.eu/commission/presscorner/home/en ('Highlights, press releases and speeches').)
- **activity**: UNKNOWN
  - kanıt: https://ec.europa.eu/commission/presscorner/home/en (gözlem: Listing is client-rendered; no dated items visible to fetch tool; API fetch failed.)
- **originality**: FAIL — FAIL: Press Corner carries official press releases, speeches and statements, not independent reporting.
  - kanıt: https://ec.europa.eu/commission/presscorner/home/en (gözlem: Press Corner carries official press releases, speeches and statements, not independent reporting.)
- **provenance**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-005: hiçbir kalem incelenmemiş
  - kanıt: https://ec.europa.eu/commission/presscorner/home/en (gözlem: Primary institutional statements of the European Commission.)
- **ownership**: PASS
  - kanıt: https://commission.europa.eu/document/97384f52-5a62-4258-a570-d15ab2ae44fa_en (gözlem: Site managed by Commission DG COMM (EU institution).)
- **perspective**: PASS
  - kanıt: https://ec.europa.eu/commission/presscorner/home/en (gözlem: Official EU institutional voice; a party to the policies it announces.)
- Özgün çalışma adayı (DOĞRULANMADI): https://ec.europa.eu/commission/presscorner/detail/en/ip_26_2361 (2026-11-06)
- Özgün çalışma adayı (DOĞRULANMADI): https://ec.europa.eu/commission/presscorner/detail/en/ip_26_2321 (2026-11-04)

## K112 — SWP
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen. German/English.
- **identity**: PASS
  - kanıt: https://www.swp-berlin.org/en/about-swp/funding (gözlem: SWP page: private legal form operating under public-sector rules; advises Bundestag/Government; states independence in topic and method choice.)
- **canonical_url**: PASS
  - kanıt: https://www.swp-berlin.org (gözlem: Homepage resolves with publications dated 12.11.2026.)
- **activity**: PASS
  - kanıt: https://www.swp-berlin.org/publikation/premiumpartner-deutschland-und-japan (gözlem: SWP-Aktuell 2026/A 57 dated 12.11.2026 and several others in Nov/Oct 2026.)
- **originality**: PASS
  - kanıt: https://www.swp-berlin.org/publikation/demokratieabbau-ohne-grenzen (gözlem: SWP-Studie 2026/S 16, 10.11.2026, 81 pp, doi 10.18449/2026S16; multi-author qualitative study.)
- **provenance**: PASS
  - kanıt: https://www.swp-berlin.org/publikation/demokratieabbau-ohne-grenzen (gözlem: Own research, drawing on V-Dem and Bertelsmann indices and literature.)
- **ownership**: PASS
  - kanıt: https://www.swp-berlin.org/en/about-swp/funding (gözlem: Core funding 100% from Bundestag-approved Chancellery grant (EUR 18.9m 2025); project funds EUR 3.87m 2025; accepts no research commissions.)
- **perspective**: PASS
  - kanıt: https://www.swp-berlin.org/en/about-swp/funding (gözlem: Government-funded and advises German government/parliament (documented).)
- Özgün çalışma (doğrulanmış): https://www.swp-berlin.org/publikation/demokratieabbau-ohne-grenzen (2026-11-10)

## K238 — RUSI
- Doğrulayıcı: cowork-verifier-B; keşif: cowork-discovery-B
- Erişim notu: No paywall seen; research-papers listing partly JS-rendered.
- **identity**: PASS
  - kanıt: https://www.rusi.org/about/our-purpose/funding (gözlem: RUSI states registered charity no. 210639 (England and Wales).)
- **canonical_url**: PASS
  - kanıt: https://rusi.org (gözlem: rusi.org loads with publication links under www.rusi.org/explore-our-research.)
- **activity**: PASS
  - kanıt: https://www.rusi.org/explore-our-research/publications/insights-papers/uk-fatf-mutual-evaluation-taskforce-third-meeting-report (gözlem: Report dated 13 Nov 2026; commentaries dated 12, 10, 9 Nov 2026.)
- **originality**: PASS
  - kanıt: https://www.rusi.org/explore-our-research/publications/insights-papers/uk-fatf-mutual-evaluation-taskforce-third-meeting-report (gözlem: RUSI taskforce report (13 Nov 2026) by Veronica Stratford-Tuke previewing UK 2027 FATF evaluation.)
- **provenance**: PASS
  - kanıt: https://www.rusi.org/explore-our-research/publications/insights-papers/uk-fatf-mutual-evaluation-taskforce-third-meeting-report (gözlem: Own convened taskforce discussions plus FATF methodology and UK government/NCA publications.)
- **ownership**: PASS
  - kanıt: https://www.rusi.org/about/our-purpose/funding (gözlem: Charity; no core government funding; funders disclosed in value bands, names not in text read.)
- **perspective**: UNKNOWN
  - kanıt: https://www.rusi.org/about/our-purpose/funding (gözlem: Says no corporate position; no evidenced institutional leaning documented.)
- Özgün çalışma (doğrulanmış): https://www.rusi.org/explore-our-research/publications/insights-papers/uk-fatf-mutual-evaluation-taskforce-third-meeting-report (2026-11-13)

## K123 — CRS Reports (Kongre)
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: congress.gov and crsreports.congress.gov refuse automated fetch (robots_disallowed); only third-party mirror everycrsreport.com readable. No paywall.
- **identity**: UNKNOWN
  - kanıt: None (gözlem: congress.gov/crs-products could not be read (robots_disallowed). A third-party mirror PDF names CRS as author agency, but no CRS/Library of Congress about page was seen.)
- **canonical_url**: UNKNOWN — BLOCKED (araç/robots/paywall engeli); kaynak kötü demek değildir
  - kanıt: https://www.congress.gov/crs-products (gözlem: Fetch refused by site (robots_disallowed); canonical URL and current content not observable. Alternate crsreports.congress.gov also failed.)
- **activity**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): spot-check partial: yalnız ayna PDF; congress.gov robots engelli
  - kanıt: https://www.everycrsreport.com/files/2026-10-14_IF13217_1669944fd8dbaa6dc8228175e94de9f0a17d208e.pdf (gözlem: CRS In Focus IF13217 'Federal Government and Anthropic: Considerations for AI Innovation and Competition', Version 4, updated 14 Oct 2026, authors Laurie Harris and Clare Y. Cho of CRS.)
- **originality**: PASS
  - kanıt: https://www.everycrsreport.com/files/2026-10-14_IF13217_1669944fd8dbaa6dc8228175e94de9f0a17d208e.pdf (gözlem: Named-analyst original policy analysis (In Focus) dated 14 Oct 2026. It is analysis, not news reporting or field data.)
- **provenance**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-005: yukarı akış izlenmedi
  - kanıt: https://www.everycrsreport.com/files/2026-10-14_IF13217_1669944fd8dbaa6dc8228175e94de9f0a17d208e.pdf (gözlem: Product is internal analyst synthesis for Congress; underlying material is public record and secondary sources, not field reporting. Government legislative-branch research service.)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: No explicit ownership/funding document seen.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: No document seen stating CRS's mandate or neutrality policy; any nonpartisan claim is unverified here.)
- Özgün çalışma (doğrulanmış): https://www.everycrsreport.com/files/2026-10-14_IF13217_1669944fd8dbaa6dc8228175e94de9f0a17d208e.pdf (2026-10-14)

## K244 — FDD
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: Intermittent client_error on fdd.org subpages (/about/, /analysis/op-eds/, a Sep 2026 policy brief). One analysis index fetch returned a stale April 2024 listing; ignored.
- **identity**: UNKNOWN
  - kanıt: None (gözlem: fdd.org homepage names Foundation for Defense of Democracies as event host; /about/ fetch failed (client_error), so no own about/legal page seen.)
- **canonical_url**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-013: fdd.org/about ve brief sayfası açılmadı; keşif BLOCKED dedi
  - kanıt: https://www.fdd.org (gözlem: fdd.org loads current content (Overnight Brief dated 12 Nov 2026, FDD-hosted event) and op-ed pages on fdd.org identify FDD authors (e.g. executive director Jonathan Schanzer).)
- **activity**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-013/spot-check partial: fdd.org sayfaları açılamadı, tarih URL'den
  - kanıt: https://www.fdd.org (gözlem: Homepage shows 'Overnight Brief' dated 12 Nov 2026 and an FDD event dated 1 Oct 2026.)
- **originality**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-013/spot-check partial
  - kanıt: https://www.fdd.org/analysis/2026/09/01/iran-on-the-verge-of-collapse/ (gözlem: Op-ed dated 1 Sep 2026 by Jonathan Schanzer with intern Zev Mendelson; original opinion/analysis, not reporting. Search results also list Policy Briefs dated 10 Sep 2026 (not opened).)
- **provenance**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-005: yukarı akış izlenmedi
  - kanıt: https://www.fdd.org/analysis/2026/09/01/iran-on-the-verge-of-collapse/ (gözlem: Think-tank opinion/policy analysis; relies on public statements, sanctions records and open sources, not field reporting. Op-ed was republished (Washington Times per search listing).)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: No funding/donor or legal-structure document seen.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: No FDD document stating its mission was read. Observed pieces advocate a hawkish Iran policy (e.g. 'revive maximum pressure'), which is an inference from titles/op-ed, not from an institutional statement.)
- Özgün çalışma adayı (DOĞRULANMADI): https://www.fdd.org/analysis/2026/09/01/iran-on-the-verge-of-collapse/ (2026-09-01)
- Özgün çalışma adayı (DOĞRULANMADI): https://www.fdd.org/analysis/after-the-midterms-whats-next-for-us-and-iran/ (UNKNOWN (post-US-midterms 2026, i.e. likely November 2026; page fetch BLOCKED))
- Özgün çalışma adayı (DOĞRULANMADI): https://www.fdd.org/analysis/france-is-latest-victim-of-iranian-cyber-sabotage-first-unleashed-on-israel/ (UNKNOWN (page fetch BLOCKED))
- Özgün çalışma adayı (DOĞRULANMADI): https://www.fdd.org/analysis/trump-administration-foreign-policy-tracker-november-2/ (UNKNOWN (likely Nov 2026))

## K132 — Xinhua
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: Open access; About page redirect loop prevented reading.
- **identity**: UNKNOWN
  - kanıt: None (gözlem: Homepage links to an About Xinhua page (https://www.news.cn/xinhuashe/) but fetching it only produced a 302 redirect loop (https to http); page not read.)
- **canonical_url**: PASS
  - kanıt: https://www.news.cn/ (gözlem: news.cn is Xinhuanet (新华网), the Xinhua News Agency website; Chinese-language edition with links to English and eight other language editions; headlines dated 2026-11-14.)
- **activity**: PASS
  - kanıt: https://www.news.cn/20261114/b620ef69ef8a4016a34cb57cc0778614/c.html (gözlem: Article published 14 Nov 2026 16:19 on US-China trade council meeting, bylined Xinhua News Agency, reporter Xie Xiyao.)
- **originality**: FAIL — FAIL: The item observed is based on information from China's Ministry of Commerce (reporter learned of the meeting from the ministry); no independent reporting evident. Per standard, state agency item
  - kanıt: https://www.news.cn/20261114/b620ef69ef8a4016a34cb57cc0778614/c.html (gözlem: The item observed is based on information from China's Ministry of Commerce (reporter learned of the meeting from the ministry); no independent reporting evident. Per standard, state agency items carry official statements.)
- **provenance**: PASS
  - kanıt: https://www.news.cn/20261114/b620ef69ef8a4016a34cb57cc0778614/c.html (gözlem: Content relies on MOFCOM (PRC government) statement; no US-side quotes. Classified as state media relaying state statements.)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: No ownership/funding document read (About page failed).)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: No fetched document states Xinhua's editorial line; observed item is PRC-government-sourced. Must be labelled state media.)
- Özgün çalışma adayı (DOĞRULANMADI): https://www.news.cn/20261114/b620ef69ef8a4016a34cb57cc0778614/c.html (2026-11-14 (from URL))
- Özgün çalışma adayı (DOĞRULANMADI): https://english.news.cn/20261112/7be726c1087641ff80c7fd909f52d11c/c.html (2026-11-12 (from URL))

## K138 — The Hindu
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: thehindu.com is SITE_BLOCKED in this environment; The Hindu is also known to use a metered paywall (not verified here).
- **identity**: UNKNOWN
  - kanıt: None (gözlem: thehindu.com fetch blocked, so no own about/legal page seen.)
- **canonical_url**: UNKNOWN — BLOCKED (araç/robots/paywall engeli); kaynak kötü demek değildir
  - kanıt: https://www.thehindu.com (gözlem: WebFetch returned SITE_BLOCKED for homepage and RSS feed; canonical status unobservable.)
- **activity**: UNKNOWN — BLOCKED (araç/robots/paywall engeli); kaynak kötü demek değildir
  - kanıt: https://www.thehindu.com (gözlem: No dated Hindu article could be opened; search results returned only third-party aggregators/UPSC digests.)
- **originality**: UNKNOWN — BLOCKED (araç/robots/paywall engeli); kaynak kötü demek değildir
  - kanıt: https://www.thehindu.com (gözlem: No original item observed.)
- **provenance**: UNKNOWN
  - kanıt: None (gözlem: Not observable; no article read.)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: Media Ownership Monitor page (https://india.mom-rsf.org/en/media/detail/outlet/the-hindu-online/) states The Hindu website is owned by Kasturi & Sons Limited, a family-owned private company, shares split among four families (26.23/26.13/24.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: No document read.)

## K153 — Addis Standard
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: No paywall observed. Article-level fetches failed (client_error). Languages en/am/om per about page.
- **identity**: PASS
  - kanıt: https://addisstandard.com/about-us/ (gözlem: Own about page states the publication is run by JAKENN Publishing P.L.C., a legally registered media company in Addis Ababa, publishing in English, Afaan Oromoo and Amharic.)
- **canonical_url**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-011: ana sayfa eski (2024) içerik; yalnız alan adı kimliği
  - kanıt: https://addisstandard.com/about-us/ (gözlem: addisstandard.com serves the outlet's own about page; homepage fetch showed Addis Standard content.)
- **activity**: UNKNOWN
  - kanıt: None (gözlem: Homepage fetch showed only 2024-dated items. A Telegram channel mirror (t.me/s/AddisstandardEng) listed recent-looking posts but without dates, and election-result posts correspond to June 2026. No dated post after 1 Oct 2026 was confirmed.)
- **originality**: UNKNOWN
  - kanıt: None (gözlem: Telegram mirror lists headlines linking to addisstandard.com articles (e.g. ?p=57846, ?p=57849), but none were opened or dated.)
- **provenance**: UNKNOWN
  - kanıt: None (gözlem: Not determinable from pages read; Telegram feed mixes own-site articles with links to AP, Middle East Eye and social posts.)
- **ownership**: PASS
  - kanıt: https://addisstandard.com/about-us/ (gözlem: Own page names JAKENN Publishing P.L.C. as operating company providing editorial and admin team and equipment. Funding sources are not stated.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: No perspective statement read.)
- Özgün çalışma adayı (DOĞRULANMADI): https://addisstandard.com/who-chief-warns-continued-violence-in-amhara-tigray-pushing-ethiopias-fragile-health-system-toward-collapse/ (UNKNOWN)
- Özgün çalışma adayı (DOĞRULANMADI): https://addisstandard.com/brief/n-61002/ (UNKNOWN)

## K154 — Sudan Tribune
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: No paywall observed. Subpage fetches for Oct-Nov 2026 articles failed (client_error). Languages en/ar per brief; only English observed.
- **identity**: PASS
  - kanıt: https://sudantribune.com/about-us (gözlem: Own about page: based in Paris, France, run by a team of Sudanese and international editors and journalists; no owner named; languages not stated.)
- **canonical_url**: UNKNOWN — PASS→UNKNOWN (kırmızı takım): RT-012: ana sayfa alan adı/tarih içermiyor; makale açılmadı
  - kanıt: https://sudantribune.com/ (gözlem: Homepage loads with Sudan-focused 'Editors Picks' headlines (Abyei, Red Sea, Sudan inflation).)
- **activity**: UNKNOWN
  - kanıt: None (gözlem: Homepage headlines carry no dates or URLs. The only article opened (https://sudantribune.com/?p=308148) is dated 14 Dec 2025 on its dateline (the page header shows viewing date). Search-result titles showing Nov 2026 dates were not corrobor)
- **originality**: UNKNOWN
  - kanıt: None (gözlem: Article opened has no byline and cites anonymous military sources, a Bangladeshi army statement and official reactions; unclear whether original or relayed.)
- **provenance**: UNKNOWN
  - kanıt: None (gözlem: Observed article mixes anonymous military sources and official statements; no wire credit seen. Cannot classify.)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: No owner or funding named on about page.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: About page describes 'independent Sudanese and international journalists and editors' (self-claim only). Exile-based publication; perspective not documented.)
- Özgün çalışma adayı (DOĞRULANMADI): https://sudantribune.com/article/321171 (UNKNOWN)
- Özgün çalışma adayı (DOĞRULANMADI): https://sudantribune.com/article/321062 (UNKNOWN)

## K159 — Dışişleri Bakanlığı
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: Open access. Languages tr/en; English edition confirmed.
- **identity**: PASS
  - kanıt: https://www.mfa.gov.tr/default.en.mfa (gözlem: English homepage of the Republic of Türkiye Ministry of Foreign Affairs; numbered press releases (e.g. No: 219, 13 Nov 2026) issued by the Ministry.)
- **canonical_url**: PASS
  - kanıt: https://www.mfa.gov.tr/default.en.mfa (gözlem: mfa.gov.tr resolves to the Ministry's site with an English version at /default.en.mfa.)
- **activity**: PASS
  - kanıt: https://www.mfa.gov.tr/no_-219_-israil-in-gazze-de-bir-hastaneye-yonelik-saldirisi-hk.en.mfa (gözlem: Press release No: 219 dated 13 Nov 2026; homepage lists items dated 13-14 Nov 2026.)
- **originality**: FAIL — FAIL: Ministry of a state; output is official statements/communiques (e.g. condemnation of attack on Nasser Hospital). No independent reporting by design.
  - kanıt: https://www.mfa.gov.tr/no_-219_-israil-in-gazze-de-bir-hastaneye-yonelik-saldirisi-hk.en.mfa (gözlem: Ministry of a state; output is official statements/communiques (e.g. condemnation of attack on Nasser Hospital). No independent reporting by design.)
- **provenance**: PASS
  - kanıt: https://www.mfa.gov.tr/no_-219_-israil-in-gazze-de-bir-hastaneye-yonelik-saldirisi-hk.en.mfa (gözlem: Primary state statement of the Turkish government. Establishes that Türkiye made the statement, not that factual claims within it are true.)
- **ownership**: PASS
  - kanıt: https://www.mfa.gov.tr/default.en.mfa (gözlem: Government ministry of the Republic of Türkiye (state body).)
- **perspective**: PASS
  - kanıt: https://www.mfa.gov.tr/default.en.mfa (gözlem: Explicit state actor: statements express official Turkish government positions (e.g. joint statement of 19 foreign ministers 14 Nov 2026).)
- Özgün çalışma adayı (DOĞRULANMADI): https://www.mfa.gov.tr/no_-212_-avrupa-komisyonu-2026-turkiye-raporu-hk.tr.mfa (2026-11-04)

## K168 — Reuters
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: reuters.com is SITE_BLOCKED in this environment; reuters.com content is partly metered/paywalled (not verified here). Evidence is syndicated copy only.
- **identity**: PASS
  - kanıt: https://www.thomsonreuters.com/en/about-us/trust-principles (gözlem: Thomson Reuters' own page on the Trust Principles describes Reuters' news business, the Founders Share Company (est. 1984) and its consent rights over any sale of the Reuters news unit.)
- **canonical_url**: UNKNOWN — BLOCKED (araç/robots/paywall engeli); kaynak kötü demek değildir
  - kanıt: https://www.reuters.com (gözlem: WebFetch returned SITE_BLOCKED for reuters.com.)
- **activity**: PASS
  - kanıt: https://www.timeslive.co.za/news/africa/2026-10-20-more-than-150-people-feared-killed-in-sudan-drone-attack-on-market-in-disputed-zone/ (gözlem: Reuters-credited story (by Nafisa Eltahir and Khalid Abdelaziz) dated 20 Oct 2026 on Abyei drone attack, republished on TimesLIVE.)
- **originality**: PASS
  - kanıt: https://www.timeslive.co.za/news/africa/2026-10-20-more-than-150-people-feared-killed-in-sudan-drone-attack-on-market-in-disputed-zone/ (gözlem: Named Reuters reporters gathered casualty claims from an Abyei official, three diplomats, an aid worker, MSF and South Sudan's foreign ministry, and states it could not independently verify them.)
- **provenance**: PASS
  - kanıt: https://www.timeslive.co.za/news/africa/2026-10-20-more-than-150-people-feared-killed-in-sudan-drone-attack-on-market-in-disputed-zone/ (gözlem: Story depends on anonymous diplomatic sources, local official claims and NGO statements; republished verbatim by other outlets under Reuters credit (copies are not independent).)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: Trust Principles page explains the Founders Share Company holds a share with special rights, but does not name Reuters' ultimate owner or funding. No ownership filing read.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: Only a self-claim (Trust Principles: integrity, independence, freedom from bias) was seen.)
- Özgün çalışma (doğrulanmış): https://www.timeslive.co.za/news/africa/2026-10-20-more-than-150-people-feared-killed-in-sudan-drone-attack-on-market-in-disputed-zone/ (2026-10-20)

## N001 — Bellingcat
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: Open access; Funding & Supporters page failed to load.
- **identity**: PASS
  - kanıt: https://www.bellingcat.com/about/who-we-are (gözlem: Own about page: 'independent investigative collective of researchers, investigators and citizen journalists', over 30 staff and contributors in 20+ countries; open-source research mission.)
- **canonical_url**: PASS
  - kanıt: https://www.bellingcat.com/ (gözlem: Homepage lists dated investigations with URLs on bellingcat.com; about pages on same domain.)
- **activity**: PASS
  - kanıt: https://www.bellingcat.com/news/2026/11/05/how-online-maps-lay-bare-the-us-military-bases-targeted-by-iran/ (gözlem: Investigation published 5 Nov 2026; homepage also lists items dated 15 Oct, 6 Oct and 1 Oct 2026.)
- **originality**: PASS
  - kanıt: https://www.bellingcat.com/news/2026/10/06/dafs-india-rss-donations/ (gözlem: 6 Oct 2026 investigation by Pooja Chaudhuri, Galen Reich, Melissa Zhu analyzing Form 990s (2020-2024): Ekal USA and Sewa USA received at least $24.4m from 34 DAF sponsors; states no evidence DAFs funded the RSS directly.)
- **provenance**: PASS
  - kanıt: https://www.bellingcat.com/news/2026/11/05/how-online-maps-lay-bare-the-us-military-bases-targeted-by-iran/ (gözlem: Own OSINT: Google/Bing/Yandex maps, DVIDS photos geolocated, compared with satellite damage images published by Tasnim, Fars and Washington Post (Planet imagery). Strava findings credited to a Sky News investigation (not Bellingcat's own).)
- **ownership**: UNKNOWN
  - kanıt: None (gözlem: Who-we-are page does not name legal entity or funders; it links a 'Funding & Supporters' page which failed to load.)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: Only self-description (ethical, verifiable open-source methods; collaborates with news orgs) seen; no external evidence of editorial perspective.)
- Özgün çalışma (doğrulanmış): https://www.bellingcat.com/news/2026/11/05/how-online-maps-lay-bare-the-us-military-bases-targeted-by-iran/ (2026-11-05)
- Özgün çalışma (doğrulanmış): https://www.bellingcat.com/news/2026/10/06/dafs-india-rss-donations/ (2026-10-06)

## N002 — ACLED
- Doğrulayıcı: cowork-verifier-C; keşif: cowork-discovery-C
- Erişim notu: Open access pages seen; data downloads may require registration (not tested).
- **identity**: PASS
  - kanıt: https://acleddata.com/about-acled (gözlem: Own about page: ACLED is a registered non-profit with 501(c)(3) status in the US and an independent, impartial monitor of conflict and protest.)
- **canonical_url**: PASS
  - kanıt: https://acleddata.com/ (gözlem: acleddata.com homepage and about page on same domain; links to Conflict Watchlist 2026 and daily Middle East data.)
- **activity**: UNKNOWN
  - kanıt: None (gözlem: Homepage lists a webinar on 26 November (year not given) and a daily Middle East strike dataset (no date). Monthly regional updates listing fetched showed July 2026 items as newest (6 July 2026), possibly stale; no dated item after 1 Oct 20)
- **originality**: PASS
  - kanıt: https://acleddata.com/series/monthly-regional-updates (gözlem: Dated listing entries for ACLED's own monthly overviews (e.g. Africa Overview: July 2026, 6 July 2026; Middle East Overview: July 2026, 3 July 2026). Conflict Index & 2026 Watchlist page describes ACLED-generated indicators (deadliness, civ)
- **provenance**: UNKNOWN
  - kanıt: None (gözlem: About page does not describe data collection method or sources; ACLED's own dataset is the output, but its upstream inputs (media, partners) were not observed.)
- **ownership**: PASS
  - kanıt: https://acleddata.com/about-acled (gözlem: About page states 501(c)(3) non-profit status and financial support from the UN Complex Risk Analytics Fund (CRAF'd).)
- **perspective**: UNKNOWN
  - kanıt: None (gözlem: Self-described 'independent, impartial' only.)
- Özgün çalışma (doğrulanmış): https://acleddata.com/update/africa-overview-july-2026 (2026-07-06)
