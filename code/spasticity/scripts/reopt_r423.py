# -*- coding: utf-8 -*-
"""r423: frozen versus re-optimised, matched dose, both sides required to pass Gate G.

Registered by paper/PREREG_reopt_r423.md, sha256 5f1a285234ca2274..., hashed before any low-dose
frozen cell was read. No optimisation is run; this is `sconecmd -e` replay inside our own staging
tree, so it consumes no Hyfydy optimiser time and never writes to the SCONE results directory.
"""
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
SRC = os.path.join(BASE, "frozen2_r410")
DST = os.path.join(BASE, "reopt_r423")
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "REOPT_RESULT_r423.json")

RUNGS = ["0.0125", "0.025"]
SEEDS = [101, 102, 103, 104, 105, 106]
# template, muscles to keep
ARMS = {"GASONLY": ("R410GAS", ("gastroc",)),
        "SOLONLY": ("R410SOL", ("soleus",)),
        "BOTH": ("R410BOTH", ("soleus", "gastroc"))}
SETTLE, T1 = 1.0, 9.73

SPANS = {"GASONLY": {"knee", "ankle"}, "SOLONLY": {"ankle"}, "BOTH": {"knee", "ankle"}}


def kvre(m):
    return re.compile(r"(target\s*=\s*%s\s+delay\s*=\s*0\.020\s+KV\s*=\s*)([0-9.]+)" % m)


def build(arm, kv, seed):
    tmpl, keep = ARMS[arm]
    src = os.path.join(SRC, "%s_s%d" % (tmpl, seed))
    name = "R423%s%s_s%d" % (arm, kv.replace(".", ""), seed)
    dst = os.path.join(DST, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    stale = os.path.join(dst, "FROZEN.par.sto")
    if os.path.exists(stale):
        os.remove(stale)
    cfg = os.path.join(dst, "config.scone")
    s = io.open(cfg, encoding="utf-8").read()
    i = s.index("name = SpasticL")                  # anchored, see build_slack_r418.py
    head, blk = s[:i], s[i:]
    for m in keep:
        mm = kvre(m).search(blk)
        assert mm, "%s: %s reflex absent from template %s" % (name, m, tmpl)
        blk = blk[:mm.start(2)] + kv + blk[mm.end(2):]
        assert kvre(m).search(blk).group(2) == kv
    for m in ("soleus", "gastroc"):
        present = bool(kvre(m).search(blk))
        assert present == (m in keep), "%s: %s present=%s keep=%s" % (name, m, present, keep)
    s2 = (head + blk).replace("signature_prefix = %s_s%d" % (tmpl, seed),
                              "signature_prefix = %s" % name)
    assert tmpl not in s2, "%s: stale prefix" % name
    io.open(cfg, "w", encoding="utf-8", newline="").write(s2)
    return dst, name


def measure(d):
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
    if not ok:
        return {"gate_G": False, "t_end": float(t[-1]), "n_cycles": len(win)}
    on = grf > thr
    st = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    an = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    hp = np.degrees(S.col(cols, dat, "hip_flexion_l"))
    sw = [float(t[b] - t[a]) for a, b in win]
    return {"gate_G": True, "t_end": float(t[-1]), "n_cycles": len(win),
            "cycle_s_mean": float(np.mean(sw)),
            "KNEE_ic": float(np.mean([kn[a] for a, _ in win])),
            "ANKLE_st": float(np.mean(an[st])),
            "HIP_ic": float(np.mean([hp[a] for a, _ in win]))}


def stat(vals):
    if not vals:
        return None
    return {"n": len(vals), "mean": float(np.mean(vals)),
            "range": [float(min(vals)), float(max(vals))]}


def overlaps(a, b):
    return not (a["range"][1] < b["range"][0] or b["range"][1] < a["range"][0])


if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    res = {"round": "REOPT_RESULT_r423", "registration": "PREREG_reopt_r423.md",
           "registration_sha256":
               "5f1a285234ca22742bc78ff6f028ad72a6cb2c1941c552c5a21b1191dc3b7113",
           "no_optimisation_run": True, "frozen": {}, "cells": {}}

    # frozen control, already on disk from r410
    ctrl = {}
    for s in SEEDS:
        d = os.path.join(SRC, "R410NONE_s%d" % s)
        ctrl["R410NONE_s%d" % s] = measure(d)
    res["cells"].update(ctrl)
    cg = [c for c in ctrl.values() if c and c["gate_G"]]
    res["frozen_control"] = {"n_gate_G": len(cg),
                             **{k: stat([c[k] for c in cg]) for k in
                                ("KNEE_ic", "ANKLE_st", "HIP_ic")}}
    print("frozen control R410NONE: Gate G %d/6" % len(cg))

    print()
    print("%-9s %-7s %-4s %-22s %-22s %s" % ("arm", "KV", "n", "KNEE_ic", "ANKLE_st", "HIP_ic"))
    for kv in RUNGS:
        res["frozen"][kv] = {}
        for arm in ARMS:
            cells = {}
            for s in SEEDS:
                d, name = build(arm, kv, s)
                subprocess.run([SCONE, "-e", "FROZEN.par"], cwd=d, capture_output=True,
                               text=True, timeout=900)
                cells[name] = measure(d)
            res["cells"].update(cells)
            g = [c for c in cells.values() if c and c["gate_G"]]
            e = {"n_gate_G": len(g), "uninformative": len(g) < 4,
                 "t_end_range": [min(c["t_end"] for c in cells.values() if c),
                                 max(c["t_end"] for c in cells.values() if c)]}
            for k in ("KNEE_ic", "ANKLE_st", "HIP_ic", "cycle_s_mean"):
                e[k] = stat([c[k] for c in g])
            res["frozen"][kv][arm] = e
            if e["KNEE_ic"]:
                print("%-9s %-7s %-4d [%+7.3f,%+7.3f]  [%+7.3f,%+7.3f]  [%+7.3f,%+7.3f]"
                      % (arm, kv, len(g), e["KNEE_ic"]["range"][0], e["KNEE_ic"]["range"][1],
                         e["ANKLE_st"]["range"][0], e["ANKLE_st"]["range"][1],
                         e["HIP_ic"]["range"][0], e["HIP_ic"]["range"][1]))
            else:
                print("%-9s %-7s %-4d Gate G 0; t_end [%.2f, %.2f]"
                      % (arm, kv, len(g), e["t_end_range"][0], e["t_end_range"][1]))
            sys.stdout.flush()

    elig = [kv for kv in RUNGS
            if res["frozen"][kv]["GASONLY"]["n_gate_G"] >= 4
            and res["frozen"][kv]["SOLONLY"]["n_gate_G"] >= 4]
    res["reading_dose"] = elig[-1] if elig else None
    print()
    print("frozen-side eligible rungs: %s -> reading dose %s" % (elig, res["reading_dose"]))

    if not elig:
        res["VERDICT"] = ("UNINFORMATIVE -- the frozen side reaches 4/6 Gate G at neither dose. "
                          "Section 5 forbids substituting non-Gate-G frozen readouts, which is "
                          "the ground on which CORRECTION_r416 retired r410.")
    else:
        rd = res["reading_dose"]
        C = res["frozen_control"]
        F = res["frozen"][rd]
        R = json.load(io.open(os.path.join(PAPER, "SPANNING_RESULT_r421.json"), encoding="utf-8"))
        rd_key = {"0.0125": "0125", "0.025": "0250"}[rd]
        RA = R["by_rung"][rd_key]["arms"]
        RC = R["control_R151C"]

        def disp(side_arm, side_ctrl, k):
            return side_arm[k]["mean"] - side_ctrl[k]["mean"]

        res["displacement_vs_own_control"] = {"frozen": {}, "reoptimised": {}}
        for arm in ("GASONLY", "SOLONLY", "BOTH"):
            res["displacement_vs_own_control"]["frozen"][arm] = {
                k: disp(F[arm], C, k) for k in ("KNEE_ic", "ANKLE_st", "HIP_ic")
            } if F[arm]["KNEE_ic"] else None
            res["displacement_vs_own_control"]["reoptimised"][arm] = {
                k: disp(RA[arm], RC, k) for k in ("KNEE_ic", "ANKLE_st", "HIP_ic")}

        P = {}
        P["P1_frozen_hip_overlaps"] = {
            "GASONLY": F["GASONLY"]["HIP_ic"], "SOLONLY": F["SOLONLY"]["HIP_ic"],
            "overlap": overlaps(F["GASONLY"]["HIP_ic"], F["SOLONLY"]["HIP_ic"]),
            "reoptimised_hip_overlapped": overlaps(RA["GASONLY"]["HIP_ic"],
                                                   RA["SOLONLY"]["HIP_ic"]),
            "VERDICT": "HOLDS" if overlaps(F["GASONLY"]["HIP_ic"],
                                           F["SOLONLY"]["HIP_ic"]) else "FAILS"}
        fg = abs(res["displacement_vs_own_control"]["frozen"]["GASONLY"]["KNEE_ic"])
        fs_ = abs(res["displacement_vs_own_control"]["frozen"]["SOLONLY"]["KNEE_ic"])
        P["P2_frozen_knee_gastroc_dominates"] = {
            "abs_knee_disp_GASONLY": fg, "abs_knee_disp_SOLONLY": fs_,
            "reoptimised_were": {
                "GASONLY": abs(res["displacement_vs_own_control"]["reoptimised"]["GASONLY"]["KNEE_ic"]),
                "SOLONLY": abs(res["displacement_vs_own_control"]["reoptimised"]["SOLONLY"]["KNEE_ic"])},
            "VERDICT": "HOLDS" if fg > fs_ else "FAILS"}

        def offspan_fraction(dd, arm):
            tot = sum(abs(dd[k]) for k in ("KNEE_ic", "ANKLE_st", "HIP_ic"))
            off = sum(abs(dd[k]) for k, j in (("KNEE_ic", "knee"), ("ANKLE_st", "ankle"),
                                              ("HIP_ic", "hip")) if j not in SPANS[arm])
            return off / tot if tot else None
        offs = {side: {arm: offspan_fraction(res["displacement_vs_own_control"][side][arm], arm)
                       for arm in ("GASONLY", "SOLONLY")
                       if res["displacement_vs_own_control"][side][arm]}
                for side in ("frozen", "reoptimised")}
        lower = all(offs["frozen"].get(a) is not None
                    and offs["frozen"][a] < offs["reoptimised"][a] for a in offs["frozen"])
        P["P3_offspan_share_lower_when_frozen"] = {
            "off_span_share": offs, "VERDICT": "HOLDS" if lower else "FAILS"}
        moved = (F["GASONLY"]["ANKLE_st"]["mean"] != C["ANKLE_st"]["mean"]
                 and F["SOLONLY"]["ANKLE_st"]["mean"] != C["ANKLE_st"]["mean"])
        P["P4_frozen_ankle_moves_sanity"] = {
            "GASONLY_ankle_disp": res["displacement_vs_own_control"]["frozen"]["GASONLY"]["ANKLE_st"],
            "SOLONLY_ankle_disp": res["displacement_vs_own_control"]["frozen"]["SOLONLY"]["ANKLE_st"],
            "VERDICT": "HOLDS" if moved else "FAILS -- frozen injection had no effect; round void"}

        # section 6 duration control on the frozen side
        ct, ck = [], []
        for arm in ("GASONLY", "SOLONLY"):
            cs = [v for k, v in res["cells"].items()
                  if k.startswith("R423%s%s_" % (arm, rd.replace(".", ""))) and v and v["gate_G"]]
            tt = np.array([c["t_end"] for c in cs])
            kk = np.array([c["KNEE_ic"] for c in cs])
            ct += list(tt - tt.mean())
            ck += list(kk - kk.mean())
        bw = float(np.polyfit(ct, ck, 1)[0]) if len(set(ct)) > 1 else 0.0
        rw = float(np.corrcoef(ct, ck)[0, 1]) if len(set(ct)) > 1 else 0.0
        span = abs(F["GASONLY"]["KNEE_ic"]["mean"] - F["SOLONLY"]["KNEE_ic"]["mean"])
        tsp = abs(np.mean(F["GASONLY"]["t_end_range"]) - np.mean(F["SOLONLY"]["t_end_range"])) \
            if F["GASONLY"].get("t_end_range") else 0.0
        res["duration_control"] = {"pooled_slope_deg_per_s": bw, "pearson_r": rw,
                                   "t_end_span_s": float(tsp), "effect_deg": float(span),
                                   "fraction": float(abs(bw) * tsp / span) if span else None}
        res["duration_control"]["CONFOUNDED"] = bool(
            res["duration_control"]["fraction"] is not None
            and res["duration_control"]["fraction"] > 0.50)
        res["predictions"] = P
        held = [k for k, v in P.items() if v["VERDICT"] == "HOLDS"]
        res["VERDICT"] = "%d of %d hold at frozen KV %s: %s" % (
            len(held), len(P), rd, ", ".join(held) or "none")
        print()
        for k, v in P.items():
            print("  %-40s %s" % (k, v["VERDICT"]))
        print()
        print("off-span share  frozen %s" % offs["frozen"])
        print("                reopt  %s" % offs["reoptimised"])

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
    print()
    print("VERDICT:", res["VERDICT"])
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
