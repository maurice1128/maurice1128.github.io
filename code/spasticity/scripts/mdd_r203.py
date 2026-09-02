# -*- coding: utf-8 -*-
"""Between-seed spread of ROM on the six EXISTING control cells, at the benchmark speed.

Read-only. No simulation. This is the input the r203 registration needs to set a minimum
detectable difference (MDD) BEFORE any speed cell is run.

ROM = per gait cycle (max - min); per cell, mean over admitted cycles.
cycle_time = mean cycle duration (it is already a per-cycle scalar; no ROM).
*_LmR = ROM of the (left - right) time series.
"""
import os, sys, glob, json
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np
import sto_utils as S

RESULTS = r"C:\Users\maurice\Documents\SCONE\results"
SEEDS = [101, 102, 103, 104, 105, 106]
SETTLE, T1 = 1.0, 13.58
BASE = ["ankle_angle_l","ankle_angle_r","knee_angle_l","knee_angle_r",
        "hip_flexion_l","hip_flexion_r","hip_adduction_l","hip_adduction_r",
        "pelvis_list","pelvis_rotation","lumbar_bending"]
LMR = [("ankle_angle_LmR","ankle_angle_l","ankle_angle_r"),
       ("knee_angle_LmR","knee_angle_l","knee_angle_r"),
       ("hip_flexion_LmR","hip_flexion_l","hip_flexion_r"),
       ("hip_adduction_LmR","hip_adduction_l","hip_adduction_r")]

def ctrl_dir(s):
    g=[d for d in glob.glob(os.path.join(RESULTS,"R151C_s%d.*"%s)) if os.path.isdir(d)]
    return sorted([d for d in g if os.path.exists(os.path.join(d,"history.txt"))])[0]

def per_seed(s):
    d=ctrl_dir(s); sto=sorted(glob.glob(os.path.join(d,"*.par.sto")))[-1]
    cols,dat=S.load_sto(sto)
    t=np.asarray(S.col(cols,dat,"time"),dtype=float)
    grf,thr=S.grf_vertical(cols,dat,"l"); idx=S.heel_strikes(t,grf,thresh=thr)
    cyc=[(idx[k],idx[k+1]) for k in range(len(idx)-1)
         if t[idx[k]]>=SETTLE and t[idx[k+1]]<=T1]
    cyc=cyc[:-1] if len(cyc)>=2 else cyc
    out={"n_cycles":len(cyc)}
    series={c:np.asarray(S.col(cols,dat,c),dtype=float) for c in BASE}
    for nm,l,r in LMR: series[nm]=series[l]-series[r]
    for nm,v in series.items():
        out[nm]=float(np.mean([v[a:b].max()-v[a:b].min() for a,b in cyc]))
    out["cycle_time"]=float(np.mean([t[b]-t[a] for a,b in cyc]))
    return out

rows=[per_seed(s) for s in SEEDS]
chans=BASE+[n for n,_,_ in LMR]+["cycle_time"]
print("="*94)
print("BETWEEN-SEED SPREAD OF ROM, six control cells, benchmark speed, window [%.2f, %.2f]"%(SETTLE,T1))
print("="*94)
print("cycles per cell: %s"%[r["n_cycles"] for r in rows])
print()
print("%-22s %10s %10s %10s   %10s"%("channel","mean","SD(n=6)","CV %","MDD_2SE"))
res={}
for c in chans:
    v=np.array([r[c] for r in rows]); m,sd=v.mean(),v.std(ddof=1)
    sd_diff=sd*np.sqrt(2.0)          # upper bound: independent across the two speeds
    se_diff=sd_diff*np.sqrt(2.0/6.0) # SE of a 6-vs-6 arm-mean difference
    mdd=2.0*se_diff
    res[c]={"mean":m,"sd":sd,"cv_pct":100*sd/abs(m) if m else None,"mdd_2se":mdd}
    print("%-22s %10.4f %10.4f %10.2f   %10.4f"%(c,m,sd,100*sd/abs(m) if m else float('nan'),mdd))
print()
print("MDD_2SE = smallest arm-mean ENDPOINT-DIFFERENCE detectable at 2 SE, 6 v 6,")
print("  assuming SD of the 0.80->1.30 difference <= sqrt(2) x SD(ROM at benchmark).")
print("  Paired seeds correlate across speeds, so sqrt(2) is an UPPER bound and MDD is CONSERVATIVE.")
json.dump({"seeds":SEEDS,"window":[SETTLE,T1],"n_cycles":[r["n_cycles"] for r in rows],
           "per_channel":res},open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\MDD_r203.json","w"),indent=1)
print("\ndeposited: paper/MDD_r203.json")
