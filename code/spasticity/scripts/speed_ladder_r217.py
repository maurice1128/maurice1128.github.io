# -*- coding: utf-8 -*-
"""PREREG_speed_ladder_r217.md -- achieved speed across the weakness severity ladder.
Read-only. No sconecmd, no optimisation. Formula and window IDENTICAL to speed_gate_r203.py."""
import io, os, glob, json, sys
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S
RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.00, 13.58
SEEDS = range(101, 107)
MIN_DUR, MIN_CYC = 9.73, 5
ARMS = [("spastic KV 0.050", "R151S", None),
        ("weak x0.800", "R151W", 0.800), ("weak x0.870", "R174W870", 0.870),
        ("weak x0.892", "R174W892", 0.892), ("weak x0.900", "R169W090", 0.900),
        ("weak x0.915", "R174W915", 0.915), ("weak x0.950", "R169W095", 0.950)]

def cell(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
    if len(ds) != 1: return None
    sto = sorted(glob.glob(os.path.join(ds[0], "*.par.sto")))
    if not sto: return None
    cols, dat = S.load_sto(sto[-1])
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k+1]) for k in range(len(idx)-1)
           if t[idx[k]] >= SETTLE and t[idx[k+1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc: return None
    a, b = cyc[0][0], cyc[-1][1]
    px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
    full = [(idx[k], idx[k+1]) for k in range(len(idx)-1) if t[idx[k]] >= SETTLE]
    return {"speed": float((px[b-1]-px[a])/(t[b-1]-t[a])),
            "dur": float(t[-1]), "cycles": len(full[:-1] if len(full) >= 2 else full)}

out = {"prereg": "PREREG_speed_ladder_r217.md", "sha256_prefix": "bd2b2443a00467d3",
       "method": "pelvis_tx displacement / elapsed over GRF-delimited window [1.00, 13.58]; "
                 "identical to speed_gate_r203.py", "arms": {}}
print("%-18s %-10s %-46s %s" % ("arm", "admitted", "achieved speed m/s (per seed)", "mean"))
for label, pre, s in ARMS:
    recs, adm = [], 0
    for sd in SEEDS:
        r = cell("%s_s%d" % (pre, sd))
        if r is None: continue
        ok = r["dur"] >= MIN_DUR and r["cycles"] >= MIN_CYC
        adm += ok
        recs.append({"seed": sd, "speed_mps": r["speed"], "dur_s": r["dur"],
                     "cycles": r["cycles"], "gateG_admitted": bool(ok)})
    sp = sorted(r["speed_mps"] for r in recs)
    out["arms"][label] = {"prefix": pre, "tib_ant_scale": s, "n_run": len(recs),
                          "n_gateG_admitted": adm, "per_seed": recs,
                          "mean_speed_mps": float(np.mean(sp)) if sp else None,
                          "min_speed_mps": min(sp) if sp else None,
                          "max_speed_mps": max(sp) if sp else None}
    print("%-18s %-10s %-46s %.4f" % (label, "%d/%d" % (adm, len(recs)),
          " ".join("%.4f" % x for x in sp), np.mean(sp)))
json.dump(out, io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\SPEED_LADDER_r217.json",
                       "w", encoding="utf-8"), indent=1)
print("\ndeposited paper/SPEED_LADDER_r217.json")
