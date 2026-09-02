# -*- coding: utf-8 -*-
"""r546: what does measurement error leave of the three readouts that DO grade weakness?

GRADEALL_r543 found three of the 81 candidates that order the weakness ladder at |rho| >= 0.8 over a
span larger than one clinical measurement error: the ankle at 75, 80 and 90 per cent of the cycle.
CLAIMS_r537 put four readouts through the motion-capture noise model and none of those three was
among them, so the manuscript's statement that grading weakness "survives nowhere" rests on readouts
that do not grade it in the first place. That is a scope error, and it is answerable.

This puts all three through the same noise model, alongside the reported endpoint for comparison, and
asks the question the manuscript leaves open: does the weakness ordering that exists on noise-free
traces survive a gait laboratory?
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEED, N_REP, FS, YAW, KMAX = 20260831, 200, 100, 10, 1
SIGMAS = [0.0, 1.0, 2.0, 3.0]
SEM = 4.9 / (1.96 * math.sqrt(2.0))
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]


def load(fam, sd):
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
    on = grf > thr
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    cy = []
    for a, b in w:
        i = np.where(~on[a:b])[0]
        cy.append({"ank": an[a:b], "dur": float(t[b] - t[a]),
                   "swing": (int(i[0]), int(i[-1])) if i.size else None})
    return cy


def pct(p):
    def f(na, sw, ke):
        return float(na[int(np.clip(round(p / 100.0 * (len(na) - 1)) + ke, 0, len(na) - 1))])
    return f


def swpk(na, sw, ke):
    if sw is None:
        return float("nan")
    a = int(np.clip(sw[0] + ke, 0, len(na) - 2))
    b = int(np.clip(sw[1] + ke, a + 1, len(na) - 1))
    return float(np.max(na[a:b]))


CANDS = [("ankle at 75%", pct(75)), ("ankle at 80%", pct(80)), ("ankle at 90%", pct(90)),
         ("ankle peak in swing", swpk)]

print("loading ...")
D = {}
for f, _ in HY + WK:
    D[f] = [x for x in (load(f, s) for s in range(101, 107)) if x]
    print("   %-12s n=%d" % (f, len(D[f])))


def value(cy, fn, sg, rng):
    out = []
    for c in cy:
        n = max(10, int(round(c["dur"] * FS)))
        g = np.linspace(0, 1, n)
        na = np.interp(g, np.linspace(0, 1, len(c["ank"])), c["ank"]) * math.cos(math.radians(YAW))
        if sg > 0:
            na = na + rng.normal(0, sg, n)
        sw = None
        if c["swing"]:
            s0 = len(c["ank"]) - 1.0
            sw = (int(c["swing"][0] / s0 * (n - 1)), int(c["swing"][1] / s0 * (n - 1)))
        ke = int(rng.integers(-KMAX, KMAX + 1)) if KMAX else 0
        out.append(fn(na, sw, ke))
    v = [x for x in out if not math.isnan(x)]
    return float(np.mean(v)) if v else float("nan")


def spear(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


print("\nweakness ordering inside the pure weakness arm, under the motion-capture model")
print("(100 Hz, yaw 10 deg, event error 1 frame; the bar for a usable span is %.2f deg)\n" % SEM)
print("%-22s %-7s %9s %10s %12s" % ("readout", "sigma", "rho", "span deg", "span > bar"))
res = {}
for nm, fn in CANDS:
    res[nm] = {}
    for sg in SIGMAS:
        rng = np.random.default_rng(SEED)
        reps = 1 if sg == 0 else N_REP
        rr, ss = [], []
        for _ in range(reps):
            per = {}
            for f, dose in WK:
                v = [value(cy, fn, sg, rng) for cy in D[f]]
                v = [x for x in v if not math.isnan(x)]
                if v:
                    per[dose] = float(np.mean(v))
            if len(per) < 3:
                continue
            ds = sorted(per)
            rr.append(spear(ds, [per[d] for d in ds]))
            ss.append(max(per.values()) - min(per.values()))
        if not rr:
            continue
        res[nm][str(sg)] = {"rho": float(np.mean(rr)), "span": float(np.mean(ss)),
                            "frac_span_above_bar": float(np.mean([x >= SEM for x in ss]))}
        r = res[nm][str(sg)]
        print("%-22s %-7.1f %9.3f %10.3f %12.2f"
              % (nm if sg == 0 else "", sg, r["rho"], r["span"], r["frac_span_above_bar"]))

print("\nat 3 deg of jitter, ranked by |rho|:")
for nm in sorted(res, key=lambda n: -abs(res[n].get("3.0", {}).get("rho", 0))):
    r = res[nm].get("3.0")
    if r:
        print("   %-22s rho %+.3f   span %.3f deg   above the bar in %.0f%% of realisations"
              % (nm, r["rho"], r["span"], 100 * r["frac_span_above_bar"]))

surv = [nm for nm in res if abs(res[nm].get("3.0", {}).get("rho", 0)) >= 0.8
        and res[nm]["3.0"]["span"] >= SEM]
print("\ncandidates still meeting BOTH criteria at 3 deg jitter: %d of %d  %s"
      % (len(surv), len(CANDS), surv or "(none)"))

io.open(os.path.join(P, "WEAKNOISE_r546.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "WEAKNOISE_r546",
 "why": ("CLAIMS_r537 tested four readouts under the noise model and none was among the three that "
         "GRADEALL_r543 found to grade weakness, so the manuscript's 'grading weakness survives "
         "nowhere' rested on readouts that do not grade it. This tests the three that do."),
 "noise_model": {"fs_hz": FS, "yaw_deg": YAW, "event_error_frames": KMAX,
                 "sigmas": SIGMAS, "n_rep": N_REP, "rng_seed": SEED},
 "usable_span_bar_deg": SEM,
 "results": res,
 "still_usable_at_3deg": surv,
}, indent=1, ensure_ascii=False))
print("\n-> WEAKNOISE_r546.json")
