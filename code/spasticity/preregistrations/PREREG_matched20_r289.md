# PREREG_matched20_r289.md — exact duration matching: a weakened reflex that completes

**Round 289. Written and hashed BEFORE any cell of this arm exists.** *Body: 3D, `H1922v7b3`.*

⛔ **`PREREG_bandfill_r287.md` (`580ec823…`) IS RUNNING AND IS NOT ALTERED, PAUSED OR ABANDONED BY THIS
DOCUMENT.** *It has a registered stopping rule and runs to its own stop. Abandoning a registered arm
because a better design occurred to us afterwards is itself a forking path, and it is not done here.
These two arms run in parallel and are reported separately.*

---

## 1. The idea, and why it is better than a band

**r285 and r287 chase a rare event.** *Plantarflexor-weakness duration is bistable (`BISTABILITY_r288.json`):
across 30 cells the seed picks a branch, and only ≈ 7 % land in the spastic band [13.58, 17.85] s. r286
returned rung 1 on one in-band cell.*

⭐ **The alternative is to move the OTHER arm.** *`P3D2_LADDER_r145.json` measured injection-only
durations — no re-optimisation: KV 0.050 → **3.87 s**, 0.025 → **8.46 s**, 0.0125 → **11.84 s**,
0.00625 → **13.57 s**, 0.003125 → **19.11 s**.* **The same KV 0.050 lesion, re-optimised the way
`run_reopt_r151.py` does it, gives 13.58–17.85 s — so re-optimisation multiplies duration by roughly
3.5–4.6×.** *At that factor KV 0.0125 and KV 0.00625 should complete the full 20.00 s.*

⚠ **The multiplier rests on a value its own deposit flags.** *`P3D2_LADDER_r145.json` annotates the
KV 0.050 rung `"contaminated by fall, not re-run"`. **So 3.5–4.6× is an estimate from a flagged number,
and the prediction that these two gains complete may simply be wrong.** If they do not complete, §3
fires and the arm reports UNINFORMATIVE.*

⭐ **What exact matching buys, if it works: both arms at `t_end` = 20.000 s, same cycle count, no band to
define, no rare-event sampling, and 36 dorsiflexor-weakness plus 5 plantarflexor-weakness completers
already on disk to compare against.** *Every duration confound this project has fought since r277
disappears when nothing falls.*

## 2. The cells

**Spastic arm, `ConditionalController` → `ReflexController` named `SpasticL`, byte-identical to
`R151S`'s block except `KV`:** *`target = soleus` and `target = gastroc`, `delay = 0.020`,
`allow_neg_V = 0`, `legs = left`, `states = "EarlyStance LateStance Liftoff Swing Landing"`.
Re-optimised exactly as `R151S` was — same warm start, same 90-generation budget, same objective, same
seeds.*

| KV | seeds | cells |
|---|---|---|
| **0.0125** | 101–106 | 6 |
| **0.00625** | 101–106 | 6 |

**12 cells.** *No muscle `max_isometric_force` is altered; `soleus_l`, `gastroc_l` and `tib_ant_l` all
remain at base. This arm differs from control by the controller block alone.*

## 3. ⛔ ADMISSION, FIXED IN ADVANCE

**A cell enters the endpoint only if `t_end` = 20.000 s.** *Cells that fall short are deposited with
their durations and are EXCLUDED from the endpoint.*

⛔ **If fewer than THREE spastic cells complete at a given KV, that KV returns UNINFORMATIVE and its
endpoint is not evaluated** — the same rule as `PREREG_bandfill_r285.md` §4, which fired and was
honoured. **No substitute endpoint, no relaxed completion criterion, and no pooling of short cells is
permitted to rescue a KV.**

## 4. ⛔ THE ENDPOINT — one channel, named before the data

**PRIMARY AND ONLY CONFIRMATORY ENDPOINT: `knee_angle_LmR`.**

**Measurement:** *`hipgap_r220.py`'s convention — window [1.00, 9.73], cycles wholly inside it, drop the
last, per-cycle mean ROM(l) − ROM(r) in degrees. The r281 guard applies.*

**Comparison:** *seed-level disjointness of the completing spastic cells against the **completing**
weakness cells already on disk — every dorsiflexor-weakness and plantarflexor-weakness cell with
`t_end` = 20.000 s.*

⭐ **PREDICTED DIRECTION, STATED SO THE TEST CAN FAIL: weakness POSITIVE, spastic NEGATIVE, ranges
disjoint.** *This is the same prediction `PREREG_bandfill_r285.md` §3 made, now tested at the other end
of the duration axis. **If the completing spastic cells come back positive, or the ranges overlap, the
prediction is wrong and that is the result.***

## 5. `hip_flexion_LmR` — deposited, not the endpoint, and it has a range it must land in

⚠ **Deposited for every cell. NOT the endpoint.**

⭐ **At matched completion it is the direct test of whether the shipped discriminator survives when
nothing falls.** *Measured from `PERCYCLE_r279.json` and reproduced independently for this
registration:*

| group | n | `hip_flexion_LmR` range |
|---|---|---|
| **completers** (`t_end` = 20.000 s) | 46 | **−0.8443 … +1.1824** |
| **fallers** | 10 | **−4.4908 … −1.2099** |
| | | **disjoint by +0.3656°** |

⛔ **So a completing spastic cell lands in one of two places and both are informative.** *Inside the
completer range → the shipped discriminator does not separate lesion type once duration is matched.
Below −1.2099 → it does separate, and the fall explanation is refuted for that cell. **Either way this
is a measurement the corpus has never been able to make**, because until now no spastic cell completed.*
⚠ *This is a deposited secondary, not the confirmatory endpoint, and it is not promoted afterwards.*

## 6. ⭐ Provenance, stated plainly

**This arm was conceived AFTER `BANDFILL_RESULT_r286.json` returned rung 1.** *Its value is not that
nobody knew anything when it was designed — it is that **its endpoint, its admission rule and its
predicted direction are fixed in this document before any of its cells exist**, which is the same
licence `PREREG_bandfill_r287.md` has and the same one r229 lost.*
⛔ **It does not make r277, r279, r280, r282, r284 or r288 confirmatory. Those remain post-hoc whatever
this returns.**

## 7. ⛔ The cost of matching, and why a null is as informative as a positive

**Reaching 20.000 s requires the reflex 4–8× weaker than the shipped KV 0.050.**

⭐ **So if the type signature exists only at severities that make the model fall, the discriminator is
clinically useless — a patient who falls is already identifiable without gait analysis.** ⛔ **A null
here is therefore as informative as a positive, and is reported at equal strength.** *The result "the
knee separates lesion type only when the model is collapsing" is a finding about what predictive gait
simulation can identify, and it generalises past this corpus.*

## 8. The ladder — four rungs, first match wins, per KV

| # | rung | criterion |
|---|---|---|
| 1 | ⛔ **UNINFORMATIVE** | fewer than 3 spastic cells reach `t_end` = 20.000 s at this KV |
| 2 | ⭐ **DISJOINT-AS-PREDICTED** | completing spastic all negative, completing weakness all positive, ranges disjoint |
| 3 | ⛔ **DISJOINT-OPPOSITE** | disjoint, signs the other way round |
| 4 | ⛔ **OVERLAP** | ranges overlap |

*Exhaustive: fewer than 3 completers, or the ranges overlap, or they are disjoint one way or the other.*
**Null, if disjoint: exhaustive permutation over the completing cells, count reported as a floor and
never as a p-value.**

## 9. Operational

- ⛔ **RUN YIELD, BINDING ON BOTH ARMS: if the user's own SCONE work needs cores, OUR cells give way —
  r287 and r289 alike.** *Never the 112 protected directories, never an existing cell.*
- **Writes only new directories under `SCONE\results`.**
- **Terminal objective, generation-0 value, final-ten-generation descent, `fitness_progress` and the
  full `history.txt` deposited per cell, treated as a DEPENDENT VARIABLE.** ⛔ *No analysis conditions
  on it.*
- **Net pelvis yaw per cycle deposited per cell**, never used to include, exclude or stratify.
- **Duplicate-directory guard**: `>= 91` history lines with a uniqueness assertion.
- ⛔ **No endpoint is computed on this arm until this arm has stopped.**

## 10. What this arm cannot do

- ⛔ **It does not separate ADD from REMOVE.**
- ⛔ **It does not test the shipped KV 0.050 lesion.** *It tests a reflex 4–8× weaker, and a null may
  mean the signature exists at 0.050 and not at 0.0125. §7 states why that is itself the finding.*
- ⚠ **It does not make the post-hoc findings confirmatory.**
- ⛔ **One model, one body, six optimiser seeds per gain. Nothing here becomes a statement about people.**
