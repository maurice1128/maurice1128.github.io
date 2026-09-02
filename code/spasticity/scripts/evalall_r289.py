# -*- coding: utf-8 -*-
"""Evaluate every landed r289 matched-completion cell to .sto so the analyses can read it.

`sconecmd -e` writes only .sto, never .par, so this cannot disturb an optimisation record.
Only R289KV* directories are touched. Cells that already have a .sto are skipped.
"""
import os, sys, glob, json, time, subprocess

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"

t0 = time.time()
done = skipped = failed = 0
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_MATCHED20_r289_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    if not os.path.isdir(d):
        print("  missing dir  %s" % dep["prefix"]); failed += 1; continue
    if glob.glob(os.path.join(d, "*.par.sto")):
        skipped += 1; continue
    r = subprocess.run([SCONECMD, "-e", dep["resolved_par"]], cwd=d,
                       capture_output=True, timeout=900)
    n = len(glob.glob(os.path.join(d, "*.par.sto")))
    print("  [%6.1fs] cell %2d  f=%.2f s%d  rc=%d  sto=%d"
          % (time.time() - t0, dep["cell"], dep["f"], dep["seed"], r.returncode, n), flush=True)
    done += n > 0
    failed += n == 0
print("\nevaluated %d, already had one %d, failed %d, %.1f s" % (done, skipped, failed, time.time() - t0))
