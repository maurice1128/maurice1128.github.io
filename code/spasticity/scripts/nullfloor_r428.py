# -*- coding: utf-8 -*-
"""r428: a batch-null floor for EVERY endpoint any mechanism claim in this corpus rests on.

WHY. KNEE_MDC_BATCHNULL_r399.json built a same-mechanism null for ONE endpoint, knee angle at
heel strike (0.5697 deg). Every other endpoint used in a mechanism claim -- ankle angle, hip
angle, gastrocnemius MTU length, gastrocnemius activation, terminal-swing knee torque -- has NO
noise floor at all. Numbers on those endpoints have been reported with nothing to read them
against, which is how CORRECTION_r427 happened.

METHOD, identical to r399's. Take families that share a MECHANISM but differ only in lineage or
severity within the same lesion type. Any edge gap between two such families is noise by
construction: they are the same disease. The largest such gap is the floor an inter-mechanism
claim must beat.

NO SIMULATION. Reads .sto files already on disk.
"""
import glob
import io
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\NULL_FLOORS_r428.json"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

# same-mechanism families. Within a group every pair is a null pair.
GROUPS = {
    "dorsiflexor_weakness": ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"],
    "spastic_plantarflexor": ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"],
}


def measure(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    if len(g) > 1:
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    cols, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    if float(t[-1]) < T1 or len(win) < 5:
        return None
    on = grf > thr
    stance = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    # terminal swing = last 15% of each cycle, the r408 convention
    tsw = np.concatenate([np.arange(a + int(0.85 * (b - a)), b) for a, b in win])

    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    an = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    hp = np.degrees(S.col(cols, dat, "hip_flexion_l"))
    out = {
        "KNEE_ic_deg": float(np.mean([kn[a] for a, _ in win])),
        "ANKLE_st_deg": float(np.mean(an[stance])),
        "HIP_ic_deg": float(np.mean([hp[a] for a, _ in win])),
        "KNEE_sw_min_deg": float(np.mean([np.min(kn[a:b]) for a, b in win])),
        "t_end_s": float(t[-1]),
    }
    for nm, col in (("GASLEN_norm", "gastroc_l.L"), ("SOLLEN_norm", "soleus_l.L"),
                    ("GASDRIVE", "gastroc_l.activation"), ("SOLDRIVE", "soleus_l.activation"),
                    ("TALEN_norm", "tib_ant_l.L"), ("TADRIVE", "tib_ant_l.activation")):
        try:
            v = S.col(cols, dat, col)
        except Exception:
            continue
        out[nm + "_swing"] = float(np.mean(v[tsw]))
        out[nm + "_stance"] = float(np.mean(v[stance]))
    try:
        ktq = S.col(cols, dat, "knee_l.torque")
        out["KTQ_tsw"] = float(np.mean(ktq[tsw]))
    except Exception:
        pass
    return out


def family(prefixes):
    out = {}
    for f in prefixes:
        cells = [measure("%s_s%d" % (f, s)) for s in SEEDS]
        cells = [c for c in cells if c]
        if len(cells) >= 4:
            out[f] = cells
    return out


def edge_gap(a, b):
    """signed nearest-edge gap; 0 when the two ranges overlap."""
    alo, ahi = min(a), max(a)
    blo, bhi = min(b), max(b)
    if ahi < blo:
        return blo - ahi
    if bhi < alo:
        return -(alo - bhi)
    return 0.0


res = {"round": "NULL_FLOORS_r428", "no_simulation_run": True,
       "method": "identical to KNEE_MDC_BATCHNULL_r399: the largest edge gap between two families "
                 "that share a MECHANISM is noise by construction, and is the floor any "
                 "between-mechanism claim on that endpoint must beat.",
       "window": "SETTLE 1.00 s, T1 9.73 s, cycles wholly inside, last kept cycle dropped, >= 5 "
                 "required, stance = leg0_l.grf_norm_y > 0.05, terminal swing = last 15%",
       "groups": {}, "floors": {}}

fams = {}
for gname, prefixes in GROUPS.items():
    f = family(prefixes)
    fams[gname] = f
    res["groups"][gname] = {k: {"n": len(v)} for k, v in f.items()}
    print("%-24s %d families with >= 4 Gate-G cells: %s"
          % (gname, len(f), ", ".join("%s(%d)" % (k, len(v)) for k, v in f.items())))

keys = sorted({k for g in fams.values() for cs in g.values() for c in cs for k in c})
print()
print("%-24s %-10s %-10s %-9s %s" % ("endpoint", "n_pairs", "largest", "median", "which pair"))
for key in keys:
    pairs = []
    for gname, f in fams.items():
        names = sorted(f)
        for a, b in itertools.combinations(names, 2):
            va = [c[key] for c in f[a] if key in c]
            vb = [c[key] for c in f[b] if key in c]
            if len(va) >= 4 and len(vb) >= 4:
                pairs.append((abs(edge_gap(va, vb)), "%s|%s" % (a, b), gname))
    if not pairs:
        continue
    pairs.sort(reverse=True)
    res["floors"][key] = {
        "n_pairs": len(pairs), "largest_null_edge_gap": pairs[0][0],
        "largest_pair": pairs[0][1], "group": pairs[0][2],
        "median_null_edge_gap": float(np.median([p[0] for p in pairs])),
        "n_pairs_with_nonzero_gap": sum(1 for p in pairs if p[0] > 0),
        "separation_rate": sum(1 for p in pairs if p[0] > 0) / len(pairs)}
    print("  %-22s %-10d %-10.5f %-9.5f %s"
          % (key, len(pairs), pairs[0][0], np.median([p[0] for p in pairs]), pairs[0][1]))

res["cross_check_against_r399"] = {
    "r399_knee_floor_deg": 0.5697331886598267,
    "r428_KNEE_ic_floor_deg": res["floors"].get("KNEE_ic_deg", {}).get("largest_null_edge_gap"),
    "note": "r399 used only the dorsiflexor-weakness families; r428 pools weakness AND spastic "
            "families, so its floor is expected to be at least as large. The LARGER value is the "
            "one a claim must beat."}
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("r399 knee floor %.5f   r428 knee floor %s"
      % (0.5697331886598267, res["cross_check_against_r399"]["r428_KNEE_ic_floor_deg"]))
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
