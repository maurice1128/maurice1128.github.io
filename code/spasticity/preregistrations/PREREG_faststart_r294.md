# PREREG_faststart_r294.md — can this model be made to walk fast at all?

**Round 294, REVISION 2. Written and hashed BEFORE any cell of this arm exists.** *Body: 3D,
`H1922v7b3` (Hyfydy).*

| rev | sha256 | status |
|---|---|---|
| 1 | `81186b7ebec848e0412c3bbbc0bee9f7443c7d1a6e29e864f320c134d33849e4` | superseded |
| **2** | **this document** | current |

⛔ **NO r294 CELL EXISTS.** *The amendment is legitimate and is recorded with its predecessor's digest.*

**What changed, and why:** *rev 1 §2 asserted that `MeasureGait15Grf15.scone` does not exist and that no
shipped drop-in preserves the objective. **Both claims were false.** The file exists at
`C:\Program Files\SCONE\scone\scenarios\Tutorials2\data\MeasureGait15Grf15.scone` (711 B) and is a
full `CompositeMeasure`. **The error was mine: I enumerated `C:\Users\maurice\Documents\SCONE` only,
found nothing, and wrote "does not exist" when I was entitled to say "not present under that tree".***
⭐ **The METHOD rev 1 chose — the in-place one-token edit — is retained. Only its justification changes,
and a registered validation is added that the alternative file makes possible (§2).**

⛔ **THIS IS A WARM-START PROBE. THE ENDPOINT IS ACHIEVED SPEED. NO LESION, NO CHANNEL, NO
DISCRIMINATION.** *It exists only to find out whether the velocity manipulation can be delivered.*

⛔ **QUEUED LAST: r289, then r291, then r293, then this. Those three are unaltered by this document.**

---

## 1. Why this matters more than another angle

⛔ **THE ANGLE-MAGNITUDE CLASS IS EXHAUSTED.** *`VIDEO_DEGRADATION_REGISTRATION.txt` records a
post-stroke ankle **MDC of 3.8–11.5 deg** and kills five earlier candidate features for having margins
below it. **Add ours: `hip_flexion_LmR` at 1.0128 deg and `knee_angle_LmR` at 2.4773 deg.** That is
seven features dead the same way, and r290's rung 2 — real as it is — separates by less than the
smallest change a clinician can detect.*

⭐ **`SPEED_CLOSURE_r208.md` does not say what its title suggests.** *Verified by reading it: a 0.50 m/s
commanded change produced **+0.075 m/s** achieved in control (15 % of intent); the spastic arm's
delivered dose was **10.845 → 10.845 → 10.821 N**, flat to 0.2 % across all three commands;
`min_velocity` is a **lower bound with a penalty, not a target**; and the registered primary is recorded
as **NOT EVALUATED**.* ⛔ **So velocity-dependence — the axis on which spasticity is clinically DEFINED,
and the basis of the Tardieu test — has never been tested in this project. It was blocked by the tool,
not refuted.**

**The blocker is identified precisely:** *the model's fast ceiling is **~1.13 m/s from this warm start**,
measured over 270 generations — a usable span of about **11 %** above the 1.02 m/s the corpus walks at,
against a spastic avoidance of **−20.5 %** in the opposite direction.*

⭐ **So the next thing is a warm start, not a study.** *If a fast warm start exists, velocity-dependence
becomes testable for the first time — and unlike an angle magnitude it is a **SLOPE**, which a
provocation can amplify above MDC. If it does not exist, the clinical claim must rest on something other
than gait kinematics, and we will have established that by measurement rather than by guess.*

## 2. ⛔ THE EDIT, ITS JUSTIFICATION, AND A REGISTERED VALIDATION

### 2a. What ships, verified against disk

| file | min_velocity | header comment | GRF max |
|---|---|---|---|
| `Tutorials2\data\MeasureGait15Grf15.scone` (711 B) | **1.5** | ⛔ "1.0" — **stale** | 1.5 |
| `Examples2\data\MeasureGait10Grf15.scone` | 1.0 | "1.0" — right by coincidence | 1.5 |
| `Tutorials\measures\MeasureGait05Grf15.scone` | **0.5** | ⛔ "1.0" — **stale** | 1.5 |

⭐ **The 1.5 file is a full `CompositeMeasure` with `GaitMeasure`, `EffortMeasure`, `DofLimits` and
`ReactionForceMeasure`.** *Rev 1's claim that no shipped drop-in carries the composite was wrong.*

⚠ **Stale headers: 2 of the 3 distinct shipped variants** — *the 0.5 and the 1.5. The closure
(`SPEED_CLOSURE_r208.md` §5) documented one; this is one more. **The two 1.0 files are correct only
because 1.0 is what the copy-pasted comment happens to say.***

### 2b. ⛔ THE CORPUS MEASURE IS NOT THE VENDOR MEASURE

*Diffed line by line against the staged `config.scone`, ignoring `min_velocity` — corpus 46 normalised
lines, vendor 37:*

| difference | corpus | vendor |
|---|---|---|
| `EffortMeasure` **MuscleActivation** | **present**, weight **1000**, `CubedMuscleActivation` | ⛔ **absent entirely** |
| `DofLimits` knee | weight **0.1**, threshold **0** | weight 0.01, threshold 5 |
| `ReactionForceMeasure max` | **1.3** | 1.5 |
| signatures | `K0`, `G13` | none |

⛔ **So "the staged block equals the vendor 1.5 block" is FALSE today, before any edit.** *Asserting it
would halt this arm over four pre-existing differences that have nothing to do with `min_velocity`.*

### 2c. ⭐ The registered method and its true justification

**Change `min_velocity` from `1.0` to `1.5` IN PLACE inside the corpus's own `CompositeMeasure`,
altering nothing else.**

⭐ **JUSTIFICATION, CORRECTED: the in-place edit guarantees that exactly ONE TOKEN differs from the
configuration every other cell in this project was optimised under.** ⛔ **NOT because no alternative
exists — one does, and §2a names it. The vendor file is rejected because adopting it would change four
further terms and break comparability with all 74 existing cells.**

### 2d. ⛔ REGISTERED VALIDATION — differential, and it gates the run

**After staging and before any cell runs, assert BOTH:**

1. **`diff(vendor 1.0 file, vendor 1.5 file)` is exactly `min_velocity: 1.0 → 1.5`** — *establishing
   what the one-token change looks like when the vendor makes it.*
2. **`diff(corpus staged, corpus original)` is exactly the same single token change.**

⛔ **If either diff touches anything else, the edit is wrong and THE ARM DOES NOT RUN.** *The comparison
result is deposited per cell.*

⭐ **This tests what an equality assertion was meant to test — that our edit is the same edit the vendor
made — without asserting an equality that was never true.**

⚠ **The written value is also read back from the staged config and deposited. The header comment is
never trusted (§2a).**

### 2e. ⚠ Instrument fact: a name that is not a source, inside our own configuration

**The corpus `ReactionForceMeasure` is `max = 1.3`, while every vendor file named `…Grf15` sets
`max = 1.5`, and our configuration derives from that family.**

⛔ **The name says 1.5 and the value is 1.3.** *This is the same failure mode as the stale header — a
name treated as a source — and it sits **inside our own configuration** rather than the vendor's, which
makes it more dangerous, not less.* ⚠ **It is recorded here as an instrument fact, next to the
`min_velocity` semantics, and nothing in this arm depends on the name.**

## 3. The cells

**Control model only. No lesion.** *`soleus_l` 3549.0, `gastroc_l` 2241.0, `tib_ant_l` 1759.0 — all at
base. No `SpasticL` block. This differs from the shipped control by one token in the objective.*

| | |
|---|---|
| `min_velocity` | **1.5** (from 1.0), in place, read back and deposited |
| generations | **600** |
| seeds | **2** (101, 102) |
| warm start | **the existing control endpoint** — each seed initialised from its own `R151C_s10n` best `.par` |
| cells | **2** |

## 4. ⛔ THE ENDPOINT — achieved speed, and nothing else

**ENDPOINT: achieved speed, computed exactly as `SPEED_LADDER_r217.json` computes it** — *`pelvis_tx`
displacement over the GRF-delimited window [1.00, 13.58], identical to `speed_gate_r203.py`.*

⛔ **No joint channel is computed by this arm's launcher or its analysis. Not the knee, not the hip, not
any of the sixteen.** *`t_end`, cycle count and terminal objective are deposited as context.*

## 5. ⭐ SUCCESS AND FAILURE, BOTH REGISTERED IN ADVANCE

| | criterion |
|---|---|
| ⭐ **SUCCESS** | **achieved speed > 1.30 m/s** — a genuine **25 %+** span above the 1.02 m/s the corpus walks at |
| ⛔ **FAILURE — THE SAME ASYMPTOTE** | achieved speed ≤ 1.30 m/s **AND** the gain over the final 100 generations < **0.02 m/s** |
| ⚠ **PARTIAL** | achieved speed ≤ 1.30 m/s but still gaining ≥ 0.02 m/s per 100 generations at generation 600 — *the budget bound, not the model* |

*The failure threshold is set from the closure's own measurement: **~0.012–0.014 m/s per 100 generations
and falling at 270 generations**. A run still gaining faster than that at 600 has not asymptoted; one
gaining slower has.*

⭐ **WHY FAILURE IS THE STRONGER RESULT.** *The closure on disk says the velocity axis is closed **for
this tool** — the manipulation was never delivered. A failure here says it is closed **for this MODEL**,
from its own warm start, at 6.7× the generation budget the corpus uses. **That is a different and much
stronger closure, and it ships at full strength.***

## 6. Scope

- ⛔ **No lesion, no channel, no discrimination.** *This arm cannot answer any question about lesion type
  and does not attempt to.*
- ⛔ **It does not revise `SPEED_CLOSURE_r208.md`.** *That document's finding — the manipulation was not
  delivered — stands. This tests whether it can be.*
- ⚠ **It does not test velocity-dependence.** *It tests whether a warm start exists from which
  velocity-dependence could be tested. That study is not authorised here.*
- ⚠ **Two seeds is a probe, not a sample.** *If both agree the answer is clear; if they disagree that is
  reported as such and the probe is inconclusive.*

## 7. Operational

- ⛔ **RUN YIELD: if the user's own SCONE work is running, our cells give way.** ⚠ *The check counts all
  `sconecmd` machine-wide and cannot distinguish our arms from the user's, so arms run SEQUENTIALLY.*
- ⛔ **ORDER: r289 → r291 → r293 → r294.** ⚠ *A registered arm still runs even if an earlier result makes
  it look unnecessary.*
- **Writes only new directories under `SCONE\results`; the 112 protected directories and every existing
  cell are untouched.**
- **Terminal objective, generation-0 value, `fitness_progress`, the full `history.txt`, `t_end`, cycle
  count and the read-back `min_velocity` deposited per cell.**
- **Duplicate-directory guard**: `>= 601` history lines with a uniqueness assertion, since this arm's
  budget is 600 generations rather than 90.

## 8. Cost

**2 cells at 600 generations.** *The corpus runs 90 generations at ≈ 204 s/cell for control, so 600
generations is ≈ 6.7× ≈ **1,360 s/cell**, and the arm is roughly **45 minutes**.* ⚠ *A model that walks
faster simulates the same 20 s, so cost should scale with generations rather than with speed.*
