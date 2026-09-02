# -*- coding: utf-8 -*-
"""PREREG_screen_r153.md
   sha256 02f3129d4b4f5759ff0df0b889b544735667e9dd29281abef3ed2a53a66e4b49

Exhaustive screen: does ANY feature cycle_features can produce survive adjustment
for ank_rom + cycle_time + ank_hs?

POOL = 30, fixed in the registration before any result: 10 testable features x 2
sides + 10 signed L-R asymmetries. The three covariates are EXCLUDED from the pool
and reported as DEGENERATE, decided in advance.

THIS SCREEN CANNOT FIND ANYTHING: 30 x 0.007937 = 0.2381, so no corrected positive
is attainable. It is an exhaustiveness argument, not a discovery instrument, and
section 2 of the registration says so before it runs.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SCREEN_r153.json"
SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
COVARS = ["ank_rom", "cycle_time", "ank_hs"]
NONFEAT = ["n_cycles", "t_end"]
POOL = 30


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


def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


raw = cells()
conds = [c for c in SPASTIC + WEAK if c in raw]
allkeys = sorted(k for k in raw[conds[0]][0][0] if k not in NONFEAT)
testable = [k for k in allkeys if k not in COVARS]
print("features available: %d   covariates excluded: %d   testable: %d"
      % (len(allkeys), len(COVARS), len(testable)))
print("  testable: %s" % testable)

lab = np.array([1 if c in SPASTIC else 0 for c in conds])


def cm(c, side, k):
    i = 0 if side == "l" else 1
    return float(np.mean([r[i][k] for r in raw[c]]))


X = np.column_stack([[cm(c, "l", k) for c in conds] for k in COVARS] + [np.ones(len(conds))])

QTY = []
for k in testable:
    QTY.append(("%s_l" % k, lambda c, k=k: cm(c, "l", k)))
    QTY.append(("%s_r" % k, lambda c, k=k: cm(c, "r", k)))
for k in testable:
    QTY.append(("%s_LmR" % k, lambda c, k=k: cm(c, "l", k) - cm(c, "r", k)))

assert len(QTY) == POOL, "pool is %d, registration fixed %d" % (len(QTY), POOL)
print("POOL = %d  (registered %d)  -- corrected floor %.4f, unreachable" % (len(QTY), POOL, POOL * 2.0 / 252))

rows = []
for name, f in QTY:
    Y = np.array([f(c) for c in conds])
    a, b = Y[lab == 1], Y[lab == 0]
    rauc, rp, rov = mwu(list(a), list(b))
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    r2 = 1.0 - float(np.var(resid) / np.var(Y)) if np.var(Y) > 0 else float("nan")
    ra, rb = resid[lab == 1], resid[lab == 0]
    sauc, sp, sov = mwu(list(ra), list(rb))
    rows.append({"name": name, "raw_auc": rauc, "raw_p": rp, "raw_overlap": rov,
                 "r2": r2, "res_auc": sauc, "res_p": sp, "res_overlap": sov,
                 "candidate": (sauc <= 0.1 or sauc >= 0.9) and sp < 0.05})

rows.sort(key=lambda r: -abs(r["raw_auc"] - 0.5))
print()
print("=" * 96)
print("THE SCREEN -- descriptive; no corrected positive is attainable (see registration section 2)")
print("=" * 96)
print("%-24s %8s %9s %6s | %8s %8s %9s %6s" %
      ("quantity", "raw_AUC", "raw_p", "ovl", "R^2", "res_AUC", "res_p", "ovl"))
for r in rows:
    print("%-24s %8.3f %9.5f %6d | %8.4f %8.3f %9.5f %6d%s"
          % (r["name"], r["raw_auc"], r["raw_p"], r["raw_overlap"], r["r2"],
             r["res_auc"], r["res_p"], r["res_overlap"],
             "  <== CANDIDATE" if r["candidate"] else ""))

print()
print("=" * 96)
print("THE THREE COVARIATES -- raw reported, residual DEGENERATE by construction")
print("=" * 96)
cov = []
for k in COVARS:
    Y = np.array([cm(c, "l", k) for c in conds])
    a, b = Y[lab == 1], Y[lab == 0]
    auc, p, ov = mwu(list(a), list(b))
    cov.append({"name": k + "_l", "raw_auc": auc, "raw_p": p, "raw_overlap": ov,
                "residual": "DEGENERATE"})
    print("%-24s %8.3f %9.5f %6d | %s" % (k + "_l", auc, p, ov, "DEGENERATE"))

# ---- the registered prediction test ----------------------------------------
sep = [abs(r["raw_auc"] - 0.5) for r in rows]
r2s = [r["r2"] for r in rows]
rho = spearman(sep, r2s)
print()
print("=" * 96)
print("REGISTERED PREDICTION (section 4): separation strength vs covariate R^2")
print("=" * 96)
print("  Spearman rho( |raw_AUC - 0.5| , R^2 ) over %d quantities = %+.4f" % (len(rows), rho))
strong = [r for r in rows if abs(r["raw_auc"] - 0.5) >= 0.4]
print("  quantities with |AUC-0.5| >= 0.4 (near-perfect raw separation): %d" % len(strong))
if strong:
    print("    their R^2: min %.4f  median %.4f  max %.4f"
          % (min(r["r2"] for r in strong),
             sorted(r["r2"] for r in strong)[len(strong) // 2],
             max(r["r2"] for r in strong)))
cands = [r["name"] for r in rows if r["candidate"]]
print()
print("CANDIDATES (residual AUC <=0.1 or >=0.9 AND uncorrected p<0.05): %r" % cands)
print("survivors at corrected 0.05: NONE POSSIBLE -- floor is %.4f" % (POOL * 2.0 / 252))

json.dump({"prereg_sha256": "02f3129d4b4f5759ff0df0b889b544735667e9dd29281abef3ed2a53a66e4b49",
           "pool": POOL, "corrected_floor": POOL * 2.0 / 252,
           "min_p_5v5": 2.0 / 252, "conds": conds,
           "screen": rows, "covariates": cov,
           "prediction_spearman_rho": rho, "candidates": cands},
          io.open(OUT, "w", encoding="utf-8"), indent=1)
print("\nwrote", OUT)
