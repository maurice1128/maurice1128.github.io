import json,numpy as np
f=json.load(open(r'C:\Users\maurice\Desktop\spasticity_paper\scone\scone_seed_features.json'))
SEV={'HEALTHY':0,'PAR20':20,'PAR40':40,'PAR60':60}
rows=[]
for c,s in SEV.items():
    for k,v in f.items():
        if k.startswith(c+'_s') and v.get('status')=='ok':
            rows.append((s,v['cycle_time'],v['ank_min'],v['ank_hs']))
A=np.array(rows); S,CT,MN,HS=A[:,0],A[:,1],A[:,2],A[:,3]
def r(a,b):
    return float('nan') if a.std()==0 or b.std()==0 else float(np.corrcoef(a,b)[0,1])
ctw,mnw,hsw=CT.copy(),MN.copy(),HS.copy()
for s in np.unique(S):
    m=S==s
    ctw[m]-=CT[m].mean(); mnw[m]-=MN[m].mean(); hsw[m]-=HS[m].mean()
print('n=',len(A))
print('WITHIN (severity fixed): cadence-vs-ank_min r=%+.3f  cadence-vs-ank_hs r=%+.3f'%(r(ctw,mnw),r(ctw,hsw)))
print('BETWEEN: sev-vs-ank_min r=%+.3f  sev-vs-ank_hs r=%+.3f  sev-vs-cadence r=%+.3f'%(r(S,MN),r(S,HS),r(S,CT)))
def part(x,y,z):
    rx=x-np.polyval(np.polyfit(z,x,1),z); ry=y-np.polyval(np.polyfit(z,y,1),z); return r(rx,ry)
print('PARTIAL (control cadence): sev-vs-ank_min r=%+.3f  sev-vs-ank_hs r=%+.3f'%(part(S,MN,CT),part(S,HS,CT)))
