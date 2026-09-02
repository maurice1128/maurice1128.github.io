# -*- coding: utf-8 -*-
"""Temporal validation: derive on EARLY tests, test on LATE tests.
Rebuilds morphine tests WITH date from raw, checks the core associations
(consumed-dose escalation -> positive; attendance -> negative) replicate out-of-time."""
import os as _os
ROOT = _os.environ.get('MMT_DATA_ROOT', '')  # local folder holding raw data/, code/, analysis/
if not ROOT: raise SystemExit('Set MMT_DATA_ROOT before running; patient data is not distributed.')

import numpy as np, pandas as pd, warnings, openpyxl, os; warnings.filterwarnings('ignore')
import statsmodels.api as sm
RAW=_os.path.join(ROOT, r'raw data'); AN=_os.path.join(ROOT, r'analysis')
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
    if r[2]==1 and r[3] in (0,1):
        dd=roc2d(r[1])
        if dd is not None:ur.append((int(r[0]),dd,int(r[3])))
wb.close()
mor=pd.DataFrame(ur,columns=['pid','date','pos']).drop_duplicates(['pid','date']).sort_values(['pid','date']).reset_index(drop=True)
dose=pd.read_parquet(os.path.join(AN,'dose_cache.parquet'))
dose_by={p:g.set_index('date')['dose_cc'].sort_index() for p,g in dose.groupby('pid')}  # consumed dose
first_dose={p:g.index.min() for p,g in dose_by.items()}
mor_by={p:g[['date','pos']].values for p,g in mor.groupby('pid')}
rows=[]
for t in mor.itertuples(index=False):
    s=dose_by.get(t.pid)
    if s is None:continue
    ref=s[s.index==t.date-pd.Timedelta(days=7)]
    if len(ref)==0 or ref.iloc[0]==0:continue
    refv=float(ref.iloc[0])
    def slope(lo,hi):
        sl=[]
        for k in range(lo,hi-1):
            pts=[(o,s[s.index==t.date+pd.Timedelta(days=o)]) for o in (k,k+1,k+2)]
            pts=[(o,float(x.iloc[0])/refv) for o,x in pts if len(x)]
            if len(pts)>=2:sl.append(np.polyfit([p[0] for p in pts],[p[1] for p in pts],1)[0])
        return max(sl) if sl else np.nan
    esc=slope(-7,8)  # peri-test max escalation slope (consumed)
    att=len(s[(s.index>=t.date-pd.Timedelta(days=7))&(s.index<t.date)])/7.0
    hist=[(d,p) for d,p in mor_by[t.pid] if d<t.date]; ppr=np.mean([p for _,p in hist]) if hist else 0.5
    rows.append((t.pid,t.date,t.pos,esc,att,ppr))
df=pd.DataFrame(rows,columns=['pid','date','pos','esc','att','ppr']).dropna()
cut=df.date.quantile(0.5)
early=df[df.date<=cut]; late=df[df.date>cut]
print(f'total {len(df)}  early(<= {cut.date()}) {len(early)}  late {len(late)}')
def assoc(d,col):
    """returns (OR per SD, OR per 0.1 of the raw variable, p). The per-0.1 scale is
    the one used for attendance throughout the manuscript (0-1 proportion)."""
    x=d[col].values; sd=x.std()+1e-9; z=(x-x.mean())/sd
    r=sm.Logit(d.pos.values,sm.add_constant(z)).fit(disp=0,cov_type='cluster',cov_kwds={'groups':d.pid.values})
    b=r.params[1]
    return np.exp(b),np.exp(b*0.1/sd),r.pvalues[1]
print('\n=== TEMPORAL validation (each period fit independently) ===')
for col,name in [('esc','consumed-dose escalation'),('att','attendance'),('ppr','prior positive rate')]:
    oe,oe10,pe=assoc(early,col); ol,ol10,pl=assoc(late,col)
    print(f'  {name:26s}: EARLY OR/SD={oe:.2f} (p={pe:.1e})  |  LATE OR/SD={ol:.2f} (p={pl:.1e})')
    if col=='att':
        print(f'  {"":26s}  per 0.1 increment: EARLY OR={oe10:.2f}  |  LATE OR={ol10:.2f}')
        print(f'  {"":26s}  (attendance SD: early {early[col].std():.3f}, late {late[col].std():.3f})')
