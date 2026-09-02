# -*- coding: utf-8 -*-
"""PREREG_3d_replication_r209.md -- 6 spastic cells, seeds 201-206.

Registration sha256 919a8cb86ab0a5d23b29ad2c7aec2a3c24d41dc0dcd12ca1ee30a7bfc35c40a5,
hashed and frozen BEFORE this file was written.

Every scenario is cloned from R151S_s101's ARCHIVED config and must differ from it in exactly
the seed line. If the assertion fires the build aborts and nothing is launched.
"""
import os, io, sys, glob, json, time, shutil, subprocess, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_seeds as GS

BASE = os.path.join(HERE, "probe3d_r141")
ROOT = os.path.join(BASE, "replication_r209")
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SEEDS = [201, 202, 203, 204, 205, 206]
CONC = 2
PREREG = "919a8cb86ab0a5d23b29ad2c7aec2a3c24d41dc0dcd12ca1ee30a7bfc35c40a5"

src = [d for d in glob.glob(os.path.join(RES, "R151S_s101.*")) if os.path.isdir(d)][0]
# The ARCHIVED config is CRLF. gen_seeds.SEED_RE anchors on [space/tab]*$ and CR is neither, so
# read_seed returns None on CRLF and set_seed REFUSES rather than writing silently -- the
# hardening its docstring describes, doing its job. Without it six cells would have run at the
# CMA-ES default seed and been reported as six new seeds. Normalise to LF, the form every
# scenario this project generates already uses and which SCONE accepts.
_raw = io.open(os.path.join(src, "config.scone"), encoding="utf-8-sig", newline="").read()
base_cfg = _raw.replace(chr(13) + chr(10), chr(10))
assert "SpasticL" in base_cfg and "KV = 0.050" in base_cfg and "legs = left" in base_cfg
assert "max_generations = 90" in base_cfg and "min_velocity = 1.0" in base_cfg

if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)

print("=" * 92)
print("BUILD -- PREREG_3d_replication_r209.md %s..." % PREREG[:16])
print("cloning from %s" % os.path.basename(src))
print("=" * 92)
man = []
for s in SEEDS:
    tag = "R209S_s%d" % s
    d = os.path.join(ROOT, tag)
    os.makedirs(d)
    for f in os.listdir(src):
        if f.endswith((".sto", ".par", ".txt", ".log")) and f != "config.scone":
            continue
        p = os.path.join(src, f)
        if os.path.isdir(p):
            shutil.copytree(p, os.path.join(d, f))
        elif f != "config.scone":
            shutil.copy2(p, os.path.join(d, f))
    # warm-start par lives at top level in the archive; the config points at par/
    warm = os.path.join(src, "H1922v7b3-TSG3Dv8g-989_fixed2.par")
    os.makedirs(os.path.join(d, "par"), exist_ok=True)
    shutil.copy2(warm, os.path.join(d, "par", os.path.basename(warm)))
    shutil.copy2(warm, os.path.join(d, os.path.basename(warm)))
    txt = GS.set_seed(base_cfg, s)
    import re
    txt = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, txt, count=1)
    io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8", newline="").write(txt)

    dl = [l for l in difflib.unified_diff(base_cfg.splitlines(), txt.splitlines(), n=0)
          if l[:1] in "+-" and l[:3] not in ("---", "+++")]
    # exactly: random_seed changed (-/+) and signature_prefix changed (-/+) = 4 lines
    assert len(dl) == 4, "%s: %d changed lines, expected 4 (seed + prefix)\n%s" % (tag, len(dl), dl)
    assert GS.read_seed(txt) == s
    man.append({"tag": tag, "seed": s, "cfg_diff_lines": len(dl), "cloned_from": os.path.basename(src)})
    print("  %-12s diff vs archive = %d lines (seed + signature_prefix)" % (tag, len(dl)))

json.dump({"prereg_sha256": PREREG, "cells": man},
          io.open(os.path.join(ROOT, "BUILD_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("  built %d cells" % len(man))


def hist(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def done_dir(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d) and hist(d) >= 91]
    if len(g) > 1:
        raise SystemExit("tag %s -> %d complete dirs" % (tag, len(g)))
    return g[0] if g else None


scen = [os.path.join(ROOT, m["tag"], "config.scone") for m in man if done_dir(m["tag"]) is None]
print("\n%d to run, concurrency %d, expected %.1f min at 204.0 s/cell\n"
      % (len(scen), CONC, len(scen) * 204.0 / CONC / 60))
t0, run, fin = time.time(), [], []
while scen or run:
    while scen and len(run) < CONC:
        c = scen.pop(0)
        tag = os.path.basename(os.path.dirname(c))
        p = subprocess.Popen([SCONE, "-o", c, "-q"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT, cwd=os.path.dirname(c))
        run.append((tag, p, time.time()))
        print("[%6.1fs] start %s" % (time.time() - t0, tag), flush=True)
    time.sleep(5)
    for r in list(run):
        tag, p, st = r
        if p.poll() is None:
            continue
        run.remove(r)
        rd = done_dir(tag)
        fin.append({"tag": tag, "rc": p.returncode, "secs": round(time.time() - st, 1),
                    "gens": (hist(rd) - 1) if rd else 0})
        print("[%6.1fs] optimiser finished %-12s rc=%d %6.1fs  (GATES NOT evaluated)"
              % (time.time() - t0, tag, p.returncode, time.time() - st), flush=True)
    json.dump({"elapsed_s": round(time.time() - t0, 1), "done": fin,
               "running": [t for t, _, _ in run]},
              io.open(os.path.join(ROOT, "PROGRESS.json"), "w", encoding="utf-8"), indent=1)
json.dump({"prereg_sha256": PREREG, "cells": man, "runs": fin},
          io.open(os.path.join(ROOT, "RUN_MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("\ntotal %.1f min, %d cells. Gates and endpoint are NOT computed here." % ((time.time() - t0) / 60, len(fin)))
