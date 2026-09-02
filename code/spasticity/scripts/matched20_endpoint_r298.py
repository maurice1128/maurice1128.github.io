"""matched20_endpoint_r298.py -- the endpoints of PREREG_matched20_r289.md (863f1376...)
and PREREG_clinical_r292.md (99fdf75a...), computed only now that the r289 arm has STOPPED.

r289 section 4 registers ONE comparison: completing spastic cells against the completing
weakness cells, POOLED -- "every dorsiflexor-weakness and plantarflexor-weakness cell with
t_end = 20.000 s". That pooled endpoint is computed and reported exactly as registered.

r292, hashed while r289 was at 4 of 12 and 0 analysed, registers the SPLIT and predicts in
advance that the pooled endpoint returns rung 4 OVERLAP by construction, because the two
weakness families sit on opposite sides of the knee.

  READING C  clinical pair      : completing spastic vs DORSIFLEXOR-weakness completers
  READING P  anatomy-matched    : completing spastic vs PLANTARFLEXOR-weakness completers

Endpoint: knee_angle_LmR, hipgap_r220.py convention, window [1.00, 9.73], drop the last
cycle, r281 guard. hip_flexion_LmR deposited as secondary, never promoted.
Read-only.
"""
import glob
import io
import itertools
import json
import math
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
FULL = 20.0
ENDPOINT = "knee_angle_LmR"
ALSO = "hip_flexion_LmR"

DF_ARMS = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    assert len(g) == 1, "%s -> %d dirs" % (tag, len(g))
    return g[0]


def measure(tag):
    try:
        d = rd(tag)
    except AssertionError as e:
        return {"tag": tag, "error": str(e)}
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        return {"tag": tag, "error": "no .par.sto"}
    cols, dat = S.load_sto(stos[-1])
    t = list(S.col(cols, dat, "time"))
    t_end = float(t[-1])
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    allc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    out = {"tag": tag, "t_end_s": t_end, "n_cycles": len(allc),
           "completes": bool(t_end >= FULL - 1e-6)}
    if t_end < T1 or not win:
        out.update({"measured": False, ENDPOINT: None, ALSO: None})
        return out

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in win) / len(win)

    out.update({"measured": True,
                ENDPOINT: rom("knee_angle_l") - rom("knee_angle_r"),
                ALSO: rom("hip_flexion_l") - rom("hip_flexion_r")})
    return out


def ladder(sp, wk, predict_disjoint_weak_positive=True):
    if len(sp) < 3 or len(wk) < 3:
        return {"RUNG": "1 UNINFORMATIVE", "n_spastic": len(sp), "n_weakness": len(wk)}
    disjoint = (min(wk) > max(sp)) or (min(sp) > max(wk))
    r = {"n_spastic": len(sp), "n_weakness": len(wk),
         "spastic_range": [min(sp), max(sp)], "weakness_range": [min(wk), max(wk)],
         "disjoint": bool(disjoint)}
    if disjoint:
        r["gap"] = (min(wk) - max(sp)) if min(wk) > max(sp) else (min(sp) - max(wk))
        if all(v > 0 for v in wk) and all(v < 0 for v in sp):
            r["RUNG"] = "2 DISJOINT-AS-PREDICTED"
        else:
            r["RUNG"] = "3 DISJOINT-OPPOSITE"
        allv = sp + wk
        n1 = len(sp)
        tot = cnt = 0
        obs = r["gap"]
        if len(allv) <= 24:
            for comb in itertools.combinations(range(len(allv)), n1):
                a = [allv[i] for i in comb]
                b = [allv[i] for i in range(len(allv)) if i not in comb]
                g = max(min(b) - max(a), min(a) - max(b))
                tot += 1
                if g >= obs - 1e-12:
                    cnt += 1
            r["permutation"] = {"assignments": tot, "count_ge_observed": cnt,
                                "floor": 1.0 / tot,
                                "note": "reported as a floor, never as a p-value"}
        else:
            r["permutation"] = {"skipped": "C(%d,%d) too large to enumerate" % (len(allv), n1)}
    else:
        r["RUNG"] = "4 OVERLAP"
        r["gap"] = None
    return r


def main():
    spastic = []
    for kv in ("0125", "00625"):
        for s in range(101, 107):
            spastic.append(measure("R289KV%s_s%d" % (kv, s)))
    df = [measure("%s_s%d" % (a, s)) for a in DF_ARMS for s in range(101, 107)]
    pf = []
    for pre in ("R276WPF005", "R276WPF010", "R276WPF020", "R285BF007", "R285BF008"):
        pf += [measure("%s_s%d" % (pre, s)) for s in range(101, 107)]
    for d in sorted(glob.glob(os.path.join(RES, "R287BF*"))):
        pf.append(measure(os.path.basename(d).split(".")[0]))

    def vals(rows, ch=ENDPOINT):
        return [r[ch] for r in rows
                if r.get("measured") and r.get("completes") and r.get(ch) is not None]

    sp_k, sp_h = vals(spastic), vals(spastic, ALSO)
    df_k, df_h = vals(df), vals(df, ALSO)
    pf_k, pf_h = vals(pf), vals(pf, ALSO)

    res = {
        "round": 298,
        "prereg_r289": "863f1376dc9b2ebb2e553c1a75a8047a2d14b29d9280e2a5171bb3ed3b0a59e0",
        "prereg_r292": "99fdf75a3ac72fa0e55b4747b78d2f42962db5808c980549463583c431a87397",
        "status": "computed only after the r289 arm stopped; its launcher read t_end only",
        "n_completing_spastic": len(sp_k),
        "n_completing_DF": len(df_k), "n_completing_PF": len(pf_k),
        "r289_REGISTERED_POOLED": ladder(sp_k, df_k + pf_k),
        "r292_READING_C_clinical_pair": ladder(sp_k, df_k),
        "r292_READING_P_anatomy_matched": ladder(sp_k, pf_k),
        "hip_secondary": {
            "note": "deposited, NOT the endpoint, not promoted",
            "spastic_range": [min(sp_h), max(sp_h)] if sp_h else None,
            "DF_range": [min(df_h), max(df_h)] if df_h else None,
            "PF_range": [min(pf_h), max(pf_h)] if pf_h else None,
            "reading_C_hip": ladder(sp_h, df_h),
            "completer_band_r279": [-0.8443, 1.1824],
            "faller_band_r279": [-4.4908, -1.2099]},
        "cells": {"spastic": spastic, "DF": df, "PF": pf}}

    io.open(os.path.join(PAPER, "MATCHED20_ENDPOINT_r298.json"), "w",
            encoding="utf-8", newline="\n").write(json.dumps(res, indent=1) + "\n")

    print("completing cells: spastic %d, dorsiflexor %d, plantarflexor %d"
          % (len(sp_k), len(df_k), len(pf_k)))
    print("\nspastic  knee %+.4f .. %+.4f" % (min(sp_k), max(sp_k)))
    print("DF weak  knee %+.4f .. %+.4f" % (min(df_k), max(df_k)))
    print("PF weak  knee %+.4f .. %+.4f" % (min(pf_k), max(pf_k)))
    for k in ("r289_REGISTERED_POOLED", "r292_READING_C_clinical_pair",
              "r292_READING_P_anatomy_matched"):
        v = res[k]
        print("\n%-34s %s" % (k, v["RUNG"]))
        if "weakness_range" in v:
            print("   spastic %+.4f..%+.4f | weakness %+.4f..%+.4f | gap %s"
                  % (v["spastic_range"][0], v["spastic_range"][1],
                     v["weakness_range"][0], v["weakness_range"][1],
                     ("%+.4f" % v["gap"]) if v.get("gap") is not None else "-"))
            if "permutation" in v and "floor" in v["permutation"]:
                print("   permutation %d of %d, floor 1/%d"
                      % (v["permutation"]["count_ge_observed"],
                         v["permutation"]["assignments"], v["permutation"]["assignments"]))
    h = res["hip_secondary"]
    print("\nHIP SECONDARY (not the endpoint)")
    print("   spastic %+.4f..%+.4f | DF %+.4f..%+.4f -> %s"
          % (h["spastic_range"][0], h["spastic_range"][1], h["DF_range"][0], h["DF_range"][1],
             h["reading_C_hip"]["RUNG"]))
    print("   r279 completer band %s | faller band %s"
          % (h["completer_band_r279"], h["faller_band_r279"]))


if __name__ == "__main__":
    main()
