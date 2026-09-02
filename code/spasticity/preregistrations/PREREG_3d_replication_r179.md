# PREREG_3d_replication_r179.md — the chance objection to PRIMARY B, and what answers it

**Round 179.** ⛔ **A NEW REGISTRATION, NOT AN EDIT.** *`PREREG_3d_specificity_r178.md` is hashed
(`c863442647576b48…`) and stays byte-identical. This adds a decision rule it does not contain — that
rule changes what kills the claim, so it cannot be an amendment to a frozen file.*

**Parent:** `PREREG_3d_specificity_r178.md`. **Evaluation of existing cells. No new simulation.**

---

## 1. ⛔ The objection, in its strongest form

**Ten channels have BOTH arms displaced from control. If the two arms' displacement directions were
independent, ~5 would be opposed. ONE is.**

| | |
|---|---|
| both arms displaced | **10 of 16** |
| **OPPOSED** | ⛔ **1** — `hip_flexion_LmR` |
| PARALLEL | **9** |
| expected opposed under independent signs | **5.0** |
| **P(≤ 1 opposed of 10 \| 50/50)** | ⛔ **0.0107** |

⛔ **THE 50/50 NULL IS WRONG AND ANTI-CONSERVATIVE ON TWO COUNTS, per the cold read.** *(i) Both
lesions impair the SAME limb, so a shared mechanical bias toward one side of every `(L−R)` channel
predicts high parallelism with no coordination at all; (ii) the channels are mechanically coupled, so
ten sign draws are not ten independent ones — effective n may be 2–3.* ⚠ **The "largely parallel"
conclusion is probably true and is NOT earned by this test.** ⭐ *Note the direction: the weak null
**inflates** the objection this document must answer, so the error runs against the claim rather than
for it.* ⛔ **And the denominator slides: "one opposed channel among sixteen" in the prose versus 1 of
**10** in the table. The table is correct.**

⭐ **THE CORRECT READING OF THE PRIOR IS NOT "the hip is special because only it is opposed."**
*It is: **the two lesions produce largely PARALLEL gait signatures — same direction on nine of ten
channels — which is why discrimination has been hard for this entire project — and there is exactly
one channel where they diverge.***

⛔ **AND THAT MAKES "1 OF 16 IS CHANCE" A LIVE OBJECTION, NOT A RHETORICAL ONE.** *Under a model where
opposition is rare — base rate ~1 in 10 — observing exactly one opposed channel among sixteen is
**precisely what that model predicts.*** ⛔ **On r151 data alone, "the hip is a mechanism readout" and
"the hip is the one chance exception" are OBSERVATIONALLY IDENTICAL. r151 cannot separate them.**

---

## 2. What answers it, and how much it is actually worth

**The r174 cells offer one thing r151 does not: the opposition can be checked at three weakness
magnitudes — ×0.870, ×0.892, ×0.915 — each independently re-optimised.**

⭐ **The argument: a chance sign agreement is a property of one draw. Re-optimising the weak arm at a
different lesion magnitude is a fresh draw, and a chance sign should not survive three of them.**

⛔ **THE HONEST LIMIT, REGISTERED BEFORE THE DATA AND STATED AS THE WEAKNESS IT IS:**

1. ⛔ **The three comparisons SHARE THE SPASTIC ARM ENTIRELY.** *All three are `S050` versus a weak
   rung — the same six cells, the same controller, on every one. **Only the weak arm varies.**
2. ⛔ **The three weak magnitudes span ±2.3 % of `tib_ant_l` force** and use **the same six seeds**
   warm-started from the same healthy par. *They are adjacent points on one axis, not three samples.*
3. ⛔ **THEREFORE THE THREE RUNGS TEST ROBUSTNESS TO WEAKNESS MAGNITUDE. THEY DO NOT MULTIPLY EVIDENCE
   ABOUT THE SIGN, AND NOTHING BELOW MAY BE REPORTED AS IF THEY DID.** ⚠ *The draft put this at "one and a half" independent draws with no derivation; the cold read called
   that too generous and it is. **Corrected to 1.0–1.2, and it is an assertion with no derivation
   either — the honest statement is that the number is not calculable from anything here and the
   design does not use it.** The honest phrasing of a pass is "the opposition is not an artifact of the
   particular weakness magnitude" — **not** "the opposition replicated three times."*
4. ⛔ **WHAT WOULD ACTUALLY ANSWER THE OBJECTION: new SPASTIC seeds, or a second spastic magnitude.
   Neither exists** — `PREREG_3d_ladder_r169.md` established the spastic axis is one point wide, and
   every attempt at a second magnitude failed Gate G on two independent optimisation paths.
   ⚠ **So the objection cannot be fully answered by any data this project currently has, and this
   registration does not claim otherwise.**

---

## 2a. ⛔⛔ THIS REGISTRATION IS NOT BLIND, AND THE KILL BRANCH IS NEARLY UNREACHABLE

**The cold read found this and it is the most serious item in the document.** *§4 of the draft said
I expect OPPOSED at all three rungs **because `MATCHED_RESULT_r174.md` already reports AUC 0.0000 at
every rung**.* ⛔ **An outcome-adjacent statistic had already been read, at all three rungs, before
the rule was written. The hash-freezing ceremony does not make a post-hoc-informed registration a
blind one.**

⛔ **Consequence, stated plainly: the kill branch is close to unreachable.** *AUC 0.0000 means every
spastic seed lies below every weak seed at all three rungs. For OPPOSED to fail at exactly one or two
rungs, one arm would have to cross the control band without disturbing that ordering — possible, but
the reader is right that the document's own hedge ("unlikely to" come apart) concedes it.*

⭐ **What follows, and it is a real cost accepted rather than a disclaimer:** *a PASS on §3 is
therefore worth **much less** than a pre-registered pass, and the result document must say so in the
same sentence as the pass, not in a footnote.* ⛔ **A FAIL, by contrast, retains full force — it would
be a failure predicted against by the seat that wrote the rule.** *The registration is asymmetric in
evidential weight and that asymmetry is now on the record instead of being smuggled.*

⚠ **What would have been required for a blind version: coding and execution by someone who has not
read `MATCHED_RESULT_r174.md`. That is not available here, and this document does not pretend the
freeze substitutes for it.**

## 3. The registered rule

**`hip_flexion_LmR` is checked for OPPOSED status at each of the three rungs, using
`PREREG_3d_specificity_r178.md` §2's unchanged definition** *(both arms outside the control band, on
opposite sides of the control mean)*, **at band multiplier ×1.0 as the PRIMARY; ×1.5 and ×2.0 are reported as sensitivity only.**

⛔ **THE MULTIPLIERS ARE NESTED AND THE DRAFT CALLED THEM A STABILITY CHECK.** *Widening a band can
only REMOVE a channel from "displaced", never add one, so OPPOSED at ×2.0 implies OPPOSED at ×1.0.
**"Row differs across multipliers" is not instability — it is a readout of effect size relative to band
width, renamed.*** ⛔ **And because UNSTABLE was an absorbing non-result, it could only ever SPARE the
claim and never retire it — a one-way escape hatch, which is SO-12's pattern for the third time and
the second time inside a registration written after SO-12.** ⭐ **Removed: UNSTABLE no longer exists as
a branch. ×1.0 decides; the other two describe.**

| outcome | registered reading |
|---|---|
| **OPPOSED at all 3 rungs** | ⭐ **the opposition is not an artifact of the particular weakness magnitude.** ⛔ *The chance objection is WEAKENED, not eliminated — §2.3. The claim stands in the form: one channel diverges where nine run parallel, robustly across weakness magnitude, on a shared spastic arm.* |
| ⛔ **OPPOSED at 1 or 2 rungs, FAILING because an arm sits INSIDE the band** | ⚠ **NOT a sign failure — a magnitude failure.** *Reported as: the opposition is present in direction but too small to clear the band at that rung. The claim is **weakened, not retired**.* |
| ⛔ **OPPOSED at 1 or 2 rungs, FAILING because both arms are displaced on the SAME side** | ⛔ **THE CLAIM DIES.** *That is sign inconstancy across adjacent weakness magnitudes — the chance exception the objection describes — and the hip result is retired in `MATCHED_RESULT_r174.md` §1's first paragraph.* |
| ⛔ **OPPOSED at 0 rungs** | ⛔ **the claim dies, and `PREREG_3d_specificity_r178.md` §3's "B = 0 → RETIRED" fires as well.** |

⭐ **ALSO REGISTERED, because a binary cannot see a decaying effect: the SIGNED MARGIN of each arm
from the control mean, in band units, at every rung.** ⛔ **A pass requires the hip's margin NOT to
decay monotonically toward the band edge across ×0.870 → ×0.915. A monotone decay with 3/3 OPPOSED is
reported as a dose-dependent opposition and the claim is weakened.**

⛔ **The parallel/opposed counts (9 and 1 on r151) are reported for the r174 cells too, at every rung.
If the parallel fraction at the matched rung falls below 0.70 — threshold fixed here, replacing the
draft's undefined "sharply" — the "largely parallel signatures" framing
in §1 is itself dose-dependent and must be reported as such.**

---

## 4. What this cannot do

- ⛔ **It cannot make the r151 prior discriminating.** *§1: on that data the two explanations are
  observationally identical, and no analysis here changes that.*
- ⛔ **It cannot supply the independence the objection needs.** *§2.4.*
- ⚠ **It adds no NEW comparison against control** — *OPPOSED is defined against the control band, so
  the draft's "adds no test against control" contradicted §3. **The band comparison is a count of six
  restarts against six restarts and is not a test**, which is the accurate statement.*
- ⛔ **It inherits every limit of r178 and of the cells** — *restarts not subjects, 20.00 s censoring,
  the untested window, muscle-force dose not ankle moment, blindness to timing.*

⚠ **Expectation, before the data: I expect OPPOSED at all three rungs, because `MATCHED_RESULT_r174.md`
already reports AUC 0.0000 on `hip_flexion_LmR` at every rung. That is a weak prediction and I am
labelling it weak** — *AUC 0.0000 is a between-arm rank statement and OPPOSED is a statement about both
arms versus control, so the two can come apart, but they are unlikely to.*
