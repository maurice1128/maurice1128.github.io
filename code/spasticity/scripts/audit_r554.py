# -*- coding: utf-8 -*-
"""r554: two code-review findings that bear on published claims, checked rather than accepted.

(1) faller_r544.py gates each directory and then picks the survivor with the most .par files. Gate G
    is t_end >= 9.73 s, so choosing among survivors is choosing on end time, which is the variable
    the faller control exists to neutralise. Every other script picks the directory first and gates
    second. This re-runs the control in the correct order and reports whether n = 17 and the mean of
    9.572 deg survive.

(2) mixedswing_r526.py keeps only the 96 grid pairs at different reflex gains and drops the 24
    same-gain pairs, so the manuscript's "no pair falls within one seed SD" is computed on a
    population from which the confusable pairs were removed. This scores all 120.
"""
import glob, io, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
ART = 0.03581801092876269


def npar(d):
    return len(glob.glob(os.path.join(d, "[0-9]*.par")))


def cell(d):
    st = sorted(glob.glob(os.path.join(d, "*.par.sto")))
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
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    pk = []
    for a, b in w:
        i = np.where(~on[a:b])[0]
        if i.size:
            pk.append(float(np.max(an[a:b][i])))
    if not pk:
        return None
    return {"t_end": float(t[-1]), "peak": float(np.mean(pk))}


def dirs(pattern):
    return [d for d in sorted(glob.glob(os.path.join(RES, pattern))) if os.path.isdir(d)]


def seed_key(d):
    return re.sub(r"\..*$", "", os.path.basename(d))


PATS = ("R276WPF*", "R285BF*", "R287BF*", "R291BF*")
print("(1) the faller control, under both selection orders\n")

# --- order as shipped: gate first, then pick among survivors
a_all = []
for p in PATS:
    for d in dirs(p):
        r = cell(d)
        if r:
            r["key"], r["npar"] = seed_key(d), npar(d)
            a_all.append(r)
best = {}
for r in a_all:
    if r["key"] not in best or r["npar"] > best[r["key"]]["npar"]:
        best[r["key"]] = r
shipped = list(best.values())

# --- correct order: pick the directory per seed FIRST, then gate
cand = {}
for p in PATS:
    for d in dirs(p):
        k = seed_key(d)
        if k not in cand or npar(d) > npar(cand[k]):
            cand[k] = d
fixed, dropped = [], 0
for k, d in cand.items():
    r = cell(d)
    if r:
        r["key"] = k
        fixed.append(r)
    else:
        dropped += 1

hy = {}
for f in HY:
    for d in dirs(f + "_s*"):
        k = seed_key(d)
        if k not in hy or npar(d) > npar(hy[k]):
            hy[k] = d
hyc = [x for x in (cell(d) for d in hy.values()) if x]
BAND = (min(r["t_end"] for r in hyc), max(r["t_end"] for r in hyc))
ctrl = {}
for d in dirs("R151C_s*"):
    k = seed_key(d)
    if k not in ctrl or npar(d) > npar(ctrl[k]):
        ctrl[k] = d
c0 = float(np.mean([x["peak"] for x in (cell(d) for d in ctrl.values()) if x]))

print("   band from the hyperreflexia arm: %.2f to %.2f s;  control %.3f deg" % (BAND + (c0,)))
out1 = {}
for lab, v in (("as shipped (gate, then pick)", shipped), ("corrected (pick, then gate)", fixed)):
    inb = [r for r in v if BAND[0] <= r["t_end"] <= BAND[1]]
    m = float(np.mean([r["peak"] for r in inb]))
    out1[lab] = {"n_admitted": len(v), "n_in_band": len(inb), "peak_mean": m,
                 "vs_control": m - c0, "in_artefact_floors": abs(m - c0) / ART,
                 "peak_min": min(r["peak"] for r in inb), "peak_max": max(r["peak"] for r in inb)}
    print("   %-30s admitted %2d   in band %2d   peak %.3f   vs control %+.3f (%.2f x floor)"
          % (lab, len(v), len(inb), m, m - c0, abs(m - c0) / ART))
print("   directories dropped by the gate under the corrected order: %d" % dropped)

print("\n(2) the mixed grid: all 120 pairs, not the 96 at different gains\n")
M = json.load(io.open(os.path.join(P, "MIXEDSWING_r526.json"), encoding="utf-8"))
cm = M.get("cell_means_swing_df_deg") or M.get("cell_means")
keys = sorted(cm)
FLOOR = 0.0891
pairs = []
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = keys[i], keys[j]
        pairs.append({"a": a, "b": b, "d": abs(float(cm[a]) - float(cm[b])),
                      "same_gain": a.split("_")[-1] == b.split("_")[-1]})
pairs.sort(key=lambda x: x["d"])
diff = [p for p in pairs if not p["same_gain"]]
same = [p for p in pairs if p["same_gain"]]
print("   %d pairs total: %d at different gains, %d at the same gain" % (len(pairs), len(diff), len(same)))
print("   grid floor for this endpoint: %.4f deg" % FLOOR)
print("   closest pair among the 96 reported: %.4f deg  (%s vs %s)"
      % (diff[0]["d"], diff[0]["a"], diff[0]["b"]))
print("   closest pair among all %d:          %.4f deg  (%s vs %s)"
      % (len(pairs), pairs[0]["d"], pairs[0]["a"], pairs[0]["b"]))
below = [p for p in pairs if p["d"] < FLOOR]
print("   pairs below the floor: %d of %d  (all same-gain: %s)"
      % (len(below), len(pairs), all(p["same_gain"] for p in below)))
for p in below[:6]:
    print("      %.4f   %s vs %s   same gain %s" % (p["d"], p["a"], p["b"], p["same_gain"]))

io.open(os.path.join(P, "AUDIT_r554.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "AUDIT_r554",
 "why": ("Two code-review findings bearing on published claims: the faller control selected its run "
         "directory among gate survivors, which is selection on the variable under test; and the "
         "mixed-grid confusability claim was computed on the 96 different-gain pairs only."),
 "faller_selection_order": out1, "band_s": list(BAND), "control_deg": c0,
 "artefact_floor_deg": ART,
 "grid_pairs": {"n_total": len(pairs), "n_different_gain": len(diff), "n_same_gain": len(same),
                "floor_deg": FLOOR,
                "closest_different_gain": diff[0], "closest_overall": pairs[0],
                "n_below_floor": len(below),
                "below_floor_all_same_gain": bool(all(p["same_gain"] for p in below)),
                "below_floor": below[:8]},
}, indent=1, ensure_ascii=False, default=float))
print("\n-> AUDIT_r554.json")
