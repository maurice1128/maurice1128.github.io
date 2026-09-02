"""Six registered features from PREREG_shape_r138.md §3, EXPLORATORY arm only (r139 Resolution 1).

WHAT THIS IS. `PREREG_shape_r138.md` registered three routes and one multiplicity pool of six, with
Tier 2 as the confirmatory set. Its own §6 then found the confirmatory design arithmetically dead:
the registered test's unit is the CONDITION, over 5 spastic vs 5 weak, and the slope Tier 2 holds
four conditions -- 2 v 2, whose two-sided p-floor is 0.3333. `PREREG_shape_RESOLUTION_r139.md` chose
Resolution 1: abandon the confirmatory arm rather than change the unit to the run, because run-level
replicates are pseudo-replicates of two lesions and R2 would buy a p by renaming the design.

SO EVERYTHING HERE IS EXPLORATORY AND LICENSES NOTHING. No correction is applied. The x6 that would
have applied is printed for comparability and is not an inferential claim.

WHY A NEW FILE. `scone/residual_test.py` must not be modified -- its own docstring forbids it "by
anyone, for any reason" -- and `sto_utils.cycle_features` returns per-cycle MEANS, so it cannot
supply Route B (second moments over cycles) or Route C (both limbs). This computes the six formulas
from the same primitives `cycle_features` uses, mirroring its conventions exactly: settle = 1.0,
GRF-delimited cycles between consecutive heel strikes, the last cycle dropped, angles in degrees,
the same heel-strike detector and threshold.

THE FEATURES, VERBATIM FROM r138 §3 -- none added, substituted or redefined:
  A1  t* = argmax_t theta'(t)                      timing of peak dorsiflexion velocity
  A2  D  = argmax_t theta(t) - argmax_t theta'(t)  velocity-angle phase lag
  B1  CV of stride time            SD(T_i) / mean(T_i) over strides within a run
  B2  CV of peak dorsiflexion velocity  SD(max theta'_i) / mean(max theta'_i) over strides
  C1  SI of peak dorsiflexion velocity  (L - R) / (0.5 * (L + R)) on max theta'
  C2  phase asymmetry              t*_L - t*_R, i.e. A1 per limb and differenced
A1, A2 and C2 are pure phase in cycle fraction; none has amplitude in it.

THE TEST, VERBATIM FROM r138 SS5: regress the feature on `ank_rom`, `cycle_time`, `ank_hs` plus a
constant at CONDITION level, take the residual, contrast spastic vs weak by two-sided Mann-Whitney U,
report AUC = U/(n1 n2), p, overlap and R^2 -- the same four numbers, in the same form, as
`ank_vel_max`'s 0.3600 / 0.5476 / 4-of-5 / 0.8030.

SIDE. The lesion is unilateral and the registered analysis reads side="l", so LEFT is treated as the
lesioned limb and RIGHT as intact. If that is wrong, C1 and C2 change sign and nothing else moves.

Writes paper/SHAPE_TEST_r139.json. Reads only scone/replay_crossed/. Nothing is launched.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils  # noqa: E402
import residual_test as RT  # noqa: E402  -- imported for its condition lists, never modified

HERE = os.path.dirname(os.path.abspath(__file__))
REPLAY = os.path.join(HERE, "replay_crossed")
SETTLE = 1.0
REFERENCE = {"name": "ank_vel_max (the scalar this is trying to rescue)",
             "auc": 0.3600, "p": 0.5476, "overlap": "4/5", "r2": 0.8030}


def _cycles(path, side):
    """The exact cycle decomposition cycle_features uses, but returning the pieces."""
    cols, d = sto_utils.load_sto(path)
    if d.size == 0:
        return None
    t = d[:, 0]
    ank = sto_utils.col(cols, d, "ankle_angle_%s" % side)
    if ank is None:
        return None
    ank = np.degrees(ank)
    grf, thr = sto_utils.grf_vertical(cols, d, side)
    if grf is None:
        return None
    hs = [i for i in sto_utils.heel_strikes(t, grf, thresh=thr) if t[i] >= SETTLE]
    if len(hs) < 3:
        return None
    cyc = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
    if len(cyc) < 2:
        return None
    return t, ank, cyc


def _per_cycle_shape(t, ank, cyc):
    """Per-cycle (t_star, t_peak_angle, vel_max, stride_time), all phases as cycle fraction."""
    out = []
    for a, b in cyc:
        tt, aa = t[a:b], ank[a:b]
        T = float(tt[-1] - tt[0])
        if T <= 0:
            continue
        vel = np.gradient(aa, tt)
        i_v = int(np.argmax(vel))
        i_a = int(np.argmax(aa))
        out.append((float((tt[i_v] - tt[0]) / T),      # t*   -- A1
                    float((tt[i_a] - tt[0]) / T),      # peak-angle phase
                    float(np.max(vel)),                # max theta'
                    float(t[b] - t[a])))               # stride time
    return out


def run_features(run_dir):
    """The six features for one run, or None if either limb fails the cycle test."""
    sto = [s for s in glob.glob(os.path.join(run_dir, "*.sto")) if os.path.getsize(s) > 1000]
    if len(sto) != 1:
        return None
    per = {}
    for side in ("l", "r"):
        c = _cycles(sto[0], side)
        if c is None:
            return None
        v = _per_cycle_shape(*c)
        if len(v) < 2:
            return None
        per[side] = np.array(v)

    L, R = per["l"], per["r"]
    tstar_L, tstar_R = float(np.mean(L[:, 0])), float(np.mean(R[:, 0]))
    vmax_L, vmax_R = float(np.mean(L[:, 2])), float(np.mean(R[:, 2]))
    denom = 0.5 * (vmax_L + vmax_R)

    return {
        "A1": tstar_L,
        "A2": float(np.mean(L[:, 1] - L[:, 0])),
        "B1": float(np.std(L[:, 3], ddof=1) / np.mean(L[:, 3])),
        "B2": float(np.std(L[:, 2], ddof=1) / np.mean(L[:, 2])),
        "C1": float((vmax_L - vmax_R) / denom) if denom != 0 else float("nan"),
        "C2": float(tstar_L - tstar_R),
        "n_cycles_l": int(len(L)),
        "n_cycles_r": int(len(R)),
    }


def collect():
    feats, covs = {}, {}
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        cond = os.path.basename(d).split(".")[0].rsplit("_s", 1)[0]
        if cond not in RT.SPASTIC + RT.WEAK:
            continue
        f = run_features(d)
        if f is None:
            continue
        sto = [s for s in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(s) > 1000]
        cf = sto_utils.cycle_features(sto[0], side="l", settle=SETTLE)
        if cf is None:
            continue
        feats.setdefault(cond, []).append(f)
        covs.setdefault(cond, []).append(cf)
    return feats, covs


def main():
    feats, covs = collect()
    conds = [c for c in RT.SPASTIC + RT.WEAK if c in feats]
    lab = np.array([1 if c in RT.SPASTIC else 0 for c in conds])

    print("=" * 92)
    print("SHAPE / VARIANCE / ASYMMETRY -- PREREG_shape_r138.md SS3, EXPLORATORY ARM (r139 Res. 1)")
    print("=" * 92)
    print("  corpus   : %s" % REPLAY)
    print("  units    : CONDITION, %d spastic v %d weak" % (int(lab.sum()), int((1 - lab).sum())))
    print("  status   : EXPLORATORY. Licenses nothing. No correction applied.")
    print("  reference: %s -> AUC %.4f  p %.4f  overlap %s  R^2 %.4f"
          % (REFERENCE["name"], REFERENCE["auc"], REFERENCE["p"],
             REFERENCE["overlap"], REFERENCE["r2"]))

    X = np.column_stack([[float(np.mean([r["ank_rom"] for r in covs[c]])) for c in conds],
                         [float(np.mean([r["cycle_time"] for r in covs[c]])) for c in conds],
                         [float(np.mean([r["ank_hs"] for r in covs[c]])) for c in conds],
                         np.ones(len(conds))])

    print("\n%-9s %5s %9s %9s %9s %9s %9s %9s" %
          ("cond", "arm", "A1", "A2", "B1", "B2", "C1", "C2"))
    vals = {}
    for k in ("A1", "A2", "B1", "B2", "C1", "C2"):
        vals[k] = np.array([float(np.mean([r[k] for r in feats[c]])) for c in conds])
    for i, c in enumerate(conds):
        print("%-9s %5s %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f"
              % (c, "SPAS" if lab[i] else "WEAK",
                 vals["A1"][i], vals["A2"][i], vals["B1"][i],
                 vals["B2"][i], vals["C1"][i], vals["C2"][i]))

    print("\n%-4s %-34s %8s %10s %10s %9s %8s"
          % ("id", "feature", "AUC", "p_raw", "p_x6(ref)", "overlap", "R^2"))
    print("-" * 92)
    out = {}
    for k in ("A1", "A2", "B1", "B2", "C1", "C2"):
        Y = vals[k]
        beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
        resid = Y - X @ beta
        r2 = 1.0 - np.var(resid) / np.var(Y) if np.var(Y) > 0 else float("nan")
        a, b = resid[lab == 1], resid[lab == 0]
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        auc = u.statistic / (len(a) * len(b))
        ov = int(sum(1 for x in a if b.min() <= x <= b.max()))
        print("%-4s %-34s %8.4f %10.6f %10.6f %6d/%-2d %8.4f"
              % (k, "residual after rom+cyc+hs", auc, u.pvalue,
                 min(1.0, u.pvalue * 6), ov, len(a), r2))
        out[k] = {"auc": float(auc), "p_raw": float(u.pvalue),
                  "p_x6_reference_only": float(min(1.0, u.pvalue * 6)),
                  "overlap": ov, "n": int(len(a)), "r2": float(r2),
                  "condition_means": {c: float(Y[i]) for i, c in enumerate(conds)}}

    fired = {r: not any(out[k]["p_raw"] < 0.05 for k in ks)
             for r, ks in (("FA", ("A1", "A2")), ("FB", ("B1", "B2")), ("FC", ("C1", "C2")))}
    fall = all(out[k]["p_raw"] >= 0.05 for k in out)
    print("\nFALSIFIERS (r138 SS7), read at RAW p because nothing here is corrected:")
    for r in ("FA", "FB", "FC"):
        print("  %-6s fires: %-5s  -> Route %s %s"
              % (r, fired[r], r[1], "dead" if fired[r] else "survives at exploratory level"))
    print("  %-6s fires: %-5s  -> %s" % ("F-ALL", fall,
          "THE SHAPE ROUTE IS CLOSED" if fall else "at least one feature separates"))

    rec = {"what": "PREREG_shape_r138.md SS3 six features, EXPLORATORY arm under r139 Resolution 1",
           "status": "EXPLORATORY -- licenses nothing, no correction applied",
           "corpus": REPLAY, "conditions": conds,
           "n_spastic": int(lab.sum()), "n_weak": int((1 - lab).sum()),
           "reference_scalar": REFERENCE, "features": out,
           "falsifiers": {**{k: bool(v) for k, v in fired.items()}, "F_ALL": bool(fall)}}
    p = os.path.abspath(os.path.join(HERE, "..", "paper", "SHAPE_TEST_r139.json"))
    json.dump(rec, open(p, "w"), indent=1)
    print("\n  wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
