# PREREG_3d_ladder_r169.md — the re-optimised 3D DOSE LADDER

**Round 169, 2026-08-10.** *Hashed before a single scenario file exists. Where this document and any
script disagree, **THIS DOCUMENT DECIDES**. It is never edited; defects go to an errata.*

**Parent:** `PREREG_3d_reopt_r151.md`, sha256 `f6a65408731cc714…` — **byte-identical on disk this
round.** *Its §3 Gate G, §5 falsifiers and §6 caveats carry over verbatim except where §6 below states
a reason.* **Prior round:** `PREREG_3d_residual_r168.md`, sha256 `e2437a0f5d49da9e…`, whose §4 gate
defect (`ERRATA_residual_gate_r168.md`) this design exists to make un-repeatable.

---

## 0. ⛔ DESIGN INPUT — measured from EXISTING r151 data, read-only, before the levels were chosen

*Disclosed as prior data used to choose levels. No new simulation. Choosing levels from prior data is
what a registration is for; choosing them after the NEW data exists is what this document forbids.*

**`ank_hs_LmR` — the equinus axis the ladder must make overlap (degrees):**

| arm | KV | `tib_ant_l` | mean | range | spread |
|---|---|---|---|---|---|
| **C control** | 0 | ×1.00 | **−3.009** | [−3.209, −2.832] | 0.377 |
| **S spastic** | 0.050 | ×1.00 | **−3.233** | [−3.813, −2.441] | 1.372 |
| **W weak** | 0 | ×0.80 | **−5.457** | [−5.777, −4.900] | 0.878 |

⛔ **SPASTICITY AT THE REGISTERED 2D MAGNITUDE IS AT CONTROL ON THIS AXIS.** *Shift from control
0.224°, against a control between-seed spread of 0.377°. **The disjointness r168 reported is not the
two mechanisms being far apart — it is weakness being far from BOTH, with spasticity indistinguishable
from control.** r168 §2 read that gap as a positivity failure. It is that, and it is also this.*

**And the two surviving endpoints are each a ONE-SIDED detector — never previously stated:**

| channel | C mean | C range | S mean | W mean |
|---|---|---|---|---|
| **`ankle_angle_LmR`** | −0.173 | **[−0.515, +0.058]** | **−0.179** ⛔ *at control* | **+2.308** |
| **`hip_flexion_LmR`** | +0.003 | **[−0.367, +0.290]** | **−2.029** | **+0.417** ⚠ *just outside control* |

⛔ **`ankle_angle_LmR` detects WEAKNESS and is blind to spasticity. `hip_flexion_LmR` detects
SPASTICITY and is nearly blind to weakness. Neither detects both, and `ank_hs_LmR` is a third
weakness-only detector.** *The r151 "perfect separations" are each one arm moving while the other sits
on the control value. That is a **double dissociation**, and it is a far stronger and far more
falsifiable claim than "the endpoints separate" — which is why §4 registers it as a co-primary.*

**The control bands are FIXED HERE, from existing data, before any new cell exists:**
**`ankle_angle_LmR` ∈ [−0.515, +0.058]** and **`hip_flexion_LmR` ∈ [−0.367, +0.290]**.

---

## 1. The prediction, written down before running — this is the part that can be wrong

**Linear extrapolation through the control anchor, one point per mechanism:**

| | slope | predicted `ank_hs_LmR` |
|---|---|---|
| spastic | **−4.48 °/KV** | KV 0.150 → **−3.68**; KV 0.400 → **−4.80** |
| weak | **−12.24 ° per unit of (1 − scale)** | ×0.95 → **−3.62**; ×0.90 → **−4.23** |

⭐ **PREDICTED CROSSING: the spastic ladder spans ≈ [−4.80, −3.23] and the weak ladder ≈ [−5.46,
−3.62]; they interleave over ≈ [−4.80, −3.62], which should contain 2 rungs of each mechanism.**

⛔ **THE HONEST WEAKNESS OF THIS PREDICTION, STATED NOW.** *The spastic slope is estimated from a
0.224° shift that is **smaller than the control between-seed spread of 0.377°**. It is a slope fitted
through noise. **The predicted KV levels are uncertain by at least a factor of two in either
direction**, and if the true spastic response is flat, no KV in a survivable range will reach the weak
ladder. That is a registered possible outcome, not a surprise to be explained afterwards.*

---

## 2. Levels — FIXED. No level may be added after seeing the data.

| mechanism | levels | cells |
|---|---|---|
| **spastic** | `KV` ∈ **{0.050, 0.150, 0.400}**, `soleus`+`gastroc`, `legs = left`, `allow_neg_V = 0` | 3 × 6 |
| **weak** | `tib_ant_l max_isometric_force` × **{0.80, 0.90, 0.95}** of 1759.0 | 3 × 6 |
| **control** | KV 0, ×1.00 | 1 × 6 |

**Seeds 101–106 at every rung**, warm-started from the same converged benchmark par,
`max_generations = 90` — identical to `PREREG_3d_reopt_r151.md` §2.

⭐ **REUSE, BY CONSTRUCTION IDENTITY AND ONLY IF VERIFIED.** *The r151 C, S(KV 0.050) and W(×0.80)
arms ARE this ladder's control, spastic rung 1 and weak rung 1 — same template, same seeds, same
generation cap, same warm start, same builder. **The build script must verify this byte-wise**: each
reused `config.scone` must be identical to the newly generated one for that rung, and each reused
`.hfd` identical to the new one. ⛔ **If any comparison fails, the rung is REBUILT AND RE-RUN, not
excused.** *This is a verification, not an assumption — `PREREG_3d_reopt_r151.md` §6's ban on pooling
covers evaluations with re-optimisations, which these are not; the ban that matters here is against
pooling things merely believed to be the same.*

⛔ **IF THE LADDERS STILL DO NOT OVERLAP, THAT IS THE RESULT AND THE DESIGN SAYS SO NOW.** *No level
is added, no KV is raised, no scale is nudged. **Adding levels until overlap appears is titration, and
`PREREG_3d_reopt_r151.md` §3 forbids it.** The registered outcome is `NO CROSSING`, and its meaning is
in §5.*

---

## 3. ⭐ The overlap-mass gate — k is fixed HERE, before the data exists

*This is the clause `ERRATA_residual_gate_r168.md` exists because of. r168 §4 tested RANGE overlap and
passed `cycle_time` on a 0.0022 s sliver holding 1 of 6 seeds per arm.*

**MATCHED REGION** on `ank_hs_LmR` = `[max(min_spastic, min_weak), min(max_spastic, max_weak)]` over
all admitted rungs, per-seed values.

⭐ **k = 6 SEEDS FROM EACH MECHANISM must lie inside it.**

**Why 6, and why it is not a preference.** ⛔ *`PREREG_3d_residual_r168.md` §2 measured that at 5 v 5
a ×13 correction is **unreachable at any AUC**, and this project's registered pool is 13. **6 v 6 is
therefore the smallest matched region from which this project's own correction can produce a
declarable result at all.** k = 6 is the arithmetic minimum for the region to be usable, derived from
an already-registered number. k = 2 — the value the errata names as what would have failed r168 — is
the floor of legitimacy, not a target.*

| gate | consequence, registered now |
|---|---|
| **≥ 6 from each** | the matched region is usable; §5 secondary runs on it |
| **< 6 from either** | ⛔ **`INSUFFICIENT MASS`.** *No matched-equinus contrast is computed and **no number from one is reported** — reporting it would repeat r168's defect knowingly.* §4 primary still stands: it does not need the region. |

---

## 4. PRIMARY — two criteria, equal weight, neither of them "does it separate"

**Channels: `ankle_angle_LmR` and `hip_flexion_LmR`. THESE TWO ONLY** — the pair that cleared ×16 at
r151. ⛔ **`ank_hs_LmR` is a COVARIATE. It may not become an endpoint here because it separated at
r151; that is exactly the post-hoc promotion R45-S forbids and how the fifth feature died.**

### 4a. SIGN CONSERVATION

**At every admitted rung, the arm mean of each channel. Spastic was −, weak was + at r151.**

| branch | reading, registered with equal weight |
|---|---|
| **CONSERVED** — same sign at all 3 spastic rungs, same sign at all 3 weak rungs, opposite between mechanisms | ⭐ **direction is a property of the MECHANISM, not of a magnitude** |
| **FLIPS or the arms CROSS** as severity varies | ⛔ **the r151 separation was a property of those two particular magnitudes** and does not generalise |

### 4b. DOUBLE DISSOCIATION — the sharper form, available because of §0

**Using the control bands fixed in §0:**

| branch | reading |
|---|---|
| **HELD** — `hip_flexion_LmR` leaves the band across the KV rungs and stays inside it across every weakness rung, AND `ankle_angle_LmR` does the converse | ⭐ **each channel indexes one mechanism.** *This is the strongest claim this design can make and it is falsifiable at every rung.* |
| **BROKEN** — either channel leaves its band for the mechanism it was blind to at r151 | ⛔ **the channels are severity indices, not mechanism indices** — the `PREREG_shape_r138.md` §3 reading |

⛔ **BOTH 4a AND 4b ARE PATTERN CRITERIA. NO p-VALUE ATTACHES TO EITHER AND NONE MAY BE QUOTED FOR
THEM.** *A 6-seed per-rung sign test caps at p = 0.031, and 2 channels × 6 rungs = 12 tests makes ×12
unreachable. Manufacturing a significance test that cannot reach its own bar is the pattern-artifact
class. These are stated as patterns and read as patterns.*

---

## 5. SECONDARY, and the outcome that would make this whole design self-defeating

**SECONDARY (only if §3 passes): within the matched region, spastic vs weak on the two channels,
exact two-sided Mann–Whitney, Bonferroni ×2 (two channels, fixed here).** *§2 of
`PREREG_3d_residual_r168.md` governs the floor: at 6 v 6 under ×2 the smallest declarable
|AUC − 0.5| is **0.4167**, and a result below it is UNRESOLVED, never "destroyed."*

⛔ **REACHED-BUT-EMPTY — registered now because it is the likeliest way this design fails.**
*§0 measures that weakness moves the equinus axis and spasticity does not. **The ladders may therefore
meet only where the weakness rung is so mild that its primary-channel means lie inside the §0 control
bands** — i.e. matched equinus achieved by making the weakness disappear.*

| | fires when | meaning |
|---|---|---|
| **REACHED-BUT-EMPTY** | §3 passes, but every weak rung inside the matched region has BOTH channel means within its §0 control band | ⛔ **the overlap was bought by abolishing the contrast. The secondary buys nothing and IS NOT REPORTED AS A NULL.** |
| **NO CROSSING** | §3 returns `INSUFFICIENT MASS` | ⛔ **at survivable magnitudes these two lesions do not produce a common equinus presentation in this model.** *A real result about the model, and it closes the matched-presentation question for this design rather than leaving it open.* |

---

## 6. Carried over from `PREREG_3d_reopt_r151.md`, verbatim and non-negotiable

- ⚠ ***"Seeds are OPTIMISER RESTARTS, NOT SUBJECTS… No sensitivity, specificity or patient-level AUC
  may be quoted from this study."*** *(§4.)* **That governs every rung of this ladder.**
- **Gate G (§3), unchanged:** *a rung is ADMITTED iff ≥ 4 of its 6 seeds each reach ≥ 9.73 s and ≥ 5
  GRF cycles after settle.* ⛔ **A rung failing Gate G is DROPPED and REPORTED AS DROPPED. It is not
  replaced by a gentler level** — that is titration, forbidden by §3 of the parent. **KV 0.400 is 8×
  the magnitude that floored an un-adapted model at 3.87 s in P3D-2; its failure is a live and
  registered possibility.**
- **§5 falsifiers carry: FG** (rung void, not negative), **FC** (control fails ⇒ nothing interpretable).
- ⛔ **§6's ban stands: no result from P3D-2 or P3D-3 may be pooled with anything here.**
- ⛔ **§6's out-of-plane caveat stands** where any channel is trunk-adjacent.
- ⚠ **`PREREG_shape_r138.md` §3, verbatim:** *"the intact limb compensates, so it is not a clean
  control… A C-route positive is therefore consistent with 'asymmetry tracks impairment severity' as
  well as with a reflex, and the design cannot separate those."*
  ⭐ **A LADDER IS THE FIRST DESIGN IN THIS PROJECT WITH ANY PURCHASE ON THAT CONFOUND, and §4b is the
  purchase:** *if asymmetry merely tracked severity, both channels would move with both mechanisms and
  the dissociation would break. **This is the strongest thing this design can claim, and it is still
  not a clinical claim.***

---

## 7. Cost — computed from the measured log, not guessed

*Source: `scone/probe3d_r141/reopt_r151/run_log.json` — **17 runs, 1346.8 s wall-clock at concurrency
2**; per-cell CPU min 104.2 s, median 134.5 s, mean 155.6 s, max 215.1 s; **79.2 s wall-clock per cell
at concurrency 2.***

| | count |
|---|---|
| ladder cells total | 6 rungs × 6 seeds + 6 control = **42** |
| **already on disk and reusable** (control, KV 0.050, ×0.80) | **18** |
| ⭐ **NEW CELLS TO RUN** | ⭐ **24** |

⭐ **PREDICTED WALL-CLOCK: 24 × 79.2 s ≈ 1901 s ≈ 32 min at concurrency 2.**
⚠ *Uncertainty is one-sided-ish and stated now: cells that FALL finish early, so a Gate-G-failing KV
0.400 rung would come in **under** estimate; cells that survive longer per generation could push it to
~45 min. **If it exceeds 60 min it is reported as exceeding this registration's estimate**, not
silently absorbed.*

**Machine, measured this round: 16 cores / 32 logical, load 5 %, 16.1 GB free, `sconecmd` 0.**
⛔ **Concurrency 2 — the project's standing convention — is 2 of 16 cores and is not raised.**

---

## 8. Operational constraints — unrelaxed

⛔ **Writes confined to `Desktop\spasticity_paper\`.** *SCONE writes its own results under
`Documents\SCONE\results\` as it always has; **the 112 protected directories matching
`^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L` and `opt_s1*`–`opt_s4*` are never read-modified, moved or deleted,
and on ANY resource conflict OUR cells yield.***

⛔ **Progress is counted from `history.txt` LINE COUNTS and from `.par`/`.sto` filenames and mtimes.
NEVER from `LAUNCH_STATUS.json`** — *that file reports healthy after the process writing it has died,
and it has cost this project three times.* **A cell is complete iff its `history.txt` has ≥ 91 lines**
— the same test `run_reopt_r151.py` uses, and the same one that survives SCONE's `" (1)"` duplicate-
directory behaviour.

⛔ **No `--run`. No `--launch`.** *Those flags belong to the registered 2D slope launchers and are not
used here. This ladder runs through a new script on `sconecmd -o <scenario> -q`, the same call
`run_reopt_r151.py` makes.* **`sto_utils.py`, `residual_test.py`, `gen_seeds.py` and every other
registered script are imported UNMODIFIED.**

⛔ **The verdict is not reported until the cells exist.**
