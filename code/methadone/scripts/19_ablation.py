# -*- coding: utf-8 -*-
"""Step 19 - ablation: does the dose-trajectory signal add ON TOP of urine history?
Rebuilds the feature table (saves to parquet for reuse) and compares feature sets."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, openpyxl, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
RAW=_os.path.join(ROOT, r'raw data'); AN=_os.path.join(ROOT, r'analysis')
FP=os.path.join(AN,'feature_table.parquet')
offs=[-28,-14,-7,-3,0,3,7,14,28]

if os.path.exists(FP):
    df=pd.read_parquet(FP); print('loaded cached feature table')
else:
    def roc2d(v):
        try:v=int(v)
        except:return None
        y,m,d=v//10000,(v//100)%100,v%100
        if not(1<=m<=12 and 1<=d<=31):return None
        try:return pd.Timestamp(year=y+1911,month=m,day=d)
        except:return None
    wb=openpyxl.load_workbook(os.path.join(RAW,'2018-2022驗尿結果.xlsx'),read_only=True,data_only=True)
    ws=wb['驗尿結果'];it=ws.iter_rows(values_only=True);next(it);ur=[]
    for r in it:
        if r[2] in (0,1) and r[3] in (0,1):
            d=roc2d(r[1])
            if d is not None:ur.append((int(r[0]),d,int(r[2]),int(r[3])))
    wb.close();ur=pd.DataFrame(ur,columns=['pid','date','drug','pos'])
    mor=ur[ur.drug==1].drop_duplicates(['pid','date']).sort_values(['pid','date']).reset_index(drop=True)
    amp=ur[ur.drug==0]
    dose=pd.read_parquet(os.path.join(AN,'dose_cache.parquet'))
    dose_by={p:g.set_index('date')['dose_mg'].sort_index() for p,g in dose.groupby('pid')}
    first_dose={p:g.index.min() for p,g in dose_by.items()}
    amp_by={p:g['date'].values for p,g in amp[amp.pos==1].groupby('pid')}
    mor_by={p:g[['date','pos']].values for p,g in mor.groupby('pid')}
    rows=[]
    for t in mor.itertuples(index=False):
        s=dose_by.get(t.pid)
        if s is None:continue
        win=s[(s.index>=t.date-pd.Timedelta(days=28))&(s.index<=t.date+pd.Timedelta(days=28))]
        if len(win)<8:continue
        ref=s[s.index==t.date-pd.Timedelta(days=7)]
        if len(ref)==0 or ref.iloc[0]==0:continue
        refv=float(ref.iloc[0]);normvals=[]
        for o in offs:
            dd=t.date+pd.Timedelta(days=o);near=s[(s.index>=dd-pd.Timedelta(days=2))&(s.index<=dd+pd.Timedelta(days=2))]
            normvals.append(float(near.iloc[near.index.get_indexer([dd],method='nearest')[0]])/refv if len(near) else np.nan)
        def slopes(lo,hi):
            sl=[]
            for k in range(lo,hi-1):
                pts=[(o,s[s.index==t.date+pd.Timedelta(days=o)]) for o in (k,k+1,k+2)]
                pts=[(o,float(x.iloc[0])/refv) for o,x in pts if len(x)]
                if len(pts)>=2:sl.append(np.polyfit([p[0] for p in pts],[p[1] for p in pts],1)[0])
            return (min(sl),max(sl)) if sl else (0.0,0.0)
        pmn,pmx=slopes(-7,1);amn,amx=slopes(0,8)
        att=len(s[(s.index>=t.date-pd.Timedelta(days=7))&(s.index<t.date)])/7.0
        ad=amp_by.get(t.pid,np.empty(0,dtype='datetime64[ns]'))
        amp_co=int(np.any(np.abs((ad-np.datetime64(t.date)).astype('timedelta64[D]').astype(int))<=30)) if len(ad) else 0
        tit=(t.date-first_dose.get(t.pid,t.date)).days
        hist=mor_by[t.pid];prior=[(d,p) for d,p in hist if d<t.date]
        n_prior=len(prior);prior_posrate=(np.mean([p for _,p in prior]) if prior else 0.5)
        last_res=(prior[-1][1] if prior else 0);days_since=((t.date-prior[-1][0]).days if prior else 999)
        rows.append(dict(pid=t.pid,pos=t.pos,**{f'nd{o}':v for o,v in zip(offs,normvals)},pmn=pmn,pmx=pmx,amn=amn,amx=amx,
            att=att,absd=refv,amp_co=amp_co,tit=tit,n_prior=n_prior,prior_posrate=prior_posrate,last_res=last_res,days_since=days_since))
    df=pd.DataFrame(rows).fillna(1.0);df.to_parquet(FP)
print('tests:',len(df),' patients:',df.pid.nunique())

dosetraj=[f'nd{o}' for o in offs]+['pmn','pmx','amn','amx','att','absd']
history=['n_prior','prior_posrate','last_res','days_since']
context=['amp_co','tit']
y=df.pos.values;g=df.pid.values
def auc(cols):
    X=df[cols].values;a=[]
    for tr,te in GroupKFold(5).split(X,y,g):
        m=HistGradientBoostingClassifier(random_state=0).fit(X[tr],y[tr]);a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return np.mean(a)
print('\n=== ABLATION: does dose-trajectory add on top of urine history? ===')
sets=[('dose-trajectory ONLY (your signal)',dosetraj),
      ('urine history ONLY',history),
      ('history + context (amph+time), NO dose',history+context),
      ('history + context + dose-trajectory (ALL)',history+context+dosetraj)]
res={}
for name,cols in sets:
    res[name]=auc(cols);print(f'  {name:46s}: AUC = {res[name]:.3f}')
add=res['history + context + dose-trajectory (ALL)']-res['history + context (amph+time), NO dose']
print(f'\n>>> dose-trajectory adds ON TOP of history+context: {add:+.3f}')
