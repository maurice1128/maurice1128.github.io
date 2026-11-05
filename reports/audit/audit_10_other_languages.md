# Audit: Section 10 (Scholarship and sources in further languages)

Targets: `reports/sections/10_other_languages.md` and `reports/sections/10_other_languages_refs.md`.
Audit date: 2026-11-05. Neither target file was edited.

**Method.** All 113 reference entries were checked against at least one catalogue or registry:

- NDL Search OpenSearch/JSON for Japanese. CiNii returned 403 and blank pages to automated requests.
- RISS (articles and monographs) for Korean, plus Kyobo Scholar for page ranges.
- Dialnet for Spanish and Portuguese.
- data.bn.org.pl for Polish.
- LIBRIS for Swedish, Danish, Norwegian, and the Uppsala Hebrew edition.
- BnF SRU for French.
- DNB SRU for German.
- Crossref and doi.org content negotiation for every DOI.
- Open Library for the remaining books.
- WebSearch for the Arabic, Hebrew and Brazilian items, and for content claims.

Google Books and LoC JSON were blocked (429/403).

Status key: **verified** = the catalogue record matches author, title, year and publisher or journal. **wrong detail** = the work exists but at least one element is wrong. **not found** = no catalogue confirmation. **fabricated-likely** = evidence suggests the work does not exist.

## 1. Reference entries

| # | Entry | Status | Evidence URL | Correction / note |
|---|---|---|---|---|
| 1 | An Pyŏng-mu 1988, *Minjung sinhak iyagi* 民衆神學 이야기, Han'guk Sinhak Yŏn'guso; rev. Han'gilsa 1991 | verified | https://www.riss.kr (bib_m "민중신학 이야기 안병무": 한국신학연구소 1988; 한길사 1991) | — |
| 2 | An Pyŏng-mu 1990, *Kalillae ŭi Yesu* 갈릴래아의 예수, HSY | verified (romanization error) | RISS: 갈릴래아의 예수, 안병무, 한국신학연구소 1990 | McCune–Reischauer for 갈릴래아 is *Kallillaea*, not "Kalillae". |
| 3 | An Pyŏng-mu 1993, *Minjung sinhak ŭl marhanda*, Minjung sinhak 2, Han'gilsa | verified | RISS: 민중신학. 2, 민중신학을 말한다, 한길사 1993 | — |
| 4 | An Pyŏng-mu 1992, 民衆神学を語る, trans. 桂川潤 and others, Shinkyō | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000002188789 | Translators are 趙容来 (Cho Yong-nae) and 桂川潤. The 2016 Kan'yō edition gives the original as 민중신학 이야기, so this is a translation of the 1988/1991 book (#1). It is not a translation of #3, as the bracketed English title implies. |
| 5 | Arjona Castro 1985, *BRAC* 56 (108): 49–58 | verified | https://dialnet.unirioja.es/servlet/articulo?codigo=6922609 | — |
| 6 | Bartsocas 1966, *JHMAS* 21 (4): 394–400 | verified | https://doi.org/10.1093/jhmas/xxi.4.394 | — |
| 7 | Benedictow 2002, *Svartedauen og senere pestepidemier i Norge*, Unipub | verified | http://libris.kb.se/bib/8875700 | — |
| 8 | Bizimana 2000, *L'Église et le génocide au Rwanda*, L'Harmattan | verified | BnF SRU (catalogue.bnf.fr), 155 p. | — |
| 9 | Būjarra 2011, *al-Ṭāʿūn wa-bidaʿ al-ṭāʿūn*, CAUS | verified | https://caus.org.lb/product/الطاعون-وبدع-الطاعون-الحراك-الاجتماع/ ; Tunisian National Library record | 751 pp., in the CAUS doctoral-thesis series. One description says the study centres on Tunisia, compared with the rest of the Maghreb. |
| 10 | Bylina 1991, *Ruchy heretyckie w średniowieczu*, Ossolineum | verified | https://data.bn.org.pl/api/bibs.json?title=Ruchy%20heretyckie%20w%20%C5%9Bredniowieczu | — |
| 11 | Bylina 2002, *Chrystianizacja wsi polskiej*, IH PAN | verified | data.bn.org.pl (same API) | — |
| 12 | Cabrera 1954, *El monte*, Ediciones C.R. | verified | Open Library (Ediciones C. R., Habana 1954) | — |
| 13 | Cantera Montenegro 2022, *Cuadernos del CEMYR* 30: 109–148 | verified | Dialnet; https://www.ull.es/revistas/index.php/cemyr/article/view/5033 | — |
| 14 | Castán Lanaspa 2020, Ediciones Universidad de Salamanca | verified | Dialnet (ISBN 978-84-1311-238-1) | — |
| 15 | Castañeda García 2011, PhD diss., El Colegio de Michoacán | verified | Dialnet (thesis directed by Thomas Calvo) | — |
| 16 | Cho Kwang 1988, *Chosŏn hugi Ch'ŏnjugyosa yŏn'gu*, Koryŏ Tae Minjok Munhwa Yŏn'guso | verified | RISS: 朝鮮後期 天主敎史 硏究, 조광, 고려대학교 民族文化硏究所 1988 | Based on his 1984 Korea Univ. PhD dissertation. |
| 17 | CTC-CCA ed. 1981, *Minjung Theology*, Singapore; Orbis 1983 | verified | https://archives.anglican.ca/link/catalog3609 ; Open Library (Zed/Orbis 1983) | Usually catalogued as edited by Kim Yong Bock. The 1983 edition was co-published by Zed (London) and Orbis. |
| 18 | Cone 1973, 解放の神学：黒人神学の展開, trans. 梶原寿, Shinkyō | verified | https://ndlsearch.ndl.go.jp/en/books/R100000002-I000001238143 | Original: *A Black Theology of Liberation* (1970). The "[verify English original]" flag can be removed. |
| 19 | Conrad 1995, review, *Medical History* 39 (3): 391–393 | verified | https://doi.org/10.1017/s0025727300060282 | — |
| 20 | Curatola Petrocchi 1977, *Allpanchis* 10: 65–92 | verified | Dialnet (Allpanchis año 9, nº 10, 1977, pp. 65–92) | — |
| 21 | Dias 2017, *Em Tempo de Histórias* 29 | verified | https://doi.org/10.26512/emtempos.v0i29.14745 | — |
| 22 | Dols 1974, Ibn al-Wardī chapter in Miles festschrift | verified | https://csms.columbia.edu/s/Epidemics-in-Pre-Modern-Islam-Bibliography.pdf ; Open Library (AUB 1974) | Add **pp. 443–455**. |
| 23 | Dols 1977, *The Black Death in the Middle East*, Princeton | verified | Open Library | — |
| 24 | Fagundes 2023, *História Revista* 28 (1): 7–25 | verified | https://doi.org/10.5216/hr.v28i1.75300 | Add the DOI. |
| 25 | Fukumoto 福本保信 n.d., 黒人奴隷のキリスト教改宗 (1)–(3), 西南学院大学国際文化論集 | wrong detail (years missing) | https://ndlsearch.ndl.go.jp/books/R000000004-I3289083 ; …-I3939854 ; …-I4039421 | (1) vol. 9 no. 2, Feb. 1995, pp. 57–77. (2) vol. 10 no. 1, Sept. 1995, pp. 35–54. (3) vol. 11 no. 1, Sept. 1996, pp. 101–125. NDL gives no reading for 保信; "Yasunobu" is likely but unconfirmed. |
| 26 | Graus 1949, *Chudina městská*, Melantrich | verified | Open Library | — |
| 27 | Guichaoua 2010, *Rwanda, de la guerre au génocide*, La Découverte | verified | BnF SRU (621 p.) | English translation confirmed: *From War to Genocide*, University of Wisconsin Press, 2015 (Open Library). |
| 28 | Guzowski 2022, *JIH* 53 (2): 193–223 | verified | https://doi.org/10.1162/jinh_a_01832 | — |
| 29 | Harrison 2000, *Stora döden*, Ordfront | verified | http://libris.kb.se/bib/7634616 | — |
| 30 | Heilman 2002, *CLAR* 11 (1): 123–138 | verified | https://doi.org/10.1080/10609160220133718 | Add the DOI. |
| 31 | Hirooka 1993, 宗教と民族主義…, 産大法学 no. 3/4 | verified (pages conflict) | https://ndlsearch.ndl.go.jp/books/R000000004-I3491124 ; https://ndlsearch.ndl.go.jp/books/R000000025-I012230000736003 | **Vol. 26**, no. 3/4, Jan. 1993. Pages are 340–361 in the NDL article index and 82–103 in the Kyoto Sangyō repository. The repository version is labelled a 研究ノート (research note). |
| 32 | Ibn Ḥajar 1993, *Badhl al-māʿūn*, ed. Kaylānī, Dār al-Kutub al-Athariyya | verified | Conrad review title (https://doi.org/10.1017/s0025727300060282) | Another edition exists: Riyadh, Dār al-ʿĀṣima, 1991 (ed. al-Kātib). |
| 33 | Iehreshii & Siretska 2020, *Halychyna* 33: 177–181 | verified | https://doi.org/10.15330/gal.33.177-181 | — |
| 34 | Ishizaka 2017a, イタリアの黒死病関係史料集, Tōsui | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I028730796 | NDL authority reading is イシザカ ナオタケ, so "Naotake" is correct. The book appeared in Dec. 2017 (26 + 770 pp.). The serial parts began in 2004 (R000000004-I6839324). |
| 35 | Ishizaka 2017b, どうしてルターの宗教改革は起こったか, Nakanishiya | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I028980413 | — |
| 36 | Ishizaka 2018, 苦難と心性, Tōsui | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I028932232 | — |
| 37 | Izdebski et al. 2022, Reply, *Nat Ecol Evol* 6 (11): 1628–1629 | verified | https://doi.org/10.1038/s41559-022-01863-3 | Full author list: A. Izdebski, M. Bauch, P. Guzowski, S. Mensing, A. M. Mercuri, T. Newfield, G. Piovesan, L. Sadori, C. Vignola, A. Masi. |
| 38 | Jensen 1987, *Den sorte død og livet i senmiddelalderen*, Nordisk Forlag | verified | http://libris.kb.se/bib/7195875 | — |
| 39 | Joseph ha-Kohen 1981, ed. Almbladh, Uppsala | verified | http://libris.kb.se/bib/7423883 | — |
| 40 | Kang In-ch'ŏl 2007, 한국의 개신교와 반공주의, Chungsim | verified | RISS bib_m | — |
| 41 | Karasch 2011, *História Revista* 15 (2) | verified | https://doi.org/10.5216/hr.v15i2.14128 | — |
| 42 | Karpiński 2000, *W walce z niewidzialnym wrogiem*, Neriton / IH PAN | verified | data.bn.org.pl | — |
| 43 | Kim Hŭng-su 1999, 한국전쟁과 기복신앙 확산 연구, HKYY | verified | RISS bib_m | Based on his 1998 SNU PhD dissertation, 한국전쟁의 충격과 기독교회의 기복신앙 확산에 관한 연구. |
| 44 | Kim Nam-sik 1990, 神社參拜와 韓國敎會, Saesun | verified (romanization error) | RISS bib_m | 參拜/참배 is *ch'ambae*, not "ch'amba". |
| 45 | Kim Sŭng-t'ae 1991, 한국기독교와 신사참배문제, HKYY | verified (romanization error) | RISS bib_m | Read "sinsa ch'ambae munje". |
| 46 | Kitamori 1946, 神の痛みの神学, Shinkyō; English SCM 1966 | wrong detail (minor) | https://ndlsearch.ndl.go.jp/books/R100000002-I000000665351 ; Open Library | The 1946 Shinkyō edition is confirmed. The first English edition was Richmond, VA: John Knox Press, **1965**; the SCM London edition followed in 1966. |
| 47 | Kolitz 1998, *Yossel Rakover s'adresse à Dieu*, trans. Marcou, Calmann-Lévy | verified (note) | BnF SRU | BnF records it as "trad. de l'allemand", published by M. Sell–Calmann-Lévy. The French was translated from German, not from the Yiddish original. |
| 48 | Kostis 1995, *Ston kairo tēs panōlēs*, PEK | verified | Open Library (Panepistēmiakes Ekdoseis Krētēs, Hērakleio 1995) | — |
| 49 | Kuramochi 1995, ペストの文化誌, Asahi | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000002434561 | — |
| 50 | Kuribayashi 1991, 荊冠の神学, Shinkyō | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000002097302 | — |
| 51 | Langer 1975, *Russian History* 2 (1): 53–67 | verified | https://doi.org/10.1163/187633175x00045 | — |
| 52 | Lara Olmo 2023, *Darom* 1 (5) | verified | Dialnet | — |
| 53 | León Tello 1977, *Sefarad* 37 (1–2): 333–337 | verified | Dialnet (Sefarad año 37, nº 1–2, 1977, pp. 333–337) | — |
| 54 | Linden 1999, *Christianisme et pouvoirs au Rwanda*, Karthala | verified | BnF SRU | English original: *Church and Revolution in Rwanda*, Manchester UP, 1977. |
| 55 | Lugan 2004, Éditions du Rocher | verified | BnF SRU | — |
| 56 | Mena García 2000, *AEA* 57 (1): 137–169 | verified | Dialnet | — |
| 57 | Mengel 2011, *Past & Present* 211: 3–34 | verified (citation); see claim C27 | https://doi.org/10.1093/pastj/gtq069 | — |
| 58 | Millones ed. 1990, *El retorno de las huacas*, SPP | verified | Open Library | The IEP co-imprint is confirmed: Lima, Instituto de Estudios Peruanos and Sociedad Peruana de Psicoanálisis. Remove the "[verify IEP]" flag. |
| 59 | Millones Figueroa 2007, *Memoria Americana* 15 (2) | verified | Dialnet | — |
| 60 | Miyahira 2001, アメリカの解放神学・黒人神学・女性神学思想 | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000002973058 | Series: 研究叢書 no. 33. |
| 61 | Miyazaki 1996, カクレキリシタンの信仰世界, Tokyo UP | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000002562001 | — |
| 62 | Miyazaki 2014, カクレキリシタンの実像, Yoshikawa | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I025127172 | — |
| 63 | Miyazaki 2018, カクレキリシタン：現代に生きる民俗信仰, KADOKAWA | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I028810081 | Kadokawa Sophia Bunko. A heavily revised edition of the 2001 Nagasaki Shinbunsha book. |
| 64 | Moreno Navarro 1997, *La antigua hermandad de los negros de Sevilla*, Univ. de Sevilla | verified | Open Library | Co-published with the Consejería de Cultura, Junta de Andalucía. |
| 65 | Moreno Navarro 2005, "Plurietnicidad…", in *El mundo festivo*, 169–188 | verified | Dialnet | Publisher: Córdoba, Universidad de Córdoba, Servicio de Publicaciones (ISBN 84-7801-784-4). |
| 66 | Morimoto 2006, アメリカ・キリスト教史, Shinkyō | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000008218448 | — |
| 67 | Murakami 1983, ペスト大流行, Iwanami shinsho | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000001611658 | — |
| 68 | Myrdal 1978, *Digerdöden: Orsakad av fattigdom och förtryck*, Ordfront | verified | http://libris.kb.se/bib/7633993 | Imprint: Ordfront / Arkivet för folkets historia. |
| 69 | Myrdal 2003, *Digerdöden, pestvågor och ödeläggelse*, Runica et Mediævalia | verified | http://libris.kb.se/bib/9123041 | — |
| 70 | Nagai 1949, 長崎の鐘, Hibiya; English trans. Johnston, Kodansha | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I000001703305 | The English translation year is **1984** (paperback 1994). The NDL card notes Hibiya Shuppan 1949. |
| 71 | Nakazono 2018, かくれキリシタンの起源, Gen Shobō | verified | https://ndlsearch.ndl.go.jp/books/R100000002-I028860404 | NDL reading ナカゾノ シゲオ. |
| 72 | Nasonov ed. 1941–55, *Pskovskie letopisi*, 2 vols | verified | Open Library | — |
| 73 | Ortiz 1992 [1921], *Los cabildos y la fiesta afrocubanos del Día de Reyes* | wrong detail (bracket date) | Open Library (Ciencias Sociales 1992); WebSearch summary of Ortiz bibliographies | The 1992 volume is a later compilation. "Los cabildos afrocubanos" appeared in *Revista Bimestre Cubana* 16 (1921). The Día de Reyes essay was a separate, later piece (1920s). "[1921]" applies only to the cabildos half. |
| 74 | Pak Hŭng-sik 2011, *Sŏyangsa yŏn'gu* 44 | verified | RISS re_a_kor | — |
| 75 | Pak Hŭng-sik 2019, *T'onghap yŏn'gu* 21 (1) | verified (typo) | RISS re_a_kor | Correct the typo "Ing'üllaendŭ" to "Ing'ŭllaendŭ". |
| 76 | Pak Po-gyŏng 2010, *Sŏn'gyo wa sinhak* 26 | verified | RISS re_a_kor | — |
| 77 | Polishchuk 2023, *Kul'turolohichnyi al'manakh* 3: 14–20 | verified | https://doi.org/10.31392/cult.alm.2022.3.3 | Crossref issued date is Feb. 2023; the DOI encodes the 2022 volume. |
| 78 | Pshenychnyi 2018, *Bulletin KNU History* 137: 34–38 | verified | https://doi.org/10.17721/1728-2640.2018.137.2.06 | — |
| 79 | Quírico 2021, *Concinnitas* 22 (40) | verified | https://doi.org/10.12957/concinnitas.2021.59062 | — |
| 80 | Reginaldo 2005, PhD diss., Unicamp | verified | https://doi.org/10.47749/t/unicamp.2005.335419 | Subtitle: *irmandades negras, experiências escravas e identidades africanas na Bahia setecentista*. The 2011 book **does exist**: *Os Rosários dos Angolas: Irmandades de africanos e crioulos na Bahia setecentista*, São Paulo: Alameda, 2011 (Open Library; ISBN 978-85-7939-082-1). |
| 81 | Reginaldo 2016, *Studia Historica: HM* 38 (1): 123–151 | verified | https://doi.org/10.14201/shhmo2016381123151 | Crossref gives only the start page (123). |
| 82 | Salfeld 1898, *Das Martyrologium des Nürnberger Memorbuches*, Simion | verified | Open Library | Series: Quellen zur Geschichte der Juden in Deutschland, Bd. 3 (from prior knowledge; not catalogue-confirmed here). |
| 83 | Sasaki n.d., 黒死病とユダヤ人迫害, 大阪府立大学紀要 人文・社会科学: 1–15 | wrong detail (year missing) | https://ndlsearch.ndl.go.jp/books/R000000004-I7025474 | **Vol. 52, 2004**, pp. 1–15. The reading "Hiromitsu" for 博光 is unconfirmed. |
| 84 | Scarano 1975, *Devoção e escravidão*, Cia. Ed. Nacional | **wrong detail (year)** | Open Library; USP *Revista de História* review (https://periodicos.usp.br/revhistoria/article/download/210091/192589/615737) | **1976**, Brasiliana vol. 357, 171 pp. A 2nd ed. appeared in 1978. No 1975 edition is attested. |
| 85 | Schopen ed. 1828–32, Cantacuzenus, CSHB | verified | Open Library (Bonnae: Weber 1828, 1831, 1832) | — |
| 86 | Schopen & Bekker 1829–55, Gregoras, CSHB | verified | Open Library | — |
| 87 | Semana 2013, *Le problème des sectes…*, L'Harmattan | verified | BnF SRU (139 p.) | — |
| 88 | Shapira 2017, *Derashot mi-shenot ha-zaʿam*, ed. Reiser | verified | https://hasidut.herzog.ac.il/en/books/sermons-from-the-years-of-rage-vol-1/ | 2 vols: critical text and facsimile. |
| 89 | Shinozaki 2013, 温存される〈浦上燔祭説〉, 社会文学 38: 75–89 | verified | https://ndlsearch.ndl.go.jp/books/R000000004-I024812190 | NDL dates it 2013, which settles the year. The reading of 美生子 ("Mioko"?) is not given in NDL. The full subtitle is 原爆死の意味づけと戦後天皇制をめぐって. |
| 90 | Shlikhta 1999, *Ukraïna moderna* 4–5: 246–286 | verified | https://doi.org/10.3138/ukrainamoderna.4.246 | — |
| 91 | Shlikhta 2022, chapter in *The 'Lviv Sobor' of 1946*, 119–145 | verified | https://doi.org/10.1163/9789004545687_008 ; https://doi.org/10.1163/9789004545687 | Editors: **Adam A. J. DeVille and Daniel Galadza**. Crossref dates the book to 2023 and the chapter to Dec. 2022 (online). |
| 92 | Silveira 2012, chapter in *Escravidão e suas sombras*, 15–64 | verified | https://doi.org/10.7476/9788523211882.0002 | Editors: **João José Reis and Elciene Azevedo**. |
| 93 | Šmahel 1993, *Husitská revoluce*, 4 vols; German 2002 | verified | Open Library | — |
| 94 | Sŏ Kwang-sŏn 1988, 恨의 이야기, Pori | verified | RISS bib_m | — |
| 95 | Sŏ Nam-dong 1983, 民衆神學의 探究, Han'gilsa | verified | RISS bib_m | — |
| 96 | Sŏ Nam-dong et al. 1984, *Han: Sinhak, munhak, misul ŭi mannam*, Pundo | verified | RISS bib_m (서남동, 분도출판사 1984) | RISS lists 서남동 as first author. No separate editor was confirmed. |
| 97 | Soares 2000, *Devotos da cor*; English *People of Faith*, Duke 2011 | verified | Open Library | — |
| 98 | Souza 2002, *Reis negros no Brasil escravista*, Editora UFMG | verified | Open Library | — |
| 99 | van 't Spijker 2011, *L'Église chrétienne au Rwanda…*, L'Harmattan | verified | BnF SRU | — |
| 100 | Stearns 2011, *Infectious Ideas*, Johns Hopkins | verified | Open Library | — |
| 101 | Stern 1982, *Allpanchis* 19: 49–77 | verified | Dialnet | — |
| 102 | Takahashi 1994, 長崎にあって哲学する：核時代の死と生, Hokuju | verified | https://ndlsearch.ndl.go.jp/books/R100000136-I1970304959862995720 | — |
| 103 | Takahashi 2004, 原爆死から平和責任へ, Hokuju | **wrong detail (title)** | https://ndlsearch.ndl.go.jp/books/R100000136-I1971430859858774444 ; https://ndlsearch.ndl.go.jp/books/R000000004-I7900582 | The main title is **続・長崎にあって哲学する** (*Zoku Nagasaki ni atte tetsugaku suru*), and 原爆死から平和責任へ is the subtitle. |
| 104 | Takahashi 2020, 永井隆「浦上燔祭説」批判への道すじ, Misuzu Haikukai | **wrong detail (not a book)** | https://ndlsearch.ndl.go.jp/books/R100000001-I42111000002923912 ; …-I42111000002923913 | This is a two-part article in the haiku magazine **『みすゞ』 nos. 850 (Dec. 2020) pp. 20–24 and 851 (Jan. 2021) pp. 26–30**. Cite it as an article. The text's "three books" is wrong (see C7). |
| 105 | Teichtal 1999, *Em ha-banim semeḥah*, ed./trans. Schindler, Ktav | verified | https://collections.ushmm.org/search/catalog/bib47101 ; https://ktav.com/products/eim-habanim-semeichah | Hebrew original: Budapest, 1943. |
| 106 | Watanabe Shigeo n.d., アメリカ黒人解放に関する一考察, 基督教論集 35: 47–64 | wrong detail (year missing) | https://ndlsearch.ndl.go.jp/books/R000000004-I3437536 | **March 1992**. |
| 107 | Yi Chin-gu 2025, *Chonggyo munhwa pip'yŏng* 48 | verified | https://scholar.kyobobook.co.kr/article/detail/4010071639708 | **pp. 305–345**; DOI 10.36429/CRRC.48.8. |
| 108 | Yi P'il-ŭn 2013, *Chungang saron* 37 | verified | RISS re_a_kor | — |
| 109 | Yi Sang-dong 2021a, 채찍질 고행, *Sarim* 75 | verified (romanization error) | RISS re_a_kor | 채찍질 is *ch'aetchikchil*, not "Ch'aektchiril". |
| 110 | Yi Sang-dong 2021b, *Sŏyang chungsesa yŏn'gu* 47 | verified | RISS re_a_kor | — |
| 111 | Yi Sang-dong 2024, 중세 서유럽의 흑사병, SKKU Press | verified | RISS bib_m | — |
| 112 | Yun Chŏng-ran 2015, 한국전쟁과 기독교, Hanul Academy | verified | RISS bib_m | — |
| 113 | Yuval 2000, *Shene goyim be-vitnekh*, Am Oved/Alma; English UC Press 2006 | verified | Open Library; DNB SRU (German: *Zwei Völker in deinem Leib*, Vandenhoeck & Ruprecht 2007) | — |

**Cited in text but missing from the reference list**

| Item | Status | Evidence | Correction |
|---|---|---|---|
| Sandnes 1978 (Nordic Deserted Farm Project) | exists, no reference entry | http://libris.kb.se/bib/7165790 | Add: Sandnes, Jørn. 1978. *Ødegårdstid i Norge: Det nordiske ødegårdsprosjekts norske undersøkelser*. Oslo: Universitetsforlaget. |
| Quintão 2002, *Lá vem o meu parente* (text: "could not be found in any catalogue") | **exists** | Open Library (Antonia Aparecida Quintão, São Paulo: Annablume, 2002); review cited at https://revistashomol.pucsp.br/index.php/revph/article/view/67923/47523 | Delete the "not found" statement and add a reference entry. |

## 2. Claims checked

| # | Claim (section 10) | Verdict | Evidence | Note |
|---|---|---|---|---|
| C1 | Murakami (1983) frames plague as the "collapse" of the medieval order | supported | NDL subtitle ヨーロッパ中世の崩壊 | — |
| C2 | Ishizaka's source collection appeared serially from 2004 and as a book in 2017 | supported | NDL part 1 (2004-02); book 2017.12 | — |
| C3 | *Kunan to shinsei* reads plague as reshaping religious sensibility; *Dōshite Rutā…* argues from plague to the Reformation | supported by titles | NDL records | No abstract was read. |
| C4 | Sasaki engages the Graus and Cohn debate | not verified | NDL record (no abstract) | Plausible from the title only. Year is 2004. |
| C5 | Miyazaki: hidden Christianity became a Japanese folk religion | supported | Subtitle of the 2018 book (現代に生きる民俗信仰) | — |
| C6 | Nakazono, curator of the Ikitsuki museum, stresses continuity with 16th-century practice | supported | hanmoto.com bio (平戸市生月町博物館・島の館 学芸員) ; https://www.hanmoto.com/bd/isbn/9784863291652 | One source calls him 館長 (director). |
| C7 | Takahashi built the critique "across three books (1994, 2004, 2020)" | **wrong** | NDL: the 2020 item is a two-part haiku-magazine article | Two books plus an article. |
| C8 | Shinozaki (2013) argues the theory survived because it served the postwar emperor system | supported by title | NDL: subtitle …戦後天皇制をめぐって | — |
| C9 | Kitamori's book appeared in 1946 and in English in 1966 | partly wrong | Open Library: John Knox Press 1965 | The first English edition is 1965. |
| C10 | Cone in Japanese in 1973 | supported | NDL | — |
| C11 | Ahn identifies Jesus with the *ochlos* of Mark | supported (standard) | CTC-CCA volume contents (Ahn essay) | — |
| C12 | Ahn is translated into Japanese (An 1992) | supported | NDL | The Japanese volume translates *Minjung sinhak iyagi* (1988), not the 1993 title. |
| C13 | Yi Chin-gu traces the "Reconstruction Church" and "Independent Presbytery" | supported | Title and abstract (Kyobo) | — |
| C14 | Kim Hŭng-su: wartime suffering spread Christianity and reshaped it toward *kibok* faith | supported | Dissertation title (RISS) | — |
| C15 | Kang In-ch'ŏl: refugee Christians turned suffering under communism into anti-communism allied with the state | plausible, not verified | Title only | — |
| C16 | Cho Kwang: a lay-founded Catholic church grew through 1801–1866 persecutions "without resident clergy" | **wrong** | https://en.wikipedia.org/wiki/Korean_Martyrs ; https://irfa.paris/en/zonesgeographiques/korea/ | Clandestine resident priests served 1795–1801 (Zhou Wenmo), 1836–39 (Maubant, Chastan, Imbert) and from 1845 (Kim Taegŏn, Ferréol, then MEP priests until 1866). Say "with few and intermittent clergy". |
| C17 | The Korean church "rejoined Rome" | **misleading** | Same sources | It never separated. It sought priests from Beijing from 1784–90 onward. The Kakure contrast does not hold in this form. |
| C18 | Yi Sang-dong compares flagellant waves of 1260 and 1349 | minor | RISS title: 1260년과 흑사병 창궐시기(1348–9년) | Use "1348–49". |
| C19 | Yi P'il-ŭn (2013) is "by title" the only study on mass attendance | not checkable | — | Judgement call; keep the hedge. |
| C20 | Scarano (1975) pioneered the field | wrong date | See #84 | Use 1976. |
| C21 | Reginaldo traces Angolan members and the Atlantic roots of Black Rosary devotion | supported | Unicamp thesis abstract (Angolan control of Bahian Rosário brotherhoods); 2016 article title | — |
| C22 | Mello e Souza: brotherhoods crowned "kings of Congo" | supported | Subtitle | — |
| C23 | Quintão "could not be found in any catalogue" | **wrong** | Open Library: Annablume 2002 | The book exists. |
| C24 | "Reginaldo (2005)… The 2011 Alameda book edition was not found" (To verify) | **wrong** | Open Library: Alameda 2011 | The book exists. |
| C25 | Moreno's title reads "de los negros", not "negritos" | supported | Open Library | — |
| C26 | Castán Lanaspa argues Spanish historiography inflated 1348–50 | supported by title | Dialnet; Villanueva Morte review "La Peste Negra sujeta a revisión" | — |
| C27 | Mengel (2011) argues Bohemia's Black Death was **milder than assumed** | **mischaracterized** | Brown Decameron excerpt and search summaries (https://webhelper.brown.edu/decameron/plague/causes/mengel.php — 503 at audit time) | The assumed view, from Carpentier's map, was that Bohemia was **spared**. Mengel argues the Black Death did reach Bohemia, with significant mortality at least in Moravia. He adds that the 1380 epidemic was more damaging for the kingdom. The recurrence point survives, but "milder than assumed" reverses his argument. |
| C28 | Guzowski asks whether the Black Death reached Poland; low-mortality argument | supported | Crossref abstract (#28) | — |
| C29 | Izdebski team's pollen data support regional variation | supported | Reply cited (#37) | The underlying paper (Izdebski et al. 2022, *Nat Ecol Evol* 6: 297–306) is not in the list. Consider adding it. |
| C30 | Šmahel's *Husitská revoluce* is four volumes (1993), German 2002 | supported | Open Library | — |
| C31 | Sandnes (1978) reports the Nordic Deserted Farm Project | supported | LIBRIS | Missing reference entry. |
| C32 | Myrdal moved from a Marxist causal account (1978) to a "plague waves" model (2003) | supported by titles | LIBRIS | — |
| C33 | Ibn al-Wardī died of plague in 1349 | supported | https://en.wikipedia.org/wiki/Ibn_al-Wardi | — |
| C34 | Būjarra studies the Maghreb 1350–1800 as a contest among jurist, physician and ruler | supported | CAUS product title | The catalogue description centres on Tunisia, compared with the wider Maghreb. |
| C35 | Teichtal turns catastrophe into an indictment of his own anti-Zionist camp | supported | Ktav and USHMM descriptions; Schindler intro | — |
| C36 | Kolitz's Yiddish monologue, French trans. 1998 | partly | BnF: translated from German | The 1998 French version was translated from German, not Yiddish. |
| C37 | Shapira's sermons are now critically edited (2017) | supported | Herzog College page | — |
| C38 | Yuval: English 2006, German 2007 | supported | Open Library; DNB | — |
| C39 | Kostis covers the Greek lands, 14th–19th c. | supported | Subtitle (Open Library) | — |
| C40 | Pskov chronicles in Nasonov 1941–55, repr. as PSRL 5 | supported | Open Library (vols 1941, 1955) | The chronicle passages on 1352 were not checked; the text already flags this. |
| C41 | Shlikhta 1999 and 2022 "are verified" | supported | DOIs | Add the 2022 editors (DeVille and Galadza). |
| C42 | Hirooka (1993) caught the church's re-emergence | plausible | NDL title | Pages conflict (340–361 vs 82–103). |
| C43 | Semana, "a Catholic writer", treats sects as a problem for the church | partly supported | BnF title; his 2015 book has a preface by abbé Amherdt | His Catholic identity is not confirmed by a catalogue. |
| C44 | Bizimana indicts the White Fathers | supported | Subtitle (BnF) | — |
| C45 | Linden "Eng. original"; Guichaoua English translation (verify) | supported | Open Library (Manchester UP 1977; U. Wisconsin Press 2015) | Remove the verify flag. |
| C46 | Nagai available in French | supported | BnF: *Les cloches de Nagasaki*, 1953 | — |
| C47 | "about 120 works in twelve languages" | approximately | The reference list has 113 entries | Fine as "about". |
| C48 | To-verify list: "Romanized readings of … Miyazaki 揚弘" | **erroneous** | NDL | No entry has 揚弘. Miyazaki is 賢太郎 (Kentarō, confirmed by NDL). The unresolved given name is Fukumoto's 保信. |

## 3. Counts

**Reference entries (113)**

| Status | Count |
|---|---|
| Verified, no change needed | 92 |
| Verified with a minor fix (romanization or typo: #2, #44, #45, #75, #109) | 5 |
| Wrong detail (#25 Fukumoto years, #46 Kitamori English year, #73 Ortiz bracket date, #83 Sasaki year, #84 Scarano year, #103 Takahashi 2004 title, #104 Takahashi 2020 not a book, #106 Watanabe year) | 8 |
| Verified with an added detail or a contradicted flag (#4 translator and original title, #22 pages, #31 pages, #58 IEP, #80 book exists, #91 editors, #92 editors, #107 pages) | 8 |
| Not found | 0 |
| Fabricated-likely | 0 |

In addition, two works cited in the text lack reference entries: Sandnes 1978, and Quintão 2002, which the section wrongly calls unfindable.

**Claims (48 checked)**

| Verdict | Count |
|---|---|
| Supported (including support from titles alone) | 32 |
| Plausible or not verifiable | 5 (C4, C15, C19, C42, C43) |
| Partly wrong or minor | 4 (C9, C18, C20, C36) |
| Wrong or mischaracterized | 6 (C7, C16, C23, C24, C27, C48) |
| Misleading | 1 (C17) |
