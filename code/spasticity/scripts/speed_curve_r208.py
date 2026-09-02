# -*- coding: utf-8 -*-
"""Achieved speed vs GENERATION, from checkpoints already on disk. No new simulation.

Replays into a scratch copy so the registered r203 result directories are never written to.
"""
import os, sys, glob, json, shutil, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCRATCH = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\_curve_scratch"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.00, 13.58


def speed_of(d, sto):
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc:
        return None, 0
    a, b = cyc[0][0], cyc[-1][1]
    px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
    return float((px[b - 1] - px[a]) / (t[b - 1] - t[a])), len(cyc)


out = {}
for tag in ("R203V130C_s101", "R203V130C_s102"):
    src = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)][0]
    pars = sorted(glob.glob(os.path.join(src, "[0-9]*.par")))
    w = os.path.join(SCRATCH, tag)
    if os.path.isdir(w):
        shutil.rmtree(w)
    os.makedirs(w)
    for f in ("config.scone", "H1922v7b3.hfd", "InitStateH0918Gait10ActA.zml"):
        shutil.copy2(os.path.join(src, f), os.path.join(w, f))
    rows = []
    for p in pars:
        gen = int(os.path.basename(p)[:4])
        shutil.copy2(p, os.path.join(w, os.path.basename(p)))
        for old in glob.glob(os.path.join(w, "*.sto")):
            os.remove(old)
        subprocess.run([SCONE, "-e", os.path.basename(p)], cwd=w,
                       capture_output=True, timeout=900)
        stos = glob.glob(os.path.join(w, "*.sto"))
        if not stos:
            rows.append({"gen": gen, "speed": None}); continue
        v, nc = speed_of(w, stos[0])
        rows.append({"gen": gen, "speed": v, "ncyc": nc})
    out[tag] = rows
    print("%s:" % tag)
    for r in rows:
        print("   gen %3d   achieved %s" % (r["gen"], "%.4f m/s" % r["speed"] if r["speed"] else "n/a"))
json.dump(out, open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\SPEEDCURVE_r208.json", "w"), indent=1)
shutil.rmtree(SCRATCH, ignore_errors=True)
print("\ndeposited: paper/SPEEDCURVE_r208.json  (scratch removed)")
