"""REGISTERED cross-validation + contralateral-drift decomposition for the L/R ratio. Round 57.

WHY. Every threshold in LR_ASYMMETRY.json is FITTED on all data and was reported as an upper
bound. The ABSOLUTE feature was required to pass LOSO (37/40 against a fitted 39/40). If the ratio
enters the manuscripts at 1.0000 mild accuracy without the same treatment, a stricter standard has
been applied to the feature that failed than to the one that succeeded -- the shape of every result
this project has withdrawn.

AND: the denominator is not inert. Right-limb ROM runs 17.6-22.6 spastic vs 19.6-28.6 weak
(CMW80 28.553). A denominator that moves with severity is not a pure within-subject normaliser.
If most of the separation comes from the denominator, the ratio is a CONTRALATERAL-ADAPTATION
measure wearing a normalisation's clothes -- which changes what the paper claims.

PREDICTIONS, WRITTEN BEFORE EXECUTION:
  PR1  Ratio SURVIVES cross-validation: mild leave-one-seed-out accuracy >= 0.875 (>= 14/16).
  PR2  Ratio's cross-validated mild accuracy EXCEEDS left-only's, by at least one seed.
  PR3  ** DECOMPOSITION. The per-subject denominator does REAL NORMALISING WORK, not signal
       carrying. ** Concretely: rom_l / rom_r(subject) will BEAT rom_l / const, where const is the
       corpus-mean right ROM. Reason: within the mild rungs the right-limb values are unordered
       and overlapping (spastic 22.59/19.42, weak 19.59/21.77), so the denominator cannot be
       carrying between-condition signal there; what it can do is remove BETWEEN-SEED scale
       variance. If instead rom_l/const matches or beats the true ratio, the denominator is inert
       and the ratio is only a unit change -- report that plainly.
  PR4  Right-limb-only remains non-discriminating at mild rungs under cross-validation.
This file must not be modified after seeing the output.
"""
import glob, json, os, sys
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S
REPLAY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_crossed")
SP = ["DR2K050","DR2K075","DR2K100","DR2K150","DR2K200"]
WK = ["PAR20","PAR40","PAR60","CMW70","CMW80"]
MSP, MWK = ["DR2K050","DR2K075"], ["PAR20","PAR40"]

def load():
    o={}
    for d in sorted(glob.glob(os.path.join(REPLAY,"*"))):
        if not os.path.isdir(d): continue
        st=[x for x in glob.glob(os.path.join(d,"*.sto")) if os.path.getsize(x)>1000]
        if len(st)!=1: continue
        c=os.path.basename(d).split(".")[0].rsplit("_s",1)[0]
        if c not in SP+WK: continue
        fl=S.cycle_features(st[0],side="l",settle=1.0); fr=S.cycle_features(st[0],side="r",settle=1.0)
        o.setdefault(c,[]).append((fl["ank_rom"],fr["ank_rom"]))
    return o
per=load()
MEANR=float(np.mean([r for c in per for (_,r) in per[c]]))
def val(k,l,r):
    return {"l":l,"r":r,"ratio":l/r,"l_over_const":l/MEANR}[k]
def fit(sp,wk):
    v=np.array(sp+wk,float); lab=np.array([1]*len(sp)+[0]*len(wk)); best=(None,-1,1)
    for t in np.unique(v):
        for s in (1,-1):
            a=float(np.mean((((v<t) if s>0 else (v>=t)).astype(int))==lab))
            if a>best[1]: best=(t,a,s)
    return best[0],best[2]
def apply(t,s,x): return int(x<t) if s>0 else int(x>=t)
def loso(k,sps,wks):
    pts=[(val(k,l,r),1) for c in sps for (l,r) in per[c]]+[(val(k,l,r),0) for c in wks for (l,r) in per[c]]
    ok=0
    for i in range(len(pts)):
        tr=[p for j,p in enumerate(pts) if j!=i]
        t,s=fit([v for v,g in tr if g==1],[v for v,g in tr if g==0])
        ok+=int(apply(t,s,pts[i][0])==pts[i][1])
    return ok/len(pts),len(pts)
def lcpo(k,sps,wks):
    accs=[]
    for a in sps:
        for b in wks:
            trs=[c for c in sps if c!=a]; trw=[c for c in wks if c!=b]
            t,s=fit([val(k,l,r) for c in trs for (l,r) in per[c]],[val(k,l,r) for c in trw for (l,r) in per[c]])
            te=[(val(k,l,r),1) for (l,r) in per[a]]+[(val(k,l,r),0) for (l,r) in per[b]]
            accs.append(np.mean([apply(t,s,v)==g for v,g in te]))
    return float(np.mean(accs)),float(np.min(accs)),len(accs)
def holdout(k):
    t,s=fit([val(k,l,r) for c in SP if c not in MSP for (l,r) in per[c]],
            [val(k,l,r) for c in WK if c not in MWK for (l,r) in per[c]])
    te=[(val(k,l,r),1) for c in MSP for (l,r) in per[c]]+[(val(k,l,r),0) for c in MWK for (l,r) in per[c]]
    return float(np.mean([apply(t,s,v)==g for v,g in te])),len(te)
print("="*76); print("REGISTERED CROSS-VALIDATION + DRIFT DECOMPOSITION"); print("="*76)
print("  corpus-mean right ROM (the constant denominator) = %.4f deg\n"%MEANR)
res={}
for scope,sps,wks in (("ALL",SP,WK),("MILD",MSP,MWK)):
    print("  %s RUNGS"%scope)
    for k,nm in (("l","left-only"),("r","right-only"),("ratio","RATIO l/r"),("l_over_const","l / const")):
        a,n=loso(k,sps,wks); m,mn,np_=lcpo(k,sps,wks)
        print("    %-13s LOSO %.4f (%d/%d)   LCPO mean %.3f min %.3f (%d folds)"%(nm,a,round(a*n),n,m,mn,np_))
        res["%s_%s"%(scope,k)]={"loso":a,"n":n,"lcpo_mean":m,"lcpo_min":mn}
    print()
print("  MILDEST-RUNG HOLDOUT (fit on severe only, test on mild):")
for k,nm in (("l","left-only"),("ratio","RATIO l/r"),("l_over_const","l / const")):
    a,n=holdout(k); print("    %-13s %.4f (%d/%d)"%(nm,a,round(a*n),n)); res["holdout_%s"%k]=a
print("\n  PR3 DECOMPOSITION -- does the per-subject denominator do real work?")
for scope in ("ALL","MILD"):
    d=res["%s_ratio"%scope]["loso"]-res["%s_l_over_const"%scope]["loso"]
    print("    %-5s LOSO  ratio %.4f  vs  l/const %.4f   diff %+.4f  -> %s"
          %(scope,res["%s_ratio"%scope]["loso"],res["%s_l_over_const"%scope]["loso"],d,
            "denominator does REAL WORK" if d>1e-9 else ("denominator INERT (unit change only)" if abs(d)<=1e-9 else "denominator HURTS")))
rr=[r for c in SP+WK for (_,r) in per[c]]; sev=[np.mean([r for (_,r) in per[c]]) for c in SP+WK]
print("\n  contralateral drift: right-limb condition means %.3f - %.3f (spread %.3f)"%(min(sev),max(sev),max(sev)-min(sev)))
json.dump(res,open(os.path.abspath(os.path.join(REPLAY,"..","..","paper","LR_CROSSVAL.json")),"w"),indent=1)
print("\n  wrote paper/LR_CROSSVAL.json")
