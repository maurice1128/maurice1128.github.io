# -*- coding: utf-8 -*-
"""Step 44 - a properly powered test of the ESCALATION-ORDERED GRADIENT.

Round-2 reviewers B2/B3/B4 established that the only quantitative support for
the gradient was a 5-point K-sweep of Spearman rho (n = 4..8 clusters), four of
whose five p-values are non-significant, including at K = 6, the resolution the
paper reports. That statistic cannot be rescued: with 6 points it has no power.

This script replaces it with the statistic the reviewers asked for: the
BOOTSTRAP DISTRIBUTION of the escalation -> P/N rank correlation across 500
refits of the K = 6 dose-change mixture (the same 500-refit machinery as
40_stability.py), plus the P/N SPREAD between the top- and bottom-escalation
components. If that distribution excludes zero while the individual per-cluster
P/N intervals do not, "boundaries unstable, gradient stable" becomes a measured
claim rather than an assertion.

Everything is computed for BOTH ordering variables --
    mx_b : PRE-test max slope  (the component the paper claims)
    mx_a : POST-test max slope (the component the paper explicitly declines to claim)
-- and on BOTH the full interpolated sample and the genuinely imputation-free
+-7 subset (free7, no -1 anywhere in All_raw_fix cols 21:36; see 42_*).

Also emitted:
  * exact permutation p for the K = 4 Spearman value flagged as degenerate
  * per-cluster within-patient conditional-logit OR on free7 (to name the
    strongest surviving contrast in 3.6)
Writes gradient_bootstrap.json
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings, sys; warnings.filterwarnings('ignore')
from scipy.special import i0
from scipy.stats import spearmanr, permutation_test
from sklearn.cluster import KMeans
import pandas as pd
from statsmodels.discrete.conditional_models import ConditionalLogit

OUT = _os.path.join(ROOT, r'analysis')
NBOOT = int(sys.argv[1]) if len(sys.argv) > 1 else 500
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm'); pos_pd, neg_pd = m2(afn[0]), m2(afn[2])
raw = cells('All_raw_fix'); rpos, rneg = m2(raw[0]), m2(raw[2])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
sa, sb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db')
xa, xb = cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
f.close()
TP, TN = 3401, 6499

svp = np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0     # dose-change branch, positives
svn = np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0     # dose-change branch, negatives
free7_p = ~(rpos[:, 21:36] == -1).any(1)
free7_n = ~(rneg[:, 21:36] == -1).any(1)

def vmpdf(t, m, k): return np.exp(k * np.cos(t - m)) / (2 * np.pi * i0(k))
def vm_mle(t, w):
    C = (w * np.cos(t)).sum(); S = (w * np.sin(t)).sum(); s = w.sum() + 1e-12
    R = min(np.sqrt(C * C + S * S) / s, 0.999); return np.arctan2(S, C), R * (2 - R * R) / (1 - R * R)
def fit7(t1, t2, K=6, seed=0, it=150, n_init=5):
    lab = KMeans(K, n_init=n_init, random_state=seed).fit_predict(
        np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
    P = np.zeros((K, len(t1))); P[lab, np.arange(len(t1))] = 1
    m1 = np.zeros(K); k1 = np.ones(K); m2_ = np.zeros(K); k2 = np.ones(K); pi = np.ones(K) / K
    for _ in range(it):
        for k in range(K):
            w = P[k]; m1[k], k1[k] = vm_mle(t1, w); m2_[k], k2[k] = vm_mle(t2, w); pi[k] = w.mean() + 1e-9
        P = np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, m2_[k], k2[k]) for k in range(K)])
        P /= P.sum(0) + 1e-300
    return (m1, k1, m2_, k2, pi)
def asg7(t1, t2, pr):
    m1, k1, m2_, k2, pi = pr
    return np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, m2_[k], k2[k]) for k in range(len(pi))]).argmax(0)

t1p = np.arctan2(pos['mn_b'][svp], pos['mn_a'][svp]); t2p = np.arctan2(pos['mx_b'][svp], pos['mx_a'][svp])
t1n = np.arctan2(neg['mn_b'][svn], neg['mn_a'][svn]); t2n = np.arctan2(neg['mx_b'][svn], neg['mx_a'][svn])
ESC = {'pre-test (mx_b, CLAIMED)': (pos['mx_b'][svp], neg['mx_b'][svn]),
       'post-test (mx_a, not claimed)': (pos['mx_a'][svp], neg['mx_a'][svn])}
SUB = {'full': (np.ones(int(svp.sum()), bool), np.ones(int(svn.sum()), bool)),
       'free7': (free7_p[svp], free7_n[svn])}

def gradient_stats(lp, ln, escp, escn, mp, mn, K=6, minn=5):
    """rank correlation between a component's mean escalation and its P/N,
    and the P/N ratio of the top- vs bottom-escalation component."""
    tp = int(mp.sum()); tn = int(mn.sum())
    e, pn = [], []
    for c in range(K):
        a = int(((lp == c) & mp).sum()); b = int(((ln == c) & mn).sum())
        if a < minn or b < minn: continue
        e.append(float(np.r_[escp[(lp == c) & mp], escn[(ln == c) & mn]].mean()))
        pn.append((a / tp) / (b / tn))
    if len(e) < 3: return None
    e = np.array(e); pn = np.array(pn)
    rho = spearmanr(e, pn).statistic
    o = np.argsort(e)
    return dict(rho=float(rho), spread=float(pn[o[-1]] / pn[o[0]]), k=len(e))

pr0 = fit7(t1p, t2p, 6)
lp0 = asg7(t1p, t2p, pr0); ln0 = asg7(t1n, t2n, pr0)

res = {}
print(f'=== gradient bootstrap ({NBOOT} K=6 refits, same machinery as 40_stability.py) ===')
rs = np.random.RandomState(0)
n7 = len(t1p)
boot_lp, boot_ln = [], []
for i in range(NBOOT):
    idx = rs.choice(n7, n7, replace=True)
    prb = fit7(t1p[idx], t2p[idx], 6, seed=0, it=60, n_init=1)
    boot_lp.append(asg7(t1p, t2p, prb)); boot_ln.append(asg7(t1n, t2n, prb))
    if (i + 1) % 100 == 0: print(f'  refit {i+1}/{NBOOT}', flush=True)

for esc_nm, (ep, en) in ESC.items():
    for sub_nm, (mp, mn) in SUB.items():
        obs = gradient_stats(lp0, ln0, ep, en, mp, mn)
        rhos, sprd = [], []
        for lp, ln in zip(boot_lp, boot_ln):
            g = gradient_stats(lp, ln, ep, en, mp, mn)
            if g: rhos.append(g['rho']); sprd.append(g['spread'])
        rhos = np.array(rhos); sprd = np.array(sprd)
        d = dict(observed_rho=obs['rho'], observed_spread=obs['spread'],
                 boot_n=len(rhos),
                 rho_median=float(np.median(rhos)),
                 rho_lo=float(np.percentile(rhos, 2.5)), rho_hi=float(np.percentile(rhos, 97.5)),
                 frac_rho_positive=float((rhos > 0).mean()),
                 spread_median=float(np.median(sprd)),
                 spread_lo=float(np.percentile(sprd, 2.5)), spread_hi=float(np.percentile(sprd, 97.5)),
                 frac_spread_gt1=float((sprd > 1).mean()))
        res[f'{esc_nm} | {sub_nm}'] = d
        print(f'\n  ordering={esc_nm}  subset={sub_nm}')
        print(f'    observed rho={d["observed_rho"]:+.2f}  spread(top/bottom P/N)={d["observed_spread"]:.2f}')
        print(f'    bootstrap rho    : median {d["rho_median"]:+.2f}  95% {d["rho_lo"]:+.2f}..{d["rho_hi"]:+.2f}'
              f'  P(rho>0)={d["frac_rho_positive"]:.3f}')
        print(f'    bootstrap spread : median {d["spread_median"]:.2f}  95% {d["spread_lo"]:.2f}..{d["spread_hi"]:.2f}'
              f'  P(spread>1)={d["frac_spread_gt1"]:.3f}')

# ---------- exact permutation p for a degenerate n=4 Spearman rho = 1 ----------
a = np.array([1., 2., 3., 4.]); b = np.array([1., 2., 3., 4.])
pt = permutation_test((a, b), lambda x, y: spearmanr(x, y).statistic,
                      permutation_type='pairings', alternative='two-sided', n_resamples=100000)
res['k4_degenerate'] = dict(rho=1.0, n=4, asymptotic_p_reported_by_scipy=0.0,
                            exact_two_sided_p=float(pt.pvalue))
print(f'\n=== K=4 degeneracy check: rho=+1.00 with n=4 -> scipy asymptotic p=0.0, '
      f'EXACT two-sided permutation p={pt.pvalue:.3f} ===')

# ---------- per-cluster within-patient OR on free7 (to name the strongest contrast) ----------
print('\n=== within-patient cluster contrasts on free7 (dose-change + stable-dose, joint model) ===')
f2 = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
c2 = lambda n: [np.array(f2[r]) for r in np.array(f2[n]).ravel()]
coeff = np.array(f2['coeff']); mu0 = v(f2['mu'])
afn2 = c2('All_fill_norm'); ppd, pds, npd_, nds = m2(afn2[0]), m2(afn2[1]), m2(afn2[2]), m2(afn2[3])
f2.close()
up = ~svp; un = ~svn
proj = lambda A, B, mk: (np.hstack([A[mk], B[mk]]) - mu0) @ coeff.T
thp = np.arctan2(proj(ppd, pds, up)[:, 1] - .0270, proj(ppd, pds, up)[:, 0] + .04) % (2 * np.pi)
thn = np.arctan2(proj(npd_, nds, un)[:, 1] - .0270, proj(npd_, nds, un)[:, 0] + .04) % (2 * np.pi)
G = np.linspace(0, 2 * np.pi, 721)[:-1]
dd = np.array([np.exp(12 * np.cos(g - thp)).sum() for g in G])
cuts = np.sort(G[[i for i in range(len(dd)) if dd[i] < dd[(i - 1) % len(dd)] and dd[i] <= dd[(i + 1) % len(dd)]]])
clab = np.empty(TP + TN, object)
clab[:TP][up] = [f'PCA-{c+1}' for c in np.searchsorted(cuts, thp) % len(cuts)]
clab[:TP][svp] = [f'7d-{c+1}' for c in lp0]
clab[TP:][un] = [f'PCA-{c+1}' for c in np.searchsorted(cuts, thn) % len(cuts)]
clab[TP:][svn] = [f'7d-{c+1}' for c in ln0]
y = np.r_[np.ones(TP), np.zeros(TN)]; pid = np.r_[pidp, pidn]
free7 = np.r_[free7_p, free7_n]
cl_res = {}
for nm, m in [('ALL tests', np.ones(TP + TN, bool)), ('free7', free7)]:
    d = pd.DataFrame(dict(y=y[m], g=pid[m])); ok = d.groupby('g').y.nunique() == 2
    k = d.g.map(ok).values
    D = pd.get_dummies(pd.Series(clab[m][k]), drop_first=True).astype(float); D = D.loc[:, D.sum() >= 10]
    r = ConditionalLogit(y[m][k], D.values, groups=pid[m][k]).fit(disp=0)
    print(f'  {nm}: n={int(k.sum())} patients={len(set(pid[m][k]))} '
          f'-> {int((r.pvalues<0.05).sum())}/{D.shape[1]} contrasts significant')
    rows = []
    for n_, b_, p_ in zip(D.columns, r.params, r.pvalues):
        print('      %-8s OR=%.2f p=%.2e %s' % (n_, np.exp(b_), p_, '*' if p_ < 0.05 else ''))
        rows.append(dict(cluster=n_, OR=float(np.exp(b_)), p=float(p_)))
    cl_res[nm] = dict(n=int(k.sum()), patients=len(set(pid[m][k])),
                      n_sig=int((r.pvalues < 0.05).sum()), n_tested=int(D.shape[1]), rows=rows)
res['within_patient_clusters'] = cl_res

json.dump(res, open(OUT + r'\gradient_bootstrap.json', 'w'), indent=2)
print('\nsaved gradient_bootstrap.json')
