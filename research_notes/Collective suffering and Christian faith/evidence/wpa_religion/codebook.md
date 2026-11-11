# Codebook: religion under slavery in the WPA ex-slave narratives (project `wpa_religion`)

Written 2026-11-11, before any narrative in the sample was coded. A pilot of 51 narratives (`reading/slavery_primary_fulltext.md` §10) supplied the categories. This recode starts from scratch and fixes three pilot weaknesses: targeted (non-random) additions, no rule for "mixed" worship, and no separation between the informant's own faith and that of others.

## Unit, scope and evidence

- **Unit:** one narrative, meaning one informant entry in a volume's INFORMANTS list in the Project Gutenberg transcription of *Slave Narratives: A Folk History of Slavery…* (1941). Several interviews of the same informant listed under one entry count as one unit. If two people are interviewed jointly under one entry, only the TOC-named informant and the family members they describe are coded.
- **Time scope:** every variable refers to slavery (before 1865) unless its definition says otherwise. Events dated "during the war" count as before 1865. On the plantation of the informant (or of the parent or kin they describe), "before freedom" or "in slavery times" also counts as before 1865.
- **Whose testimony:** the informant's own memory, and what the informant reports of parents, kin or fellow slaves (hearsay is included; the snippet shows it). Interviewer commentary is coded only when it reports what the informant said. Sentences inside a narrative that are general history and not attributable to the informant are not coded.
- **Evidence rule:** every code other than `ns` / `not_stated` needs a verbatim snippet of at most about 300 characters, copied exactly from the Gutenberg text. The analysis script checks each snippet against the source text after normalising whitespace and quotes. The locator is the Gutenberg eBook number, the volume, the TOC name, and the line range of the snippet in the Gutenberg .txt file.
- **When in doubt, code `ns`.** A statement that is only implied is not coded.

## Variables

### 1. Worship control, before 1865

First code four component flags (y/n), then derive `worship_control`.

| flag | code y when the narrative reports... | examples |
|---|---|---|
| `wc_white` | worship of the enslaved conducted or supervised by whites: a white preacher; attendance at the white church (gallery, back seats); the master, mistress or overseer reading, praying or teaching religion; an overseer present at a Black meeting; a Black preacher told what to preach | "we went to the white folks' church and sat in the gallery"; "Marster read the Bible to us Sunday" |
| `wc_blackled` | Black-led religious meetings, preaching or prayer meetings held openly or with permission and without reported white supervision: a slave preacher, prayer meetings in the quarters, a slave-built brush arbor or church | "we had prayer meetings in the quarters"; "old Uncle Ned preached to us" |
| `wc_secret` | clandestine worship or prayer hidden from whites: slipping off to the woods or hollows, hush harbors, a turned-down pot or kettle, a wet quilt, praying "in secret", meetings broken up by patrollers because they were unauthorised | "they turned a pot down at the door to catch the sound" |
| `wc_forbidden` | religion, prayer, church or meetings forbidden or denied to the enslaved, or punished | "Marster didn't 'low us to go to church or pray" |

Derived `worship_control`:
- `not_stated`: no flag is y.
- Exactly one flag y: `white_supervised`, `black_led_permitted`, `secret`, or `forbidden`.
- Only `wc_forbidden` and `wc_secret` are y: `secret` (secret worship is the community's response to the ban; the forbidden flag is kept in data.csv).
- Any other combination of two or more: `mixed`.

Derived for the key test: `black_control_pre1865` = y if `wc_blackled` or `wc_secret` is y. It is n if a worship mode is stated but neither of these is y (white-supervised and/or forbidden only). It is ns if worship control is not stated.

### 2. `obedience_preaching` (y / n / ns)
- **y:** preaching heard by the enslaved (white or Black preacher) is reported as centred on obedience to masters and on not stealing, lying or running away ("obey your master"; "don't steal marster's hogs"; "servants be obedient"). This includes preaching that says the slaves will never be free. The obedience theme must be the main or only content reported.
- **n:** the content of preaching under slavery is described and is not obedience-centred ("he preached the gospel", "about heaven and hell", "about Jesus"), or the informant denies an obedience message.
- **ns:** preaching content under slavery is not described, including mere attendance or a preacher's name without content.

### 3. `attitude_white_preachers` (negative / positive / neutral / ns)
The informant's expressed evaluation of white preachers, the white church, or the master's or mistress's religion as it bore on the enslaved, during slavery. The attitude is the one expressed at the interview.
- **negative:** criticism, irony, distrust, resentment of segregation or surveillance in church, "that wasn't real religion", "nothing about Jesus", the master's hypocrisy.
- **positive:** praise or gratitude ("he was a fine preacher", "Missus taught us the Bible and I thank her", "glad to go to the white church").
- **neutral:** white-led worship is described without evaluation.
- **ns:** white preachers, white churches and the master's religion are not mentioned.
- If both a positive and a negative judgement appear, code the one more strongly expressed and note both in `notes`. If they are equal, code negative and say so in `notes`.

### 4. `conversion_timing` (before_1865 / after_1865 / ns)
The informant's own conversion, "getting religion", baptism as a believer, or joining a church.
- **before_1865 / after_1865:** decided by an explicit date, by "after freedom" / "after the war" / "in slavery time", or by a stated age at conversion together with a stated birth year or age in a dated interview. When the arithmetic is needed, the snippet gives the age statement and the notes give the calculation. If the date falls within ±1 year of 1865, code ns.
- If there are several events (for example, baptism in slavery and joining a church later), code the first conversion or getting religion. If only a joining is stated, code the joining.
- **ns:** no datable event.

### 5. `faith_commitment_before_freedom` (y / n / ns) and `faith_subject` (self / kin / others / ns)
- **y:** an explicit statement that an enslaved person, before 1865, held personal faith or practised it. This covers personal prayer, conversion or "getting religion", shouting or "getting happy" in worship, believing or trusting God, and seeking religion (mourning in the woods). Required attendance at a white service alone does not count. The bare existence of a meeting also does not count: an identifiable person's devotion or prayer must be stated (a group statement such as "the slaves would pray and shout" is enough and gets subject = others).
- **n:** an explicit statement that the informant, or the enslaved people described, had no religion or faith before freedom ("we didn't know nothing about God").
- **ns:** neither.
- **`faith_subject`:** the closest subject with a y statement, in the order self > kin (parent, grandparent, sibling, spouse) > others (fellow slaves, "the slaves").

### 6. `postwar_black_church` (y / n / ns), plus `postwar_church_any` (y / ns)
- **`postwar_church_any` y:** the informant reports church membership, attendance or office after 1865 (including 1930s membership).
- **`postwar_black_church` y:** the church is identified as Black-run, by any of these: a Black or colored congregation; a Black denomination (AME, AME Zion, CME/Colored Methodist, "colored Baptist"); the informant or kin as its pastor, preacher, deacon or founder; a postwar withdrawal from a white church; a Black pastor named.
- **n:** postwar membership is in a white-run or mixed congregation, or the informant says they have joined no church.
- **ns:** no postwar church is mentioned, or a church is mentioned without anything that identifies its control (then `postwar_church_any` is y and `postwar_black_church` is ns).

### 7. `prayed_for_freedom` (y / n / ns)
- **y:** enslaved people (the informant, kin or others) are reported praying, singing or holding meetings for freedom or deliverance from slavery before emancipation, including prayers that the Union would win.
- **n:** explicit denial ("we never prayed for freedom", "didn't know what freedom was" said of prayer).
- **ns:** otherwise.

### 8. Interviewer and `interviewer_race` (Black / white / unknown)
- **interviewer:** as given in the narrative's header or footer (typed or handwritten [HW]), else "not recorded".
- **Black:** (a) an in-text marker ("Negro Writers' Unit" in the Florida volume; "colored" or "[HW: (Colored)]" after the name), or (b) the name is documented as a member of a Negro unit or as a Black interviewer in a published source:
  - Encyclopedia of Arkansas, "WPA Slave Narratives": Samuel S. Taylor and Pernella M. Anderson, Arkansas.
  - Notable Folklorists of Color, "The Negro Units and Projects of the Federal Writers' Project…": Florida, Georgia, South Carolina and Virginia unit members. These include Georgia's Minnie B. Ross, Ardella/Adella S. Dixon, Edwin Driskell, Louise Oliphant and Willie H. Cole; South Carolina's Augustus Ladson and Laura Lee Middleton; and Virginia's Susie R. C. Byrd, Claude W. Anderson, Thelma Dunston and David Hoggard.
- **white:** an in-text marker "[HW: (White)]" (Georgia: Sadie B. Hornsby, Grace McCune). The marker applies to every narrative by that interviewer.
- **unknown:** otherwise. Most white interviewers are not documented as white, so "unknown" mostly means probably white but undocumented, and is reported as such.

**Rules added 2026-11-11, after coding.** The codebook as written before coding did not cover these cases. They were decided when the interviewer columns were corrected (`interviewer_race_corrections.md`), and `data.csv` follows them.

- **Two or more interviews of one informant by different interviewers.** The unit is the entry, so it gets one value.
  - `interviewer` lists every credited interviewer in text order, separated by "; ".
  - `interviewer_race` is Black if any of them is documented Black. Otherwise it is white if any of them is documented white. Otherwise it is unknown.
  - `interviewer_race_source` names the interviewer who carries the documentation and gives the line of each credit.
  - Reasons. The variable exists to set apart testimony given to a Black interviewer (`results.md` §3.4 C and §3.5), so an entry partly taken down by a documented Black interviewer cannot stand among the narratives given to white or unknown interviewers only. "Unknown" means undocumented and probably white, so a documented white interviewer beside an undocumented one is the same case with documentation.
  - The rule decides six entries in the sample: Henry Brown, SC (Jessie A. Butler; Augustus Ladson) is Black; Alice Green, GA (Corry Fowler; Sadie B. Hornsby) is white; Sarah Douglas, AR (Pernella M. Anderson; Carol Graham) and Isaiah Green, GA (Minnie B. Ross; Edwin Driskell) stay Black; Tom Windham and Rachel Harris, AR, stay unknown. No sampled entry has both a documented Black and a documented white interviewer; if one did, the first clause would make it Black.
- **Where the credit stands.** The header is the block of short lines between the run of blank lines that ends the previous narrative and the informant's own text. It often lies above the informant's name ("Worker:", "Reporter:", "Prepared by", "Field Worker", or a bare name). The footer is the "Source: … / Interviewer: …" block that closes the informant's text. A block that follows the narrative after a run of three or more blank lines is the header of the next narrative and is not used. An editor ("Edited by", "Editor:"), rewriter or typist is not the interviewer.
- **Segments that also hold another informant's interview.** `interviewer` and `interviewer_race` follow the worker credited on the TOC-named informant's own interview. A credit that heads another informant's interview inside the segment is not used.
- **Surname-only credits in the Georgia Atlanta district.** "Driskell", "E. Driskell" or "E.F. Driskell" in a District 5 header is read as Edwin Driskell of the Georgia Negro unit. The same position carries "By E. Driskell" (pg13602.txt l. 8647) and "Edwin Driskell" (pg22166.txt l. 1563); "Whitley" beside it is the typist ("Typed by A.M. Whitley").

### 9. Context fields (not hypothesis variables)
- `age_1937`: the informant's stated age at the interview, or computed from a stated birth year (1937 assumed if the interview is undated); best effort, may be blank.
- `hearsay_only`: y if every religion statement coded is explicitly second-hand ("I heard them say") or the informant was born after about 1860 and reports nothing first-hand.
- `notes`: ambiguities, both-way attitudes, calculations.

## Decision examples (invented paraphrases, for calibration; not data)
- "We went to the white church and set in the gallery. At night we'd have prayer meeting in the cabins, and Mammy prayed for us to be free." → wc_white y, wc_blackled y → mixed; obedience ns; attitude neutral; faith y (kin); prayed_for_freedom y.
- "Marster wouldn't let us have no church. We'd slip off to the hollow and turn a wash pot down." → forbidden + secret → secret; faith y (others) only if praying or singing is described.
- "The white preacher told us to obey Massa and not steal. Nothing about heaven for us." → white_supervised; obedience y; attitude negative.
- "I jined the church after freedom, when I was twenty." → conversion after_1865.
- "I've been a member of Bethel A.M.E. church fifty years." → postwar_black_church y.
