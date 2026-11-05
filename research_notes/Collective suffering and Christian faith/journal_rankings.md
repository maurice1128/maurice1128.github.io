# Journal rankings and standing (checked 2026-11-05)

Purpose: verify the standing/tier of candidate journals for the "Collective suffering and Christian faith" article series, for a Taiwan-based author.

Rules: every entry gives a source URL and the date checked. Anything not confirmed from a source is marked [not confirmed]. No rank is guessed.

Sources tried (log):
- JUFO REST API (jufo-rest.csc.fi) — worked; gives JUFO level + copies of Norwegian/Danish levels.
- Norwegian Register (kanalregister.hkdir.no) — worked via the site's own search index; levels for 2026.
- scimagojr.com — 403 (Cloudflare) to curl and WebFetch; Wayback snapshot of the SJR CSV exists but web.archive.org was unreachable (connection reset by proxy); resurchify/ooir 403. Used scijournal.org (SCImago-sourced; values cross-checked against Cambridge's own metric pages — identical).
- Clarivate Master Journal List — API refused scripted queries. Used LetPub Journal Selector for WoS collection membership + CiteScore.
- Cambridge Core journal-metrics pages — worked (JIF, CiteScore, SJR).
- OUP, Wiley, T&F, SAGE, Brill, EUP, MDPI sites — 403 to scripts; figures from them are via WebSearch snippets and marked [secondary].
- THCI/TSSCI — official 2022–2025 list PDFs (NSTC 人社中心), read from hss.ntu.edu.tw and university mirrors.

Bottom line first: see the **Tier table** at the end of this file.

## Per-journal records (summary; detail tables in Steps 1–5 below)

| Journal | Publisher / society | Reputation note (sourced) |
|---|---|---|
| Comparative Studies in Society and History | Cambridge UP for the Society for the Comparative Study of Society and History (U. Michigan) | JUFO 3 (top) but Norway level 1; SSCI+AHCI; JIF 1.4; Google Scholar ranks it 14th in History (Cambridge metrics page). Interdisciplinary flagship for comparative history. |
| Past & Present | OUP for the Past and Present Society | JUFO 3 every year since 2012; Norway 2; JIF 2024 2.4, 2nd of 542 in History (OUP page via search snippet). Top history journal. Bans AI-generated text (HANDOFF.md / journal_ai_policies.md). |
| Church History: Studies in Christianity and Culture | Cambridge UP for the American Society of Church History | Norway 2, JUFO 2; AHCI + ERIH PLUS (Cambridge A&I page). Citation metrics are low (SJR Q3, JIF 0.4), as is typical for church-history journals. Society flagship. |
| Social Science History | Cambridge UP for the Social Science History Association | JUFO 2, Norway 1; SSCI+AHCI; JIF 1.3. Society flagship for historical social science. |
| JSSR | Wiley for the Society for the Scientific Study of Religion | JUFO 3, Norway 2; SSCI+AHCI; CiteScore 4.2 (20th of 760 in Religious Studies). Society flagship. |
| Sociology of Religion | OUP for the Association for the Sociology of Religion | JUFO 3, Norway 2; SSCI+AHCI; CiteScore 4.1 (23/760); highest SJR in the set (1.235). |
| Review of Religious Research | SAGE (since 2023; was Springer) for the Religious Research Association | JUFO 3 (raised from 2 in 2023), Norway 2; SSCI+AHCI. |
| Journal of Contemporary Religion | Taylor & Francis (Routledge) | JUFO 3, Norway 2; AHCI; SJR Q1. T&F reports about 386 days from acceptance to online publication (WebSearch snippet) [secondary]. |
| Journal of Religious History | Wiley for the Religious History Association (Australia) | JUFO 2, Norway 1, Denmark 2; AHCI; SJR Q2. |
| Religion | Taylor & Francis | JUFO 3 (raised 2023), Norway 2; AHCI. T&F page reportedly gives an acceptance rate of 4% and about 10 days to first decision (WebSearch snippet of tandfonline.com/journals/rrel20) [secondary; probably desk-reject driven]. |
| History Compass | Wiley | Review journal (state-of-the-field essays); ESCI only; JUFO 1, Norway 1; SJR Q1. |
| Religion Compass | Wiley | Review journal; ESCI; JUFO 1, Norway 1. |
| Studies in World Christianity | Edinburgh UP (Centre for the Study of World Christianity, Edinburgh) | AHCI; JUFO 1, Norway 1; SJR Q2. Main specialist venue for non-Western Christianity. |
| International Bulletin of Mission Research | SAGE for the Overseas Ministries Study Center | ESCI; JUFO 1 (old title), Norway 1; SJR Q2 per aggregators [secondary]. |
| Review of Religion and Chinese Society | Brill (Purdue Center on Religion and Chinese Society) | ESCI; Scopus SJR Q2; not in JUFO or the Norwegian register [not confirmed]. |
| Journal of Asian Studies | **Duke UP** (since 2021; JUFO, the Norwegian register and an old Cambridge page still name Cambridge) for the Association for Asian Studies | JUFO 3, Norway 2; SSCI+AHCI. AAS flagship. Duke UP rejects mostly AI-written manuscripts (HANDOFF.md). |
| Religions (MDPI) | MDPI, open access, APC | AHCI + Scopus Q1, but **JUFO downgraded it to 0 from 2025** (still 0 in 2026); Norway 1. MDPI flyer: median 24.5 days to first decision, 4.9 days acceptance→publication (H2 2025, via WebSearch) [secondary]. Fast, high-volume; reviewers in some fields treat it with caution. |
| 臺灣史研究 | 中研院臺灣史研究所 | THCI 第一級 (2023 rating, 2024–26). The flagship for Taiwan history. |
| 新史學 | 新史學雜誌社 | THCI 第一級 (2023 rating); JUFO 1. |
| 臺灣社會學刊 | 臺灣社會學會 | TSSCI 第一級 (2024 rating, 2025–27). |
| 台灣社會學 | 中研院社會所、臺大社會系 | TSSCI 第一級 (2024 rating, 2025–27). |
| 臺灣宗教研究 | 台灣宗教學會 | THCI 第二級 (core) (2023 rating). |
| 道風：漢語基督教文化評論 | 漢語基督教文化研究所 (Hong Kong) | Not in the THCI/TSSCI lists (it is not a Taiwanese journal); JUFO 1, Norway 1. The main Sino-Christian theology journal. |
| 玄奘佛學研究 (reference) | 玄奘大學宗教與文化學系 | 第三級 = **not core** (2023 rating). |

Acceptance rates and decision times: none officially published for the Cambridge, OUP, Wiley or EUP titles found [not confirmed]. LetPub's crowd-sourced figures are not recorded.

---
## Step 1 — Finnish JUFO levels (checked 2026-11-05)

Source: JUFO REST API, `https://jufo-rest.csc.fi/v1.1/etsi.php?issn=<ISSN>` / `?nimi=<name>`, record at `https://jufo-rest.csc.fi/v1.1/kanava/<Jufo_ID>`. Records last modified 2026-01-01 (Religions: 2026-05-26). "Level" = current 2026 level. JUFO records also carry a copy of the Norwegian and Danish levels (NO / DK) — the Norwegian level is cross-checked against kanalregister.hkdir.no in Step 2.

| Journal | JUFO ID | JUFO 2026 | JUFO history note | NO (per JUFO copy) | DK | Publisher (per JUFO) |
|---|---|---|---|---|---|---|
| Comparative Studies in Society and History | 53861 | 3 | 3 since 2012 | 1 | 2 | Cambridge UP |
| Past & Present | 64748 | 3 | 3 every year 2012–2026 | 2 | 2 | Oxford UP |
| Church History | 53455 | 2 | 2 | 2 | 1 | Cambridge UP |
| Social Science History | 67259 | 2 | 2 | 1 | 1 | Cambridge UP |
| JSSR | 59416 | 3 | 3 | 2 | 2 | Wiley |
| Sociology of Religion | 67339 | 3 | 3 | 2 | 2 | Oxford UP |
| Review of Religious Research | 66240 | 3 | raised 2→3 in 2023 | 2 | 2 | Springer Nature (note: journal moved to SAGE in 2023 — see below) |
| Journal of Contemporary Religion | 60048 | 3 | 3 | 2 | 2 | Taylor & Francis |
| Journal of Religious History | 61540 | 2 | 2 | 1 | 2 | Wiley |
| Religion | 66035 | 3 | raised 2→3 in 2023 | 2 | 2 | Taylor & Francis |
| History Compass | 57137 | 1 | 1 | 1 | – | Wiley |
| Religion Compass | 84685 | 1 | 1 | 1 | – | Wiley |
| Studies in World Christianity | 67876 | 1 | 1 | 1 | 1 | Edinburgh UP |
| International Bulletin of Mission Research | 58008 (listed under old title "International bulletin of missionary research", ISSN 0272-6122) | 1 | 1 | – | – | OMSC (now SAGE) |
| Review of Religion and Chinese Society | — | not found in JUFO by title or ISSN 2214-3947/2214-3955 [not confirmed] | | | | |
| Journal of Asian Studies | 59665 | 3 | raised 2→3 in 2023 | 2 | 2 | Cambridge UP |
| Religions (MDPI) | 76454 | **0** | 1 through 2024; **downgraded to 0 from 2025**, still 0 in 2026 | 1 | – | MDPI |
| 新史學 New History | 63979 (ISSN 1023-2249) | 1 | 1 | – | – | 新史學雜誌社 |
| 道風 Logos & Pneuma | 62781 (ISSN 1023-2583) | 1 | 1 | 1 | – | Tao Fong Shan Christian Centre |
| 臺灣史研究, 臺灣社會學刊, 臺灣社會學, 台灣宗教研究, 玄奘佛學研究 | — | not found by romanised/English title searches [not confirmed — likely unlisted] | | | | |

JUFO scale: 1 = basic, 2 = leading, 3 = top; 0 = does not meet level-1 criteria.

---
## Step 2 — Norwegian Register (Kanalregisteret, HK-dir) levels (checked 2026-11-05)

Source: kanalregister.hkdir.no — queried through the site's own public search index (the Typesense collection `uhr_tidsskrift_cache` that the search page at https://kanalregister.hkdir.no/sok uses), by ISSN. All records returned `aar` = 2026. Record page pattern: `https://kanalregister.hkdir.no/publiseringskanaler/info/tidsskrift?pid=<id>` [page URL pattern not opened; ids below are the register's record ids]. Level 2 = top ~20% of a field; 1 = approved scholarly; 0 = not approved.

| Journal | Register id | Norwegian level 2026 | Publisher per register |
|---|---|---|---|
| Comparative Studies in Society and History | 439327 | **1** | Cambridge UP |
| Past & Present | 445606 | **2** | OUP, Past and Present Society |
| Church History: Studies in Christianity and Culture | 439084 | **2** | Cambridge UP |
| Social Science History | 447012 | **1** | Cambridge UP |
| Journal for the Scientific Study of Religion | 442314 | **2** | Wiley, Society for the Scientific Study of Religion |
| Sociology of Religion | 447044 | **2** | OUP |
| Review of Religious Research | 446500 | **2** | "Springer" (register publisher field not updated) |
| Journal of Contemporary Religion | 442700 | **2** | Taylor & Francis |
| Journal of Religious History | 342223 | **1** | Wiley, Religious History Association |
| Religion | 446381 | **2** | Taylor & Francis |
| History Compass | 479850 | **1** | Wiley |
| Religion Compass | 471669 | **1** | Blackwell |
| Studies in World Christianity | 468910 | **1** | Edinburgh UP |
| International Bulletin of Mission Research | 505702 | **1** | SAGE |
| Review of Religion and Chinese Society | — | not found by title or ISSN 2214-3947 [not confirmed] | |
| Journal of Asian Studies | 341197 | **2** | Cambridge UP |
| Religions (MDPI) | 477528 | **1** | MDPI |
| 道風 Logos & Pneuma ("Dao feng: Hanyu shenxue xuekan") | 481476 | **1** | Institute of Sino-Christian Studies |
| 新史學, 臺灣史研究, 臺灣社會學刊, 臺灣社會學, 台灣宗教研究, 玄奘佛學研究 | — | not found by ISSN (新史學 1023-2249) or romanised title [not confirmed — apparently unlisted] | |

Cross-check: these match the Norway_Level copies in the JUFO records (Step 1) for every journal both list. Note CSSH is only level 1 in Norway despite JUFO 3 / DK 2.

---
## Step 3 — Scimago SJR (checked 2026-11-05)

Access log: scimagojr.com returns HTTP 403 (Cloudflare challenge) to curl and WebFetch, including `journalrank.php?out=xls` and `journal_img.php`. A Wayback snapshot of the full SJR CSV exists (`http://web.archive.org/web/20251026083950/https://www.scimagojr.com/journalrank.php?out=xls`, per archive.org/wayback/available) but web.archive.org connections were reset by the network proxy, so it could not be read. resurchify.com and ooir.org: 403. **Source actually used: scijournal.org** journal pages (state "SJR and H-Index data comes from SCImago"; page attribute `data-quartile` = best SJR quartile; data year 2025, i.e. SJR 2025 release). This is a third-party mirror — the per-category quartile was NOT available, only the best quartile. Treat as [secondary source; verify on scimagojr.com in a browser].

| Journal | scijournal.org URL | Best SJR quartile (2025) | SJR 2025 / 2024 / 2023 | Scopus subject areas (broad) |
|---|---|---|---|---|
| CSSH | https://www.scijournal.org/comparative-studies-in-society-and-history | Q1 | 0.700 / 0.477 / 0.424 | Arts & Humanities; Social Sciences |
| Past & Present | https://www.scijournal.org/past-present | Q1 | 0.788 / 0.854 / 0.770 | Arts & Humanities; Social Sciences |
| Church History | https://www.scijournal.org/church-history | **Q3** | 0.117 / 0.147 / 0.112 | Arts & Humanities; Social Sciences |
| Social Science History | https://www.scijournal.org/social-science-history | Q1 | 0.277 / 0.269 / 0.381 | Arts & Humanities; Social Sciences |
| JSSR | https://www.scijournal.org/journal-for-the-scientific-study-of-religion | Q1 | 1.068 / 1.081 / 0.979 | Arts & Humanities (+ Social Sciences per Scopus) |
| Sociology of Religion | https://www.scijournal.org/sociol-relig | Q1 | 1.235 / 1.144 / 0.968 | Arts & Humanities; Social Sciences |
| Review of Religious Research | https://www.scijournal.org/rev-relig-res | Q1 | 0.548 / 0.778 / 0.557 | Arts & Humanities |
| Journal of Contemporary Religion | https://www.scijournal.org/j-of-contemporary-religion | Q1 | 0.329 / 0.309 / 0.414 (T&F's own page also gives SJR 2025 = 0.329) | Arts & Humanities; Social Sciences |
| Journal of Religious History | https://www.scijournal.org/j-of-religious-history | **Q2** | 0.134 / 0.129 / 0.108 | Arts & Humanities |
| Religion | https://www.scijournal.org/religion | Q1 | 0.507 / 0.493 / 0.434 | Arts & Humanities; Social Sciences |
| History Compass | https://www.scijournal.org/history-compass | Q1 | 0.253 / 0.275 / 0.209 | Arts & Humanities |
| Religion Compass | https://www.scijournal.org/religion-compass | Q1 | 0.302 / 0.206 / 0.140 | Arts & Humanities |
| Studies in World Christianity | https://www.scijournal.org/studies-in-world-christianity | Q2 | 0.177 / 0.181 / 0.184 | Arts & Humanities |
| IBMR | not found on scijournal.org | [not confirmed] | | |
| Review of Religion and Chinese Society | https://www.scijournal.org/review-of-religion-and-chinese-society | Q2 | 0.145 / 0.296 / 0.126 (coverage listed 2014–2024) | [not shown] |
| Journal of Asian Studies | https://www.scijournal.org/j-asian-stud | Q1 | 0.258 / 0.350 / 0.297 | Arts & Humanities; Social Sciences |
| Religions (MDPI) | https://www.scijournal.org/religions | Q1 | 0.444 / 0.391 / 0.368 | Arts & Humanities |

Caution: SJR in humanities categories (History, Religious Studies) is low in absolute terms, so Q1 there is easy for any well-cited journal — Religions (MDPI) and the Compass review journals are Q1 by this measure. Quartile alone does not separate flagship from mid-tier in these fields; use JUFO/Norwegian levels for that. scijournal.org also shows an "Impact Factor" figure but its values (e.g. JAS 0.41) do not match Clarivate JIFs, so it is NOT recorded as a JIF.

---
## Step 4 — Web of Science indexing, Scopus, CiteScore, JIF (checked 2026-11-05)

Access log: Clarivate Master Journal List (mjl.clarivate.com) search API refuses scripted queries (HTTP 400; needs browser session/captcha). Publisher sites (OUP, Wiley, T&F, SAGE, Brill, EUP, MDPI) return 403 to scripts. **Source used for WoS index membership + CiteScore: LetPub Journal Selector** (`https://www.letpub.com/journal-selector/journal/<id>`), field "Indexing (SCI collection)" and "CiteScore / CiteScore Rank". LetPub is a third-party aggregator (Chinese editing company) that mirrors the Clarivate collection lists — reliable for membership but can lag a year. Cambridge Core "journal metrics" pages were reachable and give Clarivate JIF + CiteScore + SJR directly (and their SJR values match scijournal.org exactly, which validates Step 3's mirror).

| Journal | WoS index (LetPub) | Scopus | CiteScore (LetPub; Scopus rank in category) | JIF (source) | LetPub URL |
|---|---|---|---|---|---|
| CSSH | SSCI + AHCI | yes | 2.4 (History 80/1936; Sociology & Pol Sci 538/1530) | 2-yr JIF **1.4**, 5-yr 1.6 (Cambridge metrics page, https://www.cambridge.org/core/journals/comparative-studies-in-society-and-history/information/about-this-journal/journal-metrics ; also "Google Scholar: ranked 14th in History") | https://www.letpub.com/journal-selector/journal/12352 |
| Past & Present | SSCI + AHCI | yes | 3.7 (History 28/1936; Cultural Studies 93/1434) | JIF 2024 **2.4**, rank **2/542 in History** (OUP About page as quoted by WebSearch snippet of https://academic.oup.com/past/pages/About — page itself 403 to scripts) [secondary] | https://www.letpub.com/journal-selector/journal/12239 |
| Church History | AHCI | yes | 0.4 (History 863/1936; Religious Studies 368/760) | 2-yr JIF **0.4**, 5-yr 0.5; SJR 0.117 (Cambridge metrics page, https://www.cambridge.org/core/journals/church-history/information/about-this-journal/journal-metrics). Cambridge A&I page lists **ERIH PLUS** and Clarivate AHCI (https://www.cambridge.org/core/journals/church-history/information/about-this-journal/abstracting-and-indexing) | https://www.letpub.com/journal-selector/journal/15369 |
| Social Science History | SSCI + AHCI | yes | 1.3 (History 227/1936) | 2-yr JIF **1.3**, 5-yr 1.2 (Cambridge metrics page, https://www.cambridge.org/core/journals/social-science-history/information/about-this-journal/journal-metrics) | https://www.letpub.com/journal-selector/journal/14161 |
| JSSR | SSCI + AHCI | yes | 4.2 (Religious Studies 20/760) | JIF 2022 2.4, Sociology 59/149 (Wikipedia citing JCR) — 2025 JIF [not confirmed] | https://www.letpub.com/journal-selector/journal/11829 |
| Sociology of Religion | SSCI + AHCI | yes | 4.1 (Religious Studies 23/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/12837 |
| Review of Religious Research | SSCI + AHCI | yes | 2.9 (Religious Studies 31/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/13188 |
| Journal of Contemporary Religion | AHCI | yes | 1.6 (Religious Studies 83/760) | [not confirmed]; T&F reports SJR 2025 0.329 (WebSearch snippet) | https://www.letpub.com/journal-selector/journal/15003 |
| Journal of Religious History | AHCI | yes | 0.6 (History 621/1936; Religious Studies 265/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/17455 |
| Religion (T&F) | AHCI | yes | 2.5 (History 71/1936) | [not confirmed] | https://www.letpub.com/journal-selector/journal/13913 |
| History Compass | **ESCI** | yes | 1.5 (History 164/1936) | (ESCI journals now get a JIF but no SSCI/AHCI status) [value not confirmed] | https://www.letpub.com/journal-selector/journal/14401 |
| Religion Compass | **ESCI** | yes | 0.9 (Religious Studies 160/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/16977 |
| Studies in World Christianity | AHCI | yes | 0.4 (Religious Studies 359/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/18999 |
| IBMR | **ESCI** | yes | 0.6 (Religious Studies 251/760) | [not confirmed]; aggregators give best SJR quartile Q2 (researcher.life / resurchify, via WebSearch) [secondary] | https://www.letpub.com/journal-selector/journal/18585 |
| Review of Religion and Chinese Society | **ESCI** | yes | 1.2 (Religious Studies 120/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/39644 |
| Journal of Asian Studies | SSCI + AHCI | yes | 1.1 (History 304/1936) | Cambridge page: "Impact Factor rankings are not currently available" [JIF not confirmed] | https://www.letpub.com/journal-selector/journal/12668 |
| Religions (MDPI) | AHCI (+ DOAJ) | yes | 1.3 (Religious Studies 109/760) | [not confirmed] | https://www.letpub.com/journal-selector/journal/24832 |

Note on Review of Religious Research: published by SAGE for the Religious Research Association (SAGE journal home https://journals.sagepub.com/home/rrr and RRA site https://www.rraweb.org/journal-review-of-religious-research, via WebSearch 2026-11-05; ISSN portal records a 2023-01-01 transfer between Springer and SAGE). The Norwegian register, JUFO and LetPub still show Springer.

Note on Journal of Asian Studies: published by Duke University Press since 2021 (see HANDOFF.md / journal_ai_policies.md). Cambridge Core's JAS page is the archive, which is why it says 'Impact Factor rankings are not currently available'.

---
## Step 5 — THCI / TSSCI (Taiwan), checked 2026-11-05

System (since the 2022/2023 reform; per the official list headers): the NSTC Research Center for Humanities and Social Sciences (人文社會科學研究中心, 人社中心, hosted at NTU, https://www.hss.ntu.edu.tw) rates journals by 學門 on a 3-year rotation. Rating **第一級 / 第二級 = core journal** (THCI if the 學門 is humanities, TSSCI if social sciences). **第三級 = not core** ("無 THCI 第三級或 TSSCI 第三級"). The old "THCI Core vs THCI 收錄" distinction no longer exists.

Lists read (PDFs downloaded and converted to text):
- **2023 list** (文學一、文學二、語言學、**歷史學**、**哲學（含宗教研究）**; valid **2024-01-01 to 2026-12-31**): mirror at https://chinese.thu.edu.tw/upload/newspaper_upload/2023%E5%B9%B4%E8%A9%95%E6%AF%94%E7%B5%90%E6%9E%9C%E6%9A%A8%E6%A0%B8%E5%BF%83%E6%9C%9F%E5%88%8A%E5%90%8D%E5%96%AE.pdf (also at chinese.nccu.edu.tw/upload/36/doc/26314/2023年評比結果暨核心期刊名單.pdf)
- **2024 list** (藝術學、人類學及族群研究、**社會學及社福社工（含傳播學）**、心理學、法律學、管理學; valid **2025-01-01 to 2027-12-31**): mirror at https://lfes.chc.edu.tw/storage/074719/posts/514/files/07-7-2024年評比結果暨核心期刊名單 .pdf
- **2025 list** (教育、政治、經濟、區域研究及地理 + 綜合類; valid 2026–2028): https://rc052.ndhu.edu.tw/var/file/89/1089/img/457840939.pdf — none of the target journals appear in it.
- 2022 list (hss.ntu.edu.tw) also checked — superseded.
Official site hss.ntu.edu.tw hosts the originals (the 2022 PDF downloaded from it directly).

| Journal | Publisher (per list) | 學門 | Latest rating | Core status | Valid | Source |
|---|---|---|---|---|---|---|
| 臺灣史研究 Taiwan Historical Research | 中央研究院臺灣史研究所 | 歷史學 | **第一級** | **THCI** | 2024–2026 | 2023 list |
| 新史學 New History | 新史學雜誌社 | 歷史學 | **第一級** | **THCI** | 2024–2026 | 2023 list |
| 臺灣社會學刊 Taiwanese Journal of Sociology | 臺灣社會學會 | 社會學及社福社工 | **第一級** | **TSSCI** | 2025–2027 | 2024 list |
| 台灣社會學 Taiwanese Sociology | 中研院社會所、臺大社會系 | 社會學及社福社工 | **第一級** | **TSSCI** | 2025–2027 | 2024 list |
| 臺灣宗教研究 Taiwan Journal of Religious Studies | 台灣宗教學會 | 哲學（含宗教研究） | **第二級** | **THCI** | 2024–2026 | 2023 list |
| 玄奘佛學研究 Hsuan Chuang Journal of Buddhist Studies | 玄奘大學宗教與文化學系 | 哲學 | **第三級** | **not core** | 2024–2026 | 2023 list |
| 道風：漢語基督教文化評論 (Hong Kong) | 漢語基督教文化研究所 | — | not in the 2022/2023/2024/2025 lists | not rated [not confirmed elsewhere] | | grep of all four lists |

Also in the 2023 philosophy/religion list for context: 華人宗教研究 (政大華人宗教研究中心) 第三級; 臺大佛學研究, 佛光學報, 法鼓佛學學報 第二級.

Timing caution: the 歷史學 and 哲學 ratings expire 2026-12-31. The next round (evaluated in 2026, list expected around the turn of 2026/27, valid 2027–2029) was not yet found online on 2026-11-05 [not confirmed]. Re-check before citing THCI status for a 2027 submission.
