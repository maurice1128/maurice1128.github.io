# PREREG_bandfill_r285.md — the confirmatory test, registered before execution

**Round 285. Written and hashed BEFORE any cell of this arm exists.** *Body: 3D, `H1922v7b3` (Hyfydy).*

⛔ **THIS REGISTRATION IS NOT AMENDED AFTER ANY CELL IS SEEN. If a result suggests a change, the change
is a new registration and this one is reported as it stands.** *That rule was broken at r229 and the
cost of breaking it was a void registration and an unrecoverable executed revision.*

---

## 1. Why this arm exists

**Everything measured since r277 is POST-HOC.** *`MATCHED_FALLERS_r282.json`, `KNEE_VS_DURATION_r284.json`,
`SEPARATION_r280.json`, `PERCYCLE_r279.json`, `CONFOUND_DURATION_r277.json` — all were computed after
seeing data, all are marked post-hoc, and none is confirmatory.* ⭐ **This registration exists so that
one test is confirmatory, and its entire value comes from being written first.**

**The problem it addresses.** *The shipped 3D comparison had its two arms perfectly separated in
simulated duration: 36 dorsiflexor-weakness cells at exactly 20.00 s, 6 spastic cells at 13.58–17.85 s,
no overlap (`CONFOUND_DURATION_r277.json`). Post-hoc work then found that matching on outcome changes
which channel separates lesion type. **But only ONE weakness cell has so far landed inside the spastic
duration band, and no argument may rest on one cell.***

**Why these two doses.** *Plantarflexor weakness at f = 0.05 mostly completes the full 20.00 s; at
f = 0.10 it falls at roughly 10–13 s; at f = 0.20 it falls at roughly 7.6 s and is excluded by the
window guard. **The band 13.5–18 s that the spastic arm occupies is the gap between f = 0.05 and
f = 0.10**, and it is the only band in which the two arms can be compared at matched duration.*

## 2. The cells

**Plantarflexor weakness — `max_isometric_force` scaled on BOTH `soleus_l` and `gastroc_l`, left, model
file edit only, no controller change. Identical in every other respect to `PREREG_weakpf_r274.md`
rev 2 (`9338ce8a…`): same warm start, same 90-generation budget, same seeds, same objective.**

| f | scale | `soleus_l` | `gastroc_l` | nominal removed | seeds | cells |
|---|---|---|---|---|---|---|
| **0.07** | 0.93 | **3300.57** | **2084.13** | 47.9348 N | 101–106 | 6 |
| **0.08** | 0.92 | **3265.08** | **2061.72** | 54.7826 N | 101–106 | 6 |

**12 new cells.** *`tib_ant_l` remains 1759.0 and is not touched.*
⚠ *Nominal, not achieved: achieved removal is a post-treatment quantity and on the existing dorsiflexor
arms falls 43.7–54.2 % short of nominal (`PREREG_weakpf_r274.md` rev 2 §2). Both are deposited.*

## 3. ⛔ THE REGISTERED ENDPOINT — one channel, named before the data

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

## 4. ⛔ What counts as uninformative, fixed in advance

**If fewer than THREE plantarflexor-weakness cells land inside [13.58, 17.85] s, this arm does not
answer the question.** ⭐ *It is then reported as **UNINFORMATIVE — insufficient band coverage**, with
the durations deposited, and the endpoint is NOT evaluated at whatever n arrived.*
⛔ **No substitute endpoint, no widened band, and no pooling with out-of-band cells is permitted to
rescue it.** *Widening the band after seeing the durations is the forking path this registration exists
to close.*

## 5. The outcome ladder — four rungs, evaluated in order, first match wins

| # | rung | criterion | reading |
|---|---|---|---|
| 1 | ⛔ **UNINFORMATIVE** | fewer than 3 weakness cells inside [13.58, 17.85] s | **the arm does not answer the question; endpoint not evaluated** |
| 2 | ⭐ **DISJOINT-AS-PREDICTED** | in-band weakness all positive, spastic all negative, ranges disjoint | **`knee_angle_LmR` separates lesion type at matched duration** |
| 3 | ⛔ **DISJOINT-OPPOSITE** | ranges disjoint but the signs are the other way round | **the predicted direction was wrong; reported at full strength** |
| 4 | ⛔ **OVERLAP** | the ranges overlap | **`knee_angle_LmR` does not separate lesion type at matched duration** |

**Exhaustive by construction:** *either fewer than 3 cells are in band (rung 1), or the ranges overlap
(rung 4), or they are disjoint in one of the two directions (rungs 2, 3).*
⭐ **Rung 2 is the only rung favourable to the post-hoc finding, and rungs 3 and 4 each terminate it.
All four ship at full strength.**

**Null, if the ranges are disjoint:** *exhaustive permutation of arm labels over the in-band cells,
count reported as a floor and never as a p-value.*

## 6. Carried over unchanged from `PREREG_weakpf_r274.md` rev 2

- **Both metrics and both windows deposited for every cell**; the endpoint uses the shipped window.
- **Terminal objective, generation-0 value, final-ten-generation descent, `fitness_progress` and the
  full `history.txt` deposited per cell, and treated as a DEPENDENT VARIABLE.** ⛔ *No analysis
  conditions on it.*
- **Net pelvis yaw per cycle deposited per cell**, never used to include, exclude or stratify.
- **Duplicate-directory guard**: arms resolved by name with the resolved directory deposited per cell.
- **δ = 2.534 σ**, frozen.
- ⛔ **RUN YIELD, BINDING ON THE LAUNCHER: if the user's own SCONE work is running, our cells give way.**
- **Writes only new directories under `SCONE\results`; the 112 protected directories and every existing
  cell are untouched.**

## 7. Sequencing

⛔ **This arm does not launch until the r276 batch has finished cells 13–17.** *It is then run the same
way, `--rest`-style, one cell at a time with the yield check before each.*

## 8. What this arm cannot do

- ⛔ **It does not separate ADD from REMOVE.** *The reflex adds force during lengthening; the weakness
  removes capacity. No dose matching makes those one operation.*
- ⛔ **It does not establish that duration is the only rival.** *It removes duration as an explanation
  for this one channel in this one band, if rung 2 fires. Nothing more.*
- ⚠ **It does not make the post-hoc findings confirmatory.** *They remain post-hoc whatever this returns.*
- ⛔ **One model, one body, six optimiser seeds per dose. Nothing here becomes a statement about people.**
