# -*- coding: utf-8 -*-
"""User's idea: a previously-stable (negative) patient whose dosing pattern starts
to CHANGE (deviates from their own baseline) -> transition to positive?
Restrict to tests on a negative streak; test whether deviation-from-own-baseline
predicts the streak breaking to positive. (strictly prior info, no leakage)"""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm
AN=_os.path.join(ROOT, r'analysis')
df=pd.read_parquet(os.path.join(AN,'rich_features.parquet')).reset_index(drop=True)  # sorted pid,date
g=df.groupby('pid',sort=False)
# deviation of key pattern features from the patient's OWN prior baseline
change_cols=['sl7','sl14','cc_std','gap_mean','recent_ratio','cc_mean','miss_frac','att7']
for c in change_cols:
    pm=g[c].apply(lambda s:s.shift(1).expanding().mean()).reset_index(level=0,drop=True)
    ps=g[c].apply(lambda s:s.shift(1).expanding().std()).reset_index(level=0,drop=True)
    df['dev_'+c]=(df[c]-pm)                         # raw deviation
    df['z_'+c]=(df[c]-pm)/(ps+1e-6)                 # standardized deviation (how unusual for this patient)
df=df.fillna(0)
# a single "how much has this patient's pattern changed?" score
df['change_score']=df[['z_sl7','z_cc_std','z_gap_mean','z_recent_ratio','z_cc_mean']].abs().mean(axis=1)

def cv(sub,cols):
    if sub.pos.nunique()<2 or len(sub)<150: return np.nan,len(sub)
    X=np.nan_to_num(sub[cols].values); y=sub.pos.values; gg=sub.pid.values; a=[]
    for tr,te in GroupKFold(5).split(X,y,gg):
        if len(np.unique(y[te]))<2: continue
        m=HistGradientBoostingClassifier(random_state=0).fit(X[tr],y[tr]); a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return (np.mean(a) if a else np.nan), len(sub)

dev_feats=['dev_'+c for c in change_cols]+['z_'+c for c in change_cols]+['change_score']
for label,sub in [('previously stable: >=3 prior negatives, 0 prior pos',df[(df.neg_streak>=3)&(df.prior_posrate==0)]),
                  ('>=5 prior negatives, 0 prior pos',df[(df.neg_streak>=5)&(df.prior_posrate==0)]),
                  ('all with >=3 prior tests',df[df.n_prior>=3])]:
    posr=sub.pos.mean()*100
    a_dev,n=cv(sub,dev_feats)
    a_abs,_=cv(sub,['sl7','cc_std','gap_mean','recent_ratio','cc_mean','att7'])
    print(f'{label:44s} n={n:5d} pos={posr:4.1f}% | deviation-AUC={a_dev:.3f}  absolute-AUC={a_abs:.3f}')

# OR of the single change_score among previously-stable patients
st=df[(df.neg_streak>=3)&(df.prior_posrate==0)].copy()
z=(st.change_score-st.change_score.mean())/(st.change_score.std()+1e-9)
r=sm.Logit(st.pos.values,sm.add_constant(np.nan_to_num(z))).fit(disp=0,cov_type='cluster',cov_kwds={'groups':st.pid.values})
print(f'\nAmong previously-stable patients: "pattern change score" -> turning positive:')
print(f'   OR = {np.exp(r.params[1]):.2f} per SD  (p={r.pvalues[1]:.1e}),  n={len(st)}, positives={int(st.pos.sum())}')
