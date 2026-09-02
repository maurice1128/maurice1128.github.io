# -*- coding: utf-8 -*-
"""Does consumption fraction add predictive value over the manuscript's OWN baseline
(prior urine-test history + attendance, AUC ~0.83 in 33_max_predict.py)?

The cached feature table already holds cc_mean (consumed, cc) and mg_mean (prescribed, mg)
but never their ratio. With the concentration identified at 10 mg/cc the fraction is
frac = 10*cc_mean/mg_mean.
"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import pandas as pd, numpy as np, sys, warnings; warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

d = pd.read_parquet(_os.path.join(ROOT, r'analysis\max_features.parquet'))
d['frac'] = 10.0 * d['cc_mean'] / d['mg_mean'].replace(0, np.nan)
d['frac_last'] = 10.0 * d['cc_last'] / d['mg_mean'].replace(0, np.nan)
print('n=%d  病人=%d  陽性率=%.3f' % (len(d), d.pid.nunique(), d.pos.mean()))
print('frac: 中位=%.3f  p25=%.3f  p75=%.3f  >1 的筆數=%d'
      % (d.frac.median(), d.frac.quantile(.25), d.frac.quantile(.75), (d.frac > 1.001).sum()))

HIST = ['n_prior','last_res','last3','last5','prior_posrate','pos30','pos90','pos180',
        'n90','ewma','days_since','days_since_pos','neg_streak','pos_streak','trend',
        'amp180','tit']
ATT  = ['att7','att28','miss_frac']
DOSE = ['cc_mean','cc_std','cc_last','mg_mean','sl7','sl28']
y = d.pos.values; g = d.pid.values

def auc(cols, seed=0):
    X = d[cols].values; pr = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        m = HistGradientBoostingClassifier(max_iter=300, learning_rate=.06,
                                           random_state=seed).fit(X[tr], y[tr])
        pr[te] = m.predict_proba(X[te])[:, 1]
    return roc_auc_score(y, pr)

rows = [
 ('① 只有出席率',                       ATT),
 ('② 出席率 + 過去驗尿史（主稿基準）',        HIST + ATT),
 ('③ 基準 + 原有劑量特徵',                HIST + ATT + DOSE),
 ('④ 基準 + 服用比例',                   HIST + ATT + ['frac', 'frac_last']),
 ('⑤ 基準 + 原有劑量 + 服用比例',           HIST + ATT + DOSE + ['frac', 'frac_last']),
]
base = None
for nm, cols in rows:
    a = auc(cols)
    if nm.startswith('②'): base = a
    dd = '' if base is None or nm.startswith('②') else '   ΔAUC vs 基準 = %+.4f' % (a - base)
    print('  %-30s AUC = %.4f%s' % (nm, a, dd))
