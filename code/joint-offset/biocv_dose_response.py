"""Is the per-camera angle cost actually significant? A declared family for the dose-response.

The manuscript quoted "outlier rejection costs 0.20-0.40 deg of knee flexion per camera discarded"
in Practical implications and again in the Conclusion, and the Limitations used its cumulative form
as the paper's effect-size ceiling. Two independent cold readers found the same thing: its only
source was a table of four means with no p, no q, no interval and no n. Section 2.5 says every
contrast reduces to one mean difference per participant before testing. This one never was.

That is the paper's most concrete practical recommendation resting on its least tested quantity,
so it is tested here rather than softened in the prose.

The family is the six retention steps: two criteria (reprojection, object-space) x three retention
levels (k = 1, 2, 3), each against k = 0, on knee flexion. Exact sign-flip over 2^11 = 2048 sign
patterns, Benjamini-Hochberg within the six.

k = 0 is the no-rejection arm (noRej_conf): matched-k drops exactly k observations worst-first, so
k = 0 is no rejection by construction. Its pooled knee-flexion error differs by 0.005 deg between
the matched-k run and the multi-angle run because the two accumulate over slightly different
observation sets; the test here is per participant over each pair's own intersection, so that
difference does not enter.

POSITIVE effect = discarding raises knee-flexion error, i.e. the cost the recommendation claims.

Output: D:/BioCV/BIOCV_DOSE_RESPONSE.txt
"""
import io
import itertools
import pickle

import numpy as np

OUTF = "D:/BioCV/BIOCV_DOSE_RESPONSE.txt"
PKLS = ["D:/BioCV/_persubj.pkl", "D:/BioCV/_persubj_round5.pkl", "D:/BioCV/_persubj_v2.pkl"]

BASE = "noRej_conf"
STEPS = [
    ("reprojection criterion", 1, "mk1_re"), ("reprojection criterion", 2, "mk2_re"),
    ("reprojection criterion", 3, "mk3_re"),
    ("object-space criterion", 1, "mk1_ob"), ("object-space criterion", 2, "mk2_ob"),
    ("object-space criterion", 3, "mk3_ob"),
]

acc = {}
for f in PKLS:
    try:
        acc.update(pickle.load(open(f, "rb")))
    except OSError:
        pass

SIGNS = np.array(list(itertools.product([-1, 1], repeat=11)), dtype=float)


def per_subject(arm):
    key = ("knee_flex", arm)
    if key not in acc:
        raise SystemExit(f"no per-participant accumulator for {key}")
    return {p: s / n for p, (s, n) in
            ((p, acc[key][p]) for p in acc[key]) if n}


def exact_p(d):
    d = np.asarray(d, float)
    S = SIGNS if len(d) == 11 else np.array(
        list(itertools.product([-1, 1], repeat=len(d))), dtype=float)
    return float((np.abs((S * d).mean(axis=1)) >= abs(d.mean()) - 1e-15).sum()) / len(S)


b = per_subject(BASE)
rows = []
for crit, k, arm in STEPS:
    t = per_subject(arm)
    pids = sorted(set(b) & set(t))
    if len(pids) < 4:
        raise SystemExit(f"only {len(pids)} participants for {arm}")
    d = np.array([t[p] - b[p] for p in pids])   # positive = discarding is worse
    rows.append((crit, k, float(np.mean([b[p] for p in pids])),
                 float(np.mean([t[p] for p in pids])), float(d.mean()),
                 float(d.mean()) / k, exact_p(d), len(pids)))

ps = [r[6] for r in rows]
m = len(ps)
order = sorted(range(m), key=lambda i: ps[i])
q = [0.0] * m
prev = 1.0
for rank, i in enumerate(reversed(order), start=1):
    prev = q[i] = min(prev, ps[i] * m / (m - rank + 1))

L = []


def out(s):
    print(s)
    L.append(s)


out("DOSE-RESPONSE: DOES DISCARDING COST THE KNEE ANGLE, AND BY HOW MUCH PER CAMERA?")
out("")
out(f"Family size m = {m}: two criteria x three retention levels, each against k = 0 (no")
out("rejection). Knee flexion, mean absolute error in degrees. The inferential unit is the")
out("participant; exact sign-flip over 2^11 = 2048 patterns; Benjamini-Hochberg within the six.")
out("")
out("POSITIVE effect = discarding RAISES knee-flexion error, which is the cost the manuscript's")
out("practical recommendation claims. A negative effect would mean discarding helps.")
out("")
out(f"{'criterion':<24}{'k':>3}{'k=0 deg':>10}{'k deg':>9}{'cost deg':>10}{'per camera':>12}"
    f"{'p':>9}{'BH q':>9}  verdict")
for (crit, k, b0, bk, cost, per, p, n), qq in zip(rows, q):
    v = "SURVIVES" if qq < 0.05 else ("raw only" if p < 0.05 else "n.s.")
    out(f"{crit:<24}{k:>3}{b0:>10.3f}{bk:>9.3f}{cost:>+10.3f}{per:>+12.3f}{p:>9.4f}{qq:>9.4f}  {v}")

surv = sum(1 for qq in q if qq < 0.05)
out("")
out(f"{surv} of {m} survive BH.")
per_cam = [r[5] for r, qq in zip(rows, q) if qq < 0.05]
if per_cam:
    out(f"Per-camera cost across the surviving steps: {min(per_cam):.2f} to {max(per_cam):.2f} deg.")
    out("That range, and only that range, may be quoted as the per-camera cost.")
else:
    out("NO step survives correction. The per-camera cost must be reported as descriptive only,")
    out("and must not appear in the Conclusion or in Practical implications.")
out("")
cum = {c: max(r[4] for r in rows if r[0] == c) for c in {r[0] for r in rows}}
out("Cumulative cost at k = 3: " + "; ".join(f"{c} {v:+.3f} deg" for c, v in sorted(cum.items())))

io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\nWROTE", OUTF)
