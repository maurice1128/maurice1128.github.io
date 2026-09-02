"""Does the foot-slap discriminator survive VIDEO-grade measurement noise?

This is the gate that matters for the intended use. The measure is a peak angular VELOCITY in
early stance, obtained by differentiating the ankle angle -- and differentiation amplifies noise,
so a feature can look excellent in clean simulation and be unusable on video. Published anchors:
post-stroke ankle-angle MDC 3.8-11.5 deg; Theia3D markerless RMSD 0.96-3.71 deg; OpenCap sagittal
ankle < 11 deg RMSE; markerless validity is POOREST at the ankle.

Two things are tested, because they fail differently:
  RAW            peak plantarflexion velocity on the affected limb (absolute, deg/s)
  RATIO          affected / intact peak slap velocity -- a within-subject contrast, so a
                 systematic per-limb angular scale error partly cancels

Noise model. Independent per-frame Gaussian noise is the standard optimistic case. Real markerless
error is temporally CORRELATED (a wobbling segment estimate drifts over several frames) and
differentiating correlated noise is far less catastrophic than differentiating white noise -- but
correlated noise also carries a per-limb bias that does NOT cancel in a between-limb ratio. Both
are therefore simulated: white noise, and an AR(1)-correlated variant with a per-limb offset.

A practical mitigation is also tested: low-pass filtering the angle before differentiating, which
is what any real pipeline does. That trades noise for attenuation of the very peak being measured,
so the question is whether a usable margin survives the trade.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import col, grf_vertical, heel_strikes, load_sto  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
LOADING = 0.15
NOISE = [0.0, 1.5, 2.5, 3.5]
NBOOT = 60
FC = 6.0            # low-pass cutoff, Hz -- typical for clinical gait kinematics

SPAS = ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4",
        "SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4",
        "MMIX20S01_s1", "MMIX20S01_s2"]
NONSPAS = ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3",
           "DPAR20_s1", "DPAR20_s2", "DPAR20_s3",
           "DPAR40_s1", "DPAR40_s2", "DPAR40_s3",
           "DPAR60_s1", "DPAR60_s2", "DPAR60_s3"]

_CACHE = {}


def newest_sto(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)]
    if not ds:
        return None
    d = max(ds, key=os.path.getmtime)
    s = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
    return max(s, key=os.path.getmtime) if s else None


def load_trial(tag):
    """Cache angle waveform + loading windows for both limbs (one .sto read per trial)."""
    if tag in _CACHE:
        return _CACHE[tag]
    p = newest_sto(tag)
    if not p:
        _CACHE[tag] = None
        return None
    cols, d = load_sto(p)
    if d.size == 0:
        _CACHE[tag] = None
        return None
    t = d[:, 0]
    out = {"t": t}
    for side in ("l", "r"):
        ang = col(cols, d, "ankle_angle_%s" % side)
        grf, thr = grf_vertical(cols, d, side)
        if ang is None or grf is None:
            _CACHE[tag] = None
            return None
        hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
        if len(hs) < 4:
            _CACHE[tag] = None
            return None
        cyc = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
        wins = [(a, a + max(2, int(LOADING * (b - a)))) for a, b in cyc]
        out[side] = (np.degrees(ang), wins)
    _CACHE[tag] = out
    return out


def lowpass(x, dt, fc=FC):
    """Zero-phase 2nd-order Butterworth-equivalent via a simple forward-backward EMA."""
    if fc is None or fc <= 0:
        return x
    a = np.exp(-2.0 * np.pi * fc * dt)
    y = np.empty_like(x)
    acc = x[0]
    for i in range(len(x)):
        acc = a * acc + (1 - a) * x[i]
        y[i] = acc
    acc = y[-1]
    for i in range(len(x) - 1, -1, -1):
        acc = a * acc + (1 - a) * y[i]
        y[i] = acc
    return y


def slap(tag, sd, rng, correlated=False, filt=False):
    tr = load_trial(tag)
    if tr is None:
        return None, None
    t = tr["t"]
    dt = float(np.median(np.diff(t)))
    vals = {}
    for side in ("l", "r"):
        ang, wins = tr[side]
        a = ang
        if sd > 0:
            if correlated:
                # AR(1) noise + a fixed per-limb offset (the markerless failure mode that
                # does NOT cancel in a between-limb ratio)
                rho = 0.9
                e = rng.normal(0.0, sd * np.sqrt(1 - rho ** 2), size=ang.shape)
                n = np.empty_like(e)
                n[0] = rng.normal(0.0, sd)
                for i in range(1, len(e)):
                    n[i] = rho * n[i - 1] + e[i]
                n = n + rng.normal(0.0, sd * 0.5)
                a = ang + n
            else:
                a = ang + rng.normal(0.0, sd, size=ang.shape)
        if filt:
            a = lowpass(a, dt)
        v = np.gradient(a, t)
        vals[side] = float(np.mean([-np.min(v[i:j]) for i, j in wins]))
    return vals["l"], (vals["l"] / vals["r"] if vals["r"] > 1e-9 else np.nan)


def main():
    rng = np.random.default_rng(0)
    for tag in SPAS + NONSPAS:
        load_trial(tag)
    sp = [t for t in SPAS if _CACHE.get(t)]
    ns = [t for t in NONSPAS if _CACHE.get(t)]
    print("spastic n=%d  non-spastic n=%d\n" % (len(sp), len(ns)))

    res = {}
    for corr in (False, True):
        for filt in (False, True):
            label = "%s%s" % ("AR(1)+bias" if corr else "white",
                              " +6Hz filter" if filt else "")
            print("=== %s ===" % label)
            print("  %-7s %-26s %-26s" % ("noise", "RAW slap separated", "RATIO separated"))
            for sd in NOISE:
                n = NBOOT if sd > 0 else 1
                sep_raw = sep_rat = 0
                for _ in range(n):
                    rs = [slap(t, sd, rng, corr, filt) for t in sp]
                    rn = [slap(t, sd, rng, corr, filt) for t in ns]
                    a_s = [x[0] for x in rs if x[0] is not None]
                    a_n = [x[0] for x in rn if x[0] is not None]
                    r_s = [x[1] for x in rs if x[1] is not None and np.isfinite(x[1])]
                    r_n = [x[1] for x in rn if x[1] is not None and np.isfinite(x[1])]
                    if a_s and a_n and max(a_s) < min(a_n):
                        sep_raw += 1
                    if r_s and r_n and max(r_s) < min(r_n):
                        sep_rat += 1
                res["%s|sd%.1f" % (label, sd)] = {"raw": 100.0 * sep_raw / n,
                                                  "ratio": 100.0 * sep_rat / n}
                print("  %-7.1f %5.1f%%                      %5.1f%%"
                      % (sd, 100.0 * sep_raw / n, 100.0 * sep_rat / n))
            print()
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "slap_noise_results.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
