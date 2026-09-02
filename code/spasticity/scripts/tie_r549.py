# -*- coding: utf-8 -*-
"""r549: is the rank correlation used throughout this paper actually Spearman's rho?

An adversarial code review found that the shared helper

    def spear(x, y):
        rx = np.argsort(np.argsort(x)).astype(float)
        ry = np.argsort(np.argsort(y)).astype(float)
        return float(np.corrcoef(rx, ry)[0, 1])

assigns distinct ranks inside a tie group, broken by array order, rather than mid-ranks. The dose
vector x is heavily tied by construction: 5 distinct gains over 23 hyperreflexia cells and 6
distinct scalings over 36 weakness cells. So this is not Spearman's rho, and it is the statistic
behind rho = 0.956, behind the |rho| >= 0.8 gate, and therefore behind the counts of 3 and 25.

This recomputes every affected quantity with mid-ranks (the textbook definition, and what
scipy.stats.spearmanr returns) and reports what moves. It writes nothing except its own container.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
JOINTS = [("knee_angle_l", "knee"), ("ankle_angle_l", "ankle"), ("hip_flexion_l", "hip")]
GRID = list(range(0, 101, 5))
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]
RHO_BAR = 0.8
SEM = 4.9 / (1.96 * np.sqrt(2.0))


def old_spear(x, y):
    """the helper as shipped: argsort of argsort, no tie correction"""
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def midrank(a):
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def new_spear(x, y):
    """Spearman's rho proper: Pearson on mid-ranks"""
    rx, ry = midrank(x), midrank(y)
    if len(set(rx)) < 2 or len(set(np.round(ry, 9))) < 2:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


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
    out = {}
    for col, nm in JOINTS:
        try:
            y = np.degrees(S.col(c, dat, col))
        except Exception:
            continue
        cur, sw, stn, tof = [], [], [], []
        for a, b in w:
            seg = y[a:b]
            cur.append(np.interp(np.linspace(0, 100, 101), np.linspace(0, 100, b - a), seg))
            m = on[a:b]
            i0 = np.where(~m)[0]
            if i0.size:
                sw.append((float(np.max(seg[i0])), float(np.min(seg[i0]))))
                tof.append(float(seg[i0[0]]))
            i1 = np.where(m)[0]
            if i1.size:
                stn.append((float(np.max(seg[i1])), float(np.min(seg[i1]))))
        cu = np.mean(cur, axis=0)
        out[nm] = {"curve": cu,
                   "swing_max": np.mean([x[0] for x in sw]) if sw else None,
                   "swing_min": np.mean([x[1] for x in sw]) if sw else None,
                   "stance_max": np.mean([x[0] for x in stn]) if stn else None,
                   "stance_min": np.mean([x[1] for x in stn]) if stn else None,
                   "toe_off": np.mean(tof) if tof else None,
                   "rom": float(np.mean([c.max() - c.min() for c in cur]))}
    return out


print("loading ...")
CELLS = {}
for f, _ in HY + WK:
    CELLS[f] = [d for d in (load(f, s) for s in range(101, 107)) if d]
print("   %d hyperreflexia cells, %d weakness cells"
      % (sum(len(CELLS[f]) for f, _ in HY), sum(len(CELLS[f]) for f, _ in WK)))

CAND = []
for col, nm in JOINTS:
    for p in GRID:
        CAND.append(("%s at %d%% of cycle" % (nm, p), lambda d, nm=nm, p=p: d[nm]["curve"][p]))
    for k, lab in (("swing_max", "peak in swing"), ("swing_min", "trough in swing"),
                   ("stance_max", "peak in stance"), ("stance_min", "trough in stance"),
                   ("toe_off", "at toe-off"), ("rom", "range of motion")):
        CAND.append(("%s %s" % (nm, lab), lambda d, nm=nm, k=k: d[nm][k]))

rows = []
for nm, fn in CAND:
    rec = {"name": nm}
    ok = True
    for tag, fams in (("weak", WK), ("hyper", HY)):
        dose, val, per = [], [], {}
        for f, dd in fams:
            for d in CELLS[f]:
                try:
                    x = fn(d)
                except Exception:
                    x = None
                if x is not None:
                    dose.append(dd); val.append(float(x))
                    per.setdefault(dd, []).append(float(x))
        if len(per) < 3:
            ok = False; break
        ms = [float(np.mean(per[k])) for k in sorted(per)]
        # family-level rho: one point per dose, no ties in the dose at all
        fam_rho = new_spear(sorted(per), ms)
        rec[tag] = {"rho_old": old_spear(dose, val), "rho_new": new_spear(dose, val),
                    "rho_family": fam_rho, "span_deg": max(ms) - min(ms)}
    if ok:
        rows.append(rec)

print("\ncandidates scored: %d" % len(rows))
d_h = [abs(r["hyper"]["rho_new"] - r["hyper"]["rho_old"]) for r in rows]
d_w = [abs(r["weak"]["rho_new"] - r["weak"]["rho_old"]) for r in rows]
print("|rho_new - rho_old|   hyperreflexia: max %.4f, mean %.4f" % (max(d_h), np.mean(d_h)))
print("                      weakness:      max %.4f, mean %.4f" % (max(d_w), np.mean(d_w)))


def counts(key):
    w = [r["name"] for r in rows
         if abs(r["weak"][key]) >= RHO_BAR and r["weak"]["span_deg"] >= SEM]
    h = [r["name"] for r in rows
         if abs(r["hyper"][key]) >= RHO_BAR and r["hyper"]["span_deg"] >= SEM]
    return w, h


print("\nthe counts under each definition of rho (bar %.2f deg, |rho| >= %.1f):" % (SEM, RHO_BAR))
res = {}
for key, lab in (("rho_old", "as shipped (argsort, ties broken by array order)"),
                 ("rho_new", "Spearman proper (mid-ranks), cell level"),
                 ("rho_family", "family level, one point per dose (no ties at all)")):
    w, h = counts(key)
    res[key] = {"label": lab, "n_tone": len(h), "n_weak": len(w), "weak": w}
    print("   %-52s tone %2d   weakness %2d" % (lab, len(h), len(w)))
    if w:
        print("       %s" % ", ".join(w))

sw = [r for r in rows if r["name"] == "ankle peak in swing"][0]
print("\nthe reported endpoint, ankle peak in swing:")
for tag in ("hyper", "weak"):
    print("   %-6s rho_old %+.4f   rho_new %+.4f   rho_family %+.4f   span %.3f deg"
          % (tag, sw[tag]["rho_old"], sw[tag]["rho_new"], sw[tag]["rho_family"],
             sw[tag]["span_deg"]))

io.open(os.path.join(P, "TIE_r549.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "TIE_r549",
 "why": ("The shared rank-correlation helper used argsort of argsort, which assigns distinct ranks "
         "inside a tie group broken by array order rather than mid-ranks. The dose vector is heavily "
         "tied by construction (5 gains over 23 cells, 6 scalings over 36). This recomputes every "
         "affected quantity with mid-ranks and at the family level, where no ties exist at all."),
 "rho_bar": RHO_BAR, "span_bar_deg": SEM,
 "max_abs_change_hyper": max(d_h), "max_abs_change_weak": max(d_w),
 "mean_abs_change_hyper": float(np.mean(d_h)), "mean_abs_change_weak": float(np.mean(d_w)),
 "counts": res,
 "endpoint": {k: sw[k] for k in ("hyper", "weak")},
 "all": [{"name": r["name"],
          "hyper": {k: r["hyper"][k] for k in ("rho_old", "rho_new", "rho_family", "span_deg")},
          "weak": {k: r["weak"][k] for k in ("rho_old", "rho_new", "rho_family", "span_deg")}}
         for r in rows],
}, indent=1, ensure_ascii=False, default=float))
print("\n-> TIE_r549.json")
