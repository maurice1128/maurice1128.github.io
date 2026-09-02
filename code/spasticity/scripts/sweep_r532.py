# -*- coding: utf-8 -*-
"""r532: over the whole gait cycle and all three sagittal joints, which readout apportions best?

Every endpoint this project has scored was chosen first and scored second. The contact instant was
chosen because that is where the clinical literature looks; peak swing dorsiflexion surfaced because
it happened to be the largest effect. Neither was the answer to 'which readout is best', because
that question was never asked of the whole cycle.

The criterion is not effect size. Apportioning two lesions requires a readout that responds to BOTH,
in OPPOSITE directions from the unlesioned control -- otherwise it grades one lesion and is silent
about the other, which is what peak swing dorsiflexion does (SWINGDF_r525: weakness sits 0.43 deg
from control, inside the noise). So each candidate is scored on three things in order:

  (1) TWO-SIDED: the two arms are displaced from control in opposite directions, and each
      displacement clears twice that candidate's own within-cell seed SD. Fails -> not an
      apportionment readout, whatever its effect size.
  (2) SEPARATING: the two arms' cells do not overlap.
  (3) MEASURABLE: the arm difference, expressed against that candidate's own noise, and flagged
      for whether it is a point readout (noise averages) or a peak (noise rectifies upward).

About 80 candidates are scanned and all are reported, not only the winner.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)
CTRL = ["R151C"]
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]
JOINTS = ["knee_angle_l", "ankle_angle_l", "hip_flexion_l"]
NICE = {"knee_angle_l": "knee", "ankle_angle_l": "ankle", "hip_flexion_l": "hip"}
GRID = list(range(0, 101, 5))


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
    for j in JOINTS:
        try:
            y = np.degrees(S.col(c, dat, j))
        except Exception:
            continue
        curves, sw, stn, tof = [], [], [], []
        for a, b in w:
            seg = y[a:b]
            curves.append(np.interp(np.linspace(0, 100, 101),
                                    np.linspace(0, 100, len(seg)), seg))
            st_on = on[a:b]
            idx = np.where(~st_on)[0]
            if idx.size:
                sw.append((float(np.max(seg[idx])), float(np.min(seg[idx]))))
                tof.append(float(seg[idx[0]]))
            idx2 = np.where(st_on)[0]
            if idx2.size:
                stn.append((float(np.max(seg[idx2])), float(np.min(seg[idx2]))))
        cur = np.mean(curves, axis=0)
        out[j] = {"curve": cur.tolist(),
                  "swing_max": float(np.mean([x[0] for x in sw])) if sw else None,
                  "swing_min": float(np.mean([x[1] for x in sw])) if sw else None,
                  "stance_max": float(np.mean([x[0] for x in stn])) if stn else None,
                  "stance_min": float(np.mean([x[1] for x in stn])) if stn else None,
                  "toe_off": float(np.mean(tof)) if tof else None,
                  "rom": float(np.mean([c.max() - c.min() for c in curves]))}
    return out


print("loading corpus ...")
CELLS = {}
for f in CTRL + HY + WK:
    v = []
    for sd in SEEDS:
        r = load(f, sd)
        if r:
            v.append(r)
    CELLS[f] = v
    print("   %-12s n=%d" % (f, len(v)))

# ---- build the candidate list ------------------------------------------------------------------
CAND = []
for j in JOINTS:
    for p in GRID:
        CAND.append({"name": "%s at %d%% of cycle" % (NICE[j], p), "joint": j,
                     "kind": "point", "get": lambda d, j=j, p=p: d[j]["curve"][p]})
    for k, lab, kind in (("swing_max", "peak in swing", "peak"),
                         ("swing_min", "trough in swing", "peak"),
                         ("stance_max", "peak in stance", "peak"),
                         ("stance_min", "trough in stance", "peak"),
                         ("toe_off", "at toe-off", "point"),
                         ("rom", "range of motion", "peak")):
        CAND.append({"name": "%s %s" % (NICE[j], lab), "joint": j, "kind": kind,
                     "get": lambda d, j=j, k=k: d[j][k]})
print("\ncandidates scanned: %d" % len(CAND))


def vals(fams, g):
    out = []
    for f in fams:
        for d in CELLS[f]:
            try:
                v = g(d)
            except Exception:
                v = None
            if v is not None:
                out.append((f, float(v)))
    return out


rows = []
for cd in CAND:
    ct = vals(CTRL, cd["get"])
    hv = vals(HY, cd["get"])
    wv = vals(WK, cd["get"])
    if len(ct) < 3 or len(hv) < 8 or len(wv) < 8:
        continue
    sds = []
    for f in HY + WK:
        x = [v for g, v in hv + wv if g == f]
        if len(x) >= 2:
            sds.append(float(np.std(x, ddof=1)))
    sd = float(np.mean(sds)) if sds else float("nan")
    c0 = float(np.mean([v for _, v in ct]))
    h0 = float(np.mean([v for _, v in hv]))
    w0 = float(np.mean([v for _, v in wv]))
    dh, dw = h0 - c0, w0 - c0
    two = (dh * dw < 0) and abs(dh) > 2 * sd and abs(dw) > 2 * sd
    hvv = [v for _, v in hv]
    wvv = [v for _, v in wv]
    gap = max(min(wvv) - max(hvv), min(hvv) - max(wvv))
    rows.append({"name": cd["name"], "joint": NICE[cd["joint"]], "kind": cd["kind"],
                 "control": c0, "weakness": w0, "hyperreflexia": h0,
                 "disp_weak": dw, "disp_hyper": dh,
                 "disp_weak_in_seed_SD": dw / sd, "disp_hyper_in_seed_SD": dh / sd,
                 "two_sided": bool(two),
                 "arm_difference": w0 - h0, "cell_gap": gap, "disjoint": bool(gap > 0),
                 "seed_SD": sd, "gap_in_seed_SD": gap / sd,
                 "effect_in_seed_SD": abs(w0 - h0) / sd})

two = [r for r in rows if r["two_sided"]]
tsd = [r for r in two if r["disjoint"]]
print("\n%d of %d candidates are TWO-SIDED (both arms displaced from control, opposite directions, "
      "each clearing 2 seed SD)" % (len(two), len(rows)))
print("%d of those also separate the cells completely" % len(tsd))

print("\nTWO-SIDED AND SEPARATING, ranked by gap in seed SD:")
print("%-30s %-6s %8s %8s %8s %9s %9s %8s"
      % ("readout", "kind", "ctrl", "weak", "hyper", "armdiff", "cellgap", "gap/SD"))
for r in sorted(tsd, key=lambda x: -x["gap_in_seed_SD"])[:18]:
    print("%-30s %-6s %8.3f %8.3f %8.3f %9.3f %9.3f %8.2f"
          % (r["name"], r["kind"], r["control"], r["weakness"], r["hyperreflexia"],
             r["arm_difference"], r["cell_gap"], r["gap_in_seed_SD"]))

print("\nfor reference, the largest effects that are NOT two-sided (they grade one lesion only):")
one = sorted([r for r in rows if not r["two_sided"]], key=lambda x: -abs(x["arm_difference"]))[:8]
print("%-30s %8s %8s %8s %11s %11s"
      % ("readout", "ctrl", "weak", "hyper", "disp weak", "disp hyper"))
for r in one:
    print("%-30s %8.3f %8.3f %8.3f %8.3f/%.1f %8.3f/%.1f"
          % (r["name"], r["control"], r["weakness"], r["hyperreflexia"],
             r["disp_weak"], r["disp_weak_in_seed_SD"], r["disp_hyper"], r["disp_hyper_in_seed_SD"]))

cur = [r for r in rows if r["name"] == "knee at 0% of cycle"]
print("\nthe manuscript's current endpoint (knee at contact) sits at:")
for r in rows:
    if r["name"] in ("knee at 0% of cycle", "ankle at 0% of cycle", "ankle peak in swing"):
        print("   %-28s two-sided %-5s disjoint %-5s gap/SD %6.2f  disp w/h %+.2f/%+.2f seed SD"
              % (r["name"], r["two_sided"], r["disjoint"], r["gap_in_seed_SD"],
                 r["disp_weak_in_seed_SD"], r["disp_hyper_in_seed_SD"]))

dep = {
 "id": "SWEEP_r532",
 "why": ("Every endpoint scored in this project was chosen first and scored second. This asks the "
         "question of the whole cycle and all three sagittal joints at once, under a criterion that "
         "encodes what apportionment actually requires: a readout that responds to both lesions in "
         "opposite directions, not the largest effect."),
 "criterion": {
    "two_sided": "sign(weakness - control) opposite to sign(hyperreflexia - control), AND each "
                 "displacement exceeds twice that candidate's own within-cell seed SD",
    "separating": "the two arms' cells do not overlap",
    "note": "a peak readout rectifies measurement noise upward where a point readout averages it, "
            "so 'kind' is reported and matters for the motion-capture step"},
 "n_candidates": len(rows), "n_two_sided": len(two), "n_two_sided_and_separating": len(tsd),
 "MULTIPLICITY": ("about 80 candidates were scanned and all are recorded in this container. Any "
                  "single winner is the maximum of that scan and must be reported as such; the "
                  "statement that does not depend on selection is how many candidates satisfy the "
                  "two-sided criterion at all."),
 "all_candidates": rows,
}
io.open(os.path.join(P, "SWEEP_r532.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWEEP_r532.json")
