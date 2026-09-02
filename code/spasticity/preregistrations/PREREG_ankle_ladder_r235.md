# PRE-REGISTRATION — the second opposed channel on the extended ladder (round 235)

Registered **before any `ankle_angle_LmR` value on the extended ladder was computed**. Hashed with a
`.sha256` sidecar before extraction.

---

## 1. Why

At **r151** the registered `(L−R)` family produced **TWO** separating laterality endpoints, with
**identical statistics**:

| endpoint | S mean | W mean | AUC | p_raw | p_adj ×16 |
|---|---|---|---|---|---|
| **`ankle_angle_LmR`** | −0.179 | +2.308 | 0.000 | 0.002165 | **0.0346** |
| **`hip_flexion_LmR`** | −2.029 | +0.417 | 0.000 | 0.002165 | **0.0346** |

`PREREG_3d_reopt_r151.md` §4 registered *"**Asymmetry:** for each, `(L − R)`, signed"* — the family was
**registered before the run**; these four endpoints had simply never been computed and r151 restored
them. **So the family was predicted. The narrowing from two channels to one was not** — it was made
afterwards on window-sensitivity found in these same cells.

⛔ **Neither r221's permutation null nor r223's blind leave-one-seed-out prices that narrowing**, because
both operate on an already-narrowed channel set.

⚠ **And `ladder36_r228.py` computed all sixteen channels but deposited only
`per_seed_hip_flexion_LmR`.** The comparison this registration makes was available at r228 and was not
kept.

## 2. What is run

**The r228 analysis, on `ankle_angle_LmR`, exactly as it was run on the hip channel.** Read-only; no
simulation.

- Endpoint: `rom(ankle_angle_l) − rom(ankle_angle_r)`, where `rom` is the mean per-cycle **peak-to-peak
  excursion** — `ladder36_r228.py`'s definition (its lines 24–43), transcribed and asserted against the
  source. **`ladder36_r228.py` is registered and is NOT edited.**
- Window **[1.00, 9.73]**, left heel-strike cycles fully inside, last dropped, `v[a:b+1]` inclusive.
- `.sto` selection: `sorted(glob("*.par.sto"))[-1]`, r228's own rule — verified at r232 to select the
  same file as lowest-field-3 in all six spastic cells.
- Arms: `R151C`, `R151S`, and all six weakness severities ×0.800…×0.950, six seeds each.
- Reported: per-seed values, per-severity disjointness, **pooled 6-vs-36**, seed-level gap, and the
  **exhaustive** permutation null (924 assignments) at each severity, familywise over the same channel
  family r228 used.

## 3. ⛔ The three readings, registered before looking

**TWO-CHANNEL — `ankle_angle_LmR` is also disjoint 6-versus-36.**
⭐ **The honest headline becomes two laterality endpoints separating, not one, and that is STRONGER
than the current claim, not weaker.** Two channels that reverse sign between lesion types is a
coherent pattern; one channel of sixteen is a pick that needs a permutation null to defend.
⚠ **And the ordering follows the mechanism: the lesions act AT THE ANKLE** — plantarflexor reflex and
dorsiflexor weakness, both left-sided. **An ankle laterality channel separating is the LESS surprising
of the two, and the hip is the compensation.** If both hold, the site is reported before the
compensation, and the paper must record that it has been reporting the compensation while suppressing
the site.

**NARROWING-JUSTIFIED-IN-SAMPLE — the ankle channel separates at the matched severity but fails across
the ladder.** The narrowing was correct, **but on a criterion discovered in these cells**, and the
paper states it as in-sample rather than as a property established independently.

**NARROWING-CLEAN — the ankle channel fails outright on the extended ladder.** The narrowing was right
and the record simply shows the path.

**Reported under every reading:** that the registered analysis found two separating laterality
endpoints at r151 with identical statistics, that the narrowing to one was made on grounds found in
these cells, and that **neither selection test addresses it.**

## 4. What this decides downstream

⛔ **The 2D design is held until this returns.** A rung requiring *"the hip channel separates and the
others do not"* **would have failed on the 3D data itself**, where `ankle_angle_LmR` separated at the
same p. **What the 2D experiment should test depends on whether 3D showed one channel or two.**

## 5. Deposit

`paper/ANKLE_LADDER_r235.json` — per-seed values for all eight arms, per-severity and pooled
disjointness, gaps, exhaustive nulls, and the reading the rules select. Script
`scone/ankle_ladder_r235.py`, recording its own sha256, this registration's, and
`ladder36_r228.py`'s.

⛔ **Where this document and the code disagree, the RUN IS VOID.**
