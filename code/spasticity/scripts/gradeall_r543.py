# -*- coding: utf-8 -*-
"""r543: can ANY of the 81 candidates grade weakness depth? The test the manuscript assumed.

Two claims in the draft were checked against the containers and both were found to be stated more
broadly than they had been tested.

  (i) "tone writes degrees and weakness writes fractions of a degree" is true of the reported
      endpoint, where the ratio of displacements from control is 21 to 1. Across all 81 candidates
      the median ratio is 2.9, weakness reaches 3.95 degrees at the knee in early swing, and on 10
      of the 81 weakness displaces MORE than hyperreflexia. The asymmetry is a property of the
      selected endpoint, not of the corpus.

  (ii) "no readout recovers weakness depth" was tested by regression on two readouts and their
      combinations (PAIR_r533), not on 81.

This runs the grading test on every candidate: within the weakness arm, does the readout order the
six weakness depths; and within the hyperreflexia arm, does it order the five gains. Both are scored
by Spearman rho against the delivered dose and, because a rank correlation says nothing about
whether the span is usable, also by the span in degrees and by that span against the candidate's own
within-cell seed SD.
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
    print("   %-12s n=%d" % (f, len(CELLS[f])))

CAND = []
for col, nm in JOINTS:
    for p in GRID:
        CAND.append(("%s at %d%% of cycle" % (nm, p), lambda d, nm=nm, p=p: d[nm]["curve"][p]))
    for k, lab in (("swing_max", "peak in swing"), ("swing_min", "trough in swing"),
                   ("stance_max", "peak in stance"), ("stance_min", "trough in stance"),
                   ("toe_off", "at toe-off"), ("rom", "range of motion")):
        CAND.append(("%s %s" % (nm, lab), lambda d, nm=nm, k=k: d[nm][k]))


def spear(x, y):
    if len(set(x)) < 2 or len(set(np.round(y, 9))) < 2:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


rows = []
for nm, fn in CAND:
    rec = {"name": nm}
    ok = True
    for tag, fams in (("weak", WK), ("hyper", HY)):
        dose, val, per = [], [], {}
        for f, dd in fams:
            v = []
            for d in CELLS[f]:
                try:
                    x = fn(d)
                except Exception:
                    x = None
                if x is not None:
                    v.append(float(x)); dose.append(dd); val.append(float(x))
            if v:
                per[dd] = (float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0)
        if len(per) < 3:
            ok = False; break
        sd = float(np.mean([s for _, s in per.values() if s > 0])) or float("nan")
        ms = [per[k][0] for k in sorted(per)]
        rec[tag] = {"rho": spear(dose, val), "span_deg": max(ms) - min(ms),
                    "seed_SD": sd, "span_in_seed_SD": (max(ms) - min(ms)) / sd if sd else float("nan"),
                    "by_dose": {str(k): per[k][0] for k in sorted(per)}}
    if ok:
        rows.append(rec)

print("\ncandidates scored: %d" % len(rows))
# ref [15]'s BETWEEN-SESSION MDC for peak ankle angle in swing, inverted through that paper's
# own MDC = SEM x 1.96 x sqrt(2). One bar is applied to all 81 candidates because published
# between-session errors exist for only two of the 81 variables; this is the smaller of the two
# and therefore the more permissive. The manuscript discloses this and its sensitivity.
SEM = 4.9 / (1.96 * np.sqrt(2.0))
print("between-session measurement error used as the usability bar: %.3f deg\n" % SEM)

byw = sorted(rows, key=lambda r: -abs(r["weak"]["rho"]))
print("BEST AT ORDERING WEAKNESS DEPTH (|rho| against tibialis anterior scaling):")
print("  %-26s %7s %9s %11s   %7s %9s" % ("readout", "rho", "span deg", "span/seedSD", "rho", "span deg"))
print("  %-26s %7s %9s %11s   %7s %9s" % ("", "weak", "weak", "weak", "hyper", "hyper"))
for r in byw[:12]:
    print("  %-26s %7.3f %9.3f %11.1f   %7.3f %9.3f"
          % (r["name"], r["weak"]["rho"], r["weak"]["span_deg"], r["weak"]["span_in_seed_SD"],
             r["hyper"]["rho"], r["hyper"]["span_deg"]))

usable = [r for r in rows if abs(r["weak"]["rho"]) >= 0.8 and r["weak"]["span_deg"] >= SEM]
print("\ncandidates that BOTH order weakness (|rho| >= 0.8) AND span more than one clinical")
print("measurement error (%.2f deg): %d of %d" % (SEM, len(usable), len(rows)))
for r in usable:
    print("   %-26s rho %+.3f  span %.3f deg" % (r["name"], r["weak"]["rho"], r["weak"]["span_deg"]))

hyus = [r for r in rows if abs(r["hyper"]["rho"]) >= 0.8 and r["hyper"]["span_deg"] >= SEM]
print("\nthe same test for HYPERREFLEXIA: %d of %d" % (len(hyus), len(rows)))
for r in sorted(hyus, key=lambda r: -r["hyper"]["span_deg"])[:8]:
    print("   %-26s rho %+.3f  span %.3f deg" % (r["name"], r["hyper"]["rho"], r["hyper"]["span_deg"]))

sw = [r for r in rows if r["name"] == "ankle peak in swing"]
if sw:
    r = sw[0]
    print("\nthe reported endpoint: weakness rho %+.3f span %.3f deg; hyperreflexia rho %+.3f span %.3f deg"
          % (r["weak"]["rho"], r["weak"]["span_deg"], r["hyper"]["rho"], r["hyper"]["span_deg"]))

io.open(os.path.join(P, "GRADEALL_r543.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "GRADEALL_r543",
 "why": ("Two claims in the draft were stated more broadly than they had been tested: the 21-to-1 "
         "displacement asymmetry is a property of the selected endpoint rather than of the corpus "
         "(median ratio 2.9 across 81), and the failure to recover weakness depth had been tested by "
         "regression on two readouts, not on 81. This runs the grading test on every candidate."),
 "clinical_measurement_error_deg": SEM,
 "n_candidates": len(rows),
 "n_grading_weakness_usably": len(usable),
 "n_grading_hyperreflexia_usably": len(hyus),
 "usable_for_weakness": [r["name"] for r in usable],
 "usable_for_hyperreflexia": [r["name"] for r in hyus],
 "all": rows if False else [{k: (v if k == "name" else
                                 {kk: vv for kk, vv in v.items() if kk != "by_dose"})
                             for k, v in r.items()} for r in rows],
}, indent=1, ensure_ascii=False, default=float))
print("\n-> GRADEALL_r543.json")
