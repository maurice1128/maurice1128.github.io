# -*- coding: utf-8 -*-
"""PROBE, not a study. Two cells, control arm only, command 1.30, 270 generations.

ONE QUESTION: is the 1.023 -> 1.099 m/s shortfall a DEPTH limit or a CEILING?
Warm-started from each cell's OWN r203 V130C final .par, so this continues rather than restarts.
"""
import os, io, re, sys, glob, json, time, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_seeds as GS

BASE = os.path.join(HERE, "probe3d_r141")
ROOT = os.path.join(BASE, "probe_depth_r208")
TMPL = os.path.join(BASE, "timing3d", "config.scone")
SRC = os.path.join(BASE, "bench_D20")
RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HFD, ZML = "H1922v7b3.hfd", "InitStateH0918Gait10ActA.zml"
SEEDS = [101, 102]
GENS = 270

if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
tmpl = io.open(TMPL, encoding="utf-8-sig", newline="").read()

built = []
for s in SEEDS:
    src = [d for d in glob.glob(os.path.join(RES, "R203V130C_s%d.*" % s)) if os.path.isdir(d)][0]
    seed_par = sorted(glob.glob(os.path.join(src, "[0-9]*.par")))[-1]
    tag = "R208D%d_s%d" % (GENS, s)
    d = os.path.join(ROOT, tag)
    os.makedirs(os.path.join(d, "par"))
    shutil.copy2(os.path.join(SRC, HFD), os.path.join(d, HFD))
    shutil.copy2(os.path.join(SRC, ZML), os.path.join(d, ZML))
    shutil.copy2(seed_par, os.path.join(d, "par", "warm.par"))
    t = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = " + tag, tmpl, count=1)
    t = re.subn(r"min_velocity\s*=\s*[\d.]+", "min_velocity = 1.30", t, count=1)[0]
    t = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, t, count=1)[0]
    t = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]+"\s*\}', 'init { file = "par/warm.par" }', t, count=1)[0]
    t = GS.set_seed(t, s)
    io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8", newline="").write(t)
    chk = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
    assert "min_velocity = 1.30" in chk and "max_generations = %d" % GENS in chk
    assert 'init { file = "par/warm.par" }' in chk
    built.append({"tag": tag, "seed": s, "warm_from": os.path.basename(seed_par),
                  "warm_src": os.path.basename(src)})
    print("built %s  warm from %s" % (tag, os.path.basename(seed_par)))

json.dump({"gens": GENS, "cells": built},
          io.open(os.path.join(ROOT, "PROBE_MANIFEST.json"), "w", encoding="utf-8"), indent=1)

t0, run = time.time(), []
for b in built:
    c = os.path.join(ROOT, b["tag"], "config.scone")
    p = subprocess.Popen([SCONE, "-o", c, "-q"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.STDOUT, cwd=os.path.dirname(c))
    run.append((b["tag"], p))
    print("[%6.1fs] start %s" % (time.time() - t0, b["tag"]), flush=True)
while any(p.poll() is None for _, p in run):
    time.sleep(10)
print("\nprobe finished in %.1f s (%.1f min)" % (time.time() - t0, (time.time() - t0) / 60))
