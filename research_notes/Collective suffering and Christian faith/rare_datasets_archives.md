# Rare datasets, databases and archival collections — verification notes

Project question: why collective suffering sometimes intensifies Christian faith and sometimes erodes trust in religious institutions.
Date checked for every entry: **2026-11-05** (unless stated). WebSearch was unavailable; everything below was checked with curl (HTTP status + page text), the Library of Congress JSON API, the Harvard Dataverse API, the Zenodo API, Crossref, doi.org handle API, the Internet Archive advancedsearch API, or the Wayback availability API.

## Verification key

- **[OPEN 200]** — I fetched the page (HTTP 200) and read text on it. What I saw is quoted or paraphrased in "Seen".
- **[OPEN 200, title only]** — HTTP 200, but the page is JavaScript-rendered or I only read the title. Contents described are what the title/menu shows.
- **[API]** — metadata returned by a repository API (Dataverse, Zenodo, LoC JSON, ARDA page, IA search). Counts are what the API returned.
- **[DOI]** — DOI found in Crossref and/or resolved through the doi.org handle API. Article/data paper exists; data location may still need checking.
- **[WAYBACK]** — live site blocked (Cloudflare 403, timeout or DNS block in this sandbox), but the Wayback availability API returned a 200 snapshot (timestamp given). Existence verified; **contents not seen by me** — descriptions in brackets are from prior knowledge and must be checked.
- Anything I could not open at all is in **Unconfirmed leads** at the end.

Fields per item: name · institution · coverage · contents · bearing on devotion vs institutional trust · access · URL · verification.

---

## A. Black Death and late medieval Europe (1347–c.1500)

### A1. Plague-outbreak data (exposure measures)

1. **Digitized Biraben plague outbreaks (in Schmid et al. 2015 code-and-data package)** · Schmid, Büntgen, Easterday, Ginzler, Walløe, Bramanti, Stenseth · Europe 1347–c.1900 · Zip "pulse-of-asia-datasets-sourcecode.zip" (15,015,580 bytes) with source code and datasets for the PNAS paper on climate-driven plague reintroductions · Gives town-year plague exposure to test whether repeated outbreaks (1348, 1361–63, 1370s…) predict devotional bequests, confraternity foundings, clerical recruitment or anti-clericalism · Open (Eclipse-1.0 licence per Zenodo) · https://zenodo.org/record/14973 · [API] Zenodo record, DOI 10.5281/zenodo.14973 (resolves). Roosen & Curtis (2018) name this Zenodo record as "a digitized version of this data set" (Biraben).
2. **Büntgen et al. 2012, "Digitizing Historical Plague"** · *Clinical Infectious Diseases* · data paper describing the digitization of Biraben's catalogue · [DOI] 10.1093/cid/cis723 (Crossref; publisher page Cloudflare-blocked, abstract not retrieved).
3. **Roosen & Curtis 2018, "Dangers of Noncritical Use of Historical Plague Data"** · *Emerging Infectious Diseases* 24(1) · source critique of the Biraben dataset. Seen: Biraben's data "contains information on mentions of plague from various kinds of sources, many of which were not cited"; studies using it report 6,929 outbreaks (Europe 1347–1900), 7,711 (Europe and Asia 1347–1900), 5,559 (Europe/N. Africa 1347–1760) and 6,656 (Europe 1347–1760) · Essential caveat: absence of a record ≠ absence of plague, so exposure measures are biased toward well-documented (often ecclesiastical/urban) places · Open · https://wwwnc.cdc.gov/eid/article/24/1/17-0477_article · [OPEN 200] + [DOI] 10.3201/eid2401.170477.
4. **"Mapping the plague through natural language processing" datasets and code** · Krauer & Schmid · Zenodo 2021 · Seen: final plague datasets extracted from Sticker (1908) *Die Pest* and Biraben (1975) via NLP/geocoding; plague.zip (24.4 MB) · Independent second extraction of the Biraben/Sticker catalogues for robustness checks · CC BY-NC 4.0 · https://zenodo.org/record/6587267 · [API] DOI 10.5281/zenodo.6587267.
5. **Bauch & Büntgen 2025, supplementary data on the arrival of the Black Death** · Zenodo · Seen: documentary data on celestial phenomena and climatic anomalies (S1), weather (S2), dearth and famine indicators (S3), Mediterranean grain trade (S4), plague outbreaks (S5), chronicle grain prices (S6–S7), NW Italian grape harvests (S8), tree rings (S9); one xlsx (1.96 MB) · Lets the researcher separate famine-plus-plague compound suffering from plague alone (relevant to "punishment for sin" readings) · CC BY 4.0 · https://zenodo.org/record/17441026 · [API] DOI 10.5281/zenodo.17441026.
6. **Krauer & Dean 2020, seasonality of historical plague outbreaks — code and raw data** · Zenodo · small zip (128 KB) · Open (CC BY-NC) · https://zenodo.org/record/4240204 · [API]. Minor.
7. **Gingerich & Vogler, replication data for "Pandemics and Political Development: The Electoral Legacy of the Black Death in Germany"** · Harvard Dataverse · Seen: 36 files including `data_imp_bd_outbreaks.tab`, `data_pru_bd_outbreaks.tab`, `data_pre_ref_bd_outbreaks.tab`, district geolocation and controls; CC0 · Ready-made German/Prussian district-level Black Death outbreak coding, including a "pre-Reformation" outbreak file — useful for testing whether plague intensity predicts later Protestant adoption (institutional exit) · Open · https://doi.org/10.7910/DVN/M0PKZE · [API].
8. **Jedwab, Johnson & Koyama, replication data for "Pandemics and Cities: Evidence from the Black Death and the Long-Run"** (*Journal of Urban Economics* 2024, DOI 10.1016/j.jue.2023.103628) · Harvard Dataverse · Seen: 1,409 files incl. `All_Cities.tab`, GIS layers; CC0 · City-level mortality and population panel; can be merged with church/confraternity data · Open · https://doi.org/10.7910/DVN/TVBNBA · [API].
9. **Jedwab, Johnson & Koyama, "Data and Replication Files for The Economic Impact of the Black Death"** · openICPSR project 120682 · Listed by Dataverse search; DOI 10.3886/E120682 resolves to openicpsr.org/openicpsr/project/120682/view (page Cloudflare-blocked) · Registration typically required for openICPSR downloads [verify] · [DOI].
10. **Justinianic Pandemic Sourcebook** (Gruber, Ransohoff, McCormick, More) · Harvard Dataverse · Seen: "comprehensive catalog of outbreaks of plague in the First Pandemic documented in written sources" (541–c.750) · Comparison case for plague and Christian institutions in late antiquity · CC0 · https://doi.org/10.7910/DVN/5RSHSR · [API].
11. **Christakos et al. 2005, *Interdisciplinary Public Health Reasoning and Epidemic Modelling: The Case of Black Death*** · Springer book · [DOI] 10.1007/3-540-28165-7 (Crossref; chapters "Black Death: The Background", "Stochastic Modelling"). The book's own mortality dataset location not verified.
12. **Alfani, Bonetti & Fochesato 2023, replication package for "Pandemics and socio-economic status: plague of 1630 in northern Italy"** · ICPSR 186342 (DOI 10.3886/E186342 resolves) · Later plague, useful for method transfer · [DOI]/[API]. Article DOI 10.1080/00324728.2023.2197412.
13. **Rogowski, replication data "The Black Death in Fourteenth Century Europe"** · Harvard Dataverse · Seen: Beck-Sieber scores of Prussian counties, one tab file, CC0 · Marginal · https://doi.org/10.7910/DVN/NNDMSS · [API].

### A2. Persecution of Jews (scapegoating branch)

14. **Doten-Snitker, replication data for "The Diffusion of Exclusion: Medieval Expulsions of Jews"** · Harvard Dataverse (2024) · Seen: expulsions among "over 500 polities in the western Holy Roman Empire, 1385–1520 CE"; 28 files incl. R scripts and climate data; CC0 · Shows how religious rationales against and for exclusion spread; a structured polity-year dataset that can be linked to plague recurrence · Open · https://doi.org/10.7910/DVN/SCJL8I · [API].
15. **Jedwab, Johnson & Koyama 2019, "Negative shocks and mass persecutions: evidence from the Black Death"** · *Journal of Economic Growth* · [DOI] 10.1007/s10887-019-09167-1 (Crossref). Replication-file location not verified.
16. **Voigtländer & Voth 2012, "Persecution Perpetuated"** · *QJE* · [DOI] 10.1093/qje/qjs019 (Crossref). Uses 1348–50 pogrom coding (from Germania Judaica). Replication-file location not verified.
17. **Finley & Koyama 2018, "Plague, Politics, and Pogroms"** · *Journal of Law and Economics* · [DOI] 10.1086/699016. Data location not verified.
18. **Anderson, Johnson & Koyama 2017, "Jewish Persecutions and Weather Shocks: 1100–1800"** · *Economic Journal* · [DOI] 10.1111/ecoj.12331. Data location not verified.
19. **Medieval Ashkenaz** (Corpus der Quellen zur Geschichte der Juden im spätmittelalterlichen Reich) · https://www.medieval-ashkenaz.org/ · [OPEN 200, title only] — single-page app; no readable content in HTML. [Contents from prior knowledge: edited sources on Jews in the late-medieval Empire — verify.]
20. **Germania Judaica** · http://germania-judaica.de/ · [WAYBACK] latest snapshot 2016-01-10; live site timed out. Status of the database is uncertain.

### A3. Wills, papal and episcopal records, clergy

21. **Calendar of Wills Proved and Enrolled in the Court of Husting, London, Part 1, 1258–1358** (ed. R. R. Sharpe, 1889) · British History Online · Seen: calendared London wills, table of contents by regnal year from 43 Henry III; "free content … digitised by double rekeying" · Pious bequests (chantries, lights, fraternities, parish fabric) before vs after 1348–49 = devotion directed to institutions vs private/lay vehicles · Free · https://www.british-history.ac.uk/court-husting-wills/vol1 · [OPEN 200]. Part 2 also returns 200 (title seen; date range not read): https://www.british-history.ac.uk/court-husting-wills/vol2.
22. **Calendar of Papal Registers relating to Great Britain and Ireland, vol. 3, 1342–1362** (ed. Bliss & Johnson, 1897) · BHO · Seen: "Covers the papacies of Clement VI and Innocent VI", free, double-rekeyed · Petitions, provisions, dispensations (e.g., for under-age ordination after clerical mortality), indulgences — a direct record of institutional response and of demand for papal grace around 1348 · Free · https://www.british-history.ac.uk/cal-papal-registers/brit-ie/vol3 · [OPEN 200].
23. **Fasti Ecclesiae Anglicanae 1300–1541** (vol. 1, Lincoln diocese, ed. H. P. F. King 1962, and further volumes) · BHO · Seen: "Traces the chronology and careers of the bishops and the senior clergy" · Turnover of senior clergy as a measure of institutional disruption · Free · https://www.british-history.ac.uk/fasti-ecclesiae/1300-1541/vol1 · [OPEN 200].
24. **York Archbishops' Registers Revealed** · Borthwick Institute, University of York (+ The National Archives indexes 1304–1405) · Seen: "over 21,500 images of registers produced by the Archbishops of York between 1225 and 1650"; "26132 indexed entries" to date · Ordinations, institutions to benefices, chantry licences, wills proved, visitations across 1348–49 and 1361–62 · Free · https://archbishopsregisters.york.ac.uk/ · [OPEN 200].
25. **Episcopal registers in print on the Internet Archive** · Seen via IA API: Canterbury & York Society edition *The register of Bishop John de Halton* (Carlisle, 1909; id `registerofbishop02carluoft`); Cantilupe Society Hereford registers *Registrum Johannis Gilbert* 1375–1389 (`registrumjohanni18cath`) and *Registrum Ade de Orleton* 1317–1327 (`registrumadedeor52cath`) · Full text, free · https://archive.org/details/registrumjohanni18cath · [API].
26. **Canterbury & York Society** · https://canterburyandyork.org/ · live returns 200 with a 114-byte body (no content); [WAYBACK] snapshot 2024-07-13. [Publishes editions of English episcopal registers — verify list.]
27. **Clergy of the Church of England Database (CCEd)** · King's Digital Lab · Seen (Oct 2026 notice): "Site Temporarily Unavailable … KDL is actively working to restore access … by converting the site to a static form." · Post-1540 only; for the Reformation-era sequel, not the Black Death · Currently offline · https://theclergydatabase.org.uk/ · [OPEN 200 — outage notice].
28. **Mapping the Medieval Countryside (Inquisitions post mortem)** · https://www.inquisitionspostmortem.ac.uk/ · [OPEN 200, title only]. IPMs record deaths of tenants-in-chief; 1349 clusters measure elite mortality [content not read — verify which calendar volumes are online].
29. **Repertorium Germanicum Online (DHI Rom)** · https://rg-online.dhi-roma.it/ · [WAYBACK] 2026-05-18; live timed out. [Papal registers on German clergy and petitioners from 1378 — verify.]
30. **Medieval and Early Modern Data Bank (MEMDB)** · Rutgers · http://www2.scc.rutgers.edu/memdb/ · [WAYBACK] snapshot 2020-08-03 only; live timed out — may be defunct. [Prices, wages, currency exchange — verify.]
31. **DARMC (Digital Atlas of Roman and Medieval Civilizations)** · Harvard · https://darmc.harvard.edu/ · [WAYBACK] 2026-10-26 (live 403). Its geodatabases are on Harvard Dataverse [API]: e.g. "Geodatabase of Historical Evidence on Precipitation in Central Europe AD 1013–1504" (doi:10.7910/DVN/ARUMGE), "Archaeological Finds of Rats: AD 1–1500" (doi:10.7910/DVN/NARKTE), McCormick, More et al. "Western European Climate from Written Sources" drafts (doi:10.7910/DVN/K0AJD7).

### A4. Italy: tax, office and merchant archives

32. **Online Catasto of 1427** · Brown University (Florentine Renaissance Resources), ed. Herlihy, Klapisch-Zuber, Litchfield, Molho · Seen: "searchable database of tax information for the city of Florence in 1427–29 (c. 10,000 records)" · Household wealth, size, and ecclesiastical property holdings two generations after 1348; pairs with confraternity/testament data · Free · https://cds.library.brown.edu/projects/catasto/ · [OPEN 200].
33. **Online Tratte of Office Holders 1282–1532** · Brown University · Seen: title "Florentine Renaissance Resources: Online Tratte of Office Holders 1282–1532" · Officeholding of lay elites who also governed confraternities and Opere · https://cds.library.brown.edu/projects/tratte/ · [OPEN 200, title only].
34. **Fondo Datini** · Archivio di Stato di Prato · Seen: "un universo di oltre 150.000 documenti sciolti e circa 600 registri"; searchable database (by date, name, place, fondaco), lemmatized corpus, editions of correspondence (incl. Margherita–Francesco Datini letters) · Merchant letters 1360s–1410 full of plague-time piety, flight, vows and comments on clergy — a rare lay voice on devotion vs institutions · Free · http://datini.archiviodistato.prato.it/ (https times out) · [OPEN 200].
35. **Confraternitas** (journal, Society for Confraternity Studies) · University of Toronto Journal Production Services · Seen: title page · Open-access articles and source notes on confraternities · https://jps.library.utoronto.ca/index.php/confrat · [OPEN 200, title only].

---

## B. Enslaved and freed African Americans (1619–1877)

### B1. Testimony

36. **Born in Slavery: Slave Narratives from the Federal Writers' Project, 1936–1938** · Library of Congress · Seen via LoC JSON API: 604 catalogued items (557 photos/prints, 35 manuscript/mixed-material volumes, 34 PDFs/online text; location facets led by Texas 395, Alabama 91, North Carolina 42) · c. 2,300 narratives [count from prior knowledge — verify] with abundant testimony about forced attendance at white-controlled services vs secret "hush harbor" worship — the core evidence for devotion rising while trust in the masters' church fell · Free · https://www.loc.gov/collections/slave-narratives-from-the-federal-writers-project-1936-to-1938/ · [API] (HTML page Cloudflare 403; JSON 200).
37. **Voices Remembering Slavery: Freed People Tell Their Stories** · LoC American Folklife Center · Seen via LoC JSON: 66 items · Audio interviews (1932–1975 [verify]) incl. songs and religious memory · Free · https://www.loc.gov/collections/voices-remembering-slavery/ · [API].
38. **Fisk University ex-slave interviews (printed)** · Internet Archive · Seen via IA API: *God Struck Me Dead: Religious Conversion Experiences and Autobiographies of Ex-Slaves* (1969 reprint; ids `godstruckmedeadr0000fisk`, `godstruckmedeadr0000fisk_c6g9`; also a 2011 edition) and *Unwritten History of Slavery: Autobiographical Accounts of Negro Ex-Slaves* (1968; `unwrittenhistory0000fisk`) · Conversion narratives (visions, "struck dead") collected 1927–29 — the richest first-person source on intensified personal faith · Borrowable (IA lending) [verify] · https://archive.org/details/godstruckmedeadr0000fisk · [API].
39. **Documenting the American South: "The Church in the Southern Black Community"** · UNC Chapel Hill · https://docsouth.unc.edu/church/ · [WAYBACK] 2026-09-04 (live 503/timeout). [Full-text books, pamphlets and minutes on Black Protestant churches, c. 1780s–1920s — verify.]

### B2. Person-level databases

40. **Enslaved.org** + **Journal of Slavery and Data Preservation (JSDP)** · Michigan State University et al. · Seen: "Explore or reconstruct the lives of individuals who were enslaved…"; JSDP "publishes original datasets about the lives of enslaved Africans and their descendants … fifteenth to the early twentieth centuries" · Linked open data; church-record datasets can be pulled · Free · https://enslaved.org/ · [OPEN 200].
41. **"Black Families in the Records of Christ Church, Philadelphia"** (Belden, Hasbrouck, Rice, JSDP 6(1), 2025) · [DOI] 10.14321/jsdp.6.1.0054 (resolves to Scholarly Publishing Collective) · An Anglican parish's baptisms/marriages/burials of Black families — institutional participation in a white-led church · Open dataset [verify licence].
42. **Freedom on the Move** · Cornell-led consortium · Seen: "Centered on thousands of 'runaway' advertisements … from the colonial era through the Civil War … a free, crowdsourced database" · Ads often mention preachers, exhorters, church membership, literacy for Bible reading [content of fields not checked] · Free · https://freedomonthemove.org/ (overview: /project-overview) · [OPEN 200].
43. **North Carolina Runaway Slave Notices, 1750–1865** · UNC Greensboro Digital Library on American Slavery · Seen: "all known runaway slave notices (more than 5000 items) published in North Carolina" searchable by name, keyword, county · Keyword-searchable for "preacher", "Baptist", "Methodist" · Free · https://dlas.uncg.edu/notices/ · [OPEN 200].
44. **Last Seen: Finding Family After Slavery** · Villanova University · Seen: title only (site later returned bot challenge); JAH review [DOI] 10.1093/jahist/jaz161; Burns 2024 article using the ads [DOI] 10.1080/0144039x.2023.2260185 · Information-wanted ads, many placed in the AME *Christian Recorder* — Black church press as the institution freed people relied on · Free · https://www.informationwanted.org/ · [OPEN 200, title only].
45. **SlaveVoyages** · https://www.slavevoyages.org/ · [OPEN 200, title only] — JavaScript app; the African Names / African Origins pages were not readable. [Trans-Atlantic, intra-American voyages, African names — verify.]
46. **Slave Biographies: The Atlantic Database Network** · Michigan State University (archived site) · Seen: three datasets — enslaved people in **Maranhão, Brazil**; colonial Louisiana; freed people in antebellum Louisiana; fields: names, ethnicities, skills, occupations, illnesses; "This is an archived website that is no longer updated." · Brazil–US comparison with identical schema · Free · https://slavebiographies.org/ · [OPEN 200].
47. **Afro-Louisiana History and Genealogy 1718–1820** (G. M. Hall) · https://www.ibiblio.org/laslave/ · [WAYBACK] 2026-10-21 (live timeout). [c. 100,000 enslaved persons in Louisiana — verify.]

### B3. Emancipation and Reconstruction

48. **Freedmen and Southern Society Project** · University of Maryland · Seen: editors selected "some 50,000" documents from the National Archives on 1861–1867 · Freedpeople's letters about church property, chaplains, and separation from white congregations · Free (selected documents online; volumes in print) · https://freedmen.umd.edu/ · [OPEN 200].
49. **Freedmen's Bureau records (RG 105)** · U.S. National Archives · Seen: "The Bureau of Refugees, Freedmen, and Abandoned Lands (Record Group 105) … established … March 3, 1865" · Marriage registers, school reports and complaints, many involving Black churches as schools · Free · https://www.archives.gov/research/african-americans/freedmens-bureau · [OPEN 200]. Smithsonian Transcription Center (https://transcription.si.edu/) [WAYBACK] 2026-09-11 (live 403). NMAAHC Freedmen's Bureau page 403 — unconfirmed.
50. **Visualizing Emancipation** · University of Richmond · https://dsl.richmond.edu/emancipation/ · [WAYBACK] 2026-10-12. [Mapped emancipation events 1861–65 — verify.]
51. **Geography of Slavery in Virginia** · University of Virginia · http://www2.vcdh.virginia.edu/gos/ · [WAYBACK] 2026-10-13.
52. **Colored Conventions Project** · Seen: "Bringing Nineteenth-Century Black Organizing to Digital Life"; "Convention Records" page · Minutes of Black state/national conventions, where AME/Baptist clergy were leading delegates — measures church leadership in civic protest · Free · https://coloredconventions.org/about-records/ · [OPEN 200].

### B4. Denominational and church records

53. **ARDA: U.S. Census of Religious Bodies files** · Association of Religion Data Archives · Seen in ARDA file list: "Statistics of Churches in the United States, State File, 1890" (1890CENSST); "Census of Religious Bodies, Expanded State File, 1906" (1906STEX); County Files 1906, 1916, 1926, 1936 (1906CENSCT … 1936CENSCT); State Files 1916, 1926, 1936 · Denomination-by-county membership incl. separate Black denominations (AME, AMEZ, CME, National Baptist) — the best quantitative test that faith "migrated" to sufferer-controlled bodies after 1865 · Free download · https://www.thearda.com/data-archive?fid=1906STEX · [OPEN 200].
54. **Printed *Religious Bodies* reports (1906, 1916, 1936)** · Internet Archive · Seen via IA API: e.g. "Special Reports Religious Bodies: 1906 part 1 summary and general tables" (`specialreportsre0000unse`), "Religious bodies: 1916" (`religiousbodies00blisgoog`, `cu31924031020948`), "Religious Bodies 1936 Volume I Summary and Detailed Tables" (`in.ernet.dli.2015.58487`) · Free full text · [API].
55. **Minutes of the Annual Conferences of the Methodist Episcopal Church (and MEC, South)** · Internet Archive · Seen via IA API: 110 hits for MEC title incl. `minutesannualco01churgoog` (dated 1773 onward), and Emory microform MECS volumes (e.g. `27838123.1855.emory.edu`, `27838123.1865.emory.edu`) · [Annual membership returns reported "white" and "colored" members by circuit — check per volume] — a rare annual series on Black membership in a white-led church before and after emancipation · Free · https://archive.org/details/minutesannualco01churgoog · [API].
56. ***The Christian Recorder*** (AME Church newspaper) · Internet Archive · Seen via IA API: 50 items, e.g. `christianrecorder_1864_v4_no27_to_39`, `christianrecorder_1865_v5_no26_to_39`, 1866, 1867, 1878, 1886 volumes · Black-controlled church press during war, emancipation and Reconstruction · Free · https://archive.org/details/christianrecorder_1865_v5_no26_to_39 · [API].
57. **Southern Baptist Historical Library and Archives** · Nashville · Seen: catalog, finding aids, and "Digital Resources … Most of the resources are scanned from the originals" · Church minute books (biracial churches' discipline of enslaved members) [specific digitized minutes not checked] · https://sbhla.org/ · [OPEN 200].
58. **Virginia Baptist Historical Society & Center for Baptist Heritage and Studies** · Richmond · Seen: title only (note: vbhs.org is an unrelated psychiatric clinic) · [Holds Virginia Baptist church minute books — verify] · https://baptistheritage.org/ · [OPEN 200, title only].
59. **Moravian Archives, Winston-Salem (Southern Province)** · Seen: menus for "Memoirs", "Graveyard Database", Salem Congregation research resources · Moravian memoirs (Lebensläufe) and burial registers include enslaved/free Black members of Salem congregations [verify specific holdings] · https://moravianarchives.org/ · [OPEN 200].
60. **Moravian Archives, Bethlehem (Northern Province)** · Seen: "We collect and preserve records … of Moravians in North America" · [Caribbean mission diaries — verify] · https://www.moravianchurcharchives.org/ · [OPEN 200].
61. **Amistad Research Center** · Tulane, New Orleans · Seen: "Our cornerstone collection, the American Missionary Association archives" · AMA records: northern missionaries' schools and churches for freedpeople, 1860s–70s, with letters from Black congregants · On site / partly digitized · https://amistadresearchcenter.org/ · [OPEN 200].
62. **Institutional slavery reports** · Princeton Theological Seminary "Princeton Seminary and Slavery" (https://ptsem.edu/princeton-seminary-and-slavery/) [OPEN 200, title only]; Southern Baptist Theological Seminary "Report on Slavery and Racism in the History of SBTS" (https://www.sbts.edu/history/southern-project/) [OPEN 200, title only]; Georgetown Slavery Archive (https://slaveryarchive.georgetown.edu/) [WAYBACK] 2026-10-23 · Evidence of the church-as-perpetrator side; relevant to trust erosion.
63. **Black Press Research Collective** · https://blackpressresearchcollective.org/ · [OPEN 200, title only].
64. **NHGIS** (county census boundaries and tables, 1790–) · https://www.nhgis.org/ · [WAYBACK] 2026-10-10 (live Cloudflare). Needed to merge ARDA church counts with slave population shares.

---

## C. Brazil and the Caribbean

65. **Slave Societies Digital Archive (SSDA; formerly Ecclesiastical and Secular Sources for Slave Societies)** · Vanderbilt University (Jane Landers) · Seen: "more than 700,000 digital images dating from the sixteenth through twentieth centuries that document the lives of an estimated four to six million individuals"; "the most extensive serial records for the history of Africans in the Atlantic World"; transcriptions linked to images · Catholic baptism, marriage and burial registers of Africans and Afro-descendants (Brazil, Cuba, Colombia, Florida and elsewhere [country list not read]) — lets the researcher measure sacramental participation, godparent choice and brotherhood membership where the church was both slaveholders' and enslaved people's institution · Free · https://www.slavesocieties.org/ · [OPEN 200]. Review: Schneider 2020, *AHR* [DOI] 10.1093/ahr/rhz750. Project article on Petrópolis diocese archives: de Oliveira & Barbosa 2010, *Comma* [DOI] 10.3828/comma.2010.2.09.
66. **Slave Biographies — Maranhão dataset** · see item 46.
67. **Arquivo Público do Estado da Bahia (APEB)** · Fundação Pedro Calmon · Seen: "custodiar um acervo documental … produzido … ao longo de 214 anos, período em que a cidade do Salvador foi sede do Governo-Geral do Estado do Brasil (1549–1763)" · Colonial and provincial records incl. testaments, manumissions, irmandade papers [series not checked] · On site; partial online · https://www.ba.gov.br/fpc/arquivo-publico · [OPEN 200].
68. **Hemeroteca Digital Brasileira** · Biblioteca Nacional · https://bndigital.bn.gov.br/hemeroteca-digital/ · [WAYBACK] 2026-09-18 (live Cloudflare 403); docreader host https://memoria.bn.gov.br/ returns 200 with a near-empty body. [Digitized 19th-century newspapers incl. Catholic and abolitionist press — verify.]
69. **Afro-Ásia** (journal, CEAO-UFBA) · Seen: open-access issues (latest published 2025-12-29) · Publishes edited documents on Afro-Brazilian religion and irmandades · https://periodicos.ufba.br/index.php/afroasia · [OPEN 200].
70. **Digitarq** (Portuguese national archives portal, incl. Arquivo Histórico Ultramarino holdings) · https://digitarq.arquivos.pt/ · [OPEN 200, title only].
71. **Biblioteca Brasiliana Guita e José Mindlin (USP) digital collection** · https://digital.bbm.usp.br/handle/bbm/1 · [OPEN 200, title only].
72. **Atlas Digital da América Lusa** (UnB) · https://lhs.unb.br/atlas/ · [OPEN 200, title only].
73. **Endangered Archives Programme** (British Library) · Seen: homepage only; search for irmandade/Cuba projects returned a bot challenge (202) · https://eap.bl.uk/ · [OPEN 200, title only].
74. **Digital Library of the Caribbean / UF Digital Collections** · https://dloc.com/ · [OPEN 200, title only] (search is a JS app; cabildo holdings not confirmed).
75. **Legacies of British Slavery** (UCL) · https://www.ucl.ac.uk/lbs/ · [WAYBACK] 2026-10-31 (live Cloudflare). [Compensation records incl. clergy and church bodies as slave-owners — verify.]

---

## D. Taiwan

76. **台灣基督長老教會 (PCT) website — 重要文獻 (important documents)** · Seen: paginated list (10+ pages) of the General Assembly's public statements with years; first page shows 2010–2015 items (e.g., 台灣國是會議宣言 2010; 2012 選後呼籲; 2015 回應朱習會) · The PCT's political statements (1971 國是聲明, 1975 我們的呼籲, 1977 人權宣言 — [not seen on the first page; verify they are on later pages]) are the institutional voice of a church that sided with the sufferers under martial law · Free · https://www.pct.org.tw/ab_doc.aspx · [OPEN 200]. Individual document pages (ab_doc.aspx?DocID=…) returned HTTP 500.
77. **台灣教會公報 / Taiwan Church News Network** · Seen on "關於我們": founded 12 June 1885 by Thomas Barclay as 《台灣府城教會報》, "台灣第1份報紙", recording church news plus political, military and social events (1885 schools, 1887 province, 1894–95 war) · Continuous church press across Qing, Japanese, KMT martial-law and democratic eras; site has a "歷史" category and keyword search (e.g., 白色恐怖) · Current site free; historical run access [verify] · https://tcnn.org.tw/ (about: https://tcnn.org.tw/about) · [OPEN 200].
78. **賴永祥長老史料庫 (Elder John Lai's Archives)** · Seen: "dedicated to the study of the history of Christianity in Taiwan with special emphasis on the Presbyterian Church in Taiwan"; full text of 《教會史話》(7 series), sections 本土信徒, **原住民信徒**, **PCT原住民宣教**, PCT 地方教會, 宣教師一覽表, 馬偕的周邊 · Biographical and congregational histories that can be coded for conversion timing, 228 victims among church members, and Indigenous mission after 1945 · Free · http://www.laijohn.com/ · [OPEN 200].
79. **臺灣白話字文獻館** (Taiwanese Romanized-script documents) · NTNU · http://pojbh.lib.ntnu.edu.tw/ · live 503; [WAYBACK] 2024-08-08. [Digitized POJ church publications incl. early 府城教會報 — verify.]
80. **國家檔案資訊網** (National Archives Administration, NDC) · Seen: 二二八 keyword statistics — 28,745 catalogue entries, of which "228事件" 24,154 and "重大政治事件" 1,453; 3,212,755 full-text image pages public; 28,385,310 pages digitized; filter for 政治檔案 · Government files on 228 and political cases, incl. surveillance of churches [church-specific files not checked] · Registration/application for many files · https://aa.archives.gov.tw/ · [OPEN 200].
81. **臺灣轉型正義資料庫** (Taiwan Transitional Justice Database; National Human Rights Museum) · Seen: 9,915 cases; period 1945-08-15 to 1992-11-06; fields: name, sex, birth year, native place, prosecuting/trial bodies, sentences, judgment numbers, **occupation category**; mean age ~30 · Allows coding of clergy, seminarians and church workers among political defendants (e.g., the 1979–80 Formosa/Kaohsiung case) — measures church exposure to state violence · Free search · https://twtjdb.nhrm.gov.tw/ · [OPEN 200].
82. **國家人權記憶庫** (National Human Rights Memory Bank) · Seen: browse by 人物, 事件, 空間, 文物, 史料, 口述紀錄 for victims of 1945–1992; featured judgments · Oral histories of victims and families — religious coping and church support/abandonment · Free · https://memory.nhrm.gov.tw/ · [OPEN 200].
83. **不義遺址資料庫** (Sites of Injustice) · https://hsi.nhrm.gov.tw/nhrm/zh-tw · [OPEN 200, title only]. Also NHRM's 白色恐怖文學目錄資料庫 (https://wtl.nhrm.gov.tw/home/zh-tw — link seen, not opened).
84. **國史館 Academia Historica** · https://www.drnh.gov.tw/ · [OPEN 200, title only]; its archive system https://ahonline.drnh.gov.tw/ redirects (302) to a JS landing page. [228 and political-case archives — verify.]
85. **二二八事件紀念基金會 / 二二八國家紀念館** · https://www.228.org.tw/ · [OPEN 200, title only].
86. **臺灣史檔案資源系統** (Institute of Taiwan History archives, Academia Sinica) · Seen: catalogue search by 題名, 團體名稱, 家族名稱, 個人名稱, 地理名稱, scope 單件/案卷/系列/全宗 · Private papers (family, mission, local elite) · Free search; some items restricted · https://tais.ith.sinica.edu.tw/ · [OPEN 200].
87. **Taiwan Social Change Survey (TSCS, 臺灣社會變遷基本調查)** · Institute of Sociology, Academia Sinica; data via SRDA · Seen on download page: religion modules in 1985 and 1990 (宗教、休閒、家庭), 1994 (宗教), 1999 (宗教), 2004 (宗教文化), 2009 (宗教與文化), 2014 (宗教與文化), 2018 (七期四次 宗教與文化), 2023 (宗教, file tscs232), and 九期四次 (2028) 宗教 planned · Repeated cross-sections over martial-law end, democratization and present; religion modules carry affiliation, practice and (in some waves) trust/confidence items [item list not checked] · Questionnaires free; microdata via SRDA membership · https://www2.ios.sinica.edu.tw/sc/cht/scDownload2.php · [OPEN 200]. TSCS also listed as a collection on ARDA ("Taiwan Social Change Surveys") [OPEN 200].
88. **SRDA 學術調查研究資料庫** · Academia Sinica · Seen: TSCS, 家庭動態調查, 臺灣傳播調查 etc.; member application required · https://srda.sinica.edu.tw/ · [OPEN 200].
89. **Presbyterian Church in Canada Archives** · Toronto · Seen: exhibit "150 Years of George Leslie Mackay in Taiwan" · Northern Taiwan mission (Mackay) records [series not checked] · https://presbyterianarchives.ca/ · [OPEN 200].
90. **台南神學院** (Tainan Theological College and Seminary, founded 1869) · Seen: 黃彰輝紀念圖書館 named on page · [Seminary library holds PCT historical materials — verify] · https://www.ttcs.org.tw/ · [OPEN 200].
91. **原住民族委員會 — 原住民人口數統計資料 (monthly)** · https://www.cip.gov.tw/zh-tw/news/data-list/940F9579765AC6A0/index.html · [OPEN 200, title only]. Population denominators for Indigenous church data (no religion variable seen).
92. **原住民族文化事業基金會** · https://www.ipcf.org.tw/ · [OPEN 200, title only].
93. **臺灣記憶 Taiwan Memory** (National Central Library) · https://tm.ncl.edu.tw/index · [OPEN 200, title only].

---

## E. Contemporary religion surveys and statistics

94. **General Social Survey (GSS)** · NORC · https://gss.norc.org/ · [OPEN 200, title only]; GSS Data Explorer [WAYBACK] 2026-10-07. [Includes "confidence in organized religion" (CONCLERG) since 1973 — verify variable name.]
95. **World Values Survey** · Seen: waves 1 (1981–84) to 7 (2017–22), WVS/EVS Trend 1981–2022, wave 8 under way · Confidence in churches + importance of God across countries — tests the divergence between belief and institutional trust · Free with registration · https://www.worldvaluessurvey.org/ · [OPEN 200].
96. **European Values Study** · https://europeanvaluesstudy.eu/ · [OPEN 200, title only].
97. **ISSP Religion modules** · Seen on issp.org "by topic": Religion 1991, 1998, 2008, 2018; "Planned: … 2028 Religion V" · Confidence in churches, belief, attendance, religious upbringing · Free via GESIS (registration) · https://issp.org/data-download/by-topic/ · [OPEN 200]. GESIS module page Cloudflare-blocked.
98. **Pew Research Center datasets** · Seen: "2023-24 Religious Landscape Study (RLS) Dataset … public-use file" · Free with registration · https://www.pewresearch.org/religion/datasets/ · [OPEN 200].
99. **Gallup, Confidence in Institutions** · Seen: "The Church or Organized Religion" — great deal/quite a lot 33% (2026), 36% (2025), 32% (2024), 42% (2020) · Annual trend of institutional trust · Free tables · https://news.gallup.com/poll/1597/confidence-institutions.aspx · [OPEN 200].
100. **EKD Kirchenmitgliederstatistik** · Seen: 17,392,072 members on 31.12.2025 across 20 Landeskirchen and >11,000 congregations · Free · https://www.ekd.de/statistik-kirchenmitglieder-17279.htm · [OPEN 200].
101. **KMU 6 — Kirchenmitgliedschaftsuntersuchung 2023** · EKD (with Catholic participation [verify]) · Seen: 5,282 respondents, 592 questions; series since 1972 every ten years · Reasons for leaving, trust in church after abuse revelations · https://kmu.ekd.de/ · [OPEN 200].
102. **fowid — Forschungsgruppe Weltanschauungen in Deutschland** · Seen: pages "Kirchenaustritte: Wer, wann und warum", "Kirchenaustritte 2024", "Kirchenaustritte und Kirchensteuereinnahmen", "Nicht-Religiöse und Religiöse, 1982–2018" · Compiled church-exit series · Free · https://fowid.de/ · [OPEN 200].
103. **Deutsche Bischofskonferenz — Kirche in Zahlen** · https://www.dbk.de/kirche-in-zahlen · [WAYBACK] 2026-04-17 (live bot check 401).
104. **ARDA — church-abuse opinion polls** · Seen in ARDA's survey list: "ABC News Church Abuse, 2004", "ABC News Church in Crisis Poll, 2002", "ABC News Church Scandal Poll, 2002", "ABC News Priests and Pedophilia Poll, 2002" · Rare microdata on trust after institutional scandal (suffering caused *by* the church) · Free · https://www.thearda.com/ · [OPEN 200].
105. **Mill, Ebert, Berkessel, Gebauer, Lehmann, Jonsson — replication package, "On the Causal Effect of War on Religiosity: Gravestone Evidence from the Vietnam Draft Lottery"** · Harvard Dataverse (2026-10-20) · Seen: anonymized data and R code reproducing every result · Quasi-experimental evidence on collective suffering (war) and religiosity · Open · https://doi.org/10.7910/DVN/QIHXAE · [API].
106. **New Zealand Attitudes and Values Study** · University of Auckland · https://www.psych.auckland.ac.nz/en/about/new-zealand-attitudes-and-values-study.html · [OPEN 200, title only]. [Panel covering the Christchurch earthquakes — verify access.]
107. **U.S. Religion Census** · https://www.usreligioncensus.org/ · [OPEN 200, title only].
108. **National Congregations Study** · https://www.nationalcongregationsstudy.org/ · [OPEN 200, title only].
109. **CARA (Georgetown) Catholic statistics FAQ** · https://cara.georgetown.edu/faqs · [OPEN 200, title only].
110. **Churches North and South 2014 Congregational and Clergy Studies** · Harvard Dataverse (doi:10.7910/DVN/YFHMU3, doi:10.7910/DVN/8BTHIM) · seen in search results only (titles) · [API]. Brazil/US comparison [content not read].

---

## Counts

- Numbered entries: 110 (some bundle several resources).
- Content actually seen (OPEN 200 with text, or repository API metadata): 59 entries (1, 3–8, 10, 13–14, 21–25, 27, 32, 34, 36–38, 40, 42–43, 46, 48–49, 52–57, 59–61, 65, 67, 69, 76–78, 80–82, 86–90, 95, 97–102, 104–105).
- Existence only (title-only 200, DOI, or Wayback snapshot): 51 entries, flagged in each entry.
- Unconfirmed leads (below): 34.

## Top 10 rare datasets for this project

1. **Slave Societies Digital Archive** (700,000+ images of Catholic sacramental registers of Afro-descendants). It is the only serial, person-level record of slaves' participation in a church that was also the slaveholders' church. It lets Brazil/Cuba separate "power position" from "church role", which the US case confounds.
2. **Taiwan Transitional Justice Database** (9,915 political cases, 1945–1992, with occupation). It gives a person-level measure of state violence that can flag clergy and church workers. Link it to PCT statements and congregational histories.
3. **TSCS religion modules 1985–2023 (2028 planned)**. Nine repeated cross-sections span martial law's end, democratization and the PCT's political prominence. Microdata are on SRDA.
4. **Elder John Lai's Archives (laijohn.com)**. This free corpus of PCT congregational and biographical history includes Indigenous believers and Indigenous mission sections. It can be coded for the timing of post-1945 Indigenous conversion and for 228/White Terror victims among church members.
5. **Digitized Biraben outbreaks (Zenodo 14973), with the Krauer–Schmid NLP re-extraction and Bauch–Büntgen 2025 supplements.** These give town-year plague and famine exposure. Use the Roosen–Curtis critique as a mandatory bias check.
6. **York Archbishops' Registers** (21,500+ images, 26,132 indexed entries, 1225–1650). Ordinations, institutions, chantries and wills across 1348–49 and 1361–62 make it possible to measure devotion-through-the-institution and institutional strain in one series.
7. **Calendar of Papal Registers vol. 3 (1342–1362) and the Court of Husting wills (BHO).** They pair papal grace-seeking (petitions, indulgences, dispensations for clerical shortage) with lay testamentary piety in London.
8. **Doten-Snitker expulsions dataset (500+ polities, 1385–1520) with the Gingerich–Vogler Black Death outbreak files.** These are ready-made polity- and district-level data for the scapegoating branch and for later Reformation exit.
9. **ARDA Census of Religious Bodies county files (1890–1936), with the Methodist Episcopal conference minutes on IA.** These measure how far Black Christianity moved into Black-controlled denominations after emancipation (the Fountain timing problem). The minutes give the annual pre-1865 baseline [check that "colored" membership columns are present in the volumes used].
10. **The Christian Recorder (IA, 1864–1886 volumes) with Last Seen's information-wanted ads.** The AME press served as the institution freed people trusted to rebuild families. It is direct evidence of "faith up, own-church up".

Runners-up: Fisk *God Struck Me Dead* (conversion narratives); Slave Biographies' Maranhão dataset (Brazil–Louisiana with one schema); National Archives 228 files (24,154 catalogue entries); KMU 6 and fowid church-exit series; ARDA ABC News church-abuse polls.

## Unconfirmed leads (could not open; do not cite as verified)

1. Chiffoleau's Avignon testament sample (*La comptabilité de l'au-delà*, 1980) as a machine-readable dataset — not found.
2. Samuel K. Cohn's testament samples (six Tuscan/Umbrian cities) as data — not found.
3. Robinson's ordination data (Coventry & Lichfield, 1322–1358; Crossref shows his 1985 article in *Archives*, DOI 10.3828/archives.1985.1, and a 2016 chapter, but no "2019 ordination dataset").
4. Florence confraternity archives (Archivio di Stato di Firenze, Compagnie religiose soppresse; Henderson) — not checked online.
5. Society for Confraternity Studies website (confraternitas.ca) — timeout, no Wayback snapshot.
6. Germania Judaica database (current status; only a 2016 snapshot).
7. Regesta Imperii (live bot-check page only).
8. Voigtländer & Voth (2012) replication files — location not verified.
9. Jedwab, Johnson & Koyama (2019 JEG) persecution replication files — location not verified.
10. Finley & Koyama; Anderson, Johnson & Koyama — data locations not verified.
11. Original Biraben card-file / INED holdings — not checked.
12. Alfani's broader Italian plague database (beyond the 1630 package) — not found.
13. Avignon papal registers (Lettres communes editions; Brepols "Ut per litteras apostolicas" URL returned 404).
14. BHO Fasti 1300–1541 coverage of all twelve volumes — only vol. 1 opened.
15. CCEd content — offline (static rebuild in progress).
16. SlaveVoyages "African Origins"/names database — app not readable.
17. Christian Recorder on Accessible Archives (URL now redirects to Coherent Digital 404).
18. Smithsonian Transcription Center Freedmen's Bureau project — live 403.
19. FamilySearch Freedmen's Bureau collections (wiki URL 404).
20. Digitized Virginia Baptist biracial church minute books — not seen.
21. SBHLA digitized church minutes — specific items not seen.
22. AME Church archives / Mother Bethel archives (motherbethel.org opened, archive holdings not seen).
23. Cuban cabildo records (dLOC search is JS; EAP search blocked).
24. EAP projects on Brazilian irmandades and Cuban parish records — not seen.
25. Irmandade *compromissos* digitized by the Biblioteca Nacional / AHU (Projeto Resgate host returns an empty page).
26. Moravian Caribbean mission diaries and SPG/Codrington records (Bodleian bot check).
27. PCT Archives (台灣基督長老教會歷史資料館, Tainan) — no official web page found.
28. Full digitized run of 台灣府城教會報/台灣教會公報 (1885–) — not found online.
29. 台灣宗教資料庫 / religion.ios.sinica.edu.tw — timeout, no Wayback.
30. 原住民族綜合調查 microdata on SRDA (religion variables) — not found.
31. 台灣教會增長報告 (church growth statistics) — not found on CCEA site.
32. Yushan Theological College and Taiwan Theological Seminary archives — timeouts.
33. 全國宗教資訊網 (religion.moi.gov.tw) — timeout.
34. Ireland CSO Census 2022 religion tables (URL 404); DBK *Kirchliche Statistik* tables (bot check); GESIS ISSP pages (Cloudflare); Bottan & Perez-Truglia (abuse scandals) and Bentzen ("Acts of God") replication files — not located.
