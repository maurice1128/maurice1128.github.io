# Independent audit of the *Social Science History* submission

Audit date: 2026-11-11. Targets: `manuscript_ssh.md`, `tables_ssh.md`, `supplement_ssh.md`, `title_page_ssh.md` (rules: `../_SSH_GUIDELINES.md`). Nothing in the manuscript, the tables, the supplement or the data was edited. This file is the only file written.

## How the audit was done

- **Numbers.** The three analysis scripts were re-run with `python3 -I` from a scratch directory against the committed `data.csv` files (`husting_wills`, `gild_foundations`, `wpa_religion`). Every figure in the four target files was compared with the printed output. A few statistics were also recomputed by hand (Woolf interval for the odds ratio, a pooled two-proportion test, Fisher tests, κ on a subset).
- **Data.** Thirty rows of each `data.csv` were drawn with fresh seeds and read against the source: British History Online roll pages for the wills; Internet Archive page images of Westlake (rotated, read by Tesseract, one page also viewed as an image) for the gilds; Project Gutenberg text at the stated lines for the interviews. All 85 BHO roll pages were also downloaded to test two rules across the whole population.
- **Quotations.** Primary texts were downloaded again (Internet Archive `_djvu.txt`, Project Gutenberg, pct.org.tw, china.usc.edu, BHO) and searched directly.
- **References.** 17 articles by Crossref DOI, 26 books and one dissertation by Open Library, 22 primary editions from the downloaded texts or title pages (two of them also in Open Library). Cross-checked with `reports/references_master.md` and `reports/audit/references_status.tsv`.
- **Methods.** `git log` and `git show` on the evidence folders, the codebooks, and the reliability files.

**Limits of this audit.** Latin texts were checked against OCR, not page images (Westlake excepted). Dittmar and Meisenzahl (2020) is paywalled; its quotation was checked against the project's full-text notes only. Bottan and Perez-Truglia's page numbers, li Muisis pp. 240, 243 and the curates on p. 258, the page numbers of Islip's 1362 constitution, and the TSCS table rest on the earlier audit (`../audit_manuscript.md`), which this audit did not repeat. Monographs were checked for existence and for their generally known thesis, not read.

Source keys: **W2/W3** Wilkins vols. 2 and 3; **RAI** Raine; **AVE** Thompson (Avesbury); **LEM** Lemaître; **GER** Géraud; **RAY** Raynaldus vol. 25; **CCJ** Jones 1842; **LIB** Liberty County report; **JAC** Jacobs (Gutenberg 11030); **DOU** Douglass (Gutenberg 23); **WAL** Walker; **ALL** Allen; **JA** Jones and Allen 1794; **WES** Westlake page images; **SMI** Smith 1870; **BHO** British History Online; **PG** Project Gutenberg slave-narrative files; **CR** *Christian Recorder* scans; **PCT** pct.org.tw.

---

## 1. Numbers

"Script" means the output of the dataset's `analysis.py` on the committed data. About 780 values were compared (about 120 in the manuscript text, 330 in the tables, 330 in the supplement).

### 1A. Mismatches and near-mismatches

| # | Where | Manuscript value | Script or source value | Match? | Note |
|---|---|---|---|---|---|
| N1 | §4.3 | "No class of church recipient declines in any period." | Table 2 Panel B (same script): monasteries, nunneries, canons 22.9% → 15.8% from 1320–48 to 1349–60 (−7.1 points, p = .13); St. Paul's 21.4% → 20.2% from 1361–75 to 1376–1400. All wills: St. Paul's 18.2% → 17.6%. | **No** | The text contradicts its own table. True statement: no class shows a statistically significant decline. G1 ("no class of church recipient fell") and §7.1 ("did not fall back in 1376–1400") need the same care. |
| N2 | Title page | 11,112 words = main text 9,522 + footnotes 233 + references 1,357 | `build/wordcount.py manuscript_ssh.md`: main 9,564; footnotes 236; references 1,436; total 11,236 | **No** | Under the 12,000 limit either way. Regenerate after revision. |
| N3 | Supplement, opening and S5 | "Every figure is printed by the analysis script"; "reprints every figure in the article and in this supplement" | Not true of S2.2. The script prints the post-adjudication values (funeral κ 0.84, masses 0.84, lights 0.94, relief 1.00, alms 0.82, feast 0.81, other 0.71, founders 0.94). The blind first-pass values in S2.2 and §3.2 (0.80, 0.80, 0.88, 0.78, 0.70, 0.39, 0.70, 0.88) exist only in `reliability_firstpass.txt`. The S2.3 items "38/40 … κ 0.85", "0.63 among the 21", the 5/8/7 split of disagreements, and "crossed p = 0.05 only after six interviewer attributions were corrected" come from `reliability_independent.md` and `interviewer_race_corrections.md`. | **No** (claim) | The first-pass numbers match `reliability_firstpass.txt` exactly, and κ = 0.63 was recomputed here. Reword the claim, or add the first-pass table to the script. |
| N4 | §4.3, S3.1 | mean of 21.2 wills a year in 1340–47 | 170/8 = 21.25 | rounding | Prints as 21.2 by round-half-even. Give 21.3 or 21.25. |
| N5 | Table 4 Panel A and D | 17/400 = 4.2%; 13/400 = 3.2% | 4.25%; 3.25% | rounding | Same artifact. Use 4.3 and 3.3, or two decimals. |
| N6 | S3.1 | "1369, the third pestilence: no rise." | 1368: 28; 1369: 26. Mean of 1363–67: 14.0. Mean of 1370–73: 11.5. | **Doubtful** | Sharpe (1889: xxvii) says "no appreciable increase", but the script's own counts are about double the surrounding years. Give the counts. |
| N7 | §4.4 | pestilence mentions: "most record disruption" | Of the 8: disruption in 4 (certs. 203, 251, 391, 471); a contingency clause in 1 (27); gifts of land "about the time of the first pestilence" in 1 (13); ordinances "immediately after" in 1 (36); a foundation in 1 (279) | **Loose** | "Half record disruption." |
| N8 | Abstract | "Five regularities emerge." | The abstract then states four (demand; responses; answers of authorities; fading and endurance). G5 is absent. | Inconsistent | Say "Four regularities and one open question". |
| N9 | Table 2 Panel B, last row | mean 1.49 [1.05–1.93] etc. under the header "Wilson 95% CI" | Script: "95% CI, normal approx." | Label | Say so in the note. |
| N10 | §5.2 | negative attitudes "occur in 14 of 23 such narratives" | 25 narratives report obedience-only preaching; 23 of them state an attitude | Wording | "in 14 of the 23 that also state an attitude". |

### 1B. Manuscript text: values that match

| Section | Manuscript value | Script value | Match? |
|---|---|---|---|
| Abstract, §1, §3.2 | 1,979 wills; 509 gilds; 400 interviews; 206 describe worship | 1,980 entries less 1 empty = 1,979; 509; 400; 206 | Yes |
| §3.2 wills | random tenth = 198; κ parish 0.86, chantry 0.99, fraternity 0.95, friars 0.93, monastic 0.80; "0.80 to 1.00 for the main categories" | 198; 0.86, 0.99, 0.95, 0.93, 0.80; obit, masses, lights, charity 1.00 | Yes (named chaplain 0.57 and "pious uses" 0.83 are in S2.1 only) |
| §3.2 gilds | 51 recoded; complete agreement on dates, pestilence, clerical governance; κ 0.80–0.91 for funerals, masses, lights, chaplains; feasts 0.39; Smith 42 matched, 37 agree | `reliability_firstpass.txt`: 0.80, 0.80, 0.88, 0.91; 0.39. Script: 42, 37 | Yes (first-pass file; see N3) |
| §3.2 interviews | 2,143 segmented; 1,418 (66.2%); 400; κ 1.00 worship control and obedience; faith 0.83; attitude 0.82; postwar 0.64; prayer for freedom untestable | identical | Yes |
| §4.3 | 356 wills in 1349; 130 in 1361; mean 19.3 in 1350–59; medians 74 and 154 words | identical | Yes |
| §4.3 | n = 83, 273, 332, 252 | 83, 273, 332, 252 | Yes |
| §4.3 | parish 28.9 → 49.1 → 69.9; friars 6.0 → 9.5 → 22.6; fraternities 2.4 → 5.5 → 12.0 | identical | Yes |
| §4.3 | parish +20.8, friars +13.1, both p < .001; fraternities +6.6, p = .005 | +20.8 (χ² 27.11); +13.1 (18.39); +6.6 (7.79, p = .005) | Yes |
| §4.3 | chantries 38.6, 41.0, 41.3, 50.8 | identical | Yes |
| §4.3 | private holders 88.3 → 64.1; parish or lay body 4.3 (2.2–8.2) → 29.4 (22.8–37.1) | identical | Yes |
| §4.3 | summaries ≤120 words: chantries flat; friars 0.7 → 13.5 | chantry 17.8, 21.6, 22.2, 17.3; friars 0.7 → 13.5 | Yes |
| §4.3 | 235 women; one plague mention; mean kinds 1.49 → 3.41 | 85+84+33+33 = 235; 1 (HW1563); 1.49, 3.41 | Yes |
| §4.4 | three-quarters from four counties; 41 from London | 386/509 = 75.8%; 41 | Yes |
| §4.4 | of 500: lights 80.2; masses 58.0; funerals 50.0; chaplain 37.6; relief 35.4; any provision for the dead 70.4 | identical | Yes |
| §4.4 | founders 104: 52 lay, 42 craft (90%), 6 mixed, 4 clerical; clerical governance 11 of 509 (2.2%); 73 fabric or ornaments | identical (94/104 = 90.4%) | Yes |
| §4.4 | 286 dated 1300–89; 235 in 1349 or later (82.2%; 77.3–86.2); pestilence 8 (1.6%) | identical | Yes |
| n. 2 | dissolution rate about 4 percent | h = 0.0389 | Yes |
| §5.2 | 110 (53.4%); 26; 17; 3; 50; 92 of 206 (44.7%; 38.0–51.5) | identical | Yes |
| §5.2 | preaching 25 of 37 (67.6%; 51.5–80.4); attitude 174: 22 negative (12.6%), 39 positive, 113 neutral; 14 of 23 and 0 of 9 | identical | Yes |
| §5.2 | faith: 72 state, 3 deny; 44/92 (47.8%) against 21/114 (18.4%); OR 4.06 (2.17–7.59); Mantel–Haenszel 3.36; strict 22.8 against 14.0, OR 1.81 (0.88–3.72) | identical (Woolf interval recomputed) | Yes |
| §5.2 | prayer for freedom 13, 10 under Black control | 13; 10 (2 not stated, 1 not Black control) | Yes |
| §5.2 | median age 83; 53 Black interviewers; 7/21 (33.3%) against 15/153 (9.8%), Fisher p = .007; ten comparisons; two states | 83 (n = 301); 53; identical; 8 + 2 = 10; Arkansas 30, Florida 12 | Yes |
| §5.5 | postwar church 106; control judged 46; Black-run 41; conversion dated 28, after 1865 in 25 | identical | Yes |
| §6.1, G1, §6.3, §7.1 | 50 mixed; secret worship in 28 of 400; 110; 44.7%; 39 of 174; 28 and 25 | identical | Yes |

### 1C. Tables and supplement: blocks compared

| Block | Values | Result |
|---|---|---|
| Table 2 Panel A (n, burial stated, median words, any bequest) | 16 | All match (11.2, 49.7, 84.1, 85.1 from 83/739, 273/549, 332/395, 252/296) |
| Table 2 Panel B (12 bequest rows: 4 shares, 4 intervals, 2 changes, 2 p-values each; plus the means) | 152 | All match |
| Table 2 Panel C (5 rows by 4 periods, with intervals; n = 188, 193, 161, 153) | 44 | All match |
| Table 3 Panels A–C and notes | about 50 | All match (51/235; 41/206 = 83.4% [78.3–87.5]; 300 = 58.9%; 14 before 1300; 130; 36; 0.039) |
| Table 4 Panels A–E | about 70 | All match, bar the rounding in N5 |
| Table 1 and Table 5 figures (37.6%; 88.3/64.1; 4.3/29.4; 50.0; 80.2; 35.4; 66, 28, 110, 92 of 400 or 206; 90% of 104; 2.2%; 41 of 46) | 20 | All match |
| Supplement S1 (1,980 and 1,979; 1,550 with a will date; 509 on 471; 2,178 and 2,143; 64.1–68.1; 17 state quotas summing to 400) | 28 | All match |
| S2.1 (15 variables by 6 columns) | 90 | All match |
| S2.2 | 27 | Match `reliability_firstpass.txt`; post-adjudication sentence matches the script (92%, 92%, 100%, 92%, 96%, κ 0.81) |
| S2.3 | 36 | Match script and `second_coder.csv` (20/20, 3/3, 6/6, 1/1, 24/24, 5/5, 21/21, 2/3, 11/14, 12/19, 2/3, 3/6); κ 0.63 recomputed |
| S3.1 (13 rows by 4; enrollment counts; 5 sensitivity rows; by sex) | about 90 | All match, bar N4 and N6 |
| S3.2 (decades; survivorship; heaping 22 of 39, 6 exact in 1349; purposes by period with 8 Fisher p-values; 8 certificate numbers; coverage) | about 75 | All match |
| S3.3 (five modes; χ² 25.8, df 4; seven robustness rows; interviewer table of 8 rows; ages; hearsay 21) | about 60 | All match |
| S4 (four locators) | 4 | All match the Gutenberg lines |

---

## 2. Data spot-checks

### 2A. London wills (30 random rows; seed 987654; source BHO)

| Will | Roll | Verdict | Finding |
|---|---|---|---|
| HW0242 Redgrave | 57(19) | minor | Chantry right. `chantry_temporary` = 1 is wrong ("for life" belongs to the wife's tenure). Variable not used in the article. |
| HW1150 Hatfeld | 79(5) | debatable | Burial in the abbey church of Lesnes is typed "parish" (only "stated" is used). `parish` = 1 rests on a parish church named as the site of a chantry. |
| HW0797 Hicche | 76(86) | debatable | Obit, mass, lights right. The "Wardens of the Honour of S. Anne" hold the endowment, yet holder = private and fraternity = 0. |
| HW0447 Gauger | 63(89) | sound | |
| HW1428 Oxon | 90(36) | sound | |
| HW1228 Gloucestre | 83(110) | sound | "various religious orders and houses" coded monastic. |
| HW0770 Barton | 76(37) | sound | |
| HW0516 Hynde | 65(41) | sound | |
| HW0696 Bolyngbrok | 74(37) | debatable | `parish` = 1 rests on a bequest to the vicar by name. |
| HW0243 Atte Brok | 57(20) | sound | |
| HW0004 Bolyton | 48(104) | sound | |
| HW0480 Westmenstre | 63(269) | sound | Rents "due from the Friars Minors" rightly not coded as a gift to friars. |
| HW1672 Claverynge | 103(193) | sound | |
| HW1866 Twyford | 119(74) | sound | Holder = parish body and lay corporate body, both right. |
| HW1103 Rameseye | 78(15) | sound | |
| HW1144 Stokwell | 78(225) | **error** | Text: "TO be buried in the church of S. Giles". Coded `burial_site` = none_stated, so the will is wrongly left out of the main subset. "every religious order around the City" is coded neither friars nor monastic, unlike HW1228. |
| HW0324 Prodhome | 59(93) | minor | `chantry_temporary` = 1 wrong, as in HW0242. |
| HW0155 Massheberi | 55(23) | sound | |
| HW0383 Halgheford | 61(52) | **error** | One body, the priory and hospital of St. Mary without Bishopsgate, is counted as both monastic and hospital. |
| HW1730 Lovel | 108(72) | **error** | `monastic` = 1 rests on "held for a term under the Abbot and Convent of Westminster", a tenure clause. Holder should be the hospital (church corporate), not lay corporate. |
| HW0063 Mohun | 51(112) | sound | |
| HW0880 Egelof | 76(195) | sound | |
| HW1950 Atte Wode | 126(54) | sound | |
| HW1899 Boterwyk | 122(32) | sound | |
| HW0065 Craye | 51(117) | sound | |
| HW1852 Silkeston | 118(38) | sound | |
| HW1309 Snodilond | 89(84) | debatable | `fraternity` = 1 for a chantry "for the welfare of the brethren of the Fraternity". |
| HW1390 Forneux | 89(222) | sound | |
| HW0654 Farndon | 71(113) | sound | |
| HW0948 Northall | 76(299) | sound | |

Result: 21 sound, 4 debatable, 2 wrong only on an unused variable, 3 wrong on a variable the article uses. The errors fall on the monastic, hospital and holder codes, which the supplement already reports as the weakest (κ 0.80; holder not double-coded).

**Whole-population tests (all 85 BHO pages, 1,985 entries parsed).**

- *Burial clause.* The rule misses 5 wills, all enrolled 1349–60, where BHO prints "TO be buried" or "To he buried" (HW0742, HW1026, HW1117, HW1139, HW1144). No false positives. The 1349–60 subset should be 278, not 273. The effect on Table 2 is negligible, but the variable defines the main comparison and was never double-coded; say so.
- *Plague.* A search for pestilence, plague, mortality and epidemic finds one entry only, HW1563 (Roll 97 (15), enrolled 1369). The article's "only one summary mentions plague" is confirmed.

### 2B. Gild returns (30 random rows; seed 424242; source Westlake page images)

| Unit | Cert. | Page | Verdict | Finding |
|---|---|---|---|---|
| G0003 | 3(a) Bottisham | 138 | sound | "attend mass for a dead brother" coded masses, not funeral: defensible. |
| G0024 | 17 Ely | 142 | sound | |
| G0072 | 53 Chelmsford | 151 | sound | |
| G0080 | 61 Cirencester | 152 | sound | |
| G0095 | 74 Amcotts | 155 | sound | |
| G0102 | 81 Binbrooke | 156 | **error** | "Same purpose and plan as in 79" (a priest to sing daily mass) is not expanded. Every purpose code is 0 and `inherit_from` is blank. Cert. 80 (G0101) has the same defect. |
| G0104 | 83 Boston | 156 | sound | "Renewed 1349" classed as a document date, period before 1349: reasonable. |
| G0117 | 95 Crowland | 159 | **error** | "the alderman presents alms … to each poor man who asks it" yet `alms_general` = 0. |
| G0139 | 117 Holbeach | 164 | minor | The "craft regulation" tag has no support in the entry. |
| G0158 | 136 Lincoln | 168 | sound | |
| G0163 | 140(i) Lincoln | 169 | sound | |
| G0175 | 151 Lincoln, Barbers | 172 | sound | |
| G0178 | 154 Lincoln, Masons | 173 | sound | |
| G0196 | 170 Springthorpe | 177 | sound | |
| G0207 | 181(i) Whaplode | 178 | sound | |
| G0219 | 189 London | 181 | debatable | "They pay the Carmelites 10s. a year for celebrating" coded chaplain = 0. |
| G0233 | 203 London, St. Bride's | 184 | sound | |
| G0245 | 214 London, Barbers | 187 | **error** | "All attend dirge and mass, and month's mind for a dead brother" yet `funeral` = 0. |
| G0259 | 228 Clenchwarton | 190 | sound | |
| G0269 | 238 Lynn | 192 | sound | |
| G0279 | 248 Lynn | 194 | sound | |
| G0284 | 253 Lynn | 194–95 | not fully checked | Entry runs on to the next page, which was not fetched. |
| G0340 | 309 Outwell | 206 | **error** | "If a brother die they assemble and carry him to the church" yet `funeral` = 0. |
| G0360 | 328(ii) Swaffham | 210 | sound | Cross-reference to 327 expanded correctly. |
| G0373 | 338 Upwell | 212–13 | not fully checked | Entry begins on the previous page. |
| G0439 | 402 Bury | 226 | sound | |
| G0452 | 415 Bury | 227 | debatable | `chaplain` = 1 seems to rest on "Founded by certain priests". |
| G0469 | 432 Stradishall | 230 | sound | |
| G0481 | 444 Bedall | 232 | sound | |
| G0501 | 463 London, Painters | 236 | sound | |

Result: foundation-date class, year and period are right in all 30. Purposes: 21 sound, 2 debatable, 1 minor, 4 wrong, 2 not fully checked. Three of the four errors are missed funerals or alms, so the published shares are more likely too low than too high.

**Further checks.**

- Seven units have a cross-reference with no inheritance recorded and at most one purpose code (certs. 80, 81, 84, 86, 98, 376, 427). The supplement's statement that cross-references "are expanded" is not fully true.
- Westlake's own text gives 65 certificates "definitely" before 1349 (p. 50). The data give 51 in 1300–48 plus 14 before 1300 = 65.
- The eight pestilence entries are 7 Latin and 1 French, and none is among Smith's 42. Both statements in S3.2 hold.

### 2C. Interviews (30 random rows; seed 31337; source Project Gutenberg)

Every stored passage in the 30 rows was found in the Gutenberg file inside the stated segment.

| Narrative | Verdict | Finding |
|---|---|---|
| SC Gadsden; NC Mitchel; TX Mitchell; TX Quarls | sound | No code; only incidental mentions of religion. |
| SC Gladdeny | sound | Black preacher at a brush arbor. |
| TN Hudson, Measy | debatable | "I wuz tole dat sum ob de white peeples wuz so mean … de slaves would tek a pot": hearsay about other plantations, counted as secret worship and so as Black control. Flagged `hearsay_only`. |
| NC Littlejohn | under-coded | "I joined de church 'cause I had religion" yet `postwar_church_any` = ns. Other codes right, including prayer for the Yankees. |
| GA Jones, Fannie | sound | Joined "58 years ago": after 1865. |
| TX Price | sound | Hearsay flagged. |
| AR Gant | debatable | Black-led worship rests on "Edmond Gant was a black preacher in slavery. He married us." |
| TX Row | sound | Forbidden and secret; mother's prayer. |
| OK Dowdy | sound | Negative attitude is inferred from the report of the obedience sermon itself (see O9). |
| SC Dorroh; NC Haywood; GA Jewel; TX Davis, William; MS Kennedy; TX Brim; SC Brown | sound | |
| TX Williams, Daphne | sound | Faith of others, in a white-supervised setting. |
| SC Ryan | under-coded | "I joined church when I was 18" is used for conversion after 1865, yet `postwar_church_any` = ns. |
| OH Toler | sound | "Chu'ch was not allowed." |
| GA Bostwick | under-coded | "I jined de church" yet `postwar_church_any` = ns. |
| AR Parks | sound | Black interviewer correctly documented. |
| AL Grandberry | debatable | `faith` = y rests on "my pappy learnt to read de Bible". |
| AR Robinson | debatable | Positive attitude to white preachers rests on a kind owner who was a preacher. |
| TX Houston | sound | |
| OH Glenn | **probable over-code** | `postwar_church_any` = y rests on "I went to dances and to church with my folks", which the context places in slavery. The same passage ("We sho did have church, large meetin'") is not coded as worship. |
| NC Harris | debatable | `faith` = y rests on a father who "read de hymn book and Testament to us". |
| NC Sykes | debatable | Black-led permitted worship rests on "prayer meetin's" in a list of amusements. |

Result: 20 sound, 6 debatable, 3 under-coded, 1 probably over-coded.

**Consequences.**

- The worship-control codes are the firmest. Three of the 30 rest on thin wording (Hudson, Gant, Sykes), and each adds to the "Black control" count of 92.
- The supplement infers lower bounds from the fact that the first coding was never the more generous in the 40 double-coded narratives. This sample found one probable over-code and two loose faith codes. "At least 72", "at least 106" and "at least 39" should read "72", "106" and "39, probably undercounts".
- Six of the 25 conversions dated after 1865 have `postwar_church_any` = ns, which the codebook's own definition does not allow.
- `interviewer_race_corrections.md` records segments that hold a second informant's narrative (Cora Armstrong's segment contains Campbell Armstrong's; also Higgins, Rooks, Dillon) and two with two interviews. The article does not say that the unit is sometimes a merged segment.

### 2D. Quoted items checked at source

Westlake certs. 180, 182, 213, 382, 279 (p. 199) and 203 (p. 184); the four interview passages; Sharpe 1890: 125. All match (section 4).

---

## 3. Statistics, overreach and missing cautions

| # | Sentence | Why it is a problem | Suggested rewording |
|---|---|---|---|
| O1 | "No class of church recipient declines in any period." (§4.3); "no class of church recipient fell" (G1) | False against Table 2 (N1). | "No class of church recipient shows a statistically significant decline. Gifts to monasteries fall from 22.9 to 15.8 percent between the first two periods (p = .13), and gifts to St. Paul's are flat after 1375." |
| O2 | "The indicators of who holds the remedy are coded from records that do not depend on the response." (§3.1); "can be read without knowing how people later responded" (§1); "The sorting condition is read from the indicators and not from the response." (§6.1) | Table 1 fills indicators 1 and 3 with the same counts that Table 5 lists as the lay response: gilds with their own chaplain (37.6%), Black-led meetings (66), secret worship (28), Black control (92 of 206). For types 2 and 3 the indicator and the response are one observation. Only the narrower Table 1 note (not inferred "from whether people stayed in a church or left it") is true. | "The indicators are not inferred from whether people stayed or left. For types 2 and 3, however, the record of who administered rites is also the record of the lay response, so condition and response are not observed independently. Only for type 4 does the condition (Jones 1842; the dispute over pulpit and property) come from a different record than the response." Then drop "three contributions … coded apart from outcomes" or limit it. |
| O3 | "Li Muisis saw pilgrimage stop with the plague, and Jones and Allen printed a verse on the same pattern." (G4); "The authors also print a verse on how quickly crisis devotion fades" (§5.4); "The evidence for fading … comes from Tournai and from one verse." | Jones and Allen introduce the lines as "the following old proverb, which we think applicable to those of our colour who exposed their lives". It is a proverb about ingratitude to helpers, quoted in their own defense. It is not an observation that devotion faded in Philadelphia. Li Muisis reports from Tournai on shrines at Hasnon and Soissons; he did not see it. So fading rests on one sentence in a comparison text, and G4 is not "an observed regularity in two cases". | §5.4: "They close with an old proverb, applied to the Black nurses whose service was now slighted: …". G4: "Evidence that heightened devotion faded is one sentence in li Muisis about two shrines of St. Sebastian. I state it as a possibility. What both cases document is that bodies built by sufferers endured." Change the abstract to match. |
| O4 | "They suppressed lay custody, as Clement VI did in 1349, and as happened to the woods church at Edenton after 1831." (G3, under "Church authorities answered") | Jacobs does not say that a church authority demolished the church. In her account slaveholders acted after the revolt. | "Authorities suppressed lay custody: a pope in 1349, and slaveholders at Edenton after 1831." Head G3 "Authorities", not "Church authorities". |
| O5 | "Or they absorbed it, as parish churches absorbed the gilds. The evidence is … 509 returns." (G3); "I call this answer of the authorities 'absorb.'" (§4.4) | The returns are gilds' reports to the Crown. They contain no act of any church authority. "Absorb" is inferred from the absence of recorded conflict and from gilds meeting in parish churches. | "The returns record no conflict with church authorities, and the gilds worked inside parish churches. I read this as toleration and call it 'absorb'. No document of a church authority is cited for it." |
| O6 | "The flagellant companies at Tournai governed their own penance and buried the dead." (§6.1, type 3, "lay action has no license") | Li Muisis (LEM p. 237) says the Tournai company chose lay captains and that, at the request of the provost and governors, an Augustinian prior, his companion and two secular priests went with it "to hear confessions and, if need be, administer the sacraments". The oath (p. 243) is mentioned in §4.5; this is not. | Add the sentence to §4.5 and soften type 3: "outside the church's control, though not without clergy". |
| O7 | "Institutional self-correction may be a path to renewed trust … At Edenton an Episcopal rector addressed enslaved hearers as human beings" (G5) | One rector's conduct is not institutional self-correction. Jacobs goes on to say that his white parishioners grew dissatisfied and that he left. The context cuts against the reading and is omitted. | "One minister's conduct drew hearers (Jacobs 1861: 110), and his white parishioners objected. Neither case shows an institution correcting itself." |
| O8 | "Trust in individual white ministers followed conduct." (§5.6) | §5.3 labels this as a reading of two passages. §5.6 states it as a finding. | "In two passages, trust attaches to a minister's conduct." |
| O9 | "Negative judgments cluster with obedience preaching. They occur in 14 of 23 such narratives and in none of the 9 that describe other preaching." (§5.2) | The attitude code was read from the same passage as the preaching code. In all 14 narratives the "attitude" passage lies within eight lines of the obedience passage in the Gutenberg file, in 12 within three lines, and in 2 it is the same line ("That would be all he preach"; "Nothing about Jesus was ever said"). The association is close to definitional. The article gives this caution for faith and control but not here. No test is given (Fisher p = .002). | Add: "The two codes usually rest on one passage, so this is not an independent association." |
| O10 | "In every disagreement the first coding was the more reticent, so its counts for those variables are lower bounds." (§3.2); "at least 72", "at least 106", "at least 39" | An inference from 40 narratives. The spot-check found a probable over-code and loose codes (2C). | "so its counts are probably undercounts". Drop "at least" and "at most". |
| O11 | "The steps after 1361 exceed chance" (§4.3); §3.4 "Tests indicate whether a difference exceeds what chance would produce" | Table 2 Panel B holds 24 unadjusted tests. With a Bonferroni bound of .002, the fraternity step (p = .005) does not pass; parish, friars, St. Paul's and "any institution" do. The wills and gilds are also complete enumerations, so intervals and tests describe a notional random process, not sampling error. Only Table 4 says what its intervals mean. | "The steps after 1361 are large relative to period-to-period noise (parish and friars p < .001; fraternities p = .005, which would not survive correction for the 24 comparisons in Table 2)." Add to §3.4: "The wills and gild returns are complete enumerations of the calendars. Intervals and tests treat each period as a draw from a stable process and should be read as a scale for the differences." |
| O12 | "they did not move after either epidemic" (chantries, §4.3) | The pre-plague subset has 83 wills (interval 28.8–49.3). It is 11 percent of the wills of 1320–48 and was selected by the clause that defines the subset. "Did not move" is stronger than the data. | "show no detectable change (38.6, 41.0, 41.3 percent; the first figure rests on 83 wills)". |
| O13 | "I therefore restrict the main comparison to wills whose summary states a burial place." (§4.3) | The restriction is not in the codebook and was introduced after the all-wills results showed the artifact. A reader should be told it is post hoc. | Add "This restriction was chosen after the recording artifact was seen in the full series." |
| O14 | "Before 1349 most enrolled wills dealt with land only. The testament of movables … was usually not enrolled (Sharpe 1889: xxv)." | Page xxv supports the second sentence in part ("frequently a will of personalty not enrolled is mentioned"). The first sentence is the author's inference from the calendar. Sharpe also writes that "both real and personal estate are for the most part disposed of by one and the same testament" (xxxii). | "I infer from the abstracts that most wills enrolled before 1349 dealt with land only; Sharpe notes that a separate testament of movables often went unenrolled (1889: xxv), though he also says that one testament commonly disposed of both (xxxii)." |
| O15 | Table 2 note: "pooled two-proportion tests (chi-square, 1 df, no continuity correction)" | Several 1320–48 cells are small (fraternity 2 of 83; expected count below 5). Fisher's exact gives p = .38 where the table prints .25. No conclusion changes. | Use Fisher's exact for the period 1 to 2 column, or say that small cells make those p-values approximate. |
| O16 | "the association holds within states (Mantel–Haenszel odds ratio 3.36)" | No interval or test is given, and many state strata are sparse. | "is similar when stratified by state (3.36; no interval computed)". |
| O17 | "Its direction suggests that criticism of white religion is understated in the collection." (§5.2) | The cautions are given. But 336 of the 347 "others" are of unknown race, and the result is confounded with state. "Suggests" is the most that can be said. | Keep, and add "among narratives whose interviewer's race is not documented". |
| O18 | "The interviews took place in the Jim Crow South, mostly with white interviewers" (§5.2) | In this sample a white interviewer is documented for 11 narratives. The statement is general knowledge about the project (Blassingame), not a count from the data. | "mostly, as far as is known, with white interviewers (Blassingame 1975)". |
| O19 | "Each is an observed regularity in two cases, not a law." (§1, §6.2) | Not true of G4's first half (O3) or of G5, which the text itself calls "a question". | "G1 to G3 are observed in both cases. G4 is documented in part. G5 is a question." |
| O20 | "Heightened devotion faded with the danger" (abstract; §8 "Devotion in its heightened form faded") | Stated flatly; the body calls the evidence thin. | "Organizations built by sufferers endured; evidence that heightened devotion faded is slight." |
| O21 | "Burial, at least, was provided." (§4.2) | An inference from Avesbury's new cemetery. It says nothing about rites. | "Avesbury records mass burial in a new cemetery." |
| O22 | "Nothing in the returns shows suppression" (§4.4) | True, and the caution about the Crown follows. One London return (cert. 203) says of itself that it "indeed is no fraternity"; the article calls it a gild. | Mention that the St. Bride's return disclaims the name of fraternity. |
| O23 | "Minnie Davis of Georgia remembered her mother 'praying to herself …'" | Davis says "My mother said that … she was praying to herself". She reports her mother's later account. | "recalled her mother saying that she had been 'praying to herself …'". |

**Where the required cautions are present and adequate.** Survivorship for the gild dates (§4.4, n. 2, Table 3 note, S3.2, §7.1). The enrollment and abstract artifact for the wills (§4.3, Table 2 note, S3.1, §7.1). Interviewer and age effects for the interviews (§5.2, Table 4 note, S3.3, §7.1). The shared-passage caution for faith and control (§5.2, Table 4 Panel C). The statement that nothing is causal (§1, §3.4, §4.6, §5.6, §8). Odds-ratio wording ("about four times the odds") is correct.

---

## 4. Quotations and translations

Status: **exact** = wording matches the source.

| # | Quotation | Locator given | Status | Evidence and finding |
|---|---|---|---|---|
| 1 | *etiam laico, et si desit vir laicus, mulieri*; "even to a layman, and if no layman is at hand, to a woman" | Wilkins 2: 745–46 | exact; translation accurate | W2 p. 745. |
| 2 | *juxta doctrinam apostoli* | same | exact | W2 p. 745: `confiteantur juxta doctrinam apostoli alterutrum sua peccata`. |
| 3 | "as they are bound" | same | accurate | W2 p. 746: `confiteantur iterum, ut tenentur, suo proprio sacerdoti`. |
| 4 | "as we have heard"; priests unwilling "whether from devotion or for any stipend"; "perhaps because of the infection and the dread of contagion" | §1, §4.2 | accurate | W2 p. 745: `ut accepimus`; `devotionis zelo, aut pro stipendio aliquo`; `forsitan propter infectionem, et contagionis horrorem`. |
| 5 | The sick "believed that no confession could help them unless it was made to a priest who held the keys"; lay confession "accords with the teaching of the Church and the canons"; deacon; unction | §4.2 | accurate paraphrase | W2 pp. 745–46: `credentes nullam aliam … confessionem … utilem … nisi quae sit sacerdoti ecclesiae claves habenti`; `juxta doctrinam ecclesiae et canonica instituta`; `per diaconum`; `debet, sicut in aliis, fides sufficere sacramenti`. Date `4. id. Jan. M.ccc.xlviii` = January 10, 1349. |
| 6 | Canterbury: God "sometimes punishes in time so as not to condemn in eternity"; prayers, masses, sermons, processions, indulgences; September 28, 1348 | Wilkins 2: 738 | accurate | W2 p. 738: `quandoque punit temporaliter, ut eos aeternaliter non condemnet`; `4 cal. Octob.` 1348. |
| 7 | Zouche: processions and litanies in July; sins the cause | Raine 395–96 | accurate | RAI pp. 395–97: `hoc quippe hominum peccata efficiunt`; `processiones fiant cum decantatione letaniae`. The indulgence runs on to p. 397. |
| 8 | *nequeunt inveniri*, "cannot be found"; October 12, 1349; shortage put down to deaths | Raine 401 | exact | RAI p. 401: `propter mortalitatis pestem … nequeunt inveniri`. |
| 9 | "excessive stipends"; May 28, 1350 | Wilkins 3: 1–2 | exact | W3: `stipendia exigunt excessiva`; `5 calend. Junii, anno Domini 1350`. |
| 10 | 1362: "a new constitution with the same opening words and sharper language" | Wilkins 3: 50–51 | accurate | W3: second text opens `Effraenata generis humani cupiditas` and adds `evomunt … spumant in libidinem`. Pages per earlier audit. |
| 11 | Avesbury: more than 200 burials almost daily, early February to after Easter, new cemetery by Smithfield | Thompson 407 | accurate | AVE p. 407: `a festo Purificationis usque post Pascha, in novo tunc facto cimiterio juxta Smethfeld plus quam cc. corpora … quasi diebus singulis`. |
| 12 | Avesbury: more than 120 flagellants, mostly from Zeeland and Holland, about Michaelmas 1349, twice a day, in the sight of the people | Thompson 407–8 | accurate | AVE pp. 407–8: `plus quam vjxx homines, pro majori parte de Selond et Houlond … bis in die, in conspectu populi`. |
| 13 | Sharpe on movables; on omitted bequests | Sharpe 1889: xxv, xlviii | accurate; see O14 | BHO introduction, pages XXV and XLVIII. |
| 14 | "makes his will seeing the peril of this world and especially of the existing plague" | Sharpe 1890: 125 | exact | BHO, Roll 97 (15). |
| 15 | "The alderman collects the chaplain's salary" | Westlake cert. 180 | exact | WES p. 178. |
| 16 | "chaplain elected by them" | cert. 182 | exact | WES p. 179: "Number limited to 12 plus the chaplain elected by them." |
| 17 | "to assist the parson daily … whereby the parson's difficulties were much relieved" | cert. 382 | exact | WES p. 221. |
| 18 | "carried through the parts of the town with only a single candle of poor wax burning in front of it" | Westlake 199 | exact | WES p. 199 (image viewed). |
| 19 | "were suspended by the great plague, but renewed later by survivors and parishioners of other parishes" | Westlake 184 | exact | WES p. 184. See O22. |
| 20 | Westlake "saw" that a gild that died left no memorial | Westlake 27 | accurate paraphrase | "unless a gild survived the Black Death and continued in existence until that year, its memorial perished with it." |
| 21 | St. Katherine's, Aldersgate: Friars Minor, dirige, trental, paid | Smith 8 | accurate | SMI p. 8: "the wardeyns schul warne the frere menours … seye ther a dirige, and on the morwe to seie a trent of masses … and the wardeyns schul paie hem for here trauaile". |
| 22 | "more than the divine office"; mocked the clergy; arrival August 15, 1349 | Lemaître 231, 239 | exact | LEM p. 231 (`in die Assumptionis`); p. 239 (`plus quam divinum officium`; `sepissime deridebant`). |
| 23 | "with great murmuring, unwillingly"; town and king first; sermon; bull not shown | Lemaître 251–52 | exact | LEM pp. 251–52: `bulla tamen non ostensa`; `cum magno murmure inviti cessaverunt`. The dean is also named. |
| 24 | "when the storm ceased, the pilgrimage and the devotion ceased as well" | Lemaître 258 | exact | LEM p. 258, of Saint-Médard at Soissons; the parallel sentence concerns Hasnon. See O3. |
| 25 | n. 1: *remedium* against the panic caused by bell-ringing | Lemaître 255 | accurate | LEM p. 255: `nemo super hoc remedium apponebat`. |
| 26 | Venette: timid priests withdrew; sisters of the Hôtel-Dieu; none died without confession and viaticum; heirs died first | Géraud 2: 211–13 | accurate | GER pp. 211–13: `sacerdotes timidi recedebant`; `mori non timentes`; `Nec erat aliquis quin confessus et cum viatico`; `quia proprios haeredes ante se mori videbant`. |
| 27 | Bull: keys; cross "without the license of a superior"; blood of Jews "and often of Christians"; goods of clergy and laity; penance at home not forbidden; October 20, 1349 | Raynaldus 25: 471–72 | exact and accurate | RAY p. 471 §20: `claves Ecclesiae vilipendunt`; `sine superioris licentia`; `Judaeorum … et frequenter Christianorum sanguinem effundere … bona clericorum et laicorum diripere`; `in suis hospitiis`; `XIII kal. Novembris, anno VIII`. |
| 28 | n. 3: copy to the archbishop of Magdeburg, beginning *Molesta nobis* | Raynaldus 25: 471–72 | exact | RAY §20. |
| 29 | Bulls for the Jews, July 4 and September 26, 1348; failed "everywhere outside the county of Avignon" | Raynaldus 25: 453–55 | accurate | RAY: `VI kal. Octobris`; `ubique enim, excepto comitatu Avenionensi`. July 4 and the pages per earlier audit. |
| 30–32 | Jones: "forbid religious meetings, and religious instruction on our own plantations"; "literally shut up the kingdom of heaven against men"; "in a state of almost absolute dependence upon their owners for the words of eternal life" | Jones 1842: 158 | exact | CCJ p. 158. |
| 33–34 | "separate entirely the civil and religious condition of this people"; "disclaim all interference with the former" | Jones 1842: 73–74 | exact | CCJ pp. 73–74 (page turns after "interference with"). |
| 35 | "All attempts to suppress this class of influential men among their own colour have signally failed" | Association 1846: 13 | exact | LIB p. 13. |
| 36–38 | Jacobs: "their little church in the woods"; "was built by the colored people"; "their request was denied, and the church was demolished" | Jacobs 1861: 103 | exact | JAC ch. XII. Jacobs never names Edenton; the place is known from later scholarship and needs a word. |
| 39–40 | "to give the slaves enough of religious instruction to keep them from murdering their masters"; "but the law forbids it, and the churches withhold it" | 105; 113 | exact | JAC ch. XIII. |
| 41–42 | "it was the first time they had ever been addressed as human beings"; "God has hid himself from me" | 110; 108 | exact | JAC ch. XIII. See O7 for the omitted sequel. |
| 43–46 | Merritt; Mathews; Van Dyke; Minnie Davis | supplement S4 | exact | PG 35380 lines 2340–42 and 2120–21; PG 36020 lines 12895–97; PG 13602 lines 7131–33. See O23. |
| 47–49 | Douglass: "I love the pure, peaceable, and impartial Christianity of Christ …"; "The man who robs me of my earnings …"; "We slaves loved Mr. Cookman" | 118; 119; 54 | exact | DOU. Pages per earlier audit. |
| 50 | Walker: "one might believe it was a plan fabricated by themselves and the devils to oppress us. But hark! My master has taught me better than to believe it" | Walker 1830: 40 | exact | WAL. |
| 51–54 | Allen: "pulling him up off of his knees …"; "we all went out of the church in a body …"; "if you deny us your name …"; "preserve us from that spiritual despotism …" | 14–15; 16; 24 | exact | ALL. April 1816 confirmed. "read publicly out of meeting" supports the threat. |
| 55 | "Thus were our services extorted at the peril of our lives, yet you accuse us of extorting a little money from you" | Jones and Allen 1794: 15 | exact | JA p. 15. Burials 67 and 305 on pp. 15–16. |
| 56 | "When the war is over, and all things righted, / God is forgotten, and the soldier slighted" | 20 | exact words; **context misdescribed** | JA p. 20. See O3. |
| 57 | Dittmar and Meisenzahl: "Before religious competition led to the articulation of institutional alternatives, these shocks did not lead to institutional change" | 983 | matches project notes; not re-fetched | The sentence concerns plague before the Reformation in general. Their null result for the Black Death is at p. 988, n. 63 per the project notes. Cite both. |
| 58 | "a new and independent country" | PCT 1977 | exact | china.usc.edu/node/20514; PCT 005 `新而獨立的國家`. |
| 59 | 1990 apology (paraphrase): cowed by martial-law rule; a very few ministers and members excepted; public support and warmth; apology and compensation demanded | PCT 1990 | accurate | PCT 047: `懾於執政者長期恐怖的戒嚴統治，除極少數傳教師及信徒 … 整體教會並未給予受難者家屬應有的聲援及溫暖`; `強烈要求國民黨政府應向受難者及家屬誠心道歉，同時作必要之賠償`. |

**Translations from Latin.** All renderings checked are accurate. The two points raised by the earlier audit (T1 "layman"; T3 "as we have heard" and the causal clause) have been corrected.

---

## 5. References

66 entries. Every in-text citation has an entry and every entry is cited in the text. No fabricated work was found. 65 were re-verified here; Fu et al. (2019) rests on the earlier audit (the URL responds with a PDF of 10 MB).

| Entry | Checked by | Result |
|---|---|---|
| Belloc, Drago and Galbiati 2016 | Crossref | Correct: *QJE* 131 (4): 1875–1926. |
| Bentzen 2021 | Crossref | Correct: 192: 541–83. |
| Blassingame 1975; Chaves 1994; Larkin 1972; Lieberson 1991; Bourdieu 1971 | Crossref | Correct. Crossref gives first pages only; ranges are the known ones. |
| Bottan and Perez-Truglia 2015 | Crossref | Correct: 129: 106–19. |
| Cohn 2007 | Crossref | Correct: *Past & Present* 196 (1): 3–36. |
| Dittmar and Meisenzahl 2020 | Crossref | DOI resolves; Crossref has no volume or pages (online February 2019). 87 (2): 959–96 agrees with the master bibliography. |
| Geddes 1990 | Crossref | Correct: 2: 131–50. |
| Kubai 2007 | Crossref | **Add the issue:** *Exchange* 36 (2): 198–214. |
| Miller 1975; Russell-Wood 1974; Skocpol and Somers 1980; Robinson 2019 | Crossref | Correct. |
| Rychetská 2022 | Crossref | DOI resolves. Crossref shows advance pagination 1–31 and no volume. 9 (1): 70–100 rests on the earlier audit's relbib record. Check the printed issue. |
| Boles 2020; Casanova 1994; Duffy 1992; Fountain 2010; Frey and Wood 1998; Genovese 1974; George and Bennett 2005; Henderson 1994; Hildebrand 1995; Hirschman 1970; Irons 2008; Montgomery 1993; Norris and Inglehart 2011; Pinn 1995; Raboteau (1978) 2004; Scott 1990; Sparks 1994; Stern 1982; Weber 1978 | Open Library | Correct. |
| Cohn 1992 | Open Library | Exists. Open Library lists the 1997 paperback; 1992 is the first edition. |
| Finke and Stark 1992 | Open Library | Exists. Open Library's first hit is the 2005 edition (*1776–2005*); the 1992 title is as cited. |
| Longman 2010 | Open Library | Exists. Open Library has 2009 and 2010; 2010 is the usual date. |
| Martin 1978 | Open Library | Correct. Harper & Row (New York) and Blackwell (Oxford) both issued it in 1978. |
| Platt 1996 | Open Library | Correct. UCL Press (London); University of Toronto Press in North America. |
| Kim 1989 | Open Library | Exists (University of Hull). The master bibliography records that the Hull repository gives the subtitle "A Study of Religion and Politics". Settle the subtitle from the thesis title page. |
| Westlake 1919; Smith 1870 | Open Library; scans | Correct. Westlake is not in `references_master.md`; add it. |
| Sharpe 1889, 1890 | BHO | Correct. The master bibliography has one combined entry. |
| Wilkins 1737; Raine 1873; Thompson 1889; Lemaître 1906; Géraud 1843; Raynaldus 1880 | scans | Correct. The Wilkins URL is that of vol. 2 only; vol. 3 is also cited. |
| Jones 1842; Association 1846; Walker 1830; Allen (1833) 1880; Jones and Allen 1794; Jacobs 1861; Douglass 1845 | scans; Gutenberg | Correct. |
| *Christian Recorder* 1866–69 | scans | Items found (Virginia buildings "deeded to the Methodist Episcopal Church South, and held by white trustees"; Nashville property and departing members). The entry gives the 1869 URL only; add the 1866 volume. Earlier audit: issues of January 16–23 and March 13, 1869, and May 12 or 19, 1866. Give the dates. |
| Federal Writers' Project 1941 | Gutenberg | Correct. The URL is the site root; the supplement gives file numbers. |
| Presbyterian Church in Taiwan 1971, 1975, 1977, 1990 | pct.org.tw; china.usc.edu | Correct. |
| Fu et al. 2019 | earlier audit | Not re-read. |

**Style (Chicago author-date, as the journal applies it).**

- The reference list is consistent: no place of publication, headline capitals, DOIs, reprint dates as "(1833) 1880" in the list and "[1833] 1880" in the text.
- In-text form "(Author Year: pages)" is used throughout, with "volume: page" for Wilkins, Géraud and Raynaldus.
- Twelve parentheses give a bare page with no author or year: (113), (119), (240), (243), (472), (213), (16), (18), (20–21), (24), (15–16), (20). The journal's examples always carry author and year. Supply them or recast the sentences.
- "(Christian Recorder 1866–69)" is cited three times with no issue date.
- Whole-book citations without pages remain for Cohn 1992, Fountain 2010, Henderson 1994, Duffy 1992, Platt 1996, Montgomery 1993, Irons 2008, Sparks 1994, Boles 2020, Frey and Wood 1998, Pinn 1995, Hildebrand 1995, Longman 2010, Stern 1982 and others. §7.3 says some are known through reviews and abstracts. That is honest; reviewers will still ask for pages.

---

## 6. Facts and attributions

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| F1 | Ralph of Shrewsbury, bishop of Bath and Wells; mandate of January 10, 1349 | correct | W2 pp. 745–46. Wilkins prints the place as "Wynchelcomb"; the register has Wiveliscombe (earlier audit). Not stated in this manuscript, and not needed. |
| F2 | Canterbury chapter, September 28, 1348; Zouche, July 1348; Clement VI to York, October 12, 1349; Islip, May 28, 1350 and November 16, 1362 | correct | W2, RAI, W3. |
| F3 | Clement VI condemned the flagellants on October 20, 1349; bulls for the Jews, July 4 and September 26, 1348 | correct | RAY. |
| F4 | Flagellants at Tournai from August 15, 1349; stopped in Lent 1350 | correct | LEM pp. 231, 251–52. |
| F5 | Gilles li Muisis a Benedictine abbot; Jean de Venette a Carmelite | correct | Standard identifications; the text says "usually identified". |
| F6 | Writs for the gild returns, November 1, 1388 (supplement) | correct | Standard date. |
| F7 | Westlake: three-quarters of gilds from four counties | correct | 386 of 509. |
| F8 | Edenton; Nat Turner's revolt, 1831 | correct | Jacobs does not name the town (row 36–38 above). |
| F9 | C. C. Jones a Presbyterian minister and planter in Georgia; Synod of South Carolina and Georgia, 1833 | correct | CCJ pp. 73–74. |
| F10 | Allen had been enslaved; St. George's; incident undated, placed in 1787 or 1792–93; AME formed April 1816 | correct | ALL. |
| F11 | Yellow fever, 1793; appeals in newspapers; belief in immunity; Carey's accusation; the elders of the African church; burials 67 and 305 | correct | JA pp. 3, 15–16; "on the application of the elders of the African church". |
| F12 | Interviews of 1936–38; 17 volumes; Gutenberg transcription in 34 eBooks | correct | `gutenberg_ids.txt` lists 34. |
| F13 | PCT statements of December 29, 1971, November 18, 1975, August 16, 1977; apology of February 9, 1990 | correct | PCT pages; earlier audit for the days. |
| F14 | TSCS trust: 21.5% and 10.7%; distrust 16.0% and 26.9%; four cautions (n. 5) | correct per earlier audit | All three earlier objections (2014 categories, fieldwork dates, unweighted tables) are now in the note. |
| A1 | Bottan and Perez-Truglia: falls in affiliation and attendance; no significant fall in belief; imprecise | supported | Earlier audit. |
| A2 | Weber on theodicy and strata; on the church as claiming a monopoly | supported | Standard readings of *Economy and Society*. |
| A3 | Norris and Inglehart; Finke and Stark; Chaves; Hirschman; Scott; Genovese; Bourdieu; Martin; Casanova ("argued") | supported | Known theses; "argued" is now used for Martin and Casanova. |
| A4 | Bentzen: searches for prayer rose in March 2020; in the country panel indistinguishable from zero by about October | supported | Project full-text notes quote the sentence. |
| A5 | Belloc et al.: earthquakes delayed communes where the bishop was also ruler; belief not measured | supported | Abstract. |
| A6 | Dittmar and Meisenzahl: plague of 1500–22 and church ordinances; no comparable effect of fourteenth-century plague | supported | Project notes (p. 983; p. 988 n. 63). |
| A7 | Cohn 1992: six Tuscan and Umbrian cities; change after 1363; concentration of gifts | supported at the level of the known thesis | Not read. |
| A8 | Duffy: vigorous parish religion, "for a period that begins around 1400" | supported | The earlier caution is now in the text. |
| A9 | Robinson: similar backgrounds | supported | Abstract. The earlier unlabeled inference is gone. |
| A10 | Platt: memorial masses and priests leaving parishes | supported | `sections/04_black_death.md`. |
| A11 | Raboteau; Frey and Wood; Irons; Sparks; Boles; Fountain; Montgomery; Hildebrand; Blassingame | supported at the level of the known theses | Not read. |
| A12 | Pinn "recovers a skeptical strand in narratives and spirituals" | fair | Known argument of the book. |
| A13 | Skocpol and Somers ("contrast of contexts"); Lieberson; Geddes; George and Bennett | supported | Their terms. |
| A14 | Larkin; Miller; Russell-Wood; Kim; Longman; Kubai; Stern; Rychetská | see section 8 | |

**Corrections from `../audit_manuscript.md` and `../mock_review.md`.** All that apply to this text are reflected: p. 738 and "prior and chapter"; prayers, masses, sermons and processions, not penance; the York shortage put down to deaths; 1362 as a new constitution; the church's part at Tournai; Venette's reason and his counter-evidence; pages for Jacobs and Douglass; the discipline clause in Allen; "My master" glossed as Christ; the *remedium* note; the exception clause and the political demand in the apology; "public support"; *juxta doctrinam apostoli*; the bull's charges and its incipit; the massacres of Jews; the two American settings kept apart; the context of the 1794 pamphlet; Irons and Sparks. The Moss, Rubinstein and Tournai-murmuring errors are gone because those passages were cut.

---

## 7. Methods transparency

| # | Claim | Finding | Verdict |
|---|---|---|---|
| M1 | §3.5: a language model retrieved, parsed, wrote the codebooks, sampled, coded and analyzed | Consistent with the evidence folders. | True |
| M2 | "[TOOL, VERSION, DATES]" (§3.5, supplement, title page); "[REPOSITORY, anonymized for review]" | Four unfilled placeholders. The journal requires tool name and version, dates of use, access and a full description in the methods. | **Not yet compliant** |
| M3 | "The codebooks were written before coding and amended as documented in each codebook and in the supplement." | *Wills:* the codebook says its rules "were drafted from keyword-in-context listings of entries outside the reliability sample", so rules were developed on nine-tenths of the data. The supplement says this; §3.5 does not. Git: codebook first committed 11:03, data 11:16, codebook edited again 11:16. *Gilds:* codebook committed 11:16; dates coded by 11:23; purposes by 11:29; amendments added 11:34. Disclosed. *Interviews:* the codebook opens "A pilot of 51 narratives … supplied the categories", and says the pilot had "targeted (non-random) additions". **The pilot is mentioned nowhere in the four target files.** The codebook and the first 196 coded rows enter git in the same commit (11:16), so git cannot show which came first; the file time of the codebook (11:03) is earlier. | **Incomplete** |
| M4 | §3.5: gilds, "the second is the same model's reading of the page images, made without sight of the first" | Supported by `reliability_firstpass.txt`. But the published data were then changed: between the commit that added the second coding (11:29) and the commit that added the adjudication record (11:34), relief falls from 191 to 177 gilds, feasts rise from 51 to 56, funerals from 249 to 250. The κ values in §3.2 describe the earlier codes. The supplement says rule errors "were corrected"; §3.2 does not. | **Incomplete in the main text** |
| M5 | Wills: sample drawn before rules; rules frozen before the second coding; errors not corrected afterward | File times fit (second coding 11:11; coding script and data 11:12, said to be the word-count column only). Not provable from git, since all three entered in one commit. | Plausible, unverifiable |
| M6 | Interviews: a first recoding measured only stability; the independent coding was a separate session given the codebook and locators; not a human | Matches `reliability_independent.md` (which records a SHA-256 of the second coder's file) and section 9 of the script. | True |
| M7 | "Every coded value is stored with the verbatim passage and the locator"; "Scripts verified each interview passage" | Positive codes carry passages in all three datasets. All passages in 30 sampled interview rows were found at their locators. | True |
| M8 | First coding of interviews used keyword-selected extracts capped at about 3,200 characters | Stated in the Table 4 note and the supplement. Not in §3.2 or §3.5, where a reader looks first. Five of 20 disagreements arose from it. | Move into §3.2 |
| M9 | §3.2: "For England I read …"; "All were read in public digital copies. Translations from Latin are mine." | The title page says AI tools were used "to search and summarize literature" and "to draft text". The reading notes in `research_notes/…/reading/` were made by the model. The journal's AI rule covers translation by name. If the model produced the Latin renderings, "Translations from Latin are mine" is untrue as it stands and the use must be declared. The earlier audit made the same point. | **Inconsistent with the title page until the author has checked each rendering and says how the first drafts were made** |
| M10 | Title page acknowledgment against §3.5 | Both declare AI coding and analysis. Only the title page declares AI drafting of prose and literature search. The anonymized manuscript therefore tells reviewers nothing about AI-drafted text or AI-made translations. | Add one sentence to §3.5 or a note |
| M11 | "No human coder has yet checked the codings." | Consistent with all files. | True |
| M12 | Supplement S1.2: cross-references "are expanded" | Not for certs. 80 and 81, and probably five more (2B). | Overstated |
| M13 | Supplement S1.3: "After the independent second coding, six interviewer attributions were corrected" | Matches `interviewer_race_corrections.md` and the git change to `data.csv` at 11:51. Two of the interviewer comparisons crossed p = .05 only after this change; the supplement says so. | True |
| M14 | Dates | Every evidence file was committed on 2026-11-11 between 10:55 and 11:52 UTC. The "[DATES]" placeholder should give the real period of use. | To fill |

---

## 8. Shadow-case table (Table 5 Panel B)

| Case | Cell content | Support in the audited sections | Verdict |
|---|---|---|---|
| Ireland | Catholic church not that of state or landlords; practice rose 1850–75; part may reflect who died and who left | `06_comparative.md`: Larkin 1972; Miller 1975 ("part of the 'revolution' may be a composition effect"); "subordinate to a Protestant state and landed elite, while their church was their own" | Supported. The same section notes that Larkin (2014) traced the beginnings to parish missions of 1825–46, before the Famine. That weakens "after collective suffering" and could be said. |
| Colonial Brazil | Established Catholic church; lay brotherhoods of enslaved and free Black people managed burial and festivals; type 2 | `05_slave_religion.md`: Russell-Wood 1974. The same paragraph: "religious orders were major slaveholders" (Schwartz 1982) | **Supported but selective.** By the section's own account the church was allied with the oppressor, the condition of type 4, yet the response is type 2. The table omits the slaveholding, so the row hides a case that cuts against the typology's sorting. §7.3 half-admits this. Add the fact and list Brazil among the hard cases. |
| Korea | Most Protestant bodies complied; resisters formed separate bodies after 1945; type 4 | `06_comparative.md` cites Kim Sung-Gun 1989; the fuller account in `10_other_languages.md` rests on Kim Sŭng-t'ae 1991, Kim Nam-sik 1990 and Yi Chin-gu 2025 | Supported. Kim's thesis covers 1931–45; the post-1945 bodies rest on the other three works, which the table does not cite. |
| Rwanda | Churches allied with the state; new communities spread; Catholicism still the largest; type 4, partial | `07_global_cases.md`: Longman 2010; Kubai 2007a | Supported. |
| Andes | Taki Onqoy, 1560s; return to native deities; limit case | `07_global_cases.md`: Stern 1982b (*Peru's Indian Peoples*) | Supported. `10_other_languages.md` adds that a later debate asks how far colonial records constructed the movement (Heilman 2002). Worth a clause. |
| Taiwan | Statements of 1971, 1975, 1977; apology of 1990; "No measure of any response exists." | Primary documents, verified; Rychetská per abstract | **Mislabeled.** The panel header says "secondary literature only. No primary sources were read", and §3.1 and §6.3 say the same of all six cases. This row rests on four primary documents that the article cites and quotes. Also soften the last cell to "None known to this study", as §7.2 does. |

Labeling: Panel B, its note, §3.1 and §6.3 all mark the cases as illustrative and without evidential weight. That is adequate once the Taiwan row is excepted.

---

## 9. Journal compliance

| Requirement | Result |
|---|---|
| Length ≤12,000 words including notes and references | 11,236 by `build/wordcount.py`. Pass. Title page figure is stale (N2). |
| Abstract ≤250 words | 247. Pass, with three words to spare. The script prints 262 because it counts the keywords line. |
| Title ≤140 characters | 121. Pass. |
| Headings ≤70 characters | Longest is 66 ("3.5 Use of artificial intelligence in data collection and analysis"). Pass. |
| American spelling | Pass. "colour" and "Coloured" occur only in a quotation and a title. "Gild" follows Westlake and Smith; Merriam-Webster gives it as a variant of "guild". Say once that the spelling follows the sources. |
| Author-date form | Pass, apart from the twelve bare-page parentheses (section 5). |
| Table callouts | Five, one per table, in order. Pass. |
| Tables consistent with text | Yes, except N1. Table 1 cites certs. 180 and 213 where the text cites 180 and 182; both are right. |
| Tables submitted separately | Yes. |
| Anonymity | No name, affiliation, self-citation or repository address in the manuscript, tables or supplement. The project repository carries a personal name, so the deposit cited for review must be an anonymized copy; none exists yet. |
| AI declaration in the methods with tool, version, dates, access | Section present; details are placeholders (M2). |
| Competing interests on the title page | Present. |
| Biographical note ≤600 characters | 420. Pass. |
| Consistency of number style | The manuscript and tables write "p = .005"; the supplement writes "0.44". Choose one. |

---

## 10. Counts

| Category | Checked | Sound | Minor | Wrong or unsupported |
|---|---|---|---|---|
| Numbers | about 780 | all script-derived values match | 6 (N4, N5, N7, N8, N9, N10) | 4 (N1 text against table; N2 word count; N3 reproducibility claim; N6 "no rise") |
| Data rows | 90 (plus two whole-population tests on the wills) | 62 | 15 debatable or minor; 2 not fully checked | 11 (wills 3; gilds 4; interviews 3 under-coded, 1 probably over-coded) |
| Statistics and overreach | 23 sentences flagged | — | — | — |
| Quotations | 59 quotations and close paraphrases | 56 | 2 (O23; Dittmar locator) | 1 (verse: words exact, purpose misdescribed) |
| Translations | all Latin and Chinese renderings | accurate | 0 | 0 |
| References | 66 (65 re-verified) | 62 | 4 (Kubai issue; Kim subtitle; *Recorder* dates and URL; Rychetská pagination to confirm) | 0 fabricated |
| Facts and attributions | 28 | 28 | 0 | 0 |
| Methods claims | 14 | 6 | 3 | 5 (M2, M3, M4, M9, M12) |
| Shadow cases | 6 | 4 | 0 | 2 (Brazil selective; Taiwan mislabeled) |
| Compliance items | 14 | 10 | 3 | 1 (AI details and deposit not yet supplied) |

---

## 11. Prioritized fix list

**A. Errors that a reviewer can catch from the submission itself.**

1. **"No class of church recipient declines in any period"** (§4.3; G1; §7.1). Table 2 shows monasteries falling 22.9 to 15.8 percent and St. Paul's 21.4 to 20.2. Reword as in O1.
2. **The 1794 verse** (§5.4; G4; abstract; §8). It is an old proverb applied to slighted Black nurses. With it gone, fading rests on one sentence in li Muisis about two shrines. Rewrite G4 and the abstract as in O3 and O20.
3. **Independence of indicators and responses** (§1, §3.1, §3.3, §6.1, contribution 1). Table 1 uses the response counts as indicators for types 2 and 3. Limit the claim as in O2.
4. **Edenton and "absorb"** (G3). Slaveholders, not a church authority, are the actors Jacobs names. "Absorb" is an inference from silence. Reword as in O4 and O5.
5. **Taiwan row** of Table 5 and the three statements that all six shadow cases are secondary only. Except Taiwan. Add the slaveholding of the Brazilian church and move Brazil to the hard cases.

**B. Methods and disclosure, before submission.**

6. Fill "[TOOL, VERSION, DATES]" and the access details; create an anonymized deposit and cite it.
7. **Translations and reading** (§3.2). Either the author checks every Latin rendering against the page and says that first drafts were made with the model, or "Translations from Latin are mine" and "I read" must go. Add a sentence on AI-drafted prose to the anonymized text.
8. **Disclose the pilot of 51 narratives** that supplied the interview categories, and say whether any pilot narrative is in the sample of 400.
9. **Gild reliability** (§3.2). Say that the κ values describe the codes before adjudication and that the published data were corrected afterward (relief 191 to 177, feasts 51 to 56).
10. Move the 3,200-character extract limit into §3.2. Say that some interview segments contain a second informant.
11. Replace "lower bounds" and "at least" with "probably undercounts" (O10).
12. Correct the supplement's claim that the scripts print every figure (N3), or add the first-pass tables to the scripts.

**C. Statistical wording.**

13. §3.4 and §4.3: complete enumerations, 24 unadjusted tests, the fraternity step (O11); "no detectable change" for chantries on 83 wills (O12); the post hoc subset (O13); Fisher's exact for small cells (O15); the mean's interval (N9); no interval for the stratified odds ratio (O16).
14. §5.2: the shared-passage caution for attitude and obedience preaching (O9); "14 of the 23 that state an attitude" (N10).
15. Rounding (N4, N5); "half record disruption" (N7); the 1368–69 counts (N6).

**D. Context the sources supply.**

16. Tournai's company went with an Augustinian prior and two secular priests to hear confessions (LEM p. 237) (O6).
17. The Edenton rector's white parishioners objected and he left (O7); G5 is a question, and no "institution" corrected itself in either case.
18. Sharpe 1889: xxxii against "most enrolled wills dealt with land only" (O14).
19. Minnie Davis reports her mother's words (O23); the St. Bride's return disclaims being a fraternity (O22); Jacobs does not name Edenton.

**E. Data repairs (do not change any conclusion; make them before deposit).**

20. Wills: burial rule misses "TO be buried" and "To he buried" (5 wills, all 1349–60). Double-code the burial flag.
21. Gilds: expand the cross-references in certs. 80, 81, 84, 86, 98, 376 and 427; review funeral and alms false negatives (certs. 95, 214, 309).
22. Interviews: make `postwar_church_any` = y wherever a conversion is dated after 1865 (6 rows); review the Glenn row and the two "read the Bible" faith codes.

**F. References and form.**

23. Kubai: add issue 2. Settle Kim's subtitle and Rychetská's pages. Date the three *Christian Recorder* items and add the 1866 URL. Cite Dittmar and Meisenzahl p. 988 n. 63 for the Black Death null. Add Westlake to the master bibliography.
24. Replace the twelve bare-page parentheses with full author-date citations.
25. Regenerate the title-page word count. Make the abstract say four regularities and one question. Use one style for p-values.
