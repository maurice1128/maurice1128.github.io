"""
Publication-grade significance for the BioCV real-GT severe-joint test.
Reads biocv_rows_{mode}.npy (asym, err_reproj_mm, err_dist_mm) + biocv_trials_{mode}.npy.

Per asymmetry bin reports, for the paired difference d = err_reproj - err_dist
(POSITIVE = distance-correction better):
  - n obs, n trials
  - mean err reproj / dist, dMEAN, and 95% CLUSTER bootstrap CI (resample TRIALS,
    respecting within-trial temporal + left/right correlation -> honest inference)
  - dP95 (P95 reproj - P95 dist) with cluster bootstrap CI
  - naive obs-level Wilcoxon p (OPTIMISTIC; shown only for reference)
A bin's effect is credible iff its cluster-bootstrap CI for dMEAN (or dP95)
excludes 0. Result -> D:/BioCV/BIOCV_STATS_{mode}.txt
"""
import os, sys, numpy as np
from scipy.stats import wilcoxon

MODE = os.environ.get("BIOCV_MODE", "balanced")
B = 5000
SEED = 12345
rng = np.random.default_rng(SEED)

rows = np.load(f"D:/BioCV/biocv_rows_{MODE}.npy")
trials = np.load(f"D:/BioCV/biocv_trials_{MODE}.npy")
asym, er, ed = rows[:, 0], rows[:, 1], rows[:, 2]
uniq_trials = np.unique(trials)

BINS = [(1,1.6,'<1.6'),(1.6,2,'1.6-2'),(2,2.5,'2-2.5'),
        (2.5,3,'2.5-3'),(3,99,'>3')]

lines = []
def out(s): print(s); lines.append(s)

out(f"BioCV real Vicon GT severe-joint stats (mode={MODE}) "
    f"N={len(rows)} obs, {len(uniq_trials)} trials, {B} cluster-bootstrap reps")
out("d = err_reproj - err_dist (mm); POSITIVE = distance better. "
    "CI excludes 0 => credible.")
out(f"{'bin':>8}{'n':>7}{'nTr':>5}{'mRe':>7}{'mDi':>7}{'dMEAN':>7}"
    f"{'  dMEAN 95%CI':>18}{'dP95':>7}{'  dP95 95%CI':>18}{'  Wilcox p':>11}")

for lo, hi, nm in BINS:
    m = (asym >= lo) & (asym < hi)
    n = int(m.sum())
    if n < 20:
        out(f"{nm:>8}{n:>7}   (too few)"); continue
    er_b, ed_b, tr_b = er[m], ed[m], trials[m]
    d = er_b - ed_b
    ntr = len(np.unique(tr_b))
    dmean = d.mean()
    dp95 = np.percentile(er_b, 95) - np.percentile(ed_b, 95)
    # cluster bootstrap over trials present in this bin
    tlist = np.unique(tr_b)
    idx_by_trial = {t: np.where(tr_b == t)[0] for t in tlist}
    bs_mean = np.empty(B); bs_p95 = np.empty(B)
    for b in range(B):
        pick = rng.choice(tlist, size=len(tlist), replace=True)
        ii = np.concatenate([idx_by_trial[t] for t in pick])
        e1, e2 = er_b[ii], ed_b[ii]
        bs_mean[b] = (e1 - e2).mean()
        bs_p95[b] = np.percentile(e1, 95) - np.percentile(e2, 95)
    ci_m = np.percentile(bs_mean, [2.5, 97.5])
    ci_p = np.percentile(bs_p95, [2.5, 97.5])
    try:
        _, pw = wilcoxon(er_b, ed_b)
    except Exception:
        pw = float('nan')
    star_m = "*" if (ci_m[0] > 0 or ci_m[1] < 0) else " "
    out(f"{nm:>8}{n:>7}{ntr:>5}{er_b.mean():>7.1f}{ed_b.mean():>7.1f}"
        f"{dmean:>+7.2f}{f'[{ci_m[0]:+.1f},{ci_m[1]:+.1f}]{star_m}':>18}"
        f"{dp95:>+7.1f}{f'[{ci_p[0]:+.1f},{ci_p[1]:+.1f}]':>18}{pw:>11.1e}")

out("")
out("READ: '*' = dMEAN CI excludes 0 (trial-clustered, honest). Wilcoxon is "
    "obs-level (ignores correlation) => treat as optimistic upper bound on sig.")
open(f"D:/BioCV/BIOCV_STATS_{MODE}.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
