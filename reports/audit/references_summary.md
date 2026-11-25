# Master bibliography: verification summary

Date: 5 November 2026. Files: `reports/references_master.md` (the bibliography), `reports/audit/references_status.tsv` (one row per work: key, status, evidence, sections citing, detail to verify, notes and in-text key aliases, full entry).

## 1. Scope and method

- **Inputs:** 1315 reference lines in 16 refs files: 02_theory, 03_theologies, 04_black_death, 05_slave_religion, 06_comparative, 07_global_cases, 08_continental, 09_chinese, 10_other_languages, 10_primary_sources, 11_methodology, 12_ancient_languages, 16_biblical, 16_contemporary, 19_novelty, 20_gaps_journals. Section 02_theory arrived during the work and is included. Section 20_gaps_journals (22 entries, all duplicates of works cited elsewhere) is also included. The refs files are read as they stood at 10:16 on 5 November 2026, after the fixer edits to 02, 06 and 19; any later edits are not reflected.
- **De-duplication:** 1315 lines merged into **1072 unique works**. 164 works are cited in two or more sections. Merging used author, year and title similarity, then a manual pass. That pass caught the same work entered under different headings (for example editor vs. author, PCT vs. Presbyterian Church in Taiwan, and romanized vs. Chinese titles) and different editions of one work (original plus translation or reprint).
- **Automated checks:** `refcheck.py` was run on the eight refs files that had no TSV (02, 06, 09, 10_other_languages, 16_biblical, 16_contemporary, 19, 20). All 275 DOIs in the corpus were resolved individually on Crossref or doi.org, and all resolve. A second catalogue pass (Open Library title+author search, then Crossref bibliographic search) covered every entry that lacked catalogue or audit evidence, about 390 queries in all; false matches were removed by hand.
- **Audit reports used:** audit_02_theory, audit_03_07_16, audit_04_05_08, audit_06_19, audit_09_10_11_12, audit_10_other_languages, audit_16_biblical, audit_designs, plus fulltext_corrections_log.
- **Targeted checks:** WebSearch, Google Scholar (3 queries), Internet Archive (metadata and OCR full text), NDL Search, a Hong Kong library OPAC (via search index) and a fetched PDF title page. No email address was sent in any request.
- **Status rules:** **VERIFIED** means the work was matched in a catalogue, by DOI or in an audit, with no open bibliographic flag. **VERIFIED-DETAIL-PENDING** means the work exists but one element (pages, subtitle, edition, ISBN, series number, editor) is unconfirmed. **UNVERIFIED** means existence could not be confirmed. Flags on loci or arguments are not counted as bibliographic details, except the name of Clement VI's bull.

## 2. Counts

| Status | Works |
|---|---|
| VERIFIED | 958 |
| VERIFIED-DETAIL-PENDING | 111 |
| UNVERIFIED | 3 |
| **Total unique works** | **1072** |
| Likely non-existent | **0** |

By section. A work cited in several sections is counted in each of them. "Lines" is the number of entries in that section's refs file before de-duplication.

| Section | Lines | Works | Verified | Detail pending | Unverified |
|---|---|---|---|---|---|
| 02_theory | 105 | 105 | 104 | 1 | 0 |
| 03_theologies | 97 | 97 | 90 | 7 | 0 |
| 04_black_death | 86 | 86 | 81 | 4 | 1 |
| 05_slave_religion | 111 | 111 | 105 | 6 | 0 |
| 06_comparative | 86 | 86 | 84 | 2 | 0 |
| 07_global_cases | 92 | 92 | 87 | 5 | 0 |
| 08_continental | 71 | 71 | 56 | 15 | 0 |
| 09_chinese | 58 | 58 | 37 | 19 | 2 |
| 10_other_languages | 116 | 116 | 114 | 2 | 0 |
| 10_primary_sources | 110 | 110 | 83 | 27 | 0 |
| 11_methodology | 97 | 97 | 89 | 8 | 0 |
| 12_ancient_languages | 102 | 102 | 78 | 24 | 0 |
| 16_biblical | 62 | 62 | 61 | 1 | 0 |
| 16_contemporary | 60 | 60 | 56 | 4 | 0 |
| 19_novelty | 40 | 40 | 36 | 4 | 0 |
| 20_gaps_journals | 22 | 22 | 22 | 0 | 0 |

## 3. Unverified entries

None of these is judged likely non-existent. Each is either attested by a secondary citation or too incompletely described to search.

| Entry key | Cited in | Evidence so far | What is missing |
|---|---|---|---|
| Chen Nan-jou 陳南州 2003 | 09_chinese | section 09 writer's check: verified via reference list in Chiu 2021 | existence: no catalogue record found (WebSearch and Google Scholar, 2026-11-05); attested only as a citation in Chiu Kai-li 2021's reference list Not judged non-existent: the author is a real PCT theologian and the title is cited in a peer-reviewed article. Check the NCL catalogue. |
| Lo Kuang-hsi 羅光喜 2018 | 09_chinese | section 09 writer's check: verified via reference list in Chiu 2021; WebSearch 2026-11-05: listed as 《台灣建國神學》(羅光喜, 2018) among four texts analysed in Chiu Kai-li 2021 (airiti 16820568-202103-…-121-146); Google Scholar 2026-11-05: related article 羅光喜, 〈孕育中的台灣建國神學〉, 《新使者》 2010 | existence as a 2018 book and its publisher: no catalogue record found; only a citation in Chiu 2021 (and a 2010 《新使者》 article with a similar title) Not judged non-existent; may be a monograph or a booklet. Check NCL. |
| Nodl, Martin 2021 | 04_black_death | — | work not identified: the entry gives no title, volume number, editors or pages; no matching Nodl essay in Vorträge und Forschungen found (WebSearch 2026-11-05); title, volume, editors, pages (sec. 04) Incompletely described, not judged non-existent: Martin Nodl (Charles University) publishes on Hussite historiography. Section 04 must supply the title or drop the citation. |

## 4. Likely non-existent entries

**None.** No audit and no check in this pass found a fabricated work. These items looked doubtful at some point and are now resolved:

- **Boone n.d.** (sec. 19; URL returned 404). Found: Kyle Boone, 2013, "A Theodicy of Redemptive Suffering … Philadelphia Yellow Fever Epidemic of 1793," Olivet Nazarene University senior thesis (Digital Commons hist_ugrd/2; full text on CORE). Key becomes **Boone 2013**.
- **Zacharia, G. 2018** (sec. 19). The author is Gregory Zacharia (Macalester History Honors Project 24).
- **Gao Chunchang 2008** (sec. 19). Google Scholar lists 〈大西洋视野中的北美黑奴宗教〉, 《历史研究》 2008, with a PDF on ilas.cssn.cn. Issue and pages are still open.
- **Tiemessen 2005** (sec. 07, "Paper"). Confirmed as a paper at the CPSA annual meeting, London, Ontario, 2–5 June 2005 (PDF title page fetched).
- **van 't Spijker n.d.** (sec. 07). This is "New Christian Communities in Rwanda after the Genocide," IAMS 11th conference, Port Dickson, 2004 (audit_03_07_16). Key becomes **2004**.
- **Quintão 2002 and Reginaldo 2011** were called unfindable in an earlier draft of sec. 10; both exist (audit_10_other_languages) and are in the refs.
- **Li Huacheng 2008** was not found in open indexes (audit_06_19) but is listed verbatim on the author's faculty page (audit_09_10_11_12). Pages are still open.
- ***Religio* 2023** and **Taipei Times 2025** were removed from sec. 07 by the fixer, because the claims they supported were not in them. They are not in the master.

## 5. Conflicts resolved in the merge

| Item | Resolution | Evidence |
|---|---|---|
| Chiu Yun-fang 2013 (sec. 07) vs 2014 (sec. 09) | One book. Use **2013** (新北市：華藝學術出版社, 280 pp., ISBN 9789868961500). The year on the copyright page is still to check because Douban gives 2014-02. | Book review in 《臺灣人類學刊》; audit_03_07_16 B; audit_09 Douban |
| Thompson 1889a/b | **1889a = Murimuth/Avesbury (Rolls Series 93); 1889b = Baker (Clarendon).** Sections 10 and 12 are now consistent. | audit_09_10_11_12 A9 and fixes |
| Aberth 2017 place | **New York**: Bedford/St. Martin's (Macmillan Learning). The 2005 entry's note on the 2nd ed. now also says New York. | OL works/OL19666236W, ISBN 9781319048877; IA record |
| Raynaldus 1864 vs 1872 | Neither year fits the copy cited. The title page of IA `annalesecclesias25barouoft`, whose pages 453–55 and 470–72 are cited, reads **M DCCC LXXX (1880)**, *Ex typis Consociationis Sancti Pauli*, Bar-le-Duc/Paris/Fribourg. IA's 1864 is the series start year. **Cite as Raynaldus 1880** (vol. 25, 1334–1355), unless a different copy dated 1872 was used. | IA OCR of the title page |
| Tseng 2017 ISBN | Both ISBNs belong to this title: 9789865637378 (refs; Douban) and 9789865637446 (2017 修訂版, xx + 369 pp.). Sections 09, 16c and 19 now carry 修訂版 [rev. ed.]; give the ISBN of the copy read. | cms.trccloud.hk/opac/archives/30505; audit_09; audit_06_19 A9 |
| Dols 1974a/1974b | **1974a** = "The Comparative Communal Responses …," *Viator* 5 (sec. 04). **1974b** = Ibn al-Wardī translation, Miles Festschrift 443–55 (secs. 10, 10ps, 12). | Crossref; audit_10_other_languages #22 |
| CTC-CCA 1981 vs 1983 | One work: Singapore 1981, then Orbis/Zed 1983. Sec. 03 cites 1983. Use (1981) 1983 if the Orbis edition was read. | audit_10_other_languages #17 |
| Jones, W. R. 1973 vs (1973) 1998 | The Beacon reissue is **1998**. Sec. 03 cites the 1973 Anchor edition. | OL works/OL2702463W (ISBN 0807010332) |
| Kim and Kim 2015 | **2014** (Crossref 10.1017/CBO9781139048071; OL print 2014) | audit_06_19 A6 |
| Runge 1900 vs 1969 | One entry: Leipzig 1900, reprint Hildesheim: Olms, 1969. Sec. 08 cites the 1969 reprint. | audit_09 B; DNB |
| Kitamori 1946 / 1965 | One entry: Japanese 1946, with the English translation (John Knox 1965; SCM 1966). Sec. 03 cites 1965. | audit_10_other_languages #46 |
| Same work under two headings | Merged: Almbladh 1981 = Joseph ha-Kohen 1981; Dyson 1998 = Augustine 1998; Watson and Jenkins 2006 = Julian of Norwich 2006; PCT 1977 / PCT 1990 = Presbyterian Church in Taiwan 1977 / 1990; the romanized (sec. 07) and Chinese (sec. 09) entries for Cheng Yang-en 2005, Chou Pei-hsin 2015, Fan Chiang Hsiao-han 2019 and Huang Ying-kuei 1991; Simonsohn 1988 = 1988–91; Thornton 1998 = 1998b; Reis and Soares originals merged with their English translations | — |
| Other corrections taken from the audits | Newhouse 2011 (= "Christianity Today 2011"); Caryl 2014 (= "Foreign Policy 2014"); Kairos 1985 publisher; Mooney 1896 pages 641–1136; end pages for the 02_theory journal articles (Chaves, Stark, Stark and Bainbridge, Granqvist, Iannaccone, Glock, Weber 267–301); Bourdieu English translation | audit_02_theory; audit_03_07_16; audit_06_19 |

## 6. In-text keys that change

These citations, as written in the section texts, no longer match the master key. Change them when the bibliography is placed.

| Master key | Currently cited as (section: key) |
|---|---|
| Almbladh, Karin, ed 1981 | 10ol: Joseph ha-Kohen 1981 |
| Augustine of Hippo 1998 | 12: Dyson, R. W., ed. and trans 1998 |
| Caryl, Christian 2014 | 07: Foreign Policy 2014 |
| Chiu Yun-fang 邱韻芳 2013 | 09: Chiu Yun-fang 邱韻芳 2014 |
| CIASE (Commission indépendante sur les abus sexuels dans l'Église) 2021a | 06: CIASE (Commission indépendante sur les abus sexuels dans l'Église) 2021 |
| CIASE (Commission indépendante sur les abus sexuels dans l'Église) 2021b | 16c: CIASE (Commission indépendante sur les abus sexuels dans l'Église) 2021 |
| Commission on Theological Concerns of the Christian Conference of Asia, ed 1981 | 03: Commission on Theological Concerns of the Christian Conference of Asia (CTC-CCA), ed 1983 |
| Dols, Michael W 1974a | 04: Dols, Michael W 1974 |
| Dols, Michael W 1974b | 10ol: Dols, Michael W 1974; 10ps: Dols, Michael W 1974; 12: Dols, Michael W 1974 |
| Jones, William R (1973) 1998 | 03: Jones, William R 1973 |
| Julian of Norwich 2006 | 12: Watson, Nicholas, and Jacqueline Jenkins, eds 2006 |
| Kitamori Kazō 北森嘉蔵 1946 | 03: Kitamori, Kazoh 1965 |
| Newhouse, Catherine 2011 | 07: Christianity Today 2011 |
| Pew Research Center 2021c | 06: Pew Research Center 2021 |
| Presbyterian Church in Taiwan (台灣基督長老教會總會) 1977 | 07: PCT (Presbyterian Church in Taiwan) 1977 |
| Presbyterian Church in Taiwan (台灣基督長老教會總會) 1990 | 16b: PCT (Presbyterian Church in Taiwan; 台灣基督長老教會總會) 1990 |
| Raboteau, Albert J (1978) 2004 | 03: Raboteau, Albert J 2004 |
| Raynaldus, Odoricus 1880 | 03: Raynaldus, Odoricus 1872; 04: Raynaldus, Odoricus 1872; 10ps: Raynaldus, Odoricus 1872; 12: Raynaldus, Odoricus 1872 |
| Reis, João José 1986 | 05: Reis, João José. (1986) 1993; 11: Reis, João José 1993 |
| Reis, João José 1991 | 05: Reis, João José. (1991) 2003; 11: Reis, João José 2003 |
| Runge, Paul, ed 1900 | 08: Runge, Paul, ed 1969 |
| Simonsohn, Shlomo, ed 1988–91 | 10ps: Simonsohn, Shlomo, ed 1988 |
| Soares, Mariza de Carvalho 2000 | 05: Soares, Mariza de Carvalho. (2000) 2011; 11: Soares, Mariza de Carvalho 2011 |
| Stern, Steve J 1982a | 10ol: Stern, Steve J 1982 |
| Stern, Steve J 1982b | 07: Stern, Steve J 1982 |
| Thornton, John K 1998b | 12: Thornton, John K 1998 |
| van 't Spijker, Gerard 2004 | 07: van 't Spijker, Gerard n.d |
| Weber, Max 1946a | 02: Weber, Max 1946 |
| Weber, Max 1946b | 11: Weber, Max 1946; 19: Weber, Max 1946; 20: Weber, Max 1946 |

Letters added by the master because two works by one author share a year: CIASE 2021a (full report, sec. 06) / 2021b (summary, sec. 16c); Stern 1982a (*Allpanchis*, sec. 10) / 1982b (book, sec. 07); Weber 1946a (volume, sec. 02) / 1946b ("Social Psychology" chapter, secs. 11, 19, 20); Pew Research Center 2021c (sec. 06; the 2021a and 2021b letters in sec. 16c are kept); Dols 1974a/b. Section 02 also cites **Nirenberg 1996**, which was missing from 02_theory_refs.md (audit_02_theory #1). It is in the master.

## 7. Details still to verify (VERIFIED-DETAIL-PENDING)

The works exist; only the listed element is open. The full list, with evidence, is in the TSV (`status = VERIFIED-DETAIL-PENDING`).

**02_theory**
- Said, Edward W 1986: end page 106 (standard citation; not independently confirmed per audit_02_theory)

**03_theologies**
- Bonhoeffer, Dietrich 2010: translators (sec. 03)
- Clement VI 1349: the name *Inter sollicitudines* and any translation in Horrox 1994 (sec. 03)
- Ellacuría, Ignacio 1993: pages (sec. 03)
- Greenberg, Irving 1977: pages and quotation (sec. 03)
- Nirmal, Arvind P 1990: chapter pages (sec. 03)
- Wang Hsien-chih 王憲治, ed 1988: publisher (sec. 03); Chinese title, publisher and place (sec. 07)
- Zwingli, Huldrych 1519: critical edition (sec. 03)

**04_black_death**
- Graus, František 1987: series number (sec. 08)
- Harper-Bill, Christopher 1996: chapter title and page range (sec. 04)
- Haverkamp, Alfred 1981: pages via secondary citations (sec. 08)
- Holmes, Thomas Scott, ed 1896: place and publisher (sec. 12)

**05_slave_religion**
- *Appletons' Annual Cyclopaedia and Register of Important Events of the Year 1866* 1867: title, imprint and p. 492 AME figure; known only via secondary aggregator (sec. 05)
- *Appletons' Annual Cyclopaedia and Register of Important Events of the Year 1876* 1877: title, imprint and p. 532 AME figure; known only via secondary aggregator (sec. 05)
- Cameron, Christopher 2019: place (sec. 05)
- Ortiz, Fernando 1921: whether first published in *Revista Bimestre Cubana* (sec. 05)
- Pierce, Yolanda 2005: place (sec. 05)
- Reis, João José 1991: subtitle (sec. 08); subtitle of Portuguese original, *A morte é uma festa*, São Paulo: Companhia das Letras, 1991 (sec. 05)

**06_comparative**
- Kim, Sung-Gun 1989: subtitle: Hull repository 'A Study of Religion and Politics' vs. CRL/Open Library 'A Sociological Study of Religion and Politics'
- Salfeld, Siegmund, ed 1898: series number (sec. 10)

**07_global_cases**
- Blacket, John 1994: subtitle and pages (sec. 07)
- Chiu Yun-fang 邱韻芳 2013: year on copyright page: 2013 (review, audit_03_07_16) vs. 2014-02 (Douban record); publisher (sec. 07); Douban gives 2014; other sources give 2013 (sec. 09)
- Hansen, Peter 2009b: editor and subtitle (sec. 07)
- Worthy News n.d: author and date (page dated 29 March 2000 per audit); single informant

**08_continental**
- Carpentier, Élisabeth 1962a: 1962 series number (sec. 08)
- Colet, Anna, Josep Xavier Muntané i Santiveri, Jordi Ruíz Ventura, and Oriol Saula 2015: editor (sec. 08)
- Fredericq, Paul 1896: date 1896 vs. 1897 and series (sec. 08)
- *La peste nera: Dati di una realtà ed elementi di una interpretazione. Atti del XXX Convegno storico internazionale, Todi, 10–13 ottobre 1993* 1994: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 08)
- Lenders, Maria 1996: subtitle (sec. 08)
- López de Meneses, Amada 1959: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 08)
- Maimon, Arye, Mordechai Breuer, and Yacov Guggenheim, eds 1987–2003: publisher (sec. 08)
- Naso, Irma 1994: page range 349–81 vs. 349–83 (sec. 08)
- Oldendorp, Christian Georg Andreas 2000–2002: full editorial team (sec. 08)
- Toch, Michael 1998: series number (sec. 08)
- Vauchez, André 1981: translator (sec. 08)
- Verger, Pierre 1968: English translation title (sec. 08)

**09_chinese**
- An Derui 安德瑞 2009: venue, pages; author identity (sec. 09)
- Huang Luping 黃路蘋 2021: issue, pages (sec. 09)
- Jing Zhilong 景志龙 2008: issue, pages (sec. 09)
- Lei Yutian 雷雨田 1999: issue, pages (sec. 09)
- Li He 李荷 2004: issue, pages (sec. 09)
- Li Huacheng 李化成 2008: pages; on CNKI: not found in open indexes (sec. 19)
- Long Xiuqing 龙秀清, and Li Jinrong 李锦荣 2012: issue, pages (sec. 09)
- Moltmann, Jürgen (莫爾特曼). 1995 or 1998: year (sec. 09)
- Pinn, Anthony B. (安東尼．平) 2006: title form (為甚麼 in the catalogue vs. 為什麼), publisher, translator 周輝 and ISBN 9628322990 not confirmed (Douban ISBN record is a dead page)
- Snowden, Frank M. (弗兰克·M.斯诺登) 2022: original title not shown on the record (sec. 09)
- Tsai Jung-fang 蔡榮芳 2020: catalogue record (ISBN) not seen; Google Scholar citation record only
- Tseng, Ching-pao (曾慶豹) 2017: edition used: ISBN 9789865637378 (Douban) vs. 9789865637446 (2017 revised edition, xx+369 pp.); give the ISBN of the copy read
- Wang Cheng-wen 王政文 2012: pages (sec. 09)
- Wu Shu-chen 吳淑貞 2023: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 09)
- Zhang Jingjing 张静静 2015: issue, pages (sec. 09)
- Zhao Lixing 赵立行 2005: issue, pages (sec. 09)
- Zheng Xiaoyun 鄭筱筠 2012: issue, pages, and the disaster case studied (sec. 09)

**10_other_languages**
- Sŏ Nam-dong 서남동 and others 1984: editor (sec. 10)

**10_primary_sources**
- Allen, Richard 1833: publisher; URL confirmed only by Wayback record (sec. 10)
- Berlin, Ira, et al., eds 1982–: series volume details (sec. 10)
- Blassingame, John W 1975: end page (sec. 10)
- Boccaccio, Giovanni 1972: place; 2nd ed. 1995 (sec. 10)
- Boccaccio, Giovanni 1992: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Butler, Richard, ed 1849: full title (sec. 10)
- Chiappelli, Alberto, ed 1887: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Dinanah, Taha, ed. and trans 1927: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Duran-Reynals, M. L., and C.-E. A. Winslow, trans 1949: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Eakin, Sue, and Joseph Logsdon, eds 1968: publisher (sec. 10)
- Estes, J. Worth, and Billy G. Smith, eds 1997: subtitle and place (sec. 10)
- Fisk University Social Science Institute 1945: 1945 series details (sec. 10)
- Fredericq, Paul, ed 1889–1906: whether vol. 2 or 3 prints Clement VI's anti-flagellant bull (sec. 10)
- Giuffrida, Antonino, ed 1980: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Higginson, Thomas Wentworth 1867: pages (sec. 10)
- Johnson, Michael P 2001: end page (sec. 10)
- Krüger, Sabine 1972: title and pages (sec. 10)
- Lisini, Alessandro, and Fabio Iacometti, eds 1931–39: end date and series number (sec. 12)
- Marcus, Jacob R 1938: place and publisher of 1938 ed. (sec. 10); place and publisher (sec. 12)
- Porta, Giuseppe, ed 1995: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Randolph, Peter 1855: publisher (sec. 10)
- Rawick, George P., ed 1972: volume counts (sec. 10)
- Rébouis, H. Émile 1888: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)
- Ripley, C. Peter, ed 1985–92: end date (sec. 10)
- Rodolico, Niccolò, ed 1903–55: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10); series number (sec. 12)
- Rossi, Vittorio, and Umberto Bosco, eds 1933–42: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 10)

**11_methodology**
- Bennett, Andrew, and Jeffrey T. Checkel, eds 2015: Crossref lists 2014 online;  print date (sec. 11)
- Fields, Barbara Jeanne 1990: page range (sec. 11)
- Finke, Roger, and Rodney Stark 1986: end page (sec. 11)
- Gorski, Philip S 2000: end page (sec. 11)
- Lieberson, Stanley 1991: end page (sec. 11)
- Sewell, William H., Jr 1967: end page (sec. 11)
- Stoler, Ann Laura 2001: end page (sec. 11)

**12_ancient_languages**
- Anderson, Arthur J. O., and Charles E. Dibble, eds. and trans 1950–82: part count and end date (sec. 12)
- Branca, Vittore, ed. *Decameron*, by Giovanni Boccaccio. [ve ?: which Branca edition (Mondadori 1976 or Einaudi 1980/1992) and year; entry lacks a year; which edition: *Tutte le opere di Giovanni Boccaccio*, vol. 4 (Milan: Mondadori, 1976), or Turin: Einaudi, 1980/1992 (sec. 12)
- Chabot, J.-B., ed 1927–33: original dates (sec. 12)
- Coakley, J. F 2013: edition number (sec. 12)
- Eusebius 1932: first-edition year; Open Library record is of a 1964 printing (sec. 12)
- Harrak, Amir, trans 1999: subtitle (sec. 12)
- Lambdin, Thomas O 1978: series number (sec. 12)
- Michell, Robert, and Nevill Forbes, trans 1914: series number (sec. 12)
- Molina, Cristóbal de 2011: third translator (sec. 12)
- Müller, Marcus Joseph 1863: end page (sec. 12)
- Rosenthal, Franz 2006: edition number (sec. 12)
- Schneider, Elena A 2020: author's first name (sec. 12)
- Schwartz, Eduard, and Theodor Mommsen, eds 1903–09: GCS number and dates (sec. 12)
- Scourfield, J. H. D 1996: end page (sec. 12)
- Simonetti, Manlio, and Claudio Moreschini, eds 1976: imprint details (place, publisher, date) not confirmed in a catalogue (sec. 12)
- van Dieten, Jan Louis, trans 1973: later volumes (sec. 12)
- Witakowski, Witold, trans 1996: series number (sec. 12)
- Ziyāda, Muḥammad Muṣṭafā, ed 1934–73: date range and co-editor Saʿīd ʿĀshūr (sec. 12)

**16_biblical**
- Barmen 1934: edition and English text (sec. 16)

**16_contemporary**
- Fu, Yang-chih (傅仰止), Lin Pen-hsuan (林本炫), Tsai Ming-chang (蔡明璋), Liao Pei-shan (廖培珊), and Hsieh Shu-hui (謝淑惠), eds 2019: Romanizations of editors' names other than Fu (sec. 16)
- Pew Research Center 2006: not opened directly (sec. 16)
- Wu, Chyi-in (吳齊殷), Fu Yang-chih (傅仰止), Tsai Chia-hung (蔡佳泓), and Lin Pen-hsuan (林本炫), eds 2024: Romanizations of editors' names (sec. 16)

**19_novelty**
- Gao Chunchang 高春常 2008: issue number and pages in 《历史研究》 2008
- Winters, Joseph 2020: pages (sec. 19)

## 8. To check with institutional access

Paste the strings exactly as given (quotation marks included where shown). Each item says what to record.

### Airiti Library (華藝線上圖書館) and NCL Taiwan (國家圖書館 / 全國圖書書目資訊網 NBINet)

| Work (master key) | Database | Search string | Record |
|---|---|---|---|
| Chen Nan-jou 2003 (UNVERIFIED) | NCL / NBINet | `陳南州 認同的神學` | existence, publisher (永望文化?), year, ISBN |
| Lo Kuang-hsi 2018 (UNVERIFIED) | NCL / NBINet; Airiti | `羅光喜 台灣建國神學` | book or booklet? publisher (台灣基督長老教會總會?), year; compare 〈孕育中的台灣建國神學〉, 《新使者》 2010 |
| Tsai Jung-fang 2020 | NCL / NBINet | `蔡榮芳 從宗教到政治 黃彰輝` | ISBN, year (玉山社) |
| Wang Hsien-chih 1988 | NCL / NBINet | `台灣鄉土神學論文集` | publisher and place (台南神學院?) |
| Chiu Yun-fang 2013 | Airiti Books; NCL | `邱韻芳 祖靈與上帝` | year on copyright page (2013 vs 2014), ISBN 9789868961500 |
| Tseng Ching-pao 2017 | NCL / NBINet | `曾慶豹 約瑟和他的兄弟們` | edition (初版 vs 修訂版) and ISBN of the copy read (9789865637378 / 9789865637446) |
| Moltmann (Chinese trans.) 1995 or 1998 | NCL; HKU/CUHK | `被釘十字架的上帝 阮煒 道風` | year of the Hong Kong 道風 edition (ISBN 9789627409533) |
| Zheng Xiaoyun 2012 | Airiti | `鄭筱筠 災難現場的宗教應對體系` | 《宗教哲學》 issue and pages; which disaster is studied (Wenchuan, Yushu or 921) |
| An Derui 2009 | Airiti; Google Scholar | `安德瑞 宗教慈善與災害重建 九二一` | venue, pages, author identity |
| Wang Cheng-wen 2012 | Airiti | `王政文 改宗所引起的家庭與人際衝突` | pages in 《臺灣文獻》 63 (4) |
| Huang Luping 2021 | Airiti; ISCS (道風) site | `黃路蘋 苦難與病疾 生存危機` | 《道風》 issue and pages |
| Wu Shu-chen 2023 | Airiti; 台灣神學研究學院 repository | `吳淑貞 八八災後魯凱中會宣教再造` | degree, year, URL |
| Madsen 2012 (content) | Airiti | `Madsen 台灣學誌 2012` | check the "sevenfold within ten years" Catholic figure on p. 62 |
| Huang Po-ho 1991; Song Choan-Seng 1988 (出頭天) | NCL | `黃伯和 出頭天` | imprint for each |

### CNKI (中国知网)

| Work | Search string (title field unless noted) | Record |
|---|---|---|
| Gao Chunchang 2008 | `大西洋视野中的北美黑奴宗教` | 《历史研究》 2008 issue (期) and pages |
| Li Huacheng 2008 | `黑死病期间的英国教会` (author 李化成) | 《安徽史学》 2008 年第 1 期 pages |
| Zhao Lixing 2005 | `西方学者视野中的黑死病` | 《历史研究》 issue and pages |
| Li He 2004 | `灾难中的转变：黑死病对欧洲文化的影响` | 《中国人民大学学报》 issue and pages |
| Long Xiuqing and Li Jinrong 2012 | `论黑死病对英格兰修道院的影响` | 《贵州社会科学》 issue and pages |
| Lei Yutian 1999 | `美国黑人神学的历史渊源` | 《湘潭大学学报（哲学社会科学版）》 issue and pages |
| Jing Zhilong 2008 | `美国黑人灵歌的发展渊源及特征` | 《时代文学》 issue and pages |
| Zhang Jingjing 2015 | `《黑人的灵魂》中的灵歌与种族记忆` | 《北京第二外国语学院学报》 issue and pages |
| Snowden (Chinese trans.) 2022 | `流行病与社会：从黑死病开始的瘟疫史` | that the original is *Epidemics and Society* (2019) |

### JSTOR (end pages and page ranges)

| Work | Search string | Record |
|---|---|---|
| Sewell 1967 | `"Marc Bloch and the Logic of Comparative History"` | pages in *History and Theory* 6 (2) |
| Lieberson 1991 | `"Small N's and Big Conclusions"` | pages in *Social Forces* 70 (2) |
| Finke and Stark 1986 | `"Turning Pews into People"` | pages in *JSSR* 25 |
| Gorski 2000 | `"Historicizing the Secularization Debate"` | pages in *ASR* 65 (1) |
| Stoler 2001 | `"Tense and Tender Ties"` | pages in *JAH* 88 (3) |
| Blassingame 1975 | `"Using the Testimony of Ex-Slaves"` | pages in *JSH* 41 (4), from 473 |
| Johnson 2001 | `"Denmark Vesey and His Co-Conspirators"` | pages in *WMQ* 58 (4), from 915 |
| Said 1986 | `"Michael Walzer's Exodus and Revolution: A Canaanite Reading"` | end page in *Grand Street* 5 (2) (86–106 expected) |
| Scourfield 1996 | `"The De mortalitate of Cyprian: Consolation and Context"` | end page in *Vigiliae Christianae* 50 (1) |
| Fields 1990 | `"Slavery, Race and Ideology in the United States of America"` | pages in *New Left Review* 181 |
| Bennett and Checkel 2015 | `"Process Tracing: From Metaphor to Analytic Tool"` | print year (Crossref online 2014) |
| Winters 2020 | `"Nothing Matters: Black Death, Repetition, and an Ethics of Anguish"` | pages in *American Religion* 2 (1) |
| Greenberg 1977 | `"Cloud of Smoke, Pillar of Fire"` (in Fleischner, *Auschwitz: Beginning of a New Era?*) | chapter pages |
| Higginson 1867 | `"Negro Spirituals" Atlantic Monthly 1867` | pages (685–94 expected) |

### WorldCat (or KVK / HathiTrust for older items)

| Work | Search string | Record |
|---|---|---|
| Raynaldus, vol. 25 | `ti:"Annales ecclesiastici" AND au:Theiner AND "tomus 25"` | which printing (1872 Guérin vs 1880 Consociatio S. Pauli); cite the copy whose pages are used |
| Pinn 2006 (Chinese) | `上帝 為甚麼 黑人 苦難 惡` and ISBN `9628322990` (also HKU/CUHK catalogues) | title form, publisher (道風山?), translator 周輝 |
| Nodl 2021 (UNVERIFIED) | `au:Nodl Martin AND "Vorträge und Forschungen"` | title, volume, editors, pages; or drop the citation |
| Appletons' Annual Cyclopaedia 1866 and 1876 | HathiTrust full text: `"Annual Cyclopaedia" 1866 "African Methodist"` | exact title, imprint, and the AME figures on pp. 492 and 532 |
| Marcus 1938 | `ti:"The Jew in the Medieval World" 1938` | place and publisher of the 1938 edition |
| Holmes 1896 | `ti:"Register of Ralph of Shrewsbury"` | place and publisher (Somerset Record Society 9–10) |
| Fredericq 1896 | `ti:"De secten der geeselaars en der dansers"` | 1896 or 1897; series |
| Fredericq 1889–1906 | `ti:"Corpus documentorum inquisitionis haereticae pravitatis Neerlandicae"` | whether vol. 2 or vol. 3 prints Clement VI's anti-flagellant bull |
| Krüger 1972 | `"De mortalitate in Alamannia" Krüger Heimpel` | title and pages in the Heimpel Festschrift, vol. 2 |
| Lisini and Iacometti 1931–39; Rodolico 1903–55 | `"Cronache senesi" Rerum Italicarum Scriptores`; `"Cronaca fiorentina" Marchionne Stefani` | RIS² volume numbers and dates |
| Ziyāda 1934–73 | `al-Maqrīzī "Kitāb al-sulūk" Ziyāda ʿĀshūr` | date range; co-editor |
| Branca, *Decameron* (sec. 12) | `Boccaccio Decameron Branca` | which edition (Mondadori 1976 or Einaudi 1980/1992) |
| Zwingli 1519 | `Zwingli "Pestlied" Sämtliche Werke` | critical edition (Z I) |
| Clement VI 1349 | Horrox 1994 index; `"Inter sollicitudines" Clement VI` | whether the name *Inter sollicitudines* is attested for the 20 October 1349 bull |

### Dialnet

- López de Meneses 1959: `López de Meneses "Una consecuencia de la peste negra en Cataluña"`. Record: *Sefarad* 19 pages (currently 92–133, 321–65).
- Naso 1994: `Naso "Individuazione diagnostica della peste nera"`. Record: page range (349–81 vs 349–83).
