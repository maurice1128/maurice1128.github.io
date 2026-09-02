# -*- coding: utf-8 -*-
"""r544: does an about-to-fall gait produce the endpoint's signature without a stretch reflex?

The manuscript bounds the survival confound with a within-dose regression of the endpoint on
simulation end time. An adversarial review found that bound unsound: the guard in swingfull_r530.py
requires within-family variation in end time, and every weakness cell ends at exactly the horizon, so
all six weakness families are silently dropped and the slope is fitted on hyperreflexia families
alone and then extrapolated across a 7.28 s gap into a regime containing none of them. It also
carries no uncertainty, and the five per-family slopes are widely dispersed.

The same review pointed at a control the archive already contains and the manuscript does not use.
The plantarflexor-weakness families (r276 WPF, r285 BF, r287 BF, r291 BF) carry a lesion that is
neither of the two arms and no stretch reflex at all, and many of their cells die inside the
hyperreflexia arm's own end-time band. If short survival alone produced the endpoint's signature,
these cells would show it. This computes the endpoint on them under the corpus conventions.
"""
import glob, io, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
BAND = None   # derived below from the hyperreflexia arm itself, not preset
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


def npar(d):
    return len(glob.glob(os.path.join(d, "[0-9]*.par")))


def cell(d):
    st = sorted(glob.glob(os.path.join(d, "*.par.sto")))
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
    on = grf > thr
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    pk = []
    for a, b in w:
        i = np.where(~on[a:b])[0]
        if i.size:
            pk.append(float(np.max(an[a:b][i])))
    if not pk:
        return None
    return {"t_end": float(t[-1]), "peak": float(np.mean(pk)),
            "knee_ic": float(np.mean([kn[a] for a, _ in w]))}


def collect(pattern):
    out = []
    for d in sorted(glob.glob(os.path.join(RES, pattern))):
        if not os.path.isdir(d):
            continue
        r = cell(d)
        if r:
            r["dir"] = os.path.basename(d)
            r["npar"] = npar(d)
            out.append(r)
    return out


ctrl = None  # assigned below; the band must be known before the fallers are filtered
def one_per_seed(v):
    """A lineage-seed can have more than one run directory. Keep the one with the most .par files,
    which is the rule every other script in this corpus uses. Selecting on t_end instead, as an
    earlier version of this file did, would choose runs by the very variable under test."""
    best = {}
    for r in v:
        k = re.sub(r"\..*$", "", r["dir"])
        if k not in best or r["npar"] > best[k]["npar"]:
            best[k] = r
    return list(best.values())


print("loading the two lesion arms first, to derive the band ...")
fall = []
for pat in ("R276WPF*", "R285BF*", "R287BF*", "R291BF*"):
    fall += collect(pat)
# one cell per lineage-seed: keep the run with the most .par files, as elsewhere
fall = one_per_seed(fall)



ctrl = one_per_seed(collect("R151C_s*"))
hy = one_per_seed([r for f in HY for r in collect(f + "_s*")])
wk = one_per_seed([r for f in WK for r in collect(f + "_s*")])
BAND = (min(r["t_end"] for r in hy), max(r["t_end"] for r in hy))
print("   band derived from the hyperreflexia arm: %.2f to %.2f s" % BAND)
hy_band = [r for r in hy if BAND[0] <= r["t_end"] <= BAND[1]]
inband = [r for r in fall if BAND[0] <= r["t_end"] <= BAND[1]]
print("   fallers: %d admitted, %d inside that band" % (len(fall), len(inband)))

V = lambda v, k="peak": [x[k] for x in v]
c0 = float(np.mean(V(ctrl)))
print("\n%-34s %4s %-16s %10s %11s" % ("group", "n", "t_end range (s)", "peak (deg)", "vs control"))
rows = {}
for nm, v in (("control R151C", ctrl),
              ("non-reflex fallers, in band", inband),
              ("hyperreflexia, in band", hy_band),
              ("hyperreflexia, all", hy),
              ("dorsiflexor weakness, all", wk)):
    if not v:
        continue
    m = float(np.mean(V(v)))
    rows[nm] = {"n": len(v), "t_end_min": min(x["t_end"] for x in v),
                "t_end_max": max(x["t_end"] for x in v), "peak_mean": m,
                "peak_min": min(V(v)), "peak_max": max(V(v)), "vs_control": m - c0,
                "knee_ic_mean": float(np.mean(V(v, "knee_ic")))}
    print("%-34s %4d %6.2f-%-9.2f %10.3f %+11.3f"
          % (nm, len(v), rows[nm]["t_end_min"], rows[nm]["t_end_max"], m, m - c0))

ART = 0.03581801092876269
f = rows.get("non-reflex fallers, in band")
h = rows.get("hyperreflexia, in band")
if f and h:
    print("\nfaller cells: peak range [%.3f, %.3f]; hyperreflexia in the same band [%.3f, %.3f]"
          % (f["peak_min"], f["peak_max"], h["peak_min"], h["peak_max"]))
    gap = f["peak_min"] - h["peak_max"]
    print("disjoint: %s, gap %.3f deg" % (gap > 0, gap))
    print("the fallers' displacement from control is %+.3f deg = %.2f x the %.4f deg artefact floor"
          % (f["vs_control"], abs(f["vs_control"]) / ART, ART))
    print("\nknee at contact, same three groups: control %.3f, fallers %.3f, hyperreflexia %.3f"
          % (float(np.mean(V(ctrl, "knee_ic"))), f["knee_ic_mean"], h["knee_ic_mean"]))

# the duration slope, recomputed without the guard that drops the weakness arm
allc = [(r["t_end"], r["peak"], "H") for r in hy] + [(r["t_end"], r["peak"], "W") for r in wk]
sl_pool = float(np.polyfit([x[0] for x in allc], [x[1] for x in allc], 1)[0])
per_fam = []
for f_ in HY + WK:
    v = one_per_seed(collect(f_ + "_s*"))
    ts = [x["t_end"] for x in v]
    if len(v) >= 3 and len(set(round(x, 3) for x in ts)) > 1:
        per_fam.append(float(np.polyfit(ts, [x["peak"] for x in v], 1)[0]))
print("\nthe duration slope as the manuscript computes it, per family: %s"
      % " ".join("%+.3f" % x for x in per_fam))
print("   mean %+.4f deg/s, SD %.4f, SE %.4f over %d families -- and every one of them is a"
      % (np.mean(per_fam), np.std(per_fam, ddof=1), np.std(per_fam, ddof=1) / np.sqrt(len(per_fam)),
         len(per_fam)))
print("   HYPERREFLEXIA family, because all 36 weakness cells end at the horizon and the guard in")
print("   swingfull_r530.py requires within-family variation in end time.")
print("   propagated over the 7.28 s arm gap: %+.3f deg, but +-%.3f at one SE of the slope"
      % (np.mean(per_fam) * 7.28, np.std(per_fam, ddof=1) / np.sqrt(len(per_fam)) * 7.28))

io.open(os.path.join(P, "FALLER_r544.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "FALLER_r544",
 "why": ("The within-dose duration regression excludes every weakness family by construction and "
         "carries no uncertainty. The archive contains a stronger control the manuscript does not "
         "use: plantarflexor-weakness lineages, which carry no stretch reflex and die inside the "
         "hyperreflexia arm's own end-time band."),
 "band_s": list(BAND),
 "band_derivation": "min and max t_end of the admitted hyperreflexia arm, not a preset window",
 "groups": rows,
 "artefact_floor_deg": ART,
 "duration_slope_per_family": per_fam,
 "duration_slope_mean": float(np.mean(per_fam)),
 "duration_slope_SE": float(np.std(per_fam, ddof=1) / np.sqrt(len(per_fam))),
 "duration_slope_families_are_all_hyperreflexia": True,
 "pooled_slope_ignoring_the_guard": sl_pool,
}, indent=1, ensure_ascii=False))
print("\n-> FALLER_r544.json")
