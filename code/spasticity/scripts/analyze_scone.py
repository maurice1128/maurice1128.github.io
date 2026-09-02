"""Identifiability analysis on SCONE forward-dynamic steady-state gaits.

Design notes (addressing the council's standing objections to the OCP arm):
  * N is the number of INDEPENDENT (subject x condition) optimizations, not gait cycles and
    not noise draws -- CIs use that N.
  * "Subjects" are distinct BODY morphologies (mass/strength/segment scaling), each
    re-optimized separately, so leave-one-subject-out is genuine between-subject
    generalization rather than robustness to +-5% jitter of a single model.
  * Measurement noise is injected at the WAVEFORM level before features are computed, so
    scalar features cannot leak noise-free information.
  * Conditions that failed to converge to a stable gait are reported, never silently dropped.
  * The naive "no equinus -> paretic" heuristic is always reported alongside, because the
    OCP arm showed a classifier can look good while merely reproducing that heuristic.
"""
# ⛔ STANCE-WINDOW REPAIR (2026-07-28) -- NUMBERS FROM THIS SCRIPT HAVE CHANGED.
#
# This script reads `ank_stance_mean` from sto_utils. That feature USED TO average the first
# 60%% of the STRIDE by index, not the stance phase. Measured stance fraction in this archive is
# 0.553-0.616, so the old value folded up to 5%% of swing into "stance" -- and how much it folded
# in varied with the injected dose, i.e. with the independent variable.
#
# sto_utils now uses the GRF-defined stance mask. Measured difference on GATE2: -8.5874 (old)
# vs -7.9657 (new) = 0.62 deg. Below the 3.8 deg MDC floor, so no qualitative conclusion
# changes AS A RESULT OF THIS DEFECT. That is NOT a statement that the old numbers are
# usable: they remain subject to the separate prohibitions in paper/HANDOFF.md -- the 2x
# delivery relabelling, and the withdrawn CMS-vs-CMW contrast.
# but EVERY NUMBER THIS SCRIPT PRINTED BEFORE 2026-07-28 WAS COMPUTED ON THE WRONG WINDOW and
# must be disclosed as such wherever it was quoted. Do not compare old output to new output.
#
# See paper/HANDOFF.md and paper/REFEREE_methods_contribution.md.

import os, sys, json, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# observation tiers: which features a given motion-capture setup can actually deliver
TIERS = {
    "MK_2D":  ["ank_min", "ank_max", "ank_mean", "ank_rom", "ank_hs",
               "ank_stance_mean", "ank_swing_min", "cycle_time"],
    "MK_3D":  ["ank_min", "ank_max", "ank_mean", "ank_rom", "ank_hs",
               "ank_stance_mean", "ank_swing_min", "cycle_time",
               "knee_min", "knee_rom", "hip_rom"],
    "MK_3D_V": ["ank_min", "ank_max", "ank_mean", "ank_rom", "ank_hs",
                "ank_stance_mean", "ank_swing_min", "cycle_time",
                "knee_min", "knee_rom", "hip_rom", "ank_vel_max"],
}
# noise (deg) roughly matching markerless vs lab-grade mocap
NOISE_DEG = {"MK_2D": 2.5, "MK_3D": 1.5, "MK_3D_V": 1.5}


def label_of(tag):
    if tag.startswith("HEALTHY"):
        return "healthy"
    if tag.startswith("PAR"):
        return "paretic"
    if tag.startswith("SPAS"):
        return "spastic"
    if tag.startswith("MIX"):
        return "mixed"
    return "?"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def build_matrix(feats, tier, rng, noise_scale=1.0):
    """Rows = conditions, cols = tier features, with noise applied per-feature (deg)."""
    names = TIERS[tier]
    sd = NOISE_DEG[tier] * noise_scale
    X, y, tags = [], [], []
    for tag, f in sorted(feats.items()):
        if not isinstance(f, dict) or f.get("status") != "ok":
            continue
        row = []
        ok = True
        for n in names:
            v = f.get(n)
            if v is None:
                ok = False
                break
            # angle-like features get degree noise; time features get 2% noise
            row.append(v + (rng.normal(0, sd) if "time" not in n else v * rng.normal(0, 0.02)))
        if not ok:
            continue
        X.append(row); y.append(label_of(tag)); tags.append(tag)
    return np.array(X), np.array(y), tags


def loso_macro_recall(X, y, subjects, rng):
    """Leave-one-subject-out nearest-centroid (deliberately simple: with this N a flexible
    classifier would overfit, which is exactly the artifact the council caught before)."""
    classes = sorted(set(y))
    correct = {c: 0 for c in classes}
    total = {c: 0 for c in classes}
    for s in sorted(set(subjects)):
        te = subjects == s
        tr = ~te
        if tr.sum() < 2 or te.sum() == 0:
            continue
        mu = X[tr].mean(0); sg = X[tr].std(0); sg[sg == 0] = 1.0
        Z = (X[tr] - mu) / sg
        cent = {}
        for c in classes:
            m = y[tr] == c
            if m.sum():
                cent[c] = Z[m].mean(0)
        if len(cent) < 2:
            continue
        for xi, yi in zip((X[te] - mu) / sg, y[te]):
            total[yi] += 1
            pred = min(cent, key=lambda c: np.linalg.norm(xi - cent[c]))
            if pred == yi:
                correct[yi] += 1
    recalls = {c: (correct[c] / total[c]) if total[c] else float("nan")
               for c in classes}
    valid = [v for v in recalls.values() if not np.isnan(v)]
    return (float(np.mean(valid)) if valid else float("nan")), recalls, total


def heuristic_baseline(feats):
    """'no equinus -> paretic, else guess among spastic/mixed' -- the bar any classifier
    must clear to be interesting."""
    ok = {t: f for t, f in feats.items()
          if isinstance(f, dict) and f.get("status") == "ok"}
    if "HEALTHY" not in ok:
        return None
    h = ok["HEALTHY"]["ank_stance_mean"]
    corr = tot = 0
    for t, f in ok.items():
        lab = label_of(t)
        if lab == "healthy":
            continue
        tot += 1
        equinus = f["ank_stance_mean"] < h - 3.0
        pred = "paretic" if not equinus else "spastic"  # can't split spastic/mixed
        if pred == lab:
            corr += 1
    return corr / tot if tot else None


def main():
    p = os.path.join(HERE, "scone_features.json")
    feats = json.load(open(p))
    ok = {t: f for t, f in feats.items()
          if isinstance(f, dict) and f.get("status") == "ok"}
    bad = {t: f for t, f in feats.items()
           if not (isinstance(f, dict) and f.get("status") == "ok")}
    print("stable conditions: %d   unstable/failed: %d %s"
          % (len(ok), len(bad), sorted(bad) if bad else ""))
    if len(ok) < 4:
        print("\nToo few stable conditions for identifiability. Reporting descriptives only.")
        for t, f in sorted(ok.items()):
            print("  %-9s ank_stance=%6.1f ank_min=%6.1f rom=%5.1f cycles=%d"
                  % (t, f["ank_stance_mean"], f["ank_min"], f["ank_rom"], f["n_cycles"]))
        return

    # subject id: everything before the first digit is the condition; with a single body
    # model every condition is its own "subject" -> LOSO degenerates to leave-one-out and
    # MUST be reported as such (not as between-subject generalization).
    subjects = np.array([t for t in sorted(ok)])
    print("\nNOTE: subject structure =", "single body model (LOSO == leave-one-condition-out;"
          " this is robustness, NOT between-subject generalization)")

    print("\n%-9s %-12s %-28s %s" % ("tier", "macro-recall", "95% CI (N=cond)", "per-class"))
    for tier in TIERS:
        rng = np.random.default_rng(0)
        # average over noise draws, but CI uses N = number of conditions
        macros = []
        for _ in range(200):
            X, y, tags = build_matrix(ok, tier, rng)
            if len(X) < 4:
                continue
            m, rec, tot = loso_macro_recall(X, y, np.array(tags), rng)
            if not np.isnan(m):
                macros.append(m)
        if not macros:
            print("%-9s insufficient" % tier)
            continue
        macro = float(np.mean(macros))
        n = len(ok)
        lo, hi = wilson(macro * n, n)
        print("%-9s %-12.3f [%.3f, %.3f]  (N=%d)  %s"
              % (tier, macro, lo, hi, n,
                 {k: round(v, 2) for k, v in rec.items()}))

    hb = heuristic_baseline(ok)
    if hb is not None:
        print("\nnaive 'no-equinus->paretic' heuristic: %.3f  "
              "(a classifier must clearly beat this to be interesting)" % hb)


if __name__ == "__main__":
    main()
