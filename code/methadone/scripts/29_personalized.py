# -*- coding: utf-8 -*-
"""Doctor's intuition: predict from DEVIATION vs the patient's OWN baseline, not
absolute dose. (1) personalized prediction; (2) how many tests until a patient's
dose signature stabilises. All features use PRIOR tests only (no leakage)."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
AN=_os.path.join(ROOT, r'analysis')
df=pd.read_parquet(os.path.join(AN,'feature_table.parquet')).reset_index(drop=True)
# df is already sorted by (pid, date) from step 19
g=df.groupby('pid',sort=False)
# personalised features: deviation of this test's escalation/attendance from the
# patient's own PRIOR mean (shift(1) so only past tests are used)
for col in ['pmx','att','absd']:
    pm=g[col].apply(lambda s:s.shift(1).expanding().mean()).reset_index(level=0,drop=True)
    df['prior_'+col]=pm
    df['dev_'+col]=df[col]-pm
df=df.fillna(df.median(numeric_only=True))
y=df.pos.values; grp=df.pid.values
def auc(cols):
    X=np.nan_to_num(df[cols].values); a=[]
    for tr,te in GroupKFold(5).split(X,y,grp):
        m=HistGradientBoostingClassifier(random_state=0).fit(X[tr],y[tr]); a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return np.mean(a)
pop_dose=['pmx','att']                                   # population (absolute)
pers_dose=['dev_pmx','prior_pmx','dev_att','prior_att','dev_absd','prior_absd']  # personalised
hist=['n_prior','prior_posrate','last_res','days_since','att']
print('=== (1) Personalised vs population prediction ===')
print(f'  population absolute dose+att      : AUC={auc(pop_dose):.3f}')
print(f'  PERSONALISED (deviation-from-self): AUC={auc(pers_dose):.3f}')
print(f'  history + attendance (baseline)   : AUC={auc(hist):.3f}')
print(f'  history + attendance + PERSONALISED dose : AUC={auc(hist+pers_dose):.3f}')
print(f'  >>> personalised dose increment over history+att: {auc(hist+pers_dose)-auc(hist):+.3f}')

print('\n=== (2) How many tests until a patient\'s escalation signature stabilises? ===')
# for patients with >=8 tests, running mean of pmx; count tests until within 15% of final mean
ns=[]
for pid,s in g['pmx']:
    x=s.values
    if len(x)<8: continue
    final=np.mean(x);
    if abs(final)<1e-9: continue
    run=np.cumsum(x)/np.arange(1,len(x)+1)
    within=np.abs(run-final)<=0.15*abs(final)
    # first index from which it stays within band
    k=len(x)
    for i in range(len(x)):
        if within[i:].all(): k=i+1; break
    ns.append(k)
ns=np.array(ns)
print(f'  patients with >=8 tests: {len(ns)}')
print(f'  tests until signature stabilises (within 15% of final): median {np.median(ns):.0f}, IQR {np.percentile(ns,25):.0f}-{np.percentile(ns,75):.0f}, mean {ns.mean():.1f}')
for thr in [3,5,8,10]:
    print(f'    stabilised by {thr:2d} tests: {(ns<=thr).mean()*100:.0f}% of patients')
