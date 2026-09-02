# PREREG_3d_matched_r174.md — the SEVERITY-MATCHED comparison

**Round 174, 2026-08-10.** *Hashed before a single scenario file exists. Where this document and any
script disagree, **THIS DOCUMENT DECIDES**. Never edited; defects go to an errata.*

**Parents:** `PREREG_3d_reopt_r151.md` `f6a65408…`, `PREREG_3d_ladder_r169.md` `e3ec76aa…`,
`PREREG_3d_continuation_r172.md` `35ac02b4…` — all byte-identical on disk this round.
**Motivation:** `STANDING_OBSERVATIONS.md` **SO-10** — *the two arms have never been placed on a common
severity scale, and every discrimination claim this project has made presupposes they are.*

---

## 1. ⛔ THE METRIC IS THE EXPERIMENT

### 1a. The causal argument that disqualifies every gait-derived metric

**Let L = lesion, Z = optimiser seed/basin, G = achieved gait, F = fitness, Y = endpoint.**
**Structure: L → G, Z → G, G → F, G → Y.**

⛔ **Fitness, gait duration, speed and metabolic cost are ALL CHILDREN OF G. Matching on any of them
partially conditions on G, and conditioning on G blocks the path L → G → Y that this experiment
exists to measure.** *That is "matching away the answer" in its general form. **It is not a caveat
about one candidate; it disqualifies the whole family**, including the fitness candidate SO-10 itself
proposed (`S050` 61.3, a `W080` seed at 61.2).*

⚠ **The collider objection is therefore not merely a limitation here — for gait-derived metrics it is
fatal, and it is fatal for the same reason the 2D cost-matching analysis was retracted.**

**Also disqualified, individually:**

| candidate | why it may never be the matching metric |
|---|---|
| `ankle_angle_LmR`, `hip_flexion_LmR` | ⛔ **they are the ENDPOINTS** |
| `ank_hs_LmR` | ⛔ **r168 measured it at AUC 1.0000 against the label — matching on a perfect label-separator is matching on the arm** |
| gait duration | ⛔ child of G, **and censored at the 20.00 s cap on every admitted non-spastic cell (r172)** |
| best-`par` fitness | ⛔ child of G |

### 1b. ⭐ The registered metric: UPSTREAM LESION DOSE on a fixed reference trajectory

**Both lesions are expressed as newtons of muscle force added or removed, evaluated on the CONTROL
arm's own gait — one fixed reference trajectory, identical in construction for both arms.**

**Weak dose(s)** = mean over cycles of `(1 − s) × tib_ant_l` force actually used on the reference gait.
**Spastic dose(KV)** = mean over cycles of `KV × max(0, ce_vel_norm) × max_isometric_force`, summed
over `soleus_l` and `gastroc_l`, with added excitation clipped to `≤ 1 − excitation_ref`.

⭐ **It is upstream of G for both arms**, because it is a property of the lesion applied to a
trajectory that neither lesion produced. **Conditioning on it does not condition on G.**

### 1c. ⛔ Its defects, registered in the same breath

1. ⛔ **Moment arms are ignored.** *Plantarflexors and `tib_ant` act about the ankle with different
   moment arms and opposite sign. **Matching muscle-force magnitude is NOT matching ankle torque**, and
   this metric asserts the former. It is a dose, not a moment.*
2. ⛔ **It is first-order and open-loop.** *The reflex's true input is the LESIONED gait's fiber
   velocity, not the control gait's. The metric deliberately refuses that, because using the lesioned
   gait would make it a child of G again.* ⚠ **So it is exact as a specification of the perturbation
   applied and approximate as a description of the perturbation experienced.**
3. ⚠ **`ce_vel_norm > 0` is assumed to mean lengthening** (the stretch-reflex input, consistent with
   `allow_neg_V = 0`). *Measured on control: positive for 33 % of samples on `soleus_l` and 43 % on
   `gastroc_l`, which is consistent with stance dorsiflexion and not with a sign error.*
4. ⚠ **Excitation clipping is applied**; without it the dose would overstate what the model can deliver.

⛔ **These are stated now so that no result below may be read as a torque-matched comparison. It is a
force-dose-matched comparison, and that is a weaker and honest claim.**

---

## 2. ⚠ Design input, measured from CONTROL CELLS ONLY, before the levels were chosen

*Disclosed as prior data used to choose levels — the same disclosure r169 §0 made.*

| | value |
|---|---|
| `tib_ant_l` mean force on the control gait | **125.853 N** |
| **spastic dose at KV 0.050** | ⭐ **13.627 N** *(seed range 13.582–13.673)* |
| ⭐ **MATCHING SCALE s\*** | ⭐ **0.8917** → `max_isometric_force` **1568.5 N** |

⛔ **A UNITS ERROR IN THIS SEAT'S OWN DOSE SCRIPT, DISCLOSED: the first version read `tib_ant_l.F` as
newtons and returned 0.072 N for a 1759 N muscle, giving s\* = −189.45.** *`<muscle>.F` is
**identical to `<muscle>.mtu_force_norm`** — force NORMALISED by `max_isometric_force`. **This is the
r145 radians-as-degrees class**, caught because a negative scale is impossible. The corrected reading
is annotated in `dose_r174.py`.*

⚠ **Note what the correction did to the direction of titration.** *On the gait-derived metrics that
§1a disqualifies, spasticity is the MORE severe arm and matching would require weakness more severe
than ×0.80. **On the registered upstream metric the match is at ×0.892 — milder than ×0.80.** The
direction of titration is metric-dependent, which is SO-10.1 restated, and it is why the metric had to
be fixed before the rungs.*

---

## 3. Design — levels FIXED, none may be added after seeing the data

**Spasticity is FIXED at KV 0.050** — the only viable magnitude, established on two independent
optimisation paths (r169 from-healthy 6/6, r172 continuation 6/6 at the same setting).

| rung | `tib_ant_l` scale | dose (N) | vs spastic 13.627 N |
|---|---|---|---|
| **WM087** | ×0.870 | **16.361** | bracket ABOVE |
| ⭐ **WM892** | ⭐ **×0.892** | ⭐ **13.591** | ⭐ **THE MATCH** |
| **WM915** | ×0.915 | **10.697** | bracket BELOW |

**6 seeds (101–106) per rung. 18 new cells.**
⚠ **The two brackets exist so a result at the match cannot be a knife-edge artifact of one scale.**
⛔ **If the endpoints behave differently at ×0.892 than at both brackets, that is a finding about
knife-edge sensitivity and NOT a discrimination result.**

⛔ **No rung may be added afterwards.** *`PREREG_3d_reopt_r151.md` §3 forbids titrating and this
document forbids it again.*

---

## 4. Warm start — registered and justified against BOTH known defects

⭐ **FROM-HEALTHY, and both arms have it.**

| defect | why it does not bite here |
|---|---|
| **r169's depth confound** | *it bites when comparing rungs at DIFFERENT severities within an arm. **This design's primary compares ONE spastic point to ONE weak point, and both are from-healthy at depth 90** — depth-matched by construction.* |
| **r172's path dependence** | *avoided entirely: there is no chain.* |
| **§74's control-flow defect** | ⭐ **structurally absent — there is nothing to advance.** *And the runner is fixed anyway: see §7.* |

⛔ **The cost: the three weak rungs are at matched depth to each other and to `S050`, but a
dose–response ACROSS the three weak rungs remains uninterpretable as severity alone, because it is the
same single-path design r169 used. No within-arm dose–response may be claimed.**

---

## 5. The three branches, registered with EQUAL weight

| branch | reading |
|---|---|
| ⭐ **MATCH FOUND, ENDPOINTS SEPARATE** | **two lesions of comparable upstream dose are distinguishable on gait kinematics** — the strongest result this project can produce. ⚠ ***"Seeds are OPTIMISER RESTARTS, NOT SUBJECTS… No sensitivity, specificity or patient-level AUC may be quoted from this study."*** *Verbatim, non-negotiable.* |
| ⛔ **MATCH FOUND, ENDPOINTS DO NOT SEPARATE** | ⛔ **THE DISCRIMINATION WAS SEVERITY ALL ALONG.** *`PREREG_shape_r138.md` §3's confound is confirmed rather than excluded, and every separation this project has reported becomes a severity difference wearing a mechanism's name.* ⭐ **The cleanest negative in the project's history, and this seat does not flinch from it: it is registered here at equal weight, before the cells exist, and it will be reported in §1 of the result if it fires.** |
| ⛔ **NO MATCH EXISTS** | *fires if the matched rung fails Gate G, or if s\* falls outside the viable range.* **The model cannot pose the question — a harder limit than the ceiling.** |

⛔ **Gate G unchanged: ≥ 4 of 6 seeds each ≥ 9.73 s and ≥ 5 GRF cycles after settle.** *A rung failing
it is DROPPED, never replaced, never re-magnituded.*

**Endpoints: `ankle_angle_LmR` and `hip_flexion_LmR` ONLY**, control bands fixed at r169 §0
(`[−0.5153, +0.0581]` and `[−0.3671, +0.2900]`), exact two-sided Mann–Whitney 6 v 6, **Bonferroni ×2,
pool fixed here.** ⚠ *`PREREG_3d_residual_r168.md` §2 governs the floor: at 6 v 6 under ×2 the smallest
declarable |AUC − 0.5| is **0.4167**, and anything below it is UNRESOLVED, never "no difference".*

---

## 6. Cost — computed from the measured log

*Measured 79.2 s wall-clock per cell at concurrency 2.*
**18 new cells × 79.2 s ≈ 1426 s ≈ 24 min.**
**Reusable:** ⭐ *`R151S` (KV 0.050, from-healthy, depth 90, ADMITTED 6/6) is the spastic arm and is
NOT re-run.* ⚠ *`R169W080/W090/W095` are from-healthy depth 90 but at doses 25.2 / 12.6 / 6.3 N —
**none is at s\***, so they are context, not the comparison.* ⛔ **Concurrency 2. Not raised.**

---

## 7. Operational — including the §74 runner fix

⛔ **THE RUNNER ADVANCES AND REPORTS ON GATE G, NOT ON GENERATION COUNT.** *§74's root cause was
`run_continuation_r172.py` treating 90 generations as viability. **This design has no chain, so the
defect is structurally absent — and the runner still evaluates Gate G before reporting any cell as
usable, so completion is never printed as survival.***

⛔ **Complete iff `history.txt` ≥ 91 lines AND the tag resolves to exactly ONE such directory**
*(the r170 killed-cell hazard).* ⛔ **Progress from `history.txt` line counts and mtimes only —
`LAUNCH_STATUS.json` is never read.**
⛔ **Calibration gate first: the reused `R151S` cells must reproduce r169's endpoints to 1 × 10⁻⁹ on
ALL THREE channels including `ank_hs_LmR`** — *r169 checked two of three and the unchecked one was the
channel its gate ran on.* **If it fails, nothing is reported.**
⛔ **Writes confined to `Desktop\spasticity_paper\`; the 112 protected directories are untouchable and
our cells yield.** ⛔ **No `--run`, no `--launch`. Registered scripts imported UNMODIFIED.**
⛔ **The verdict is not reported until the cells exist.**
