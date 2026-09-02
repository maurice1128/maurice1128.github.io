"""Can the gait waveform classify the MECHANISM -- or is it only re-reading the optimizer's cost?

HISTORY OF THIS FILE.
v1 asked whether the whole time-normalized waveform could separate spastic from non-spastic
conditions, having watched seven hand-picked scalars fail. It reported 0.857 (6/7 conditions) at
p = 0.147 and was read as "close, needs more conditions". Council round 9 dismantled that reading:

  * fitness ALONE, with zero kinematics, also scores 0.857. So does the generation number.
  * the discriminant score correlates with fitness at r = 0.963 (p = 7.8e-13).
  * regressing the waveform on fitness first collapses accuracy to 0.143 -- chance.
  * the INTACT limb, which carries no lesion and no reflex, classifies at least as well.
  * mechanism-scrambled sham labelings score 0.857 too, including "the three paretic conditions
    are the spastic class". The feature space is one-dimensional and that dimension is severity.
  * the `.sto` files were selected by modification time, so 8/10 spastic runs were analysed at
    generation 59-83 while their optimizations had reached 103-337.
  * and the fix v1 proposed -- more conditions -- was shown by simulation to make things WORSE:
    a generative model containing zero mechanism information, sampled at 12 conditions, reaches
    median p = 0.0022 under exact permutation. Expanding the grid would have certified the
    confound at publishable significance.

WHAT v2 CHANGES.
 1. Waveforms come from `replay_cache.replay_all`, which replays each run's best `.par` into a
    directory it has just emptied and asserts exactly one `.sto` results. Every number is
    traceable to a named controller. A single `GEN_CAP` is applied to every arm alike.
 2. Exact enumeration over all condition-label assignments replaces Monte Carlo permutation.
    With 7-10 conditions the exact null is small enough to enumerate, and the minimum attainable
    p is reported so a "non-significant" result is not confused with an underpowered one.
 3. THREE CONFOUND BASELINES RUN AUTOMATICALLY AND ARE PRINTED FIRST, so no waveform result can
    ever again be reported without the number that explains it away:
      - fitness alone            (if this ties the waveform, the waveform adds nothing)
      - generation alone         (detects optimization-depth leakage)
      - waveform residualized on fitness (what survives after cost is removed -- the real test)
 4. The intact limb is classified alongside the affected limb. It should FAIL. If it does not,
    the signal is not lesion-specific and the result is void.
 5. Sham labelings that scramble mechanism while preserving severity ordering are scored. If a
    sham ties the true labeling, the classifier is reading severity.

WHAT WOULD COUNT AS A REAL RESULT: affected-limb accuracy above chance AFTER residualizing on
fitness, with the intact limb at chance and every sham below the true labeling. Nothing less.
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from replay_cache import replay_all  # noqa: E402
from sto_utils import col, grf_vertical, heel_strikes, load_sto, muscle_signal  # noqa: E402

NPTS = 100
GEN_CAP = 90          # every arm read at the same depth; the non-spastic arm stopped at 90
CHANNELS = ["ankle_angle", "knee_angle", "hip_flexion"]

# condition -> (label, runs).  label 0 = no spastic component, 1 = spastic component.
# The cost-matched arms (CMW70/80, CMS020/030) are included so the severity axes overlap; see
# paper/RESULT_fitness_is_severity_not_mechanism.md.
CONDITIONS = {
    "HEALTHY": (0, ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"]),
    "PAR20":   (0, ["DPAR20_s1", "DPAR20_s2", "DPAR20_s3"]),
    "PAR40":   (0, ["DPAR40_s1", "DPAR40_s2", "DPAR40_s3"]),
    "PAR60":   (0, ["DPAR60_s1", "DPAR60_s2", "DPAR60_s3"]),
    "PAR70":   (0, ["CMW70_s1", "CMW70_s2"]),
    "PAR80":   (0, ["CMW80_s1", "CMW80_s2"]),
    "SPAS002": (1, ["CMS020_s1", "CMS020_s2"]),
    "SPAS003": (1, ["CMS030_s1", "CMS030_s2"]),
    "SPAS005": (1, ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"]),
    "SPAS01":  (1, ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"]),
}


def waveform(sto, side="l", settle=1.0, with_emg=False):
    """Cycle-averaged, time-normalized waveform. Time normalization removes cadence, which
    confounded the very first candidate feature."""
    cols, d = load_sto(sto)
    if d.size == 0:
        return None
    t = d[:, 0]
    grf, thr = grf_vertical(cols, d, side)
    if grf is None:
        return None
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    if len(hs) < 4:
        return None
    cycles = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
    if len(cycles) < 2:
        return None
    sigs = []
    for ch in CHANNELS:
        x = col(cols, d, "%s_%s" % (ch, side))
        if x is None:
            return None
        sigs.append(np.degrees(x))
    if with_emg:
        for m in ("soleus", "tib_ant"):
            a = muscle_signal(cols, d, m, side, "activation")
            if a is None:
                return None
            sigs.append(a)
    out = []
    for x in sigs:
        norm = [np.interp(np.linspace(0, 1, NPTS), np.linspace(0, 1, b - a), x[a:b])
                for a, b in cycles]
        out.append(np.mean(norm, axis=0))
    return np.concatenate(out)


def loco_accuracy(X, cond, labels):
    """Leave-one-CONDITION-out nearest-centroid, scored per condition.

    The unit of analysis is the condition, never the seed: CMA-ES seeds share body model,
    objective, warm start and controller family, so treating them as independent subjects is
    pseudo-replication -- an error already on this project's record.
    """
    conds = sorted(labels)
    y = np.array([labels[c] for c in cond], float)
    correct = 0
    for held in conds:
        te = np.array([c == held for c in cond])
        tr = ~te
        if len(set(y[tr])) < 2:
            return None                      # this labeling cannot be cross-validated
        mu, sd = X[tr].mean(axis=0), X[tr].std(axis=0) + 1e-9
        Z = (X - mu) / sd
        # weight each condition equally so an arm with more seeds cannot dominate the centroid
        def centroid(v):
            cs = [c for c in conds if c != held and labels[c] == v]
            return np.mean([Z[np.array([c == k for c in cond])].mean(axis=0) for k in cs], axis=0)
        c0, c1 = centroid(0), centroid(1)
        pred = (np.linalg.norm(Z[te] - c1, axis=1) < np.linalg.norm(Z[te] - c0, axis=1))
        if (pred.mean() > 0.5) == (labels[held] > 0.5):
            correct += 1
    return correct / len(conds)


def exact_p(X, cond, labels):
    """Exact permutation over every condition-label assignment with the same class balance."""
    conds = sorted(labels)
    k = sum(labels.values())
    acc = loco_accuracy(X, cond, labels)
    if acc is None:
        return None, None, None
    null = []
    for combo in itertools.combinations(conds, k):
        alt = {c: (1 if c in combo else 0) for c in conds}
        a = loco_accuracy(X, cond, alt)
        if a is not None:
            null.append(a)
    null = np.array(null)
    return acc, float(np.mean(null >= acc)), 1.0 / len(null)


def residualize(X, f):
    """Remove everything linearly predictable from fitness, column by column."""
    A = np.column_stack([np.ones_like(f), f])
    beta, *_ = np.linalg.lstsq(A, X, rcond=None)
    return X - A @ beta


def report(name, X, cond, labels):
    acc, p, pmin = exact_p(X, cond, labels)
    if acc is None:
        print("  %-34s  not cross-validatable" % name)
        return None
    flag = "  <- ABOVE CHANCE" if p < 0.05 else ""
    print("  %-34s  acc=%.3f  exact p=%.4f (min %.4f)%s" % (name, acc, p, pmin, flag))
    return {"acc": acc, "p": p, "p_min": pmin}


def main():
    tags, cond, lab_of = [], [], {}
    for c, (lab, ts) in CONDITIONS.items():
        lab_of[c] = lab
        for t in ts:
            tags.append(t)
            cond.append(c)

    print("Replaying each run from its best .par at GEN_CAP=%d ...\n" % GEN_CAP)
    recs = replay_all(tags, gen_cap=GEN_CAP)

    keep = [i for i, t in enumerate(tags) if "error" not in recs[t]]
    if not keep:
        print("\nnothing replayed -- cannot proceed")
        return
    fit = np.array([recs[tags[i]]["fitness"] for i in keep])
    gen = np.array([recs[tags[i]]["gen"] for i in keep], float)
    ck = [cond[i] for i in keep]
    labels = {c: lab_of[c] for c in sorted(set(ck))}

    print("\n%s\nDEPTH CHECK (must be comparable across arms, or nothing below is valid)\n%s"
          % ("=" * 72, "=" * 72))
    for v in (0, 1):
        g = [gen[j] for j, c in enumerate(ck) if labels[c] == v]
        f = [fit[j] for j, c in enumerate(ck) if labels[c] == v]
        print("  label %d  n=%-2d  gen %d-%d (mean %.1f)   fitness %.4f-%.4f"
              % (v, len(g), min(g), max(g), np.mean(g), min(f), max(f)))

    print("\n%s\nCONFOUND BASELINES -- read these before any waveform number\n%s"
          % ("=" * 72, "=" * 72))
    out = {"gen_cap": GEN_CAP, "n_runs": len(keep), "baselines": {}, "waveform": {}}
    out["baselines"]["fitness"] = report("fitness alone (no kinematics)",
                                         fit.reshape(-1, 1), ck, labels)
    out["baselines"]["generation"] = report("generation alone", gen.reshape(-1, 1), ck, labels)

    for with_emg in (False, True):
        for side, sname in (("l", "AFFECTED limb"), ("r", "INTACT limb (must fail)")):
            W, cc, ff = [], [], []
            for j, i in enumerate(keep):
                w = waveform(recs[tags[i]]["sto"], side=side, with_emg=with_emg)
                if w is None:
                    continue
                W.append(w)
                cc.append(ck[j])
                ff.append(fit[j])
            if len(set(cc)) < 3:
                continue
            W, ff = np.array(W), np.array(ff)
            lb = {c: labels[c] for c in sorted(set(cc))}
            tag = "%s / %s" % (sname, "kin+EMG" if with_emg else "kinematics only")
            print("\n%s\n%s  (%d runs, %d conditions, %d features)\n%s"
                  % ("-" * 72, tag, len(W), len(lb), W.shape[1], "-" * 72))
            r_raw = report("raw waveform", W, cc, lb)
            r_res = report("waveform residualized on fitness", residualize(W, ff), cc, lb)
            out["waveform"][tag] = {"raw": r_raw, "residualized": r_res}

            if side == "l" and not with_emg and r_raw:
                print("\n  sham labelings (scramble mechanism, keep severity ordering):")
                order = sorted(lb, key=lambda c: np.mean(ff[np.array(cc) == c]))
                k = sum(lb.values())
                shams = {"most-expensive-k are 'spastic'": set(order[-k:]),
                         "cheapest-k are 'spastic'": set(order[:k])}
                for nm, s in shams.items():
                    a = loco_accuracy(W, cc, {c: (1 if c in s else 0) for c in lb})
                    if a is not None:
                        note = "  <- TIES the true labeling" if a >= r_raw["acc"] else ""
                        print("    %-38s acc=%.3f%s" % (nm, a, note))
                        out["waveform"][tag].setdefault("shams", {})[nm] = a

    json.dump(out, open(os.path.join(HERE, "waveform_classify_v2.json"), "w"), indent=2)
    print("\n-> waveform_classify_v2.json")


if __name__ == "__main__":
    main()
