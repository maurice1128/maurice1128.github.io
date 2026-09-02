# -*- coding: utf-8 -*-
"""r600: a falling control whose lesion is independent of the plantarflexors.

A reviewer objected to the duration control of section 3.3 on a point the paper had not answered: the
seventeen fallers carry a plantarflexor-weakness lesion, which is a manipulation of the same muscle
group whose overactivity is claimed to drive the effect. What the argument needs is a limb that falls
for a reason that has nothing to do with the calf.

The archive contains one, and it was never used. R404WKHAM060 scales hamstring force to 0.60 on the
same 3D model and controller as the primary corpus. The hamstrings cross the hip and the knee and not
the ankle, and they are not plantarflexors. All six seeds fall, and they fall earlier than any
hyperreflexia run in the corpus.

They fall too early to pass criterion G, which requires an end time of at least 9.73 s, so this is not
a duration-matched comparison and cannot be reported as one. It is the stronger asymmetric case: if a
limb that fails sooner than any hyperreflexia run still reads as unimpaired at this landmark, then
falling by itself does not produce the signature. Each run is measured over the cycles it completed
before ending, under the corpus conventions in every other respect.

Reads only. Nothing in the archive is written or removed.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE = 1.0
ART = 0.03581801092876269


def npar(d):
    return len(glob.glob(os.path.join(d, "[0-9]*.par")))


def read(d, tmax):
    st = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not st:
        return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1)
           if t[hs[k]] >= SETTLE and t[hs[k + 1]] <= tmax]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if len(cyc) < 3:
        return None
    on = grf > thr
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    pk = [float(np.max(an[a:b][np.where(~on[a:b])[0]])) for a, b in cyc
          if np.where(~on[a:b])[0].size]
    if not pk:
        return None
    return {"t_end": float(t[-1]), "n_cycles": len(pk), "peak": float(np.mean(pk)),
            "knee_ic": float(np.mean([kn[a] for a, _ in cyc]))}


def family(prefix, tmax):
    best = {}
    for d in sorted(glob.glob(os.path.join(RES, prefix + "_s*"))):
        if not os.path.isdir(d):
            continue
        k = os.path.basename(d).split(".")[0]
        r = read(d, tmax)
        if r is None:
            continue
        r["npar"] = npar(d)
        if k not in best or r["npar"] > best[k]["npar"]:
            best[k] = r
    return best


ctrl = family("R151C", 9.73)
hyp = {}
for f in ("R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"):
    hyp.update(family(f, 9.73))
ham = family("R404WKHAM060", 9.03)

c0 = float(np.mean([v["peak"] for v in ctrl.values()]))
rows = {}
for lab, v in (("control, unlesioned", ctrl),
               ("hyperreflexia, all admitted", hyp),
               ("hamstring weakness x0.60", ham)):
    pk = [x["peak"] for x in v.values()]
    rows[lab] = {"n_runs": len(v), "t_end_min": min(x["t_end"] for x in v.values()),
                 "t_end_max": max(x["t_end"] for x in v.values()),
                 "mean_cycles": float(np.mean([x["n_cycles"] for x in v.values()])),
                 "peak_mean": float(np.mean(pk)), "peak_min": min(pk), "peak_max": max(pk),
                 "vs_control_deg": float(np.mean(pk)) - c0,
                 "knee_ic_mean": float(np.mean([x["knee_ic"] for x in v.values()]))}

print("%-30s %4s %-14s %7s %10s %11s" % ("", "runs", "t_end (s)", "cycles", "peak (deg)", "vs control"))
for k, r in rows.items():
    print("%-30s %4d %6.2f-%-7.2f %7.1f %10.3f %+11.3f"
          % (k, r["n_runs"], r["t_end_min"], r["t_end_max"], r["mean_cycles"],
             r["peak_mean"], r["vs_control_deg"]))

h, m = rows["hyperreflexia, all admitted"], rows["hamstring weakness x0.60"]
gap = m["peak_min"] - h["peak_max"]
print("\nhamstring runs end %.2f to %.2f s; every hyperreflexia run ends later (%.2f s at the earliest)"
      % (m["t_end_min"], m["t_end_max"], h["t_end_min"]))
print("hamstring peak range [%.3f, %.3f] against hyperreflexia [%.3f, %.3f]: disjoint by %.3f deg"
      % (m["peak_min"], m["peak_max"], h["peak_min"], h["peak_max"], gap))
print("displacement from control %+.3f deg = %.2f x the %.4f deg protocol artefact"
      % (m["vs_control_deg"], abs(m["vs_control_deg"]) / ART, ART))
print("knee at contact: control %.3f, hamstring %.3f, hyperreflexia %.3f"
      % (rows["control, unlesioned"]["knee_ic_mean"], m["knee_ic_mean"], h["knee_ic_mean"]))

io.open(os.path.join(P, "HAMCTRL_r600.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "HAMCTRL_r600",
 "why": ("The duration control of section 3.3 uses plantarflexor-weakness lineages, a manipulation of "
         "the same muscle group whose overactivity is claimed to drive the effect. This is a falling "
         "control whose lesion is independent of the plantarflexors: hamstring force scaled to 0.60 "
         "on the same model and controller."),
 "lesion": "hamstrings max isometric force scaled to 0.60; the hamstrings cross hip and knee, not the ankle",
 "not_duration_matched": ("these runs end between 6.46 and 9.03 s and so fail criterion G, which "
                          "requires 9.73 s. They fall earlier than every hyperreflexia run, which "
                          "makes the comparison asymmetric in the direction that favours the "
                          "objection rather than the answer."),
 "measurement": "peak swing dorsiflexion over the cycles completed before each run ended, corpus conventions otherwise",
 "artefact_floor_deg": ART,
 "groups": rows,
 "disjoint_from_hyperreflexia": bool(gap > 0),
 "gap_deg": gap,
}, indent=1, ensure_ascii=False))
print("\n-> HAMCTRL_r600.json")
