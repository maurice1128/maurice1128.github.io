# -*- coding: utf-8 -*-
"""Step 39 - is the dose-change cluster-outcome pattern an artefact of K?

K = 6 was an investigator choice (§2.4), so we refit the dose-change branch at
K = 4, 5, 6, 7, 8 and report, for each resolution: how many clusters are
significant (patient-clustered logistic, FDR), the range of P/N, and the rank
correlation between a cluster's mean post-test escalation slope and its P/N.
If the escalation-is-higher-risk ordering holds at every K, the finding is not
an artefact of the chosen resolution.
Writes k_robustness.json
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, json, warnings; warnings.filterwarnings('ignore')
from scipy.special import i0
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

OUT = _os.path.join(ROOT, r'analysis')
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm'); pos_pd, neg_pd = m2(afn[0]), m2(afn[2])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
sa, sb, xa, xb = cells('slope_burst_min_7da'), cells('slope_burst_min_7db'), cells('slope_burst_max_7da'), cells('slope_burst_max_7db')
pos = dict(mn_a=v(sa[0]), mn_b=v(sb[0]), mx_a=v(xa[0]), mx_b=v(xb[0]))
neg = dict(mn_a=v(sa[2]), mn_b=v(sb[2]), mx_a=v(xa[2]), mx_b=v(xb[2]))
TP, TN = 3401, 6499
svp = ~(~(np.abs(np.diff(pos_pd[:, 21:36], axis=1)).sum(1) != 0))
svn = ~(~(np.abs(np.diff(neg_pd[:, 21:36], axis=1)).sum(1) != 0))

def vmpdf(t, m, k): return np.exp(k * np.cos(t - m)) / (2 * np.pi * i0(k))
def vm_mle(t, w):
    C = (w * np.cos(t)).sum(); S = (w * np.sin(t)).sum(); s = w.sum() + 1e-12
    R = min(np.sqrt(C * C + S * S) / s, 0.999); return np.arctan2(S, C), R * (2 - R * R) / (1 - R * R)
def fit(t1, t2, K, it=120):
    lab = KMeans(K, n_init=5, random_state=0).fit_predict(np.column_stack([np.cos(t1), np.sin(t1), np.cos(t2), np.sin(t2)]))
    P = np.zeros((K, len(t1))); P[lab, np.arange(len(t1))] = 1
    m1 = np.zeros(K); k1 = np.ones(K); m2_ = np.zeros(K); k2 = np.ones(K); pi = np.ones(K) / K
    for _ in range(it):
        for k in range(K):
            w = P[k]; m1[k], k1[k] = vm_mle(t1, w); m2_[k], k2[k] = vm_mle(t2, w); pi[k] = w.mean() + 1e-9
        P = np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, m2_[k], k2[k]) for k in range(K)]); P /= P.sum(0) + 1e-300
    return (m1, k1, m2_, k2, pi)
def asg(t1, t2, pr):
    m1, k1, m2_, k2, pi = pr
    return np.array([pi[k] * vmpdf(t1, m1[k], k1[k]) * vmpdf(t2, m2_[k], k2[k]) for k in range(len(pi))]).argmax(0)

t1p = np.arctan2(pos['mn_b'][svp], pos['mn_a'][svp]); t2p = np.arctan2(pos['mx_b'][svp], pos['mx_a'][svp])
t1n = np.arctan2(neg['mn_b'][svn], neg['mn_a'][svn]); t2n = np.arctan2(neg['mx_b'][svn], neg['mx_a'][svn])
escp = pos['mx_a'][svp]
pidp_s = pidp[svp]; pidn_s = pidn[svn]

print('=== dose-change branch: cluster-outcome pattern across resolutions K ===')
print(f'{"K":>3} {"clusters":>8} {"sig(q<.05)":>11} {"P/N range":>14} {"n higher":>9} {"n lower":>8} {"Spearman(escalation, P/N)":>28}')
res = {}
for K in [4, 5, 6, 7, 8]:
    pr = fit(t1p, t2p, K)
    lp = asg(t1p, t2p, pr); ln = asg(t1n, t2n, pr)
    y = np.r_[np.ones(int(svp.sum())), np.zeros(int(svn.sum()))]
    lab = np.r_[lp, ln]; pid = np.r_[pidp_s, pidn_s]
    pns = []; ps = []; escs = []; keep = []
    for c in range(K):
        pN = int((lp == c).sum()); nN = int((ln == c).sum())
        if pN < 5 or nN < 5: continue
        pn = (pN / TP) / (nN / TN)
        inc = (lab == c).astype(float)
        r = sm.Logit(y, sm.add_constant(inc)).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid})
        pns.append(pn); ps.append(float(r.pvalues[1])); escs.append(float(escp[lp == c].mean())); keep.append(c)
    q = multipletests(ps, method='fdr_bh')[1]
    nsig = int((q < 0.05).sum())
    nhi = int(sum(1 for pn, qq in zip(pns, q) if pn > 1.2 and qq < 0.05))
    nlo = int(sum(1 for pn, qq in zip(pns, q) if pn < 0.83 and qq < 0.05))
    rho, pv = spearmanr(escs, pns)
    print(f'{K:>3} {len(pns):>8} {nsig:>11} {min(pns):>6.2f}-{max(pns):<7.2f} {nhi:>9} {nlo:>8} '
          f'{rho:>+15.2f} (p={pv:.3g})')
    res[K] = dict(n_clusters=len(pns), n_sig=nsig, pn_min=float(min(pns)), pn_max=float(max(pns)),
                  n_higher=nhi, n_lower=nlo, spearman_rho=float(rho), spearman_p=float(pv),
                  PN=[float(x) for x in pns], q=[float(x) for x in q])
json.dump(res, open(OUT + r'\k_robustness.json', 'w'), indent=2)
print('\nA positive Spearman at every K means: the more a cluster escalates the consumed dose')
print('after the test, the higher its positive/negative occurrence ratio -- independently of K.')
print('saved k_robustness.json')
