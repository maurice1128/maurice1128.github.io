# -*- coding: utf-8 -*-
"""Achieved speed vs GENERATION for the depth probe. Replays into a full scratch copy."""
import os, sys, glob, json, shutil, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCR = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\_curve3"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.00, 13.58
def speed_of(sto):
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k+1]) for k in range(len(idx)-1)
           if t[idx[k]] >= SETTLE and t[idx[k+1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc: return None
    a, b = cyc[0][0], cyc[-1][1]
    px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
    return float((px[b-1]-px[a])/(t[b-1]-t[a]))
out = {}
for tag in ("R208D270_s101", "R208D270_s102"):
    src = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)][0]
    w = os.path.join(SCR, tag)
    if os.path.isdir(w): shutil.rmtree(w)
    os.makedirs(w)
    for f in os.listdir(src):
        if not f.endswith(".sto"):
            s = os.path.join(src, f)
            (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, os.path.join(w, f))
    pars = sorted(glob.glob(os.path.join(w, "[0-9]*.par")))
    keep = [pars[0]] + pars[1::max(1, len(pars)//10)] + [pars[-1]]
    seen, rows = set(), []
    for p in keep:
        g = int(os.path.basename(p)[:4])
        if g in seen: continue
        seen.add(g)
        for old in glob.glob(os.path.join(w, "*.sto")): os.remove(old)
        subprocess.run([SCONE, "-e", os.path.basename(p)], cwd=w, capture_output=True, timeout=900)
        st = glob.glob(os.path.join(w, "*.sto"))
        rows.append({"gen": g, "speed": speed_of(st[0]) if st else None})
    out[tag] = sorted(rows, key=lambda r: r["gen"])
    print("%s  (%d checkpoints on disk, %d sampled)" % (tag, len(pars), len(rows)))
    for r in out[tag]:
        print("   gen %3d   %s" % (r["gen"], ("%.4f m/s" % r["speed"]) if r["speed"] else "n/a"))
json.dump(out, open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\SPEEDCURVE_r208.json","w"), indent=1)
shutil.rmtree(SCR, ignore_errors=True)
print("\ndeposited paper/SPEEDCURVE_r208.json")
