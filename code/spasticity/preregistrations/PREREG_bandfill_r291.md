# PREREG_bandfill_r291.md — closing the two gaps r290 left open

**Round 291, REVISION 2. Written and hashed BEFORE any cell of this arm exists.** *Body: 3D,
`H1922v7b3`.*

| rev | sha256 | status |
|---|---|---|
| 1 | `49b1a3b40c9fe967c73834acb1a13a7919dff2e04679a4bdfe94384e5434e489` | superseded |
| **2** | **this document** | current |

⛔ **NO r291 CELL EXISTS. NO r291 RESULT EXISTS.** *The amendment is therefore legitimate; it is recorded
with its predecessor's digest rather than made silently.*

**What changed:** *rev 1 widened the spastic comparison group to three KV values. The widening cannot be
data-driven — none of those cells exists — but it happened **after** r290 returned rung 2 in our favour,
and that is an argument a reader has to accept rather than a fact they can check.* ⭐ **Rev 2 removes the
need for the argument: BOTH the original group and the widened group are computed and reported side by
side, neither designated primary (§3a).**

⛔ **`PREREG_bandfill_r285.md` (`c27a7265…`), `PREREG_bandfill_r287.md` (`580ec823…`) and
`PREREG_matched20_r289.md` (`863f1376…`) are NOT altered by this document.** *r285 stands permanently at
rung 1. r287 stopped on its registered coverage rule and produced rung 2. r289 is running and runs to
its own stop.*

---

## 1. The two gaps this arm exists to close

**`BANDFILL_ENDPOINT_r290.json` returned rung 2, DISJOINT-AS-PREDICTED**: knee spastic −1.8890…−0.2135
against weakness +2.2638…+2.7347, gap +2.4773°, with `hip_flexion_LmR` overlapping at −0.9049°.
*Independently recomputed at `VERIFY_R290.json` on a second code path.* **Two things bound it.**

⛔ **GAP 1 — THE PERMUTATION IS AT ITS FLOOR.** *Three in-band weakness cells against six spastic gives
C(9,6) = 84, so **1/84 is the smallest number the design can return however clean the separation.** It
is a coverage limit reported as a floor, and it cannot improve without more cells on both sides.*

⛔ **GAP 2 — THE SPASTIC SIDE IS ONE CONDITION.** *All six spastic cells are KV 0.050 from `R151S`. The
weakness side spans three doses and three arms; the spastic side spans none. **If that one condition has
an idiosyncrasy, it is the whole spastic arm.***

⚠ **r289 addresses both, but only at `t_end` = 20.000 s and only if its cells complete** — *and its §1
records that the completion prediction rests on a figure `P3D2_LADDER_r145.json` itself flags as
`"contaminated by fall, not re-run"`. **r289 may return UNINFORMATIVE and leave both gaps open.** This
arm does not depend on it.*

## 2. ⛔ THE ENDPOINT — carried from r285 §3, unaltered

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

⚠ **APPENDED NOTE, NEW TEXT AND NOT PART OF THE CARRIED SECTION.** *The block above is r285 §3 carried
forward with its wording unchanged. **It is not byte-identical to r285 §3.*** ⭐ **The endpoint, the
band, the r281 guard and the predicted direction are unchanged. The only thing this arm varies is the
SPASTIC COMPARISON GROUP, and it varies it by computing BOTH the original and the widened group rather
than replacing one with the other — see §3a.**

## 3. The cells

**SPASTIC SIDE — the new part, and the reason this arm exists.**
*`ConditionalController` → `ReflexController` named `SpasticL`, byte-identical to `R151S`'s block except
`KV`: `target = soleus` and `target = gastroc`, `delay = 0.020`, `allow_neg_V = 0`, `legs = left`, all
five gait states. Re-optimised exactly as `R151S` was — same warm start, same 90-generation budget, same
objective. No muscle `max_isometric_force` is altered.*

| KV | seeds | cells | expectation |
|---|---|---|---|
| **0.035** | 101–106 | 6 | *longer than KV 0.050's 13.58–17.85 s* |
| **0.070** | 101–106 | 6 | *shorter; the gain ladder puts KV 0.150 at ≈ 3.3 s* |

⚠ *Expectations are stated so they can be wrong. **Cells landing outside [13.58, 17.85] s are deposited
and excluded by the same rule as every other cell.***

**WEAKNESS SIDE — continuation of the r287 sampling.**
*Plantarflexor weakness, `max_isometric_force` scaled on both `soleus_l` and `gastroc_l`, left, at
**f = 0.05, 0.07, 0.08**, seeds **152 upward**. Run order: for seed = 152, 153, …, run f = 0.05, then
0.07, then 0.08.*

### 3a. ⛔ TWO READINGS, BOTH REPORTED, NEITHER PRIMARY

**The endpoint is computed twice, against two spastic comparison groups, and both ship at full strength
whatever they say.**

| | reading | spastic group | weakness group |
|---|---|---|---|
| ⭐ **A** | **the original group** | the six `R151S` KV 0.050 cells, exactly as `PREREG_bandfill_r285.md` §3 names them | all in-band weakness cells |
| ⭐ **B** | **the widened group** | all in-band spastic cells across **KV 0.050, 0.035 and 0.070** | the same in-band weakness cells |

⭐ **READING A EXISTS SPECIFICALLY SO THE WIDENING CANNOT BE READ AS A POST-HOC ADJUSTMENT.** *It is
r285 §3's comparison exactly as written, extended only by the weakness cells the sampling adds — which
r285 §3 already contemplated when it said "the plantarflexor-weakness cells restricted to those whose
`t_end` lands inside the band".*

⭐ **READING B EXISTS BECAUSE ONE SPASTIC CONDITION IS NOT A SPASTIC ARM.** *If KV 0.050 has an
idiosyncrasy, reading A cannot detect it and reading B can.*

⛔ **IF A AND B DISAGREE, THAT DISAGREEMENT IS THE RESULT AND NEITHER IS CHOSEN.** *No rule in this
document prefers one, and none is added later.*

⚠ **WHICH READING CLOSES WHICH GAP, fixed here so a larger n cannot be misreported:**
*Reading **A** closes **GAP 1 only** — its permutation floor falls as weakness cells accumulate, but its
spastic side stays one condition, so it does nothing for GAP 2.* **Reading B is the only one that closes
GAP 2.** ⛔ **A bigger n in reading A must NOT be reported as if it addressed the spastic-side
narrowness.**

## 4. ⛔ THE STOPPING RULE

**Stop when the in-band count reaches EIGHT weakness cells AND at least THREE spastic conditions are
represented in band, or when 60 cells of this arm have run, whichever comes first.**

⛔ **THE RULE READS `t_end` AND THE KV / f LABEL ONLY. IT DOES NOT READ `knee_angle_LmR`, AND THE
ENDPOINT IS NOT COMPUTED UNTIL THE ARM HAS STOPPED.** ⭐ *Stopping on coverage cannot bias an endpoint
the stopping rule never looks at. Stopping on the endpoint value would be the forking path; it is
forbidden here and is not implemented in the runner.*

*In-band means measured under the r281 guard AND `t_end` inside [13.58, 17.85] s. The pool already
contains three in-band weakness cells (`R276WPF005_s101` 16.21 s, `R285BF008_s105` 15.14 s,
`R287BF007_s109` 16.17 s) and one spastic condition (KV 0.050, six cells).*

## 5. Pooling, and what would have voided it

**Cells from r276, r285, r287 and r291 all enter the endpoint.**

⭐ **Legitimate for one reason: the endpoint, the band, the guard and the predicted direction have not
moved since r285, which was written before any of these cells existed.**
⛔ **What would have voided it:** *changing the channel; changing the band; relaxing the r281 guard;
reversing or removing the predicted direction; or choosing any of those after seeing a cell. **None has
happened, and if any does, pooling ends and the affected arm stands alone.***

## 6. ⚠ The uninformative branch — a bigger n must not disguise an unfixed gap

**If fewer than THREE spastic conditions land in band, reading B is not available, the arm reports
reading A at whatever in-band n it reached, AND reports GAP 2 as STILL OPEN in the same sentence as the
result.**

⛔ **A larger weakness n does not close GAP 2 and may not be presented as though it does.** *GAP 1 is a
coverage limit on the permutation floor; GAP 2 is a design limit on the spastic side. They are closed by
different cells and are reported separately.*

## 7. The ladder — evaluated once, after the arm stops

**The ladder is evaluated SEPARATELY for reading A and reading B, and both rungs are reported.**

| # | rung | criterion |
|---|---|---|
| 1 | ⛔ **UNINFORMATIVE** | fewer than 3 in-band weakness cells (reading A), or fewer than 3 spastic conditions in band (reading B) |
| 2 | ⭐ **DISJOINT-AS-PREDICTED** | in-band weakness all positive, in-band spastic all negative, ranges disjoint |
| 3 | ⛔ **DISJOINT-OPPOSITE** | disjoint, signs the other way round |
| 4 | ⛔ **OVERLAP** | the ranges overlap |

**Null: exhaustive permutation over the in-band cells, count reported as a floor and never as a
p-value.** ⭐ *With 8 weakness and 12+ spastic in band the floor falls well below 1/84, which is what
closes GAP 1.*

## 8. Operational

- ⛔ **RUN YIELD: if the user's own SCONE work is running, our cells give way.** ⚠ *The check counts all
  `sconecmd` machine-wide and cannot distinguish our own arms from the user's, so arms are run
  SEQUENTIALLY, never in parallel. This arm launches only after r289 stops.*
- **Writes only new directories under `SCONE\results`; the 112 protected directories and every existing
  cell are untouched.**
- **Terminal objective, generation-0 value, final-ten-generation descent, `fitness_progress` and the
  full `history.txt` deposited per cell, treated as a DEPENDENT VARIABLE.** ⛔ *No analysis conditions
  on it.*
- **Net pelvis yaw per cycle deposited per cell**, never used to include, exclude or stratify.
- **Duplicate-directory guard**: `>= 91` history lines with a uniqueness assertion.

## 9. What this arm cannot do

- ⛔ **It does not separate ADD from REMOVE.**
- ⛔ **It does not make any post-hoc finding confirmatory.** *r277, r279, r280, r282, r284 and r288
  remain post-hoc whatever this returns.*
- ⛔ **It does not revise r290.** *`BANDFILL_ENDPOINT_r290.json` stands as rung 2 under the original
  group, permanently, and nothing this arm returns changes it. r285, r287 and r289 are likewise
  untouched.*
- ⚠ **It does not test whether the knee separation survives outside the band.** *The band is where
  duration is matched; outside it, duration is the rival again.*
- ⛔ **One model, one body, six optimiser seeds per condition. Nothing here becomes a statement about
  people.**
