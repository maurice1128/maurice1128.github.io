"""Swing-phase plantarflexor co-contraction — the one variable the clinical literature says works.

WHY THIS, AND WHY IT IS DIFFERENT FROM THE FIVE FAILED FEATURES.
All five were KINEMATIC (joint angles and their derivatives) and all were measured in an adapted
gait. Two independent problems killed them: adaptation is a many-to-one map on kinematics, and the
surviving margins (1-2 deg) sit far below the post-stroke ankle MDC (3.8-11.5 deg).

This feature is neither. It is a TIMING/ACTIVATION variable, and it is the only quantity in the
retrieved clinical literature that actually predicted something: in 40 adults undergoing tibial
motor nerve block (Front Neurol 2022, PMC9196860), clinically graded triceps surae spasticity did
NOT predict who improved (OR 1.12, PPV 33 %), whereas soleus spastic co-contraction during
early-mid SWING on dynamic EMG did (OR 4.72). The authors' own reading: the static stretch-reflex
measure fails to capture the dynamic overactivity that matters.

Mechanistically it is also the right place to look. Swing is when the plantarflexors should be
SILENT and the ankle is being dorsiflexed to clear the foot -- i.e. exactly when a velocity-
dependent plantarflexor reflex is provoked, and exactly when a weak dorsiflexor fails. The two
mechanisms predict OPPOSITE abnormalities in the same window:

    spasticity -> soleus/gastroc ACTIVE during swing when they should be quiet  (excess)
    weakness   -> tibialis anterior UNDER-active / saturated during swing        (deficit)

So this reports, per limb and per gait cycle: plantarflexor activation during swing, dorsiflexor
activation during swing, and their ratio. Adaptation can suppress the kinematic consequence of the
reflex while the reflex still fires -- activation may therefore survive where angle does not.

Clinically this needs surface EMG rather than motion capture. That is a real cost, but surface EMG
of soleus/TA is far cheaper and more portable than a gait lab, and it is what the literature
already supports.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import grf_vertical, heel_strikes, load_sto, muscle_signal  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
GEN_CAP = 90
SWING_FROM = 0.62   # fraction of the gait cycle where swing begins (toe-off ~60-62 %)

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


def swing_activations(path, side="l", settle=1.0):
    cols, d = load_sto(path)
    if d.size == 0:
        return None
    t = d[:, 0]
    grf, thr = grf_vertical(cols, d, side)
    if grf is None:
        return None
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    if len(hs) < 3:
        return None
    cycles = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]
    if len(cycles) < 2:
        return None

    sig = {}
    for mus in ("soleus", "gastroc", "tib_ant"):
        a = muscle_signal(cols, d, mus, side, "activation")
        if a is None:
            return None
        sig[mus] = a

    out = {}
    for mus, a in sig.items():
        sw, st = [], []
        for i, j in cycles:
            k = i + int(SWING_FROM * (j - i))
            sw.append(float(np.mean(a[k:j])))
            st.append(float(np.mean(a[i:k])))
        out["%s_swing" % mus] = float(np.mean(sw))
        out["%s_stance" % mus] = float(np.mean(st))
    # the discriminating ratio: plantarflexor drive vs dorsiflexor drive during swing
    pf = 0.5 * (out["soleus_swing"] + out["gastroc_swing"])
    df = out["tib_ant_swing"]
    out["pf_swing"] = pf
    out["pf_df_swing_ratio"] = pf / df if df > 1e-6 else float("nan")
    out["n_cycles"] = len(cycles)
    return out


def main():
    res = {}
    print("%-10s %-4s %-9s %-9s %-9s %-11s" %
          ("group", "n", "soleus_sw", "gastro_sw", "tibant_sw", "PF/DF ratio"))
    for g, tags in GROUPS.items():
        rows = []
        for t in tags:
            p = newest_sto(t)
            if not p:
                continue
            f = swing_activations(p, "l")
            if f:
                rows.append(f)
                res["%s/%s" % (g, t)] = f
        if not rows:
            print("%-10s  --" % g)
            continue

        def m(k):
            v = [r[k] for r in rows]
            return float(np.mean(v)), (float(np.std(v, ddof=1)) if len(v) > 1 else 0.0)
        s_, ss = m("soleus_swing")
        gg, gs = m("gastroc_swing")
        ta, tas = m("tib_ant_swing")
        rt, rts = m("pf_df_swing_ratio")
        print("%-10s %-4d %.3f±%.3f %.3f±%.3f %.3f±%.3f %6.2f±%.2f"
              % (g, len(rows), s_, ss, gg, gs, ta, tas, rt, rts))

    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "scone_swing_cocontraction.json"), "w"), indent=2)

    print("\n--- overlap check: spastic vs non-spastic ---")
    for key in ("soleus_swing", "pf_swing", "pf_df_swing_ratio"):
        sp = [v[key] for k, v in res.items() if k.split("/")[0].startswith("SPAS")]
        wk = [v[key] for k, v in res.items()
              if not k.split("/")[0].startswith(("SPAS", "MIX"))]
        if not sp or not wk:
            continue
        sep = min(sp) > max(wk)
        print("  %-20s spastic %.4f-%.4f | non-spastic %.4f-%.4f  %s"
              % (key, min(sp), max(sp), min(wk), max(wk),
                 "**SEPARATED** (gap %+.4f)" % (min(sp) - max(wk)) if sep else "overlap"))
    mx = [v["pf_df_swing_ratio"] for k, v in res.items() if k.split("/")[0].startswith("MIX")]
    if mx:
        print("  mixed PF/DF ratio: %.2f - %.2f" % (min(mx), max(mx)))


if __name__ == "__main__":
    main()
