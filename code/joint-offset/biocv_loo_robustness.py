"""Does any single participant carry a headline result?

With eleven participants and a sign-flip floor of 0.000977, a contrast reaching that floor means
all eleven agreed in direction -- and a referee's first question is whether one of them is doing
the work. The question is sharper here than usual: section 3.4 discloses that P26's hip-flexion
error more than doubles under the offset correction, so at least one participant is a demonstrated
outlier on at least one outcome.

This drops each participant in turn and re-runs the exact sign-flip test on the remaining ten
(2^10 = 1024 patterns, floor 0.001953). A result is robust if the verdict holds for all eleven
drops. Reported per contrast: the full-sample effect, the range of the eleven leave-one-out
effects, the worst (largest) leave-one-out p, and which participant produces it.

This is the analysis a referee asked for and the manuscript did not have. It can only strengthen
or weaken what is already claimed; it is not a new claim.

Output: D:/BioCV/BIOCV_LOO_ROBUSTNESS.txt
"""
import io
import itertools
import pickle

import numpy as np

OUTF = "D:/BioCV/BIOCV_LOO_ROBUSTNESS.txt"
PKLS = ["D:/BioCV/_persubj.pkl", "D:/BioCV/_persubj_round5.pkl", "D:/BioCV/_persubj_v2.pkl"]

# (label, level, baseline arm, treated arm) -- the contrasts the paper's claims rest on.
CONTRASTS = [
    ("[pos:HKA] uniform vs confidence weighting", "posl", "noRej_unif", "noRej_conf"),
    ("[pos:HKA] criterion, adaptive rejection", "posl", "rep_conf", "objd_conf"),
    ("[pos:HKA] LOO offset correction", "posl", "noRej_conf", "loo_corr"),
    ("[pos:HKA] GN: no rejection vs reproj rejection", "posl", "lm_noRej", "lm_repRej"),
    ("hip, criterion at matched k=2", "hip", "mk2_re", "mk2_ob"),
    ("knee, criterion at matched k=2", "knee", "mk2_re", "mk2_ob"),
    ("knee, criterion, adaptive rejection", "knee", "rep_conf", "objd_conf"),
    ("hip, uniform vs confidence weighting", "hip", "noRej_unif", "noRej_conf"),
    ("knee flexion, LOO offset correction", "knee_flex", "noRej_conf", "loo_corr"),
    ("knee flexion, GN: no rejection vs reproj", "knee_flex", "lm_noRej", "lm_repRej"),
    ("knee flexion, adaptive reprojection rejection", "knee_flex", "noRej_conf", "rep_conf"),
    ("frontal knee, uniform vs confidence weighting", "knee_abd", "noRej_unif", "noRej_conf"),
    ("hip flexion, uniform vs confidence weighting", "hip_flex", "noRej_unif", "noRej_conf"),
]

# The within-limb difference section 3.1 leads on, which is a difference of differences and so
# cannot be expressed as one arm pair.
SUBSETS = {"knee+ankle": ("knee", "ankle"), "hip+ankle": ("hip", "ankle"),
           "hip+knee+ankle": ("hip", "knee", "ankle")}

acc = {}
for f in PKLS:
    try:
        acc.update(pickle.load(open(f, "rb")))
    except OSError:
        pass


def sm(level, arm):
    key = (level, arm)
    if key not in acc:
        return None
    return {p: v[0] / v[1] for p, v in acc[key].items() if v[1] > 0}


def subset_mean(joints, arm):
    if any((j, arm) not in acc for j in joints):
        return None
    pids = set.intersection(*[set(acc[(j, arm)]) for j in joints])
    out = {}
    for p in pids:
        s = sum(acc[(j, arm)][p][0] for j in joints)
        n = sum(acc[(j, arm)][p][1] for j in joints)
        if n:
            out[p] = s / n
    return out


def exact_p(d):
    d = np.asarray(d, float)
    S = np.array(list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


def loo(pids, diffs):
    """Full-sample effect and p, then the eleven leave-one-out refits."""
    d = np.array([diffs[p] for p in pids])
    full_e, full_p = float(d.mean()), exact_p(d)
    rows = []
    for p in pids:
        dd = np.array([diffs[q] for q in pids if q != p])
        rows.append((p, float(dd.mean()), exact_p(dd)))
    return full_e, full_p, rows


L = []


def out(s):
    print(s)
    L.append(s)


out("LEAVE-ONE-PARTICIPANT-OUT ROBUSTNESS OF THE HEADLINE CONTRASTS")
out("")
out("Each participant dropped in turn; the exact sign-flip test re-run on the remaining ten")
out("(2^10 = 1024 patterns, smallest attainable p = 0.001953). 'worst p' is the largest p over the")
out("eleven refits and 'driver' the participant whose removal produces it. A contrast is robust")
out("when the direction is unchanged in all eleven refits and the worst p stays below 0.05.")
out("")
out(f"{'contrast':<48}{'effect':>9}{'p':>9}{'LOO min':>10}{'LOO max':>10}{'worst p':>9}"
    f"{'driver':>8}  verdict")

rows_out = []
for label, level, a, b in CONTRASTS:
    A, B = sm(level, a), sm(level, b)
    if A is None or B is None:
        out(f"{label:<48}  [arms not in the stored per-participant means]")
        continue
    pids = sorted(set(A) & set(B))
    diffs = {p: A[p] - B[p] for p in pids}
    e, p, rr = loo(pids, diffs)
    es = [x[1] for x in rr]
    worst = max(rr, key=lambda t: t[2])
    same_sign = all((x[1] > 0) == (e > 0) for x in rr)
    ok = same_sign and worst[2] < 0.05
    v = "robust" if ok else ("direction flips" if not same_sign else "p > 0.05 on one drop")
    out(f"{label:<48}{e:>+9.3f}{p:>9.4f}{min(es):>+10.3f}{max(es):>+10.3f}"
        f"{worst[2]:>9.4f}{worst[0]:>8}  {v}")
    rows_out.append((label, ok))

# The section 3.1 headline: {knee,ankle} against {hip,ankle} under matched k = 2, in mm.
A2, B2 = subset_mean(SUBSETS["knee+ankle"], "mk2_re"), subset_mean(SUBSETS["knee+ankle"], "mk2_ob")
A3, B3 = subset_mean(SUBSETS["hip+ankle"], "mk2_re"), subset_mean(SUBSETS["hip+ankle"], "mk2_ob")
if None not in (A2, B2, A3, B3):
    pids = sorted(set(A2) & set(B2) & set(A3) & set(B3))
    diffs = {p: (A2[p] - B2[p]) - (A3[p] - B3[p]) for p in pids}
    e, p, rr = loo(pids, diffs)
    es = [x[1] for x in rr]
    worst = max(rr, key=lambda t: t[2])
    same_sign = all((x[1] > 0) == (e > 0) for x in rr)
    ok = same_sign and worst[2] < 0.05
    out(f"{'{knee,ankle} vs {hip,ankle} at matched k=2 (mm)':<48}{e:>+9.3f}{p:>9.4f}"
        f"{min(es):>+10.3f}{max(es):>+10.3f}{worst[2]:>9.4f}{worst[0]:>8}  "
        f"{'robust' if ok else 'NOT robust'}")
    rows_out.append(("{knee,ankle} vs {hip,ankle} at matched k=2", ok))

n_ok = sum(1 for _l, ok in rows_out if ok)
out("")
out(f"{n_ok} of {len(rows_out)} headline contrasts are robust to dropping any single participant.")
frag = [l for l, ok in rows_out if not ok]
if frag:
    out("")
    out("Not robust -- the manuscript must say so wherever these are quoted:")
    for l in frag:
        out("  " + l)
else:
    out("")
    out("No headline result depends on any one participant.")

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
