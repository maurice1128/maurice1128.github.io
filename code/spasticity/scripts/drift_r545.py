# -*- coding: utf-8 -*-
"""r545: how far does the tone score move under measurement noise, and is it the same for both arms?

Section 3.5 offers an absolute tone score, T = control mean minus the patient's reading, with a
threshold. An adversarial review pointed out that the readout is a MAXIMUM, that a maximum rectifies
noise upward rather than averaging it away, and that the upward bias is not the same in the two arms
because their peaks differ in curvature: a flatter peak recruits more samples into the maximum and
therefore rectifies harder. If that is right, an absolute score cannot be calibrated, however well
the ordering holds.

This measures three things directly: the curvature and sample count near each arm's swing peak, the
rectification bias per arm at each noise level, and what the bias does to T and to the gaps between
adjacent rungs of the ladder that section 3.5 reports.
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEED, N_REP, FS = 20260831, 250, 100
SIGMAS = [0.0, 1.0, 2.0, 3.0]
CTRL = ["R151C"]
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


def load(fam, sd):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    if float(t[-1]) < T1 or len(w) < 5:
        return None
    on = grf > thr
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    seg = []
    for a, b in w:
        i = np.where(~on[a:b])[0]
        if i.size:
            y = an[a:b][i]
            g2 = np.linspace(0, 1, max(10, int(round((t[b] - t[a]) * FS * len(i) / (b - a)))))
            seg.append(np.interp(g2, np.linspace(0, 1, len(y)), y))
    return seg or None


print("loading ...")
D = {}
for f in CTRL + [x[0] for x in HY] + WK:
    v = [x for x in (load(f, s) for s in range(101, 107)) if x]
    D[f] = v
    print("   %-12s n=%d" % (f, len(v)))
ARMS = {"control": CTRL, "hyperreflexia": [x[0] for x in HY], "weakness": WK}

# ---- geometry of each arm's swing peak -----------------------------------------------------------
print("\n%-16s %10s %14s %16s" % ("arm", "samples", "within 0.5 deg", "curvature/samp2"))
geom = {}
for nm, fams in ARMS.items():
    ns, near, curv = [], [], []
    for f in fams:
        for cell in D[f]:
            for y in cell:
                ns.append(len(y))
                m = float(np.max(y))
                near.append(int(np.sum(y > m - 0.5)))
                i = int(np.argmax(y))
                if 1 <= i < len(y) - 1:
                    curv.append(abs(float(y[i - 1] - 2 * y[i] + y[i + 1])))
    geom[nm] = {"samples": float(np.mean(ns)), "within_half_deg": float(np.mean(near)),
                "curvature": float(np.mean(curv))}
    print("%-16s %10.1f %14.1f %16.3f"
          % (nm, geom[nm]["samples"], geom[nm]["within_half_deg"], geom[nm]["curvature"]))

# ---- the rectification bias, measured ------------------------------------------------------------
rng = np.random.default_rng(SEED)
clean, bias = {}, {}
for nm, fams in ARMS.items():
    cl = [float(np.mean([np.max(y) for y in cell])) for f in fams for cell in D[f]]
    clean[nm] = float(np.mean(cl))
    bias[nm] = {}
    for sg in SIGMAS:
        if sg == 0:
            bias[nm]["0.0"] = 0.0
            continue
        vals = []
        for _ in range(N_REP):
            v = [float(np.mean([np.max(y + rng.normal(0, sg, y.shape)) for y in cell]))
                 for f in fams for cell in D[f]]
            vals.append(float(np.mean(v)))
        bias[nm][str(sg)] = float(np.mean(vals)) - clean[nm]

print("\n%-8s %12s %14s %12s %14s" % ("sigma", "bias control", "bias hyper", "bias weak", "arm gap W-H"))
gaps = {}
for sg in SIGMAS:
    k = str(sg)
    g = (clean["weakness"] + bias["weakness"][k]) - (clean["hyperreflexia"] + bias["hyperreflexia"][k])
    gaps[k] = g
    print("%-8.1f %12.3f %14.3f %12.3f %14.3f"
          % (sg, bias["control"][k], bias["hyperreflexia"][k], bias["weakness"][k], g))
print("   gap at 3 deg is %.1f per cent of its clean value"
      % (100 * gaps["3.0"] / gaps["0.0"]))

# ---- what that does to the tone score and to the ladder -------------------------------------------
print("\ntone score T = control mean - reading, per dose, at each noise level:")
rung = {}
for f, dose in HY:
    rung[dose] = {}
    for sg in SIGMAS:
        k = str(sg)
        c0 = clean["control"] + bias["control"][k]
        if sg == 0:
            v = float(np.mean([np.mean([np.max(y) for y in cell]) for cell in D[f]]))
        else:
            v = float(np.mean([np.mean([np.mean([np.max(y + rng.normal(0, sg, y.shape))
                                                 for y in cell]) for cell in D[f]])
                               for _ in range(N_REP // 5)]))
        rung[dose][k] = c0 - v
print("   %-10s %s" % ("gain", "  ".join("%8s" % ("sigma " + str(s)) for s in SIGMAS)))
for dose in sorted(rung):
    print("   KV %.3f  %s" % (dose, "  ".join("%8.3f" % rung[dose][str(s)] for s in SIGMAS)))
drift = max(abs(rung[d]["3.0"] - rung[d]["0.0"]) for d in rung)
adj = [abs(rung[sorted(rung)[i + 1]]["0.0"] - rung[sorted(rung)[i]]["0.0"])
       for i in range(len(rung) - 1)]
print("\n   largest drift in T between sigma 0 and 3: %.3f deg" % drift)
print("   adjacent-rung gaps on the clean ladder: %s" % " ".join("%.3f" % a for a in adj))
print("   rungs the drift exceeds: %d of %d" % (sum(1 for a in adj if a < drift), len(adj)))

io.open(os.path.join(P, "DRIFT_r545.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "DRIFT_r545",
 "why": ("Section 3.5 offers an absolute tone score. The readout is a maximum, which rectifies noise "
         "upward, and the two arms' peaks differ in curvature, so the bias is not common to them. "
         "This measures the bias and what it does to the score."),
 "peak_geometry": geom, "clean_means": clean, "bias_by_sigma": bias,
 "arm_gap_by_sigma": gaps,
 "tone_score_by_dose_and_sigma": {str(k): v for k, v in rung.items()},
 "largest_drift_deg": drift, "adjacent_rung_gaps_deg": adj,
 "n_rep": N_REP, "rng_seed": SEED,
}, indent=1, ensure_ascii=False))
print("\n-> DRIFT_r545.json")
