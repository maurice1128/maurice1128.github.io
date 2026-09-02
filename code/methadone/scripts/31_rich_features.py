# -*- coding: utf-8 -*-
"""Pull HARD: build a rich, doctor-mimicking feature set (all strictly PRE-test,
no leakage) and see how high AUC goes. Missed doses, prescribed-vs-consumed gap,
multi-timescale slopes, volatility, attendance trends, urine history, tenure."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, openpyxl, os; warnings.filterwarnings('ignore')
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
RAW=_os.path.join(ROOT, r'raw data'); AN=_os.path.join(ROOT, r'analysis')
FP=os.path.join(AN,'rich_features.parquet')
if os.path.exists(FP):
    df=pd.read_parquet(FP); print('loaded cached rich features')
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
    dby={p:g.set_index('date').sort_index() for p,g in dose.groupby('pid')}   # dose_mg=presc, dose_cc=consumed
    first_dose={p:g.index.min() for p,g in dby.items()}
    mor_by={p:g[['date','pos']].values for p,g in mor.groupby('pid')}
    def sl(days,vals):
        return np.polyfit(days,vals,1)[0] if len(vals)>=2 else 0.0
    rows=[]
    for t in mor.itertuples(index=False):
        s=dby.get(t.pid)
        if s is None: continue
        w=s[(s.index>=t.date-pd.Timedelta(days=28))&(s.index<t.date)]   # strictly pre-test 28d
        if len(w)<5: continue
        cc=w['dose_cc'].values.astype(float); mg=w['dose_mg'].values.astype(float)
        offs=(w.index-t.date).days.values.astype(float)
        ref=cc[-min(len(cc),3):].mean()  # recent consumed as ref (avoid /0)
        ncc=cc/(np.median(cc)+1e-6); nmg=mg/(np.median(mg)+1e-6)
        present=set((w.index).date); alld=[(t.date-pd.Timedelta(days=k)).date() for k in range(1,29)]
        miss=sum(1 for dd in alld if dd not in present)/28.0
        # longest consecutive missing gap
        flags=[0 if dd in present else 1 for dd in alld[::-1]]
        longest=cur=0
        for fgt in flags:
            cur=cur+1 if fgt else 0; longest=max(longest,cur)
        att7=len(w[w.index>=t.date-pd.Timedelta(days=7)])/7.0
        att14=len(w[w.index>=t.date-pd.Timedelta(days=14)])/14.0
        att28=len(w)/28.0
        hist=[(d,p) for d,p in mor_by[t.pid] if d<t.date]; np_=len(hist)
        ppr=np.mean([p for _,p in hist]) if hist else 0.0
        pos90=sum(1 for d,p in hist if p and (t.date-d).days<=90)
        neg_streak=0
        for d,p in reversed(hist):
            if p==0: neg_streak+=1
            else: break
        days_since=(t.date-hist[-1][0]).days if hist else 999
        ad=amp_by.get(t.pid,np.array([],dtype='datetime64[ns]'))
        amp180=int(np.sum((np.datetime64(t.date)-ad).astype('timedelta64[D]').astype(int).clip(min=-1)<=180) if len(ad) else 0)
        tit=(t.date-first_dose.get(t.pid,t.date)).days
        rows.append(dict(pid=t.pid,pos=t.pos,
            cc_mean=cc.mean(),cc_std=cc.std(),cc_last=cc[-1],cc_min=cc.min(),cc_max=cc.max(),
            mg_mean=mg.mean(),mg_std=mg.std(),mg_last=mg[-1],
            gap_mean=np.mean(np.abs(nmg-ncc)),gap_last=abs(nmg[-1]-ncc[-1]),
            adher=cc.mean()/(mg.mean()/10+1e-6),
            sl7=sl(offs[offs>=-7],ncc[offs>=-7]),sl14=sl(offs[offs>=-14],ncc[offs>=-14]),sl28=sl(offs,ncc),
            recent_ratio=(cc[offs>=-7].mean()/(cc[offs<-14].mean()+1e-6)) if (offs<-14).any() else 1.0,
            n_presc_changes=int((np.diff(mg)!=0).sum()),
            miss_frac=miss,longest_gap=longest,att7=att7,att14=att14,att28=att28,att_trend=att7-att28,
            n_prior=np_,prior_posrate=ppr,pos90=pos90,neg_streak=neg_streak,days_since=days_since,
            amp180=amp180,tit=tit))
    df=pd.DataFrame(rows).fillna(0); df.to_parquet(FP)
print(f'tests: {len(df)}  patients: {df.pid.nunique()}  features: {df.shape[1]-2}')
y=df.pos.values; g=df.pid.values
FEATS=[c for c in df.columns if c not in ('pid','pos')]
dose_feats=[c for c in FEATS if c.startswith(('cc','mg','gap','adher','sl','recent','n_presc','miss','longest'))]
hist_feats=['n_prior','prior_posrate','pos90','neg_streak','days_since']
att_feats=['att7','att14','att28','att_trend']
def auc(cols):
    X=np.nan_to_num(df[cols].values); a=[]
    for tr,te in GroupKFold(5).split(X,y,g):
        m=HistGradientBoostingClassifier(random_state=0,max_iter=300).fit(X[tr],y[tr]); a.append(roc_auc_score(y[te],m.predict_proba(X[te])[:,1]))
    return np.mean(a)
print('\n=== PULL HARD: how high can AUC go? ===')
print(f'  attendance only           : {auc(att_feats):.3f}')
print(f'  RICH dose only            : {auc(dose_feats):.3f}   (was ~0.62 with simple dose)')
print(f'  history + attendance      : {auc(hist_feats+att_feats):.3f}')
print(f'  history + att + RICH dose : {auc(hist_feats+att_feats+dose_feats):.3f}')
print(f'  EVERYTHING                : {auc(FEATS):.3f}')
print(f'  >>> RICH-dose increment over history+att: {auc(hist_feats+att_feats+dose_feats)-auc(hist_feats+att_feats):+.3f}')
