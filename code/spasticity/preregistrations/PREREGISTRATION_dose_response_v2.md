# PRE-REGISTRATION v2 — Equinus dose–response against TRUE injected stretch-reflex gain

**Status:** registered, NOT executed. No cell has been launched. No `sconecmd` invocation was made in
preparing this document.
**Written:** 2026-08-02, by an independent designer reading this project for the first time.
**Deliberately not read:** `COUNCIL_*.md`, `WATCHDOG.md`, `HANDOFF.md`, `REFEREE_*.md`,
`PREREGISTRATION_dose_response.md`, `_VOID_PREREGISTRATION_dose_response_prelaunch.md`.
Every number below was measured directly from code, scenario files and archived `.sto` / `history.txt`
during preparation, and the measuring commands are stated so they can be repeated.

---

**REVISION 2026-08-02 (round 37) — eight referee blockers implemented before launch.** An external
referee returned DO NOT LAUNCH. The corrections are listed here so that what changed is on the record
BEFORE any cell exists, and every one of them is implemented in code as well as in prose:

| # | what was wrong | where it is now fixed |
|---|---|---|
| B1+B2 | the endpoint was read from a `*.par.sto` **the optimizer never writes**, from a far earlier generation than the run's best `.par`, and non-deterministically when a directory held two | **§7.1a** (registered replay step) and **§4.3** (rewritten selection rule + assertion) |
| B3 | the F4 saturation falsifier was near-certain to fire at the ladder top, and §0.5's "soleus 0.00 %" was false at true KV 0.200 | **§0.5** corrected, **§9.1 F4** branch written out in full |
| B4 | C2 required a certification string that does not appear anywhere in the registered launcher's output | **§7C C2** rewritten against the strings the launcher actually emits |
| B5 | void condition V1 was dead code — mutually exclusive with exclusion E6 | **§1.2 V1** made reachable |
| B6 | the registered launch command used the wrong default tags, named DR2K scenarios that did not exist, and spawned all 80 cells unthrottled | **§11**, `gen_conditions.CONDITIONS`, `gen_seeds.main` / `launch_throttled` |
| B7 | the scenario template carried neither `max_generations` nor the registered `min_progress`, and nothing asserted them | `opt2/TEMPLATE_working.scone`, `gen_conditions.apply_registered_stopping_rule`, `gen_seeds.assert_registered_stopping_rule`, **§6** |
| B8 | E4's generation threshold was off by one against `history.txt`'s convention | **§7.2 E4** and **§8**, after measuring the convention on 107 archived runs |
| — | the project's own instruments (`check_structure.py`, `check_unused.py`, `verify_placement.py`) appeared in no registered step, and `verify_placement.py` never returns a bare `PASS` | new **§12** |

**One `sconecmd -e` replay was executed during this revision** — exactly one — on
`DOSER3100_s1.H0914M.GH2010.S10W.D10.I.R1`, to verify that the command §7.1a registers actually
produces a `.sto`. Registering an unexecuted command is blocker B4 repeated. No optimization was
launched. Its result is reported in §0.4.

**Scope.** This is a DOSE–RESPONSE CHARACTERISATION: equinus magnitude versus true delivered gain KV of
a unilateral velocity-dependent plantarflexor stretch reflex. It establishes which gains produce
clinically recognisable equinus. **It is not a spasticity-versus-weakness comparison and contains no
weakness arm.** No claim about discriminating the two conditions may be drawn from it.

---

## 0. What was verified before registering (and the exact evidence)

### 0.1 The injection form is the current, side-correct one

`C:\Users\maurice\Desktop\spasticity_paper\scone\gen_conditions.py`, `spastic_block()` (lines 54–116),
emits a `ConditionalController` carrying `legs = left` (line 105), enclosing a `ReflexController`
named `SpasticL`, with SIDE-FREE targets `soleus` / `gastroc` (line 111). `make_scenario()`
(lines 119–173) splices that block as the last child of `GaitStateController /
ConditionalControllers`, never under a `CompositeController`. `kv=0.0` emits the block with
`KV = 0.000`, not no block (lines 128–137).

Confirmed present in the archive:
`C:\Users\maurice\Documents\SCONE\results\DOSER0000_s1.H0914M.GH2010.S10W.D10.I.R1\config.scone`
lines 150–168 hold exactly that block with `legs = left`, `target = soleus`, `target = gastroc`,
`KV = 0.000`, `allow_neg_V = 0`.

### 0.2 Delivery is 1.0x under the new form; 2.0x under the old

`delivered_gain.py` run on staged single-`.sto` copies:

| run | declared KV | rho[soleus_l] | rho[gastroc_l] | copies | verdict |
|---|---|---|---|---|---|
| `DOSER1050_s1.H0914M.GH2010.S10W.D10.I.R1` | 0.050 | 1.0252 | 1.0041 | 1.000000 / 0.999998 | PASS |
| `DOSER3100_s1.H0914M.GH2010.S10W.D10.I.R1` | 0.100 | 0.9749 | 0.9928 | 1.000000 / 1.000001 | PASS |
| `SPAS01_s2.H0914M.GH2010.R4.S10W.D10.I.R2` | 0.100 | 2.0015 | 2.0219 | 2.000000 / 2.000000 | FAIL |

The 2x defect is therefore not a narrative — the instrument reads `copies = 2.000000` to six decimals
on the old form. **Every archived `SPAS*` phenotype is at twice its label.** The relabelling used
throughout this document is exact: nominal 0.05 → true 0.100; nominal 0.10 → true 0.200.

Caveat recorded honestly: the 1.0x property rests on **two** runs at two gains, not on a broad
verification. §7 makes the per-cell gate, not the archive, responsible for establishing it.

### 0.3 The failure that killed the previous attempt — reproduced, and diagnosed differently

Claim under test: the KV = 0 control emits no delivered-signal channel.

**Confirmed.** Column headers of
`...\DOSER0000_s1.H0914M.GH2010.S10W.D10.I.R1\0005_13.034_0.937.par.sto` contain
`soleus_l.input`, `soleus_l.excitation`, `soleus_l.RF`, `gastroc_l.RF` — and contain **no**
`soleus_l.RV`, `gastroc_l.RV`, `soleus_l.V`, `gastroc_l.V`.
The same headers in `DOSER1050`, `DOSER2071`, `DOSER3100` **do** contain all four. SCONE writes a
contribution channel only when a contribution exists; a zero-gain reflex writes nothing.

**But the brief's diagnosis is wrong in a way that matters.** Staged into a directory holding
`config.scone` plus exactly one `.sto`, `delivered_gain.py` returns on the control:

```
DOSER0000_s1.H0914M.GH2010.S10W.D10.I.R1       PASS
   gastroc_l  declared KV=0   rho[KV]=n/a | copies=- ... |D|max=0.000e+00 ctrl(gastroc_r)=0.0e+00
   soleus_l   declared KV=0   rho[KV]=n/a | copies=- ... |D|max=0.000e+00 ctrl(soleus_r)=0.0e+00
```

The verdict is **PASS**, not ABSTAIN — a *vacuous* PASS, produced by the `Kd == 0` branch of
`delivered_gain.verify()` (line ~668), which flags only the case "declared 0 but something was
delivered". `rho` is `n/a` and `copies` is undefined. The ABSTAIN actually observed on the live
directory is
`ValueError: expected exactly one .sto beside config.scone, found 2` — a housekeeping condition
unrelated to the zero gain, which also fires on `DOSER2071` and `DOSER3100` (both non-zero cells).

Consequence for the design, and it is the crux: **any gate written on `rho` or `copies` is UNDEFINED
on the control, while the instrument's own verdict is PASS.** A design that reads that PASS as
certification would be certifying nothing, because `|D|max = 0` is equally consistent with
*"the block is present and its gain is zero"* and *"the block was silently discarded"*. §7C solves
this structurally and never touches the treatment cells' signal gate.

### 0.4 The archived `.sto` are REPLAY ARTEFACTS OF THE WRONG GENERATION — not optimizer output

This subsection replaces a weaker one. The original said only that a directory can hold more than one
`.sto` and that the choice moves the endpoint by 0.966–1.287 deg. That is true, and it understates the
problem by an order of magnitude. Measured 2026-08-02 over the whole archive:

**(a) SCONE's optimizer never writes a `*.par.sto`.** It writes `*.par`, `history.txt`,
`config.scone` and `optimization.log`. **148 of the 316 non-protected result directories under
`C:\Users\maurice\Documents\SCONE\results\` contain no `.sto` at all.** "Read the `.sto` in the run
directory" is therefore not a procedure that can be applied to a fresh run — there would be nothing
to read for any of the 80 cells.

**(b) Every `.sto` that does exist is a later replay, and of the wrong generation.**

| directory | `.sto` present (generation) | best `.par` | its generation |
|---|---|---|---|
| `DOSER0000_s1...` | 0005, 0009 | `0034_0.827_0.628.par` | **34** |
| `DOSER1050_s1...` | 0006 | `0034_7.066_0.791.par` | **34** |
| `DOSER2071_s1...` | 0011, 0012 | `0041_0.912_0.772.par` | **41** |
| `DOSER3100_s1...` | 0009, 0011 | `0026_31.656_0.853.par` | **26** |
| `SPAS01_s3...` | 0180 | `0333_0.813_0.790.par` | **333** |

Not one belongs to its run's best controller. The `.sto` mtimes fall INSIDE the optimizer's own
writing window — in `DOSER3100_s1` the two `.sto` were written at 03:20:36 and 03:24:19 while `.par`
files kept appearing until 03:44:10 — so they are the output of an analysis script that replayed
"the best `.par` so far" while the run was still improving.

**(c) The error this induces is larger than the decision threshold.** The one replay executed during
this revision (§7.1a's registered command, isolated directory, `DOSER3100_s1`'s actual best `.par`
`0026_31.656_0.853.par`) gives

> `ank_stance_mean` = **−8.922 deg** (5 complete cycles, `t_end` = 10.00)

against **−7.621** and **−6.655** from the two stale gen-9 / gen-11 files. The discrepancy is
**1.30–2.27 deg**, i.e. **34–60 % of the 3.8 deg decision threshold**, on top of the 0.966–1.287 deg
within-directory spread. **The `DOSER…` row of §2.1 is therefore withdrawn as a phenotype anchor**
(−2.56 / −3.78 / −4.12 / −6.65 were all read from stale files); it is retained only as evidence that
the 1.0x form runs and converges.

> ### ⛔ (c-bis) WITHDRAWAL EXTENDED — the `DOSER` row was not the only one read from stale files
>
> **Corrected 2026-08-02. This section proved that EVERY archived `.sto` is a mid-run replay
> artefact, and then withdrew only one of the four rows that rest on them. That was incoherent.**
>
> **Also withdrawn as phenotype anchors, on the identical evidence:**
>
> | row | value as published | status |
> |---|---|---|
> | healthy, n = 8 | −1.263 ± 0.850 | **WITHDRAWN** |
> | true KV 0.100, n = 6 | −3.638 ± 4.502 | **WITHDRAWN** |
> | true KV 0.200, n = 6 | −9.223 ± 2.678 | **WITHDRAWN** |
>
> These three rows are the **sole** source of `SD_plan` (§3.1), `Δ_alt` (§3.2), §2.2's defence of the
> top rung, and F5's reference value. **Every quantity downstream of them is therefore provisional
> until §2.1 is rebuilt from converged-best replays**, and the seed count in §3.3 is not yet
> determined.
>
> Re-derivation at converged bests indicates the planning SD is **substantially larger** than the
> 3.7043 published here — measured at **6.34** over the three-run 0.200 cell, against which n = 16
> carries far less power than §3.3 claims. **The exact figure is not stated here because it is
> membership-dependent** (see the registration requirement immediately below); it is stated by
> `dose_response_v2.py`, which computes it from a declared cell membership.
>
> **★ REGISTRATION REQUIREMENT, binding on every Δ_EQ figure in this document.** A Δ_EQ value is
> meaningless without a four-part tuple, and omitting it has now produced six mutually inconsistent
> values for the same quantity from the same data — quoted by the document, by two auditors and by an
> external referee. Every Δ_EQ must therefore declare:
>
> 1. **phenotype measure** — `ank_mean` or `ank_stance_mean`. They differ by 0.5–2 deg and must never
>    be compared across.
> 2. **sign convention** — this document uses *positive = more equinus*, which is the negative of the
>    raw ankle angle.
> 3. **reference baseline** — the healthy pool or the KV = 0 control. **These differ by 0.8178 deg
>    in `ank_stance_mean`** (the registered primary measure), 0.5831 deg in `ank_mean`.
>    ⛔ **CORRECTED 2026-08-02 round 43. This line previously read "These differ by 0.62 deg" — a
>    figure in `ank_mean`, quoted inside the clause that forbids comparing across measures.** The
>    prohibition was violated by its own worked example. Recomputed on the converged-best replays:
>    healthy pool (n = 8) −0.9472 vs control −0.1294 → **0.8178** (`ank_stance_mean`); −1.0349 vs
>    −0.4518 → **0.5831** (`ank_mean`). The old 0.62 is nearest the whole-cycle figure, which is what
>    identifies it.
>    **And "HEALTHY" itself was ambiguous, which is how the error survived.** Three different
>    referents were in use tonight: the **8-run healthy pool** (what `dose_response_v2.py` actually
>    averages, and what is registered), the **single run tagged `HEALTHY`** (+0.2081 stance — a
>    fresh reviewer and, on first pass, the watchdog both read it this way, giving 0.3375), and
>    whatever the stale files gave. **Element 3 of the tuple was itself untupled.** Registered
>    henceforth: *baseline `healthy` means the 8-tag pool listed in `ARCHIVE_HEALTHY`, never the run
>    whose tag is the bare word `HEALTHY`.*
> 4. **cell membership** — the exact run tags in each cell, listed.
>
> Worked demonstration on the converged-best replays, all four combinations defensible:
> 3 seeds vs `HEALTHY` **+5.532** · 3 seeds vs KV=0 control **+4.908** · 2 seeds vs `HEALTHY`
> **+3.464** · 2 seeds vs control **+2.841**, against the **+2.375** published in §2.1.
> **The sign of the 0.100 → 0.200 increment is likewise membership-dependent: positive in seven of
> eight (membership × measure) combinations and negative in one.** No monotonicity claim may be made
> until the tuple is fixed by `dose_response_v2.py`.

**(d) The selection was also non-deterministic.** Two independent auditors reading the same four
anchor directories obtained different controllers for the three directories holding two `.sto` and
agreed only on the one holding a single `.sto`. `delivered_gain.py` refuses outright
(`expected exactly one .sto beside config.scone, found 2`).

Consequence: the endpoint must have a PRODUCER, not a scavenger. **§7.1a registers a replay step**
that generates the `.sto` from a registered `.par` in an isolated directory, and **§4.3** registers
which `.par` that is, with an assertion.

### 0.5 Saturation — measured, and NOT what the brief anticipated

`gastroc_l.input` (pre-clip controller sum) versus `gastroc_l.excitation` (clipped to [0,1]):

| run | true KV | soleus_l max input | soleus_l frac clipped | gastroc_l max input | gastroc_l frac clipped |
|---|---|---|---|---|---|
| `HEALTHY_s1...R1` | 0 (no block) | 0.155 | 0.0000 | **2.066** | **0.3387** |
| `DOSER0000_s1...` | 0.000 | 0.237 | 0.0000 | 2.003 | 0.3357 |
| `DOSER1050_s1...` | 0.050 | 0.589 | 0.0000 | 2.028 | 0.3806 |
| `DOSER2071_s1...` | 0.071 | 0.619 | 0.0000 | 1.932 | 0.3656 |
| `DOSER3100_s1...` | 0.100 | 0.862 | 0.0000 | 1.798 | 0.3756 |
| `SPAS005_s2...` | 0.100 (2x) | 0.618 | 0.0000 | 1.623 | 0.3586 |
| `SPAS01_s2...` | 0.200 (2x) | 1.080 | 0.0010 | 1.813 | 0.4675 |
| `SPAS01_s3...` | 0.200 (2x) | 1.322 | 0.0010 | 1.562 | 0.3726 |
| `SPAS01_s4...` | 0.200 (2x) | 1.107 | 0.0010 | 1.825 | 0.4655 |

**gastroc_l excitation clips at exactly 1.0 for 33.6–46.8 % of samples in EVERY run, including HEALTHY
at zero injected gain.** The clipping is a property of the baseline Geyer–Herr controller, not of the
injection. Reading that as "the ladder top is meaningless" would be wrong.

The quantity that actually matters is marginal: what fraction of the **injected** `RV` integral lands
where `input > 1` and is therefore discarded. Measured on the runs that carry the `RV` channel:

⛔ **CORRECTED 2026-08-02 (blocker B3). The original version of this table stopped at true KV 0.100
and concluded "soleus 0.00 % across the entire registered ladder" and "the trend reaches 15 % near
true KV ≈ 0.25". Both statements are false at the ladder top.** The measurement was extended to every
archived run carrying the `RV` channel, i.e. to true KV 0.200:

| run | true KV | soleus_l discarded | gastroc_l discarded |
|---|---|---|---|
| `DOSER1050_s1` | 0.050 | 0.00 % | 2.58 % |
| `DOSER2071_s1` | 0.071 | 0.00 % | 2.95 % / 2.98 % (two `.sto`) |
| `DOSER3100_s1` | 0.100 | 0.00 % | 5.22 % / 5.03 % (two `.sto`) |
| `BSPAS005_s2` | 0.100 | 0.00 % | 1.51 % |
| `BSPAS005_s1` | 0.100 | 0.00 % | 5.99 % |
| `SPAS005_s2` | 0.100 | 0.00 % | 7.15 % |
| `SPAS005_s4` | 0.100 | 0.00 % | 7.98 % |
| `SPAS005_s3` | 0.100 | 0.00 % | 9.20 % |
| `SPAS005` | 0.100 | 0.00 % | 11.16 % |
| `BSPAS01_s2` | **0.200** | **2.32 %** | 6.89 % |
| `SPAS01` | **0.200** | **4.94 %** | 8.03 % |
| `SPAS01_s3` | **0.200** | **3.04 %** | 11.27 % |
| `SPAS01_s4` | **0.200** | **2.94 %** | 13.02 % |
| `SPAS01_s2` | **0.200** | **2.95 %** | 13.36 % |
| `BSPAS01_s1` | **0.200** | **5.31 %** | **15.56 %** |

(Command: for each `.sto`, `sum(|RV|[input > 1]) / sum(|RV|)` per muscle, on the columns
`<muscle>.RV` and `<muscle>.input`, `sto_utils.load_sto`.)

What the corrected numbers say:

* **soleus is NOT a 0.00 % channel at the ladder top.** At true KV 0.200 it discards **2.32–5.31 %**
  (n = 6). The 0.00 % figure holds only for true KV ≤ 0.100.
* **gastroc at true KV 0.200 discards 6.89–15.56 %, median ≈ 12.1 % (n = 6) — not the ~10 % a linear
  extrapolation from 0.05/0.071/0.100 predicted.** The growth is faster than linear.
* **One of the six archived runs at true KV 0.200 (`BSPAS01_s1`, 15.56 %) already exceeds the
  registered 15 % F4 falsifier**, and three more sit at 11.3–13.4 %. F4 is not a formality at the top
  rung; it is a live branch that will probably be taken by at least one seed.

Because "decide after seeing which seeds fire" is exactly the manoeuvre this document exists to
prevent, **§9.1 F4 now carries its consequence branch in full, written before launch**: the
aggregation rule from per-seed fractions to a per-cell verdict, and what happens to the fixed
sequence, to F2/`KV_hat`, and to the reported result when the TOP rung is the cell that fires.

The ladder is still capped at true KV = 0.200 — see §2.2 for why the alternative (capping at 0.150)
was rejected.

### 0.6 Convergence depth — measured, and the brief's range is understated

Running-best fitness excess above final, at generation 100, for the six archived spastic runs that
exceeded 100 generations:

| run | last gen | best@90 | best@100 | final | excess@100 |
|---|---|---|---|---|---|
| `SPAS005_s2...R2` | 319 | 0.7738 | 0.7626 | 0.6738 | **+0.0888 (13.2 %)** |
| `SPAS005_s3...R3` | 329 | 0.7128 | 0.7128 | 0.6697 | **+0.0431 (6.4 %)** |
| `SPAS005_s4...R4` | 309 | 0.8279 | 0.8191 | 0.7451 | **+0.0740 (9.9 %)** |
| `SPAS01_s2...R2` | 279 | 0.9737 | 0.9737 | 0.8042 | **+0.1695 (21.1 %)** |
| `SPAS01_s3...R3` | 329 | 1.1112 | 1.0988 | 0.7926 | **+0.3062 (38.6 %)** |
| `SPAS01_s4...R4` | 299 | 0.8557 | 0.8377 | 0.8079 | **+0.0297 (3.7 %)** |

Observed range **+0.0297 to +0.3062 (3.7 %–38.6 %)**, not 0.089–0.306. The brief's conclusion holds —
a 90-generation cap measures unconverged controllers — but two of six runs are inside a 90-gen cap's
reach, so the effect is heterogeneous, not uniform.

At 250 generations the picture is much better:

| run | rb@200 | rb@250 | improvement 200→250 | residual 250→final |
|---|---|---|---|---|
| `SPAS005_s2` | 0.7114 | 0.6941 | 2.49 % | 3.01 % |
| `SPAS005_s3` | 0.6817 | 0.6761 | 0.83 % | 0.96 % |
| `SPAS005_s4` | 0.7599 | 0.7534 | 0.85 % | 1.11 % |
| `SPAS01_s2` | 0.8292 | 0.8141 | 1.86 % | 1.23 % |
| `SPAS01_s3` | 0.8764 | 0.8154 | 7.49 % | 2.87 % |
| `SPAS01_s4` | 0.8212 | 0.8079 | 1.64 % | 0.00 % |

This is the empirical basis for the 250-generation cap and the 5 % plateau gate in §8.

### 0.7 Channel and parameter-layout identity across the archive

Checked on 10 archived runs spanning HEALTHY / SPAS005 / SPAS01 / DOSER:
`sto_utils.col()` resolves `ankle_angle_l` to `/jointset/ankle_l/ankle_angle_l/value` in **all 10**
(there are 3 candidate columns containing that substring in every file);
`grf_vertical()` resolves to `leg0_l.grf_norm_y` with threshold 0.05 BW in **all 10**;
`t_end = 10.00` s in all 10; the emitted `.par` has **36** lines in 9 of 10 (the exception,
`BHEALTHY_s1...`, has 65 and is a different series not used here).

The resolution is *correct* in all 10 — but `col()` reaches it by fuzzy suffix matching, which
`delivered_gain.py`'s own header calls "unacceptable in a verification instrument". §4.2 asserts it.

---

## 1. STOPPING RULE — stated before any cell launches

### 1.1 What ends the study with a result

* **S-A (transition found).** The fixed-sequence procedure of §9.2 identifies KV\*. Report and stop.
* **S-B (null).** The fixed sequence fails at its first step — the highest registered dose, true
  KV = 0.200, does not exceed the 3.8 deg threshold. Report **"no clinically recognisable equinus at
  any true KV ≤ 0.200"** and **stop.** The ladder is **not** extended upward, no additional rung is
  added, no seed is added, and no secondary phenotype is promoted. Extending a ladder after a null
  is the exact manoeuvre this document exists to prevent.
* **S-C (ceiling).** If ≥ 50 % of the seeds in the top cell are excluded under §7, that cell is
  reported as **NOT CHARACTERISABLE**, the effective ladder top becomes the highest cell with
  < 50 % exclusions, and the fixed sequence starts there. Report and stop.

### 1.2 What makes the pipeline itself untrustworthy (study voided, NO dose–response reported)

Any one of these voids the study. The failure is reported in full, together with the exclusion counts;
no transition point, no fitted slope, and no threshold verdict is published.

* **V1** — ⛔ **REWRITTEN 2026-08-02 (blocker B5). The previous wording was unreachable dead code**:
  it fired on a **non-excluded** seed returning `FAIL` or `ABSTAIN`, while **E6** excludes any
  treatment seed whose `delivered_gain.py` verdict is ≠ `PASS`. Every seed V1 could have fired on was
  removed from V1's own population by E6 first. The primary delivery-integrity void condition could
  therefore never fire, in any dataset.

  **V1 is now evaluated on the E6-EXCLUDED seeds, which is what makes it reachable:**

  > **V1 fires if `delivered_gain.py` returns verdict `FAIL` on any staged treatment seed,
  > excluded or not.**

  Rationale for putting `FAIL` and only `FAIL` here. `FAIL` means the instrument **measured**
  `copies` or `rho` and found them outside tolerance — i.e. the injected block delivered the wrong
  amount. The block text is generated by one function (`gen_conditions.spastic_block`) and is
  byte-identical across all 16 seeds of a cell (C1 asserts this), so a wrong delivery is a property
  of the **injection mechanism**, not of the seed. One `FAIL` implicates all 80 runs, and no
  exclusion arithmetic can repair it. The study is voided.

  `ABSTAIN` and `NO_INJECTION_DECLARED_AND_NONE_DELIVERED` are **not** V1. They mean the instrument
  could not form a verdict on that directory — a per-seed, per-record condition. They remain E6
  seed-level exclusions and are counted in the E6 column of §7.3. (`ABSTAIN` for the multi-`.sto`
  cause specifically cannot arise at all once §7.1/§7.1a staging is applied, because the staged
  directory holds exactly one `.sto` by construction.)
* **V2** — The control fails structural certification §7C (any of C1–C5).
* **V3** — The resolved ankle column name, or the resolved GRF channel name, or the GRF threshold, is
  not byte-identical across all 80 runs.
* **V4** — The reported CMA-ES dimension (`dim=` in the startup line) or the emitted `.par` line count
  is not 36 in every run.
* **V5** — Any scenario lacks `random_seed`, or any two scenarios within a cell share one, or any
  scenario's `min_progress` / `max_generations` differs from §6
  (`gen_seeds.assert_registered_stopping_rule`, which calls `assert_distinct_seeds`, raises). This is
  a **pre-launch** gate: it runs on the generated files before `--launch` starts anything.
* **V6** — Any cell's seed-to-seed SD of the primary phenotype exceeds **7.409 deg** = 2 x the planning
  SD of 3.7043 deg (§3). This means the planning SD was wrong and the power calculation of §3 is void;
  the correct response is to void the study, not to reinterpret it at whatever power was achieved.
* **V7** — Any `C:\Users\maurice\Desktop\spasticity_paper\scone\opt_seeds\log_<TAG>_s<k>.txt` is
  missing or empty, or `check_unused.check()` on it returns anything other than
  `ok / no unused-property warning` (i.e. any of `NO_LOG`, `LOG_UNUSABLE`, `WARNING` — §12.3). This is
  the silent-discard failure mode documented in `gen_conditions.make_scenario`. **Not** the results
  directory's `optimization.log`: 327 of the 328 archived ones are zero bytes (§7C2).
* **V8** — Total exclusions across the study exceed 30 of 80 seeds (37.5 %). At that attrition the
  surviving optima are a selected subpopulation and no unbiased cell mean exists.

**Explicitly forbidden.** Nothing in §1.2 may be resolved by moving a threshold. If a gate fails, the
study is voided and re-registered; the gate is not adjusted in the direction that makes it pass.

---

## 2. The KV ladder

All values below are **TRUE DELIVERED** gain, i.e. what `delivered_gain.py` must read back as
`K_hat`. They are written into `spastic_block(kv)` unchanged, because the current form delivers 1.0x
(§0.2).

### 2.1 Anchors used to place the ladder

| anchor | source | true KV | primary phenotype |
|---|---|---|---|
| frozen-controller ceiling | `scone\scone_naive_ladder.json` | 0.010 (nom 0.005) walks | rom 19.66, lr 1.28 |
| | | 0.020 (nom 0.010) and above **fall** | `null` |
| healthy reference, n = 8 | `HEALTHY_s1..s4`, `DHEALTHY_s1..s3`, `HEALTHY` | 0 | `ank_stance_mean` **−1.263 ± 0.850** |
| adapted, n = 6 | `SPAS005*` + `BSPAS005*` (nom 0.05) | **0.100** | **−3.638 ± 4.502** |
| adapted, n = 6 | `SPAS01*` + `BSPAS01*` (nom 0.10) | **0.200** | **−9.223 ± 2.678** |
| adapted | `SPAS02` (nom 0.20) | 0.400 | fitness 40.24 @ gen 19, **no `.sto`** |
| adapted | `SPAS05`/`SPAS10`/`SPAS20` | 1.0 / 2.0 / 4.0 | fitness 62.8–84.0, **no `.sto`** |
| new 1.0x form, 1 seed, ~30–40 gen | `DOSER0000/1050/2071/3100` | 0 / 0.05 / 0.071 / 0.10 | ⛔ **WITHDRAWN** (−2.56 / −3.78 / −4.12 / −6.65 were read from stale mid-run replay `.sto`, §0.4). Retained only as evidence the 1.0x form runs and converges. The one value re-measured under §7.1a — `DOSER3100`, true KV 0.100 — is **−8.922**, not −6.65 |

Reading these together: the live region is true KV ∈ (0, ~0.3]. Below true 0.05 nothing happens; at
true 0.100 the mean equinus shift versus healthy is **2.375 deg — below the 3.8 deg threshold**; at
true 0.200 it is **7.960 deg — above it**. The transition therefore sits between 0.100 and 0.200, and
at true 0.400 the optimizer no longer finds a walking gait at all.

### 2.2 The registered ladder

| cell | TAG | true KV | why this rung |
|---|---|---|---|
| C | `DR2K000` | **0.000** | control. Carries the block with gain zero. Certified structurally (§7C). |
| 1 | `DR2K050` | **0.050** | below every archived observation of equinus; establishes the lower edge and the expected null. Directly anchored by `DOSER1050` (rho verified 1.0041/1.0252). |
| 2 | `DR2K100` | **0.100** | ⛔ its anchor (−3.638 ± 4.502, expected Δ = 2.375) is **withdrawn** per §0.4(c-bis). Retained as a rung on mechanism, not on that anchor: it is the lowest dose at which any archived run shows equinus. Expected Δ to be restated by `dose_response_v2.py`. |
| 3 | `DR2K150` | **0.150** | ⛔ **zero archived observations** — nothing exists between delivered 0.1017 and 0.2008. Retained only as the bracketing rung; it has no anchor and none is claimed. First to be dropped under §2.3. |
| ~~4~~ | ~~`DR2K200`~~ | ~~0.200~~ | ⛔ **REMOVED FROM THE DOSE–RESPONSE LADDER.** Re-registered as a separate hypothesis, §2.2a. |

**Why the ladder stops at 0.200.** Two independent reasons, both measured. (a) Saturation: at true KV
0.200 gastroc already discards **6.89–15.56 %** of the injected drive (median ≈ 12.1 %, n = 6) and
soleus **2.32–5.31 %** — corrected numbers, §0.5; the earlier "15 % near 0.25" was a linear
extrapolation and the growth is faster than linear. (b) Viability: true 0.400 produced fitness 40.2
and no `.sto` in the archive. Rungs above 0.200 would measure a mixture of "more spasticity" and
"less of the increment arrives", which is not a dose–response.

> ### ⛔ 2.2a — `DR2K200` IS NO LONGER A DOSE RUNG. Struck and re-registered, 2026-08-02.
>
> **Why the defence below is struck.** Every one of its three arguments rests on the archived
> 0.200 anchor **−9.223 ± 2.678, withdrawn in §0.4(c-bis)**. Argument 1 invokes Δ_EQ = 7.96 from that
> anchor; argument 2 calls 0.200 "the only dose known to produce equinus" on the same basis. **A
> defence built entirely on a withdrawn anchor cannot survive the withdrawal**, and leaving it in
> place would have the document defending a rung it no longer contains.
>
> **Why it cannot be a dose rung on the measured data.** At converged bests the 0.100 → 0.200
> increment is **0.84 deg against a pooled SD of at least 3.7 (measured 6.34 over the three-run
> cell) — 0.23 SD or less.** No seed count this study will pay for resolves that; n would run to the
> hundreds. **As a dose rung it is dead weight costing 16 seeds.** Worse, its sign is not even
> established: positive in seven of eight (membership × measure) combinations and negative in one.
>
> **Re-registered as its own hypothesis, H2, with its own null, stated before launch:**
>
> - **H2:** at true KV 0.200 the delivered increment saturates — *the fraction of injected drive
>   discarded by excitation clipping exceeds 15 %.*
> - **H2 null:** it does not.
> - **Test:** the lower bound of the cell's 95 % CI on discard fraction exceeds 15 % (the same
>   interval-not-point rule as F4). **This is a proportion, not a 0.84 deg difference, so it is
>   testable at far lower n** — 6 seeds, not 16.
> - **H2 is independent of H1.** It is reported whatever the dose–response shows, and it does **not**
>   enter the §9.2 sequence.
>
> **`DR2K200` is removed from the start of the §9.2 sequence.** As previously registered the sequence
> *began* at the one rung whose anchor cannot be reproduced.
>
> The 16 seeds it releases are reallocated to `DR2K050` and `DR2K100`, per the rule that any retained
> rung carries the same n as every other.

**~~Why the ladder was NOT re-capped at 0.150 (blocker B3, decided before launch).~~** ⛔ **STRUCK —
the argument below rests on the withdrawn 0.200 anchor. Retained only as a record of the reasoning
that was superseded.** The referee
offered a choice: cap at 0.150, or write the F4 branch now. **The branch was written (§9.1 F4) and
the top rung kept**, because capping at 0.150 is not a cap — it is a different study:

1. **It destroys the power calculation.** §3.2 fixes n = 16 from an archive-anchored alternative of
   Δ_EQ = 7.96 deg, which exists **only** at true KV 0.200 (n = 6, 6/6 equinus). There is no archived
   observation at 0.150 at all, so a 0.150-topped ladder has no effect size, hence no justified n,
   hence no registered power. Re-deriving n after moving the top rung is a redesign, not a
   correction.
2. **It converts the study's most likely outcome into an uninformative null.** The fixed sequence
   (§9.2) starts at the top rung. Starting it at 0.150 — the one rung with no anchor — makes S-B
   ("no equinus at any registered dose") the probable report, from a ladder that deliberately
   excluded the only dose known to produce equinus.
3. **F4 is a falsifier, not a nuisance.** Its firing at the top rung IS a finding: it says the
   delivered increment saturates before the phenotype does, and §9.1 F4 now says exactly what is
   reported when that happens. Removing the rung would delete the observation instead of reporting
   it.

The cost is stated plainly: **the top rung is expected to deliver ~12 % less gastroc drive than its
label**, so its true delivered dose is below 0.200 by an unmeasured amount, and every conclusion at
that rung is reported with the F4 label attached.

**Spacing is uniform at 0.050.** Consequence stated up front: the discrete transition point can never
be localised more finely than ±0.025 in true KV.

### 2.3 Pre-committed reduction order, if compute forces a cut

> **⛔ REWRITTEN 2026-08-02.** The previous text justified the drop order by calling `DR2K200`
> *"the best-anchored rung in the archive (6/6 seeds, all equinus, SD 2.678)"* — **an anchor
> withdrawn in §0.4(c-bis)**, and it contradicted both §2.2 (which defended keeping that rung) and
> §9.2 (whose sequence starts there). As written it was also an **unbounded post-launch escape
> hatch**: "if compute forces a cut" had no numeric trigger, so it could be invoked at any time for
> any reason. Both defects are fixed below.

**Trigger, numeric and pre-committed.** A cut may be invoked **only** when, at a wall-clock
checkpoint of **240 hours** after the first cell launches, the number of cells having reached
generation 249 is **fewer than 60 of 80**. No other circumstance permits a cut. If the trigger is not
met, the ladder runs as registered.

**Order, and it is fixed.** Cells are dropped **first `DR2K150`, then `DR2K050`** — the two rungs
whose anchors are weakest, `DR2K150` having **zero archived observations** (nothing exists between
delivered 0.1017 and 0.2008) and `DR2K050` resting on a single run.

**The number of seeds is never reduced.** Cutting n destroys the inference; cutting rungs only
coarsens it.

**`DR2K200` is not in this order because it is no longer a rung of the dose–response** — see §2.2, in
which it is re-registered as a separate hypothesis with its own null.

---

## 3. Seed count — by power calculation

### 3.1 Planning SD, from the archive

Across-seed SD of the primary phenotype at fixed dose, computed on the archived runs listed in §2.1:

* healthy, n = 8: SD = **0.850**
* true KV 0.100, n = 6: SD = **4.502**
* true KV 0.200, n = 6: SD = **2.678**

Pooled across the two spastic cells (df = 10): **SD_plan = 3.7043 deg.**

The healthy cell is deliberately **excluded** from the pooling. Pooling all three gives 2.893, which
is optimistic: the archive shows the spastic cells are 3–5 x more variable than healthy, and every
comparison in this study has a spastic cell on one side.

### 3.2 The calculation

Confirmatory test (§9.2): one-sided Welch t of H0: Δ_EQ ≤ 3.8 against H1: Δ_EQ > 3.8, α = 0.05.
Alternative: the archive-anchored effect at the top rung, **Δ_EQ = 7.96 deg** (§2.1), rounded down to
7.6 = 2 x threshold. SD_plan = 3.7043. `SE = SD·sqrt(2/n)`, `ncp = (7.6 − 3.8)/SE`, power from the
noncentral t.

| n/cell | df | t_crit (1-sided) | SE | ncp | **power** |
|---|---|---|---|---|---|
| 10 | 18 | 1.734 | 1.657 | 2.294 | 0.713 |
| 12 | 22 | 1.717 | 1.512 | 2.513 | 0.785 |
| **13** | 24 | 1.711 | 1.453 | 2.615 | **0.815** |
| 16 | 30 | 1.697 | 1.310 | 2.901 | 0.883 |

Criterion A (power ≥ 0.80 for the confirmatory test) is met from **n = 13**.

Second, independent criterion, aimed squarely at the failure the brief names — a verdict decided by
rounding. Two-sided 95 % CI half-width on Δ_EQ at SD_plan:

| n/cell | half-width (deg) | vs threshold 3.800 | two-sided power for a 3.8 shift |
|---|---|---|---|
| 6 | 4.765 | **exceeds** | 0.362 |
| 9 | 3.702 | 0.974 x | 0.534 |
| 13 | 2.999 | 0.789 x | 0.709 |
| 15 | 2.771 | 0.729 x | 0.774 |
| **16** | **2.675** | **0.704 x** | **0.802** |

Criterion B (two-sided power ≥ 0.80 to detect a 3.8 deg shift) is met from **n = 16**, where the CI
half-width is 2.675 deg — **1.125 deg clear of the threshold**, not 0.01 deg clear.

### 3.3 Registered seed count

**n = 16 seeds per cell**, `random_seed = 1 … 16`, the same 16 integers in every cell (a paired
design across cells; distinctness is required *within* a cell, per
`gen_seeds.assert_distinct_seeds`).

> ⛔ **CORRECTED 2026-08-02 round 43. This line read "5 cells x 16 = 80 optimizations" and three
> artifacts described three different studies.** §2.2a struck rung 4 and left the cell count
> standing here and in three other places (§6, §8, §9.1 F1). Meanwhile the generator had **already
> written** `DR2K200_s1..s16` — sixteen seeds for the cell §2.2a re-registered as a **six**-seed
> separate hypothesis — and `dose_response_v2.py` launched a 16-seed `DR2KHEALTHY` cell that
> **appears nowhere in this document and was never generated**.
>
> **RECONCILED, with `dose_response_v2.py` as the single source and the other two checked against
> it:**
>
> | | cells | runs |
> |---|---|---|
> | dose ladder | `DR2K000` / `050` / `100` / `150`, 16 seeds each | **64** |
> | H2 (separate hypothesis, not a rung) | `DR2K200`, **6** seeds | **6** |
> | healthy | **none launched** — `BASELINE = "control"`, so Δ_EQ is defined against the KV=0 cell and the healthy pool is an *archive* reference for placing rungs (§2.1), not a launch cell | 0 |
> | | | **= 70 optimizations** |
>
> **Not 80.** The compute estimate in §3.4 scales accordingly: 70 runs at 12.6–14.1 h and 4-way
> concurrency is **≈ 221–247 h ≈ 9.2–10.3 days**.
>
> `DR2K200_s7..s16` — ten generated scenarios that no cell claims — are moved to
> `scone/opt_seeds/_SURPLUS_not_registered/` with a README, not deleted, so a later reader can
> verify the surplus was surplus and not a silently dropped rung. Two pre-launch gates now enforce
> this and both must pass before any cell launches: `assert_tags_exist()` (every registered tag has
> a scenario) and **`assert_cell_counts()` (every scenario belongs to a registered cell)**. The
> second is the new one, and it is the one that catches surplus — *"extra cells quietly ran" is how
> uneven n enters, and uneven n across rungs is forbidden outright.* Verified both directions:
> with the surplus present the gate fires naming all ten; with it quarantined, **70/70 pass.**
>
> **⛔ STILL OPEN — the other three "5 cells" occurrences are NOT fixed by this note.** §6, §8 and
> **§9.1 F1** still say five. **F1 is the monotonicity falsifier and its stated precondition is
> "all 5 cells analysable", which can now never be satisfied — the primary falsifier cannot fire.**
> That is a separate correction and it is named as outstanding rather than folded in here.

**Analysability floor: n_retained ≥ 9.** Computed, not argued: at n = 9 the two-sided CI half-width is
3.702 deg, still below the 3.800 deg threshold; at n = 8 it is 3.972 deg, above it. A cell with fewer
than 9 retained seeds cannot in principle place the threshold outside its own CI, is reported as
**INDETERMINATE-BY-ATTRITION**, and contributes nothing to the fit or the fixed sequence.
Launching 16 tolerates 7 exclusions (43.8 %) before hitting the floor.

**No seed is ever replaced.** Re-running an excluded seed until the cell fills selects for well-behaved
optima and biases every cell mean.

> ⛔ **AMENDED 2026-08-02 round 43 — the rule as written did not distinguish two things, and the
> practice had already diverged from it.** `scone/replay_registered/replay_ledger.json` holds **26
> entries: `E5_STO_0` × 12, `ok` × 12, `E5_SELECTION` × 2** — and the twelve `ok` rows are **the
> same twelve tags** as the twelve failures (`HEALTHY_s1..s4`, `DHEALTHY_s1..s3`, `SPAS005`,
> `SPAS005_s2`, `SPAS01`, `SPAS01_s2`, `BSPAS01_s1`). Under the sentence above, read literally,
> **round 42 replaced twelve seeds and the study would be void.**
>
> **Ruling: the practice was right and the rule was underspecified.** The two operations are not
> the same kind of thing:
>
> | | what it is | is re-running it selection? |
> |---|---|---|
> | **re-optimization** | a fresh CMA-ES run with a new random seed | **YES — forbidden.** A different optimum is drawn; re-drawing until the cell fills selects for well-behaved optima. |
> | **replay** | `sconecmd -e` on a **fixed, already-chosen `.par`**, deterministic | **NO — permitted.** The controller is decided before the replay; re-running after an infrastructure failure returns the identical trajectory. |
>
> The twelve `E5_STO_0` rows were **infrastructure failures — the replay wrote no `.sto`** — not
> results the analyst disliked. A deterministic re-derivation of an already-selected controller
> cannot select for anything, because there is nothing left to select.
>
> **Registered, and binding:**
> 1. **"No seed is ever replaced" governs OPTIMIZATION only.** It is absolute there.
> 2. **A replay may be re-run only after a NON-RESULT** — `E5_STO_0` (no file written) or a
>    documented crash. **Re-running a replay that produced a `.sto` is forbidden**, whatever the
>    value in it, because at that point there *is* something to select on.
> 3. **Every replay attempt, including failures, stays in `replay_ledger.json`.** The ledger is the
>    audit trail; a re-run that leaves no failed row is indistinguishable from selection.
>    *(This is the only reason the divergence was visible at all — the ledger recorded its own
>    failures. Had it logged successes only, the practice and the rule would have silently
>    disagreed for the life of the study.)*

### 3.4 Compute budget (stated so the design cannot be quietly truncated)

From `.par` modification times on the archived deep runs (which ran ~4 concurrent):
`SPAS005_s2` gens 0→320 in 16.9 h = **3.18 min/gen**; `SPAS005_s3` 3.03; `SPAS005_s4` 3.21;
`SPAS01_s2` 3.38; `SPAS01_s3` 3.06; `SPAS01_s4` 3.22.
At 250 generations that is **12.6–14.1 h per run**; 80 runs at 4-way concurrency is
**≈ 252–282 h ≈ 10.5–11.8 days**, plus one 1-generation sidecar (§7C4, ~5 min).
If that budget is unavailable, the response is §2.3 (drop rungs), never a reduction in n or in
generations.

---

## 4. THE primary phenotype — exactly one

### 4.1 Definition

**`ank_stance_mean` of the LEFT (lesioned) ankle**, in degrees, from
`C:\Users\maurice\Desktop\spasticity_paper\scone\sto_utils.py`, `cycle_features(path, side="l",
settle=1.0)`, key `"ank_stance_mean"`. Sign: SCONE convention, **negative = plantarflexion**.

Reported as **EQ = −ank_stance_mean** (positive degrees of stance plantarflexion), and the endpoint is

> **Δ_EQ(KV) = mean EQ over retained seeds of cell KV − mean EQ over retained seeds of cell KV = 0.**

`ank_stance_mean` averages, over complete GRF-delimited gait cycles, the ankle angle at those samples
whose vertical GRF exceeds the same threshold the heel-strike detector used (`sto_utils.py`
lines 167–193). This is the **repaired** definition; the pre-repair version averaged the first 60 % of
the stride by sample index. Measured true stance fraction in this model is **0.549–0.633** across the
archive, and it varies with dose, so the old proxy's bias was a function of the axis being measured.

### 4.2 Why this one, and why not the obvious alternatives

`ank_min` and `ank_swing_min` are **not** the phenotype and are not eligible for promotion. Measured
on healthy runs: `HEALTHY_s1` `ank_min = −13.91`, `ank_swing_min = −13.91`; `HEALTHY_s3` −14.82.
Those large plantarflexion minima are physiological push-off at toe-off, present at zero injected
gain, and they would read as severe equinus in a healthy model. Equinus is a **stance** phenomenon;
`ank_stance_mean` is the only listed feature that isolates it. `ank_hs` (angle at heel strike) is a
defensible alternative but is a single-sample statistic and is registered as a **secondary,
descriptive** quantity only.

**Column-resolution assertions (V3).** Because `sto_utils.col()` matches by suffix and 3 columns in
each file contain the substring `ankle_angle_l`, the analysis script must, for every run, record the
resolved column name and the resolved GRF channel name and threshold, and assert that all 80 runs
resolve to `/jointset/ankle_l/ankle_angle_l/value` and to `leg0_l.grf_norm_y` at threshold 0.05.
Any deviation triggers V3.

### 4.3 Which controller is measured — registered rule (rewritten, blockers B1+B2)

⛔ **The previous rule selected among `*.par.sto` files already present in the run directory. It is
withdrawn.** SCONE's optimizer never writes a `*.par.sto`; 148 of 316 archived directories have none;
and every one that exists is a stale mid-run replay artefact (§0.4). A rule that ranks non-existent
files selects nothing, and a rule that ranks stale files selects the wrong controller.

**The registered rule now selects a `.par`, and the `.sto` is PRODUCED from it by §7.1a.**

> Within each run directory, the registered controller is the `.par` whose filename's **third
> underscore-delimited field (best fitness) is numerically smallest** — the MINIMUM-FITNESS `.par`.
>
> **ASSERTION (registered, mechanical, not advisory): that same `.par` must also be the
> MAXIMUM-GENERATION `.par` in the directory.** SCONE writes a `.par` only when the running best
> improves, so in an untouched run directory the best is necessarily the last. If the two disagree,
> the directory is not a monotone best-so-far series — files were copied in, deleted, or two
> processes wrote there — and **the seed fails the registered exclusion condition E5**. There is no
> tie-break and no repair.
>
> A tie for the minimum fitness is likewise **E5**: two distinct controllers claiming one best
> fitness is a condition the run is not supposed to be able to produce, and no tie-break rule is
> registered.

**Implemented in code, not only here:**
`C:\Users\maurice\Desktop\spasticity_paper\scone\sto_utils.py`,
`select_registered_par(run_dir)` → `{par, gen, fitness, max_gen, n_par}`, raising
`sto_utils.RegisteredSelectionError` (= exclusion E5) on every branch above. The analysis script must
record `par`, `gen`, `fitness`, `max_gen` and `n_par` for all 80 runs.

Verified on seven archived directories on 2026-08-02 — `DOSER0000/1050/2071/3100_s1`, `SPAS005_s2`,
`SPAS01_s3`, `HEALTHY_s1` — all seven select a unique minimum-fitness `.par` that is also the
maximum-generation `.par` (gen 34/34/41/26/320/333/22), so the assertion is satisfiable, not merely
strict.

---

## 5. Threshold for "no clinically recognisable equinus"

Post-stroke ankle MDC in this literature is **3.8–11.5 deg**. Registered:

* **Primary threshold: 3.8 deg** — the *most generous to detection* end of the range, chosen so that a
  null result cannot be blamed on an insensitive criterion.
* **Secondary threshold: 11.5 deg** — the conservative end. The same fixed sequence is run at 11.5 and
  reported as an explicitly labelled secondary; it does not share multiplicity with the primary and
  cannot rescue a primary null.

Verdict language, fixed now:

* **EQUINUS** at a dose ⟺ the one-sided 95 % lower confidence bound on Δ_EQ exceeds 3.8 deg.
* **NO CLINICALLY RECOGNISABLE EQUINUS** at a dose ⟺ the two-sided 95 % upper bound on Δ_EQ is
  below 3.8 deg.
* **INDETERMINATE** otherwise (the CI straddles 3.8). An indeterminate cell is reported as
  indeterminate; it is never described as null.

---

## 6. Stopping rule and warm-start policy — IDENTICAL in every cell

Written into `TEMPLATE_working.scone` once and inherited unchanged by all 5 cells including the
control. Any per-cell deviation voids the study (V-class failure).

⛔ **CORRECTED 2026-08-02 (blocker B7). Until this revision the template did not contain these
values.** `C:\Users\maurice\Desktop\spasticity_paper\scone\opt2\TEMPLATE_working.scone` carried
`min_progress = 1e-4` and **no `max_generations` at all**, and nothing anywhere compared the template
against this table. A scenario keeping `1e-4` stops when the fitness landscape flattens — and it
flattens at a different generation for every dose, which is precisely the depth confound this section
exists to remove. Three changes, all made before launch:

1. **The template now carries `min_progress = 0` and `max_generations = 250`.**
2. **`gen_conditions.apply_registered_stopping_rule()`** writes both into every generated scenario
   structurally (rewriting an existing declaration or inserting one after `CmaOptimizer {`), then
   **reads them back and raises** if the write did not land — the same discipline `set_seed` had to
   adopt after a silent `str.replace` no-op wrote no `random_seed` at all.
3. **`gen_seeds.assert_registered_stopping_rule(built)`** is a PRE-LAUNCH GATE over all 80 generated
   scenarios: each must declare `min_progress` and `max_generations` **exactly once** with the
   registered values, and must carry a `random_seed` that is **distinct within its cell**
   (`assert_distinct_seeds`). It raises before anything is launched.

`random_seed` is deliberately absent from the template, because it must differ per seed; it is
written per-seed by `gen_seeds.set_seed()` and asserted by the gate above.

Executed 2026-08-02 on the 80 generated DR2K scenarios:
`stopping-rule check: 80/80 scenarios carry min_progress = 0 and max_generations = 250 (terminal
generation index 249)`, and `seed check: 80/80 scenarios carry a random_seed`, 16 distinct per cell.

| property | registered value |
|---|---|
| `init_file` | `ResultH0914Gait10.par` — the healthy reference, for every cell including KV = 0.200 |
| `min_progress` | `0` |
| `max_generations` | `250` — terminal generation index **249** (see §8; generation 250 never exists) |
| `random_seed` | `1 … 16`, written by `gen_seeds.set_seed()` and read back and asserted |
| `max_duration` | `10` |
| `fixed_control_step_size` | `0.005` |
| `integration_accuracy` | `0.002` |
| `state_init_file` | `InitStateGait10.zml` |
| `initial_state_offset` | `"0~0.01<-0.5,0.5>"` |
| model file | `H0914M_osim4.osim`, **unmodified**, in every cell — this study lesions the controller only, never the plant |

**No cell may be warm-started from another cell's result.** All 80 runs start from the same healthy
`.par`.

### Why any variation is fatal — and it is not hypothetical

* **Warm start.** The 36 free parameters form a shared, warm-startable layout *only because the
  injected block declares no free parameter*. Verified: the emitted `.par` has exactly 36 lines in
  `HEALTHY_s1..s4`, `DHEALTHY_s1`, `SPAS005_s2`, `SPAS01_s2`, `DOSER0000_s1`, `DOSER3100_s1` — control
  and treated alike. If one cell were warm-started from a spastic optimum and another from healthy,
  CMA-ES would begin in a different basin. The endpoint is a *difference between converged optima*,
  and the observed multi-modality at fixed dose is large (SD 2.678–4.502 deg). An initialisation
  difference is then arithmetically indistinguishable from a dose effect. It is not a bias that can
  be corrected for afterwards; it is the same number.
* **Generation cap.** Verified in §0.6: at generation 100 the archived spastic runs sit 3.7 %–38.6 %
  above their final fitness. A cell stopped earlier yields a systematically worse controller, and a
  worse controller walks differently. Crucially, **the runs that keep improving longest are the
  spastic ones** — so an unequal cap biases *in the direction of the hypothesis*.
* **`min_progress`.** A non-zero `min_progress` makes the stopping generation a random variable that
  depends on the fitness landscape, which differs by dose. `min_progress = 0` with a hard
  `max_generations` makes depth a constant of the design rather than an outcome of it.

---

## 7. Per-cell gates, exclusion, and the STRUCTURAL certification of the control

### 7.1a THE REPLAY STEP — registered (blockers B1+B2)

**No `.sto` exists until this step produces it.** This step runs once per seed, before every
instrument, and is the sole origin of every number in the study.

| item | registered value |
|---|---|
| **which `.par` is replayed** | the one selected by **§4.3**: minimum-fitness, asserted to be maximum-generation, else E5 |
| **isolated output directory** | `C:\Users\maurice\Desktop\spasticity_paper\scone\replay_registered\<run-directory-name>\` — one directory per seed, created by the step |
| **exact command** | `"C:\Program Files\SCONE\bin\sconecmd.exe" -e <isolated-dir>\<GGGG_median_best.par>` with `cwd = <isolated-dir>` |
| **what is copied in** | the chosen `.par`; `config.scone`; every `*.osim`; every `*.zml`; `ResultH0914Gait10.par` — all **copied** out of the run directory, which is opened read-only |
| **provenance of `config.scone`** | the `config.scone` **SCONE itself archived inside the run directory at launch** — NOT `opt_seeds\<TAG>_s<k>.scone` and NOT `opt2\<TAG>.scone`, either of which may have been regenerated or edited after the run started. Its SHA-256 is written to `PROVENANCE.json` beside the `.sto`, so C1 can be re-run later against the exact bytes replayed |
| **acceptance** | exactly one `.sto` larger than 1000 bytes must exist in the isolated directory afterwards. Any other count is **E5** (`status = "E5_STO_<n>"`) |
| **record kept** | `PROVENANCE.json`: source directory, chosen `.par`, generation, fitness, `max_gen`, `n_par`, SHA-256 of `config.scone` and of the produced `.sto`, the exact command, return code, UTC timestamp |
| **implementation** | `C:\Users\maurice\Desktop\spasticity_paper\scone\replay_all.py`, `replay_registered(run_dir)`; CLI `python replay_all.py --registered <run-dir> …` |

**NEVER IN PLACE.** The isolated directory is the only place anything is written or deleted.
`replay_all.py`'s own comment records why: replaying into the results directory and then taking the
newest `*.sto` there "can silently pick up a stale file from an earlier replay of a DIFFERENT
generation — which previously caused features to be read from gen-6 controllers while the reported
fitness came from the best par." That is exactly the defect §0.4 measures, and it is also why
**`replay_final.py` must NOT be used for this study**: it replays inside the run directory after
deleting the run directory's `.sto` files.

**Executed once during registration, to prove the command works** (one `sconecmd -e`, no
optimization): on `DOSER3100_s1.H0914M.GH2010.S10W.D10.I.R1` → selected
`0026_31.656_0.853.par` (generation 26 = max generation), status `ok`, exactly one `.sto`
produced in the isolated directory, and the source directory verified byte-for-byte unchanged
afterwards (still holding its 15 `.par`, its 2 stale `.sto`, `history.txt`, `config.scone`,
`optimization.log`). The endpoint it yields is in §0.4(c).

### 7.1 Staging (applies to all cells)

After §7.1a, each seed's isolated replay directory already contains `config.scone` and **exactly one
`.sto`** — the one produced from the §4.3 controller — so it *is* the staged directory; no second copy
step is required. The property that matters is unchanged and is asserted by §7.1a: run against a
directory holding two `.sto`, `delivered_gain.py` raises
`expected exactly one .sto beside config.scone, found 2` and ABSTAINs — verified live on
`DOSER0000`, `DOSER2071`, `DOSER3100`. Staged, the same runs return PASS.

Staging and replay **copy**; they never delete or move anything under
`C:\Users\maurice\Documents\SCONE\results\`.

### 7.2 Exclusion criteria (seed-level, mechanical, evaluated in this order)

| code | criterion |
|---|---|
| **E1 FELL** | `t_end < 9.9` s (max_duration is 10 s; all archived surviving runs read exactly 10.00) |
| **E2 NOT WALKING** | `cycle_features(..., side="l")` returns `None` — fewer than 2 complete GRF-delimited cycles after the 1.0 s settle |
| **E3 DEGENERATE GAIT** | best fitness > **2.0**. Non-tuned: the archive's walking runs span 0.60–1.14 and its failed runs 8.63–83.98; the interval (1.14, 8.63) is empty, and 2.0 lies inside it |
| **E4 UNCONVERGED** | ⛔ **CORRECTED AGAIN 2026-08-02 — the 5 % improvement clause is REMOVED. It was symmetric in form and asymmetric in effect.** The clause dropped seeds still improving at generation 249; the one archived run it excludes is **`SPAS01_s3` (7.49 % over 199→249)**, which is **the only converged top-rung run showing no equinus at all** (+2.6563 deg, dorsiflexed) against `SPAS01_s4` at −10.6019. **§6 of this document argues at length against depth-correlated exclusion, and E4 reintroduced exactly that bias inside a nominally equal cap** — an exclusion whose rule is neutral and whose effect is to remove the evidence against the hypothesis. **Replaced by a convergence criterion uncorrelated with the endpoint:** the largest generation index in `history.txt` is **< 249**. That is it. Every seed reaching the registered generation budget is analysed. **The improvement rate is still RECORDED for every seed and reported as a both-ways sensitivity** (analysis repeated with and without the seeds that would have failed the old 5 % clause), so the information is retained without letting it decide inclusion |
| **E5 AMBIGUOUS RECORD** | §4.3 does not select exactly one `.par` (no parseable `.par`; a tie for the minimum fitness; or the minimum-fitness `.par` is not the maximum-generation `.par`), **or** §7.1a's isolated replay does not produce exactly one `.sto`, **or** the resolved ankle/GRF column or threshold differs from §4.2 |

**E4's off-by-one, measured rather than assumed (blocker B8).** The convention was read off 107
archived runs that declare an explicit `max_generations`. Every run that reached its cap has a
`history.txt` with **exactly `max_generations` data rows, indexed 0 … max_generations − 1** — e.g.
`CMW70_s1`, `CMW80_s1`, `DHEALTHY_s1..s3`, `DPAR20_s1..s3`, `DPAR40_s1..s3`, `EQS010_s1..s3` all
declare `max_generations = 90` and all end at row index **89** with 90 rows;
`CTLUP1`/`CTLZERO` declare 12 and end at 11.

Therefore **`max_generations = 250` ⇒ the terminal generation index is 249, and generation 250 NEVER
EXISTS.** The registered `200 → 250` window and §8's `rb(250)` were both unsatisfiable: no
`history.txt` in this study can contain a row for generation 250, so a fail-closed analysis would
have excluded **all 80 seeds** under E4 and an unguarded one would have crashed. The window is now
**199 → 249** (still 50 generations, still 20 % of the run) and the terminal statistic is `rb(249)`.

**"Last generation" means the largest generation index in `history.txt`, and nothing else.** It must
NOT be read from `.par` filenames. SCONE writes a `.par` only on an improvement, so the highest `.par`
generation is systematically below the last generation run — measured: `DPAR60_s1` ran 90 generations
with its highest `.par` at generation **29**; `DPAR20_s2` 90 generations, highest `.par` at **37**;
`CMW80_s2` 90 generations, highest `.par` at **57**. Reading E4 off the `.par` names would have
excluded most or all of a fully converged study. (In the other direction, `.par` indices may exceed
the last `history.txt` index — `SPAS005_s2`: history ends at 319, highest `.par` is 320 — which is a
second reason the two must not be conflated.)
| **E6 UNVERIFIED DELIVERY** | treatment cells only: `delivered_gain.py` verdict ≠ `PASS` on the staged directory. The gate is the tool's own: `\|copies − 1\| ≤ 1e-3` and `\|rho − 1\| ≤ 0.15`. ⛔ **AMENDED 2026-08-02: the ±0.15 rho tolerance is too loose to keep the abscissa honest.** At true KV 0.200 it admits delivered gains from **0.170 to 0.230** — a **26 % span**, wider than the 0.100→0.150 rung spacing, so two seeds nominally at the same dose can differ by more than one registered step and the x-axis of §9.2 is not the quantity it is labelled. **Registered fix: every seed's MEASURED `K_hat` is recorded and the analysis uses it as the abscissa, not the nominal KV.** The ±0.15 gate is retained only as an outlier screen. This is preferred to tightening the tolerance because it keeps every delivered seed while making §9.2's x-axis exactly what the section claims it is |

### 7.3 Reporting of exclusions — a headline number

The abstract and the results table both carry: **total seeds excluded / 80**, and a 5 x 6 matrix of
exclusion counts by cell and by code. Per-cell exclusions are reported as k/16. A cell falling below
n_retained = 9 is labelled INDETERMINATE-BY-ATTRITION (§3.3). Study-wide exclusions above 30/80
trigger V8.

### 7.C STRUCTURAL certification of the KV = 0 control

The control cannot be certified by measuring a delivered signal, because a zero-gain reflex emits no
signal — verified in §0.3. It is certified by proving it was **correctly instantiated**. All five
checks must pass; failure of any one triggers V2.

**C1 — BLOCK IDENTITY (file-level).** Extract, by brace matching, the `ConditionalController` whose
subtree contains `name = SpasticL`, from every one of the 80 `config.scone` files. Normalise the two
`KV = %.3f` numerals to a placeholder. Assert the 80 normalised blocks are **byte-identical**. This
proves the control differs from the treatment cells in the gain literal and in nothing else —
not in `legs`, not in `states`, not in target names, not in `delay`, not in `allow_neg_V`, not in
placement within `ConditionalControllers`. Verified feasible: `DOSER0000`'s block sits at
`config.scone` lines 150–168 in exactly this form.

**C2 — SIMULATOR ACCEPTANCE (startup log).** The specific silent failure this project has already
suffered is a block that SCONE *parses, names in* `Warning, unused properties:`*, and then ignores*
(documented in `gen_conditions.make_scenario` lines 139–157; the same class of failure produced the
0x losses `SPASpf`, `SPASpf2`). That failure is invisible in the `.sto` and invisible to
`delivered_gain.py` on a zero-gain cell. It is visible **only** in SCONE's own startup output.

⛔ **CORRECTED 2026-08-02 (blocker B4). The string this condition demanded does not exist in the
registered launcher's output, so C2 was unsatisfiable and would have voided the study under V2 on all
80 cells.** Two separate facts, both measured:

* **The results-directory `optimization.log` is not a usable artefact.** Of the **328** archived
  `optimization.log` files under `C:\Users\maurice\Documents\SCONE\results\`, **327 are zero bytes**.
  The single exception is
  `C:\Users\maurice\Documents\SCONE\results\PF60L.H0914M.GH2010.S10W.D10.I\optimization.log`, 85
  bytes, holding
  `00:57:52 Starting optimization PF60L.H0914M.GH2010.S10W.D10.I dim=36 lambda=14 mu=7`.
  That one line is where the old C2 format came from — a file the pipeline does not reliably
  produce. Run against a zero-byte one, this project's own instrument correctly refuses:
  `check_unused.py` returns **`LOG UNUSABLE (0 bytes)`**, not a pass.
* **The launcher log — the artefact that IS produced — uses a different format.**
  `gen_seeds.py --launch` captures `sconecmd`'s stdout+stderr to `opt_seeds\log_<TAG>_s<k>.txt`
  (no `-q`, `stdout=lg, stderr=STDOUT`), and `gen_conditions.py --launch` was fixed the same way on
  2026-08-02 (`-q` removed, redirect added, logs to `opt2\launch_logs\log_<TAG>.txt`). Measured on
  the 16 surviving launcher logs in `opt_seeds\` (31.7–42.6 kB) and 6 in `opt_spseed\`
  (428–510 kB), the startup block is:

  ```
  16:04:44 SCONE version 2.4.4.3333
  16:04:44 Created model H0914M; dofs=9 muscles=14 mass=74.5314
  16:04:44 Imported 29 of 36, skipped 8 parameters from ...\ResultH0914Gait10.par
  16:04:44 pooled_evaluator started threads: 32
  16:04:44 Creating folder C:/Users/maurice/Documents/SCONE/results/HEALTHY_s1.H0914M.GH2010.S10W.D10.I.R1
  Starting optimization, dim=36
  ```

  The line is **`Starting optimization, dim=36`** — no timestamp, no tag, and **`lambda=` and `mu=`
  do not occur anywhere in the file** (`grep -c "lambda=" → 0`).

**C2, restated against what the registered launcher actually emits.** Certification requires, for
every one of the 80 runs, all four:

1. `C:\Users\maurice\Desktop\spasticity_paper\scone\opt_seeds\log_<TAG>_s<k>.txt` exists and is
   non-empty (observed size for a completed run: tens to hundreds of kB);
2. it contains the literal line **`Starting optimization, dim=36`** — this carries C3's `dim` as
   well, and is the only place `dim` appears;
3. it contains a line **`Creating folder C:/Users/maurice/Documents/SCONE/results/<TAG>_s<k>.…`**,
   which is what BINDS the log to its results directory (the log filename alone does not);
4. it contains **no** occurrence of `unused propert`, as adjudicated by
   `check_unused.check(log_path)` — which must return `ok`, and which fails closed with
   `NO LAUNCHER LOG` or `LOG UNUSABLE` rather than passing on an absent or truncated file.

The `gen_conditions.py --launch` path remains **forbidden for this study** — not because it destroys
the log any more (it no longer does) but because it launches the 17-entry `CONDITIONS` table, not a
per-seed cell set, and writes no `random_seed`.

**C3 — PARAMETER-LAYOUT IDENTITY.** `dim=36` in the startup line and 36 lines in every emitted `.par`,
in all 80 runs. This proves the injected block introduced no free parameter, and therefore that the
`init_file` warm start applies identically in the control and in every treatment cell. Verified
achievable across 9 archived runs (§0.7).

**C4 — INSTANTIATION-BY-CONSTRUCTION SIDECAR.** C1–C3 still cannot distinguish *"block present, gain
zero"* from *"block silently discarded"*: both produce zero delivered signal. One extra run closes it.

Take the control's **own scenario file**, change **only** the two literals `KV = 0.000` → `KV = 0.050`,
and assert by diff that exactly two lines changed. Run that sidecar with `max_generations = 1`. It is
not part of the study; no endpoint is computed from it. Certification requires:

1. the sidecar's `.sto` header contains `soleus_l.RV` **and** `gastroc_l.RV` — channels the control's
   `.sto` cannot contain by construction (verified: `DOSER0000` has `soleus_l.input` but none of
   `soleus_l.RV`, `gastroc_l.RV`, `soleus_l.V`, `gastroc_l.V`, while `DOSER1050` has all four); and
2. `delivered_gain.py` returns `PASS` on the staged sidecar with `|copies − 1| ≤ 1e-3` for **both**
   muscles and `ctrl(soleus_r) = ctrl(gastroc_r) = 0`.

Because the sidecar and the control differ by exactly two numerals, a PASS on the sidecar certifies
that **the block as written in the control's own file** is instantiated exactly once, on the left leg,
wired to `soleus_l` and `gastroc_l`. One sidecar suffices for the cell (the block text is identical
across seeds; only `random_seed` differs, and C1 verifies that per seed).

**C5 — NULL-DELIVERY CERTIFICATE.** `delivered_gain.py` on every staged control seed must return
`PASS` with `|D|max` exactly `0.000e+00` for both `soleus_l` and `gastroc_l`, and `0.0e+00` of
undeclared drive on `soleus_r` and `gastroc_r`. Verified reproducible (§0.3).

**C5 is recorded as VACUOUS and is explicitly NOT accepted as evidence of instantiation.** `rho` reads
`n/a` and `copies` is undefined; the PASS is produced by a branch that only flags "declared 0 but
something delivered". Its evidentiary value is exactly one proposition — *nothing arrived* — which is
what the control requires. Instantiation is established by C1–C4 and by nothing else.

**What has NOT been done here.** The signal gate that failed on the control — `|copies − 1| ≤ 1e-3`,
`|rho − 1| ≤ 0.15` — is **unchanged**, and it applies unchanged to all four treatment cells. It is not
loosened, not widened, and not made conditional. It is simply **not applicable** to a cell in which the
measured quantity does not exist, and the control is certified by a different instrument that measures
something that does exist: the scenario's structure, the simulator's acceptance of it, the parameter
layout, and a two-byte perturbation of the control's own file.

---

## 8. Depth / convergence verification per cell

Per seed, from `history.txt`: compute the running-best fitness `rb(g) = min{best_fitness(g') : g' ≤ g}`
and record `rb(49)`, `rb(99)`, `rb(149)`, `rb(199)`, `rb(249)`, the final value, and the last
generation index. E4 (§7.2) excludes any seed whose last `history.txt` generation index is below 249,
or that improved by more than 5 % over generations 199→249.

⛔ **Indices corrected 2026-08-02 (blocker B8).** This section previously asked for `rb(250)` and a
`200→250` window. `history.txt` is 0-indexed and holds exactly `max_generations` rows, so with
`max_generations = 250` its indices run **0 … 249 and generation 250 does not exist** — measured on
107 archived runs (§7.2). `rb(250)` was undefined for every seed the study can produce, which would
have excluded all 80 cells under a fail-closed reading. The window `199→249` spans the same 50
generations.

Per cell, report: median and range of `rb(249)`; median and range of the 199→249 improvement; and the
count of E4 exclusions.

**Cross-cell depth homogeneity check.** Kruskal–Wallis on the seed-level 199→249 improvement across
the 5 cells. If p < 0.05, the cells are not equally converged and the primary comparison is confounded
by depth; report this prominently alongside the result. This is a **reported diagnostic, not an
exclusion** — using it to drop cells after seeing the data would be a post-hoc rule.

**Why 250 and not 90 or 100.** Verified §0.6: at generation 100 the archived spastic runs sat
3.7 %–38.6 % above their eventual best. At 250 the residual to the eventual best is 0.00 %–3.01 % and
the 200→250 improvement is 0.83 %–7.49 % (those §0.6 figures were computed on runs of 280–330
generations, where both 200 and 250 exist as indices; the gate itself uses 199→249, §7.2). A 90-generation cap measures unconverged controllers, and it
does so *differentially by dose*.

---

## 9. Falsification conditions and the fixed analysis plan

### 9.1 What would falsify the dose–response premise

* **F1 MONOTONICITY.** Jonckheere–Terpstra test for an ordered alternative in EQ across the 5 cells
  (increasing equinus with increasing KV), one-sided, α = 0.05, on seed-level values from analysable
  cells. **A non-significant JT with all 5 cells analysable falsifies the premise that this injection
  produces a graded equinus.** Report and stop; do not fall back to pairwise comparisons.
* **F2 LINEARITY.** F test for lack of fit of the registered linear model (§9.3) against the saturated
  one-mean-per-cell model. If p < 0.05, the continuous transition-point estimate is **not reported at
  all** and only the discrete bracket of §9.2 stands. No alternative functional form may be fitted.
* **F3 SPECIFICITY (contralateral control).** ⛔ **CORRECTED 2026-08-02 — a magnitude floor is added,
  and without it F3 was near-certain to fire for reasons unrelated to specificity.**

  **The defect.** The ratio clause `|Δ_EQ_right| > |Δ_EQ_left|` **has a denominator the design
  deliberately drives to ≈ 0 at the low rungs.** `DR2K050` and the control are registered *expecting*
  `Δ_EQ_left ≈ 0`; any contralateral noise then exceeds it and F3 trips. **Measured on archived data,
  F3 fires on 6 of 10 injected runs, including both certified 0.100-cell runs** — so the rung
  registered to demonstrate nothing is exactly where the falsifier trips, **and tripping it kills the
  whole study.** Same shape as F4 before it was corrected: a falsifier firing on the design rather
  than on the phenomenon.

  **Corrected criterion.** The identical phenotype is computed on `side="r"`. F3 fires if, in any
  analysable cell:

  1. **`Δ_EQ_right` exceeds 3.8 deg** — the absolute clause, unchanged and unconditional; **or**
  2. **`|Δ_EQ_right| > |Δ_EQ_left|` AND `|Δ_EQ_left| ≥ 3.8 deg`** — the ratio clause, now gated by a
     **magnitude floor on its own denominator.**

  **Rationale for the floor.** The ratio clause exists to detect *"the response is bilateral rather
  than unilateral."* That question is only meaningful where there is a left-side response to be
  bilateral about. Below the decision threshold there is no established left-side effect, so the
  ratio is a comparison of two noise terms and its firing carries no information about specificity.
  **The floor is set at the same 3.8 deg used everywhere else in this document, so it introduces no
  new free parameter.**

  (`delivered_gain.py` already verifies `soleus_r`/`gastroc_r` carry `0.0e+00` of undeclared
  drive, so any right-side kinematic shift is compensatory, which is a legitimate finding but not this
  phenotype.)
* **F4 SATURATION — branch written out in full BEFORE launch (blocker B3).**

  **Statistic.** For each retained seed and each muscle m ∈ {`soleus_l`, `gastroc_l`}, compute
  `f_sat(seed, m) = Σ|RV|[input > 1] / Σ|RV|` on the seed's registered `.sto` (§7.1a). Report all
  `f_sat` values per seed; they are part of the results table, not an internal quantity.

  **Aggregation rule, fixed now.** A cell is **F4-SATURATED** iff the **median of `f_sat` over the
  cell's retained seeds exceeds 15 % for either muscle.** Median, not "any seed": with a measured
  seed-to-seed range of 6.89–15.56 % at true KV 0.200, an "any seed" rule is decided by the single
  most extreme optimum, and a rule whose outcome one seed can flip is a rule that gets re-read after
  the data arrive. The 15 % threshold itself is unchanged and is not adjustable (§1.2).

  **Consequence branch, fixed now — every arm of it.** If a cell is F4-SATURATED:
  1. it is **reported in full** — n_retained, mean, SD, Welch CI, per-seed `f_sat` — and labelled
     *"delivered dose understated: median gastroc/soleus discard = X %"*;
  2. it is **excluded from the §9.3 step-7 linear fit and from `KV_hat`**, because its abscissa (the
     delivered dose) is not the value plotted;
  3. it **remains in the §9.2 fixed sequence and in F1 (Jonckheere–Terpstra)**. Those are statements
     about the *declared* dose, which is what an experimenter controls, and dropping the top rung
     from the sequence after seeing `f_sat` would change the sequence's starting point on the basis
     of data — the exact prohibition in §9.3;
  4. **if the F4-SATURATED cell is the ladder top (`DR2K200`)** — the outcome §0.5 says is most
     likely — the fixed sequence still starts there and the reported result reads
     *"KV\* = k, with the ladder top saturated: the true delivered dose at 0.200 is below 0.200 by an
     unmeasured amount, so KV\* is an upper bound on the declared-dose transition and the
     dose–response slope above 0.150 is not estimated."* No rung is added, removed or re-run;
  5. **if EVERY treatment cell is F4-SATURATED**, no dose–response is reported: the study reports
     *"the injection saturates before the phenotype does across the whole registered ladder"*, which
     is a falsification of the dose–response premise and terminates the study exactly as F1 does.

  **Measured basis (§0.5, corrected).** soleus/gastroc: 0.00 %/2.58 % at true KV 0.050;
  0.00 %/~2.97 % at 0.071; 0.00 %/1.51–11.16 % at 0.100 (n = 6); **2.32–5.31 % / 6.89–15.56 % at
  0.200 (n = 6, gastroc median ≈ 12.1 %, one run already over 15 %)**. The earlier claim that this
  gate "should not bind" on the registered ladder is **withdrawn**: it is expected to bind at the top
  rung, which is why the branch above is registered rather than deferred.
* **F5 CONTROL ANCHORING.** The control cell's mean EQ must lie within 3.8 deg of the archived healthy
  mean (1.263 deg, i.e. within [−2.537, 5.063]). If it does not, the KV = 0 cell is not a healthy
  baseline and Δ_EQ is a difference against an unknown reference. Report; the study is **not** voided
  (Δ_EQ remains internally interpretable), but every absolute claim about equinus magnitude is
  withdrawn.

### 9.2 Transition point — identified by a rule fixed before any data exist

**Fixed-sequence (step-down) testing on the ordered ladder.** Doses are tested in decreasing order —
0.200, 0.150, 0.100, 0.050 — each by a one-sided Welch t test of

> H0: Δ_EQ(KV) ≤ 3.8   vs   H1: Δ_EQ(KV) > 3.8,  α = 0.05

on seed-level EQ, cell versus control. Testing continues while H0 is rejected and **stops at the first
non-rejection.**

> **KV\* = the lowest dose at which the sequence is still rejecting.**

Because the sequence is fixed in advance and monotone, family-wise error is controlled at 0.05 with
**no multiplicity adjustment and no adjustable parameter**. If the first step (0.200) fails, KV\* is
undefined and stopping rule S-B (§1.1) applies.

**The bracket is part of the answer.** With 0.050 spacing, the reported result is
"the transition lies in (KV\* − 0.05, KV\*]", i.e. KV\* ± 0.025. No finer claim is permitted from the
discrete ladder.

The same sequence is run at the 11.5 deg secondary threshold and reported separately and as
secondary.

### 9.3 Fixed analysis plan (no step is chosen after seeing data)

> ### ★ REGISTERED ANALYSIS CODE — HASH, added 2026-08-02 round 43
>
> **This document contained NO hash of anything.** Blocker B8's remedy was *"write the analysis
> code, dry-run it, and hash it into the document before launch"*; the code was written at round 42
> and prints `hash this into the pre-registration` on every run, and **the hash was never entered.**
> A hash that is computed and not recorded is not a hash — it is a printout. Half a control is the
> half that does not work.
>
> | artifact | bytes | sha256 |
> |---|---|---|
> | `scone/dose_response_v2.py` | **26,689** | **`401997fa1e3eaeb77cf1f73f9481874d1154f77a66f39dc2f19c7144a0b51e25`** |
> | `paper/FROZEN_MANIFEST.json` | 299,223 | `faae1e369bb5c6e27df682d22512388c6ae9d1ddc623fb9035b9cd3fdc72e7c8` |
>
> **The script changed three times on 2026-08-02** — `384ed943…` → `47b9c9d9…` → `401997fa…` —
> under the padding fix, the signed-transition fix, and the cell-count reconciliation. **Each change
> was to a quantity that decides the study's result, and without a recorded hash none of them would
> be detectable after the fact.** That is precisely the interval in which this project's defects
> have always lived.
>
> **Binding: any edit to `dose_response_v2.py` after launch invalidates the study unless the new
> hash is recorded here with the reason, before the endpoint is recomputed.**
>
> ⛔ **Step 0 below still says "all 80 scenarios". The registered launch set is 70** (§3.3, as
> corrected): 64 dose + 6 H2, no healthy cell. Named as outstanding rather than silently edited,
> because §9.3's steps are a registered sequence and rewriting them wholesale mid-round is how the
> `abs()` transition rule survived — a printed rule describing a different rule from the one that
> ran.

0. **Run the registered instruments on all 80 scenarios and their launcher logs (§12), BEFORE any
   endpoint is computed.** `check_structure.py` must return `OK` for all 80; `verify_placement.py`
   must return `PASS_WITH_UNVERIFIED` for all 80 (it never returns a bare `PASS` — §12);
   `check_unused.check()` must return `ok` for all 80 logs. Any other verdict is C1/C2 failure → V2.
1. **Replay every seed (§7.1a)**, then stage (§7.1). Record for each run: the selected `.par`, its
   generation, its fitness, the directory's `max_gen` and `n_par`, the SHA-256 of the replayed
   `config.scone` and of the produced `.sto`, the resolved column names, the GRF threshold, the
   `.par` line count, and the `dim=` from the startup log.
2. Run all §7 gates and §7C. Freeze the exclusion table. **No later step may alter it.**
3. Compute EQ per retained seed (§4.1). Report per-cell n_retained, mean, SD, and the seed-level values.
4. **F5**, then **F3**, then **F4**. Any trigger is applied before step 5.
5. **F1** (Jonckheere–Terpstra). If non-significant with all cells analysable: report the falsification
   and stop.
6. **§9.2** fixed sequence at 3.8 deg → KV\* and its bracket. Report Welch 95 % CIs on Δ_EQ for all four
   treatment cells regardless of where the sequence stopped.
7. **F2** lack-of-fit F test of `EQ_ij = β0 + β1·KV_i + ε_ij` (OLS on seed-level values, all analysable
   cells including the control) against the one-mean-per-cell model. If p ≥ 0.05, report β1 with its
   95 % CI and the continuous estimate `KV_hat` solving `β1·KV = 3.8`, with a 95 % CI from a
   nonparametric bootstrap over seeds — **10 000 resamples, stratified by cell, percentile method,
   `numpy` seed fixed at 20260802**. If p < 0.05, report the lack of fit and **omit `KV_hat` entirely**.
8. Depth diagnostics and the Kruskal–Wallis homogeneity check (§8).
9. Secondary, all explicitly labelled and none able to rescue a primary null: the 11.5 deg sequence;
   `ank_hs`; `ank_rom`; `stance_frac`; `cycle_time`; per-cell saturation fractions.

**Not permitted at any point:** adding a rung, adding a seed, replacing an excluded seed, changing the
primary phenotype, changing a threshold, changing the fixed sequence order, fitting any functional
form other than the registered linear one, or reporting a transition point when F2 fails.

---

## 10. What this design CANNOT establish

1. **It cannot distinguish spasticity from weakness.** There is no weakness arm and no discrimination
   analysis. Nothing here bears on the clinical question of which treatment a given patient needs.
2. **It cannot attribute the equinus to the reflex rather than to the optimizer's response to it.**
   Δ_EQ is a difference between two *converged optima*: the reflex is injected and then CMA-ES re-tunes
   all 36 parameters around it. Separating "the reflex holds the foot down" from "the controller
   adapted into a plantarflexed gait" requires a frozen-controller arm, which this design does not
   have. The archive's frozen-controller ceiling is true KV ≈ 0.010
   (`scone_naive_ladder.json`: nominal 0.005 walks, nominal 0.010 and above fall) — roughly **20 x
   below** the adapted ladder — so the frozen number cannot stand in for the adapted one.
3. **Seeds are not subjects.** n = 16 is 16 local optima of one optimizer on one body model
   (`H0914M_osim4.osim`), one controller family (Geyer–Herr, 36 parameters), 2-D sagittal, level ground,
   one cost function, one speed target. Every CI is a within-model, within-controller-family precision
   statement. **No population or clinical inference is licensed.**
4. **It cannot localise the transition below ±0.025 in true KV**, the half-spacing of the ladder —
   and even the continuous `KV_hat`, if F2 permits it, is an interpolation under an assumed linear form.
5. **It says nothing about true KV > 0.200**, and nothing about whether the model's failure above true
   KV ≈ 0.4 (`SPAS02`, archived nominal 0.20: fitness 40.24 at generation 19, no `.sto`) is a
   physiological ceiling or an optimizer failure. Under stopping rule S-B the ladder is not extended to
   find out.
6. **It cannot validate `ank_stance_mean` as a clinical equinus measure.** It is a simulation kinematic.
   The 3.8–11.5 deg MDC range comes from instrumented human gait analysis; its transfer to this model's
   ankle angle is an assumption, not a result, and it is load-bearing for every verdict in §5.
7. **It inherits an unquantified transfer risk from the 2x defect.** Every number used to *place* the
   ladder (§2.1) came from a differently-wired controller. Delivery has been re-verified at 1.0x on two
   runs (§0.2), but only the **gain relabelling** is assumed to transfer; the archived **phenotype
   magnitudes** are not assumed to, and the study does not test them.
8. **It cannot detect a saturation effect confined to gastroc's already-clipped 34–47 % of the stride.**
   The `.sto` records the pre-clip contribution, so the F4 gate measures discarded drive by
   reconstruction, not by direct observation of what the muscle received.
9. **The 3.8 deg threshold is a floor, not a consensus.** A result of "equinus at KV\* = 0.150" means
   equinus at the most detection-generous end of the published MDC range; at 11.5 deg the answer may
   differ, which is why §5 registers the secondary.

---

## 11. Registered artefacts

* Generator: `C:\Users\maurice\Desktop\spasticity_paper\scone\gen_conditions.py`, `spastic_block(kv)`
  **unmodified**; the five cells `DR2K000/050/100/150/200` added to `CONDITIONS`; new
  `apply_registered_stopping_rule()` (§6).
* **Scenario generation (step 1 of the launch, registered):**
  ```
  python gen_conditions.py
  ```
  writes `opt2\DR2K{000,050,100,150,200}.scone`. ⛔ **Blocker B6: those five scenarios did not exist
  before 2026-08-02** — neither in `CONDITIONS` nor in `opt2\` — so any `--tags DR2K…` invocation
  would have printed "missing scenario" five times and launched nothing.
* **Seeds and launch (step 2, registered, exact):**
  ```
  python gen_seeds.py --tags DR2K000,DR2K050,DR2K100,DR2K150,DR2K200 \
                      --seeds 16 --max-concurrent 4 --launch
  ```
  ⛔ **Blocker B6, three defects in the previously registered command
  (`gen_seeds.py --seeds 16 --launch`):** it omitted `--tags`, so it would have fallen through to
  `DEFAULT_TAGS = HEALTHY,PAR20,PAR40,PAR60` and launched **64 optimizations of the wrong
  conditions**, all looking normal; it named DR2K scenarios that did not exist; and its launch loop
  `Popen`-ed every scenario back to back, starting **all 80 CMA-ES runs at once** against §3.4's own
  budget arithmetic ("80 runs at 4-way concurrency"). `gen_seeds.py` now **refuses to launch** without
  an explicit `--tags` and without an explicit `--max-concurrent`, and `launch_throttled()` holds the
  cap. It is the stdout+stderr-capturing path required by §7C2.
* Phenotype: `C:\Users\maurice\Desktop\spasticity_paper\scone\sto_utils.py`,
  `cycle_features(...)["ank_stance_mean"]`, **unmodified**. The same file gained
  `select_registered_par()` / `RegisteredSelectionError` (§4.3); `cycle_features`, `load_sto`, `col`,
  `grf_vertical` and `heel_strikes` are untouched.
* Replay step: `C:\Users\maurice\Desktop\spasticity_paper\scone\replay_all.py`,
  `replay_registered(run_dir)` (§7.1a). **`replay_final.py` is NOT part of this study** — it replays
  in place after deleting the run directory's `.sto`.
* Delivery instrument: `C:\Users\maurice\Desktop\spasticity_paper\scone\delivered_gain.py`, thresholds
  unmodified (`TOL_COPIES = 1e-3`, `TOL_RHO = 0.15`).
* Structural instruments: `check_structure.py`, `check_unused.py`, `verify_placement.py` — registered
  in **§12**, with the exact verdict strings each can emit.
* Scenario template: `C:\Users\maurice\Desktop\spasticity_paper\scone\opt2\TEMPLATE_working.scone`,
  now carrying `min_progress = 0` and `max_generations = 250` (§6).
* Raw output: `C:\Users\maurice\Documents\SCONE\results\DR2K{000,050,100,150,200}_s{1..16}.*`
* Replay output (the only place the study writes): 
  `C:\Users\maurice\Desktop\spasticity_paper\scone\replay_registered\<run-dir>\`
* Analysis script to be written at execution time as
  `C:\Users\maurice\Desktop\spasticity_paper\scone\dose_response_v2.py`. It must be committed **before**
  the exclusion table is inspected.

**Pre-launch state, verified 2026-08-02:** `gen_conditions.py` builds all 17 conditions including the
five DR2K cells at `min_progress = 0`, `max_generations = 250`; `gen_seeds.py --tags DR2K… --seeds 16`
builds **80** scenarios and both pre-launch gates pass (`80/80` carry the registered stopping rule,
`80/80` carry a `random_seed`, 16 distinct per cell); `check_structure.py` returns **`OK` on all 80**
and `verify_placement.py` returns `PASS_WITH_UNVERIFIED`, with actual chain
`CmaOptimizer/SimulationObjective/GaitStateController/ConditionalControllers/ConditionalController/ReflexController`.
**C1 is satisfiable and was checked in advance:** normalising `KV = %.3f` to a placeholder, the
injected block is **byte-identical across all 80 generated scenarios** (one distinct SHA-256,
`b3e0db1a715b8b0d…`), so the five cells differ in the gain literal and the `random_seed` and in
nothing else.

---

## 12. Registered instruments and their EXACT verdict strings

Blocker: `check_structure.py`, `check_unused.py` and `verify_placement.py` already implement
conditions C1 and C2 but appeared in **no registered step**, so nothing in the analysis plan ever ran
them. They are registered here, with the exact strings each can emit — because the failure this
avoids is a downstream check asserting the wrong literal and failing on all 80 cells.

### 12.1 `verify_placement.py` — THE SINGLE ENTRY POINT (C1 + C2 combined)

```
python verify_placement.py <scenario.scone | result-dir> [...] [--name SpasticL]
                           [--expect-reflexes 2] [--expect-kv X] [--log PATH] [--json]
```

| what it can return | meaning |
|---|---|
| `ERROR` | the input could not be read or parsed. Fails closed. |
| `FAIL` | at least one check failed; `failures[]` says which and why |
| `PASS_WITH_UNVERIFIED` | **every check that ran passed.** `could_not_verify[]` is never empty |

> ⚠ **IT NEVER RETURNS A BARE `PASS`.** There is no code path that emits the string `PASS` on its
> own. **Any downstream assertion written as `verdict == "PASS"` fails on all 80 cells.** The
> registered assertion is `verdict == "PASS_WITH_UNVERIFIED"`.

Process exit code: `0` **only if every target returned `PASS_WITH_UNVERIFIED`**, else `1`.
Confirmed by execution on `opt_seeds\DR2K000_s1.scone` (2026-08-02):
`1 target(s): 0 FAIL, 0 ERROR, 1 PASS_WITH_UNVERIFIED`, exit 0.

The always-populated `could_not_verify[]` items are, verbatim: *delivered gain magnitude*; *per-side
duplication factor*; *whether SCONE accepted the file at run time*; *SCONE's own acceptance of this
scenario* (when no usable log); *that this parser and SCONE's parser agree*; *model / .osim side of
the impairment*. `PASS_WITH_UNVERIFIED` is **not** a clean bill of health, and this document never
treats it as one — delivered gain is established by `delivered_gain.py` (E6/V1) and per-side
multiplicity by C4.

### 12.2 `check_structure.py` — C1, pre-run, reads the FILE

```
python check_structure.py <scenario.scone> [...] [--name SpasticL] [--expect-reflexes 2]
                          [--expect-kv X] [--json]
```

Per-target `status` is exactly one of **`OK`**, **`FAIL`**, **`ERROR`**. Exit code `0` iff every
target is `OK`, else `1`. Registered assertion: `status == "OK"` for all 80.

### 12.3 `check_unused.py` — C2, post-launch, reads the LAUNCHER LOG

```
python check_unused.py <log_TAG.txt> [...]
```

`check(log_path)` returns `(ok: bool, message: str)`. The summary line is **`PASSED:`** or
**`FAILED:`**; exit code `0` / `1`. Its log-parser state — `parse_unused_tree()` — is exactly one of

| state | consequence |
|---|---|
| `NO_LOG` | `ok = False`, message begins `NO LAUNCHER LOG` |
| `LOG_UNUSABLE` | `ok = False`, message begins `LOG UNUSABLE (<n> bytes)` — the log stops before `Creating folder` / `Starting optimization` |
| `NO_WARNING` | `ok = True`, message `no unused-property warning` ← **the only accepting state** |
| `WARNING` | `ok = False`; the message names the ACTUAL PARENT CHAIN the block landed under |

Registered assertion: `ok is True` and state `NO_WARNING`, for all 80 launcher logs.

⚠ Verified 2026-08-02: run against `DOSER3100_s1`'s archived `optimization.log` (0 bytes) this
instrument returns **`LOG UNUSABLE (0 bytes)`**, not a pass. That is the correct behaviour and it is
why C2 is written against `opt_seeds\log_<TAG>_s<k>.txt` and not against `optimization.log` (§7C2).

### 12.4 `delivered_gain.py` — E6 / V1 / C5, reads the `.sto`

Verdict is exactly one of **`PASS`**, **`FAIL`**, **`ABSTAIN`**,
**`NO_INJECTION_DECLARED_AND_NONE_DELIVERED`**. E6 excludes a treatment seed on any verdict ≠ `PASS`;
**V1 (§1.2) voids the study on `FAIL` specifically**, excluded or not.

`NO_INJECTION_DECLARED_AND_NONE_DELIVERED` deserves its own line: the tool used to identify an
injection by a target name ending `_l`/`_r`, the exact syntax the current 1.0x block removes, and it
therefore certified a correct unilateral delivery by silence. It now keys on the enclosing
controller's `name` (`SpasticL`), which is why the block's `name` is load-bearing and why C1 asserts
it per seed.

**Protected, never touched by this study:** anything matching `opt_s1*`, `opt_s2*`, `opt_s3*`,
`opt_s4*`, `KF60L`, `KE40L`, `HF60L`, `DF20L`, `PF20L`, `s1KF60L` under
`C:\Users\maurice\Documents\SCONE\results\`.

---

*Registered 2026-08-02. Any change to any section above requires a new version of this document
stating what changed and why, published before the affected cells are re-run.*
