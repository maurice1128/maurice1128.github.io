# PREREG_3d_force_r213.md — a second afferent model, and what a null from it would be worth

**Registered before any cell is launched.** *Anchor `scone/force_dose_r213.py` →
`paper/FORCE_DOSE_r213.json`.* **One arm. Six cells. Nothing on disk is re-run.**

## 0. A. THE QUESTION, AND WHAT THIS ARM IS NOT

⭐ **A1. THE QUESTION: does a SECOND AFFERENT MODEL — force feedback — under re-optimisation also
produce no kinematic signature?** ⛔ **True or false regardless of what any paper says.**

⛔ **A2. NO LITERATURE FRAMING APPEARS ANYWHERE HERE.** No published work is characterised, confirmed
or corrected, and no sentence of the form "confirms X" or "corrects our signal choice" is licensed.
Where a citation is unavoidable it is to the file `LITERATURE_r213.md`, ⚠ *coordinator-supplied and
unverified in its entirety* — never to a person or a seat.

⚠ **A3. THE MOTIVATION ALREADY REVERSED ONCE, WITHIN ONE SESSION:** dispatched as a correction —
that force feedback was the better-supported signal — and withdrawn by the coordinating seat in the
same session. ⛔ **The arm is recorded as a THIRD DATA POINT and nothing more.**

## 1. B. THE DESIGN — the only two things that change

⛔ **B1. Identical to the existing spastic arm except the feedback signal and its two matched
parameters:** same muscles (`soleus`, `gastroc`), `legs = left`, `delay = 0.020`, seeds 101–106, warm
start `par/H1922v7b3-TSG3Dv8g-989_fixed2.par`, `max_generations` 90, `min_velocity` 1.0, `bench_D20`
base.

**The existing lesion, verbatim from `scone/probe3d_r141/bench_D20_spasL/config.scone`:**

```
ConditionalController {
    states = "EarlyStance LateStance Liftoff Swing Landing"
    legs = left
    ReflexController {
        name = SpasticL
        MuscleReflex { target = soleus,  delay = 0.020, KV = 0.050, allow_neg_V = 0 }
        MuscleReflex { target = gastroc, delay = 0.020, KV = 0.050, allow_neg_V = 0 }
    }
}
```

⛔ **B2. The new arm replaces `KV = 0.050, allow_neg_V = 0` with `KF = 0.041989, F0 = 0.10,
allow_neg_F = 0` on both muscles, and changes NOTHING ELSE.**
⛔ **B3. The build ASSERTS the two configs differ in exactly those lines and ABORTS otherwise** — on
the diff, before launch, as `run_replication_r209.py` does.

## 2. C. THE MAGNITUDE AND DUTY ANCHOR — measured, not chosen

⛔ Both parameters come from `scone/force_dose_r213.py` → `paper/FORCE_DOSE_r213.json`: read-only,
no simulation, six control cells `R151C_s101..106`, window [1.00, 13.58].

⭐ **C1. MAGNITUDE.** `dose_r174.py`'s formula, unmodified including the excitation clamp
`min(du, max(0, 1-u))`, with `ce_vel_norm` swapped for `mtu_force_norm`. **The registered KV = 0.050
arm delivers 13.6266 N; KF\* = 0.041989 at F0 = 0.10 delivers the same.** ⛔ **NOT porting 0.050
across — it matches delivered newtons, the principle `dose_r174.py` used to set the weakness match at
×0.892. Registered precedent, not a new invention.**

⭐ **C2. DUTY.** The velocity term is active on **38.4 %** of samples; at F0 = 0.10 the force term is
active on **38.5 %**. ⛔ **DEFECT #48 CONTROLLED FOR THE FIRST TIME.** *#48 (round 14): a term active
on a different fraction of the cycle is an uncontrolled second variable at matched mean. A disclosure
for roughly two hundred rounds; now a parameter value.*

⚠ **C3.** Validation already passed: **the KV side reproduces the registered 13.627 N.**

⛔ **C4. THE `F0 = 0` DOSE-ONLY VARIANT IS A NAMED ALTERNATIVE AND IS NOT RUN** (`KF* = 0.019899`).
*Reason, so a later seat finds a decision and not an omission: it matches dose but leaves the force
term active on 96.1 % of samples against 38.4 % — the #48 confound the primary controls.*

## 3. D. THE THREE CAVEATS — they are what make the anchor usable

⛔ **D1. MATCHED DUTY IS NOT MATCHED PHASE.** Both terms active on ~38 % of samples does not mean the
same 38 %: velocity fires while the fibre lengthens, force while the muscle loads. ⛔ **Phase overlap
was NOT measured. This is the residual gap and the honest limit of the anchor.**

⛔ **D2. `F0`'s SEMANTICS ARE INFERRED, NOT DOCUMENTED.** `du = KF × max(0, F_norm − F0)` is assumed
by analogy with the `KL`/`L0` pattern; no SCONE parameter reference ships on disk — the file
`resources/help/keywords.txt` names `muscle_reflex.txt`, which is not installed. ⛔ **A WRONG
ASSUMPTION INVALIDATES THE DUTY MATCH WHILE LEAVING THE DOSE MATCH INTACT** — the dose figure comes
from `mtu_force_norm` directly, not from SCONE's internal evaluation. ⚠ *Supporting, not decisive: the
vendor's own `230119.H1922v7b3.D20/config.scone` uses `KF`, `F0` and `allow_neg_F = 0` together, and
that flag exists because the term can go negative.*

⛔ **D3. MATCHING BOTH MEAN AND DUTY CONCENTRATES THE SAME NEWTONS INTO A HIGHER PEAK:** peak `du`
rises from **0.0101** at F0 = 0 to **0.0170** at F0 = 0.10.

## 4. E. THE ASYMMETRY THAT DECIDES WHAT A NULL MEANS

⛔ **E1. THE BASE CONTROLLER ALREADY CARRIES A FREE `KF` GAIN ON THESE MUSCLES. IT HAD NO VELOCITY
GAIN.** *From `scone/probe3d_r141/bench_D20/config.scone`, the two ipsilateral blocks in full:*

```
MuscleReflex { target = soleus,  KL = "~0.5<0,10>" L0 = "~0.9<0.5,2>" KF = "~1<-10,10>" delay = 0.035 }
MuscleReflex { target = gastroc, KL = "~0.5<0,10>" L0 = "~0.9<0.5,2>" KF = "~1<-10,10>" delay = 0.035 }
```

⛔ **E2. CONSEQUENCE: the optimiser can partially cancel a KF lesion by REDUCING ITS OWN `KF` — a
single-parameter route that was NOT available against the KV lesion.** *Exact cancellation is blocked:
the lesion runs at `delay = 0.020` against the base's 0.035 and at `F0 = 0.10` against no threshold, so
the two are not the same signal. But near-cancellation is far cheaper for force than for velocity.*

⛔ **E3. THEREFORE A KF NULL IS WEAKER EVIDENCE THAN A KV NULL, BY CONSTRUCTION — said here, before
the result exists.** ⚠ *The measured −20.5 % avoidance already shows this optimiser adapts away from
a provocation it has no direct handle on; against one it does have a handle on, a larger avoidance is
the expected outcome, not a discovery.*

⭐ **E4. THE DELIVERED-DOSE READOUT IS THEREFORE MANDATORY, NOT OPTIONAL:** the arm reports how much
of the injected 13.6266 N survives re-optimisation, by the same method as the KV arm.

## 5. F. BOTH OUTCOMES AT EQUAL WEIGHT, NEITHER RANKED

- **F1. KF PRODUCES A KINEMATIC SIGNATURE WHERE KV DID NOT** → discriminability depends on which
  afferent model is injected. A substantial result about the method.
- **F2. KF ALSO PRODUCES NOTHING** → ⛔ **the licensed sentence is exactly: "a second afferent
  model, cruder than the published one, also yields no kinematic signature."** ⛔ **NOT "independent
  confirmation": ours is a single FIXED gain on two muscles in one leg, against personalised gains AND
  thresholds. A null from a cruder model is weaker, and the document says which it is.**

⛔ **F3. No threshold, no verdict, no ranking of which outcome is more interesting.**

## 6. G/H. Gate G, procedure, and the seed rule for ALL THREE ARMS

⛔ **Gate G, from the `.sto`, BEFORE any endpoint: G1 `history.txt` ≥ 91 lines with the tag
resolving to exactly one such directory; G2 duration ≥ 9.73 s; G3 ≥ 4 admitted cycles in
[1.00, 13.58].** ⛔ **The `.sto` comes from `sconecmd -e` on the final `.par`, a SEPARATE REGISTERED
STEP** — the optimiser writes `.par` only, and skipping it once produced a silent 0-of-54 admission
table; budgeted for the six NEW cells only.

⛔ **H1. Endpoints IMPORT `analyse_ladder_r169.py`'s OWN `rom()`/`cycles_in()` and `pb_r179.py`'s OWN
`meas()`/`rd()`, where the sixteen registered channels are computed. NOT REIMPLEMENTED.**
⛔ **H2. VALIDATE BEFORE TRUST: a published value from `PRIMARYB_RESULT_r179.json` is reproduced
before any new value is computed; ABORT if it is not.**

⛔ **H3. Comparison arm = EXISTING `R151S` cells, REUSED not re-run; control band = EXISTING `R151C`
cells.** ⭐ **The gate rule, fixed now, one clause per arm:**
- ⛔ **H3-a. NEW `KF` cell fails Gate G → that seed drops from BOTH ARMS.**
- ⛔ **H3-b. Reused `R151S` cell fails → same, that seed drops from BOTH ARMS.**
- ⛔ **H3-c. `R151C` control cell fails → it leaves THE BAND**, now min–max over survivors; *below
  FOUR surviving control cells no band is computed and the study aborts.*
- ⛔ **H3-d. EXPLICITLY: a seed dropped under H3-a/H3-b is NOT dropped from the band** — a shared
  reference entering both sides identically; surviving control seeds listed beside the result.
- ⛔ **H3-e. Below FOUR seeds surviving in BOTH arms: UNDERPOWERED, no fraction, counts only.**

## 7. Cost and scope

**6 cells × 204.0 s = 1,224 s serial; concurrency 2 → 612 s = 10.2 min.**
⛔ **No new magnitudes, channels or speeds. Nothing on disk is re-run. The 112 protected directories
yield nothing; ours yield on any conflict. Progress from `history.txt` line counts and directory mtimes
only.**
