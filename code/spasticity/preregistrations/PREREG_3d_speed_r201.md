# PREREG_3d_speed_r201.md — walking speed as the provocation axis, in 3D

**Registered BEFORE any cell is launched.** *Parents: `PREREG_3d_matched_r174.md`,
`PREREG_3d_replication_r179.md`. Step-1 arithmetic: `paper/SPEED_DOSE_r200.json`, produced by
`scone/speed_dose_r200.py`.*

**Why this task and not another.** *Level walking at one speed is the only task the 3D corpus
contains. Every feature this project has buried was measured at that single speed. **The spastic
reflex is velocity-gated by construction, so speed is the mechanism's own signature axis** — and it is
the one axis that changes the delivered provocation without touching KV, whose ceiling is registered.*

---

## 0. ⛔ THE ARITHMETIC THAT OPENED THIS AND CLOSED ITS ALTERNATIVE

**Delivered dose = `KV × max(0, ce_vel_norm) × Fmax`, summed over `soleus_l` and `gastroc_l`, with the
excitation clamp `min(du, max(0, 1−u))`. Method copied unmodified from `dose_r174.py`.**

⛔ **DOSE-MATCHING TO KV 0.150 IS DEAD ON ARITHMETIC.** *KV 0.150 delivers 40.880 N against KV 0.050's
13.627 N — exactly 3.0000×. Reaching it by speed needs **3.06 m/s**, which is above the human
walk–run transition and outside anything this model was optimised for. **Closed without a run.***

⭐ **THE SLOPE ROUTE IS OPEN.** *The clamp never binds — tested to k = 20, the dose stays exactly
proportional — so **dose = 13.340 N per (m/s) × speed**, linear, no saturation. Across 0.80–1.30 m/s
the spastic provocation spans **10.67–17.34 N, a 1.62× range**, while the weak arm's `(1−s)·Fmax` is
constant in speed by construction. **That asymmetry is what this design measures.***

### 0a. ⛔ THE ASSUMPTION THIS STUDY EXISTS TO TEST — registered as a primary reported quantity, not as a limitation

⛔ **The 13.340 N/(m/s) line assumes fibre velocity scales linearly with gait speed — TIME-SCALING —
and that is an ASSUMPTION, NOT A MEASUREMENT.** *Real gait changes stride length and duty factor with
speed. Step 1 credited speed with a proportional rise in `ce_vel_norm` that a faster gait may not
produce, so **it is an optimistic bound: a bound that failed would have been conclusive, and one that
succeeds is not.** The single-speed corpus contains no second speed against which to check it.*

⭐ **REGISTERED OUTCOME 3 BELOW MEASURES IT DIRECTLY, AND EITHER RESULT IS REPORTED AS A FINDING:** *if
achieved dose does not track the line, **that is a fact about the model's gait strategy — how it
chooses to go faster — not a failure of this design**, and the primary is then interpreted against a
measured dose axis instead of a speed axis.*

---

## 1. Design

| | |
|---|---|
| **speeds** | **0.80, 1.02, 1.30 m/s** — *1.02 is the MEASURED benchmark (control mean 1.0215 m/s, per-seed 1.0158–1.0252), not a nominal target; 0.80 and 1.30 are the ends of step 1's reachable band* |
| **arms** | control · spastic **KV 0.050** · weak **`tib_ant_l` ×0.892** |
| **seeds** | 6 per cell — 101…106 |
| **cells** | 3 speeds × 3 arms × 6 seeds = **54** |
| **start** | from-healthy warm start, **identical treatment for all three arms**, no continuation |

⛔ **NO NEW MAGNITUDES. KV stays 0.050 and the weak scale stays ×0.892.** *The KV ceiling is registered
and titrating against it is forbidden. This design changes the TASK, not the lesion.*

⛔ **Both defects the parent studies recorded are structurally excluded:** *r169's depth confound —
every cell runs from-healthy to the same cap, so no arm is deeper than another; r172's path dependence
— no cell continues from another cell's `.par`.*

---

## 2. ⛔ PRIMARY — the slope, on all sixteen channels

⭐ **PRIMARY: `d(channel)/d(speed)` per seed, fitted across the three speeds, for all 16 registered
channels.**

`ankle_angle_l`, `ankle_angle_r`, `knee_angle_l`, `knee_angle_r`, `hip_flexion_l`, `hip_flexion_r`,
`hip_adduction_l`, `hip_adduction_r`, `pelvis_list`, `pelvis_rotation`, `lumbar_bending`, `cycle_time`,
`ankle_angle_LmR`, `knee_angle_LmR`, `hip_flexion_LmR`, `hip_adduction_LmR`

⛔ **The channel set is inherited unchanged from `PREREG_3d_replication_r179.md`. No new channels, no
post-hoc selection, and ALL SIXTEEN ARE REPORTED WHATEVER THEY SHOW.**

### 2a. ⭐ What a within-cell slope buys, and what it does not

⭐ **BUYS: it cancels seed-basin variation.** *Each slope is computed within one seed across three
speeds, so the optimiser basin that seed fell into is differenced out. **Basin variation has dominated
every between-arm comparison this project has made** — it is the `Z → G` path that the r174 causal
argument names and that no between-arm contrast has ever removed.*

⛔ **DOES NOT BUY: three points, six seeds, one model, one controller, one objective.** *A three-point
slope has one degree of freedom for curvature and none to spare. The seeds are optimiser restarts, not
subjects. **No coverage claim, no p-value and no patient-level inference may be drawn from this
design**, exactly as in the parent studies.*

---

## 3. ⛔ GATE G FIRST — and a failed speed is an ANSWER

⛔ **Gate G is evaluated from the `.sto` at every speed, for every arm, BEFORE any endpoint is
computed.** *Complete iff `history.txt` ≥ 91 lines and the tag resolves to exactly one such directory.*

⭐ **A speed at which an arm fails is a RESULT, not attrition: it bounds the range this model can walk
at all, and it is reported as the answer to "can this model do the task".** *This project has twice
mistaken a boundary for a setback.*

### 3a. ⛔ Registered NOW: what happens if an arm survives two speeds but not three

⛔ **A two-point contrast is a DIFFERENCE, not a slope, and it will be reported under that name — never
as a slope, never pooled with three-point slopes, and never used for the primary comparison.**

⭐ **The arm is NOT dropped.** *Dropping it would condition on survival, which is a descendant of the
lesion, and this project has already recorded collider conditioning once. The two-point difference is
reported beside the surviving three-point slopes, labelled as a different quantity, and the primary
comparison is made only among arms with all three speeds.*

⛔ **If NO arm survives all three speeds, the primary is not computed and the study reports the
viability boundary as its result.**

---

## 4. Registered outcome 3 — the dose axis, measured

**Achieved delivered dose is computed at every speed for the spastic arm, by the step-1 method, and
checked against the registered line `dose = 13.340 N per (m/s) × speed`.**

- ⭐ **Tracks the line** → the time-scaling assumption holds, speed is a clean dose axis, and the
  primary reads as registered.
- ⛔ **Does not track** → *the assumption is refuted. **The primary is then interpreted against the
  MEASURED dose per cell rather than against nominal speed**, and the failure is reported as a finding
  about how this model goes faster.*

⚠ **This is registered as an outcome, not a diagnostic, so it is reported whichever way it falls.**

---

## 5. ⛔ BOTH BRANCHES, EQUAL WEIGHT

⭐ **SLOPES SEPARATE THE ARMS** → *the reflex's defining property — velocity dependence — reaches gait
kinematics, and every single-speed feature this project buried was measured at the wrong altitude.*

⛔ **SLOPES DO NOT SEPARATE** → *velocity dependence does not reach the kinematics. **The strongest
remaining idea closes on the mechanism's own terms**, which is the cleanest negative available to this
project: not "we failed to find a feature" but "the mechanism's signature axis does not carry the
signal."*

⚠ **Neither branch is preferred here and no prediction is registered**, *because the seat writing this
has seen the step-1 arithmetic and nothing else.*

---

## 6. Cost — measured, not relayed

⛔ **The figure supplied to this seat was 79.2 s/cell. IT DOES NOT VERIFY.** *Measured from the six
completed control cells at identical depth and warm start — `history.txt` mtime minus directory
creation time:*

| cells | lines | wall clock |
|---|---|---|
| `R151C_s101`…`s104` | 91 | 211.7, 213.7, 214.2, 213.4 s |
| `R151C_s105`…`s106` | 91 | 185.8, 185.2 s |

**Mean 204.0 s/cell — 2.6× the relayed figure.**

| | |
|---|---|
| 54 cells × 204.0 s | **11,016 s** serial |
| **concurrency 2** | ⭐ **5,508 s = 91.8 min ≈ 1.53 h** |
| the relayed figure would have predicted | 35.6 min |

⚠ **These six cells may have run under contention, which would inflate per-cell wall time; the measured
figure is therefore an upper bound and the true cost may be lower.** ⛔ **It is registered as measured
rather than adjusted.**

⛔ **Concurrency 2. The 112 protected directories under `C:\Users\maurice\Documents\SCONE\results\`
yield nothing; our cells yield on any conflict. No `--run` beyond these 54 cells. Progress is counted
from `history.txt` line counts and directory mtimes ONLY — `LAUNCH_STATUS.json` is never read.**

---

## 7. What this study does NOT do

⛔ **No sit-to-stand. No slopes. No mirrored-lesion arm. No new KV. No new weak scale. No new channel
set. No continuation from any existing `.par`. No document repair while this runs.**
⛔ **Writes confined to `C:\Users\maurice\Desktop\spasticity_paper\` and the 54 new result
directories. The frozen manuscripts are not opened.**
