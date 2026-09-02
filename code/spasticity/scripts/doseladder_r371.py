# -*- coding: utf-8 -*-
"""PREREG_doseladder_r370.md (e4401084...) -- detection threshold across the KV ladder.

A = mean soleus_l.activation over stance samples of the admissible cycles. One per cell.
Per rung: disjointness against the dorsiflexor-weakness arm, reduced to seed means so the
permutation unit is consistent (section 6). KV 0.050 (R203 S) is reported for continuity and
EXCLUDED from every primary test (section 3). Section 7's confound audit runs first and is
deposited whatever it says.
"""
import glob
import hashlib
import io
import itertools
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DOSELADDER_r371.json"
PREREG_SHA = "e4401084e5ad865c9160e99281f991909607fb60a376fbc35b15bf5821d252a2"
SETTLE, T1 = 1.0, 9.73

LADDER = [("0.00625", ["R289KV00625"], True),
          ("0.0125", ["R289KV0125"], True),
          ("0.035", ["R291KV0035"], True),
          ("0.050", ["R203V080S", "R203V105S", "R203V130S"], False),   # seen -> not primary
          ("0.070", ["R291KV0070"], True)]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
CONTROL = ["R203V080C", "R203V105C", "R203V130C"]


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


def tags_for(fams):
    out = []
    for f in fams:
        seen = set()
        for d in sorted(glob.glob(os.path.join(RES, f + "_s*"))):
            b = os.path.basename(d).split(".")[0]
            if b not in seen:
                seen.add(b)
                out.append(b)
    return out


def audit(fam):
    """Section 7: min_velocity, model digest, presence of the SpasticL controller."""
    try:
        d = rd(tags_for([fam])[0])
    except Exception as e:
        return {"error": str(e)}
    a = {"dir": os.path.basename(d)}
    cfg = os.path.join(d, "config.scone")
    if os.path.exists(cfg):
        txt = io.open(cfg, encoding="utf-8", errors="replace").read()
        m = re.search(r"min_velocity\s*=\s*([0-9.]+)", txt)
        a["min_velocity"] = float(m.group(1)) if m else None
        a["has_SpasticL"] = "SpasticL" in txt
        m = re.search(r"name\s*=\s*SpasticL.*?KV\s*=\s*([0-9.]+)", txt, re.S)
        a["config_KV"] = float(m.group(1)) if m else None
    hfd = glob.glob(os.path.join(d, "*.hfd"))
    if hfd:
        a["model_file"] = os.path.basename(hfd[0])
        a["model_sha256"] = hashlib.sha256(io.open(hfd[0], "rb").read()).hexdigest()[:16]
        txt = io.open(hfd[0], encoding="utf-8", errors="replace").read().splitlines()
        for i, l in enumerate(txt):
            if "tib_ant_l" in l:
                for j in range(i, min(i + 8, len(txt))):
                    m = re.search(r"max_isometric_force\s*=\s*([0-9.]+)", txt[j])
                    if m:
                        a["tib_ant_l_max_isometric_force"] = float(m.group(1))
                        break
                break
    return a


def measure(tag):
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        return rec
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        return rec
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        return rec
    t = dat[:, 0]
    rec["t_end_s"] = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    rec["n_cycles_in_window"] = len(win)
    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["gate_G"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec
    rec["gate_G"] = True
    on = grf > thr
    idx = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    v = S.muscle_signal(cols, dat, "soleus", "l", "activation")
    rec["A"] = float(np.mean(v[idx]))
    return rec


def seed_means(tags, cells):
    out = {}
    for tg in tags:
        r = cells[tg]
        if not r.get("gate_G") or r.get("A") is None:
            continue
        sd = tg.split("_")[-1]
        out.setdefault(sd, []).append(r["A"])
    return {k: float(np.mean(v)) for k, v in out.items()}


def floor(a, b):
    allv = list(a) + list(b)
    n1 = len(a)
    obs = max(min(b) - max(a), min(a) - max(b))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        x = [allv[i] for i in comb]
        y = [allv[i] for i in range(len(allv)) if i not in comb]
        if max(min(y) - max(x), min(x) - max(y)) >= obs - 1e-12:
            cnt += 1
        tot += 1
    return {"n_total": tot, "n_at_least_as_extreme": cnt, "floor": "1/%d" % tot}


def main():
    res = {"registration": "PREREG_doseladder_r370.md", "registration_sha256": PREREG_SHA,
           "endpoint": "A = mean soleus_l.activation over stance samples of admissible cycles",
           "registered_predictions": {
               "1_monotonic": "A per rung non-decreasing in KV over 0.00625, 0.0125, 0.035, 0.070",
               "2_threshold": "KV* = 0.035; rungs >= KV* disjoint from DF-weak, below overlap",
               "3_direction": "wherever a rung separates, SPASTIC HIGH"},
           "excluded_from_primary": "KV 0.050 (R203 S) -- values were seen before registration",
           "cells": {}}

    print("=== section 7 confound audit ===")
    aud = {}
    for _, fams, _ in LADDER:
        for f in fams:
            aud[f] = audit(f)
    for f in DFWEAK + CONTROL:
        aud[f] = audit(f)
    res["CONFOUND_AUDIT_sec7"] = aud
    mv = {}
    for f, a in aud.items():
        mv.setdefault(a.get("min_velocity"), []).append(f)
    for k in sorted(mv, key=lambda x: (x is None, x)):
        print("  min_velocity=%-6s %s" % (k, ", ".join(sorted(mv[k]))))
    res["CONFOUND_AUDIT_sec7"]["_min_velocity_groups"] = {str(k): sorted(v) for k, v in mv.items()}
    between = len(mv) > 1
    res["BETWEEN_SCENARIO"] = between
    print("  -> comparison is %s" % ("BETWEEN-SCENARIO (min_velocity differs across arms)"
                                     if between else "within-scenario"))

    print()
    print("=== measurement ===")
    wtags = tags_for(DFWEAK)
    for tg in wtags:
        res["cells"][tg] = measure(tg)
    wsm = seed_means(wtags, res["cells"])
    w = sorted(wsm.values())
    print("DFWEAK  seeds=%d  A seed-mean [%.6f, %.6f]" % (len(w), w[0], w[-1]))

    ctags = tags_for(CONTROL)
    for tg in ctags:
        res["cells"][tg] = measure(tg)
    csm = seed_means(ctags, res["cells"])
    c = list(csm.values())
    c_mean, c_sd = float(np.mean(c)), float(np.std(c, ddof=1))
    print("CONTROL seeds=%d  mean %.6f  sd %.6f" % (len(c), c_mean, c_sd))
    res["control_band"] = {"n_seeds": len(c), "mean": c_mean, "sd": c_sd,
                           "seed_means": csm}
    res["dfweak_arm"] = {"n_seeds": len(w), "range": [w[0], w[-1]], "seed_means": wsm}

    print()
    rungs = {}
    for kv, fams, primary in LADDER:
        tg = tags_for(fams)
        for x in tg:
            if x not in res["cells"]:
                res["cells"][x] = measure(x)
        sm = seed_means(tg, res["cells"])
        s = sorted(sm.values())
        e = {"KV": float(kv), "families": fams, "in_primary": primary,
             "n_seeds": len(s), "seed_means": sm}
        if len(s) < 4:
            e["VERDICT"] = "UNINFORMATIVE"
            e["why"] = "section 8: fewer than 4 Gate-G seeds (%d)" % len(s)
            print("  KV %-8s n=%d  UNINFORMATIVE" % (kv, len(s)))
        else:
            e["range"] = [s[0], s[-1]]
            e["mean"] = float(np.mean(s))
            e["z_vs_control"] = (e["mean"] - c_mean) / c_sd if c_sd > 0 else None
            gap = max(w[0] - s[-1], s[0] - w[-1])
            e["gap_vs_dfweak"] = gap
            e["separated"] = bool(gap > 0)
            if gap > 0:
                e["direction"] = "SPASTIC HIGH" if s[0] > w[-1] else "SPASTIC LOW"
                e["permutation"] = floor(s, w)
                e["VERDICT"] = "SEPARATED"
            else:
                e["VERDICT"] = "OVERLAP"
            print("  KV %-8s n=%d  A [%.6f, %.6f] mean %.6f  z=%+.2f  gap %+.6f  %s%s%s"
                  % (kv, len(s), s[0], s[-1], e["mean"], e["z_vs_control"], gap, e["VERDICT"],
                     "  " + e["direction"] if gap > 0 else "",
                     "" if primary else "   [NOT PRIMARY - seen]"))
        rungs[kv] = e
    res["rungs"] = rungs

    # section 4 prediction assessment, primary rungs only
    prim = [k for k, _, p in LADDER if p and rungs[k].get("VERDICT") in ("SEPARATED", "OVERLAP")]
    means = [(float(k), rungs[k]["mean"]) for k in prim]
    means.sort()
    mono = all(means[i][1] <= means[i + 1][1] + 1e-12 for i in range(len(means) - 1))
    seps = [(float(k), rungs[k]["VERDICT"] == "SEPARATED") for k in prim]
    seps.sort()
    thresh, clean = None, True
    for kvv, sep in seps:
        if sep and thresh is None:
            thresh = kvv
        if thresh is not None and not sep:
            clean = False
    dirs = [rungs[k].get("direction") for k in prim if rungs[k].get("VERDICT") == "SEPARATED"]
    res["PREDICTION_ASSESSMENT"] = {
        "primary_rungs": prim,
        "1_monotonic": {"holds": bool(mono), "rung_means": {str(a): b for a, b in means}},
        "2_threshold": {"registered_KVstar": 0.035,
                        "observed_KVstar": thresh,
                        "single_clean_threshold": bool(clean and thresh is not None),
                        "verdict": ("NO THRESHOLD" if thresh is None or not clean
                                    else ("CONFIRMED" if thresh == 0.035
                                          else "THRESHOLD AT %s, NOT THE REGISTERED 0.035" % thresh))},
        "3_direction": {"all_separations_spastic_high": bool(dirs and all(d == "SPASTIC HIGH" for d in dirs)),
                        "observed": dirs},
    }

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False))
    print()
    pa = res["PREDICTION_ASSESSMENT"]
    print("P1 monotonic          : %s" % pa["1_monotonic"]["holds"])
    print("P2 threshold          : %s" % pa["2_threshold"]["verdict"])
    print("P3 direction all HIGH : %s  %s" % (pa["3_direction"]["all_separations_spastic_high"],
                                              pa["3_direction"]["observed"]))
    print("between-scenario      : %s" % between)
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
