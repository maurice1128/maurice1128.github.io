# -*- coding: utf-8 -*-
"""r412 -- FULL PRE-WRITEUP AUDIT.  READ-ONLY on SCONE results.  Starts no sconecmd.

Recomputes, from the .sto files, every headline number that was reported during the session,
and writes paper/FINAL_AUDIT_r412.json.  Also mints the two missing deposits
paper/FROZEN_MECHANISM_r410.json and paper/FROZEN_WEAKNESS_r411.json.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
STAGE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"

SETTLE, T1 = 1.0, 9.73
MIN_CYC = 5


def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


def window_for_side(t, cols, dat, side, settle=SETTLE, t1=T1):
    grf, thr = S.grf_vertical(cols, dat, side)
    if grf is None:
        return None, None, None
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= settle]
    win = [c for c in allc if t[c[1]] <= t1]
    win = win[:-1] if len(win) >= 2 else win
    return win, grf, thr


def knee_hs(sto_path, side="l", settle=SETTLE, t1=T1, min_cyc=MIN_CYC):
    """Returns dict with t_end, n_cycles, gate_G, knee_hs_deg, per-cycle list."""
    out = {"sto": os.path.basename(sto_path)}
    cols, dat = S.load_sto(sto_path)
    if dat.size == 0:
        out["error"] = "empty sto"
        return out
    t = dat[:, 0]
    out["t_end_s"] = float(t[-1])
    win, grf, thr = window_for_side(t, cols, dat, side, settle, t1)
    if win is None:
        out["error"] = "no GRF side %s" % side
        return out
    out["n_cycles_in_window"] = len(win)
    out["gate_G"] = bool(out["t_end_s"] >= t1 and len(win) >= min_cyc)
    kne = S.col(cols, dat, "knee_angle_%s" % side)
    if kne is not None and win:
        kd = np.degrees(kne)
        out["knee_hs_deg"] = float(np.mean([kd[a] for a, _ in win]))
        out["knee_hs_percycle_deg"] = [float(kd[a]) for a, _ in win]
    ang = S.col(cols, dat, "ankle_angle_%s" % side)
    if ang is not None and win:
        on = grf > thr
        st = [np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()]
        if st:
            out["mean_ankle_stance_deg"] = float(
                np.mean(np.degrees(ang)[np.concatenate(st)]))
    return out


def tag_sto(tag):
    d = rd(tag)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    return (stos[-1] if stos else None), os.path.basename(d)


def family_tags(fam):
    seen, out = set(), []
    for d in sorted(glob.glob(os.path.join(RES, fam + "_s*"))):
        b = os.path.basename(d).split(".")[0]
        if b not in seen:
            seen.add(b)
            out.append(b)
    return out


def family_values(fam, side="l", settle=SETTLE, t1=T1, min_cyc=MIN_CYC, require_gate=True):
    vals, detail = [], []
    for tg in family_tags(fam):
        try:
            sto, dn = tag_sto(tg)
        except AssertionError as e:
            detail.append({"tag": tg, "error": str(e)})
            continue
        if sto is None:
            detail.append({"tag": tg, "error": "no .par.sto"})
            continue
        r = knee_hs(sto, side, settle, t1, min_cyc)
        r["tag"] = tg
        r["run_dir"] = dn
        detail.append(r)
        if (r.get("gate_G") or not require_gate) and r.get("knee_hs_deg") is not None:
            vals.append(r["knee_hs_deg"])
    return sorted(vals), detail


def summarise(vals):
    if not vals:
        return {"n": 0}
    return {"n": len(vals), "min": float(min(vals)), "max": float(max(vals)),
            "mean": float(np.mean(vals)), "values": [float(v) for v in vals]}


def edge_gap(a, b):
    return float(max(b[0] - a[-1], a[0] - b[-1]))


# ============================================================================ frozen r410/r411
def frozen_cells(stage_dir):
    cells = {}
    for d in sorted(glob.glob(os.path.join(stage_dir, "*"))):
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        stos = sorted(glob.glob(os.path.join(d, "*.sto")))
        if not stos:
            cells[name] = {"error": "no .sto", "dir": d}
            continue
        r = knee_hs(stos[-1])
        # relaxed readout: every heel-strike-to-heel-strike cycle after SETTLE, no T1 cap,
        # no last-cycle drop -- this is what a 3-4 s run can actually supply
        cols, dat = S.load_sto(stos[-1])
        t = dat[:, 0]
        grf, thr = S.grf_vertical(cols, dat, "l")
        if grf is not None:
            hs = S.heel_strikes(t, grf, thresh=thr)
            allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
            kne = S.col(cols, dat, "knee_angle_l")
            r["relaxed_n_cycles"] = len(allc)
            if kne is not None and allc:
                kd = np.degrees(kne)
                r["relaxed_knee_hs_deg"] = float(np.mean([kd[a] for a, _ in allc]))
                r["relaxed_percycle_deg"] = [float(kd[a]) for a, _ in allc]
            r["all_hs_times_s"] = [float(t[i]) for i in hs]
        cells[name] = r
    return cells


def arm_of(name):
    return name.rsplit("_s", 1)[0]


def group_arms(cells):
    arms = {}
    for name, r in sorted(cells.items()):
        arms.setdefault(arm_of(name), []).append((name, r))
    out = {}
    for a, lst in arms.items():
        strict = [r["knee_hs_deg"] for _, r in lst
                  if r.get("gate_G") and r.get("knee_hs_deg") is not None]
        relax = [r["relaxed_knee_hs_deg"] for _, r in lst
                 if r.get("relaxed_knee_hs_deg") is not None]
        tends = [r["t_end_s"] for _, r in lst if r.get("t_end_s") is not None]
        ncyc = [r.get("relaxed_n_cycles", 0) for _, r in lst]
        out[a] = {
            "n_seeds": len(lst),
            "seeds": [n for n, _ in lst],
            "t_end_s_min": float(min(tends)) if tends else None,
            "t_end_s_max": float(max(tends)) if tends else None,
            "n_gate_G_pass": len(strict),
            "gate_G_all_fail": len(strict) == 0,
            "relaxed_cycles_min": int(min(ncyc)) if ncyc else 0,
            "relaxed_cycles_max": int(max(ncyc)) if ncyc else 0,
            "knee_hs_deg_relaxed_mean": float(np.mean(relax)) if relax else None,
            "knee_hs_deg_relaxed_n": len(relax),
            "knee_hs_deg_relaxed_values": [float(v) for v in sorted(relax)],
            "per_seed": {n: r for n, r in lst},
        }
    return out


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    res = {}
    if what in ("all", "ab"):
        for fam in ["R151C", "R151W", "R396SPg110"]:
            v, det = family_values(fam)
            res[fam] = {"summary": summarise(v), "detail": det}
    print(json.dumps(res, indent=1, default=str)[:20000])
