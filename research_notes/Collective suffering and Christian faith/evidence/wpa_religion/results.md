# Religion under slavery in the WPA ex-slave narratives: a coded random sample (project `wpa_religion`)

Prepared 2026-11-11 under `_EVIDENCE_BRIEF.md`. All counts come from `data.csv`, `double_code.csv` and `corpus_screen.csv` in this folder. Running `python3 analysis.py` re-prints every table. Each coded value in `data.csv` carries a verbatim snippet and a locator (Gutenberg eBook number, line number in the plain-text file, volume and informant). The merge script checked all 400 rows against the source text and found no non-verbatim snippets.

**Correction, 2026-11-11.** Interviewer credit lines that stand above the old segment start had been missed or taken from the next narrative; `interviewer` was corrected in 116 rows and `interviewer_race` in 12 (Black 47 → 56, white 11 → 12, unknown 342 → 332), which changes only the interviewer-race figures in §2, the interviewer row of §3.4, §3.5, §4 item 3 and the `interviewer_race` row of the last table; details are in §2 and `interviewer_corrections.csv`.

## Headline (for an article appendix)

We drew a state-stratified random sample of 400 of the 1,418 WPA ex-slave narratives (Library of Congress deposit, Project Gutenberg edition) that mention religion, and coded it against a pre-registered codebook. Of the 206 narratives that describe how worship was organised before 1865, 44.7% (95% CI 38.0–51.5) report some Black-controlled worship, either permitted Black-led meetings or secret meetings. 53.4% report white-supervised worship only. Where preaching content is described, two-thirds of reports are obedience-only sermons (25/37, 67.6%, CI 51.5–80.4). Narratives that report Black control of worship report personal faith or prayer before freedom far more often than those that do not: 47.8% against 18.4%, an odds ratio of 4.1 (CI 2.2–7.6; state-stratified Mantel–Haenszel OR 3.4; Fisher p < 0.0001). The gap is smaller when the measure is restricted to the informant's own or a relative's faith (22.8% against 14.0%, OR 1.8, CI 0.9–3.7). Much of the association therefore comes from the same passages that describe secret or Black-led meetings. Only 28 of the 400 narratives date the informant's own conversion, and 25 of these fall after 1865. That pattern fits Fountain's emancipation-timing argument, but the informants' youth in 1865 (median age 83 in 1937) largely predetermines it, so the timing data cannot adjudicate between the two accounts.

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

**Segment start (changed 2026-11-11).** The first version of `segment.py` started each segment at the heading that names the informant. In most states the header block above that heading carries the interviewer credit ("Interviewer: …", "Worker: …", "NAME OF WORKER--…", "Prepared by …", "X, Field Worker", or a bare name), so the credit was left at the end of the previous segment. `segment.py` now starts a segment at the first line after the run of three or more blank lines that separates narratives in the Gutenberg text, provided that block has at most 12 lines and no wrapped prose. Effect on the 2,143 segments: 925 starts move up (by 1–11 lines, one by 20), 4 move down past a stray note, and the previous segments end correspondingly earlier. The keyword screen gives the same result for every narrative (the same 1,418), so the sample of 400 and the double-coding subsample are identical, and every snippet locator still falls inside its segment. `segment_lines` in `data.csv` and the line columns of `corpus_screen.csv` now follow the new boundaries; `second_coder.csv` keeps the boundaries the second coder was given. Boundaries can still be wrong where two INFORMANTS entries share a surname (for example the two "Brown, William" entries, where the header forms a stub segment of its own). The sampled entries concerned, and those that hold two interviews or an appended narrative, are listed in `OWN_LINES` in `pipeline/merge.py` with the line ranges of the informant's own interview or interviews.

**Keyword screen (step 2).** A narrative counted as mentioning religion if it contained at least one core term. The core terms were church (including dialect *chu'ch*), preach, pray/prayer, baptiz/baptis, convert, religion/'ligion, Jesus, camp meeting, brush or bush or hush arbor/harbor, a turned pot or kettle, sermon, Bible, deacon, revival, mourner, prayer meeting and Sunday school. Street names such as "Church St." were excluded. "Lord" and "God" were excluded because they are frequent exclamations. **1,418 of 2,143 narratives mention religion (66.2%, CI 64.1–68.1).** With "Lord/God" included the figure is 1,581. `corpus_screen.csv` gives the result for every narrative.

**Sample (step 3).** 400 narratives were drawn from the 1,418, proportionally by state using largest-remainder allocation, with `random.Random(20261111)` and no replacement within state. The allocation was AL 26, AR 94, FL 12, GA 40, IN 10, KS 0, KY 5, MD 5, MO 15, MS 7, NC 33, OH 7, OK 18, SC 58, TN 6, TX 61, VA 3. Coding order was shuffled (seed 20261112) so that coder drift is not confounded with state. The double-coding subsample of 40 used seed 20261113. All of this is in `pipeline/screen_sample.py`.

**Coding.** The codebook (`codebook.md`) was written before any sampled narrative was read. For each narrative the coder read compact extracts: every paragraph containing a religion term (with trimming of long paragraphs to the matching sentences ±1), plus the header and footer (`pipeline/packets.py`). Every non-`ns` code carries a verbatim snippet. `pipeline/merge.py` verifies each snippet against the Gutenberg text (all 400 rows pass), derives `worship_control` and `black_control_pre1865` from the component flags, and assigns `interviewer_race` by documented rules.

**Interviewer race.** Race was coded only where it is documented:
- **In-text markers:** "Negro Writers' Unit" in Florida header blocks; "colored" or "(Colored)" after the interviewer's name (Pernella Anderson, Adella S. Dixon, Levi D. Shelby Jr.); and "[HW: (White)]" (Sadie B. Hornsby and Grace McCune, Georgia).
- **Published lists:**
  - Encyclopedia of Arkansas, "WPA Slave Narratives" (https://encyclopediaofarkansas.net/entries/WPA-Slave-Narratives-4041), names Samuel S. Taylor and Pernella M. Anderson as Black interviewers.
  - Notable Folklorists of Color, "The Negro Units and Projects of the Federal Writers' Project…" (https://notablefolkloristsofcolor.org/centers-and-landscapes/the-negro-units-of-the-federal-writers-project-and-state-writers-projects-1935-1943/), lists Negro-unit members for Florida, Georgia (including Minnie B. Ross and Edwin Driskell), South Carolina (including Augustus Ladson) and Virginia (including Susie Byrd, Claude W. Anderson and David Hoggard).
- **Surname-only header credits (Georgia, District 5):** Atlanta narratives are headed "Driskell", "E. Driskell" or "E.F. Driskell", typed or handwritten, sometimes with the typist "Whitley". These are read as Edwin Driskell: all 13 such lines in the four Georgia volumes stand between a narrative break and the next title, one heads the first narrative of pt. 3, and the same position reads "By E. Driskell / Typed by A.M. Whitley" above Lewis Favor and "Edwin Driskell" above Isaiah Green's second interview. Three sampled narratives are affected (Mose Davis, George Eason, Jennie Kendricks).
- **Entries with more than one interviewer** (rule added 2026-11-11, `codebook.md` §8): all interviewers are listed, and the entry is coded Black if any of them is documented Black, otherwise white if any is documented white. Four sampled entries have a documented interviewer among two: Sarah Douglas (AR; Pernella M. Anderson and Carol Graham), Isaiah Green (GA; Minnie B. Ross and Edwin Driskell), Henry Brown (SC; Jessie A. Butler and Augustus Ladson) and Alice Green (GA; Corry Fowler and Sadie B. Hornsby, coded white).
- **Appended narratives:** where a segment also holds the narrative of another informant whose own entry could not be located, that narrative's credit is not counted (for example Tom Morgan, AR: his own interviewer is Irene Robertson; the Pernella Anderson interview in his segment is Charity Morris's).

Results: Black 56, white 12, unknown 332. "Unknown" is mostly white interviewers, but they are undocumented.

**Correction of 2026-11-11.** The first version read the credit from the first and last lines of the old segments, which begin below the header block. Every sampled narrative was therefore re-read at its header and footer in freshly downloaded texts (`pipeline/interviewer_fix.py`; each change with its evidence line is in `interviewer_corrections.csv`):
- `interviewer` changed in 116 rows. 72 were "not recorded" although the header or footer names the worker; 109 remain "not recorded" from the first version (61 Texas, 18 Oklahoma, 12 Missouri and 18 others, where the text names nobody). 35 carried the credit of the next narrative, whose header had been read as this narrative's footer, or of an appended narrative; 34 of them now have their own credit and 1 (Alec Bostwick, GA) has none and is "not recorded", which makes 110. 4 named the editor where the footer names the interviewer. 5 gained a second interviewer.
- `interviewer_race` changed in 12 rows. Ten moved from unknown to Black: J.M. Parker, Mary Watson and William Brown (AR, Samuel S. Taylor); Cora Armstrong (AR, "Interviewer: Pernella Anderson, colored"; the Taylor line above her segment heads Campbell Armstrong's narrative); Claude Augusta Wilson (FL, Negro Writers' Unit, James Johnson); Milton Hammond (GA, Minnie B. Ross); Mose Davis, George Eason and Jennie Kendricks (GA, Driskell); Henry Brown (SC, second interview by Augustus Ladson). Tom Morgan (AR) moved from Black to unknown and Alice Green (GA) from unknown to white.
- The first version's statement that handwritten Georgia "Driskell" blocks are reviewer notes under the preceding narrative is withdrawn: they head the following narrative. For the same reason Hannah Austin's attribution to Minnie B. Ross no longer rests on a handwritten "Ross" (that block heads Celestia Avery); her own header has "Minnie B. Ross" typed.
- No code column was changed. Four Arkansas rows were found to draw snippets from an appended narrative of another informant (Katie Dillon, Bert Higgins, Tom Morgan, and two of three snippets for William Henry Rooks); their codes are left as they were and need a separate check.

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
- **Attitude to white preachers, the white church or the master's religion is stated in 174 narratives:**
  - neutral or descriptive: 113 (64.9%);
  - positive: 39 (22.4%, CI 16.9–29.2), usually about an individual master's or mistress's piety or kindness;
  - negative: 22 (12.6%, CI 8.5–18.4).
- **Negative attitudes cluster with obedience preaching:** 14 of the 23 narratives that report obedience preaching and state an attitude are negative, against 0 of 9 that describe non-obedience content (§6 of analysis output). Example: "'That is all the sermon we heard,' remarked Mr. Hammond" (Milton Hammond, vol. IV-2, pg22166.txt l. 2559).

### 3.3 Faith before freedom, prayer for freedom, conversion, postwar churches

- **Faith commitment before 1865: y = 72 (18.0%), n = 3, ns = 325.** By subject, among the 75 stated: self 28, kin 15, others 32. One explicit n: "I didn' go much, 'cause I didn' have 'ligion, den" (Susan Snow, vol. IX, pg12055.txt l. 3828).
- **Prayer for freedom: 13 (3.2%); 1 explicit denial.** Nine of the 13 come from secret or mixed-worship narratives. Example: "she was praying to herself: 'Oh, Lord, please send the Yankees on and let them set us free'" (Minnie Davis, vol. IV-1, pg13602.txt l. 7102).
- **Conversion timing:** dated in **only 28 of 400 (7.0%)**. Of these, after 1865: **25 (89.3%, CI 72.8–96.3)**; before 1865: 3. One pre-1865 case is W.E. Northcross's 1897 autobiography: "I confessed a hope in Christ at the age of thirteen years" (born 1840; vol. I, pg36020.txt l. 9772).
- **Postwar church:**
  - some postwar membership, attendance or office is mentioned in 106 narratives (26.5%);
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
| white or unknown interviewers only (n = 179) | 46.2% | 18.8% | p = 0.0001 |
| informants aged 80+ (n = 110) | 44.7% | 14.3% | p = 0.0005 |
| stratified by state | – | – | Mantel–Haenszel OR 3.36 |

**How to read this.** The co-occurrence is robust to interviewer race, informant age, hearsay and state. It is sensitive to how faith is measured. When an informant describes secret or Black-led worship, the same sentences usually describe people praying and shouting. When the outcome is restricted to the informant's own or a relative's faith, the difference shrinks and loses statistical significance. A narrative that remembers its own community's worship tends also to remember its piety. These data show association within testimony, not that control of worship produced faith.

### 3.5 Interviewer race (documented Black n = 56 vs white or unknown n = 344)

| reported | Black interviewer | white/unknown | Fisher p |
|---|---|---|---|
| obedience-only preaching | 7/56 (12.5%) | 18/344 (5.2%) | 0.07 |
| negative attitude, all narratives | 7/56 (12.5%) | 15/344 (4.4%) | 0.02 |
| negative attitude, among those stating an attitude | 7/22 (31.8%) | 15/152 (9.9%) | 0.01 |
| positive attitude, among those stating an attitude | 3/22 (13.6%) | 36/152 (23.7%) | 0.41 |
| Black control of worship | 14/56 (25.0%) | 78/344 (22.7%) | 0.73 |
| faith before freedom | 12/56 (21.4%) | 60/344 (17.4%) | 0.46 |
| postwar Black-run church | 10/56 (17.9%) | 31/344 (9.0%) | 0.06 |

The direction matches the critique made by Blassingame (1975) and Escott (1979): informants were more critical of white religion when speaking to Black interviewers. Black interviewers are concentrated in Arkansas (29 of 56) and Florida (12), so the comparison is confounded with state. The documented-white group is only 12 narratives. Before the correction of 2026-11-11 (§2) the groups were 47 and 353 and the two negative-attitude rows read 6/47 against 16/353 (p = 0.03) and 6/19 against 16/155 (p = 0.02); the direction and size of the difference are unchanged.

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
   - Interviewer race is documented for only 68 of 400 narratives.
   - State editors revised the texts: dialect was imposed under Lomax's guidance, and handwritten edits appear in the Georgia volumes. Some narratives are interviewer paraphrase, e.g. Florida, Charles Grandy (VA) and Squires Jackson (FL); these are coded only where the paraphrase reports what the informant said.
4. **Questionnaire prompts.** The national questionnaire asked "Did the slaves have a church on your plantation? … Who was your favorite preacher?" (item 10). It also asked "Tell why you joined a church and why you think all people should be religious" (item 19; Administrative Files, #13847). Item 19 inflates present-day and postwar church statements. Item 10 steers toward plantation churches, which are often white-run, rather than toward clandestine worship.
5. **Measurement.**
   - Faith before freedom is recorded only when stated, so 81% of narratives are `ns`. Silence is not evidence of unbelief.
   - Black control of worship and reported faith often come from the same passage (§3.4).
   - Conversion is datable in only 7% of narratives.
   - "Black-run" postwar churches are counted only when identifiable. Most of the 106 postwar memberships were almost certainly in Black congregations but are not counted as such.
6. **Segmentation and extracts.**
   - About 1.6% of TOC entries could not be segmented separately.
   - The coder read keyword-selected extracts, not complete narratives. A religion statement without any listed keyword (e.g. "the Lord") could be missed. Extracts were capped at about 3,200 characters, and 19 longer narratives were truncated.
7. **Single first coder.** The same-session recode (§3.6) is intra-coder stability only. The independent second coding covers 40 narratives, was done by a separate session of the same model and not by a human rater, and could not assess `prayed_for_freedom` (last section).

## 5. Bearing on the article's claims

- **"Who holds the remedy" claim:** consistent with the data, as association only. In the slaves' own memory, white-held religion is overwhelmingly supervised and often obedience-only, and evaluations of it are mixed. Where the community held some control of worship, the testimony is roughly four times as likely to show devotion and almost all reports of praying for freedom occur. The association weakens to a non-significant OR of 1.8 when only the informant's or a relative's own faith counts.
- **"Deliverance/emancipation" rival (Fountain 2010):** consistent, but not a fair test. Dated conversions are overwhelmingly post-1865 and 89% of identifiable postwar churches were Black-run. Both patterns follow from informants' youth in 1865 and from the timing of institutional Black church-building after 1865, not necessarily from emancipation as such.
- **Neither account is refuted by these data.** The evidence fits a two-track pattern: devotion in self-controlled spaces before 1865, and institutional affiliation in Black-run churches after it.

**Changes from the pilot of 51 narratives.**
- That pilot included 9 targeted additions. In it, Black-led worship appeared in 26 of 51 narratives, and conversion was dated in 7 of 51, 5 of them after 1865.
- In this random sample, Black control is reported in 92 of 206 narratives stating control (23% of all 400), and dated conversions remain rare (28 of 400). The pilot's figures are not directly comparable, because of its targeted additions and different denominators.

## 6. Files

- `codebook.md`: categories, decision rules and examples (written before coding).
- `data.csv`: 400 rows, one per sampled narrative. It holds the informant, state, volume, Gutenberg eBook number, segment line range (header block included since 2026-11-11), interviewer and documented race with source, age, hearsay flag, all codes, notes, and a verbatim snippet with a `pg<eBook>.txt line N; vol., "informant"` locator for every substantive code.
- `double_code.csv`: the first coder's own same-session recodes of the 40 reliability narratives (intra-coder stability).
- `second_coder.csv`: the independent blind second coding of the same 40 narratives, with snippets, locators and notes.
- `reliability_independent.md`: the independent reliability table, every disagreement with both codes and snippets, and their classification.
- `corpus_screen.csv`: all 2,143 segmented narratives, with locator, keyword hits, religion flag and sampled flag.
- `interviewer_corrections.csv`: the 117 rows whose `interviewer` or `interviewer_race` changed on 2026-11-11, with old and new values and the Gutenberg line that shows the credit.
- `analysis.py`: re-runnable; prints every table above.
- `pipeline/`: the segmentation, screening and sampling, extract-generation and merge/verification scripts, the interviewer correction of 2026-11-11 (`interviewer_fix.py`), plus the list of Gutenberg eBook numbers. The raw downloads are not redistributed; they are re-downloadable from the URLs above.

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
| interviewer_race (context) | 40/40 = 100% after the correction of 2026-11-11; 38/40 = 95% at the blind comparison | 1.00; 0.85 at the blind comparison | 9 / 9; 7 / 9 at the blind comparison |
| hearsay_only (context) | 37/40 = 92.5% | 0.63 | 3 / 6 |

The worship-control flags and obedience preaching were reproduced exactly, but agreement is lower for attitude to white preachers (the neutral–positive boundary), faith before freedom and above all postwar church attendance, and in all 20 disagreements on hypothesis variables the first coder has `ns` or `neutral` where the second coder has a substantive code (5 from text outside the keyword extract, 8 from codebook ambiguity, 7 from judgement), so the first-pass counts for those three variables are conservative lower bounds. These figures come from 40 narratives coded by a second session of the same model and not by a human rater, they leave `prayed_for_freedom` untested, and they supersede the same-session recode in §3.6, which is intra-coder stability only. The `interviewer_race` row is no longer a blind figure: the two disagreements (J.M. Parker, Alice Green) were first-coder errors that the correction of 2026-11-11 removed from `data.csv`, so `analysis.py` now prints 40/40.
