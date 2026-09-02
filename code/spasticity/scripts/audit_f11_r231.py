# -*- coding: utf-8 -*-
"""F11 -- can the deposited spastic hip_flexion_LmR values be re-derived from the archive?

Three of the six values behind the headline mean (-2.105) reportedly match no .sto. This
recomputes the r228 endpoint from EVERY .sto present in every spastic cell, using
ladder36_r228.py's definition transcribed exactly (its lines 24-43):

    cycles = left heel-strike delimited, fully inside [1.00, 9.73], last dropped
    rom(ch) = mean over cycles of degrees(max(v[a:b+1]) - min(v[a:b+1]))
    hip_flexion_LmR = rom(hip_flexion_l) - rom(hip_flexion_r)

PEAK-TO-PEAK EXCURSION DIFFERENCE, not a point-wise angle difference.

READ ONLY. Writes nothing into the corpus.
"""
import io
import os
import sys
import glob
import json
import math

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = [101, 102, 103, 104, 105, 106]
TAG = "R151S"
TOL = 5e-4


def endpoint(path, settle=SETTLE, t1=T1, drop_last=True):
    cols, dat = S.load_sto(path)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= settle and t[idx[k + 1]] <= t1]
    if drop_last:
        cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc:
        return None, 0

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)
    return rom("hip_flexion_l") - rom("hip_flexion_r"), len(cyc)


def main():
    dep = json.load(io.open(os.path.join(PAPER, "LADDER36_r228.json"),
                            encoding="utf-8"))["per_seed_hip_flexion_LmR"]["S"]
    deposited = dict(zip(SEEDS, dep))

    out = {"definition": "r228: peak-to-peak excursion difference, [1.00,9.73], last dropped",
           "tolerance": TOL, "deposited": deposited, "cells": {}}

    print("deposited spastic values: %s\n" % {k: round(v, 4) for k, v in deposited.items()})
    for s in SEEDS:
        ds = [x for x in glob.glob(os.path.join(RES, "%s_s%d.*" % (TAG, s)))
              if os.path.isdir(x)
              and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
        cell = {"n_dirs": len(ds), "deposited": deposited[s], "stos": [], "match": None}
        if len(ds) != 1:
            cell["error"] = "%d qualifying dirs" % len(ds)
            out["cells"][s] = cell
            print("s%d: %d qualifying dirs" % (s, len(ds)))
            continue
        d = ds[0]
        stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
        cell["dir"] = os.path.basename(d)
        cell["n_sto"] = len(stos)
        cell["r228_would_pick"] = os.path.basename(stos[-1]) if stos else None
        print("s%d  %d .sto   r228 picks %s   deposited %+.4f"
              % (s, len(stos), cell["r228_would_pick"], deposited[s]))
        for p in stos:
            v, nc = endpoint(p)
            hit = v is not None and abs(v - deposited[s]) < TOL
            cell["stos"].append({"sto": os.path.basename(p), "value": v, "n_cycles": nc,
                                 "matches_deposit": bool(hit),
                                 "mtime": os.path.getmtime(p)})
            if hit:
                cell["match"] = os.path.basename(p)
            flag = "  <== MATCHES DEPOSIT" if hit else ""
            picked = " [r228 picks this]" if p == stos[-1] else ""
            print("     %-34s %s  cyc %2d%s%s"
                  % (os.path.basename(p),
                     ("%+8.4f" % v) if v is not None else "   none ", nc, picked, flag))
        if cell["match"] is None:
            print("     >>> NO .sto IN THIS CELL REPRODUCES THE DEPOSITED VALUE")
        out["cells"][s] = cell
        print()

    unmatched = [s for s in SEEDS if out["cells"][s].get("match") is None]
    out["unmatched_seeds"] = unmatched
    out["n_unmatched"] = len(unmatched)
    json.dump(out, io.open(os.path.join(PAPER, "AUDIT_F11_r231.json"), "w",
                           encoding="utf-8"), indent=1)
    print("=" * 78)
    print("seeds with NO reproducing .sto: %r" % unmatched)
    print("wrote AUDIT_F11_r231.json")


if __name__ == "__main__":
    main()
