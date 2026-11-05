# Fact-check audit: sections 6 and 19

Auditor: independent adversarial check, 5 November 2026. Section and refs files were not edited.

Method: all 42 DOIs in the two refs files were resolved on Crossref (api.crossref.org/works/DOI). Abstracts came from Crossref and OpenAlex. Books were checked in Open Library (search and edition records). The Library of Congress JSON endpoint only returns digitised items and gave no hits for these in-copyright books, and Google Books returned HTTP 429, so neither was used. Other sources: Internet Archive metadata, publisher and repository pages (Voltaire Foundation, bepress Digital Commons, Hull repository, De Gruyter), Google Scholar HTML (four queries, 3–4 s apart) and web search. No email address was sent. Section 19's descriptions of the economics studies were compared line by line with `research_notes/.../reading/open_access_studies_fulltext.md`.

Status key: **verified** · **wrong detail** · **misattributed** · **unsupported** · **not found** · **fabricated-likely**.

## A. Problems found (summary)

| # | Sec. | Item | Status | Problem | Correction |
|---|---|---|---|---|---|
| 1 | 19 (§19.2 table; §19.5 no. 4; §19.6) | Belloc, Drago and Galbiati **2016**: "about 60 episcopal-see cities … Religiosity … *not* measured: the channel is inferred, partly from present-day church counts … (2014 draft, 29)" | wrong detail (version mismatch) | The row is headed 2016 (QJE), but every detail comes from the 2014 NBER draft. The published QJE abstract adds an ancillary result that the draft lacks: "seismic events provoked a positive and statistically significant differential effect on the construction and further ornamentation of religious buildings between episcopal and non-episcopal see cities." The religious channel in the published version therefore has a medieval proxy, not only present-day church counts. The reading notes also say the QJE sample differs (121–122 cities). Source: https://doi.org/10.1093/qje/qjw020 (abstract via OpenAlex). | Head the row "Belloc, Drago, and Galbiati 2014 draft (published 2016)", or rewrite it from the QJE version: "…the published version adds a medieval proxy (differential church building and ornamentation after quakes); lay belief and trust are still not measured." Soften §19.6 "each infers its religious channel" for Belloc. |
| 2 | 19 (§19.2; refs) | Zacharia 2018 *[verify]*: "Scholar snippet only; repository returned HTTP 403" | wrong detail (incomplete) + understated overlap | The repository page loads (HTTP 200). The author is **Gregory Zacharia**, Macalester History Honors Projects 24, 2018. The abstract says Chapter One "argues that the Black Death highlighted institutional shortcomings within the Catholic Church as a public health institution, opening the doors for new expressions of religious criticism." That is a direct overlap with the "Church lost trust after 1348" claim, which the section treats as a student-thesis commonplace. https://digitalcommons.macalester.edu/history_honors/24/ | Ref: "Zacharia, Gregory. 2018. … History Honors Projects 24, Macalester College." Remove the [verify]. In §19.2, add: "Ch. 1 argues the Black Death exposed the Church's institutional shortcomings and opened the way to religious criticism (path-dependence framework)." |
| 3 | 19 (§19.2) | Zacharia is "the only cross-catastrophe comparison found that includes the Black Death" | unsupported (incomplete search) | Another undergraduate honours thesis compares the Black Death with a later epidemic: Heather Carmody, "The Black Death of Europe and Cholera in 19th Century London: A Comparative Study," Honors Thesis, Loyola Marymount University, 2012. https://scholars.lmu.edu/en/publications/the-black-death-of-europe-and-cholera-in-19th-century-london-a-co/ (full text: digitalcommons.lmu.edu/honors-thesis/6). Its religious content is unknown. | "…one of at least two undergraduate cross-catastrophe comparisons that include the Black Death (also Carmody 2012, plague vs. London cholera)". Add Carmody to 19.7's follow-ups. |
| 4 | 19 (refs; §19.2; §19.4) | Boone n.d., "[verify: author, title and year; URL returned HTTP 404]" | wrong detail (incomplete; now resolvable) | The search index (Olivet Digital Commons via CORE) gives: Kyle Boone, "A Theodicy of Redemptive Suffering in African American Involvement Led by Absalom Jones and Richard Allen in the Philadelphia Yellow Fever Epidemic of 1793," senior thesis, History, Olivet Nazarene University, April 2013. The repository URL still returns 404 (rechecked), and the CORE record is behind Cloudflare, so this rests on the index entry only. https://core.ac.uk/works/33339470 | "Boone, Kyle. 2013. 'A Theodicy of Redemptive Suffering in African American Involvement Led by Absalom Jones and Richard Allen in the Philadelphia Yellow Fever Epidemic of 1793.' Senior thesis, Olivet Nazarene University." Change "Boone n.d." to "Boone 2013" in text. |
| 5 | 6 (1918/COVID para.) | "most Americans report no lasting change in religious life (Bentzen 2021; section 16)" | unsupported (by the cited source) | Bentzen 2021 measures Google prayer searches. The only US self-report it mentions is Pew's "one in ten … strengthened" (reading notes, §6). The "no change" figure is Pew's: 68% of US adults said their own faith had "not changed much" (survey fielded June–August 2020, released 27 Jan 2021). That is not evidence of *lasting* change either way. https://trentonmonitor.com/news/2021/jan/27/14-nation-survey-shows-us-faith-has-stayed-stronge | "…but in mid-2020 about two-thirds of Americans said their faith had not changed much (Pew Research Center 2021)." Add the Pew entry to the refs. |
| 6 | 6 (Korea para.; table; refs) | Kim, Sebastian C. H., and Kirsteen Kim. **2015**. *A History of Korean Christianity*. CUP | wrong detail (year) | Crossref (10.1017/CBO9781139048071) dates it 24 Nov 2014, and Open Library has the print edition as 2014. Reviews appeared in 2015, which is probably the source of the error. | 2014. Change "Kim and Kim 2015" to "Kim and Kim 2014" in the text and table. |
| 7 | 6 (refs) | Kairos Theologians 1985 … "Braamfontein: Kairos Theologians/Skotaville. Revised 2nd ed., Grand Rapids, MI: Eerdmans, 1986." | wrong detail (minor) | The Sept 1985 first edition was issued by the Kairos Theologians, Braamfontein (printed by Springs Advertiser). Skotaville published the revised 2nd edition (Braamfontein, 1986), co-published by Eerdmans. https://en.wikipedia.org/wiki/Kairos_Document; OL edition https://openlibrary.org/books/OL2458959M | "Braamfontein: Kairos Theologians, 1985. Rev. 2nd ed., Braamfontein: Skotaville; Grand Rapids, MI: Eerdmans, 1986." |
| 8 | 6 (Lisbon para.) | "the Jesuit Gabriel Malagrida, who preached that sin caused the disaster, was later executed (Molesky 2015 *[verify]*)" | verified, but misleading causal implication | The facts are right. *Juízo da verdadeira causa do terremoto* (Lisbon, 1756) blamed divine punishment for sin, and Malagrida was garrotted and burned in the Rossio on 21 Sept 1761. He was not executed for the sermon, though. Pombal had him implicated in the 1758 Távora conspiracy and handed to the Inquisition, which condemned him for heresy over later visionary writings. https://archive.org/details/1756G.MalagridaJuizoDaVerdadeiraCausaDoTerremoto ; https://en.wikipedia.org/wiki/Gabriel_Malagrida | "…Malagrida, whose 1756 pamphlet blamed the disaster on sin, was exiled from court, implicated by Pombal in the 1758 Távora plot and executed by the Inquisition for heresy in 1761." Keep Molesky with a page reference. |
| 9 | 19 (refs) | Tseng 2017 "[verify place and possible 2016 first printing]" | wrong detail (minor) | Library records list the 2017 Tainan, 臺灣教會公報社 printing as a **修訂版** (revised edition), so an earlier first edition exists. https://cms.trccloud.hk/opac/archives/30505 ; review: https://cir.nii.ac.jp/crid/1050848249893638272 | Add "修訂版 [rev. ed.]". Keep the place. Note "first ed. earlier (probably 2016)". |
| 10 | 19 (refs) | Gao Chunchang 2008, venue "[verify]" | verified (venue), issue and pages not found | Google Scholar (rechecked) lists 〈大西洋视野中的北美黑奴宗教〉, 高春常, 《历史研究》, 2008, with a PDF at ilas.cssn.cn (UploadFile/2011817135053482.pdf), which returns 403 from here. Issue and pages are still unconfirmed. | Keep 《历史研究》 2008. The issue number and pages need CNKI. |
| 11 | 19 (refs) | Li Huacheng 2008, 《安徽史学》 no. 1 | not found (open indexes) | Web search and Scholar did not surface this article (Li 2013 in 《历史研究》 *is* confirmed on Scholar). It is probably real but unverified here. | Mark *[verify on CNKI]*. |
| 12 | 19 (§19.2) | Belloc row "Overlap" and §19.6 claim that "the reading notes confirm each infers its religious channel" | wrong detail (minor) | See #1. True of the 2014 draft and of Dittmar–Meisenzahl and Ager–Ciccone. The QJE Belloc version has a measured (indirect) religiosity proxy. | "…none measures lay faith or institutional trust" is still correct; drop "each infers its religious channel" or except Belloc 2016. |

Smaller notes (not counted as errors):
- **Phillips and Killingray 2003.** Routledge and Crossref give the title as *The Spanish Influenza Pandemic of 1918–1919*. The cover and the *Medical History* review use "1918–19", so either form is acceptable.
- **Kim Sung-Gun 1989.** The Hull repository subtitle is "a study of religion and politics". CRL and Open Library have "a sociological study of religion and politics" (https://hull-repository.worktribe.com/output/4210369). Use the repository form or note the variant. Hull and the 1989 date are confirmed.
- **Meier 2016.** The abstract also argues that the short-term demographic consequences "must have been catastrophic". Section 6 could list Meier with the maximalists as well as for the cultural turn.
- **Larkin 2014** is posthumous (Larkin died March 2012). "Larkin himself later traced" is fine, but "in a posthumously published article" would be clearer.
- **Chaney 2013** also reports that deviant floods did *not* raise a proxy for popular religiosity. This is worth adding, because it strengthens the "leaders' power, not lay faith" contrast.

## B. References: section 6 (82 entries)

| Ref | Status | Evidence | Correction |
|---|---|---|---|
| Barović 2026, IJAGS 11(1): 48–71 | verified | https://doi.org/10.51442/ijags.0076 (Crossref; issued 29 Jun 2026) | — |
| Barr 2020, NHR 24(4): 79–97 | verified | https://doi.org/10.1353/nhr.2020.0046 | — |
| Bays 2012, Wiley-Blackwell | verified | Open Library (Chichester, Wiley-Blackwell, 2011/2012) | — |
| Becker 1994 / trans. 1998 | verified | OL: Armand Colin 1994; Berg 1998, "War and Faith: The Religious Imagination in France, 1914–1930", trans. Helen McPhail (https://openlibrary.org/works/OL36035607W) | Remove "[verify translator]" |
| Bentzen 2021, JEBO 192: 541–83 | verified | https://doi.org/10.1016/j.jebo.2021.10.014 | — |
| Bergen 1996, UNC | verified | https://openlibrary.org/works/OL2920996W | — |
| Berkovits 1973, Ktav | verified | Open Library | — |
| Bottan & Perez-Truglia 2015 | verified | https://doi.org/10.1016/j.jpubeco.2015.07.008 | — |
| Braun & Radner 2005 | verified | SVEC 2005:02, Voltaire Foundation: https://voltaire.ox.ac.uk/publication/lisbon-earthquake-1755/ | Remove the [verify] |
| Brenner 1980; Routledge 2017 | verified | OL (Free Press 1980); https://doi.org/10.4324/9781315131979 | — |
| Bristow 2012, OUP | verified | Open Library | — |
| Brown 2009, 2nd ed., Routledge | verified | Open Library (2001; 2009) | — |
| Carmil & Breznitz 1991, JTS 4(3): 393–405 | verified | https://doi.org/10.1002/jts.2490040307 | — |
| CIASE 2021 | verified | Final report, Oct 2021 (also confirmed in audit_03_07_16) | — |
| Cloete & Smit 1984, Eerdmans | verified | https://openlibrary.org/books/OL7877613M | — |
| Cohn 2007, P&P 196: 3–36 | verified | https://doi.org/10.1093/pastj/gtm005 | — |
| Corley 1996a, RSS 24(1): 9–53 | verified | https://doi.org/10.1080/09637499608431724 | — |
| Corley 1996b, RSS 24(4): 289–343 | verified | https://doi.org/10.1080/09637499608431748 | — |
| de Gruchy 1979, Eerdmans | verified | Open Library | — |
| DeMallie 1982, PHR 51(4): 385–405 | verified | https://doi.org/10.2307/3639782 | — |
| de Wet 2022, EC 13(3): 287–315 | verified | https://doi.org/10.1628/ec-2022-0021 | — |
| Dols 1977, Princeton | verified | Open Library | — |
| Dowd 1992, JHU | verified | Open Library (JHU; 1991/1992 printings) | — |
| Einbinder 2018, Penn | verified | https://doi.org/10.9783/9780812295214 | — |
| Elphick 2012, UVA Press | verified (subtitle) | https://openlibrary.org/books/OL25121816M ("Protestant missionaries and the racial politics of South Africa") | Remove "[verify subtitle]" |
| Elphick & Davenport 1997, UC Press | verified | Open Library | — |
| Ericksen & Heschel 1999, Fortress | verified | https://openlibrary.org/books/OL16947295M | — |
| Evans 1987, Clarendon | verified | Open Library (Oxford: Clarendon Press, 1987) | Remove "[verify publisher]" |
| Fackenheim 1970, NYU Press | verified | Open Library | — |
| Faust 2008, Knopf | verified | Open Library | — |
| Finley & Koyama 2018, JLE 61(2): 253–77 | verified | https://doi.org/10.1086/699016 | — |
| Fountain 2010, LSU | verified | Open Library | — |
| Ganiel 2016, OUP | verified | https://doi.org/10.1093/acprof:oso/9780198745785.001.0001 | — |
| Goen 1985, Mercer | verified | Open Library | — |
| Harper 2017, Princeton | verified | Open Library | — |
| Hovannisian 1992, St. Martin's | verified | https://openlibrary.org/books/OL1539348M | — |
| Jenkins 2014, HarperOne | verified | Open Library | — |
| Kairos Theologians 1985 | wrong detail (minor) | see A7 | see A7 |
| Kendrick 1956, Methuen | verified | Open Library | — |
| Kerr 1996, Columba | verified | Open Library | — |
| Kim & Kim 2015 | wrong detail (year) | https://doi.org/10.1017/CBO9781139048071 (2014) | 2014 |
| Kim Sung-Gun 1989, Hull PhD | verified (subtitle variant) | https://hull-repository.worktribe.com/output/4210369 | see note |
| Kracht 2018, Nebraska | verified | Open Library | — |
| Larkin 1972, AHR 77(3): 625–52 | verified | https://doi.org/10.2307/1870344 | — |
| Larkin 2014, NHR 18(1): 74–92 | verified | https://doi.org/10.1353/nhr.2014.0019 | — |
| Lee 2010, Hawai'i | verified | Open Library (2009/2010; 2010 edition with subtitle) | — |
| Lehmann 1980, Kohlhammer | verified | Church History review record (Christentum und Gesellschaft 9, 186 pp.) | — |
| Lehmann & Trepp 1999, V&R | verified | Open Library | — |
| Lian Xi 2010, Yale | verified | Open Library | — |
| Little 2007, CUP | verified | https://doi.org/10.1017/CBO9780511812934 (online 2006, print 2007) | — |
| Martin 1991, Beacon | verified | Open Library | — |
| Meier 2003, V&R | verified (subtitle) | https://openlibrary.org/books/OL3753384M | Remove "[verify subtitle]" |
| Meier 2016, EME 24(3): 267–92 | verified | https://doi.org/10.1111/emed.12152 | — |
| Miller 1975, JSH 9(1): 81–98 | verified | https://doi.org/10.1353/jsh/9.1.81 | — |
| Molesky 2015, Knopf | verified | Open Library | — |
| Mooney 1896 | verified | IA: https://archive.org/details/ghostdancesioux00moonrich (Washington 1896, pp. 641–1136 = 14th Annual Report BAE, 1892–93, pt. 2) | Remove "[verify series details]"; add "pp. 641–1136" |
| Mordechai & Eisenberg 2019 | verified | https://doi.org/10.1093/pastj/gtz009 | — |
| Mordechai et al. 2019 | verified | https://doi.org/10.1073/pnas.1903797116 | — |
| Morris 1975 | verified | https://doi.org/10.1017/S0025727300020275 | — |
| Neiman 2002 | verified | Open Library | — |
| Newfield 2022 | verified | https://doi.org/10.1525/sla.2022.6.4.575 | — |
| Noll 2006, UNC | verified | Open Library | — |
| Park 2003, UW Press | verified | https://ci.nii.ac.jp/ncid/BA63588217 ; reviews dated 2003 | — |
| Phillips 2008, HS 9(7): 34–36 | verified | https://doi.org/10.1353/hsp.2008.0022 | — |
| Phillips & Killingray 2003 | verified | https://doi.org/10.4324/9780203468371 | title variant (note) |
| Rable 2010, UNC | verified | Open Library | — |
| Rosenberg 1962, Chicago | verified | Open Library | — |
| Rubenstein 1966, Bobbs-Merrill | verified | Open Library | — |
| Salfeld 1898, Simion | verified | Open Library | — |
| Snape 2005, Routledge | verified | Open Library | — |
| Snape 2009, SCH 45: 371–403 | verified | https://doi.org/10.1017/S0424208400002643 | — |
| Stauff 2025, OUP | verified | https://doi.org/10.1093/9780197749456.001.0001; subtitle "Confession, Politics, Devotion" (retailer and OUP listings) | — |
| Stearns 2011, JHU | verified (subtitle) | https://openlibrary.org/books/OL24880396M | Remove "[verify subtitle]" |
| Stout 2006, Viking | verified | Open Library | — |
| Suny 2015, Princeton | verified | Open Library | — |
| Wallace 1956 | verified | https://doi.org/10.1525/aa.1956.58.2.02a00040 | — |
| Wallace 1970, Knopf | verified | Open Library | — |
| Warren 2017, Basic | verified | Open Library | — |
| Wilkinson 1978, SPCK | verified | Open Library | — |
| Wilson C. R. 1980, Georgia | verified | Open Library | — |
| Wilson P. H. 2009, Belknap / Allen Lane | verified | Open Library | — |
| Winter 1995, CUP | verified | Open Library | — |
| Yang 2012, OUP | verified | Open Library | — |
| Yuval 2006, UC Press | verified (translators) | Translated by Barbara Harshav and Jonathan Chipman (library and bookseller records, e.g. https://relbib.de/Record/1613054173/Details) | Remove "[verify translators]" |

## C. References: section 19 (39 entries)

| Ref | Status | Evidence | Correction |
|---|---|---|---|
| Ager & Ciccone 2018, JEEA 16(4): 1021–68 | verified | https://doi.org/10.1093/jeea/jvx029 | — |
| Alexander et al. 2004, UC Press | verified | https://openlibrary.org/works/OL15335245W | — |
| Belloc et al. 2014 draft (NBER URL) | verified | URL returns 200 | — |
| Belloc et al. 2016, QJE 131(4): 1875–1926 | verified | https://doi.org/10.1093/qje/qjw020 | (see A1 for the description) |
| Bentzen 2019, EJ 129(622): 2295–2321 | verified | https://doi.org/10.1093/ej/uez008 | — |
| Bentzen 2021 | verified | Crossref | — |
| Boone n.d. | wrong detail (incomplete) | see A4 | Boone, Kyle. 2013 … |
| Bottan & Perez-Truglia 2015 | verified | Crossref | — |
| Chaney 2013, Econometrica 81(5): 2033–53 | verified | https://doi.org/10.3982/ECTA10233 | — |
| Cohn 1992, JHU | verified | Open Library | — |
| Cunningham & Grell 2000, CUP | verified | Open Library | — |
| Davie 1994, Blackwell | verified | Open Library | — |
| Dittmar & Meisenzahl 2020, REStud 87(2): 959–96 | verified | https://doi.org/10.1093/restud/rdz002 (Crossref lacks vol./pages; pages from the published PDF per the reading notes) | — |
| Fountain 2010 | verified | Open Library | — |
| Frijters et al. 2024, JSSR 63(1): 62–75 | verified | https://doi.org/10.1111/jssr.12879 (online 31 Aug 2023) | — |
| Furlong 2021 | verified | https://doi.org/10.17077/etd.006336 (Crossref "approved" Dec 2021); subtitle per Iowa Research Online | Remove the year flag |
| Gao Chunchang 2008 | verified (venue only) | Google Scholar listing (历史研究, 2008) | issue/pages still to verify |
| Goatley 1996, Orbis | verified | OL; Harvey review https://doi.org/10.2307/3169535 (CH 66(3): 644–45) | — |
| Ishchuk 2026, OPREE 46(4) | verified | https://doi.org/10.55221/2693-2229.2782 | — |
| Janku et al. 2012, Routledge | verified | Open Library | — |
| Jedwab et al. 2019, JEG 24(4): 345–95 | verified | https://doi.org/10.1007/s10887-019-09167-1 | — |
| Jedwab et al. 2022, JEL 60(1): 132–78 | verified | https://doi.org/10.1257/jel.20201639 | — |
| Jones 1971, HTR 64(4): 541–57 | verified | https://doi.org/10.1017/S0017816000023439 | — |
| Jones (1973) 1998, Beacon | verified (1998) | https://openlibrary.org/books/OL683610M (Beacon 1998) | Remove "1997 or 1998" flag |
| Li Huacheng 2008 | not found | — | verify on CNKI |
| Li Huacheng 2013, 历史研究 | verified | Google Scholar listing | — |
| Neiman 2002 | verified | Open Library | — |
| Pinn 1995, Continuum | verified | Open Library | Remove "[verify]" |
| Raboteau (1978) 2004 | verified | Open Library | — |
| Rausch 2016, Acta Koreana 19(1): 69–97 | verified | https://doi.org/10.18399/acta.2016.19.1.003 | — |
| Stark 1996 | verified | Open Library | — |
| Stearns 2009, HC 7(5): 1363–75 | verified | https://doi.org/10.1111/j.1478-0542.2009.00634.x | — |
| Thomas 1993, Temple | verified | Open Library | — |
| Tseng 2017 | wrong detail (minor) | see A9 | add 修訂版 |
| Turner 2021, De Gruyter, 139–56 | verified | https://doi.org/10.1515/9783110713350-010; ed. Gerard Delanty; subtitle "Critical Perspectives on the Covid-19 Crisis" (https://www.degruyterbrill.com/document/doi/10.1515/9783110713350/html) | Remove the "[verify]" on volume subtitle and editor |
| Voas & Crockett 2005 | verified | https://doi.org/10.1177/0038038505048998 | — |
| Weber 1946 | verified | Open Library (Gerth and Mills, OUP 1946) | The chapter "The Social Psychology of the World Religions" is pp. 267–301 (standard pagination; not opened here) |
| Winters 2020, American Religion 2(1) | verified | https://doi.org/10.2979/amerreli.2.1.01 | — |
| Zacharia 2018 | wrong detail (incomplete) | see A2 | Gregory Zacharia |

## D. Claims

| # | Sec. | Claim | Status | Evidence | Correction |
|---|---|---|---|---|---|
| 1 | 6 | Lisbon destroyed on All Saints' Day 1755; Pombal directed reconstruction | verified | Kendrick, Molesky (standard) | — |
| 2 | 6 | Malagrida preached sin as cause; later executed | verified, causal implication misleading | see A8 | see A8 |
| 3 | 6 | Larkin 1972: "devotional revolution" 1850–75; Famine, loss of Gaelic culture, Catholicism as identity substitute | verified | doi 10.2307/1870344; https://en.wikipedia.org/wiki/Devotional_Revolution | — |
| 4 | 6 | Miller 1975 used the 1834 data; attendance high in the east, low in the west; Famine composition effect | verified (moderate) | Miller's later essay describes the 1975 use of the 1834 Commissioners of Public Instruction attendance data (https://muse.jhu.edu/article/184493/pdf); secondary summaries give the regional pattern | "1834 religious census" is better put as "the 1834 Commissioners of Public Instruction returns" |
| 5 | 6 | Larkin 2014 traced the beginnings to parish missions 1825–46 | verified | Crossref title; posthumous | — |
| 6 | 6 | Barr 2020 extends the revolution to the diaspora | verified | Article opening (Crossref) | — |
| 7 | 6 | Christians prominent among the 1919 declaration signers (count flagged) | verified | 16 of 33 signers were Christian (Protestant), 15 Cheondogyo, 2 Buddhist: https://en.wikipedia.org/wiki/Korean_Declaration_of_Independence | Write "16 of the 33 signatories"; Park 2003 confirmed as 2003, UW Press |
| 8 | 6 | Armenian Church canonized victims as martyrs in 2015 | verified | 23 April 2015, Holy Etchmiadzin, about 1.5 million: https://agbu.org/press-release/martyrs-armenian-genocide-canonized-mother-see-holy-etchmiadzin ; https://www.aljazeera.com/news/2015/4/23/armenia-church-canonises-1-5-million-genocide-victims | Add the date; cite AGBU or Mother See communiqué |
| 9 | 6 | Barović 2026: diaspora religiosity tied to the church's communal activities; some doubt Armenian identity would exist without it | verified | Abstract (Crossref) | — |
| 10 | 6 | Belhar Confession drafted 1982 | verified | 1982 draft by the DRMC synod; adopted 1986; WARC Ottawa 1982 declared apartheid's theological justification a heresy and suspended the NGK (and NHK): https://ngtt.journals.ac.za/pub/article/view/352/457 | Optionally add "adopted 1986" and the WARC ruling |
| 11 | 6 | Kairos Document 1985 attacked "state theology" and "church theology" | verified | Sept 1985: https://en.wikipedia.org/wiki/Kairos_Document | — |
| 12 | 6 | Ghost Dance 1889–90, ended at Wounded Knee; Mooney 1896 | verified | IA metadata (above) | — |
| 13 | 6 | Dowd: pan-Indian nativism 1745–1815, Neolin, Tenskwatawa; Martin: Redstick War 1813–14 as "sacred revolt"; Handsome Lake from 1799 | verified | Titles and publisher descriptions; standard | — |
| 14 | 6 | Brenner 1980 surveyed survivors; both lost and strengthened faith | verified | Survey of 708 Israeli survivors (608 questionnaires, 100 interviews) per bibliographic descriptions (Taylor & Francis listing https://www.taylorfrancis.com/books/9781412852975) | Add "708 survivors in Israel" if wanted |
| 15 | 6 | Carmil & Breznitz: greater belief in God among survivors and their children than controls | verified | Abstract (doi 10.1002/jts.2490040307) | — |
| 16 | 6 | Rubenstein 1966 rejected the God of history; Fackenheim 1970, Berkovits 1973 renewed fidelity | verified | Bibliographic records; standard readings | — |
| 17 | 6 | Faust 2008 "Good Death"; Noll 2006 theological crisis; Rable 2010 and Stout 2006 both sides claimed divine favour; Goen 1985 schisms; Wilson 1980 Lost Cause | verified | Publisher descriptions and standard readings | — |
| 18 | 6 | Rosenberg 1962: judgment in 1832, sanitation in 1866 | verified | Subtitle and standard reading | — |
| 19 | 6 | Morris 1975: Oxford cholera pamphlets 1832–54 | verified | Crossref (1832, 1849, 1854) | — |
| 20 | 6 | Evans 1987: Hamburg 1892, merchant oligarchy refused to filter water | verified | Standard reading of *Death in Hamburg* | — |
| 21 | 6 | Justinianic debate: Mordechai & Eisenberg and Mordechai et al. minimalist; Newfield says the Black Death analogy inflated estimates; Meier: cultural/religious reorientation; de Wet: pro-imperial power discourse | verified | Abstracts (Crossref/OpenAlex) | Note that Meier 2016 is also catastrophist on short-term effects |
| 22 | 6 | Einbinder 2018: continuity of worldview among Iberian and Provençal Jews | verified | Library and publisher descriptions (https://libcat.scu.edu/Record/b3736630) | — |
| 23 | 6 | Dols 1977: martyrdom and mercy; no flagellants or attacks on minorities; Ibn al-Wardī died of plague 1349 | verified | Standard (Dols; Ibn al-Wardī d. Aleppo 1349) | — |
| 24 | 6 | Stearns 2011: parallel contagion debates | verified | Subtitle (OL) | — |
| 25 | 6 | Wilson 2009: religion one driver among several; Lehmann crisis piety; Stauff | verified (Lehmann content not opened) | OL; Church History review record | Lehmann pages remain on the to-verify list |
| 26 | 6 | Jenkins 2014; Becker 1994; Wilkinson 1978; Snape "diffusive" Christianity; Winter 1995; Brown 2009 (1960s) | verified | Bibliographic records; standard readings | — |
| 27 | 6 | Bays 2012; Yang 2012 red/black/gray markets; Lian Xi 2010 | verified | Bibliographic records; Yang's triple-market model is the book's thesis | — |
| 28 | 6 | Kim Sung-Gun: shrine issue split churches; resisters formed own bodies after 1945 | verified | Hull abstract (differing responses of the Catholic, Methodist and Presbyterian churches); the Kosin split of 1952 is standard | — |
| 29 | 6 | Bristow: culture of optimism and forgetting; Phillips 2008: religious explanations incl. divine punishment; Aladura | verified | Phillips excerpt (Crossref); Bristow publisher description | — |
| 30 | 6 | COVID: "most Americans report no lasting change (Bentzen 2021)" | unsupported (by citation) | see A5 | see A5 |
| 31 | 6 | Abuse: belief persists while affiliation, attendance and giving fall (Bottan & Perez-Truglia) | verified | Reading notes §4 | — |
| 32 | 19 | Belloc et al. description | wrong detail | see A1 | see A1 |
| 33 | 19 | Dittmar & Meisenzahl: 1500–1522 plague → ordinances 0.11–0.14 per outbreak; Black Death null (988 n. 63); alternative needed (983); belief/trust not measured | verified | Reading notes §1 (pp. 983, 986, 988) | — |
| 34 | 19 | Bottan & Perez-Truglia: −10.4 pp identification, −12.2 pp attendance, belief unchanged (imprecise); switching about 3 years then no religion; zip and county units | verified | Reading notes §4 (pp. 107, 113–14) | — |
| 35 | 19 | Ager & Ciccone: membership and seating rise with rainfall risk; insurance theorised not measured; belonging, not belief | verified | Reading notes §7 (pp. 3, 5) and published abstract | — |
| 36 | 19 | Bentzen 2019: belief but not attendance, second-hand via Ager & Ciccone | verified as reported (flag correctly kept) | Reading notes §7 p. 7; "Not obtained" table | — |
| 37 | 19 | Bentzen 2021: prayer searches up about 30%, independent of closures; nothing on trust | verified | Reading notes §6 | — |
| 38 | 19 | Chaney 2013: deviant floods → highest religious authority less likely replaced | verified | Abstract | Optionally add the null on the popular-religiosity proxy |
| 39 | 19 | Frijters et al. 2024: no evidence disasters raise religious importance | verified | Abstract: estimates "near-zero"; short-run *negative* attendance effects | Can drop "[read before describing]" for the abstract-level claim |
| 40 | 19 | Jedwab et al. 2019 (124 towns; mortality lowered persecution where Jews were economically needed); 2022 legitimacy claim historiographical | verified | Reading notes §§2–3 | — |
| 41 | 19 | Weber: theodicy of fortune vs. suffering by stratum | verified | "Social Psychology of the World Religions" (Gerth & Mills 1946) | pp. 267–301 |
| 42 | 19 | Stark 1996: nursing in the Antonine and Cyprianic plagues raised survival and conversion | verified | Standard (ch. 4) | — |
| 43 | 19 | Cunningham & Grell: reviewers note it does not explain confessional differences | verified (supported) | E. Malcolm's review asks whether Catholic southern Europe shared the same expectations: https://muse.jhu.edu/article/15315/summary (search summary) | Name the reviewer |
| 44 | 19 | Zacharia: Black Death, 1666 London fire, 1755 Lisbon as "interruptions" | verified, but overlap understated | see A2 | see A2 |
| 45 | 19 | Zacharia "the only cross-catastrophe comparison found that includes the Black Death" | unsupported (incomplete) | see A3 | see A3 |
| 46 | 19 | Turner 2021: comparative history of responses to catastrophes in a political theology of COVID | verified | Crossref; De Gruyter TOC | — |
| 47 | 19 | Ishchuk 2026: trust in God (existential) vs trust in the Church (institutional legitimacy); trust "redistribution" toward army and volunteers; KIIS/Razumkov surveys | verified | Abstract (Crossref) | — |
| 48 | 19 | Rausch 2016 compares Catholic and Protestant theodicies of Korea's collective suffering | verified | Abstract: six Korean Christians, three Catholic and three Protestant | — |
| 49 | 19 | Stearns 2009 warns against monolithic "responses" | verified | Abstract | — |
| 50 | 19 | Fountain: fewer than 40% of datable conversions before freedom | verified | LSU Press description: https://muse.jhu.edu/book/33081 | — |
| 51 | 19 | Boone thesis on 1793 yellow fever redemptive-suffering theodicy | verified (content) | see A4 | see A4 |
| 52 | 19 | Gao 2008, Li 2008/2013, Tseng 2017 as separate Sinophone treatments | partly verified | see A9–A11 | — |
| 53 | 19 | Winters 2020 as the "Black death" = Black mortality false positive | verified | Crossref; appears in C1 rerun | — |
| 54 | 19 | Search-log rerun C1 "Black Death" "slave religion" (Crossref) | verified | Total 1,347,084 (identical); top ten slave-religion items plus Winters 2020 | — |
| 55 | 19 | Rerun C3 plague slavery theodicy comparative (Crossref) | verified | Total 1,244,717 (identical); Rausch 2016, "Job's Silence on Slavery", "Faust, the Plague, and Theodicy" present | — |
| 56 | 19 | Rerun C5 catastrophe religiosity "institutional trust" (Crossref) | verified | Total 404,416 (identical); COVID-conspiracy and vaccine-trust items | — |
| 57 | 19 | Rerun C6 "believing without belonging" disaster (Crossref) | verified | Total 622,685 (identical); Davie-related items only | — |
| 58 | 19 | Rerun C12 Black Death trust in church decline faith lay piety (Crossref) | verified | Total 1,503,322 (identical); no comparative item | — |
| 59 | 19 | Rerun G13 "collective suffering" Christianity "trust in the church" (Scholar) | verified | "6 results", Ishchuk 2026 among them | — |
| 60 | 19 | Rerun G11 "Black Death" "slave Christianity" (Scholar) | verified | "3 results", none relevant (Larsen, *White Lies*, home/slavery afterlife) | — |

## E. Counts

References (121 entries: 82 in section 6, 39 in section 19):
- verified: 115 (incl. 1 venue-only: Gao 2008)
- wrong detail: 5 (Kim & Kim year; Kairos 1985/1986 publisher; Boone author/title/year; Zacharia name; Tseng revised edition). The Belloc 2016 problem is a description problem, so it is counted under claims.
- not found: 1 (Li Huacheng 2008)
- misattributed: 0
- fabricated-likely: 0
- In addition, 16 inline or ref "[verify]" flags can now be removed (Becker translator, Braun SVEC, Elphick subtitle, Evans publisher, Meier subtitle, Mooney series, Stearns subtitle, Yuval translators, Jones 1998, Pinn, Furlong year, Turner editor, Park count, Armenian 2015, Malagrida, Zacharia name).

Claims (60 checked):
- verified: 52 (7 of them are search re-runs, all matching exactly)
- wrong detail: 2 (Belloc version; Zacharia overlap understated)
- unsupported: 2 (COVID "no lasting change" citation; "only cross-catastrophe comparison")
- verified but misleading wording: 1 (Malagrida)
- partly verified: 3 (Miller attendance pattern at moderate confidence; Lehmann content not opened; Sinophone items)
- misattributed: 0
- fabricated-likely: 0
