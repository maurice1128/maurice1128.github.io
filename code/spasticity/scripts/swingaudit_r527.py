# -*- coding: utf-8 -*-
"""r527: the two things that decide whether r525/r526 survive, before any of it reaches the paper.

r526 finds peak swing dorsiflexion grades reflex gain with a weakness coefficient at the noise
floor, and separates every mixed-grid combination. Two threats stand in front of that result and
both favour it if left unchecked.

(1) SURVIVAL. 74 of 96 mixed-grid cells passed the gate. If the dropped cells are concentrated
    where both lesions are deep, the surviving grid is a biased sample and the flat weakness
    gradient is partly a selection effect. The manuscript already carries this confound for the
    knee and cannot quietly avoid it here.

(2) RANGE. The weakness coefficient is indistinguishable from zero over the scalings that survive.
    If severe dorsiflexor weakness never survives, the claim is not 'swing dorsiflexion is immune to
    weakness' but the far weaker 'over the mild weakness this model can walk with, it is immune' --
    and clinical drop foot is not in that range. This measures where the surviving range ends.

(3) STATIONARITY. Rule 3, which the endpoint has never been through. A per-cycle series that does
    not keep one sign is not a stable readout.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
WEAK = {"060": 0.60, "070": 0.70, "080": 0.80, "100": 1.00}
GAIN = {"0125": 0.0125, "0250": 0.0250, "0500": 0.0500, "1100": 0.1100}


def probe(fam, sd):
    """returns (exists, admitted, t_end, n_cycles, per-cycle swing dorsiflexion)"""
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return {"exists": True, "admitted": False, "why": "no sto"}
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return {"exists": True, "admitted": False, "why": "empty sto"}
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    te, nc = float(t[-1]), len(w)
    if te < T1:
        return {"exists": True, "admitted": False, "why": "fell at %.2f s" % te,
                "t_end": te, "n_cycles": nc}
    if nc < 5:
        return {"exists": True, "admitted": False, "why": "only %d cycles" % nc,
                "t_end": te, "n_cycles": nc}
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    on = grf > thr
    pc = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pc.append(float(np.max(an[a:b][idx])))
    return {"exists": True, "admitted": True, "t_end": te, "n_cycles": nc, "per_cycle": pc}


cells = {}
for wk, wv in WEAK.items():
    for gk, gv in GAIN.items():
        fam = "R424W%s%s" % (wk, gk)
        got = []
        for sd in range(101, 107):
            r = probe(fam, sd)
            if r:
                got.append(r)
        cells[(wv, 2 * gv)] = got

# ---- (1) survival -----------------------------------------------------------------------------
print("admitted seeds per cell (of those that exist):")
print("   %-9s" % "weakness" + "".join("  KV %.3f" % (2 * g) for g in sorted(GAIN.values())))
surv = {}
for wv in sorted(WEAK.values()):
    line = "   x%.2f    " % wv
    for gv in sorted(GAIN.values()):
        g = cells[(wv, 2 * gv)]
        a, n = sum(1 for x in g if x["admitted"]), len(g)
        surv[(wv, 2 * gv)] = (a, n)
        line += "     %d/%d" % (a, n)
    print(line)

by_w = {wv: (sum(surv[(wv, 2 * g)][0] for g in GAIN.values()),
             sum(surv[(wv, 2 * g)][1] for g in GAIN.values())) for wv in WEAK.values()}
by_g = {2 * gv: (sum(surv[(w, 2 * gv)][0] for w in WEAK.values()),
                 sum(surv[(w, 2 * gv)][1] for w in WEAK.values())) for gv in GAIN.values()}
print("\nsurvival by weakness: " + "  ".join("x%.2f %d/%d" % (w, a, n) for w, (a, n) in sorted(by_w.items())))
print("survival by gain:     " + "  ".join("KV%.3f %d/%d" % (g, a, n) for g, (a, n) in sorted(by_g.items())))

# ---- (2) where the surviving weakness range ends -----------------------------------------------
alive_w = sorted(w for w, (a, n) in by_w.items() if a > 0)
full_w = sorted(w for w, (a, n) in by_w.items() if n and a == n)
print("\nweakness scalings with any surviving cell: %s" % alive_w)
print("weakness scalings surviving in every cell:  %s" % full_w)
print("SCALING NOTE: x1.00 is NO weakness. The deepest weakness with any survivor is x%.2f, "
      "which is a %d%% reduction in tibialis anterior force." % (min(alive_w), round(100 * (1 - min(alive_w)))))

# ---- (3) stationarity --------------------------------------------------------------------------
allpc = [x["per_cycle"] for g in cells.values() for x in g if x["admitted"] and len(x["per_cycle"]) >= 5]
per = [float(np.mean([p[i] for p in allpc])) for i in range(5)]
hy = [x["per_cycle"] for (w, g), c in cells.items() if g >= 0.100 for x in c
      if x["admitted"] and len(x["per_cycle"]) >= 5]
lo = [x["per_cycle"] for (w, g), c in cells.items() if g <= 0.050 for x in c
      if x["admitted"] and len(x["per_cycle"]) >= 5]
diff = [float(np.mean([p[i] for p in lo]) - np.mean([p[i] for p in hy])) for i in range(5)]
print("\nstationarity (rule 3): per-cycle difference, low gain minus high gain")
print("   by cycle: " + "  ".join("%+.3f" % d for d in diff))
print("   one sign: %s   spread %.3f deg   window mean %.3f   spread/mean %.2f"
      % (all(d > 0 for d in diff) or all(d < 0 for d in diff),
         max(diff) - min(diff), float(np.mean(diff)), (max(diff) - min(diff)) / abs(np.mean(diff))))

dep = {
 "id": "SWINGAUDIT_r527",
 "why": ("Two threats stand in front of r525/r526 and both favour the result if left unchecked: a "
         "survival bias in which cells reach the gate, and a weakness range too mild to be the "
         "clinical lesion. Rule 3 has also never been applied to this endpoint."),
 "survival": {"per_cell_admitted_of_existing": {"x%.2f_KV%.3f" % k: list(v) for k, v in sorted(surv.items())},
              "by_weakness": {str(k): list(v) for k, v in sorted(by_w.items())},
              "by_gain": {str(k): list(v) for k, v in sorted(by_g.items())}},
 "weakness_range": {"any_survivor": alive_w, "complete_survival": full_w,
                    "deepest_surviving_scaling": min(alive_w),
                    "deepest_surviving_as_percent_force_lost": round(100 * (1 - min(alive_w)))},
 "stationarity_rule3": {"per_cycle_difference_deg": diff,
                        "keeps_one_sign": bool(all(d > 0 for d in diff) or all(d < 0 for d in diff)),
                        "spread_deg": max(diff) - min(diff),
                        "window_mean_deg": float(np.mean(diff)),
                        "spread_over_mean": (max(diff) - min(diff)) / abs(float(np.mean(diff)))},
 "per_cycle_pooled_deg": per,
}
io.open(os.path.join(P, "SWINGAUDIT_r527.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWINGAUDIT_r527.json")
