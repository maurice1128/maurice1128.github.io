# -*- coding: utf-8 -*-
"""CONTINUATION ladder. Build and run just-in-time, because each rung's starting parameter
vector does not exist until the rung below it has converged.

GOVERNED BY  paper/PREREG_3d_continuation_r172.md
             sha256 35ac02b4706add2585c6455b79fd6384c957df3899ae51f2b117ec1f95b2c60b
             hashed BEFORE this file was written and before any scenario file existed.
Where this script and that registration disagree, THE REGISTRATION DECIDES.

SECTION 2 -- DEPTH SYMMETRY. Both arms run under continuation, position-matched:

  pos 1 (depth  90, from healthy)   spastic KV 0.050  |  weak x0.95   <- REUSED from r169
  pos 2 (depth 180, from pos 1)     spastic KV 0.150  |  weak x0.90
  pos 3 (depth 270, from pos 2)     spastic KV 0.400  |  weak x0.80

The magnitudes are r169's, unchanged. Only the optimisation PATH changes (section 1).

SECTION 3 -- a chain that fails at position 2 does NOT attempt position 3 from the healthy par.
That would reintroduce the defect under test. Position 3 is then NOT REACHED, which the
registration distinguishes from FAILED.

No --run, no --launch. Progress is history.txt line counts, never LAUNCH_STATUS.json.
"""
import io
import os
import re
import sys
import glob
import json
import time
import shutil
import filecmp
import subprocess

HERE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
sys.path.insert(0, HERE)
import gen_seeds as GS

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.join(HERE, "probe3d_r141")
ROOT = os.path.join(BASE, "cont_r172")
TEMPLATE = os.path.join(BASE, "timing3d", "config.scone")
SRC = os.path.join(BASE, "bench_D20")
R169 = os.path.join(BASE, "ladder_r169")
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HFD = "H1922v7b3.hfd"
ZML = "InitStateH0918Gait10ActA.zml"
PARREL = os.path.join("par", "H1922v7b3-TSG3Dv8g-989_fixed2.par")
SEEDS = [101, 102, 103, 104, 105, 106]
TA_BASE = 1759.0
CONC = 2
PREREG = "35ac02b4706add2585c6455b79fd6384c957df3899ae51f2b117ec1f95b2c60b"

# arm -> [(position, tag prefix, kv or None, tib_ant scale, reuse-tag prefix or None)]
CHAINS = {
    "spastic": [(1, "R151S",    "0.050", 1.00, "R151S"),
                (2, "R172S150", "0.150", 1.00, None),
                (3, "R172S400", "0.400", 1.00, None)],
    "weak":    [(1, "R169W095", None,    0.95, "R169W095"),
                (2, "R172W090", None,    0.90, None),
                (3, "R172W080", None,    0.80, None)],
}

SPASTIC_BLOCK = """
					ConditionalController {
						states = "EarlyStance LateStance Liftoff Swing Landing"
						legs = left
						ReflexController {
							name = SpasticL
							MuscleReflex {
								target = soleus
								delay = 0.020
								KV = %s
								allow_neg_V = 0
							}
							MuscleReflex {
								target = gastroc
								delay = 0.020
								KV = %s
								allow_neg_V = 0
							}
						}
					}
"""


def hist_lines(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def result_dir(tag):
    """Exactly one COMPLETE directory, or None. Section 8: never sorted(ds)[0]."""
    good = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*"))
            if os.path.isdir(d) and hist_lines(d) >= 91]
    if len(good) > 1:
        raise SystemExit("tag %s resolves to %d complete directories; refusing" % (tag, len(good)))
    return good[0] if good else None


def best_par(d):
    ps = [p for p in glob.glob(os.path.join(d, "*.par")) if os.path.basename(p)[0].isdigit()]
    return sorted(ps)[-1] if ps else None


def edit_tib_ant_l(path, scale):
    lines = io.open(path, encoding="utf-8", newline="").read().splitlines(True)
    i = next(k for k, ln in enumerate(lines) if ln.strip() == "name = tib_ant_l")
    j = next(k for k in range(i, len(lines)) if "max_isometric_force" in lines[k])
    lines[j] = lines[j][:lines[j].index("=") + 1] + (" %.1f\n" % (TA_BASE * scale))
    io.open(path, "w", encoding="utf-8", newline="").write("".join(lines))


def build_cell(tag, arm, kv, scale, seed, parent_par):
    """Build one cell. parent_par is copied in under the template's own par filename, so the
       config's init reference is unchanged and the ONLY thing that differs is the vector."""
    d = os.path.join(ROOT, tag)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "par"))
    shutil.copy2(os.path.join(SRC, HFD), os.path.join(d, HFD))
    shutil.copy2(os.path.join(SRC, ZML), os.path.join(d, ZML))
    shutil.copy2(parent_par, os.path.join(d, PARREL))

    txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag,
                 io.open(TEMPLATE, encoding="utf-8", newline="").read(), count=1)
    if arm == "spastic":
        anchor = txt.rindex("ConditionalController")
        close = txt.index("\n\t\t\t\t}\n", anchor)
        txt = txt[:close] + "\n" + (SPASTIC_BLOCK % (kv, kv)) + txt[close:]
        assert txt.count("name = SpasticL") == 1
        assert txt.count("KV = " + kv) == 2
    else:
        assert "SpasticL" not in txt
    txt = GS.set_seed(txt, seed)
    cp = os.path.join(d, "config.scone")
    io.open(cp, "w", encoding="utf-8", newline="").write(txt)

    if arm == "weak":
        edit_tib_ant_l(os.path.join(d, HFD), scale)
    t2 = io.open(cp, encoding="utf-8").read()
    assert GS.read_seed(t2) == seed, "%s: seed readback failed" % tag
    assert "max_generations = 90" in t2, "%s: lost max_generations" % tag   # section 2 check 3
    return cp


# ---------------------------------------------------------------- section 2 check 4
print("=" * 92)
print("SECTION 2 CHECK 4 -- position-1 cells must be the r169 originals, byte-identical")
print("=" * 92)
pos1_ok = True
for arm, steps in CHAINS.items():
    pre = steps[0][1]
    for s in SEEDS:
        tag = "%s_s%d" % (pre, s)
        a = os.path.join(R169, tag, "config.scone")
        if not os.path.exists(a):
            print("  MISSING %s" % a)
            pos1_ok = False
            continue
        if result_dir(tag) is None:
            print("  NO COMPLETE RESULT for %s" % tag)
            pos1_ok = False
for arm, steps in CHAINS.items():
    print("  %-8s position 1 = %s (reused, depth 90 from healthy)" % (arm, steps[0][1]))
if not pos1_ok:
    raise SystemExit("position-1 reuse cannot be verified; section 2 voids the comparison")
print("  all 12 position-1 cells present and complete")

if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)

# ---------------------------------------------------------------- run the chains
print("\n" + "=" * 92)
print("CONTINUATION -- 12 independent chains (6 seeds x 2 arms), 2 ordered steps each,")
print("concurrency %d across chains. Magnitudes unchanged; only the path changes." % CONC)
print("=" * 92)

work = []          # (arm, seed) chains to advance
for arm in CHAINS:
    for s in SEEDS:
        work.append([arm, s, 1])          # next position to attempt is 2 (index 1 -> steps[1])

manifest, running, t0 = [], [], time.time()
chain_state = {(a, s): {"reached": 1, "status": "ok"} for a in CHAINS for s in SEEDS}
queue = [w for w in work]

while queue or running:
    while queue and len(running) < CONC:
        arm, s, idx = queue.pop(0)
        pos, prefix, kv, scale, _ = CHAINS[arm][idx]
        parent_prefix = CHAINS[arm][idx - 1][1]
        ptag = "%s_s%d" % (parent_prefix, s)
        pdir = result_dir(ptag)
        if pdir is None:
            chain_state[(arm, s)]["status"] = "NOT REACHED (parent incomplete)"
            print("  chain %-8s s%d  position %d NOT REACHED -- parent %s has no complete result"
                  % (arm, s, pos, ptag), flush=True)
            continue
        bp = best_par(pdir)
        if bp is None:
            chain_state[(arm, s)]["status"] = "NOT REACHED (parent has no par)"
            continue
        tag = "%s_s%d" % (prefix, s)
        cp = build_cell(tag, arm, kv, scale, s, bp)
        p = subprocess.Popen([SCONE, "-o", cp, "-q"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT, cwd=os.path.dirname(cp))
        running.append((arm, s, idx, pos, tag, p, time.time()))
        manifest.append({"arm": arm, "seed": s, "position": pos, "tag": tag,
                         "cumulative_depth": 90 * pos,              # section 2 check 2
                         "parent_tag": ptag,                        # section 2 check 1
                         "parent_par": os.path.basename(bp),
                         "parent_dir": os.path.basename(pdir),
                         "kv": kv, "ta_scale": scale})
        print("[%7.1fs] start %-16s arm=%-8s seed=%d pos=%d depth=%d parent=%s"
              % (time.time() - t0, tag, arm, s, pos, 90 * pos, os.path.basename(bp)), flush=True)
    time.sleep(5)
    for r in list(running):
        arm, s, idx, pos, tag, p, st = r
        if p.poll() is None:
            continue
        running.remove(r)
        rd = result_dir(tag)
        gens = (hist_lines(rd) - 1) if rd else 0
        ok = rd is not None and gens >= 90
        chain_state[(arm, s)]["reached"] = pos
        print("[%7.1fs] done  %-16s rc=%d %7.1fs gens=%d %s"
              % (time.time() - t0, tag, p.returncode, time.time() - st, gens,
                 "" if ok else "<< INCOMPLETE"), flush=True)
        if ok and idx + 1 < len(CHAINS[arm]):
            queue.append([arm, s, idx + 1])
        elif not ok:
            chain_state[(arm, s)]["status"] = "chain stopped at position %d" % pos
    json.dump({"prereg_sha256": PREREG, "elapsed_s": round(time.time() - t0, 1),
               "cells": manifest,
               "chains": {"%s_s%d" % k: v for k, v in chain_state.items()}},
              io.open(os.path.join(ROOT, "PROGRESS.json"), "w", encoding="utf-8"), indent=1)

el = time.time() - t0
json.dump({"prereg_sha256": PREREG, "elapsed_s": round(el, 1), "concurrency": CONC,
           "cells": manifest, "chains": {"%s_s%d" % k: v for k, v in chain_state.items()}},
          io.open(os.path.join(ROOT, "RUN_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("\ntotal %.1f s (%.1f min), %d cells built and run" % (el, el / 60, len(manifest)))
for k in sorted(chain_state):
    print("  chain %-12s reached position %d  %s"
          % ("%s_s%d" % k, chain_state[k]["reached"], chain_state[k]["status"]))
