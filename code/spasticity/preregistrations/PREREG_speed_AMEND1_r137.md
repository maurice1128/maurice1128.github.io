# PREREG_speed AMENDMENT 1 — a slow arm, registered before any speed run exists

**Amendment 1 to `PREREG_speed_r89.md`. Round 137, 2026-08-05. NOT LAUNCHED.**

⛔ **This is a named amendment, not an edit.** *`PREREG_speed_r89.md` is left byte-identical. Where
this amendment and the parent disagree, **this amendment decides only on the points it names**; every
other clause of the parent stands unaltered.*

## 0. Provenance — what existed when this was written

| document | bytes | sha256 |
|---|---|---|
| **amended document** `paper/PREREG_speed_r89.md` | **11,237** | `4d64cd58a5e85feea75c94bf4b0a65e53dfd5a17c18b90d2af893a005e045ec6` |
| **generator** `scone/gen_speed_r89.py` | **7,390** | `c99d4a0af4ced131df37ecbf410f32893d529a9522ad6be38ea35deefc3eb85f` |
| **this amendment** | *see `COUNCIL_round137.md`* | *recorded there and in the defect register after the last write* |

**Corpus state at the time of writing, confirmed from disk and not from any status file:**

- **Zero runs of the speed study exist.** *The study has never been launched; `SPEEDS` has produced no
  directory.*
- **210** `SG*` slope-study directories carrying `.par`; **96 of 120** Tier-2 cells complete in the
  registered seed range 107–116; `sconecmd` **2**.
- **The only archived non-1.0 m/s directories are four uphill cells at `S08W`** (`UPL05`, `UPL10`,
  `UPL15`, `UPU2V8`). ⚠ **They carry `.par` and ZERO `.sto`** — *no kinematics, so no stretch velocity
  is recoverable from them at any speed other than 1.0.*

⛔ **This amendment was written before any speed run existed. That is the whole of its value and it is
the one property that cannot be recovered later.**

## 1. What is wrong with the registered design, and why an amendment rather than a new study

**The parent registers `min_velocity ∈ {1.0, 1.4, 1.8}` and `NEW_SPEEDS = [1.4, 1.8]`. The provocation
runs upward only.** ⛔ **1.0 m/s is ordinary walking, not slow.**

**The Tardieu contrast requires a speed at which the velocity-dependent reflex is SILENT, not merely
quieter.** The registered design has a loud end and no silent end, so its difference-of-differences is
taken between two speeds **both of which carry a spastic contribution**. *A slow arm supplies the
missing pole.*

⚠ **This is a gap in the design, not a defect in the parent's execution.** *It is amended rather than
re-registered because §§4–9 of the parent — the mechanism gate, the feasibility discipline, the power
statement, and what makes the negative final — are the parts worth keeping, and re-registering would
put them back in play.*

## 2. The slow speed: what the disk supports, and what it does not

⛔ **Nothing on disk determines the value. It is proposed below as an explicit judgement call.**

**What was searched, and what each source gives:**

| source | what it could have given | what it gives |
|---|---|---|
| parent §2(c) | peak `fiber_velocity_norm` versus speed | **only at `min_velocity = 1.0`** — spastic arm mean 2.0520, weak 2.8658. **One speed. No slope against speed exists.** |
| the four `S08W` directories | stretch velocity at 0.8 m/s | ⛔ **`.par` only, zero `.sto`. Nothing measurable.** |
| parent §2(a) | precedent for a slow target | *"5 at 0.8, 4 at 0.6"* — **scenario counts, not outcomes.** They establish that such scenarios have been built, and nothing about the reflex |
| the controller | the reflex's velocity dependence in closed form | `MuscleReflex { target = soleus, KV, allow_neg_V = 0 }` — contribution ∝ `KV × max(0, v_fiber)`. **Monotone in stretch velocity, with no speed→velocity mapping anywhere on disk** |

⛔ **THEREFORE: THE VALUE IS A JUDGEMENT CALL AND IS LABELLED AS ONE.**

> **Proposed slow arm: `min_velocity = 0.6 m/s`.** **This number was chosen, not derived.**

*The reasons it was chosen, offered as reasons and not as a derivation:* it is the slowest value with
any precedent in the corpus (4 scenarios), so it is not an unprecedented regime; it is a substantial
fraction below ordinary walking rather than a token reduction; and it keeps the arm on the existing
`min_velocity` knob rather than requiring a new scenario parameter.

⚠ **A derived-sounding number that was chosen would be worse than a labelled one. This is labelled.**

### 2a. The measurement that WOULD derive it, registered here so a future amendment can stop guessing

**Probe P1, if it is ever run:** peak `fiber_velocity_norm` (max of `gastroc_l`, `soleus_l`, settle
1.0 s) in `DR2K000` at `min_velocity` ∈ {0.6, 0.8, 1.0}, seed 101. **That is a three-point mapping of
stretch velocity against speed and it is exactly what §2(c) is missing.** *It is not part of this
amendment's run cost and is not proposed for launch here.*

## 3. Why lowering the floor should lower the speed — the one thing that IS derived

⚠ **`min_velocity` is a FLOOR, not a target. Lowering a floor does not command a slower gait.** *There
is no `max_velocity` and no target-speed term: the scenario's `GaitMeasure` carries `min_velocity`
alone.*

⛔ **The parent's own §2(b) is the evidence that the floor nonetheless binds.** Achieved forward pelvis
velocity over the 48 level runs: **mean 1.005, min 0.956, max 1.070 against a threshold of 1.0** —
*"The controller sits ON the threshold, it does not exceed it."* **Headroom +0.005 m/s.**

**The floor binds because `EffortMeasure` (`use_cost_of_transport = 1`) pushes speed down and
`min_velocity` stops it.** *So lowering the floor should lower achieved speed. This is the derived
part of the amendment, and its container is §2(b) of the parent.*

⚠ **It is an inference from a binding constraint at one value, not a measurement at 0.6.** *§4's gate
below verifies it rather than assuming it.*

## 4. Feasibility gate for the slow arm, and its registered fallback — modelled on parent §5

⛔ **An arm with no gate is an arm that will be quietly dropped later.**

**S2 — SLOW FEASIBILITY PROBE, RUN FIRST AND ALONE.** One cell, **`DR2K000` at `min_velocity = 0.6`,
seed 101.** All four clauses must hold:

1. **≥ 2 complete GRF-delimited gait cycles** under `cycle_features` — the parent's §6.2(b) criterion.
2. **Achieved forward pelvis velocity within `[0.55, 0.75] m/s`**, settle 1.0 s. ⛔ **A BAND, not a
   `≥`.** *The parent's S1 uses `≥ 1.6` because it provokes upward and only underachievement is the
   risk. Here the risk is the opposite: a floor of 0.6 is satisfied by walking at 1.0. **A one-sided
   test would pass an arm that never went slow**, which would silently destroy the contrast this
   amendment exists to create.*
3. **Terminal best fitness within one order of magnitude of the matched `v = 1.0` cell** — the
   parent's third clause, adopted unchanged and for the parent's stated reason.
4. **Peak `fiber_velocity_norm` materially below its 1.0 m/s value in the same condition**, reported
   as a ratio against §2(c)'s `DR2K000` mean of **2.1121**. ⚠ **No threshold is registered for this
   clause because none can be derived** (§2). **It is registered as REPORTED, not as PASS/FAIL**, and
   it is the quantity a future amendment needs.

**REGISTERED FALLBACK.** **If S2 fails, the slow arm is not launched**, the design reverts to the
parent's `{1.0, 1.4, 1.8}`, and that reversion is reported as **SLOW ARM NOT ATTAINABLE** — *not as a
design choice, and not omitted from the write-up.* **Its cost is already stated in §6 below.**

⚠ **Clause 2 can fail in a way clause 1 cannot see:** *a run that walks at 1.0 m/s while nominally
targeting 0.6 satisfies every other clause. That is the failure this gate exists for.*

## 5. What this amendment does NOT change

**Unchanged, explicitly:** the five conditions; `n = 6` per cell and seeds 101–106; the budget
(`min_progress = 0`, `max_generations = 90`, `init_file = ResultH0914Gait10.par`, no warm start); the
models, none of which this study creates; the primary `ank_rom ~ condition + v + arm:v`, weak minus
spastic; **F1, F2 and F3 and the conditions under which the negative is final**; §7's registration of
the study as a **mechanism screen and not a clinical test**; and §8's launch gates, including
⛔ **"Tier 2 finishes first. Nothing in this study launches while it holds the cores."**

**The 1.8 arm keeps its own S1 gate and its own fallback. S2 is independent of S1: either arm can fail
without the other.**

## 6. The cost, and the honest power consequence

| | design | new runs | total |
|---|---|---|---|
| parent, 1.0 arm reusable | {1.0, 1.4, 1.8} | 60 | 60 |
| **amended, 1.0 arm reusable** | **{0.6, 1.0, 1.4, 1.8}** | **90** | **90** |
| amended, 1.0 arm NOT reusable | as above | 120 | 120 |

**The slow arm costs 30 additional runs** — 5 conditions × 1 level × 6 seeds.

**Recomputed on the parent's own basis — the slope study's realised SE 0.6847 at Σ(D−D̄)² = 12.6667,
not a design assumption:**

| design | Σ(v−v̄)² | projected SE(β_speed) at n = 6 | `beta_req` | **required effect in SE** |
|---|---|---|---|---|
| parent {1.0, 1.4, 1.8} | 0.3200 | 4.3078 | 2.7810 | **0.646** |
| **amended {0.6, 1.0, 1.4, 1.8}** | **0.8000** | **2.7245** | **1.8540** | **0.680** |
| amended fallback {0.6, 1.0, 1.4} | 0.3200 | 4.3078 | 2.7810 | 0.646 |
| amended fallback {0.6, 1.0} | 0.0800 | 8.6156 | 5.5620 | 0.646 |

⛔ **THE SLOW ARM DOES NOT IMPROVE CLINICAL POWER. IT SLIGHTLY WORSENS IT: 0.646 → 0.680 SE.**

*Widening the range from 0.8 to 1.2 m/s lowers `beta_req` from 2.7810 to 1.8540, but it lowers the
standard error faster than it lowers the requirement, and the ratio moves the wrong way by 5.3 %.*
⚠ **This is registered because it is the amendment's weakest number and because the parent's §7
already establishes that no clinical claim is available at n = 6 in either direction.**

**The amendment is justified by the mechanism contrast — the silent pole for M2 — and by nothing
else.** ⛔ **It must not be presented as buying power, because it does not.**

## 7. The mechanism gate is a DESIGN, not a GUARANTEE

⚠ **The parent's §4 states M1 and M2. Neither has been tested. The gate's existence must not be read as
evidence that it works.**

⛔ **The same avoidance that defeated the slope study can recur here, and the slow arm does not prevent
it.** *A re-optimised controller can meet a slow target by a different strategy — shorter steps, more
double support, a different ankle trajectory — and a difference-of-differences taken across such a
change can cancel the signal along with the confound. **The gate would report that outcome as
MECHANISM-NULL, which is the correct label, but it would not have prevented it.***

⚠ **Specifically, "silent" may not be attainable at any walkable speed.** *Peak plantarflexor stretch
velocity is driven substantially by the stance-to-swing transition, which does not vanish as speed
falls. **This amendment assumes a silent pole is reachable and registers no evidence that it is** —
S2 clause 4 measures it, and if the ratio is near 1.0 the premise of this amendment fails and should
be reported as having failed.*

**Extension to §4, registered:** **M2 is computed over the amended level set** when the slow arm is
attained, and over the parent's set when it is not. **Which set was used is reported with Δ_M**, so a
reader can tell whether the silent pole was present.

## 8. The generator change this requires — stated, and NOT made

⛔ **`scone/gen_speed_r89.py` is NOT modified by this amendment and is left byte-identical
(`c99d4a0a…`, 7,390 B). Building the slow arm requires a change to it, and that is a separate
authorisation.**

**The change required, stated precisely so it can be authorised or refused on its merits:**

1. **`SPEEDS = [1.0, 1.4, 1.8]` → must include `0.6`.**
2. **`NEW_SPEEDS = [1.4, 1.8]` → must include `0.6`**, since no 0.6 cell exists to reuse.

**Two things verified as NOT needing change**, so the request stays minimal:

- **`tag_of`** is `"SPD%02d_%s" % (round(v * 10), cond)` → **`0.6` yields `SPD06_*`**, which collides
  with nothing and needs no edit.
- **`set_min_velocity`** substitutes with `"%.1f"` and asserts exactly one match → **`0.6` is written
  as `min_velocity = 0.6`** with no format change.

⚠ **The reuse verification, the budget assertion and the G5 tag-collision gate all extend to the new
cells unchanged.** *No new gate is needed in the generator; only the two lists move.*

## 9. What this amendment fixes and what it leaves open

**Fixed, and cannot move after any speed datum exists:**

1. **The slow value is 0.6 m/s and it is a labelled judgement**, not a derivation.
2. **S2's four clauses**, including that clause 2 is a **band** and clause 4 is **reported, not
   pass/fail**.
3. **The fallback's identity: SLOW ARM NOT ATTAINABLE**, reported, not silent.
4. **`beta_req` and the required effect in SE under all four designs**, including that the amendment
   **worsens** the ratio to 0.680.
5. **The run cost: 30 new runs, 90 or 120 total.**
6. **That §4's gate is a design and has never been tested**, and that a silent pole may be unreachable.

**Left open, and named as open:** whether 0.6 is the right value (§2a says what would settle it);
whether a silent pole exists at any speed; and whether the generator change is authorised.

## 10. Skipped, and said so

- **Nothing was launched and nothing was simulated.** *No feasibility probe was run; S2 is registered,
  not executed.*
- **No Tier-2 run was read** — 96 carried `.par` at the time of writing and none was opened.
- **The four `S08W` directories were listed and their `.sto` count measured (zero); their `.par` files
  were not parsed.**
- **`PREREG_speed_r89.md` §§ beyond 9 and the parent's own skipped items** were not re-audited.
- **The parent's `beta_req` figures were recomputed and reproduce exactly** (2.7810 and 5.5620 from
  `(3.800 − 1.5752) / range`); **the parent's SE figures also reproduce** (4.308, 8.616). *No
  discrepancy was found in the document being amended.*
