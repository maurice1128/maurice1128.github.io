# -*- coding: utf-8 -*-
"""r526: the decisive test. Does peak swing dorsiflexion grade hyperreflexia INDEPENDENTLY of
weakness, on the mixed grid where both lesions are present at once?

Registered prediction P4 was tested on knee-at-contact and held: different combinations of the two
lesions give overlapping knee readings, so one knee angle cannot apportion them. Real patients carry
both lesions, so any readout offered for apportionment must be tested on the grid where both are
present, not only on the single-lesion ladders.

The question here is whether peak swing dorsiflexion is a function of reflex gain alone. If the
weakness coefficient is at the noise floor while the gain coefficient is large, the variable grades
plantarflexor overactivity specifically, and a second reading is free to grade the weakness. If it
is contaminated by weakness depth, it fails the same way the knee does.
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73

# R424W<weakness><archived gain>; delivered gain is twice the archived label (section 2.2)
WEAK = {"060": 0.60, "070": 0.70, "080": 0.80, "100": 1.00}
GAIN = {"0125": 0.0125, "0250": 0.0250, "0500": 0.0500, "1100": 0.1100}


def readouts(fam, sd):
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
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    on = grf > thr
    pk = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
    return ({"swing_df": float(np.mean(pk)) if pk else None,
             "knee_ic": float(np.mean([kn[a] for a, _ in w]))})


rows = []
for wk, wv in WEAK.items():
    for gk, gv in GAIN.items():
        fam = "R424W%s%s" % (wk, gk)
        for sd in range(101, 107):
            r = readouts(fam, sd)
            if r and r["swing_df"] is not None:
                rows.append({"fam": fam, "weak": wv, "kv": 2.0 * gv, "seed": sd,
                             "swing_df": r["swing_df"], "knee_ic": r["knee_ic"]})
print("mixed-grid cells admitted: %d of %d" % (len(rows), len(WEAK) * len(GAIN) * 6))

print("\npeak swing dorsiflexion, cell means (deg):")
print("   %-10s" % "weakness" + "".join("  KV %.3f" % (2 * g) for g in sorted(GAIN.values())))
grid = {}
for wv in sorted(WEAK.values()):
    line = "   x%.2f     " % wv
    for gv in sorted(GAIN.values()):
        v = [r["swing_df"] for r in rows if r["weak"] == wv and abs(r["kv"] - 2 * gv) < 1e-9]
        grid[(wv, 2 * gv)] = (float(np.mean(v)), len(v)) if v else (None, 0)
        line += "  %7.3f" % np.mean(v) if v else "        -"
    print(line)

print("\nknee at contact, cell means (deg), for comparison:")
for wv in sorted(WEAK.values()):
    line = "   x%.2f     " % wv
    for gv in sorted(GAIN.values()):
        v = [r["knee_ic"] for r in rows if r["weak"] == wv and abs(r["kv"] - 2 * gv) < 1e-9]
        line += "  %7.3f" % np.mean(v) if v else "        -"
    print(line)


def fit(y):
    """least squares of y on [1, delivered gain, weakness scaling]"""
    A = np.array([[1.0, r["kv"], r["weak"]] for r in rows])
    b = np.array([r[y] for r in rows])
    coef, res, rank, sv = np.linalg.lstsq(A, b, rcond=None)
    pred = A.dot(coef)
    ss = float(np.sum((b - pred) ** 2))
    r2 = 1.0 - ss / float(np.sum((b - np.mean(b)) ** 2))
    # standard errors
    dof = len(b) - 3
    s2 = ss / dof
    cov = s2 * np.linalg.inv(A.T.dot(A))
    se = np.sqrt(np.diag(cov))
    return coef, se, r2, dof


seed_sd = {}
for y in ("swing_df", "knee_ic"):
    sds = []
    for f in set(r["fam"] for r in rows):
        v = [r[y] for r in rows if r["fam"] == f]
        if len(v) >= 2:
            sds.append(float(np.std(v, ddof=1)))
    seed_sd[y] = float(np.mean(sds))

print("\nregression on the mixed grid, both lesions entered together:")
out = {}
for y in ("swing_df", "knee_ic"):
    coef, se, r2, dof = fit(y)
    # the span each lesion commands across the ranges actually run
    kv_span = coef[1] * (max(r["kv"] for r in rows) - min(r["kv"] for r in rows))
    wk_span = coef[2] * (max(r["weak"] for r in rows) - min(r["weak"] for r in rows))
    out[y] = {
        "intercept": coef[0],
        "gain_coefficient_deg_per_unit_KV": coef[1], "gain_SE": se[1],
        "weakness_coefficient_deg_per_unit_scaling": coef[2], "weakness_SE": se[2],
        "span_commanded_by_gain_deg": kv_span,
        "span_commanded_by_weakness_deg": wk_span,
        "specificity_ratio": abs(kv_span) / abs(wk_span) if wk_span else None,
        "weakness_span_in_seed_SD": abs(wk_span) / seed_sd[y],
        "gain_span_in_seed_SD": abs(kv_span) / seed_sd[y],
        "seed_SD_deg": seed_sd[y], "R2": r2, "dof": dof}
    o = out[y]
    print("  %-9s  gain %+8.3f (SE %.3f) -> span %+7.3f deg = %6.1f seed SD" %
          (y, coef[1], se[1], kv_span, o["gain_span_in_seed_SD"]))
    print("             weak %+8.3f (SE %.3f) -> span %+7.3f deg = %6.1f seed SD   "
          "specificity %.1f:1   R2 %.3f" %
          (coef[2], se[2], wk_span, o["weakness_span_in_seed_SD"], o["specificity_ratio"], r2))

# ---- P4 on this variable: do different combinations give overlapping readings? -----------------
cells = [(k, v[0]) for k, v in grid.items() if v[0] is not None]
pairs = []
for i in range(len(cells)):
    for j in range(i + 1, len(cells)):
        (w1, g1), y1 = cells[i]
        (w2, g2), y2 = cells[j]
        if g1 != g2:                       # different reflex gain
            pairs.append({"a": {"weak": w1, "kv": g1, "deg": y1},
                          "b": {"weak": w2, "kv": g2, "deg": y2},
                          "sep_deg": abs(y1 - y2)})
pairs.sort(key=lambda p: p["sep_deg"])
floor = seed_sd["swing_df"]
conf = [p for p in pairs if p["sep_deg"] < floor]
print("\nP4 on peak swing dorsiflexion: pairs at DIFFERENT reflex gains whose readings sit closer")
print("than one seed SD (%.3f deg) -- these are the confusable combinations: %d of %d"
      % (floor, len(conf), len(pairs)))
for p in conf[:6]:
    print("   x%.2f KV %.3f (%7.3f)  vs  x%.2f KV %.3f (%7.3f)   apart %.3f"
          % (p["a"]["weak"], p["a"]["kv"], p["a"]["deg"],
             p["b"]["weak"], p["b"]["kv"], p["b"]["deg"], p["sep_deg"]))
if not conf:
    print("   none; the closest such pair is %.3f deg apart, %.1f seed SD"
          % (pairs[0]["sep_deg"], pairs[0]["sep_deg"] / floor))

dep = {
 "id": "MIXEDSWING_r526",
 "why": ("Real patients carry both lesions. A readout offered for apportionment has to be tested "
         "where both are present, not only on the single-lesion ladders. Registered prediction P4 "
         "was tested this way on knee-at-contact and held; this applies the same test to peak swing "
         "dorsiflexion."),
 "design": "R424W<weakness><archived gain>, 4 weakness levels x 4 gains, delivered gain = 2x label",
 "n_cells_admitted": len(rows),
 "cell_means_swing_df_deg": {"x%.2f_KV%.3f" % k: v[0] for k, v in sorted(grid.items())},
 "regression": out,
 "P4_on_this_variable": {
    "seed_SD_floor_deg": floor,
    "n_pairs_at_different_gains": len(pairs),
    "n_confusable_below_floor": len(conf),
    "closest_pair_deg": pairs[0]["sep_deg"] if pairs else None,
    "closest_pair_in_seed_SD": (pairs[0]["sep_deg"] / floor) if pairs else None,
    "confusable": conf[:12]},
}
io.open(os.path.join(P, "MIXEDSWING_r526.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> MIXEDSWING_r526.json")
