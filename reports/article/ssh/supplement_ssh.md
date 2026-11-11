# Online supplementary material

**Article:** "Who Holds the Remedy? Suffering, Lay Initiative, and the Church in Plague-Era England and the United States under Slavery"

This supplement is anonymized for review. It summarizes the three codebooks (S1), gives the full reliability tables (S2) and robustness checks (S3), lists the locators of the interview passages quoted in the article (S4), and states where data and code are deposited (S5). Every figure is printed by the analysis script of the dataset concerned.

**Who did the coding.** A large language model ([TOOL, VERSION, DATES]) collected, parsed, coded, and analyzed all three datasets under the author's direction. The codebooks were written before coding and amended as documented in S1. No human coder has yet checked the codings. Second codings are described in S2.

---

## S1. Codebook summaries

### S1.1 London Husting wills, 1320–1400

- **Source.** Sharpe (1889, 1890), in the British History Online text. An entry is the editor's English abstract of a will enrolled in the Court of Husting. The court enrolled wills that devised City land. Sharpe calendared pious and charitable gifts and omitted bequests that he judged of no special interest.
- **Unit and scope.** One will. Every entry enrolled in calendar years 1320–1400 (N = 1,980). One "vacant space" entry is excluded, leaving 1,979.
- **Periods.** By enrollment year: 1320–48, 1349–60, 1361–75, 1376–1400. The will's own date is available for 1,550 wills and is used in a sensitivity check.
- **Bequest codes (present or absent).** Parish church; chantry or priest to celebrate (with sub-codes for perpetual and for a term); obit or anniversary; masses or trentals; lights; fraternity or gild; friars; monasteries, nunneries, and canons; hospitals and lepers; the poor, prisoners, roads, and bridges; St. Paul's; a named chaplain to pray; unspecified "pious uses"; any mention of pestilence. The burial clause, addresses, and gifts to individual friars or nuns are not counted as bequests to institutions.
- **Holder of chantry or obit property.** For wills with a chantry or obit: private (wife, heirs, executors, or no holder named); parish body; lay corporate body; church corporate body. Detected by co-occurrence in a sentence. Not double-coded.
- **Other fields.** Sex, occupation, cleric flag, burial site, word count of the summary, and a verbatim snippet and locator for each coded item.
- **Procedure and amendments.** The first coding is a deterministic rule set (regular expressions with context exclusions). The reliability sample was drawn before any rule was written, and rules were developed only on entries outside it. The rules were frozen before the second coding. The codebook file was last edited after the data file was produced. The one later change to the coding script added the word-count column.

### S1.2 English gild returns, 1388–89

- **Source.** Westlake (1919: 137–238), the calendar of the gild certificates returned under the writs of November 1, 1388. The calendar is an English summary of Latin, French, and English returns. Page images were rotated, cut into cells, and read by optical character recognition. Certificate number, place, dedication, and the date statement were transcribed from the page images.
- **Unit and scope.** One gild (509 gilds on 471 certificates).
- **Foundation date.** Class of statement (exact year; approximate; "time without memory"; date of statutes or charter only; "lately begun"; reign only; relative to the pestilence; none), year where given, decade, and period (before or after 1349).
- **Purposes (present or absent).** Lights; masses or prayers for dead members; funeral attendance or burial; chaplain or priest maintained or sought; relief of members; alms to the poor generally; feast; other (church fabric, procession, peace among members, pilgrimage, bells, craft regulation, roads or bridges, hospital, plays). Cross-references in the calendar ("as in 166") are expanded.
- **Founders.** Lay parishioners or townspeople; craft or occupational group; mixed; clergy. Coded by reading each sentence that contains a founding verb.
- **Clergy role in governance.** Coded 1 only where a cleric has a stated part in governing the gild. Cases in which lay people direct, pay, or elect a chaplain are coded 0.
- **Amendments made during coding (recorded in the codebook).** The unit was confirmed as the gild, not the certificate. Date classes were added for statements that the first list did not foresee ("lately begun"; a year that dates statutes or a charter; reign only; pre-1300 tradition; dates relative to the pestilence). Westlake's "c." dates are kept as approximate, and results are reported with and without them. Founders and clerical governance were coded by reading, because keywords proved unreliable. Rule errors found when the second coding was adjudicated were corrected and are listed in the deposited reliability file.

### S1.3 Interviews with formerly enslaved people, 1936–38

- **Source.** Federal Writers' Project (1941), in the Project Gutenberg transcription of the Library of Congress deposit (34 eBooks). The supplements later edited by Rawick and the Virginia interviews published separately are not included.
- **Frame and sample.** 2,178 informant entries were parsed and 2,143 narratives segmented. A keyword screen found 1,418 that mention religion (66.2%; 95% CI 64.1–68.1). From these, 400 were drawn at random with a recorded seed, in proportion to each state's share: Alabama 26, Arkansas 94, Florida 12, Georgia 40, Indiana 10, Kansas 0, Kentucky 5, Maryland 5, Missouri 15, Mississippi 7, North Carolina 33, Ohio 7, Oklahoma 18, South Carolina 58, Tennessee 6, Texas 61, Virginia 3.
- **Worship control before 1865.** Four component codes: white-supervised; Black-led with permission; secret; forbidden. Derived: one mode, or "mixed" where two or more are reported. "Black control" means Black-led or secret.
- **Obedience preaching.** Yes where preaching heard by the enslaved is reported as centered on obedience to masters. No where other content is described.
- **Attitude to white preachers, the white church, or the master's religion.** Negative, positive, neutral, or not stated.
- **Faith before freedom.** Yes only where the narrative states that an identifiable enslaved person prayed, converted, shouted in worship, or trusted God before 1865. Attendance alone does not count. Subject: self, kin, or others.
- **Other codes.** Timing of the informant's own conversion; prayer for freedom; any postwar church; postwar church identifiable as Black-run; interviewer and documented race of interviewer; age; whether the testimony is hearsay only.
- **Evidence rule.** Every substantive code carries a verbatim passage and a locator (eBook number and line). A script checked each passage against the source text.
- **Procedure and amendments.** The codebook was written before any sampled narrative was read. The first coding used keyword-selected extracts, capped at about 3,200 characters. After the independent second coding, six interviewer attributions were corrected, and three counts are now reported as bounds (S2.3). All changes are listed in the change log deposited with the data.

---

## S2. Reliability

### S2.1 London wills: rule coding against a blind second reading (n = 198)

| Variable | Rule = 1 | Second = 1 | Agreement | Cohen's κ | Rule false positives / negatives |
|---|---|---|---|---|---|
| Parish church | 76 | 73 | 93.4% | 0.86 | 8 / 5 |
| Chantry | 71 | 72 | 99.5% | 0.99 | 0 / 1 |
| Obit | 6 | 6 | 100% | 1.00 | 0 / 0 |
| Masses, trentals | 10 | 10 | 100% | 1.00 | 0 / 0 |
| Lights | 27 | 27 | 100% | 1.00 | 0 / 0 |
| Fraternity | 11 | 10 | 99.5% | 0.95 | 1 / 0 |
| Friars | 24 | 25 | 98.5% | 0.93 | 1 / 2 |
| Monastic | 29 | 29 | 94.9% | 0.80 | 5 / 5 |
| Hospital | 16 | 18 | 99.0% | 0.94 | 0 / 2 |
| Poor, prisons, roads, bridges | 23 | 23 | 100% | 1.00 | 0 / 0 |
| St. Paul's | 17 | 17 | 99.0% | 0.94 | 1 / 1 |
| Named chaplain to pray | 2 | 5 | 98.5% | 0.57 | 0 / 3 |
| Unspecified "pious uses" | 77 | 87 | 91.9% | 0.83 | 3 / 13 |
| Pestilence mention | 0 | 0 | 100% | not defined | 0 / 0 |
| Sex (female) | 18 | 20 | 99.0% | 0.94 | 0 / 2 |

The second coder is the language model reading each sampled entry without sight of the rule output. Rule errors were not corrected afterward. Parish and monastic false positives arise from churches named only as the site of a chantry, from addresses, and from rectors or priors named to identify a person.

### S2.2 Gild returns: rule-based codes against a reading of the page images (n = 51)

| Variable | Agreement, blind first pass | κ, blind first pass |
|---|---|---|
| Date class, decade, period, pestilence mention | 100% | 1.00 |
| Funeral | 90.2% | 0.80 |
| Masses | 90.2% | 0.80 |
| Chaplain | 96.1% | 0.91 |
| Lights | 96.1% | 0.88 |
| Relief of members | 90.2% | 0.78 |
| General alms | 86.3% | 0.70 |
| Feast | 90.2% | 0.39 |
| Other | 86.3% | 0.70 |
| Founders | 96.1% | 0.88 |
| Clergy role in governance | 100% | 1.00 |

Both codings were made by the same language model, so the table tests consistency and not independent human judgment. After adjudication, which is no longer blind, agreement was 92% for funerals and masses, 100% for relief, 92% for alms, and 96% for feasts (κ 0.81).

**Cross-check with Smith (1870).** Forty-two returns printed or summarized by Smith were matched by place and dedication. Foundation dates agree in 37. The five exceptions are one disagreement (Lincoln Tilers), one partial agreement (Chesterfield), and three differences of classification in which the calendar is the more cautious.

### S2.3 Interviews: independent second coding (n = 40)

| Variable | Agreement | Cohen's κ | Substantive codes, first / second coder |
|---|---|---|---|
| White-supervised, Black-led, secret, forbidden (each) | 40/40 | 1.00 | 20/20, 3/3, 6/6, 1/1 |
| Worship control; Black control (derived) | 40/40 | 1.00 | 24 / 24 |
| Obedience preaching | 40/40 | 1.00 | 5 / 5 |
| Attitude to white preachers | 35/40 | 0.82 (0.63 among the 21 where both state an attitude) | 21 / 21 |
| Conversion timing | 39/40 | 0.79 | 2 / 3 |
| Faith before freedom | 37/40 | 0.83 | 11 / 14 |
| Subject of faith | 37/40 | 0.85 | 11 / 14 |
| Postwar church, any | 33/40 | 0.64 | 12 / 19 |
| Postwar Black-run church | 39/40 | 0.79 | 2 / 3 |
| Prayer for freedom | 40/40 | not defined (no substantive code by either coder) | 0 / 0 |
| Interviewer race (context) | 38/40 at the blind comparison; 39/40 after one row was corrected | 0.85; 0.93 | 7 / 9; 8 / 9 |
| Hearsay only (context) | 37/40 | 0.63 | 3 / 6 |

The second coder was a separate session of the same language model. It was given only the codebook and the locators, read each narrative in full, and saved its codes before any first-coder file was opened. It was not a human rater. In all 20 disagreements on substantive variables, the first coding has no code or a neutral code where the second has a substantive one: 5 arise from text outside the keyword extract, 8 from ambiguity in the codebook, and 7 from judgment. The first-coder counts for faith before freedom, postwar church, and non-neutral attitude are therefore reported as lower bounds, and the neutral count as an upper bound.

**Intra-coder stability.** Before the independent coding, the first coder recoded the same 40 narratives in the same working session. Agreement was 95% to 100% (κ 0.88 to 1.00). This measures stability only and is not reported in the article as reliability.

---

## S3. Robustness checks

### S3.1 London wills

**All wills, by enrollment period (%).** These figures mainly reflect changes in what was enrolled and abstracted (see the article, section 4.3).

| Bequest | 1320–48 (n = 739) | 1349–60 (n = 549) | 1361–75 (n = 395) | 1376–1400 (n = 296) |
|---|---|---|---|---|
| Parish church | 9.5 | 37.3 | 63.0 | 76.4 |
| Chantry or priest to celebrate | 24.6 | 34.1 | 39.2 | 47.6 |
| Chantry said to be perpetual | 0.9 | 2.4 | 2.0 | 6.4 |
| Obit | 1.5 | 2.9 | 4.3 | 9.5 |
| Masses, trentals | 3.5 | 3.8 | 10.9 | 13.2 |
| Lights | 3.9 | 7.5 | 15.9 | 22.0 |
| Fraternity | 0.5 | 3.6 | 11.1 | 20.6 |
| Friars | 1.5 | 6.0 | 21.0 | 34.1 |
| Monasteries, nunneries, canons | 7.2 | 12.8 | 22.5 | 28.0 |
| Hospitals, lepers | 3.1 | 7.5 | 15.4 | 22.6 |
| St. Paul's | 2.8 | 6.4 | 18.2 | 17.6 |
| Poor, prisoners, roads, bridges | 6.0 | 10.0 | 20.0 | 25.3 |
| Unspecified "pious uses" | 32.9 | 49.0 | 49.4 | 36.8 |

**Enrollment counts.** 1349: 356 wills, against a mean of 21.2 a year in 1340–47. 1350: 50. 1361: 130, against a mean of 19.3 a year in 1350–59. 1360: none (the roll is missing). 1369, the third pestilence: no rise.

**Sensitivity checks (%, four periods in order).**

| Check | Chantry | Parish | Friars | Fraternity |
|---|---|---|---|---|
| Lay testators only | 24.2 / 34.0 / 39.8 / 47.4 | | 1.1 / 6.5 / 22.4 / 34.4 | 0.6 / 3.9 / 11.3 / 21.0 |
| Excluding the 356 enrollments of 1349 | 24.6 / 39.9 / 39.2 / 47.6 | 9.5 / 61.1 / 63.0 / 76.4 | | |
| Periods by the will's own date (n = 1,550) | 28.4 / 36.2 / 40.4 / 46.5 | | 1.8 / 9.5 / 22.7 / 35.8 | 0.9 / 4.8 / 12.9 / 23.0 |
| Summaries of 120 words or fewer | 17.8 / 21.6 / 22.2 / 17.3 | | rises from 0.7 to 13.5 | |
| Summaries of more than 120 words | 47.4 / 56.3 / 53.5 / 64.1 | | rises from 4.1 to 45.3 | |

**By sex.** Women are 235 of 1,979 testators. Their chantry shares are 29.4, 28.6, 39.4, and 45.5 percent across the four periods, with no significant change between adjacent periods. Gifts to friars rise as for men: 1.2, 4.8, 21.2, and 39.4 percent.

**Pestilence.** One summary mentions plague (Sharpe 1890: 125; Roll 97 (15), enrolled 1369).

### S3.2 Gild returns

**Stated foundation years by decade (survivors to 1388–89).**

| Decade | All with a year | Exact | Approximate |
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

**Survivorship.** Assume a constant rate of foundation and a constant annual hazard of dissolution, h. The observed ratio of annual rates after and before 1349 (5.5) would then arise from survival alone if h is about 0.039, a half-life of about 18 years. Survivors were also rising before 1349, by a factor of about 1.4 per decade. Against that trend, observed counts are 2.0 times the projection in 1349–59, about 1.5 times in the 1360s and 1370s, and 0.86 times in the 1380s. The projection rests on 51 gilds and is fragile. The data are compatible with a modest excess of foundations after 1349 and equally with survivorship alone.

**Heaping.** Of 39 approximate years in 1300–89, 22 end in 9. Only 6 gilds give 1349 as an exact year.

**Purposes by period of stated foundation.**

| Purpose | Before 1349 (n = 51) | 1349 or later (n = 233) | Fisher p |
|---|---|---|---|
| Funeral | 62.7% | 56.2% | 0.44 |
| Masses for the dead | 74.5% | 58.4% | 0.039 |
| Chaplain | 51.0% | 36.5% | 0.059 |
| Lights | 84.3% | 83.7% | 1.00 |
| Relief of members | 41.2% | 35.2% | 0.43 |
| General alms | 39.2% | 34.8% | 0.63 |
| Feast | 19.6% | 11.6% | 0.17 |
| Other | 33.3% | 40.8% | 0.35 |

Gilds dated after 1349 are not more concerned with the dead than older survivors. The p-values are unadjusted, and none would survive a Bonferroni correction.

**Pestilence mentions (8 of 509).** Chesterton (cert. 13); March (27); Tydd St Giles (36); London, St. Mary at St. Bride's (203); Lynn, St. James (251); Lynn, Corpus Christi (279); Oxford, St. Thomas (391); London, Brewers at All Hallows London Wall (471). All eight are Latin or French returns. None corresponds to a return printed by Smith (1870).

**Coverage.** Norfolk 164 gilds, Lincolnshire 123, Cambridgeshire 60, Suffolk 39, London 41.

### S3.3 Interviews

**Faith before freedom by mode of worship (206 narratives that describe worship).** Secret 11/17 (64.7%); mixed 25/50 (50.0%); Black-led with permission 8/26 (30.8%); white-supervised 21/110 (19.1%); forbidden 0/3. Chi-square = 25.8, df = 4, p = 3 × 10⁻⁵; two cells have expected counts below 5.

**Checks on the association between Black control of worship and stated faith.**

| Check | Faith stated where Black control is reported | Where it is not | Odds ratio or p |
|---|---|---|---|
| All 206 narratives | 44/92 = 47.8% | 21/114 = 18.4% | OR 4.06 (2.17–7.59) |
| Informant's own faith or a relative's only | 21/92 = 22.8% | 16/114 = 14.0% | OR 1.81 (0.88–3.72); p = 0.14 |
| Faith evidence not part of the worship passage | 28/92 = 30.4% | 20/114 = 17.5% | OR 2.06 (1.07–3.96); p = 0.03 |
| Excluding hearsay-only narratives (n = 188) | 46.3% | 19.8% | p = 0.0001 |
| White or unknown interviewers only (n = 182) | 37/81 = 45.7% | 18/101 = 17.8% | Fisher p = 8 × 10⁻⁵ |
| Informants aged 80 or more (n = 110) | 44.7% | 14.3% | p = 0.0005 |
| Stratified by state | | | Mantel–Haenszel OR 3.36 |

**Interviewer race.** A Black interviewer is documented for 53 narratives and a white interviewer for 11. The remaining 336 are undocumented and probably mostly white.

| Reported | Black interviewer | White or unknown | Fisher p |
|---|---|---|---|
| Obedience-only preaching | 7/53 = 13.2% | 18/347 = 5.2% | 0.034 |
| Negative attitude, all narratives | 7/53 = 13.2% | 15/347 = 4.3% | 0.017 |
| Negative attitude, among those stating an attitude | 7/21 = 33.3% | 15/153 = 9.8% | 0.007 |
| Positive attitude, among those stating an attitude | 3/21 = 14.3% | 36/153 = 23.5% | 0.42 |
| Black control of worship | 11/53 = 20.8% | 81/347 = 23.3% | 0.86 |
| Faith before freedom | 12/53 = 22.6% | 60/347 = 17.3% | 0.34 |
| Prayer for freedom | 4/53 = 7.5% | 9/347 = 2.6% | 0.079 |
| Postwar Black-run church | 10/53 = 18.9% | 31/347 = 8.9% | 0.047 |

These comparisons are fragile. Two of them crossed p = 0.05 only after six interviewer attributions were corrected. One reclassified narrative carries obedience preaching, a negative attitude, and a postwar Black-run church at once. The script prints ten comparisons, and none is adjusted for multiple testing. Black interviewers are concentrated in Arkansas (30 of 53) and Florida (12), so the comparison is confounded with state.

**Informants' age.** Median 83 at interview (interquartile range 78–88; age recorded for 301). Twenty-one narratives are hearsay only.

**Questionnaire.** The national questionnaire asked whether the slaves had a church on the plantation and asked informants to say why they joined a church. The first prompt steers toward plantation churches, and the second raises reports of present-day membership.

---

## S4. Locators for interview passages quoted in the article

| Informant | Volume | Project Gutenberg file and line |
|---|---|---|
| Susan Merritt | XVI, Texas, part 3 | pg35380.txt, lines 2340–42 |
| William Mathews | XVI, Texas, part 3 | pg35380.txt, lines 2120–21 |
| Charlie Van Dyke | I, Alabama | pg36020.txt, lines 12896–97 |
| Minnie Davis | IV, Georgia, part 1 | pg13602.txt, lines 7131–33 |

---

## S5. Data and code availability

The three datasets, their codebooks, the second codings, the reliability files, the change logs, and the analysis scripts are deposited at [REPOSITORY, anonymized for review]. Each analysis script uses only the Python standard library and reprints every figure in the article and in this supplement. The full texts of the editions are not redistributed. Each coded row carries the locator needed to find its source: volume, page, and roll for the wills; certificate, page, and image for the gilds; eBook number and line for the interviews. The editions are public: Sharpe (1889, 1890) at British History Online, Westlake (1919) and Smith (1870) at the Internet Archive, and the Federal Writers' Project (1941) narratives at Project Gutenberg.
