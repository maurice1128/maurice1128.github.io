# London Husting wills, 1320–1400: pious bequests before and after the plagues of 1348–49 and 1361–62

Project `husting_wills`. All numbers below are printed by `analysis.py` (it reads `data.csv` and `double_coding.csv`). Every will can be traced through its locator (volume, printed page, BHO page, roll and entry number) and the verbatim snippet columns in `data.csv`.

## 1. Question

Did London testators' pious bequests shift after the Black Death (1348–49) and the second plague (1361–62)? The test is between two readings:

- **Redistribution within the church:** gifts move toward intercession that the testator or a lay body controls (chantries, obits, fraternities), alongside the parish and religious houses.
- **Collapse of trust:** gifts move away from the parish and religious houses.

## 2. Source and edition

- **Edition:** Sharpe, ed. (1889; 1890), the calendar of wills enrolled in the Court of Husting, in the British History Online (BHO) digitisation. BHO says the text was "digitised by double rekeying."
- **What an entry is:** a short English abstract, not the will itself. Sharpe says he calendared "the names of the testators, their place of burial (when stated) … bequests for the maintenance of chantries, the fabric of S. Paul's and other churches, as well as of London Bridge, and similar pious and charitable gifts." He omitted "bequests of no special interest or importance" (Sharpe 1889, xlviii).
- **What was enrolled:** the Husting enrolled wills that devised City land. Sharpe notes that testators often made a separate testament of movables, which "does not appear on the rolls" (Sharpe 1889, xxv).
- **The two plagues in the rolls:** Sharpe ties the 1348–49 spike in enrolments to the Black Death and notes a smaller rise in 1361–62 (Sharpe 1889, xxvii).

## 3. Method

**Downloads.** I downloaded all 85 BHO roll pages from 13 Edward II (1319–20) to 1 Henry IV (1399–1400), with a pause of at least 1.5 s between requests. A parser (`scripts/parse.py`) split each page into entries. An entry starts with the testator's surname in bold and ends with "Roll N (M)". There are 1,991 entries on those pages and 1,985 roll locators, so coverage is complete apart from 6 entries whose roll locator is irregular.

**Unit and scope.** The unit is one will. Scope is every entry enrolled in calendar years 1320–1400, which gives N = 1,980. The full population is coded, with no sampling. One "vacant space" entry is excluded, leaving 1,979 for analysis.

**Dating.**
- **Enrolment year:** the regnal year plus the day and month in the court heading (e.g. "[2 Feb.]"). Edward III's regnal year starts 25 January, Richard II's 22 June, Henry IV's 30 September and Edward II's 8 July.
- **Will year:** the "Dated … A.D." year, available for 1,550 of the 1,979 wills.

**Periods.** P1 1320–48, P2 1349–60, P3 1361–75, P4 1376–1400.

**Coding.**
1. I wrote `codebook.md` before coding.
2. The 10% reliability sample (198 wills, `random.seed(20261111)`) was drawn before any rule was written. Rules were developed only on entries outside that sample.
3. The **first coder** is a deterministic rule set (`scripts/code_wills.py`): regular expressions with context exclusions. It ignores the burial clause, addresses ("near the Friars Preachers", "held of the Prior of …"), and gifts to individual friars or nuns. It resolves "the said church" to the church last named.
4. The rules were frozen before the second coding.
5. The **second coder** is the model, reading the 198 sampled entries from their text alone, blind to the rule output (`double_coding.csv`).

**Statistics.** Proportions are given with Wilson 95% intervals. Adjacent periods are compared with pooled two-proportion tests: chi-square with 1 df, no continuity correction. A 4×2 chi-square tests the four periods together.

## 4. Sample

| Period | N wills | Calendar years with enrolments | Mean per year | Women | Clerics | Median length of the summary (words) |
|---|---|---|---|---|---|---|
| P1 1320–48 | 739 | 29 | 25.5 | 85 (11.5%) | 41 | 74 |
| P2 1349–60 | 549 | 11 | 49.9 | 84 (15.3%) | 40 | 98 |
| P3 1361–75 | 395 | 15 | 26.3 | 33 (8.4%) | 33 | 129 |
| P4 1376–1400 | 296 | 25 | 11.8 | 33 (11.1%) | 5 | 154 |

**Enrolment spikes (a mortality marker):**
- 1349: 356 wills, against a mean of 21.2 a year in 1340–47 (16.8 times as many).
- 1350: 50 wills.
- 1361: 130 wills, against a mean of 19.3 a year in 1350–59.
- 1360: no wills. The calendar has no roll for 34 Edward III, and Sharpe notes that Roll 88 is missing.
- 1369 (the third pestilence): no rise (7–26 a year in 1368–70).

Full counts by year are in the `analysis.py` output.

## 5. Reliability (rule coder vs. blind second coding, n = 198)

| Variable | Rule = 1 | Second = 1 | Agreement | Cohen's κ | Rule false positives / negatives |
|---|---|---|---|---|---|
| Parish church | 76 | 73 | 93.4% | 0.86 | 8 / 5 |
| Chantry | 71 | 72 | 99.5% | 0.99 | 0 / 1 |
| Obit | 6 | 6 | 100% | 1.00 | 0 / 0 |
| Masses/trentals | 10 | 10 | 100% | 1.00 | 0 / 0 |
| Lights | 27 | 27 | 100% | 1.00 | 0 / 0 |
| Fraternity | 11 | 10 | 99.5% | 0.95 | 1 / 0 |
| Friars | 24 | 25 | 98.5% | 0.93 | 1 / 2 |
| Monastic | 29 | 29 | 94.9% | 0.80 | 5 / 5 |
| Hospital | 16 | 18 | 99.0% | 0.94 | 0 / 2 |
| Charity (poor, prisons, roads, bridges) | 23 | 23 | 100% | 1.00 | 0 / 0 |
| St Paul's | 17 | 17 | 99.0% | 0.94 | 1 / 1 |
| Named chaplain to pray | 2 | 5 | 98.5% | 0.57 | 0 / 3 |
| Unspecified "pious uses" | 77 | 87 | 91.9% | 0.83 | 3 / 13 |
| Pestilence mention | 0 | 0 | 100% | n/a | 0 / 0 |
| Sex (female) | 18 | 20 | 99.0% | 0.94 | 0 / 2 |

**Where the rules erred:**
- **Parish and monastic false positives** come from three sources:
  - churches named only as the *site* of a chantry, inside a list ("chantries in the said church of S. John and the church of S. Mary atte Naxe");
  - addresses ("his house near the New Abbey");
  - rectors or priors named only to identify a person.
- **"Pious uses" misses** occur because the rules look for the literal phrase "pious/charitable uses". The second coder also counted "to be sold for the good of his soul".
- **Named chaplain** is rare, and κ is low (0.57). It is reported for completeness only.

Because the rules were frozen before the second coding, none of these errors were corrected.

## 6. Results

### Table 1. Share of all wills with each bequest type, by enrolment period (%, Wilson 95% CI)

| Bequest | P1 1320–48 (n=739) | P2 1349–60 (n=549) | P3 1361–75 (n=395) | P4 1376–1400 (n=296) | P1→P2 | P2→P3 |
|---|---|---|---|---|---|---|
| Parish church | 9.5 [7.6–11.8] | 37.3 [33.4–41.5] | 63.0 [58.2–67.7] | 76.4 [71.2–80.8] | +27.9, p<.001 | +25.7, p<.001 |
| Chantry / priest to celebrate | 24.6 [21.7–27.9] | 34.1 [30.2–38.1] | 39.2 [34.6–44.1] | 47.6 [42.0–53.3] | +9.4, p<.001 | +5.2, p=.10 |
| — said to be perpetual | 0.9 [0.5–1.9] | 2.4 [1.4–4.0] | 2.0 [1.0–3.9] | 6.4 [4.1–9.8] | +1.4, p=.04 | −0.3, p=.73 |
| — for years / for life | 8.5 [6.7–10.8] | 8.6 [6.5–11.2] | 9.6 [7.1–12.9] | 15.5 [11.9–20.1] | 0.0, p=.98 | +1.1, p=.58 |
| Obit / anniversary | 1.5 [0.8–2.6] | 2.9 [1.8–4.7] | 4.3 [2.7–6.8] | 9.5 [6.6–13.3] | +1.4, p=.08 | +1.4, p=.25 |
| Masses / trentals | 3.5 [2.4–5.1] | 3.8 [2.5–5.8] | 10.9 [8.2–14.3] | 13.2 [9.8–17.5] | +0.3, p=.77 | +7.1, p<.001 |
| Lights | 3.9 [2.7–5.6] | 7.5 [5.6–10.0] | 15.9 [12.7–19.9] | 22.0 [17.6–27.0] | +3.5, p=.006 | +8.5, p<.001 |
| Fraternity / gild | 0.5 [0.2–1.4] | 3.6 [2.4–5.6] | 11.1 [8.4–14.6] | 20.6 [16.4–25.6] | +3.1, p<.001 | +7.5, p<.001 |
| Friars | 1.5 [0.8–2.6] | 6.0 [4.3–8.3] | 21.0 [17.3–25.3] | 34.1 [29.0–39.7] | +4.5, p<.001 | +15.0, p<.001 |
| Monasteries / nunneries / canons | 7.2 [5.5–9.3] | 12.8 [10.2–15.8] | 22.5 [18.7–26.9] | 28.0 [23.2–33.4] | +5.6, p<.001 | +9.8, p<.001 |
| Hospitals / lepers | 3.1 [2.1–4.6] | 7.5 [5.6–10.0] | 15.4 [12.2–19.3] | 22.6 [18.2–27.7] | +4.4, p<.001 | +8.0, p<.001 |
| St Paul's | 2.8 [1.9–4.3] | 6.4 [4.6–8.7] | 18.2 [14.7–22.3] | 17.6 [13.7–22.3] | +3.5, p=.002 | +11.9, p<.001 |
| Poor / prisoners / roads / bridges | 6.0 [4.5–7.9] | 10.0 [7.8–12.8] | 20.0 [16.4–24.2] | 25.3 [20.7–30.6] | +4.1, p=.007 | +10.0, p<.001 |
| Unspecified "pious uses" | 32.9 [29.6–36.4] | 49.0 [44.8–53.2] | 49.4 [44.5–54.3] | 36.8 [31.5–42.5] | +16.1, p<.001 | +0.4, p=.91 |
| Any specified pious/charitable bequest | 40.2 [36.7–43.8] | 61.7 [57.6–65.7] | 78.0 [73.6–81.8] | 87.2 [82.9–90.5] | +21.6, p<.001 | +16.2, p<.001 |
| Burial place stated | 11.2 | 49.7 | 84.1 | 85.1 | | |
| Mentions plague/pestilence | 0 | 0 | 1 (0.3) | 0 | | |

**Every category rises.** The pattern runs in step with two things:
- the appearance of the burial clause (stated in 11% of P1 summaries, 84–85% in P3–P4);
- longer summaries (median 74 → 154 words).

This is mainly a change in *what reached the enrolled text and Sharpe's abstract*. Before c. 1349 most enrolled wills dealt with land only; the testament of movables, where most small pious gifts sat, was usually separate and not enrolled (Sharpe 1889, xxv). Table 1 therefore cannot by itself measure a change in piety.

### Table 2. Wills whose summary states a burial place (a proxy for wills whose "soul" part was enrolled and calendared)

| Bequest | P1 (n=83) | P2 (n=273) | P3 (n=332) | P4 (n=252) | P1→P2 | P2→P3 |
|---|---|---|---|---|---|---|
| Parish church | 28.9 [20.3–39.4] | 49.1 [43.2–55.0] | 69.9 [64.7–74.6] | 79.8 [74.4–84.3] | +20.2, p=.001 | +20.8, p<.001 |
| Chantry | 38.6 [28.8–49.3] | 41.0 [35.4–46.9] | 41.3 [36.1–46.6] | 50.8 [44.7–56.9] | +2.5, p=.69 | +0.2, p=.95 |
| Obit | 4.8 [1.9–11.7] | 3.3 [1.7–6.1] | 4.8 [3.0–7.7] | 9.5 [6.5–13.8] | −1.5, p=.52 | +1.5, p=.35 |
| Masses / trentals | 8.4 [4.1–16.4] | 5.1 [3.1–8.4] | 11.7 [8.7–15.7] | 14.7 [10.8–19.6] | −3.3, p=.26 | +6.6, p=.004 |
| Lights | 12.0 [6.7–20.8] | 9.5 [6.6–13.6] | 18.1 [14.3–22.6] | 23.4 [18.6–29.0] | −2.5, p=.50 | +8.5, p=.003 |
| Fraternity | 2.4 [0.7–8.4] | 5.5 [3.4–8.9] | 12.0 [9.0–16.0] | 23.4 [18.6–29.0] | +3.1, p=.25 | +6.6, p=.005 |
| Friars | 6.0 [2.6–13.3] | 9.5 [6.6–13.6] | 22.6 [18.4–27.4] | 38.9 [33.1–45.0] | +3.5, p=.32 | +13.1, p<.001 |
| Monastic | 22.9 [15.2–33.0] | 15.8 [11.9–20.5] | 23.8 [19.5–28.7] | 28.6 [23.3–34.4] | −7.1, p=.13 | +8.0, p=.014 |
| Hospital | 9.6 [5.0–17.9] | 11.4 [8.1–15.7] | 17.2 [13.5–21.6] | 24.2 [19.3–29.9] | +1.7, p=.66 | +5.8, p=.044 |
| St Paul's | 7.2 [3.4–14.9] | 10.3 [7.2–14.4] | 21.4 [17.3–26.1] | 20.2 [15.7–25.6] | +3.0, p=.41 | +11.1, p<.001 |
| Poor / prisoners / roads / bridges | 8.4 [4.1–16.4] | 13.9 [10.3–18.5] | 22.0 [17.9–26.7] | 27.8 [22.6–33.6] | +5.5, p=.19 | +8.1, p=.011 |
| Self/lay intercession (chantry, obit, masses, fraternity, named chaplain) | 44.6 [34.4–55.3] | 45.4 [39.6–51.4] | 53.0 [47.6–58.3] | 66.7 [60.6–72.2] | +0.8, p=.89 | +7.6, p=.06 |
| Institutions (parish, friars, monastic, hospital, St Paul's) | 38.6 [28.8–49.3] | 55.3 [49.4–61.1] | 75.3 [70.4–79.6] | 85.7 [80.9–89.5] | +16.8, p=.007 | +20.0, p<.001 |

**Dispersion.** I counted how many of the 11 specified bequest types each will contains. In wills stating a burial place, the mean rises:

| | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| Mean number of bequest types | 1.49 [1.05–1.93] | 1.74 [1.52–1.97] | 2.65 [2.42–2.88] | 3.41 [3.13–3.70] |

### Table 3. Who holds or supervises the chantry/obit property (wills with a chantry or obit)

| Holder named in the chantry/obit passage | P1 (n=188) | P2 (n=193) | P3 (n=161) | P4 (n=153) |
|---|---|---|---|---|
| Private only: wife, heirs or executors, "charged with the maintenance of a chantry" | 88.3 [82.9–92.1] | 78.8 [72.5–83.9] | 80.1 [73.3–85.6] | 64.1 [56.2–71.2] |
| Parish body: rector and/or churchwardens or parishioners | 2.1 [0.8–5.3] | 4.1 [2.1–8.0] | 6.8 [3.9–11.8] | 19.6 [14.1–26.6] |
| Lay corporate: Mayor/Commonalty, Bridge wardens, craft or fraternity | 2.7 [1.1–6.1] | 8.8 [5.6–13.7] | 9.3 [5.7–14.8] | 15.0 [10.2–21.5] |
| Church corporate: Dean and Chapter, prior and convent, master and brethren | 8.0 [4.9–12.7] | 10.9 [7.2–16.1] | 8.1 [4.8–13.3] | 15.0 [10.2–21.5] |
| Parish body **or** lay corporate | 4.3 [2.2–8.2] | 13.0 [8.9–18.4] | 13.7 [9.2–19.8] | 29.4 [22.8–37.1] |

- Private only: P1→P2 −9.5 points (p = .012); P3→P4 −16.1 points (p = .001).
- Lay corporate: P1→P2 +6.1 points (p = .010).
- This variable was not double-coded. It rests on co-occurrence in a sentence, so it is a rough indicator.

### By sex

Women are 235 of 1,979 testators. Their shares follow the men's direction. The intervals are wide (P3 and P4 have 33 women each), and no change between adjacent periods for women's chantries is significant: 29.4% → 28.6% → 39.4% → 45.5%. Friars rise for women as for men: 1.2% → 4.8% → 21.2% → 39.4%.

### Sensitivity

| Check | Chantry | Parish | Friars | Fraternity |
|---|---|---|---|---|
| Lay testators only | 24.2 / 34.0 / 39.8 / 47.4 | | 1.1 / 6.5 / 22.4 / 34.4 | 0.6 / 3.9 / 11.3 / 21.0 |
| Excluding the 356 enrolments of 1349 | 24.6 / 39.9 / 39.2 / 47.6 | 9.5 / 61.1 / 63.0 / 76.4 | | |
| Periods by the will's own date (n = 1,550) | 28.4 / 36.2 / 40.4 / 46.5 | | 1.8 / 9.5 / 22.7 / 35.8 | 0.9 / 4.8 / 12.9 / 23.0 |
| Summaries of 120 words or fewer | 17.8 / 21.6 / 22.2 / 17.3 (flat) | | rises 0.7 → 13.5 | |
| Summaries over 120 words | 47.4 / 56.3 / 53.5 / 64.1 | | rises 4.1 → 45.3 | |

- **Lay testators only:** same pattern as all wills.
- **Excluding 1349:** the short summaries of 1349 dilute P2.
- **By the will's own date:** same direction as by enrolment date.
- **By summary length:** with length held roughly constant, chantries do not move between P1 and P3, while friars still rise.

### Pestilence in the text

One summary mentions plague: HW1563, Sharpe vol. 2, p. 125, Roll 97 (15), enrolled 1369. The testator "makes his will seeing the peril of this world and especially of the existing plague." Sharpe's abstracts rarely keep such phrases, so this absence says nothing about how testators felt.

## 7. What the data can and cannot show

**Can show:**
- In this calendar, gifts to the parish church, friars, St Paul's, hospitals and religious houses appear in a rising share of summaries after 1349, and again after 1361. Nothing here looks like withdrawal from church institutions.
- Chantries funded by City property were already common before the plague: 25% of all wills, and 39% of wills whose summary states a burial place. Among the latter, the chantry share does not jump after 1348–49 or 1361–62 (39% → 41% → 41%). It rises only after 1376 (51%).
- Lay-held or parish-held intercession grows slowly. Fraternity gifts go from about 1% to 21%. Chantries placed with parish bodies or lay corporations grow from 4.3% [2.2–8.2] to 29.4% [22.8–37.1] of chantry/obit wills. This growth runs through the church's own sites (parish churches and their fraternities).

**Cannot show:**
- **Recording artefacts.** The largest shifts coincide with changes in what was enrolled (a testament of land vs. of movables) and in how much Sharpe abstracted. Small movable bequests are under-recorded before 1349. Sharpe's "&c." hides further items, and he omitted what he judged unimportant. The burial-stated subset reduces this problem but does not remove it.
- **Who is covered.** Only property-holding Londoners (and some outsiders holding City property) who had wills enrolled in the Husting. That is mostly men; women are 12%. Wills proved only in church courts are excluded.
- **Amounts.** These are presence/absence codes. They do not measure money, the number of masses, or the length of chantries. Cohn's and Chiffoleau's key measures (the size and concentration of gifts, counts of masses) cannot be reproduced here.
- **Coding error.** The rules overstate parish and monastic gifts slightly (8 and 5 false positives per 198). They miss about 15% of "for the good of his soul" sales. The chantry-holder variable was not double-coded.
- **Causation.** Enrolment periods mix the shock of plague with secular change: the growth of fraternities and of parish churchwardens, and possibly a change in Sharpe's calendaring style between Part 1 (to 1358) and Part 2 (from 1358).

## 8. Comparison with the literature review (sections 04 and 08)

**Cohn (1992), Tuscan and Umbrian cities.** The review summarises Cohn as finding the decisive change after the second plague (1363). Testators stopped spreading many small pious gifts and concentrated on fewer, larger, perpetual memorial gifts within church institutions.

The London calendar does not show that concentration. The number of bequest types per will *rises* after 1361, and perpetual chantries stay rare (2% of wills in P3, 6% in P4). It does show the second plague as a point where friars, St Paul's, masses, lights and fraternities appear more often (P2→P3). It also shows memorial chantries already common before 1348. Because of the recording problems above, this is weak evidence against concentration in London, not a refutation of Cohn.

**Chiffoleau (1980), Avignon.** The review summarises him as finding accumulated masses and confraternities, with the investment still flowing through the church. London points the same way:
- masses and trentals: 4% → 11–13% of wills;
- lights: 4% → 22%;
- fraternities: about 1% → 21%.

But this calendar cannot count masses.

## 9. Headline for the article appendix

In the calendared Husting wills of property-holding Londoners enrolled 1320–1400 (N = 1,979), gifts to parish churches, friars, St Paul's, hospitals and religious houses appear more often, not less, after 1348–49 and again after 1361–62. Intercession that testators or lay bodies controlled also grows within the same churches:
- wills with fraternity gifts: 0.5% before 1349, 20.6% in 1376–1400;
- chantries entrusted to parish or lay corporate bodies: 4.3% of chantry/obit wills in P1, 29.4% in P4.

Chantries funded by City property were already common before the plague (about 39% of wills whose summary records a burial). Their share did not jump after either plague and rose only after 1376. Much of the apparent post-plague increase reflects changes in what was enrolled and in how fully the editor summarised it. These are binary codes from nineteenth-century abstracts (rule coding, κ = 0.80–1.00 for the main categories), not measures of value. The evidence fits "devotion redistributed within the church" better than "trust in the church collapsed", but it cannot establish either.

## 10. Files

- `codebook.md`: categories, rules and examples, written before coding.
- `data.csv`: one row per will (1,980 rows). It holds the locator (`vol`, `page`, `bho_page`, `roll`, `court_heading`), dates, testator, sex, occupation, cleric flag, burial site, 14 bequest indicators, chantry sub-codes and holder, a verbatim snippet for each coded item, and the summary's word count. The full BHO text is not redistributed; use the locator.
- `double_coding.csv`: the blind second coding of the 198-will random sample.
- `analysis.py`: prints every table above. Run `python3 -I analysis.py` (standard library only).
- `scripts/parse.py`, `scripts/code_wills.py`, `scripts/pages.tsv`: rebuild `data.csv` from the BHO pages.
  - Download each URL listed in `pages.tsv`.
  - Run `python3 -I parse.py RAW_DIR pages.tsv entries.json`.
  - Keep enrolment years 1320–1400 and number the entries HW0001… in calendar order.
  - Run `python3 -I code_wills.py wills.json data.csv`.

  The coding rules were frozen before the second coding. The only later change to `code_wills.py` added the word-count output column.

## 11. Edition used (Chicago author-date)

Sharpe, Reginald R., ed. 1889. *Calendar of Wills Proved and Enrolled in the Court of Husting, London, A.D. 1258–A.D. 1688*. Part 1, *1258–1358*. London: printed by order of the Corporation of the City of London. British History Online. https://www.british-history.ac.uk/court-husting-wills/vol1.

Sharpe, Reginald R., ed. 1890. *Calendar of Wills Proved and Enrolled in the Court of Husting, London, A.D. 1258–A.D. 1688*. Part 2, *1358–1688*. London: printed by order of the Corporation of the City of London. British History Online. https://www.british-history.ac.uk/court-husting-wills/vol2.

Both accessed 11 November 2026. BHO's own record gives the original publisher as "Her Majesty's Stationery Office, London". Check the imprint against a scan before the article goes to print.
