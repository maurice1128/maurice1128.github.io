# -*- coding: utf-8 -*-
"""Round 233 -- is the hip channel an optimiser-distance readout?
Implements PREREG_optdist_r233.md. READ-ONLY. No simulation.
"""
import io
import os
import re
import sys
import glob
import json
import hashlib

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PREREG = os.path.join(PAPER, "PREREG_optdist_r233.md")
WARM = "H1922v7b3-TSG3Dv8g-989_fixed2.par"
SEEDS = [101, 102, 103, 104, 105, 106]
PAR_RE = re.compile(r"^(\d+)_([\d.]+)_([\d.]+)\.par$")
ARMS = [("C", "R151C"), ("S", "R151S"), ("W800", "R151W"), ("W870", "R174W870"),
        ("W892", "R174W892"), ("W900", "R169W090"), ("W915", "R174W915"),
        ("W950", "R169W095")]
SCALE = {"W800": 0.800, "W870": 0.870, "W892": 0.892, "W900": 0.900,
         "W915": 0.915, "W950": 0.950}


def _sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def read_par(p):
    """columns: name / value / CMA-mean / CMA-std"""
    names, val, std = [], [], []
    for ln in io.open(p, encoding="utf-8", errors="replace"):
        f = ln.split("\t")
        if len(f) < 4:
            continue
        try:
            v = float(f[1]); s = float(f[3])
        except ValueError:
            continue
        names.append(f[0].strip()); val.append(v); std.append(s)
    return names, np.array(val), np.array(std)


def cell_dir(prefix, seed):
    ds = [x for x in glob.glob(os.path.join(RES, "%s_s%d.*" % (prefix, seed)))
          if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    return ds[0] if len(ds) == 1 else (sorted(ds)[0] if ds else None)


def select_par(d):
    rows = []
    for f in os.listdir(d):
        m = PAR_RE.match(f)
        if m:
            rows.append((float(m.group(3)), int(m.group(1)), f))
    if not rows:
        return None, None, None
    best = min(r[0] for r in rows)
    tied = sorted([r for r in rows if r[0] == best], key=lambda r: -r[1])  # highest gen
    return os.path.join(d, tied[0][2]), best, len(tied)


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def main():
    dep = json.load(io.open(os.path.join(PAPER, "LADDER36_r228.json"),
                            encoding="utf-8"))["per_seed_hip_flexion_LmR"]
    warm_path = None
    cells = []
    for tag, prefix in ARMS:
        for s in SEEDS:
            d = cell_dir(prefix, s)
            if d is None:
                continue
            wp = os.path.join(d, WARM)
            if warm_path is None and os.path.exists(wp):
                warm_path = wp
            par, fit, ntie = select_par(d)
            if par is None or not os.path.exists(wp):
                continue
            _, w, sd = read_par(wp)
            _, x, _ = read_par(par)
            if len(x) != len(w):
                continue
            z = (x - w) / np.where(sd > 0, sd, np.nan)
            z = z[np.isfinite(z)]
            cells.append({
                "arm": tag, "seed": s, "par": os.path.basename(par),
                "tied": ntie > 1, "fitness": fit,
                "n_params": int(len(z)),
                "D_norm": float(np.sqrt(np.mean(z ** 2))),
                "D_raw": float(np.linalg.norm(x - w)),
                "D_max": float(np.max(np.abs(z))),
                "endpoint": dep[tag][SEEDS.index(s)] if tag in dep else None,
                "scale": SCALE.get(tag)})

    res = {"round": 233, "metric": "D_norm = sqrt(mean(((x-w)/s)^2)); s = warm-start std",
           "warm_start": WARM, "warm_start_sha256": _sha(warm_path) if warm_path else None,
           "provenance": {"script": os.path.basename(__file__),
                          "script_sha256": _sha(os.path.abspath(__file__)),
                          "prereg_sha256": _sha(PREREG)},
           "cells": cells}

    lz = [c for c in cells if c["endpoint"] is not None]     # lesioned arms only
    res["n_cells_total"] = len(cells)
    res["n_with_endpoint"] = len(lz)

    corr = {}
    for dm in ("D_norm", "D_raw", "D_max"):
        corr[dm] = {"pooled_vs_endpoint": pearson([c[dm] for c in lz],
                                                  [c["endpoint"] for c in lz])}
        per = {}
        for tag, _ in ARMS:
            g = [c for c in lz if c["arm"] == tag]
            r = pearson([c[dm] for c in g], [c["endpoint"] for c in g]) if len(g) >= 3 else None
            if r is not None:
                per[tag] = r
        corr[dm]["within_arm"] = per
        vals = list(per.values())
        corr[dm]["within_arm_mean_abs"] = float(np.mean(np.abs(vals))) if vals else None
        corr[dm]["within_arm_mean_signed"] = float(np.mean(vals)) if vals else None
        corr[dm]["pooled_vs_fitness"] = pearson([c[dm] for c in cells],
                                                [c["fitness"] for c in cells])
        wk = [c for c in lz if c["scale"] is not None]
        am = {}
        for tag in SCALE:
            g = [c[dm] for c in wk if c["arm"] == tag]
            if g:
                am[tag] = float(np.mean(g))
        if len(am) >= 3:
            corr[dm]["armmean_vs_scale"] = pearson([SCALE[k] for k in sorted(am)],
                                                   [am[k] for k in sorted(am)])
        corr[dm]["arm_means"] = am
    res["correlations"] = corr

    p = corr["D_norm"]["pooled_vs_endpoint"]
    wm = corr["D_norm"]["within_arm_mean_abs"]
    signs = {k: np.sign(corr[k]["pooled_vs_endpoint"]) for k in corr
             if corr[k]["pooled_vs_endpoint"] is not None}
    if len(set(signs.values())) > 1:
        res["READING"], res["REASON"] = "SPLIT", "the three distance metrics disagree in sign"
    elif p is not None and wm is not None and abs(p) >= 0.5 and wm >= 0.4:
        res["READING"] = "STRONG"
        res["REASON"] = ("pooled r = %+.4f (|r| >= 0.5) and mean within-arm |r| = %.4f "
                         "(>= 0.4)" % (p, wm))
    elif p is not None and wm is not None and (abs(p) >= 0.5) != (wm >= 0.4):
        res["READING"] = "SPLIT"
        res["REASON"] = ("pooled r = %+.4f and mean within-arm |r| = %.4f disagree on the "
                         "threshold" % (p, wm))
    else:
        res["READING"] = "WEAK"
        res["REASON"] = ("pooled r = %+.4f, mean within-arm |r| = %.4f" % (p, wm))

    json.dump(res, io.open(os.path.join(PAPER, "OPTDIST_r233.json"), "w",
                           encoding="utf-8"), indent=1)

    print("cells: %d (%d with endpoint)   warm start sha %s"
          % (len(cells), len(lz), (res["warm_start_sha256"] or "")[:16]))
    print("\narm-mean D_norm and endpoint:")
    for tag, _ in ARMS:
        g = [c for c in cells if c["arm"] == tag]
        if not g:
            continue
        ep = [c["endpoint"] for c in g if c["endpoint"] is not None]
        print("  %-5s n=%d  D_norm %8.3f   endpoint %s   fitness %6.3f"
              % (tag, len(g), np.mean([c["D_norm"] for c in g]),
                 ("%+.4f" % np.mean(ep)) if ep else "   n/a  ",
                 np.mean([c["fitness"] for c in g])))
    print()
    for dm in ("D_norm", "D_raw", "D_max"):
        c = corr[dm]
        print("%-7s pooled r(endpoint) %+.4f | within-arm mean|r| %s | r(fitness) %+.4f | "
              "arm-mean vs scale %s"
              % (dm, c["pooled_vs_endpoint"],
                 ("%.4f" % c["within_arm_mean_abs"]) if c["within_arm_mean_abs"] is not None else "n/a",
                 c["pooled_vs_fitness"],
                 ("%+.4f" % c.get("armmean_vs_scale")) if c.get("armmean_vs_scale") is not None else "n/a"))
    print("\n  within-arm r (D_norm): %s"
          % {k: round(v, 3) for k, v in corr["D_norm"]["within_arm"].items()})
    print("\nREADING = %s\n  %s" % (res["READING"], res["REASON"]))
    print("wrote OPTDIST_r233.json")


if __name__ == "__main__":
    main()
