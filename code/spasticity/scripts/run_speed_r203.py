# -*- coding: utf-8 -*-
"""PREREG_3d_speed_r203.md -- 54 cells: 3 speeds x 3 arms x 6 seeds.

Registration sha256 2a939305b25ec234ec3a9ceaf2ebbd073345cd005d73b316485c4724f9f7ea09,
hashed and frozen BEFORE this file was written and before any scenario existed.

ARMS, and where each comes from:
  control  timing3d/config.scone                          -- unmodified base
  spastic  bench_D20_spasL/config.scone + max_generations  -- CERTIFIED post-fix SpasticL block,
           legs = left, target soleus/gastroc unsuffixed, KV = 0.050 FIXED (not a free parameter).
           Defect #49's doubling is absent from this form; it was verified 2026-07-27 at
           K_hat/K_declared = 0.9975.  bench_D20_spasL lacks `max_generations`, and running the
           spastic arm at a different depth would rebuild r169's depth confound, so it is added.
  weak     timing3d/config.scone + tib_ant_l x0.892 in the .hfd  -- one model line

SPEED is GaitMeasure/min_velocity: 0.80, 1.05, 1.30.  Nothing else varies with speed.

EVERY built scenario is diffed against its own template before anything is launched, and the
run aborts if any cell differs in more than the intended lines.
"""
import io
import os
import re
import sys
import glob
import json
import time
import shutil
import difflib
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_seeds as GS

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.join(HERE, "probe3d_r141")
ROOT = os.path.join(BASE, "speed_r203")
T_CTRL = os.path.join(BASE, "timing3d", "config.scone")
T_SPAS = os.path.join(BASE, "bench_D20_spasL", "config.scone")
SRC = os.path.join(BASE, "bench_D20")
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HFD, ZML = "H1922v7b3.hfd", "InitStateH0918Gait10ActA.zml"
PARREL = os.path.join("par", "H1922v7b3-TSG3Dv8g-989_fixed2.par")
SEEDS = [101, 102, 103, 104, 105, 106]
SPEEDS = [("V080", 0.80), ("V105", 1.05), ("V130", 1.30)]
ARMS = ["C", "S", "W"]
TA_BASE = 1759.0
WEAK_SCALE = 0.892
CONC = 2
PREREG = "2a939305b25ec234ec3a9ceaf2ebbd073345cd005d73b316485c4724f9f7ea09"


def set_speed(txt, v):
    out, n = re.subn(r"min_velocity\s*=\s*[\d.]+", "min_velocity = %.2f" % v, txt, count=1)
    assert n == 1, "min_velocity not found exactly once"
    return out


def edit_tib_ant_l(path, scale):
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines(True)
    i = next(k for k, ln in enumerate(lines) if ln.strip() == "name = tib_ant_l")
    j = next(k for k in range(i, len(lines)) if "max_isometric_force" in lines[k])
    lines[j] = lines[j][:lines[j].index("=") + 1] + (" %.1f\n" % (TA_BASE * scale))
    io.open(path, "w", encoding="utf-8", newline="").write("".join(lines))
    return lines[j].strip()


def ndiff(a_txt, b_txt):
    """Count changed lines by a REAL diff, not positionally.

    The positional version returned None whenever the line count changed, and `set_seed`
    legitimately ADDS a `random_seed` line. That aborted the first build -- correctly, since a
    guard that cannot tell an intended insertion from an unintended one must fail closed."""
    d = [l for l in difflib.unified_diff(a_txt.splitlines(), b_txt.splitlines(), n=0)
         if l[:1] in "+-" and l[:3] not in ("---", "+++")]
    return len(d)


def hist_lines(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def result_dir(tag):
    good = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*"))
            if os.path.isdir(d) and hist_lines(d) >= 91]
    if len(good) > 1:
        raise SystemExit("tag %s resolves to %d complete dirs; refusing" % (tag, len(good)))
    return good[0] if good else None


# ------------------------------------------------------------------ build
if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)

ctrl_t = io.open(T_CTRL, encoding="utf-8-sig", newline="").read()
spas_t = io.open(T_SPAS, encoding="utf-8-sig", newline="").read()
# the ONLY edit to the certified spastic template: give it the same depth as the others
assert "max_generations" not in spas_t, "spastic template already caps generations"
spas_t = spas_t.replace("CmaOptimizer {\n", "CmaOptimizer {\n\tmax_generations = 90\n", 1)
assert "max_generations = 90" in spas_t
assert spas_t.count("SpasticL") == 1 and "KV = 0.050" in spas_t
assert "legs = left" in spas_t
src_hfd = io.open(os.path.join(SRC, HFD), encoding="utf-8", newline="").read()

print("=" * 96)
print("BUILD -- PREREG_3d_speed_r203.md %s..." % PREREG[:16])
print("=" * 96)
manifest, diffrep = [], []
for vtag, v in SPEEDS:
    for arm in ARMS:
        base = spas_t if arm == "S" else ctrl_t
        for s in SEEDS:
            tag = "R203%s%s_s%d" % (vtag, arm, s)
            d = os.path.join(ROOT, tag)
            os.makedirs(os.path.join(d, "par"))
            shutil.copy2(os.path.join(SRC, HFD), os.path.join(d, HFD))
            shutil.copy2(os.path.join(SRC, ZML), os.path.join(d, ZML))
            shutil.copy2(os.path.join(SRC, PARREL), os.path.join(d, PARREL))
            txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, base, count=1)
            txt = set_speed(txt, v)
            txt = GS.set_seed(txt, s)
            io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8", newline="").write(txt)

            # scenario must differ from its OWN template in exactly: prefix, min_velocity, seed
            nd = ndiff(base, txt)
            assert nd <= 6, "%s: %d changed lines, expected <= 6 (prefix, min_velocity, seed)" % (tag, nd)

            taline = None
            if arm == "W":
                taline = edit_tib_ant_l(os.path.join(d, HFD), WEAK_SCALE)
            cur_hfd = io.open(os.path.join(d, HFD), encoding="utf-8", newline="").read()
            hd = ndiff(src_hfd, cur_hfd)
            # one CHANGED line shows as 2 diff lines under difflib (one -, one +)
            want_hd = 2 if arm == "W" else 0
            assert hd == want_hd, \
                "%s: model changed %r diff-lines, expected %d" % (tag, hd, want_hd)

            t2 = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
            assert GS.read_seed(t2) == s
            assert "max_generations = 90" in t2
            assert ("SpasticL" in t2) == (arm == "S")
            manifest.append({"tag": tag, "speed": v, "arm": arm, "seed": s,
                             "cfg_diff_lines": nd, "hfd_diff_lines": hd, "ta_line": taline})
        diffrep.append((vtag, arm, nd, hd))
    print("  %s  min_velocity = %.2f   arms C/S/W x 6 seeds = 18 cells" % (vtag, v))

print("\n  DIFF VERIFICATION (scenario vs its own template; model vs bench_D20):")
for vtag, arm, nd, hd in diffrep:
    print("    %s %s   config differs in %d lines   model differs in %d lines" % (vtag, arm, nd, hd))
print("  built %d cells" % len(manifest))
json.dump({"prereg_sha256": PREREG, "cells": manifest},
          io.open(os.path.join(ROOT, "BUILD_MANIFEST.json"), "w", encoding="utf-8"), indent=1)

# ------------------------------------------------------------------ run
scen = [os.path.join(ROOT, m["tag"], "config.scone") for m in manifest
        if result_dir(m["tag"]) is None]
print("\n%d to run, %d already complete, concurrency %d" %
      (len(scen), len(manifest) - len(scen), CONC))
print("expected %.1f min at 204.0 s/cell\n" % (len(scen) * 204.0 / CONC / 60.0))

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
        print("[%7.1fs] optimiser finished %-16s rc=%d %6.1fs gens=%d  (GATES NOT evaluated)"
              % (time.time() - t0, tag, p.returncode, time.time() - st, gens), flush=True)
    json.dump({"elapsed_s": round(time.time() - t0, 1), "done": done,
               "running": [t for t, _, _ in running]},
              io.open(os.path.join(ROOT, "PROGRESS.json"), "w", encoding="utf-8"), indent=1)

el = time.time() - t0
json.dump({"prereg_sha256": PREREG, "elapsed_s": round(el, 1), "concurrency": CONC,
           "cells": manifest, "runs": done},
          io.open(os.path.join(ROOT, "RUN_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("\ntotal %.1f s (%.1f min), %d cells" % (el, el / 60, len(done)))
print("GATES G1/G2/G3 are evaluated by the analysis, not here. Reaching 90 generations is not")
print("surviving, and this script never claims it is.")
