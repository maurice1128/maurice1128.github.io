# DEVIATIONS AND EXECUTOR-MADE CHANGES — round 62, downhill-provocation study

**This file is a holding record, not an amendment.** `PREREG_slope.md` §10 is the registered home
for deviations, but §8 states that any modification of that document invalidates the registration
and that amendments require `paper\PREREG_slope.sha256` to be **re-issued carrying both hashes with
their dates**. That is a re-issue of a registration, which is a council decision and not an
executor's. **Nothing below has been written into `PREREG_slope.md`, whose hash is unchanged:**

```
PREREG_slope.md    53689 B    sha256 678eba3d43d15391feffe53cca3544349daacdb3253eb5b28f2cad55738530a2
```

Each item below is stated in the form §10 requires — what changed, why, and **whether it was made
before or after the primary was computed**. At the time of writing **the primary has not been
computed and no feature has been extracted from any slope run**, so every item here is a
*correction*, not a *deviation*, in §10's own distinction. That distinction is the whole point of
the timestamp and it is recorded now, while it is still true.

The instrument these items attach to:

```
scone\slope_analysis_r62.py   125379 B   sha256 b91ac22c12cd0630c29546dbccfb3e021da5d50c0908528798f70ecf37ce3c9d
```

---

## D1 — `random_seed` added as a content-resolution key. **FLAGGED FOR RATIFICATION.**

**Status: an executor-made resolution-rule change. It must be signed off or replaced.** Recorded in
the same form `scone\replay_crossed.py` used for its selection-rule relaxation, which is this
project's precedent for an executor changing a registered rule under measurement.

**What §7.4 registers.** Cells are resolved by CONTENT, never by name, never by mtime. The
registered key is `min_progress` ∧ `max_generations` ∧ terminal generation ∧ `model_file` **and the
`<gravity>` vector inside it** ∧ injected `KV` ∧ `tib_ant_l max_isometric_force` ∧ `min_velocity` ∧
`random_seed`. §7.4 is explicit that the first three are identical across all 21 cells by design and
that gravity is the slope discriminator.

**What was measured.** Executing the resolver read-only against the live results root:
**the registered key does not separate this study's D = 0 cells from the CROSSED corpus's level
runs.** `DR2K000_s1..s4` and `HEALTHY_s1..s4 (1)` carry `min_progress = 0`, `max_generations = 90`,
terminal generation 89, `min_velocity = 1.0`, `init_file = ResultH0914Gait10.par`, `KV = 0.000`,
`tib_ant_l = 1759 N` and a level `<gravity>`. They therefore resolve into cell `(DR2K000, D = 0)`
exactly as `SG0_DR2K000_s101..s106` do. §7.4's rule — *"A cell that resolves to more directories
than it has registered seeds halts the analysis"* — then fires **permanently**, because those
directories are on disk for good. The registered key is not merely imprecise here; it is
non-terminating.

**The change.** `random_seed`, read from each run's **own archived `config.scone`**, is required to
lie in this study's registered range. §5.3 fixes that range at `101 .. 116` in advance of the
corpus; §6.2(c) gives the 12 primary cells 101–106 at Tier 1 and 101–116 at Tier 2, leaving control
and manipulation-check cells at 101–106. The crossed corpus used seeds 1–4.

**Why this is not resolution by name.** `random_seed` is a registered budget constant read out of
the run's own artifact — the same class of key as `min_progress` — and §7.4's own table already
lists `random_seed | run's own config.scone | seed identity within a cell` as a resolution key. This
uses it for exactly that. **Directory names and mtimes remain unused and remain forbidden.**

**Effect, measured.** 384 directories present; 112 matching the protected pattern and skipped before
being opened; 43 already carrying SCONE's `" (1)"` collision suffix; 272 offered to the resolver;
**5 resolved**, 267 excluded each with a printed reason. Without the key, 37 resolved and the
analysis halted.

**What could replace it if ratification is refused.** Renaming or archiving the colliding crossed
directories would also work, but that writes to a shared read-only corpus and is worse. A council
may instead amend §7.4 to name the seed range explicitly.

**Made before the primary was computed. → a correction, not a deviation.**

---

## D2 — multiplicity is computed but not applied, and this project's other script applies it

**Disclosed because two results in one manuscript handling multiplicity differently, with no
sentence explaining why, is an unexplained inconsistency of exactly the kind this project keeps
finding at review.** Disclosed by us rather than discovered.

`scone\crossed_endpoint.py` line 175 computes `n_eff = (Σλ)² / Σλ²` from the feature correlation
spectrum and then **multiplies its primary p-value by it** (`p_adj = p_primary * n_eff`, line 188).

`scone\slope_analysis_r62.py` computes `n_eff` **by the identical arithmetic, re-executed on this
corpus**, prints it before the contrast — and **does not adjust the primary.**

**Justification.** §4.6 of this registration does two things the crossed study's registration did
not. It registers the multiplicity figure as a quantity to be *computed on this corpus before the
contrast*, and, in the same section, it registers where inference actually rests: the
condition-level permutation *"is reported but is not the inferential basis; inference rests on the
seed-level CI in §1.3."* The registered primary here is an **estimate with a confidence interval**
read against a fixed decision threshold (`β_req = 0.4450`), not a p-value screened at α. There is no
p-value in the decision path of §6.2(c) — the Tier-1 and Tier-2 rules are stated entirely in terms
of `β̂_int` against fixed constants — so there is nothing for an `n_eff` multiplier to act on. §4.6
also warns that the same figure has been computed as 1.15, 2.35 and 3.19 by three parties on three
feature sets and that `CROSSED_RESULT.json`'s `n_eff = 1.1527` **does not transfer** to this corpus.

**Consequence to write into the manuscript.** The two studies differ because their primaries differ
in kind: the crossed study's primary is a screened exact p-value and takes the correction; the slope
study's primary is an interval estimate against a pre-registered threshold and does not. The
`n_eff` figure is still reported for this corpus, so a referee can apply it if they disagree.

**Made before the primary was computed. → a correction, not a deviation.**

---

## D3 — the −5° tier's evaluations are terminating early, not merely converging worse

**Recorded as evidence, not as a change.** §5.3 registered in advance that *"the −5 degree tier may
fail to converge from cold"*, and §7.1 registers gate G4 with a fallback to {0, 2}. Nothing here
alters either. What the artifacts add is the **mechanism**, and it is sharper than "converges worse".

Measured from raw `history.txt` and directory creation times:

| run | terminal gen | wall clock | terminal `best_fitness` | gen-0 `best_fitness` |
|---|---|---|---|---|
| `SG0_DR2K000_s101` | 89 | 29.78 min | 0.616297 | 17.2551 |
| `SG0_DR2K000_s103` | 89 | 47.85 min | 0.633911 | 17.0553 |
| **`SG5_DR2K000_s101`** | **89** | **4.53 min** | **29.3567** (min 26.2813 at gen 88) | **93.2379** |

The D = 0 and D = 5 control scenarios are byte-identical apart from `signature_prefix` and
`model_file`, so measure, budget, cold start and seed policy are the same and the only difference is
`<gravity>`. **A full 90-generation run costs 4.53 min at D = 5 against ~42 min at D = 0 — the same
number of generations in about a tenth of the wall clock.** Generations do not become cheap; a
generation costs what its evaluations cost. **The evaluations are ending early**, which is what a
model falling early in the trial looks like, and it is corroborated by the cold-start cost being
5.4× higher and by 90 generations recovering only to ~26 against ~0.62.

**Why this strengthens G4 rather than changing it.** G4's registered criterion is whether the D = 5
control yields ≥ 2 complete cycles under `cycle_features`. **The probe passed it**, and returned
`ank_rom` 35.88° against §3.2's registered prediction of 23.0 [21.5, 24.0]. A run that falls early
can still stagger through two cycles, so the criterion admits exactly the runs whose ROM is inflated
by non-convergence rather than by slope — defect **A7** (equal generation *numbers* are not equal
*convergence*) arriving through the gate written to keep it out.

**Handling, already in the hashed instrument and requiring no change.** Terminal `best_fitness`,
`best_gen`, terminal `median_fitness` and **gen-0 `best_fitness`** are carried per run as
first-class columns read from each run's own `history.txt`; per-(D, arm) means and spreads are
printed; an order-of-magnitude flag fires; and `β_int` is reported **both unadjusted and with
terminal fitness as a covariate**. The unadjusted value of §1.3 is the sole decision quantity and
**fitness never reweights, drops or excludes a seed** — adding a convergence-based exclusion after
seeing this would be the post-hoc filter §6.2(e) forbids.

**Recorded before the primary was computed.**

---

## D4 — wall-clock cost, which §9 item 7 records as unmeasured

§9 item 7: *"Wall-clock cost was not measured. Run counts are registered (114 / 234); hours are not
… The superseded draft asserted ~5.5 h per run and ~1.8 days at 4-way concurrency; that figure is
not adopted here because its source was not identified."*

**Now measured**, from raw `history.txt` modification times against result-directory creation times,
at the study's actual concurrency of 2 (`gen_slope_r60.MAX_CONCURRENT = 2`, confirmed against
running `sconecmd` processes):

| basis | min/generation | min per 90-gen run | wall clock, Tier 1 (114 runs) |
|---|---|---|---|
| **steady state — last four D = 0 runs** | **0.53** | **≈ 47.8** | **≈ 45 h ≈ 1.9 days** |
| all six D = 0 runs, including the opening pair | 0.466 | ≈ 42.0 | ≈ 40 h |
| opening pair only (unrepresentative) | 0.33 | ≈ 29.8 | ≈ 28 h |

**≈ 45 h is the estimate.** The all-runs average is dragged down by an opening pair that ran at
0.33 min/gen and has not been reproduced since; the last four runs sit at 0.53 min/gen and are
independently consistent with completion times of about one pair per 49 min. **Tier 2 (234 runs) is
≈ 93 h ≈ 3.9 days at the same rate.** If the −5° tier terminates early as D3 describes, Tier 1 falls
towards ≈ 29 h — but that is a symptom of D3, not a saving.

This is ~7× cheaper than the superseded draft's unadopted ~5.5 h/run. §9 item 7 called compute *"the
binding practical risk to this design"*; on this measurement it is not.

---

## D5 — three numbers in the executor's first progress report came from a pre-hash build

**Not a deviation from the registration. A reporting error, corrected here because this project's
central pathology is reported numbers differing from registered numbers.**

The self-test was run three times: once before its sections (0) and (2b) existed, and twice after.
Those sections draw from the same fixed-seed RNG stream, so inserting them shifts every subsequent
number. The harvest of the final run's output failed to match two lines, and the earlier values were
carried forward.

| quantity | reported earlier | actual, hashed build |
|---|---|---|
| null mean recovered `β̂_int` | +0.005367 | **+0.013634** |
| null empirical sd of `β̂_int` | 0.348859 | **0.344270** |
| null rejections of 2000 | 111 | **113** |

Everything else quoted — type-I rate 0.0565, power 110/400 and 275/400, every noiseless recovery,
the PASS verdict — came from the final hashed build and stands. **The corrected sd of 0.344270 sits
closer to the registration's §5.4 design SE of 0.3405 than the misquoted value did**, so the
agreement between the estimator and the registered power calculation is stronger, not weaker.

The full artifact, bound to the instrument's sha256 and reproducible bit-for-bit across two runs, is
`paper\SLOPE_SELFTEST_r62.json`.

---

## Items requiring a decision

| item | decision needed |
|---|---|
| **D1** | **Ratify or replace the `random_seed` resolution key.** Until then the analysis is blocked on a rule the executor changed. |
| D2 | Confirm the multiplicity divergence is written into the manuscript, not left implicit. |
| D1–D5 | Decide whether to fold these into `PREREG_slope.md` §10 under the §8 re-issue procedure, which requires `PREREG_slope.sha256` to carry **both** hashes with their dates. Until that happens this file is the record and §10 reads *"(none at time of registration)"*. |
