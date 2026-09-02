"""
Publication figure for the BioCV real-GT asymmetry finding.
Panel A: mean 3D position error (mm) vs asymmetry, reproj vs distance.
Panel B: distance advantage dMEAN = err_reproj - err_dist with 95% trial-cluster
         bootstrap CI; horizontal 0 line; shaded onset region asym>=2.5.
Reads biocv_rows_{mode}.npy + biocv_trials_{mode}.npy -> D:/BioCV/biocv_asym_{mode}.png
"""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODE = os.environ.get("BIOCV_MODE", "balanced")
B = 5000
rng = np.random.default_rng(7)
rows = np.load(f"D:/BioCV/biocv_rows_{MODE}.npy")
trials = np.load(f"D:/BioCV/biocv_trials_{MODE}.npy")
asym, er, ed = rows[:, 0], rows[:, 1], rows[:, 2]

BINS = [(1.6,2,'1.6-2',1.8),(2,2.5,'2-2.5',2.25),
        (2.5,3,'2.5-3',2.75),(3,4,'>3',3.3)]
xs, mre, mdi, dmean, lo_ci, hi_ci = [], [], [], [], [], []
for a, b, nm, mid in BINS:
    m = (asym >= a) & (asym < b)
    if m.sum() < 20: continue
    er_b, ed_b, tr_b = er[m], ed[m], trials[m]
    xs.append(mid); mre.append(er_b.mean()); mdi.append(ed_b.mean())
    tl = np.unique(tr_b); idx = {t: np.where(tr_b == t)[0] for t in tl}
    bs = np.empty(B)
    for k in range(B):
        pick = rng.choice(tl, size=len(tl), replace=True)
        ii = np.concatenate([idx[t] for t in pick])
        bs[k] = (er_b[ii] - ed_b[ii]).mean()
    dmean.append((er_b - ed_b).mean())
    ci = np.percentile(bs, [2.5, 97.5]); lo_ci.append(ci[0]); hi_ci.append(ci[1])

xs = np.array(xs)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot(xs, mre, 'o-', color='#c44', label='reprojection removal')
ax1.plot(xs, mdi, 's-', color='#37a', label='distance (object-space) removal')
ax1.set_xlabel('camera-distance asymmetry  max/min'); ax1.set_ylabel('mean 3D position error (mm)')
ax1.set_title('BioCV real Vicon GT — ankle/wrist'); ax1.legend(); ax1.grid(alpha=.3)

yerr = np.vstack([np.array(dmean) - np.array(lo_ci), np.array(hi_ci) - np.array(dmean)])
ax2.axhline(0, color='k', lw=.8)
ax2.axvspan(2.5, xs.max() + 0.2, color='#37a', alpha=.08)
ax2.errorbar(xs, dmean, yerr=yerr, fmt='D-', color='#37a', capsize=4)
ax2.set_xlabel('camera-distance asymmetry  max/min')
ax2.set_ylabel('distance advantage  (err_reproj − err_dist, mm)')
ax2.set_title('advantage emerges at asym ≳ 2.5  (95% trial-cluster CI)')
ax2.grid(alpha=.3)
fig.tight_layout()
fig.savefig(f"D:/BioCV/biocv_asym_{MODE}.png", dpi=140)
print(f"saved D:/BioCV/biocv_asym_{MODE}.png")
print("bins:", [b[2] for b in BINS if True])
print("dMEAN:", [f"{d:+.2f}" for d in dmean])
print("CIs:", [f"[{l:+.1f},{h:+.1f}]" for l, h in zip(lo_ci, hi_ci)])
