# -*- coding: utf-8 -*-
"""r533: can TWO angles from one recording recover BOTH lesion magnitudes, when neither can alone?

Neither single readout apportions. Knee at contact responds to both lesions but confounds them: the
mixed-grid regression (MIXEDSWING_r526) gives it a weakness coefficient of -2.729 against a gain
coefficient of -41.603, so one knee angle is consistent with many (gain, weakness) pairs, which is
registered prediction P4 and it held. Peak swing dorsiflexion responds strongly to gain and barely
to weakness (SWINGDF_r525: weakness sits 0.43 deg from control), so it grades tone and is silent
about the other lesion.

Their failures are complementary. If the ankle pins the gain down, the knee's departure from what
that gain alone would produce is the weakness. That is a decomposition, and it needs no strength
test -- both numbers come from one gait recording.

The mixed grid is the place to test it, because both lesion magnitudes are known exactly there.
Everything is scored leave-one-out, and additionally leave-one-WEAKNESS-LEVEL-out, because a model
fitted and tested on the same four weakness levels would flatter itself.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
WEAK = {"060": 0.60, "070": 0.70, "080": 0.80, "100": 1.00}
GAIN = {"0125": 0.0125, "0250": 0.0250, "0500": 0.0500, "1100": 0.1100}


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
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    on = grf > thr
    pk = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
    if not pk:
        return None
    return {"knee_ic": float(np.mean([kn[a] for a, _ in w])), "swing_df": float(np.mean(pk))}


rows = []
for wk, wv in WEAK.items():
    for gk, gv in GAIN.items():
        for sd in range(101, 107):
            r = load("R424W%s%s" % (wk, gk), sd)
            if r:
                r.update({"weak": wv, "kv": 2.0 * gv, "seed": sd})
                rows.append(r)
print("mixed-grid cells: %d" % len(rows))

Y = {"kv": np.array([r["kv"] for r in rows]), "weak": np.array([r["weak"] for r in rows])}
FEAT = {
    "knee at contact alone": lambda r: [1.0, r["knee_ic"]],
    "peak swing dorsiflexion alone": lambda r: [1.0, r["swing_df"]],
    "both angles": lambda r: [1.0, r["knee_ic"], r["swing_df"]],
    "both angles + their product": lambda r: [1.0, r["knee_ic"], r["swing_df"],
                                              r["knee_ic"] * r["swing_df"]],
}


def loo(feat, target, groups=None):
    """leave-one-out (or leave-one-group-out) prediction of `target`"""
    A = np.array([feat(r) for r in rows])
    b = Y[target]
    pred = np.empty_like(b)
    keys = groups if groups is not None else np.arange(len(rows))
    for k in np.unique(keys):
        te = keys == k
        tr = ~te
        if tr.sum() < A.shape[1] + 1:
            pred[te] = np.nan
            continue
        coef, _, _, _ = np.linalg.lstsq(A[tr], b[tr], rcond=None)
        pred[te] = A[te].dot(coef)
    m = ~np.isnan(pred)
    ss = float(np.sum((b[m] - pred[m]) ** 2))
    tot = float(np.sum((b[m] - np.mean(b[m])) ** 2))
    return {"R2": 1.0 - ss / tot if tot else float("nan"),
            "RMSE": float(np.sqrt(ss / m.sum())),
            "n": int(m.sum())}


wgroups = np.array([r["weak"] for r in rows])
ggroups = np.array([r["kv"] for r in rows])

print("\nRecovering the REFLEX GAIN (true range %.3f to %.3f):"
      % (Y["kv"].min(), Y["kv"].max()))
print("   %-32s %-22s %s" % ("readout", "leave-one-cell-out", "leave-one-gain-level-out"))
res = {}
for n, f in FEAT.items():
    a, b = loo(f, "kv"), loo(f, "kv", ggroups)
    res.setdefault(n, {})["kv"] = {"loo": a, "logo": b}
    print("   %-32s R2 %6.3f RMSE %.4f   R2 %6.3f RMSE %.4f"
          % (n, a["R2"], a["RMSE"], b["R2"], b["RMSE"]))

print("\nRecovering the WEAKNESS SCALING (true range %.2f to %.2f) -- this is the one that matters, "
      "because no single angle has managed it:" % (Y["weak"].min(), Y["weak"].max()))
print("   %-32s %-22s %s" % ("readout", "leave-one-cell-out", "leave-one-weakness-level-out"))
for n, f in FEAT.items():
    a, b = loo(f, "weak"), loo(f, "weak", wgroups)
    res.setdefault(n, {})["weak"] = {"loo": a, "logo": b}
    print("   %-32s R2 %6.3f RMSE %.4f   R2 %6.3f RMSE %.4f"
          % (n, a["R2"], a["RMSE"], b["R2"], b["RMSE"]))

# --- what the pair buys, stated as the residual decomposition -----------------------------------
A1 = np.array([[1.0, r["swing_df"]] for r in rows])
c1, _, _, _ = np.linalg.lstsq(A1, Y["kv"], rcond=None)
kv_hat = A1.dot(c1)
A2 = np.array([[1.0, k] for k in kv_hat])
c2, _, _, _ = np.linalg.lstsq(A2, np.array([r["knee_ic"] for r in rows]), rcond=None)
resid = np.array([r["knee_ic"] for r in rows]) - A2.dot(c2)
rr = float(np.corrcoef(resid, Y["weak"])[0, 1])
print("\nthe decomposition, stated directly:")
print("   step 1  ankle swing peak -> reflex gain            R2 %.3f" % (1 - np.sum((Y["kv"] - kv_hat) ** 2) / np.sum((Y["kv"] - Y["kv"].mean()) ** 2)))
print("   step 2  knee at contact, minus what that gain predicts, correlates with weakness r = %+.3f "
      "(R2 %.3f)" % (rr, rr * rr))

# --- and the honest limit: is the weakness recovery better than chance in DEGREES? --------------
best = max(FEAT, key=lambda n: res[n]["weak"]["logo"]["R2"])
print("\nbest weakness recovery: %s, leave-one-weakness-level-out R2 %.3f, RMSE %.4f in scaling "
      "units (the true levels are %.2f apart at the closest)"
      % (best, res[best]["weak"]["logo"]["R2"], res[best]["weak"]["logo"]["RMSE"], 0.10))

dep = {
 "id": "PAIR_r533",
 "why": ("Neither single angle apportions: the knee confounds the two lesions, the ankle swing peak "
         "is silent about weakness. Their failures are complementary, so this asks whether the pair "
         "recovers both lesion magnitudes on the grid where both are known."),
 "n_cells": len(rows),
 "grid": "R424W<weakness><archived gain>, delivered gain = 2x label",
 "results": res,
 "decomposition": {
    "step1_ankle_to_gain_R2": float(1 - np.sum((Y["kv"] - kv_hat) ** 2)
                                    / np.sum((Y["kv"] - Y["kv"].mean()) ** 2)),
    "step2_knee_residual_vs_weakness_r": rr,
    "step2_R2": rr * rr},
 "CAVEATS": [
    "the grid has four weakness levels and four gains; leave-one-level-out is reported because a "
    "model fitted and tested on the same levels would flatter itself",
    "the weakness scalings run x0.60 to x1.00, a 40 per cent force reduction at the deepest. "
    "Clinical drop foot is more severe than anything in this range",
    "both angles come from the same recording and share its errors, so their measurement errors are "
    "not independent; this analysis uses noise-free simulation values and says nothing about how "
    "the pair behaves under motion-capture error. That is SWINGMOCAP_r531's question"],
}
io.open(os.path.join(P, "PAIR_r533.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> PAIR_r533.json")
