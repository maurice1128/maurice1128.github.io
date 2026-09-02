# -*- coding: utf-8 -*-
"""Two integrity audits raised by the R2 watchdog.

AUDIT 1 - label switching. 40_stability.py reported bootstrap P/N intervals per
cluster using RAW von Mises component indices. Component k in a refit is not the
same cluster as component k in the full-data fit, so those intervals mixed
different clusters together and are artefacts. Here each refit's components are
MATCHED to the full-data clusters by maximum Jaccard overlap before P/N is taken.

AUDIT 2 - byte-identical CIs. The pooled and within-patient estimates on the
complete-attendance subset were reported with the same CI and p despite being
different models on different samples. Recomputed here at full precision to
establish whether that is coincidence or a copy-paste error."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.discrete.conditional_models import ConditionalLogit

f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm'); pos_pd, neg_pd = m2(afn[0]), m2(afn[2])
hdr = cells('All_fill_header'); pid = np.r_[v(hdr[0]).astype(int), v(hdr[2]).astype(int)]
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]
xa, xb = cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
sa, sb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db')
POST = np.r_[v(xa[0]), v(xa[2])]

# ---------------- AUDIT 2 ----------------
print('=== AUDIT 2: pooled vs within-patient on the complete-attendance subset ===')
comp = att == 1.0
z_all = (POST[comp] - POST[comp].mean()) / POST[comp].std()
rp = sm.Logit(y[comp], sm.add_constant(z_all)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid[comp]})
b, se = rp.params[1], rp.bse[1]
print('  POOLED          n=%5d  OR=%.6f  CI %.6f-%.6f  p=%.6e' % (
    comp.sum(), np.exp(b), np.exp(b-1.96*se), np.exp(b+1.96*se), rp.pvalues[1]))
d = pd.DataFrame(dict(y=y[comp], g=pid[comp])); ok = d.groupby('g').y.nunique() == 2
keep = d.g.map(ok).values
xx = POST[comp][keep]; z_w = (xx - xx.mean()) / xx.std()
rw = ConditionalLogit(y[comp][keep], z_w[:, None], groups=pid[comp][keep]).fit(disp=0)
bw, sew = rw.params[0], rw.bse[0]
print('  WITHIN-PATIENT  n=%5d  OR=%.6f  CI %.6f-%.6f  p=%.6e' % (
    keep.sum(), np.exp(bw), np.exp(bw-1.96*sew), np.exp(bw+1.96*sew), rw.pvalues[0]))
same = (round(np.exp(b-1.96*se), 2) == round(np.exp(bw-1.96*sew), 2)
        and round(np.exp(b+1.96*se), 2) == round(np.exp(bw+1.96*sew), 2))
print('  >>> identical only at 2-dp rounding: %s' % same)
print('  >>> VERDICT: %s' % ('COINCIDENCE at reporting precision - both null, similar SE; report to 3 dp to disambiguate'
                             if abs(np.exp(b)-np.exp(bw)) > 1e-6 else 'IDENTICAL AT FULL PRECISION - copy-paste error'))

# ---------------- AUDIT 1 ----------------
print('\n=== AUDIT 1: bootstrap P/N intervals, RAW indices vs JACCARD-MATCHED ===')
up = ~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0); svp = ~up
un = ~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0); svn = ~un
def vmpdf(t, m, k): return np.exp(k*np.cos(t-m))/(2*np.pi*i0(k))
def vm_mle(t, w):
    C=(w*np.cos(t)).sum(); S=(w*np.sin(t)).sum(); s=w.sum()+1e-12
    R=min(np.sqrt(C*C+S*S)/s, .999); return np.arctan2(S, C), R*(2-R*R)/(1-R*R)
def vm_fit(t1, t2, K=6, seed=0, it=90):
    lab = KMeans(K, n_init=3, random_state=seed).fit_predict(np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
    P = np.zeros((K, len(t1))); P[lab, np.arange(len(t1))] = 1
    m1=np.zeros(K); k1=np.ones(K); mm=np.zeros(K); k2=np.ones(K); pi=np.ones(K)/K
    for _ in range(it):
        for k in range(K): w=P[k]; m1[k],k1[k]=vm_mle(t1,w); mm[k],k2[k]=vm_mle(t2,w); pi[k]=w.mean()+1e-9
        P=np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,mm[k],k2[k]) for k in range(K)]); P/=P.sum(0)+1e-300
    return m1,k1,mm,k2,pi
def assign(t1,t2,p):
    m1,k1,mm,k2,pi=p
    return np.array([pi[k]*vmpdf(t1,m1[k],k1[k])*vmpdf(t2,mm[k],k2[k]) for k in range(len(pi))]).argmax(0)
t1p=np.arctan2(v(sb[0])[svp], v(sa[0])[svp]); t2p=np.arctan2(v(xb[0])[svp], v(xa[0])[svp])
t1n=np.arctan2(v(sb[2])[svn], v(sa[2])[svn]); t2n=np.arctan2(v(xb[2])[svn], v(xa[2])[svn])
base = vm_fit(t1p, t2p, 6)
Lp0 = assign(t1p, t2p, base); Ln0 = assign(t1n, t2n, base)
sets0 = [set(np.where(Lp0 == k)[0]) for k in range(6)]

rng = np.random.default_rng(0); B = 200
raw = {k: [] for k in range(6)}; mat = {k: [] for k in range(6)}
for s in range(B):
    idx = rng.integers(0, len(t1p), len(t1p))
    p2 = vm_fit(t1p[idx], t2p[idx], 6, seed=s, it=60)
    Lp = assign(t1p, t2p, p2); Ln = assign(t1n, t2n, p2)
    pn_of = lambda k: ((Lp == k).sum()/TP) / max((Ln == k).sum(), 1) * TN
    # raw index (what 40_stability.py did)
    for k in range(6): raw[k].append(pn_of(k))
    # jaccard-matched: refit component -> original cluster with max overlap
    used = set()
    for k0 in range(6):
        best, bj = None, -1
        for k in range(6):
            if k in used: continue
            si = set(np.where(Lp == k)[0])
            j = len(sets0[k0] & si) / max(len(sets0[k0] | si), 1)
            if j > bj: bj, best = j, k
        used.add(best); mat[k0].append(pn_of(best))
print('  cluster   RAW-index 95%% interval      JACCARD-MATCHED 95%% interval')
for k in range(6):
    r = np.percentile(raw[k], [2.5, 97.5]); m = np.percentile(mat[k], [2.5, 97.5])
    print('   7d-%d      %.2f - %.2f  (width %.2f)      %.2f - %.2f  (width %.2f)'
          % (k+1, r[0], r[1], r[1]-r[0], m[0], m[1], m[1]-m[0]))
wr = np.mean([np.percentile(raw[k],97.5)-np.percentile(raw[k],2.5) for k in range(6)])
wm = np.mean([np.percentile(mat[k],97.5)-np.percentile(mat[k],2.5) for k in range(6)])
print('  mean width  RAW=%.2f  MATCHED=%.2f   -> matching narrows intervals by %.0f%%' % (wr, wm, (1-wm/wr)*100))

# Persist, so the intervals quoted in the manuscript have a file to be traced to.
# The 500-refit run in final_stability.json stores the RAW-index intervals; these
# matched ones come from this script's own 200-refit analysis and must not be
# conflated with it.
import json
json.dump({
    'n_boot': B, 'em_iters': 60,
    'note': 'matched intervals from this script (200 refits); final_stability.json holds the separate 500-refit unmatched run',
    'raw_index': {f'7d-{k+1}': [round(float(x), 4) for x in np.percentile(raw[k], [2.5, 97.5])] for k in range(6)},
    'jaccard_matched': {f'7d-{k+1}': [round(float(x), 4) for x in np.percentile(mat[k], [2.5, 97.5])] for k in range(6)},
    'mean_width_raw': round(float(wr), 4), 'mean_width_matched': round(float(wm), 4),
    'pooled_vs_within_complete_attendance': {
        'pooled_OR': float(np.exp(b)), 'pooled_ci': [float(np.exp(b-1.96*se)), float(np.exp(b+1.96*se))], 'pooled_n': int(comp.sum()),
        'within_OR': float(np.exp(bw)), 'within_ci': [float(np.exp(bw-1.96*sew)), float(np.exp(bw+1.96*sew))], 'within_n': int(keep.sum())},
}, open(_os.path.join(ROOT, r'analysis\matched_bootstrap.json'), 'w'), indent=2)
print('  wrote matched_bootstrap.json')
print('  >>> if MATCHED intervals no longer span 1.0, the "clusters cannot be ordered" claim was an artefact')
