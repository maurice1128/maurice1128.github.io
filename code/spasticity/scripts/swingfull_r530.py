# -*- coding: utf-8 -*-
"""r530: put peak swing dorsiflexion through every gate knee-at-contact was put through.

The endpoint has so far passed rule 1 (seed noise floor), rule 3 (stationarity) and the
survival-matched test. That is three of the checks the primary endpoint carries. Promoting it on
three would repeat the mistake this project has made before. This runs the rest, with the corpus
conventions unchanged: SETTLE 1.00 s, T1 9.73 s, cycles wholly inside, last kept cycle dropped, >= 5
required, contact = rising edge of the leg's vertical GRF through 0.05, family (not cell) as the
unit of analysis.

Gates run here:
  0  protocol artefact floor, by the SHAM_READOUT_r406 chaining protocol
  1  within-cell seed SD, cell-level gap, multiple of the artefact floor
  2  within-dose duration control
  3  within-window stationarity, per arm
  4  displacement from control against the artefact floor
  5  unlesioned-side control
  6  family level: Welch interval, exhaustive permutation of all C(11,5) relabellings, LOFO
  7  sensitivity to the admissibility gate
  8  speed control
"""
import glob, io, itertools, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

CTRL = [("R151C", None)]
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]
SHAM = {"spastic KV0.100": ["R151S", "R400SPgc1", "R400SPgc2", "R400SPgc3"],
        "weak x0.80": ["R151W", "R400WKc1", "R400WKc2", "R400WKc3"]}


def load(fam, sd, t1=T1):
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
    out = {"t_end": float(t[-1])}
    for side in ("l", "r"):
        grf, thr = S.grf_vertical(c, dat, side)
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= t1]
        w = w[:-1] if len(w) >= 2 else w
        if side == "l":
            out["n_cycles"] = len(w)
            if float(t[-1]) < t1 or len(w) < 5:
                out["admitted"] = False
                return out
            out["admitted"] = True
        if not w:
            continue
        an = np.degrees(S.col(c, dat, "ankle_angle_%s" % side))
        on = grf > thr
        pk = []
        for a, b in w:
            idx = np.where(~on[a:b])[0]
            if idx.size:
                pk.append(float(np.max(an[a:b][idx])))
        out["peak_" + side] = float(np.mean(pk)) if pk else None
        if side == "l":
            out["per_cycle"] = pk
    try:
        px = S.col(c, dat, "pelvis_tx")
        a0, b0 = w[0][0], w[-1][1]
        out["speed"] = float((px[b0] - px[a0]) / (t[b0] - t[a0]))
    except Exception:
        out["speed"] = None
    return out


def famcells(fam, t1=T1):
    v = []
    for sd in SEEDS:
        r = load(fam, sd, t1)
        if r and r.get("admitted") and r.get("peak_l") is not None:
            r["fam"], r["seed"] = fam, sd
            v.append(r)
    return v


print("loading corpus ...")
CELLS = {f: famcells(f) for f, _ in CTRL + HY + WK}
for k in SHAM:
    for f in SHAM[k]:
        if f not in CELLS:
            CELLS[f] = famcells(f)
for f, _ in CTRL + HY + WK:
    print("   %-12s n=%d" % (f, len(CELLS[f])))

hy = [c for f, _ in HY for c in CELLS[f]]
wk = [c for f, _ in WK for c in CELLS[f]]
ct = CELLS["R151C"]
V = lambda s: [c["peak_l"] for c in s]
R = []


def rep(tag, ok, txt):
    R.append({"gate": tag, "pass": bool(ok), "detail": txt})
    print("  [%s] %-34s %s" % ("PASS" if ok else "FAIL", tag, txt))


print("\n=== gate 0: protocol artefact floor (SHAM_READOUT_r406 protocol) ===")
shifts = {}
for name, chain in SHAM.items():
    base = np.mean(V(CELLS[chain[0]])) if CELLS[chain[0]] else None
    row = {}
    for f in chain:
        v = V(CELLS[f])
        row[f] = {"n": len(v), "mean": float(np.mean(v)) if v else None,
                  "shift": float(np.mean(v) - base) if v and base is not None else None}
        print("   %-16s %-14s n=%d  mean %8.3f  shift %+7.3f"
              % (name, f, len(v), np.mean(v) if v else float("nan"),
                 (np.mean(v) - base) if v and base is not None else float("nan")))
    shifts[name] = row
ART = max(abs(r["shift"]) for row in shifts.values() for r in row.values()
          if r["shift"] is not None)
print("   largest protocol shift on this endpoint: %.4f deg   (knee-at-contact: 0.5860)" % ART)

print("\n=== gate 1: seed noise floor and cell-level gap ===")
sds = [float(np.std(V(CELLS[f]), ddof=1)) for f, _ in HY + WK if len(CELLS[f]) >= 2]
SEED_SD = float(np.mean(sds))
gap = min(V(wk)) - max(V(hy))
rep("1 seed floor / cell gap", gap > 0,
    "gap %+.3f deg = %.1f seed SD (%.3f) = %.2f x artefact (%.3f)"
    % (gap, gap / SEED_SD, SEED_SD, gap / ART, ART))

print("\n=== gate 2: within-dose duration control ===")
sl = []
for f, _ in HY + WK:
    v = CELLS[f]
    if len(v) >= 3 and len(set(round(c["t_end"], 3) for c in v)) > 1:
        sl.append(float(np.polyfit([c["t_end"] for c in v], [c["peak_l"] for c in v], 1)[0]))
slope = float(np.mean(sl)) if sl else 0.0
dt = float(np.mean([c["t_end"] for c in hy]) - np.mean([c["t_end"] for c in wk]))
prop = slope * dt
eff = float(np.mean(V(wk)) - np.mean(V(hy)))
rep("2 duration control", abs(prop) < 0.5 * abs(eff),
    "within-dose slope %+.4f deg/s over an arm gap of %+.2f s propagates %+.3f deg = %.1f%% of the "
    "%.3f deg effect (bar: 50%%)" % (slope, dt, prop, 100 * abs(prop / eff), eff))

print("\n=== gate 3: within-window stationarity ===")
per = [float(np.mean([c["per_cycle"][i] for c in wk if len(c["per_cycle"]) > i])
             - np.mean([c["per_cycle"][i] for c in hy if len(c["per_cycle"]) > i]))
       for i in range(5)]
spread = max(per) - min(per)
onesign = all(x > 0 for x in per) or all(x < 0 for x in per)
rep("3 stationarity", onesign and spread < abs(np.mean(per)),
    "per-cycle %s ; one sign %s ; spread %.3f = %.2f x window mean"
    % (" ".join("%+.3f" % x for x in per), onesign, spread, spread / abs(np.mean(per))))

print("\n=== gate 4: displacement from control ===")
dc_w = float(np.mean(V(wk)) - np.mean(V(ct)))
dc_h = float(np.mean(V(hy)) - np.mean(V(ct)))
rep("4 displacement (hyperreflexia)", abs(dc_h) > ART,
    "%+.3f deg = %.2f x artefact" % (dc_h, abs(dc_h) / ART))
rep("4 displacement (weakness)", abs(dc_w) > ART,
    "%+.3f deg = %.2f x artefact" % (dc_w, abs(dc_w) / ART))
# r534 correction: a magnitude test alone passes a readout on which BOTH arms move the same way,
# which is not an apportionment. SWEEP_r532 scores the sign too and is the convention. Both arms
# here are displaced from control in the SAME direction, 21x apart in size, so the endpoint grades
# how severe the equinus is and cannot say which lesion produced it.
rep("4 two-sided (sign reversal)", dc_h * dc_w < 0,
    "weakness %+.3f and hyperreflexia %+.3f are on the %s side of control"
    % (dc_w, dc_h, "opposite" if dc_h * dc_w < 0 else "SAME"))

print("\n=== gate 5: unlesioned-side control ===")
rh = [c["peak_r"] for c in hy if c.get("peak_r") is not None]
rw = [c["peak_r"] for c in wk if c.get("peak_r") is not None]
rc = [c["peak_r"] for c in ct if c.get("peak_r") is not None]
r_eff = float(np.mean(rw) - np.mean(rh)) if rh and rw else float("nan")
share = abs(r_eff / eff) if eff else float("nan")
byrung = {}
for f, kv in HY:
    v = [c["peak_r"] for c in CELLS[f] if c.get("peak_r") is not None]
    if v:
        byrung[kv] = float(np.mean(v) - np.mean(rc))
rep("5 unlesioned side", share < 0.35,
    "right ankle arm difference %+.3f deg = %.1f%% of the lesioned side (knee carried 35.5%%); "
    "displacement from control by gain %s"
    % (r_eff, 100 * share, " ".join("%.3f:%+.2f" % (k, v) for k, v in sorted(byrung.items()))))

print("\n=== gate 6: family level ===")
fh = [float(np.mean(V(CELLS[f]))) for f, _ in HY if CELLS[f]]
fw = [float(np.mean(V(CELLS[f]))) for f, _ in WK if CELLS[f]]
mh, mw = float(np.mean(fh)), float(np.mean(fw))
vh, vw = float(np.var(fh, ddof=1)), float(np.var(fw, ddof=1))
se = math.sqrt(vh / len(fh) + vw / len(fw))
df = (vh / len(fh) + vw / len(fw)) ** 2 / ((vh / len(fh)) ** 2 / (len(fh) - 1)
                                           + (vw / len(fw)) ** 2 / (len(fw) - 1))
d = mw - mh
def _t_crit(df, p=0.975):
    """t(p, df) by bisection on the Student CDF.

    Until r573 this was a two-value lookup, tcrit = 2.776 if df < 5 else 2.571. Those are t at df 4
    and df 5 and wrong at every df between, including the df 4.117 this analysis returns, where the
    lookup inflates the interval by about half a per cent. See WELCH_CORRECTION_r573.json."""
    from math import lgamma, log, exp

    def _bcf(a, b, x):
        EPS, FP = 3e-16, 1e-300
        qab, qap, qam = a + b, a + 1.0, a - 1.0
        c, d = 1.0, 1.0 - qab * x / qap
        d = 1.0 / (d if abs(d) > FP else FP)
        h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d; c = 1.0 + aa / c
            d = 1.0 / (d if abs(d) > FP else FP); c = c if abs(c) > FP else FP
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d; c = 1.0 + aa / c
            d = 1.0 / (d if abs(d) > FP else FP); c = c if abs(c) > FP else FP
            de = d * c; h *= de
            if abs(de - 1.0) < EPS:
                break
        return h

    def _cdf(t):
        x = df / (df + t * t)
        a, b = df / 2.0, 0.5
        if x < (a + 1.0) / (a + b + 2.0):
            ib = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1.0 - x)) * _bcf(a, b, x) / a
        else:
            ib = 1.0 - exp(lgamma(a + b) - lgamma(a) - lgamma(b) + b * log(1.0 - x) + a * log(x)) * _bcf(b, a, 1.0 - x) / b
        return 1.0 - 0.5 * ib

    lo, hi = 0.0, 30.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0
tcrit = _t_crit(df)
print("   hyper families %s" % " ".join("%.3f" % x for x in fh))
print("   weak  families %s" % " ".join("%.3f" % x for x in fw))
print("   difference %+.3f deg, 95%% CI approx [%.3f, %.3f], Welch df %.2f"
      % (d, d - tcrit * se, d + tcrit * se, df))
allf = fh + fw
obs = abs(np.mean(fw) - np.mean(fh))
cnt = sum(1 for idx in itertools.combinations(range(len(allf)), len(fh))
          if abs(np.mean([allf[i] for i in range(len(allf)) if i not in idx])
                 - np.mean([allf[i] for i in idx])) >= obs - 1e-12)
tot = math.comb(len(allf), len(fh))
rep("6 exhaustive permutation", cnt == 1, "observed split ranked %d of %d, p = %.4f" % (cnt, tot, cnt / tot))
# LOFO
allc = [(c["peak_l"], "H") for c in hy] + [(c["peak_l"], "W") for c in wk]
fams = [(f, "H") for f, _ in HY] + [(f, "W") for f, _ in WK]
ok = 0
for f, lab in fams:
    held = [(c["peak_l"], lab) for c in CELLS[f]]
    rest = [(c["peak_l"], "H") for g, _ in HY if g != f for c in CELLS[g]] + \
           [(c["peak_l"], "W") for g, _ in WK if g != f for c in CELLS[g]]
    th = 0.5 * (np.mean([v for v, l in rest if l == "H"]) + np.mean([v for v, l in rest if l == "W"]))
    ok += sum(1 for v, l in held if (("H" if v < th else "W") == l))
base = max(len(hy), len(wk)) / float(len(hy) + len(wk))
rep("6 leave-one-family-out", ok / len(allc) > base,
    "%d of %d = %.1f%% against a %.1f%% majority baseline" % (ok, len(allc), 100 * ok / len(allc), 100 * base))

print("\n=== gate 7: sensitivity to the admissibility gate ===")
gs = {}
for t1 in (9.73, 10.5, 11.5, 12.5, 13.0):
    h = [c["peak_l"] for f, _ in HY for c in famcells(f, t1)]
    w = [c["peak_l"] for f, _ in WK for c in famcells(f, t1)]
    gs[t1] = (min(w) - max(h), len(h), len(w)) if h and w else (None, len(h), len(w))
    print("   gate %.2f s : gap %+.3f  (hyper %d, weak %d)"
          % (t1, gs[t1][0] if gs[t1][0] is not None else float("nan"), len(h), len(w)))
rep("7 gate sensitivity", all(v[0] is not None and v[0] > 0 for v in gs.values()),
    "cell-level non-overlap holds at every gate tested to 13.0 s")

print("\n=== gate 8: speed control ===")
sh = [c["speed"] for c in hy if c.get("speed") is not None]
sw = [c["speed"] for c in wk if c.get("speed") is not None]
sp_sl = []
for f, _ in HY + WK:
    v = [c for c in CELLS[f] if c.get("speed") is not None]
    if len(v) >= 3:
        sp_sl.append(float(np.polyfit([c["speed"] for c in v], [c["peak_l"] for c in v], 1)[0]))
sps = float(np.mean(sp_sl)) if sp_sl else 0.0
sgap = float(np.mean(sh) - np.mean(sw)) if sh and sw else 0.0
sprop = sps * sgap
rep("8 speed control", abs(sprop) < 0.5 * abs(eff),
    "within-dose slope %+.3f deg/(m/s) over a speed gap of %+.4f m/s propagates %+.3f deg = %.1f%% "
    "of the effect" % (sps, sgap, sprop, 100 * abs(sprop / eff)))

npass = sum(1 for r in R if r["pass"])
print("\n=== %d of %d gates pass ===" % (npass, len(R)))
for r in R:
    if not r["pass"]:
        print("   FAILED: %s -- %s" % (r["gate"], r["detail"]))

dep = {
 "id": "SWINGFULL_r530",
 "why": ("The endpoint had passed three of the checks the primary endpoint carries. Promoting it on "
         "three would repeat a mistake this project has made. This runs the rest under unchanged "
         "corpus conventions."),
 "artefact_floor_deg": ART, "artefact_floor_knee_for_comparison_deg": 0.5860145801831838,
 "sham_chains": shifts,
 "seed_SD_deg": SEED_SD, "cell_gap_deg": gap,
 "arm_effect_deg": eff,
 "means_deg": {"control": float(np.mean(V(ct))), "weakness": float(np.mean(V(wk))),
               "hyperreflexia": float(np.mean(V(hy)))},
 "family_means_deg": {"hyperreflexia": fh, "weakness": fw},
 "welch": {"difference_deg": d, "se": se, "df": df,
           "ci95": [d - tcrit * se, d + tcrit * se]},
 "permutation": {"rank": cnt, "total": tot, "p": cnt / tot},
 "lofo": {"correct": ok, "n": len(allc), "accuracy": ok / len(allc), "baseline": base},
 "gate_sensitivity": {str(k): {"gap_deg": v[0], "n_hyper": v[1], "n_weak": v[2]} for k, v in gs.items()},
 "gates": R,
 "n_pass": npass, "n_gates": len(R),
}
io.open(os.path.join(P, "SWINGFULL_r530.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> SWINGFULL_r530.json")
