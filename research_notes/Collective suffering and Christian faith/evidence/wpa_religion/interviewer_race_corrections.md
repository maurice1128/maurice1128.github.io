# Interviewer-race corrections to `data.csv` (project `wpa_religion`)

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

- **Credit belongs to another informant merged into the segment.** The TOC-named informant's own interviewer is as coded.
  - AR-II-3-064, Bert Higgins (Bernice Bowden): the Samuel S. Taylor forms from l. 6906 are for Annie Hill.
  - AR-II-6-024, William Henry Rooks (Irene Robertson): the Samuel S. Taylor line at l. 2456 is for Amanda Rosa.
  - AR-II-2-042, Katie Dillon (Bernice Bowden): the Pernella Anderson line at l. 4595 is for Alice Dixon.
- **Two interviews by different interviewers under one entry.** The codebook has no rule for this, so the rows were left as coded and need a decision.
  - GA-IV-2-005, Alice Green: first interview "Written by: Corry Fowler" (race undocumented); second, from l. 1084, "Written by: Sadie B. Hornsby" (documented white). Coded unknown.
  - SC-XIV-1-028, Henry Brown: first interview credited to Jessie A. Butler at l. 3637 (race undocumented); second, from l. 3738, to Augustus Ladson (documented Black). Coded unknown, and the `interviewer` column says "W. W. Dixon", which matches neither.

## Other errors noticed in these rows, not changed

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
