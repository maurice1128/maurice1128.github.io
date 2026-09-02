# -*- coding: utf-8 -*-
"""Run the 18 re-optimised arms, concurrency 2 (project standing convention).

Each is an OPTIMISATION -- sconecmd on the scenario, NOT -e. Results land in
SCONE/results/<signature_prefix>.*; the 112 protected directories are never
touched and our runs yield.
"""
import os, sys, time, json, subprocess, glob, io

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\reopt_r151"
LOG = os.path.join(ROOT, "run_log.json")
CONC = 2

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"


def already_done(tag):
    """SCONE appends ' (1)' rather than overwriting -- the G5 hazard the 2D study
    registered, with 43 such directories already on disk. Skip anything complete."""
    for d in glob.glob(os.path.join(RESULTS, tag + ".*")):
        h = os.path.join(d, "history.txt")
        if os.path.exists(h) and sum(1 for _ in io.open(h, errors="replace")) >= 91:
            return True
    return False


scen = sorted(glob.glob(os.path.join(ROOT, "R151*", "config.scone")))
skipped = [c for c in scen if already_done(os.path.basename(os.path.dirname(c)))]
scen = [c for c in scen if c not in skipped]
print("scenarios: %d to run, %d already complete, concurrency %d"
      % (len(scen), len(skipped), CONC))
for c in skipped:
    print("  skip (complete): %s" % os.path.basename(os.path.dirname(c)))
t0 = time.time()
running, done = [], []

while scen or running:
    while scen and len(running) < CONC:
        c = scen.pop(0)
        tag = os.path.basename(os.path.dirname(c))
        p = subprocess.Popen([SCONE, "-o", c, "-q"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                             cwd=os.path.dirname(c))
        running.append((tag, p, time.time()))
        print("[%6.1fs] start %s" % (time.time() - t0, tag), flush=True)
    time.sleep(2)
    for r in list(running):
        tag, p, st = r
        if p.poll() is not None:
            running.remove(r)
            done.append({"tag": tag, "rc": p.returncode, "secs": round(time.time() - st, 1)})
            print("[%6.1fs] done  %-14s rc=%d  %.1fs"
                  % (time.time() - t0, tag, p.returncode, time.time() - st), flush=True)

el = time.time() - t0
json.dump({"elapsed_s": round(el, 1), "runs": done},
          io.open(LOG, "w", encoding="utf-8"), indent=1)
print("\ntotal %.1f s (%.1f min) for %d runs" % (el, el / 60, len(done)))
print("nonzero rc: %r" % [d for d in done if d["rc"] != 0])
