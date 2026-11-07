# Final assembly log

Doc: 45d1c62d-42ea-45fe-b97c-8362d45232bc (https://claude.ai/artifact/9d44o3yGKzh75XrxRxcArw), main tab body fb0e3d80-fa34.
Started 2026-11-05. Starting doc rev: 253.

## Step 1: citation-key fixes

### Section files (reports/sections/*.md)
Applied with scratchpad script keyfix.py (old -> new, count):
- 10ol: Joseph ha-Kohen 1981 -> Almbladh 1981 (2)
- 12: Dyson 1998 -> Augustine of Hippo 1998 (2); Watson and Jenkins 2006 -> Julian of Norwich (2006)/Julian of Norwich 2006 (2); Dols 1974 -> 1974b (4); Thornton 1998 -> 1998b (2); Raynaldus 1872 -> 1880 (1)
- 07: Foreign Policy 2014 -> Caryl 2014 (2); Christianity Today 2011 -> Newhouse 2011 (2); Stern 1982 -> 1982b (2); van 't Spijker n.d. -> 2004 (1)
- 09: Chiu Yun-fang 2014 -> 2013 (1); (Chen 2003) -> (Chen Nan-jou 2003 *[unverified]*); (Lo 2018) -> (Lo Kuang-hsi 2018 *[unverified]*)
- 06: CIASE 2021 -> 2021a (2); Pew Research Center 2021 -> 2021c (2). Kim and Kim 2014 already correct in file.
- 16c: CIASE 2021 -> 2021b (1)
- 03: CTC-CCA 1983 -> 1981 (2); Jones 1973 -> Jones [1973] 1998 (3); Kitamori 1965 -> 1946 (2); Raboteau 2004 -> Raboteau [1978] 2004 (2); Raynaldus 1872 -> 1880 (1)
- 04: Dols 1974 -> 1974a (2); Raynaldus 1872 -> 1880 (7); Nodl 2021 [verify] -> Nodl 2021 (identified, see below)
- 10ol: Dols 1974 -> 1974b (2); Stern 1982 -> 1982a (2)
- 10ps: Dols 1974 -> 1974b (2); Simonsohn 1988 -> 1988–91 (2)
- 05: Reis [1991] 2003 -> Reis 1991; Reis [1986] 1993 -> Reis 1986; Soares [2000] 2011 -> Soares 2000
- 11 (methodology): Reis 2003 -> 1991 (2); Reis 1993 -> 1986; Soares 2011 -> 2000 (2); Weber 1946 -> 1946b
- 08: Runge 1969 -> Runge 1900; Soares ([2000] 2011) -> Soares (2000)
- 15: Raynaldus -> 1880; Reis -> 1991; Stern -> 1982b (Taki Onqoy, follows sec. 07); Weber 1946 -> 1946b
- 02: Weber 1946 -> 1946a (5); 19: Weber 1946 -> 1946b (3); 20: Weber 1946 -> 1946b (3)
- Boone 2013 and Kim and Kim 2014 were already correct in the files.
- PCT and CTC-CCA kept as in-text abbreviations (defined in the text); "See" cross-references added to references_master.md: "CTC-CCA. See Commission on Theological Concerns…" and "PCT. See Presbyterian Church in Taiwan."

### Nodl 2021: identified
Crossref (query author Nodl, plague Bohemia): Nodl, Martin. 2021. "Impacts of the Plague Epidemic on the Kingdom of Bohemia in the Second Half of the XIVth Century and at the Beginning of the XVth Century." Studia Historica Gedanensia 12 (2): 44–62. https://doi.org/10.4467/23916001HG.21.004.14986. Its abstract states that Czech debate concluded plague was not a significant or decisive cause of the Hussite revolution, which is exactly the claim cited in sec. 04. Citation kept, [verify] removed; master and 04 refs entry replaced; master counts now 959 verified / 111 detail pending / 2 unverified.

### Live doc (main tab)
Same changes applied in the doc (rev 253 -> 307), by find/replace ("as":"text") or by character range where the old key is a prefix of the new one (Weber 1946a/b, CIASE 2021a/b, Dols 1974a/b, Stern 1982a/b, Thornton 1998b), so formatting is untouched. Counts in the doc matched the files: Raynaldus 10, Weber 13 (5 a + 8 b), CIASE 3, bare Dols 1974 6, Stern 1982 4 (+ "Stern (1982)" 1), Thornton 1998 1.
- "[unverified]" after Chen Nan-jou 2003 and Lo Kuang-hsi 2018 inserted in italics.
- Nodl 2021: "[verify]" removed in text; its to-verify bullet now says resolved (Studia Historica Gedanensia 12 (2): 44–62).
- Checked afterwards (0 hits): "Kim and Kim 2015", "Boone n.d", "Jones 1973", "2004, 2014"; the only "1872" left is a date range in a table (US South, 1865–1872).

## Step 2: renumbering (doc rev 307 -> 385)
Level-2 headings in current document order, old -> new number (mapped by TITLE):

| Doc order | Title | Old | New | Section file |
|---|---|---|---|---|
| 1 | Introduction and research question | 1 | 1 | (doc only) |
| 2 | Theoretical frameworks | 2 | 2 | 02_theory |
| 3 | Christian theologies of suffering | 3 | 3 | 03_theologies |
| 4 | Case 1: The Black Death | 4 | 4 | 04_black_death |
| 5 | Case 2: Enslaved and freed African Americans | 5 | 5 | 05_slave_religion |
| 6 | Comparative cases | 6 | 6 | 06_comparative |
| 7 | Expanded cases | 7 | 7 | 07_global_cases |
| 8 | Continental European scholarship | 8 | 8 | 08_continental |
| 9 | Chinese-language scholarship | 9 | 9 | 09_chinese |
| 10 | Scholarship and sources in further languages | 10 | 10 | 10_other_languages |
| 11 | Guide to primary sources | 10 | 11 | 10_primary_sources |
| 12 | Rare datasets and specialized archives | 11 | 12 | 11_rare_datasets |
| 13 | Sources in ancient and historical languages | 12 | 13 | 12_ancient_languages |
| 14 | Methodological debates | 11 | 14 | 11_methodology |
| 15 | Synthesis | 15 | 15 | 15_synthesis |
| 16 | Biblical-theological reflection | 16 | 16 | 16_biblical |
| 17 | Implications for the contemporary church | 16 | 17 | 16_contemporary |
| 18 | Novelty check | 19 | 18 | 19_novelty |
| 19 | Research gaps, contribution and journal fit | 20 | 19 | 20_gaps_journals |
| 20 | References | (pending) | 20 | references_master.md / References tab |

Subsections renumbered: 12.1–12.11 -> 13.1–13.11; 11.1–11.10 -> 14.1–14.10; 19.1–19.7 -> 18.1–18.7; 20.1–20.4 -> 19.1–19.4. 2.x–4.x, 15.x and 16.x (biblical) unchanged; 17 has no numbered subsections.

Cross-references: the doc was exported to markdown and every "section(s) N", "§N" and "N.M" reference was listed (112 hits). Ambiguous old numbers were resolved by context:
- old "section 10" = Further languages (Korean literature, Hebrew texts) -> 10; = primary sources (Jones and Allen's Narrative; plague-era remedy routes) -> 11
- old "section 11" = Methodology (comparative design, Jews of 1348–51, process tracing, core pair, phase-indexed comparison) -> 14; 11.6/11.7/11.10 -> 14.6/14.7/14.10; "novelty review (section 11)" in sec. 2 -> 18
- old "section 12" (ancient languages) -> 13
- old "section 16" = contemporary church (COVID, abuse, Korea trust, secure societies, Taylor, Voas and Crockett transmission, political alignment, Taiwan survey trust) -> 17. No reference pointed to the biblical section 16.
- old "section 19"/19.x -> 18/18.x; old 20 had no inbound refs.
Changed references (39): see reports/audit/final_assembly_renumber_map.txt (all 77 find/replace pairs, plus "19.1 Verdict -> 18.1 Verdict"); same strings applied to the section .md files (all found once; one needed the markdown form "*Narrative* (section 11)").
Not changed (correct already): refs to sections 2–9, 15, 15.x, 2.x, 3.x, 4.5; "§17", "§50", "ITC 2000, §2.1", "§§31–34" are not cross-references.

## Step 3: tabs (doc rev 386)
- Created tab "References" (file 847f85c5-3bc3, body 602f27a0-cc92) and tab "Verification" (file 0fc38af1-c458, body 7f269564-4fb3); order: main tab a0 ("Tab 1", name untouched), References a1, Verification a2. The server set display.tabsLocation = "left".
- Main tab: pending block "References (Chicago author-date)" replaced by "## 20. References" + a sentence with a mention chip linking to the References tab.
- Verification tab: what was checked, counts (959/111/2/0 after Nodl), 21-row corrections table, unverified works, 111 detail-pending items grouped by new section number, institutional-access search strings (Nodl row dropped as resolved; Raynaldus row reworded for 1880).
- References tab: filled from references_master.md in five parts (A–C, D–H, I–M, N–S, T–Z).
