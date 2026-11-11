# Interviewer-race corrections to `data.csv` (project `wpa_religion`)

**Status.** This file records two passes made on 2026-11-11. The first pass (six rows) is described first and is left as written. The second pass, at the end, decided the items the first pass left open and re-read the interviewer column for all 400 rows. Where the two differ, the second pass holds. Line ranges quoted for segments in the first-pass sections are those of the first segmentation; `data.csv` now carries the header-block ranges.

## First pass

Applied 2026-11-11. Six rows were changed from `interviewer_race` = unknown to Black. In each, a documented Black interviewer is credited for the narrative but the first coder's extract did not show the credit line. No code column other than `interviewer`, `interviewer_race` and `interviewer_race_source` was touched. Result: Black 47 → 53, unknown 342 → 336, white 11 unchanged.

## Two corrections to the earlier report

The independent second-coder report first described this as "five rows, four by Samuel S. Taylor and one Florida Negro Writers' Unit". Checking each credit line against the text before editing showed that was wrong in two ways:

- **Cora Armstrong is credited to Pernella Anderson, not Samuel S. Taylor.** The Taylor line above her segment start belongs to the preceding informant, Campbell Armstrong, whose narrative fills lines 2003–2226 of her segment. Her own piece (lines 2230–2272) is headed "Interviewer: Pernella Anderson, colored." The row is still Black, on different evidence.
- **A sixth row has the same defect.** Milton Hammond's narrative is headed "Minnie B. Ross." two lines above his segment start. The first check missed it because the credit is a bare name with no "Interviewer:" label.

## The six rows

Line numbers are in the Project Gutenberg plain-text file `pg<eBook>.txt`, as elsewhere in this project. The documentation rule for each interviewer is the one already in `codebook.md` §8.

| nid | informant | evidence line (verbatim) | where | interviewer set to | documentation of race |
|---|---|---|---|---|---|
| AR-II-5-076 | Parker, J.M. | `Interviewer: Samuel S. Taylor` | pg11544.txt l. 6904; segment starts at l. 6908 ("Person Interviewed: J.M. Parker") | Samuel S. Taylor | Encyclopedia of Arkansas, "WPA Slave Narratives" |
| AR-II-7-019 | Watson, Mary | `NAME OF WORKER--Samuel S. Taylor` | pg11422.txt l. 1930; segment starts at l. 1937 ("1. Name and address of informant--Mary Watson") | Samuel S. Taylor | Encyclopedia of Arkansas |
| AR-II-1-091 | Brown, William | `Interviewer: Samuel S. Taylor` | pg11255.txt l. 9060, followed at l. 9061 by "Person interviewed: William Brown"; segment starts at l. 9067 | Samuel S. Taylor | Encyclopedia of Arkansas |
| AR-II-1-024 | Armstrong, Cora | `Interviewer: Pernella Anderson, colored.` | pg11255.txt l. 2230, inside the segment (2003–2276); her piece ends "--Cora Armstrong, colored." at l. 2272 | Pernella Anderson | in-text "colored"; Encyclopedia of Arkansas |
| FL-III-050 | Wilson, Claude Augusta | `American Guide, (Negro Writers' Unit)` and `James Johnson, Field Worker` | pg12297.txt l. 8650 and 8652; segment starts at l. 8656 ("CLAUDE AUGUSTA WILSON") | James Johnson | in-text "Negro Writers' Unit" |
| GA-IV-2-012 | Hammond, Milton | `Minnie B. Ross.` | pg22166.txt l. 2462; segment starts at l. 2464 ("EX SLAVE / MILTON HAMMOND.") | Minnie B. Ross | Notable Folklorists of Color, Negro Units (GA) |

Each row's `interviewer_race_source` now carries the same source string used for that interviewer elsewhere in `data.csv`, followed by `[corrected 2026-11-11: credit line …; see interviewer_race_corrections.md]`.

## How the rows were found

Every one of the 400 segments, plus the ten lines above its start, was searched for the documented names and markers in `codebook.md` §8 (Samuel S. Taylor, Pernella Anderson, "Negro Writers' Unit", "colored" after an interviewer's name, the Georgia, South Carolina and Virginia Negro-unit names, "[HW: (White)]", Sadie B. Hornsby, Grace McCune). Each hit that disagreed with the coded race was then read in context. No row coded Black or white lacks a marker.

## Rows examined and deliberately left unchanged

*After the second pass: the three merged rows keep their interviewer and race, but their codes turned out to rest on the appended interviews (open item below). Alice Green and Henry Brown are decided.*

- **Credit belongs to another informant merged into the segment.** The TOC-named informant's own interviewer is as coded.
  - AR-II-3-064, Bert Higgins (Bernice Bowden): the Samuel S. Taylor forms from l. 6906 are for Annie Hill.
  - AR-II-6-024, William Henry Rooks (Irene Robertson): the Samuel S. Taylor line at l. 2456 is for Amanda Rosa.
  - AR-II-2-042, Katie Dillon (Bernice Bowden): the Pernella Anderson line at l. 4595 is for Alice Dixon.
- **Two interviews by different interviewers under one entry.** The codebook has no rule for this, so the rows were left as coded and need a decision.
  - GA-IV-2-005, Alice Green: first interview "Written by: Corry Fowler" (race undocumented); second, from l. 1084, "Written by: Sadie B. Hornsby" (documented white). Coded unknown.
  - SC-XIV-1-028, Henry Brown: first interview credited to Jessie A. Butler at l. 3637 (race undocumented); second, from l. 3738, to Augustus Ladson (documented Black). Coded unknown, and the `interviewer` column says "W. W. Dixon", which matches neither.

## Other errors noticed in these rows, not changed

*After the second pass: both are corrected.*

- **AR-II-1-024, Cora Armstrong: `age_1937` is 86,** which is Campbell Armstrong's age from the header above her segment. Her own text says "I was ten years old at surrender", about 82 in 1937. Both values fall in the 80+ group used in `analysis.py`.
- **The `interviewer` name column is still incomplete.** Of the 173 rows still marked "not recorded", about 30 have a named worker in the eight lines above the segment start (North Carolina "Worker:", Ohio "Reporter:", South Carolina "Prepared by", the Florida field workers). Their race is either undocumented or already coded from the unit marker, so no analysis is affected.

## Effect on the analysis

`python3 analysis.py` was re-run after the edit. Only sections 3G and 5 changed, plus the `interviewer_race` line of section 10. Values as the script prints them:

| output | before | after |
|---|---|---|
| interviewer_race counts | Black 47, unknown 342, white 11 | Black 53, unknown 336, white 11 |
| 3G, white/unknown interviewers only | n = 185; 38/83 = 45.8% (35.5–56.4) vs 18/102 = 17.6% (11.5–26.2); Fisher p = 4.825e-05 | n = 182; 37/81 = 45.7% (35.3–56.5) vs 18/101 = 17.8% (11.6–26.4); Fisher p = 7.966e-05 |
| obedience-only preaching | 6/47 = 12.8% (6.0–25.2) vs 19/353 = 5.4% (3.5–8.3); p = 0.0986 | 7/53 = 13.2% (6.5–24.8) vs 18/347 = 5.2% (3.3–8.0); p = 0.0343 |
| negative attitude, all narratives | 6/47 = 12.8% (6.0–25.2) vs 16/353 = 4.5% (2.8–7.2); p = 0.0328 | 7/53 = 13.2% (6.5–24.8) vs 15/347 = 4.3% (2.6–7.0); p = 0.0168 |
| positive attitude, all narratives | 3/47 = 6.4% (2.2–17.2) vs 36/353 = 10.2% (7.5–13.8); p = 0.6 | 3/53 = 5.7% (1.9–15.4) vs 36/347 = 10.4% (7.6–14.0); p = 0.453 |
| secret worship | 3/47 = 6.4% (2.2–17.2) vs 25/353 = 7.1% (4.8–10.2); p = 1 | 3/53 = 5.7% (1.9–15.4) vs 25/347 = 7.2% (4.9–10.4); p = 1 |
| Black control of worship | 9/47 = 19.1% (10.4–32.5) vs 83/353 = 23.5% (19.4–28.2); p = 0.583 | 11/53 = 20.8% (12.0–33.5) vs 81/347 = 23.3% (19.2–28.1); p = 0.861 |
| faith before freedom | 11/47 = 23.4% (13.6–37.2) vs 61/353 = 17.3% (13.7–21.6); p = 0.314 | 12/53 = 22.6% (13.5–35.5) vs 60/347 = 17.3% (13.7–21.6); p = 0.341 |
| prayer for freedom | 3/47 = 6.4% (2.2–17.2) vs 10/353 = 2.8% (1.5–5.1); p = 0.187 | 4/53 = 7.5% (3.0–17.9) vs 9/347 = 2.6% (1.4–4.9); p = 0.0789 |
| postwar Black-run church | 8/47 = 17.0% (8.9–30.1) vs 33/353 = 9.3% (6.7–12.8); p = 0.122 | 10/53 = 18.9% (10.6–31.4) vs 31/347 = 8.9% (6.4–12.4); p = 0.0471 |
| negative, among those stating an attitude | 6/19 = 31.6% (15.4–54.0) vs 16/155 = 10.3% (6.5–16.1); p = 0.0185 | 7/21 = 33.3% (17.2–54.6) vs 15/153 = 9.8% (6.0–15.5); p = 0.00721 |
| positive, among those stating an attitude | 3/19 = 15.8% (5.5–37.6) vs 36/155 = 23.2% (17.3–30.5); p = 0.572 | 3/21 = 14.3% (5.0–34.6) vs 36/153 = 23.5% (17.5–30.8); p = 0.416 |
| section 10, interviewer_race, first vs second coder | 38/40 = 95.0%, κ 0.85 | 39/40 = 97.5%, κ 0.93 |

Most of the movement comes from one narrative. Milton Hammond reports obedience-only preaching, a negative attitude, Black control of worship and a postwar Black-run church, so moving him into the Black-interviewer group shifts four comparisons at once. Two p-values cross 0.05 as a result (obedience-only preaching and postwar Black-run church). They are unadjusted for the ten comparisons the script prints and should be read as fragile.

The pre-correction file is recoverable from git (`data.csv` at commit `0819d5f`).

## Second pass: rule for two interviewers, age of Cora Armstrong, full re-reading of the interviewer column

Applied 2026-11-11, later the same day. All 34 eBooks were downloaded again. For every sampled narrative the header block, the footer and every header block inside the segment were read against the text. Result: Black 53 → 56, white 11 → 12, unknown 336 → 332. `interviewer_name_corrections.csv` lists all 116 rows whose interviewer columns changed, with the line number and verbatim text of each credit.

### 1. Entries with two interviews by different interviewers

Rule added to `codebook.md` §8: `interviewer` lists every credited interviewer in text order; `interviewer_race` is Black if any of them is documented Black, otherwise white if any is documented white, otherwise unknown.

| nid | informant | credits (verbatim) | interviewer now | race |
|---|---|---|---|---|
| SC-XIV-1-028 | Brown, Henry | `Jessie A. Butler` pg18912.txt l. 3637; `Augustus Ladson` l. 3739 | Jessie A. Butler; Augustus Ladson | unknown → Black (Ladson: Notable Folklorists of Color, SC) |
| GA-IV-2-005 | Green, Alice | `Written by: Corry Fowler,` pg22166.txt l. 935; `Written by: Sadie B. Hornsby` l. 1092 | Corry Fowler; Sadie B. Hornsby | unknown → white (Hornsby: in-text "[HW: (White)]") |
| AR-II-2-051 | Douglas, Sarah | `Interviewer: Pernella M. Anderson` pg13700.txt l. 5697; `Interviewer: Carol Graham` l. 5767 | Pernella M. Anderson; Carol Graham | Black, unchanged |
| GA-IV-2-006 | Green, Isaiah (Isaac) | `Submitted by Minnie B. Ross` pg22166.txt l. 1332; `Edwin Driskell` l. 1563 | Minnie B. Ross; Edwin Driskell | Black, unchanged |
| AR-II-7-065 | Windham, Tom | `Interviewer: Mrs. Bernice Bowden` pg11422.txt l. 6044; `Name of interviewer: Martin - Barker` l. 6153 | Bernice Bowden; Martin - Barker | unknown, unchanged |
| AR-II-3-048 | Harris, Rachel | `Interviewer: Mrs. Bernice Bowden` pg19446.txt l. 4986; `Name of Interviewer: Irene Robertson` l. 5057 | Bernice Bowden; Irene Robertson | unknown, unchanged |

- Henry Brown's `interviewer` had read "W. W. Dixon". That line (l. 3894) heads the next narrative, John C. Brown and Adeline Brown.
- Henry Brown's coded snippets come from both interviews (attitude l. 3704 from Butler's; worship control and faith l. 3869 from Ladson's). Alice Green's come from both as well (faith l. 1015 and conversion l. 1076 from Fowler's; worship control l. 1202 and attitude l. 1204 from Hornsby's). An evidence-based rule would therefore not have separated them either.
- The two interviews under Rachel Harris give different ages and addresses (90, Pine Bluff; 80, Hazen) and may be two women of the same name. No code rests on either.
- The independent second coder had coded Alice Green white at the blind comparison.

### 2. Cora Armstrong, AR-II-1-024

`age_1937` 86 → 82: "I was ten years old at surrender" (pg11255.txt l. 2240), so born about 1855; the interview is undated and 1937 is assumed. 86 is the age in Campbell Armstrong's header (l. 2000). No other code was taken from his narrative. The row has two non-`ns` codes, `wc_white` y and attitude neutral, and both rest on l. 2247 ("Old Miss would carry me to church sometimes when it was hot so we could fan for her"), inside her own text (l. 2230–2272). His narrative (l. 2003–2226) contains no church, prayer, preaching, Bible or baptism term. `hearsay_only` n is consistent with her age. `notes` now records the merge and the age calculation. The analysis output for age is unchanged (median 83, IQR 78–88; she stays in the 80+ group).

### 3. The `interviewer` name column

- **115 names changed.** 69 rows read "not recorded" although the text names the worker. The other 46 break down as follows.
  - 28 carried a different worker's name, in nearly every case the credit of the next narrative, which stood in the tail of the old segment.
  - 10 carried an editor ("Elmer Turnage (editor)", "Editor G. L. Andrews").
  - 5 gained a second interviewer.
  - 2 carried a descriptive label in place of the name (Hannah Austin, Benny Dillard).
  - 1 became "not recorded": Alec Bostwick, GA. His own header page is a placeholder, and "Barragan-Harris" heads the next narrative.
- **By state:** South Carolina 31, North Carolina 23, Georgia 19, Florida 11, Indiana 10, Ohio 6, Arkansas 6, Mississippi 4, Maryland 2, Missouri 2, Alabama 1.
- **107 rows remain "not recorded"** because the text names no worker: Texas 61, Oklahoma 18, Missouri 10, Tennessee 6, Georgia 6, Kentucky 3, Mississippi 2, Arkansas 1. The Texas and Oklahoma headers carry only a file number or the project name.
- **Credits of other informants were not used.** Bert Higgins (Annie Hill's forms, Samuel S. Taylor, from pg19446.txt l. 6906), William Henry Rooks (Amanda Rosa, Taylor, pg11709.txt l. 2456) and Katie Dillon (Alice Dixon, Pernella Anderson, pg13700.txt l. 4595) keep Bernice Bowden, Irene Robertson and Bernice Bowden. The same holds for the appended interviews in the segments of Mal Boyd, Henry Turner, Janie Gallman, Anne Rice, Jesse Williams, Louisa Davis, John C. Brown, George Morrison and Zenia Culp.
- **Four race codes changed with the names.**

| nid | informant | evidence line (verbatim) | where | change |
|---|---|---|---|---|
| GA-IV-1-035 | Davis, Mose | `E. Driskell` | pg13602.txt l. 7280, below "Whitley / [HW: Unedited / Atlanta]", two lines above the title "EX-SLAVE MOSE DAVIS" | unknown → Black |
| GA-IV-1-038 | Eason, George | `Driskell]` | pg13602.txt l. 8144, in "[HW: Atlanta / Dist. 5 / Driskell]", two lines above the title "THE EXPERIENCE OF GEORGE EASON IN SLAVERY TIME" | unknown → Black |
| GA-IV-3-001 | Kendricks, Jennie | `Driskell` | pg18484.txt l. 174, below "[HW: Dist 5 / Ex-Slave #63] / Whitley, / 1-22-36", two lines above "EX SLAVE / JENNIE KENDRICKS" | unknown → Black |
| AR-II-5-044 | Morgan, Tom | `Name of Interviewer: Pernella Anderson` | pg11544.txt l. 4346, followed at l. 4350 by "This Information given by: Charity Morris"; his own header is "Interviewer: Miss Irene Robertson", l. 4311 | Black → unknown |

- **Why "Driskell" is a credit and not a reviewer's note.** The first version treated the handwritten "Driskell" lines as notes at the foot of the preceding narrative, because the one at pg13602.txt l. 8142–8144 follows Benny Dillard's narrative, which is headed "Written by: Grace McCune [HW: (white)]". All 13 Driskell lines in the four Georgia eBooks were checked (pg13602.txt l. 2228, 7280, 8144, 8647; pg22166.txt l. 1563; pg18484.txt l. 174, 1266, 1910, 4691, 5959; pg18485.txt l. 3556, 4954, 5412). Each follows a run of four blank lines and stands directly above the title of the next narrative. One reads "By E. Driskell / Typed by A.M. Whitley" (pg13602.txt l. 8647) and one "Edwin Driskell" (pg22166.txt l. 1563). Benny Dillard and Minnie Davis keep Grace McCune and Sadie B. Hornsby, white.
- **The statement in the first pass that "no row coded Black or white lacks a marker" was wrong for Tom Morgan.** After this pass it was checked again for all 400 rows against the names in `pipeline/merge.py` and the markers in each row's own header: no row coded Black or white lacks one, and no row coded unknown has one.
- **Hannah Austin (GA-IV-1-005)** stays Black on better evidence: her own header reads "Whitley / 1-25-37 / [HW: Dis #5 / Unedited] / Minnie B. Ross" (pg13602.txt l. 607–611). The handwritten "Ross]" at l. 718 heads the next narrative.
- **Two Missouri rows** (Hannah Allen, Rhody Holsell) hold a second interview headed "Interviewed by J. Tom Miles." (pg35379.txt l. 490 and 5122). The first interview in each names no one, so the entry is recorded as "J. Tom Miles (second interview; first uncredited)".

### 4. Segmentation script

`pipeline/segment.py` now starts each segment at its header block (`results.md` §2). The 2,143 segments, every keyword count, the frame of 1,418, the sample of 400, its coding order and the 40 double-coding ids are identical on re-run. Of the 85 credit lines that stood above the old segment start, 82 now fall inside the segment. The other three are Moses Mitchell (AR), Wadley Clemons (AL) and Willis Williams (SC), where the name search itself found a later line.

### 5. Effect on the analysis

`python3 analysis.py` was re-run. Sections 3G and 5 and the `interviewer_race` line of section 10 changed; nothing else did. Values as the script prints them:

| output | after the first pass | now |
|---|---|---|
| interviewer_race counts | Black 53, unknown 336, white 11 | Black 56, unknown 332, white 12 |
| 3G, white/unknown interviewers only | n = 182; 37/81 = 45.7% (35.3–56.5) vs 18/101 = 17.8% (11.6–26.4); Fisher p = 7.966e-05 | n = 179; 36/78 = 46.2% (35.5–57.1) vs 19/101 = 18.8% (12.4–27.5); Fisher p = 0.0001447 |
| obedience-only preaching | 7/53 = 13.2% (6.5–24.8) vs 18/347 = 5.2% (3.3–8.0); p = 0.0343 | 7/56 = 12.5% (6.2–23.6) vs 18/344 = 5.2% (3.3–8.1); p = 0.0655 |
| negative attitude, all narratives | 7/53 = 13.2% (6.5–24.8) vs 15/347 = 4.3% (2.6–7.0); p = 0.0168 | 7/56 = 12.5% (6.2–23.6) vs 15/344 = 4.4% (2.7–7.1); p = 0.0227 |
| positive attitude, all narratives | 3/53 = 5.7% (1.9–15.4) vs 36/347 = 10.4% (7.6–14.0); p = 0.453 | 3/56 = 5.4% (1.8–14.6) vs 36/344 = 10.5% (7.7–14.1); p = 0.331 |
| secret worship | 3/53 = 5.7% (1.9–15.4) vs 25/347 = 7.2% (4.9–10.4); p = 1 | 3/56 = 5.4% (1.8–14.6) vs 25/344 = 7.3% (5.0–10.5); p = 0.781 |
| Black control of worship | 11/53 = 20.8% (12.0–33.5) vs 81/347 = 23.3% (19.2–28.1); p = 0.861 | 14/56 = 25.0% (15.5–37.7) vs 78/344 = 22.7% (18.6–27.4); p = 0.733 |
| faith before freedom | 12/53 = 22.6% (13.5–35.5) vs 60/347 = 17.3% (13.7–21.6); p = 0.341 | 12/56 = 21.4% (12.7–33.8) vs 60/344 = 17.4% (13.8–21.8); p = 0.457 |
| prayer for freedom | 4/53 = 7.5% (3.0–17.9) vs 9/347 = 2.6% (1.4–4.9); p = 0.0789 | 4/56 = 7.1% (2.8–17.0) vs 9/344 = 2.6% (1.4–4.9); p = 0.0933 |
| postwar Black-run church | 10/53 = 18.9% (10.6–31.4) vs 31/347 = 8.9% (6.4–12.4); p = 0.0471 | 10/56 = 17.9% (10.0–29.8) vs 31/344 = 9.0% (6.4–12.5); p = 0.0556 |
| negative, among those stating an attitude | 7/21 = 33.3% (17.2–54.6) vs 15/153 = 9.8% (6.0–15.5); p = 0.00721 | 7/22 = 31.8% (16.4–52.7) vs 15/152 = 9.9% (6.1–15.6); p = 0.0097 |
| positive, among those stating an attitude | 3/21 = 14.3% (5.0–34.6) vs 36/153 = 23.5% (17.5–30.8); p = 0.416 | 3/22 = 13.6% (4.7–33.3) vs 36/152 = 23.7% (17.6–31.0); p = 0.414 |
| documented-white interviewers only | n = 11: negative 1, positive 2, obedience y 2 | n = 12: negative 1, positive 2, obedience y 2 |
| section 10, interviewer_race, first vs second coder | 39/40 = 97.5%, κ 0.93 | 40/40 = 100.0%, κ 1.00 |

The two p-values that crossed 0.05 in the first pass (obedience-only preaching, postwar Black-run church) are above it again. The two negative-attitude comparisons are below 0.05 in all three versions of the data.

### 6. Open item: four Arkansas rows are coded from an appended interview

The codebook says that in a merged segment only the TOC-named informant is coded. In four rows the coded snippets come, wholly or partly, from another informant's interview appended to the segment. Each of those interviews was taken down by a documented Black interviewer.

| nid | TOC informant, own interviewer, own text | appended interview | codes that rest on the appended interview |
|---|---|---|---|
| AR-II-3-064 | Bert Higgins, Bernice Bowden, pg19446.txt l. 6817–6896 | Annie Hill, Samuel S. Taylor, l. 6901–7069 | `wc_white`, attitude neutral, faith y (kin): all three snippets at l. 7063 |
| AR-II-6-024 | William Henry Rooks, Irene Robertson, pg11709.txt l. 2348–2451 | Amanda Rosa, Samuel S. Taylor, l. 2456–2634 | `wc_blackled` and attitude positive (l. 2562–2563); the postwar-church snippet (l. 2422) is his own |
| AR-II-2-042 | Katie Dillon, Bernice Bowden, pg13700.txt l. 4529–4588 | Alice Dixon, Pernella Anderson, l. 4593–4724 | `wc_blackled` (l. 4616) |
| AR-II-5-044 | Tom Morgan, Irene Robertson, pg11544.txt l. 4311–4339 | Charity Morris, Pernella Anderson, l. 4344–4428 | `wc_white`, attitude neutral, faith y (self): snippets at l. 4367–4371 |

- **What was done.** Nothing was recoded. All four rows are coded unknown, by the TOC-named informant's own interviewer, as the rule in `codebook.md` §8 requires. Each row's `notes` now states where its snippets come from.
- **What it needs.** A decision between two repairs. Either the codes that rest on the appended interview are set to `ns` (the codebook's rule), which changes the worship-control and faith counts in `results.md` §3.1 to §3.4 by up to four rows. Or the four rows are kept as coded "as found", as the first coder did for three segments whose whole text is another informant's interview (Jennie Washington, Frank Williams, Annie Taylor), and their interviewer becomes the one who took down the coded text, which is Black in all four.
- **How much the second choice would move.** With the four rows counted as Black, `analysis.py` prints: Black 60, unknown 328, white 12; 3G n = 175, 36/76 = 47.4% (36.5–58.4) vs 17/99 = 17.2% (11.0–25.8), Fisher p = 2.593e-05; obedience-only preaching 7/60 vs 18/340, p = 0.0782; negative attitude, all narratives, 7/60 vs 15/340, p = 0.0326; negative among those stating an attitude 7/25 = 28.0% (14.3–47.6) vs 15/149 = 10.1% (6.2–15.9), p = 0.0211; positive among those stating an attitude 4/25 vs 35/149, p = 0.604; Black control of worship 16/60 vs 76/340, p = 0.506; faith before freedom 14/60 vs 58/340, p = 0.274; prayer for freedom 4/60 vs 9/340, p = 0.115; postwar Black-run church 11/60 vs 30/340, p = 0.0358. This run is a sensitivity check only; `data.csv` and `results.md` do not use it.

