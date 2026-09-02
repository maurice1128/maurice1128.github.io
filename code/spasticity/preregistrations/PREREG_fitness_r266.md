# PREREG_fitness_r266.md — can the two arms be compared at all?

**Written BEFORE the fitness table was assembled, round 266.** *The analyst has been told, by a
first-time reader, that control ≈ 0.987, weakness 1.004–1.052 and the reflex arm 19.381–38.532. That
much is already seen and is recorded here rather than presented as a prediction. The conditioning
analysis below has not been run.*

---

## 1. The question

Every reflex-versus-weakness claim in this project assumes the arms are comparable optimisation
outcomes. **They may not be.** If the reflex controller was truncated mid-descent at ~31× the control's
objective while the weakness controllers converged back to control level, then any kinematic difference
between the arms is confounded with **how well the controller was trained**, and that confound is
prior to lesion type, magnitude, site and antagonism.

## 2. What is computed

1. **Terminal objective for all 48 analysed cells** — `OPTDIST_r233.json` → `cells[].fitness`, and
   independently each cell's `history.txt` last-generation `best_fitness`.
2. **The same for all 24 gate-failed cells** (KV 0.150, KV 0.400), *plus their generation-0 values*,
   so the "never left the starting basin" claim is visible rather than inferred.
3. **Descent over the final ten generations** and terminal `fitness_progress`, per cell — a converged
   run is flat, a truncated one is not.
4. **Overlap of the objective distributions** between the reflex arm and the weakness ladder.
5. **Conditioning**, if and only if step 4 permits it: does any reflex-versus-weakness difference —
   yaw, swing-phase deviation, phase of peak deviation, channel displacement — survive adjustment for
   terminal objective?

## 3. ⛔ THE READING THAT IS REGISTERED IN ADVANCE AS MOST LIKELY

⛔ **CONDITIONING MAY BE IMPOSSIBLE, AND IF SO THAT IS THE RESULT, NOT A FAILURE TO OBTAIN ONE.**
*If the objective ranges do not overlap — 1.05 against 19.4 — there is **no common support**, and a
regression across them is **extrapolation, not adjustment**. No statistical technique bridges a gap
with no overlap.*

⭐ **If that is the answer it will be stated in those words: the two arms cannot be compared, because
the design required reflex cells optimised to control-level objective and those do not exist.** *That
is a statement about the corpus, and it subsumes every other confound rather than adding to them.*

## 4. The other readings

- **A — the ranges overlap enough to condition, and the reflex/weakness differences survive.**
  *Reported; the objective confound is measured and excluded.*
- **B — they overlap enough to condition, and the differences do NOT survive.** ⛔ *Then the corpus
  cannot support a lesion comparison at all, and that is the paper.*
- **C — no common support.** *Section 3. The most likely outcome.*
- **D — the deposited `fitness` and the `history.txt` terminal value disagree.** *Then neither is
  trusted and the discrepancy is reported before anything is built on either.*

## 5. Consequences already fixed, whatever the numbers

- ⛔ **A fifth non-comparability enters §M3**: *the weakness arms were re-optimised back to
  control-level objective and the reflex arm was not.*
- ⛔ **§7c's gain ladder must be re-read as a ladder in optimisation outcome** unless the KV 0.150 and
  KV 0.400 cells show real descent. *If KV 0.400 cells sit within a hair of their generation-0 value,
  "12 of 12 terminate at 0.690–0.700 s" is a measurement of optimiser failure, §7c.1's "cleanest datum"
  claim is withdrawn, and §7c.3's "the gate selected its own conclusion" acquires a competing reading
  that cannot be dismissed: **Gate G excluded cells whose controller was never trained, which is what a
  gate is for.***
- ⛔ **The survivor-bias direction argument in §7c.2 is withdrawn** if the surviving KV 0.150 cells are
  the converged ones rather than the least destabilised ones. *The sign of that selection on yaw would
  be unknown.*
