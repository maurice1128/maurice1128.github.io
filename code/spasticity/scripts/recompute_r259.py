"""recompute_r259.py -- round 259.

The two analyses this project DISCLOSED as metric-dependent instead of computing.
Disclosure is not the cheaper form of rigour; it was the more comfortable one.

  A. The section 1 / section 2 classifier, under BOTH metrics.
  B. The section 4 per-severity permutation null and reach census, under BOTH metrics.

Self-test first: the excursion runs must reproduce CLASSIFIER_r222.json, LMRONLY_r223.json
and PERMNULL_r221.json exactly. If they do not, nothing below is trusted.

Read-only. Classifier procedure copied unchanged from classifier_r222.py.
"""
import glob
import io
import itertools
import json
import os
import sys

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import metric_r255 as MR

PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SEEDS = list(range(101, 107))
CH = MR.CH
LMR = [p + "_LmR" for p in MR.PAIR]
CLF_ARMS = [("S", "R151S", 1), ("W870", "R174W870", 0),
            ("W892", "R174W892", 0), ("W915", "R174W915", 0)]
SEV = ["W870", "W892", "W915"]


def load_all(T1):
    """cell -> {metric: {channel: value}} for every arm used by sections 1-4."""
    V = {}
    for arm, pre in MR.ARMS.items():
        V[arm] = []
        for s in SEEDS:
            sto = sorted(glob.glob(os.path.join(MR.rd("%s_s%d" % (pre, s)), "*.par.sto")))[-1]
            V[arm].append(MR.meas(sto, T1)[0])
    return V


def run_cv(X, y, seed_of, chans, lab):
    """classifier_r222.py run_cv, verbatim in logic."""
    preds, truths, picks = [], [], []
    for s in SEEDS:
        te = seed_of == s
        tr = ~te
        Xtr, ytr = X[tr], lab[tr]
        if ytr.sum() == 0 or ytr.sum() == len(ytr):
            return None
        mu, sd = Xtr.mean(0), Xtr.std(0)
        sd = np.where(sd > 0, sd, 1.0)
        Ztr = (Xtr - mu) / sd
        a, b = Ztr[ytr == 1], Ztr[ytr == 0]
        smd = np.abs(a.mean(0) - b.mean(0))
        j = int(np.argmax(smd))
        thr = 0.5 * (a[:, j].mean() + b[:, j].mean())
        sign = 1.0 if a[:, j].mean() > b[:, j].mean() else -1.0
        Zte = (X[te] - mu) / sd
        p = (sign * Zte[:, j] > sign * thr).astype(int)
        preds.extend(p.tolist())
        truths.extend(lab[te].tolist())
        picks.append(chans[j])
    return np.asarray(preds), np.asarray(truths), picks


def classifier(V, metric, chans):
    X, y, seed_of = [], [], []
    for arm, pre, lab in CLF_ARMS:
        for i, s in enumerate(SEEDS):
            X.append([V[arm][i][metric][c] for c in chans])
            y.append(lab)
            seed_of.append(s)
    X = np.asarray(X, float)
    y = np.asarray(y, int)
    seed_of = np.asarray(seed_of, int)
    preds, truths, picks = run_cv(X, y, seed_of, chans, y)
    acc = float((preds == truths).sum()) / 24.0
    return {"n_channels": len(chans), "accuracy": acc,
            "confusion": {"TP": int(((preds == 1) & (truths == 1)).sum()),
                          "FN": int(((preds == 0) & (truths == 1)).sum()),
                          "FP": int(((preds == 1) & (truths == 0)).sum()),
                          "TN": int(((preds == 0) & (truths == 0)).sum())},
            "channel_per_fold": picks,
            "hip_flexion_LmR_chosen_of_6": sum(1 for p in picks if p == "hip_flexion_LmR"),
            "hip_flexion_r_chosen_of_6": sum(1 for p in picks if p == "hip_flexion_r"),
            "ankle_angle_LmR_chosen_of_6": sum(1 for p in picks if p == "ankle_angle_LmR")}


def permnull(V, metric, sev):
    """Section 4: exhaustive C(12,6), 6 reflex vs 6 weakness at one severity.

    Statistic: the seed-level gap on hip_flexion_LmR. familywise = how many assignments
    reach the observed gap on ANY of the 16 channels; hip_only = on hip_flexion_LmR.
    """
    vals = {c: np.array([x[metric][c] for x in V["S"]] + [x[metric][c] for x in V[sev]])
            for c in CH}
    lab0 = np.array([1] * 6 + [0] * 6)

    def gap(v, lab):
        a, b = v[lab == 1], v[lab == 0]
        return (b.min() - a.max()) if b.mean() > a.mean() else (a.min() - b.max())

    obs = gap(vals["hip_flexion_LmR"], lab0)
    fam = hip = tot = 0
    reach = set()
    for comb in itertools.combinations(range(12), 6):
        lab = np.zeros(12, int)
        lab[list(comb)] = 1
        tot += 1
        hit = False
        for c in CH:
            if gap(vals[c], lab) >= obs - 1e-12:
                hit = True
                reach.add(c)
                if c == "hip_flexion_LmR":
                    hip += 1
        if hit:
            fam += 1
    return {"observed_gap_deg": float(obs), "n_assignments": tot,
            "familywise_count": fam, "familywise_proportion": fam / float(tot),
            "hip_only_count": hip, "hip_only_proportion": hip / float(tot),
            "selection_cost": (fam - hip) / float(tot),
            "channels_ever_reaching": sorted(reach),
            "n_channels_ever_reaching": len(reach)}


def main():
    out = {"round": 259,
           "why": ("sections 1, 2 and 4 disclosed that their results might be metric-dependent "
                   "rather than computing whether they are. This computes it."),
           "self_test": {}, "windows": {}}

    V = load_all(9.73)

    # ---- self-test against the deposits
    e16 = classifier(V, "excursion", CH)
    e4 = classifier(V, "excursion", LMR)
    d222 = json.load(io.open(os.path.join(PAPER, "CLASSIFIER_r222.json"), encoding="utf-8"))
    d223 = json.load(io.open(os.path.join(PAPER, "LMRONLY_r223.json"), encoding="utf-8"))
    st = {"CLASSIFIER_r222_channel_per_fold": e16["channel_per_fold"] == d222["channel_per_fold"],
          "CLASSIFIER_r222_confusion": e16["confusion"] == d222["confusion"],
          "LMRONLY_r223_channel_per_fold": e4["channel_per_fold"] == d223["channel_per_fold"],
          "LMRONLY_r223_confusion": e4["confusion"] == d223["confusion"]}
    p221 = permnull(V, "excursion", "W870")
    d221 = json.load(io.open(os.path.join(PAPER, "PERMNULL_r221.json"), encoding="utf-8"))
    st["PERMNULL_r221_W870_familywise"] = (
        p221["familywise_count"] == d221["severities"]["W870"]["familywise_count"])
    st["PERMNULL_r221_W870_gap"] = abs(
        p221["observed_gap_deg"] - d221["severities"]["W870"]["observed_gap_deg"]) < 1e-9
    out["self_test"] = st
    print("SELF-TEST against deposits:", st)
    if not all(st.values()):
        print("  *** SELF-TEST FAILED -- results below are NOT trusted ***")

    w = {"classifier": {}, "permnull": {}}
    for m in ("excursion", "mean_angle"):
        w["classifier"]["%s_16ch" % m] = classifier(V, m, CH)
        w["classifier"]["%s_4LmR" % m] = classifier(V, m, LMR)
        w["permnull"][m] = {s: permnull(V, m, s) for s in SEV}
    out["windows"]["9.73"] = w

    with io.open(os.path.join(PAPER, "RECOMPUTE_r259.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    print("\n-- CLASSIFIER, window [1.00, 9.73]")
    for k, v in w["classifier"].items():
        print("   %-22s acc %d/24  picks: %s"
              % (k, int(v["accuracy"] * 24), v["channel_per_fold"]))
    print("\n-- SECTION 4 NULLS, window [1.00, 9.73]")
    for m in ("excursion", "mean_angle"):
        for s in SEV:
            v = w["permnull"][m][s]
            print("   %-11s %-5s gap %+7.4f  familywise %d/924  hip %d/924  cost %+.4f  "
                  "channels reaching %d"
                  % (m, s, v["observed_gap_deg"], v["familywise_count"], v["hip_only_count"],
                     v["selection_cost"], v["n_channels_ever_reaching"]))


if __name__ == "__main__":
    main()
