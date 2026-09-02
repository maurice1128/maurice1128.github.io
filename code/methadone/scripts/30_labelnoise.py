# -*- coding: utf-8 -*-
"""Is the low AUC a label-noise ceiling (false-negative contamination)?
Compare prediction AUC on SUPERVISED patients (trustworthy negatives) vs
UNSUPERVISED patients (negatives may be false). If supervised > unsupervised,
the ceiling is label noise, not the model."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, os, openpyxl; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
AN=_os.path.join(ROOT, r'analysis')
wb=openpyxl.load_workbook(_os.path.join(ROOT, r'raw data\陪同驗尿的名單.xlsx'),read_only=True,data_only=True)
ws=wb.active; it=ws.iter_rows(values_only=True); next(it); sup=set()
for r in it:
    if r[1] is not None:
        try: sup.add(int(r[1]))
        except: pass
wb.close()
df=pd.read_parquet(os.path.join(AN,'feature_table.parquet')).reset_index(drop=True)
df['supervised']=df.pid.isin(sup)
# personalised dose features (prior-only)
g=df.groupby('pid',sort=False)
for col in ['pmx','att','absd']:
    pm=g[col].apply(lambda s:s.shift(1).expanding().mean()).reset_index(level=0,drop=True)
    df['prior_'+col]=pm; df['dev_'+col]=df[col]-pm
df=df.fillna(df.median(numeric_only=True))
FE=['n_prior','prior_posrate','last_res','days_since','att','dev_pmx','prior_pmx','dev_att']
def auc(sub):
    if sub.pos.nunique()<2: return np.nan,0,0
    X=np.nan_to_num(sub[FE].values); y=sub.pos.values; grp=sub.pid.values; a=[]
    for tr,te in GroupKFold(5).split(X,y,grp):
        if len(np.unique(y[te]))<2: continue
        m=HistGradientBoostingClassifier(random_state=0).fit(X[tr],y[tr]); a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return (np.mean(a) if a else np.nan), len(sub), int(sub.pos.sum())

sup_df=df[df.supervised]; uns_df=df[~df.supervised]
print('Full model = history + attendance + personalised dose')
for name,sub in [('SUPERVISED patients (clean negatives)',sup_df),
                 ('UNSUPERVISED patients (negatives may be false)',uns_df),
                 ('ALL patients',df)]:
    A,n,npos=auc(sub); print(f'  {name:46s}: AUC={A:.3f}  (n={n}, pos={npos}, {npos/n*100:.0f}%)')
print('\n(If SUPERVISED AUC clearly > UNSUPERVISED -> the low overall AUC is a label-noise')
print(' ceiling from false negatives, not a modelling failure.)')
