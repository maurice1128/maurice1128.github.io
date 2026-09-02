# -*- coding: utf-8 -*-
"""Covariate-residual test on the two (L-R) channels of the re-optimised 3D study.

GOVERNED BY  paper/PREREG_3d_residual_r168.md
             sha256 e2437a0f5d49da9e429aa36ac969873df28e4dde90527a495db48b356d3cb5b2
             hashed BEFORE this file was written and before any number of this test existed.

Where this script and that registration disagree, THE REGISTRATION DECIDES.

WHAT THIS DOES NOT DO
  - no simulation, no sconecmd, no -e replay, no --run, no --launch
  - never writes, moves or deletes anything under Documents\\SCONE\\results (read-only)
  - imports residual_test.py and sto_utils.py UNMODIFIED; both are registered scripts

ORDER IS FIXED BY THE REGISTRATION:
  section 5 calibration gate  ->  section 4 common-support gate  ->  section 3 residual
A failure at either gate stops the run; nothing partial is reported.
"""
import io
import os
import sys
import glob
import json
import math
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
import sto_utils as S
import residual_test                       # imported for provenance; main() is NOT called
assert hasattr(residual_test, "main")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PAPER = os.path.abspath(os.path.join(HERE, "..", "paper"))
DEPOSIT = os.path.join(PAPER, "REOPT3D_RESULT_r151.json")
OUT = os.path.join(PAPER, "RESIDUAL3D_RESULT_r168.json")
RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SETTLE = 1.0
TOL = 1e-9
BONF = 2                                   # registered pool: 2 channels, fixed in section 3
FLOOR_X2 = 0.4166666666666667              # section 2, |AUC-0.5| declarable at 6v6 under x2
CHANNELS = ["ankle_angle_LmR", "hip_flexion_LmR"]


def die(msg):
    print("\n" + "=" * 78)
    print("STOP -- %s" % msg)
    print("Nothing written.")
    print("=" * 78)
    sys.exit(2)


# ------------------------------------------------------------------ exact MWU
def mwu_two_sided(a, b):
    """Exact two-sided Mann-Whitney by enumeration, identical to analyse_reopt_r151.py."""
    n, m = len(a), len(b)
    obs = sum(1 for x in a for y in b if x > y) + 0.5 * sum(1 for x in a for y in b if x == y)
    allv = list(a) + list(b)
    cnt = tot = 0
    for comb in itertools.combinations(range(n + m), n):
        A = [allv[i] for i in comb]
        B = [allv[i] for i in range(n + m) if i not in comb]
        u = sum(1 for x in A for y in B if x > y) + 0.5 * sum(1 for x in A for y in B if x == y)
        tot += 1
        if abs(u - n * m / 2.0) >= abs(obs - n * m / 2.0) - 1e-9:
            cnt += 1
    return obs / (n * m), cnt / float(tot)


# ------------------------------------------------ section 5: calibration gate
print("=" * 78)
print("SECTION 5 -- CALIBRATION GATE (refuse to report anything new until a known")
print("             number reproduces from the per-seed values)")
print("=" * 78)

if not os.path.exists(DEPOSIT):
    die("deposit not found: %s" % DEPOSIT)
dep = json.load(io.open(DEPOSIT, encoding="utf-8"))
per = dep["endpoints"]
known = dep["registered_asymmetry_endpoints"]["endpoints"]
WINDOW = dep["window"]
T0, T1 = float(WINDOW[0]), float(WINDOW[1])

if abs(T0 - SETTLE) > TOL:
    die("deposit window lower bound %.6f != registered settle %.2f" % (T0, SETTLE))

PAIRS = {"ankle_angle_LmR": ("ankle_angle_l", "ankle_angle_r"),
         "hip_flexion_LmR": ("hip_flexion_l", "hip_flexion_r"),
         "knee_angle_LmR": ("knee_angle_l", "knee_angle_r"),
         "hip_adduction_LmR": ("hip_adduction_l", "hip_adduction_r")}

arms = {"S": [], "W": []}
for a in ("S", "W"):
    for s in SEEDS:
        k = "%s_%d" % (a, s)
        if k in per:
            arms[a].append(k)
for a in ("S", "W"):
    if len(arms[a]) != 6:
        die("arm %s carries %d seeds, registration section 5 requires exactly 6" % (a, len(arms[a])))

lmr = {}
for ch, (L, R) in PAIRS.items():
    lmr[ch] = {k: per[k][L] - per[k][R] for k in arms["S"] + arms["W"]}

fails = 0
print("%-20s %14s %14s %14s %14s" % ("channel", "S mean recomp", "S mean deposit", "W recomp", "W deposit"))
for ch in PAIRS:
    sm = float(np.mean([lmr[ch][k] for k in arms["S"]]))
    wm = float(np.mean([lmr[ch][k] for k in arms["W"]]))
    ds, dw = known[ch]["S_mean"], known[ch]["W_mean"]
    ok = abs(sm - ds) <= TOL and abs(wm - dw) <= TOL
    fails += (not ok)
    print("%-20s %14.9f %14.9f %14.9f %14.9f  %s"
          % (ch, sm, ds, wm, dw, "OK" if ok else "*** MISMATCH ***"))
if fails:
    die("%d of 4 registered (L-R) means did not reproduce to %g" % (fails, TOL))
print("\n  4/4 reproduce to %g. Window [%.2f, %.4f] confirmed from the deposit." % (TOL, T0, T1))
print("  Gate PASSED -- new numbers may now be computed.")


# ---------------------------------- covariate: ank_hs_LmR, read-only from .sto
def find_run(tag):
    ds = [d for d in glob.glob(os.path.join(RESULTS, tag + ".*")) if os.path.isdir(d)]
    ds = [d for d in ds if os.path.exists(os.path.join(d, "history.txt"))]
    return sorted(ds)[0] if ds else None


def sto_for(d):
    s = glob.glob(os.path.join(d, "*.par.sto"))
    return sorted(s)[-1] if s else None


def ank_hs_lmr(sto):
    """Section 3: mean over the endpoint's OWN cycles of deg(ankle_l) - deg(ankle_r),
       sampled at LEFT GRF heel strikes, window [T0, T1], last cycle dropped."""
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    if grf is None:
        return None, None, None, 0
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= T0 and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc:
        return None, None, None, 0
    al = np.degrees(np.asarray(S.col(cols, dat, "ankle_angle_l"), dtype=float))
    ar = np.degrees(np.asarray(S.col(cols, dat, "ankle_angle_r"), dtype=float))
    hs = [a for a, _ in cyc]
    hl = float(np.mean([al[i] for i in hs]))
    hr = float(np.mean([ar[i] for i in hs]))
    return hl - hr, hl, hr, len(cyc)


print("\n" + "=" * 78)
print("COVARIATE ank_hs_LmR -- computed read-only from the r151 .sto files")
print("=" * 78)
cov = {}
print("%-8s %8s %10s %10s %12s %10s" % ("seed", "cycles", "ank_hs_l", "ank_hs_r", "ank_hs_LmR", "cyc_time"))
for a in ("S", "W"):
    for k in arms[a]:
        seed = int(k.split("_")[1])
        tag = "R151%s_s%d" % (a, seed)
        d = find_run(tag)
        if d is None:
            die("no run directory for %s -- refusing to substitute a value" % tag)
        sto = sto_for(d)
        if sto is None:
            die("no .sto for %s -- registration section 9 forbids replaying to create one" % tag)
        v, hl, hr, nc = ank_hs_lmr(sto)
        if v is None:
            die("no cycles in window for %s" % tag)
        cov[k] = {"ank_hs_LmR": v, "ank_hs_l": hl, "ank_hs_r": hr,
                  "cycle_time": per[k]["cycle_time"], "ank_rom_l": per[k]["ankle_angle_l"],
                  "n_cycles": nc, "sto": os.path.basename(sto)}
        print("%-8s %8d %10.4f %10.4f %12.4f %10.4f" % (k, nc, hl, hr, v, per[k]["cycle_time"]))


# -------------------------------- section 4: common-support gate, BEFORE any residual
print("\n" + "=" * 78)
print("SECTION 4 -- COMMON-SUPPORT GATE (covariates only; no residual computed yet)")
print("=" * 78)
support = {}
for c in ("cycle_time", "ank_hs_LmR"):
    sv = [cov[k][c] for k in arms["S"]]
    wv = [cov[k][c] for k in arms["W"]]
    lo, hi = max(min(sv), min(wv)), min(max(sv), max(wv))
    ok = lo <= hi
    support[c] = {"S_range": [min(sv), max(sv)], "W_range": [min(wv), max(wv)],
                  "overlap": [lo, hi] if ok else None, "overlaps": bool(ok)}
    print("  %-12s  S [%9.4f, %9.4f]   W [%9.4f, %9.4f]   -> %s"
          % (c, min(sv), max(sv), min(wv), max(wv),
             ("OVERLAP [%.4f, %.4f]" % (lo, hi)) if ok else "*** NO OVERLAP ***"))

usable = [c for c in ("cycle_time", "ank_hs_LmR") if support[c]["overlaps"]]
res = {"registration": "PREREG_3d_residual_r168.md",
       "registration_sha256": "e2437a0f5d49da9e429aa36ac969873df28e4dde90527a495db48b356d3cb5b2",
       "calibration_gate": "PASSED 4/4 to 1e-9",
       "window": [T0, T1], "n_S": 6, "n_W": 6, "bonferroni": BONF,
       "floor_abs_auc_minus_half_6v6_x2": FLOOR_X2,
       "covariates_per_seed": cov, "common_support": support,
       "covariates_usable": usable}

if not usable:
    res["verdict"] = "NOT APPLICABLE"
    res["reason"] = ("section 4: neither registered covariate has common support between S and W. "
                     "Adjustment would extrapolate into a region containing no observations; "
                     "per the registration NO residual number is reported.")
    print("\n  ⛔ VERDICT (c) NOT APPLICABLE -- no residual is computed or reported.")
    json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1)
    print("  wrote %s" % OUT)
    sys.exit(0)

if len(usable) == 1:
    print("\n  ⚠ only %r has common support; the residual is fitted on that covariate alone,"
          % usable[0])
    print("    and the result must say which covariate could not be adjusted for.")


# ------------------------------------------------ section 3: the residual test
def run_spec(name, ch, colnames, verdict_bearing):
    Y = np.array([lmr[ch][k] for k in arms["S"] + arms["W"]], dtype=float)
    X = np.column_stack([[cov[k][c] for k in arms["S"] + arms["W"]] for c in colnames]
                        + [np.ones(12)])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    r2 = 1.0 - float(np.var(resid)) / float(np.var(Y))
    a_raw, b_raw = Y[:6].tolist(), Y[6:].tolist()
    a_res, b_res = resid[:6].tolist(), resid[6:].tolist()
    auc_raw, p_raw = mwu_two_sided(a_raw, b_raw)
    auc_res, p_res = mwu_two_sided(a_res, b_res)
    k = BONF if verdict_bearing else 1
    padj = min(1.0, p_res * k)
    d = abs(auc_res - 0.5)
    if not verdict_bearing:
        verd = "NOT VERDICT-BEARING"
    elif padj < 0.05:
        verd = "SURVIVES"
    else:
        verd = "UNRESOLVED"
    print("\n  [%s] %s" % (name, ch))
    print("    model: %s ~ %s + 1" % (ch, " + ".join(colnames)))
    print("    betas: " + "  ".join("%s %+.5f" % (c, b) for c, b in zip(colnames + ["const"], beta)))
    print("    R^2 = %.4f  -> covariates explain %.1f%% of per-seed %s" % (r2, 100 * r2, ch))
    print("    RAW      AUC %.4f  p %.6f" % (auc_raw, p_raw))
    print("    RESIDUAL AUC %.4f  p %.6f  p_adj(x%d) %.6f   |AUC-0.5| %.4f vs floor %.4f  -> %s"
          % (auc_res, p_res, k, padj, d, FLOOR_X2, verd))
    return {"channel": ch, "spec": name, "covariates": colnames,
            "betas": beta.tolist(), "r2": r2,
            "auc_raw": auc_raw, "p_raw": p_raw,
            "auc_resid": auc_res, "p_resid": p_res, "p_adj": padj,
            "abs_auc_minus_half": d, "floor": FLOOR_X2,
            "verdict": verd, "verdict_bearing": verdict_bearing,
            "resid_S": a_res, "resid_W": b_res}


print("\n" + "=" * 78)
print("SECTION 3 -- PRIMARY, per seed, n=12, Bonferroni x%d, exact two-sided MWU" % BONF)
print("=" * 78)
res["primary"] = [run_spec("PRIMARY", ch, usable, True) for ch in CHANNELS]

print("\n" + "=" * 78)
print("SENSITIVITY -- the literal residual_test.py covariate list, design (a).")
print("NOT VERDICT-BEARING. Known circular for ankle_angle_LmR: ank_rom_l is a")
print("component of that outcome. Reported so the reader sees what reuse would do.")
print("=" * 78)
res["sensitivity"] = [run_spec("SENSITIVITY(a)", ch, ["ank_rom_l", "cycle_time", "ank_hs_l"], False)
                      for ch in CHANNELS]

surv = [r["channel"] for r in res["primary"] if r["verdict"] == "SURVIVES"]
res["verdict"] = "SURVIVES" if len(surv) == 2 else ("MIXED" if surv else "UNRESOLVED")
res["surviving_channels"] = surv

print("\n" + "=" * 78)
print("VERDICT: %s   surviving channels: %r" % (res["verdict"], surv))
print("Reminder from section 2: an UNRESOLVED result is NOT evidence of destruction --")
print("at 6v6 under x2 this test cannot separate attenuation from abolition.")
print("=" * 78)

json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1)
print("\nwrote %s" % OUT)
