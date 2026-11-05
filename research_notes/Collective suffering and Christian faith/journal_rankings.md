# Journal rankings and standing (checked 2026-11-05)

Purpose: verify the standing/tier of candidate journals for the "Collective suffering and Christian faith" article series, for a Taiwan-based author.

Rules: every entry gives a source URL and the date checked. Anything not confirmed from a source is marked [not confirmed]. No rank is guessed.

Sources tried (log):
- (in progress)

## Per-journal records

(in progress — appended as verified)

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
