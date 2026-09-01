"""Identifiability: which muscle group is weak, from unilateral SCONE gait.
Leave-one-condition-out CV (each condition held out once; trained on the rest, all severities).
Reports given-impaired top-1 / top-3 (chance 0.20 / 0.60) + per-group.
"""
import numpy as np, glob, re, os, json
import pandas as pd
from scipy.interpolate import interp1d
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
MECHS = ['PF','DF','KE','KF','HF']
NPTS = 25
JOINTS = ['hip_flexion','knee_angle','ankle_angle']

def load_sto(p):
    L=open(p).read().splitlines(); hi=[i for i,l in enumerate(L) if l.lower().startswith('time')][0]
    cols=L[hi].split('\t'); d=np.array([[float(x) for x in l.split('\t')] for l in L[hi+1:] if l.strip()])
    return cols,d
def ang(cols,d,j,s):
    p=f'/jointset/{j.split("_")[0]}_{s}/{j}_{s}/value'
    m=[i for i,c in enumerate(cols) if c==p]
    return np.degrees(d[:,m[0]]) if m else None
def rs(y):
    return interp1d(np.linspace(0,100,len(y)),y)(np.linspace(0,100,NPTS))

def feats(sto, rng=None, noise=0.0):
    cols,d=load_sto(sto); s=int(len(d)*0.4); f={}
    for j in JOINTS:
        l=ang(cols,d,j,'l')[s:]; r=ang(cols,d,j,'r')[s:]
        # apply measurement noise to the RAW signals so that ALL features (including the
        # ROM/min/max summaries used for the headline) reflect capture error
        if noise and rng is not None:
            l = l + rng.normal(0, noise, len(l))
            r = r + rng.normal(0, noise, len(r))
        wl,wr=rs(l),rs(r)
        for i in range(NPTS):
            f[f'S::{j}_p{i:02d}']=float(wl[i])                 # paretic waveform
            # NOTE: per-point contralateral difference removed - the previous np.roll(NPTS//2)
            # shifted ~2.9 s over a multi-cycle window instead of half a gait cycle, so those
            # features were not phase-aligned and were uninformative. Phase-independent
            # asymmetry summaries (ROM/min/max differences, below) are used instead.
        f[f'S::{j}_ROM']=float(np.ptp(l)); f[f'S::{j}_min']=float(np.min(l)); f[f'S::{j}_max']=float(np.max(l))
        f[f'A::{j}_ROMd']=float(np.ptp(l)-np.ptp(r))
        f[f'A::{j}_mind']=float(np.min(l)-np.min(r)); f[f'A::{j}_maxd']=float(np.max(l)-np.max(r))
    return f

def dataset(n_rep=8, noise=2.0, seed=0):
    rng=np.random.default_rng(seed); rows=[]
    for folder in sorted(glob.glob(os.path.join(RES,'*.I'))):
        tag=os.path.basename(folder).split('.')[0]
        m=re.match(r'(PF|DF|KE|KF|HF)(\d+)L$',tag)
        if not m: continue
        qc=glob.glob(os.path.join(folder,'qc.sto*'))
        if not qc: continue
        for _ in range(n_rep):
            f=feats(qc[0],rng,noise); f['mech']=m.group(1); f['sev']=int(m.group(2)); f['tag']=tag
            rows.append(f)
    return pd.DataFrame(rows)

def run(df, seeds=10):
    fc=[c for c in df.columns if c.startswith(('S::','A::'))]
    tags=sorted(df.tag.unique())
    for m in MECHS: df[f'is_{m}']=(df.mech==m).astype(int)
    agg1=[];agg3=[];per={m:[0,0] for m in MECHS}
    for seed in range(seeds):
        c1=c3=n=0
        for ho in tags:
            tr=df[df.tag!=ho]; te=df[df.tag==ho]
            Y=tr[[f'is_{m}' for m in MECHS]].to_numpy(int)
            mdl=Pipeline([('imp',SimpleImputer(strategy='median')),
                          ('clf',MultiOutputClassifier(RandomForestClassifier(300,random_state=seed,n_jobs=-1,class_weight='balanced')))])
            mdl.fit(tr[fc].to_numpy(float),Y)
            P=np.array([p[:,1] if p.shape[1]==2 else np.zeros(len(te)) for p in mdl.predict_proba(te[fc].to_numpy(float))]).T
            Pm=P.mean(0); order=np.argsort(-Pm); true=MECHS.index(te.mech.iloc[0])
            n+=1
            if order[0]==true: c1+=1; per[te.mech.iloc[0]][0]+=1
            if true in order[:3]: c3+=1
            per[te.mech.iloc[0]][1]+=1
        agg1.append(c1/n); agg3.append(c3/n)
    print(f'\n=== SCONE unilateral weakness identifiability (LOCO, {len(tags)} conditions, {seeds} seeds) ===')
    print(f'AGGREGATE top-1 = {np.mean(agg1):.3f} ± {np.std(agg1):.3f}   (chance 0.20)')
    print(f'AGGREGATE top-3 = {np.mean(agg3):.3f} ± {np.std(agg3):.3f}   (chance 0.60)')
    print('per-group top-1:')
    for m in MECHS:
        h,t=per[m]; print(f'  {m}_w: {h}/{t} = {h/max(t,1):.2f}')
    return np.mean(agg1),np.mean(agg3)

if __name__=='__main__':
    df=dataset()
    print(f'loaded {df.tag.nunique()} conditions x {len(df)//df.tag.nunique()} noise reps, {len([c for c in df.columns if c.startswith(("S::","A::"))])} features')
    run(df)
