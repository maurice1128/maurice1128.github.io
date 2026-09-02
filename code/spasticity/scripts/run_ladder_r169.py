# -*- coding: utf-8 -*-
"""Run the 24 NEW cells of PREREG_3d_ladder_r169.md
   sha256 e3ec76aa98759c821ef410889d3fc5d2840297bfc93482e00efc85e244e6d703

Each is an OPTIMISATION -- sconecmd -o <scenario> -q, NOT -e, and NOT --run/--launch.
Concurrency 2 (project standing convention, 2 of 16 cores; section 7 forbids raising it).

Section 8: a cell is COMPLETE iff its history.txt has >= 91 lines. Progress is counted from
history.txt line counts and from file mtimes -- NEVER from LAUNCH_STATUS.json, which reports
healthy after the process writing it has died and has cost this project three times.

The 18 reused r151 cells are NOT re-run: build_ladder_r169.py verified them byte-identical.
The 112 protected directories are never touched; on any resource conflict our cells yield.
"""
import io
import os
import sys
import glob
import json
import time
import subprocess

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141\ladder_r169"
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
LOG = os.path.join(ROOT, "run_log.json")
PROG = os.path.join(ROOT, "progress.json")
CONC = 2

man = json.load(io.open(os.path.join(ROOT, "BUILD_MANIFEST.json"), encoding="utf-8"))
NEW = set(man["new_tags"])


def complete(tag):
    """SCONE appends ' (1)' rather than overwriting -- the G5 hazard the 2D study registered."""
    for d in glob.glob(os.path.join(RESULTS, tag + ".*")):
        h = os.path.join(d, "history.txt")
        if os.path.exists(h) and sum(1 for _ in io.open(h, errors="replace")) >= 91:
            return True
    return False


def gens(tag):
    """Generations done so far, from history.txt line count. Never from LAUNCH_STATUS.json."""
    best = 0
    for d in glob.glob(os.path.join(RESULTS, tag + ".*")):
        h = os.path.join(d, "history.txt")
        if os.path.exists(h):
            best = max(best, max(0, sum(1 for _ in io.open(h, errors="replace")) - 1))
    return best


scen = sorted(c for c in glob.glob(os.path.join(ROOT, "*", "config.scone"))
              if os.path.basename(os.path.dirname(c)) in NEW)
done_already = [c for c in scen if complete(os.path.basename(os.path.dirname(c)))]
scen = [c for c in scen if c not in done_already]

print("ladder r169: %d new cells, %d already complete, %d to run, concurrency %d"
      % (len(NEW), len(done_already), len(scen), CONC), flush=True)

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
        print("[%7.1fs] start %s" % (time.time() - t0, tag), flush=True)
    time.sleep(5)
    for r in list(running):
        tag, p, st = r
        if p.poll() is not None:
            running.remove(r)
            done.append({"tag": tag, "rc": p.returncode, "secs": round(time.time() - st, 1),
                         "gens": gens(tag)})
            print("[%7.1fs] done  %-16s rc=%d %7.1fs  gens=%d  (%d/%d)"
                  % (time.time() - t0, tag, p.returncode, time.time() - st, gens(tag),
                     len(done), len(NEW) - len(done_already)), flush=True)
    json.dump({"elapsed_s": round(time.time() - t0, 1),
               "running": [t for t, _, _ in running],
               "done": done,
               "gens_by_tag": {t: gens(t) for t in sorted(NEW)}},
              io.open(PROG, "w", encoding="utf-8"), indent=1)

el = time.time() - t0
json.dump({"prereg_sha256": "e3ec76aa98759c821ef410889d3fc5d2840297bfc93482e00efc85e244e6d703",
           "elapsed_s": round(el, 1), "concurrency": CONC,
           "skipped_complete": [os.path.basename(os.path.dirname(c)) for c in done_already],
           "runs": done},
          io.open(LOG, "w", encoding="utf-8"), indent=1)
print("\ntotal %.1f s (%.1f min) for %d runs" % (el, el / 60, len(done)), flush=True)
bad = [d for d in done if d["rc"] != 0 or d["gens"] < 90]
print("nonzero rc or short history: %r" % bad, flush=True)
