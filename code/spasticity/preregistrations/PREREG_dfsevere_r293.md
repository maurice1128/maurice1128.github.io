# PREREG_dfsevere_r293.md — can dorsiflexor weakness fall at all?

**Round 293. Written and hashed BEFORE any cell of this arm exists.** *Body: 3D, `H1922v7b3` (Hyfydy).*

⛔ **THIS IS A DURATION PROBE. THE ENDPOINT IS `t_end`. IT IS NOT A DISCRIMINATION TEST AND MUST NOT BE
WRITTEN AS ONE.** *No joint channel is computed by this arm's launcher or by its analysis.*

⛔ **`PREREG_bandfill_r285.md`, `_r287.md`, `PREREG_matched20_r289.md`, `PREREG_bandfill_r291.md` and
`PREREG_clinical_r292.md` are NOT altered by this document.**

---

## 1. The missing cell of the design

**`CONFOUND_DURATION_r277.json` established that the shipped 3D comparison has ZERO duration overlap
between its arms** — 36 dorsiflexor-weakness cells at exactly 20.00 s, 6 spastic cells at 13.58–17.85 s.
⛔ **Duration and arm label are collinear, so no statistical adjustment exists. Overlap has to be
manufactured, and it can be manufactured from either side.**

| | falls | completes |
|---|---|---|
| spastic, plantarflexor | **yes** (shipped, 13.58–17.85 s) | *r289, in progress* |
| weakness, plantarflexor | **yes** (r276/r285/r287) | **yes** |
| ⛔ **weakness, dorsiflexor — THE CLINICAL PAIR** | ⛔ **UNKNOWN** | **yes** (36 cells) |

⭐ **This arm fills the one empty box.** *Route 1 raises the spastic arm to completion (r289). Route 2 —
this arm — lowers the dorsiflexor-weakness arm until it falls, if it can.*

⚠ **The shipped ladder stops at ×0.800 and every one of its 36 cells completes 20.00 s, so the
interesting region is far below anything this project has run.**

## 2. The cells

**Dorsiflexor weakness: `max_isometric_force` scaled on `tib_ant_l` ALONE. Model-file edit only, no
controller change — identical in every other respect to the shipped `R151W` / `R174W` arms: same warm
start, same 90-generation budget, same objective, same seeds.** *`soleus_l` (3549.0) and `gastroc_l`
(2241.0) are NOT touched.*

| scale | `tib_ant_l` `max_isometric_force` | seeds | cells |
|---|---|---|---|
| **×0.50** | **879.5** | 101–106 | 6 |
| **×0.30** | **527.7** | 101–106 | 6 |
| **×0.10** | **175.9** | 101–106 | 6 |
| **×0.00** | **0** | 101–106 | 6 |

**24 cells.** ⭐ *×0.00 — complete loss of the muscle — is included because it bounds the question: if
even total dorsiflexor loss does not produce a falling gait, no dorsiflexor severity does.*

⚠ **RISK, REGISTERED: `max_isometric_force = 0` may be rejected by the model or the integrator.** *If
×0.00 is not admissible it is reported as **NOT ADMISSIBLE**, with the failure recorded, and the ladder
stands at ×0.50 / ×0.30 / ×0.10. **It is not silently replaced by a small non-zero value.***

## 3. ⛔ THE REGISTERED PURPOSE AND ENDPOINT

**PURPOSE, stated before the data: to determine whether dorsiflexor weakness can produce a falling gait
in this model at all, and if so at what severity.**

**ENDPOINT: `t_end`.** *Per cell, from the `.par.sto`, with cycle count and Gate-G admission
(`MIN_DUR = 9.73`, `MIN_CYC = 5`) deposited alongside.*

⛔ **NO JOINT CHANNEL IS COMPUTED IN THIS ARM.** *Not `knee_angle_LmR`, not `hip_flexion_LmR`, not any
of the sixteen. The launcher reads `t_end` only and the analysis reads `t_end`, cycles and Gate-G only.*

## 4. ⭐ THE NULL IS THE INFORMATIVE BRANCH, AND IT IS REGISTERED AS A RESULT

⛔ **If no dorsiflexor severity down to and including ×0.00 produces a cell that falls inside
[13.58, 17.85] s, then DORSIFLEXOR WEAKNESS IS STRUCTURALLY NON-FALLING IN THIS MODEL.**

⭐ **That is not a failed run. It is a stronger statement than "the arms happened not to overlap":** *it
would mean the shipped comparison set a lesion that falls against a lesion that **cannot** fall, at any
severity, including total loss of the muscle.* **It belongs in the paper as a result, and it is reported
at full strength.**

⚠ *A weaker variant is also registered: cells may fall but only BELOW the band — `t_end` < 13.58 s
without passing through it. That is reported as **FALLS BUT SKIPS THE BAND**, and it is consistent with
the bistability already measured at `BISTABILITY_r288.json`, where plantarflexor weakness jumps from
≈ 8 s to ≈ 20 s with a 3.53 s empty run in between.*

## 5. ⛔ What happens next is NOT decided here

**If cells DO fall inside [13.58, 17.85] s, a SEPARATE registration — written after the durations are
known and BEFORE any joint channel is opened on these cells — will compare them against the six spastic
cells on `knee_angle_LmR` and `hip_flexion_LmR`.**

⛔ **That comparison is deliberately NOT in this document.** *Putting it here would let the choice of
which cells to compare be made in the same breath as seeing which cells fell.*

## 6. The ladder — evaluated on `t_end` only, after the arm stops

| # | rung | criterion |
|---|---|---|
| 1 | ⛔ **NOT ADMISSIBLE** | the ×0.00 condition is rejected by the model; recorded, ladder stands at the other three |
| 2 | ⭐ **FALLS IN BAND** | at least one cell has `t_end` inside [13.58, 17.85] s — the follow-on registration of §5 becomes available |
| 3 | ⚠ **FALLS BUT SKIPS THE BAND** | cells fall (`t_end` < 20.000 s) but none lands inside the band |
| 4 | ⛔ **STRUCTURALLY NON-FALLING** | every cell at every severity, including ×0.00, completes 20.000 s |

*Exhaustive on `t_end`: either a cell lands in band, or cells fall outside it, or nothing falls.*
⭐ **Rungs 2, 3 and 4 all ship at full strength. Rung 4 is the one this project would find most
surprising and it is registered as a result, not as an absence.**

## 7. Operational

- ⛔ **RUN YIELD: if the user's own SCONE work is running, our cells give way.** ⚠ *The check counts all
  `sconecmd` machine-wide and cannot distinguish our arms from the user's, so arms run SEQUENTIALLY.*
- ⛔ **ORDER: r289 finishes, then r291, then r293.** ⚠ **If r289's result makes r291 or r293 look
  unnecessary, they still run.** *Declining to run a registered arm because an earlier result was
  favourable is the same forking path in reverse.*
- **Writes only new directories under `SCONE\results`; the 112 protected directories and every existing
  cell are untouched.**
- **Terminal objective, generation-0 value, final-ten-generation descent, `fitness_progress` and the
  full `history.txt` deposited per cell, treated as a DEPENDENT VARIABLE.**
- **Duplicate-directory guard**: `>= 91` history lines with a uniqueness assertion.

## 8. What this arm cannot do

- ⛔ **It cannot discriminate lesion type.** *It measures duration and nothing else.*
- ⛔ **It does not make any post-hoc finding confirmatory.**
- ⚠ **It does not test whether a falling dorsiflexor cell resembles a spastic one.** *That is §5's
  follow-on and it is not authorised by this document.*
- ⛔ **One model, one body, six optimiser seeds per severity. Nothing here becomes a statement about
  people.**
