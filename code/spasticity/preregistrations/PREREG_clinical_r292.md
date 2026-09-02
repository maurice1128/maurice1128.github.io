# PREREG_clinical_r292.md — the clinical pair, split from the anatomy-matched pair

**Round 292. Written and hashed BEFORE any r289 cell is analysed.** *r289 is at 4 of 12 cells run and
0 analysed at the time of writing. No endpoint of any kind has been computed on it.*

⛔ **`PREREG_matched20_r289.md` (`863f1376…`) IS NOT ALTERED.** *Its registered endpoint is reported
exactly as it stands, including the outcome this document predicts it will return. r285, r287, r290 and
r291 are likewise untouched.*

---

## 1. The defect in r289 §4, found after it was hashed

**r289 §4 defines its comparison as:** *"seed-level disjointness of the completing spastic cells against
the **completing** weakness cells already on disk — every dorsiflexor-weakness and plantarflexor-weakness
cell with `t_end` = 20.000 s."*

⛔ **That is ONE POOLED GROUP, and the two families in it behave OPPOSITELY on the registered endpoint
channel.** *Measured from `CHANNELS_G2_r219.json` and `BANDFILL_ENDPOINT_r290.json`:*

| group | `knee_angle_LmR` |
|---|---|
| spastic, KV 0.050 | **−0.8898** |
| **dorsiflexor** weakness (W870 / W892 / W915) | **−0.6294 / −0.7827 / −0.6052** — *same sign as spastic* |
| **plantarflexor** weakness, in band | **+2.2638 … +2.7347** — *opposite sign* |

⭐ **PREDICTED IN ADVANCE, SO IT CANNOT LATER LOOK LIKE AN EXCUSE: r289's registered pooled endpoint
will return rung 4, OVERLAP** — *not because the knee fails, but because a pooled group spanning
−0.78 … +2.73 straddles the spastic range −1.889 … −0.2135 by construction.* ⛔ **It is reported as
rung 4 regardless, because that is what was registered.**

⚠ **This defect was invisible when r289 was written.** *The dorsiflexor/plantarflexor split on the knee
was established afterwards, by reading `CHANNELS_G2_r219.json` — which had measured all sixteen channels
including the knee since r219. **The channel was never missing; the second muscle group was.***

## 2. ⭐ Why the split matters more than the pooling

⛔ **THE CLINICAL PAIR IS PLANTARFLEXOR SPASTICITY versus DORSIFLEXOR WEAKNESS.** *Both produce equinus,
the treatments are opposite, and telling them apart is the question this project exists to answer.*

⚠ **r290 did not answer it.** *r290 compared plantarflexor spasticity against **plantarflexor** weakness
— which `PREREG_weakpf_r274.md` chose deliberately, to hold anatomy constant. That is a real question
and it got a real answer (rung 2). **It is not the clinical question.***

⭐ **r289 is the arm that can answer the clinical question, because making spastic cells complete
20.000 s lets them be compared against the 36 dorsiflexor-weakness cells that also complete — same
duration, same cycle count, no fall confound.** *That comparison has never been available in this
project.*

## 3. ⛔ Two readings, registered here, reported separately, NEVER pooled

**Endpoint, convention, guard and predicted direction are carried from `PREREG_bandfill_r285.md` §3
unchanged: `knee_angle_LmR`, `hipgap_r220.py` convention, window [1.00, 9.73], cycles wholly inside,
drop the last, per-cycle mean ROM(l) − ROM(r) in degrees, r281 guard.**

| | reading | spastic group | weakness group |
|---|---|---|---|
| ⭐ **C** | **THE CLINICAL PAIR** | completing r289 spastic cells (`t_end` = 20.000 s) | the **36 dorsiflexor**-weakness completers |
| **P** | **the anatomy-matched pair** | the same completing r289 spastic cells | the **plantarflexor**-weakness completers (r276 / r285 / r287) |

⛔ **THE TWO WEAKNESS FAMILIES ARE NEVER MERGED.** *They behave oppositely on the endpoint channel, so
pooling them hides exactly the distinction that matters.*

**PREDICTED DIRECTIONS, STATED SO EACH CAN FAIL:**

- ⭐ **Reading C — knee: OVERLAP predicted.** *The shipped scan has spastic −0.8898 against dorsiflexor
  weakness −0.6294 / −0.7827 / −0.6052, same sign. **If reading C comes back disjoint, the prediction is
  wrong and that is a positive result for the clinical question.***
- **Reading P — knee: DISJOINT predicted, weakness positive and spastic negative.** *r290 found this at
  13.58–17.85 s; reading P tests whether it survives at 20.000 s.*

## 4. ⭐ `hip_flexion_LmR` — the most consequential number left in this project

**Deposited as secondary for both readings. NOT the endpoint. Not promoted afterwards.**

⭐ **Reading C's hip value is the direct test of whether the shipped headline survives when nothing
falls.** *The shipped claim is spastic −2.1053 against dorsiflexor weakness +0.3594 / +0.5533 / +0.4429 —
opposed and separated. Post-hoc work (`PERCYCLE_r279.json`, `CONFOUND_DURATION_r277.json`) found the
separation tracks falling: 46 completers span −0.8443 … +1.1824 and 10 fallers span −4.4908 … −1.2099,
disjoint by +0.3656°. **Every spastic cell in the shipped corpus fell; every dorsiflexor-weakness cell
completed.***

⛔ **PREDICTED IN ADVANCE: at matched completion the hip separation will NOT survive** — *the completing
spastic cells are predicted to land inside the completer range −0.8443 … +1.1824, overlapping the
dorsiflexor-weakness cells.* ⭐ **If they land below −1.2099, the fall explanation is refuted and the
shipped headline survives. Either way this is the measurement the corpus has never been able to make.**

## 5. Scope, and what this document does not do

- ⛔ **No new cells.** *This is an analysis registration over r289's cells plus cells already on disk.*
- ⛔ **It does not alter r289's registered endpoint**, which is computed and reported as registered,
  including its predicted rung 4.
- ⛔ **It does not make any post-hoc finding confirmatory.** *r277, r279, r280, r282, r284, r288 and
  r290's hip secondary remain post-hoc.*
- ⚠ **It does not revise r290.** *r290 stands as rung 2 on the anatomy-matched pair at 13.58–17.85 s,
  permanently.*
- ⚠ **Reading C rests on r289 producing at least 3 completing spastic cells.** *If fewer complete,
  reading C is reported as UNINFORMATIVE at whatever n it reached and the clinical question stays open.*

## 6. The ladder — evaluated separately for C and P, after r289 stops

| # | rung | criterion |
|---|---|---|
| 1 | ⛔ **UNINFORMATIVE** | fewer than 3 completing spastic cells, or fewer than 3 in the weakness group |
| 2 | ⭐ **DISJOINT-AS-PREDICTED** | ranges disjoint in the direction predicted for that reading |
| 3 | ⛔ **DISJOINT-OPPOSITE** | disjoint, the other way round |
| 4 | ⛔ **OVERLAP** | the ranges overlap |

**Null: exhaustive permutation within each reading, count reported as a floor and never as a p-value.**
⛔ **No endpoint is computed until r289 has stopped.**
