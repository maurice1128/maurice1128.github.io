# PREREG_3d_speed_r202.md — walking speed as the provocation axis, in 3D

**Registered BEFORE any cell is launched.** *Supersedes the UNHASHED draft `PREREG_3d_speed_r201.md`
(9,328 B, pre-read sha256 `9ce3687678eeb15a…`), which was cold-read before hashing and failed: its
primary was not a computable quantity. **r201 is kept frozen as the record of what the rule caught and
is not edited.***

**Parents:** `PREREG_3d_matched_r174.md`, `PREREG_3d_replication_r179.md`.
**Step-1 arithmetic:** `paper/SPEED_DOSE_r200.json`, from `scone/speed_dose_r200.py`.

---

## 0. Why speed, and what step 1 does and does not establish

**Delivered dose = `KV × max(0, ce_vel_norm) × Fmax` over `soleus_l` and `gastroc_l`, with the
excitation clamp. Method from `dose_r174.py`, unmodified. It reproduces the registered 13.627 N.**

⛔ **THE DOSE-MATCHING ROUTE IS CLOSED ONLY CONDITIONALLY, AND AN EARLIER DRAFT CALLED IT "DEAD ON
ARITHMETIC", WHICH WAS WRONG.** *The correct statement: **IF** dose is linear in speed, then matching
KV 0.150's 40.880 N at KV 0.050 requires **3.06 m/s** and is unreachable for a walking gait.* ⛔ **That
linearity is this study's own untested premise, so the closure rests on the assumption the study
exists to test. A ROUTE CLOSED BY AN ASSUMPTION IS NOT CLOSED.** *If dose grows superlinearly with
speed the required speed is lower and the closure fails; §4 measures this directly.*

⚠ **Also corrected from the earlier draft: "KV 0.150 is exactly 3.0000× KV 0.050" is an IDENTITY, not
a finding.** *Dose is linear in KV by definition and the clamp does not bind, so 3× KV must give 3×
dose. Nothing was learned from it, and as printed 13.627 × 3 = 40.881, not 40.880.*

⭐ **What step 1 DOES establish, and it is enough to justify this study: the clamp never binds (tested
to k = 20), so nothing saturates anywhere in the reachable range.** *Under the linearity assumption the
provocation spans 10.67–17.34 N across 0.80–1.30 m/s, a 1.62× range, while the weak arm's parameter is
speed-invariant.*

⚠ **"Reachable band" is a statement about the DOSE ARITHMETIC, not about the model's dynamics. Whether
this model can walk at 0.80 or 1.30 m/s at all is unknown and §3 treats it as an outcome.**

---

## 1. Design

| | |
|---|---|
| **commanded speeds** | **0.80, 1.05, 1.30 m/s** — evenly spaced |
| **arms** | control · spastic **KV 0.050** · weak **`tib_ant_l` ×0.892** |
| **seeds** | 101…106 |
| **cells** | 3 speeds × 3 arms × 6 seeds = **54** |
| **start** | from-healthy warm start, identical for all arms, **no continuation** |

⛔ **Why 1.05 and not the 1.0215 benchmark, stated rather than disguised:** *an earlier draft used
{0.80, 1.02, 1.30}, whose midpoint carries **3.8 %** of the fitted slope — verified — making the
"slope" a two-point difference in all but name. **1.05 is the even-spacing midpoint of the band**, and
it is within 0.03 m/s of the measured benchmark so the from-healthy warm start still applies. **The
point was moved for leverage, not chosen for fidelity.***

⛔ **No new magnitudes. KV stays 0.050, weak stays ×0.892. This design changes the TASK, not the
lesion.** ⛔ **r169's depth confound and r172's path dependence are structurally excluded: every cell
runs from-healthy to the same cap, and no cell continues from another's `.par`.**

---

## 2. ⛔ PRIMARY — fully specified so it can be computed without a further decision

### 2a. The scalar, fixed now, ONE rule for all sixteen channels

⭐ **SCALAR = RANGE OF MOTION (ROM): per gait cycle, max − min of the channel; per cell, the mean of
that over admitted cycles.**

⛔ **One sentence of justification, and it is mechanistic: the injected reflex opposes muscle
LENGTHENING, so its first-order kinematic consequence is a COMPRESSION OF EXCURSION — and ROM is
excursion, while being invariant to the postural offsets both lesions independently produce, which a
mean or a peak would confound with the effect.**

⛔ **NO PER-CHANNEL CHOICES. Sixteen channels, one rule, no exceptions except the one below, which is
forced by the data type and is registered here rather than decided later.**

⚠ **`cycle_time` is ALREADY a per-cycle scalar and has no within-cycle range.** *Its per-cell value is
the MEAN over admitted cycles. This is the only channel not reduced by ROM, and it is named now.*

⚠ **This differs from the parent studies, whose endpoint was the MEAN of an `LmR` channel.** *Stated
because it matters: the parents measured the LEVEL of an asymmetry; this study measures the SLOPE of an
excursion. **The numbers are not comparable to the parents' and no comparison to them is registered.***

### 2b. The primary quantity

⭐ **For each seed and each arm: `slope = d(ROM)/d(ACHIEVED speed)`, ordinary least squares over the
three cells of that seed, for each of the 16 channels.**

⛔ **THE x-AXIS IS ACHIEVED SPEED, NOT COMMANDED SPEED.** *This removes the artifact the first cold read
identified at the arithmetic level: if an arm undershoots its command, its points sit at different x
rather than being compressed against an interval it never traversed.*

### 2c. ⛔ The separation criterion, registered as a number

**Per channel, let `SD_c` be the between-seed standard deviation of the CONTROL arm's slope on that
channel (n = 6).**

⭐ **A lesion arm SEPARATES on a channel iff `|mean_arm(slope) − mean_control(slope)| ≥ 2 × SD_c`.**

⭐ **THE STUDY REPORTS SEPARATION iff at least 3 of the 16 channels clear that bar for the same arm.**

⛔ **This is NOT a significance test and must never be reported as one.** *There is no p-value, no null
distribution and no coverage claim — §2d.* ⚠ **And it is ANTI-CONSERVATIVE, for a reason this project
has already recorded: the 16 channels are mechanically coupled and four of them (`*_LmR`) are
deterministic functions of eight others, so "3 of 16" is not 3 independent successes.** *The count is
registered as a decision rule, not as evidence about chance.*

### 2d. What the within-seed slope buys, and what it does not

⭐ **BUYS: each slope is computed within one seed across three speeds, so a seed's additive basin
offset differences out** — *the `Z → G` path that has dominated every between-arm comparison here.*

⛔ **DOES NOT BUY, and this is registered because an earlier draft overclaimed it:** *the three cells of
a seed are INDEPENDENT optimisations sharing a warm start and a seed index, not a guaranteed common
basin. **If basins re-randomise per cell, the pairing is cosmetic.** Differencing removes additive
offsets only; a basin that scales a channel multiplicatively scales its slope too.* ⛔ **Three points,
six seeds, one model, one controller, one objective. No coverage claim and no patient-level
inference.**

---

## 3. ⛔ GATES — evaluated per CELL, before any endpoint

**Gate G1 — completion.** *`history.txt` ≥ 91 lines AND the tag resolves to exactly one such directory.*

⭐ **Gate G2 — ACHIEVED SPEED TOLERANCE, and it is a GATE, not a diagnostic.** *Achieved speed =
forward pelvis travel ÷ elapsed time over the admitted window, the same measure step 1 used.*

⛔ **A cell whose achieved speed differs from its command by more than ±0.04 m/s is DROPPED and not
analysed.** *Registered as a number before any data exists. **Rationale: a compressed speed interval
reads exactly like reduced speed-sensitivity, which is this study's headline, so an out-of-tolerance
cell can manufacture the result.** ±0.04 bounds worst-case interval compression at 16 % of the 0.50
design span; the control arm's own command-to-achieved error at benchmark is +0.0215, so the tolerance
is achievable and not vacuous.*

⚠ **Gate G3 — gait validity.** *A cell that completes 91 lines with a non-walking or degenerate gait
must not enter the primary. **Registered criterion: at least 4 admitted gait cycles in the window**,
by the same heel-strike detection step 1 used. Fewer than 4 → dropped.*

### 3a. ⛔ Survival, registered at SEED level because the gates are per cell

⭐ **A seed CONTRIBUTES A SLOPE for an arm iff all three of its cells pass G1, G2 and G3.**

⛔ **Seeds and cells that drop are THEMSELVES A REGISTERED RESULT: the per-arm, per-speed count of
dropped cells and the reason for each is reported in full, whatever it shows.** ⚠ **Dropping on
survival is conditioning on a descendant of the lesion — a collider — so the drop counts are reported
as an outcome and the surviving-seed analysis is labelled COMPLETE-CASE, never as the whole picture.**

⛔ **If an arm has fewer than 4 contributing seeds, its slopes are reported and labelled UNDERPOWERED,
and it is not used for the §2c separation decision.**

⛔ **If a seed survives at only TWO speeds, the quantity is a DIFFERENCE, not a slope. It is reported
under the name "difference", the seed's slope entry is left EMPTY, and it is never pooled with slopes
or used for the primary.**

⛔ **If NO arm has 4 contributing seeds, the primary is not computed and the study reports the
viability boundary as its result.**

---

## 4. ⛔ Registered outcome — the assumption, measured in ALL THREE ARMS

⭐ **For every cell in every arm — including control and weak — compute the positive-lengthening
integral `mean(max(0, ce_vel_norm))` for `soleus_l` and `gastroc_l`, and the delivered dose at that
arm's own KV.**

⛔ **Computing the VELOCITY term in all three arms is what makes a deviation attributable.** *Control
has KV = 0, so its dose is identically zero — but its `ce_vel_norm` is not, and it is the reference for
how THIS MODEL goes faster.*

- ⭐ **Velocity term tracks the 13.340 N/(m/s) line in all arms** → *the time-scaling assumption holds,
  speed is a clean dose axis, and §0's conditional closure of the dose-matching route becomes firm.*
- ⛔ **Does not track, and fails in ALL arms** → *a fact about the model's gait strategy — how it
  chooses to go faster — not a spastic-specific effect, and §0's closure is void.*
- ⛔ **Does not track, and fails ONLY in the spastic arm** → *the reflex is altering the gait that
  generates the reflex, which is a mechanism finding in its own right.*

⛔ **The primary is NOT reinterpreted against a measured-dose x-axis. An earlier draft registered that
fallback and it is withdrawn: control's dose is identically 0 and the weak arm's is speed-invariant, so
both slopes are undefined on a dose axis and the between-arm comparison cannot be performed there.**
*Achieved speed remains the x-axis in all branches; the velocity term is reported beside it.*

---

## 5. ⛔ BOTH BRANCHES, EQUAL WEIGHT — no prediction is registered

⭐ **SLOPES SEPARATE** → *velocity dependence, the reflex's defining property, reaches gait kinematics —
and every single-speed feature this project buried was measured at the wrong altitude.*

⛔ **SLOPES DO NOT SEPARATE** → *velocity dependence does not reach the kinematics. **The strongest
remaining idea closes on the mechanism's own terms** — not "we failed to find a feature" but "the
mechanism's signature axis does not carry the signal."*

⚠ **The seat writing this has seen step 1's arithmetic and no cell data. No prediction is registered
and neither branch is preferred.**

---

## 6. Cost — measured, and its extrapolation stated

⛔ **The figure 79.2 s/cell was supplied to this seat and DOES NOT VERIFY.** *Measured from the six
completed control cells at identical depth and warm start (`history.txt` mtime − directory creation):
211.7, 213.7, 214.2, 213.4, 185.8, 185.2 s → **mean 204.0 s/cell**, 2.58× the relayed figure.*

| | |
|---|---|
| 54 × 204.0 s | **11,016 s** serial |
| **concurrency 2** | ⭐ **5,508 s = 91.8 min ≈ 1.53 h** |

⚠ **Two caveats, stated rather than netted against each other:** *(i) the six measured cells are
CONTROL arm at the benchmark speed only, so applying 204.0 s to spastic and weak cells at 0.80 and
1.30 m/s is an extrapolation; (ii) if those cells ran under contention the per-cell figure is inflated
— **in which case the ÷2 for concurrency 2 is not also available, and an earlier draft claimed both.***
⛔ **No per-cell timeout is registered; a non-converging cell has unbounded cost and must be killed by
hand if one appears.**

⛔ **Concurrency 2. The 112 protected directories under `C:\Users\maurice\Documents\SCONE\results\`
yield nothing; our cells yield on any conflict. Progress is counted from `history.txt` line counts and
directory mtimes ONLY — `LAUNCH_STATUS.json` is never read.**

---

## 7. Scope

⛔ **No sit-to-stand. No terrain inclines (the word "slope" in this document means `d(ROM)/d(speed)`
throughout and never a surface gradient). No mirrored-lesion arm. No new KV, no new weak scale, no new
channel set, no continuation from any existing `.par`. No document repair while this runs. Writes
confined to `C:\Users\maurice\Desktop\spasticity_paper\` and the 54 new result directories. The frozen
manuscripts are not opened.**
