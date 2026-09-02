# PREREG_3d_replication_r209.md — is the hip sign reversal seed-dependent?

**Registered before any cell is launched.** Result under test: `MATCHED_RESULT_r174.md`. Parents:
`PREREG_3d_matched_r174.md`, `PREREG_3d_replication_r179.md`. Draft 2; draft 1 (`.bak_r381_`) was
rejected on a blind read and is superseded, not amended.

---

## 1. What this study is

`MATCHED_RESULT_r174.md`'s hip finding rests on one spastic arm of six cells. This study
re-optimises that arm on six seeds never optimised or analysed before, and asks whether the
`hip_flexion_LmR` result comes back.

**It tests seed-dependence and nothing more.** The new cells share with the original arm the warm
start `par/H1922v7b3-TSG3Dv8g-989_fixed2.par`, the model `models/H1922v7b3.hfd`, the initial state
`data/InitStateH0918Gait10ActA.zml` — itself asymmetric between the legs — and the left-only lesion
(`legs = left`), measured on a left-minus-right channel. The seed perturbs the search, not the
starting point.

**So this does not answer the frozen-arm objection.** The compensation explanation — that the
left-minus-right displacement follows from a left-only lesion on an already-asymmetric initial
state, rather than from spasticity as such — is untouched by reseeding and stays open whichever way
this comes out. An earlier claim by the coordinating seat to the user, that new seeds would turn one
observation into a replication, was too strong; that correction is that seat's to carry, and the
scope above supersedes it.

---

## 2. Endpoint, defined here

The endpoint is `hip_flexion_LmR` = **`rom(L) − rom(R)`**, in degrees.

For one cycle and one joint, `rom() = math.degrees(max − min)` over that cycle's samples. `rom(L)`
and `rom(R)` are those per-cycle values for `hip_flexion_l` and `hip_flexion_r`; the cell's value is
their difference averaged over the cycles admitted by gate G3. Implementation of record:
`analyse_ladder_r169.py:163`.

**It is a difference of per-cycle ranges of motion — not of joint-angle levels, and not a global
range over the trial.** A first provenance attempt used levels and reproduced nothing; global range
is the r145 defect forbidden by `PREREG_3d_reopt_r151.md`:61–63.

---

## 3. The anchor, and the two preconditions that were tested

The original spastic arm is `R151S_s101..s106` (r169's `S050` cells, KV 0.050):

| seed | `hip_flexion_LmR` | t_end | n_cycles |
|---|---|---|---|
| 101 | −1.575016 | 17.85 | 9 |
| 102 | −1.558770 | 14.96 | 9 |
| 103 | −2.858404 | 13.58 | 9 |
| 104 | −1.349297 | 16.94 | 9 |
| 105 | −1.628149 | 14.27 | 9 |
| 106 | −3.203713 | 14.82 | 9 |

mean **−2.0289**, SD (n−1) **0.7897**, range [−3.2037, −1.3493] — reproducing r174's reported −2.03
and −3.20 to −1.35.

**3a. Provenance was tested and passed.** Replaying the six original `.par` files through
`sconecmd -e` — the path the new cells will use — and reducing with `analyse_ladder_r169.py`'s own
`rom()` and `cycles_in()` reproduces all six archived values to within **1.42e−14**; six of six
match. Deposit: `PROVENANCE2_r209.json`.

**3b. The gate asymmetry is moot, as a checked fact.** Gates G1–G3 postdate the r169 cells, so a
naive comparison would filter the new arm and not the old. All six originals were run through the
gates and all six pass: `t_end` 13.58–17.85 against ≥ 9.73 s, 9 admitted cycles each against ≥ 4,
all complete. Gating removes no original cell, the anchor is unchanged, and the comparison is
filtered-to-filtered.

**3c. The anchor is bimodal — reported, not used as a criterion.** Four cells sit near −1.5
(−1.3493, −1.5588, −1.5750, −1.6281) and two far out (−2.8584, −3.2037). **The mean −2.0289 is
realised by no cell; it falls in the gap between the clusters,** and no statement that "the mean
reproduced" should be read without that. No criterion below is built on the clusters — the band of
§5 is calibrated on the observed SD, which already contains the bimodality.

---

## 4. Design — the only difference from the existing arm is the seed

| | value | source |
|---|---|---|
| arm | spastic, KV 0.050 fixed, `legs = left`, `allow_neg_V = 0` | `bench_D20_spasL` block |
| seeds | **201, 202, 203, 204, 205, 206** | §4a |
| `max_generations` | 90 | `R151S_s101` config line 3 |
| `min_velocity` | 1.0 | `R151S_s101` config line 351 |
| warm start | `par/H1922v7b3-TSG3Dv8g-989_fixed2.par` | line 8 |
| model | `models/H1922v7b3.hfd`, unmodified | — |
| state | `data/InitStateH0918Gait10ActA.zml` | line 14 |
| weak arm | **existing `×0.892` cells, reused, not re-run** | on disk |

**4a. Seeds 201–206 are new.** `.R101`–`.R116` are in use across the corpus; 201–206 appear nowhere.
The check enumerates the `.R<n>` suffix of result-directory names, so it would miss a run whose
config seed differs from its directory tag, or one whose directory was deleted.

**4b. Config assertion, and the procedure if it fires.** The build asserts that each new scenario
differs from `R151S_s101`'s archived config in exactly the seed line. **If it fires: the build aborts
before launching any cell; the differing lines are appended verbatim to this file under a dated
heading; nothing is launched under this registration; and a launch may proceed only under a new
registration file with a new r-number that names the difference.** Nothing is salvaged in place.

---

## 5. What counts as reproduction — one condition, fixed before the data

The tested quantity is a difference between two 6-cell arm means, so the tolerance is the standard
error of that difference, not the spread of individual cells:

```
SD (n-1, individual cells)                0.7897
SE_diff(n_new) = 0.7897 * sqrt(1/6 + 1/n_new)
band(n_new)    = -2.0289 +/- 2 * SE_diff(n_new)
```

⛔ **THE BAND IS A FUNCTION OF THE NUMBER OF SURVIVING NEW CELLS, AND ALL THREE REACHABLE VALUES ARE
REGISTERED HERE so that none is derived after seeing how many survived:**

| n_new | SE_diff | band |
|---|---|---|
| **6** | 0.4559 | **[−2.941, −1.117]** |
| **5** | 0.4782 | **[−2.985, −1.073]** |
| **4** | 0.5097 | **[−3.048, −1.009]** |

*Below n_new = 4 the arm is UNDERPOWERED (§6) and no band applies.*

**REPRODUCES iff the new arm mean lies within band(n_new).** An arm at a quarter of the original
magnitude fails at every n_new. Draft 1's band, mean ± 2 SD of individual cells = [−3.6082, −0.4496],
is withdrawn: it could return only one answer, and the quarter-magnitude arm passed it.
⚠ *Its width, stated in one unit rather than two: **3.1586 wide = 6.93 SE_diff**, against this band's
**1.8236 wide = 4.00 SE_diff**. An earlier version of this paragraph said "4.90 SEM wide", which was
two errors in one phrase — a HALF-width labelled a width, and draft 1 quoted in SEM-of-the-mean while
draft 2 was quoted in SE_diff, so the two were not comparable as printed. The figure came from the
requirements file supplied to this seat.* **The individual-cell SD is not a tolerance anywhere
here; it appears only as the input to the SE above.**

**5a. The displacement condition is dropped.** Draft 1 additionally required the arm mean to lie
below the control floor −0.3671. The band's upper edge is −1.117, so that condition is entailed by
the magnitude condition and cannot change any verdict; it is dropped rather than kept as decoration.
The control band `[−0.3671, +0.2900]`, fixed at r169 §0, is still printed with the result for
context.

**5b. Denominator rule.** The arm mean is taken **over the cells that pass the gates**, not over all
six. All six originals pass (§3b), so the rule is symmetric between arms and anchor and band are
computed the same way. The number of passing cells is reported with the mean.

⭐ **REPORTING REQUIREMENT, registered here and not a decision rule: the SIX NEW PER-CELL VALUES and
the NEW ARM'S SD are deposited and printed beside the verdict, whatever it is.** *The criterion is
unchanged. **The reason is that a mean-only test is blind to cluster reshuffling: with the anchor's
4-near/2-far structure (§3c), every composition from 0 to 5 far-out cells lands inside the band, so
REPRODUCES is compatible with seed-dependence at the cell level.** Printing the cells lets a reader see
that blind spot instead of having to trust around it.*

---

## 6. Outcomes — every case has a slot

Let *m* be the new arm mean over passing cells.

- **fewer than 4 of 6 cells pass the gates → UNDERPOWERED.** No reproduction verdict; gate results
  reported whatever they are.
- **m ∈ [−2.941, −1.117] → REPRODUCES on new seeds.** The result is not a property of seeds 101–106.
- **m < 0 and m ∉ [−2.941, −1.117] → SAME DIRECTION, MAGNITUDE NOT REPRODUCED.** Both means printed.
  This covers *m* below −2.941 as well as *m* between −1.117 and 0.
- **m ≥ 0 → DOES NOT REPRODUCE.**

The third case may not be written up as a partial success, a qualified reproduction, or a
reproduction with a caveat; it has a name here so it cannot be argued about once the number is
visible.

**No prediction is registered** — the seat writing this has seen the original arm's spread, which is
what sets the band, and no new cell. **No interpretation of any outcome is registered,** positive or
negative: this file commits to a measurement and to the four labels above, and nothing further.

---

## 7. Gates, replay, cost, scope

Gate G is applied from the `.sto` before any endpoint is computed: **G1** `history.txt` ≥ 91 lines
and the tag resolves to exactly one directory; **G2** duration ≥ 9.73 s; **G3** ≥ 4 admitted cycles
in the window [1.00, 13.58].

**The `.sto` is produced by `sconecmd -e` on the final `.par`, as a separate replay step** — the
optimiser writes `.par` only. Registered explicitly because its absence silently produced a 0-of-54
admission table in the speed study, which would have read as total viability failure.

6 cells × 204.0 s = 1,224 s serial; at concurrency 2, 612 s = **10.2 min**. The 204.0 s/cell is
measured on control cells at this depth; the spastic arm terminated before the cap in every
speed-study cell, so it is an upper bound.

**One arm. Six cells.** No new magnitudes, channels, speeds or weak cells, and no re-run of anything
on disk. Concurrency 2; the 112 protected directories yield nothing and ours yield on any conflict.
Progress from `history.txt` line counts and directory mtimes only. Writes confined to
`C:\Users\maurice\Desktop\spasticity_paper\` and the six new result directories. The frozen
manuscripts are not opened.
