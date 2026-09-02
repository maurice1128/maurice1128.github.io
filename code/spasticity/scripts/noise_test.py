"""Does the 1.25 deg inter-limb asymmetry margin survive realistic mocap measurement noise?

This is the test the manuscript admits was never run ("nothing here says it survives measurement
error"). Published anchors: post-stroke ankle-angle MDC 3.8-11.5 deg; Theia3D markerless RMSD
0.96-3.71 deg (SEM 0.91-3.25); OpenCap sagittal ankle < 11 deg RMSE; markerless validity is
POOREST at the ankle. So the relevant noise levels are ~1.5 deg (best-case multi-camera
markerless), 2.5 deg (realistic markerless), 3.5 deg (2D video / conservative).

Method: add zero-mean Gaussian noise per FRAME to the ankle-angle waveform of each limb
independently (independent noise is the right model for pose-estimation jitter; systematic
per-subject bias would partly cancel in a between-limb difference, so this is neither the
best nor worst case), recompute per-cycle ROM, recompute affected-minus-intact asymmetry,
and ask how often spastic and weakness are still separated. Also averages over N strides,
since averaging is the obvious clinical mitigation.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import col, grf_vertical, heel_strikes, load_sto  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
NOISE = [0.0, 1.5, 2.5, 3.5]
NBOOT = 100   # 400 was needlessly slow; 100 draws already pins these percentages to ~5%

SPAS = ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4",
        "SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"]
WEAK = ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3",
        "DPAR20_s1", "DPAR20_s2", "DPAR20_s3",
        "DPAR40_s1", "DPAR40_s2", "DPAR40_s3",
        "DPAR60_s1", "DPAR60_s2", "DPAR60_s3"]


def newest_sto(tag):
    """Resolve the .sto at call time and verify it still exists.

    Replay scripts delete stale .sto files before regenerating them, so a path resolved once
    can vanish mid-run. Resolve late and skip anything missing rather than crashing.
    """
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)]
    if not ds:
        return None
    d = max(ds, key=os.path.getmtime)
    s = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
    if not s:
        return None
    p = max(s, key=os.path.getmtime)
    return p if os.path.exists(p) else None


def cycle_roms(path, side, settle=1.0):
    """Per-cycle ankle ROM plus the raw waveform, so noise can be injected before ROM is taken."""
    cols, d = load_sto(path)
    t = d[:, 0]
    ang = col(cols, d, "ankle_angle_%s" % side)
    if ang is None:
        return None, None
    ang = np.degrees(ang)
    grf, thr = grf_vertical(cols, d, side)
    if grf is None:
        return None, None
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    if len(hs) < 3:
        return None, None
    return ang, list(zip(hs[:-1], hs[1:]))


#: Waveform cache. Re-reading the .sto inside the bootstrap loop meant ~64,000 file loads
#: (400 draws x 4 noise levels x 2 stride settings x 20 runs) and the script never finished.
#: Load each trial once, then add fresh noise to the cached array per draw.
_CACHE = {}


def load_once(path):
    if path in _CACHE:
        return _CACHE[path]
    if not path or not os.path.exists(path):
        _CACHE[path] = None
        return None
    try:
        d = {}
        for side in ("l", "r"):
            ang, cyc = cycle_roms(path, side)
            if ang is None:
                _CACHE[path] = None
                return None
            d[side] = (ang, cyc)
    except (OSError, IOError):
        _CACHE[path] = None
        return None
    _CACHE[path] = d
    return d


def asym_with_noise(path, sd, rng, n_strides=None):
    d = load_once(path)
    if d is None:
        return None
    out = {}
    for side in ("l", "r"):
        ang, cyc = d[side]
        a = ang + rng.normal(0.0, sd, size=ang.shape) if sd > 0 else ang
        roms = [float(a[i:j].max() - a[i:j].min()) for i, j in cyc]
        if n_strides:
            roms = roms[:n_strides]
        out[side] = float(np.mean(roms))
    return out["l"] - out["r"]


def main():
    rng = np.random.default_rng(0)
    paths = {}
    for t in SPAS + WEAK:
        p = newest_sto(t)
        if p:
            paths[t] = p
    for i, t in enumerate(list(paths)):
        load_once(paths[t])
        print("  cached %d/%d" % (i + 1, len(paths)), flush=True)
    sp = [t for t in SPAS if t in paths]
    wk = [t for t in WEAK if t in paths]
    print("spastic n=%d  weakness n=%d" % (len(sp), len(wk)))

    print("\n%-8s %-10s %-22s %-22s %-12s" %
          ("noise", "strides", "spastic asym", "weakness asym", "separated?"))
    results = {}
    for sd in NOISE:
        for nstr in (None, 10):
            sep = 0
            gaps = []
            for _ in range(NBOOT if sd > 0 else 1):
                sv = [asym_with_noise(paths[t], sd, rng, nstr) for t in sp]
                wv = [asym_with_noise(paths[t], sd, rng, nstr) for t in wk]
                sv = [x for x in sv if x is not None]
                wv = [x for x in wv if x is not None]
                if not sv or not wv:
                    continue
                gaps.append(min(wv) - max(sv))
                if max(sv) < min(wv):
                    sep += 1
            n = NBOOT if sd > 0 else 1
            pct = 100.0 * sep / max(n, 1)
            results["sd%.1f_n%s" % (sd, nstr or "all")] = pct
            print("%-8.1f %-10s %-22s %-22s %5.1f%% separated (median gap %+.2f deg)"
                  % (sd, nstr or "all",
                     "%.2f..%.2f" % (min(sv), max(sv)),
                     "%.2f..%.2f" % (min(wv), max(wv)),
                     pct, float(np.median(gaps)) if gaps else float("nan")))
    json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "noise_test_results.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
