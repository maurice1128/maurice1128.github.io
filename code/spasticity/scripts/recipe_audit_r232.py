# -*- coding: utf-8 -*-
"""A -- two selection recipes, side by side, and what each does to the headline.

Two audits disagree about whether the deposited spastic values reproduce. Both may be right:

  RECIPE-L  sorted(glob("*.par.sto"))[-1]   lexicographically last = HIGHEST GENERATION
            -- what ladder36_r228.py literally does (its line 28)
  RECIPE-F  the replay of the LOWEST FIELD-3 .par = BEST FITNESS
            -- what PREREG_mechanism_r230.md section 8 registers

They differ only where a cell carries more than one .sto. Spastic cells carry 8-14; every
other arm carries one. That is why control, W800 and W950 reproduce under both and only the
spastic arm splits.

Endpoint is ladder36_r228.py's, transcribed exactly: per-cycle peak-to-peak EXCURSION
difference, window [1.00, 9.73], last cycle dropped, v[a:b+1] inclusive.

READ ONLY.
"""
import io
import os
import re
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
PAR_RE = re.compile(r"^(\d+)_([\d.]+)_([\d.]+)\.par$")

ARMS = [("S", "R151S"), ("W800", "R151W"), ("W870", "R174W870"), ("W892", "R174W892"),
        ("W900", "R169W090"), ("W915", "R174W915"), ("W950", "R169W095"), ("C", "R151C")]


def cell_dir(prefix, seed):
    ds = [x for x in glob.glob(os.path.join(RES, "%s_s%d.*" % (prefix, seed)))
          if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
    return ds[0] if len(ds) == 1 else (sorted(ds)[0] if ds else None)


def endpoint(path):
    cols, dat = S.load_sto(path)
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc:
        return None

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)
    return rom("hip_flexion_l") - rom("hip_flexion_r")


def recipe_L(d):
    s = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    return (s[-1] if s else None)


def recipe_F(d):
    best = None
    for f in os.listdir(d):
        m = PAR_RE.match(f)
        if not m:
            continue
        fit = float(m.group(3))
        if best is None or fit < best[0] or (fit == best[0] and int(m.group(1)) < best[1]):
            best = (fit, int(m.group(1)), f)
    if best is None:
        return None
    p = os.path.join(d, best[2] + ".sto")
    return p if os.path.exists(p) and os.path.getsize(p) > 0 else None


def main():
    dep = json.load(io.open(os.path.join(PAPER, "LADDER36_r228.json"),
                            encoding="utf-8"))["per_seed_hip_flexion_LmR"]
    out = {"recipes": {"L": "sorted(glob)[-1] = highest generation (ladder36_r228.py:28)",
                       "F": "lowest field-3 .par = best fitness (PREREG rev3 section 8)"},
           "arms": {}}
    print("%-5s %-4s | %-9s %-9s | %-9s %-9s | %s"
          % ("arm", "seed", "deposit", "RECIPE-L", "diff L", "RECIPE-F", "files differ?"))
    for tag, prefix in ARMS:
        rows = []
        for s in SEEDS:
            d = cell_dir(prefix, s)
            if d is None:
                rows.append({"seed": s, "error": "no qualifying dir"}); continue
            pl, pf = recipe_L(d), recipe_F(d)
            vl = endpoint(pl) if pl else None
            vf = endpoint(pf) if pf else None
            dv = dep[tag][SEEDS.index(s)] if tag in dep else None
            same = (pl == pf)
            rows.append({"seed": s, "deposited": dv, "L_value": vl, "F_value": vf,
                         "L_file": os.path.basename(pl) if pl else None,
                         "F_file": os.path.basename(pf) if pf else None,
                         "same_file": same, "n_sto": len(glob.glob(os.path.join(d, "*.par.sto"))),
                         "L_matches_deposit": (vl is not None and dv is not None
                                               and abs(vl - dv) < 5e-4),
                         "F_matches_deposit": (vf is not None and dv is not None
                                               and abs(vf - dv) < 5e-4)})
            print("%-5s %-4d | %+9.4f %+9.4f | %9.1e %+9.4f | %s"
                  % (tag, s, dv if dv is not None else float('nan'),
                     vl if vl is not None else float('nan'),
                     abs(vl - dv) if (vl is not None and dv is not None) else float('nan'),
                     vf if vf is not None else float('nan'),
                     "SAME" if same else "DIFFER (%d sto)" % rows[-1]["n_sto"]))
        out["arms"][tag] = rows
        print()

    # gap under both recipes
    def vals(tag, key):
        return [r[key] for r in out["arms"][tag] if r.get(key) is not None]
    res = {}
    for key, label in (("deposited", "DEPOSIT"), ("L_value", "RECIPE-L"), ("F_value", "RECIPE-F")):
        sm = max(vals("S", key))
        wk = [min(vals(t, key)) for t in ("W800", "W870", "W892", "W900", "W915", "W950")]
        res[label] = {"spastic_mean": sum(vals("S", key)) / len(vals("S", key)),
                      "spastic_max": sm, "weak_min_pooled": min(wk),
                      "gap": min(wk) - sm, "disjoint": bool(min(wk) > sm)}
    out["gap_analysis"] = res
    print("=" * 78)
    print("%-10s %-13s %-13s %-13s %-11s %s"
          % ("recipe", "spastic mean", "spastic max", "weak min", "gap", "DISJOINT?"))
    for k, v in res.items():
        print("%-10s %+13.4f %+13.4f %+13.4f %+11.4f  %s"
              % (k, v["spastic_mean"], v["spastic_max"], v["weak_min_pooled"], v["gap"],
                 "YES" if v["disjoint"] else "NO"))
    json.dump(out, io.open(os.path.join(PAPER, "RECIPE_AUDIT_r232.json"), "w",
                           encoding="utf-8"), indent=1)
    print("\nwrote RECIPE_AUDIT_r232.json")


if __name__ == "__main__":
    main()
