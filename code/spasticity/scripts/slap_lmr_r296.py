# -*- coding: utf-8 -*-
"""Foot slap, both limbs and their difference, with the duration confound handled.

Two corrections to slap3d_r295.py, both of which matter.

1. IT MEASURED ONLY THE LEFT LIMB. Both lesions are left-sided, so the right limb is an internal
   control and the LEFT-MINUS-RIGHT difference removes anything common to the cell -- gait speed,
   optimiser idiosyncrasy, and a per-subject sensor bias in a real recording. That is the same
   construction that gave hip_flexion_LmR and knee_angle_LmR whatever signal they had.

2. ITS CLINICAL COMPARISON WAS DURATION-CONFOUNDED. The six spastic cells all fall at 13.58-17.85 s
   and all 36 dorsiflexor-weakness cells complete 20.00 s, which is precisely the confound
   CONFOUND_DURATION_r277.json identified and SEPARATION_r280.json showed can masquerade as a type
   effect. So this script splits every comparison by outcome and refuses to pool across it, and it
   picks up the r289 KV 0.0125 / 0.00625 spastic cells, which COMPLETE, as the matched partner for
   the 36 completing dorsiflexor cells.

Reported per cell, per filter (raw / 20 Hz / 6 Hz):
  slap_vel_l, slap_vel_r, slap_vel_LmR   peak plantarflexion velocity in the loading response
  t_flat_l,   t_flat_r,   t_flat_LmR     heel strike to early-stance ankle-angle minimum
  cv_l                                   stride-to-stride CV of slap velocity, left

UNREGISTERED, EXPLORATORY. Read-only. Generates a candidate; does not test one.
"""
import io, os, sys, glob, json, math
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, LOADING = 1.0, 0.15
SEEDS = list(range(101, 107))
ARMS = [("C", "R151C"), ("S", "R151S"), ("W800", "R151W"), ("W870", "R174W870"),
        ("W892", "R174W892"), ("W900", "R169W090"), ("W915", "R174W915"), ("W950", "R169W095")]
DF = ("W800", "W870", "W892", "W900", "W915", "W950")


def butter_lp(x, t, fc):
    if fc is None:
        return np.asarray(x, dtype=float)
    x = np.asarray(x, dtype=float)
    dt = float(np.median(np.diff(t)))
    wc = math.tan(math.pi * fc * dt)
    k1, k2 = math.sqrt(2.0) * wc, wc * wc
    a0 = k2 / (1.0 + k1 + k2); a1, a2 = 2.0 * a0, a0
    b1 = 2.0 * a0 * (1.0 / k2 - 1.0); b2 = 1.0 - (a0 + a1 + a2 + b1)

    def once(v):
        y = np.empty_like(v); y[0] = y[1] = v[0]
        for i in range(2, len(v)):
            y[i] = a0 * v[i] + a1 * v[i-1] + a2 * v[i-2] + b1 * y[i-1] + b2 * y[i-2]
        return y
    return once(once(x)[::-1])[::-1]


def side(cols, dat, t, s, fc):
    """Loading-response slap velocity and time-to-flat for one limb, its own heel strikes."""
    grf, thr = S.grf_vertical(cols, dat, s)
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(a, b) for a, b in zip(idx[:-1], idx[1:]) if t[a] >= SETTLE]
    if len(cyc) < 3:
        return None, None, None
    ang = butter_lp(np.degrees(np.asarray(S.col(cols, dat, "ankle_angle_" + s), dtype=float)), t, fc)
    vel = np.gradient(ang, t)
    sv, tf = [], []
    for a, b in cyc:
        n = max(3, int(LOADING * (b - a)))
        e = min(a + n, b)
        sv.append(float(-np.min(vel[a:e])))
        tf.append(float(t[a + int(np.argmin(ang[a:e]))] - t[a]))
    cv = float(np.std(sv) / np.mean(sv)) if np.mean(sv) else None
    return float(np.mean(sv)), float(np.mean(tf)), cv


def cell(d):
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1])
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    out = {"t_end_s": float(t[-1])}
    out["completes"] = bool(abs(out["t_end_s"] - 20.0) < 1e-9)
    for label, fc in (("raw", None), ("f20", 20.0), ("f6", 6.0)):
        sl, tl, cvl = side(cols, dat, t, "l", fc)
        sr, tr, _ = side(cols, dat, t, "r", fc)
        if sl is None or sr is None:
            return None
        out["slap_l_" + label] = sl
        out["slap_r_" + label] = sr
        out["slap_LmR_" + label] = sl - sr
        out["tflat_l_" + label] = tl
        out["tflat_LmR_" + label] = tl - tr
        out["cv_l_" + label] = cvl
    return out


def find_dir(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    return ds[0] if len(ds) == 1 else None


groups = {}
for key, pref in ARMS:
    for s in SEEDS:
        d = find_dir("%s_s%d" % (pref, s))
        if not d:
            continue
        r = cell(d)
        if r:
            groups.setdefault(key, {})["s%d" % s] = r

for pat, key in (("RUN_WEAKPF_r276_cell*.json", "WPF"), ("RUN_MATCHED20_r289_cell*.json", "S289")):
    for p in sorted(glob.glob(os.path.join(PAPER, pat))):
        dep = json.load(open(p))
        d = os.path.join(RES, dep["result_dir"])
        if not os.path.isdir(d) or not glob.glob(os.path.join(d, "*.par.sto")):
            continue
        r = cell(d)
        if r:
            r["label"] = dep.get("kv", dep.get("f"))
            groups.setdefault(key, {})["c%02d" % dep["cell"]] = r


def vals(key, field, completes=None):
    out = []
    for c in groups.get(key, {}).values():
        if completes is not None and c["completes"] != completes:
            continue
        v = c.get(field)
        if v is not None:
            out.append(v)
    return out


def dfvals(field, completes=None):
    return [v for k in DF for v in vals(k, field, completes)]


def sep(a, b):
    if len(a) < 2 or len(b) < 2:
        return None
    gap = max(min(b) - max(a), min(a) - max(b))
    return {"n_a": len(a), "n_b": len(b), "a": [min(a), max(a)], "b": [min(b), max(b)],
            "a_mean": float(np.mean(a)), "b_mean": float(np.mean(b)),
            "disjoint": bool(gap > 0), "gap": gap}


FIELDS = ["slap_l_raw", "slap_LmR_raw", "tflat_l_raw", "tflat_LmR_raw", "cv_l_raw",
          "slap_l_f20", "slap_LmR_f20", "slap_LmR_f6"]
res = {}
print("=" * 96)
print("CLINICAL PAIR, MATCHED ON COMPLETION: r289 spastic (completes) vs 36 dorsiflexor-weak (completes)")
print("=" * 96)
print("%-16s %8s %8s %22s %22s %10s" % ("feature", "n_spas", "n_weak", "spastic range", "weakDF range", "disjoint"))
for f in FIELDS:
    s = sep(vals("S289", f, True), dfvals(f, True))
    res["matched_completion_" + f] = s
    if not s:
        print("%-16s  not evaluable (r289 still running?)" % f); continue
    print("%-16s %8d %8d %22s %22s %10s" % (
        f, s["n_a"], s["n_b"], "%+.4f .. %+.4f" % tuple(s["a"]), "%+.4f .. %+.4f" % tuple(s["b"]),
        ("YES  gap %+.4f" % s["gap"]) if s["disjoint"] else ""))

print()
print("=" * 96)
print("UNMATCHED, for reference only: R151S spastic (ALL FALL) vs 36 dorsiflexor-weak (ALL COMPLETE)")
print("  duration-confounded by construction -- reported so it is not mistaken for the row above")
print("=" * 96)
for f in FIELDS:
    s = sep(vals("S", f), dfvals(f))
    res["unmatched_" + f] = s
    if not s:
        continue
    print("%-16s %8d %8d %22s %22s %10s" % (
        f, s["n_a"], s["n_b"], "%+.4f .. %+.4f" % tuple(s["a"]), "%+.4f .. %+.4f" % tuple(s["b"]),
        ("YES  gap %+.4f" % s["gap"]) if s["disjoint"] else ""))

out = {"what": "foot slap bilaterally and as left-minus-right, split by outcome",
       "status": "UNREGISTERED, EXPLORATORY; read-only; generates a candidate, does not test one",
       "corrections_to_r295": ["left limb only -> both limbs and LmR",
                               "clinical comparison was duration-confounded -> split by completion"],
       "n_by_group": {k: len(v) for k, v in groups.items()},
       "per_cell": groups, "separations": res}
p = os.path.join(PAPER, "SLAP_LMR_r296.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
