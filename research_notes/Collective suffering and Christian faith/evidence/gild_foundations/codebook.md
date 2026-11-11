# Codebook: gild_foundations

Written before coding (2026-11-11). Source of units: H. F. Westlake, *The Parish Gilds of Mediaeval England* (London: SPCK, 1919), Appendix "The Gild Certificates of 1389: An Analysis", pp. 137–238. Scan used: Internet Archive `parishgildsofmed00westuoft` (University of Toronto copy), PDF pages 161–262 (printed page = PDF page − 24). Cross-check: Toulmin Smith, *English Gilds* (EETS o.s. 40, 1870), Internet Archive `englishgildsorig00smit`.

## Important note on the nature of the text

Westlake's appendix is a **calendar** (English summary) of the returns made under the writs of 1 November 1388, not a transcription. "Verbatim" snippets in data.csv are verbatim **from Westlake's calendar** (or from Toulmin Smith's printed text where so labelled), not from the Latin/French/English originals in TNA C 47. The table has five columns: (1) certificate no. and language; (2) place, dedication and date of foundation; (3) origin, purpose and religious provisions; (4) friendly benefits to members; (5) remarks. Westlake's N.B.: where "founded" is used in column 3 the purpose of foundation is clearly stated in the original.

## Unit

One gild described in the appendix. A single certificate (one PRO number) sometimes covers several gilds, lettered (a), (b), (c)…; each lettered gild is a separate unit with the same `cert_no` and its own `sub` letter. A row that only continues a gild from the previous page is merged into that gild. Rows that are craft "statutes" with no fraternity element are still units (they are returns) but flagged `founders=craft`.

## Identification variables

| variable | rule |
|---|---|
| unit_id | sequential, `G0001`… in table order |
| cert_no | Westlake's certificate number (column 1); `sub` = letter (a), (b)… or blank |
| lang | L / F / E as given in column 1 |
| county | the most recent county heading in column 2 (Westlake prints the county in capitals at the first gild of each county) |
| place | town/parish name as printed (most recent place heading carries forward to subsequent entries until a new one) |
| dedication | dedication as printed (e.g., "Holy Trinity", "B.V.M.", "Corpus Christi") |
| page | Westlake printed page; `pdf_page` = page in the IA PDF |

## Foundation date

`date_raw`: the verbatim date line(s) in column 2 (e.g., "1346-7.", "No date.", "Time without memory.").

`date_class`, one of:
- **exact** — a single year or a two-year regnal span (e.g., "1346-7", "1379"). `found_year` = first year.
- **approx** — a year qualified by "c.", "about", "before", "after", or a range wider than two years, or a stated decade, or a reign ("temp. Edw. III"). `found_year` = stated year where one is given (for "before 1350", year = 1350 and flagged); otherwise blank.
- **after_pestilence** — dated only by reference to the pestilence (e.g., "after the great pestilence") with no year.
- **time_out_of_mind** — "time without memory", "time out of mind", "beyond memory", "of old", "long before" etc.
- **not_stated** — "No date." or column blank.

If column 2 gives only "No date" but column 3 or 5 gives a foundation year (e.g., "founded in 1360"), the year is taken from column 3/5 and `date_source` records the column. If column 3/5 gives "before the pestilence"/"after the pestilence" with no year, `date_class` = after_pestilence (or `approx` with `pre_pest_flag`) and the snippet is recorded.

`decade` = floor(found_year/10)*10 for exact and approx-with-year. `period`: **pre** = 1300–1348; **post** = 1349–1389; **early** = before 1300; blank otherwise. A year range "1348-9" (regnal year 22–23 Edw. III) is assigned by first year (1348 → pre); this is a known edge case and is listed separately.

## Pestilence mention

`pest_mention` = 1 if any column for the unit mentions pestilence, plague, mortality, death of brethren in the pestilence, "great death", "qualm" etc. `pest_snippet` = the verbatim clause. Also coded for the Toulmin Smith cross-check text where available.

## Purposes (binary, each 0/1; coded from columns 3–5 of the unit, plus inherited "General purpose as in (a)" — see below)

| variable | code 1 when the text states… | not coded |
|---|---|---|
| funeral | attendance at, or provision for, the funeral/burial/obsequies of members: "funeral", "burial", "bury", "buried", "corpse", "body (of a dead brother)", "hearse/herse", torches or candles "at funerals", "dirige … at funerals", payment for burial of poor members | requiems or masses for dead not tied to a funeral (→ masses) |
| masses | masses, prayers, obits, anniversaries, trentals, diriges, requiems, or a priest celebrating **for dead members/brethren/benefactors or "the souls of …"/"quick and dead"/"faithful departed"**; "mass for a dead brother" | masses in honour of a saint only, with no reference to the dead |
| chaplain | the gild maintains/finds/hires a chaplain or priest ("a priest to celebrate daily", "maintenance of chaplain", "to find a chaplain") | priest merely mentioned as officiant or as excluded from membership |
| lights | candles, tapers, torches, lights, lamps, wax, cierges (any purpose, including at funerals) | |
| aid | relief or mutual aid **for members**: any substantive entry in the "Friendly benefits" column, or text stating aid to poor/sick/aged/imprisoned/robbed/shipwrecked brethren, loans to members, payment for members' burial in poverty | alms to the poor in general (→ alms_general) |
| alms_general | alms/doles/feeding of the poor not restricted to members ("soul-alms to the poor", "poor of the town") | |
| feast | a communal meal/drinking: "feast" in the sense of a gild feast or general meeting with food/drink, "ale", "drink", "dinner", "eat", "breakfast", "potation", "bread and ale", "banquet" | "Feast of Corpus Christi" or any liturgical feast day |
| other | any other stated purpose: church fabric/ornaments, procession, pilgrimage, plays, roads/bridges, hospital, school, keeping peace/charity/love among members, craft regulation. `other_text` lists the keywords found. | |

**Inheritance rule.** Westlake often writes "General purpose as in (a)" for lettered gilds of one certificate. When a unit says this, its purposes include those of the referenced gild's column 3 ("general purpose"), and `inherit_from` records the referenced unit. Specific provisions listed after "General purpose as in (a)." are added.

**Content-free entries.** Where Westlake records only "Lists of names and payments only", "No ordinances", "Statutes only", or columns 3–4 are blank, all purpose variables are 0 and `content_free` = 1. These units are excluded from purpose percentages (denominator = units with any stated content).

## Founders

`founders`: **parishioners** (text says founded by parishioners / men of the town / brethren / "certain persons" / named laymen); **craft** (a craft or mystery is named as the gild's membership or founder, or Westlake marks C.S. "craft statutes"); **clergy** (founded by a rector, vicar, chaplain, priest, clerk, prior, bishop); **mixed** (clergy and laity together named); **not_stated** (default). `founders_snippet` records the text.

## Clergy role in governance

`clergy_gov` = 1 if the text gives a cleric (rector, vicar, parson, chaplain, priest, clerk, bishop, archdeacon, official, dean, prior) a stated role in the gild's government, finance, discipline or admission (e.g., "Transgressors … to be punished by Bishop of Ely", "the parson to be one of the keepers", "the chaplain shall keep the chest", "with consent of the vicar"). `clergy_excluded` = 1 if clergy are excluded from membership/office ("No chaplain … shall be admitted"). The gild merely hiring a chaplain is coded under `chaplain`, not `clergy_gov`. `clergy_snippet` records the text.

## Procedure

1. Page images are rendered from the IA PDF at 300 dpi, rotated (tables are printed landscape), segmented into cells on the printed rules, and each cell OCR'd (Tesseract 5, psm 6). The OCR text of each cell is saved (work/cells_all.json).
2. Units are assembled from the rows (county/place carried forward; continuation rows merged).
3. Codes are assigned by a transparent keyword/rule script (scripts/code.py) applying the rules above; every code of 1 stores the verbatim snippet that triggered it. Foundation dates are read from column 2 by rule; every date and every pestilence mention is then checked by the model against the page image (and corrections recorded in `check_note`).
4. Double coding: after a pause, a random 10% of units (seed 1389) is coded independently by reading the page images, without looking at the first codes, for date_class, found_year decade, period, pest_mention and the eight purpose variables, founders and clergy_gov. Agreement: percent agreement and Cohen's kappa per variable.
5. Cross-check with Toulmin Smith: for returns that Smith prints in full and can be matched by place + dedication, compare foundation date statement and purposes; record discrepancies.

## Examples

- Cambridge, Annunciation B.V.M. (cert. 4), "1379": date_class=exact, found_year=1379, period=post; lights=1 ("A candle before the image of the Virgin"); funeral=1 ("Four torches … for funerals of members at whose requiems the brethren will attend"); masses=1 ("requiems"); aid=1 (benefits column: "Brethren who become poor … 7d. weekly"); clergy_excluded=1 ("No chaplain … shall be admitted").
- Bottisham, Holy Trinity (cert. 3a), "Time without memory": date_class=time_out_of_mind; lights=1; masses=1 ("attend mass for a dead brother or sister"); alms_general=1 ("A halfpenny to the poor in soul-alms"); other=fabric.
- Cambridge, St Katharine (cert. 6): clergy_gov=1 ("Transgressors against the statutes to be punished by Bishop of Ely or his officer").
