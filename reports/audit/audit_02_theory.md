# Audit: section 2 (Theoretical frameworks) and its reference list

Audited files: `reports/sections/02_theory.md`, `reports/sections/02_theory_refs.md` (not edited).
Date: 2026-11-05. Auditor: independent fact-check (Claude).

Methods: Crossref REST API for all 58 DOIs in the list (metadata and, where deposited, abstracts); OpenAlex for JSTOR end pages and author order (the daily OpenAlex budget ran out partway through); Open Library and Crossref bibliographic search for books and entries without a DOI; web search for publisher pages, catalogue records and abstracts; the project's full-text notes (`research_notes/.../open_access_studies_fulltext.md`) for Ager & Ciccone, Bentzen 2021, Dittmar & Meisenzahl, Jedwab et al., Finley & Koyama and Voas & Chaves. JSTOR and PubMed returned bot challenges, so a few end pages rest on secondary catalogue records (marked).

Status codes: **OK** = verified as written; **FIX** = an error to correct; **ADD** = a detail is missing (fill-in); **NOTE** = acceptable but worth a nuance; **UNV** = could not be verified independently.

## Summary counts

| Item | Count |
|---|---|
| Reference entries checked | 100 |
| References: OK as written (including 7 whose "verify" flags this audit resolves) | 85 |
| References: missing from list (cited in text) | 1 (Nirenberg 1996) |
| References: pages or DOIs to add (ADD) | 12 entries |
| References: NOTE or UNV (Exline 2013 editors, Lincoln 1985 chapter, Lincoln 2003 year) | 3 |
| References: not found / fabricated | 0 |
| Core claims checked | 72 |
| Claims: OK | 58 |
| Claims: FIX (wrong or misattributed) | 4 |
| Claims: NOTE (imprecise or incomplete) | 8 |
| Claims: UNV | 2 |

No reference appears to be fabricated. Every DOI resolves to the stated work, with matching authors, year, volume, issue and first page.

## 1. Reference list

### 1a. Entries needing a change

| # | Entry | Status | Problem | Correction | Evidence |
|---|---|---|---|---|---|
| 1 | Nirenberg 1996 | **FIX (missing)** | Cited twice in text (§2.9 and the synthesis table) but absent from `02_theory_refs.md` | Add: Nirenberg, David. 1996. *Communities of Violence: Persecution of Minorities in the Middle Ages*. Princeton, NJ: Princeton University Press. (Same entry already in `04_black_death_refs.md`) | `04_black_death_refs.md` |
| 2 | Chaves 1994 | ADD | End page missing | *Social Forces* 72 (3): 749–74 (standard citation; JSTOR page blocked) | https://doi.org/10.2307/2579779 |
| 3 | Stark 1971 | ADD | End page missing | *Review of Religious Research* 12 (3): 165–76 | https://www.suicideinfo.ca/resource/siecno-19901095/ |
| 4 | Stark & Bainbridge 1979 | ADD | End page missing | *JSSR* 18 (2): 117–31 | https://relbib.de/Record/1642751537 |
| 5 | Granqvist 1998 | ADD | End page missing | *JSSR* 37 (2): 350–67 | reference lists citing it (Sage); Crossref start page 350 |
| 6 | Iannaccone 1990 | ADD | End page missing | *JSSR* 29 (3): 297–314 (standard citation; JSTOR blocked) | https://doi.org/10.2307/1386460 |
| 7 | Said 1986 | ADD / UNV | End page missing | *Grand Street* 5 (2): 86–106 (standard citation; not independently confirmed) | https://doi.org/10.2307/25006845 |
| 8 | Bourdieu 1971 | ADD | End page and English translation marked "verify" | 295–334 confirmed; English trans. "Genesis and Structure of the Religious Field," *Comparative Social Research* 13 (1991): 1–44, confirmed by several bibliographies | https://hirr.hartfordinternational.edu/articles/4167/ |
| 9 | Glock 1964 | ADD | Pages missing | In Lee and Marty, eds., *Religion and Social Conflict*, 24–36 | https://econbiz.de/Record/the-role-of-deprivation-in-the-origin-and-evolution-of-religious-groups-glock-charles/10002448376 |
| 10 | Weber 1946 | ADD | Chapter pages marked "verify" | Oxford edition: "The Social Psychology of the World Religions," 267–301 (confirmed in a citation of the OUP printing); "The Sociology of Charismatic Authority," 245–52 (standard; UNV). The "To verify" note's 279–313 is the Routledge reissue pagination and should not be used with the 1946 OUP imprint | catalogue/citation search |
| 11 | Kay et al. 2010; Frazier et al. 2009; Smith et al. 2000 | ADD | No DOI, unlike other journal entries | Kay: 10.1037/a0021140; Frazier: 10.1111/j.1467-9280.2009.02381.x; Smith: 10.1002/(SICI)1520-6629(200003)28:2<169::AID-JCOP5>3.0.CO;2-I. All other details match Crossref | Crossref bibliographic search |
| 12 | Exline 2013 | NOTE | "edited by Kenneth I. Pargament" | Pargament is editor-in-chief; vol. 1 associate editors are Julie J. Exline and James W. Jones. Crossref mislabels Exline as the chapter's editor; she is its author. Either form is acceptable; fuller: "edited by Kenneth I. Pargament, Julie J. Exline, and James W. Jones" | https://doi.org/10.1037/14045-025 |
| 13 | Erikson 1994 | OK (subtitle confirmed) | Subtitle marked "verify" | 1994 Norton hardcover: *Explorations in Disaster, Trauma, and Community* is correct. The 1995 paperback is subtitled *The Human Experience of Modern Disasters*; do not mix them | https://www.publishersweekly.com/9780393035940 |
| 14 | Kirkpatrick 2005 | OK | Open Library says 2004 | Library catalogues give c2005; Guilford's listing date is 18 Oct 2004. Keep 2005 | https://www.guilford.com/books/Attachment-Evolution-and-the-Psychology-of-Religion/Lee-Kirkpatrick/9781593850883 |
| 15 | Lincoln 1985 | UNV | Lincoln's own chapter not given | His chapter is "Notes toward a Theory of Religion and Revolution" (confirmed in the volume's contents). Pages not confirmed (recollection: 266–92). Cite the chapter, not only the edited volume | https://find.library.upenn.edu/catalog/991810893503681 |
| 16 | Lincoln 2003 | NOTE | Year | Crossref and Open Library give 2002 (released late 2002); the book carries ©2003. Either is defensible; a 2nd ed. appeared in 2006 | https://doi.org/10.7208/chicago/9780226481944.001.0001 |
| 17 | Dittmar & Meisenzahl 2020 | OK | Crossref lacks volume and pages | 87 (2): 959–96 confirmed from the published PDF in project notes | notes §1 |
| 18 | Voas, Olson & Crockett 2002 | OK | Crossref lists the authors as Voas, Crockett, Olson | OpenAlex and the article give Voas, Olson, Crockett, as in the entry. End page 230 (standard) | https://doi.org/10.2307/3088893 |
| 19 | Marx 1994 | OK (editor) / UNV (wording) | Editor marked "verify" | Joseph O'Malley (ed., with Richard A. Davis), Cambridge Texts in the History of Political Thought; Crossref confirms the chapter at pp. 57–70. For the quotation wording see claim C-24 | https://doi.org/10.1017/CBO9781139168007.007 |
| 20 | Morris 1984; Berger 1999 | OK | Publisher marked "verify" | Morris: Free Press, New York (Open Library). Berger: Eerdmans with the Ethics and Public Policy Center (Open Library: Eerdmans) | openlibrary.org |

### 1b. Entries verified as written (OK)

Crossref DOI metadata matches title, authors, year, volume(issue) and pages (or first page, for JSTOR DOIs) for:
Abu-Raiya et al. 2015; Ager & Ciccone 2018 (online 2017, print 2018); Alexander et al. 2004; Auriol et al. 2020; Bentzen 2019; Bentzen 2021; Chaves & Gorski 2001; Chen 2010; Cohn 2007; Davie 1990; Dehejia, DeLeire & Luttmer 2007; Dianteill 2003; Exline et al. 2014; Exline et al. 2011; Eyerman 2001; Finley & Koyama 2018; Frijters et al. 2024 (online 2023); Gill & Lundsgaarde 2004; Granqvist & Kirkpatrick 2004; Granqvist, Mikulincer & Shaver 2010; Greenberg et al. 1990; Höllinger & Muckenhuber 2019; Iannaccone 1992; Iannaccone 1994; Immerzeel & van Tubergen 2013 (online 2011); Jedwab, Johnson & Koyama 2019; Kay et al. 2008; Kirkpatrick & Shaver 1990 (315–34); Lang & Chvaja 2024; Lincoln 1985 (volume); Marwell 1996; Mitchell 1990; Molteni 2021; Morgan & Wilkinson 2001; Norris & Inglehart 2004; 2011; Páez et al. 2015; Pargament, Koenig & Perez 2000; Pargament et al. 1998 (710–24); Park 2010; Ruiter & van Tubergen 2009; Sætrevik & Sjåstad 2022; Schnabel & Schieman 2022 (online 2021); Shaw, Joseph & Linley 2005; Stark 1999; Tedeschi & Calhoun 2004; Vail et al. 2010 ("III" is the author's own usage); Voas & Crockett 2005.

Books checked through Open Library, Crossref or catalogues and found correct: Berger 1967; Bruce 2011; Casanova 1994; Collins 2004; Davie 1994; Durkheim 1995 (Fields trans.); Erikson 1976; Finke & Stark 1992; Fountain 2010; Genovese 1974; Girard 1982; 1986 (Freccero trans.); Granqvist 2020 (*A Wider View*, Guilford); Hirschman 1970; Lincoln 1989 (subtitle correct); Lincoln 1994; Martin 1978 (Harper & Row / Blackwell); McAdam 1982; Moore 1987; Pargament 1997; Raboteau 2004; Riesebrodt 2010; Scott 1990; Smith 1996 (Routledge); Stark & Bainbridge 1987 (Peter Lang; Rutgers 1996 reprint); Stark & Finke 2000; Taylor 2007; Walzer 1985 (Basic Books); Weber 1963 (Beacon); Weber 1978.

## 2. Claims

### 2a. Claims needing correction (FIX)

| ID | Location | Claim in text | Finding | Correction | Evidence |
|---|---|---|---|---|---|
| C-1 | §2.4 | "Stark (1971) found no link between psychopathology and religious commitment." | Wrong direction. Stark argued that the evidence weighs against the proposition, and his own data showed the relationship was the opposite of the received view: psychopathology was *negatively* related to religious commitment | "Stark (1971) found that psychopathology was, if anything, negatively related to religious commitment, the reverse of what deprivation theory assumed." | https://relbib.de/Record/182239466X ; https://hirr.hartfordinternational.edu/?p=4627 |
| C-2 | §2.9 | "Quantitative work finds persecution concentrated where states were weak or authority over Jews was contested (Jedwab, Johnson, and Koyama 2019; Finley and Koyama 2018)." | Misattribution to Jedwab et al. Their finding is that higher plague mortality *lowered* the probability of persecution where Jews were economically complementary, with scapegoating stronger where antisemitic priming existed (and the liturgical-calendar result). The weak-state or contested-authority result is Finley & Koyama 2018 (contested rights over Jews in the Empire) and, for weak states, Anderson, Johnson & Koyama 2017 (*Economic Journal* 127: 924–58) | "Persecution was most intense where authority over Jews was contested (Finley and Koyama 2018) and where states were weak (Anderson, Johnson, and Koyama 2017); it was less likely where plague mortality was higher and Jews were economically needed (Jedwab, Johnson, and Koyama 2019)." Add Anderson et al. 2017 to refs if used | project notes §2, §9, §10 |
| C-3 | §2.7 | "Lincoln (1985) distinguishes religions of the status quo, of resistance and of revolution." | Incomplete typology. Lincoln's scheme has a fourth type, religions of counterrevolution (status quo, resistance, revolution, counterrevolution); it is set out in the 1985 essay and restated in *Holy Terrors* | Add "and of counterrevolution". The counterrevolution type also suits the model (an establishment church allied with the perpetrators) | LibraryThing/Christian Century summaries of *Holy Terrors*; https://find.library.upenn.edu/catalog/991810893503681 |
| C-4 | §2.5 | "Bentzen (2019; 2021) refines the thesis: surprise matters more than need, and prior religiosity is the stock that crisis draws on." | Conflates two results. Bentzen 2021 says "the availability of religion as a coping tool seems to be more important than the 'need' for such a tool". The surprise result is separate: unexpected shocks raise religiosity more than expected ones (Bentzen 2019; restated in 2021). "Surprise matters more than need" appears in neither | "Bentzen refines the thesis: unexpected shocks raise religiosity more than expected ones (2019), and the availability of religion, meaning prior religiosity, matters more than material 'need' (2021)." | project notes §6 (quotes from Bentzen 2021) |

### 2b. Claims that are imprecise or incomplete (NOTE)

| ID | Location | Claim | Finding | Suggested wording |
|---|---|---|---|---|
| C-5 | §2.5 | Lang & Chvaja (2024): insecurity raised willingness to join normative groups, "but the result was inconclusive when the group was framed as religious" | Accurate but one-sided. The abstract adds that when participants were reassigned from insecure to secure environments and vice versa, "we found strong support for the existential insecurity theory" | Add: "though switching participants between environments gave strong support to the insecurity theory." (https://doi.org/10.1525/collabra.126508) |
| C-6 | §2.7 | "Mitchell (1990) argues that Scott understates how domination shapes consciousness itself" (in a paragraph on Scott 1990) | Mitchell's article critiques Scott's *Weapons of the Weak* (1985) and its material/ideological dualism, not *Domination and the Arts of Resistance* (1990, same year) | "Mitchell (1990), responding to Scott's earlier *Weapons of the Weak*, argues ..." |
| C-7 | §2.2 | "Berger withdrew his prediction that pluralism would erode religion (Berger 1999)." | In 1999 Berger retracted secularization theory in general ("essentially mistaken"). His specific revision of the pluralism argument, that pluralism relativizes rather than secularizes, came in *The Many Altars of Modernity* (2014) | "Berger later abandoned secularization theory (Berger 1999) ..." |
| C-8 | §2.7 | Hirschman: members "may protest from within, stay loyal or leave" | Loyalty in Hirschman is not a third option alongside exit and voice. It moderates the choice between them (it delays exit and activates voice) | "may protest from within or leave; loyalty delays exit and makes voice more likely" |
| C-9 | §2.4 | "The privileged control churches and receive rewards. The deprived accept more compensators and form sects in tension with society (Stark and Bainbridge 1979)." | The 1979 article sets out the church–sect–cult typology in terms of tension. The power–compensator propositions belong to Stark & Bainbridge 1980 ("Towards a Theory of Religion: Religious Commitment," *JSSR* 19 (2): 114–28) and 1987 | Cite 1987 (and 1980) for the power–compensator propositions; keep 1979 for "sects in tension" |
| C-10 | §2.5 | "Multilevel studies support the link at the national level ... and both public and private religiosity in Europe (Immerzeel and van Tubergen 2013)." | Immerzeel & van Tubergen stress individual-level insecurity (unemployment, war experience) as much as country-level insecurity. Their finding of effects on both private and public religiosity is correct | Drop "at the national level" for this study, or say "at both the individual and national levels" |
| C-11 | §2.1 | "A church is a hierocratic organization that claims a monopoly on dispensing or withholding the goods of salvation (Weber 1978)." | Close paraphrase. Weber's definition (E&S, ch. 1, §17): a compulsory hierocratic organization is a "church" insofar as its staff claims a monopoly of the legitimate use of hierocratic coercion, that is, psychic coercion by distributing or denying religious benefits | Acceptable; for precision: "claims a monopoly of the legitimate use of 'hierocratic coercion', the granting or withholding of religious benefits" |
| C-12 | §2.6 | RCOPE "measures discontent with clergy and congregation separately from discontent with God *[verify subscale name]*" | Verified. The subscale is **Interpersonal Religious Discontent** ("expressing confusion and dissatisfaction with the relationship of clergy or members to the individual in the stressful situation"), one of 21 five-item subscales. Spiritual Discontent is the separate God-directed subscale. The Brief RCOPE (1998) does not include it | Replace the tag with "(the 'Interpersonal Religious Discontent' subscale)". Source: RCOPE PDF on kennethpargament.com; BGSU RCOPE sheet |

### 2c. Claims checked and found correct (OK)

| ID | Claim | Evidence |
|---|---|---|
| C-13 | Weber: "theodicy of good fortune" for privileged strata; salvation and compensation religions for negatively privileged strata | Gerth & Mills 1946, "Social Psychology," pp. 271 ff. (standard text) |
| C-14 | Weber: archaic religion read suffering as a sign of divine disfavour (the "[verify passage]" tag) | Same essay, c. p. 271: suffering as "a symptom of odiousness in the eyes of the gods and as a sign of secret guilt". The tag can be resolved to that passage (page from the standard edition, not rechecked against a scan) |
| C-15 | Weber: charisma arises in "distress"; routinization | Gerth & Mills, "Sociology of Charismatic Authority," p. 245 ("natural leaders in times of psychic, physical, economic, ethical, religious, political distress"); E&S on routinization |
| C-16 | Riesebrodt 2010: religion as practices promising to avert misfortune, cope with crisis, provide salvation | Riesebrodt's definition, *The Promise of Salvation* |
| C-17 | Morgan & Wilkinson 2001: theodicy turned into "sociodicy" that legitimates adversity and inequality and neglects affliction | Crossref abstract (verbatim "sociodicy"; "legitimizing rationalizations of social adversities, inequalities and injustice") |
| C-18 | Berger 1967: nomos, anomic threats; theodicies legitimate for both poor and rich; "masochistic" attitude; Job; incarnation; plausibility structure | *Sacred Canopy*, ch. 3 (standard) |
| C-19 | Durkheim: collective effervescence; piacular rites | *Elementary Forms*, Book III ch. 5 |
| C-20 | Páez et al. 2015 as the first full test; effects of perceived emotional synchrony, including in protest marches | Abstract: Durkheim's predicted effects "remained untested as a whole"; four studies covering folkloric marches and protest demonstrations |
| C-21 | Erikson 1976: Buffalo Creek 1972, coal-company dam; collective trauma as damage to communal bonds | standard; reviews |
| C-22 | Erikson 1994: human-caused and toxic disasters as "a new species of trouble" that breeds distrust | Title phrase correct; the book's cases (mercury spill, gasoline leak, Three Mile Island) and its argument about lost trust match standard summaries (Kirkus; Yale page) |
| C-23 | Alexander et al. 2004 carrier groups; Eyerman 2001: slavery as cultural trauma formed after emancipation by a generation for whom slavery was past | CUP sample/description: identity "emerged in the post-Civil War period ... articulated by a generation of black intellectuals for whom slavery was a thing of the past" |
| C-24 | Marx: "the expression of real suffering and a protest against real suffering"; "the opium of the people" | Substance correct. The quoted wording matches the MECW/Progress translation; O'Malley's 1994 wording **UNV** ("To verify" item stands) |
| C-25 | Glock 1964: five deprivations; conditions (shared, felt, no secular alternative, leadership); economic deprivation leads to sects | Glock chapter; Hartford Encyclopedia |
| C-26 | Stark & Bainbridge 1987: "general compensators" | *A Theory of Religion* |
| C-27 | Stark 1999 rebuilt theory around exchange with the gods and set compensators aside | Abstract confirms the exchange basis. The dropping of compensators is consistent with Stark's later work (Stark & Finke 2000) but **UNV** in the 1999 text |
| C-28 | Iannaccone 1990/1992/1994: religious capital; strictness screens free riders | abstracts |
| C-29 | Ager & Ciccone 2018: common rainfall risk raised 19th-century county membership; "more than a third" persists today | Notes §7: "greater common risk"; persistence ρ 0.36–0.5 |
| C-30 | "Chronic risk raises belonging, while surprise shocks raise belief (Ager and Ciccone 2018, summarizing Bentzen's working paper)" | Notes §7: A&C WP p. 5 and p. 7 (Bentzen: beliefs, not attendance) |
| C-31 | Chen 2010: Indonesian crisis raised Islamic intensity as ex post insurance; credit access weakened it | JPE abstract |
| C-32 | Dehejia et al. 2007: attendance buffered happiness against income shocks more for Black than white Americans | NBER w11576 summary |
| C-33 | Auriol et al. 2020: insured Ghanaian Pentecostals gave less to their church | Crossref abstract |
| C-34 | Chaves & Gorski 2001; Voas, Olson & Crockett 2002; Marwell 1996 | abstracts and titles |
| C-35 | Norris & Inglehart: insecurity sustains religiosity | standard |
| C-36 | Ruiter & van Tubergen 2009: 60 countries; insecurity predicts attendance | title and abstract |
| C-37 | Gill & Lundsgaarde 2004: welfare spending substitutes for religion | title and abstract |
| C-38 | Höllinger & Muckenhuber 2019: "only a very small impact" | Crossref abstract, verbatim |
| C-39 | Molteni 2021: "far less clear than expected" | publisher abstract, verbatim |
| C-40 | Frijters et al. 2024: near-zero effects; short-term fall in attendance as recovery crowds out worship | Crossref abstract |
| C-41 | Pargament 1997: coping as a search for significance | standard |
| C-42 | Pargament et al. 1998 positive/negative patterns; RCOPE 2000 adjustment correlates | Abstracts: poorer adjustment with punishing-God reappraisal, spiritual discontent and reappraisal of God's powers; better with benevolent reappraisal, seeking support and others |
| C-43 | Smith et al. 2000: flood coping predicted religious and psychological outcomes | title and abstract (1993 Midwest flood, church members) |
| C-44 | Exline et al. 2014: six domains (divine, demonic, interpersonal, moral, doubt, ultimate meaning) | RSS scale paper (standard; matches the published scale) |
| C-45 | Exline et al. 2011: anger toward God predicted by holding God responsible and seeing oneself as a victim; unresolved anger harms adjustment | Abstract (via PSU Pure / EurekAlert): "holding God responsible for severe harm, attributions of cruelty, difficulty finding meaning, and seeing oneself as a victim"; worse adjustment when anger stayed unresolved over a year |
| C-46 | Abu-Raiya et al. 2015: struggles predict distress in a national sample | title |
| C-47 | Park 2010 global vs. situational meaning | abstract |
| C-48 | Tedeschi & Calhoun 2004 spiritual change domain; Shaw et al. 2005; Frazier et al. 2009 | abstracts |
| C-49 | Kay et al. 2008: lowered control raises belief in a controlling God and support for external systems | title and abstract |
| C-50 | Kay et al. 2010: "hydraulic" relation between government instability and religious control | title |
| C-51 | Kirkpatrick & Shaver 1990; Granqvist 1998; Granqvist & Kirkpatrick 2004: compensation (insecure attachment, sudden conversion) vs. correspondence (secure attachment, religious caregivers) | titles and abstracts |
| C-52 | Greenberg et al. 1990; Vail et al. 2010: mortality salience strengthens afterlife belief and worldview defence | Vail abstract: "mortality salience produces increased belief in afterlife, supernatural agency ..." |
| C-53 | Sætrevik & Sjåstad 2022: MS effects fail to replicate | title |
| C-54 | Schnabel & Schieman 2022: religion protected mental health in March 2020 but reduced support for public-health measures | Crossref abstract |
| C-55 | Bourdieu 1971: monopoly of the legitimate management of the goods of salvation; magic as the religion of the dominated | standard |
| C-56 | Scott 1990: public and hidden transcripts | standard |
| C-57 | Walzer 1985: Exodus as a paradigm of revolutionary politics; Said 1986 "Canaanite reading" | titles |
| C-58 | Smith 1996; Morris 1984 (indigenous perspective); McAdam 1982 | standard |
| C-59 | Lincoln 1994: authority as the effect of right speaker, setting and audience; corrodes when trust is withdrawn | *Authority: Construction and Corrosion* (standard) |
| C-60 | Dittmar & Meisenzahl 2020: institutional change after plague only with the Reformation | notes §1 (Black Death null; 1500s effect tied to the Reformation) |
| C-61 | Chaves 1994: secularization as declining scope of religious authority | title and article |
| C-62 | Davie 1990 coined "believing without belonging" (year) | *Social Compass* 37 (4), Dec. 1990 |
| C-63 | Voas & Crockett 2005: belief eroded at the same rate as belonging; generational; "only about half of parental religiosity ... absence of religion almost always passed on" | Crossref abstract, near-verbatim |
| C-64 | Casanova 1994: three theses (differentiation, decline, privatization) | standard |
| C-65 | Martin 1978: monopoly plus elite alliance leads to anticlericalism; Poland and Ireland | standard |
| C-66 | Moore 1987: persecuting society c. 950–1250, driven by elites | title and argument |
| C-67 | Girard: *The Scapegoat* opens with Machaut on Jews poisoning wells; "texts of persecution"; four stereotypes | Ch. 1, "Guillaume de Machaut and the Jews" (English ed.). Resolves the "To verify" item |
| C-68 | Cohn 2007: elites and town councils led burnings; Cohn 2018: compassion more common than hate | titles and abstracts |
| C-69 | Papacy condemned the massacres; some prince-bishops profited | notes §9 (Finley & Koyama: papal condemnation; Archbishop Baldwin of Trier) |
| C-70 | Fountain 2010: mass conversion largely after 1865 | consistent with Fountain's argument (section 5 refs) |
| C-71 | Collins 2004 interaction ritual chains | title |
| C-72 | Bentzen 2021 (as cited elsewhere in the section and table): private prayer rose without the church | notes §6 |

## 3. Status of the section's own "To verify" list

| Item | Resolution |
|---|---|
| Weber 1946 pages and passages | "Social Psychology" 267–301 (OUP); disfavour passage c. p. 271; charisma "distress" p. 245 |
| Weber 1978 church definition | Part One, ch. 1, §17 (hierocratic organization; church) |
| Glock 1964 pages | 24–36 |
| Bourdieu English translation | *Comparative Social Research* 13 (1991): 1–44, confirmed |
| RCOPE subscale | "Interpersonal Religious Discontent" |
| Exline et al. 2014 six domains | Correct as listed |
| Kirkpatrick year | 2005 (©2005) is correct |
| Eyerman 2001 | Confirmed |
| Erikson 1994 | Title and subtitle confirmed; distrust argument consistent with summaries |
| Lincoln 1985 | Chapter is "Notes toward a Theory of Religion and Revolution"; typology has **four** types (add counterrevolution); pages UNV |
| Marx 1994 | Editor O'Malley confirmed; translation wording UNV |
| Morris 1984, Berger 1999 publishers | Free Press; Eerdmans / EPPC, confirmed |
| Girard 1986 | Machaut analysis is chapter 1, confirmed |
| End pages | Chaves 774; Stark & Bainbridge 131; Stark 1971 176; Iannaccone 314; Granqvist 367; Said 106 (UNV) |

## 4. Comparison with the project's open-access full-text notes

- **Ager & Ciccone:** consistent ("common risk", >1/3 persistence, belonging rather than belief, the second-hand Bentzen point).
- **Bentzen 2021:** consistent on private prayer and the stock effect. §2.5's "surprise matters more than need" misquotes the "availability vs. need" passage (C-4).
- **Voas & Chaves 2016:** not cited in section 2. Its cohort-replacement finding agrees with the Voas & Crockett summary.
- **Jedwab et al. 2019:** the notes show the weak-state attribution in §2.9 is wrong (C-2).
- **Finley & Koyama 2018; Dittmar & Meisenzahl 2020:** consistent.
