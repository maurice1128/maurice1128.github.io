"""pairing_r251.py -- round 251, step 1 (of a registered two-step: PREREG_pairing_r251.md).

Does the shared optimiser seed survive re-optimisation?

If it does, the cells are paired and the permutation null must swap arm labels WITHIN seed
(2**6 = 64 assignments). If it does not, the unpaired C(12,6) = 924 null is correct.

Read-only. Uses per-seed arrays already deposited; recomputes nothing from .sto.
Per-seed arrays in LADDER36_r228.json / ANKLE_LADDER_r235.json are in SEED ORDER (s101..s106);
verified here against the sorted copies in their own `disjointness` blocks.
"""
import io, json, os, itertools

PAPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper")
ARMS = ["C", "S", "W800", "W870", "W892", "W900", "W915", "W950"]


def load(n):
    return json.load(io.open(os.path.join(PAPER, n), encoding="utf-8"))


def mean(v):
    return sum(v) / len(v)


def pearson(a, b):
    ma, mb = mean(a), mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    return num / (da * db) if da and db else float("nan")


def rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for pos, i in enumerate(s):
        r[i] = pos + 1
    return r


def spearman(a, b):
    return pearson(rank(a), rank(b))


def icc_two_way(mat):
    """mat[arm][seed]. Two-way decomposition: value = mu + arm + seed + err.
    Returns the share of non-arm variance attributable to seed."""
    na, ns = len(mat), len(mat[0])
    grand = mean([v for row in mat for v in row])
    arm_m = [mean(row) for row in mat]
    seed_m = [mean([mat[a][s] for a in range(na)]) for s in range(ns)]
    ss_seed = na * sum((m - grand) ** 2 for m in seed_m)
    ss_err = sum((mat[a][s] - arm_m[a] - seed_m[s] + grand) ** 2
                 for a in range(na) for s in range(ns))
    df_seed, df_err = ns - 1, (na - 1) * (ns - 1)
    ms_seed, ms_err = ss_seed / df_seed, ss_err / df_err
    var_seed = (ms_seed - ms_err) / na
    icc = var_seed / (var_seed + ms_err) if (var_seed + ms_err) > 0 else 0.0
    return {"ms_seed": ms_seed, "ms_err": ms_err, "F_seed": ms_seed / ms_err,
            "var_seed_component": var_seed, "icc_seed": icc,
            "ss_seed": ss_seed, "ss_err": ss_err, "df_seed": df_seed, "df_err": df_err}


def f_p(F, d1, d2, n=200000):
    """Monte-Carlo-free upper tail of F via regularised incomplete beta (continued fraction)."""
    x = d2 / (d2 + d1 * F)
    a, b = d2 / 2.0, d1 / 2.0
    # continued fraction for I_x(a,b)
    import math
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 300):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        d = 1e-30 if abs(d) < 1e-30 else d
        d = 1.0 / d
        c = 1.0 + num / c
        c = 1e-30 if abs(c) < 1e-30 else c
        f *= c * d
        if abs(1.0 - c * d) < 1e-12:
            break
    return front * (f - 1.0)


def block(per_seed, name):
    # order check: per_seed must be the unsorted (seed-order) copy
    mat = [per_seed[a] for a in ARMS]
    pairs = {}
    pv, sv = [], []
    for a, b in itertools.combinations(ARMS, 2):
        p, s = pearson(per_seed[a], per_seed[b]), spearman(per_seed[a], per_seed[b])
        pairs["%s~%s" % (a, b)] = {"pearson": p, "spearman": s}
        pv.append(p)
        sv.append(s)
    ic = icc_two_way(mat)
    ic["p_seed_effect"] = f_p(ic["F_seed"], ic["df_seed"], ic["df_err"])
    return {"channel": name, "n_arms": len(ARMS), "n_seeds": 6,
            "pairwise": pairs,
            "n_pairs": len(pv),
            "pearson_mean": mean(pv), "pearson_min": min(pv), "pearson_max": max(pv),
            "pearson_positive_count": sum(1 for x in pv if x > 0),
            "spearman_mean": mean(sv),
            "spearman_positive_count": sum(1 for x in sv if x > 0),
            "seed_variance": ic}


def main():
    lad = load("LADDER36_r228.json")
    ank = load("ANKLE_LADDER_r235.json")
    hip = lad["per_seed_hip_flexion_LmR"]
    ankp = ank["per_seed"]

    # verify seed-order arrays are NOT the sorted copies
    chk = {}
    for k, v in lad["disjointness"].items():
        chk["hip_" + k] = (hip[k] != v["seeds"] and sorted(hip[k]) == sorted(v["seeds"]))

    res = {"round": 251,
           "prereg": "PREREG_pairing_r251.md",
           "question": "does the shared optimiser seed survive re-optimisation",
           "inputs": ["LADDER36_r228.json", "ANKLE_LADDER_r235.json"],
           "seed_order_arrays_confirmed_unsorted": chk,
           "hip_flexion_LmR": block(hip, "hip_flexion_LmR"),
           "ankle_angle_LmR": block(ankp, "ankle_angle_LmR")}

    with io.open(os.path.join(PAPER, "PAIRING_r251.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    for ch in ["hip_flexion_LmR", "ankle_angle_LmR"]:
        b = res[ch]
        print("=== %s   (%d arm pairs, 6 seeds)" % (ch, b["n_pairs"]))
        print("   pearson  mean %+.4f   range %+.4f .. %+.4f   positive %d/%d"
              % (b["pearson_mean"], b["pearson_min"], b["pearson_max"],
                 b["pearson_positive_count"], b["n_pairs"]))
        print("   spearman mean %+.4f   positive %d/%d"
              % (b["spearman_mean"], b["spearman_positive_count"], b["n_pairs"]))
        v = b["seed_variance"]
        print("   seed effect: F(%d,%d) = %.4f   p = %.4f   ICC = %+.4f"
              % (v["df_seed"], v["df_err"], v["F_seed"], v["p_seed_effect"], v["icc_seed"]))
    print()
    print("seed-order arrays confirmed unsorted:", all(res["seed_order_arrays_confirmed_unsorted"].values()))


if __name__ == "__main__":
    main()
