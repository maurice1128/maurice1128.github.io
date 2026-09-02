# Formally abandoned experimental arms

Written 2026-07-27. Recorded explicitly because an undeclared abandonment previously sat as a
phantom prerequisite in this project and produced defect #21: an arm that everyone assumed was
"still coming" but that nobody was running, which blocked decisions that did not actually depend
on it.

**An arm listed here is not paused, not deprioritised, and not waiting for compute. It is dead.
Do not restart it. If a future argument requires one of these, the argument is wrong.**

---

## 1. `UPL05` / `UPL10` / `UPL15` — uphill continuation ladder

**Status: ABANDONED. Do not restart.**

The runs themselves succeeded — 0.616 / 0.646 / 0.690, converged, and the continuation-ladder
technique (each rung warm-started from the one below) is a genuine technical result worth keeping
as a note. The arm is dead for two independent reasons:

1. **Wrong walking speed.** Verified from the scenario files: `UPL*` carry `min_velocity = 0.8`
   (signature `S08W`), while *every* other condition in the project — level, downhill, and all
   impairment arms — carries `min_velocity = 1.0` (`S10W`). Walking speed is the strongest single
   determinant of walking cost (r = −0.89 in patients). A three-point task axis with a speed jump
   at one anchor lets a **speed** effect enter as a **task** effect. Every uphill run in this
   project's history is at reduced speed because uphill does not converge at 1.0 m/s.
2. **No impairment models exist.** Every `UP*` result directory carries no `.R4.` token, i.e. **no
   injected reflex**, and `uphill_ladder.py` builds its rungs from the intact `H0914M_osim4.osim`
   only. There is no uphill spastic model and no uphill weakness model. The arm was never a
   two-mechanism comparison; it was three healthy gaits on a slope.

**Consequence, recorded so it is not rediscovered as a surprise:** the slope pre-registration's
original three-task axis (downhill −2° / level / uphill +1.5°) was **not executable**. It has been
amended to level 0° / downhill −2° / downhill −5°, all at `min_velocity = 1.0`. Replacing uphill
with a second downhill grade is strictly better — a monotone trend at constant speed is a cleaner
velocity-dependence test than one containing a speed jump, and downhill is the mechanism-relevant
direction (it raises plantarflexor stretch velocity at loading).

## 1b. `RD2*` / `RE2*` — downhill 2° task arm

**Status: ABANDONED 2026-07-27. Do not restart.**

This is arithmetic, not fatigue. The downhill panel is **6 conditions, 3 spastic / 3 non-spastic**.
Exact enumeration over condition-level label assignments gives an attainable p-floor of
**1/C(6,3) = 0.05 one-sided, 0.10 two-sided** — reached only if the true labelling is the unique
strict maximum. **The experiment cannot clear α = 0.05 two-sided even at perfect separation.** It
was underpowered by construction before a single feature was extracted.

The runs were also dead: `history.txt` untouched for 155–259 minutes across three consecutive
watchdog rounds, and no `sconecmd` process on any of them.

**Consequence, recorded so it is not rediscovered:** with uphill already dropped for the
`min_velocity = 0.8` speed confound and downhill now abandoned, **the pre-registered slope /
velocity-dependence experiment has no executable task axis and is not runnable as designed.**
`paper/PREREGISTRATION_slope_velocity_dependence.md` is therefore dormant, not pending. Reviving it
would need ≥4 conditions per arm at each of ≥3 task levels, all at `min_velocity = 1.0` — a larger
experiment than anything run so far.

## 1c. `DSPAS005_*` / `DSPAS01_*` — batch-matched spastic arm at `max_generations = 90`

**Status: KILLED 2026-07-27 (6 processes). Design disproved.**

Launched to close blocker R10-2 — the class label being perfectly predictable from the optimizer's
stopping rule. Four of six were stuck at fitness **9.4–13.5** (the falling regime) at generation
30–36, and this was the *predicted* outcome:

- a healthy controller with the reflex added falls at **KV ≥ 0.01** (`scone_naive_ladder.json`);
- the original `SPAS01` runs needed **242–337 generations** to climb out of that regime.

So `max_generations = 90` cannot produce a *converged* spastic arm. **Matching the budget therefore
guarantees not matching convergence.** That is a property of the problem, not a bad choice of
number, and it is a real result about this experimental design.

**But it kills only one direction of the fix.** It says: do not clamp the spastic arm down to the
non-spastic arm's budget. The inverse is untested and cheap — **re-run the NON-spastic arm uncapped
under the class-1 settings**, letting depth equalise at the spastic arm's natural depth instead of
below it. The non-spastic arm converges cheaply, so this is affordable.

**The level-ground dataset is therefore NOT void.** It is void only if that inverted extension also
fails. That test has not been run.

## 1d. `CMW70_*` / `CMW80_*` — heavy-weakness half of the cost-matched contrast

**Status: CLOSED 2026-07-27 on relevance, not failure. Do not restart.**

These ran correctly and produced usable gaits (TA −70 % and −80 %, real equinus at −3.96° and
−10.51°). They are closed because the design they belong to was withdrawn: cost-matching is
conditioning on a **descendant of the gait trajectory**, which creates a spurious path rather than
removing one, and the analytical equivalent had already been done at zero compute (residualizing
the waveform on fitness gives 0.143, exact p = 1.0000).

They are also no longer running — no live `sconecmd`, `history.txt` ages 92–196 minutes, at
generations 80/72/89/57 against a 90 cap. **I previously reported them as progressing; that was
wrong.**

Recorded explicitly rather than left stalled, because an undeclared stall is exactly the pattern
that produced defect #21 — an arm nobody was running but everyone assumed was coming.

**Retained value:** `CMW80` remains the only pure-weakness condition producing equinus comparable
in magnitude to the strongest spastic condition, so its converged gaits stay available as data.
What is abandoned is the cost-matched *contrast*, not the runs.

## 2. `B*` — asymmetric-controller (`symmetric = 0`) arm

**Status: ABANDONED for clinical claims. Do not restart.**

This is not a compute decision. Round 8 (Part D2) measured the arm's *healthy baseline* as
non-physiological: intact limb +8.40° / +11.18°, `BHEALTHY_s2` affected +9.00°, against a
literature range of roughly 0 to −2°. **Better optimization of an abnormal gait is still an
abnormal gait.** The runs reached generation 81–99 at fitness 0.609–1.097 and then stalled; the
stall is irrelevant, because finishing them would not have made the baseline physiological.

Its stated purpose also lapsed independently. `symmetric = 0` was justified as necessary so the
controller could adapt asymmetrically to a unilateral lesion. Rounds 9 and 10 then showed that the
**intact limb classifies at least as well as the affected limb**, which removes the premise that
the discriminative signal is a lateralised adaptation at all.

**Consequence:** `symmetric = 0` must stop appearing as an outstanding prerequisite. Where an
argument previously read "this needs to be rechecked under `symmetric = 0`", the correct reading is
now that the asymmetry story is not supported and the check is not owed.

**Retained caveat, unchanged:** the models in use *are* `symmetric = 1`, so the controller cannot
compensate asymmetrically, and any asymmetry a classifier finds is a passive mechanical consequence
rather than a neural response. That is a **limitation to state in the write-up**, not a reason to
revive this arm.

## 3. `TON005_*` / `TON01_*` — activation-matched tonic control

**Status: HELD, NOT abandoned — but no fourth launch until diagnosed.**

Three launches, three failures: generation 4–7, fitness 76.1–95.0, i.e. the model cannot walk at
all. Relaunching a fourth time without a diagnosis would be repeat-error (c) — treating a silently
failing experiment as though more attempts will fix it.

**⛔ The diagnosis is already done and needs no replay. The round-13 instruction below was wrong.**

`opt_tonic/TON01_s1.scone` sets `C0 = 0.4054` on both `soleus_l` and `gastroc_l`; `TON005_s1`
sets `0.3266`. `tonic_targets.json` shows these were taken as the source runs' **mean activation** —
not as the reflex's contribution. Applying the verified-exact **2.000×** delivery factor (measured
on `C0` terms specifically), the constant offset actually delivered was **0.8108** and **0.6532**
of maximum excitation, permanently, on both plantarflexors, against a clamp ceiling of 1.0.

**The arm could not walk, and the reason is on the face of the config.** No replay required.

*Superseded instruction, kept for the record:* ~~"replay the generation-0 `.par` and determine
whether the model falls within the first stride"~~ — issued at round 13, superseded at round 17.

The arm retains real scientific value if it can be made to walk: it is the control that separates
*velocity dependence* from *added activation cost*, which is the distinction the whole project
turns on.

## 4. `MMIX40S01` / `MMIX40S02` — mixed at higher severity

**Status: ABANDONED. Do not restart.**

Fitness 14.0–62.9 across generations 22–78 — never converged, i.e. never learned to walk.
`MMIX20S01` (0.953 / 0.987 at generation 103 / 114) is the only usable mixed condition. Mixed
conditions are in any case excluded from the primary two-class test by pre-registration and are
reported descriptively only.

## 5. Cost-matched spastic arm `CMS020_*` / `CMS030_*`

**Status: STOPPED mid-run 2026-07-27, and abandoned.**

Four processes stopped. Verified from raw `.sto` (`scone/verify_equinus.py`): KV 0.02 is **+3.68°
more dorsiflexed than healthy** and KV 0.03 is −0.50° (ambiguous). These are the two *least*
equinus-producing conditions in the entire dataset. They cannot support the contrast they were
launched for, and the cost-matching design they belong to was independently shown to be collider
conditioning — cost is a descendant of the gait trajectory, not a common cause of condition and
gait, so conditioning on it creates a spurious path rather than removing one.

**`CMW70_*` / `CMW80_*` were NOT stopped and are NOT abandoned.** They produce real equinus
(−3.96° and −10.51°), and TA −80 % is one half of the only equinus-matched pair currently in the
data.

## 6. `EQS010_s1/s2/s3` + `EQW60_s1/s2/s3` — equinus ladder rung 0

**Recorded by the standing watchdog, 2026-07-28, at the coordinator's request.** The kill was ruled
at council round 24 and had been outstanding eight rounds; this is the trail entry that was missing.

**State at time of death** (read from raw `.par`; no `sconecmd` process for any of the six):

| tag | `.par` | `.sto` | max gen | last `.par` write |
|---|---|---|---|---|
| EQS010_s1 | 5 | **0** | 89 | 663 min |
| EQS010_s2 | 7 | **0** | 87 | 665 min |
| EQS010_s3 | 4 | **0** | 72 | 765 min |
| EQW60_s1 | 2 | **0** | 84 | 681 min |
| EQW60_s2 | 2 | **0** | 51 | 831 min |
| EQW60_s3 | 2 | **0** | 86 | 698 min |

**Why abandoned, not restarted:**

1. **The spastic arm carries the 2× injection defect.** `EQS010` was generated before the
   `legs = left` + side-free-target fix, so its declared KV 0.10 was delivered at effective 0.20.
   Replaying it would measure a superseded condition.
2. **No phenotype was ever produced.** All six sat at `nsto = 0` for eight consecutive council
   rounds. `.sto` files come from an explicit replay, never from optimization, and that replay was
   never run. The arm consumed compute for eleven to fourteen hours and yielded no measurement.
3. **Its purpose is subsumed.** Rung 0 existed to give matched-depth multi-seed equinus measurements
   at KV 0.10 and TA −60 %. That is exactly what the planned dose–response characterisation at true
   1.0× delivery will provide, on a generator that is now verified.

**What is retained:** the `.par` files stay on disk. They are a valid record of a converged
optimization under a *known and characterised* 2× delivery, and may serve as a warm-start source or
as a historical comparison — provided any use states the effective gain (0.20, not 0.10).

**What must not be done:** do not quote any phenotype from this arm. None was ever computed, and any
computed later would carry the 2× defect without the label saying so.
