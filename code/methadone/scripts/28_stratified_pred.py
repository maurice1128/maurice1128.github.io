# -*- coding: utf-8 -*-
"""User's idea: prior urine history dominates prediction, but it is UNINFORMATIVE
for patients with no relapse history. In that subgroup, does the (pre-test) dose
trajectory predict a FIRST positive? Strictly pre-test features (no leakage)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
AN=_os.path.join(ROOT, r'analysis')
df=pd.read_parquet(os.path.join(AN,'feature_table.parquet'))
pre_dose=['nd-28','nd-14','nd-7','nd-3']            # strictly before test day
pre=['nd-28','nd-14','nd-7','nd-3','pmn','pmx']      # pre-test dose + pre slopes
att=['att']; hist=['n_prior','prior_posrate','last_res','days_since']

def cv(sub,cols):
    if sub.pos.nunique()<2 or len(sub)<150: return np.nan,0
    X=np.nan_to_num(sub[cols].values); y=sub.pos.values; g=sub.pid.values
    a=[]
    for tr,te in GroupKFold(5).split(X,y,g):
        if len(np.unique(y[te]))<2: continue
        m=HistGradientBoostingClassifier(random_state=0).fit(X[tr],y[tr])
        a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return (np.mean(a) if a else np.nan), len(sub)

# strata by prior relapse history
strata={
 'NO prior positive (clean history)': df[df.prior_posrate==0],
 'has some prior positives': df[(df.prior_posrate>0)&(df.prior_posrate<0.5)],
 'chronic (prior_posrate>=0.5)': df[df.prior_posrate>=0.5],
 'ALL patients': df,
}
print(f'{"stratum":36s} {"n":>6s} {"pos%":>6s} | {"att":>6s} {"dose":>6s} {"dose+att":>9s} {"hist+att":>9s}')
for name,sub in strata.items():
    posr=sub.pos.mean()*100
    a_att,_=cv(sub,att); a_dose,_=cv(sub,pre); a_da,n=cv(sub,pre+att); a_ha,_=cv(sub,hist+att)
    print(f'{name:36s} {len(sub):>6d} {posr:>5.1f}% | {a_att:>6.3f} {a_dose:>6.3f} {a_da:>9.3f} {a_ha:>9.3f}')
print('\n(Key: in "clean history", hist is uninformative -> does dose/dose+att beat att-alone?)')

# focused: in clean-history subgroup, dose increment over attendance
clean=df[df.prior_posrate==0]
a_att,_=cv(clean,att); a_da,_=cv(clean,pre+att)
print(f'\nCLEAN-history subgroup: attendance AUC={a_att:.3f}, dose+attendance AUC={a_da:.3f}, increment={a_da-a_att:+.3f}')
print(f'  (n={len(clean)}, {clean.pos.sum()} first-relapse positives, {clean.pid.nunique()} patients)')
