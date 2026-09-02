# PREREG_weakpf_r274.md — was it lesion TYPE, or was it always anatomy?

**Round 274, REVISION 2. Written before any `WEAK-PF` cell exists.** *Body: 3D, `H1922v7b3`.*

| rev | sha256 | status |
|---|---|---|
| 1 | `a46eb62c7a9509c7c2a9fafc806ae48da2815f6d942e83c43cf35fe3b919a775` | superseded |
| **2** | **this document** | current |

**Rev 2 answers a deposits-not-argument audit of rev 1. Three findings, all upheld against measurement:**
*the dose match is nominal and cannot be otherwise (§2); the ladder was NOT exhaustive and 39 of 192
tests had no verdict (§6); and §1 misstated its own cited deposit (§1).* **No cell had run.**

⛔ **This registration replaces the full 2 × 2 for now. `PREREG_2x2_r270.md` (rev 5, `c956c0d7…`) does
not run — see §7.**

---

## 1. The question, and why one arm answers it

**For two hundred and seventy rounds this project's headline rested on one contrast:** on
`hip_flexion_LmR`, the plantarflexor reflex arm sits at **−2.1053** (2.0362 below the control band)
while the dorsiflexor weakness rungs sit **above** it, spanning +0.2808 to +0.7257
(`MARGINS_r248.json` → `hip_flexion_LmR.arms`).

⛔ **CORRECTED AT REV 2: FIVE of the six weakness rungs clear the band, not six.** *The same deposit
records W800 at `margin: -0.0694`, `side: "INSIDE"`, `clears_band: false` — its mean of +0.2808 lies
below the band's upper edge of +0.3502. Rev 1 asserted "every rung" and its own citation said
otherwise.*

⚠ **AND THE ARM THAT DOES NOT CLEAR IS ×0.800 — THE SEVERITY THIS DESIGN PROPOSES AS ITS HEADLINE
CELL.** ⭐ **REGISTERED PREDICTION, BEFORE THE RUN: on the primary channel, the analogous existing
lesion at the analogous dose lands INSIDE the control band. So `INCONCLUSIVE` — or
`NO-REFERENCE-DISPLACEMENT` — at f = 0.20 on `hip_flexion_LmR` is the EXPECTED outcome, not a
disappointment, and it will be reported as a predicted null rather than a failed experiment.**

⛔ **Two explanations have never been separated: reflex-versus-weakness (TYPE), or
plantarflexor-versus-dorsiflexor (ANATOMY).** *Every existing reflex cell is on the plantarflexors and
every existing weakness cell is on the dorsiflexor, so the two factors are perfectly confounded in the
corpus as it stands.*

⭐ **A plantarflexor WEAKNESS arm breaks that confound by itself.**

- *If `WEAK-PF` drives `hip_flexion_LmR` **negative**, like the plantarflexor reflex → **the headline
  was anatomy.***
- *If it drives it **positive**, like the dorsiflexor weakness → **the headline was type.***

## 2. ⭐ Why this comparison is clean where the crossed design is not

**Within one muscle group the fractional and absolute dose footings share a denominator, so they
coincide.** *At f = 0.20 on `soleus_l` + `gastroc_l`:*

| arm | delivered / removed | source |
|---|---|---|
| `SPASTIC-PF`, KV 0.050 (exists) | **+136.2664 N** | `VERIFY_F5_r231.json` → `spastic_dose_corrected_V_N` |
| `WEAK-PF`, f = 0.20 (new) | **−136.9565 N** | 0.20 × 684.78256379, `FOOTING_r272.json` |
| **absolute mismatch** | **0.6901 N = 0.5065 %** | |

⛔ **The 5.44× cross-group absolute-force confound that makes the crossed 2 × 2's magnitude comparison
uninterpretable does not exist here.** *It arises only between muscle groups. Inside one group there is
nothing to confound.*

⛔ **THE MATCH IS ON THE COMMANDED QUANTITY. IT CANNOT BE ON THE ACHIEVED ONE, AND THAT IS NOT A
DEFECT OF THIS DESIGN.**

*Measured on the existing dorsiflexor arms, which use the identical implementation, window
[1.00, 13.58]:*

| arm | scale | nominal removed | **achieved removed** | shortfall |
|---|---|---|---|---|
| W950 | 0.950 | 6.2927 N | **2.8802 N** | −54.2 % |
| W900 | 0.900 | 12.5853 N | **6.5519 N** | −47.9 % |
| W800 | 0.800 | 25.1706 N | **14.1781 N** | −43.7 % |

**The controller re-optimises and compensates: at scale 0.800 the muscle still achieves 0.887 of its
control force, not 0.800.** ⛔ **So achieved force is a POST-TREATMENT quantity and cannot be matched in
advance at all** — the same lesson as the terminal objective, which this project also has to refuse to
condition on because it is an outcome of the thing being designed.

⚠ **AND THE TWO SIDES ARE NOT THE SAME KIND OF QUANTITY.** *`MARGINS_r248.json` →
`lesion_magnitude.units_caveat`, carried forward here in its own words: the reflex figure is a **nominal
commanded** force increment — a dimensionless excitation increment multiplied by `Fmax` — while the
weakness figure is scaled from an **achieved** force read from `.sto`; they are "not the same KIND of
newton", and that deposit records the scope conflict as **unresolved**.* **Rev 1 asserted the footings
"coincide" and did not carry that forward.*

⭐ **WHAT THE 0.5065 % IS, STATED EXACTLY: a match of COMMANDED quantities. Achieved delivery will
differ, and by analogy with the dorsiflexor arms the weakness side is expected to fall short by roughly
40–55 %. Both commanded and achieved are measured and deposited per cell after the run.**

⭐ **AND THE PIVOT STILL HOLDS, FOR A REASON THE CROSSED DESIGN COULD NEVER CLAIM: within one muscle
group both arms share a denominator, so whatever the commanded-to-achieved factor is, it applies to the
same muscles under the same optimiser.** *Across muscle groups it does not. A nominal match within a
group is a better object than an achieved match across groups, which is what the 2 × 2 was trying and
failing to build.*

⚠ **What remains, and is not removed by this design: ADD versus REMOVE.** *The reflex adds force during
lengthening; the weakness removes force capacity. These are not one operation with opposite sign, and
no dose matching makes them so.* **A difference between these two arms may be an add-versus-remove
difference. This is the single interpretive limit of the design and it is stated here rather than
discovered later.**

## 3. The cells

**`WEAK-PF`: `max_isometric_force` scaled on BOTH `soleus_l` and `gastroc_l` by the same factor. Model
file edit only, no controller change — exactly as `WEAK-DF` is implemented.**

| f | scale | `soleus_l` | `gastroc_l` | **nominal** removed | seeds | cells |
|---|---|---|---|---|---|---|
| 0.05 | 0.950 | 3371.55 | 2128.95 | 34.2391 N | 101–106 | 6 |

| 0.10 | 0.900 | 3194.10 | 2016.90 | 68.4783 N | 101–106 | 6 |
| ⭐ **0.20** | **0.800** | **2839.20** | **1792.80** | **136.9565 N** | 101–106 | **6** |

**18 new cells.** ⛔ **Three doses, not one: a single-condition arm is the cardinality defect that
defeated every type claim in this corpus, and it is not repeated here.** *f = 0.20 is the
absolute-matched comparison; f = 0.05 and 0.10 give the dose-response and guard against reading one
condition as a category.*

**Comparison arms, reused, named with their cumulative optimisation depth so the wrong twin cannot be
resolved silently:**

| role | arm | depth | note |
|---|---|---|---|
| control | `R151C` s101–106 | **90** | the band comes from these six cells |
| reflex | `R151S` s101–106 | **90** | KV 0.050, f = 0.19899 |
| weakness reference | `R169W095`, `R169W090`, `R151W` | **90** | ⛔ **NOT `R172W090` (180) or `R172W080` (270)** |

⛔ **The `>= 91` history-line guard CANNOT distinguish depth-90 from depth-180/270 arms** — each
continuation stage writes its own 91-line history and cumulative depth appears in no file inside the
cell (`CONTINUATION_RESULT_r172.json`). **Arms are therefore resolved by name, and the resolved
directory is deposited per cell.**

⚠ *`R209S` and `R203V105S` also carry a KV 0.050 `SpasticL` block under a similar signature;
`R203V105S` has `min_velocity = 1.05` and is a different condition. **`R151S` is named explicitly for
this reason.***

## 4. Cost

**18 cells.** ⛔ **CORRECTED AT REV 2: 212.02 s/cell over the TEN arms that completed → 1.06 h.**
*Rev 1 said "the eight arms that actually completed" and named a set it did not describe: `R172W090`
and `R172W080` also completed 6/6 seeds at 20.0 s and 14 cycles and are simply absent from
`COST_r270.json` (209.34 and 241.93 s/cell). `SESSION_MEASURE_r275.json` → `completion_census`.* *The corpus-wide 147.6 s/cell gives 0.74 h but is contaminated by four collapsed
arms costing 5.3–47.4 s/cell; it is not used here.*
⚠ *Range, if `WEAK-PF` behaves like the fastest or slowest completing arm: **0.50 h to 2.25 h**.
Removing 1158 N of `Fmax` from the only propulsors is the largest untested insult in this project and
the arm may fail to walk — see rung 1.*

⛔ **RUN YIELD, BINDING ON THE LAUNCHER: if the user's own SCONE work is running, our cells give way.**
*The launcher checks for competing SCONE processes before each cell and suspends rather than competing.*

## 5. Measurement, carried over unchanged

- **Both metrics** — per-cycle EXCURSION and per-cycle MEAN ANGLE — **and both windows**, [1.00, 9.73]
  and [1.00, 13.58], reported for every result. Neither is primary.
- **The sixteen channels** of `MODEL_DESCRIPTORS_r253.json` → `channels_16`.
- ⭐ **MULTIPLICITY OVER THE TESTS THAT CAN ACTUALLY ADJUDICATE.** *16 channels × 2 metrics ×
  2 windows × 3 doses = 192, **minus the 39 that fall to rung 0** (13 cells × 3 doses) = **153**, so
  α′ = 0.05 / 153 = **3.268 × 10⁻⁴**.* ⛔ **Excluding them from the denominator is the point: 39 tests
  that cannot adjudicate must not inflate a correction applied to the 153 that can.** ⚠ *The rung-0
  count is deposited before analysis and is a property of the EXISTING reflex arm, not of any new
  cell, so it cannot be tuned by the result.* ⛔ *The 2 × 2 registration corrected for 16 while
  performing 192; that defect is not carried forward.*
- **δ = 2.534 σ per channel, frozen at the sixteen n = 6 control-band widths**, invariant to n.
  ⚠ *δ carries ~33.5 % sampling error as a six-point range statistic; it is reproducible, not precise.*
- **Terminal objective, generation-0 value, descent over the final ten generations, terminal
  `fitness_progress` and the full `history.txt` deposited per cell, and reported as a DEPENDENT
  VARIABLE.** ⛔ *No analysis conditions on it. It is dominated by a termination penalty and is an
  outcome of the lesion.*
- **Net pelvis yaw per cycle deposited per cell as a continuous outcome**, never used to include,
  exclude or stratify.

## 6. The ladder — four rungs, reachable by inspection

*Evaluated per channel × metric × window × dose, in this order, first match wins. **`d` is that
channel's δ; the sign convention is displacement from the control band.***

| # | rung | criterion | reading |
|---|---|---|---|
| 1 | **FAILURE-DOMINATED** | fewer than 2 `WEAK-PF` cells complete ≥ 2 gait cycles at this dose | kinematics undefined; **time-to-failure is the reported endpoint** |
| 2 | ⛔ **ANATOMY** | `WEAK-PF` displaced beyond the band **on the same side as `SPASTIC-PF`** | **the existing headline was a plantarflexor-site effect, not a lesion-type effect** |
| 3 | ⭐ **TYPE** | `WEAK-PF` displaced beyond the band **on the opposite side to `SPASTIC-PF`** | **the existing headline was a lesion-type effect: reflex and weakness oppose within one muscle group** |
| 4 | **INCONCLUSIVE** | `WEAK-PF` mean lies within the control band | **too small to assign at n = 6 on this channel** |
| 0 | ⛔ **NO-REFERENCE-DISPLACEMENT** | **evaluated FIRST: `SPASTIC-PF` lies INSIDE the control band on this channel** | **the reference lesion produced no displacement here, so it has no side and no type comparison is available; the channel is counted and EXCLUDED from the multiplicity family** |

⛔ **REV 1 CLAIMED THIS LADDER WAS EXHAUSTIVE BY INSPECTION. IT WAS NOT, AND THE CORPUS ALREADY
REFUTED IT.** *Rungs 2 and 3 are defined relative to the side `SPASTIC-PF` is displaced. **If
`SPASTIC-PF` is inside the band it has no side**, and a displaced `WEAK-PF` then matched no rung at
all.*

**Measured: `SPASTIC-PF` lies inside the band in 13 of 64 channel × metric × window cells** —
`ankle_angle_l` (both windows), `ankle_angle_r`, `ankle_angle_LmR`, `knee_angle_r`, `knee_angle_LmR`,
`hip_adduction_r`, `pelvis_rotation` (both), `lumbar_bending` (both windows, both metrics) — **and in
12 of those the existing weakness arms are already displaced, usually all six severities.** ⛔ **39 of
the 192 registered tests had no defined verdict.**

⭐ **Rung 0 closes it, and the exhaustiveness argument now runs: either `SPASTIC-PF` has no side (rung
0), or `WEAK-PF` fails to produce cells (rung 1), or `WEAK-PF` is outside the band on one side or the
other (rungs 2, 3), or it is inside (rung 4). Mutually exclusive, jointly exhaustive.**
⚠ *That is the same form of argument rev 1 made and got wrong, so it is stated with its failure case
named: the case rev 1 missed is exactly rung 0.*
⛔ *`REACH_2x2_r273.json` proved a seven-rung ladder reachable over a space **97.8 % of which is
physically impossible**, and produced zero self-consistent witnesses for its rung 1. A ladder whose
exhaustiveness is a two-line argument does not need that machinery and cannot be certified by it.*

⚠ **ANATOMY and TYPE are equally reportable and neither is a fallback.** *ANATOMY terminates the
project's original claim and ships at full strength as the headline if it fires. **It is the more likely
outcome and this registration does not treat it as failure.***

⚠ **The primary channel for the question is `hip_flexion_LmR`, because that is where the existing
contrast lives — but every channel is reported and no channel is privileged in the analysis.**

## 7. ⛔ The eleven blockers against the full 2 × 2, recorded so they are not lost

**`PREREG_2x2_r270.md` rev 5 does not run until these are fixed. This pivot does not dissolve them.**

⚠ **SOURCING NOTE, REV 2.** *Rev 1 quoted the figures in B1, B2 and B11 as though sourced; they were
in-session measurements appearing in no file — the exact failure mode this document warns about. They
are now deposited at `SESSION_MEASURE_r275.json` and cited from it.*

1. ⛔ **B1 — rung 3's sign disjunct has no precision requirement.** *Measured: **3,840** configurations
   fire INTERACTION on a bare sign flip with overlapping HL intervals. §6a claims the opposite. Under a
   null the signs disagree with p ≈ 0.5, so the ladder's most likely route is a coin flip returning the
   project's terminal negative, pre-empting rungs 4–7.*
2. ⛔ **B2 — the reachability gate certifies over an impossible space.** *Only **2.19 %** of its 190,512
   configurations are self-consistent, and **0 of 63,504** FAILURE-DOMINATED witnesses are physically
   possible — `SESSION_MEASURE_r275.json`, with the four consistency rules stated there.*
3. ⛔ **B3 — multiplicity registered for 16 tests against a search performing 192.** *Fixed in §5 here.*
4. **B4 — rung 2's floor clause is dead at n = 14.** *The generator still enumerates n = 6 floors; an
   arm may lose 9 of 14 cells and be certified adequately powered.*
5. **B5 — rungs 4 and 5 decide on bare point estimates**, no TOST and no CI containment; rung 5 has no
   significance criterion at all.
6. **B6 — rung 6 requires the permutation count "at its floor"**, i.e. maximal significance, for a
   *clean negative*.
7. **B7 — the control arm stays at 6 cells while lesion arms go to 14**, so at n = 14 rung 6 ships a
   clean negative for a displacement resolved at p ≈ 2 × 10⁻⁶.
8. **B8 — §6b states the wrong direction for rung 5.** *A larger δ makes rung 5 harder, not looser.*
9. **B9 — no null is registered for the primary endpoint.** *`PERMNULL_r221.json` is a two-arm 6 v 6 at
   one window; the endpoint is a four-arm interaction.*
10. **B10 — four registered criteria are undefined**: "usable cells", "the type effect" (the registered
    measure and the fixture's implementation are different quantities), "channels separate by muscle
    group", and the HL confidence level.
11. **B11 — §6's INCONCLUSIVE justification is stale and was never exhaustive.** *Registered as
    1,296 + 3,792 = 5,088; at rev 5 the total is 5,184 and the split is 1,296 / 3,264 / **624 matching
    neither pattern**.*

## 8. ⛔ The round-two audit was never completed

**Three of six agents finished — `grid`, `ladder`, `judgement`. Three died on a session limit —
`deposits`, `rev3-delta`, `reconcile`.**

⛔ **No `deposits` read and no `rev3-delta` read exist against ANY revision of the 2 × 2 registration,
and no reconciler ran.** *`grid` and `judgement` read rev 3 and were mapped forward to rev 5 by hand,
unreviewed. `ladder` re-measured against rev 5 itself.* ⚠ **The eleven blockers above are therefore a
partial audit's output, not a complete one, and the absence of the `deposits` read — the brief with the
best record on this project — is the largest known gap.**

## 8a. The two cells that tie on best fitness

*The audit flagged `R151W_s102` and `R169W090_s106` as raising under `sto_utils.select_registered_par`
exclusion E5 — two `.par` files at equal minimum fitness.*

⭐ **Measured, and the registered convention resolves both.** *The rule is: field 3 of the `.par`
filename is best fitness, ties broken by **highest generation**, since SCONE writes only on improvement.*

| cell | tied files | resolved | analysed `.sto` |
|---|---|---|---|
| `R151W_s102` | `0038_47.286_1.051`, `0060_19.759_1.051` | **gen 0060** | `0060_19.759_1.051.par.sto` ✅ |
| `R169W090_s106` | `0026_16.199_1.016`, `0068_35.019_1.016` | **gen 0068** | `0068_35.019_1.016.par.sto` ✅ |

⚠ **So the correct cell is analysed in both cases and no data is affected.** *What the audit found is a
code-versus-convention mismatch: `select_registered_par` raises on a tie instead of applying the
documented tie-break, while the analysis path takes the lexicographically last file — which IS the
highest generation, hence the registered answer. **The defect is in the helper, not in the corpus, and
it is recorded rather than silently relied upon.***

## 9. What this design cannot do

- ⛔ **It does not separate ADD from REMOVE** (§2).
- ⛔ **It does not cross type with muscle group.** *That needs the full 2 × 2, and the 2 × 2 needs its
  eleven blockers fixed.*
- ⚠ **It does not establish the attainable optimum of the lesioned problem.** *18 cells run the same
  90-generation budget as the rest of the corpus, for comparability.*
- ⛔ **One model, one body, six optimiser seeds. Nothing here becomes a statement about people.**
