# -*- coding: utf-8 -*-
"""Foot slap on the CURRENT 3D corpus. An EVENT/TIMING feature, not an angle magnitude.

Why this and why now. Seven angle-magnitude features in this project have died the same way:
their between-arm margins (1-2.5 deg) sit below the post-stroke ankle MDC of 3.8-11.5 deg
(VIDEO_DEGRADATION_REGISTRATION.txt). `video_observable.py` proposed the escape -- a camera is
bad at sub-degree magnitudes and good at events and their timing -- and predicted that foot slap
goes in OPPOSITE directions for the two mechanisms:

  dorsiflexor weakness   tibialis anterior cannot control the eccentric drop, so the foot slaps
                         down after contact: LARGE early-stance plantarflexion velocity
  plantarflexor spasticity  the plantarflexors are already active at contact, the foot is pointed
                         down before it lands, and there is nothing left to slap: SMALL velocity

That was computed on the OLD 2D corpus, whose conditions no longer exist. The current 3D corpus
has something that one did not: a PLANTARFLEXOR-weakness arm, so weakness can be tested with the
anatomy held constant as well as against the clinical pair.

`SLAP_CUTOFF_SWEEP_r152.json` also established, on that old corpus, that a 6 Hz low-pass -- the
standard gait-analysis filter -- destroys the feature completely at ZERO noise, while 20-30 Hz
keeps it. This script therefore reports every cell at both cutoffs and unfiltered, so the filter
sensitivity is measured on this corpus rather than carried over.

Measured per left-limb cycle, from `video_observable.py`'s definitions:
  slap_vel   peak PLANTARFLEXION angular velocity of the ankle within the first 15 % of the cycle
             after heel strike, deg/s, reported as a positive number
  t_flat     time from heel strike to the early-stance ankle-angle minimum, seconds

UNREGISTERED, EXPLORATORY. Read-only, nothing re-simulated. This generates a candidate; it does
not test one. Any test of it must be registered separately, before the channel is compared.
"""
import io, os, sys, glob, json, math
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, LOADING = 1.0, 0.15
SEEDS = list(range(101, 107))
ARMS = [("C", "R151C", "control"),
        ("S", "R151S", "spastic PF reflex KV 0.050"),
        ("W800", "R151W", "dorsiflexor weak x0.800"),
        ("W870", "R174W870", "dorsiflexor weak x0.870"),
        ("W892", "R174W892", "dorsiflexor weak x0.892"),
        ("W900", "R169W090", "dorsiflexor weak x0.900"),
        ("W915", "R174W915", "dorsiflexor weak x0.915"),
        ("W950", "R169W095", "dorsiflexor weak x0.950")]


def butter_lp(x, t, fc):
    """Zero-phase 2nd-order Butterworth low-pass, applied forward then backward.
    Written out rather than imported so the script has no scipy dependency."""
    if fc is None:
        return np.asarray(x, dtype=float)
    x = np.asarray(x, dtype=float)
    dt = float(np.median(np.diff(t)))
    wc = math.tan(math.pi * fc * dt)
    k1, k2 = math.sqrt(2.0) * wc, wc * wc
    a0 = k2 / (1.0 + k1 + k2)
    a1, a2 = 2.0 * a0, a0
    b1 = 2.0 * a0 * (1.0 / k2 - 1.0)
    b2 = 1.0 - (a0 + a1 + a2 + b1)

    def once(v):
        y = np.empty_like(v)
        y[0] = y[1] = v[0]
        for i in range(2, len(v)):
            y[i] = a0 * v[i] + a1 * v[i - 1] + a2 * v[i - 2] + b1 * y[i - 1] + b2 * y[i - 2]
        return y

    return once(once(x)[::-1])[::-1]


def cell(d):
    cols, dat = S.load_sto(sorted(glob.glob(os.path.join(d, "*.par.sto")))[-1])
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(idx[k], idx[k + 1]) for k in range(len(idx) - 1) if t[idx[k]] >= SETTLE]
    if len(cyc) < 3:
        return None
    ang_raw = np.degrees(np.asarray(S.col(cols, dat, "ankle_angle_l"), dtype=float))
    out = {"t_end_s": float(t[-1]), "n_cycles": len(cyc)}
    for label, fc in (("raw", None), ("f20", 20.0), ("f6", 6.0)):
        ang = butter_lp(ang_raw, t, fc)
        vel = np.gradient(ang, t)          # deg/s, positive = dorsiflexion
        sv, tf = [], []
        for a, b in cyc:
            n = max(3, int(LOADING * (b - a)))
            seg = slice(a, min(a + n, b))
            # plantarflexion is the negative direction; report its peak as a positive number
            sv.append(float(-np.min(vel[seg])))
            j = int(np.argmin(ang[a:min(a + n, b)]))
            tf.append(float(t[a + j] - t[a]))
        out["slap_vel_%s" % label] = float(np.mean(sv))
        out["t_flat_%s" % label] = float(np.mean(tf))
        out["slap_vel_%s_cv" % label] = float(np.std(sv) / np.mean(sv)) if np.mean(sv) else None
    return out


def find_dir(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)
          and os.path.exists(os.path.join(x, "history.txt"))
          and sum(1 for _ in io.open(os.path.join(x, "history.txt"), errors="replace")) >= 91
          and glob.glob(os.path.join(x, "*.par.sto"))]
    return ds[0] if len(ds) == 1 else None


rows = {}
print("%-7s %-7s %9s %10s %10s %10s %9s" %
      ("arm", "id", "t_end", "slap_raw", "slap_f20", "slap_f6", "t_flat"))
for key, pref, _d in ARMS:
    rows[key] = {}
    for s in SEEDS:
        d = find_dir("%s_s%d" % (pref, s))
        if not d:
            continue
        r = cell(d)
        if not r:
            continue
        rows[key]["s%d" % s] = r
        print("%-7s %-7s %9.3f %10.2f %10.2f %10.2f %9.4f"
              % (key, "s%d" % s, r["t_end_s"], r["slap_vel_raw"], r["slap_vel_f20"],
                 r["slap_vel_f6"], r["t_flat_raw"]), flush=True)

rows["WPF"] = {}
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_WEAKPF_r276_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    if not os.path.isdir(d) or not glob.glob(os.path.join(d, "*.par.sto")):
        continue
    r = cell(d)
    if not r:
        continue
    r["f"] = dep["f"]; r["seed"] = dep["seed"]
    rows["WPF"]["c%02d" % dep["cell"]] = r
    print("%-7s %-7s %9.3f %10.2f %10.2f %10.2f %9.4f"
          % ("WPF", "c%02d" % dep["cell"], r["t_end_s"], r["slap_vel_raw"],
             r["slap_vel_f20"], r["slap_vel_f6"], r["t_flat_raw"]), flush=True)


def summarise(key, field):
    v = [c[field] for c in rows.get(key, {}).values() if c.get(field) is not None]
    return (len(v), float(np.mean(v)), min(v), max(v)) if v else (0, None, None, None)


DF = ("W800", "W870", "W892", "W900", "W915", "W950")
out = {"what": "foot slap on the current 3D corpus; event/timing feature, not an angle magnitude",
       "status": "UNREGISTERED, EXPLORATORY -- generates a candidate, does not test one",
       "definitions": {"slap_vel": "peak plantarflexion angular velocity in the first 15% of the "
                                   "cycle after heel strike, deg/s, positive",
                       "t_flat": "time from heel strike to the early-stance ankle-angle minimum, s",
                       "filters": "raw, 20 Hz and 6 Hz zero-phase 2nd-order Butterworth"},
       "why_both_filters": "SLAP_CUTOFF_SWEEP_r152.json found 6 Hz destroys the feature at zero "
                           "noise on the OLD 2D corpus; measured here rather than carried over",
       "per_cell": rows}
for field in ("slap_vel_raw", "slap_vel_f20", "slap_vel_f6", "t_flat_raw", "slap_vel_raw_cv"):
    g = {}
    for k in ("C", "S", "WPF"):
        n, m, lo, hi = summarise(k, field)
        g[k] = {"n": n, "mean": m, "min": lo, "max": hi}
    dfv = [c[field] for k in DF for c in rows.get(k, {}).values() if c.get(field) is not None]
    g["DF_pooled"] = ({"n": len(dfv), "mean": float(np.mean(dfv)), "min": min(dfv), "max": max(dfv)}
                      if dfv else {"n": 0})
    out.setdefault("summary", {})[field] = g

p = os.path.join(PAPER, "SLAP3D_r295.json")
json.dump(out, io.open(p, "w", encoding="utf-8"), indent=1)

print()
for field in ("slap_vel_raw", "slap_vel_f20", "slap_vel_f6", "t_flat_raw"):
    g = out["summary"][field]
    print("=" * 78)
    print(field)
    for k, lbl in (("C", "control"), ("S", "spastic PF"), ("DF_pooled", "weak DF (clinical pair)"),
                   ("WPF", "weak PF (anatomy-matched)")):
        e = g[k]
        if not e.get("n"):
            print("  %-26s n=0" % lbl); continue
        print("  %-26s n=%-3d mean %10.3f   range %10.3f .. %10.3f"
              % (lbl, e["n"], e["mean"], e["min"], e["max"]))
print("\nwrote %s (%d bytes)" % (p, os.path.getsize(p)))
