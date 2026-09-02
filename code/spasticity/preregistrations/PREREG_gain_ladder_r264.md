# PREREG_gain_ladder_r264.md — the reflex gain ladder that was on disk all along

**Round 264.** ⛔ **THIS REGISTRATION IS NOT BLIND AND CANNOT BE. Read §1 before reading anything else.**

---

## 1. ⛔ WHAT WAS ALREADY SEEN, BEFORE THIS WAS WRITTEN

**A first-time reader, given the manuscript and the deposits, located 24 directories the manuscript
twice asserted did not exist, and ran a first pass. Its results were reported to this analyst before
this registration was written.** *Recorded here in full, so that nothing below can be presented as a
prediction:*

| gain | cells with ≥2 cycles | mean yaw deg/cycle | durations |
|---|---|---|---|
| KV 0.050 | 6/6 | +1.40 | all ≥ 13.58 s |
| KV 0.150 (R169) | 3/6 | +7.27 | 5.25–6.01 s; others 0.66–1.70 |
| KV 0.150 (R172) | 3/6 | +4.59 | 5.62–7.70 s; others 0.85–1.54 |
| KV 0.400 | 0/12 | — | all 12 terminate at 0.69–0.70 s |

⭐ **So this registration governs only the CONDUCT of the confirmatory run — its reproduction check,
its separations, its endpoints and its bounds — not the direction of its result, which is already
known.** ⚠ **A registration written after the numbers is worth less than one written before, and this
document does not claim otherwise. It is written because the alternative — running it with no
registration at all — is worse, and because the bounds below are the part that can still bind.**

## 2. What is computed

**Read-only, from `.par.sto` files already on disk. No simulation is run and no controller is
re-optimised.**

1. **REPRODUCTION FIRST.** *The KV 0.050 arm is recomputed by this script and must match
   `TURN_r260.json` per seed and in the arm mean (+1.3681 / +1.5576). **If it does not, nothing else
   in the run is reported.***
2. Net pelvis yaw per gait cycle for every KV 0.150 and KV 0.400 cell, by the same code path.
3. **Time-to-failure and cycles-to-failure for every cell**, co-primary with yaw.
4. The two optimisation paths **R169 and R172 reported separately, never pooled**.

## 3. Constraints, fixed here and binding on the report

- ⛔ **SURVIVOR BIAS. The KV 0.150 yaw estimates are computed on the cells that survived long enough to
  complete cycles — the least destabilised of the six.** ⭐ **So they are a LOWER bound, and the bias
  runs toward the null. That is what makes the direction safe, and it must be stated at the number,
  not in a footnote.**
- ⛔ **THE TWO PATHS MUST NEVER BE POOLED.** *They differ by roughly 1.6× in the first pass. Pooling
  them would manufacture a precision neither supports.*
- ⛔ **TIME-TO-FAILURE IS CO-PRIMARY, NOT A FOOTNOTE.** *At KV 0.400 no cell completes cycles, so yaw
  is undefined and time-to-failure is the only measurable endpoint. **12 of 12 cells terminating at
  0.69–0.70 s is the cleanest datum in the set precisely because it requires no gait cycle at all.***
- ⚠ **2–4 cycles is a thin basis for a per-cycle mean.** *Per-cycle spread is reported alongside every
  KV 0.150 mean.*

## 4. What this buys, at exactly this width

⭐ **A three-point gain → yaw → time-to-failure relation in the same body breaks the CARDINALITY
confound on the reflex axis.** *"One reflex condition" has been the fatal objection to the mechanism,
to the turning, and to every attempt to call anything reflex-specific. It is not true.*

⛔ **AND IT DOES NOT BUY THE 2 × 2, AND THE MANUSCRIPT MUST KEEP SAYING SO**, in the reader's words:
*"A plantarflexor-weakness arm and a dorsiflexor-reflex arm, six seeds each, are runs that do not
exist and cannot be substituted read-only. Until they exist, no statement about lesion **type** is
available from this corpus at any level of effort, and the paper should stop attempting one."*

⚠ **Nor does it repair the magnitude, site or antagonist confounds (§M3), which are untouched by a
gain ladder within one lesion type.**

## 5. Readings

- **A — yaw rises monotonically with gain across the three levels, in both paths separately, and
  failure time falls.** *Reported as a within-lesion-type dose–response, with the survivor-bias
  direction stated at the number.*
- **B — the paths disagree in direction.** *Reported as such; no pooled claim is made, and the
  gain ladder does not support a dose–response.*
- **C — the reproduction of KV 0.050 fails.** ⛔ *Nothing is reported and the discrepancy is
  investigated first.*
