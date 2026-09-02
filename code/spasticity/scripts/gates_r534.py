# -*- coding: utf-8 -*-
"""r534: every candidate readout, side by side, through the same gates.

SWEEP_r532 scanned 81 candidates on separation alone and found seven that are two-sided and
separating. Separation is where this project has been fooled before, so no candidate is comparable
to the manuscript's endpoint until it has been through what that endpoint went through. This runs
one battery over the candidates that matter, so the comparison is like for like.

Two gates are added to the corpus set because the candidates differ in a way the old ones did not:

  STEEPNESS. A readout taken where the joint is moving fast converts a phase error into a reading
  error. The winner of r532's scan, ankle at 85 per cent, sits where the control curve falls 5.5 deg
  in a tenth of a cycle; the band at 40 to 50 per cent sits where it moves a sixth as fast. Steepness
  is reported as degrees per one per cent of cycle, which is directly the error a one per cent
  phase mistake buys.

  TWO-SIDEDNESS is scored here against the artefact floor measured for that candidate, not against
  its seed SD as in r532, because that is the bar the manuscript's endpoint had to clear.
"""
import glob, io, itertools, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)
CTRL = ["R151C"]
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]
SHAM = {"spastic": ["R151S", "R400SPgc1", "R400SPgc2", "R400SPgc3"],
        "weak": ["R151W", "R400WKc1", "R400WKc2", "R400WKc3"]}


def load(fam, sd, t1=T1):
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
    out = {"t_end": float(t[-1])}
    for side in ("l", "r"):
        grf, thr = S.grf_vertical(c, dat, side)
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= t1]
        w = w[:-1] if len(w) >= 2 else w
        if side == "l" and (float(t[-1]) < t1 or len(w) < 5):
            return None
        if not w:
            continue
        for j, nm in (("knee_angle_%s" % side, "knee"), ("ankle_angle_%s" % side, "ankle")):
            y = np.degrees(S.col(c, dat, j))
            cur = [np.interp(np.linspace(0, 100, 101), np.linspace(0, 100, b - a), y[a:b])
                   for a, b in w]
            out["%s_%s" % (nm, side)] = np.array(cur)
        if side == "l":
            on = grf > thr
            pk = []
            for a, b in w:
                idx = np.where(~on[a:b])[0]
                if idx.size:
                    pk.append(float(np.max(np.degrees(S.col(c, dat, "ankle_angle_l"))[a:b][idx])))
            out["swingpk"] = np.array(pk) if pk else None
        try:
            px = S.col(c, dat, "pelvis_tx")
            out["speed"] = float((px[w[-1][1]] - px[w[0][0]]) / (t[w[-1][1]] - t[w[0][0]]))
        except Exception:
            out["speed"] = None
    return out


print("loading ...")
CELLS = {}
for f in CTRL + [x[0] for x in HY + WK] + [x for v in SHAM.values() for x in v]:
    if f in CELLS:
        continue
    CELLS[f] = [d for d in (load(f, s) for s in SEEDS) if d]
    print("   %-12s n=%d" % (f, len(CELLS[f])))

# readout(cell) -> per-cycle array; the mean of that array is the cell value
CANDS = [
 ("knee at contact  [current]", lambda d, s="l": d["knee_%s" % s][:, 0], "knee", [0]),
 ("ankle 40-50% window", lambda d, s="l": d["ankle_%s" % s][:, 40:51].mean(axis=1), "ankle",
  list(range(40, 51))),
 ("ankle at 45%", lambda d, s="l": d["ankle_%s" % s][:, 45], "ankle", [45]),
 ("ankle at 85%  [scan winner]", lambda d, s="l": d["ankle_%s" % s][:, 85], "ankle", [85]),
 ("ankle peak in swing", lambda d, s="l": d["swingpk"], "ankle", None),
]


def cellvals(fams, fn, side="l"):
    out = []
    for f in fams:
        for d in CELLS[f]:
            try:
                v = fn(d, side)
            except Exception:
                v = None
            if v is not None and len(v):
                out.append((f, float(np.mean(v)), np.asarray(v), d))
    return out


REP = {}
for name, fn, joint, phases in CANDS:
    ct = cellvals(CTRL, fn)
    hy = cellvals([f for f, _ in HY], fn)
    wk = cellvals([f for f, _ in WK], fn)
    if not (ct and hy and wk):
        continue
    hv = [v for _, v, _, _ in hy]
    wv = [v for _, v, _, _ in wk]
    cv = [v for _, v, _, _ in ct]
    sd = float(np.mean([np.std([v for g, v, _, _ in hy + wk if g == f], ddof=1)
                        for f, _ in HY + WK if len([1 for g, _, _, _ in hy + wk if g == f]) >= 2]))
    # artefact floor by the chaining protocol, on THIS readout
    art = 0.0
    for chain in SHAM.values():
        base = np.mean([v for _, v, _, _ in cellvals([chain[0]], fn)]) if CELLS[chain[0]] else None
        for f in chain[1:]:
            x = [v for _, v, _, _ in cellvals([f], fn)]
            if x and base is not None:
                art = max(art, abs(float(np.mean(x)) - base))
    c0, h0, w0 = float(np.mean(cv)), float(np.mean(hv)), float(np.mean(wv))
    dh, dw = h0 - c0, w0 - c0
    gap = max(min(wv) - max(hv), min(hv) - max(wv))
    eff = w0 - h0
    # duration control
    sl = []
    for f, _ in HY + WK:
        v = [(d["t_end"], val) for g, val, _, d in hy + wk if g == f]
        if len(v) >= 3 and len(set(round(x[0], 3) for x in v)) > 1:
            sl.append(float(np.polyfit([x[0] for x in v], [x[1] for x in v], 1)[0]))
    dslope = float(np.mean(sl)) if sl else 0.0
    dtg = float(np.mean([d["t_end"] for _, _, _, d in hy]) - np.mean([d["t_end"] for _, _, _, d in wk]))
    dprop = dslope * dtg
    # stationarity
    per = []
    for i in range(5):
        a = [s[i] for _, _, s, _ in hy if len(s) > i]
        b = [s[i] for _, _, s, _ in wk if len(s) > i]
        if a and b:
            per.append(float(np.mean(b) - np.mean(a)))
    stat_ok = bool(per) and (all(x > 0 for x in per) or all(x < 0 for x in per))
    spread = (max(per) - min(per)) if per else float("nan")
    # unlesioned side
    rh = [v for _, v, _, _ in cellvals([f for f, _ in HY], fn, "r")]
    rw = [v for _, v, _, _ in cellvals([f for f, _ in WK], fn, "r")]
    rshare = abs((np.mean(rw) - np.mean(rh)) / eff) if rh and rw and eff else float("nan")
    # steepness: deg per 1% of cycle at the readout location
    steep = float("nan")
    if phases:
        p = phases[len(phases) // 2]
        cc = np.mean([d["ankle_l"] if joint == "ankle" else d["knee_l"] for d in CELLS["R151C"]],
                     axis=(0, 1))
        lo, hi = max(0, p - 1), min(100, p + 1)
        steep = abs(float(cc[hi] - cc[lo])) / (hi - lo)
    # family level
    fh = [float(np.mean([v for g, v, _, _ in hy if g == f])) for f, _ in HY]
    fw = [float(np.mean([v for g, v, _, _ in wk if g == f])) for f, _ in WK]
    allf = fh + fw
    obs = abs(np.mean(fw) - np.mean(fh))
    cnt = sum(1 for idx in itertools.combinations(range(len(allf)), len(fh))
              if abs(np.mean([allf[i] for i in range(len(allf)) if i not in idx])
                     - np.mean([allf[i] for i in idx])) >= obs - 1e-12)
    tot = math.comb(len(allf), len(fh))
    lab = [(v, "H") for v in hv] + [(v, "W") for v in wv]
    ok = 0
    for f, tag in [(f, "H") for f, _ in HY] + [(f, "W") for f, _ in WK]:
        held = [(v, tag) for g, v, _, _ in hy + wk if g == f]
        rest = [(v, "H") for g, v, _, _ in hy if g != f] + [(v, "W") for g, v, _, _ in wk if g != f]
        th = 0.5 * (np.mean([v for v, l in rest if l == "H"]) + np.mean([v for v, l in rest if l == "W"]))
        sgn = 1 if np.mean(hv) < np.mean(wv) else -1
        ok += sum(1 for v, l in held if ((("H" if sgn * v < sgn * th else "W")) == l))
    REP[name] = {
        "control": c0, "weakness": w0, "hyperreflexia": h0,
        "disp_weak": dw, "disp_hyper": dh, "artefact_floor": art, "seed_SD": sd,
        "two_sided_vs_artefact": bool(dh * dw < 0 and abs(dh) > art and abs(dw) > art),
        "disp_weak_in_artefact": dw / art if art else float("nan"),
        "arm_difference": eff, "cell_gap": gap, "disjoint": bool(gap > 0),
        "gap_in_seed_SD": gap / sd,
        "duration_slope": dslope, "duration_propagated": dprop,
        "duration_pct_of_effect": 100 * abs(dprop / eff) if eff else float("nan"),
        "stationary": stat_ok, "per_cycle": per, "stationarity_spread": spread,
        "unlesioned_share": rshare,
        "steepness_deg_per_pct": steep,
        "permutation_rank": cnt, "permutation_p": cnt / tot,
        "lofo_accuracy": ok / len(lab),
    }

hdr = ("readout", "2side", "disj", "gap/SD", "dispW/art", "dur%", "stat", "R-side", "steep", "LOFO", "perm p")
print("\n%-28s %5s %5s %7s %9s %6s %5s %7s %6s %6s %8s" % hdr)
for n, r in REP.items():
    print("%-28s %5s %5s %7.2f %9.2f %6.1f %5s %7.2f %6.2f %6.3f %8.4f"
          % (n, r["two_sided_vs_artefact"], r["disjoint"], r["gap_in_seed_SD"],
             r["disp_weak_in_artefact"], r["duration_pct_of_effect"], r["stationary"],
             r["unlesioned_share"], r["steepness_deg_per_pct"], r["lofo_accuracy"],
             r["permutation_p"]))

print("\nartefact floor and noise, per readout:")
for n, r in REP.items():
    print("   %-28s artefact %.3f   seed SD %.3f   cell gap %.3f   arm diff %+.3f"
          % (n, r["artefact_floor"], r["seed_SD"], r["cell_gap"], r["arm_difference"]))

dep = {"id": "GATES_r534",
       "why": ("SWEEP_r532 ranked 81 candidates on separation alone. Separation is where this "
               "project has been fooled before. This runs the corpus battery over the candidates "
               "that matter so the comparison with the manuscript's endpoint is like for like, and "
               "adds steepness, which converts a phase error into a reading error and is what "
               "distinguishes the scan winner from the band beneath it."),
       "candidates": REP}
io.open(os.path.join(P, "GATES_r534.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> GATES_r534.json")
