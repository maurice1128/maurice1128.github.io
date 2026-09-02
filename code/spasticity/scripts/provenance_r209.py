# -*- coding: utf-8 -*-
"""PROVENANCE TEST -- does the sconecmd -e replay path reproduce the archived r169 values?

Precondition for PREREG_3d_replication_r209. If replaying the ORIGINAL .par files through the
same path the new cells will use does not return LADDER_RESULT_r169.json's per_cell values, then
the planned comparison is between two PIPELINES, not two seed sets.

Works in scratch copies. The r174/r169 result directories are never written to.
"""
import os, sys, glob, json, shutil, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCR = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\_prov"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.00, 13.58
DEG = 180.0 / np.pi

arch = json.load(open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\LADDER_RESULT_r169.json"))["per_cell"]

def endpoint(sto):
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k+1]) for k in range(len(idx)-1)
           if t[idx[k]] >= SETTLE and t[idx[k+1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    a, b = cyc[0][0], cyc[-1][1]
    l = np.asarray(S.col(cols, dat, "hip_flexion_l"), dtype=float)[a:b]
    r = np.asarray(S.col(cols, dat, "hip_flexion_r"), dtype=float)[a:b]
    d = l - r
    return float(np.mean(d)), float(np.mean(d) * DEG), len(cyc), float(t[-1])

print("=" * 96)
print("PROVENANCE TEST -- replay of the ORIGINAL r169 S050 .par files")
print("=" * 96)
print("%-6s %12s %12s %12s %7s %8s %10s" %
      ("seed", "archived", "replay rad", "replay deg", "ncyc", "t_end", "match?"))
rows, ok = {}, 0
for s in range(101, 107):
    src = [d for d in glob.glob(os.path.join(RES, "R151S_s%d.*" % s)) if os.path.isdir(d)][0]
    w = os.path.join(SCR, "s%d" % s)
    if os.path.isdir(w): shutil.rmtree(w)
    os.makedirs(w)
    for f in os.listdir(src):
        if not f.endswith(".sto"):
            p = os.path.join(src, f)
            (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, os.path.join(w, f))
    par = sorted(glob.glob(os.path.join(w, "[0-9]*.par")))[-1]
    subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=w, capture_output=True, timeout=900)
    st = glob.glob(os.path.join(w, "*.sto"))
    if not st:
        print("%-6d  REPLAY PRODUCED NO .sto" % s); continue
    rad, deg, nc, te = endpoint(st[0])
    a = arch["S050_%d" % s]["hip_flexion_LmR"]
    best = deg if abs(deg - a) < abs(rad - a) else rad
    m = abs(best - a) < 1e-3
    ok += m
    rows["s%d" % s] = {"archived": a, "replay_rad": rad, "replay_deg": deg,
                       "ncyc": nc, "t_end": te, "match": bool(m), "par": os.path.basename(par)}
    print("%-6d %12.6f %12.6f %12.6f %7d %8.2f %10s" % (s, a, rad, deg, nc, te, "YES" if m else "NO"))
print("\nreproduced %d of 6 to 1e-3" % ok)
json.dump(rows, open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\PROVENANCE_r209.json", "w"), indent=1)
shutil.rmtree(SCR, ignore_errors=True)
print("deposited paper/PROVENANCE_r209.json  (scratch removed)")
