# -*- coding: utf-8 -*-
"""r525: score peak swing dorsiflexion the way knee-at-contact is scored, and against patients.

The largest effect in this study sits in a sub-paragraph of section 3.2 and has never been scored
the way the primary endpoint is: cell by cell, against the seed noise floor, and against the spread
a patient population presents. Section 3.5 concludes that no readout serves one patient, but reached
that on knee-at-contact alone and against the whole stroke population. The clinical question is
narrower: a patient who already has spastic equinovarus, whose two components are to be apportioned.
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]
CT = [("R151C", None)]


def cell(fam, sd):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    if float(t[-1]) < T1 or len(w) < 5:
        return None
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    on = grf > thr
    pk = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
    return float(np.mean(pk)) if pk else None


def arm(fams):
    out = []
    for f, kv in fams:
        for sd in range(101, 107):
            x = cell(f, sd)
            if x is not None:
                out.append({"fam": f, "dose": kv, "seed": sd, "peak": x})
    return out


hy, wk, ct = arm(HY), arm(WK), arm(CT)
print("cells: hyper %d  weak %d  control %d" % (len(hy), len(wk), len(ct)))

hv = [c["peak"] for c in hy]
wv = [c["peak"] for c in wk]
cv = [c["peak"] for c in ct]
gap = min(wv) - max(hv)                          # weakness is the more dorsiflexed arm
sds = []
for src in (hy, wk):
    for f in set(c["fam"] for c in src):
        v = [c["peak"] for c in src if c["fam"] == f]
        if len(v) >= 2:
            sds.append(float(np.std(v, ddof=1)))
seed = float(np.mean(sds))
eff = float(np.mean(wv) - np.mean(hv))
print("\nhyper %.3f   weak %.3f   control %.3f   effect %.3f deg"
      % (np.mean(hv), np.mean(wv), np.mean(cv) if cv else float("nan"), eff))
print("cell gap %.3f   disjoint %s   seed SD %.3f   gap/SD %.2f"
      % (gap, gap > 0, seed, gap / seed))

print("\nhyperreflexia ladder:")
for f, kv in HY:
    v = [c["peak"] for c in hy if c["fam"] == f]
    if v:
        print("   KV %.3f   %7.3f   (n=%d)" % (kv, np.mean(v), len(v)))
print("weakness ladder:")
for f, kv in WK:
    v = [c["peak"] for c in wk if c["fam"] == f]
    if v:
        print("   x%.3f    %7.3f   (n=%d)" % (kv, np.mean(v), len(v)))

# ---- against patients -----------------------------------------------------------------------
Phi = lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def pooled(m0, s0, m1, s1):
    """total SD of the whole cohort from two subgroup means and SDs of equal size"""
    return math.sqrt((s0 * s0 + s1 * s1) / 2.0 + ((m1 - m0) ** 2) / 4.0)


VAR = {
    "knee at contact": {
        "eff": 5.2799, "within": [7.93, 9.16], "pooled": pooled(8.30, 7.93, 8.03, 9.16),
        "SEM": 3.7041 / math.sqrt(2.0),
        "SEM_note": "ref [13], redefined in section 3.5"},
    "peak swing dorsiflexion": {
        "eff": eff, "within": [4.20, 4.21], "pooled": pooled(2.76, 4.20, 9.99, 4.21),
        "SEM": 4.9 / (1.96 * math.sqrt(2.0)),
        "SEM_note": "ref [15] MDC 4.9 deg at ICC 0.941, inverted through that paper's own "
                    "definition MDC = SEM x 1.96 x sqrt(2)"},
}

print("\n%-26s %8s %8s %7s %7s %10s" % ("variable", "effect", "pop SD", "SEM", "d", "misclass"))
out = {}
for n, v in VAR.items():
    row = {"effect_deg": v["eff"], "SEM_deg": v["SEM"], "SEM_source": v["SEM_note"],
           "within_subgroup_SD_deg": v["within"], "pooled_cohort_SD_deg": v["pooled"]}
    for conv, sd in (("within_subgroup", float(np.mean(v["within"]))),
                     ("pooled_cohort", v["pooled"])):
        tot = math.sqrt(sd * sd + v["SEM"] ** 2)
        d = v["eff"] / tot
        row[conv] = {"population_SD_deg": sd, "total_SD_deg": tot, "cohens_d": d,
                     "misclassification_rate": Phi(-d / 2)}
    out[n] = row
    pc = row["pooled_cohort"]
    print("%-26s %8.3f %8.3f %7.3f %7.3f %9.1f%%"
          % (n, v["eff"], pc["population_SD_deg"], v["SEM"], pc["cohens_d"],
             100 * pc["misclassification_rate"]))

print("\nwithin-subgroup convention, for comparison:")
for n, v in out.items():
    w = v["within_subgroup"]
    print("   %-26s d %.3f -> %.1f%%" % (n, w["cohens_d"], 100 * w["misclassification_rate"]))

dep = {
    "id": "SWINGDF_r525",
    "why": ("Section 3.5 concludes that no readout serves one patient, but reached that on "
            "knee-at-contact alone. This scores the study's largest effect the same way, cell by "
            "cell and against the same patient cohort, so the two can be compared."),
    "n_cells": {"hyperreflexia": len(hy), "weakness": len(wk), "control": len(ct)},
    "simulation": {
        "hyper_mean_deg": float(np.mean(hv)), "weak_mean_deg": float(np.mean(wv)),
        "control_mean_deg": float(np.mean(cv)) if cv else None,
        "effect_deg": eff, "cell_gap_deg": gap, "cells_disjoint": bool(gap > 0),
        "mean_within_family_seed_SD_deg": seed, "gap_in_seed_SD": gap / seed,
        "by_hyper_dose": {str(kv): float(np.mean([c["peak"] for c in hy if c["fam"] == f]))
                          for f, kv in HY if [c for c in hy if c["fam"] == f]},
        "by_weak_dose": {str(kv): float(np.mean([c["peak"] for c in wk if c["fam"] == f]))
                         for f, kv in WK if [c for c in wk if c["fam"] == f]}},
    "against_patients": out,
    "EXTERNAL_CORRESPONDENCE": (
        "ref [5] splits its 34 patients by initial-contact type and reports peak swing ankle angle "
        "of 2.76 deg in the forefoot-contact group and 9.99 deg in the rearfoot group. Forefoot "
        "contact is the plantarflexor-dominant presentation. The simulation's two arms sit at "
        "%.2f and %.2f deg on a variable nothing in the objective function targets."
        % (float(np.mean(hv)), float(np.mean(wv)))),
    "CAVEATS": [
        "the effect is carried almost entirely by one lesion: weakness displaces this variable "
        "0.43 deg from control, so a high reading means hyperreflexia is ABSENT rather than that "
        "weakness is present. In a patient already known to have spastic equinovarus that is the "
        "apportionment being asked for; as a screening variable across all stroke it is not",
        "ref [5] splits its cohort by initial-contact type, which is close to the quantity being "
        "predicted, so the within-subgroup SD is conditioned on the outcome and understates what "
        "an unselected patient presents. The pooled cohort SD is the honest denominator and is the "
        "one quoted in the table",
        "ref [15]'s MDC is from treadmill walking and its authors state it may not be used to "
        "interpret overground studies",
        "this endpoint has not been through the stationarity rule or the batch null"],
}
io.open(os.path.join(P, "SWINGDF_r525.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWINGDF_r525.json")
