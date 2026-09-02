# PREREG_turn_dose_r262.md — does turning survive the magnitude confound?

**Written BEFORE the dose regression was computed, round 262.**

---

## 1. The claim being tested

`TURN_r260.json` shows the weakness arms' net rotation per cycle appears **flat** — roughly 0.33–0.50
deg/cycle across a **4× dose range** — while the reflex arm is 1.37–1.56, three to seven times any of
them.

⭐ **If turn rate does not scale with weakness dose, then dose is excluded as the explanation of the
reflex arm's turning**, because the magnitude confound's whole force is "the reflex arm is 5–22×
bigger", and a quantity flat across 4× of weakness is not responding to size.

## 2. What is computed

1. **OLS of turn rate on delivered dose within the weakness arms only** (36 cells, 6 rungs × 6 seeds):
   slope, standard error, 95 % CI.
2. **The slope that would be required** to reach the reflex arm's observed rate at the reflex arm's
   dose, and whether the fitted CI excludes it.
3. **Seed-level disjointness** of turn rate, reflex against every weakness arm, both windows.
4. **Sign consistency** of the net rotation across the six seeds in every arm.

## 3. The bound, fixed before the numbers

⚠ **With ONE reflex condition, "reflex-specific" and "specific to this particular large lesion" remain
unseparated.** ⭐ **What weakness flatness can buy is the exclusion of DOSE as the explanation. It
cannot establish TYPE.** ⛔ **The report will say exactly that much and no more, whatever the slope
turns out to be.**

*A second reflex gain would separate them. Gate G admits none: KV 0.150 and 0.400 are 0/6.*

## 4. Readings

- **A — the weakness slope is flat and its CI excludes the required slope.** *Dose is excluded as the
  explanation of the reflex arm's turning. Type is NOT thereby established.*
- **B — the weakness slope is flat but the CI is too wide to exclude the required slope.** *Nothing is
  excluded; report the width and say the test was underpowered.*
- **C — the weakness slope is positive and consistent with reaching the reflex rate.** *Turning is
  dose-driven like everything else in this corpus, and the apparent dissociation dissolves.*
- **D — turn rate is not seed-level disjoint between reflex and weakness on a given window.** *Then
  the arm-level difference is reported with its overlap and is not called a separation on that window.*

## 5. The mechanism, named as a hypothesis and not a result

⚠ **HYPOTHESIS, UNTESTED:** *a unilateral velocity-dependent plantarflexor reflex produces asymmetric
push-off, which produces a yaw moment; a symmetric bilateral loss of dorsiflexor strength does not.*
**It is plausible, it is not tested by anything in this corpus, and it predicts one checkable thing:
that the net rotation is consistently toward the same side across seeds.** *That prediction is checked
here. Confirming it does not confirm the mechanism — many accounts predict a consistent sign — but
falsifying it would rule this one out.*
