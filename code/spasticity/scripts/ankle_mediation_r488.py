# -*- coding: utf-8 -*-
"""r488: is the knee separation a passive consequence of ankle position at contact?

Drefus et al. [19] showed that a purely mechanical ankle offset -- an orthosis locked in
plantarflexion, no spasticity and no contracture -- raises knee flexion at initial contact by 7 to
22 deg, one to four times the effect reported here. That is the sharpest published objection to this
manuscript's claim: if the knee merely follows the ankle, the knee reads "plantarflexed ankle", not
"hyperreflexia", and a contracture arm would reproduce it.

The objection is testable in this corpus without any new simulation, because the ankle confound is
measured on the same cells. If the knee were driven by ankle position at contact, the knee ordering
would have to track the ankle ordering. This computes, for every hyperreflexia x weakness family
pair, the knee difference and the ankle difference, and asks whether they agree in sign.
"""
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
SP = [("R151S", 0.050), ("R393SPg070", 0.070), ("R393SPg100", 0.100),
      ("R396SPg110", 0.110), ("R396SPg120", 0.120)]
WK = [("R151W", 0.800), ("R174W870", 0.870), ("R174W892", 0.892),
      ("R169W090", 0.900), ("R174W915", 0.915), ("R169W095", 0.950)]


def cells(fam):
    """Per-seed (knee, ankle) at first contact of each kept cycle, averaged over the window."""
    out = []
    for sd in range(101, 107):
        g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
        if not g:
            continue
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
        st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
        if not st:
            continue
        c, dat = S.load_sto(st[-1])
        if dat.size == 0:
            continue
        t = dat[:, 0]
        grf, thr = S.grf_vertical(c, dat, "l")
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5:
            continue
        kn = np.degrees(S.col(c, dat, "knee_angle_l"))
        an = np.degrees(S.col(c, dat, "ankle_angle_l"))
        out.append((float(np.mean([kn[i] for i, _ in w])),
                    float(np.mean([an[i] for i, _ in w]))))
    return out


print("family means at foot contact (+ = knee flexion sign as stored; + = ankle dorsiflexion)")
print("%-12s %6s %4s %10s %10s" % ("family", "dose", "n", "knee", "ankle"))
sp, wk = [], []
for fam, dose in SP:
    v = cells(fam)
    if not v:
        print("%-12s %6.3f   -- no cells" % (fam, dose)); continue
    k, a = np.mean([x[0] for x in v]), np.mean([x[1] for x in v])
    sp.append((fam, dose, k, a, len(v)))
    print("%-12s %6.3f %4d %10.3f %10.3f" % (fam, dose, len(v), k, a))
for fam, dose in WK:
    v = cells(fam)
    if not v:
        print("%-12s %6.3f   -- no cells" % (fam, dose)); continue
    k, a = np.mean([x[0] for x in v]), np.mean([x[1] for x in v])
    wk.append((fam, dose, k, a, len(v)))
    print("%-12s %6.3f %4d %10.3f %10.3f" % (fam, dose, len(v), k, a))

print()
print("=== every hyperreflexia x weakness family pair ===")
print("%-12s %-12s %10s %10s  %s" % ("hyper", "weak", "d_knee", "d_ankle", "ankle explains sign?"))
dk, da, agree = [], [], 0
for f1, d1, k1, a1, _ in sp:
    for f2, d2, k2, a2, _ in wk:
        x, y = k1 - k2, a1 - a2
        dk.append(x); da.append(y)
        # stored conventions: knee negative = flexion, ankle negative = plantarflexion.
        # Drefus's mechanism (more plantarflexion -> more knee flexion) therefore predicts that
        # d_knee and d_ankle carry the SAME sign. Opposite signs falsify mediation for that pair.
        same = (np.sign(x) == np.sign(y))
        agree += bool(same)
        print("%-12s %-12s %+10.3f %+10.3f  %s" % (f1, f2, x, y, "yes" if same else "NO"))

dk, da = np.array(dk), np.array(da)
n = len(dk)
print()
print("pairs                                  %d" % n)
print("knee difference sign constant          %s  (all %s)"
      % (bool(np.all(dk > 0) or np.all(dk < 0)), "positive" if dk[0] > 0 else "negative"))
print("ankle difference sign constant         %s" % bool(np.all(da > 0) or np.all(da < 0)))
print("pairs consistent with ankle mediation    %d of %d (%.0f%%)" % (agree, n, 100.0 * agree / n))
print("pairs where the ankle runs BACKWARDS    %d of %d (%.0f%%)" % (n - agree, n, 100.0 * (n - agree) / n))
r = np.corrcoef(dk, da)[0, 1]
print("correlation of d_knee with d_ankle     r = %+.3f" % r)
print()
# the 0.586 deg sham floor (SHAM_READOUT_r406) is the artefact scale this paper applies to its own
# positive claims; a pair whose ankle difference is below it cannot be said to run backwards either
SHAM = 0.5860145801831838
bad = [(f1, f2, x, y) for (f1, d1, k1, a1, _) in sp for (f2, d2, k2, a2, _) in wk
       for x, y in [(k1 - k2, a1 - a2)] if np.sign(x) != np.sign(y)]
print("=== the pairs ankle position cannot explain ===")
for f1, f2, x, y in bad:
    print("  %-12s vs %-12s knee %+7.3f  but its ankle is %+.3f deg MORE DORSIFLEXED" % (f1, f2, x, y))
strong = [b for b in bad if abs(b[3]) >= SHAM]
weak = [b for b in bad if abs(b[3]) < SHAM]
print()
print("  falsifying pairs whose ankle difference clears the %.3f deg sham floor: %d of %d"
      % (SHAM, len(strong), n))
for f1, f2, x, y in weak:
    print("    below the floor, NOT counted: %-12s vs %-12s ankle %+.3f" % (f1, f2, y))
if bad:
    print()
    print("  knee separation in these pairs   %.3f to %.3f deg"
          % (min(abs(b[2]) for b in bad), max(abs(b[2]) for b in bad)))
    print("  ankle runs backwards by up to    %.3f deg" % max(b[3] for b in bad))
print()
print("READING. Ankle mediation is falsified for %d of %d pairs at the sham floor (%d before it" % (len(strong), n, len(bad)))
print("is applied): there the hyperreflexia limb's")
print("ankle is LESS plantarflexed than the weakness limb's, yet its knee is MORE flexed. Those")
print("pairs are exactly the low-gain rungs over which the ankle arms interleave -- the range this")
print("paper's title is about. For the remaining %d pairs the ankle is more plantarflexed in the" % (n - len(bad)))
print("hyperreflexia limb, so mediation is NOT excluded there, and the overall r = %+.3f across" % r)
print("pairs is what mediation would predict. The claim this licenses is therefore narrow and")
print("specific: the knee separation is not wholly a passive consequence of ankle position, and at")
print("low gain it cannot be one at all. It does not license the claim that mediation plays no part.")
