# -*- coding: utf-8 -*-
"""Council H1+H4: does the signal survive with STRICTLY PRE-TEST features
   (no day >= test), and does dose add over a prior-urine-history baseline?"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm
AN=_os.path.join(ROOT, r'analysis')
df=pd.read_parquet(os.path.join(AN,'feature_table.parquet'))
y=df.pos.values; g=df.pid.values
def cv_auc(cols):
    X=np.nan_to_num(df[cols].values); a=[]
    for tr,te in GroupKFold(5).split(X,y,g):
        m=HistGradientBoostingClassifier(random_state=0).fit(X[tr],y[tr]); a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return np.mean(a),np.std(a)
def or_sd(col):
    x=df[col].values; z=(x-np.nanmean(x))/np.nanstd(x)
    r=sm.Logit(y,sm.add_constant(np.nan_to_num(z))).fit(disp=0,cov_type='cluster',cov_kwds={'groups':g})
    return np.exp(r.params[1]),r.pvalues[1]

pre_dose=['nd-28','nd-14','nd-7','nd-3']          # strictly before test day
post_dose=['nd3','nd7','nd14','nd28']
pre_all=pre_dose+['pmn','pmx','att']              # pre-test dose+slope+attendance
full=['nd-28','nd-14','nd-7','nd-3','nd0','nd3','nd7','nd14','nd28','pmn','pmx','amn','amx','att']
history=['n_prior','prior_posrate','last_res','days_since']

print('=== H1: continuous escalation — POST-test (leaky) vs PRE-test (honest) ===')
for name,c in [('post-test max slope (amx) [PAPER, leaky]','amx'),('pre-test max slope (pmx) [honest]','pmx')]:
    o,p=or_sd(c); print(f'  {name:44s}: OR/SD={o:.2f}  p={p:.1e}')

print('\n=== H1: prediction AUC — full (leaky) vs strictly pre-test ===')
for name,c in [('full ±28 incl. post-test [PAPER]',full),
               ('PRE-test only (dose+slope+attendance)',pre_all),
               ('attendance only',['att'])]:
    m,s=cv_auc(c); print(f'  {name:42s}: AUC={m:.3f} ± {s:.3f}')

print('\n=== H4: does PRE-test dose add over a prior-history + attendance baseline? ===')
base=history+['att']
for name,c in [('history + attendance (baseline)',base),
               ('  + PRE-test dose/slope',base+pre_dose+['pmn','pmx'])]:
    m,s=cv_auc(c); print(f'  {name:38s}: AUC={m:.3f} ± {s:.3f}')
mb,_=cv_auc(base); mf,_=cv_auc(base+pre_dose+['pmn','pmx'])
print(f'  >>> PRE-test dose increment over history+attendance: {mf-mb:+.3f}')
