# -*- coding: utf-8 -*-
"""Build and run the 18 severity-matched weak cells of PREREG_3d_matched_r174.md
   sha256 3d62010f81bc5a62721b522432ea77756566d7bf2d6ff1182b9fd472e8d038d1
   hashed BEFORE this file was written and before any scenario existed.

Where this script and that registration disagree, THE REGISTRATION DECIDES.

DESIGN (section 3): spasticity FIXED at KV 0.050 (reused, R151S, not re-run). Weak arm at
tib_ant_l x {0.870, 0.892, 0.915} -- upstream doses 16.361 / 13.592 / 10.698 N against the
spastic 13.627 N. All FROM-HEALTHY, depth 90, so both arms are depth-matched by construction.

SECTION 7 -- THE section 74 FIX. There is no chain here, so nothing advances and the
control-flow defect is structurally absent. The runner nevertheless evaluates GATE G before
reporting any cell as usable, so optimiser completion is never printed as survival. Reaching
90 generations is not surviving: r169's S150 cells all reached 90 and fell in under 8 s.

No --run. No --launch. Progress from history.txt line counts only.
"""
import io
import os
import re
import sys
import glob
import json
import time
import shutil
import subprocess

HERE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
sys.path.insert(0, HERE)
import gen_seeds as GS

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.join(HERE, "probe3d_r141")
ROOT = os.path.join(BASE, "matched_r174")
TEMPLATE = os.path.join(BASE, "timing3d", "config.scone")
SRC = os.path.join(BASE, "bench_D20")
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HFD, ZML = "H1922v7b3.hfd", "InitStateH0918Gait10ActA.zml"
PARREL = os.path.join("par", "H1922v7b3-TSG3Dv8g-989_fixed2.par")
SEEDS = [101, 102, 103, 104, 105, 106]
TA_BASE = 1759.0
CONC = 2
MIN_DUR, MIN_CYC, SETTLE = 9.73, 5, 1.0
PREREG = "3d62010f81bc5a62721b522432ea77756566d7bf2d6ff1182b9fd472e8d038d1"

RUNGS = [("R174W870", 0.870, 16.361),
         ("R174W892", 0.892, 13.592),
         ("R174W915", 0.915, 10.698)]


def edit_tib_ant_l(path, scale):
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines(True)
    i = next(k for k, ln in enumerate(lines) if ln.strip() == "name = tib_ant_l")
    j = next(k for k in range(i, len(lines)) if "max_isometric_force" in lines[k])
    lines[j] = lines[j][:lines[j].index("=") + 1] + (" %.1f\n" % (TA_BASE * scale))
    io.open(path, "w", encoding="utf-8", newline="").write("".join(lines))
    return lines[j].strip()


def line_diff(a, b):
    x = io.open(a, encoding="utf-8").read().splitlines()
    y = io.open(b, encoding="utf-8").read().splitlines()
    return [k for k in range(min(len(x), len(y))) if x[k] != y[k]], len(x) == len(y)


def hist_lines(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def result_dir(tag):
    good = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*"))
            if os.path.isdir(d) and hist_lines(d) >= 91]
    if len(good) > 1:
        raise SystemExit("tag %s resolves to %d complete directories; refusing" % (tag, len(good)))
    return good[0] if good else None


# ------------------------------------------------------------------ build
if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
tmpl = io.open(TEMPLATE, encoding="utf-8", newline="").read()
manifest = []
print("=" * 92)
print("BUILD -- PREREG_3d_matched_r174.md %s..." % PREREG[:16])
print("=" * 92)
for prefix, scale, dose in RUNGS:
    for s in SEEDS:
        tag = "%s_s%d" % (prefix, s)
        d = os.path.join(ROOT, tag)
        os.makedirs(os.path.join(d, "par"))
        shutil.copy2(os.path.join(SRC, HFD), os.path.join(d, HFD))
        shutil.copy2(os.path.join(SRC, ZML), os.path.join(d, ZML))
        shutil.copy2(os.path.join(SRC, PARREL), os.path.join(d, PARREL))
        txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, tmpl, count=1)
        assert "SpasticL" not in txt, "%s: weak arm must carry no reflex block" % tag
        txt = GS.set_seed(txt, s)
        cp = os.path.join(d, "config.scone")
        io.open(cp, "w", encoding="utf-8", newline="").write(txt)
        taline = edit_tib_ant_l(os.path.join(d, HFD), scale)
        diffs, samelen = line_diff(os.path.join(SRC, HFD), os.path.join(d, HFD))
        assert samelen and len(diffs) == 1, "%s: model must differ in exactly 1 line, got %r" % (tag, diffs)
        t2 = io.open(cp, encoding="utf-8").read()
        assert GS.read_seed(t2) == s and "max_generations = 90" in t2
        manifest.append({"tag": tag, "scale": scale, "dose_N": dose, "seed": s,
                         "ta_line": taline, "warm_start": "from-healthy, depth 90"})
    print("  %-10s x%.3f  dose %6.3f N  6 cells  %s" % (prefix, scale, dose, taline))
json.dump({"prereg_sha256": PREREG, "cells": manifest},
          io.open(os.path.join(ROOT, "BUILD_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("  built %d cells; every model differs from control in exactly one line" % len(manifest))

# ------------------------------------------------------------------ run
scen = [os.path.join(ROOT, m["tag"], "config.scone") for m in manifest
        if result_dir(m["tag"]) is None]
print("\n%d to run, %d already complete, concurrency %d"
      % (len(scen), len(manifest) - len(scen), CONC))
t0, running, done = time.time(), [], []
while scen or running:
    while scen and len(running) < CONC:
        c = scen.pop(0)
        tag = os.path.basename(os.path.dirname(c))
        p = subprocess.Popen([SCONE, "-o", c, "-q"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT, cwd=os.path.dirname(c))
        running.append((tag, p, time.time()))
        print("[%7.1fs] start %s" % (time.time() - t0, tag), flush=True)
    time.sleep(5)
    for r in list(running):
        tag, p, st = r
        if p.poll() is None:
            continue
        running.remove(r)
        rd = result_dir(tag)
        gens = (hist_lines(rd) - 1) if rd else 0
        done.append({"tag": tag, "rc": p.returncode, "secs": round(time.time() - st, 1),
                     "gens": gens})
        # section 7: completion is NOT survival, and this line must not imply it
        print("[%7.1fs] optimiser finished %-14s rc=%d %6.1fs gens=%d  (Gate G NOT yet evaluated)"
              % (time.time() - t0, tag, p.returncode, time.time() - st, gens), flush=True)
    json.dump({"elapsed_s": round(time.time() - t0, 1), "done": done,
               "running": [t for t, _, _ in running]},
              io.open(os.path.join(ROOT, "PROGRESS.json"), "w", encoding="utf-8"), indent=1)

el = time.time() - t0
json.dump({"prereg_sha256": PREREG, "elapsed_s": round(el, 1), "concurrency": CONC,
           "cells": manifest, "runs": done},
          io.open(os.path.join(ROOT, "RUN_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("\ntotal %.1f s (%.1f min), %d cells" % (el, el / 60, len(done)))
print("⛔ Gate G is evaluated by the analysis script, not here. Reaching 90 generations is not")
print("   surviving: r169's S150 cells all reached 90 and fell in under 8 s.")
