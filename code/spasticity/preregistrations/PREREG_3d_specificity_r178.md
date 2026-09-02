# PREREG_3d_specificity_r178.md — is the hip signal specific, or one projection of a globally different gait?

**Round 179, 2026-08-11.** *Where this document and any script disagree, **THIS DOCUMENT DECIDES**.*

**Two hashes, per `WATCHDOG.md`'s round-176 rule — the first registration in this project to be cold
read before freezing.** *Pre-read draft: 10,877 B, sha256 `eb73059217330e1c3eba4a506e714218719a6dd23a0405abad08b51103e4fbf5`,
recorded in `PREREG_3d_specificity_r178.PREREAD.sha256`. **This document is the post-read version and
differs substantially.*** *What the read changed is listed in §7.*

**Parents:** `PREREG_3d_reopt_r151.md` `f6a65408…` (channel set), `PREREG_3d_matched_r174.md`
`3d62010f…` (cells). ⛔ **Evaluation of existing cells. No new simulation.**

---

## 0. ⛔ The draft's central claim was measured with the wrong instrument, and it is withdrawn here

**The draft said: "The 'everything separates' scenario is ALREADY FALSIFIED on r151 data. Eight of
twelve do not." That was measured by AUC, which compares SPASTIC to WEAK. The threat is about
spasticity versus NORMAL.** ⛔ **Different instrument, different question. The claim is withdrawn.**

⭐ **Applying the criterion this document actually registers — spastic arm mean outside the control
band — to the same r151 data gives 10 OF 16, WHICH IS THIS DOCUMENT'S OWN "GLOBAL" ROW.**

| | count | reading |
|---|---|---|
| by AUC (spastic vs weak) — the draft's instrument | 4 of 12 separate | *"not everything separates"* |
| ⛔ **by DISPLACEMENT (spastic vs control) — the registered instrument** | ⛔ **10 of 16** | ⛔ **GLOBAL** |

**Displaced on r151:** `knee_angle_l`, `knee_angle_r`, `hip_flexion_l`, `hip_flexion_r`,
`hip_adduction_l`, `pelvis_list`, `cycle_time`, `knee_angle_LmR`, `hip_flexion_LmR`,
`hip_adduction_LmR`.
**OPPOSED on r151: 1 of 16 — `hip_flexion_LmR`, and only it.**

⛔ **So the prior already answers the global question, and the answer is: THE SPASTIC GAIT IS GLOBALLY
DIFFERENT.** ⭐ **And the narrow claim survives it intact: the hip is still the only channel on which
the two arms move in opposite directions from control.** ⚠ **Both are true at once. That joint outcome
was unregistered in the draft, and §3 registers it.**

### 0a. ⛔⛔ AND THEREFORE PRIMARY A IS NOT A TEST — it is already determined by data on disk

**PRIMARY A compares the SPASTIC arm to the CONTROL arm. Both are r151 cells: `R151S` and `R151C`.
The r174 study added only WEAK cells.** ⛔ **So PRIMARY A's answer cannot change when the r174 data is
analysed. It is 10 of 16 now and it will be 10 of 16 then.**

⛔ **A registration that presented it as a test would have registered a branch that could not fire —
the exact class this document was read to catch, sitting in the document doing the catching.**

⭐ **Re-scoped: PRIMARY A is reported as a DESCRIPTION of existing data, not as a test, and its number
is stated here, before freezing, rather than presented later as a finding.** ⛔ **The only genuinely new
comparison the r174 cells support is PRIMARY B, and PRIMARY B is the test.**

### 0b. What I expect, before the data

⛔ **I expect PRIMARY B to return 1 and for it to be `hip_flexion_LmR`** — that is what the prior gives
at one weakness magnitude, and the test extends it to three. ⚠ **This is a weaker prediction than the
draft's and I am stating it as the weaker one: the outcome I expect is the one that preserves the
existing claim.**

⛔ **What would falsify it and what I will do:** *if PRIMARY B returns 0, the hip claim is RETIRED and
`MATCHED_RESULT_r174.md` §1 says so in its first paragraph. If it returns > 1, the hip is one of
several and the claim is reported in that weaker form.* ⚠ **A9 was the first correction this project
made toward a stronger result. The risk is a registration that protects it. §0a is the evidence that
this one does not — it demotes the author's own headline test to description.**

---

## 1. The channel set — complete, fixed, reported whatever it shows

**Per-side ROM (8):** `ankle_angle_l/r`, `knee_angle_l/r`, `hip_flexion_l/r`, `hip_adduction_l/r`.
**Unpaired ROM (3):** `pelvis_list`, `pelvis_rotation`, `lumbar_bending`. **Cadence (1):** `cycle_time`.
**Asymmetry (4):** `(L−R)` of each paired channel. **TOTAL 16.**

⛔ **All sixteen computed, all sixteen reported.** *Selecting after seeing which separated is the
post-hoc promotion R45-S forbids.* ⛔ **`ank_hs_LmR` stays barred.**

⛔ **THE SIXTEEN ARE NOT SIXTEEN FREE VALUES.** *The four `(L−R)` channels are algebraic functions of
eight per-side channels, so there are **12 free quantities**. A single-joint displacement registers
twice.* ⚠ **Counts are reported over 16 AND over the 12 free quantities, and any threshold phrased as
"half" refers to the 16-set with this inflation stated.**

**Definitions, because two competent analysts would otherwise differ:**
**ROM** = per-cycle peak-to-peak, over cycles wholly inside the window, averaged across cycles —
`analyse_reopt_r151.py`'s definition, unchanged. **Arm mean** = mean of the six per-seed channel
values. **`L−R`** = left minus right; **the LEFT limb carries both lesions** (`soleus`/`gastroc`
reflex; `tib_ant_l` scaling). **Window** `[1.00, 13.58]`, GRF-delimited, settle 1.0 s.

⚠ **The window spans ≈ 10.6 cycles at `cycle_time` ≈ 1.19 s. Cycles are whole-cycle delimited so a
partial cycle is dropped, not truncated** — *but the window remains the untested defect recorded in
`MATCHED_RESULT_r174.md` §8 and nothing here settles it.*

⛔ **The design is BLIND TO TIMING.** *All 16 channels are amplitude or cadence. A gait with identical
ROMs and completely restructured phase scores as unchanged. **"Globally different" is therefore tested
only in amplitude**, and a null on these channels is not evidence of no reorganisation.*

---

## 2. The criteria, and the null rate that is NOT known

**DISPLACED:** the arm mean lies outside the control band (min, max over six control seeds).
**OPPOSED:** spastic and weak means are both outside the band AND on opposite sides of the control
mean.

⛔ **THE DRAFT JUSTIFIED ITS THRESHOLDS WITH "at 6 v 6 a chance complete separation has p = 2/924, so
with 16 channels the expected number by chance is 0.035". THAT NUMBER BELONGS TO A DIFFERENT
CRITERION** — *complete separation between arms, which neither DISPLACED nor OPPOSED uses.* ⛔ **It is
withdrawn.**

⛔ **The null rate of DISPLACED — a mean of six against the min–max of six — IS NOT KNOWN AND IS NOT
COMPUTED HERE. No chance-level reassurance is offered for either criterion.** ⚠ *It is plainly not
1-in-462; a mean of six falling outside the range of six other draws from a noisy process is an
ordinary event. **Thresholds below are conventions, not null-referenced.***

⛔ **AND THE BAND'S WEAKNESS IS RESTATED WHERE IT DECIDES, NOT ONLY WHERE IT IS HARMLESS.** *The draft
listed "max−min of SIX values, badly estimated" as a defect of the ranking statistic `d`, which decides
nothing, and omitted it for the band, which decides everything.* ⛔ **The band is a max−min of six
optimiser restarts. It is not a confidence interval, it has no coverage claim, and every count in this
document turns on it.**

⭐ **BAND SENSITIVITY IS MANDATORY, NOT OPTIONAL: every count is reported at band ×1.0, ×1.5 and ×2.0
about the control mean.** ⛔ **If a count changes row between ×1.0 and ×1.5, the result reports the
count as UNSTABLE and no branch is claimed.**

**Ranking statistic `d` = (arm mean − control mean) / control spread.** ⛔ *Ranks within a count; never
changes one. No p attaches to it. Its denominator is the same badly-estimated six-restart range.*

---

## 3. PRIMARY B — the test — and the joint table

**Comparison: `S050` vs `W892`, the registered match, 6 v 6. `W870` and `W915` computed identically as
brackets.**

⛔ **Complete partition over (count, whether the hip is in it) — the draft left "exactly 1, not the
hip" with no branch at all:**

| OPPOSED count | hip included? | registered reading |
|---|---|---|
| **0** | — | ⛔ **the hip claim is RETIRED**; `MATCHED_RESULT_r174.md` §1 says so in its first paragraph |
| **exactly 1** | yes | ⭐ **the hip claim survives in its narrow form** |
| **exactly 1** | ⛔ **no** | ⛔ **the hip claim is RETIRED and ANOTHER channel carries the opposition** — *a different result, reported as one* |
| **> 1** | yes | ⚠ **the hip is one of several opposed channels** — weaker, reported as such |
| **> 1** | no | ⛔ **the hip claim is RETIRED**; the opposition lives elsewhere |

**PRIMARY A (description, not test): count DISPLACED for the spastic arm. Reported at all three band
multipliers, over 16 and over 12 free quantities.**

⛔ **THE JOINT TABLE, registered because the prior already lands in a cell the draft did not cover:**

| A | B = 0 | B = 1 = hip | B > 1 |
|---|---|---|---|
| **≤ 3** | ⛔ narrow gait change, **no opposed channel — hip retired** | ⭐ strongest available | ⚠ several opposed |
| **4–7** | ⛔ hip retired | ⭐ narrow claim survives a broad displacement | ⚠ several opposed |
| ⛔ **≥ 8** | ⛔ **globally different gait AND nothing opposed — the whole discrimination claim reduces to "this gait is different"** | ⛔⭐ **globally different gait, and the hip is still the ONLY opposed channel — THIS IS WHAT THE PRIOR GIVES.** *Reported as: the spastic gait differs broadly, and one channel distinguishes the mechanisms by direction. **Neither half may be reported without the other.*** | ⚠ globally different, several opposed |

⛔ **"Neither primary rescues the other" was the draft's whole rule for disagreement and it forbade one
resolution without registering any. The table above replaces it.**

---

## 4. The control table — required output

⛔ **The result must print, for all 16 channels: the six control-seed values, the control mean, and the
band.** *`MATCHED_RESULT_r174.md`'s control mean of +0.003° appeared with no source while carrying the
entire opposite-sides argument; a cold reader found it. **The six `hip_flexion_LmR` control seeds are
backfilled into that document this round.***

---

## 5. What this design cannot do

- ⛔ **Nothing is tested against control.** *Every count is six restarts against six restarts. **No test
  against control exists in this project and this design does not add one.***
- ⛔ **It cannot distinguish compensation from mechanism even if the counts are narrow.** *A narrow
  displacement is consistent with a narrow compensation.*
- ⛔ **It is blind to timing** — §1.
- ⛔ **It inherits every limit of the cells:** *restarts not subjects; 20.00 s censoring on every weak
  arm; the untested window; muscle-force dose, not ankle moment.*
- ⚠ **`cycle_time` is not a joint angle and its `d` is not comparable to a ROM channel's.** *It is kept
  because selection is forbidden.*

---

## 6. Operational

⛔ **Existing `.sto` only. No optimisation, no `--run`, no `--launch`.** ⛔ **Writes confined to
`Desktop\spasticity_paper\`; 112 protected directories untouched.**
⛔ **A cell is used iff its tag resolves to exactly ONE directory with `history.txt` ≥ 91 lines.**
⛔ **IF ANY ARM HAS FEWER THAN SIX USABLE SEEDS, the analysis STOPS and reports that** — *the bands,
the "6 v 6" and every count assume six, and no branch here is valid at n < 6.*
⛔ **If a bracket rung lands in a different PRIMARY B row than `W892`, both are reported and the result
states that the row is dose-dependent.**
⛔ **CALIBRATION GATE, extended: one channel of EACH TYPE — a per-side ROM, an `(L−R)`, an unpaired
ROM, and `cycle_time` — must reproduce r151/r174 to 1 × 10⁻⁹ before any new channel is reported.**
*The draft gated sixteen channels on three legacy ones and said nothing about the thirteen whose code
path is new.*
⛔ **Registered scripts imported UNMODIFIED; the analysis script is hashed at first verdict and any
later edit declared in `AMENDMENTS_r174.md`.**

---

## 7. What the cold read changed — the rule's first exercise

| # | draft | final |
|---|---|---|
| 1 | thresholds justified by a 0.035 chance rate | ⛔ **withdrawn — it belonged to a different criterion; DISPLACED's null rate stated as UNKNOWN** |
| 2 | "already falsified, 8 of 12" | ⛔ **withdrawn — measured by AUC, the wrong instrument; the registered criterion gives 10 of 16, GLOBAL** |
| 3 | PRIMARY A presented as the test | ⛔ **re-scoped to description — it uses only r151 cells and cannot change** |
| 4 | PRIMARY B branches incomplete | ⭐ **complete 5-cell partition** |
| 5 | disagreement forbidden, not resolved | ⭐ **3 × 3 joint table registered** |
| 6 | band weakness disclosed only for `d` | ⭐ **restated where it decides; band sensitivity ×1.0/×1.5/×2.0 mandatory** |
| 7 | 16 channels treated as 16 | ⭐ **12 free quantities stated; counts reported both ways** |
| 8 | ROM, limb, sign undefined | ⭐ **defined** |
| 9 | no rule for n < 6 or bracket disagreement | ⭐ **both registered** |
| 10 | calibration on 3 legacy channels | ⭐ **one of each type** |
| 11 | timing blindness unstated | ⭐ **stated** |

⭐ **Eleven changes, and two of them — items 2 and 3 — invalidated the draft's headline reasoning.
The rule was adopted because the absence of registration reads had a measured three-defect cost. Its
first use found two more, in the registration written by the seat that argued for the rule.**
