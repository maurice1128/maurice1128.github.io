# PREREG_3d_continuation_r172.md — the 3D ladder re-run under a CONTINUATION warm start

**Round 172, 2026-08-10.** *Hashed before a single scenario file exists. Where this document and any
script disagree, **THIS DOCUMENT DECIDES**. It is never edited; defects go to an errata.*

**Parents:** `PREREG_3d_ladder_r169.md` `e3ec76aa…` and `PREREG_3d_reopt_r151.md` `f6a65408…`, both
byte-identical on disk this round. **Gate G, the falsifiers, the control bands and every caveat carry
over from them unchanged unless §6 states a reason.**

## 0. ⛔ The defect this exists to test

**Every rung of r169 was warm-started from the HEALTHY benchmark parameter vector.**
`build_ladder_r169.py`:12 — *"seeds 101-106 at every rung, max_generations = 90, same warm start"* —
and :45, `PARF = par/H1922v7b3-TSG3Dv8g-989_fixed2.par`.

⛔ **This project had already diagnosed and solved that exact failure, in 2D, in its own repository.**
`equinus_ladder.py`:32, verbatim:

> *"Direct high-gain attempts do not converge: SPAS02 (KV 0.2) ended at fitness 32.99, SPAS05 at
> 57.73, SPAS10 at 49.14 — **the model falls over. Each rung is therefore warm-started from the
> converged solution of the rung below**, the technique that worked for the uphill ladder where
> one-step attempts failed at 66-95."*

⛔ **`PREREG_3d_reopt_r151.md` §1's central argument applies to r169 at the rung level: a healthy-tuned
vector dropped onto a lesioned model measures ADAPTATION FAILURE, NOT THE LESION.** *r151 made that
argument to justify re-optimising instead of evaluating. r169 re-optimised, but started every rung
from the same healthy point — so KV 0.400 was asked to travel four times as far as KV 0.050 in the
same 90 generations. **r169's Gate-G collapse is confounded with search distance.**

## 1. ⛔ THIS IS NOT TITRATION, and the distinction is the whole licence for running it

**`PREREG_3d_reopt_r151.md` §3:** *"Do NOT titrate — that is a new registration."* **`PREREG_3d_ladder_r169.md`
§2:** *"No level is added, no KV is raised, no scale is nudged."*

⭐ **THE MAGNITUDES DO NOT MOVE. KV 0.150 and KV 0.400 and ×0.90 and ×0.80 — the exact values r169
registered, unchanged, none added, none removed.** *What changes is the OPTIMISATION PATH: each rung
warm-starts from the converged parameter vector of the rung below, per seed.*

⛔ **Titration changes the MAGNITUDE until the search succeeds. This changes the PATH to a FIXED
magnitude.** *The first lets the data choose what is tested; the second leaves what is tested fixed
and changes only how hard the optimiser is asked to work to get there. **A titrated result cannot be
falsified by its own design, because the design moves to wherever the answer is. This one can: if the
registered magnitudes still fail Gate G under continuation, that is a stronger negative than r169
could produce, and §3 records it as such in advance.***

## 2. ⛔⛔ DEPTH SYMMETRY — the thing that would ruin this, solved by running, not by argument

**`equinus_ladder.py`:34:** *"The weakness arm is warm-started the same way for symmetry of treatment:
**any difference in warm-start policy between arms would be a new batch effect**, and this project
already has one of those."*
**`equinus_ladder.py`:75:** *"**A warm start inherits its parent's optimization depth** … A matched
continuation *policy* is not a matched starting *depth*."*

⛔ **A continuation rung at 90 generations is NOT depth-comparable to a from-healthy rung at 90
generations. r169's admitted rungs — S050, W080, W090, W095 — are ALL from-healthy at depth 90.
Continuation-running spasticity and comparing it to those would rebuild the depth confound this
project has retracted results over.**

⭐ **THE DECISION: BOTH ARMS RUN UNDER CONTINUATION, POSITION-MATCHED. The comparison is only ever
made at equal chain position, therefore at equal cumulative depth.**

| chain position | cumulative depth | **spastic** | **weak** |
|---|---|---|---|
| **1** | 90 from healthy | `KV 0.050` — ⭐ **reuse r169 `R151S`** | `×0.95` — ⭐ **reuse r169 `R169W095`** |
| **2** | 180 | `KV 0.150` from pos-1's par | `×0.90` from pos-1's par |
| **3** | 270 | `KV 0.400` from pos-2's par | `×0.80` from pos-2's par |

*Both chains start at their own mildest rung, both reuse an existing depth-90 from-healthy cell as
position 1, both add exactly 90 generations per step, same seeds 101–106, same objective, same
`max_generations = 90` per rung.*

**HOW IDENTICAL TREATMENT IS SHOWN, not asserted** — the build script must verify and the result must
report all four:
1. every cell's parent `.par` is the pos-(n−1) cell **of the same seed and the same arm**;
2. cumulative depth per cell = 90 × position, tabulated per cell, both arms;
3. `max_generations = 90` present in every generated config;
4. the two position-1 cells regenerate **byte-identical** to their r169 originals.

⛔ **IF ANY OF THE FOUR FAILS, THE COMPARISON IS VOID AND NO ENDPOINT IS REPORTED.**

⛔ **A LIMITATION THAT SURVIVES THIS FIX AND IS REGISTERED NOW.** *Within an arm, severity and depth
now advance together, so a WITHIN-arm dose–response is confounded with optimisation depth and **no
within-arm dose–response may be claimed from this study.** Only BETWEEN-arm comparison at matched
position is depth-clean.* ⚠ **This does not touch r169's weakness dose–response** — W080/W090/W095 are
all from-healthy at depth 90, mutually depth-matched, and that result stands on its own data.

## 3. Branches, registered before the data

| outcome | what it means |
|---|---|
| ⭐ **rungs now clear Gate G** | **the one-point-wide spastic axis was an ARTIFACT of the warm start.** r169 §1's crossing prediction returns to play and sign conservation becomes answerable for the first time. ⛔ **It also means `LADDER_RESULT_r169.md` states a conclusion its own data cannot support — that is a CORRECTION TO A SHIPPED DOCUMENT, filed as such, not reported as a new finding.** |
| ⭐ **rungs still fail under continuation** | **the ceiling is a property of the MODEL, not of the search.** *Far stronger than r169 could claim: the strongest available warm start, the technique this project's 2D line proved, still does not get there. The negative becomes reportable rather than provisional.* |
| ⚠ **INTERMEDIATE — the chain dies partway** | *continuation is SEQUENTIAL: a chain can clear position 2 and fail at position 3, or fail at 2 and never reach 3.* ⛔ **A position that is never reached is recorded as NOT REACHED, which is NOT the same as failed.** *If position 2 fails, position 3 is not attempted from the healthy par as a fallback — that would reintroduce the very defect under test.* **Per-arm, per-seed chain termination is tabulated.** |

⛔ **In every branch, a failing rung is still DROPPED, never replaced and never re-magnituded.**

## 4. Endpoints and primaries — unchanged from `PREREG_3d_ladder_r169.md`

**Channels `ankle_angle_LmR` and `hip_flexion_LmR` only; `ank_hs_LmR` remains a COVARIATE and may not
become an endpoint. Control bands fixed at r169 §0: [−0.5153, +0.0581] and [−0.3671, +0.2900].
Overlap-mass gate k = 6. Co-primaries 4a sign conservation and 4b double dissociation, BOTH PATTERN
CRITERIA WITH NO p-VALUE.** ⚠ *4a is now read at matched chain position and, per §2, carries the
depth confound within each arm.*

## 5. Calibration gate — before anything new is reported

**The reused position-1 cells must reproduce r151/r169's ENDPOINTS, not merely their bytes**, to
1 × 10⁻⁹. ⭐ **This round the check covers ALL THREE channels including `ank_hs_LmR`** — *r169's
calibration checked two of three, and the unchecked one was the channel its §5 gate ran on. That gap
was found by a cold read and is closed here rather than repeated.*

⛔ **If it fails, nothing is reported.**

## 6. Carried verbatim and non-negotiable

- ⚠ ***"Seeds are OPTIMISER RESTARTS, NOT SUBJECTS… No sensitivity, specificity or patient-level AUC
  may be quoted from this study."*** *(`PREREG_3d_reopt_r151.md` §4.)*
- **Gate G unchanged: ≥ 4 of 6 seeds each ≥ 9.73 s and ≥ 5 GRF cycles after settle.** *The 9.73 s is
  0.80 × the 12.16 s `bench_D20` baseline recorded at `PREREG_3d_discrimination_r150.md`:15.*
- ⛔ **No pooling with P3D-2 or P3D-3.** ⛔ **The out-of-plane caveat stands.**
- ⚠ **`PREREG_shape_r138.md` §3's severity confound stands**, and r169 forfeited the ladder's purchase
  on it when the dissociation broke. **Nothing here restores that purchase in advance.**

## 7. Cost — computed from the measured log, not guessed

*Measured: 79.2 s wall-clock per cell at concurrency 2; per-cell CPU median 134.5 s, mean 155.6 s.*

| | count |
|---|---|
| chain cells | 2 arms × 3 positions × 6 seeds = **36** |
| reusable position-1 cells | 2 arms × 6 seeds = **12** |
| ⭐ **NEW CELLS** | ⭐ **24** |

⭐ **Continuation does not serialise the whole run: the 12 chains (6 seeds × 2 arms) are mutually
independent, and only the 2 steps WITHIN a chain are ordered.** *With 12 independent chains, a
concurrency of 2 is never starved, so the wall-clock is the same as r169's:*
⭐ **24 × 79.2 s ≈ 1901 s ≈ 32 min.**

⚠ *One-sided uncertainty, stated now: r169's spastic cells finished in ~10 s because they FELL. **If
continuation works, those cells will survive and take ~135–215 s each, so the true figure could reach
~45 min.** Over 60 min is reported as exceeding this estimate, not silently absorbed.*
⛔ **Concurrency 2 stays. No reason to raise it is offered and none is taken.**

## 8. Operational constraints — unrelaxed

⛔ **Writes confined to `Desktop\spasticity_paper\`. The 112 protected directories are untouchable and
our cells yield on any conflict.** ⛔ **Progress from `history.txt` LINE COUNTS and file mtimes only —
never `LAUNCH_STATUS.json`. A cell is complete iff `history.txt` ≥ 91 lines, and a tag must resolve to
exactly ONE such directory** *(the r170 killed-cell hazard: `sorted(ds)[0]` returns the truncated
directory, not the `" (1)"` sibling).*
⛔ **No `--run`, no `--launch`, no `-e` during optimisation.** **`sto_utils.py`, `gen_seeds.py`,
`equinus_ladder.py` and every registered script are imported or read UNMODIFIED.**
⛔ **The verdict is not reported until the cells exist.**
