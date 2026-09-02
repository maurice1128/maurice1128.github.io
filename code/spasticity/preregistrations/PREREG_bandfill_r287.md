# PREREG_bandfill_r287.md — continuation of r285: seed sampling for band coverage

**Round 287. Written and hashed BEFORE any cell of this continuation exists.** *Body: 3D,
`H1922v7b3` (Hyfydy).*

⛔ **`PREREG_bandfill_r285.md` (`c27a72650f7d2bb13eb6ae3d7f8b876124036270ef105a604bea92dcd73512ab`) IS
NOT AMENDED. It returned rung 1, UNINFORMATIVE, and is reported as rung 1 permanently.** *This is a
separate registration that continues its sampling. If a result suggests a change to either document,
the change is a third registration.*

---

## 1. Why a continuation, and why sampling rather than dose

**r285 ran 12 cells at f = 0.07 and f = 0.08 and put exactly ONE inside the band.** *Its §4 fired, the
endpoint was not evaluated, and no band was widened, no endpoint substituted and no out-of-band cell
pooled.* ⚠ **The temptation to pool was real and is on the record: every measured weakness cell read
knee-positive against six spastic all-negative, so pooling would have produced a wide disjoint gap.
§4 forbade it and it stayed forbidden.**

⛔ **THE STRUCTURAL REASON, AND IT IS A RESULT ABOUT THE MODEL RATHER THAN A NOTE ABOUT A RUN: DURATION
IS BISTABLE, NOT DOSE-GRADED.** *At f = 0.07, three cells fall at **7.16 / 7.36 / 7.93 s** and three run
**19.74 / 20.00 / 20.00 s**. Same dose, same body, same warm start — **and nothing in between. The seed
picks the branch.*** ⭐ **So no refinement of the dose axis fills the band, and the whole strategy of
tuning lesion severity to match duration is dead.** *A cell landing in [13.58, 17.85] s is a rare event,
not a reachable setting.*

**Rate, measured over all 30 plantarflexor-weakness cells run so far: 2 in band** — `WPF_c00` at
16.21 s and `BF_c10` at 15.14 s — **≈ 7 %.** *Three in-band cells therefore needs on the order of 45
further cells at that rate.*

## 2. ⛔ THE ENDPOINT — CARRIED FROM r285 §3 WORD FOR WORD, UNCHANGED

**PRIMARY AND ONLY CONFIRMATORY ENDPOINT: `knee_angle_LmR`.**

**Measurement:** *`hipgap_r220.py`'s convention applied to `knee_angle_LmR` — window [1.00, 9.73],
cycles wholly inside it, drop the last, per-cycle mean ROM(l) − ROM(r) in degrees. The r281 guard
applies: a cell whose `t_end` is short of 9.73 s is NOT measured.*

**Comparison:** *seed-level disjointness of the six spastic cells (`R151S` s101–106, depth 90) against
the plantarflexor-weakness cells **restricted to those whose `t_end` lands inside [13.58, 17.85] s** —
the observed spastic duration range. Weakness cells outside that band are deposited and excluded from
the endpoint.*

⭐ **PREDICTED DIRECTION, STATED SO THE TEST CAN FAIL: weakness POSITIVE, spastic NEGATIVE, and the two
ranges disjoint.** *Post-hoc values that generated this prediction: spastic mean −0.8898, plantarflexor
weakness mean +3.8568. **If the weakness cells come back negative, or the ranges overlap, the prediction
is wrong and that is the result.***

⚠ **`hip_flexion_LmR` is measured and deposited but is NOT the endpoint.** *Post-hoc work found the
shipped discriminator fails at matched outcome and fails in the informative direction — weakness reading
MORE negative than spastic, against a shipped claim that more negative means spastic. That observation
is post-hoc and stays post-hoc; this registration does not launder it.*

⛔ **NOTHING ABOVE DIFFERS FROM r285 §3 BY ONE CHARACTER. The endpoint, the band, the guard, the
comparison and the predicted direction are all fixed by a document written before any cell of either
arm existed.**

## 3. ⭐ Pooling r285's cells — and why it is legitimate

**The 12 cells of r285 are pooled with this continuation's cells into the endpoint.**

⭐ **This is legitimate for exactly one reason: the endpoint, the band, the guard and the predicted
direction are unchanged from a registration written before ANY of these cells existed.** *Pooling
across registrations is illegitimate when the later registration adjusts the target after seeing the
earlier data. Here nothing about the target moved — only how many seeds are drawn.*
⛔ **If any part of §2 had been altered, the r285 cells could not be pooled and this continuation would
have to stand alone.**

## 4. The cells

**Same lesion, same implementation, same everything except the seeds.** *Plantarflexor weakness —
`max_isometric_force` scaled on BOTH `soleus_l` and `gastroc_l`, left, model-file edit only, no
controller change. Same warm start, same 90-generation budget, same objective as
`PREREG_weakpf_r274.md` rev 2 and `PREREG_bandfill_r285.md`.*

| f | scale | `soleus_l` | `gastroc_l` | seeds |
|---|---|---|---|---|
| 0.07 | 0.93 | 3300.57 | 2084.13 | **107–151** |
| 0.08 | 0.92 | 3265.08 | 2061.72 | **107–151** |

*`tib_ant_l` remains 1759.0 and is not touched.*

**RUN ORDER, FIXED HERE:** *for seed = 107, 108, … 151, run (f = 0.07, seed) then (f = 0.08, seed).*
**Cells are run in that order and no other.**

## 5. ⛔ THE STOPPING RULE — registered in advance, and it is about COVERAGE, not the endpoint

**Stop when THREE in-band cells exist, or when 45 cells of this continuation have run, whichever comes
first.**

*In-band means `measured` under the r281 guard AND `t_end` inside [13.58, 17.85] s. The r285 arm already
contributes one such cell (`R285BF008_s105`, 15.14 s), and `WPF_c00` (16.21 s) is from
`PREREG_weakpf_r274.md` rev 2's f = 0.05 arm.*

⛔ **THIS IS NOT A PEEKING RULE, AND THE DISTINCTION IS THE WHOLE POINT.** *The stopping criterion reads
only `t_end` — whether a cell landed in the band. **It does not read `knee_angle_LmR`, and the endpoint
is NOT computed until the arm has stopped.*** ⭐ **Stopping on coverage cannot bias an endpoint the
stopping rule never looks at.** *Stopping on the endpoint value would be the forking path; that is
forbidden here and is not implemented in the runner.*

⚠ **If 45 cells run without producing three in-band cells, the arm returns UNINFORMATIVE again**, with
the durations deposited, and the endpoint is again not evaluated. *No further continuation is authorised
by this document.*

## 6. Cost

**Up to 45 cells.** *Observed mean over the r285 arm is ≈ 269 s/cell, so the cap is roughly **3.4 h**.
Cells that fall early cost less; cells that complete cost more.*
⛔ **RUN YIELD, BINDING ON THE LAUNCHER: if the user's own SCONE work is running, our cells give way.**
**Writes only new directories under `SCONE\results`; the 112 protected directories and every existing
cell are untouched.**

## 7. Carried over unchanged

- **Both metrics and both windows deposited per cell**; the endpoint uses the shipped window.
- **Terminal objective, generation-0 value, final-ten-generation descent, `fitness_progress` and the
  full `history.txt` deposited per cell, treated as a DEPENDENT VARIABLE.** ⛔ *No analysis conditions
  on it.*
- **Net pelvis yaw per cycle deposited per cell**, never used to include, exclude or stratify.
- **Duplicate-directory guard**: `>= 91` history lines with a uniqueness assertion, resolved directory
  deposited per cell.
- **δ = 2.534 σ**, frozen.

## 8. What this arm cannot do

- ⛔ **It does not separate ADD from REMOVE.**
- ⛔ **It does not establish that duration is the only rival explanation.** *If the endpoint fires it
  removes duration for one channel in one band. Nothing more.*
- ⚠ **It does not make any post-hoc finding confirmatory.** *r277, r279, r280, r282 and r284 remain
  post-hoc whatever this returns.*
- ⛔ **One model, one body. Nothing here becomes a statement about people.**
