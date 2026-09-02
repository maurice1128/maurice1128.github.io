# -*- coding: utf-8 -*-
"""r420 RECONNAISSANCE (not a registered test): where is the survival edge for SINGLE-muscle spasticity?

The mechanism test has been blocked all project by one fact: gastroc-only cells do not survive.
r407 (re-optimised) got 0/6 at KV 0.050, 0.070, 0.090, 0.110. r410 (frozen) fell at 3.3-3.6 s.
BUT NO ROUND EVER TESTED BELOW KV 0.050 for a single muscle. The clinical headline needs KV 0.110;
a MECHANISM comparison does not -- it needs the lowest dose at which BOTH single-muscle arms walk.

This is a cheap frozen sweep to locate that edge before committing optimiser time. It is explicitly
EXPLORATORY: it selects a dose, it does not test a hypothesis, and no number from it may be quoted
as a result. Its only output is a decision about where to register the real test.

Writes only inside our own staging tree; nothing touches the SCONE results directory.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC = os.path.join(BASE, "frozen2_r410")
DST = os.path.join(BASE, "recon_r420")
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\RECON_LOWDOSE_r420.json"

RUNGS = ["0.005", "0.010", "0.020", "0.030", "0.040"]
SEEDS = [101, 102, 103, 104, 105, 106]
ARMS = {"GAS": ("R410GAS", "gastroc"), "SOL": ("R410SOL", "soleus")}

SETTLE, T1 = 1.0, 9.73

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sto_utils as S  # noqa: E402


def kvre(muscle):
    return re.compile(r"(target\s*=\s*%s\s+delay\s*=\s*0\.020\s+KV\s*=\s*)([0-9.]+)" % muscle)


def build(arm, kv, seed):
    tmpl, muscle = ARMS[arm]
    src = os.path.join(SRC, "%s_s%d" % (tmpl, seed))
    name = "R420%s%s_s%d" % (arm, kv.replace(".", ""), seed)
    dst = os.path.join(DST, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    stale = os.path.join(dst, "FROZEN.par.sto")
    if os.path.exists(stale):
        os.remove(stale)

    cfg = os.path.join(dst, "config.scone")
    s = io.open(cfg, encoding="utf-8").read()
    i = s.index("name = SpasticL")                 # anchored; see build_slack_r418.py
    head, blk = s[:i], s[i:]
    m = kvre(muscle).search(blk)
    assert m, "%s: %s KV not found in SpasticL" % (name, muscle)
    blk = blk[:m.start(2)] + kv + blk[m.end(2):]
    assert kvre(muscle).search(blk).group(2) == kv, "%s: KV not set" % name
    other = "soleus" if muscle == "gastroc" else "gastroc"
    assert not kvre(other).search(blk), "%s: template carries a %s reflex too" % (name, other)
    s2 = (head + blk).replace("signature_prefix = %s_s%d" % (tmpl, seed),
                              "signature_prefix = %s" % name)
    assert tmpl not in s2, "%s: stale signature_prefix" % name
    io.open(cfg, "w", encoding="utf-8", newline="").write(s2)
    return dst, name


def gate(d):
    sto = os.path.join(d, "FROZEN.par.sto")
    if not os.path.exists(sto):
        return None
    cols, dat = S.load_sto(sto)
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    ok = float(t[-1]) >= T1 and len(win) >= 5
    K = np.degrees(S.col(cols, dat, "knee_angle_l"))
    return {"t_end": float(t[-1]), "n_cycles": len(win), "gate_G": bool(ok),
            "knee_hs": float(np.mean([K[a] for a, _ in win])) if win else None}


if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    res = {"round": "RECON_LOWDOSE_r420",
           "status": "EXPLORATORY RECONNAISSANCE. Selects a dose for a later registered test. "
                     "No number here may be quoted as a result.",
           "why": "no round ever tested a single-muscle spastic reflex below KV 0.050. r407 and "
                  "r410 both started at 0.050 and both found 0/6 survival for gastroc-only.",
           "arms": {}}
    for arm in ARMS:
        res["arms"][arm] = {}
        for kv in RUNGS:
            cells = {}
            for s in SEEDS:
                d, name = build(arm, kv, s)
                subprocess.run([SCONE, "-e", "FROZEN.par"], cwd=d, capture_output=True,
                               text=True, timeout=900)
                cells[name] = gate(d)
            g = [c for c in cells.values() if c and c["gate_G"]]
            res["arms"][arm][kv] = {"n_gate_G": len(g), "cells": cells,
                                    "t_end_range": [min(c["t_end"] for c in cells.values() if c),
                                                    max(c["t_end"] for c in cells.values() if c)]}
            print("  %-4s KV %-6s  Gate G %d/6   t_end [%.2f, %.2f]"
                  % (arm, kv, len(g), res["arms"][arm][kv]["t_end_range"][0],
                     res["arms"][arm][kv]["t_end_range"][1]))
            sys.stdout.flush()

    both = [kv for kv in RUNGS
            if res["arms"]["GAS"][kv]["n_gate_G"] >= 4 and res["arms"]["SOL"][kv]["n_gate_G"] >= 4]
    res["highest_dose_where_BOTH_arms_reach_4_of_6"] = max(both) if both else None
    res["VERDICT"] = ("frozen single-muscle cells reach Gate G at KV %s or below; a registered "
                      "mechanism test is possible there" % max(both)) if both else (
        "NO dose in {0.005 .. 0.040} lets BOTH single-muscle arms reach 4/6 under a FROZEN "
        "controller. Frozen replay is the harshest case -- no adaptation at all -- so this does "
        "not rule out the re-optimised test, but it means the frozen route is closed.")
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    print()
    print("VERDICT:", res["VERDICT"])
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
