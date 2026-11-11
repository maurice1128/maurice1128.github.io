# Independent second-coder reliability (project `wpa_religion`)

Prepared 2026-11-11. Compares the first coder's codes in `data.csv` with a blind second coding in `second_coder.csv` for the 40 narratives listed in `double_code.csv`. `python3 analysis.py` (section 10) re-prints the table and the disagreement list.

## Result in brief

- **Worship control and obedience preaching were reproduced exactly** (40/40 on all four component flags, `worship_control`, `black_control_pre1865` and `obedience_preaching`; κ = 1.00).
- **Faith before freedom: κ = 0.83** (37/40). **Attitude to white preachers: κ = 0.82** (35/40). **Postwar church, any: κ = 0.64** (33/40). Conversion timing and postwar Black church: 39/40 each, κ = 0.79 (few non-`ns` cases, so one disagreement moves κ a long way).
- **`prayed_for_freedom` could not be assessed:** both coders coded all 40 `ns`, so κ is undefined.
- **Every one of the 20 disagreements on hypothesis variables runs the same way:** the first coder has `ns` or `neutral` where the second coder has a substantive code. The first coder never coded something the second coder left `ns`. The first-pass counts for faith, postwar church and non-neutral attitude are therefore conservative.

## How the second coding was done

- **Coder.** A separate session of the same model family as the first coder, started with no access to the first session. It is independent in the sense of not having seen the first codes or the first coder's working extracts. It is not a human rater and it shares the first coder's training, so shared reading habits can still inflate agreement.
- **Blinding.** Before coding, only `codebook.md` was read. The 40 `nid` values were taken from `double_code.csv`, and the eBook number, informant name, segment line range and interviewer name were taken from `data.csv` and `corpus_screen.csv` by a script that kept those columns and discarded all others. No code column, no snippet or note column, and neither `results.md` nor `analysis.py` was opened until `second_coder.csv` had been written (SHA-256 `9afe0353…f21f523`, unchanged since).
- **Texts.** The 22 Project Gutenberg eBooks were downloaded afresh and each narrative was read in full at the segment line range, not as keyword extracts. This differs from the first coder, who read keyword-selected extracts capped at about 3,200 characters.
- **Codes.** All codebook variables were coded, with a verbatim snippet for every non-`ns` code. A script checked every snippet against the Gutenberg text after normalising whitespace and quotes; all pass.
- **Unit corrections.** Two segments contain material on other people, which was not coded: Laura House (AR; lines 9475–9898 are a multi-informant piece on Pinkey Howard and others) and Jesse Williams (SC; lines 6346–6392 are a short piece on Mary Williams).

## Agreement table (first coder in `data.csv` vs second coder, n = 40)

| variable | agreement | Cohen's κ | non-`ns` cases, first / second | first coder's same-session recode vs second coder (κ) |
|---|---|---|---|---|
| wc_white | 40/40 = 100% | 1.00 | 20 / 20 | 1.00 |
| wc_blackled | 40/40 = 100% | 1.00 | 3 / 3 | 1.00 |
| wc_secret | 40/40 = 100% | 1.00 | 6 / 6 | 1.00 |
| wc_forbidden | 40/40 = 100% | 1.00 | 1 / 1 | 1.00 |
| worship_control (derived) | 40/40 = 100% | 1.00 | 24 / 24 | 1.00 |
| black_control_pre1865 (derived) | 40/40 = 100% | 1.00 | 24 / 24 stated; 9 / 9 y | 1.00 |
| obedience_preaching | 40/40 = 100% | 1.00 | 5 / 5 (4 y, 1 n) | 1.00 |
| attitude_white_preachers | 35/40 = 87.5% | 0.82 | 21 / 21 | 0.89 |
| conversion_timing | 39/40 = 97.5% | 0.79 | 2 / 3 | 0.79 |
| faith_commitment_before_freedom | 37/40 = 92.5% | 0.83 | 11 / 14 | 0.83 |
| faith_subject | 37/40 = 92.5% | 0.85 | 11 / 14 | 0.86 |
| postwar_church_any | 33/40 = 82.5% | 0.64 | 12 / 19 | 0.69 |
| postwar_black_church | 39/40 = 97.5% | 0.79 | 2 / 3 | 0.79 |
| prayed_for_freedom | 40/40 = 100% | NA (all `ns` in both) | 0 / 0 | NA |
| *context:* interviewer_race | 38/40 = 95% | 0.85 | 7 / 9 documented | – |
| *context:* hearsay_only | 37/40 = 92.5% | 0.63 | 3 / 6 y | – |

Across the 14 hypothesis variables, 540 of 560 cells agree (96.4%), and 29 of the 40 narratives agree on every one of them.

Three cautions about reading the table:

1. **κ = 1.00 on the worship flags rests on 24 narratives that state a mode**, and only 3 Black-led, 6 secret and 1 forbidden case. It shows the flags are applied the same way; it does not bound the error for rare categories tightly.
2. **Attitude agreement is weaker than κ = 0.82 suggests.** Much of the agreement is the 19 narratives both coders left `ns`. Among the 21 where both state an attitude, agreement is 16/21 (76%, κ = 0.63).
3. **`age_1937`** was not scored with κ. It differs in four rows where the first coder left it blank and the second coder found or computed an age (Alice Green 76, Millie Simpkins 109, Emma Chapman about 85, Carrie Davis about 83).

## Every disagreement, with both codes and snippets

"Outside extract" was checked by re-running `pipeline/packets.py` on each segment and testing whether the second coder's snippet falls inside the extract the first coder would have read.

| # | narrative | variable | first coder | second coder | class |
|---|---|---|---|---|---|
| 1 | Mahala Jewel (GA-IV-2-040) | attitude | neutral: "All de slaves went to church wid deir white folks, and sot in de back part of de meetin' house." | positive: "Out dar in de car'iage us could listen to de singin' and it sho' did sound sweet. Meetin' days was big days." | judgement |
| 2 | Anthony Dawson (OK-XIII-016) | faith, faith_subject | ns | y, self: "I always been a deep Christian and depend on God and know his unseen Son, the King of Glory. I learned about Him when I was a little boy." (l. 2638–2639) | outside extract |
| 3 | Charlie Hudson (GA-IV-2-028) | attitude | neutral: "Sometimes when dere was a jubilee comin' off, slaves was 'lowed to go to deir Marsters' church." | positive: "I was burnt up den, 'cause I didn't have de privilege of ridin' 'hind Miss Betsey on old Puss no more when she went to meetin'." | judgement |
| 4 | Charlie Hudson | postwar_church_any | ns (note: "joined church after Bible verse, undated") | y: "When dey read dis passage of de Bible to me, I 'cided to jine up wid de church." | codebook ambiguity |
| 5 | Mandy Hadnot (TX-XVI-2-026) | faith, faith_subject | ns (note: "date relative to 1865 unclear") | y, self: "Den she make me say de Lord Prayer for her jus' like she allus make me say it for a night prayer when I lil' gal." | judgement |
| 6 | Mandy Hadnot | postwar_church_any | ns | y: "He come two mile every Sunday and us go to Lugene Baptist church." (told after "When freedom come", when she was 16) | judgement |
| 7 | Elijah Henry Hopkins (AR-II-3-082) | attitude | neutral: "…might go to a church on one of them. But you couldn't go no place where there wasn't a white man looking on." | negative: same sentence, read as resentment of surveillance | judgement |
| 8 | John F. Van Hook (GA-IV-4-007) | attitude | neutral: "so we all went to the white folks' church, about two miles away; it was called Clarke's Chapel." | positive: "long after we were free Mr. Tommy would give long talks at our meetings. We loved to listen to him" (l. 2504–2505) | outside extract (truncated) |
| 9 | John F. Van Hook | postwar_church_any, postwar_black_church | ns, ns | y, y: "after the war, darkies used to meet at each others' houses for religious services until they got churches of their own." (l. 2500–2502) | outside extract (truncated) |
| 10 | Uncle Jake (GA-IV-2-039) | conversion_timing, faith, faith_subject | ns (note: "white family's reminiscence of 'Uncle Jake', not first-person ex-slave testimony; not coded") | before_1865, y, self: "I's been a vessel ob His for nigh onto sixty years" (speech quoted in a scene set during the war) | codebook ambiguity |
| 11 | Frank Menefee (AL-I-083) | attitude | neutral: "De preacher was Rev'ren Frank Hugely." | positive: "I used to love to hear dem sing." | judgement |
| 12 | Frank Menefee | postwar_church_any | ns | y: "Some says de church can't save you, but I sho' feels safer in hit, an' I jined 'caze I wants to be better dan I was an' try to be saved." | codebook ambiguity |
| 13 | Silva Durant (SC-XIV-1-075) | postwar_church_any | ns | y: "I was married over dere in Bethel M. E. Church" | codebook ambiguity |
| 14 | Julia Grace (AR-II-3-017) | postwar_church_any | ns | y: "Then I puts 'em on and switches into church and ever'body thinks they has been ironed." | codebook ambiguity |
| 15 | Carrie Davis (AL-I-033) | postwar_church_any | ns (note: "joined church undated") | y: "Dat's why I j'ined de church and still tries to de right." | codebook ambiguity |

Context variables:

| # | narrative | variable | first coder | second coder | class |
|---|---|---|---|---|---|
| 16 | J.M. Parker (AR-II-5-076) | interviewer_race | unknown ("not recorded") | Black: "Interviewer: Samuel S. Taylor" stands at l. 6903, five lines above the segment start at l. 6908 | outside segment |
| 17 | Alice Green (GA-IV-2-005) | interviewer_race | unknown (Corry Fowler) | white: the entry holds two interviews; the second (l. 1084 onward) is "Written by: Sadie B. Hornsby" | outside extract, and no codebook rule for two interviewers |
| 18 | Alice Green | hearsay_only | n | y: age 76 is given only in the second interview's header, and she "warn't no bigger dan dis here little Sallie Mae" (a child of two or three) when the war ended | outside extract |
| 19 | John F. Van Hook | hearsay_only | n | y: born 1862; "What I know about the things that took place during the war was told me by my mother and other old people." (l. 1979–1980) | outside extract, and codebook ambiguity |
| 20 | Uncle Jake | hearsay_only | n | y: the whole piece is a third party's account | codebook ambiguity |

## Classification of the disagreements

Counting each differing cell among the 14 hypothesis variables (20 cells):

| class | cells | narratives | what it is |
|---|---|---|---|
| First coder missed text outside the keyword extract | 5 | 2 | Dawson's statement of lifelong faith has "Christian", "God" and "the Word" but none of the extract keywords. Van Hook's narrative is 36,700 characters and the extract was cut at the cap before his account of postwar meetings. |
| Codebook ambiguity | 8 | 6 | (a) Whether an undated "I joined the church" counts as postwar or 1930s membership: Hudson, Menefee, Carrie Davis. (b) Whether incidental church use counts as attendance: Grace, Durant. (c) Whether a third party's sketch counts as the informant's testimony: Uncle Jake, 3 cells. |
| Judgement difference | 7 | 5 | Mild affect read as neutral or as evaluation (Jewel, Hudson, Menefee, Hopkins), and dating by narrative order in Hadnot (3 cells). |

Notes on the classes:

- **The undated-joining rule is systematic, not noise.** The first coder consistently left `postwar_church_any` as `ns` when a joining was undated, and said so in `notes`. The second coder counted these because the statements are given in the present tense as answers to the questionnaire's "why you joined a church" item. Either rule is defensible; the codebook should state one. The first coder's own two passes split on Julia Grace for the same reason.
- **On Uncle Jake the first coder's reading is probably the better one.** The piece is a white author's literary sketch based on a story from a third party. The codebook's unit rule ("one informant entry in the INFORMANTS list") pulls the other way, which is why the second coder coded the quoted speech. The codebook should exclude such pieces explicitly.
- **The attitude disagreements all move away from neutral.** Four of the 13 narratives the first coder called neutral were called positive by the second coder and one negative. The codebook gives "glad to go to the white church" as a positive example but no rule for weak affect ("it sho' did sound sweet", "I used to love to hear dem sing").
- **Full reading added little on the worship variables.** No worship flag changed. The cost of the extract method shows only in faith statements without keywords and in narratives long enough to hit the cap (19 of the 400, per `results.md`).

## Decisions the second coder made where the codebook is silent

These were fixed before unblinding and happen to match the first coder in most cases; they are listed because a human coder could reasonably decide otherwise.

- **Worship flags describe the informant's own (or kin's) setting.** Bans reported for a neighbouring plantation (John Brown, OK) or "some of the plantations" (Dawson) were noted, not flagged.
- **A meeting with no stated controller gets no flag.** "We hed church under a arbor" with a preacher of unstated race (McMillan, OH) and "we'uns goes to church and de preacher's name, it was Jack Ditto" (Bormer, TX) were left `not_stated`.
- **First-person plural counts as self** for `faith_subject` when the informant was old enough to take part (Gill, Rhodes, Carruthers).
- **A white preacher who is the master, described as kind but with no worship described,** was coded attitude `neutral` (Emma Chapman), because the codebook reserves `ns` for "not mentioned".
- **Punishment for shouting in the fields the day after church** (Carrie Davis) was not coded as religion forbidden.
- **Conversion needs an explicit date** as the codebook says. Joinings dated only by narrative order (Hadnot at about nine, before "When freedom come"; Menefee's baptism) were left `ns`.
- **`hearsay_only` was applied to slavery-era religion statements,** not to the informant's own postwar membership.

## What this means for the results in `results.md`

1. **Worship control (44.7% Black control; 53.4% white-supervised only) and obedience preaching (25/37).** Reproduced exactly on the subsample. No rewording needed. These can now be described as replicated by an independent blind coder on 40 narratives, with the caveat that the second coder is a model session and that the subsample holds only 5 narratives with preaching content.
2. **Key test (Black control × faith before freedom, OR 4.1).** The exposure variable is fully reliable here. The outcome is undercounted by the first coder: 11 of 40 against 14 of 40. The three additions fall one each in a Black-control narrative, a white-supervised narrative and a narrative with no worship mode, so there is no sign that the undercount is differential. Within the subsample the contrast is 6/9 against 5/15 for the first coder and 7/9 against 6/15 for the second. The headline can stand, but it should say that faith was coded conservatively from keyword extracts and is a lower bound.
3. **Attitude to white preachers (neutral 64.9%, positive 22.4%, negative 12.6% of 174).** This split should be reworded. The boundary between neutral and positive depends on the coder's threshold for mild affect: among the 21 subsample narratives where both coders state an attitude, agreement is 76% (κ = 0.63), and the second coder classed 4 of the first coder's 13 neutral cases as positive and 1 as negative. The neutral share is better reported as an upper bound and the positive share as a lower bound. The negative count is stable (4 of 4 confirmed, plus one added).
4. **Postwar church, any (106 of 400, 26.5%).** This should be reworded as "at least 106". It excludes undated joining statements and incidental attendance, which an independent coder counted in 7 further narratives of the 40 (19 against 12). The share of identifiable postwar churches that are Black-run (41 of 46) is not affected; the one disagreement there comes from truncated text.
5. **Conversion timing (25 of 28 after 1865).** Not affected. The only disagreement is the Uncle Jake sketch.
6. **Prayer for freedom (13 of 400).** Reliability is still unknown, because no subsample narrative was coded y or n by either coder. This should be stated wherever the figure is used.
7. **Interviewer race (§3.5).** See the side finding below; the Black-interviewer count is understated.

## Side findings outside the reliability comparison

- **Interviewer credit lines cut off by segmentation.** J.M. Parker's interviewer line sits just above his segment start, so the first coder recorded "not recorded". A check of all 179 "not recorded" rows in `data.csv` found four more with a documented Black interviewer in the eight lines above the segment start and `interviewer_race` = unknown: Mary Watson, William Brown and Cora Armstrong (all AR, Samuel S. Taylor) and Claude Augusta Wilson (FL, "Negro Writers' Unit", James Johnson). With Parker that is five rows, which would raise the Black-interviewer group from 47 to 52. Re-running the two attitude comparisons of §3.5 with those five moved gives 6/52 against 16/348 (Fisher p = 0.05, was 0.03) and, among those stating an attitude, 6/20 against 16/154 (p = 0.02, unchanged). `data.csv` was not changed here.
- **The same check shows many "not recorded" rows do have a named worker** above the segment start (North Carolina "Worker:" lines, Ohio "Reporter:" lines, South Carolina "Prepared by" lines). Their race is undocumented, so `interviewer_race` is unaffected, but the `interviewer` column is incomplete.

- **Follow-up, 2026-11-11: the interviewer columns of `data.csv` have since been corrected** (`results.md` §2, `pipeline/fix_interviewers.py`). The tables above are left as they stood at the comparison. On the corrected data the `interviewer_race` row reads 39/40, κ = 0.93: J.M. Parker now agrees, and Alice Green remains the one disagreement, because the two-interviewer rule added to `codebook.md` §8 codes her `unknown` where the second coder coded white. The full check moved more rows than the five listed here, so §3.5 of `results.md` now gives 7/54 against 15/346 for negative attitude (p = 0.02) and 7/20 against 15/154 among those stating an attitude (p = 0.005), not the 6/52 and 6/20 of the quick check.

## Files

- `second_coder.csv`: 40 rows. Identifier and locator, all codes, a verbatim snippet and Gutenberg line locator for each non-`ns` code, and notes on ambiguities.
- `analysis.py`, section 10: prints the agreement table and the disagreement list from `data.csv` and `second_coder.csv`.
- This file.
