# gild_foundations: results

**Question.** Did English parish gilds multiply after the Black Death? Did their stated purposes centre on what lay members controlled: funerals, masses for dead members, lights and mutual aid? In other words, did the laity hold the remedy inside the church?

**Short answer.** Of the gilds that survived to 1388–9 and stated a foundation year, about four in five give a year after 1349. That count cannot show that gilds multiplied after the plague, because gilds that had died out by 1389 were never recorded. The stated purposes are clear. Lights, provision for dead members, lay-hired chaplains and member relief dominate. The founders named are almost all lay. The clergy are rarely given any part in running the gilds.

---

## 1. Source and method

- **Units.** Each unit is one gild in H. F. Westlake's calendar of the gild certificates returned under the writs of 1 November 1388 (TNA C 47). The calendar is the Appendix to Westlake (1919), pp. 137–238. The scan used is Internet Archive `parishgildsofmed00westuoft`, PDF pp. 161–262; printed page = PDF page − 24. The calendar has 509 gilds on 471 certificates. Westlake's own county totals for Norfolk (164), Lincolnshire (123), Cambridgeshire (60) and Suffolk (39) are reproduced exactly.
- **Text capture.** The OCR files on Internet Archive (`_djvu.txt`) are unusable for the Appendix because the tables are printed sideways. The page images were therefore rendered at 300 dpi, rotated, shear-corrected and cut into cells on the printed rules. Each cell was read with Tesseract 5.
- **Identification and dates.** Certificate number, language, county, place, dedication and the verbatim date statement were transcribed by reading the page images, not taken from OCR. The file is `pipeline/identification_transcribed.tsv`. Unit-to-OCR-row mapping was checked for all 509 units.
- **Coding.** Codes were assigned under a codebook written before coding (`codebook.md`); amendments made during coding are dated at its end.
  - Purposes were coded by transparent keyword rules on OCR'd columns 3–5 (`pipeline/code.py`). Westlake's cross-references ("General purpose as in (a)", "as in 166") were expanded.
  - Founders and clergy governance were coded by reading every relevant sentence (`pipeline/make_overrides.py`).
  - Every code of 1 stores the verbatim Westlake snippet that triggered it (`*_snip` columns in `data.csv`), with page, PDF page, certificate and OCR row locators.
- **What "verbatim" means here.** Westlake's calendar is an English summary of Latin, French and English originals. Snippets are verbatim from Westlake, not from the returns themselves.
- **Reliability.** A random 10% (n = 51, seed 1389) was coded a second time from the page images, without consulting the first codes (§6).
- **Cross-check.** 42 returns that Toulmin Smith (1870) prints or summarises were matched by place and dedication (`crosscheck_smith.csv`; §7).
- **Statistics.** Proportions carry Wilson 95% intervals. Period contrasts use two-sided Fisher exact tests. Everything in this file is printed by `analysis.py`.

## 2. Survivorship bias (read before the tables)

The 1388–9 inquiry recorded only gilds that existed in 1388–9. A gild founded in 1320 enters the data only if it survived the famine years, the Black Death of 1348–9, the plagues of 1361–2, 1369 and 1375, and ordinary decay. A gild founded in 1380 had to survive only a few years.

Westlake says this himself: "unless a gild survived the Black Death and continued in existence until that year, its memorial perished with it" (p. 27). Several returns describe near-extinction in 1349:
- the Brewers of All Hallows, London Wall: "all the founders died except John Enefeld", cert. 471, p. 238;
- St James, Lynn: "the larger part of the brethren died in the great pestilence", cert. 251, p. 194;
- St Mary, St Bride's, London: "suspended by the great plague", cert. 203, p. 184.

A stock of survivors therefore piles up near the date of observation even if the foundation rate never changed. Two numbers show how strong this is:

- **Constant-hazard model.** Assume a constant foundation rate and a constant annual dissolution hazard *h*. The observed post/pre ratio of annual rates (5.5) would arise from survival alone if *h* ≈ 0.039 per year, a gild half-life of about 18 years. That rate is not implausible for small voluntary bodies. Any one-off Black Death loss would lower the hazard needed.
- **Pre-plague trend.** Survivors were already rising steeply before 1349: about ×1.4 per decade from the 1300s to the 1340s. Projecting that trend forward, the observed rates (exact + approximate years) are:
  - 1349–59: 2.0 times the projection;
  - 1360s and 1370s: about 1.5 times;
  - 1380s: 0.86 times.

  With exact years only the excess is 1.7, 1.2, 1.2 and 0.67. The projection rests on only 51 pre-1349 gilds, and their number was itself cut down by the plague. It is fragile in both directions.

**These data cannot establish that gilds multiplied after the Black Death.** They are compatible with a modest excess of foundations in 1349–59 above an already rising curve. They are equally compatible with survivorship alone.

## 3. Foundation dates

**Table 1. Form of the foundation-date statement (all 509 gilds)**

| date statement | n | % [95% CI] |
|---|---|---|
| exact year (incl. regnal spans such as "1346-7") | 257 | 50.5 [46.2, 54.8] |
| no date stated | 130 | 25.5 [21.9, 29.5] |
| approximate ("c. 1369", "? 1376") | 43 | 8.4 [6.3, 11.2] |
| "time without memory", "of old time", "formerly" | 36 | 7.1 [5.2, 9.6] |
| date of statutes/licence/deed/charter only | 19 | 3.7 [2.4, 5.8] |
| "lately/newly/just begun" | 11 | 2.2 [1.2, 3.8] |
| reign only (temp. Edw. III / Ric. II) | 6 | 1.2 |
| pre-1300 charter or tradition; "7 Ed." | 5 | 1.0 |
| dated relative to the pestilence | 2 | 0.4 |

Gilds with a usable foundation year: 300/509 = 58.9% [54.6, 63.1]. Gilds with none: 41.1%. Fourteen of the years fall before 1300 and 286 fall in 1300–1389.

**Table 2. Stated foundation years by decade, 1300–1389 (survivors to 1388–9)**

| decade | all with year | exact | approx. |
|---|---|---|---|
| 1300s | 7 | 4 | 3 |
| 1310s | 4 | 4 | 0 |
| 1320s | 9 | 6 | 3 |
| 1330s | 12 | 10 | 2 |
| 1340s | 32 (1340–48: 19; 1349: 13) | 23 | 9 |
| 1350s | 40 | 38 | 2 |
| 1360s | 50 | 44 | 6 |
| 1370s | 74 | 64 | 10 |
| 1380s (to early 1389) | 58 | 54 | 4 |

The approximate years are heaped. Of 39 "c." years in 1300–89, 22 end in 9: 1309 (3), 1329 (3), 1339 (1), 1349 (7), 1359 (1), 1369 (4) and 1379 (3). Westlake is evidently turning statements such as "for forty years" into 1389 − 40. Great Yarmouth, cert. 367, says "This they have done for 40 years" and is dated 1348. Part of the 1349 spike is therefore a rounding artefact. Only 6 gilds give 1349 as an exact year.

**Table 3. Pre- vs post-plague foundations (survivors only)**

| subset | 1300–1348 | 1349–1389 | share post-1349 [95% CI] | annual rate ratio |
|---|---|---|---|---|
| exact + approx years | 51 (1.04/yr) | 235 (5.73/yr) | 82.2% [77.3, 86.2] | 5.5 |
| exact years only | 41 | 206 | 83.4% [78.3, 87.5] | 6.0 |
| exact, excluding 1348–49 | 40 | 200 | 83.3% [78.1, 87.5] | 6.0 |
| period-level (adds "lately begun", temp. Ric. II, statutes ≤1348, "before the pestilence") | 61 | 247 | 80.2% [75.4, 84.3] | — |

These shares describe the stock that survived to 1389, not the flow of foundations (§2). The 36 "time out of mind" gilds, and most of the 130 undated ones, are probably older foundations and would lower every share if they could be dated.

## 4. Stated purposes

The denominator is the 500 gilds whose entry states any content. Nine are lists of names, charters only, or blank.

**Table 4. Purposes (any mention; codes non-exclusive)**

| purpose | n/500 | % [95% CI] |
|---|---|---|
| lights (candles, tapers, torches, gild-light) | 401 | 80.2 [76.5, 83.5] |
| masses/prayers for dead members (incl. requiem, trental, obit, dirige) | 290 | 58.0 [53.6, 62.2] |
| funeral attendance / burial of members | 250 | 50.0 [45.6, 54.4] |
| chaplain or priest maintained (or sought "when funds permit") | 188 | 37.6 [33.5, 41.9] |
| relief/mutual aid for members | 177 | 35.4 [31.3, 39.7] |
| alms to the poor generally (incl. soul-alms) | 150 | 30.0 [26.1, 34.2] |
| gild feast / drinking | 56 | 11.2 [8.7, 14.3] |
| other | 192 | 38.4 [34.2, 42.7] |
| **any provision for dead members (funeral or masses)** | 352 | 70.4 [66.3, 74.2] |
| **any of lights / funeral / masses / aid** | 467 | 93.4 [90.9, 95.3] |

The "other" purposes by tag are:
- church fabric or ornaments: 73
- procession: 60
- peace or charity among members: 51
- pilgrimage: 28
- bells: 17
- craft regulation: 11
- roads or bridges, and hospital: 5 each
- plays: 2

**Table 5. Purposes by period of stated foundation (content gilds with a year in 1300–1389)**

| purpose | pre-1349 (n = 51) | post-1349 (n = 233) | Fisher p |
|---|---|---|---|
| funeral | 62.7% | 56.2% | 0.44 |
| masses for dead | 74.5% | 58.4% | 0.039 |
| chaplain | 51.0% | 36.5% | 0.059 |
| lights | 84.3% | 83.7% | 1.00 |
| aid to members | 41.2% | 35.2% | 0.43 |
| general alms | 39.2% | 34.8% | 0.63 |
| feast | 19.6% | 11.6% | 0.17 |
| other | 33.3% | 40.8% | 0.35 |

Gilds dated after 1349 are **not** more death-centred than older survivors. If anything, the older survivors more often have masses and chaplains. This plausibly reflects survivorship again: better-endowed gilds lasted, and older gilds had time to add provisions. The p-values are unadjusted across eight tests. None would survive a Bonferroni correction.

## 5. Pestilence, founders, clergy

**Explicit pestilence mentions** appear in 8/509 entries (1.6% [0.8, 3.1]). All verbatim from Westlake:
- Chesterton (cert. 13, p. 141): "Lands given by different persons about the time of the 'first pestilence.'"
- March (27, p. 145): "If the gild should be destroyed through the pestilence or any other destructive agent, its goods are to go to the fabric of the chapel."
- Tydd St Giles, St Mary (36, p. 146): "Ordinances made immediately after the 'first pestilence' (i.e., c. 1349)."
- London, St Mary at St Bride's (203, p. 184): "These and other devout purposes were suspended by the great plague, but renewed later by survivors and parishioners of other parishes."
- Lynn, St James (251, p. 194): "'A long time before the great pestilence.'" … "The larger part of the brethren died in the great pestilence, but afterwards others entered."
- Lynn, Corpus Christi (279, p. 199): "In the great pestilence which at Lynn was in 1349, in which the greater part of the people of that town died, three men (seeing that) the venerated sacrament … was being carried through the parts of the town with only a single candle of poor wax burning in front of it …". This is the only explicit plague-occasioned foundation.
- Oxford, St Thomas (391, p. 223): "In the first pestilence the property fell into a ruinous condition and the emoluments became in consequence so small as not to suffice for a chaplain."
- London, Brewers at All Hallows London Wall (471, p. 238): "This went on till the first pestilence, when all the founders died except John Enefeld, who afterwards got together some people, brewers and others …".

Most of these record disruption, death or refoundation, not a motive for founding. Westlake's own judgement fits: "there is little hint in any of their records that the shadow of death lay heavily upon them after the first visitation" (p. 28).

**Founders.** Founders are described for 104 gilds. Of these:

| founders | n/104 | % [95% CI] |
|---|---|---|
| lay parishioners, townsmen or named laymen "and others" | 52 | 50.0 [40.6, 59.4] |
| craft or occupational group | 42 | 40.4 [31.5, 50.0] |
| mixed clergy and laity | 6 | 5.8 |
| clergy (incl. two clerks' gilds) | 4 | 3.8 [1.5, 9.5] |

**Clergy role in governance.** A cleric is given a stated role in governing the gild in 11/509 entries (2.2% [1.2, 3.8]):
- the Bishop of Ely's jurisdiction over Cambridge gilds (certs. 6, 9, 10);
- a vicar as custos or governor (77, 234);
- a vicar helping choose the chaplain (205);
- the consent of a prior and convent (236);
- presentation to a chantry (385);
- archiepiscopal ratification of deeds (386, 387);
- a gild "governed by a prior (or cantor)" (404).

In two gilds clergy are barred from membership or office: "No chaplain … shall be admitted", cert. 4; "No one in holy orders may be an officer", cert. 10.

The more common pattern is the reverse: laity employing or directing clergy. 37.6% of gilds maintain or seek a chaplain. Examples:
- "The alderman collects the chaplain's salary" (180);
- "chaplain elected by them" (182);
- "The two wardens to pay the priest" (213);
- a chaplain "to assist the parson daily … whereby the parson's difficulties were much relieved" (382).

## 6. Reliability (random 10%, n = 51)

**Blind first pass** (primary rule-based codes against an independent reading of the page images; `reliability_firstpass.txt`):

| variable | % agreement | κ |
|---|---|---|
| date class, decade, period, pestilence | 100 | 1.00 |
| funeral | 90.2 | 0.80 |
| masses | 90.2 | 0.80 |
| chaplain | 96.1 | 0.91 |
| lights | 96.1 | 0.88 |
| aid | 90.2 | 0.78 |
| general alms | 86.3 | 0.70 |
| feast | 90.2 | 0.39 |
| other | 86.3 | 0.70 |
| founders | 96.1 | 0.88 |
| clergy governance | 100 | 1.00 |

**Adjudication.** Rule errors found in adjudication were corrected (listed in `reliability_firstpass.txt`):
- header text leaking into the benefits column;
- lower-case "feast" missed;
- "collected alms" read as almsgiving.

Agreement after correction (no longer blind): funeral 92%, masses 92%, aid 100%, alms 92%, feast 96% (κ 0.81), other 86% (κ 0.71). Remaining disagreements are mostly cross-references that the codebook expands and the second reading did not.

Both codings were done by the same model. This tests consistency, not independent human judgement. The "feast" and "other" codes are the weakest. Dates, pestilence and the headline purposes (lights, funerals, masses) are robust.

## 7. Cross-check with Toulmin Smith (1870)

Forty-two returns were matched by place and dedication: 10 from Norwich, 17 from Lynn and other Norfolk places, and 15 from Lincoln, Hull, Beverley, York, Lancaster, Chesterfield, Killingholme and Ludlow.

**Foundation dates agree in 37/42.** The five exceptions:

- **Disagreement.** Lincoln, Tilers (cert. 157). Westlake has "No date"; Smith has "was founded A.D. 1346" (p. ~184).
- **Partial.** Chesterfield, St Mary (45). Smith prints "begun … A.D. 1218" (p. ~165) as the foundation date; Westlake doubts it ("No date … (? 1218)").
- **Classification differences** (Westlake is the more cautious in all three):
  - Lancaster (69) and the Lincoln Fullers (153): Westlake records the year as that of the statutes; Smith's side-notes read it as "begun". Smith's own text says "These ordinances were made … A.D. 1377".
  - Ludlow Palmers (392): Westlake gives 1284 as the foundation; Smith says the 1284 ordinances revised earlier ones and that "the foundation and endowment of the gild were some years older".

**Dedications.** Westlake's dedications sometimes differ from Smith's titles, for example "Corpus Christi (St Michael-on-the-Hill)" against "Gild of St Michael on the Hill". At one point Smith reads an illegible dedication as Resurrection.

**Pestilence wording.** None was found in the OCR of either Internet Archive copy of Smith's printed ordinances. "Pestilence" occurs only in the editor's introduction, which notes that some returns date themselves by it. None of the eight Westlake entries that mention the pestilence corresponds, by place, dedication and language, to a return Smith prints. All eight are Latin or French returns.

## 8. Comparison with the literature review

**What the review claims about gilds.**
- `reports/sections/04_black_death.md` says little about English gilds specifically. Its claims about confraternities are that they "expressed lay initiative inside the church, not against it" (para. "Confraternities and charity", on Henderson's Florence). It also says that "wills, chantries, saints and confraternities all ran through the church" and that "demand rose, and the church supplied it". The summary table marks confraternity records as evidence that "demand for intercession rose, but mostly through the church".
- `10_primary_sources.md` adds two things. It notes that Smith's printed ordinances "contain no explicit plague wording, so post-1349 foundations cannot be counted from Smith alone". It also suggests that gilds show devotion rising "in sufferer-controlled channels" and possibly "a shift of trust" away from the parish.

**Assessment.**
- **"Lay initiative inside the church": supported.** Gilds are overwhelmingly lay-founded (90% of described founders) and lay-governed. Clergy have a stated governing role in only 2%. Yet their purposes are ecclesial: lights before church images (80%), masses and lay-hired chaplains (38%), and church fabric (73 gilds). Several explicitly exist to relieve a poor rector or parson.
- **"A shift of trust" away from the parish: qualified.** Lay control of the remedy is clear. Lay control *against* the parish is not: the gilds supplement it.
- **"Demand rose" for intercession: qualified.** Most surviving gilds give post-1349 dates, but survivorship (§2) prevents reading this as proliferation. Explicit plague wording is rare (8/509). Only one entry presents the plague as the occasion of a foundation. Post-1349 foundations are not more focused on the dead than older survivors.
- **"Smith alone cannot count post-1349 foundations": supported.** Westlake's calendar of all 509 returns does yield dates for 59% of gilds. It adds eight pestilence references from Latin and French returns that Smith did not print. The survivorship limit still applies.

**Recommended wording.** The review should not say that English gilds "proliferated" after 1348 on the strength of the 1389 returns. The safe wording is: "most gilds surviving in 1389 dated themselves after 1349."

## 9. Limits

1. **Survivorship.** This is the strongest limit (§2). The returns are a census of survivors, so foundation counts by decade are not foundation rates.
2. **A calendar, not the originals.** Westlake's summaries select and paraphrase. Absence of a purpose in the calendar does not prove absence in the return. Westlake's "c." dates are his conversions of relative statements and are heaped.
3. **Coverage.** Returns survive unevenly: 76% come from Norfolk, Lincolnshire, Cambridgeshire and Suffolk, with 41 from London. Westlake notes that many returns are lost (p. 38). The results describe the East Anglian and Lincolnshire gild world above all.
4. **Self-description to the Crown.** The 1388–9 returns were made to a government suspicious of gilds and their property. Gilds had reasons to stress piety and charity and to understate feasting and political or economic functions. This may depress the "feast" and "craft regulation" counts.
5. **OCR and rules.** Purposes were coded by keyword rules on OCR'd text. Reliability against an image reading is good for the main purposes (κ ≈ 0.8–0.9) and weak for "feast" in the blind pass.
6. **No causal inference.** Nothing here shows that the plague caused gild foundation, or that gild members' motives were plague-related.

## 10. Headline for the article appendix

In the 1388–9 returns calendared by Westlake, 509 English gilds are described. Of the 286 that state a foundation year between 1300 and 1389, 235 (82% [77, 86]) give a year in 1349 or later. Because only gilds that survived to 1388–9 were recorded, this pattern cannot by itself show that gilds multiplied after the Black Death. A constant dissolution rate of about 4% a year would produce it, and explicit references to the pestilence occur in only 8 entries (1.6%). The gilds' stated purposes centre on what lay members controlled: lights (80% of entries with content), provision for dead members' funerals or masses (70%), member relief (35%) and a chaplain the gild itself paid (38%). Founders, where named, are lay in 90% of cases, and clergy are given a governing role in about 2%. The returns thus document lay management of intercession and care inside the parish church, not a turn away from it.

## 11. Editions used (Chicago author-date)

Smith, Toulmin, and Lucy Toulmin Smith, eds. 1870. *English Gilds: The Original Ordinances of More than One Hundred Early English Gilds*. Early English Text Society, Original Series 40. London: N. Trübner for the Early English Text Society. Internet Archive, https://archive.org/details/englishgildsorig0000smit (OCR text; also consulted: https://archive.org/details/englishgildsorig00smit).

Westlake, H. F. 1919. *The Parish Gilds of Mediæval England*. London: Society for Promoting Christian Knowledge; New York: Macmillan. Appendix, "The Gild Certificates of 1389: An Analysis," 137–238. Internet Archive, https://archive.org/details/parishgildsofmed00westuoft.

## Files

- `codebook.md`: categories and decision rules, with dated amendments.
- `data.csv`: one row per gild. It holds the locators (`cert`, `sub`, `page`, `pdf_page`, `ocr_rows`), the verbatim `date_raw`, the codes, a snippet column for each code, and the OCR'd columns 3–5.
- `analysis.py`: prints every table above, using the standard library only.
- `double_coding.csv`: the second coding.
- `reliability_firstpass.txt`: the blind agreement figures.
- `crosscheck_smith.csv`: the Toulmin Smith comparison.
- `pipeline/`: image-processing, OCR, mapping and coding scripts, the transcribed identification table, row maps and manual overrides.
