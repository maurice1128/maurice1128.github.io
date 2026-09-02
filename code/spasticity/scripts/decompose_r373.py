# -*- coding: utf-8 -*-
"""How much of the KV0.035-vs-DFweak stance activation gap IS the added reflex term?

The lesion adds RV = KV*max(0,V(t-0.020)) to soleus drive. The endpoint is soleus stance
activation. If the gap were simply that added term read back, RV would account for all of it.
This measures what fraction it actually accounts for. UNREGISTERED, POST-HOC, descriptive.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S
RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\DECOMPOSE_r373.json"

def cell(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1: return None
    f = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))[-1]
    cols, dat = S.load_sto(f); t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l"); on = grf > thr
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k+1]) for k in range(len(hs)-1) if t[hs[k]] >= 1.0]
    win = [c for c in allc if t[c[1]] <= 9.73]; win = win[:-1] if len(win) >= 2 else win
    if t[-1] < 9.73 or len(win) < 5: return None
    st = np.concatenate([np.arange(a,b)[on[a:b]] for a,b in win if on[a:b].any()])
    sw = np.concatenate([np.arange(a,b)[~on[a:b]] for a,b in win if (~on[a:b]).any()])
    o = {"channels_present": [c for c in cols if c.startswith("soleus_l.")]}
    for ch in ("soleus_l.activation","soleus_l.excitation","soleus_l.RV"):
        v = S.col(cols, dat, ch)
        o[ch] = {"stance": float(np.mean(v[st])), "swing": float(np.mean(v[sw]))} if v is not None else None
    return o

res = {"what": "fraction of the stance activation gap attributable to the added reflex term RV",
       "status": "UNREGISTERED, POST-HOC, descriptive; changes no verdict", "arms": {}}
fams = {"KV0.035": ["R291KV0035"], "KV0.0125": ["R289KV0125"], "KV0.00625": ["R289KV00625"],
        "DFweak": ["R151W","R169W090","R169W095","R174W870","R174W892","R174W915"]}
for nm, fs in fams.items():
    rows = []
    for f in fs:
        for sd in range(101, 107):
            r = cell("%s_s%d" % (f, sd))
            if r: rows.append(r)
    def m(ch, ph):
        v = [r[ch][ph] for r in rows if r.get(ch)]
        return float(np.mean(v)) if v else None
    res["arms"][nm] = {"n": len(rows),
                       "A_stance": m("soleus_l.activation","stance"),
                       "A_swing":  m("soleus_l.activation","swing"),
                       "RV_stance": m("soleus_l.RV","stance"),
                       "RV_swing":  m("soleus_l.RV","swing")}
    print(nm, json.dumps(res["arms"][nm]))
w = res["arms"]["DFweak"]["A_stance"]
for nm in ("KV0.035","KV0.0125","KV0.00625"):
    a = res["arms"][nm]; rv = a["RV_stance"]; d = a["A_stance"] - w
    a["gap_vs_DFweak"] = d
    a["RV_share_of_gap"] = (rv / d) if (rv is not None and d) else None
    a["reorganised_share"] = (1 - rv / d) if (rv is not None and d) else None
    print("%-10s gap %+.6f  RV_stance %+.6f  RV share %s"
          % (nm, d, rv if rv is not None else float('nan'),
             ("%.1f%%" % (100*rv/d)) if (rv is not None and d) else "n/a"))
io.open(OUT,"w",encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print("wrote", OUT, os.path.getsize(OUT), "B")
