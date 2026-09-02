# -*- coding: utf-8 -*-
"""Two analytic figures for the sensitivity analyses (manuscript Figures 6 and 7).

 fig_robustness.png  (Figure 6): escalation & attendance OR (95% CI) across
     pooled / within-patient / vs-confirmed-true-negative analyses.  Both are
     reported PER SD so the three estimates are on one scale.
 fig_truenegative.png (Figure 7): per-cluster P/N against (a) all negatives,
     (b) confirmed true negatives with ALL positives (the comparison originally
     run), and (c) the LIKE-FOR-LIKE comparison in which positives are also
     restricted to the supervised patients.  (c) removes the population mismatch
     in (b) and is the honest read of this sensitivity analysis.

Requires supp_table_S1.csv (run 37_supp_sensitivity.py first).
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import h5py, numpy as np, pandas as pd, warnings, openpyxl, os; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.discrete.conditional_models import ConditionalLogit
OUT = _os.path.join(ROOT, r'analysis')

wb = openpyxl.load_workbook(_os.path.join(ROOT, r'raw data\陪同驗尿的名單.xlsx'), read_only=True, data_only=True)
ws = wb.active; it = ws.iter_rows(values_only=True); next(it); sup = set()
for r in it:
    if r[1] is not None:
        try: sup.add(int(r[1]))
        except Exception: pass
wb.close()
f = h5py.File(_os.path.join(ROOT, r'code\including_False_N_splitdata_testingvalidating\aim2.mat'), 'r')
cells = lambda n: [np.array(f[r]) for r in np.array(f[n]).ravel()]
m2 = lambda a: (a.T if a.shape[0] == 57 else a); v = lambda a: np.array(a).ravel()
afn = cells('All_fill_norm'); pos_pd, neg_pd = m2(afn[0]), m2(afn[2])
hdr = cells('All_fill_header'); pidp = v(hdr[0]).astype(int); pidn = v(hdr[2]).astype(int)
att = np.r_[v(cells('freq_All')[0]), v(cells('freq_All')[2])]
xa = cells('slope_burst_max_7da')
pos_mx = v(xa[0]); neg_mx = v(xa[2])
TP, TN = 3401, 6499; y = np.r_[np.ones(TP), np.zeros(TN)]; pid = np.r_[pidp, pidn]
z = lambda x: (x - np.nanmean(x)) / (np.nanstd(x) + 1e-9)
esc = z(np.r_[pos_mx, neg_mx]); atz = z(att)
sup_p = np.isin(pidp, list(sup)); sup_n = np.isin(pidn, list(sup))
keep_pub = np.r_[np.ones(TP, bool), sup_n]     # all positives vs supervised negatives
keep_lfl = np.r_[sup_p, sup_n]                 # like-for-like

def logit_or(col, mask=None):
    if mask is None: mask = np.ones(len(y), bool)
    r = sm.Logit(y[mask], sm.add_constant(np.nan_to_num(col[mask]))).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pid[mask]})
    b, se = r.params[1], r.bse[1]; return np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)
def cond_or(col):
    r = ConditionalLogit(y, np.nan_to_num(col).reshape(-1, 1), groups=pid).fit(disp=0)
    b, se = r.params[0], r.bse[0]; return np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)

# ---------------- Figure 6: robustness ----------------
analyses = ['Pooled\n(all data)', 'Within-patient\n(fixed effects)',
            'vs confirmed true negatives\n(all positives)', 'vs confirmed true negatives\n(like-for-like)']
esc_res = [logit_or(esc), cond_or(esc), logit_or(esc, keep_pub), logit_or(esc, keep_lfl)]
att_res = [logit_or(atz), cond_or(atz), logit_or(atz, keep_pub), logit_or(atz, keep_lfl)]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.5, 5))
for ax, res, title, col in [(a1, esc_res, 'Consumed-dose post-test escalation', '#c0392b'),
                            (a2, att_res, 'Pre-test attendance (protective)', '#2471a3')]:
    yy = np.arange(len(res))[::-1]
    for i, (o, lo, hi) in zip(yy, res):
        ax.plot([lo, hi], [i, i], color=col, lw=3); ax.plot(o, i, 'o', color=col, ms=9)
        ax.text(hi * 1.03, i, f'OR {o:.2f}', va='center', fontsize=9)
    ax.axvline(1, ls='--', color='k', lw=.8); ax.set_yticks(yy); ax.set_yticklabels(analyses, fontsize=8)
    ax.set_xscale('log'); ax.set_xlabel('Odds ratio per SD (95% CI)'); ax.set_title(title, fontsize=11)
    ax.set_xlim(0.35, 2.6)
fig.suptitle('Direction of the escalation and attendance associations across sensitivity analyses\n'
             '(all estimates per SD, so the panels are directly comparable)', fontsize=12, y=1.04)
plt.tight_layout(); fig.savefig(OUT + r'\fig_robustness.png', dpi=140, bbox_inches='tight'); plt.close()

# ---------------- Figure 7: true-negative sensitivity ----------------
S1 = os.path.join(OUT, 'supp_table_S1.csv')
if not os.path.exists(S1):
    raise SystemExit('run 37_supp_sensitivity.py first (supp_table_S1.csv missing)')
t = pd.read_csv(S1)
t = t.sort_values('cluster')
clusters = t.cluster.tolist()
fig, ax = plt.subplots(figsize=(12, 4.8)); x = np.arange(len(clusters)); w = 0.27
ax.bar(x - w, t.PN, w, label='vs all negatives (primary)', color='#95a5a6')
ax.bar(x, t.PN_tn_pub, w, label='vs confirmed true negatives, all positives', color='#e67e22')
ax.bar(x + w, t.PN_tn_lfl, w, label='vs confirmed true negatives, like-for-like positives', color='#8e44ad')
ax.axhline(1, ls='--', color='k', lw=.8)
ax.axhline(1.2, ls=':', color='#c0392b', lw=.8); ax.axhline(0.83, ls=':', color='#2471a3', lw=.8)
ax.set_xticks(x); ax.set_xticklabels(clusters)
ax.set_ylabel('P/N occurrence ratio')
ax.set_title('Cluster associations against confirmed (supervised) true negatives.\n'
             'Restricting positives to the same supervised patients removes the population mismatch;\n'
             'the pattern is mixed rather than uniformly strengthened. Dotted lines: the 1.2 / 0.83 labelling thresholds.',
             fontsize=10)
ax.legend(fontsize=8)
plt.tight_layout(); fig.savefig(OUT + r'\fig_truenegative.png', dpi=140, bbox_inches='tight'); plt.close()
print('saved fig_robustness.png (Fig 6), fig_truenegative.png (Fig 7)')
print('escalation ORs/SD:', [round(o, 2) for o, _, _ in esc_res])
print('attendance ORs/SD:', [round(o, 2) for o, _, _ in att_res])
