# -*- coding: utf-8 -*-
"""Replay the registered solution of each r203 speed cell to produce its .sto.

PREREG_3d_speed_r203.md 8.2: the solution evaluated is the FINAL .par written by the
optimisation. `sconecmd -e` writes only .sto, never .par, so replaying cannot disturb the
optimisation record. No optimiser is running (checked before launch).
"""
import os, sys, glob, time, subprocess
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SEEDS = [101, 102, 103, 104, 105, 106]
tags = ["R203%s%s_s%d" % (v, a, s) for v in ("V080", "V105", "V130")
        for a in ("C", "S", "W") for s in SEEDS]
t0 = time.time(); ok = miss = 0
for i, tag in enumerate(tags, 1):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not g:
        print("  MISSING dir %s" % tag); miss += 1; continue
    d = g[0]
    pars = sorted(glob.glob(os.path.join(d, "[0-9]*.par")))
    if not pars:
        print("  NO PAR %s" % tag); miss += 1; continue
    par = pars[-1]
    for old in glob.glob(os.path.join(d, "*.sto")):
        os.remove(old)
    subprocess.run([SCONECMD, "-e", os.path.basename(par)], cwd=d,
                   capture_output=True, timeout=900)
    n = len(glob.glob(os.path.join(d, "*.sto")))
    ok += (n > 0)
    if i % 9 == 0 or n == 0:
        print("[%6.1fs] %2d/54 %-16s par=%-28s sto=%d" %
              (time.time() - t0, i, tag, os.path.basename(par), n), flush=True)
print("\nreplayed %d of %d, %d missing, %.1f s" % (ok, len(tags), miss, time.time() - t0))
