# -*- coding: utf-8 -*-
"""PREREG_hipflex_r152.md
   sha256 b060df86b598b215e4d8f7783695c30693e402d37cd71cc7b8f333c31076f212

Was the spastic signal always in CONTRALATERAL HIP FLEXION, and did the 2D study
miss it by measuring the wrong joint?

POST HOC: the channel was found in r151's 3D re-optimisation as the one endpoint of
twelve where the spastic arm is displaced from control. Tested here on a different
corpus. Legitimate, and never a registered primary.

Procedure is `residual_test.py`'s, unmodified: condition-level means over
`replay_crossed`, 5 spastic v 5 weak, exact two-sided Mann-Whitney, AUC = U/25,
overlap counted the same way, covariates ank_rom + cycle_time + ank_hs + constant.
`residual_test.py` itself is READ and NOT modified.
"""
import io, os, sys, glob, json, itertools

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPLAY = r"C:\Users\maurice\Desktop\spasticity_paper\scone\replay_crossed"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\HIPFLEX_r152.json"
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
POOL = 3                                   # registered and fixed


def cells():
    out = {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        sto = [s for s in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(s) > 1000]
        if len(sto) != 1:
            continue
        cond = os.path.basename(d).split(".")[0].rsplit("_s", 1)[0]
        if cond not in SPASTIC + WEAK:
            continue
        fl = sto_utils.cycle_features(sto[0], side="l", settle=1.0)
        fr = sto_utils.cycle_features(sto[0], side="r", settle=1.0)
        if fl is None or fr is None:
            continue
        out.setdefault(cond, []).append((fl, fr))
    return out


def mwu(a, b):
    """Exact two-sided Mann-Whitney by enumeration, plus AUC and overlap."""
    n, m = len(a), len(b)
    def U(x, y):
        return sum(1 for p in x for q in y if p > q) + 0.5 * sum(1 for p in x for q in y if p == q)
    obs = U(a, b)
    allv = list(a) + list(b)
    cnt = tot = 0
    for comb in itertools.combinations(range(n + m), n):
        A = [allv[i] for i in comb]
        B = [allv[i] for i in range(n + m) if i not in comb]
        u = U(A, B)
        tot += 1
        if abs(u - n * m / 2.0) >= abs(obs - n * m / 2.0) - 1e-9:
            cnt += 1
    ov = int(sum(1 for x in a if min(b) <= x <= max(b)))
    return obs / (n * m), cnt / float(tot), ov


raw = cells()
conds = [c for c in SPASTIC + WEAK if c in raw]
print("conditions: %d  (%d spastic, %d weak), seeds per condition: %s"
      % (len(conds), sum(c in SPASTIC for c in conds), sum(c in WEAK for c in conds),
         sorted(set(len(raw[c]) for c in conds))))


def cm(c, side, k):
    i = 0 if side == "l" else 1
    return float(np.mean([r[i][k] for r in raw[c]]))


lab = np.array([1 if c in SPASTIC else 0 for c in conds])
X = np.column_stack([[cm(c, "l", "ank_rom") for c in conds],
                     [cm(c, "l", "cycle_time") for c in conds],
                     [cm(c, "l", "ank_hs") for c in conds],
                     np.ones(len(conds))])

QTY = [("hip_flexion_r", lambda c: cm(c, "r", "hip_rom")),
       ("hip_flexion_l", lambda c: cm(c, "l", "hip_rom")),
       ("hip_flex_L_minus_R", lambda c: cm(c, "l", "hip_rom") - cm(c, "r", "hip_rom"))]

print()
print("%-9s %12s %12s %12s %10s %10s %9s"
      % ("cond", "hipflex_r", "hipflex_l", "L-R", "ank_rom", "cyc_time", "ank_hs"))
for c in conds:
    print("%-9s %12.3f %12.3f %12.3f %10.3f %10.3f %9.3f"
          % (c, cm(c, "r", "hip_rom"), cm(c, "l", "hip_rom"),
             cm(c, "l", "hip_rom") - cm(c, "r", "hip_rom"),
             cm(c, "l", "ank_rom"), cm(c, "l", "cycle_time"), cm(c, "l", "ank_hs")))

res = {"prereg_sha256": "b060df86b598b215e4d8f7783695c30693e402d37cd71cc7b8f333c31076f212",
       "conds": conds, "pool": POOL, "tests": {}}

print()
print("=" * 82)
print("STEP 1 -- RAW, exact two-sided Mann-Whitney 5v5, Bonferroni x%d" % POOL)
print("=" * 82)
print("%-20s %9s %9s %10s %10s %8s" % ("quantity", "S mean", "W mean", "AUC", "p", "p_adj"))
for name, f in QTY:
    Y = np.array([f(c) for c in conds])
    a, b = Y[lab == 1], Y[lab == 0]
    auc, p, ov = mwu(list(a), list(b))
    padj = min(1.0, p * POOL)
    res["tests"][name] = {"raw": {"S_mean": float(a.mean()), "W_mean": float(b.mean()),
                                  "auc": auc, "p": p, "p_adj": padj, "overlap": ov,
                                  "separates": padj < 0.05}}
    print("%-20s %9.3f %9.3f %10.4f %10.6f %8.4f  overlap %d/5%s"
          % (name, a.mean(), b.mean(), auc, p, padj, ov,
             "  *** SEPARATES ***" if padj < 0.05 else ""))

print()
print("=" * 82)
print("STEP 2 -- RESIDUAL after ank_rom + cycle_time + ank_hs  (THE TEST THAT DECIDES)")
print("=" * 82)
print("%-20s %9s %10s %10s %8s %8s" % ("quantity", "R^2", "AUC", "p", "p_adj", "overlap"))
for name, f in QTY:
    Y = np.array([f(c) for c in conds])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    r2 = 1.0 - float(np.var(resid) / np.var(Y))
    a, b = resid[lab == 1], resid[lab == 0]
    auc, p, ov = mwu(list(a), list(b))
    padj = min(1.0, p * POOL)
    res["tests"][name]["residual"] = {"r2": r2, "auc": auc, "p": p, "p_adj": padj,
                                      "overlap": ov, "separates": padj < 0.05,
                                      "betas": beta.tolist()}
    print("%-20s %9.4f %10.4f %10.6f %8.4f %8d/5%s"
          % (name, r2, auc, p, padj, ov,
             "  *** SEPARATES ***" if padj < 0.05 else ""))

json.dump(res, io.open(OUT, "w", encoding="utf-8"), indent=1)
print()
print("wrote", OUT)
rawsep = [n for n, _ in QTY if res["tests"][n]["raw"]["separates"]]
ressep = [n for n, _ in QTY if res["tests"][n]["residual"]["separates"]]
print("RAW separates      : %r" % rawsep)
print("RESIDUAL separates : %r" % ressep)
