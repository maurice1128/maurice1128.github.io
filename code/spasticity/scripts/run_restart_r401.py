# -*- coding: utf-8 -*-
"""run_restart_r401.py -- multi-restart sweep at KV 0.130.

WHY. r396 climbed KV 0.100 -> 0.110 -> 0.120 and stalled: at 0.130 all four attempts failed
Gate G, but not uniformly -- t_end came out 1.55, 1.56 and 9.66 s. The 9.66 misses the 9.73 s
gate by 0.07 s. The same bimodality appeared at WK x0.60 (three cells at t_end 20.00 with
objective ~1.08, three at 7.5 s with objective ~68). Within one rung, one protocol and one
budget, the CMA-ES random seed decides which basin is found.

So this does not change severity, chaining, budget or endpoint. It only draws more samples
from the same lottery: each surviving KV 0.120 parent is re-optimised to KV 0.130 under
several different `random_seed` values. The parent .par is held fixed within a fan; only the
optimiser's own seed varies.

⛔ SAFETY, unchanged from the corpus launchers:
  * writes ONLY into a new staging tree under spasticity_paper; SCONE writes ONLY new
    directories under SCONE\\results;
  * the 112 protected directories are never opened for write, and every new directory name is
    asserted against the protected pattern before harvest;
  * YIELD: before each cell, count sconecmd processes; if any is running that is not ours,
    suspend and report rather than compete.

Usage:  python run_restart_r401.py --stage
        python run_restart_r401.py --rest
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
RES = r"C:\Users\maurice\Documents\SCONE\results"
ROOT = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC_S = os.path.join(ROOT, "reopt_r151", "R151S_s101")
STAGE = os.path.join(ROOT, "restart_r401")
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
PROTECTED = re.compile(r"^(s[1-4])?(KF|KE|HF|DF|PF)[0-9]+L")

KV = 0.130
GENS = 90
SETTLE, T1, MIN_CYC = 1.0, 9.73, 5
PARENT_SEEDS = [102, 105, 106]           # the KV 0.120 cells that passed Gate G
RESTARTS = [201, 202, 203, 204, 205, 206, 207, 208]


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def cells():
    out = []
    for ps in PARENT_SEEDS:
        for rs in RESTARTS:
            out.append({"parent_prefix": "R396SPg120_s%d" % ps, "parent_seed": ps,
                        "restart_seed": rs, "kv": KV,
                        "prefix": "R401SPg130p%dr%d" % (ps, rs)})
    return out


def best_par_by_generation(cd, warm_basename=None):
    """Highest generation among the run's own outputs, excluding the staged warm start.

    Carried from run_dfsevere_r293.py: selecting by the objective encoded in the filename is
    unsafe whenever the warm start was optimised under a different objective, and that defect
    corrupted the r294 deposits.
    """
    pars = [p for p in sorted(glob.glob(os.path.join(cd, "[0-9]*.par")))
            if os.path.basename(p) != (warm_basename or "")]
    if not pars:
        return None
    return max(pars, key=lambda p: int(os.path.basename(p).split("_")[0]))


def resolve_parent(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    assert len(g) == 1, "%s -> %d dirs" % (prefix, len(g))
    par = best_par_by_generation(g[0])
    assert par, "no .par in " + g[0]
    return {"dir": g[0], "par": par, "par_sha256": sha(par),
            "generation": int(os.path.basename(par).split("_")[0])}


def stage():
    os.makedirs(STAGE, exist_ok=True)
    man = {"arm": "RESTART_r401", "kv": KV, "generations": GENS,
           "why": ("KV 0.130 failed 0/4 in r396 with t_end 1.55, 1.56 and 9.66 s -- the 9.66 "
                   "misses the 9.73 s gate by 0.07 s. Within a rung the CMA-ES seed decides "
                   "the basin, so this draws more samples from the same lottery."),
           "only_change": "the optimiser's random_seed. Severity, chaining, budget, endpoint fixed.",
           "parent_seeds": PARENT_SEEDS, "restart_seeds": RESTARTS, "cells": []}
    for c in cells():
        d = os.path.join(STAGE, c["prefix"])
        for sub in ("models", "data", "par"):
            os.makedirs(os.path.join(d, sub), exist_ok=True)
        p = resolve_parent(c["parent_prefix"])
        warm = "WARM_%s_g%04d.par" % (c["parent_prefix"], p["generation"])
        shutil.copyfile(p["par"], os.path.join(d, "par", warm))
        assert sha(os.path.join(d, "par", warm)) == p["par_sha256"]
        shutil.copyfile(os.path.join(SRC_S, "H1922v7b3.hfd"),
                        os.path.join(d, "models", "H1922v7b3.hfd"))
        shutil.copyfile(os.path.join(SRC_S, "InitStateH0918Gait10ActA.zml"),
                        os.path.join(d, "data", "InitStateH0918Gait10ActA.zml"))
        cfg = io.open(os.path.join(SRC_S, "config.scone"), encoding="utf-8").read()
        cfg, n = re.subn(r"KV\s*=\s*0\.050", "KV = %.3f" % KV, cfg)
        assert n == 2, "expected 2 KV substitutions, made %d" % n
        cfg, n = re.subn(r"max_generations\s*=\s*\d+", "max_generations = %d" % GENS, cfg, 1)
        assert n == 1
        cfg, n = re.subn(r'init\s*\{\s*file\s*=\s*"[^"]*"\s*\}',
                         'init { file = "par/%s" }' % warm, cfg, 1)
        assert n == 1
        cfg, n = re.subn(r"random_seed\s*=\s*\d+", "random_seed = %d" % c["restart_seed"], cfg, 1)
        assert n == 1
        cfg, n = re.subn(r"signature_prefix\s*=\s*\S+",
                         "signature_prefix = %s" % c["prefix"], cfg, 1)
        assert n == 1
        io.open(os.path.join(d, "config.scone"), "w", encoding="utf-8",
                newline="\n").write(cfg)
        back = io.open(os.path.join(d, "config.scone"), encoding="utf-8").read()
        assert len(re.findall(r"KV\s*=\s*%.3f\b" % KV, back)) == 2
        assert re.search(r"random_seed\s*=\s*%d\b" % c["restart_seed"], back)
        assert re.search(r'init\s*\{\s*file\s*=\s*"par/%s"\s*\}' % re.escape(warm), back)
        man["cells"].append({**c, "warm": warm, "parent_par": os.path.basename(p["par"]),
                             "parent_par_sha256": p["par_sha256"],
                             "parent_generation": p["generation"],
                             "config_sha256": sha(os.path.join(d, "config.scone"))})
    io.open(os.path.join(PAPER, "RESTART_STAGE_r401.json"), "w",
            encoding="utf-8").write(json.dumps(man, indent=2, ensure_ascii=False))
    print("staged %d cells under %s" % (len(man["cells"]), STAGE))
    print("manifest %s" % os.path.join(PAPER, "RESTART_STAGE_r401.json"))


def competing():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "@(Get-Process -Name sconecmd -EA SilentlyContinue).Count"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return int(out or 0)
    except Exception:
        return -1


def evaluate(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return {"status": "NO_RESULT_DIR"}
    dup = len(g) > 1
    if dup:
        # A re-run makes SCONE create a "... (1)" twin. Choose the directory that actually
        # optimised -- the one with the most .par files -- and record that a twin existed.
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    stos = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not stos:
        # SCONE's optimiser writes .par but NOT .par.sto; replay the resolved .par to make it.
        # Carried from run_chain_r393.py, which does the same before measuring.
        par = best_par_by_generation(g[0])
        if par:
            subprocess.run([SCONE, "-e", os.path.basename(par)], cwd=g[0],
                           capture_output=True, timeout=1800)
            stos = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not stos:
        return {"status": "NO_STO_AFTER_REPLAY", "dir": os.path.basename(g[0])}
    cols, dat = S.load_sto(stos[-1])
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    o = {"status": "OK", "duplicate_result_dir": dup, "dir": os.path.basename(g[0]), "t_end_s": float(t[-1]),
         "n_cycles_in_window": len(win)}
    o["gate_G"] = bool(float(t[-1]) >= T1 and len(win) >= MIN_CYC)
    if o["gate_G"]:
        kne = np.degrees(S.col(cols, dat, "knee_angle_l"))
        o["knee_at_heelstrike_deg"] = float(np.mean([kne[a] for a, _ in win]))
        on = grf > thr
        st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
        o["ank_stance_mean_deg"] = float(np.mean(np.degrees(S.col(cols, dat,
                                                                  "ankle_angle_l"))[st]))
    return o


def run_all():
    cs = cells()
    recs = []
    for i, c in enumerate(cs):
        f = os.path.join(PAPER, "RUN_RESTART_r401_cell%02d.json" % i)
        if os.path.exists(f):
            recs.append(json.load(io.open(f, encoding="utf-8")))
            continue
        n = competing()
        if n > 0:
            print("YIELD: %d sconecmd already running. Suspending, not competing." % n)
            return recs
        d = os.path.join(STAGE, c["prefix"])
        before = set(os.listdir(RES))
        t0 = time.time()
        p = subprocess.run([SCONE, "-o", os.path.join(d, "config.scone"), "-q"],
                           capture_output=True, text=True, cwd=d)
        wall = time.time() - t0
        new = sorted(set(os.listdir(RES)) - before)
        for nd in new:
            assert not PROTECTED.match(nd), "refusing: protected name created " + nd
        rec = {"cell": i, **c, "wall_clock_s": wall, "returncode": p.returncode,
               "new_result_dirs": new}
        rec.update(evaluate(c["prefix"]))
        io.open(f, "w", encoding="utf-8").write(json.dumps(rec, indent=1, ensure_ascii=False))
        recs.append(rec)
        print("cell %02d %-22s %-14s wall %6.1f s  t_end %-6s gate %-5s knee_HS %s"
              % (i, c["prefix"], rec.get("status"), wall,
                 ("%.2f" % rec["t_end_s"]) if rec.get("t_end_s") else "-",
                 rec.get("gate_G"),
                 ("%+.4f" % rec["knee_at_heelstrike_deg"])
                 if rec.get("knee_at_heelstrike_deg") is not None else "-"))
    ok = [r for r in recs if r.get("gate_G")]
    out = {"arm": "RESTART_r401", "kv": KV, "n_cells": len(recs), "n_gate_G": len(ok),
           "hit_rate": len(ok) / float(len(recs)) if recs else None,
           "prior_attempt": "r396 KV 0.130: 0 of 4 passed, t_end 1.55 / 1.56 / 9.66",
           "knee_at_heelstrike_deg": sorted(r["knee_at_heelstrike_deg"] for r in ok),
           "cells": recs}
    io.open(os.path.join(PAPER, "RESTART_RESULT_r401.json"), "w",
            encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
    print()
    print("Gate G: %d of %d restarts" % (len(ok), len(recs)))
    if ok:
        v = out["knee_at_heelstrike_deg"]
        print("knee at heel strike: [%+.4f, %+.4f]" % (v[0], v[-1]))
    print("wrote %s" % os.path.join(PAPER, "RESTART_RESULT_r401.json"))
    return recs


ap = argparse.ArgumentParser()
ap.add_argument("--stage", action="store_true")
ap.add_argument("--rest", action="store_true")
a = ap.parse_args()
if a.stage:
    stage()
elif a.rest:
    run_all()
else:
    ap.print_help()
