# Pilot 30 — Köken ve bağımsız teyit

_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._


Denetçi: cowork-provenance-01. 24 edge (17 iddia düzeyi, 7 kaynak düzeyi). `EXT:` ile başlayan uçlar 30'luk küme dışındaki kökenlerdir (AFP, Axios, MOFCOM, Glasnaya…).

**Sonuç:** Pilot kaynaklar arasında gerçekten bağımsız teyit bulunamadı (`independent_corroboration` edge sayısı: 0). Resmî açıklama yalnız açıklamanın yapıldığını kanıtlar.

## Sahte bağımsız teyit örnekleri (iddia düzeyi)
| Kimden → Kime | İlişki | Kapsam | Kanıt | Güven |
|---|---|---|---|---|
| K083 → K029 | same_statement | Kremlin spokesman Peskov's 14 Nov 2026 statement that a Putin-Xi-Trump meeting is set for 19 Nov in Shenzhen at APEC. TASS (https://tass.com/politics/2218203) quotes Pesk | https://tass.com/politics/2218203 | high |
| K168 → K029 | same_wire | Same Peskov/APEC story: Naftemporiki credit 'ΑΠΕ-ΜΠΕ, με πληροφορίες από Reuters'. Reuters and Naftemporiki are one evidence family, not two confirmations. | https://www.naftemporiki.gr/kosmos/2189099/to-kremlino-epivevaiose-tis-synomilies-ton-proedron-poytin-si-kai-tramp-stin-kina-stis-19-noemvrioy/ | medium |
| K168 → K083 | derives_from | TASS item of 14 Nov 2026 'White House says Trump to meet with Putin, Xi Jinping in China': source given as a White House spokesperson 'as relayed by Reuters and the Assoc | https://tass.com/world/2218067 | medium |
| K159 → K003 | same_statement | Turkish MFA Press Release No. 219 (13 Nov 2026, https://www.mfa.gov.tr/no_-219_-israil-in-gazze-de-bir-hastaneye-yonelik-saldirisi-hk.en.mfa) condemning Israel's strike o | https://sana.sy/en/politics/2358392/ | high |
| K132 → K083 | same_statement | Nasser Hospital (Khan Younis) strike, 12 Nov 2026: Xinhua (Palestinian security/medical sources, Gaza Civil Defense spokesman, Gaza health authorities; six dead, 20+ woun | https://english.news.cn/20261112/5b8ad84afb164433b214404f89a2ea27/c.html | high |
| K020 → K065 | derives_from | Haaretz 8 Sep 2026 report (excerpt from its reporters' forthcoming book) that UAE president warned Netanyahu about 10 days before 7 Oct 2023. Al-Monitor's piece is AFP co | https://al-monitor.com/originals/2026/09/netanyahu-under-fire-over-report-uae-warned-october-7-attack | high |
| K020 → K065 | same_anonymous_tip | Underlying origin of the UAE-warning claim: anonymous sources cited by Haaretz. Single-origin claim; the UAE MFA response ('open and direct lines of communication') neith | https://al-monitor.com/originals/2026/09/netanyahu-under-fire-over-report-uae-warned-october-7-attack | medium |
| EXT:Axios → K065 | derives_from | Al-Monitor (Ben Caspit, Nov 2026, day not shown) says Mossad chief was in Washington, meeting CIA director and possibly Rubio/Witkoff, 'citing three sources familiar' per | https://www.al-monitor.com/originals/2026/11/mossad-chief-visits-us-fears-grow-netanyahu-could-strike-iran-block-eisenkot | high |
| K047 → K065 | same_statement | Al-Monitor/AFP (6 Nov 2026) attributes Iran's army spokesman Akraminia's statements to IRNA and the tanker-hit-a-mine claim to state TV; IRNA is therefore a conduit for t | https://www.al-monitor.com/originals/2026/11/iran-says-forces-stronger-beginning-war | high |
| K132 → K065 | same_statement | Iranian-military claims that 'violating' tankers hit naval mines near Hormuz (Nov 2026). Xinhua (12-13 Nov) sources the army statement and IRGC Navy's Sepah News and note | https://english.news.cn/20261113/bac14b7b749f4d4dbc9a93429e9065b4/c.html | medium |
| K003 → K004 | derives_from | Syria Direct (23 Oct 2026) cites SANA (link https://sana.sy/en/economic/2319012/) for 'nearly 20,000 companies registered since the fall of the Assad regime by May 2026'. | https://syriadirect.org/syria-reconnects-to-global-finance-but-ordinary-syrians-are-still-struggling/ | low |
| EXT:Glasnaya → K086 | republishes | Meduza 14 Nov 2026 feature carries 'Источник: «Гласная»' and says Meduza 'publishes this material in full'; original Glasnaya piece dated 13 Nov 2026. Meduza and Glasnaya | https://meduza.io/feature/2026/11/14/ranshe-vrachi-privivali-sebe-chumu-ya-privila-sebe-tyurmu | high |
| N001 → EXT:Planet-WaPo | same_imagery | Bellingcat 5 Nov 2026 base-damage geolocation uses a Camp Arifjan image 'captured by Planet on March 4, 2026' as published by The Washington Post (https://www.washingtonp | https://www.bellingcat.com/news/2026/11/05/how-online-maps-lay-bare-the-us-military-bases-targeted-by-iran/ | high |
| N001 → EXT:Sky-News | derives_from | Bellingcat's Strava running-data finding at Muwaffaq Salti links to a Sky News investigation; not Bellingcat's own finding. | https://www.bellingcat.com/news/2026/11/05/how-online-maps-lay-bare-the-us-military-bases-targeted-by-iran/ | medium |
| K083 → EXT:Radev-Facebook | same_statement | TASS 14 Nov 2026 'Bulgaria to stop supplying weapons to Ukraine - PM' is based entirely on a Facebook post by Bulgarian PM Radev; origin is a politician's social post. | https://tass.com/world/2218193 | high |
| K132 → EXT:MOFCOM | same_statement | Xinhua 14 Nov 2026 on first US-China trade council meeting (13 Nov): reporter 'learned from the Ministry of Commerce'; no US-side quotes. Single-party account of a bilate | https://www.news.cn/20261114/b620ef69ef8a4016a34cb57cc0778614/c.html | high |
| K168 → EXT:timeslive-businessday | republishes | Reuters (Eltahir/Abdelaziz, 20 Oct 2026) Abyei market drone-strike story, sourced to Abyei information minister, three diplomatic sources, an aid worker, MSF and South Su | https://www.timeslive.co.za/news/africa/2026-10-20-more-than-150-people-feared-killed-in-sudan-drone-attack-on-market-in-disputed-zone/ | high |

## Kaynak düzeyi kurumsal ilişkiler (iddia bağımlılığıyla karıştırılmamalı)
| Kimden → Kime | İlişki | Kapsam | Kanıt | Güven |
|---|---|---|---|---|
| K083 → K132 | partnership | TASS-Xinhua cooperation strategy 2026-2030 signed 2 Sep 2025 (Beijing): shared access to news feeds in Chinese/Russian/English plus photo/video exchange, joint social-med | https://tass.com/society/2010797 | high |
| K168 → K029 | derives_from | Naftemporiki foreign news item credited verbatim 'Πηγή: ΑΠΕ-ΜΠΕ, με πληροφορίες από Reuters' with a Reuters photo credit; Naftemporiki relays the Athens-Macedonian News A | https://www.naftemporiki.gr/kosmos/2189099/to-kremlino-epivevaiose-tis-synomilies-ton-proedron-poytin-si-kai-tramp-stin-kina-stis-19-noemvrioy/ | medium |
| K029 → EXT:CMG | partnership | Naftemporiki Group MoU with China Media Group (CPC Publicity Department-linked), 30 Oct 2023: news collaboration, sharing resources/images/video, exchange of economic con | https://naftemporiki.gr/english/1531029/naftemporiki-and-china-media-group-sign-memorandum-of-cooperation | medium |
| EXT:AFP → K065 | republishes | Al-Monitor 6 Nov 2026 piece on Iran's military posture/Hormuz carries AFP credit (AFP teams in Tehran and Washington); a second AFP-credited Al-Monitor item (8 Sep 2026,  | https://www.al-monitor.com/originals/2026/11/iran-says-forces-stronger-beginning-war | high |
| K086 → EXT:Glasnaya | partnership | Meduza about/republishing page describes only a CC BY policy for Meduza's own content and invites collaboration inquiries; it does not mention Glasnaya. A republication r | https://meduza.io/en/pages/about | low |
| K123 → EXT:US-public-record | derives_from | CRS In Focus IF13217 v4 (14 Oct 2026) attributes its facts to DOD/Commerce/State/GSA, USAspending.gov, executive orders, statutes, court filings, company statements and u | https://www.everycrsreport.com/files/2026-10-14_IF13217_1669944fd8dbaa6dc8228175e94de9f0a17d208e.pdf | medium |
| K244 → EXT:Washington-Times | republishes | FDD op-ed of 1 Sep 2026 (Schanzer/Mendelson) is also published by The Washington Times under the same headline; the FDD text cites no sources or links in the fetched exce | https://www.fdd.org/analysis/2026/09/01/iran-on-the-verge-of-collapse/ | medium |

## Köken aileleri ve çözülmemiş bağımlılıklar
| ID | Aile (öneri) | Çözülmemiş |
|---|---|---|
| K001 | UNKNOWN (own-field-reporting:K001 unconfirmed) | Which items are ministry/SANA copy vs own reporting; Arabic root fetch failed |
| K003 | state-statement:syria | SANA casualty figures for Nasser strike: origin unnamed; Syria Direct's cited SANA figure not confirmed at linked URL |
| K004 | own-field-reporting:K004 (one SANA-derived figure) | 20,000-company figure vs linked SANA page (1,846 in 2026) |
| K007 | own-dataset:K007 | Whether Omran's event data draws on media from other set members (Enab Baladi, SANA) UNKNOWN |
| K020 | own-reporting:haaretz (anonymous-sourced) | Haaretz original URL not captured; Anonymous source identities |
| K029 | wire:ΑΠΕ-ΜΠΕ+Reuters (for sampled foreign item) | Share of wire vs own reporting UNKNOWN; China Media Group MoU (2023) effects on content UNKNOWN |
| K031 | own-analysis:K031 | PDF text unread |
| K039 | UNKNOWN | Entire provenance profile |
| K047 | state-statement:iran (IRNA conduit) | IRNA page not read |
| K051 | UNKNOWN (relay of third-party reports likely) | Brussels-cyberattack item: original outlet unknown; Fetch failed twice |
| K065 | mixed:AFP-wire + Axios-relay + own anonymous sources | Proportion of Originals that is AFP/Axios relay; Axios original for Nov item; Article dates absent |
| K070 | state-statement:azerbaijan | No claim-level overlap tested |
| K077 | UNKNOWN | Upstream of Hetq investigative work unseen |
| K080 | own-field-reporting:K080 | Other outlets' coverage used as secondary context not enumerated |
| K083 | state-statement:russia (TASS) + feed-share with Xinhua | Volume of TASS-Xinhua feed reuse UNKNOWN |
| K086 | mixed:own+partner-republication(Glasnaya) | Meduza-Glasnaya recurrence; Share of daily news rewrites |
| K225 | UNKNOWN | Entire provenance profile |
| K105 | institution:eu-commission (primary statements) | EEAS vs Commission separation must be kept at claim level |
| K112 | own-research:K112 | Shared use of V-Dem with other set members UNKNOWN |
| K238 | own-research:K238 (convened taskforce) | Dependence on UK government publications not enumerated |
| K123 | institution:us-congress-crs (public-record synthesis) | CRS footnotes not visible; own site robots-blocked |
| K244 | own-analysis:fdd (advocacy; republished Washington Times) | No upstream evidence identifiable |
| K132 | state-statement:prc (Xinhua) + feed-share with TASS | UN casualty figure vs Gaza MoH data; Xinhua-Naftemporiki/CMG links UNKNOWN |
| K138 | UNKNOWN | Entire provenance profile (PTI/Reuters syndication likely but unseen) |
| K153 | UNKNOWN | Entire provenance profile |
| K154 | UNKNOWN | Whether Abyei coverage relies on Reuters/AP/own sourcing |
| K159 | state-statement:turkiye (primary) | Origin of '>1,600 killed since ceasefire' figure |
| K168 | wire:reuters | Reuters originals for Peskov/White House stories not opened |
| N001 | own-osint:bellingcat (shared imagery with Planet/WaPo, Tasnim, Fars; Sky News for Strava) | Imagery provider for Tasnim/Fars images |
| N002 | dataset:acled (own coded event data) | ACLED's upstream media inputs may include other set members UNKNOWN; Downstream reuse by set members not found |

Sınırlar: edge `observed_at` değerleri toplu yazım zamanıdır; sayfalar bazen araç özetiyle okundu; birkaç yukarı akış orijinali (Reuters, Axios) açılamadı.
