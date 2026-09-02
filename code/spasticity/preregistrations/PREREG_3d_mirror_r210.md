# PREREG_3d_mirror_r210.md — one mirrored arm, and what it can and cannot calibrate

**Registered before any cell is launched.** *Parents `PREREG_3d_matched_r174.md`,
`PREREG_3d_replication_r179.md`; procedure `scone/pb_r179.py` → `PRIMARYB_RESULT_r179.json`.*
**One arm. Six cells. Three channel families, never pooled.**

## 0. ⛔ TWO FALSE PREMISES, BOTH THE COORDINATING SEAT'S

⚠ **That seat authorised this on the premise that `tib_ant_r` × 0.892 against `tib_ant_l` × 0.892 is
"sign-opposite a priori by symmetry"; draft 1 wrote it down. False, and the error is that seat's.**
⛔ **Not because ROM is non-negative** (the quantity classified, `(a−c)`, is signed) **but because NO
COORDINATE REFLECTION IS APPLIED** — a lesion relocated on an unchanged model in an unchanged frame.
Mirroring SWAPS which limb's response lands in a named channel: ipsilateral in one arm, contralateral
in the other. Nothing negates. *(Endpoints are per-cycle ROM `degrees(max−min)`; `cycle_time` is a
duration in seconds, not a ROM.)* ⚠ **Second error, same seat, written by draft 2 under a stop sign:
calling `LmR(mirror) = −LmR(original)` an IDENTITY and "tautological". It is neither** — it comes from
six fresh simulations with a different lesion on a different limb and needs result-level symmetry,
which F2 denies. **Demoted to a PREDICTION (B2).**

## 1. ⛔ THREE CHANNEL FAMILIES — split, never pooled

| family | channels | status |
|---|---|---|
| derived `*_LmR` | four, one per paired joint | ⚠ **PREDICTION, not identity: `LmR(mirror) = −LmR(orig)`** |
| ⭐ **paired ROM** | `ankle_angle`/`knee_angle`/`hip_flexion`/`hip_adduction` × `_l`,`_r` | ⭐ **the headline** |
| unpaired | `pelvis_list`, `pelvis_rotation`, `lumbar_bending`, `cycle_time` | no side to swap |

⛔ **B1. The headline fraction comes from the EIGHT PAIRED CHANNELS ONLY.** ⛔ **B2. The four `*_LmR`
stay OUT of it**, reported as their own family, prediction first and result beside it: whether each
mirrored `LmR` is in fact the sign-flip of the original's. ⭐ *A free live check on this model's mirror
symmetry;* ⚠ *`hip_flexion_LmR` opposed at every parent dose, so it has teeth.* ⛔ **B3. Per-family
denominators; NO fraction below FOUR jointly displaced channels — counts instead.** ⚠ *At four it
admits only {0, .25, .5, .75, 1} — the study's whole resolution against a 1.0000 comparator.*
⚠ **B4.** Each `*_LmR` is `o[p+"_l"] − o[p+"_r"]`: sixteen channels, at most **TWELVE independent**.

## 2. ⭐ THE PRIMARY — do the eight paired ROM channels come back PARALLEL?

⛔ **Not "is the floor near zero".** ⭐ **Do the ipsilateral and the contralateral response, which the
mirror puts in the same named channel, move the same way relative to the control band** — empirical,
not guaranteed by symmetry. ⛔ **AND THE COMPARATOR IS 1.0000, NOT 0.89:**
*from the deposit `paper/PARENT_BYFAMILY_r210.json` — `scone/parent_byfamily_r210.py` re-read
`PRIMARYB_RESULT_r179.json`, no simulation, split it by family, counts asserted to sum back to the
published pooled ones.*

| family | W870 | W892 | W915 |
|---|---|---|---|
| ⭐ **paired ROM (the headline family)** | **5/5 = 1.0000** | **4/4 = 1.0000** | **3/3 = 1.0000** |
| unpaired | 1/1 = 1.0000 | 1/1 = 1.0000 | 1/1 = 1.0000 |
| derived `*_LmR` | 2/3 = 0.6667 | 2/3 = 0.6667 | 2/3 = 0.6667 |
| pooled, as published | 8/9 = 0.8889 | 7/8 = 0.8750 | 6/7 = 0.8571 |

⛔ **On the eight paired channels the parent is 1.0000 at every dose; the whole departure from 1.0 in
the published 0.89 / 0.88 / 0.86 is ONE derived channel, `hip_flexion_LmR`, at all three doses — from
the family B2 excludes.** 1. ⛔ **The like-for-like comparator is 1.0000**; draft 2's *"0.89 gains a
scale"* is DELETED, 0.89 not being a paired-channel number. 2. ⛔ **Parent paired denominators are 5,
4, 3** — W892, this dose, sits at B3's floor and W915 below it, where B3 would forbid a fraction.
3. ⚠ **The 0.89 / 0.88 gap is DIFFERENT DOSES, not rounding:** 0.8889 = W870, 0.8750 = W892,
0.8571 = W915; this arm is × 0.892, so its parent figure is 0.88. 4. ⚠ **The pooled figure rests on one
derived channel** (B4).

⛔ **C1. No threshold for "low" versus "high", and NO VERDICT. Both branches — LOW = side-specific
response; HIGH = largely SIDE-INDEPENDENT response — are reported, NEITHER RANKED, as jointly-displaced
counts beside each fraction plus the per-channel opposition list in full. Calibration, not a test.**
⚠ *Draft 2 called the high branch "the more interesting outcome"; REMOVED because a cold read showed
the design cannot support it — it cannot distinguish side-independence from "this statistic rarely goes
low".*

## 3. Design

| | value |
|---|---|
| new arm | **`tib_ant_r` × 0.892**, model edit only |
| seeds | **101–106**, the seeds the existing weak arm uses |
| comparison | existing `R174W892` (`tib_ant_l` × 0.892) cells, ⛔ **REUSED, not re-run** |
| control | existing `R151C` cells, ⛔ **REUSED** — supplies the band |
| depth / speed / warm start | 90 generations, `min_velocity` 1.0, `par/H1922v7b3-TSG3Dv8g-989_fixed2.par` |

⚠ **`bench_D20` = `scone/probe3d_r141/bench_D20`, the in-tree copy of
`scenarios/Benchmarks/230119.H1922v7b3.D20`** (model `H1922v7b3`, 19-DoF). ⛔ **G1. The build asserts
BOTH halves:** *the new model differs from `bench_D20`'s in exactly one line, `max_isometric_force`
under `name = tib_ant_r`; `R174W892`'s differs from the same baseline in exactly one, `tib_ant_l`.*
⚠ *Draft 1 asserted only the first half.*

## 4. Procedure — imported, validated, called with explicit channels

⛔ **E1. `pb_r179.py`'s OWN `meas()` and `rd()` are IMPORTED, not reimplemented.** ⛔ **E2. VALIDATE
BEFORE TRUST: it must first reproduce a published number — spastic × W892 = 8 jointly displaced, 7
parallel, 0.88; if not, the mirrored number is NOT computed and the failure is reported.**
⚠ **E3. Definitions, respecified prose; the imported code is authority for `meas()`/`rd()` ONLY, while
the displaced / opposed / fraction logic is written fresh here and E1's warning applies to it:** band =
min–max of the surviving `R151C` cells per channel; **`c` is the CONTROL MEAN**
(`cm = float(np.mean(c))`), inert while inside the band, and it is; displaced = arm mean outside the
band; opposed = both displaced and `(a−c)·(b−c) < 0`; fraction = not-opposed over jointly displaced.
⛔ **E4. The headline computation RECEIVES THE EIGHT PAIRED CHANNEL NAMES AS AN EXPLICIT ARGUMENT,
never a default** — *E2 runs the same path over the pooled number, so pooling is one default away.*

## 5. Seeds and gates — the shortfall rule, decided now, for ALL THREE ARMS

⛔ **Gate G, from the `.sto`, before any endpoint: G1 `history.txt` ≥ 91 lines with the tag resolving
to exactly one such directory; G2 duration ≥ 9.73 s; G3 ≥ 4 admitted cycles in `[1.00, 13.58]`.**
⛔ **The `.sto` comes from `sconecmd -e` on the final `.par`, a separate registered step.** ⚠ **Against
§7's "nothing on disk is re-run": the replay exists — `R174W892_s101…s106` and `R151C_s101…s106` each
hold 6 `*.par.sto`**, so Gate G reads those and `sconecmd -e` is budgeted for the six NEW cells only.

⭐ **D. THE ARMS ARE SEED-MATCHED; THE RULE IS FIXED NOW, one clause per arm:**
- ⛔ **D-a. MIRRORED cell fails Gate G → that seed drops from BOTH ARMS.**
- ⛔ **D-b. Reused `R174W892` cell fails → same, drops from BOTH ARMS** *(G2/G3 unasserted there, D2).*
- ⛔ **D-c. `R151C` control cell fails → it leaves THE BAND**, now min–max over survivors; *below FOUR,
  no band is computed and the study aborts.*
- ⛔ **D-d. Explicitly: a seed dropped under D-a/D-b is NOT dropped from the band** — *a shared
  reference entering both sides identically; surviving control seeds listed beside it.*
- ⛔ **Below FOUR seeds surviving in BOTH arms: UNDERPOWERED, no fraction;** at 4 or 5, computed on the
  reduced common set, seeds listed, reused cells of dropped seeds discarded.
- ⛔ **If any seed drops, the PARENT figure is RECOMPUTED on the surviving seeds**, pooled and
  paired-only, so both sides rest on the same cells. ⚠ *At six, §2's deposit stands.*

⚠ **D1.** The per-tag assertion applies to the SURVIVING seed set: **runner and analysis take the seed
set as an input argument, not the hard-coded `range(101, 107)`.** ⛔ **D2. G1 status of the six reused
`R174W892` cells: 6 of 6 — G1 ONLY, NOT Gate G.** *Basis: `rd()` resolved them (`assert len(g) == 1`
over directories with ≥ 91 `history.txt` lines) and `meas()` returned for all six. G2 and G3 are
unasserted there, evaluated fresh for all three arms, D-a/-b/-c following.*

## 6. ⛔ WHAT THIS DOES NOT ANCHOR

⛔ **F1. A mirror is the same mechanism relocated, not an opposite one** — *the same-axis opposite of
`tib_ant_l × 0.892` is `tib_ant_l × 1.12`, same side and sign-reversed parameter. This anchors
side-dependence, not mechanism reversal; its fraction is not the floor r174's ceiling needs.*
⛔ **F2. Symmetry is asserted at the MODEL-EDIT level ONLY** — *result-level symmetry would need a
symmetric base model, warm start (both arms share `H1922v7b3-TSG3Dv8g-989_fixed2.par`) and band; none
is established.* ⛔ **F3. The band is NOT mirror-matched** — *separate `_l`/`_r` min–max statistics,
differing in width.* ⚠ **F4.** *A range statistic over n = 6, driven by two extreme cells, widening
with n.* ⚠ **F5.** *The ceiling pools 35 channel-comparisons, this floor is one arm-pair over at most
eight, and neither is given uncertainty.*

## 7. Cost and scope

**6 cells × 204.0 s = 1,224 s serial; concurrency 2 → 612 s = 10.2 min.**
⛔ **No new magnitudes, channels or speeds. Nothing on disk is re-run. Concurrency 2. The 112 protected
directories yield nothing; ours yield on any conflict. Progress from `history.txt` lines and mtimes.**
⛔ **`tib_ant_l × 1.12` is a RECORDED CANDIDATE for a future registration and nothing more** — *the
same-axis opposite of `tib_ant_l × 0.892`; it, not a mirror, would anchor mechanism reversal.* ⛔ **Not
drafted, costed or built here.**
