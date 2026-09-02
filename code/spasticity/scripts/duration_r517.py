# -*- coding: utf-8 -*-
"""r517: recompute the knee duration control on the CURRENT 23-cell corpus.

HEADLINE_DURATION_QUANT_r417 was computed on 17 Gate-G hyperreflexia cells against a 6.392 deg
headline and a 9.365 s arm gap. The manuscript propagates its slopes over 7 s against 5.280 deg on
23 cells, and the raw pooled slope it quotes (+0.487) is in no container. This computes all of it
once, on the corpus the paper actually analyses.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


def cells(fam):
    out = []
    for sd in range(101, 107):
        g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
        if not g: continue
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
        st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
        if not st: continue
        c, dat = S.load_sto(st[-1])
        if dat.size == 0: continue
        t = dat[:, 0]
        grf, thr = S.grf_vertical(c, dat, "l")
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k+1]) for k in range(len(hs)-1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5: continue
        kn = np.degrees(S.col(c, dat, "knee_angle_l"))
        out.append({"fam": fam, "t_end": float(t[-1]),
                    "knee": float(np.mean([kn[i] for i, _ in w]))})
    return out


hy = [c for f in HY for c in cells(f)]
wk = [c for f in WK for c in cells(f)]
th = [c["t_end"] for c in hy]; tw = [c["t_end"] for c in wk]
gap = float(np.mean(tw) - np.mean(th))
HEAD = 5.2799217587110885

allc = hy + wk
raw = np.polyfit([c["t_end"] for c in allc], [c["knee"] for c in allc], 1)
rawr = float(np.corrcoef([c["t_end"] for c in allc], [c["knee"] for c in allc])[0, 1])

per = {}
for f in HY:
    v = [c for c in hy if c["fam"] == f]
    if len(v) >= 3:
        per[f] = {"n": len(v),
                  "slope": float(np.polyfit([c["t_end"] for c in v], [c["knee"] for c in v], 1)[0]),
                  "t_end_span_s": float(max(c["t_end"] for c in v) - min(c["t_end"] for c in v))}
    else:
        per[f] = {"n": len(v), "slope": None, "reason": "below the four-seed bar"}
usable = [p["slope"] for p in per.values() if p["slope"] is not None]

dep = {
 "id": "DURATION_r517",
 "why": ("HEADLINE_DURATION_QUANT_r417 was computed on 17 hyperreflexia cells, a 6.392 deg headline "
         "and a 9.365 s gap. This recomputes the control on the 23-cell corpus the paper analyses."),
 "n_cells": {"hyperreflexia": len(hy), "weakness": len(wk)},
 "t_end_s": {"hyperreflexia": [float(min(th)), float(max(th)), float(np.mean(th))],
             "weakness": [float(min(tw)), float(max(tw)), float(np.mean(tw))],
             "arm_gap_s": gap, "arms_overlap": bool(max(th) > min(tw))},
 "raw_pooled": {"slope_deg_per_s": float(raw[0]), "pearson_r": rawr,
                "propagated_deg": float(raw[0]) * gap,
                "as_fraction_of_headline": abs(float(raw[0]) * gap) / HEAD,
                "note": "not the statistic rule 2 specifies: gain and end time are themselves related"},
 "within_dose_by_family": per,
 "within_dose_mean": {"n_families_usable": len(usable),
                      "mean_slope_deg_per_s": float(np.mean(usable)) if usable else None,
                      "propagated_deg": float(np.mean(usable)) * gap if usable else None,
                      "as_fraction_of_headline": (abs(float(np.mean(usable)) * gap) / HEAD)
                                                 if usable else None},
 "headline_deg": HEAD,
}
io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\DURATION_r517.json", "w",
        encoding="utf-8", newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print(json.dumps({k: dep[k] for k in ("n_cells","t_end_s","raw_pooled","within_dose_by_family",
                                      "within_dose_mean")}, indent=1, ensure_ascii=False))
