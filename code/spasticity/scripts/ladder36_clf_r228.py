# -*- coding: utf-8 -*-
"""PREREG_classifier_r222.md  sha256 c0a13d6758a9e2876230 (prefix)

Leave-one-SEED-out CV, 6 spastic vs 36 weak, all 4 LmR channels, window [1.00, 9.73].
Read-only: recomputes channels from .sto, runs no simulation.

GUARDS, per registration section 3:
  1. every fitting step inside the fold -- standardisation, selection, threshold
  2. the SEED is held out, not the cell: fold k removes the spastic cell AND all three
     weak cells carrying seed 100+k
  3. permutation null over the WHOLE procedure, selection included
"""
import io, os, sys, glob, json, math, itertools
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = list(range(101, 107))
PAIR = ["ankle_angle", "knee_angle", "hip_flexion", "hip_adduction"]
UNP = ["pelvis_list", "pelvis_rotation", "lumbar_bending"]
CH = [p + "_LmR" for p in PAIR]   # RESTRICTED to the four (L-R) channels, per PREREG_lmr_only_r223.md
ARMS = [("S","R151S",1),("W800","R151W",0),("W870","R174W870",0),("W892","R174W892",0),("W900","R169W090",0),("W915","R174W915",0),("W950","R169W095",0)]


def meas(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91]
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(ds[0], "*.par.sto")))[-1])
    t = list(S.col(cols, dat, "time"))
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)
           if t[idx[k]] >= SETTLE and t[idx[k + 1]] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc

    def rom(ch):
        v = S.col(cols, dat, ch)
        return sum(math.degrees(max(v[a:b + 1]) - min(v[a:b + 1])) for a, b in cyc) / len(cyc)
    o = {c: rom(c) for c in [p + s for p in PAIR for s in ("_l", "_r")] + UNP}
    o["cycle_time"] = (t[cyc[-1][1]] - t[cyc[0][0]]) / len(cyc)
    for p in PAIR:
        o[p + "_LmR"] = o[p + "_l"] - o[p + "_r"]
    return o


# ---- build the design matrix: 24 cells x 16 channels, with seed and label
X, y, seed_of, name_of = [], [], [], []
for arm, pre, lab in ARMS:
    for s in SEEDS:
        X.append([meas("%s_s%d" % (pre, s))[c] for c in CH])
        y.append(lab); seed_of.append(s); name_of.append("%s_s%d" % (arm, s))
X = np.asarray(X, float); y = np.asarray(y, int); seed_of = np.asarray(seed_of, int)
assert X.shape == (42, 4) and y.sum() == 6


def run_cv(lab):
    """Leave-one-seed-out CV. Every fit is inside the fold. Returns (preds, truths, picks)."""
    preds, truths, picks = [], [], []
    for s in SEEDS:
        te = seed_of == s
        tr = ~te
        Xtr, ytr = X[tr], lab[tr]
        if ytr.sum() == 0 or ytr.sum() == len(ytr):     # degenerate fold under a shuffle
            return None
        mu, sd = Xtr.mean(0), Xtr.std(0)
        sd = np.where(sd > 0, sd, 1.0)
        Ztr = (Xtr - mu) / sd
        a, b = Ztr[ytr == 1], Ztr[ytr == 0]
        smd = np.abs(a.mean(0) - b.mean(0))             # selection: TRAINING ONLY
        j = int(np.argmax(smd))
        thr = 0.5 * (a[:, j].mean() + b[:, j].mean())
        sign = 1.0 if a[:, j].mean() > b[:, j].mean() else -1.0
        Zte = (X[te] - mu) / sd
        p = (sign * Zte[:, j] > sign * thr).astype(int)
        preds.extend(p.tolist()); truths.extend(lab[te].tolist()); picks.append(CH[j])
    return np.asarray(preds), np.asarray(truths), picks


obs = run_cv(y)
preds, truths, picks = obs
tp = int(((preds == 1) & (truths == 1)).sum()); tn = int(((preds == 0) & (truths == 0)).sum())
fp = int(((preds == 1) & (truths == 0)).sum()); fn = int(((preds == 0) & (truths == 1)).sum())
acc = (tp + tn) / 42.0
hip_picks = sum(1 for p in picks if p == "hip_flexion_LmR")

print("confusion  TP %d  FN %d  FP %d  TN %d" % (tp, fn, fp, tn))
print("accuracy   %d/42 = %.4f   (majority baseline 36/42 = 0.8571)" % (tp + tn, acc))
print("channel picked per fold:", picks)
print("hip_flexion_LmR chosen %d of 6 folds" % hip_picks)

# ---- guard 3: permutation null over the WHOLE procedure.
# C(42,6) = 5,245,786 assignments x 6 folds = 31.5M CV fits. Exhaustive enumeration is INFEASIBLE
# here, so the null is SAMPLED and the sample count is reported, per PREREG_ladder36_r228.md
# section 2: "No silent substitution of sampling for enumeration."
from math import comb
TOTAL = comb(42, 6)
NSAMP = 20000
rng = np.random.default_rng(20228)
print("\npermutation null: C(42,6) = %d assignments -- INFEASIBLE exhaustively." % TOTAL)
print("SAMPLED with %d random label assignments, seed 20228." % NSAMP)
ge = tot = 0
for _ in range(NSAMP):
    lab = np.zeros(42, int)
    lab[rng.choice(42, 6, replace=False)] = 1
    r = run_cv(lab)
    if r is None:
        continue
    p2, t2, _ = r
    tot += 1
    if (p2 == t2).sum() / 42.0 >= acc:
        ge += 1
print("assignments evaluated %d   accuracy >= observed in %d   proportion %.6f" % (tot, ge, ge / tot))

json.dump({"prereg": "PREREG_ladder36_r228.md sha256 ab738d522a4ad937ce2d",
           "design": "leave-one-SEED-out, 6 spastic vs 36 weak, 4 LmR channels, window [1.00, 9.73]",
           "confusion": {"TP": tp, "FN": fn, "FP": fp, "TN": tn},
           "accuracy": acc, "majority_baseline": 36 / 42.0,
           "channel_per_fold": picks, "hip_chosen_of_6": hip_picks,
           "permutation_null": {"method": "SAMPLED, %d of C(42,6)=%d assignments, seed 20228" % (tot, TOTAL),
                                "assignments_evaluated": tot, "count_ge_observed": ge,
                                "proportion": ge / tot}},
          io.open(os.path.join(PAPER, "LADDER36CLF_r228.json"), "w", encoding="utf-8"), indent=1)
print("\ndeposited paper/LADDER36CLF_r228.json")
