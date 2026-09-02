# -*- coding: utf-8 -*-
"""r529: the specificity of peak swing dorsiflexion, computed without the additive assumption.

r526 fitted the mixed grid with an additive model and returned a weakness coefficient
indistinguishable from zero, which reads as 'this endpoint is immune to weakness'. Inspection of the
cell means shows that is wrong: the weakness effect CHANGES SIGN across the gain range, from -1.20
degrees at the lowest gain to +1.45 at KV 0.100, and an additive model averages a sign-flipping
effect to nothing. The near-zero coefficient is an artefact of the model, not a property of the
endpoint.

This recomputes the specificity three ways that do not assume additivity:
  (a) the largest weakness excursion at any single gain, against the smallest step between gains,
  (b) an interaction model, and
  (c) whether the ordering by gain is preserved at every weakness level, which is what an
      apportionment actually needs.
"""
import io, json, os
import numpy as np

P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
G = json.load(io.open(os.path.join(P, "MIXEDSWING_r526.json"), encoding="utf-8"))
SD = {"swing_df": 0.089, "knee_ic": 0.556}          # seed SD on the mixed grid, from r526

grid = {}
for k, v in G["cell_means_swing_df_deg"].items():
    if v is None:
        continue
    w, kv = k.split("_KV")
    grid[(float(w[1:]), float(kv))] = v

WK = sorted(set(w for w, _ in grid))
KV = sorted(set(g for _, g in grid))
print("peak swing dorsiflexion cell means:")
print("   %-8s" % "" + "".join("  KV %.3f" % g for g in KV))
for w in WK:
    print("   x%.2f   " % w + "".join("  %7.3f" % grid[(w, g)] if (w, g) in grid else "        -"
                                      for g in KV))

# ---- (a) weakness excursion at fixed gain, vs the step between gains --------------------------
print("\n(a) weakness excursion within each gain column, and the step to the next gain:")
exc = {}
for g in KV:
    v = [grid[(w, g)] for w in WK if (w, g) in grid]
    exc[g] = max(v) - min(v)
steps = [(KV[i], KV[i + 1], abs(np.mean([grid[(w, KV[i])] for w in WK if (w, KV[i]) in grid])
                               - np.mean([grid[(w, KV[i + 1])] for w in WK if (w, KV[i + 1]) in grid])))
         for i in range(len(KV) - 1)]
for g in KV:
    print("   KV %.3f  weakness excursion %.3f deg" % (g, exc[g]))
for a, b, d in steps:
    print("   KV %.3f -> %.3f  step %.3f deg" % (a, b, d))
worst = max(exc.values())
smallest = min(d for _, _, d in steps)
print("   WORST CASE: largest weakness excursion %.3f vs smallest gain step %.3f -> specificity %.2f:1"
      % (worst, smallest, smallest / worst))

# ---- (b) interaction model ----------------------------------------------------------------------
A, b = [], []
for (w, g), y in grid.items():
    A.append([1.0, g, w, g * w])
    b.append(y)
A, b = np.array(A), np.array(b)
coef, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
pred = A.dot(coef)
r2 = 1.0 - float(np.sum((b - pred) ** 2)) / float(np.sum((b - np.mean(b)) ** 2))
dof = len(b) - 4
s2 = float(np.sum((b - pred) ** 2)) / dof
se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T.dot(A))))
print("\n(b) with an interaction term:")
for n, c, e in zip(["intercept", "gain", "weakness", "gain x weakness"], coef, se):
    print("   %-16s %+9.3f  (SE %.3f, t %+.2f)" % (n, c, e, c / e if e else float("nan")))
print("   R2 %.4f" % r2)
# the weakness slope evaluated at each gain, which the additive model hides
print("   weakness slope at each gain (deg per unit scaling):")
wslope = {}
for g in KV:
    wslope[g] = coef[2] + coef[3] * g
    print("     KV %.3f  %+8.3f" % (g, wslope[g]))
print("   the slope changes sign: %s" % (min(wslope.values()) < 0 < max(wslope.values())))

# ---- (c) is the ordering by gain preserved at every weakness level? -----------------------------
print("\n(c) ordering by gain, checked separately at each weakness level:")
allmono = True
for w in WK:
    v = [grid[(w, g)] for g in KV if (w, g) in grid]
    mono = all(v[i] > v[i + 1] for i in range(len(v) - 1))
    allmono = allmono and mono
    print("   x%.2f  %s  %s" % (w, "  ".join("%7.3f" % x for x in v),
                                "monotone" if mono else "NOT MONOTONE"))
# and the practical question: can a reading be inverted by weakness?
inv = []
for i in range(len(KV) - 1):
    for w1 in WK:
        for w2 in WK:
            a, bb = (w1, KV[i]), (w2, KV[i + 1])
            if a in grid and bb in grid and grid[a] <= grid[bb]:
                inv.append({"lower_gain_cell": "x%.2f KV%.3f" % a, "value": grid[a],
                            "higher_gain_cell": "x%.2f KV%.3f" % bb, "value2": grid[bb]})
print("   adjacent-gain inversions caused by weakness: %d" % len(inv))
for x in inv:
    print("     %s (%.3f) does NOT read above %s (%.3f)"
          % (x["lower_gain_cell"], x["value"], x["higher_gain_cell"], x["value2"]))

dep = {
 "id": "SWINGSPEC_r529",
 "why": ("r526's additive model returned a weakness coefficient near zero, which reads as immunity. "
         "The weakness effect changes sign across the gain range, so an additive model averages it "
         "to nothing. The near-zero coefficient is an artefact of the model. This recomputes the "
         "specificity without assuming additivity."),
 "CORRECTION": ("the 32.5:1 specificity ratio in MIXEDSWING_r526 must not be quoted. It divides the "
                "gain span by an additive weakness span that is near zero only because the effect "
                "reverses sign. The defensible figure is the worst-case ratio in (a)."),
 "weakness_excursion_by_gain_deg": {str(k): v for k, v in exc.items()},
 "gain_steps_deg": [{"from": a, "to": b, "step_deg": d} for a, b, d in steps],
 "worst_case_specificity": {"largest_weakness_excursion_deg": worst,
                            "smallest_gain_step_deg": smallest,
                            "ratio": smallest / worst},
 "interaction_model": {"coefficients": {"intercept": coef[0], "gain": coef[1], "weakness": coef[2],
                                        "gain_x_weakness": coef[3]},
                       "SE": {"intercept": se[0], "gain": se[1], "weakness": se[2],
                              "gain_x_weakness": se[3]},
                       "R2": r2,
                       "weakness_slope_by_gain": {str(k): v for k, v in wslope.items()},
                       "slope_changes_sign": bool(min(wslope.values()) < 0 < max(wslope.values()))},
 "ordering": {"monotone_in_gain_at_every_weakness_level": bool(allmono),
              "adjacent_gain_inversions_caused_by_weakness": len(inv), "inversions": inv},
}
io.open(os.path.join(P, "SWINGSPEC_r529.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWINGSPEC_r529.json")
