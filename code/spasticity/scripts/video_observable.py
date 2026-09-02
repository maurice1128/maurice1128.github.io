"""Video-observable discriminators: EVENTS and TIMING, not sub-degree magnitudes.

WHY THIS FRAMING.
The intended use is mass screening from video, so electrodes are out and the measure must survive
a camera. Five previous features failed, and they failed for a shared reason: all were magnitudes
of a joint angle, and the surviving margins (1-2 deg) sit far below the reported post-stroke ankle
MDC of 3.8-11.5 deg. But a camera is bad at sub-degree magnitudes and GOOD at events and their
timing -- when the foot contacts, how fast it goes flat, how consistent the pattern is.

Two candidates, both standard clinical observations, both never tested here, and both predicted to
go in OPPOSITE directions for the two mechanisms:

1. FOOT SLAP / loading response.
   Dorsiflexor weakness: the foot contacts and then drops uncontrolled, because tibialis anterior
   cannot do the eccentric control -- the classic audible foot slap. Fast plantarflexion in early
   stance.
   Plantarflexor spasticity: the plantarflexors are ALREADY active at contact, so the foot is
   pointed down before it lands (toe/forefoot first) and there is no slap to control.
   Measured as: peak plantarflexion velocity in the first 15% of stance, and time from initial
   contact to foot-flat.

2. STRIDE-TO-STRIDE VARIABILITY.
   A velocity-dependent reflex is a THRESHOLD process: it fires only when stretch velocity exceeds
   threshold, so on strides that happen to be slower it may not fire at all -> the gait should be
   more variable stride to stride.
   Weakness is a constant capacity reduction with no threshold -> comparatively regular.
   Measured as coefficient of variation of per-cycle ankle ROM and of cycle time.

Both are computed per limb. Both are ratios or timings rather than absolute angles, so a
systematic per-limb angular bias (the dominant markerless error mode at the ankle) largely cancels.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import col, grf_vertical, heel_strikes, load_sto  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
LOADING = 0.15      # fraction of the cycle treated as loading response

GROUPS = {
    "HEALTHY": ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"],
    "PAR20": ["DPAR20_s1", "DPAR20_s2", "DPAR20_s3"],
    "PAR40": ["DPAR40_s1", "DPAR40_s2", "DPAR40_s3"],
    "PAR60": ["DPAR60_s1", "DPAR60_s2", "DPAR60_s3"],
    "SPAS005": ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"],
    "SPAS01": ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"],
    "MIX20S01": ["MMIX20S01_s1", "MMIX20S01_s2"],
}


def newest_sto(tag):
    ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)]
    if not ds:
        return None
    d = max(ds, key=os.path.getmtime)
    s = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
    return max(s, key=os.path.getmtime) if s else None


def video_features(path, side="l", settle=1.0):
    cols, d = load_sto(path)
    if d.size == 0:
        return None
    t = d[:, 0]
    ang = col(cols, d, "ankle_angle_%s" % side)
    grf, thr = grf_vertical(cols, d, side)
    if ang is None or grf is None:
        return None
    ang = np.degrees(ang)
    vel = np.gradient(ang, t)
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    if len(hs) < 4:
        return None
    cycles = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
    if len(cycles) < 3:
        return None

    slap, t_flat, roms, ctimes, contact_ang = [], [], [], [], []
    for a, b in cycles:
        k = a + max(2, int(LOADING * (b - a)))
        seg = vel[a:k]
        # foot slap = fastest PLANTARflexion (negative velocity) just after contact
        slap.append(float(-np.min(seg)) if seg.size else np.nan)
        # time from contact until the ankle stops plantarflexing (foot flat)
        idx = np.where(vel[a:b] >= 0)[0]
        t_flat.append(float(t[a + idx[0]] - t[a]) if idx.size else float(t[b] - t[a]))
        roms.append(float(np.ptp(ang[a:b])))
        ctimes.append(float(t[b] - t[a]))
        contact_ang.append(float(ang[a]))

    def cv(x):
        x = np.asarray(x, float)
        m = np.mean(x)
        return float(np.std(x, ddof=1) / abs(m)) if len(x) > 1 and abs(m) > 1e-9 else np.nan

    return {
        "n_cycles": len(cycles),
        "foot_slap_vel": float(np.nanmean(slap)),      # deg/s of plantarflexion after contact
        "time_to_flat": float(np.nanmean(t_flat)),     # s
        "contact_angle": float(np.mean(contact_ang)),  # + = dorsiflexed at contact
        "cv_rom": cv(roms),                            # stride-to-stride variability
        "cv_cycle_time": cv(ctimes),
    }


def main():
    res = {}
    keys = ["foot_slap_vel", "time_to_flat", "contact_angle", "cv_rom", "cv_cycle_time"]
    print("%-10s %-4s %-11s %-11s %-11s %-10s %-10s" %
          ("group", "n", "slap(deg/s)", "t_flat(s)", "contact(deg)", "CV_rom", "CV_time"))
    for g, tags in GROUPS.items():
        rows = []
        for t in tags:
            p = newest_sto(t)
            if not p:
                continue
            f = video_features(p, "l")
            if f:
                rows.append(f)
                res["%s/%s" % (g, t)] = f
        if not rows:
            print("%-10s  --" % g)
            continue
        v = {k: (float(np.nanmean([r[k] for r in rows])),
                 float(np.nanstd([r[k] for r in rows], ddof=1)) if len(rows) > 1 else 0.0)
             for k in keys}
        print("%-10s %-4d %6.1f±%-4.1f %.3f±%.3f %6.2f±%-4.2f %.3f±%.3f %.3f±%.3f"
              % (g, len(rows), v["foot_slap_vel"][0], v["foot_slap_vel"][1],
                 v["time_to_flat"][0], v["time_to_flat"][1],
                 v["contact_angle"][0], v["contact_angle"][1],
                 v["cv_rom"][0], v["cv_rom"][1],
                 v["cv_cycle_time"][0], v["cv_cycle_time"][1]))

    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "scone_video_features.json"), "w"), indent=2)

    print("\n--- separation check (spastic incl. mixed vs healthy+weakness) ---")
    for k in keys:
        sp = [v[k] for kk, v in res.items()
              if kk.split("/")[0].startswith(("SPAS", "MIX")) and np.isfinite(v[k])]
        wk = [v[k] for kk, v in res.items()
              if kk.split("/")[0].startswith(("HEALTHY", "PAR")) and np.isfinite(v[k])]
        if not sp or not wk:
            continue
        hi = min(sp) > max(wk)
        lo = max(sp) < min(wk)
        tag = ("**SEPARATED** spastic HIGHER (gap %+.3f)" % (min(sp) - max(wk))) if hi else \
              ("**SEPARATED** spastic LOWER (gap %+.3f)" % (min(wk) - max(sp))) if lo else "overlap"
        print("  %-16s spastic %8.3f-%-8.3f | non-spastic %8.3f-%-8.3f  %s"
              % (k, min(sp), max(sp), min(wk), max(wk), tag))


if __name__ == "__main__":
    main()
