# PRE-REGISTRATION — Equinus dose–response against TRUE injected reflex gain KV at verified 1.0x delivery

**Status:** written before any data for this experiment exists. Nothing below may be revised after
the first cell is launched. Deviations are reported as deviations, in the results, with reasons.

**Author's position:** independent experimental designer. I have read only code, scenario files,
`.sto`/`.par`/`history.txt` raw output, and script logs. I have not read `COUNCIL_*.md`,
`WATCHDOG.md`, `RESULT_*.md`, `RETRACTION_*.md`, or `KV_RELABELLING_NOTE.md`. Every quantitative
claim below that is attributed to the archive was recomputed by me from raw files, not taken from
any summary. Scripts I used are in
`C:\Users\maurice\AppData\Local\Temp\claude\C--Users-maurice-Desktop-robotic-research\18345f77-cae2-4f19-8c12-3bc1459ace70\scratchpad\`
(`probe.py`, `copies.py`, `sat.py`, `satscale.py`, `seeds.py`, `primary.py`, `gate2.py`).

---

## 0. What I verified myself before writing this

These are measurements, not citations. They constrain every choice below.

### 0.1 The 2x history is real, and I can see it in the raw `.sto`

For a `MuscleReflex` the muscle's `input` channel is the sum of its reflex contributions. For
`gastroc_l` there is exactly one force term (`gastroc_l.RF`) and one velocity term
(`gastroc_l.RV`) and no cross-muscle term, so

```
copies  =  integral | input - RF |  /  integral | RV |
```

is a direct, config-free instance count. Measured:

| run | file | declared KV | measured `copies` (gastroc_l) |
|---|---|---|---|
| `SPAS005.H0914M.GH2010.R4.S10W.D10.I` | `0074_1.026_0.814.par.sto` | 0.050 | **2.0000** |
| `SPAS01.H0914M.GH2010.R4.S10W.D10.I` | `0079_8.322_1.138.par.sto` | 0.100 | **2.0000** |
| `GATE2.H0914M.GH2010.S10W.D10.I` (post-fix) | `0000_89.606_22.581.par.sto` | 0.100 | **1.0000** |

`soleus_l` gives 2.12 / 2.01 / 1.07 on the same statistic because it additionally carries
`tib_ant_l-soleus_l.RF`, which contaminates the residual. **gastroc_l is the clean channel and is
the one this pre-registration gates on.**

Right leg was never driven, in any of the three: `gastroc_r` residual = **0.00000** exactly;
`soleus_r` residual ≤ 0.018. The old bug doubled onto the LEFT, it did not go bilateral.

Corroborating arithmetic: generation-0 fitness (frozen healthy warm-start, no adaptation) is a
function of *delivered* gain only —
`SPAS005` declared 0.050 at 2x → **22.887**; `GATE2` declared 0.100 at 1x → **22.581**.
Same delivered gain, same cost. `SPAS01` declared 0.100 at 2x (delivered 0.200) → **75.105**.

**Therefore: every archived spastic label is halved-into-truth by doubling it.**
`SPAS005` = TRUE KV 0.10. `SPAS01` = TRUE KV 0.20. `SPAS02` = TRUE KV 0.40.
`scone_naive_ladder.json` (frozen controller) declared 0.04/0.03/0.02/0.01/0.005 = TRUE
0.08/0.06/0.04/0.02/0.010.

### 0.2 Saturation: the muscle excitation clamp is already binding, at every gain, before any injection

`sat.py` / `satscale.py`, computed on the archived `.sto`:

| run | muscle | `frac(t)` with `input > 1.0` | `input` max | share of delivered reflex drive discarded by the [0,1] clamp |
|---|---|---|---|---|
| SPAS005 (true 0.10) | `soleus_l` | 0.000 | 0.848 | 0.000 |
| SPAS005 | `gastroc_l` | **0.420** | 2.206 | **0.112** |
| SPAS005 | `gastroc_r` (**no injection**) | **0.363** | 2.260 | — |
| SPAS01 (true 0.20) | `soleus_l` | 0.005 | 1.383 | 0.012 |
| SPAS01 | `gastroc_l` | **0.409** | 1.790 | **0.080** |
| SPAS01 | `gastroc_r` (**no injection**) | **0.366** | 2.113 | — |
| GATE2 (true 0.10, gen 0) | `gastroc_l` | **0.423** | 2.003 | — |

The un-injected right gastrocnemius is clipped 36% of the time with a command peaking at 2.26.
**Gastrocnemius saturation is a property of the optimized healthy Geyer–Herr controller, not of the
lesion, and it is present at generation 0.**

Frozen-kinematics extrapolation (scale only the injected gain, hold the gait fixed) —
share of commanded reflex drive that actually reaches the muscle:

| TRUE KV | 0.01 | 0.05 | 0.10 | 0.20 | 0.30 | 0.40 | 1.00 |
|---|---|---|---|---|---|---|---|
| `soleus_l` (from SPAS005) | 1.000 | 1.000 | 1.000 | 0.984 | 0.968 | 0.956 | 0.893 |
| `gastroc_l` (from SPAS005) | 0.888 | 0.888 | 0.888 | 0.888 | 0.881 | 0.873 | 0.724 |

Consequences that the design must absorb:

1. There is **no saturation *onset*** for gastroc — there is a **constant ~11% loss floor at every
   gain including the smallest**, because the baseline command already sits above the clamp.
2. Soleus has full headroom to TRUE KV ≈ 0.15 and only loses 4.4% by 0.40. **Soleus carries the
   dose-response; gastroc is partially inert throughout.**
3. Equal KV increments are therefore **not** equal delivered-drive increments. KV remains the
   registered dose axis because it is the manipulated variable, but the delivered post-clamp
   impulse is a mandatory co-reported axis (§9).

### 0.3 Seed-to-seed spread, recomputed by me from `.sto`

`seeds.py` / `primary.py`. θ_st,L = mean left ankle angle over GRF-defined stance, degrees,
plantarflexion negative.

| group | true KV | n | θ_st,L mean | **sd** | spread | (L−R) mean | (L−R) sd |
|---|---|---|---|---|---|---|---|
| `HEALTHY_s1..s4` | 0 | 4 | −1.568 | **0.748** | 1.754 | −0.238 | 0.573 |
| `DHEALTHY_s1..s3` | 0 | 3 | −0.505 | **0.295** | 0.589 | −0.879 | 1.476 |
| `PAR60_s1..s4` | 0 (weakness arm) | 4 | −4.803 | **0.472** | 1.074 | −4.258 | 0.481 |
| `SPAS005*` | **0.10** | 4 | −2.459 | **3.565** | **7.877** | −7.010 | 1.978 |
| `SPAS01*` | **0.20** | 4 | −8.663 | **3.214** | **7.182** | −10.934 | 1.910 |

Per-seed values at true KV 0.10: **+1.643, −0.754, −4.492, −6.234**. That 7.9° spread within one
condition is larger than the 3.8° MDC floor and larger than the between-rung effect. **This is the
binding design constraint.** The weakness arm and the healthy cells are 5–10× tighter; the spastic
arm is where the variance lives.

### 0.4 There was never a stopping rule

`history.txt` for `SPAS005` ends at generation 69, but `.par` files continue to generation 74 and
the run's last file is timestamped 19 minutes after the last history flush. `SPAS005_s2` reached
generation **319** and was still improving (`fitness_progress` 0.00076/gen). Archived depths:
gen 74, 320, 59, 71 (KV 0.10) and 79, 279, 329, 99 (KV 0.20). **These runs were killed by hand, at
different depths, in the middle of the axis being measured.** Best fitness by ceiling:

| run | gen ≤ 100 | gen ≤ 250 | final | excess of gen≤100 over final | excess of gen≤250 over final |
|---|---|---|---|---|---|
| `SPAS005_s2` | 0.7626 | 0.6941 | 0.6738 (g319) | **+0.089** | +0.020 |
| `SPAS01_s2` | 0.9737 | 0.8141 | 0.8042 (g279) | **+0.170** | +0.010 |
| `SPAS01_s3` | 1.0988 | 0.8154 | 0.7926 (g329) | **+0.306** | +0.023 |
| `DHEALTHY_s1` | 0.6026 | — | 0.6026 (g89) | 0.000 | — |

Healthy cells are done by generation ~75. **Spastic cells are not done at generation 100 and are
essentially done at 250.** A shared budget must be set by the slowest arm, not the fastest.

### 0.5 Viability ceiling, from archived best fitness (all at 2x, relabelled)

| tag | TRUE KV | gen-0 fitness | best fitness reached | walks? |
|---|---|---|---|---|
| `DHEALTHY_s1` | 0 | — | 0.603 | yes |
| `SPAS005` group | 0.10 | 22.89 | 0.672–0.835 | yes |
| `SPAS01` group | 0.20 | 75.11 | 0.804–1.138 | yes |
| `SPAS02` | 0.40 | 92.38 | **32.991** | **no** |
| `SPAS05` | 1.00 | 94.48 | **57.729** | **no** |
| `SPAS10` | 2.00 | — | **49.140** | **no** |
| `SPAS20` | 4.00 | — | **57.516** | **no** |

And with a **frozen** healthy controller (`scone_naive_ladder.json`, relabelled ×2): walks at
TRUE KV 0.010, falls at TRUE KV 0.020, 0.04, 0.06, 0.08.

**The entire viable adapted range is TRUE KV ∈ (0, ~0.3]. The transition is bracketed between 0.10
and 0.20.** That is where the ladder must be dense.

---

## 1. The KV ladder

**Eight rungs, in TRUE (declared = delivered, 1.0x-verified) gain:**

| rung | TRUE KV | why this value |
|---|---|---|
| R0 | **0.000** | Control and the reference for the primary endpoint. Structurally identical to every other rung (§1.1). |
| R1 | **0.050** | One √2-step below the lowest archived-and-viable gain. Establishes the flat foot of the curve. Well above the frozen-controller ceiling (0.020), so the whole ladder is in the adapted regime this study is about. |
| R2 | **0.071** | √2 spacing. |
| R3 | **0.100** | Exact reproduction of archived `SPAS005` at correct delivery. Measured there: θ_st,L = −2.459 ± 3.565°, deficit ≈ −1.9° vs healthy — **below the 3.8° MDC floor**. Lower bracket of the transition. |
| R4 | **0.141** | √2 spacing; the geometric midpoint of the bracketed transition. This rung exists solely because R3 and R5 straddle the threshold. |
| R5 | **0.200** | Exact reproduction of archived `SPAS01`. Measured: θ_st,L = −8.663 ± 3.214°, deficit ≈ −8.2° — **inside the 3.8–11.5° MDC band**. Upper bracket of the transition. |
| R6 | **0.283** | √2 spacing; the highest gain not already known to be non-viable. Tests whether equinus keeps growing or plateaus once soleus starts clipping. |
| R7 | **0.400** | Equals archived `SPAS02`'s delivered gain, which reached only fitness 32.991. Pre-declared **viability-ceiling probe**. It is expected to fail and is run under identical treatment anyway, because a ceiling asserted without running it is not a measurement. Its failures are data (§6), not exclusions. |

R1–R7 form a geometric ladder with ratio √2 (0.050 → 0.400 in six steps). The spacing was chosen
**before any new data**, from the archive facts in §0.5 and §0.3, and is documented here so it
cannot be re-chosen later.

Rungs are **not** placed logarithmically past 0.40 and **not** placed below 0.05: below 0.05 the
adapted controller absorbs the reflex and the cell is indistinguishable from R0 (archived true
0.10 already sits inside the healthy CI); above 0.40 no archived run has ever produced a gait.

### 1.1 The KV = 0 rung must contain the block

R0 must be generated **with the spastic `ConditionalController` present and `KV = 0.000`**, not
with the block omitted. Otherwise R0 differs from R1–R7 in scenario topology and in the emitted
`.sto` channel set, and the three verification instruments cannot be run identically on it.

**This requires a change to the generator.** `gen_conditions.py:121` reads `if kv > 0:` and omits
the block entirely at zero. That branch must be changed to always emit the block. Recorded here as
a required, pre-data modification; if it is not made, R0 is not a valid control and the primary
endpoint has no reference.

### 1.2 On saturation and the ladder ceiling

The brief asks whether "gain increments beyond saturation deliver nothing". Measured answer (§0.2):
**not in the way expected.** Soleus is unclipped through R5 and loses only 4.4% at R7. Gastroc
loses a *constant* ~11% at every rung including R1, because the healthy controller already
over-commands it. So no rung is wasted for saturation reasons — but the gastroc half of the
"plantarflexor spasticity" is partially inert throughout, and the KV axis is not linear in
delivered drive. This is a limitation to report (§10.4), not a reason to shorten the ladder.

---

## 2. Seeds per rung

**n = 8 CMA-ES seeds per rung. 8 rungs × 8 seeds = 64 optimizations.**

Justification, from the measured spread in §0.3. The largest within-cell sd of the primary measure
is **σ = 3.565°** (`SPAS005` group, true KV 0.10, n = 4). The reference rung R0 has σ ≈ 0.75°
(`HEALTHY_s1..s4`). The primary endpoint is a difference of two independent rung means, so its
standard error is √(σ²_cell/n + σ²_R0/n) and its CI uses Welch's t:

| n per rung | SE of Δθ | Welch df | 95% CI half-width | verdict |
|---|---|---|---|---|
| 4 | 1.821 | 3.5 | **5.63°** | useless — wider than the whole MDC floor |
| 6 | 1.487 | 5.4 | **3.79°** | sits exactly on the 3.8° threshold; the "no equinus" verdict would be decided by rounding |
| **8** | **1.288** | **7.6** | **3.03°** | **strictly inside 3.8° — adopted** |
| 12 | 1.052 | 11.4 | 2.33° | better, but 96 runs |

**n = 8 is the smallest count at which a pre-stated "no clinically recognisable equinus" verdict is
assertable at all.** At n = 6 the CI half-width (3.79°) is indistinguishable from the threshold
(3.8°), so the negative claim would be unfalsifiable in practice. That is the entire argument; it
is not a convention.

No top-up rule is registered. Adding seeds after seeing the CIs is optional stopping. If compute
forces a reduction, it must be applied **uniformly to all eight rungs**, and the "no equinus"
verdict (§5) becomes **unavailable for the whole experiment** if any surviving rung's CI half-width
exceeds 3.8°.

**Seeds are optimizer restarts of one body model. They are not subjects.** Every CI in this study
is a within-model, within-objective statement.

**Cost:** measured 3.17 min/generation (`SPAS005_s2`: gen 0 at 2026-07-25 22:02, gen 319 at
2026-07-26 14:55). At 250 generations that is 13.2 h per run, **845 core-hours total**.

---

## 3. Stopping rule and warm-start policy

### 3.1 Stopping — identical in every cell

```
max_generations = 250
min_progress    = 0            # progress-based early stop DISABLED
```

The analysed solution for a cell is its **best `.par` at generation ≤ 250**. No cell may be stopped
earlier or continued longer, for any reason.

*Why 250:* §0.4. At generation 250 the three deepest archived spastic seeds sit within
0.010–0.023 fitness of where they land by generation 280–330. At generation 100 they sit
0.089–0.306 away — an order of magnitude worse, and the size of that gap is itself
condition-dependent.

*Why `min_progress = 0`:* the template currently uses `min_progress = 1e-4`, which makes the stop
generation a function of the run's own progress trajectory. Cells that plateau early are then
measured shallower than cells that keep improving — **depth becomes a function of dose, and depth
is the axis being measured.** That is not a bias that can be corrected afterwards; it is the same
confound as the killed-by-hand depths in §0.4, formalised.

### 3.2 Warm start — identical in every cell

Every cell warm-starts from the **byte-identical** file
`C:\Users\maurice\Desktop\spasticity_paper\scone\opt2\ResultH0914Gait10.par`,
SHA256 `1179513094aa5cd48713a2242d279a77ff3492e92b75e3f67f08a686940246fd`.

Model: `H0914M_osim4.osim`, SHA256 `0877508abbb38a603f7c75446a9fdf58aeb2912a667ad9d395e7e23e44eea5f6`.
Initial state: `InitStateGait10.zml`, SHA256 `121fe25d2c2c29fa348f37fd7b2c697e72b80c86f76525fcc6aa8dbf5a62539f`.
No `.osim` is modified for any rung — this experiment has no weakness arm and the plant is constant.

**Continuation ladders are forbidden.** Warm-starting rung *k* from rung *k−1*'s solution (the
technique used in `equinus_ladder.py`, and the natural response to a rung that will not converge)
would make each cell's outcome a function of its position in the ladder rather than of its gain,
would break seed independence between adjacent rungs, and would confound "dose–response" with
"continuation-depth response". If R6 or R7 will not converge from the healthy warm start, **that
is the result** (§8), and it must not be rescued — rescuing only the hard rungs makes warm-start
depth a function of dose, which is the identical confound in a different coat.

### 3.3 Why any variation would be fatal

The dose axis and the effort axis are collinear here. Higher KV both (a) is the manipulated
variable and (b) makes the optimization problem harder, so it costs more generations and starts
further from any solution. **Any policy that lets a hard cell run longer, restart, or inherit a
better initial point maps directly onto the dose axis.** A dose–response curve produced under such
a policy is a plot of "how much optimizer help each gain received", and no amount of post-hoc
matching recovers the intended quantity — §0.4 is the demonstration: the archive's seed spread at
one gain is 7.9°, and its depths span generation 59 to 320, and the two cannot be disentangled
after the fact.

---

## 4. The primary phenotype measure — exactly one

### θ_st,L — mean left (affected) ankle angle over the stance phase of complete strides, in degrees, plantarflexion negative.

### Primary endpoint

```
Δθ(rung)  =  mean_over_seeds θ_st,L(rung)  −  mean_over_seeds θ_st,L(R0)
```

Δθ < 0 = equinus. Units degrees. This is the quantity the 3.8–11.5° MDC is defined on.

### Computation, fully specified — do not delegate to `sto_utils.cycle_features`

For each surviving cell, one `.sto` produced by re-simulating that cell's best `.par`
(generation ≤ 250) with `sconecmd -e` on that cell's own scenario, at the scenario's
`fixed_control_step_size = 0.005` and `integration_accuracy = 0.002`.

1. **Parse.** Header ends at the line `endheader`; the next line is tab-separated column names.
   **Assert `inDegrees=no` in the header.** Abort the cell if absent or `yes`.
2. **Ankle.** Column named **exactly** `/jointset/ankle_l/ankle_angle_l/value`. Convert with
   `np.degrees`. Abort if that exact column is absent — do not fall back to substring matching.
3. **GRF.** Column named **exactly** `leg0_l.grf_norm_y` (body-weight normalised). Threshold
   `0.05 BW`.
4. **Heel strikes.** Upward crossings of the threshold that then remain above it for ≥ **0.15 s**
   continuously; accepted crossings must be ≥ **0.30 s** apart; only crossings at **t ≥ 1.0 s**
   are kept.
5. **Cycles.** Consecutive accepted heel strikes; **drop the last cycle** (it may be truncated by a
   fall). Require **≥ 3 complete cycles** (stricter than `sto_utils`' 2).
6. **Stance mask** within each cycle: samples with `leg0_l.grf_norm_y > 0.05`. Require a non-empty
   mask in every cycle.
7. **θ per cycle** = mean ankle angle over that cycle's stance mask. **θ_st,L** = unweighted mean
   over cycles.
8. Report alongside every cell: number of cycles, mean stance fraction, `t_end`.

### Critical read of `sto_utils.py` — why the helper is used only for parsing, and what it gets wrong

`C:\Users\maurice\Desktop\spasticity_paper\scone\sto_utils.py`:

- **`cycle_features["ank_stance_mean"]` is not stance.** Line 176–177 averages over
  `ank[a : a + int(0.6*(b-a))]` — **the first 60% of the stride by sample index**, not the
  GRF-defined stance phase. Measured stance fraction across the archive ranges **0.553
  (`SPAS01`) to 0.616 (`SPAS005_s2`)**, so the proxy silently folds up to 5% of swing into
  "stance", and *how much it folds in changes with the dose*. In the archive it happens to agree
  with the correct measure to within 0.4° (§0.3, `primary.py`) — that is luck, not design, and it
  will not survive a rung where stance shortens. Same defect in `ank_swing_min` (last 40% by index).
- **`grf_vertical` returns two different thresholds** depending on which channel exists: `0.05` for
  `grf_norm_y`, `20.0 N` for `grf_y`. Those are not equivalent (0.05 BW ≈ 37 N for this model).
  Both channels are present in every `.sto` I inspected, so the first branch always wins today —
  but nothing enforces that, and a build that stopped emitting `grf_norm_y` would silently change
  the event detector mid-experiment. **This pre-registration pins the channel by exact name.**
- **`inDegrees` is never checked** (line 149 unconditionally applies `np.degrees`). A file with
  `inDegrees=yes` would be scaled by 57.3 with no error.
- **`col()` has a three-level fallback** ending in a substring match (line 63–65). Convenient,
  and exactly the mechanism by which a renamed channel produces a plausible wrong number instead
  of an exception. Not used here.
- **`load_sto` uses `np.fromstring(..., sep="\t")`**, deprecated in NumPy; on failure it silently
  drops to a per-row `float()` loop that *skips* malformed rows (line 41–46). A partially corrupt
  `.sto` therefore yields a short, valid-looking array. The registered pipeline asserts
  `data.shape[0] == nRows` from the header.
- What it gets **right** and is reused verbatim: the `endheader`-terminated parse (the note at
  line 3–6 is correct), and the `min_stance` / `min_gap` heel-strike guard (line 104–130), whose
  rationale — a scuffing foot producing two "strides" per real stride — is a real failure mode of
  exactly the pathological gaits this ladder generates. Those constants (0.15 s, 0.30 s) are
  adopted unchanged and frozen here.

### Alternatives considered and rejected — recorded so they cannot be substituted later

| candidate | measured seed sd @ true KV 0.10 | why rejected |
|---|---|---|
| `ank_min` (peak plantarflexion) | 3.876° | Single-sample extremum on a 0.01 s grid; noisier than θ_st,L and not the quantity the MDC describes. |
| `ank_hs` (angle at heel strike) | — | One sample per cycle. `verify_equinus.py`'s own docstring records that an earlier round reached the **opposite sign** on the paretic arm from this metric. Single-sample measures excluded categorically. |
| **L−R stance asymmetry** | **1.978°** (vs 3.565° for θ_st,L) | Tempting — roughly half the variance. Rejected as *primary* because **the contralateral limb is not a fixed reference**: θ_st,R moved from +5.80/+6.45/+3.82/+2.14 (true KV 0.10) to +0.85/+0.67/+5.79/+1.78 (true KV 0.20). An L−R measure attributes contralateral compensation to ipsilateral equinus, and the 3.8–11.5° MDC is defined on an ankle angle, not a between-limb difference. **Registered as the single named SECONDARY (§9); always reported; never substituted for the primary.** |
| L−R minimum ankle angle | 0.950° | Lowest variance of all — and **flat across the dose axis**: −5.660° at true KV 0.10 vs −5.647° at true KV 0.20. A measure with a 0.013° dose sensitivity and a 0.95° noise floor is a precision instrument pointed at nothing. Its inclusion here is a warning: low variance is not evidence of a good endpoint. |

---

## 5. Threshold for "no clinically recognisable equinus"

The post-stroke ankle-angle minimal detectable change in this literature is **3.8°–11.5°**. That is
a range, not a threshold, and choosing within it after seeing data would decide the result. Fixed
now:

- **NO-EQUINUS** — a rung is so classified iff the **upper (less negative) limit of the 95% Welch
  CI of Δθ is above −3.8°** *and* the point estimate is above −3.8°. i.e. the entire interval lies
  inside (−3.8°, +∞).
- **EQUINUS-POSITIVE** — iff the **upper limit of the CI is below −3.8°**. i.e. the entire interval
  lies at or beyond the MDC floor.
- **INDETERMINATE** — the CI straddles −3.8°. Reported as indeterminate. **Not rounded into either
  class**, and not resolvable by adding seeds to that rung alone.

**The floor (3.8°) is used, not the midpoint or the ceiling.** Rationale: the operative claim here
is a *negative* one ("this gain does not produce recognisable equinus"), and a negative claim must
be conservative in the direction that makes it hardest to assert. Using 11.5° would let a rung with
9° of equinus be called "no equinus", which is indefensible.

Mandatory co-reporting for every rung, positive or not: whether the point estimate also clears
**−11.5°**, i.e. whether the equinus is recognisable under the *most* conservative published MDC.
Rungs between −3.8° and −11.5° are described in the results as *"recognisable under the low end of
the published MDC range, not under the high end"* — in those exact terms, with both numbers.

*Prior expectation from the relabelled archive, recorded now so it cannot be claimed as a
prediction afterwards:* R3 (0.10) should land NO-EQUINUS or INDETERMINATE (archived deficit
≈ −1.9°); R5 (0.20) should land EQUINUS-POSITIVE (archived deficit ≈ −8.2°, inside the band but
not past 11.5°).

---

## 6. Per-cell gates, and what happens to a cell that fails one

Every gate below is run on **every** cell, including R0, before the cell's `.sto` is read for the
primary measure. **A cell whose gates have not all passed contributes nothing to any number in the
results.**

| gate | instrument | pass condition |
|---|---|---|
| **A — nothing discarded** | `check_unused.py` on the launch log | Zero `unused properties` blocks naming `SpasticL`, `MuscleReflex`, `target`, or `KV`. Also refuses `legs = opposite` / `legs = other` in the scenario. |
| **B — declared amount arrived** | `delivered_gain.py` on (`config.scone`, `.sto`) | Verdict **PASS**. `copies` within `TOL_COPIES = 1e-3` of 1.0; `|rho − 1| ≤ TOL_RHO = 0.15`; per-window IQR ≤ 0.30; fitted lag ≈ 0.020 s. **ABSTAIN is not a pass. A raised exception is not a pass.** |
| **C — arrived in the declared phases** | `state_gating.py` on (`config.scone`, `.sto`) | Verdict **PASS**. ABSTAIN is not a pass. |
| **D — independent copy count** *(added by this pre-registration)* | direct residual on `gastroc_l`: `∫|input − RF| / ∫|RV|` | **1.000 ± 0.005.** Verified by me to return **2.0000** on both archived 2x runs and **1.0000** on `GATE2`. Uses no config parsing and produces a *number* in regimes where `delivered_gain.py` raises (§ below). |
| **E — right leg untouched** | same residual on the right | `gastroc_r` residual = 0 (measured exactly 0.00000 in all three reference runs); `soleus_r` residual ≤ 0.02. |
| **F — warm start is the intended one** | SHA256 of the run directory's `ResultH0914Gait10.par` | `1179513094aa5cd48713a2242d279a77ff3492e92b75e3f67f08a686940246fd`. Same for the `.osim` and `.zml` hashes in §3.2. |
| **G — seeds are actually distinct** | scenario text + `history.txt` | The cell's scenario contains `random_seed = k` for its own k; no two cells within a rung have byte-identical `history.txt`. |
| **H — the gain is the declared gain** | archived `config.scone` | `KV` equals the rung value to 3 decimals on **both** `soleus` and `gastroc`; `allow_neg_V = 0`; `delay = 0.020`; `legs = left`; targets written **side-free**. |
| **I — depth** | `history.txt` | Contains a row at generation ≥ 249. See §7. |
| **J — measurable gait** | primary pipeline (§4) | ≥ 3 complete left cycles after t = 1.0 s, non-empty stance mask in each. |

**Gate G is not paranoia.** `gen_seeds.py` inserts the seed by string-replacing the literal
`min_progress = 1e-4`:

```python
txt = txt.replace("min_progress = 1e-4",
                  "min_progress = 1e-4\n\trandom_seed = %d" % s, 1)
```

This pre-registration sets `min_progress = 0` (§3.1). **The replacement then becomes a silent
no-op, no `random_seed` is written, and all eight "seeds" of a rung run byte-identical
optimizations** — the seed spread would read as 0.0 and the study would report fabricated
precision. The generator must be fixed before launch, and Gate G must confirm the fix on every
cell rather than on the generator.

### Failure handling

- A cell failing **any** of A–I is **re-run once from scratch with the same seed index**. If it
  fails again, it is a **permanent exclusion**.
- **Gate J is different.** A cell that passes A–I but fails J has a **non-viable gait**. This is
  **data, not an exclusion**: it means the model cannot walk at that gain. Non-viable cells are
  counted, reported per rung, and are **never re-run** — re-running until a cell walks is
  selection on the outcome.
- **No cell may be removed for any reason not on the list above.** In particular: a high fitness,
  an ugly gait, a surprising Δθ, or an outlying seed is **not** a gate failure. There is no
  outlier rule in this study.

### Exclusion reporting (mandatory table in the results)

One row per excluded or non-viable cell: rung | seed index | gate failed (A–J) | the measured value
of the failing statistic | re-run attempted (y/n) | re-run outcome | final disposition
(excluded / non-viable). Plus, next to every rung's estimate: **n surviving / 8**.

- A rung with **< 6 surviving seeds** has its CI reported but is **barred from contributing to the
  transition estimate** (§9), and that bar is stated in the results text.
- A rung with **≥ 4 of 8 non-viable** is declared **beyond the walkable ceiling** and its Δθ is not
  reported at all (a mean over the survivors of a mostly-falling condition is a survivorship
  statistic).

### A note on the `copies ∈ {0,1,2}` guardrail

`delivered_gain.py` **raises** rather than fails when `copies` lands outside 0/1/2 ± 0.15
(lines 641–648). The new scenario form's correctness rests entirely on `legs = left` being the
single source of truth for side, while an explicit `_l` suffix on a target **overrides** `legs`
(`concrete_targets` docstring, and row 4 of the four-way probe in `gen_conditions.spastic_block`:
`legs = right` + `target = soleus_l` **drives the left leg**). A future edit that reintroduces a
sided target under a `legs` scope can produce 3 or 4 copies — and Gate B would then throw, not
fail. **An exception must never be read as "no problem".** Gate D exists to produce a number in
exactly that regime.

---

## 7. Depth / convergence verification per cell

1. **Depth reached.** `history.txt` must contain generation ≥ 249. A cell whose history stops
   earlier was killed (the archive's actual failure mode, §0.4) and fails Gate I.
2. **Depth residual, per cell.** `residual = best_fitness(gen ≤ 125) − best_fitness(gen ≤ 250)`.
   Reported for every cell.
3. **Registered convergence criterion:** the **median depth residual across a rung's surviving
   seeds must be ≤ 0.10** fitness units. Calibration: for the three deepest archived spastic seeds
   the excess of best-at-gen-100 over best-at-final was 0.089 / 0.170 / 0.306, while the excess of
   best-at-gen-250 was 0.020 / 0.010 / 0.023 (§0.4).
4. **If any rung fails (3), the ENTIRE experiment is re-run at `max_generations = 500`** — all 64
   cells, not the offending rung. Extending only hard rungs makes depth a function of dose, which
   is the confound §3.3 exists to prevent.
5. **Mandatory depth-sensitivity analysis.** Recompute the *complete* primary analysis using each
   cell's best `.par` at **generation ≤ 125** instead of ≤ 250. If the transition interval (§9)
   moves by more than one rung between the two depths, the result is reported as **depth-dependent
   and no transition value is claimed**. This is a pre-registered robustness check with a
   pre-stated consequence, not an optional sensitivity appendix.
6. Report per rung: mean and range of best fitness, mean and range of generation at which the best
   `.par` was found, and the full fitness-vs-generation curves as a figure.

---

## 8. Falsification

Stated before data. Each condition has a fixed consequence.

**F1 — NO DOSE–RESPONSE.** Declared iff **both**:
   (a) the Spearman rank correlation between rung KV and per-seed Δθ (all viable seeds pooled, KV
       as the ranking variable) has a 95% seed-level bootstrap CI **containing 0**; **and**
   (b) the difference between the most-negative and least-negative viable rung means is
       **< 3.8°**.
   Both are required. Either alone is weaker evidence and is reported as such.
   *Consequence:* injected velocity-dependent reflex gain does not control equinus magnitude in
   this model at any viable gain, and the project's spastic arm does not model the clinical sign
   it claims to model.

**F2 — SPASTICITY PRODUCES NO CLINICALLY RECOGNISABLE EQUINUS AT ALL.** Declared iff every rung
   R0–R7 is classified NO-EQUINUS. *Consequence:* the clinical premise — that both mechanisms
   present with equinus and the question is which — fails on the spastic side, and no
   discrimination study built on this arm can be about mechanism.

**F3 — TRANSITION BELOW THE TESTED RANGE.** Declared iff **R1 (KV 0.050) is already
   EQUINUS-POSITIVE**. *Consequence:* the onset is not in [0.050, 0.400]; the ladder must be
   re-run downward (0.0125, 0.0177, 0.025, 0.0354) under this same protocol. The current ladder's
   transition estimate is **not** reported.

**F4 — TRANSITION ABOVE THE TESTED RANGE.** Declared iff the **highest viable rung is still
   NO-EQUINUS**. Because every rung above it is non-viable, this is not "test higher gains" — it
   is the specific, reportable finding that **no gain at which this model walks produces
   recognisable equinus**. The ladder must not be extended upward to rescue it; §0.5 already shows
   what lies above.

**F5 — NON-MONOTONE.** Declared iff any rung mean is **more than 3.8° less negative** than the mean
   of a lower rung (a reversal larger than the MDC floor). *Consequence:* the dose axis is not
   monotone; **no single transition point may be reported**; the full curve is published with the
   reversal stated.

---

## 9. Analysis plan, fixed in advance

### 9.1 Per-rung statistics

For each rung: n surviving / 8; n non-viable; mean, sd, and **Welch 95% CI of Δθ** against R0
(two independent means, unequal variances, Welch–Satterthwaite df). Classification by §5.
No between-rung hypothesis test is registered — the estimand is a threshold crossing, not a
difference. Any p-value that appears in the results is a post-hoc addition and must be labelled
as such in the sentence that reports it.

### 9.2 The transition point — identification rule, fixed here

**KV\*** is defined as the **interval between adjacent rungs** [KV_below, KV_above] such that:

- rung KV_above is **EQUINUS-POSITIVE**, and
- **every** rung below it is **NO-EQUINUS or INDETERMINATE**, and
- both rungs have ≥ 6 surviving seeds.

**Reported as an interval, never as an interpolated scalar.** The ladder has seven non-zero points
at √2 spacing; interpolating a crossing between them is not supported by eight seeds per rung.
If more than one such interval exists (possible only under F5), no transition is reported.

### 9.3 Continuous secondary estimate — one model, fixed here

Fitted **once**, to the per-seed Δθ of all viable cells, unweighted least squares:

```
Δθ(KV)  =  − A · KV^p / (KV^p + KV50^p)        A > 0,  p > 0,  KV50 > 0
```

Report **KV50** with a **2000-resample seed-level bootstrap CI** (resample seeds within rung with
replacement, refit each time). **No alternative functional form may be fitted after seeing the
data.** If this fit fails to converge or returns a boundary solution, the result is reported as
*"no continuous fit obtainable"* — it is **not** replaced by another model.

### 9.4 Registered secondary endpoint

**L−R stance asymmetry**, θ_st,L − θ_st,R, computed by the identical pipeline on
`/jointset/ankle_r/ankle_angle_r/value` and `leg1_r.grf_norm_y`. Reported for every rung with the
same CI machinery. Its role is to show whether the ipsilateral change is accompanied by
contralateral compensation. **It may not be substituted for the primary under any circumstances**,
including if it turns out to be cleaner — which, on the archive, it is (§4).

### 9.5 Mandatory second rendering of the dose axis

Because ~11% of the commanded gastrocnemius reflex drive is discarded by the excitation clamp at
**every** gain (§0.2), each cell must also report the **delivered post-clamp reflex impulse**

```
I_m  =  ∫ [ clip(B_m(t) + D_m(t), 0, 1) − clip(B_m(t), 0, 1) ] dt ,
        D_m = delivered reflex contribution,  B_m = input − D_m
```

for `soleus_l` and `gastroc_l`. The dose–response is plotted against **KV** (the registered
primary axis, because KV is the manipulated variable) **and**, as a pre-registered secondary
rendering, against **I_soleus_l + I_gastroc_l**. If the two renderings disagree about
monotonicity, both are shown and the disagreement is the headline.

### 9.6 Frozen at this point

Rung values; seed count; stopping rule; warm-start policy; primary measure and every constant in
its computation; the −3.8° threshold and its direction; the gate list and the exclusion rule; the
convergence criterion and its consequence; the falsification conditions; the transition
identification rule; the one continuous model and its bootstrap; the secondary endpoint. Nothing
in this list may be chosen or adjusted after the first cell is launched.

---

## 10. What this design CANNOT establish

1. **Nothing about discriminating spasticity from weakness.** It has one arm. It cannot say gait
   distinguishes the two causes. Its only contribution to that question is identifying which gains
   put the spastic arm inside the equinus-positive population where the question becomes askable.
2. **Nothing about patients.** Eight seeds of one planar musculoskeletal model. Seeds are optimizer
   restarts, not subjects: no anthropometric variation, no sensor noise, no 3-D motion, no
   inter-subject controller differences. Every CI is a within-model, within-objective statement.
3. **Nothing about the acute effect of a reflex.** The controller **fully re-optimizes at every
   gain**. What is measured is the equilibrium of *reflex + completely re-adapted CNS*. A flat
   dose–response under this design is ambiguous between "the reflex is weak" and "adaptation is
   strong", and this design cannot separate them. The complementary frozen-controller experiment
   cannot be run on the same range: the frozen healthy controller falls at TRUE KV ≥ 0.020, below
   the ladder's first rung.
4. **That KV is the right dose axis.** Delivery is verified at 1.0x, but ~11% of the gastroc
   command is discarded by the clamp at every gain, and the fraction rises above KV ≈ 0.3. Equal
   KV steps are not equal delivered-drive steps, and the gastrocnemius half of the injection is
   partially inert throughout. §9.5 mitigates; it does not fix.
5. **That the equinus is plantarflexor-driven** rather than a whole-gait reorganisation. All 36
   controller parameters are free to move. A more plantarflexed stance may be the cheapest way to
   walk *with* the reflex rather than a direct mechanical consequence *of* it.
6. **Generalisation across objective functions.** `GaitMeasure.min_velocity = 1.0`,
   `EffortMeasure` (Wang2012) at weight 0.1, ankle `DofMeasure` limits ±60°, `ReactionForceMeasure`
   max 1.5 BW from t = 1 s. Equinus magnitude at a given KV is a property of that objective as much
   as of the lesion.
7. **Anything about the archived 2x results.** Relabelling them (`SPAS005` → true 0.10,
   `SPAS01` → true 0.20) is arithmetically sound and I verified `copies = 2.0000` on both — but
   they were run at uncontrolled, hand-killed depths (gen 59–320) under an older scenario topology
   (block **outside** the `GaitStateController`, ungated by gait phase) and are **not**
   interchangeable with the new cells. They are used here as priors for ladder placement. They may
   never be pooled with the new data.
8. **Whether the resulting equinus range overlaps the weakness arm's.** Archived `PAR60_s*` sits at
   θ_st,L = −4.803 ± 0.472° (deficit ≈ −4.3°). If no rung's CI overlaps that, the discrimination
   study this ladder is meant to enable will have no matched population — but establishing that
   requires re-running the weakness arm under these same rules, which is a different experiment
   and is not registered here.

---

## 11. Where I think the framing given to me is itself wrong

Stated plainly, because a pre-registration that silently accepts a flawed brief is worse than none.

**11.1 "SPASTICITY = an injected unilateral velocity-dependent stretch reflex" understates a change
of intervention.** In the archived form the block sat **outside** the `GaitStateController` and was
active unconditionally. In the post-fix form (`gen_conditions.spastic_block`) it sits **inside**
`GaitStateController / ConditionalControllers` as a `ConditionalController` gated on
`states = "EarlyStance LateStance Liftoff Swing Landing"`. Same gain, different controller
topology. The 1.0x fix and the topology change arrived together, so "at 1.0x delivery" is not the
only thing that differs from the archive. R3 and R5 are therefore *not* clean replications of
`SPAS005`/`SPAS01`; they are the closest available, and the results must say so.

**11.2 The `state_gating.py` instrument is near-vacuous as the brief specifies it.** It verifies
that the injection is active in *exactly* the declared phases. The generator declares **all five**
phases. A subset test over the full set can only detect *absence* in a phase — which Gate A already
catches from SCONE's own warning, more cheaply and more certainly. **Recommendation, not
registered as part of the primary design:** run one additional calibration cell per experiment
declaring a proper subset (e.g. `states = Swing`) and verify it is measurably OFF elsewhere. Only
then does Instrument 3 carry information.

**11.3 "the guardrail currently certifies only copies near 0, 1 or 2" is a live hazard, not a
footnote.** The new form's correctness rests entirely on `legs = left`, while an explicit `_l`
suffix on a target **silently overrides** `legs` (documented in `concrete_targets`, and
demonstrated by row 4 of the generator's own four-way probe: `legs = right` + `target = soleus_l`
drives the **left** leg and is bit-identical to a left-sided run). A regression there can yield 3
or 4 copies, at which point `delivered_gain.py` **raises** instead of failing. In a batch of 64
runs an exception is very easily logged and stepped over. Gate D exists because of this.

**11.4 "equinus magnitude versus TRUE KV" presumes KV is a dose. It is a gain on a signal that is
then clipped.** Measured (§0.2): the optimized healthy Geyer–Herr controller already commands
gastrocnemius **above** the excitation clamp for 36–42% of the trial **on both legs, with no
injection at all** (`gastroc_r.input` max **2.260**). So the gastrocnemius half of the
"plantarflexor spasticity" loses ~11% of its injected drive at *every* rung including the smallest,
and the soleus is doing most of the work. **KV is not proportional to delivered drive.** I register
KV as the primary axis only because pre-registration requires the manipulated variable to be the
axis; §9.5 makes the honest axis mandatory alongside it.

**11.5 "nothing currently on disk answers that" is too strong, and the pre-registration is stronger
for saying so.** Relabelled, the archive **already brackets the transition** between true KV 0.10
(deficit ≈ −1.9°, below the 3.8° floor) and true KV 0.20 (deficit ≈ −8.2°, inside the band), and
**already bounds viability** between true 0.20 (converges to 0.80–1.14) and true 0.40 (best
32.991). A pre-registration that pretended otherwise would have picked its rungs blind. I used the
archive, the ladder is dense between 0.10 and 0.20 **because** of it, and that choice is recorded
here — before new data — so it is not available for revision afterwards. What the archive genuinely
cannot supply is a *calibrated* answer: n = 4 at heterogeneous, hand-killed depths, with a 7.9°
seed spread, at a delivery multiplier of 2.

**11.6 The three-instrument list omits the two failure modes that actually destroyed the archive's
usability.** Neither is about delivery.
   (a) **There was never a stopping rule.** Depths span generation 59–320 and the runs were killed
       by hand mid-optimization (§0.4). Delivery verification would not have caught one byte of
       this.
   (b) **The seed mechanism can silently collapse.** `gen_seeds.py` writes `random_seed` by string-
       replacing the literal `min_progress = 1e-4`. This pre-registration's own stopping rule
       (`min_progress = 0`) breaks that replacement, after which eight "seeds" are one run repeated
       and the study reports fabricated precision (§6, Gate G).
   Any future "run every instrument on every cell" policy that stops at the three named instruments
   will reproduce the archive's condition with better paperwork.

**11.7 "the MDC used in this literature is 3.8–11.5 degrees" is being asked to do a job a 3×-wide
range cannot do.** Midpoint or ceiling would change the classification of R5 (archived deficit
−8.2°) from positive to negative. I register the **floor**, for the *negative* claim only, and
require both ends to be reported for every rung (§5). Any results text that states a single MDC
without both numbers is misreporting.

**11.8 The stated clinical motivation is about a choice between two treatments, but this experiment
characterises one arm.** That is a legitimate scoping decision and I have written the design to it.
It does mean the ladder can "succeed" — a clean, monotone, well-identified transition — and still
leave the project no better off, if the resulting equinus-positive range does not overlap the
weakness arm's (archived `PAR60`: −4.803 ± 0.472°). The success criterion that actually matters to
the project is an overlap, and it cannot be evaluated until the weakness arm is re-run under these
same rules. That should be planned now, not discovered later.
