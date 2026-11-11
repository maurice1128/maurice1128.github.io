# Codebook: London Husting wills, 1320–1400 (project `husting_wills`)

Written before coding (2026-11-11). Rules were drafted from keyword-in-context listings of entries *outside* the reliability sample; the 10% reliability sample (198 wills, drawn with `random.seed(20261111)` before any rule was written) was not looked at while the rules were written.

## Source and unit

- Source: Reginald R. Sharpe, ed., *Calendar of Wills Proved and Enrolled in the Court of Husting, London, A.D. 1258–A.D. 1688*, Part 1 (1889) and Part 2 (1890), as digitised on British History Online (BHO), one web page per regnal-year roll.
- **Unit = one calendared entry** (one testator's will as summarised by Sharpe). An entry begins with the testator's surname in bold and ends with its roll locator, e.g. `Roll 74 (13)`. Codicils, later court notes ("Whereupon came …") and second testaments printed inside the same entry belong to that entry.
- **Scope**: every entry whose *enrolment* date falls in calendar years 1320–1400 inclusive. The full population is coded (no sampling was needed: 1,980 entries).
- Entries with no bequest content (e.g. "[Vacant space left for insertion of will]") are kept and flagged `empty_entry = 1`; they are excluded from proportions.

## Identification variables

| Variable | Rule |
|---|---|
| `will_id` | HW0001… in calendar order |
| `vol`, `page`, `bho_page`, `roll` | Volume (1 = 1889, 2 = 1890), printed page on which the entry begins, BHO page slug, and Sharpe's roll locator `Roll N (M)` |
| `regnal_heading` | BHO page title, e.g. "23 Edward III (part 1 of 2)" |
| `court_heading` | The court-date heading under which the entry is printed (e.g. "Monday next after the Feast of S. Hilary [13 Jan.]") |
| `enrol_year` | Calendar year of the court date: regnal year + the day/month given in square brackets in the court heading. Regnal years begin 8 July (Edward II), 25 Jan. (Edward III), 22 June (Richard II), 30 Sept. (Henry IV); years begin 1 Jan. (modern style). |
| `will_year` | The A.D. year in the "Dated …, A.D. YYYY" clause, if any (as printed; Sharpe normally gives modern-style years). Blank if "No date" or no A.D. year. |
| `period` | P1 = enrolled 1320–1348; P2 = 1349–1360; P3 = 1361–1375; P4 = 1376–1400. |
| `testator`, `occupation` | Name as printed; occupation/status words printed after the name or inside the parentheses (e.g. "fishmonger", "Knt.", "clerk", "relict of …"). |
| `sex` | F if the parenthesis contains *wife of / relict / widow / daughter of* or the forename is a female name, or if the entry refers to the testator as "her"/"she" more than "his"/"he"; otherwise M. Ambiguous cases are listed in `analysis` output. |
| `cleric` | 1 if the occupation/title contains chaplain, clerk (in holy orders sense cannot be separated: "clerk" counted), rector, vicar, parson, canon, priest, prebendary, dean, archdeacon, or the forename is "Sir X" *and* no "Knt." |

## Coding rules common to all bequest variables

1. **A bequest = the testator gives money, goods, rent or property (outright, in remainder, in trust, or as a charge on property) to, or for, the beneficiary or purpose.** Contingent remainders and gifts-over ("in default … to the Mayor and Commonalty") count.
2. **The burial clause does not count** ("To be buried in the church of the Friars Minors" alone ≠ a bequest to the friars). The burial sentence is coded separately (`burial_site`) and is used only to resolve later references to "the said church".
3. **Places used as addresses do not count** ("a tenement near the Friars Preachers", "in the parish of S. Augustine near S. Paul's Gate", "held of the Prior of Christ Church").
4. **Gifts to individual religious do not count as gifts to the institution** ("To Friar John his son …", "Katherine his sister, a Minoress"). A gift to "the friars" or "each order of friars" does count.
5. A will can carry any number of codes. Each code = 1 if at least one qualifying passage exists; the qualifying passage(s) are copied verbatim into `<variable>_snip`.
6. Sharpe's summaries frequently abbreviate ("Bequests to the said church … religious orders, hospitals, &c."). Code what is printed; "&c." is not expanded.

## Bequest indicators (binary)

| Variable | Code 1 when the entry … | Examples (from the calendar) | Not coded |
|---|---|---|---|
| `parish` | gives to a **parish church** or its fabric/work, high altar, rector, vicar, parson, parish chaplains/"ministers", churchwardens or parishioners as such; tithes forgotten; "Bequests to the said church" where the said church is a parish church. Any parish church (own or another, in or outside London). | "To the high altar of his parish church of S. Mary Magdalen … for tithes … forgotten"; "Bequests to the fabric of the aforesaid church, its chaplains"; "remainder to the aforesaid church of S. Mary Magdalen for pious uses" | a chantry/light merely *located* in the parish church (coded `chantry`/`lights`); burial there |
| `chantry` | provides for a **chantry**, chantry priest(s), or a chaplain/priest to celebrate for the soul(s) for any term (perpetual or for years), including property charged with a chantry and chantries in remainder. | "charged with the maintenance of a chantry in the said church for the first five years"; "four chantry priests to celebrate for the good of his soul" | an existing chantry named only as an address or as the testator's own office |
| `chantry_perpetual` | sub-code of `chantry`: the passage says perpetual / for ever / in perpetuity / "and their successors", or founds a chantry on property in mortmain | "to the Dean and Chapter … and their successors, so that they maintain a chantry" | |
| `chantry_temporary` | sub-code of `chantry`: chantry for a stated number of years or for a life | "Provision made for a chantry for two years" | |
| `obit` | provides for an **obit, anniversary, year's mind** | "subject to certain charges for the aforesaid chantry and for his obit" | |
| `masses` | (additional variable) **trentals, masses, Placebo/Dirige, requiem** not described as a chantry | "a trental of masses by the Augustinian Friars" | |
| `lights` | gives for **lights, lamps, tapers, torches, candles, wax** (church lights or funeral lights) | "for maintaining a light in the same"; "five round wax tapers … to burn around his corpse" | wax-chandler as occupation |
| `fraternity` | gives to a **fraternity, brotherhood, gild** (religious or craft fraternity) or its light/alms/wardens | "To the alms of the Fraternity of S. John the Baptist of the Tailors" | Guildhall |
| `friars` | gives to **friars** of any order (Minors/Grey, Preachers/Black, Carmelites/White, Augustinian/Austin, Crutched, Pied, of the Sack), to their convents or "the four orders", or for friars' masses/attendance | "to each order of mendicant friars"; "a trental of masses by the Augustinian Friars" | individual named friar; friars' house as address |
| `monastic` | gives to a **monastery, priory, abbey, nunnery, house of canons, the Charterhouse, the house of S. Thomas de Acon, the Minoresses, anchorites/recluses**, their prior/abbot/convent, or "religious orders"/"religious houses" generically | "To the Prior and Convent of the church of S. Bartholomew de Smethefeld certain houses"; "Bequests to religious orders" | individual monk/nun; rents owed to a house ("held of the Prior of …") |
| `hospital` | gives to a **hospital, spital, leper house** or its inmates (S. Bartholomew's hospital, S. Mary without Bishopsgate, Elsing Spital, S. Thomas of Southwark, S. Giles, Le Lok, Bedlem, etc.) | "the lepers at le lokes"; "the hospitals of Elsyngesspetull, S. Bartholomew in Smethefeld" | |
| `charity` | gives to **the poor, prisoners/prisons, poor girls' marriages, bedridden, roads, highways, bridges (incl. London Bridge), causeways** | "five shillings … to the work of London Bridge"; "the poor inmates of Neugate" | Bridge as address ("near London Bridge", "Bridge Street", "held under the Wardens of London Bridge") |
| `cathedral` | gives to **S. Paul's** (fabric, old/new work, Dean and Chapter, shrine of S. Erkenwald, its chaplains, its indulgence/pardon) | "to the fabric of S. Paul's Church"; "to the Dean and Chapter of S. Paul's … so that they maintain a chantry" | burial in S. Paul's churchyard; "S. Paul's Gate/Wharf/Chain" as address; individual canons |
| `named_chaplain` | names a chaplain/priest (by name or as "Sir N.") **to celebrate or pray**, or gives to a named chaplain in a passage that asks for prayers/masses/chantry | "to Sir Walter … chaplain, to celebrate for his soul" | gifts to a named chaplain with no prayer request (e.g. a son who is a chaplain) |
| `pious_uses` | (additional) property or residue to be sold or applied **"for pious (and charitable) uses"** without further specification | "to be sold for pious uses" | |
| `pestilence` | mentions plague, pestilence, mortality, epidemic (verbatim snippet) | "seeing the peril of this world and especially of the existing plague" | "the death of X" |

## Control of intercession (who holds the property for chantry/obit)

`chantry_trustee` (only for wills with `chantry` or `obit` = 1), from the passage(s) that set up the chantry/obit:

- `lay_corporate` — Mayor/Aldermen/Commonalty/Chamberlain of London, Wardens of London Bridge, wardens of a craft/mistery/company, or a fraternity (as holder, supervisor or gift-over taker).
- `parish_body` — rector and/or churchwardens/parishioners of a parish.
- `church_corporate` — Dean and Chapter of S. Paul's, a prior/abbot/abbess and convent, master and brethren of a hospital or house.
- `private` — none of the above named: property left to wife, heirs, executors or others charged with the chantry ("charged with the maintenance of a chantry"), or provision with no holder named.

If several are named, all are recorded (`;`-separated); binary flags `trustee_lay_corporate`, `trustee_parish_body`, `trustee_church_corporate`, `trustee_private` are derived.

## `burial_site` (from the "To be buried …" clause)

parish / friars / religious_house / hospital / st_pauls / other_or_unspecified / none_stated.

## Procedure

1. All rules are implemented as regular expressions with context exclusions in `scripts/code_wills.py` (copied into this folder); the same text and rules always give the same codes.
2. The rule coder is the *first* coder. The *second* coder is a human-style close reading by the model of the 198-entry random sample, done from the entry text alone without viewing the rule output, recorded in `double_coding.csv`. Agreement (percent agreement, Cohen's kappa) is reported per variable; disagreements are listed and characterised (false positives vs. false negatives of the rules).
