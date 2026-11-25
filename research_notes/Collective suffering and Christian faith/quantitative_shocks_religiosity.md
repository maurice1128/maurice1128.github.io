# Quantitative and Social-Science Evidence on Collective Shocks, Religiosity, Religious Institutions, and Religious Persecution (priority: Black Death and historical plague)

How the notes were checked (read this first):
- **Bibliographic data.** I checked every DOI, volume, issue and page range below against Crossref metadata (api.crossref.org), and most against OpenAlex as well. Each entry's DOI link resolves to the publisher record.
- **Findings.** Abstracts were read from OpenAlex, IDEAS/RePEc, Europe PMC, PLoS, NBER or Pew pages. Several findings come from the full text of open-access working papers or published PDFs: Jedwab, Johnson & Koyama 2017 (MPRA WP), Jedwab, Johnson & Koyama 2020 (IIEP WP of the JEL survey), and Dittmar & Meisenzahl 2020 (open-access ReStud PDF).
- **[unverified] tags.** A claim is marked [unverified] when I could not open a source that confirms it.
- **Search budget.** The shared WebSearch budget for this session ran out partway through. After that I used only direct page fetches and DOI or metadata lookups for works I already knew to look for. As a result, some subtopics (Rwanda, Holocaust survivors, Hurricane Katrina, enslaved-African-American church statistics) have thinner coverage. These are flagged under Gaps.

---

## 1. Black Death and historical plague: persecution, religious institutions, the Reformation and secularization

### Takeaway
The economics literature treats the Black Death (1347–52) as a plausibly exogenous mortality shock. Its main causal findings about religion concern **persecution of the religious minority (Jews)** rather than Christian religiosity itself. Scapegoating raised the baseline probability of pogroms. Yet within the set of cities that had Jewish communities, *higher* mortality *lowered* the probability of persecution, because economic complementarities mattered more when labor was scarce. Political fragmentation and ecclesiastical lordship intensified pogroms, and medieval pogroms predict 1920s–30s Nazi-era antisemitism. On the institutional Church, the leading synthesis (Jedwab, Johnson & Koyama 2022, JEL) concludes that the plague contributed to "a decline in the authority of religious institutions". Its evidence for this is mostly historiographical, not causal estimation. The most rigorous causal plague–Reformation link is Dittmar & Meisenzahl (2020): plague outbreaks in 1500–1522 raised the probability that a German city adopted a Protestant church ordinance by about 14 percentage points per outbreak.

### Cited Findings

**A. Black Death and Jewish persecution**

- **Jedwab, Remi, Noel D. Johnson, and Mark Koyama. 2019. "Negative Shocks and Mass Persecutions: Evidence from the Black Death." *Journal of Economic Growth* 24 (4): 345–95. https://doi.org/10.1007/s10887-019-09167-1.**
  - **Design and data.** City-level data on Black Death mortality and Jewish persecutions in Western Europe. In the working-paper version: of 1,869 cities, 363 had a Jewish community in 1347 and 263 localities have mortality estimates. The main sample is the intersection, 124 cities.
  - **Identification.** OLS with geographic and institutional controls, plus two instruments. The first is market access to Messina (the plague's entry port), conditional on access to all cities. The second is the number of months between a city's infection date and October 1347. The authors check pre-trends: before 1347, persecutions did not differ between high- and low-mortality cities. — [IDEAS abstract](https://ideas.repec.org/a/kap/jecgro/v24y2019i4d10.1007_s10887-019-09167-1.html); [MPRA WP 78630, 2017](https://mpra.ub.uni-muenchen.de/78630/1/MPRA_paper_78630.pdf)
  - **Finding (published abstract).** "Negative shocks increase the likelihood that minorities are persecuted. But, as shocks become more severe, the persecution probability decreases if there are economic complementarities between majority and minority groups … cities which experienced higher plague mortality were less likely to persecute." For a given mortality shock, persecutions were more likely where people were more inclined to believe conspiracy theories blaming Jews, and less likely where Jews played an important economic role. — [IDEAS](https://ideas.repec.org/a/kap/jecgro/v24y2019i4d10.1007_s10887-019-09167-1.html)
  - **Numbers (2017 WP; may differ from the published version).** About half of cities with a Jewish community persecuted it. The baseline constant is 0.831, so the average probability of persecution was very high. The mortality coefficient is −0.009, meaning a 1 SD (≈0.18) rise in mortality goes with a 0.34 SD fall in persecution probability. Non-parametrically, persecution probability rises to about 0.8 at 20% mortality and then falls toward 0 at 80% mortality. — [MPRA WP](https://mpra.ub.uni-muenchen.de/78630/1/MPRA_paper_78630.pdf)
  - **Religious-calendar mechanism (WP).** The protective effect of high mortality was weaker in cities first infected in January or April–May (Epiphany and Easter, when Christians were "inclined to blame Jews for the death of Jesus"). It was stronger for December or February–March (Advent and Lent penance seasons). — [MPRA WP](https://mpra.ub.uni-muenchen.de/78630/1/MPRA_paper_78630.pdf)
  - **Relevance.** Collective suffering channeled through Christian religious frames (liturgical seasons, blood libels) shaped *who* was blamed. This supports framing religion as a meaning-making system that can turn suffering outward.

- **Finley, Theresa, and Mark Koyama. 2018. "Plague, Politics, and Pogroms: The Black Death, the Rule of Law, and the Persecution of Jews in the Holy Roman Empire." *Journal of Law and Economics* 61 (2): 253–77. https://doi.org/10.1086/699016.**
  - **Design.** Data on pogrom intensity, historical trade routes, and ecclesiastical and political boundaries in the Holy Roman Empire.
  - **Finding.** "Communities close to Archbishoprics, Bishoprics, and Imperial Free cities experienced more intense and violent persecutions than did those governed by the emperor." The authors argue that political fragmentation worsened rent-seeking. — [OpenAlex abstract](https://api.openalex.org/works/doi:10.1086/699016)
  - **Relevance.** Proximity to *ecclesiastical* lordship predicted more violent persecution. This is evidence that Church institutions were implicated in shock-induced violence, which bears on later institutional distrust.

- **Anderson, Robert Warren, Noel D. Johnson, and Mark Koyama. 2017. "Jewish Persecutions and Weather Shocks: 1100–1800." *Economic Journal* 127 (602): 924–58. https://doi.org/10.1111/ecoj.12331.**
  - **Design.** Panel of 1,366 city-level persecutions of Jews in 936 European cities, 1100–1800, matched to reconstructed growing-season temperature.
  - **Finding.** "A one standard deviation decrease in average growing season temperature increased the probability of a persecution between one-half and one percentage points (relative to a baseline probability of two percent)." The effect was strongest with poor soil quality or weak states. The authors attribute the long-run decline in persecution after 1500 partly to rising state fiscal and legal capacity. — [OpenAlex abstract](https://api.openalex.org/works/doi:10.1111/ecoj.12331)

- **Voigtländer, Nico, and Hans-Joachim Voth. 2012. "Persecution Perpetuated: The Medieval Origins of Anti-Semitic Violence in Nazi Germany." *Quarterly Journal of Economics* 127 (3): 1339–92. https://doi.org/10.1093/qje/qjs019.** (NBER WP 17113, 2011.)
  - **Design.** Uses plague-era (1348–50) pogroms as an indicator of local medieval antisemitism in German towns.
  - **Finding.** These pogroms "reliably predict violence against Jews in the 1920s, votes for the Nazi Party, deportations after 1933, attacks on synagogues, and letters to *Der Stürmer*". Persistence was lower in cities with high trade or immigration. — [Crossref abstract](https://doi.org/10.1093/qje/qjs019); [NBER w17113](https://www.nber.org/papers/w17113)
  - **Gap.** I could not verify effect-size magnitudes; neither the NBER page nor the abstract gives them.
  - **Relevance.** Plague-induced religious hostility persisted for about 600 years, a canonical cultural-persistence result.

- **Cohn, Samuel K., Jr. 2007. "The Black Death and the Burning of Jews." *Past & Present* 196 (1): 3–36. https://doi.org/10.1093/pastj/gtm005.**
  - **Type.** Historical, not econometric.
  - **Content.** Describes the 1348–51 burnings as "the most monumental of medieval Jewish persecutions", which eradicated the principal Rhineland communities. He argues the social character of the persecutors (who ordered and led them, and why) "remains hypothetical". — [OpenAlex](https://api.openalex.org/works/doi:10.1093/pastj/gtm005)
  - **Relevance.** The standard historical counterpart cited by Jedwab, Johnson & Koyama.

- **Becker, Sascha O., and Luigi Pascali. 2019. "Religion, Division of Labor, and Conflict: Anti-Semitism in Germany over 600 Years." *American Economic Review* 109 (5): 1764–1804. https://doi.org/10.1257/aer.20170279.**
  - **Design.** Data on more than 1,000 German cities.
  - **Finding.** After the Reformation (1517), persecutions of Jews and anti-Jewish publications became more common in Protestant than in Catholic areas, especially where Jews had been moneylenders. The mechanism: Protestants were not bound by the Catholic usury ban, so they competed with Jews in moneylending. — [Crossref abstract](https://doi.org/10.1257/aer.20170279)

- **Johnson, Noel D., and Mark Koyama. 2019. *Persecution and Toleration: The Long Road to Religious Freedom*. Cambridge: Cambridge University Press. https://doi.org/10.1017/9781108348102.**
  - **Type.** Book combining economic reasoning and historical evidence, from the fall of Rome to the present. — [OpenAlex](https://api.openalex.org/works/doi:10.1017/9781108348102)
  - **Use in the JEL survey.** Jedwab, Johnson & Koyama (2022) cite pp. 110–12 for the claim that the plague's universality and the "inability of religious leaders to offer protection" called the Church's legitimacy into question. — [IIEP WP version of JEL survey](http://www2.gwu.edu/~iiep/assets/docs/papers/2020WP/JedwabIIEP2020-14.pdf)

**B. Black Death, religious institutions, clergy, and dissent**

- **Jedwab, Remi, Noel D. Johnson, and Mark Koyama. 2022. "The Economic Impact of the Black Death." *Journal of Economic Literature* 60 (1): 132–78. https://doi.org/10.1257/jel.20201639.**
  - **Abstract.** Treats the plague as a plausibly exogenous shock. Among its long-run effects it lists "the demise of serfdom in western Europe, a decline in the authority of religious institutions, and the emergence of stronger states". — [Crossref abstract](https://doi.org/10.1257/jel.20201639)
  - **Section 4.5, "How Did the Plague Impact Religious Institutions?" (WP version).** Contents:
    - Clergy were "disproportionately hard hit", citing Christakos et al. 2005, 133–38, with "a shortage of trained clergy for decades". English chroniclers in the 1360s described churches "left unserved and empty through lack of priests".
    - Flagellant movements lay outside Church control.
    - The Pope declared a 1350 Jubilee in response.
    - "The universal nature of the plague and the inability of religious leaders to offer protection for it called into question the legitimacy of the Church."
    - Quoting Green (2014, 255): "the impact of the Black Death seemed only to confirm the failures of the institutional Church. What emerged to fill the spiritual vacuum was a vibrant lay piety that, in time, encouraged further reform."
    - Organic collective piety (processions, fasts, prayer) arose alongside. Dissenting movements followed: Lollards, Hussites, and the Brethren of the Common Life. These are described as prefiguring the Reformation.
    - The survey says the Black Death "was not associated with any saints" despite priests' self-sacrifice. — [IIEP WP 2020-14](http://www2.gwu.edu/~iiep/assets/docs/papers/2020WP/JedwabIIEP2020-14.pdf)
  - **Relevance.** This is **the key citation for the "dual effect" in the Black Death case**: institutional legitimacy eroded while lay piety intensified. Note, however, that the survey supports this with historiography, not with causal estimates.
  - **Craft guilds.** The same survey reports that Richardson (2005, *Rationality and Society* 17: 139–89) and Richardson & McBride (2009, *Journal of Economic Behavior & Organization* 71 (2): 172–86) argue that post-plague craft guilds bundled religious services (prayers for souls in purgatory) with economic cooperation. — [IIEP WP](http://www2.gwu.edu/~iiep/assets/docs/papers/2020WP/JedwabIIEP2020-14.pdf). These citations come from the JEL reference list; I did not open the Richardson papers [unverified beyond the reference list].

- **Jedwab, Remi, Noel D. Johnson, and Mark Koyama. 2024. "Pandemics and Cities: Evidence from the Black Death and the Long-Run." *Journal of Urban Economics* 139: 103628. https://doi.org/10.1016/j.jue.2023.103628.**
  - Bibliographic data verified via Crossref. No abstract was retrievable [content unverified].
  - Its SSRN predecessors are "Bones, Bacteria and Break Points" (2016, https://doi.org/10.2139/ssrn.2800002) and "Pandemics, Places, and Populations" (2019, https://doi.org/10.2139/ssrn.3343855). The links between these versions are inferred from title evolution and are [unverified].

**C. Plague and the Protestant Reformation and secularization**

- **Dittmar, Jeremiah E., and Ralf R. Meisenzahl. 2020. "Public Goods Institutions, Human Capital, and Growth: Evidence from German History." *Review of Economic Studies* 87 (2): 959–96. https://doi.org/10.1093/restud/rdz002.**
  - **Design.** German cities that adopted Protestant church ordinances (from 1522) mandating public goods: schooling, poor relief, and audited "common chests" for church income.
  - **Identification.** Plague outbreaks in 1500–1522 serve as an instrument for adoption, controlling for plague frequency in 1350–1499.
  - **Finding.**
    - "Each additional plague outbreak between 1500 and 1522 increases the propensity of adopting a law by 14 percentage points." The F-statistic on the excluded instrument is above 34.
    - A city with an ordinance by 1600 was 1.61 log points larger in 1800.
    - The proposed mechanism: "Plagues weakened incumbent elites and increased demand for public goods institutions." Religious and political publications (ideological competition) rose where plagues struck. — [open-access published PDF](https://researchonline.lse.ac.uk/id/eprint/91195/3/Dittmar_public_goods_institutions_published.pdf); [OpenAlex abstract](https://api.openalex.org/works/doi:10.1093/restud/rdz002)
  - **Relevance.** This is the cleanest causal evidence that **epidemic shocks accelerated institutional religious change** (the Protestant takeover of Church functions and assets) in the Reformation era.

- **Cantoni, Davide, Jeremiah Dittmar, and Noam Yuchtman. 2018. "Religious Competition and Reallocation: The Political Economy of Secularization in the Protestant Reformation." *Quarterly Journal of Economics* 133 (4): 2037–96. https://doi.org/10.1093/qje/qjy011.** (NBER WP 23934, 2017.)
  - **Design.** Novel microdata on monastery closures, university graduates' occupations, students' fields of study, and construction.
  - **Finding.**
    - Secular authorities "acquired enormous amounts of wealth from monasteries closed during the Reformation, particularly in Protestant regions".
    - Protestant university graduates shifted to secular, especially administrative, occupations, and students shifted from theology to secular subjects.
    - New construction shifted from religious to secular buildings (palaces, administrative buildings).
    - The reallocation was "not driven by preexisting economic or cultural differences", and the Reformation "played an important causal role in the secularization of the West". — [OpenAlex abstract](https://api.openalex.org/works/doi:10.1093/qje/qjy011)
  - **Gap.** I could not verify the specific magnitudes (shares of theology students and so on).

- **Becker, Sascha O., Steven Pfaff, and Jared Rubin. 2016. "Causes and Consequences of the Protestant Reformation." *Explorations in Economic History* 62: 1–25. https://doi.org/10.1016/j.eeh.2016.07.007.** A review of individual-, city- and region-level quantitative research on the adoption, diffusion and consequences of the Reformation. — [IDEAS abstract](https://ideas.repec.org/a/eee/exehis/v62y2016icp1-25.html)

- **Rubin, Jared. 2014. "Printing and Protestants: An Empirical Test of the Role of Printing in the Reformation." *Review of Economics and Statistics* 96 (2): 270–86. https://doi.org/10.1162/rest_a_00368.** Instruments for printing with distance from Mainz. Cities with at least one press by 1500 were "at minimum 29 percentage points more likely to be Protestant by 1600." — [OpenAlex](https://api.openalex.org/works/doi:10.1162/rest_a_00368)

- **Rubin, Jared. 2017. *Rulers, Religion, and Riches: Why the West Got Rich and the Middle East Did Not*. Cambridge: Cambridge University Press. https://doi.org/10.1017/9781139568272.** Bibliographic data verified via Crossref. The book's thesis (that religious legitimation of rulers declined in Protestant Europe) is from my prior knowledge and is [unverified here].

- **Ekelund, Robert B., Jr., Robert F. Hébert, and Robert D. Tollison. 2002. "An Economic Analysis of the Protestant Reformation." *Journal of Political Economy* 110 (3): 646–71. https://doi.org/10.1086/339721.**
  - **Argument.** Models the medieval Church as a monopolist whose price discrimination in "spiritual services" pushed members "on the margin of defection". Protestant entry was easier in entrepreneurial societies marked by the decline of feudalism.
  - **Evidence.** Only informal tests, using primogeniture and urban growth. — [OpenAlex](https://api.openalex.org/works/doi:10.1086/339721)
  - **Relevance.** A supply-side, anticlerical-demand account that complements the Black Death and legitimacy narrative.

- **Pfaff, Steven, and Katie E. Corcoran. 2012. "Piety, Power, and the Purse: Religious Economies Theory and Urban Reform in the Holy Roman Empire." *Journal for the Scientific Study of Religion* 51 (4): 757–76. https://doi.org/10.1111/j.1468-5906.2012.01680.x.**
  - **Design.** Systematic city-level analysis of reform adoption in the Holy Roman Empire.
  - **Finding.** "Mixed support for demand-side factors and entry control mechanisms, and firm support for political incentives." — [OpenAlex](https://api.openalex.org/works/doi:10.1111/j.1468-5906.2012.01680.x)
  - **Relevance.** A **JSSR precedent** for quantitative Reformation work.

- **Becker, Sascha O., Jared Rubin, and Ludger Woessmann. 2021. "Religion in Economic History: A Survey." In *The Handbook of Historical Economics*, edited by Alberto Bisin and Giovanni Federico, 585–639. London: Academic Press/Elsevier. https://doi.org/10.1016/B978-0-12-815874-6.00029-0.** Pages and DOI were verified via Crossref. The editors' names are from my knowledge and are [unverified].

- **Becker, Sascha O., Jared Rubin, and Ludger Woessmann. 2024. "Religion and Growth." *Journal of Economic Literature* 62 (3): 1094–1142. https://doi.org/10.1257/jel.20231666.** Frames religion's effects through physical capital, human capital, labor and TFP, including "rituals, legal institutions, political economy, and conflict." — [OpenAlex](https://api.openalex.org/works/doi:10.1257/jel.20231666)

- **Becker, Sascha O., and Ludger Woessmann. 2009. "Was Weber Wrong? A Human Capital Theory of Protestant Economic History." *Quarterly Journal of Economics* 124 (2): 531–96. https://doi.org/10.1162/qjec.2009.124.2.531.** Bibliographic data verified via Crossref; background only.

**D. Plague's economic effects (context for mechanisms)**

- **Alfani, Guido, and Tommy E. Murphy. 2017. "Plague and Lethal Epidemics in the Pre-Industrial World." *Journal of Economic History* 77 (1): 314–43. https://doi.org/10.1017/S0022050717000092.** Survey of plagues from late Antiquity to about 1800. "Apparently similar epidemics could have deeply different consequences" depending on environmental and institutional factors. — [Crossref abstract](https://doi.org/10.1017/S0022050717000092)

- **Alfani, Guido, and Marco Percoco. 2019. "Plague and Long-Term Development: The Lasting Effects of the 1629–30 Epidemic on the Italian Cities." *Economic History Review* 72 (4): 1175–1201. https://doi.org/10.1111/ehr.12652.** New plague-mortality data for 56 cities, c. 1575–1700. Severely hit cities were displaced to a lower growth path. — [Crossref abstract](https://doi.org/10.1111/ehr.12652)

- **Alfani, Guido. 2022. "Epidemics, Inequality, and Poverty in Preindustrial and Early Industrial Times." *Journal of Economic Literature* 60 (1): 3–40. https://doi.org/10.1257/jel.20201640.** The distributive outcomes of epidemics are "mediated by a range of factors, chief among them the institutional framework in place at the onset of each crisis." — [Crossref abstract](https://doi.org/10.1257/jel.20201640)
  - **Relevance.** A methodological warning against assuming one uniform shock effect, which suits a "sometimes intensifies, sometimes erodes" argument.

**E. Other historical natural experiments: shocks raising religious authority**

- **Belloc, Marianna, Francesco Drago, and Roberto Galbiati. 2016. "Earthquakes, Religion, and Transition to Self-Government in Italian Cities." *Quarterly Journal of Economics* 131 (4): 1875–1926. https://doi.org/10.1093/qje/qjw020.**
  - **Design.** Panel of northern-central Italian cities, 1000–1300, with earthquake data.
  - **Finding.**
    - Earthquakes *retarded* the transition to communal self-government in episcopal-see cities (where the political and religious leader was the same person) but not in other cities.
    - The effect holds even for earthquakes "felt by the population but did not cause any material damage."
    - Earthquakes differentially raised the construction and ornamentation of religious buildings in episcopal sees.
    - Interpretation: earthquakes, read as "manifestation of the will and outrage of God", were a shock to religious beliefs that strengthened political-religious leaders. — [Crossref abstract](https://doi.org/10.1093/qje/qjw020)
  - **Relevance.** Strong causal evidence that disasters *raised* the authority of religious institutions in a medieval Christian setting. This is a useful contrast with the Black Death's legitimacy-eroding effect.

- **Chaney, Eric. 2013. "Revolt on the Nile: Economic Shocks, Religion, and Political Power." *Econometrica* 81 (5): 2033–53. https://doi.org/10.3982/ECTA10233.**
  - **Design.** Centuries of Nile flood data.
  - **Finding.**
    - During deviant floods, Egypt's highest religious authority (the chief judge) was less likely to be replaced, and allocations to religious structures increased.
    - But "deviant floods did not increase a proxy for popular religiosity."
    - Economic downturns raised the *political* power of religious leaders through their ability to coordinate revolt. — [OpenAlex](https://api.openalex.org/works/doi:10.3982/ECTA10233)
  - **Relevance.** Separates *institutional* power from *popular* religiosity, which is directly useful for the dual-effect framing.

### Inferences
- The economics of the Black Death supports three religion-related channels:
  1. Scapegoating and persecution of religious out-groups, moderated by economic complementarity and political structure.
  2. A legitimacy shock to the institutional Church (clergy mortality, failure of intercession, schism) coinciding with intensified lay piety. This is mostly historiographical in the JEL survey.
  3. Over a longer horizon, plague as a trigger for institutional religious change in the Reformation era (Dittmar & Meisenzahl's 1500–1522 plague instrument).
- Belloc et al. (earthquakes strengthen episcopal rulers) and Chaney (floods strengthen religious authority but not popular religiosity) show that a shock's effect on institutions depends on whether religious leaders can credibly claim to explain or mitigate it. The Black Death's universality and its high clergy mortality plausibly undercut that claim. This is my synthesis, not a tested result.
- The non-monotonic result in Jedwab, Johnson & Koyama (2019) suggests a general template: moderate suffering intensifies religiously framed blame, while extreme suffering shifts incentives toward material survival.

### Gaps
- I found no causal study that directly estimates Black Death mortality's effect on *Christian* religiosity, clerical recruitment, monastic vocations, donations or bequests to the Church, or later Protestant adoption at the city level. The only causal plague–Reformation link I verified is Dittmar & Meisenzahl's 1500–1522 plague instrument. Search was cut short (budget exhausted) before I could check for newer papers, for example on Black Death mortality and Reformation adoption, clerical quality after 1348, or chantry and bequest data.
- Heldring, Robinson & Vollmer, "The Long-Run Impact of the Dissolution of the English Monasteries", appears in the JEL reference list as a June 2020 working paper. Its final publication venue is [unverified].
- Akçomak, Webbink & ter Weel (2016) on the Brethren of the Common Life is cited in the JEL survey as quantitative work. I did not verify its bibliographic details.
- Effect-size magnitudes for Voigtländer & Voth 2012 and for Cantoni, Dittmar & Yuchtman 2018 were not retrieved.

---

## 2. Disasters, epidemics and religiosity: causal and quasi-experimental evidence

### Takeaway
A consistent body of causal economics work finds that unpredictable collective shocks raise religiosity. Earthquakes raise individual religiosity (Bentzen 2019). COVID-19 raised prayer-search intensity by 30% globally (Bentzen 2021). War exposure raised religious-group and ritual participation (Henrich et al. 2019). Agricultural risk and floods increased church membership in the 19th- and 20th-century US (Ager & Ciccone 2018; Ager, Hansen & Lønstrup). Economic crisis raised Islamic religious intensity in Indonesia (Chen 2010). Two mechanisms recur and are hard to separate: **psychological coping** and **mutual (club-good) insurance**. Results are not uniform. In Canada, disaster frequency and costs *eroded* religious preferences, while human losses intensified them among the already religious (Zapata 2018). Panel evidence after 9/11 showed only modest, short-lived effects (Uecker 2008).

### Cited Findings
- **Bentzen, Jeanet Sinding. 2019. "Acts of God? Religiosity and Natural Disasters across Subnational World Districts." *Economic Journal* 129 (622): 2295–2321. https://doi.org/10.1093/ej/uez008.**
  - **Design.** Combines a global individual-level religiosity dataset with spatial earthquake data across subnational districts.
  - **Finding.**
    - "Individuals become more religious if an earthquake recently hit close by."
    - The effect decays over time, but "data on children of immigrants reveal a persistent effect across generations."
    - Religious coping is "the main mediating channel," although "mutual insurance or migration cannot be ruled out entirely." — [Crossref abstract](https://doi.org/10.1093/ej/uez008)
  - **Gap.** I did not retrieve exact coefficients or dataset sizes.

- **Bentzen, Jeanet Sinding. 2021. "In Crisis, We Pray: Religiosity and the COVID-19 Pandemic." *Journal of Economic Behavior & Organization* 192: 541–83. https://doi.org/10.1016/j.jebo.2021.10.014.**
  - **Design.** Daily and weekly Google search data for 107 countries.
  - **Finding.**
    - Prayer searches relative to all searches rose 30% in the early pandemic, "the highest level ever recorded."
    - By 1 April 2020, more than half the world's population had prayed to end the coronavirus (back-of-envelope estimate).
    - Prayer searches stayed 10% higher than before throughout 2020, especially in Europe and the Americas.
    - The rise held across income, inequality and insecurity levels and for all religions except Buddhism.
    - The rise "is not merely a substitute for services in the physical churches that closed down." — [IDEAS](https://ideas.repec.org/a/eee/jeborg/v192y2021icp541-583.html); [Europe PMC](https://europepmc.org/search?query=DOI:10.1016/j.jebo.2021.10.014)

- **Sibley, Chris G., and Joseph Bulbulia. 2012. "Faith after an Earthquake: A Longitudinal Study of Religion and Perceived Health before and after the 2011 Christchurch New Zealand Earthquake." *PLoS ONE* 7 (12): e49648. https://doi.org/10.1371/journal.pone.0049648.**
  - **Design.** New Zealand Attitudes and Values Study panel, 2009 and 2011 waves. N = 3,745 analysed; 501 lived in Canterbury and 801 were personally affected.
  - **Finding.**
    - Canterbury showed "a net increase of 3.4% in religious faith," while faith nationally declined by about 0.9% per year (χ²(3, N = 3740) = 12.39, p = .006).
    - Religious faith gave no superior buffering of self-rated health.
    - Earthquake-affected *apostates* showed health declines. — [PLoS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0049648)
  - **Relevance.** A pre/post panel inside a secularizing society. The shock both converted some people and was followed by apostasy among others, which is direct micro evidence for divergent responses.

- **Henrich, Joseph, Michal Bauer, Alessandra Cassar, Julie Chytilová, and Benjamin Grant Purzycki. 2019. "War Increases Religiosity." *Nature Human Behaviour* 3 (2): 129–35. https://doi.org/10.1038/s41562-018-0512-3.**
  - **Design.** Surveys of 1,709 individuals in Uganda, Sierra Leone and Tajikistan, exploiting quasi-random intensity of war exposure.
  - **Finding.**
    - People with greater war exposure "were more likely to participate in Christian or Muslim religious groups and rituals, even several years after the conflict."
    - The result is robust to comparisons within the same communities, ethnic groups and religions. — [Europe PMC abstract](https://europepmc.org/search?query=DOI:10.1038/s41562-018-0512-3)
  - **Relevance.** The closest causal analogue for collective violent trauma (relevant to slavery and genocide), and it includes Christian participants.

- **Ager, Philipp, and Antonio Ciccone. 2018. "Agricultural Risk and the Spread of Religious Communities." *Journal of the European Economic Association* 16 (4): 1021–68. https://doi.org/10.1093/jeea/jvx029.**
  - **Design.** Uses common rainfall risk in 19th-century US counties, holding expected agricultural output constant.
  - **Finding.**
    - "A greater share of the population was organized in religious communities in counties with greater common agricultural risk."
    - The effect is stronger in more agricultural counties and with growing-season rainfall risk.
    - More than one-third of the 19th-century differences persist to the turn of the 21st century. — [OpenAlex](https://api.openalex.org/works/doi:10.1093/jeea/jvx029)
  - **Relevance.** Shows a 19th-century American church-membership response to insecurity, consistent with the insurance mechanism.

- **Ager, Philipp, Casper Worm Hansen, and Lars Lønstrup. 2016. "Church Membership and Social Insurance: Evidence from the Great Mississippi Flood of 1927." Discussion Papers on Business and Economics 7/2016, University of Southern Denmark. https://doi.org/10.2139/ssrn.2862290.** (Earlier version: "… Evidence from the American South," University of Copenhagen Discussion Paper 14-29, 2014, https://doi.org/10.2139/ssrn.2533411.)
  - **Finding.**
    - "A significant increase in church membership in flooded counties," stronger where economic losses were severe and credit access was limited.
    - "Fundamental denominations gained more members," consistent with club-goods theory. — [EconPapers](https://econpapers.repec.org/RePEc:hhs:sdueko:2016_007); [EconPapers 2014](https://econpapers.repec.org/RePEc:kud:kuiedp:1429)
  - **Relevance.** Covers the American South, the region of the slavery case. Whether it was later published in a journal is [unverified]. The coefficient sizes were not retrieved.

- **Chen, Daniel L. 2010. "Club Goods and Group Identity: Evidence from Islamic Resurgence during the Indonesian Financial Crisis." *Journal of Political Economy* 118 (2): 300–354. https://doi.org/10.1086/652462.**
  - **Design.** Relative price shocks from the 1997–98 Indonesian financial crisis.
  - **Finding.**
    - Economic distress caused increased religious intensity (Koran study, Islamic school attendance).
    - Credit availability reduced this effect.
    - Religious institutions smoothed consumption, especially for those less religious before the crisis. — [OpenAlex](https://api.openalex.org/works/doi:10.1086/652462)

- **Dehejia, Rajeev, Thomas DeLeire, and Erzo F. P. Luttmer. 2007. "Insuring Consumption and Happiness through Religious Organizations." *Journal of Public Economics* 91 (1–2): 259–79. https://doi.org/10.1016/j.jpubeco.2006.05.004.**
  - **Data.** Consumer Expenditure Survey (CEX) and National Survey of Families and Households (NSFH).
  - **Finding.**
    - Religious contributors insured consumption against income shocks, with "strong insurance effects for whites."
    - Religious attendance insured *happiness* against income shocks, with "strong happiness insurance effects for blacks but smaller effects for whites." — [IDEAS](https://ideas.repec.org/a/eee/pubeco/v91y2007i1-2p259-279.html)
  - **Relevance.** Directly relevant to the African American case. It suggests that the Black church's buffering role is psychological and communal more than financial.

- **Auriol, Emmanuelle, Julie Lassébie, Amma Panin, Eva Raiber, and Paul Seabright. 2020. "God Insures Those Who Pay? Formal Insurance and Religious Offerings in Ghana." *Quarterly Journal of Economics* 135 (4): 1799–1848. https://doi.org/10.1093/qje/qjaa015.**
  - **Design.** RCT enrolling Pentecostal church members in Ghana in funeral insurance.
  - **Finding.**
    - Insured members gave significantly less to their church in dictator games.
    - The insurance is "derived from beliefs in an interventionist God," alongside material community insurance. — [OpenAlex](https://api.openalex.org/works/doi:10.1093/qje/qjaa015)

- **Zapata, Oscar. 2018. "Turning to God in Tough Times? Human versus Material Losses from Climate Disasters in Canada." *Economics of Disasters and Climate Change* 2 (3): 259–81. https://doi.org/10.1007/s41885-018-0029-2.**
  - **Design.** Canadian provinces, 1992–2012, with an instrumental-variables approach.
  - **Finding.**
    - "The number and the economic costs of disasters erode religion preferences."
    - Among religious individuals, "human losses increase the intensity of their religious preferences." — [IDEAS](https://ideas.repec.org/a/spr/ediscc/v2y2018i3d10.1007_s41885-018-0029-2.html)
  - **Correction.** The brief's speculative "Zapata on disasters and Catholicism in Latin America" does not match a paper I could verify. The verified Zapata paper is about **Canada**.
  - **Relevance.** Explicit evidence of **divergent effects** by type of loss and by prior religiosity.

- **Molteni, Francesco, Riccardo Ladini, Ferruccio Biolcati, Antonio M. Chiesi, Giulia Maria Dotti Sani, Simona Guglielmi, Marco Maraffi, Andrea Pedrazzani, Paolo Segatti, and Cristiano Vezzoni. 2021. "Searching for Comfort in Religion: Insecurity and Religious Behaviour during the COVID-19 Pandemic in Italy." *European Societies* 23 (sup1): S704–20. https://doi.org/10.1080/14616696.2020.1836383.**
  - **Design.** ResPOnsE COVID-19 rolling cross-section survey.
  - **Finding.**
    - Italians with a COVID-19 contagion in the family reported higher attendance at religious services (via web, radio and TV) and more prayer.
    - The effect held "primarily for those who received religious socialization during their childhood."
    - "A short-term religious revival is possible" even amid secularization. — [OpenAlex](https://api.openalex.org/works/doi:10.1080/14616696.2020.1836383)

- **Boguszewski, Rafał, Marta Makowska, Marta Bożewicz, and Monika Podkowińska. 2020. "The COVID-19 Pandemic's Impact on Religiosity in Poland." *Religions* 11 (12): 646. https://doi.org/10.3390/rel11120646.**
  - **Design.** April 2020 quota online sample, N = 1,001.
  - **Finding.**
    - 21.3% spent more time praying or practising.
    - Among those who previously practised several times a week, 61.3% increased.
    - Increases were also seen among those who had practised once every few years (15.9%) and never (7.4%).
    - New increases among irregular practitioners were associated with job-loss fear. — [OpenAlex](https://api.openalex.org/works/doi:10.3390/rel11120646)

- **Uecker, Jeremy E. 2008. "Religious and Spiritual Responses to 9/11: Evidence from the Add Health Study." *Sociological Spectrum* 28 (5): 477–509. https://doi.org/10.1080/02732170802206047.**
  - **Design.** Panel data from the National Longitudinal Study of Adolescent Health.
  - **Finding.** 9/11 had "only modest and short-lived effects" on young adults' religiosity and spirituality, varying by group; "no remarkable religious revival occurred." — [OpenAlex](https://api.openalex.org/works/doi:10.1080/02732170802206047)

### Inferences
- Effects are strongest and most persistent where the shock is unpredictable or lethal, where formal insurance and credit are weak, and where people were religiously socialized before the shock. This fits historical Black Death Europe and the antebellum South better than modern welfare states.
- Several studies (Ager–Hansen–Lønstrup, Chen, Dehejia et al.) find that strict or "fundamental" groups gain most. That is consistent with evangelical Baptist and Methodist growth among enslaved and freed African Americans. This is an inference by analogy, not a tested link.

### Gaps
- Quantitative studies of Hurricane Katrina's effect on religiosity *levels*: I verified only Chan, Rhodes & Pérez (2012), which looks at religiousness as a *buffer* (see section 4), not as an outcome.
- Further disaster-religiosity studies may exist that I could not locate after the search budget ran out (for example, the 2004 tsunami, Japan 2011, or Latin American earthquakes).

---

## 3. Existential security / insecurity theory and its critiques

### Takeaway
Norris & Inglehart's existential-security thesis (insecurity sustains religiosity; security erodes it) is strongly supported at the **macro** level. Multilevel tests find individual- and contextual-insecurity effects on both attendance and private religiosity (Ruiter & van Tubergen 2009; Immerzeel & van Tubergen 2013; Storm 2017). However, Höllinger & Muckenhuber (2019) find that individual life conditions and threatening experiences have "only a very small impact" at the micro level. Welfare-state substitution (Gill & Lundsgaarde 2004) offers a rational-choice alternative mechanism.

### Cited Findings
- **Norris, Pippa, and Ronald Inglehart. 2004. *Sacred and Secular: Religion and Politics Worldwide*. Cambridge: Cambridge University Press. https://doi.org/10.1017/CBO9780511791017. 2nd ed., 2011, https://doi.org/10.1017/CBO9780511894862.**
  - The 2nd edition "develops a theory of existential security."
  - It argues religiosity "persists most strongly among vulnerable populations, especially in poorer nations and in failed states," while "a systematic erosion of religious practices, values and beliefs has occurred among the more prosperous strata in rich nations." — [OpenAlex (2nd ed.)](https://api.openalex.org/works/doi:10.1017/cbo9780511894862)

- **Inglehart, Ronald F. 2021. *Religion's Sudden Decline: What's Causing It, and What Comes Next?* New York: Oxford University Press. https://doi.org/10.1093/oso/9780197547045.001.0001.**
  - "From 1981 to 2007, most countries became more religious, but from 2007 to 2020, the overwhelming majority became less religious."
  - Religion spread because it "encouraged sharing when there was no social security system, and is conducive to mental health and coping with insecure conditions."
  - Erosion of pro-fertility norms is the proposed driver of decline. — [OpenAlex](https://api.openalex.org/works/doi:10.1093/oso/9780197547045.001.0001)

- **Ruiter, Stijn, and Frank van Tubergen. 2009. "Religious Attendance in Cross-National Perspective: A Multilevel Analysis of 60 Countries." *American Journal of Sociology* 115 (3): 863–95. https://doi.org/10.1086/603536.**
  - **Data.** European/World Values Surveys, 60 nations.
  - **Finding.**
    - Religious regulation diminishes attendance.
    - Education has only small negative effects.
    - "Religious attendance is strongly affected by personal and societal insecurities," by religious socialization and by urbanization.
    - These theories together "explain 75% of the cross-national variation." — [OpenAlex](https://api.openalex.org/works/doi:10.1086/603536)

- **Immerzeel, Tim, and Frank van Tubergen. 2013. "Religion as Reassurance? Testing the Insecurity Theory in 26 European Countries." *European Sociological Review* 29 (2): 359–72. https://doi.org/10.1093/esr/jcr072.**
  - **Data.** European Social Survey 2002–2008, 26 countries.
  - **Design.** Separates *public* (attendance) from *private* (subjective) religiosity.
  - **Finding.** "Strong support" for insecurity theory. Religiosity is higher among those with insecure jobs, unemployed or low-status parents, those who experienced war in their country, and those who lost a partner, and in countries with lower welfare spending and higher unemployment. — [OpenAlex](https://api.openalex.org/works/doi:10.1093/esr/jcr072)
  - **Relevance.** Personal *war experience* predicts religiosity, and the study measures public and private religiosity separately, which is useful for the dual-effect framing.

- **Storm, Ingrid. 2017. "Does Economic Insecurity Predict Religiosity? Evidence from the European Social Survey 2002–2014." *Sociology of Religion* 78 (2): 146–72. https://doi.org/10.1093/socrel/srw055.**
  - **Data.** ESS, 31 countries, 7 waves.
  - **Finding.**
    - Lower income, lower GDP and lower welfare availability predict more religiosity.
    - Rising welfare expenditure reduced country-level religiosity over 12 years.
    - Religious people feel more economically secure regardless of income, which supports "religious stress buffering." — [OpenAlex](https://api.openalex.org/works/doi:10.1093/socrel/srw055)

- **Höllinger, Franz, and Johanna Muckenhuber. 2019. "Religiousness and Existential Insecurity: A Cross-National Comparative Analysis on the Macro- and Micro-Level." *International Sociology* 34 (1): 19–37. https://doi.org/10.1177/0268580918812284.**
  - **Data.** World Values Survey wave 6 (2010–14).
  - **Finding.** There is a strong macro-level correlation between better life conditions and lower religiousness, but "individual life conditions and threatening experiences, however, have only a very small impact on religiousness." — [Crossref abstract](https://doi.org/10.1177/0268580918812284)
  - **Relevance.** The key micro-level critique.

- **Gill, Anthony, and Erik Lundsgaarde. 2004. "State Welfare Spending and Religiosity: A Cross-National Analysis." *Rationality and Society* 16 (4): 399–436. https://doi.org/10.1177/1043463104046694.** As governments take over welfare functions historically provided by churches, people with elastic demand for spiritual goods reduce participation. There is a "strong negative relationship" between welfare spending and participation after modernization controls. — [OpenAlex](https://api.openalex.org/works/doi:10.1177/1043463104046694)

- **Kay, Aaron C., Danielle Gaucher, Jamie L. Napier, Mitchell J. Callan, and Kristin Laurin. 2008. "God and the Government: Testing a Compensatory Control Mechanism for the Support of External Systems." *Journal of Personality and Social Psychology* 95 (1): 18–35. https://doi.org/10.1037/0022-3514.95.1.18.** Experiments show that lowered personal control causally raises belief in "a controlling God." Across 67 nations, lower personal control is associated with higher support for governmental control. — [OpenAlex](https://api.openalex.org/works/doi:10.1037/0022-3514.95.1.18)
  - **Relevance.** A psychological microfoundation for the macro insecurity thesis.

- **Iyer, Sriya. 2016. "The New Economics of Religion." *Journal of Economic Literature* 54 (2): 395–441. https://doi.org/10.1257/jel.54.2.395.** Bibliographic data verified via Crossref; this is a survey for background.

### Inferences
- For a JSSR review, the macro/micro discrepancy (Höllinger & Muckenhuber) and the public/private split (Immerzeel & van Tubergen) are the main critiques of insecurity theory.
- Insecurity theory predicts a level shift. It does not by itself predict *which* institution gains. The substitution and scandal literature (section 6) fills that gap.

### Gaps
- I did not verify specific critiques of Norris & Inglehart from religious-economies scholars (for example, Stark and Finke responses, or Voas). The search budget was exhausted.

---

## 4. Religious coping after collective trauma (9/11, disasters, war, genocide, Holocaust)

### Takeaway
Immediate reliance on religion after collective trauma is very common: 90% of US adults reported "turning to religion" after 9/11. Pre-existing religiousness buffers distress through optimism and purpose (Katrina and Rita survivors) and through positive religious coping (the 1993 flood). Longer-run *changes* in religiosity are often modest (Uecker 2008), except where trauma is severe and prolonged, as with war (Henrich et al. 2019).

### Cited Findings
- **Schuster, Mark A., Bradley D. Stein, Lisa H. Jaycox, Rebecca L. Collins, Grant N. Marshall, Marc N. Elliott, Annie J. Zhou, David E. Kanouse, Janina L. Morrison, and Sandra H. Berry. 2001. "A National Survey of Stress Reactions after the September 11, 2001, Terrorist Attacks." *New England Journal of Medicine* 345 (20): 1507–12. https://doi.org/10.1056/NEJM200111153452024.**
  - **Design.** Random-digit-dial survey 3–5 days after 9/11, N = 569 US adults.
  - **Finding.**
    - 44% reported one or more substantial stress symptoms.
    - They coped by talking with others (98%), "turning to religion (90 percent)," group activities (60%) and donations (36%). — [OpenAlex abstract](https://api.openalex.org/works/doi:10.1056/nejm200111153452024)

- **Chan, Christian S., Jean E. Rhodes, and John E. Pérez. 2012. "A Prospective Study of Religiousness and Psychological Distress among Female Survivors of Hurricanes Katrina and Rita." *American Journal of Community Psychology* 49 (1–2): 168–81. https://doi.org/10.1007/s10464-011-9445-y.**
  - **Design.** 386 low-income, predominantly Black single mothers enrolled *before* the hurricanes.
  - **Finding.** Pre-disaster religiousness predicted higher post-disaster social resources and higher optimism and sense of purpose. Only optimism and purpose mediated better psychological outcomes. — [OpenAlex](https://api.openalex.org/works/doi:10.1007/s10464-011-9445-y)
  - **Relevance.** Concerns African American Christian women, so it is relevant to the slavery-era analogue.

- **Smith, Bruce W., Kenneth I. Pargament, Curtis Brant, and Joan M. Oliver. 2000. "Noah Revisited: Religious Coping by Church Members and the Impact of the 1993 Midwest Flood." *Journal of Community Psychology* 28 (2): 169–86. https://doi.org/10.1002/(SICI)1520-6629(200003)28:2<169::AID-JCOP5>3.0.CO;2-I.**
  - **Design.** 209 church members at 6 weeks after the flood and 131 at 6 months.
  - **Finding.** Religious attributions and coping predicted psychological *and religious* outcomes, controlling for exposure. Positive religious coping may mediate the effect of religious dispositions. — [OpenAlex](https://api.openalex.org/works/doi:10.1002/(sici)1520-6629(200003)28:2%3C169::aid-jcop5%3E3.0.co;2-i)

- **Henrich et al. 2019 (war).** See section 2. Participation effects persisted "several years after the conflict." — [Europe PMC](https://europepmc.org/search?query=DOI:10.1038/s41562-018-0512-3)

- **Immerzeel & van Tubergen 2013.** Having "experienced a war in their own country" predicts higher religiosity in ESS data. — [OpenAlex](https://api.openalex.org/works/doi:10.1093/esr/jcr072)

- **Brenner, Reeve Robert. 1980. *The Faith and Doubt of Holocaust Survivors*. New York: Free Press. Reissued 2017, London: Routledge. https://doi.org/10.4324/9781315131979.**
  - The existence of the 2017 Routledge edition, including a chapter "The Faith of Holocaust Survivors" (pp. 85–125), is verified via Crossref. — [Crossref](https://doi.org/10.4324/9781315131979)
  - The 1980 publisher, the survey design (a survey of survivors in Israel) and the findings are from my prior knowledge and are **[unverified]**. Do not cite numbers without checking the book.

### Inferences
- The coping literature mostly measures religion as a *buffer* rather than as an *outcome*. Studies that measure change in religiosity after trauma (Uecker; Sibley & Bulbulia; Henrich et al.) find effects ranging from modest to substantial depending on severity and duration.

### Gaps
- **Rwanda genocide survivors' religiosity.** I found no verified quantitative study; the search budget was exhausted before this was searched. Reviewers may expect literature on post-genocide shifts from the Catholic Church to Pentecostal and Adventist churches or to Islam, given clergy complicity. I could not verify it.
- **Holocaust survivors.** Only Brenner's book was located, and its contents are unverified.

---

## 5. Quantitative work on enslaved and freed African Americans' religion (1619–1877)

### Takeaway
I found little causal-inference work in economics on the religion of enslaved African Americans. The most relevant verified quantitative pieces are indirect:
- Southern US church membership responded to floods and risk (Ager & Ciccone; Ager, Hansen & Lønstrup).
- Religious attendance insures *happiness* more strongly for Black Americans (Dehejia et al. 2007).
- AME membership roughly tripled in the decade after emancipation, according to annual reports compiled in a secondary source.

### Cited Findings
- **AME membership statistics.** These come from a Wikipedia page, which is a secondary aggregator; the report writer should cite the underlying primary sources.
  - 1846: 17,375 members (no citation on the page).
  - 1856: about 20,000, "mainly in the North" (citing Campbell 1995 and Owens 2014).
  - 1866: about 70,000 (citing *The Annual Cyclopedia: 1866*, 1867, p. 492).
  - 1876: about 207,000 (citing *The Annual Cyclopedia: 1876*, 1877, p. 532).
  - The near-tripling from 1866 to 1876 follows directly from the 1866 and 1876 figures. — [Wikipedia, "African Methodist Episcopal Church"](https://en.wikipedia.org/wiki/African_Methodist_Episcopal_Church). [Primary sources unverified; check *Appletons' Annual Cyclopaedia* directly.]
- **Finke, Roger, and Rodney Stark. 2005. *The Churching of America, 1776–2005: Winners and Losers in Our Religious Economy*. New Brunswick, NJ: Rutgers University Press. https://doi.org/10.36019/9780813541136.** The existence of the edition is verified via Crossref (online 2020). Its specific statistics on Black Methodist and Baptist membership are **[unverified]**.
- **Dehejia, DeLeire & Luttmer 2007.** Religious attendance gives Black Americans strong *happiness* insurance against income shocks; for whites the insurance runs through consumption. — [IDEAS](https://ideas.repec.org/a/eee/pubeco/v91y2007i1-2p259-279.html)
- **Ager, Hansen & Lønstrup 2014/2016.** Church membership rose in flooded counties of the American South in 1927, with gains concentrated in "fundamental denominations." — [EconPapers](https://econpapers.repec.org/RePEc:hhs:sdueko:2016_007)
- **Stark, Rodney. 1996. *The Rise of Christianity: A Sociologist Reconsiders History*. Princeton, NJ: Princeton University Press. https://doi.org/10.1515/9780691214290.**
  - Bibliographic data verified via Crossref. Its chapter arguing that Christians' higher survival and nursing during the Antonine and Cyprianic epidemics drove conversion is from my prior knowledge and is **[unverified here]**.
  - **Relevance.** The classic sociological claim that epidemics *grow* Christianity through networks and differential survival.

### Inferences
- The economics of religion predicts that, under extreme insecurity and denial of formal institutions, people move toward strict, high-commitment, mutual-aid congregations. The post-emancipation surge of independent Black denominations (AME and Black Baptist conventions) is consistent with both the club-goods/insurance account and the account of exit from white-controlled institutions. This is my inference; no causal study was verified.

### Gaps
- I could not verify the following (search budget exhausted):
  - Census of Religious Bodies 1890/1906 figures for Black denominations.
  - Methodist Episcopal "colored members" series, 1790–1860.
  - Black Baptist totals around 1860 and 1890.
  - Quantitative studies of Great Awakening conversion rates among enslaved people.
- I found no economics or quantitative-sociology paper that uses causal inference on enslaved people's religiosity or on post-1865 Black church growth. Coverage here should rely on the historians who compiled denominational statistics (for example, Frey & Wood 1998; Walker 1982; Montgomery 1993; Lincoln & Mamiya 1990), all **[unverified in this session]**.

---

## 6. The "dual effect": shocks that raise private religiosity while lowering institutional trust or attendance (or vice versa)

### Takeaway
Several well-identified studies separate the **private/belief** dimension from the **institutional/participation** dimension:
- Black Death: institutional legitimacy fell while lay piety rose (historiographical; JEL 2022).
- COVID-19: prayer rose globally while in-person attendance collapsed (Bentzen 2021; Boguszewski et al. 2022). Polish evidence shows polarization.
- Church scandals: participation and giving fell without measurable change in beliefs (Bottan & Perez-Truglia 2015). Members switched to other denominations rather than leaving religion (Hungerman 2013).
- Nile floods: religious *authority's* power rose without a rise in *popular* religiosity (Chaney 2013).
- Christchurch: faith rose among the affected, while apostates' health declined (Sibley & Bulbulia 2012).

### Cited Findings
- **Bottan, Nicolas L., and Ricardo Perez-Truglia. 2015. "Losing My Religion: The Effects of Religious Scandals on Religious Participation and Charitable Giving." *Journal of Public Economics* 129: 106–19. https://doi.org/10.1016/j.jpubeco.2015.07.008.**
  - **Design.** Event study exploiting the spatial and temporal distribution of US Catholic clergy-abuse scandals at the zip-code level.
  - **Finding.**
    - A scandal causes "a significant and long-lasting decline in religious participation" locally.
    - It does "not generate a statistically significant decline in religious beliefs, pro-social beliefs."
    - It causes a long-lasting decline in charitable giving, "an order of magnitude larger than the direct costs of the scandals." — [IDEAS](https://ideas.repec.org/a/eee/pubeco/v129y2015icp106-119.html)
  - **Relevance.** The cleanest causal evidence that **institutional trust shocks reduce participation without eroding belief**, which is the dual effect in its purest form.

- **Hungerman, Daniel M. 2013. "Substitution and Stigma: Evidence on Religious Markets from the Catholic Sex Abuse Scandal." *American Economic Journal: Economic Policy* 5 (3): 227–53. https://doi.org/10.1257/pol.5.3.227.**
  - **Finding.**
    - The Catholic population fell, offset by gains in non-Catholic participation *and* in non-affiliation.
    - About $3 billion in donations shifted to non-Catholic faiths.
    - Baptist churches gained significantly; the Episcopal Church did not. — [Crossref abstract](https://doi.org/10.1257/pol.5.3.227)
  - **Relevance.** A shock that delegitimizes one church can *redirect* faith to stricter rivals, an analogue for Lollard, Hussite and Protestant entry after a Church legitimacy crisis.

- **Boguszewski, Rafał, Marta Makowska, and Monika Podkowińska. 2022. "Changes in Intensification of Religious Involvement during the COVID-19 Pandemic in Poland." *PLOS ONE* 17 (6): e0269015. https://doi.org/10.1371/journal.pone.0269015.**
  - **Design.** Two online surveys: N = 1,072 (November 2020) and N = 1,080 (April 2021).
  - **Finding.**
    - Institutional practice fell "threefold to 11.9%" from 31.2% before the pandemic.
    - Non-attenders rose from 23.1% to 57.0%.
    - More respondents reported a *decrease* (20.1%) than an *increase* (10.6%) in time spent praying.
    - Increases were predicted by older age and prior frequent practice; decreases by younger age and infrequent prior practice.
    - "The pandemic has accelerated process of polarization of Polish religiosity." — [OpenAlex](https://api.openalex.org/works/doi:10.1371/journal.pone.0269015)
  - **Relevance.** **Polarization** (the devout intensify and the marginal drift away) is a strong mechanism for "sometimes intensifies, sometimes erodes."

- **Pew Research Center. 2021. "More Americans Than People in Other Advanced Economies Say COVID-19 Has Strengthened Religious Faith." January 27, 2021.**
  - **Design.** Surveys of 14,276 adults in 14 advanced economies, 10 June to 3 August 2020.
  - **Finding.**
    - In the US, 28% said their own faith became stronger and 4% weaker.
    - The 14-country median was 10% stronger and 3% weaker.
    - In the US, 28% said the nation's faith strengthened and 14% said it weakened. — [Pew](https://www.pewresearch.org/religion/2021/01/27/more-americans-than-people-in-other-advanced-economies-say-covid-19-has-strengthened-religious-faith/)

- **Bentzen 2021.** Prayer intensity rose and stayed elevated even though "physical churches … closed down"; the rise is "not merely a substitute" for services. — [IDEAS](https://ideas.repec.org/a/eee/jeborg/v192y2021icp541-583.html)

- **Chaney 2013.** Nile shocks raised religious authorities' political power, but "deviant floods did not increase a proxy for popular religiosity." — [OpenAlex](https://api.openalex.org/works/doi:10.3982/ECTA10233)

- **Jedwab, Johnson & Koyama 2022 (JEL), Black Death.** Legitimacy of the institutional Church was "called into question," with "a vibrant lay piety" filling the "spiritual vacuum" (quoting Green 2014). — [IIEP WP](http://www2.gwu.edu/~iiep/assets/docs/papers/2020WP/JedwabIIEP2020-14.pdf)

- **Belloc, Drago & Galbiati 2016.** The opposite pattern: earthquakes *raised* religious leaders' institutional power and spending on religious buildings. — [Crossref abstract](https://doi.org/10.1093/qje/qjw020)

- **Zapata 2018.** The frequency and costs of disasters erode religious preferences overall, while human losses intensify religiosity among the religious. — [IDEAS](https://ideas.repec.org/a/spr/ediscc/v2y2018i3d10.1007_s41885-018-0029-2.html)

- **Immerzeel & van Tubergen 2013.** Insecurity raises *both* public (attendance) and private (subjective) religiosity in ESS data. In ordinary insecurity, then, the two dimensions move together; divergence seems to need an institution-specific shock. — [OpenAlex](https://api.openalex.org/works/doi:10.1093/esr/jcr072)

### Inferences
- A synthesis across the studies:
  - **Generalized insecurity raises both private and public religiosity** (insecurity theory; Bentzen; Henrich et al.; Ager et al.).
  - **Divergence arises when the shock also discredits or disables the institution.** The Church failed to protect, its clergy died, or it was complicit or scandal-hit (Black Death; abuse scandals). Or access to the institution was blocked (COVID closures).
  - **Where religious leaders can credibly interpret or mitigate the shock and control the response** (episcopal sees in Belloc et al.; Egyptian judges in Chaney), institutional power *rises*.
- For enslaved African Americans, this framework predicts intensified private Christian faith alongside distrust of white-controlled churches. The pathway would be exit to independent Black congregations after 1865 (AME membership roughly tripling between 1866 and 1876), analogous to Hungerman's substitution toward stricter rival denominations. This is an analogy, not a tested result.
- Prior religious socialization repeatedly moderates responses: Molteni et al. (childhood socialization), Boguszewski et al. (prior practice), Zapata (already religious), and Bentzen 2019 (persistence among children of immigrants). This supports a "polarization" rather than a uniform-shift model.

### Gaps
- I found no study that measures private belief and institutional trust *simultaneously* before and after a historical epidemic. The Black Death dual effect rests on historiography, not on measured outcomes.
- I did not verify survey-based evidence on trust in churches during COVID-19 (for example, Gallup confidence in organized religion) because of the search budget.
- Panel studies following religiosity among the same people over a full epidemic cycle, beyond the 2020–21 wave studies, were not located.
