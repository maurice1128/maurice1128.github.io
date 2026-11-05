# Final-batch fact-check: synthesis, gaps/journals, conferences, AI policies, seminary notes

Auditor: independent adversarial check, 2026-11-05. No target file was edited. Pages were opened with curl (text extracted with Python) or WebFetch. PDFs were downloaded and read with pdftotext.

Status key: **OK** = confirmed at the source · **ERROR** = wrong and needs correcting · **STALE** = was true once but is now out of date · **INCONSISTENT** = contradicts another project file · **OVERSTATED** = goes further than the source · **UNVERIFIED** = source not reachable or claim not found.

## Time-sensitive items (deadlines and dates)

| # | File | Item | Status | Evidence | Correction |
|---|---|---|---|---|---|
| T1 | seminary_application.md §1.1, §5.1, §5.4 | 政大宗教所 116 碩士班考試入學 registration 2026/11/24–12/8 | **OK, but incomplete** | 116碩班簡章.pdf (religion.nccu.edu.tw/upload/34/doc/43599/), p. 1 and 重要日程表: getting a 繳費帳號 runs 115.11.24 09:00 to **115.12.8 12:00 noon**. Entering registration data runs 115.11.24 09:00 to 12.8 15:00. Fee NT$1,300. **筆試 116.2.1–2.2**; for 1151, 宗教傳統與理論 and 專業英文 are both on 2 Feb 2027 according to the 附錄九 timetable. Interview 116.3.8 10:00. Interview documents are uploaded by **116.3.2 17:00**. | Add: "繳費帳號須於 12/8 **中午 12 時**前取得" (after noon you cannot pay, so you cannot register). Add the written exam on 2027/2/1 and the 2027/3/2 17:00 upload deadline for interview documents. The note "審查資料上傳至 12/8 17:00" applies to the 新住民組 (1159) and the generic schedule. 宗教所一般生 submits no review material when registering. |
| T2 | seminary_application.md §2.7 | UChicago MA "第二輪 2027/4/2（國際生最終）" | **ERROR** | divinity.uchicago.edu/admissions/admissions-info: "Master's Programs Round 2: Monday, April 5, 2027 (Final deadline for international students)" | Change to **2027/4/5**. The PhD and MA priority deadline of 2027/1/5 is correct. |
| T3 | conferences_timeline.md (a), 台灣宗教學會 row | "2026: 23–24 Oct 2026, 輔仁大學濟時樓" | **STALE** | sites.google.com/view/tjrsfortars/年會研討會/本會會議訊息: 【大會公告】 the meeting was postponed because of Typhoon 薔琵 to **2026/10/30 (五)–10/31 (六)**, still at 輔仁大學濟時樓 9F. The abstract deadline of 2026/4/30 is confirmed. | Change the date to 30–31 Oct 2026 and note the postponement. |
| T4 | conferences_timeline.md (a), AAR row | "online June sessions 21–24 Jun 2027" | **UNVERIFIED / likely ERROR** | aarweb.org/events/annual-meetings/future-dates/ lists only "2026 Online June Sessions June 23-25" and in-person dates (2027 Washington DC, Nov 20–23, confirmed). No 2027 June dates appear. "21–24" looks copied from Denver, Nov 21–24, 2026. | Write "2027 online June sessions: dates not announced *[not confirmed]*". |
| T5 | conferences_timeline.md (a), ISSR row | Registration deadline 8 Nov 2026 | OK (3 days away) | conference-system.sisr-issr.org/conferences/conference-2027/ | No change. The plan does not target ISSR. |
| T6 | seminary_application.md §2.2–2.15, §5.4 | Upcoming deadlines: Harvard GSAS 2026/12/1 17:00; PTS PhD 12/1; Emory GDR 12/1; CUHK Main Round and HKPFS 12/1; Cambridge funding 12/8 (Gates US 10/14); Cambridge final 2027/4/28; Edinburgh PhD 2027/8/30; Yale priority 1/8, standard 2/1, aid 3/1 | OK | gsas.harvard.edu/program/religion; ptsem.edu/academics/programs-courses/phd-studies/; gdr.emory.edu/admissions/; gs.cuhk.edu.hk/…/mphil-phd-religious-studies; postgraduate.study.cam.ac.uk/courses/directory/dvdvmpmtr; study.ed.ac.uk/…/68-world-christianity; divinity.yale.edu/admissions-aid/how-to-apply | — |

## Target 1: 15_synthesis.md

| # | Item | Status | Evidence | Correction |
|---|---|---|---|---|
| 1.1 | §15.4 rival table, "Provision or relief" row: Claim "Affiliation follows material aid and falls when aid ends (Madsen 2012)" | **MISATTRIBUTED** | HANDOFF.md l.255: Madsen "反對「救濟停止就流失」的物質解釋". audit_designs.md #2 says the same. The row's own evidence cell then says "not materialism", so the row contradicts itself. | Attribute the rival claim generically, or to provision theories (Stark 1996; Ager and Ciccone 2018), and keep Madsen as the test case: "Catholic affiliation grew with US relief; Madsen attributes the post-1960s decline to lost dependence and paternal authority, not to aid ending." |
| 1.2 | Same row: "Taiwan's 'flour religion' claim has no scholarly source" | **INCONSISTENT** with section 9 | 09_chinese.md l.81 cites Madsen 2012, p. 62: missionaries worried about "flour Christians" (麵粉基督徒), and some families were baptized to secure relief (chinese_language_scholarship.md l.228 [verified: PDF]). Section 7's "no source" covers only the generic Protestant 麵粉教 claim. | "The generic 'flour religion' (麵粉教) claim is unsourced; Madsen (2012, 62) documents Catholic missionaries' worry about 'flour Christians', while rejecting a materialist account of decline." Align 07 l.37/l.113 the same way. |
| 1.3 | §15.2: Korea coded C; "Korea shows that an outside perpetrator does not guarantee outcome A" | Supported by sections 6 (l.29) and 10 (l.27), but **INCONSISTENT** with the 06 opening | 06_comparative.md l.3 lists "Koreans under Japan" among cases where "faith and the sufferers' own church rose together" (= A) | Fix section 6's opening sentence to drop Korea, or say "Koreans under Japan (split: resisters' bodies rose, the compliant establishment lost them)". Also note that section 10 calls the same case "pattern B" (l.120) under the older lettering, where B = "faith migrates". In the synthesis that outcome is C. Use one lettering throughout. |
| 1.4 | §15.1 Demand step: "Prayer searches … faded in most regions by about October (Bentzen 2021)" | **OVERSTATED (minor)** | Corrected section 16 l.93 and fulltext_corrections_log l.35: "faded by about October 2020 **except in Europe and the Americas**" | Use section 16's wording. |
| 1.5 | §15.1 condition 6 / outcome B: Cohn 1992, 1363 turning point, given with no tag | **INCONSISTENT** tagging | 20_gaps_journals.md gap 6 and "To verify" mark the same claim *[verify at first hand]*. 04 l.37 states it untagged. | Either clear the tag in 20 or add it in 15. The claim matches Cohn's standard argument (six Tuscan and Umbrian cities; 1363), so clearing the tag after a first-hand read is fine. |
| 1.6 | §15.1 condition 1: "Weber 1946 *[verify]*" | Tag can be cleared | 19_novelty.md l.9 already cites "Weber 1946, 267–301". "The Social Psychology of the World Religions" in Gerth and Mills occupies pp. 267–301. | Cite as Weber 1946, 267–301 and drop the tag (also in 20 and 20_refs). |
| 1.7 | §15.4 deliverance row: "26 of 51 narratives report Black-led worship before" | OK, caveat missing | 05 l.71–80: 9 of the 51 are targeted draws that over-represent secret worship; the systematic sample gives 19 of 42 | Add "(19 of 42 in the systematic draw)". The same applies to §15.3, "31 and 26 of 51". |
| 1.8 | Case table, PCT "partial F (1990)" | OK | 16_contemporary.md l.82: the 1990 apology says "the church as a whole did not give the victims' families the support they deserved" | — |
| 1.9 | PCT "1955–65 growth campaign predates its political turn" | OK (matches corrected 07 l.21; audit_designs #1) | — | — |
| 1.10 | Rwanda row (C; partial D; Pentecostal; Islam) | OK against 07 l.45–49 | Pentecostal growth; Islam stream small (about 2% in 2022) and partly protective | Optional: "partial D (small; c. 2% Muslim in 2022)". |
| 1.11 | Belloc, Fountain, Bianchi | Not used in 15 / consistent | 15 does not cite Belloc or Bianchi. Fountain's use ("formal commitment followed freedom") matches 05 l.96 and audit_06_19 #50 (fewer than 40% of datable conversions before freedom). | — |
| 1.12 | Dittmar and Meisenzahl: "changed German church law only once an organised Protestant alternative existed" | OK | Matches corrected 04 l.95–97 (quote at p. 983; ordinances, not exit) | — |
| 1.13 | Jacobs 1861 ch. XIII, "God has hid himself from me" | OK | Gutenberg #11030, ch. "XIII. The Church and Slavery", l.2793 | — |
| 1.14 | Larkin 2014 (parish missions 1825–46); Miller 1975; Kim Sung-Gun 1989; Schwartz 1982 (orders as slaveholders); Ralph's mandate (Wilkins 2:745–46); li Muisis (Lemaître 258); Tournai bells (Lemaître 255); *Christian Recorder* 13 Mar. 1869; Pew 2025b (69% no impact); Hout and Fischer | OK | audit_06_19 rows 5, 28; audit_04_05_08 #1 fix; fulltext_corrections_log; 10_primary_sources l.41; 16 l.93 | — |
| 1.15 | Counts: "Seven conditions", "Six outcomes plus a minor branch", "Five indicators", "Six rivals" | OK | Lists in the file match | — |

## Target 2: 20_gaps_journals.md and 20_gaps_journals_refs.md

Tier data compared with journal_rankings.md: all 16 rows match (JUFO, NO, SJR, WoS, THCI/TSSCI). I re-queried JUFO levels myself through jufo-rest.csc.fi for 12 journals, and all match: CSSH 3/NO1, Church History 2/NO2, History Compass 1/NO1, JRH 2/NO1, IBMR (old title) 1, SWC 1/NO1, JAS 3/NO2, SSH 2/NO1, JSSR 3/NO2, SocRel 3/NO2, P&P 3/NO2, RRR 3/NO2. RRCS has no record (ISSN 2214-3947), which also matches.

| # | Item | Status | Evidence | Correction |
|---|---|---|---|---|
| 2.1 | CSSH: JIF 1.4; ≤14,000 including abstract, notes and bibliography; gold OA, APC £2,610 | OK | cambridge.org CSSH journal-metrics (2-yr IF 1.4; "ranked 14th in History"); preparing-your-materials ("fourteen thousand words or less … including notes and bibliography and abstract"); fees-and-pricing ("GBP (£) 2610 USD ($) 3655") | — |
| 2.2 | SSH ≤12,000 including footnotes and references | OK | cambridge.org SSH preparing-your-materials: "main text no longer than 12,000 words (inclusive of footnotes and references)" | — |
| 2.3 | CSSH, SSH, Church History: "Allowed with disclosure" | OK | Identical "Use of Artificial Intelligence (AI) Tools" section on all three Cambridge pages (opened) | — |
| 2.4 | *Past & Present*: banned; ≤12,000 including footnotes | OK | academic.oup.com/past/pages/General_Instructions (WebFetch): "We will not consider articles which contain AI-generated text or argument"; "should not exceed 12,000 words including footnotes" | — |
| 2.5 | IBMR: 4,000–7,000 including endnotes; Chicago 17th, endnotes only; no AI text | OK | omsc.ptsem.edu/ibmr/guidelines-writers/: "typically 4,000–7,000 words in length, including endnotes"; "Chicago Manual of Style (17th Edition), supplemented by … SBL"; no AI mention | Optional: add "+ SBL style" and "typically". |
| 2.6 | History Compass, JRH, JSSR: "Allowed with disclosure (Wiley, July 2026)" | OK at publisher level | authors.wiley.com/ethics-guidelines: "Last updated: July 2026", wording verified | — |
| 2.7 | JAS (Duke UP): banned, "work substantially written by generative AI" | OK | dukeupress.edu ethics statement, wording verified | — |
| 2.8 | RRCS: "**Banned**: Brill does 'not accept papers … generated by' AI" | **INCONSISTENT / OVERSTATED** | journal_ai_policies.md rates RRCS "**Risk**", with "generated" undefined and revised AI-assisted drafting not expressly banned. 20's own To-verify list asks "whether Brill treats an author-revised AI draft as 'generated by' AI". Quote verified at degruyterbrill.com ("As of September 2026") and brill.com/page/ethics_aipolicy. | "High risk: Brill does 'not accept papers … generated by' AI (term undefined)". Version (a) only remains the right advice. |
| 2.9 | 《臺灣史研究》: "Academia Sinica guideline (January 2026)" | Minor | The PDF's CreationDate is 2026-01-16. journal_ai_policies.md notes that a search dated its issue to December 2025. Disclosure wording verified ("研究過程中如實質性地使用生成式AI之協助…均應依照學術慣例予以揭露"). | "(PDF dated January 2026)". |
| 2.10 | Gap 2: split measured "for one contemporary war, in survey data (Ishchuk 2026)"; table: "trust in God and trust in the Church diverge and trust is 'redistributed'" | **OVERSTATED** | OpenAlex abstract (doi 10.55221/2693-2229.2782; OPRE 46(4) confirmed on Crossref). The God/Church distinction is **conceptual** ("belong to different levels of religious experience"). KIIS/Razumkov survey data measure trust in the Church against other institutions, and the redistribution goes **to the Armed Forces and volunteer networks**, not to other religious bodies. The abstract also says the war "does not destroy institutional trust in the Church". | "for one contemporary war, Ishchuk (2026) distinguishes trust in God from trust in the Church conceptually and uses survey data to show trust redistributed from the Church to the army and volunteer networks (abstract only)". |
| 2.11 | Gap 3 / table: Belloc wording | OK | Matches the corrected wording in fulltext_corrections_log, "Belloc consistency pass" | — |
| 2.12 | Gap 6: Fountain "most datable conversions after emancipation"; 26 of 51 | OK; same caveat as 1.7 | — | Add "(19 of 42 systematic)". |
| 2.13 | Refs: Chaves 1994 "[end page: verify]" | Can be cleared | Crossref first page 749; the article runs 749–74 | Drop the tag. |
| 2.14 | Refs: Ishchuk, Stearns, Slater and Ziblatt, Dittmar and Meisenzahl | OK | Crossref: OPRE 46(4) 2026; History Compass 7(5): 1363–75; CPS 46(10): 1301–27; RES (online 2019; 87(2) 2020) | — |
| 2.15 | Refs: Weber 1946 "[chapter page range: verify]" | Can be cleared | See 1.6: pp. 267–301 | Add 267–301. |
| 2.16 | §20.3 intro: "Every first-choice venue now allows AI-drafted text" | OK for the English first choices | The Chinese companions are "Unclear", as the table says | — |

## Target 3: conferences_timeline.md

| # | Conference | Status | Evidence URL | Correction |
|---|---|---|---|---|
| 3.1 | ASCH 2027: 7–10 Jan, Omni Royal Orleans; early bird ends 1 Dec | OK | churchhistory.org/annualmeeting/annual-meeting-2027 | — |
| 3.2 | AHA 2027: 7–10 Jan, New Orleans | OK | historians.org/event/2027-aha-annual-meeting/ (WebFetch) | — |
| 3.3 | ASCH 2028 Seattle 6–9 Jan; 2029 New York 4–7 Jan | OK | churchhistory.org/annualmeeting/future-conferences | — |
| 3.4 | SSSR 2027: Baltimore, Renaissance Harborplace, 8–10 Oct; 2026 call 1 Feb–31 Mar, in person only | OK | sssreligion.org upcoming-meetings; call-for-papers | — |
| 3.5 | ASA 2027: 6–10 Aug, Chicago; call 2 Nov 2026–25 Feb 2027 | OK | asanet.org 2027 overview ("Last Updated: November 2, 2026") | — |
| 3.6 | ASR "88th" 2027 | UNVERIFIED (plausible) | sociologyofreligion.com failed (TLS name mismatch). A search snippet says 2026 = 87th (New York, 8–10 Aug), so 2027 = 88th is consistent. | Keep [not confirmed]. |
| 3.7 | AAR 2027: Washington DC, 20–23 Nov | OK | aarweb.org future-dates | — |
| 3.8 | AAR online June 2027: 21–24 Jun | **UNVERIFIED / likely ERROR** | See T4 | Mark as not announced. |
| 3.9 | IMC Leeds 2027: 5–8 Jul, hybrid, "Communities"; papers 31 Aug, sessions 30 Sep 2026 | OK | imc.leeds.ac.uk/imc-2027/ | — |
| 3.10 | IMC 2028 page "404" | UNVERIFIED | Proxy 502 on imc.leeds.ac.uk/imc-2028/ (could not reproduce the 404) | — |
| 3.11 | ICMS 2027: 13–15 May, hybrid; deadline 15 Sep passed | OK | wmich.edu/medievalcongress/call ("has now passed") | — |
| 3.12 | SSHA 2026: 51st, Atlanta Hilton, 19–22 Nov 2026; extended to 1 Apr 2026 | OK | ssha.org/conference/call-for-papers/ | — |
| 3.13 | Yale-Edinburgh 2027: 3–5 Jun, Kenya, St Paul's University, Limuru; theme; "call … will be announced later" | OK | yale-edinburgh.yale.edu. The CSWC page was unreachable (DNS outside the allowed network). | — |
| 3.14 | 台灣宗教學會 2026 | **STALE** | See T3 | 30–31 Oct 2026. |
| 3.15 | 台灣宗教學會 2025: 17–18 Oct, 唯心聖教台中道場 | OK | …/年會研討會/歷屆研討會 | — |
| 3.16 | 臺灣社會學會 2026: 21–22 Nov, 東吳外雙溪; abstract 15 Jul; decision 15 Aug; full paper 15 Oct; members only | OK | tsameetings.org.tw (home) and page.php?menu_id=77 | — |
| 3.17 | TSA full paper "≥6,000 字, or ≥3,500 words in English"; "English sessions added in 2026" | **PARTLY UNVERIFIED** | menu_id=77 gives "6000-15000字". No English-session or 3,500-word text was found on that page. | "6,000–15,000 字" (state the cap). Mark the English-session claim *[not confirmed]* unless the source page is cited. |
| 3.18 | EASSSR 9th: 12–14 Jul 2027, Kyung Hee; abstract by 28 Feb 2027; acceptance by 1 Apr; theme | OK | easssr.org …/the-9th-annual-conference… | — |
| 3.19 | ISSR 39th: 15–20 Feb 2027, Buenos Aires; papers extended to 25 Jun 2026; registration 8 Nov 2026 | OK | conference-system.sisr-issr.org | — |
| 3.20 | §(c) checklist: "No AI policy was found on the *Sociology of Religion* or *IBMR* pages. Wiley (…) … unconfirmed." | **STALE / INCONSISTENT** | journal_ai_policies.md and 20 §20.3 confirm Wiley's publisher policy (July 2026) for History Compass, JRH and JSSR. Sage's policy applies to IBMR and OUP's journal-level policy to SocRel. | "Wiley (publisher policy, July 2026): allowed with disclosure. IBMR: Sage policy. SocRel: OUP policy, disclosure in the cover letter and the manuscript." |

## Target 4: journal_ai_policies.md (pages opened: 11)

| # | Policy page | Status | Evidence | Note |
|---|---|---|---|---|
| 4.1 | CUP publisher, "AI Contributions to Research Content" (5 quotes) | OK, verbatim | cambridge.org …/authorship-and-contributorship | Two quotes differ only by link spacing |
| 4.2 | CSSH/SSH/Church History identical section (6 quotes checked) | OK, verbatim | cambridge.org preparing-your-materials (CSSH, SSH, CH) | — |
| 4.3 | Wiley ethics guidelines, "Last updated: July 2026" (6 quotes) | OK, verbatim, date confirmed | authors.wiley.com/ethics-guidelines/index.html | — |
| 4.4 | Wiley AI guidelines (6 quotes, including literature summarisation not requiring disclosure) | OK, verbatim | wiley.com/en-gb/publish/article/ai-guidelines/ | — |
| 4.5 | Taylor & Francis AI policy (5 quotes) | OK, verbatim | taylorandfrancis.com/our-policies/ai-policy/ | — |
| 4.6 | Sage AI policy (7 quotes, including "Analysis of experiences and themes") | OK, verbatim | sagepub.com/en-us/nam/artificial-intelligence-policy | — |
| 4.7 | De Gruyter Brill, "As of September 2026" (5 quotes) | OK, verbatim, date confirmed | degruyterbrill.com …/artificial-intelligence | — |
| 4.8 | brill.com/page/ethics_aipolicy (3 quotes, stricter image rule) | OK, verbatim; no date on the page (© 2016–2026) | brill.com/page/ethics_aipolicy | — |
| 4.9 | Duke UP ethics statement (3 quotes) | OK, verbatim | dukeupress.edu …/ethics-statement-for-journals | — |
| 4.10 | *Past & Present* item on AI | OK (WebFetch, segmented) | academic.oup.com/past/pages/General_Instructions | curl gives 403. The fragments match. |
| 4.11 | IBMR writers' guidelines: "no AI mention" | OK | omsc.ptsem.edu/ibmr/guidelines-writers/ | — |
| 4.12 | Academia Sinica guideline PDF, created 2026-01-16; quotes | OK | pdfinfo CreationDate 2026-01-16; disclosure sentence found | — |
| 4.13 | MDPI, COPE, OUP journal ethics | UNVERIFIED this round | 403 to curl and WebFetch | The file already notes these were reached only through a reader. No contradiction found. |

No misquotation was found in the policy file.

## Target 5: seminary_application.md (admissions and faculty pages opened: 26)

| # | Item | Status | Evidence | Correction |
|---|---|---|---|---|
| 5.1 | 政大 exam registration 2026/11/24–12/8 | OK, incomplete | See T1 | Add the noon cutoff, the 2/1 exam and the 3/2 upload deadline |
| 5.2 | 政大 甄試: 9/29–10/13, interview 11/9, quota 4 (1151); 歷史系 AI question verbatim; "已出版之正式學術論文" | OK | 116碩博甄簡章.pdf (lines 13–55, 1101–1117, 1317–1349) | — |
| 5.3 | 政大 exam: quota 3, 專業英文 12% + 宗教傳統與理論 38%, up to 10 interviewed, interview 116/3/8; 新住民組 1 extra place, review only, 2 letters | OK | 116碩班簡章.pdf p. 29, p. 110 | — |
| 5.4 | Yale MAR: IELTS only, 7.0 in each band, "Scores from the TOEFL are not accepted"; 5-page sample; 2-page statement; $50/$75; 3 letters on academic potential; no AI text | OK | divinity.yale.edu/admissions-aid/how-to-apply | — |
| 5.5 | Cambridge AI wording (3 quotes) | OK, verbatim | postgraduate.study.cam.ac.uk/apply/how/ai-postgraduate-applications. No date on the page. | — |
| 5.6 | Cambridge MPhil: High II.i; 67% or GPA 3.7 "in relevant subjects"; IELTS 7.5 (7.0 each), TOEFL 110 (25 each); proposal of about 500 words; ≤6,000 words of written work; dates 9/9, 12/8, 10/14, 4/28 | OK | …/dvdvmpmtr, /requirements, /apply | — |
| 5.7 | Harvard GSAS AI quote; Religion PhD: ≤20-page sample; SOP ≤1,000 words; GRE not accepted; TOEFL 5 (105 before), speaking 4.5 (23); IELTS 7.5 (speaking 6.5); master's "not required"; 12/1 17:00 | OK | gsas.harvard.edu/apply/applying-degree-programs; /program/religion | The "personal statement ≤500 words" limit was not checked |
| 5.8 | UChicago: 1,500 words; 15–25 pages; TOEFL 104 (26 each), IELTS 7 (7 each); PhD 2027/1/5 | OK | divinity.uchicago.edu/admissions/admissions-info | — |
| 5.9 | UChicago MA round 2, "2027/4/2" | **ERROR** | Same page: **April 5, 2027** | See T2 |
| 5.10 | Duke: TOEFL 93/23 (MTS), 108/27 (ThM); IELTS 6.5 and 7.5; 4–8 pages; 1/15 international final; $60 | OK | divinity.duke.edu/admissions/how-apply | — |
| 5.11 | PTS PhD: 12/1/2026; 700–1,000-word sketch; one modern language; international TOEFL 100 (25 each), IELTS 7.0, Duolingo 130 | OK | ptsem.edu phd-studies; international-students | — |
| 5.12 | Emory GDR: 12/1; about 20 pages; SOP about 4 pages; GRE optional (code 5187) | OK | gdr.emory.edu/admissions/index.html | — |
| 5.13 | CUHK MPhil-PhD: Main Round 2026/12/1; Clearing 2027/3/31; English or Chinese paper | OK | gs.cuhk.edu.hk …/mphil-phd-religious-studies | — |
| 5.14 | Edinburgh World Christianity PhD: 2:1, US GPA 3.25 plus relevant master's at ≥67%; 3,000–5,000-word sample; IELTS 7.0/6.0; TOEFL 100/20 and 5.0/4.0; 13 Sep / 30 Aug 2027; no fee; supervisors Chow, Wild-Wood, Feitoza, Murray; "details of any published work" | OK | study.ed.ac.uk …/68-world-christianity | Note that Wild-Wood is listed as Programme Director |
| 5.15 | Faculty: Starr (Acting Senior Associate Dean; Professor of Asian Christianity and Theology); Jennings (Mellon Professor…); Evans (Associate Professor of American Religions; *A Theology of Brotherhood*, 2024); Cooper (Associate Professor of Religion and Society and Black Church Studies); Barreto (Associate Professor of World Christianity); Adogame (Maxwell M. Upson Professor); Kennedy (Assistant Professor of the History of Medieval Christianity; health, medicine, aging, disability); Guest (Professor in the Sociology of Religion); Lai Pan-chiu (Professor); Chow (Senior Lecturer; Co-director CSWC; Co-editor *SWC*); 鄭仰恩 (page titled 研究員); Forrest (Oriel: "Emeritus Fellow (2023)") | OK, all 12 | URLs as listed in §4 of the file | — |

## Counts

| Target | Items checked | OK | Error | Stale | Inconsistent | Overstated or misattributed | Unverified |
|---|---|---|---|---|---|---|---|
| 1 Synthesis | 15 | 9 | 0 | 0 | 3 (1.2, 1.3, 1.5) | 2 (1.1, 1.4) | 0 (1.6, 1.7 are tag and caveat fixes) |
| 2 Gaps / journals (+ refs) | 16 (+12 JUFO re-queries) | 13 | 0 | 0 | 1 (2.8) | 1 (2.10) | 0 (2.9 minor) |
| 3 Conferences | 20 | 14 | 0 | 2 (3.14, 3.20) | (3.20 also) | 0 | 4 (3.6, 3.8, 3.10, 3.17) |
| 4 AI policies | 13 pages | 12 | 0 | 0 | 0 | 0 | 1 (MDPI, COPE, OUP blocked) |
| 5 Seminary | 15 groups (26 pages) | 14 | 1 (Chicago 4/5) | 0 | 0 | 0 | 0 (T1 incomplete) |

## Fixes applied (seminary/timeline/plan)

| Item | Action | File changed | Doc changed (yes/no) |
|---|---|---|---|
| T1 / 5.1 | 政大宗教所 考試入學: added 繳費帳號 cutoff 2026/12/8 12:00 noon (data entry to 15:00; fee NT$1,300), written exam 2027/2/1, interview-document upload deadline 2027/3/2 17:00, interview 2027/3/8 10:00, quota 3; clarified that the 12/8 17:00 upload applies to 新住民組 1159 / the generic schedule; cited 116碩班簡章.pdf URL. Mirrored in §5.1 and §5.4 (new 2027/2–3 row) | research_notes/Collective suffering and Christian faith/seminary_application.md | no (not in the doc) |
| T2 / 5.9 | UChicago MA round 2: 2027/4/2 → 2027/4/5 (final for international applicants), with source quote | seminary_application.md §2.7 | no |
| 5.14 (note) | Wild-Wood marked as Programme Director | seminary_application.md §2.8 | no |
| T3 / 3.14 | 台灣宗教學會 2026: postponed by Typhoon 薔琵 to 30–31 Oct 2026, 輔仁大學濟時樓 9F (originally 23–24 Oct) | reports/design/conferences_timeline.md | yes (PLAN doc) |
| T4 / 3.8 | AAR "online June sessions 21–24 Jun 2027" removed → "2027 online June sessions: dates not announced *[not confirmed]*" (page lists only 2026 June 23–25); recommended set reworded "if announced" | conferences_timeline.md | yes |
| 3.17 | TSA full paper → 6,000–15,000 字; removed unconfirmed 3,500-word English length and "English sessions added in 2026" | conferences_timeline.md | yes |
| 3.20 | Checklist: Wiley confirmed (publisher guidelines last updated July 2026; disclosure in Acknowledgments/Methods); IBMR → Sage policy; SocRel → OUP policy (cover letter + manuscript) | conferences_timeline.md | yes |
| 2.8 (PLAN AI-use table) | RRCS was already "High risk", not "Banned"; added "(\"generated by AI\" undefined)" | — | yes |
| Not fixed (out of scope) | reports/design/article_1.md l.93 and its PLAN-doc paragraph still say the Wiley journals' AI policies are "unconfirmed" — stale per 2.6/3.20 | — | no |
