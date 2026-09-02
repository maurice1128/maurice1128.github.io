# PREREG_shape_r138.md — three routes, ONE multiplicity pool, registered before any feature is computed

**Round 138, 2026-08-05. NOT RUN. No feature named in this document has been computed on any run, at
either tier.** *Where this document and any analysis script disagree, THIS DOCUMENT DECIDES.*

## 0. Corpus state at the time of writing — measured from disk

| | value |
|---|---|
| Tier-2 cells complete (`.par` present, seeds 107–116) | **96 of 120** |
| **Tier-2 runs that DO NOT YET EXIST** | **24** |
| slope corpus overall | **210 of 234** |
| `sconecmd` | **2** |
| features computed for this document | ⛔ **zero, on either tier** |

⛔ **Tier 2 has never been opened by any analysis. That is the entire asset this document is trying to
spend well, and 24 of its runs did not exist when this was written.**

**Conditions present in Tier 2, from directory names only:** `DR2K050` (30), `DR2K075` (27), `PAR20`
(20), `PAR40` (20). *No run data was read.*

## 1. The claim

**`ank_vel_max` separated the arms perfectly raw — AUC 0.0000, p 0.0079365, overlap 0/5 — and died as a
residual after `ank_rom`, `cycle_time` and `ank_hs`: AUC 0.3600, p 0.5476, overlap 4/5, R² 0.8030.**
*That test was run on a scalar.*

**A stretch reflex has a latency. Latency is phase information, and a peak collapses it.** The
registered question is whether discriminating information survives where the scalar did not — in
**shape** (Route A), in **second moments** (Route B), or in **within-run limb asymmetry** (Route C).

⛔ **The trajectories already exist. No route costs cores and nothing here is launched.**

## 2. Confirmatory / exploratory split — available now and never again

| set | status | consequence |
|---|---|---|
| **Tier 2** (seeds 107–116) | ⛔ **CONFIRMATORY. Held out.** | every number in §4 is computed here, once |
| **Tier 1** (seeds 101–106) | **EXPLORATORY** | has been analysed repeatedly and is contaminated |

⛔ **A Tier-1 result may NOT be promoted to confirmatory afterwards, under any circumstances,
including if it is the only route that survives.** *Tier-1 outputs are reported as exploratory in the
same table, labelled, and carry no correction because they license nothing.*

## 3. The three routes, with feature sets fixed exactly

⚠ **Functional analysis is where researcher degrees of freedom live. Each feature below is a formula
over the time-normalised trajectory θ(t), t ∈ [0, 1] over the GRF-delimited cycle, settle 1.0 s. Two
features per route. Six in total. No feature may be added, substituted or redefined after this
document is hashed.**

### Route A — trajectory shape (the phase a peak destroys)

| id | feature | formula |
|---|---|---|
| **A1** | **timing of peak dorsiflexion velocity** | `t* = argmax_t θ'(t)` — *the direct latency proxy; a scalar peak reports `max θ'`, this reports WHEN* |
| **A2** | **velocity–angle phase lag** | `Δ = argmax_t θ(t) − argmax_t θ'(t)` |

*Both are pure phase in units of cycle fraction. **Neither has amplitude in it**, which is the property
that makes them non-trivially different from `ank_vel_max`.*

### Route B — stride-to-stride variability

| id | feature | formula |
|---|---|---|
| **B1** | **CV of stride time** | `SD(T_i) / mean(T_i)` over strides i within a run |
| **B2** | **CV of peak dorsiflexion velocity** | `SD(max θ'_i) / mean(max θ'_i)` over strides |

⛔ **The argument for Route B, registered because it is the reason this is not merely another
feature:** *a second moment is orthogonal to the mean. `ank_rom` and `cycle_time` are means, so
adjusting for them cannot remove a variance signal the way it removed the peak.* **A reflex is
state-dependent and should add variance that scales with velocity; weakness is deterministic.**

⚠ **Registered weakness:** *variance also rises with instability, and the D = 5 cells lost **eight
runs** to `NO_CYCLES` at Tier 1. **Instability is present in this corpus and is confounded with
grade.** A Route-B positive that tracks grade rather than arm is the expected confound and it is named
here so it cannot be explained away later.*

### Route C — within-run paretic vs intact asymmetry

The injection is unilateral and `H0914M` carries both `_r` and `_l`, so both limbs exist in every run.

| id | feature | formula |
|---|---|---|
| **C1** | **SI of peak dorsiflexion velocity** | `(L − R) / (0.5 × (L + R))` on `max θ'` |
| **C2** | **phase asymmetry** | `t*_L − t*_R`, i.e. A1 computed per limb and differenced |

⛔ **The argument for Route C:** *a within-run limb difference removes subject-level covariates **by
construction** — and subject-level covariates are exactly the class that ate the velocity signal.*

⚠ **Registered weakness:** *the intact limb compensates, so it is **not a clean control**, and the
compensation may itself scale with impairment. A C-route positive is therefore consistent with
"asymmetry tracks impairment severity" as well as with a reflex, and the design cannot separate
those.*

## 4. ONE multiplicity pool — and the pool size is forced, not chosen

⛔ **The pool is every test any route runs against the held-out set: 6 features × 1 confirmatory test
each = 6 TESTS. Bonferroni ×6 across all three routes.**

⚠ **Three registrations with three corrections would be multiplicity laundering. There is one pool.**

**The pool size of 6 is not a preference. It is the maximum the test can carry**, given that the
minimum attainable two-sided exact p from a 5-versus-5 Mann–Whitney is **2 / C(10,5) = 0.0079365**:

| pool | p_adj for PERFECT separation | |
|---|---|---|
| 6 | **0.0476** | ⛔ **clears 0.05 — barely** |
| 7 | 0.0556 | **fails** |
| 13 | 0.1032 | fails |

⛔ **AT SEVEN TESTS, A PERFECT SEPARATION NO LONGER REACHES SIGNIFICANCE. The design has exactly one
chance and it requires a perfect result: the only outcome that can survive correction is AUC 0.0000 or
1.0000 with overlap 0/5.** *Registered now so that a seventh feature cannot be added later without
destroying the whole pool, and so that a near-miss cannot be presented as encouraging.*

## 5. The test — identical, so the comparison is direct

**The confirmatory test is the one already registered in `scone/residual_test.py`, unchanged:**
regress the feature on **`ank_rom`, `cycle_time`, `ank_hs`** plus a constant, take the residual, and
test spastic versus weak by **two-sided Mann–Whitney U**, reporting **AUC = U / (n₁ n₂)**, **p**,
**overlap** (count of spastic values inside the weak range) and **R²** — *the same four numbers, in
the same form, as `ank_vel_max`'s 0.3600 / 0.5476 / 4-of-5 / 0.8030.*

⚠ **Only the Bonferroni constant changes: `BONFERRONI = 2` becomes 6, because the pool changed.**
**No covariate is added, removed or reweighted.**

## 6. ⛔ BLOCKING STRUCTURAL FINDING — the test as written CANNOT run on Tier 2

**The residual test's unit of analysis is the CONDITION, and it is defined over ten:**
`SPASTIC = [DR2K050, DR2K075, DR2K100, DR2K150, DR2K200]`,
`WEAK = [PAR20, PAR40, PAR60, CMW70, CMW80]` — **5 versus 5.**

⛔ **Tier 2 contains four of them: `DR2K050`, `DR2K075`, `PAR20`, `PAR40`. That is 2 versus 2.**

*`DR2K200` and `CMW80` exist only as Tier-1 manipulation-check cells at n = 4 and are **not** escalated;
`DR2K100`, `DR2K150`, `PAR60` and `CMW70` have **no runs in the slope corpus at all**.*

| unit | n₁ v n₂ | minimum attainable two-sided p | ×6 |
|---|---|---|---|
| condition, as the test is written | **2 v 2** | **0.3333** | **1.0000** |
| condition, as the test was validated | 5 v 5 | 0.0079365 | 0.0476 |

⛔ **AT 2 VERSUS 2 THE FLOOR IS 0.3333. NO RESULT IS POSSIBLE — not corrected, not uncorrected, not
with a perfect separation. The confirmatory design as specified is arithmetically dead before a single
feature is computed.**

⚠ **This was found by measuring the condition sets, not by running anything, and it is the reason this
document stops here rather than proceeding.** **Two candidate resolutions exist and this document
chooses NEITHER — the choice is the user's and it changes what the held-out set is worth:**

- **Resolution 1 — keep the identical test, change the held-out set.** *Tier 2 is not a usable
  confirmatory set for a condition-level test. Something else must be, or the confirmatory arm is
  abandoned.*
- **Resolution 2 — keep Tier 2, change the unit to the run.** *Then n is large and the p-floor is not
  binding — **but the test is no longer identical**, the §5 comparison to 0.3600 / 0.5476 is no longer
  direct, and all spastic runs descend from **two** distinct lesions, so run-level replicates are
  pseudo-replicates of 2 conditions, not 57 independent observations.*

⛔ **Choosing Resolution 2 silently would convert a clean held-out design into a pseudo-replicated one
while keeping the language of the clean design. That is precisely the substitution this project has
spent the day finding, and it is registered here in advance instead.**

## 7. Falsifiers — what kills each route

| | fires when | consequence |
|---|---|---|
| **FA** | neither A1 nor A2 reaches p_adj < 0.05 as a residual | **Route A dead.** *Phase carries no information the scalar did not, and "the peak collapsed the latency" is refuted as stated* |
| **FB** | neither B1 nor B2 reaches p_adj < 0.05 as a residual | **Route B dead.** *The orthogonality argument in §3 is refuted: a second moment was removable by mean covariates after all* |
| **FC** | neither C1 nor C2 reaches p_adj < 0.05 as a residual | **Route C dead.** *Within-run differencing does not rescue the signal* |
| **F-ALL** | **all six fail** | ⛔ **The shape route is CLOSED.** *Three mechanistically distinct rescues of the same dead scalar, all failing, is a result about `ank_vel_max` and not about the analyses: the information is genuinely absent after ROM, cadence and equinus, and no further reanalysis of this feature is registered* |

## 8. The split verdict — decided NOW, before any route has an outcome

⛔ **ONE route surviving out of six tests is registered IN ADVANCE as SUGGESTIVE AND NOT CONFIRMATORY.**

*Reason, registered: the correction is calibrated so that a single perfect separation lands at
p_adj = 0.0476. **A lone hit sitting exactly at the floor is not distinguishable from the pool doing
what pools do** — under the null, the chance that at least one of six tests shows perfect separation
is ≈ 4.7 %, which is the correction itself.*

⛔ **TWO OR MORE routes surviving is a FINDING**, and is reported as one. *Under independence the joint
probability is ≈ 9 × 10⁻⁴; **the six tests are NOT independent** — features within a route correlate,
and A1 appears inside C2 by construction — **so this is registered as a decision rule and NOT as an
exact level**, because the correlation structure is unknown and this document will not pretend
otherwise.*

⚠ **After tonight, whichever route survives will look like the one we meant all along. That is why
this section exists and why it is dated.**

## 9. The honest limitation, stated as a live possibility

⛔ **The shape features may be collinear with `ank_rom`, `cycle_time` and `ank_hs` for exactly the same
reason the peak was.** *`ank_hs` is ankle angle at heel strike — a phase-adjacent quantity — and the
three covariates already explained **80.30 %** of condition-level `ank_vel_max`. A trajectory's shape
and its range are not independent, and a phase feature may be recoverable from a cadence and an
equinus angle.*

⚠ **This is not a hedge. It is a stated possible state of the world, and if it is true THE FALSIFIER
SHOULD FIRE.** *That is what F-ALL is for. A route that could not die would be worthless, and the
correct response to F-ALL firing is to report the shape route as closed — not to add features.*

## 10. What was skipped, and what was not done

- ⛔ **No feature was computed on any run, Tier 1 or Tier 2. No `.sto` was opened. No trajectory was
  loaded.** *The only disk reads were directory names, condition lists in `residual_test.py`, and the
  four reference numbers quoted in §1.*
- **`scone/residual_test.py` was read and NOT modified.** *The `BONFERRONI = 2 → 6` change in §5 is
  stated as required, not made; editing it is a separate authorisation.*
- **The exploratory Tier-1 arm was not run** and no exploratory numbers exist.
- **§6's two resolutions were not chosen**, and no analysis proceeds until one is.
- **Nothing launched; Tier 2 holds the cores.**
