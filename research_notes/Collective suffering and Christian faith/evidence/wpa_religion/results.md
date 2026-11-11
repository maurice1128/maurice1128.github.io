# Religion under slavery in the WPA ex-slave narratives: a coded random sample (project `wpa_religion`)

Prepared 2026-11-11 under `_EVIDENCE_BRIEF.md`. All counts come from `data.csv`, `double_code.csv`, `second_coder.csv` and `corpus_screen.csv` in this folder. Revised 2026-11-11 after an independent second coding and a correction of six interviewer attributions, and again the same day after the interviewer columns were re-read against the source text for all 400 narratives; every change is listed in the change log at the end. Running `python3 analysis.py` re-prints every table. Each coded value in `data.csv` carries a verbatim snippet and a locator (Gutenberg eBook number, line number in the plain-text file, volume and informant). The merge script checked all 400 rows against the source text and found no non-verbatim snippets.

## Headline (for an article appendix)

We drew a state-stratified random sample of 400 of the 1,418 WPA ex-slave narratives (Library of Congress deposit, Project Gutenberg edition) that mention religion, and coded it against a pre-registered codebook. Of the 206 narratives that describe how worship was organised before 1865, 44.7% (95% CI 38.0–51.5) report some Black-controlled worship, either permitted Black-led meetings or secret meetings. 53.4% report white-supervised worship only. Where preaching content is described, two-thirds of reports are obedience-only sermons (25/37, 67.6%, CI 51.5–80.4). Narratives that report Black control of worship report personal faith or prayer before freedom far more often than those that do not: 47.8% against 18.4%, an odds ratio of 4.1 (CI 2.2–7.6; state-stratified Mantel–Haenszel OR 3.4; Fisher p < 0.0001). The gap is smaller when the measure is restricted to the informant's own or a relative's faith (22.8% against 14.0%, OR 1.8, CI 0.9–3.7). Much of the association therefore comes from the same passages that describe secret or Black-led meetings. Faith before freedom was coded conservatively from keyword extracts and its counts are best read as lower bounds: an independent blind coder reading the full texts found it in 14 of 40 narratives where the first coder found 11. Only 28 of the 400 narratives date the informant's own conversion, and 25 of these fall after 1865. That pattern fits Fountain's emancipation-timing argument, but the informants' youth in 1865 (median age 83 in 1937) largely predetermines it, so the timing data cannot adjudicate between the two accounts. The independent second coding of 40 narratives reproduced the worship-control and obedience-preaching codes exactly (κ = 1.00) and gave κ = 0.83 for faith before freedom; the second coder was a separate session of the same model, not a human rater.

## 1. Source and edition

Federal Writers' Project. 1941. *Slave Narratives: A Folk History of Slavery in the United States from Interviews with Former Slaves*. 17 vols. Typewritten records, 1936–1938. Washington, DC: Library of Congress. Read in the Project Gutenberg plain-text (UTF-8) transcriptions, Project Gutenberg Literary Archive Foundation, 2004–2011, accessed November 11, 2026, https://www.gutenberg.org/ebooks/ followed by the eBook number. The eBooks and volumes are:
- Vol. I, Alabama: #36020.
- Vol. II, Arkansas, pts. 1–7: #11255, #13700, #19446, #25154, #11544, #11709, #11422.
- Vol. III, Florida: #12297.
- Vol. IV, Georgia, pts. 1–4: #13602, #22166, #18484, #18485.
- Vol. V, Indiana: #13579.
- Vol. VI, Kansas: #11485.
- Vol. VII, Kentucky: #11920.
- Vol. VIII, Maryland: #11552.
- Vol. IX, Mississippi: #12055.
- Vol. X, Missouri: #35379.
- Vol. XI, North Carolina, pts. 1–2: #22976, #31219.
- Vol. XII, Ohio: #13217.
- Vol. XIII, Oklahoma: #20785.
- Vol. XIV, South Carolina, pts. 1–4: #18912, #21508, #36022, #28170.
- Vol. XV, Tennessee: #19932.
- Vol. XVI, Texas, pts. 1–4: #30576, #30967, #35380, #35381.
- Vol. XVII, Virginia: #28973.
- Administrative Files: #13847, used for the questionnaire and Botkin's introduction.

All 34 eBooks returned by the Gutenberg search "slave narratives folk history" were downloaded, with a pause of at least 1.2 s between requests. The list is in `pipeline/gutenberg_ids.txt`.

Locators in `data.csv` cite the line number in the downloaded `pg<eBook>.txt` file. The Gutenberg transcriptions do not keep the typescript page numbers, except where the volume index prints them (the South Carolina, North Carolina and Texas volumes); those numbers are kept in `corpus_screen.csv` via the INFORMANTS list.

## 2. Method

**Segmentation (step 1).** Each volume's INFORMANTS list was parsed: 2,178 informant entries, including the Kentucky "combined interviews" but excluding the excerpt compilations in Florida and Georgia pt. 4. Each entry was then located in the body by searching forward for a heading containing the informant's name, with a fallback that uses the surname and a block break (`pipeline/segment.py`). 2,143 narratives were segmented (98.4%). The 35 entries that could not be located separately remain inside a neighbouring segment. When such a merged segment was sampled, only the TOC-named informant was coded and `notes` records the merge (9 cases). Botkin's own introduction speaks of "some two thousand narratives" (Administrative Files, #13847).

*Segment start (changed 2026-11-11).* A segment now starts at its header block: the short lines between the run of blank lines that ends the previous narrative and the informant's name, which is where most volumes put the worker's credit. The first version started at the name and backed up only over lines of a few known shapes, so the credit often fell into the tail of the previous segment. Re-running `pipeline/segment.py` and `pipeline/screen_sample.py` on freshly downloaded texts gives the same 2,143 segments, the same keyword counts for every segment, the same frame of 1,418 and the same sample of 400 in the same coding order. Only line ranges moved: 937 segment starts, 191 of them in the sample. `corpus_screen.csv` (`start_line`, `end_line`, `n_chars`) and `segment_lines` in `data.csv` carry the new ranges; snippet locators are absolute line numbers and did not change. Three sampled segments still start below their credit because the name search found a later line (Moses Mitchell, AR; Wadley Clemons, AL; Willis Williams, SC); their interviewers were read by eye.

**Keyword screen (step 2).** A narrative counted as mentioning religion if it contained at least one core term. The core terms were church (including dialect *chu'ch*), preach, pray/prayer, baptiz/baptis, convert, religion/'ligion, Jesus, camp meeting, brush or bush or hush arbor/harbor, a turned pot or kettle, sermon, Bible, deacon, revival, mourner, prayer meeting and Sunday school. Street names such as "Church St." were excluded. "Lord" and "God" were excluded because they are frequent exclamations. **1,418 of 2,143 narratives mention religion (66.2%, CI 64.1–68.1).** With "Lord/God" included the figure is 1,581. `corpus_screen.csv` gives the result for every narrative.

**Sample (step 3).** 400 narratives were drawn from the 1,418, proportionally by state using largest-remainder allocation, with `random.Random(20261111)` and no replacement within state. The allocation was AL 26, AR 94, FL 12, GA 40, IN 10, KS 0, KY 5, MD 5, MO 15, MS 7, NC 33, OH 7, OK 18, SC 58, TN 6, TX 61, VA 3. Coding order was shuffled (seed 20261112) so that coder drift is not confounded with state. The double-coding subsample of 40 used seed 20261113. All of this is in `pipeline/screen_sample.py`.

**Coding.** The codebook (`codebook.md`) was written before any sampled narrative was read. For each narrative the coder read compact extracts: every paragraph containing a religion term (with trimming of long paragraphs to the matching sentences ±1), plus the header and footer (`pipeline/packets.py`). Every non-`ns` code carries a verbatim snippet. `pipeline/merge.py` verifies each snippet against the Gutenberg text (all 400 rows pass), derives `worship_control` and `black_control_pre1865` from the component flags, and assigns `interviewer_race` by documented rules.

**Interviewer race.** Race was coded only where it is documented:
- **In-text markers:** "Negro Writers' Unit" in Florida footers; "colored" or "(Colored)" after the interviewer's name (Pernella Anderson, Adella S. Dixon, Levi D. Shelby Jr.); and "[HW: (White)]" (Sadie B. Hornsby and Grace McCune, Georgia).
- **Published lists:**
  - Encyclopedia of Arkansas, "WPA Slave Narratives" (https://encyclopediaofarkansas.net/entries/WPA-Slave-Narratives-4041), names Samuel S. Taylor and Pernella M. Anderson as Black interviewers.
  - Notable Folklorists of Color, "The Negro Units and Projects of the Federal Writers' Project…" (https://notablefolkloristsofcolor.org/centers-and-landscapes/the-negro-units-of-the-federal-writers-project-and-state-writers-projects-1935-1943/), lists Negro-unit members for Florida, Georgia (including Minnie B. Ross), South Carolina and Virginia (including Susie Byrd, Claude W. Anderson and David Hoggard).
- **Surname-only credits:** "Driskell" or "E. Driskell" in a Georgia District 5 (Atlanta) header is read as Edwin Driskell, a listed member of the Georgia Negro unit (`codebook.md` §8).
- **Entries with two interviewers:** Black if either is documented Black, otherwise white if either is documented white (`codebook.md` §8, rule added 2026-11-11).

Results: Black 56, white 12, unknown 332. "Unknown" is mostly white interviewers, but they are undocumented. The first version had Black 47, white 11, unknown 342. Two corrections on 2026-11-11 produced the present counts; `interviewer_race_corrections.md` gives the rows and evidence lines, and `interviewer_name_corrections.csv` lists every changed row.

- **Six rows, unknown to Black (Black 53).** A documented Black interviewer's credit was not in the first-pass extract, in five cases because it sits just above the segment start.
- **Six more rows, after every header and footer was re-read (Black 56, white 12).**
  - Henry Brown (SC) is Black and Alice Green (GA) is white under the new rule for two interviewers: Jessie A. Butler and Augustus Ladson; Corry Fowler and Sadie B. Hornsby.
  - Mose Davis, George Eason and Jennie Kendricks (GA) are Black. Their headers carry "E. Driskell" or "Driskell". The first version read the handwritten "Driskell" lines as reviewer notes at the foot of the preceding narrative, because one of them follows a narrative headed "Written by Grace McCune [HW: (white)]". That reading was wrong: all 13 Driskell lines in the four Georgia eBooks follow the run of blank lines that ends one narrative and stand directly above the title of the next.
  - Tom Morgan (AR) is unknown, not Black. The "Pernella Anderson" line in his segment heads the appended interview of Charity Morris; his own interviewer is Irene Robertson.
- **Hannah Austin (GA) is no longer a weaker attribution.** Her own header names Minnie B. Ross (pg13602.txt l. 611). The handwritten "Ross" first used as evidence heads the next narrative.
- **Interviewer names.** The `interviewer` column was wrong or empty in 115 rows: 69 read "not recorded" although the text names the worker, and 46 carried a different name, usually the credit of the next narrative or an editor. 107 rows remain "not recorded" because the text names no one (Texas 61, Oklahoma 18, Missouri 10, Tennessee 6, Georgia 6, Kentucky 3, Mississippi 2, Arkansas 1).

## 3. Results (n = 400 unless stated; Wilson 95% CIs)

### 3.1 Who controlled worship before 1865

| worship_control | n | % of 400 | % of 206 stating control (CI) |
|---|---|---|---|
| white-supervised only | 110 | 27.5 | 53.4 (46.6–60.1) |
| Black-led, permitted, only | 26 | 6.5 | 12.6 (8.8–17.9) |
| secret only (incl. secret + forbidden) | 17 | 4.2 | 8.3 (5.2–12.8) |
| forbidden only | 3 | 0.8 | 1.5 (0.5–4.2) |
| mixed (two or more modes) | 50 | 12.5 | 24.3 (18.9–30.6) |
| not stated | 194 | 48.5 | – |

Any mention of a mode, in all 400 narratives: white-supervised 158 (39.5%), Black-led permitted 66 (16.5%), secret 28 (7.0%), forbidden 13 (3.2%). Black control of some worship (Black-led or secret) appears in **92/206 = 44.7% (38.0–51.5)** of narratives stating control.

Typical white-supervised description: "the overseer stood there to see the preacher talked as he wanted him to talk" (Charlie Van Dyke, vol. I, pg36020.txt l. 12896).

Typical secret description: "Sometimes at night us gather 'round the fireplace and pray and sing and cry, but us daren't 'low our white folks know it" (Susan Merritt, vol. XVI-3, pg35380.txt l. 2340).

### 3.2 Preaching heard and attitude to white preachers

- **Preaching content is described in 37 narratives.** 25 of them report **obedience-only preaching (67.6%, CI 51.5–80.4)**, 6.2% of all 400. Example: "All he could preach 'bout was obey de massa, obey de overseer, obey dis, obey dat" (William Mathews, vol. XVI-3, pg35380.txt l. 2094).
- **Attitude to white preachers, the white church or the master's religion is stated in 174 narratives.** On the first coder's reading:
  - neutral or descriptive: at most 113 (64.9%, CI 57.6–71.6);
  - positive: at least 39 (22.4%, CI 16.9–29.2), usually about an individual master's or mistress's piety or kindness;
  - negative: 22 (12.6%, CI 8.5–18.4).
- **Read the neutral share as an upper bound and the positive share as a lower bound.** The first coder coded mild affect ("it sho' did sound sweet", "I used to love to hear dem sing") as neutral. Of the 13 subsample narratives it coded neutral, the independent second coder coded 4 positive and 1 negative; where both coders state an attitude they agree in 16 of 21 (κ = 0.63). The negative count is the stable one: all 4 subsample negatives were confirmed. The CIs above are sampling intervals only and do not include this coding uncertainty.
- **Negative attitudes cluster with obedience preaching:** 14 of the 23 narratives that report obedience preaching and state an attitude are negative, against 0 of 9 that describe non-obedience content (§6 of analysis output). Example: "'That is all the sermon we heard,' remarked Mr. Hammond" (Milton Hammond, vol. IV-2, pg22166.txt l. 2559).

### 3.3 Faith before freedom, prayer for freedom, conversion, postwar churches

- **Faith commitment before 1865: y = at least 72 (18.0%, CI 14.5–22.1), n = 3, ns = 325.** This is a conservative lower bound. The first coder read keyword extracts, and the independent second coder, reading the full texts, found faith in 14 of the 40 subsample narratives against 11 (κ = 0.83); none of the first coder's y codes was disputed. By subject, among the 75 stated: self 28, kin 15, others 32. One explicit n: "I didn' go much, 'cause I didn' have 'ligion, den" (Susan Snow, vol. IX, pg12055.txt l. 3828).
- **Prayer for freedom: 13 (3.2%, CI 1.9–5.5); 1 explicit denial.** The reliability of this code is untested: neither coder coded any of the 40 double-coded narratives y or n, so κ is undefined. Nine of the 13 come from secret or mixed-worship narratives. Example: "she was praying to herself: 'Oh, Lord, please send the Yankees on and let them set us free'" (Minnie Davis, vol. IV-1, pg13602.txt l. 7102).
- **Conversion timing:** dated in **only 28 of 400 (7.0%)**. Of these, after 1865: **25 (89.3%, CI 72.8–96.3)**; before 1865: 3. One pre-1865 case is W.E. Northcross's 1897 autobiography: "I confessed a hope in Christ at the age of thirteen years" (born 1840; vol. I, pg36020.txt l. 9772).
- **Postwar church:**
  - some postwar membership, attendance or office is mentioned in at least 106 narratives (26.5%, CI 22.4–31.0). The first coder did not count undated statements of having joined a church or incidental attendance; the independent second coder counted them and found 19 against 12 in the 40-narrative subsample (κ = 0.64), so the count would be higher under that broader rule;
  - the church is identifiable as Black-run in 41 (10.2% of 400; 41 of the 46 where control could be judged, 89.1%), via AME, AME Zion, CME, "colored" church, the informant as pastor or deacon, or a withdrawal;
  - 5 are explicitly not in a church or are in a white-run one.
  - Example: "Thomas was at one time a member of Shiloh, but is now a member of the Mt. Sinai colored church" (vol. XIV-3, pg36022.txt l. 848).

### 3.4 Key test: Black control of worship × faith commitment before freedom

**A. All 206 narratives stating worship control.**

| Black control before 1865 | faith y | faith not y | % faith y (CI) |
|---|---|---|---|
| yes | 44 | 48 | 47.8 (37.9–57.9) |
| no (white-supervised and/or forbidden only) | 21 | 93 | 18.4 (12.4–26.5) |

Odds ratio 4.06 (2.17–7.59); χ² = 20.4, df 1, p = 6×10⁻⁶; Fisher exact p = 1×10⁻⁵.

**B. Five categories.** Faith y in: secret 11/17 (64.7%); mixed 25/50 (50.0%); Black-led permitted 8/26 (30.8%); white-supervised 21/110 (19.1%); forbidden 0/3. χ² = 25.8, df 4, p = 3×10⁻⁵ (2 cells have expected count < 5).

**C. Robustness checks.**

| check | faith y if Black control | faith y if not | OR / p |
|---|---|---|---|
| informant's own or kin's faith only | 21/92 = 22.8% | 16/114 = 14.0% | OR 1.81 (0.88–3.72); p = 0.14 |
| faith evidence not part of the worship snippet | 28/92 = 30.4% | 20/114 = 17.5% | OR 2.06 (1.07–3.96); p = 0.03 |
| excluding hearsay-only narratives (n = 188) | 46.3% | 19.8% | p = 0.0001 |
| white or unknown interviewers only (n = 179) | 36/78 = 46.2% (CI 35.5–57.1) | 19/101 = 18.8% (CI 12.4–27.5) | Fisher p = 0.0001447 |
| informants aged 80+ (n = 110) | 44.7% | 14.3% | p = 0.0005 |
| stratified by state | – | – | Mantel–Haenszel OR 3.36 |

**How to read this.** The co-occurrence is robust to interviewer race, informant age, hearsay and state. It is sensitive to how faith is measured. When an informant describes secret or Black-led worship, the same sentences usually describe people praying and shouting. When the outcome is restricted to the informant's own or a relative's faith, the difference shrinks and loses statistical significance. A narrative that remembers its own community's worship tends also to remember its piety. These data show association within testimony, not that control of worship produced faith. Faith is undercounted by the extract method (§3.3). In the reliability subsample the three narratives where the second coder added faith fall one each under Black control, white supervision and no stated mode, so there is no sign that the undercount differs between the two groups, but 40 narratives cannot rule that out.

### 3.5 Interviewer race (documented Black n = 56 vs white or unknown n = 344)

Counts, Wilson 95% CIs and Fisher p-values are as `analysis.py` section 5 prints them after both corrections of the interviewer columns (`interviewer_race_corrections.md`). The earlier figures are in that file and in the change log.

| reported | Black interviewer | white/unknown | Fisher p |
|---|---|---|---|
| obedience-only preaching | 7/56 = 12.5% (6.2–23.6) | 18/344 = 5.2% (3.3–8.1) | 0.0655 |
| negative attitude, all narratives | 7/56 = 12.5% (6.2–23.6) | 15/344 = 4.4% (2.7–7.1) | 0.0227 |
| negative attitude, among those stating an attitude | 7/22 = 31.8% (16.4–52.7) | 15/152 = 9.9% (6.1–15.6) | 0.0097 |
| positive attitude, among those stating an attitude | 3/22 = 13.6% (4.7–33.3) | 36/152 = 23.7% (17.6–31.0) | 0.414 |
| Black control of worship | 14/56 = 25.0% (15.5–37.7) | 78/344 = 22.7% (18.6–27.4) | 0.733 |
| faith before freedom | 12/56 = 21.4% (12.7–33.8) | 60/344 = 17.4% (13.8–21.8) | 0.457 |
| prayer for freedom | 4/56 = 7.1% (2.8–17.0) | 9/344 = 2.6% (1.4–4.9) | 0.0933 |
| postwar Black-run church | 10/56 = 17.9% (10.0–29.8) | 31/344 = 9.0% (6.4–12.5) | 0.0556 |

The direction matches the critique made by Blassingame (1975) and Escott (1979): informants were more critical of white religion when speaking to Black interviewers. Four cautions apply.

- **The p-values are fragile.** Only the two negative-attitude comparisons are below 0.05 in every version of the data: 0.0328 and 0.0185 at first, 0.0168 and 0.00721 after the six-row correction, 0.0227 and 0.0097 now. Obedience-only preaching and postwar Black-run church went from 0.0986 and 0.122 to 0.0343 and 0.0471 with the six rows and are back above 0.05 (0.0655 and 0.0556). The script prints ten comparisons and none is adjusted for multiplicity.
- **State confounding.** Black interviewers are concentrated in Arkansas (29 of 56) and Florida (12), so the comparison is confounded with state.
- **Small comparison groups.** The documented-white group is only 12 narratives, all from Georgia, and the attitude and prayer-for-freedom codes carry the reliability limits given in §3.2 and §3.3.
- **Four Arkansas rows are unresolved.** In Bert Higgins, William Henry Rooks, Katie Dillon and Tom Morgan the coded snippets come from another informant's interview appended to the segment, taken down by Samuel S. Taylor or Pernella Anderson. The rows are coded unknown, by the TOC-named informant's own interviewer. Their codes were not changed; `interviewer_race_corrections.md` gives the lines and what the table would show if the four were counted as Black.

### 3.6 Intra-coder stability (step 5)

Forty narratives (seed 20261113) were recoded by the same coder after all 400 first codes were complete. The coder worked from freshly generated, shuffled extracts and did not see the first codes. This measures intra-coder stability, not inter-rater reliability; the independent second coding is reported in "Independent second-coder reliability" at the end of this file.

| variable | agreement | Cohen's κ |
|---|---|---|
| worship_control, black_control_pre1865, all four component flags | 100% | 1.00 |
| obedience_preaching, conversion_timing, postwar_black_church | 100% | 1.00 |
| attitude_white_preachers | 95% | 0.92 |
| faith_commitment_before_freedom | 95% | 0.88 |
| faith_subject | 95% | 0.90 |
| postwar_church_any | 97.5% | 0.94 |
| prayed_for_freedom | 100% | undefined (all 40 ns in both passes) |

The disagreements concern mild positive tone (Mahala Jewel, Frank Menefee), whether "when we had a black preacher that was Heaven" counts as devotion (Anthony Dawson), and an incidental church attendance (Julia Grace). They are listed in the analysis output.

**Caveat: these are not independent inter-rater statistics.** The same coder (the model) produced both passes within one working session, with only a short pause after the first pass, and may have remembered first-pass judgements. The κ values are therefore an upper bound on reliability and should be cited only as intra-coder stability. A separate model session given only `codebook.md` has since recoded the same 40 IDs blind; cite those figures (last section of this file, and `reliability_independent.md`) for inter-rater reliability.

## 4. Limits (what the data can and cannot show)

1. **Frame.**
   - The Gutenberg edition reproduces the 1941 Library of Congress deposit only: about 2,100–2,300 narratives. Rawick's supplements (e.g. most of Mississippi; Louisiana is absent) and the Virginia Hampton interviews published in *Weevils in the Wheat* are not included. Virginia has 14 narratives and Kansas 3 (Kansas drew 0 in the sample).
   - Arkansas is 32% of the corpus and 23.5% of the sample.
   - Proportions are conditional on a narrative mentioning religion. 48.5% of sampled narratives say nothing about pre-1865 worship; their religion talk is postwar or present-day.
2. **Informants' age.** Median age at interview was 83 (IQR 78–88; age recorded for 301), so the typical informant was about 11 in 1865. 29.6% were 79 or younger (under about 7 in 1865), and 8.3% were 72 or younger (born after slavery, or infants). Their accounts of slavery-era worship are partly childhood memory and partly family report; 21 narratives are hearsay-only. The same age structure makes post-1865 conversions almost inevitable, so the 25-of-28 figure cannot by itself support Fountain's (2010) claim that most enslaved people converted only after emancipation.
3. **Interview context.** The interviews took place in the 1930s Jim Crow South, mostly by white interviewers, with informants who often depended on white relief. Positive memories of masters and their religion should be read accordingly.
   - Interviewer race is documented for only 68 of 400 narratives (56 Black, 12 white).
   - State editors revised the texts: dialect was imposed under Lomax's guidance, and handwritten edits appear in the Georgia volumes. Some narratives are interviewer paraphrase, e.g. Florida, Charles Grandy (VA) and Squires Jackson (FL); these are coded only where the paraphrase reports what the informant said.
4. **Questionnaire prompts.** The national questionnaire asked "Did the slaves have a church on your plantation? … Who was your favorite preacher?" (item 10). It also asked "Tell why you joined a church and why you think all people should be religious" (item 19; Administrative Files, #13847). Item 19 inflates present-day and postwar church statements. Item 10 steers toward plantation churches, which are often white-run, rather than toward clandestine worship.
5. **Measurement.**
   - Faith before freedom is recorded only when stated, so 81% of narratives are `ns`. Silence is not evidence of unbelief, and the stated count is a conservative lower bound (§3.3).
   - Black control of worship and reported faith often come from the same passage (§3.4).
   - Conversion is datable in only 7% of narratives.
   - "Black-run" postwar churches are counted only when identifiable. Most of the postwar memberships (at least 106) were almost certainly in Black congregations but are not counted as such.
   - The split of attitudes between neutral and positive depends on the coder's threshold for mild affect (§3.2). Neutral is an upper bound and positive a lower bound.
   - The reliability of the prayer-for-freedom code is untested (§3.3).
6. **Segmentation and extracts.**
   - About 1.6% of TOC entries could not be segmented separately.
   - The coder read keyword-selected extracts, not complete narratives. A religion statement without any listed keyword (e.g. "the Lord") could be missed. Extracts were capped at about 3,200 characters, and 19 longer narratives were truncated. The independent second coding found both effects: 5 of its 20 disagreements come from text outside the extract.
   - Interviewer credit lines that sit just above a segment start were not in the extract. The interviewer columns were therefore re-read against the text for all 400 rows. After the six rows corrected first, a further 115 names and 6 race codes changed (`interviewer_race_corrections.md`, `interviewer_name_corrections.csv`).
   - In four sampled Arkansas segments the coded snippets belong to another informant whose interview is appended to the segment (§3.5, fourth caution). The codebook says only the TOC-named informant is coded; these rows have not been recoded.
7. **Single first coder.** The same-session recode (§3.6) is intra-coder stability only. The independent second coding covers 40 narratives, was done by a separate session of the same model and not by a human rater, and could not assess `prayed_for_freedom` (last section).

## 5. Bearing on the article's claims

- **"Who holds the remedy" claim:** consistent with the data, as association only. In the slaves' own memory, white-held religion is overwhelmingly supervised and often obedience-only, and evaluations of it are mixed. Where the community held some control of worship, the testimony has about four times the odds of showing devotion (47.8% against 18.4%), and 10 of the 13 reports of praying for freedom occur there. The devotion counts are conservative lower bounds, the attitude split between neutral and positive depends on the coder, and the reliability of the prayer-for-freedom code is untested. The association weakens to a non-significant OR of 1.8 when only the informant's or a relative's own faith counts.
- **"Deliverance/emancipation" rival (Fountain 2010):** consistent, but not a fair test. Dated conversions are overwhelmingly post-1865 and 89% of identifiable postwar churches were Black-run. Both patterns follow from informants' youth in 1865 and from the timing of institutional Black church-building after 1865, not necessarily from emancipation as such.
- **Neither account is refuted by these data.** The evidence fits a two-track pattern: devotion in self-controlled spaces before 1865, and institutional affiliation in Black-run churches after it.

**Changes from the pilot of 51 narratives.**
- That pilot included 9 targeted additions. In it, Black-led worship appeared in 26 of 51 narratives, and conversion was dated in 7 of 51, 5 of them after 1865.
- In this random sample, Black control is reported in 92 of 206 narratives stating control (23% of all 400), and dated conversions remain rare (28 of 400). The pilot's figures are not directly comparable, because of its targeted additions and different denominators.

## 6. Files

- `codebook.md`: categories, decision rules and examples (written before coding).
- `data.csv`: 400 rows, one per sampled narrative (interviewer columns corrected on 2026-11-11: six rows, then a full re-reading). It holds the informant, state, volume, Gutenberg eBook number, segment line range, interviewer and documented race with source, age, hearsay flag, all codes, notes, and a verbatim snippet with a `pg<eBook>.txt line N; vol., "informant"` locator for every substantive code.
- `double_code.csv`: the first coder's own same-session recodes of the 40 reliability narratives (intra-coder stability).
- `second_coder.csv`: the independent blind second coding of the same 40 narratives, with snippets, locators and notes.
- `reliability_independent.md`: the independent reliability table, every disagreement with both codes and snippets, and their classification.
- `interviewer_race_corrections.md`: the rows whose interviewer race was corrected, with the evidence line for each, the analysis output before and after, and the open items.
- `interviewer_name_corrections.csv`: the 116 rows whose `interviewer`, `interviewer_race` or `interviewer_race_source` changed in the full re-reading, with old and new values, old and new segment range, and the line number and verbatim text of each credit.
- `corpus_screen.csv`: all 2,143 segmented narratives, with locator, keyword hits, religion flag and sampled flag (line ranges re-generated 2026-11-11 with the header-block segment start).
- `analysis.py`: re-runnable; prints every table above.
- `pipeline/`: the segmentation, screening and sampling, extract-generation and merge/verification scripts, plus the list of Gutenberg eBook numbers. The raw downloads are not redistributed; they are re-downloadable from the URLs above.

## References

Blassingame, John W. 1975. "Using the Testimony of Ex-Slaves: Approaches and Problems." *Journal of Southern History* 41 (4): 473–92.

Escott, Paul D. 1979. *Slavery Remembered: A Record of Twentieth-Century Slave Narratives*. Chapel Hill: University of North Carolina Press.

Federal Writers' Project. 1941. *Slave Narratives: A Folk History of Slavery in the United States from Interviews with Former Slaves*. 17 vols. Washington, DC: Library of Congress. Project Gutenberg eBooks as listed in §1.

Fountain, Daniel L. 2010. *Slavery, Civil War, and Salvation: African American Slaves and Christianity, 1830–1870*. Baton Rouge: Louisiana State University Press.

## Independent second-coder reliability

Added 2026-11-11. A separate model session recoded the 40 narratives in `double_code.csv` blind: it was given only `codebook.md` and the identifiers and source locators, re-downloaded the Gutenberg texts, read each narrative in full (not the keyword extracts), and saved `second_coder.csv` before opening any first-coder code, `results.md` or `analysis.py`. The table compares the first codes in `data.csv` with that second coding; `analysis.py` section 10 re-prints it, and `reliability_independent.md` lists every disagreement with both codes, snippets and a classification.

| variable | agreement (n = 40) | Cohen's κ | non-`ns` cases, first / second coder |
|---|---|---|---|
| wc_white, wc_blackled, wc_secret, wc_forbidden | 40/40 = 100% each | 1.00 each | 20/20, 3/3, 6/6, 1/1 |
| worship_control; black_control_pre1865 (derived) | 40/40 = 100% | 1.00 | 24 / 24 |
| obedience_preaching | 40/40 = 100% | 1.00 | 5 / 5 |
| attitude_white_preachers | 35/40 = 87.5% | 0.82 (0.63 among the 21 where both state an attitude) | 21 / 21 |
| conversion_timing | 39/40 = 97.5% | 0.79 | 2 / 3 |
| faith_commitment_before_freedom | 37/40 = 92.5% | 0.83 | 11 / 14 |
| faith_subject | 37/40 = 92.5% | 0.85 | 11 / 14 |
| postwar_church_any | 33/40 = 82.5% | 0.64 | 12 / 19 |
| postwar_black_church | 39/40 = 97.5% | 0.79 | 2 / 3 |
| prayed_for_freedom | 40/40 = 100% | NA (all 40 `ns` for both coders) | 0 / 0 |
| interviewer_race (context) | 38/40 = 95% at the blind comparison; 40/40 = 100% after the J.M. Parker and Alice Green rows were corrected, which is what `analysis.py` now prints | 0.85; 1.00 after the corrections | 7 / 9; 9 / 9 after the corrections |
| hearsay_only (context) | 37/40 = 92.5% | 0.63 | 3 / 6 |

The worship-control flags and obedience preaching were reproduced exactly, but agreement is lower for attitude to white preachers (the neutral–positive boundary), faith before freedom and above all postwar church attendance, and in all 20 disagreements on hypothesis variables the first coder has `ns` or `neutral` where the second coder has a substantive code (5 from text outside the keyword extract, 8 from codebook ambiguity, 7 from judgement), so the first-pass counts for those three variables are conservative lower bounds. These figures come from 40 narratives coded by a second session of the same model and not by a human rater, they leave `prayed_for_freedom` untested, and they supersede the same-session recode in §3.6, which is intra-coder stability only.

## Change log

All entries are dated 2026-11-11. Numbers not listed here are unchanged from the first version, including the worship-control table (§3.1), obedience preaching (25/37), the key test (§3.4 A and B, OR 4.06) and conversion timing (25 of 28).

1. **Reliability wording.** §3.6 retitled from "Reliability" to "Intra-coder stability" and its caveat reworded, so that the same-session recode is no longer presented as inter-rater reliability. Limit 7 in §4 and the `double_code.csv` entry in §6 reworded to match.
2. **Independent second coding added.** New section "Independent second-coder reliability", new files `second_coder.csv` and `reliability_independent.md`, and a new section 10 in `analysis.py`.
3. **Interviewer attributions corrected in `data.csv` (six rows).** AR-II-5-076 (J.M. Parker), AR-II-7-019 (Mary Watson), AR-II-1-091 (William Brown), AR-II-1-024 (Cora Armstrong), FL-III-050 (Claude Augusta Wilson) and GA-IV-2-012 (Milton Hammond) changed from unknown to Black, with the interviewer's name and source filled in. Evidence lines are in the new file `interviewer_race_corrections.md`. An earlier note in `reliability_independent.md` gave five rows and credited Cora Armstrong to Samuel S. Taylor; both points were wrong and are corrected there.
4. **Numbers that changed because of entry 3,** as `analysis.py` prints them:
   - §2: Black 47, white 11, unknown 342 → Black 53, white 11, unknown 336.
   - §3.4 C, white or unknown interviewers only: n = 185, 45.8% against 17.6%, p = 4.825e-05 → n = 182, 37/81 = 45.7% (35.3–56.5) against 18/101 = 17.8% (11.6–26.4), Fisher p = 7.966e-05.
   - §3.5, whole table. Obedience-only preaching 6/47 against 19/353, p = 0.0986 → 7/53 against 18/347, p = 0.0343. Negative attitude, all narratives, 6/47 against 16/353, p = 0.0328 → 7/53 against 15/347, p = 0.0168. Negative attitude among those stating one, 6/19 against 16/155, p = 0.0185 → 7/21 against 15/153, p = 0.00721. Positive attitude among those stating one, 3/19 against 36/155, p = 0.572 → 3/21 against 36/153, p = 0.416. Black control of worship 9/47 against 83/353, p = 0.583 → 11/53 against 81/347, p = 0.861. Faith before freedom 11/47 against 61/353, p = 0.314 → 12/53 against 60/347, p = 0.341. Postwar Black-run church 8/47 against 33/353, p = 0.122 → 10/53 against 31/347, p = 0.0471. A prayer-for-freedom row was added (4/53 against 9/347, p = 0.0789), CIs were added to every cell, and the commentary now warns that the p-values are fragile and unadjusted.
   - §3.5 text: Arkansas 26 of 47 and Florida 11 → Arkansas 30 of 53 and Florida 12.
   - §4, limit 3: interviewer race documented for 58 of 400 → 64 of 400.
   - Independent reliability table, `interviewer_race` row: 38/40, κ 0.85 at the blind comparison; `analysis.py` now prints 39/40, κ 0.93.
5. **Rewordings that follow from the independent second coding** (no count changed):
   - §3.2: the neutral attitude share is given as an upper bound ("at most 113") and the positive share as a lower bound ("at least 39"), with the subsample evidence. CI added for the neutral share.
   - §3.3: faith before freedom is given as a conservative lower bound ("at least 72"); postwar church as "at least 106"; prayer for freedom is marked as untested for reliability. CIs added for these three counts.
   - §3.4, "How to read this": a sentence on the faith undercount and whether it differs by worship control.
   - §4, limits 5 and 6: the same three cautions, the share of disagreements due to the extract method, and the interviewer credit lines.
   - Headline: two sentences added, one on faith as a lower bound and one on the independent reliability result.
6. **Two wording errors corrected in §5.** "Roughly four times as likely to show devotion" described an odds ratio as a ratio of proportions; it now reads "about four times the odds (47.8% against 18.4%)". "Almost all reports of praying for freedom" now reads "10 of the 13".
7. **Open items at the time of entries 3 and 4.** Two entries with two interviews by different interviewers (Alice Green, GA; Henry Brown, SC) were coded unknown pending a codebook rule. Cora Armstrong's `age_1937` (86) was the preceding informant's age. The `interviewer` name column was incomplete for about 30 rows. All three are closed by entries 8 to 11.
8. **Codebook rule for an entry with two interviewers** (`codebook.md` §8): Black if any interviewer is documented Black, otherwise white if any is documented white, otherwise unknown; `interviewer` lists all of them. Applied in `data.csv`: SC-XIV-1-028 (Henry Brown; Jessie A. Butler; Augustus Ladson) unknown → Black, and its `interviewer` no longer reads "W. W. Dixon", which heads the next narrative; GA-IV-2-005 (Alice Green; Corry Fowler; Sadie B. Hornsby) unknown → white. Three further clarifications were added to §8: where the credit stands, segments that hold another informant's interview, and surname-only "Driskell" credits.
9. **`age_1937` of AR-II-1-024 (Cora Armstrong) 86 → 82** ("I was ten years old at surrender", pg11255.txt l. 2240). No other code in the row comes from Campbell Armstrong's narrative: both snippets are at l. 2247, in her own text, and his text (l. 2003–2226) has no religion term. `notes` records the merge. No printed figure changes: the row stays in the 80+ group, and the median (83) and IQR (78–88) are the same.
10. **`interviewer` name column re-read against the text for all 400 rows.** 115 names changed: 69 rows read "not recorded" although the text names the worker, and 46 carried a different name (the next narrative's credit, an editor, or one of two interviewers). 107 rows remain "not recorded". Four race codes changed because the name now recorded is documented, or the old code rested on another informant's credit:
    - GA-IV-1-035 (Mose Davis), GA-IV-1-038 (George Eason) and GA-IV-3-001 (Jennie Kendricks) unknown → Black: header credits "E. Driskell" and "Driskell", read as Edwin Driskell. §2 no longer says that these lines are reviewer notes.
    - AR-II-5-044 (Tom Morgan) Black → unknown: the Pernella Anderson line in his segment heads Charity Morris's interview.
    - Every changed row is in `interviewer_name_corrections.csv` with the line number and text of the credit.
11. **Numbers that changed because of entries 8 and 10,** as `analysis.py` prints them:
    - §2: Black 53, white 11, unknown 336 → Black 56, white 12, unknown 332.
    - §3.4 C, white or unknown interviewers only: n = 182, 37/81 = 45.7% (35.3–56.5) against 18/101 = 17.8% (11.6–26.4), Fisher p = 7.966e-05 → n = 179, 36/78 = 46.2% (35.5–57.1) against 19/101 = 18.8% (12.4–27.5), Fisher p = 0.0001447.
    - §3.5, whole table. Obedience-only preaching 7/53 against 18/347, p = 0.0343 → 7/56 against 18/344, p = 0.0655. Negative attitude, all narratives, 7/53 against 15/347, p = 0.0168 → 7/56 against 15/344, p = 0.0227. Negative attitude among those stating one, 7/21 against 15/153, p = 0.00721 → 7/22 against 15/152, p = 0.0097. Positive attitude among those stating one, 3/21 against 36/153, p = 0.416 → 3/22 against 36/152, p = 0.414. Black control of worship 11/53 against 81/347, p = 0.861 → 14/56 against 78/344, p = 0.733. Faith before freedom 12/53 against 60/347, p = 0.341 → 12/56 against 60/344, p = 0.457. Prayer for freedom 4/53 against 9/347, p = 0.0789 → 4/56 against 9/344, p = 0.0933. Postwar Black-run church 10/53 against 31/347, p = 0.0471 → 10/56 against 31/344, p = 0.0556.
    - §3.5 text: Arkansas 30 of 53 → 29 of 56; Florida 12 unchanged; documented-white group 11 → 12. The first caution was rewritten, because obedience-only preaching and postwar Black-run church are above p = 0.05 again, and a fourth caution was added (entry 13).
    - §4, limit 3: interviewer race documented for 64 of 400 → 68 of 400. Limit 6 reworded.
    - Independent reliability table, `interviewer_race` row: `analysis.py` now prints 40/40, κ 1.00 (39/40, κ 0.93 before), because the second coder had coded Alice Green white.
    - Two `analysis.py` section 5 lines that §3.5 does not show moved as well: positive attitude, all narratives, 3/53 against 36/347, p = 0.453 → 3/56 against 36/344, p = 0.331; secret worship 3/53 against 25/347, p = 1 → 3/56 against 25/344, p = 0.781.
12. **Segmentation script.** `pipeline/segment.py` now starts a segment at its header block (§2, "Segment start"). The segments, keyword screen, frame and sample are unchanged; `corpus_screen.csv` and `segment_lines` in `data.csv` carry the new line ranges.
13. **Open item, not changed: four Arkansas rows coded from an appended interview.** In AR-II-3-064 (Bert Higgins), AR-II-6-024 (William Henry Rooks), AR-II-2-042 (Katie Dillon) and AR-II-5-044 (Tom Morgan) some or all coded snippets come from another informant's interview appended to the segment (Annie Hill, Amanda Rosa, Alice Dixon, Charity Morris), each taken down by Samuel S. Taylor or Pernella Anderson. The codebook says only the TOC-named informant is coded. The codes were left as first coded and each row's `notes` now says so; the lines, and the §3.4 C and §3.5 figures if the four rows were counted as Black, are in `interviewer_race_corrections.md`. Recoding them would change the worship-control and faith counts in §3.1 to §3.4 by up to four rows.
