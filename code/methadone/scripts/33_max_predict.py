# -*- coding: utf-8 -*-
"""PUSH FOR 90%: maximal prior-history features (recency, streaks, windowed
positivity, EWMA) + rich dose + attendance. All strictly prior (no leakage).
Try to exploit relapse autocorrelation as hard as possible."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, openpyxl, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
RAW=_os.path.join(ROOT, r'raw data'); AN=_os.path.join(ROOT, r'analysis')
FP=os.path.join(AN,'max_features.parquet')
if os.path.exists(FP):
    df=pd.read_parquet(FP); print('loaded cached max features')
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
            dd=roc2d(r[1])
            if dd is not None: ur.append((int(r[0]),dd,int(r[2]),int(r[3])))
    wb.close(); ur=pd.DataFrame(ur,columns=['pid','date','drug','pos'])
    mor=ur[ur.drug==1].drop_duplicates(['pid','date']).sort_values(['pid','date']).reset_index(drop=True)
    amp_by={p:np.sort(g.date.values) for p,g in ur[(ur.drug==0)&(ur.pos==1)].groupby('pid')}
    dose=pd.read_parquet(os.path.join(AN,'dose_cache.parquet'))
    dby={p:g.set_index('date').sort_index() for p,g in dose.groupby('pid')}
    first_dose={p:g.index.min() for p,g in dby.items()}
    rows=[]
    for pid,grp in mor.groupby('pid'):
        recs=grp[['date','pos']].values
        for i in range(len(recs)):
            t_date,t_pos=recs[i]; prior=recs[:i]
            npr=len(prior)
            def winrate(days):
                m=[p for d,p in prior if (t_date-d).days<=days]
                return (np.mean(m) if m else 0.0, len(m))
            r30=winrate(30);r90=winrate(90);r180=winrate(180)
            last_res=prior[-1][1] if npr else 0
            last3=np.mean([p for _,p in prior[-3:]]) if npr else 0.0
            last5=np.mean([p for _,p in prior[-5:]]) if npr else 0.0
            ppr=np.mean([p for _,p in prior]) if npr else 0.0
            # EWMA
            ew=0.0;a=0.45
            for _,p in prior: ew=a*p+(1-a)*ew
            dsl=(t_date-prior[-1][0]).days if npr else 999
            dslp=next(((t_date-d).days for d,p in reversed(prior) if p==1),999)
            neg_streak=0
            for _,p in reversed(prior):
                if p==0:neg_streak+=1
                else:break
            pos_streak=0
            for _,p in reversed(prior):
                if p==1:pos_streak+=1
                else:break
            trend=r30[0]-ppr
            # rich dose (pre-test 28d)
            s=dby.get(pid); dose_f={}
            if s is not None:
                w=s[(s.index>=t_date-pd.Timedelta(days=28))&(s.index<t_date)]
                if len(w)>=4:
                    cc=w['dose_cc'].values.astype(float);mg=w['dose_mg'].values.astype(float)
                    offs=(w.index-t_date).days.values.astype(float);ncc=cc/(np.median(cc)+1e-6)
                    sl=lambda dd,vv:(np.polyfit(dd,vv,1)[0] if len(vv)>=2 else 0.0)
                    present=set(w.index.date);miss=sum(1 for k in range(1,29) if (t_date-pd.Timedelta(days=k)).date() not in present)/28.0
                    dose_f=dict(cc_mean=cc.mean(),cc_std=cc.std(),cc_last=cc[-1],mg_mean=mg.mean(),
                        sl7=sl(offs[offs>=-7],ncc[offs>=-7]),sl28=sl(offs,ncc),miss_frac=miss,
                        att7=len(w[w.index>=t_date-pd.Timedelta(days=7)])/7.0,att28=len(w)/28.0)
            ad=amp_by.get(pid,np.array([],dtype='datetime64[ns]'))
            amp180=int(np.sum((np.datetime64(t_date)-ad).astype('timedelta64[D]').astype(int)<=180) if len(ad) else 0)
            rows.append(dict(pid=pid,pos=t_pos,n_prior=npr,last_res=last_res,last3=last3,last5=last5,
                prior_posrate=ppr,pos30=r30[0],pos90=r90[0],pos180=r180[0],n90=r90[1],ewma=ew,
                days_since=dsl,days_since_pos=dslp,neg_streak=neg_streak,pos_streak=pos_streak,trend=trend,
                amp180=amp180,tit=(t_date-first_dose.get(pid,t_date)).days,**dose_f))
    df=pd.DataFrame(rows).fillna(0);df.to_parquet(FP)
print(f'tests {len(df)} patients {df.pid.nunique()} feats {df.shape[1]-2}')
y=df.pos.values;g=df.pid.values
hist=['n_prior','last_res','last3','last5','prior_posrate','pos30','pos90','pos180','ewma','days_since','days_since_pos','neg_streak','pos_streak','trend']
dose=[c for c in df.columns if c.startswith(('cc','mg','sl','miss','att'))]
allf=[c for c in df.columns if c not in ('pid','pos')]
def auc(cols,model='hgb'):
    X=np.nan_to_num(df[cols].values);a=[]
    for tr,te in GroupKFold(5).split(X,y,g):
        m=HistGradientBoostingClassifier(random_state=0,max_iter=600,learning_rate=0.05,l2_regularization=1.0).fit(X[tr],y[tr])
        a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return np.mean(a)
print('\n=== PUSH FOR 90 ===')
print(f'  RICH history only        : {auc(hist):.3f}')
print(f'  RICH history + dose+att  : {auc(hist+dose):.3f}')
print(f'  EVERYTHING (tuned)       : {auc(allf):.3f}')
