# Notes for the author only (not for submission)

Manuscript: `manuscript_ssh.md`. Companion files: `tables_ssh.md`, `title_page_ssh.md`, `bio_note_ssh.md`, `supplement_ssh.md`. Prepared 11 November 2026.

Contents:

1. Status and word counts
2. The five generalizations as finally worded
3. Open issues you must settle before submission
4. Claims weakened or dropped, and why
5. Audit items applied (`audit_manuscript.md`)
6. Mock-review corrections applied, and "check" items not asserted
7. Quotation checklist
8. Close paraphrases of primary sources to check
9. Works cited whose full text nobody in the project has read
10. Reference details still pending

---

## 1. Status and word counts

| Part | Words |
|---|---|
| Abstract | 247 (limit 250) |
| 1 Introduction | 864 |
| 2 Theory and prior work | 1,054 |
| 3 Design, cases, data, and methods | 1,300 |
| 4 Plague-era England | 2,286 |
| 5 Enslaved and free Black Christians in the United States | 1,832 |
| 6 A typology of responses | 1,140 |
| 7 Discussion | 827 |
| 8 Conclusion | 219 |
| Footnotes (5) | 233 |
| References (66 entries) | 1,357 |
| **Text + notes + references** | **11,112** (limit 12,000) |
| Whole file including title, abstract, keywords | 11,394 |

- Title: 121 characters including spaces (limit 140). The longest section heading is 66 characters (limit 70).
- Tables: 5, in `tables_ssh.md`, with callouts in the text.
- Section 4 is about 400 words over its planned budget, and sections 2, 3, 6, 7 and 8 are under theirs. The total leaves about 900 words of room.
- Counts are whitespace-separated tokens, counted by script. Word will give a slightly different figure. Update `title_page_ssh.md` after you revise.

## 2. The five generalizations as finally worded (section 6.2)

- **G1.** After collective suffering, demand for religious goods persisted or rose, and abandonment of faith is rare in the record.
- **G2.** Responses toward the church varied with who held the remedy and who delivered care. (Four types: devotion inside the church; lay custody inside the church; lay custody outside the church; separation. Limit case from the secondary literature: rejection.)
- **G3.** Church authorities answered lay initiative in three ways: they delegated the remedy and reclaimed it, suppressed lay custody, or absorbed it.
- **G4.** Heightened devotion faded when the danger passed, while organizations built by sufferers endured.
- **G5 (tentative).** Institutional self-correction may be a path to renewed trust. Stated as a question for further work.

Each is presented as an observed regularity in two cases, with its evidence and scope. None is presented as a law.

## 3. Open issues you must settle before submission

**A. Things only you can supply**

1. `[TOOL, VERSION, DATES]` in section 3.5 and in the supplement, and `[TOOL, VERSION, DATES; access]` on the title page. The journal asks for tool name, version, dates of use, and how it was accessed.
2. `[REPOSITORY, anonymized for review]` in section 3.5 and in the supplement. The project repository is named after a person, so it must not be linked in the anonymous files. Make an anonymized archive for review, and put the real link only on the title page.
3. Author details, funding statement and biographical note.
4. `cover_letter_ssh.md` (written separately) still has `[TITLE]` and `[WORD COUNT]` and calls the second case "the slave South". The article's title now says "the United States under Slavery", because the case includes free Black Philadelphia. Align the letter.

**B. The first person and "my translation"**

5. The text uses "I" and says once (section 3.2) "Translations from Latin are mine." That is true only after you have checked and adopted each rendering against the page image. The renderings were drafted by the AI tool. See section 7 below. If you do not adopt them, change the sentence.
6. Section 3.5 says the model worked "under my direction". Confirm that this describes what you did.

**C. Statements that rest on OCR, not page images**

7. All Latin was checked against OCR text, not against page images. Long-s spellings were normalised by eye. Check each Latin phrase in section 7 below against the scan.
8. `ut tenentur` ("as they are bound") and `juxta doctrinam apostoli` in Ralph's mandate were not in the independent audit. I re-checked both in the Internet Archive OCR of Wilkins vol. 2 on 11 November 2026: `confiteantur juxta doctrinam apoftoli alterurri fua peccaca etiam laico` (p. 745) and `eadem peccata confiteantur iterum, ut tenentur, fuo proprio facerdoti` (p. 746). The manuscript does not name the apostle. The phrase "confess … to one another" echoes James 5:16, but the manuscript does not say so, because nobody checked it. Section 4.2 also paraphrases two further clauses from the same OCR that are new to this manuscript and need your eye on the page image: (a) `praedicta confeffio facta laico in cafu praemiffo juxta doctrinam ecclefiae et canonica inftituta, ad remiffionem peccatorum eis multum falubris effe poterit` (confession to a lay person in this case accords with the teaching of the Church and the canons; OCR reads `inftimta`); (b) `quid in tali neceffitatis articulo agere debeant, ignorantes, et credentes nullam aliam etiam in cafu neceffitatis confeffionem peccatorum fuorum utilem aut meritoriam eis effe, nifi quae fit facerdoti ecclefiae claves habenti` (the sick do not know what to do and believe that only confession to a priest with the keys can help).
9. Smith (1870: 8), the St Katherine Aldersgate gild paying the Friars Minor: the page number was inferred from running heads in the OCR. Check it.
10. Westlake's certificate 382 is quoted without a page number (the results file gives the certificate only). Add the page.
11. Avesbury (Thompson 1889: 407–8): the reading notes are the only check. The audit did not cover this text.

**D. Evidence and method**

12. **No human has coded anything.** Section 3.5 says so plainly. A reviewer may ask for a human-coded subsample. If you can code even 40 units of each dataset yourself, do it and report the agreement.
13. **Codebook timing.** The wills and gild codebook files were last modified after their data files. The manuscript therefore says "written before coding and amended as documented". The supplement lists the amendments recorded in the gild codebook. The wills codebook records no amendments. Look at the file history and add a line to the supplement if anything changed.
14. **Interviewer-race figures.** The manuscript uses the corrected figures in `results.md` (Black 53, white 11, unknown 336; negative attitude 7/21 against 15/153, Fisher p = .007). The comparison is described as fragile. Two narratives with two interviewers each are still coded "unknown" pending a codebook rule (change log, item 7).
14a. **Line locators for two interview quotations.** `results.md` gives line 2094 for the William Mathews passage and line 7102 for the Minnie Davis passage. In the Gutenberg files downloaded on 11 November 2026 they are at lines 2120–21 and 7131–33 (`data.csv` also has 7131 for Davis). The supplement (S4) uses the checked lines. Correct `results.md` to match.
15. **The wills' main comparison** uses the subset with a stated burial place. The first-period cell is small (n = 83), and its intervals are wide. The text reports only the steps after 1361 as exceeding chance.
16. **"Three-quarters" of gilds from four counties** is 386 of 509 (75.8%), from Westlake's county totals in the results file.
17. **Table 3, Panel A, "exact years only (n = 247)"**: 41 + 206, from the results file.
18. **Table 1** has two cells marked "Not recorded in the sources coded" (funds and care in the plantation South). A reviewer may ask for more. The interviews mention community-paid funeral sermons (literature review, section 15), but this was not coded in the random sample, so it is not claimed.

**E. Framing choices you may want to change**

19. Title: "the United States under Slavery" replaces "the Slave South", for the reason in item 4.
20. G3's label "delegate and reclaim" is kept, but the text says that Ralph's mandate applies established doctrine on necessity and is not an innovation. The mock reviewer objected to "lent" and "decided"; neither word is used.
21. The Tournai town ordinances are not used at all. Footnote 1 says that li Muisis's *remedium* means a remedy for the panic caused by bell-ringing and that the article's term is independent of his.
22. Taiwan is one paragraph in section 7.2 plus footnote 5 with the survey figures. If you want the survey figures out, delete footnote 5 and the Fu et al. reference (saves about 150 words).
23. G5 has no indicator of its own. The five indicators code who holds the remedy and who delivers care. Self-correction is observed from what a church said about its failure and what then changed. The article says only that the cases are too few.

## 4. Claims weakened or dropped, and why

| Claim in the brief or in earlier drafts | What the article now says | Why |
|---|---|---|
| Gilds multiplied after the Black Death | "Of the 286 gilds that state a year between 1300 and 1389, 235 give 1349 or later … This cannot show that gilds multiplied." Persistence is claimed, not a surge. | Survivorship: only gilds alive in 1388–89 were recorded. A dissolution rate near 4% a year gives the same ratio. |
| Wills show devotion rising after 1349 | Only the burial-clause subset is used for the main comparison. The text says much of the rise in all wills is a recording artifact, and that the wills "cannot establish either reading". G1 rests on the absence of any recorded decline, and section 7 adds that fuller recording could mask a decline. | Enrollment practice changed about 1349, and Sharpe's summaries lengthen. |
| London does not show Cohn's concentration of gifts | "Weak evidence about London and no test of Cohn." | Presence/absence codes cannot measure the size of gifts. Cohn's book was not read. |
| Black control of worship went with faith ("four times as likely") | "About four times the odds (odds ratio 4.06)", then the weaker result for the informant's own or a relative's faith (odds ratio 1.81, not significant), and "association within testimony". | Wording corrected in the results file. One passage often supplies both codes. |
| "Almost all" prayers for freedom came from Black-controlled worship | "10 of them", with "reliability of that code is untested". | Results file, change log items 5 and 6. |
| Faith before freedom in 72 narratives; positive attitude in 39; neutral in 113; postwar church in 106 | "At least 72", "at least 39", "at most 113", "at least 106". | The independent second coder found more substantive codes in every disagreement. |
| WPA conversion dates support Fountain | "The interview sample cannot test this." | Median age 83 in 1937: informants were children in 1865. |
| Commitment followed control of worship after 1865 | Not claimed. The text says people who already worshipped moved into Black-run churches when they could, that how many did so is not known, and that Fountain's reading is not excluded for the majority. | Freedom brought deliverance and control together. |
| "The church of his day taught that the remedy for the plague was penance" | "Church authorities in England explained the plague as punishment for sin and ordered liturgical answers." | Audit F4, O1. The Canterbury letter is from the prior and chapter and orders prayers, masses, sermons and processions. |
| The hierarchy's own records of its clergy's failure | "Records of a shortage of priests, and in two of them of priests' unwillingness. The York letter attributes the shortage to deaths." | Audit O3. |
| The remedy passed to a town government at Tournai | Dropped. | Audit O4; coordinator's instruction. |
| Tournai murmuring against the clergy as evidence that a serving church was still distrusted | Dropped. | Audit O7: the context was reversed. |
| Andrew Moss quotation | Dropped. | Audit quotation 26: wrong attribution. |
| Rubinstein on the Presbyterian Church in Taiwan | Dropped. Rubinstein is not cited. | Audit A19: the old claim was wrong. |
| Taiwan survey item on religious leaders speaking in public; the 2018 referendums | Dropped. | Audit F33, O20: there is no 2018 peak. |
| Robinson "undercuts the old account of an inferior replacement clergy" | "Found from ordination lists that men ordained in the plague years came from much the same backgrounds." | Audit A12: the inference was not Robinson's. |
| Duffy as evidence about 1348–62 | "Though for a period that begins around 1400." | Audit A10. |
| Martin and Casanova "showed" | "Argued". | Audit A6. |
| Clement VI suppressed the flagellants for acting without licence | The bull's charges of bloodshed against Jews and Christians and of plunder are stated. "I do not assess how far those charges were fair." | Mock review; audit O6. No historian's doubt is attributed, because none was verified. |
| "No human agent" inflicted suffering in the plague case | Dropped. A paragraph acknowledges the massacres of Jews and the papal bulls of 1348, and says the typology does not cover that violence. | Mock review, Reviewer 2, concern 3. |
| Jones and Allen 1794 shows "a remedy in its own hands" | The nursing is described as care, on terms not the community's own. The pamphlet is described as a defense against Mathew Carey. | Mock review; audit O13. |
| Colored Methodist Episcopal Church (1870) as a hard case | Not used. | The project marks its founding details "verify". Hildebrand is cited only for competition among Methodist bodies. |
| Venette: bequests to churches as evidence of devotion | His stated reason is given: the dying saw their heirs die first. His claim that none died unconfessed is set against Ralph. | Audit F20, O24. |
| Avignon: papal physicians and cemetery | Not used. | Space; and audit F12 (the same paragraph reports the pope's seclusion). |
| Flagellants at Tournai were stopped by town and king | The sermon arranged by bishop, chapter and governors, the announcement of the papal mandate, and "the bull was not shown" are added. | Audit F17. |
| AME founded "to preserve us from that spiritual despotism" | The clause is attached to the adoption of a form of discipline. | Audit quotation 37. |
| The Philadelphia elders "answered a complaint" | The elder's threat answers the group's separate worship and building subscription. | Audit O12. |
| Douglass's class-leader "stood with the master" | "The oppressor and the church officer are one person." | Audit O11. |
| "Trust attaches to conduct and not to office" | "I read these two passages as attaching trust to conduct, not to office." | Audit O9. |
| Brazil's religious orders as slaveholders (Schwartz 1982) | Not cited. Table 5 says only "an established Catholic church". | Reference budget; the detail is not needed. |
| Rwanda: figures for new churches and Catholic share | Not given. | Flagged "verify" in the literature review. |
| Korea: compliance and post-1945 separation | "Are reported to have". | The detail comes from Korean-language works cited in the literature review, not from Kim (1989), whose dissertation nobody read. See section 9. |
| A Black Death–slavery comparison has never been made | "To my knowledge, these two well-documented cases have not been set side by side with evidence coded under one scheme." | Student theses exist (literature review, section 19). The narrower claim is about coded evidence. |

## 5. Audit items applied (`audit_manuscript.md`)

Applied to every passage carried over from `manuscript_sce.md`:

- **Quotations.** No. 26 (Andrew Moss) dropped. No. 31 (Walker): gloss added, "The master he means is Christ." No. 37 (Allen): reframed. No. 19: C. C. Jones cited as pp. 73–74. Nos. 20–24, 33, 42: Jacobs pages 103, 105, 108, 110, 113. Nos. 29, 30, 32: Douglass pages 118, 119, 54. Nos. 3 and 14 (block quotations): not used, so the missing ellipses do not arise. No. 39 (1971 statement): not quoted. No. 41 (1990 apology): paraphrased, not quoted.
- **Translations.** T1/T4: "if no layman is at hand". T3: "as we have heard" restored; the causal link ("because no priests could be found … many were dying") restored; "the infection and the dread of contagion". T5: "faith in the sacrament must suffice, as in other cases". T20/T21: "public support and warmth"; "cowed by martial-law rule".
- **Citations.** Canterbury letter: p. 738 only, dated 28 September 1348, from the prior and chapter. Islip 1362: Wilkins 3: 50–51, 16 November 1362, "a new constitution with the same opening words". Raynaldus: the bull at §§20–22, pp. 471–72 (footnote 3); imprint 1880. Bottan and Perez-Truglia: pp. 113–14. Holmes's register is not cited, so the imprint question does not arise; the place of dating is not stated, so Wilkins's "Wynchelcomb" does not arise.
- **Facts.** F4, F6, F8, F17, F20 applied as described in section 4 above. F12, F30–F34: Avignon and the public-speech item not used; the trust series is in footnote 5 with four cautions and the fieldwork dates. F43, F44: methods and supplement reworded.
- **Attributions.** A6, A10, A12, A33 applied. A4, A19, A27, A28: the works are not cited.
- **Overreach list (26 sentences).** Equivalent sentences were rewritten or dropped: O1–O4, O6–O13, O15, O20–O25. O5, O14, O16–O19, O26 concern passages that are not carried over.
- **Anonymization and workflow traces.** No author-facing flags, no `[[EVIDENCE]]` placeholders, and no repository link in the manuscript. The only bracketed items are the required placeholders `[TOOL, VERSION, DATES]` and `[REPOSITORY, anonymized for review]`.
- **Method statements.** Section 3.5 states that a large language model performed the coding under written codebooks; that codebooks were written before coding and amended as documented; that the first interview recode was by the same coder and measures intra-coder stability only; and that the independent second coding was by a separate session of the same model, not a human.
- **One audit detail not carried into the text:** the source table for the survey labels the third wave "2019". Footnote 5 gives the fieldwork dates (July 2018 to February 2019) instead.

Coordinator's corrections of 11 November on the interview data: all figures in section 5.2, Table 4 and the supplement were re-read from the corrected `results.md` and its change log (Black interviewers 53; 7/21 against 15/153, p = .007; "about four times the odds"; bounds on attitude, faith and postwar church; prayer for freedom 13, reliability untested).

## 6. Mock-review corrections applied, and "check" items not asserted

**Applied (verifiable from project files):**

- Ralph of Shrewsbury's mandate applies established doctrine on necessity; its words *juxta doctrinam apostoli* are quoted; the duty to confess again is part of the rule.
- "Remedy" is defined analytically. Li Muisis's *remedium* is explained in footnote 1.
- Clement VI's bull also charges the shedding of the blood of Jews and Christians and the seizure of goods. The saving clause for private penance is kept.
- The persecution of Jews in 1348–51 is acknowledged, with the two papal bulls and Raynaldus's admission that they failed outside the county of Avignon.
- The plantation South and free Black Philadelphia are treated as different settings, under separate headings.
- The 1794 *Narrative* is presented as an answer to Mathew Carey, and the false assumption of immunity is stated.
- Biracial Southern churches are acknowledged (Irons 2008; Sparks 1994).
- Venette and li Muisis are identified as a Carmelite and a Benedictine abbot, with a sentence of source criticism for Venette.
- Hard cases are named in section 6.3.
- The quantitative material is now the body of the article, not an appendix.

**Marked "check" in the mock review and therefore NOT asserted:**

- Peter Lombard, Aquinas and Lateran IV canon 21 on lay confession; Teetaert's study.
- The name *Inter sollicitudines* for the bull (footnote 3 says it is unverified).
- Kieckhefer or Haverkamp on whether the charge of anti-Jewish violence was fair.
- The Colored Methodist Episcopal Church's founding in 1870 and any transfer of property.
- For Taiwan: the 1975 seizure of Bibles; the 1951 General Assembly; named Presbyterian victims of 1947; Kao Chun-ming's imprisonment; the 1995 presidential apology; the context of the 1971 statement.
- That English people "watched but did not join" the flagellants. The text says only that Avesbury does not report how Londoners responded.

## 7. Quotation checklist

Every direct quotation in the manuscript, in order. "Checked" says what the project has done so far. All scans were checked as OCR text only; the page images still need your eye.

| # | Quotation as printed | Section | Edition | Locator | URL | Whose translation | Checked |
|---|---|---|---|---|---|---|---|
| 1 | "even to a layman, and if no layman is at hand, to a woman" (*etiam laico, et si desit vir laicus, mulieri*) | 1 | Wilkins 1737, vol. 2 | p. 745 | https://archive.org/details/conciliamagnaebr02wilk | AI draft; yours once checked | Latin: audit, exact. Translation follows audit T1. |
| 2 | *juxta doctrinam apostoli* | 1 | Wilkins 1737, vol. 2 | p. 745 | as no. 1 | not translated in quotation marks ("apostolic teaching") | Re-checked in OCR, 11 November 2026 (`juxta doctrinam apoftoli`). Check the page image. |
| 3 | "as they are bound" (*ut tenentur*) | 1 | Wilkins 1737, vol. 2 | p. 746 | as no. 1 | AI draft | Re-checked in OCR, 11 November 2026. Check the rendering and the page image. |
| 4 | "their little church in the woods" | 1 | Jacobs 1861 | p. 103 (ch. XII) | https://archive.org/details/incidentsinlifeo1861jaco ; text https://www.gutenberg.org/ebooks/11030 | none | Audit, exact |
| 5 | "was built by the colored people" | 1 | Jacobs 1861 | p. 103 | as no. 4 | none | Audit, exact |
| 6 | "their request was denied, and the church was demolished" | 1 | Jacobs 1861 | p. 103 | as no. 4 | none | Audit, exact. Source has a capital T; the manuscript runs it into a sentence. |
| 7 | "Before religious competition led to the articulation of institutional alternatives, these shocks did not lead to institutional change" | 2 | Dittmar and Meisenzahl 2020 | p. 983 | https://doi.org/10.1093/restud/rdz002 | none | Reading notes (full text read) |
| 8 | "invisible institution" | 2 | Raboteau (1978) 2004 | title | not open access | none | Title only |
| 9 | "as we have heard" (*ut accepimus*) | 4.2 | Wilkins 1737, vol. 2 | p. 745 | as no. 1 | AI draft, after audit T3 | Audit |
| 10 | "cannot be found" (*nequeunt inveniri*) | 4.2 | Raine 1873 | p. 401 | https://archive.org/details/historicalpapers00rain | AI draft | Audit, exact |
| 11 | "excessive stipends" (*stipendia … excessiva*) | 4.2 | Wilkins 1737, vol. 3 | p. 1 | https://archive.org/details/conciliamagnaebr03wilk | AI draft | Audit, exact |
| 12 | "makes his will seeing the peril of this world and especially of the existing plague" | 4.3 | Sharpe 1890 | p. 125; Roll 97 (15) | https://www.british-history.ac.uk/court-husting-wills/vol2 | none (Sharpe's English) | Dataset snippet (will HW1563) |
| 13 | "The alderman collects the chaplain's salary" | 4.4 | Westlake 1919 | cert. 180 (page not recorded) | https://archive.org/details/parishgildsofmed00westuoft | none (Westlake's English) | Results file |
| 14 | "chaplain elected by them" | 4.4 | Westlake 1919 | cert. 182 (page not recorded) | as no. 13 | none | Results file |
| 15 | "to assist the parson daily … whereby the parson's difficulties were much relieved" | 4.4 | Westlake 1919 | cert. 382 (page not recorded) | as no. 13 | none | Results file |
| 16 | "carried through the parts of the town with only a single candle of poor wax burning in front of it" | 4.4 | Westlake 1919 | p. 199, cert. 279 | as no. 13 | none | Results file. The source reads "was being carried through …"; the manuscript begins the quotation at "carried". |
| 17 | "were suspended by the great plague, but renewed later by survivors and parishioners of other parishes" | 4.4 | Westlake 1919 | p. 184, cert. 203 | as no. 13 | none | Results file |
| 18 | "more than the divine office" (*plus quam divinum officium*) | 4.5 | Lemaître 1906 | p. 239 | https://archive.org/details/chroniqueetannal00lemuuoft | AI draft | Audit, exact; T11 accurate |
| 19 | "without the license of a superior" (*sine superioris licentia*) | 4.5 | Raynaldus 1880, vol. 25 | p. 471 | https://archive.org/details/annalesecclesias25barouoft | AI draft | Audit, exact; T12 accurate |
| 20 | "with great murmuring, unwillingly" (*cum magno murmure inviti*) | 4.5 | Lemaître 1906 | p. 252 | as no. 18 | AI draft | Audit, exact; T13 accurate |
| 21 | "when the storm ceased, the pilgrimage and the devotion ceased as well" (*Cessante autem tempestate cessavit etiam peregrinatio et devotio*) | 4.5 | Lemaître 1906 | p. 258 | as no. 18 | AI draft | Audit, exact; T15 accurate. The sentence concerns Saint-Médard at Soissons. |
| 22 | "forbid religious meetings, and religious instruction on our own plantations" | 5.1 | C. C. Jones 1842 | p. 158 | https://archive.org/details/religiousinstruc01jone | none | Audit, exact (part of the longer passage) |
| 23 | "literally shut up the kingdom of heaven against men" | 5.1 | C. C. Jones 1842 | p. 158 | as no. 22 | none | Audit, exact |
| 24 | "in a state of almost absolute dependence upon their owners for the words of eternal life" | 5.1 | C. C. Jones 1842 | p. 158 | as no. 22 | none | Audit, exact |
| 25 | "separate entirely the civil and religious condition of this people" | 5.1 | C. C. Jones 1842 | p. 73 | as no. 22 | none | Audit, exact |
| 26 | "disclaim all interference with the former" | 5.1 | C. C. Jones 1842 | pp. 73–74 | as no. 22 | none | Audit, exact |
| 27 | "All attempts to suppress this class of influential men among their own colour have signally failed" | 5.1 | Association … Liberty County 1846 | p. 13 | https://archive.org/details/226033457.4721.emory.edu | none | Audit, exact. British spelling "colour" is the source's. |
| 28 | "to give the slaves enough of religious instruction to keep them from murdering their masters" | 5.1 | Jacobs 1861 | p. 105 | as no. 4 | none | Audit, exact |
| 29 | "but the law forbids it, and the churches withhold it" | 5.1 | Jacobs 1861 | p. 113 | as no. 4 | none | Audit, exact |
| 30 | "Sometimes at night us gather 'round the fireplace and pray and sing and cry, but us daren't 'low our white folks know it" (split by the attribution) | 5.2 | Federal Writers' Project 1941, vol. XVI pt. 3, Susan Merritt | pg35380.txt, lines 2340–42 | https://www.gutenberg.org/ebooks/35380 | none | Script-verified snippet; re-checked against the Gutenberg text on 11 November 2026 |
| 31 | "All he could preach 'bout was obey de massa, obey de overseer, obey dis, obey dat" | 5.2 | same, William Mathews | pg35380.txt, lines 2120–21 (the results file says line 2094) | as no. 30 | none | Re-checked against the Gutenberg text. "He" is a Black man who preached: "If a cullud man take de notion to preach, he couldn't preach 'bout de Gospel." The manuscript now says so. |
| 32 | "the overseer stood there to see the preacher talked as he wanted him to talk" | 5.2 | vol. I, Charlie Van Dyke | pg36020.txt, lines 12896–97 | https://www.gutenberg.org/ebooks/36020 | none | Script-verified snippet; re-checked against the Gutenberg text |
| 33 | "praying to herself: 'Oh, Lord, please send the Yankees on and let them set us free'" | 5.2 | vol. IV pt. 1, Minnie Davis | pg13602.txt, lines 7131–33 (the results file says line 7102) | https://www.gutenberg.org/ebooks/13602 | none | Re-checked against the Gutenberg text: "My mother said that all the time he was praying out loud like that, she was praying to herself". The white minister was praying that the Yankees be driven back. |
| 34 | "I love the pure, peaceable, and impartial Christianity of Christ: I therefore hate the corrupt, slaveholding, women-whipping, cradle-plundering, partial and hypocritical Christianity of this land" | 5.3 | Douglass 1845 | p. 118 (Appendix) | https://archive.org/details/narrativeoflifeo1845doug | none | Audit, exact |
| 35 | "The man who robs me of my earnings at the end of each week meets me as a class-leader on Sunday morning, to show me the way of life" | 5.3 | Douglass 1845 | p. 119 | as no. 34 | none | Audit, exact. The sentence continues ", and the path of salvation". |
| 36 | "one might believe it was a plan fabricated by themselves and the devils to oppress us. But hark! My master has taught me better than to believe it" | 5.3 | Walker 1830, 3rd ed. | p. 40 | https://archive.org/details/walkersappealinf00walk | none | Audit, exact |
| 37 | "We slaves loved Mr. Cookman" | 5.3 | Douglass 1845 | p. 54 (ch. IX) | as no. 34 | none | Audit, exact |
| 38 | "it was the first time they had ever been addressed as human beings" | 5.3 | Jacobs 1861 | about p. 110 | as no. 4 | none | Audit, exact; page "about 110" |
| 39 | "God has hid himself from me" | 5.3 | Jacobs 1861 | about p. 108 | as no. 4 | none | Audit, exact; page "about 108" |
| 40 | "pulling him up off of his knees, and saying, 'You must get up—you must not kneel here.'" | 5.4 | Allen (1833) 1880 | pp. 14–15 | https://archive.org/details/lifeexperiencego1880alle | none | Audit, exact |
| 41 | "we all went out of the church in a body, and they were no more plagued with us in the church" | 5.4 | Allen (1833) 1880 | p. 15 | as no. 40 | none | Audit, exact |
| 42 | "if you deny us your name, you cannot seal up the scriptures from us, and deny us a name in heaven" | 5.4 | Allen (1833) 1880 | p. 16 | as no. 40 | none | Audit, exact. Source begins "and if you deny us". |
| 43 | "preserve us from that spiritual despotism which we have so recently experienced" | 5.4 | Allen (1833) 1880 | p. 24 | as no. 40 | none | Audit, exact; now attached to the form of discipline |
| 44 | "Thus were our services extorted at the peril of our lives, yet you accuse us of extorting a little money from you" | 5.4 | Jones and Allen 1794 | p. 15 | https://archive.org/details/b32886561 | none | Re-checked in OCR, 11 November 2026 (long-s print). Page from the reading notes. |
| 45 | "When the war is over, and all things righted, / God is forgotten, and the soldier slighted" | 5.4 | Jones and Allen 1794 | p. 20 | as no. 44 | none | Re-checked in OCR, 11 November 2026. Page from the reading notes. |
| 46 | "a new and independent country" | 7.2 | Presbyterian Church in Taiwan 1977, English text | — | https://china.usc.edu/node/20514 | none (existing English text) | Audit, exact |

Scare-quoted terms that are the article's own and not quotations: "remedy", "hold", "the church", "delegate and reclaim", "absorb", "time without memory" (Table 3; Westlake's phrase as given in the results file), "pious uses" (supplement; Sharpe's phrase).

## 8. Close paraphrases of primary sources to check

| Statement in the manuscript | Source and locator | Status |
|---|---|---|
| Canterbury: God sometimes punishes in time so as not to condemn in eternity; prayers, masses, sermons, processions, indulgences; 28 September 1348 | Wilkins 1737, 2: 738 | Audit T16, F4, F5 |
| Zouche ordered processions and litanies in July 1348 and named human sins as the cause | Raine 1873: 395–96 | Reading notes |
| Ralph: parishes without a priest; deacon may give the Eucharist; faith in the sacrament suffices for unction; recovered penitents confess again | Wilkins 1737, 2: 745–46 | Audit F3, T3, T5 |
| Clement VI allowed York additional ordinations "on account of the mortality", 12 October 1349 | Raine 1873: 401 | Audit F6 |
| Islip, 28 May 1350: priests leaving cures for privately paid annual masses | Wilkins 1737, 3: 1–2 | Audit F7 |
| Islip, 16 November 1362: a new constitution, same opening words, sharper language | Wilkins 1737, 3: 50–51 | Audit F8. "Sharper language" is from the reading notes. |
| Avesbury: more than 200 burials almost daily, Candlemas to after Easter 1349, new cemetery by Smithfield; more than 120 flagellants, mostly from Zeeland and Holland, about Michaelmas 1349, twice a day, in the sight of the people | Thompson 1889: 407–8 | Reading notes only |
| Sharpe: enrolled wills dealt with land; the testament of movables was usually not enrolled; he omitted bequests of no special interest | Sharpe 1889: xxv, xlviii | Results file |
| St Katherine's gild, Aldersgate: wardens call the Friars Minor for a dirige and a trental and pay them | Smith 1870: 8 (page inferred) | Reading notes; check page |
| Westlake: a gild that did not survive left no memorial | Westlake 1919: 27 | Results file |
| Flagellants reach Tournai 15 August 1349; people mock clergy; companies bury the dead by Advent and receive gifts; oath | Lemaître 1906: 231, 239, 240, 243 | Audit F13–F16 |
| Bull of 20 October 1349: keys despised; blood of Jews and often of Christians; goods of clergy and laity seized; private penance at home not forbidden | Raynaldus 1880, 25: 471–72 | Audit F18, T17, T18; charges of bloodshed and plunder from the reading notes |
| Tournai, Lent 1350: proclamations by town and king; sermon arranged by bishop, chapter and governors; mandate announced, bull not shown | Lemaître 1906: 251–52 | Audit F17 |
| Bulls protecting Jews, 4 July and 26 September 1348; Raynaldus: they failed everywhere except the county of Avignon | Raynaldus 1880, 25: 453–55 | Reading notes; literature review section 4 |
| Venette: timid priests withdrew, leaving the ministry to bolder religious; Hôtel-Dieu sisters; none died without confession and viaticum; bequests because heirs died first | Géraud 1843, 2: 211–13 | Audit F9, F20, T9 |
| Li Muisis: many curates and chaplains who heard confessions and visited the sick died | Lemaître 1906: 258 | Audit F11 |
| Jacobs: an old man who wanted to read the Bible; a rector whose sermons people gladly attended; a mother whose children had all been taken, in a class meeting | Jacobs 1861: 113, 110, 108 | Audit |
| Douglass: Cookman believed to have helped persuade a rich slaveholder to free his slaves | Douglass 1845: 54 | Earlier checklist |
| Allen: separate worship and subscription; elder's threat; Methodist by conviction; dispute over pulpit and property; April 1816 | Allen (1833) 1880: 15–17, 18, 20–21, 24 | Audit O12, F25, note on pp. 18, 20–21 |
| 1793: newspaper appeals on the assumption of immunity; elders of the African church; Carey's accusation; burials 67 (1792) and 305 (1793) | Jones and Allen 1794: 3–5, 15–16 | Reading notes |
| *Christian Recorder*: Kentucky congregations stayed in the AME, and Virginia societies in buildings deeded to the Southern church (between the mastheads of 16 and 23 January 1869); Nashville letter (12 or 19 May 1866); treason charge (13 March 1869) | Internet Archive bound runs | Audit F27, F28. Poor OCR. |
| Presbyterian Church in Taiwan: dates of 1971, 1975, 1977 and 9 February 1990; the apology's confession, its exception for a few ministers and members, and its demand to the government | pct.org.tw documents 001, 003, 005, 047 | Audit F29, A33, T20, T21 |
| Taiwan survey: 21.5% and 10.7% high trust; 16.0% and 26.9% distrust; fieldwork July 2018 to February 2019; extra categories in 2014 | Fu et al. 2019, appendix 4, p. 222 | Audit F30. "Appear to be unweighted" and "about 4 to 6 percent Protestant" from the earlier checklist and audit F31. |

## 9. Works cited whose full text nobody in the project has read

"Read" here means that the project's reading notes or audit record a reading of the full text, or of the stated part of it. Bibliographic existence was verified for every work cited (`references_status.tsv`), but that is not the same thing. The article says in section 7.3 that several monographs are known through reviews and abstracts.

**Known only from abstracts, publisher descriptions, reviews, or general knowledge of the argument (38 secondary works):**

Blassingame 1975; Boles 2020; Bourdieu 1971; Casanova 1994; Chaves 1994; Cohn 1992; Cohn 2007; Duffy 1992; Finke and Stark 1992; Fountain 2010; Frey and Wood 1998; Geddes 1990; Genovese 1974; George and Bennett 2005; Henderson 1994; Hildebrand 1995; Hirschman 1970; Irons 2008; Kim 1989; Kubai 2007; Larkin 1972; Lieberson 1991; Longman 2010; Martin 1978; Miller 1975; Montgomery 1993; Norris and Inglehart 2011; Pinn 1995; Platt 1996; Raboteau (1978) 2004; Robinson 2019 (abstract); Russell-Wood 1974; Rychetská 2022 (abstract); Scott 1990; Skocpol and Somers 1980; Sparks 1994; Stern 1982; Weber 1978.

Points where the article leans on one of these for more than a general position, and which you should check first:

- **Cohn 1992:** the turning point after the plague of 1363 and gifts staying within church institutions. No page is given.
- **Fountain 2010:** that most enslaved people became Christians with or after emancipation. No page is given.
- **Robinson 2019:** similar backgrounds of plague-year ordinands (abstract).
- **Platt 1996:** memorial masses drawing priests from parishes. The literature review notes that reviewers fault his causal evidence.
- **Irons 2008; Sparks 1994:** biracial congregations.
- **Boles 2020:** Black members leaving over access and equality.
- **Montgomery 1993:** the postwar move into Black-governed denominations.
- **Hildebrand 1995:** competing Methodist bodies.
- **Larkin 1972; Miller 1975; Russell-Wood 1974; Kim 1989; Longman 2010; Kubai 2007; Stern 1982:** the shadow cases in Table 5 and section 6.3. All wording is that of report. For Korea, the statement that most Protestant bodies complied and that resisters formed separate bodies after 1945 comes from Korean-language works named in the literature review (section 10), which are not in the article's reference list. Either read Kim (1989) and confirm that it supports the statement, or cite one of those works.
- **Blassingame 1975:** that informants spoke differently to Black and white interviewers.
- **Pinn 1995:** a skeptical strand in narratives and spirituals.
- **Weber 1978; Bourdieu 1971; Chaves 1994; Hirschman 1970; Finke and Stark 1992; Norris and Inglehart 2011; Martin 1978; Casanova 1994; Scott 1990; Genovese 1974:** one-sentence statements of well-known positions.
- **Skocpol and Somers 1980; Lieberson 1991; Geddes 1990; George and Bennett 2005:** method references, cited for their standard arguments.

**Read in full or in the relevant part (per reading notes or audit):**

- Secondary: Bentzen 2021; Bottan and Perez-Truglia 2015; Dittmar and Meisenzahl 2020. Belloc, Drago and Galbiati 2016: the 2014 working draft was read in full, the published article in abstract only.
- Primary texts and editions: Allen (1833) 1880, pp. 5–24; Association … Liberty County 1846 (the passage on p. 13; extent of reading not recorded); *Christian Recorder*, sampled issues in poor OCR; Douglass 1845; Jacobs 1861; Jones and Allen 1794; C. C. Jones 1842 (the passages cited; extent not recorded); Géraud 1843, vol. 2, pp. 210–18; Lemaître 1906, pp. 222–59; Raine 1873, the four plague documents; Raynaldus 1880, the sections cited; Thompson 1889, pp. 406–8; Walker 1830; Wilkins 1737, the letters cited; Smith 1870, partially; Presbyterian Church in Taiwan 1971, 1975, 1977, 1990 (web texts; the 1975 text was located but its content is not described in the article).
- Coded sources: Sharpe 1889, 1890 (all 1,979 entries, by rule; 198 read closely); Westlake 1919, appendix (all 509 entries via OCR; 51 read from page images); Federal Writers' Project 1941 (400 narratives in keyword extracts; 40 in full).
- Fu et al. 2019: the table on p. 222 only.

## 10. Reference details still pending

| Reference | Detail to settle |
|---|---|
| Sharpe 1889, 1890 | British History Online gives the original publisher as "Her Majesty's Stationery Office, London". The reference list has "Corporation of the City of London", following the results file. Check the imprint on a scan. |
| Smith 1870 | The results file gives the editors as Toulmin Smith and Lucy Toulmin Smith; the master bibliography has "Smith, Toulmin, ed." The reference list follows the master bibliography. |
| Westlake 1919 | Not in the master bibliography; taken from the gild results file. The appendix is pp. 137–238. |
| Thompson 1889 | Listed in the master bibliography as "1889a". Cited here as 1889 because only one work by Thompson is cited. |
| Stern 1982; Kubai 2007 | In the master bibliography as 1982b and 2007a. Cited without the letter for the same reason. |
| Raboteau (1978) 2004; Allen (1833) 1880 | Chicago 18 puts the original year in parentheses in the reference list. The text has square brackets, "Allen ([1833] 1880)", to avoid nested parentheses. Follow the copyeditor. |
| Association … Liberty County 1846 | Cited in the text in short form as "Association 1846". |
| Kim 1989 | Subtitle differs between the Hull repository ("A Study of Religion and Politics") and library catalogues ("A Sociological Study of Religion and Politics"). |
| Blassingame 1975; Lieberson 1991 | End pages marked "detail to verify" in the master bibliography (473–92; 307–20). |
| Fu et al. 2019 | Romanization of the editors' names other than Fu. |
| *Christian Recorder* | Issue dates within the bound volumes are approximate (see section 8). |
| Douglass 1845; Jacobs 1861 | Page numbers are those of the first editions, taken by the audit from the scans' running heads. Jacobs pp. 108 and 110 are "about". |
| Publishers' places | Omitted throughout, following Chicago 18. Restore them if the journal's copyeditor asks. |
| Bourdieu 1971 | Cited in the French original. An English translation appeared in *Comparative Social Research* 13 (1991): 1–44. |
