# PRE-REGISTRATION — downhill provocation of the spastic/weak margin (r58)

> ## ⛔ READ THIS FIRST — THIS IS A *COMPETING, UNMERGED* REGISTRATION, AND NOTHING HAS LAUNCHED
>
> A **concurrent session wrote and hashed `paper/PREREG_slope.md` at 2026-08-03 20:57:28**
> (sha256 `c9bb74fc8bad17161a9a6b3a6f50a3ff17178883339fd7349d8deaedd5eaf5b4`, 11477 bytes) while
> this document was being prepared. It registers a **different design for the same question**.
> That file has **not** been read into this one, **not** edited, and **not** overwritten.
>
> **This study was therefore NOT LAUNCHED.** Every pre-launch gate below passed and every scenario
> is built, but no `sconecmd` process was started. Two registrations for one question, both live,
> is precisely the provenance failure this project has catalogued; resolving it is a decision for
> the principal investigator, not for an executor. Section 12 states the conflict and section 13
> the one finding that is urgent regardless of which design wins.
>
> Filed under a distinct name so that neither registration is destroyed and both timestamps stand.

**Written 2026-08-03, before any cell of this study has been launched.** No `PG*` result directory
existed at the time of writing; gate V4 verifies that from the results tree itself, not from memory.

Hashed artifacts (sha256, computed before any launch):

| file | bytes | sha256 |
|---|---|---|
| `scone/slope_analysis.py` | 28933 | `45be4a184e994404c941858556a832d221e0318fcb53da8452555ea0212a959d` |
| `scone/gen_slope.py` | 20820 | `6d46ec618407f949f72626ee52187186e93ea0bfd1c04fa590c584b6d0120dda` |
| `paper/PREREG_slope_r58.md` | *(this file)* | see `paper/PREREG_slope_r58.sha256` |

---

## 0. Why this study exists, and what it is allowed to conclude

A 48-run level-ground crossed study (`COUNCIL_round48.md`, `crossed_endpoint.py`) separated the two
lesion arms statistically, but **the mild-severity margin never reaches the 3.8° clinical minimal
detectable change.** Recomputed on the registered angular endpoint from the existing crossed replay
corpus, on 2026-08-03, before this study was designed:

| level-ground mild margin, `ank_stance_mean`, Δ_EQ deg | value |
|---|---|
| mild spastic pooled (`DR2K050`, `DR2K075`) | **+1.99** |
| mild weak pooled (`PAR20`, `PAR40`) | **−0.32** |
| **MARGIN(0°)** | **+2.31** |
| widest single pairwise mild margin (`DR2K050` − `PAR20`) | +3.34 |
| narrowest (`DR2K075` − `PAR40`) | +1.29 |
| pooled within-condition SD (df 36) | **2.1192** |

*(The ~2.8° figure quoted in the commissioning brief is the mild margin on filtered `ank_rom`, the
crossed study's own primary. On the angular endpoint registered here the same gap is +2.31°. Both
are below 3.8°; the choice between them is one axis of the conflict in section 12.)*

Every candidate feature this project has produced has died at that gap. **This study asks one
question: does a provocation manoeuvre raise the effect size?** It is not a feature search, and
section 8 fixes in advance what a null buys so that it cannot be spun afterwards.

---

## 1. MECHANISM — the pre-registered rationale

**Downhill walking drives faster loading-phase dorsiflexion, which is exactly what a
velocity-dependent stretch reflex resists; a weak tibialis anterior is not provoked by the same
demand.** A plantarflexor stretch reflex is gated on stretch *velocity* (the Lance definition, and
the Tardieu R1/R2 logic); raising the dorsiflexion-velocity demand at loading response should
recruit it harder. A reduced `max_isometric_force` in tib_ant is a *force* deficit and is
velocity-independent — steeper ground asks the same weak muscle for the same eccentric control, so
its equinus should be roughly flat in slope.

**The two arms should therefore diverge more as slope steepens. The registered primary is a
slope × mechanism INTERACTION, not "the margin gets bigger".**

This distinction is inherited verbatim and deliberately from
`PREREGISTRATION_slope_velocity_dependence.md` (2026-07-27), which registered it for the same
reason: *a main effect — both arms offset alike at every task — is a severity/task effect and does
**not** count.* If both arms gain equinus together as the slope steepens, that is gravity acting on
a walker, and it carries no mechanism information whatsoever.

---

## 2. DESIGN

### 2.1 Uphill is dropped entirely and is not to be reintroduced

Every uphill run in this project's history carries `min_velocity = 0.8` (signature `S08W`) while
every other condition — level, downhill, and all impairment arms — carries `min_velocity = 1.0`
(`S10W`). Verified again from the archive on 2026-08-03. Uphill does not converge at 1.0 m/s in
this model. Walking speed is the single strongest determinant of walking cost in patients
(r = −0.89), so one of three task anchors differing in speed would let a **speed** effect enter the
residual slope as a **task** effect. That confound is why the uphill arm was abandoned, and
restarting it would spend compute on a permanently confounded anchor.

**Every cell in this study is `S10W` (`min_velocity = 1.0`), asserted by gate V3.**

### 2.2 Conditions, stated explicitly

Three task conditions spanning stretch-velocity demand at constant target speed:
**level 0°, downhill −2°, downhill −5°.** Slope is imposed by tilting gravity in the `.osim`;
the terrain `blueprint` property is silently ignored by `ModelOpenSim` and is not used.

Crossed with the lesion arms, **prioritising the MILD rungs, since that is where the problem is.**
The rungs are the level-ground study's own arms (`gen_conditions.CROSSED_SPASTIC` /
`CROSSED_WEAK`), re-tagged; nothing new is invented.

| code | lesion | level-ground equivalent | role |
|---|---|---|---|
| `K000` | none; the KV block present with gain `0.000` | `DR2K000` | **structural zero-gain control** |
| `K050` | plantarflexor KV = 0.050 | `DR2K050` | **mild spastic — PRIMARY** |
| `K075` | plantarflexor KV = 0.075 | `DR2K075` | **mild spastic — PRIMARY** |
| `K100` | plantarflexor KV = 0.100 | `DR2K100` | moderate spastic — SECONDARY anchor |
| `W20` | `tib_ant_l` × 0.80 (−20 %) | `PAR20` | **mild weak — PRIMARY** |
| `W40` | `tib_ant_l` × 0.60 (−40 %) | `PAR40` | **mild weak — PRIMARY** |
| `W60` | `tib_ant_l` × 0.40 (−60 %) | `PAR60` | moderate weak — SECONDARY anchor |

**THE CELL LIST, EXPLICITLY — 21 cells × 8 seeds = 168 runs:**

```
PGL0K000 PGL0K050 PGL0K075 PGL0K100 PGL0W20 PGL0W40 PGL0W60     (level,      0°)
PGD2K000 PGD2K050 PGD2K075 PGD2K100 PGD2W20 PGD2W40 PGD2W60     (downhill, −2°)
PGD5K000 PGD5K050 PGD5K075 PGD5K100 PGD5W20 PGD5W40 PGD5W60     (downhill, −5°)
```
each with seeds `_s1` … `_s8`, `random_seed = 1…8`.

**`HEALTHY` is deliberately omitted, and the reason is measured rather than assumed.** In the
existing level corpus `HEALTHY` and `DR2K000` return *bit-identical* per-seed values
(−0.505, −0.800, −0.211, −0.496). That identity is the expected signature of a correctly inert
zero-gain block: same model, same seed, same objective. Running both would buy 24 runs of nothing,
and the same argument holds at every slope because the block's inertness does not depend on
gravity. `K000` is the reference; `HEALTHY` is not re-run.

**Level ground is RE-RUN inside this study rather than imported from the existing corpus.** The
existing level cells are at the same budget and would have been reusable, but this project's worst
defects are corpus mixtures, and one launch / one budget / one seed set / one code path is worth 56
runs. The existing level corpus is used only as an *external replication check* (section 7, S4).
*(This is the second axis of the conflict in section 12: the competing registration reuses them.)*

### 2.3 One budget, no exceptions

`min_progress = 0`, `max_generations = 90` in **every** cell including the control, written by
`gen_conditions.apply_registered_stopping_rule` and **read back** (gate V1). Terminal generation
index is therefore 89 and generation 90 never exists. `min_progress = 0` makes the stopping
generation a design constant instead of a random variable that depends on the fitness landscape —
which differs by dose, and which is exactly how the class label became predictable from the
scenario's stopping rule in the archive.

Warm start is `init_file = ResultH0914Gait10.par` in **every** cell at **every** slope. No
continuation ladder is used: a warm start that differs by slope would confound the slope factor
with search depth, and the identical-budget design exists to prevent precisely that.

### 2.4 Seeds per cell: 8, justified against the level-ground within-condition SD

The level-ground study ran **n = 4** with a measured pooled within-condition SD of **2.1192°** on
this endpoint. Simulated power for the registered primary (4000 draws, one-sided α = 0.05,
condition-level, seed SD 2.1192, `sd_rung` = the unknown rung-to-rung heterogeneity):

| true β_int (°/deg) | n = 4, sd_rung 0.73 | n = 8, sd_rung 0.73 | n = 8, sd_rung 0 |
|---|---|---|---|
| 0.30 (minimum clinically meaningful) | 0.176 | 0.235 | 0.367 |
| **0.50 (predicted)** | 0.358 | **0.522** | **0.700** |
| 0.70 | 0.570 | 0.790 | 0.923 |
| 0.80 | 0.703 | 0.890 | 0.967 |
| Type-I at β_int = 0 | — | 0.028 | 0.051 |

Doubling 4 → 8 buys +0.16 power at the predicted effect; 8 → 16 would buy far less, because the
binding term is rung-to-rung heterogeneity with only two mild rungs per arm and **no number of
seeds can remove it**. Eight is where the seed term stops dominating. It also drives the
co-primary margin CI half-width to **1.53°** (2 rungs × 8 seeds = 16 observations per arm), which
is what makes MARGIN(−5°) resolvable against the 3.8° MDC at all.

**Stated plainly and in advance: this design has ~52–70 % power at the predicted β_int = 0.50 and
only ~24–37 % at the minimum clinically meaningful β_int = 0.298.** It is powered to detect an
interaction large enough to *rescue* the margin, not the smallest interaction that could exist. A
null therefore means "no interaction of the size that would matter", which is exactly the question
section 8 commits to answering, and it is not to be reported as "no interaction".

### 2.5 ⛔ THE SIGN TRAP, FOUND PRE-LAUNCH — the reason this study builds its own `.osim` files

The model walks in **+X**, measured not assumed: `DHEALTHY_s1`'s replay has pelvis_tx
0.0000 → +10.0740 over 10 s. Gravity's along-travel component therefore **aids** travel downhill:

> **downhill grade θ → `gx = +g·sin θ`, `gy = −g·cos θ`**

Every genuine downhill run in the archive agrees (`D2*`, `RD2*`, `E2*`, `SLDN2` all use
`gx = +0.342247 = +g·sin 2°`), and `uphill_ladder.make_rung` writes `gx = −g·sin θ` for uphill.

**But `opt2/H0914M_DN5.osim` carries `gx = −0.854706` and `opt2/H0914M_UP5.osim` carries
`gx = +0.854706` — the pair is sign-swapped, and copies of both sit in eleven `opt_*` directories.**
The consequence is already on disk: the archived run **`SLOPEDN5` walked 5° UPHILL** and
**`SLOPEUP5` walked 5° DOWNHILL**, each under the opposite label. Reusing `H0914M_DN5.osim` would
have produced an uphill study named downhill, and nothing downstream would have caught it — the
directory name, the tag, and the log would all have read "DN5".

This study therefore **never reuses a pre-existing slope `.osim`.** `gen_slope.set_gravity` derives
`gx`/`gy` from the grade, writes them, and reads them back; gate **V2** re-reads the gravity vector
of every scenario's `model_file` and **rejects any negative `gx`** as uphill.

---

## 3. PRIMARY ENDPOINT — fixed, and computable now

```
ank_stance_mean = sto_utils.cycle_features(sto, side="l", settle=1.0)["ank_stance_mean"]
```

Degrees; **left (lesioned) ankle**; the mean over the **GRF-defined stance samples** of each
complete heel-strike-to-heel-strike cycle beginning at or after **t = 1.0 s**, averaged over
cycles, with the last cycle dropped. Stance is the *measured* stance (vertical GRF above the same
threshold the heel-strike detector used), never a fixed fraction of the stride — the fixed-fraction
proxy's bias was itself a function of the dose.

```
Δ_EQ(run) = mean( ank_stance_mean over the SAME-SLOPE K000 control cell ) − ank_stance_mean(run)
```
**positive = more equinus.**

**Referencing to the same-slope control is load-bearing.** Walking downhill changes the ankle angle
of *any* walker; without the per-slope subtraction the "slope effect" would be dominated by that
geometric offset, which is common to both arms and carries no mechanism information. *(It is also
why this design runs a `K000` cell at every slope and the competing one does not.)*

This is the identical measure and identical convention as the level-ground registered primary.
Running this pipeline on the existing crossed corpus reproduces `COUNCIL_round48.md` §1 to four
decimals (`DR2K050` +2.5676, `DR2K075` +1.4171, `DR2K100` +2.0061, `DR2K150` +5.8054,
`DR2K200` +7.3632) — verified 2026-08-03, before launch.

**Window:** settle 1.0 s to the last complete cycle; simulation `max_duration = 10 s`.

---

## 4. PREDICTED DIRECTION AND MAGNITUDE, PER ARM PER SLOPE

Written down before the data exist. Level-ground entries are the **measured** values from the
existing corpus and are reproduced so the predictions can be *scored*, not re-derived. These
numbers are encoded in `slope_analysis.PREDICTED` and printed beside the observed values.

| condition | Δ_EQ at 0° | Δ_EQ at −2° | Δ_EQ at −5° | direction |
|---|---|---|---|---|
| `K050` mild spastic | +2.57 *(measured)* | **+3.6** | **+5.4** | rises with slope |
| `K075` mild spastic | +1.42 *(measured)* | **+2.4** | **+4.2** | rises with slope |
| `K100` moderate spastic | +2.01 *(measured)* | **+3.1** | **+5.0** | rises with slope |
| `W20` mild weak | −0.77 *(measured)* | **−0.7** | **−0.6** | approximately flat |
| `W40` mild weak | −0.13 *(measured)* | **−0.1** | **0.0** | approximately flat |
| `W60` moderate weak | +3.17 *(measured)* | **+3.3** | **+3.5** | approximately flat |

| | 0° | −2° | −5° |
|---|---|---|---|
| **MARGIN (mild spastic − mild weak)** | +2.31 *(measured)* | **+3.20** | **+4.80** |

**Predicted β_int = +0.50 °/deg of downhill grade.**
**Minimum clinically meaningful β_int = (3.8 − 2.31)/5 = +0.298 °/deg** — the smallest interaction
that would carry the mild margin to the MDC at −5°.

---

## 5. THE FALSIFIER — written as a condition that could actually occur

The registered claim is refuted if **any** of the following is observed:

- **F1 (the expected null).** β_int is not significantly positive at one-sided α = 0.05 on the
  four mild rungs. Concretely: the fitted MARGIN at −5° fails to exceed MARGIN(0°) by more than the
  fit's own noise. *This is a wholly plausible outcome — the level-ground data show mild `K075`
  producing **less** equinus than mild `K050`, so the mild end is not even monotone in dose, and a
  slope term may find nothing to amplify.*
- **F2 (reversal).** β_int is significantly **negative**: the arms *converge* as the slope steepens.
  This would occur if downhill loading recruits compensatory tib_ant activity that the weak arm
  cannot supply, driving the weak arm's equinus up faster than the spastic arm's. That is a
  physically coherent alternative and it would refute the velocity-dependence rationale outright.
- **F3 (main effect only).** Both arms gain equinus with slope by a similar amount — a significant
  `b_slope` with a null `b_int`. **This does not count as support and is explicitly not
  reinterpretable as one.** It is gravity acting on a walker.
- **F4 (feasibility).** The −5° arm does not produce gait at all (section 6.2). The manoeuvre then
  cannot be pushed past −2° at 1.0 m/s in this model, which is itself a reportable limit.

---

## 6. STOPPING RULE

### 6.1 Optimizer level
`min_progress = 0`, `max_generations = 90`, identical in all 168 cells. No cell is extended,
restarted, re-seeded, or given a different budget for any reason.

### 6.2 Study level — the −5° feasibility gate, pre-committed
A one-step −5° downhill has **never** been shown to converge in this model. The only genuine −5°
downhill run in the archive (`SLOPEUP5`, mislabelled — see §2.5) reached best fitness **73.709** at
generation 38 of 40 from this same warm start, against **0.613–0.888** for every −2° run and 0.603
for level. The risk that the −5° arm is simply a pile of falls is real and is handled in advance:

> **`PGD5K000_s1` is launched first and is the gate.** The remaining 55 −5° cells launch **only**
> if it passes the registered exclusions **E5** (≥ 2 complete GRF-delimited cycles after settle)
> and **E6** (best fitness < 3.0) — evaluated by calling the *hashed* `slope_analysis.replay`, so
> the criterion is the registered one and not a fresh judgement. The outcome is written to
> `paper/SLOPE_D5_GATE.json`.
>
> **If it fails, the −5° arm is dropped IN FULL**, the primary is refitted on the two-level slope
> factor {0°, −2°} with the registered loss of power, and "downhill provocation cannot be pushed
> beyond −2° in this model at 1.0 m/s" is reported as a finding. **No substitute grade is
> introduced** — choosing a new grade after seeing that −5° failed would be a data-dependent design
> change.

The gate cell is a legitimate registered cell and is analysed as one if it passes; it is not a
throwaway and costs no extra compute.

### 6.3 Analysis level
**One look.** No interim analysis, no peeking at any endpoint before the corpus is complete.
`slope_analysis.py` is run **once**, as hashed. **No feature may be promoted to primary after the
data are seen** (R45-S). If the primary fails, the claim is abandoned — not re-membered, not
re-filtered, not swapped for a secondary. A cell retaining fewer than **6 of 8** seeds after the
registered exclusions is reported **INDETERMINATE-BY-ATTRITION** and the whole verdict is flagged
`[DEGRADED]`.

### 6.4 Registered exclusions, applied before any endpoint is read
| code | condition |
|---|---|
| **E1** | launcher log missing, zero bytes, or never reaching `Starting optimization` |
| **E2** | `check_unused` verdict not clean for that cell's log (block discarded, or the log cannot establish either way) |
| **E3** | the result directory cannot be resolved **by content** to exactly one candidate |
| **E4** | the registered replay does not produce exactly one `.sto` > 100 000 bytes |
| **E5** | `cycle_features` returns `None` — fewer than two complete GRF-delimited cycles after settle (the "fell over" exclusion) |
| **E6** | best fitness ≥ 3.0 (this project's existing convergence threshold, `task_slope` / `uphill_ladder.CONVERGED`) |

---

## 7. TESTS

**PRIMARY** — condition-level OLS on the **four mild rungs only**, S = downhill grade magnitude in
degrees (0, 2, 5), ARM = 1 spastic / 0 weak:

```
Δ_EQ = b0 + b_arm·ARM + b_slope·S + b_int·(ARM·S) + e        n = 12, df = 8
```

`b_int = d(MARGIN)/dS`. **Directional, one-sided, α = 0.05; b_int > 0 is the prediction and
nothing else is a confirmation.** A significant `b_int < 0` is F2 and is reported as a refutation,
never as "an effect".

**Unit of analysis = CONDITION, not seed.** Seeds are replicate searches of one physics, not
subjects. This is the level-ground study's registered unit and it is not changed here.

**CO-PRIMARY (estimation)** — MARGIN(−5°) and its two-sided 95 % CI read against the 3.8° MDC,
pooled over the two mild rungs per arm at seed level (N = 16 per arm, half-width ≈ 1.53°). It is
registered because the interaction p-value alone cannot say whether the margin became *usable*. The
condition-level margin CI is reported alongside it every time, as a sensitivity, without exception.

**SECONDARY — never promotable (R45-S)**
- **S1** the same interaction on all six lesion rungs (adds `K100`, `W60`); better powered, still
  secondary, because the problem this study exists to solve is at the mild end.
- **S2** seed-level refit of the primary, reported as sensitivity only; a seed-level df is not an
  honest df if rung heterogeneity is real.
- **S3** MARGIN(S) at each slope with CIs at both seed and condition level.
- **S4** agreement of the re-run level cells with the existing level corpus (external replication).

---

## 8. WHAT A NULL BUYS — stated in advance

**If the mild margin does not grow with slope, the effect size is not recoverable by provocation,
and the negative becomes FINAL rather than provisional.**

That is the point of running this. The level-ground result is currently a *provisional* negative:
"we could not find a feature that clears the MDC". A registered, adequately-designed provocation
manoeuvre that fails converts it into a *final* one: "the margin is not there to be found by
raising task demand, and the mechanism-specific signature does not survive CMA-ES re-optimisation
of the gait". That is a publishable outcome, and it is the reason this study is worth 168 runs even
though the most likely result is a null.

A null is **not** to be followed by another feature search, another manoeuvre, another endpoint, or
another filter. Saying so before the data exist is what stops it being spun afterwards.

Two honest limits on the null, registered now so they cannot be produced later as excuses:
1. The design has only ~24–37 % power at the *minimum clinically meaningful* β_int = 0.298 (§2.4).
   A null bounds the interaction at roughly ≤ 0.5–0.7 °/deg; it does not exclude a small real one.
   The conclusion licensed is *"no interaction large enough to rescue the margin"*.
2. If the −5° gate fails (§6.2), the null rests on a 2° provocation only, and that must be stated
   in the abstract rather than in a limitations paragraph.

---

## 9. PER-CELL VERIFICATION ARTIFACTS — named in advance

For every one of the 168 cells:

1. **`scone/opt_slope58/launch_logs/log_<TAG>.txt`** — non-empty and containing
   `Starting optimization`. Checked as **E1**. (60 of 60 archived `optimization.log` files are zero
   bytes because an earlier launcher passed `-q` and dropped the redirect; the launcher here omits
   `-q` and redirects both streams, which is the only way SCONE's `Warning, unused properties:`
   survives.)
2. **`check_unused.py` verdict on that log** — a *real* verdict, one of clean / discarded /
   cannot-establish. Checked as **E2**; abstention is a failure, not a pass.
3. **`check_structure.py` verdict on `scone/opt_slope58/<TAG>.scone`** — a *real* verdict, with its
   `could not verify` list reported rather than suppressed.
4. **Content-based directory resolution**, recorded in each cell's `PROVENANCE.json`:
   resolved **only** by `min_progress == 0` **AND** `max_generations == 90` **AND** terminal
   generation from `history.txt` == 89. **Never by name and never by mtime.** SCONE appends `" (1)"`
   to colliding directories rather than overwriting, and prior tag collisions in this project
   silently mixed two corpora at different budgets — `CMW70`/`CMW80` archive copies also ran at 90
   and also stop at 89, so `min_progress` was the only discriminator. The terminal generation is
   read from `history.txt`, never from `.par` filenames, because SCONE writes a `.par` only on
   improvement and the `.par` maximum is the last generation that *improved*, not the last that
   *ran*.

---

## 10. PRE-LAUNCH GATES — all executed, all passed

| gate | what it asserts | result |
|---|---|---|
| **V1** | every generated scenario carries `min_progress = 0` and `max_generations = 90`, exactly once each, plus a present and within-condition-distinct `random_seed` | **PASS** 168/168 |
| **V2** | every scenario's `model_file` carries the gravity vector its slope requires, read back from the `.osim`, and **no negative `gx`** (= uphill) anywhere | **PASS** 168/168 |
| **V3** | every cell is `S10W` (`min_velocity = 1.0` exactly once) and carries its registered `KV` exactly twice (soleus + gastroc) inside a `legs = left` `ConditionalController` named `SpasticL` | **PASS** 168/168 |
| **V4** | no tag collides with any existing result directory; none matches the protected pattern | **PASS** 0/168 collide; 376 existing dirs, **112 protected**, untouched |
| **V5a** | `check_structure.py` on the **CONTROL** cell returns a real verdict | **PASS** — `OK`, chain `CmaOptimizer/SimulationObjective/GaitStateController/ConditionalControllers/ConditionalController/ReflexController`, with 3 explicit `could not verify` items |
| **V5b** | `check_unused.py` on a **CONTROL-cell launcher log** produced through the shipped launch path | **NOT RUN — it requires starting a `sconecmd` process, and this study did not launch (see the banner and section 12).** |

`check_structure` was also run on a spastic cell (`PGD5K050_s1`, `--expect-kv 0.05`) and returned
`OK` on the same chain. Its three `could not verify` items — delivered gain magnitude, per-side
duplication factor, and run-time acceptance — are reported rather than suppressed; the third is
what V5b exists to close, and the first is *not* closed by anything in this study
(`delivered_gain.py` cannot read the current side-free target syntax and returns
`NO_INJECTION_DECLARED_AND_NONE_DELIVERED` on a correct unilateral delivery).

Analysis-code self-test, run before hashing and writing nothing into the project: the registered
interaction estimator recovers a planted β_int of +0.500000 exactly, returns −0.500000 under a
reversed mechanism, and has simulated Type-I error 0.051 at sd_rung = 0 and 0.028 with rung
heterogeneity present (conservative, not anti-conservative).

---

## 11. LAUNCH RECORD

**NOT LAUNCHED. Zero `sconecmd` processes were started by this study. No PID exists to report.**

Everything up to the launch line is done: 21 `.osim` files with verified gravity, 21 base
scenarios, 168 seed scenarios, all four generation-time gates passed, both static structural
verdicts obtained. The intended launch was:

```
python gen_slope.py --structgate     # V5b: 1-generation control run -> log for check_unused
python gen_slope.py --run            # supervisor: PGD5K000_s1 gate first, then 112, then 55
```

with concurrency capped at **4** — the value the 48-run level study ran at on this machine — and
every cell started at **`BELOW_NORMAL_PRIORITY_CLASS`** so our cells yield to the user's own work
on contention. Each `sconecmd` opens a 32-thread pooled evaluator on a 16-core / 32-thread machine,
so 4 concurrent processes already oversubscribe it; that is why the cap is 4 and not higher.

Expected wall time, from the measured 90-generation runs of the existing crossed corpus
(~1.1–1.4 h per run at 4-way; 48 runs in 16.6 h): **≈ 39 h for the 112 level/−2° cells, ≈ 58 h for
all 168** if the −5° gate passes.

---

## 12. ⛔ THE CONFLICT — two live registrations for one question

`paper/PREREG_slope.md` was written and hashed by a **concurrent session** at **2026-08-03
20:57:28**, while this document was being prepared. It is untouched. The two designs answer the
same question and are **not** compatible:

| | `PREREG_slope.md` (20:57, hashed) | this document (r58) |
|---|---|---|
| primary endpoint | filtered `ank_rom`, 30 Hz + 6 Hz zero-phase Butterworth | `ank_stance_mean`, Δ_EQ vs **same-slope** control |
| level mild margin cited | 2.84° | 2.31° (on its own endpoint) |
| seeds per cell | 4 | 8 |
| level cells | **reused** from the crossed corpus | **re-run** inside the study |
| conditions | 4 mild only | 7 (mild + zero-gain control + 2 moderate anchors) |
| per-slope zero-gain control | none | `K000` at every slope (required by its endpoint) |
| new runs | 32 | 168 |
| falsifier | CI includes zero **OR** −5° gap < 3.8° | F1–F4, incl. reversal and feasibility |
| −5° convergence risk | not addressed | pre-committed gate, §6.2 |
| gravity sign | not addressed | §2.5 — **the swapped `DN5`/`UP5` pair** |

**Neither was launched. This needs a human decision, and it needs it before either launches**, for
three reasons:

1. **Machine contention.** Both supervisors cap at 4 concurrent `sconecmd`, each of which opens a
   32-thread evaluator. Running both is 8 processes / 256 threads on 32 logical CPUs, on a machine
   the user works on. Wall-time estimates in both documents become meaningless.
2. **Provenance.** Two files named `PREREG_slope*.md`, both hashed, both claiming to register "the"
   downhill study, is the exact failure mode this project's catalogue is built from.
3. **One of them is cheaper and one is more defensible.** The 32-run design is 5× cheaper and can
   reuse the level corpus; the 168-run design carries its own control at every slope, which its
   endpoint requires, and does not inherit the level corpus's n = 4. That is a real trade, not a
   quality ordering, and it is the PI's to make.

## 13. THE ONE FINDING THAT IS URGENT REGARDLESS OF WHICH DESIGN WINS

**`opt2/H0914M_DN5.osim` and `opt2/H0914M_UP5.osim` are sign-swapped (§2.5), and copies sit in
eleven `opt_*` directories.** Any −5° arm that reuses `H0914M_DN5.osim` will walk **uphill** under a
downhill label, at `S10W`, where it will not converge — reproducing the exact speed/task confound
that caused the uphill arm to be abandoned, while every artifact reads "DN5". The competing
registration does not mention gravity signs and its §1.2 does not say which `.osim` the −5° arm
uses. **This must be checked before either study launches.**

Two archived runs are already mislabelled on disk and should be annotated rather than trusted:
`SLOPEDN5` walked 5° uphill, `SLOPEUP5` walked 5° downhill.

## 14. Deviations from this document

Any deviation is recorded here with its date, its reason, and whether it was made before or after
the primary was computed.

- **2026-08-03, before any launch:** the study was **not launched**, on discovery of the competing
  hashed registration in §12. Gates V1–V4 and V5a were executed and passed; **V5b was not run**,
  because it requires starting a `sconecmd` process. Recorded as a deviation rather than quietly
  omitted.
