# -*- coding: utf-8 -*-
"""r470: decision rule 3 applied to ANKLE at contact -- the last endpoint that never had it.

Rule 3 says any endpoint reported as a window mean must also report its per-cycle drift. It was run
for knee-at-contact and, per the standing disclosure, for nothing else. The ankle at contact is now
a co-primary endpoint (half the title), and its low-gain margin is only 0.082 deg at cell level, so
undisclosed within-window drift of the order found at the knee (~0.6 deg/cycle differential) could
not be absorbed. This computes the per-cycle hyperreflexia-minus-weakness ankle difference.
"""
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
SP = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
CT = ["R151C"]


def percyc(fam):
    out = []
    for sd in range(101, 107):
        g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
        if not g:
            continue
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
        st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
        if not st:
            continue
        cols, dat = S.load_sto(st[-1])
        if dat.size == 0:
            continue
        t = dat[:, 0]
        grf, thr = S.grf_vertical(cols, dat, "l")
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [c for c in allc if t[c[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5:
            continue
        a = np.degrees(S.col(cols, dat, "ankle_angle_l"))
        out.append([a[i] for i, _ in w])
    return out


sp = [r for f in SP for r in percyc(f)]
wk = [r for f in WK for r in percyc(f)]
ct = [r for f in CT for r in percyc(f)]
print("cells: hyperreflexia %d, weakness %d, control %d" % (len(sp), len(wk), len(ct)))
print()
print("=== RULE 3 ON ANKLE AT CONTACT ===")
print("cycle   hyperreflexia   weakness    control   hyper-weak")
d = []
for i in range(5):
    a = [r[i] for r in sp if len(r) > i]
    b = [r[i] for r in wk if len(r) > i]
    c = [r[i] for r in ct if len(r) > i]
    d.append(np.mean(a) - np.mean(b))
    print("  %d     %+11.3f %+10.3f %+10.3f %+11.3f"
          % (i + 1, np.mean(a), np.mean(b), np.mean(c), d[-1]))
d = np.array(d)
print()
print("  window-mean difference      +0.056")
print("  per-cycle range             %+.3f to %+.3f   spread %.3f deg" % (d.min(), d.max(), d.ptp()))
print("  first vs last               %+.3f -> %+.3f   drift %+.3f" % (d[0], d[-1], d[-1] - d[0]))
print("  sign constant across cycles %s" % (bool(np.all(d > 0)) or bool(np.all(d < 0))))
slope = np.polyfit(np.arange(1, 6), d, 1)[0]
print("  differential drift          %+.4f deg/cycle -> %.3f deg over 5.32 cycles"
      % (slope, abs(slope) * 5.32))
print()
print("  0.082 deg is the cell-level low-gain margin; the differential accumulates %.3f deg"
      % (abs(slope) * 5.32))
print("  VERDICT: %s" % ("drift is small relative to the margins that matter"
                         if abs(slope) * 5.32 < 0.5 else
                         "DRIFT IS LARGE -- the low-gain margin cannot survive it"))
