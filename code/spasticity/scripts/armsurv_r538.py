# -*- coding: utf-8 -*-
"""r538: does the ARM separation survive survival matching? The test r528 did not do.

SWINGSURV_r528 restricted the mixed grid to cells in which every seed runs the full simulation and
compared two REFLEX GAINS. That is a gain contrast. Limitation 2 of the manuscript is about the ARM
contrast -- hyperreflexia against weakness -- and the two are not the same question. Reporting the
gain result as though it settled the arm question conflated them.

The matched subset of the mixed grid contains no pure-weakness cell, so the arm contrast cannot be
made there at all. It can be made on the main corpus, and that is what this does: restrict the
eleven lesion families to cells in which EVERY admitted seed reaches the full horizon, then ask
whether the arms still separate, on each candidate readout.

If no hyperreflexia family survives intact, that is itself the answer and must be reported as such
rather than worked around.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1, FULL = 1.0, 9.73, 19.9
CTRL = [("R151C", None)]
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
    te = float(t[-1])
    if te < T1 or len(w) < 5:
        return {"t_end": te, "admitted": False}
    on = grf > thr
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    cur_a = np.array([np.interp(np.linspace(0, 100, 101), np.linspace(0, 100, b - a), an[a:b])
                      for a, b in w])
    pk = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
    return {"t_end": te, "admitted": True, "full": te >= FULL,
            "knee_ic": float(np.mean([kn[a] for a, _ in w])),
            "ank45": float(np.mean(cur_a[:, 45])),
            "ank4050": float(np.mean(cur_a[:, 40:51])),
            "ank85": float(np.mean(cur_a[:, 85])),
            "swingpk": float(np.mean(pk)) if pk else None}


CELLS = {}
for f, _ in CTRL + HY + WK:
    CELLS[f] = [d for d in (load(f, s) for s in range(101, 107)) if d]

print("survival by family (admitted cells / cells reaching the full 20 s):")
full_fams = {"H": [], "W": []}
for tag, fams in (("H", HY), ("W", WK)):
    for f, dose in fams:
        v = [d for d in CELLS[f] if d.get("admitted")]
        nf = sum(1 for d in v if d.get("full"))
        intact = bool(v) and nf == len(v)
        if intact:
            full_fams[tag].append(f)
        print("   %-12s %-6s dose %-7s admitted %d, full-horizon %d  %s"
              % (f, tag, str(dose), len(v), nf, "INTACT" if intact else ""))
print("\nfamilies intact under survival matching: hyperreflexia %s, weakness %s"
      % (full_fams["H"] or "NONE", full_fams["W"] or "NONE"))

KEYS = [("knee at contact", "knee_ic"), ("ankle at 45%", "ank45"),
        ("ankle 40-50% window", "ank4050"), ("ankle at 85%", "ank85"),
        ("ankle peak in swing", "swingpk")]

out = {"survival_by_family": {f: {"admitted": len([d for d in CELLS[f] if d.get("admitted")]),
                                 "full": sum(1 for d in CELLS[f] if d.get("full"))}
                              for f, _ in HY + WK},
       "intact_families": full_fams}

if not full_fams["H"] or not full_fams["W"]:
    print("\nNO ARM CONTRAST IS AVAILABLE UNDER SURVIVAL MATCHING on the main corpus:")
    print("   %s arm has no family in which every admitted seed reaches the horizon."
          % ("the hyperreflexia" if not full_fams["H"] else "the weakness"))
    print("   This is the honest answer to Limitation 2 and it applies to EVERY readout equally:")
    print("   the arms cannot be compared at matched survival here, so no readout can be shown to")
    print("   separate them independently of cells dying. The manuscript already states this for")
    print("   the knee; it is now established that it is a property of the CORPUS, not of the")
    print("   endpoint, and that changing endpoint does not escape it.")
    out["VERDICT"] = ("no arm contrast exists under survival matching on the main corpus, because "
                      "no hyperreflexia family has every admitted seed reaching the horizon. The "
                      "confound is a property of the corpus and is not escaped by changing the "
                      "readout. Any claim that a new endpoint 'escapes Limitation 2' on the "
                      "strength of SWINGSURV_r528 is wrong: that container compares two reflex "
                      "GAINS, not the two arms.")
else:
    print("\narm separation restricted to intact families:")
    print("   %-24s %9s %9s %9s %8s" % ("readout", "hyper", "weak", "cell gap", "disjoint"))
    res = {}
    for nm, k in KEYS:
        hv = [d[k] for f in full_fams["H"] for d in CELLS[f] if d.get("full") and d.get(k) is not None]
        wv = [d[k] for f in full_fams["W"] for d in CELLS[f] if d.get("full") and d.get(k) is not None]
        if not hv or not wv:
            continue
        gap = max(min(wv) - max(hv), min(hv) - max(wv))
        res[nm] = {"hyper_mean": float(np.mean(hv)), "weak_mean": float(np.mean(wv)),
                   "n_hyper": len(hv), "n_weak": len(wv),
                   "cell_gap": gap, "disjoint": bool(gap > 0)}
        print("   %-24s %9.3f %9.3f %9.3f %8s"
              % (nm, np.mean(hv), np.mean(wv), gap, gap > 0))
    out["arm_separation_matched"] = res

io.open(os.path.join(P, "ARMSURV_r538.json"), "w", encoding="utf-8", newline="").write(json.dumps(
    {"id": "ARMSURV_r538",
     "why": ("SWINGSURV_r528 compared two reflex GAINS on survival-matched cells and was described "
             "as settling Limitation 2, which is about the ARM contrast. They are different "
             "questions. This asks the arm question on the main corpus, where pure-weakness cells "
             "exist."),
     "definition": "a family is intact if every one of its admitted cells reaches %.0f s" % FULL,
     **out}, indent=1, ensure_ascii=False))
print("\n-> ARMSURV_r538.json")
