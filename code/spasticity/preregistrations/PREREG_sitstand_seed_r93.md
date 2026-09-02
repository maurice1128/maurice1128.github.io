# PREREG_sitstand_seed_r93.md — the sit-to-stand seed run, stop rule registered before it runs

**Registered 2026-08-05, round 93. NOT LAUNCHED at the time of hashing.** Addendum to
`PREREG_sitstand_r91.md` (`59f1c341…`), which stands unmodified.

**Where this document and any script disagree, THIS DOCUMENT DECIDES.**

---

## 1. WHAT ROUND 92 ESTABLISHED, AND WHY THIS RUN EXISTS

The feasibility probe returned **terminal and achieved optimum 101.2070** against the gait corpus's
**0.59–0.68** — **148.8× the worst gait cell.** Registered criterion 3 fired and the verdict was
**NOT ATTAINABLE at that budget from cold.**

**The diagnosis, written into the probe scenario before it ran:** `ResultH0914Gait10.par` is a
solution vector for the `GaitStateController` and the sit-to-stand scenario runs a
`ReflexController`; *loading it would not be a warm start, it would be noise indexed into the wrong
parameters.*

⚠ **Therefore 90 generations from cold on a fresh controller is not a test of the task — it is a test
of the budget.** **The gait corpus never had to solve its task cold; it inherited a converged seed.
Sit-to-stand has none. This run builds one.**

---

## 2. THE RUN

- **One control cell, NO LESION.** `DR2K000` conditions, unlesioned.
- **`max_generations = 1000`, `min_progress = 0`.**
- **Same controller** (`ControllerReflexBalance_H0914M.scone`, the recorded deviation) **and same
  measure** as the probe, with the corrected `min`/`max` `DofMeasure` schema.
- **New tag.** No reuse of `STS_PROBE_T15b`.
- **Trajectory reported at generations 250, 500 and 1000** — not the endpoint alone.

---

## 3. ★ THE STOP RULE, FIXED BEFORE THE RUN SO THE OUTCOME CANNOT BE RENEGOTIATED

The gait reference is **0.59–0.68**; one order of magnitude above its worst cell is **≈ 6.8**, and
the registered threshold is stated as **below 7.0**.

| outcome | criterion | consequence |
|---|---|---|
| **CONVERGED** | terminal best fitness **< 7.0** | **Freeze that `.par` as the sit-to-stand `init_file`.** The study becomes launchable at 60 cells with a real warm start. |
| **IMPROVING BUT SHORT** | terminal ≥ 7.0, and still descending at 1000 — the last 100 generations show a fall of more than 5 % of the run's total improvement | **Report the trajectory and the projected budget. DO NOT EXTEND SILENTLY.** Any extension is a new registered decision. |
| **FLAT** | terminal ≥ 7.0 and the last 100 generations fall by 5 % or less of the run's total improvement | **SIT-TO-STAND IS NOT ATTAINABLE with this controller and measure at any budget this project can afford.** A result, not a failure — it closes the task as G4's fallback closed the 5° tier. |

⚠ **"Flat" and "improving but short" are separated by a stated numeric criterion, computed from the
run's own history, so neither this seat nor the coordinator chooses which one applies after seeing
the curve.**

---

## 4. WHAT THIS RUN DOES NOT RESOLVE — kept open in the record

1. **Whether the shipped jump crouch is the right initial state for a rise.** It was chosen for its
   +25° dorsiflexion, not tuned for standing, and it is not varied here.
2. **The gait-state-scoped injection against a stateless balance controller.** Untouched, untested,
   and **it is the thing that decides whether a lesioned cell can exist at all.** ⚠ **If the seed
   converges, that becomes the next blocker and is solved in that order — not before.**

---

## 5. PRE-FLIGHT GATES, AND ONE NOW STANDING FOR EVERY SCENARIO

- **G5 tag collision**, against a results root holding 490+ directories of which **43 already carry
  `" (1)"`.**
- ★ **THE UNUSED-PROPERTIES GATE, ADOPTED AS STANDING FOR EVERY SCENARIO THIS PROJECT LAUNCHES —
  not only new ones.** Round 92's probe built a model, reported 28 dimensions and advanced
  generations while `DofMeasure > position` was **wholly unconsumed**, so the rise target contributed
  nothing. *A property SCONE does not consume is a claim the scenario makes and the simulator
  ignores.*
  ⚠ **`scone/check_unused.py` already existed for exactly this, and the slope study gated on it at
  G1/G2 via a discarded short launch. The instrument was there; running it on a NEW SCENARIO TYPE is
  what was missing.**
- **Concurrency: total `sconecmd` at most 3, `BELOW_NORMAL`, abort if already above 2, this run
  killed first if the user's own study appears, Tier 2 never touched.**
