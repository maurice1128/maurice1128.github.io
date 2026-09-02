# -*- coding: utf-8 -*-
"""r528: does peak swing dorsiflexion separate where NOTHING is dying?

Limitation 2 of the manuscript is that the knee's separating window and the model's survival edge
coincide: at the two gains where no cell falls, the knee sits inside the weakness band, and at the
lowest separating gain five of six cells fall. The knee therefore cannot be shown to separate
independently of cells dying, and the manuscript says so.

This applies the manuscript's own survival-matched definition -- cells in which EVERY seed runs the
full simulation -- to peak swing dorsiflexion. If the gradient survives on that subset, this endpoint
is not subject to the confound that binds the knee. If it does not, it is subject to the same one and
must be reported the same way.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1, FULL = 1.0, 9.73, 19.9      # FULL: the simulation's own horizon, 20 s
WEAK = {"060": 0.60, "070": 0.70, "080": 0.80, "100": 1.00}
GAIN = {"0125": 0.0125, "0250": 0.0250, "0500": 0.0500, "1100": 0.1100}


def probe(fam, sd):
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
    te = float(t[-1])
    if te < T1 or len(w) < 5:
        return {"t_end": te, "admitted": False}
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    on = grf > thr
    pk = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
    return {"t_end": te, "admitted": True, "full": te >= FULL,
            "swing_df": float(np.mean(pk)) if pk else None,
            "knee_ic": float(np.mean([kn[a] for a, _ in w]))}


cell = {}
for wk, wv in WEAK.items():
    for gk, gv in GAIN.items():
        fam = "R424W%s%s" % (wk, gk)
        v = [probe(fam, sd) for sd in range(101, 107)]
        cell[(wv, 2 * gv)] = [x for x in v if x]

print("cells where EVERY existing seed runs the full %.0f s (the manuscript's survival-matched bar):" % FULL)
print("   %-9s" % "weakness" + "".join("  KV %.3f" % (2 * g) for g in sorted(GAIN.values())))
matched = {}
for wv in sorted(WEAK.values()):
    line = "   x%.2f    " % wv
    for gv in sorted(GAIN.values()):
        v = cell[(wv, 2 * gv)]
        ok = bool(v) and all(x["admitted"] and x["full"] for x in v)
        matched[(wv, 2 * gv)] = ok
        line += "     %-3s" % ("yes" if ok else "no")
    print(line)

gains = sorted(set(g for (w, g), ok in matched.items() if ok))
print("\ngains at which at least one cell is fully survival-matched: %s" % gains)


def summarise(key, sel):
    v = {}
    for (w, g), c in cell.items():
        if sel(w, g):
            x = [y[key] for y in c if y["admitted"] and y[key] is not None]
            if x:
                v[(w, g)] = (float(np.mean(x)), len(x))
    return v


out = {}
for key in ("swing_df", "knee_ic"):
    sub = summarise(key, lambda w, g: matched[(w, g)])
    if len(set(g for _, g in sub)) < 2:
        print("\n%s: fewer than two survival-matched gains; no gradient computable" % key)
        out[key] = {"computable": False}
        continue
    # seed SD within the matched subset
    sds = []
    for (w, g) in sub:
        x = [y[key] for y in cell[(w, g)] if y["admitted"] and y[key] is not None]
        if len(x) >= 2:
            sds.append(float(np.std(x, ddof=1)))
    sd = float(np.mean(sds))
    gs = sorted(set(g for _, g in sub))
    per_gain = {g: float(np.mean([m for (w, gg), (m, n) in sub.items() if gg == g])) for g in gs}
    span = per_gain[gs[0]] - per_gain[gs[-1]]
    # adjacent-gain separation, the sharpest test
    adj = [(gs[i], gs[i + 1], per_gain[gs[i]] - per_gain[gs[i + 1]]) for i in range(len(gs) - 1)]
    print("\n%s on the survival-matched subset (seed SD %.3f deg):" % (key, sd))
    for g in gs:
        print("   KV %.3f   %8.3f" % (g, per_gain[g]))
    print("   span across matched gains %+.3f deg = %.1f seed SD" % (span, abs(span) / sd))
    for a, b, d in adj:
        print("   KV %.3f -> %.3f : %+.3f deg = %.1f seed SD" % (a, b, d, abs(d) / sd))
    # do the individual CELLS separate between adjacent matched gains?
    disj = []
    for a, b, _ in adj:
        va = [y[key] for (w, g) in sub if g == a for y in cell[(w, g)] if y["admitted"] and y[key] is not None]
        vb = [y[key] for (w, g) in sub if g == b for y in cell[(w, g)] if y["admitted"] and y[key] is not None]
        disj.append({"from": a, "to": b, "disjoint": bool(min(va) > max(vb) or min(vb) > max(va)),
                     "gap_deg": max(min(va) - max(vb), min(vb) - max(va))})
    for d in disj:
        print("   cells KV %.3f vs %.3f: disjoint %s, gap %+.3f deg (%.1f seed SD)"
              % (d["from"], d["to"], d["disjoint"], d["gap_deg"], d["gap_deg"] / sd))
    out[key] = {"computable": True, "seed_SD_deg": sd,
                "matched_gains": gs, "mean_by_gain_deg": {str(k): v for k, v in per_gain.items()},
                "span_deg": span, "span_in_seed_SD": abs(span) / sd,
                "adjacent": [{"from": a, "to": b, "diff_deg": d, "in_seed_SD": abs(d) / sd}
                             for a, b, d in adj],
                "adjacent_cell_disjointness": disj}

dep = {
 "id": "SWINGSURV_r528",
 "why": ("Limitation 2 binds the knee: its separating window coincides with the model's survival "
         "edge, so the knee cannot be shown to separate independently of cells dying. This applies "
         "the manuscript's own survival-matched definition to peak swing dorsiflexion."),
 "survival_matched_definition": "every existing seed of the cell runs the full %.0f s" % FULL,
 "matched_cells": {"x%.2f_KV%.3f" % k: bool(v) for k, v in sorted(matched.items())},
 "results": out,
}
io.open(os.path.join(P, "SWINGSURV_r528.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWINGSURV_r528.json")
