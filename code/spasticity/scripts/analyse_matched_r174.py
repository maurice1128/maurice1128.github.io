# -*- coding: utf-8 -*-
"""Analyse the severity-matched comparison.

GOVERNED BY  paper/PREREG_3d_matched_r174.md
             sha256 3d62010f81bc5a62721b522432ea77756566d7bf2d6ff1182b9fd472e8d038d1

ORDER IS FIXED BY THE REGISTRATION AND NOTHING IS SKIPPED:
  1  calibration gate on ALL THREE channels, incl. ank_hs_LmR (r169 checked two of three,
     and the unchecked one was the channel its own section 5 gate ran on)
  2  Gate G from the .sto -- duration and GRF cycles. FITNESS IS NOT THE CRITERION.
  3  ACHIEVED dose on the delivered cells, against the SPECIFIED 13.592 N
  4  the primary: S050 vs the matched weak rung, exact two-sided MWU 6 v 6, Bonferroni x2

Replay (sconecmd -e) evaluates an already-converged par to produce kinematics. Not an
optimisation, not --run, not --launch.
"""
import io
import os
import sys
import glob
import json
import math
import itertools
import subprocess

HERE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
sys.path.insert(0, HERE)
import numpy as np
import sto_utils as S

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "MATCHED_RESULT_r174.json")
SCONE = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SEEDS = [101, 102, 103, 104, 105, 106]
MIN_DUR, MIN_CYC, MIN_SEEDS, SETTLE = 9.73, 5, 4, 1.0
TOL = 1e-9
BONF = 2
FLOOR_X2 = 0.4166666666666667
FMAX = {"soleus_l": 3549.0, "gastroc_l": 2241.0, "tib_ant_l": 1759.0}
KV = 0.050
SPEC_DOSE = 13.592
SPASTIC_DOSE_CTRL = 13.627
PREREG = "3d62010f81bc5a62721b522432ea77756566d7bf2d6ff1182b9fd472e8d038d1"

ARMS = [("S050  KV 0.050",  "R151S",    "spastic", None),
        ("W870  x0.870",    "R174W870", "weak",    0.870),
        ("W892  x0.892",     "R174W892", "weak",   0.892),
        ("W915  x0.915",    "R174W915", "weak",    0.915)]
CH = ["ankle_angle_LmR", "hip_flexion_LmR"]


def die(m):
    print("\n" + "=" * 92); print("STOP -- %s" % m); print("Nothing reported."); print("=" * 92)
    sys.exit(2)


def hist(d):
    h = os.path.join(d, "history.txt")
    return sum(1 for _ in io.open(h, errors="replace")) if os.path.exists(h) else 0


def rdir(tag):
    g = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*"))
         if os.path.isdir(d) and hist(d) >= 91]
    if len(g) != 1:
        die("tag %s resolves to %d complete directories" % (tag, len(g)))
    return g[0]


def bpar(d):
    p = [x for x in glob.glob(os.path.join(d, "*.par")) if os.path.basename(x)[0].isdigit()]
    return sorted(p)[-1] if p else None


def sto_of(d):
    s = glob.glob(os.path.join(d, "*.par.sto"))
    return sorted(s)[-1] if s else None


def cyc_of(cols, dat, t, t1):
    grf, thr = S.grf_vertical(cols, dat, "l")
    if grf is None:
        return []
    idx = S.heel_strikes(t, grf, thresh=thr)
    c = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
         if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= t1]
    return c[:-1] if len(c) >= 2 else c


def rom(cols, dat, chan, cyc):
    v = S.col(cols, dat, chan)
    return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)


def hsang(cols, dat, chan, cyc):
    v = S.col(cols, dat, chan)
    return sum(math.degrees(v[a]) for a, _ in cyc) / len(cyc)


def measure(sto, t1):
    cols, dat = S.load_sto(sto)
    t = list(S.col(cols, dat, "time"))
    c = cyc_of(cols, dat, t, t1)
    if not c:
        return None
    return {"n_cycles": len(c), "t_end": t[-1],
            "ankle_angle_LmR": rom(cols, dat, "ankle_angle_l", c) - rom(cols, dat, "ankle_angle_r", c),
            "hip_flexion_LmR": rom(cols, dat, "hip_flexion_l", c) - rom(cols, dat, "hip_flexion_r", c),
            "ank_hs_LmR": hsang(cols, dat, "ankle_angle_l", c) - hsang(cols, dat, "ankle_angle_r", c)}


def achieved_dose(sto, t1, kind, scale):
    """Section 3: the dose ACTUALLY delivered on the cell's own achieved gait."""
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), float)
    c = cyc_of(cols, dat, t, t1)
    if not c:
        return None
    a, b = c[0][0], c[-1][1]
    if kind == "weak":
        f = np.asarray(S.col(cols, dat, "tib_ant_l.F"), float)[a:b] * FMAX["tib_ant_l"]
        return float((1.0 - scale) * np.mean(np.abs(f)))
    tot = np.zeros(b - a)
    for m in ("soleus_l", "gastroc_l"):
        v = np.asarray(S.col(cols, dat, m + ".ce_vel_norm"), float)[a:b]
        u = np.asarray(S.col(cols, dat, m + ".excitation"), float)[a:b]
        du = np.minimum(KV * np.maximum(0.0, v), np.maximum(0.0, 1.0 - u))
        tot = tot + du * FMAX[m]
    return float(np.mean(tot))


def mwu(a, b):
    n, m = len(a), len(b)
    obs = sum(1 for x in a for y in b if x > y) + 0.5 * sum(1 for x in a for y in b if x == y)
    allv = list(a) + list(b)
    cnt = tot = 0
    for cc in itertools.combinations(range(n + m), n):
        A = [allv[i] for i in cc]
        B = [allv[i] for i in range(n + m) if i not in cc]
        u = sum(1 for x in A for y in B if x > y) + 0.5 * sum(1 for x in A for y in B if x == y)
        tot += 1
        if abs(u - n * m / 2.0) >= abs(obs - n * m / 2.0) - 1e-9:
            cnt += 1
    return obs / (n * m), cnt / float(tot)


# ---------------------------------------------------------------- replay
runs = {}
for lab, pre, kind, sc in ARMS:
    for s in SEEDS:
        runs[(pre, s)] = rdir("%s_s%d" % (pre, s))
need = [d for d in runs.values() if sto_of(d) is None]
if need:
    print("replaying %d cells (sconecmd -e, evaluation of a converged par)" % len(need))
    for d in need:
        subprocess.run([SCONE, "-e", bpar(d)], capture_output=True, timeout=900, cwd=d)
    if [d for d in runs.values() if sto_of(d) is None]:
        die("replay produced no .sto")
    print("done\n")

# ---------------------------------------------------------------- 1. calibration
print("=" * 92)
print("1. CALIBRATION GATE -- reused R151S must reproduce r169's endpoints on ALL THREE channels")
print("=" * 92)
lad = json.load(io.open(os.path.join(PAPER, "LADDER_RESULT_r169.json"), encoding="utf-8"))
ref = lad["rung_summary"]["S050"]
T1_R169 = lad["window"][1]
cal = {}
for s in SEEDS:
    cal[s] = measure(sto_of(runs[("R151S", s)]), T1_R169)
fails = 0
for c in CH + ["ank_hs_LmR"]:
    got = float(np.mean([cal[s][c] for s in SEEDS]))
    want = ref[c]["mean"]
    ok = abs(got - want) <= TOL
    fails += (not ok)
    print("  %-18s recomputed %16.10f   r169 %16.10f   %s"
          % (c, got, want, "OK" if ok else "*** MISMATCH ***"))
if fails:
    die("%d of 3 channels failed to reproduce r169 to %g" % (fails, TOL))
print("\n  3/3 reproduce, including ank_hs_LmR -- the channel r169's own calibration skipped.")

# ---------------------------------------------------------------- 2. Gate G
print("\n" + "=" * 92)
print("2. GATE G from the .sto -- >= %.2f s AND >= %d cycles, >= %d of 6. FITNESS IS NOT THE CRITERION."
      % (MIN_DUR, MIN_CYC, MIN_SEEDS))
print("=" * 92)
gate, per = {}, {}
for lab, pre, kind, sc in ARMS:
    durs, cycs = [], []
    for s in SEEDS:
        cols, dat = S.load_sto(sto_of(runs[(pre, s)]))
        t = list(S.col(cols, dat, "time"))
        c = cyc_of(cols, dat, t, t[-1])
        durs.append(t[-1]); cycs.append(len(c))
        per["%s_%d" % (pre, s)] = {"dur": t[-1], "cycles": len(c)}
    npass = sum(1 for d, c in zip(durs, cycs) if d >= MIN_DUR and c >= MIN_CYC)
    gate[pre] = {"label": lab, "kind": kind, "scale": sc, "durations": durs, "cycles": cycs,
                 "n_pass": npass, "admitted": npass >= MIN_SEEDS}
    print("  %-16s %s  cycles %s  -> %d/6 %s"
          % (lab, " ".join("%5.2f" % x for x in durs), " ".join("%2d" % x for x in cycs),
             npass, "ADMITTED" if npass >= MIN_SEEDS else "*** DROPPED ***"))

adm = [p for p in gate if gate[p]["admitted"]]
if "R151S" not in adm or "R174W892" not in adm:
    die("the matched pair is not both admitted; branch NO DEFENSIBLE MATCH")

T1 = min(min(gate[p]["durations"]) for p in adm)
print("\n  common window across admitted arms: [%.2f, %.4f]" % (SETTLE, T1))

# ---------------------------------------------------------------- 3. achieved dose
print("\n" + "=" * 92)
print("3. ACHIEVED dose on the delivered cells vs the SPECIFIED %.3f N" % SPEC_DOSE)
print("=" * 92)
dose = {}
for lab, pre, kind, sc in ARMS:
    v = [achieved_dose(sto_of(runs[(pre, s)]), T1, kind, sc) for s in SEEDS]
    dose[pre] = v
    spec = SPASTIC_DOSE_CTRL if kind == "spastic" else (1 - sc) * 125.853
    print("  %-16s achieved mean %8.3f N  [%7.3f, %7.3f]   specified %8.3f N   drift %+7.3f N (%+.1f%%)"
          % (lab, np.mean(v), min(v), max(v), spec, np.mean(v) - spec,
             100 * (np.mean(v) - spec) / spec))
gapN = float(np.mean(dose["R174W892"]) - np.mean(dose["R151S"]))
print("\n  ACHIEVED MATCH GAP (weak x0.892 minus spastic KV 0.050): %+.3f N  (%.1f%% of the spastic dose)"
      % (gapN, 100 * gapN / np.mean(dose["R151S"])))

# ---------------------------------------------------------------- 4. primary
print("\n" + "=" * 92)
print("4. PRIMARY -- S050 vs W892 at matched upstream dose, exact two-sided MWU 6 v 6, Bonferroni x%d" % BONF)
print("=" * 92)
vals = {}
for lab, pre, kind, sc in ARMS:
    for s in SEEDS:
        vals[(pre, s)] = measure(sto_of(runs[(pre, s)]), T1)
prim = {}
print("%-18s %11s %11s %8s %10s %10s %9s" % ("endpoint", "S050 mean", "W892 mean", "AUC", "p_raw", "p_adj", "verdict"))
for c in CH:
    a = [vals[("R151S", s)][c] for s in SEEDS]
    b = [vals[("R174W892", s)][c] for s in SEEDS]
    auc, p = mwu(a, b)
    padj = min(1.0, p * BONF)
    d = abs(auc - 0.5)
    verd = "SEPARATES" if padj < 0.05 else ("UNRESOLVED" if d < FLOOR_X2 else "NO")
    prim[c] = {"S_mean": float(np.mean(a)), "W_mean": float(np.mean(b)), "S": a, "W": b,
               "auc": auc, "p_raw": p, "p_adj": padj, "abs_auc_minus_half": d, "verdict": verd}
    print("%-18s %11.4f %11.4f %8.4f %10.6f %10.6f %9s" % (c, np.mean(a), np.mean(b), auc, p, padj, verd))

sep = [c for c in CH if prim[c]["verdict"] == "SEPARATES"]
branch = ("MATCH FOUND, ENDPOINTS SEPARATE" if sep else
          "MATCH FOUND, ENDPOINTS DO NOT SEPARATE")
print("\n  BRANCH: %s   separating: %r" % (branch, sep))
print("  floor: at 6 v 6 under x%d the smallest declarable |AUC-0.5| is %.4f" % (BONF, FLOOR_X2))

# brackets, for the knife-edge check registered in section 3
print("\n  BRACKETS (registered so a result at the match cannot be a knife-edge artifact):")
for pre in ("R174W870", "R174W915"):
    if pre not in adm:
        print("    %s DROPPED" % pre)
        continue
    for c in CH:
        a = [vals[("R151S", s)][c] for s in SEEDS]
        b = [vals[(pre, s)][c] for s in SEEDS]
        auc, p = mwu(a, b)
        print("    %-10s %-18s AUC %.4f  p %.6f  p_adj %.6f"
              % (pre, c, auc, p, min(1.0, p * BONF)))

json.dump({"prereg_sha256": PREREG, "calibration": "PASSED 3/3 to 1e-9", "window": [SETTLE, T1],
           "gate": gate, "per_seed": per, "achieved_dose": dose,
           "achieved_match_gap_N": gapN, "primary": prim, "branch": branch,
           "floor_x2": FLOOR_X2,
           "per_cell": {"%s_%d" % k: v for k, v in vals.items()}},
          io.open(OUT, "w", encoding="utf-8"), indent=1,
          default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("\nwrote %s" % OUT)
