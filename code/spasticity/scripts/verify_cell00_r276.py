# -*- coding: utf-8 -*-
"""Independent verification of WEAK-PF cell 0 (R276WPF005_s101).

Purpose: the deposit RUN_WEAKPF_r276_cell00.json records terminal_objective = 20.9748
but NOT the simulated duration. Duration is the quantity the rung-1 FAILURE-DOMINATED
criterion is written against, and the objective->duration map (r ~= -0.998, FITNESS_r266)
was fitted on the spastic/control/dorsiflexor arms only -- applying it to a plantarflexor
weakness arm is extrapolation. This script measures t_end directly.

`sconecmd -e` writes only .sto, never .par, so this cannot disturb the optimisation record
of a cell, and it does not touch any cell outside R276WPF*.

Measured, in the same way the shipped gate measures them (speed_gate_r203.py):
  t_end   -- last time sample in the .sto
  cycles  -- left heel-strike-delimited cycles fully inside [SETTLE, t_end]
  gate G  -- MIN_DUR 9.73 s and MIN_CYC 5, the registered admission test
"""
import os, sys, glob, json, subprocess, time
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE = 1.00
MIN_DUR, MIN_CYC = 9.73, 5
TAG = "R276WPF005_s101"

d = [x for x in glob.glob(os.path.join(RES, TAG + ".*")) if os.path.isdir(x)]
if not d:
    print("MISSING dir %s" % TAG); sys.exit(1)
d = d[0]

pars = sorted(glob.glob(os.path.join(d, "[0-9]*.par")))
par = pars[-1]
print("cell dir : %s" % os.path.basename(d))
print("par      : %s  (%d bytes)" % (os.path.basename(par), os.path.getsize(par)))

sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))
if not sto:
    t0 = time.time()
    r = subprocess.run([SCONECMD, "-e", os.path.basename(par)], cwd=d,
                       capture_output=True, timeout=900)
    print("evaluated in %.1f s, rc=%d" % (time.time() - t0, r.returncode))
    sto = sorted(glob.glob(os.path.join(d, "*.par.sto")))
if not sto:
    print("NO STO PRODUCED"); sys.exit(1)
sto = sto[-1]
print("sto      : %s  (%d bytes)" % (os.path.basename(sto), os.path.getsize(sto)))

cols, dat = S.load_sto(sto)
t = np.asarray(S.col(cols, dat, "time"), dtype=float)
t_end = float(t[-1])

grf, thr = S.grf_vertical(cols, dat, "l")
idx = S.heel_strikes(t, grf, thresh=thr)
cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
       if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= t_end]
n_cyc = len(cyc)

px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
speed = None
if n_cyc >= 2:
    a, b = cyc[0][0], cyc[-1][1]
    speed = float((px[b - 1] - px[a]) / (t[b - 1] - t[a]))

# The extrapolated prediction, recorded so the extrapolation can be judged, not trusted.
obj = 20.9748
t_pred = 20.0 * (1.0 - (obj - 2.9) / 100.0)

out = {
    "purpose": "independent measurement of cell 0 duration; the deposit records only objective",
    "tag": TAG,
    "par": os.path.basename(par),
    "sto": os.path.basename(sto),
    "terminal_objective": obj,
    "t_end_s": t_end,
    "n_cycles_after_settle": n_cyc,
    "settle_s": SETTLE,
    "speed_mps": speed,
    "gateG": {
        "MIN_DUR": MIN_DUR, "MIN_CYC": MIN_CYC,
        "dur_ok": bool(t_end >= MIN_DUR),
        "cyc_ok": bool(n_cyc >= MIN_CYC),
        "admitted": bool(t_end >= MIN_DUR and n_cyc >= MIN_CYC),
    },
    "objective_extrapolation": {
        "formula": "t_end ~= 20 * (1 - (objective - 2.9)/100), FITNESS_r266",
        "fitted_on": "spastic / control / dorsiflexor-weakness arms only",
        "predicted_t_end_s": t_pred,
        "error_s": t_end - t_pred,
        "note": "recorded to judge whether the map transfers to a plantarflexor-weakness arm",
    },
}
p = r"C:\Users\maurice\Desktop\spasticity_paper\paper\VERIFY_CELL00_r276.json"
with open(p, "w") as f:
    json.dump(out, f, indent=1)

print()
print("t_end            = %.3f s" % t_end)
print("cycles (>=%.2fs)  = %d" % (SETTLE, n_cyc))
print("speed            = %s" % ("%.4f m/s" % speed if speed is not None else "undefined"))
print("gate G admitted  = %s  (needs dur>=%.2f, cyc>=%d)" % (out["gateG"]["admitted"], MIN_DUR, MIN_CYC))
print("objective map    : predicted %.3f s, actual %.3f s, error %+.3f s" % (t_pred, t_end, t_end - t_pred))
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
