"""Spatiotemporal ASYMMETRY features — the measures the reliability literature says are
actually detectable in a clinic.

Why this file exists. Our discriminator was inter-limb ankle ROM asymmetry with a ~1.25 deg
margin. Published minimal detectable change for ankle joint angles in post-stroke gait is
3.8-11.5 deg, and markerless systems are worst at the ankle specifically, so that margin is
3-9x BELOW what can be measured. By contrast, spatiotemporal asymmetry (step length, swing time,
stance time) has reported ICC 0.93-0.98 in chronic stroke and needs only foot-contact timing and
position -- obtainable from 2D sagittal video. So we test whether the SAME conditions separate on
measures that are actually measurable.

Definitions (per side, from vertical GRF and calcaneus position):
  stance_time  : GRF above threshold within a cycle
  swing_time   : cycle_time - stance_time
  step_length  : anterior distance between contralateral heel contacts
  double_support: fraction of cycle with BOTH feet loaded
Asymmetry is reported as affected-minus-intact and as a symmetry ratio.
"""
import numpy as np

from sto_utils import col, grf_vertical, heel_strikes, load_sto


def _contacts(t, grf, thr, settle=1.0):
    hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= settle]
    return hs


def spatiotemporal(path, settle=1.0):
    """Return per-side stance/swing/step-length plus asymmetry, or None if unusable."""
    cols, d = load_sto(path)
    t = d[:, 0]
    out = {}
    contact = {}
    for side in ("l", "r"):
        grf, thr = grf_vertical(cols, d, side)
        if grf is None:
            return None
        hs = _contacts(t, grf, thr, settle)
        if len(hs) < 3:
            return None
        loaded = grf > thr
        cyc_t, st_t = [], []
        for a, b in zip(hs[:-1], hs[1:]):
            cyc_t.append(float(t[b] - t[a]))
            seg = loaded[a:b]
            st_t.append(float(seg.sum()) / max(len(seg), 1) * (t[b] - t[a]))
        contact[side] = (hs, loaded)
        cyc = float(np.median(cyc_t))
        stance = float(np.median(st_t))
        out["%s_cycle" % side] = cyc
        out["%s_stance" % side] = stance
        out["%s_swing" % side] = cyc - stance
        # Stance percentage as DUTY FACTOR over the whole steady window, not a median of
        # per-cycle values. When cycle segmentation is bimodal (scuffing foot) the median of
        # per-cycle stance is nonsense -- it previously reported DPAR60 at 4.3% stance when the
        # true duty factor is 58.8%. Duty factor is segmentation-independent.
        win = loaded[hs[0]:hs[-1]]
        out["%s_stance_pct" % side] = 100.0 * float(win.sum()) / max(len(win), 1)
        out["%s_stance_pct_percycle" % side] = 100.0 * stance / cyc if cyc else float("nan")

    # step length: anterior calcaneus separation at each heel strike
    for side in ("l", "r"):
        other = "r" if side == "l" else "l"
        ca = col(cols, d, "calcn_%s.pos_x" % side)
        cb = col(cols, d, "calcn_%s.pos_x" % other)
        if ca is None or cb is None:
            continue
        hs = contact[side][0]
        steps = [float(ca[i] - cb[i]) for i in hs]
        if steps:
            out["%s_step_len" % side] = float(np.median(steps))

    # double support: fraction of time both loaded
    both = contact["l"][1] & contact["r"][1]
    out["double_support_pct"] = 100.0 * float(both.sum()) / len(both)

    # asymmetry, affected (left) minus intact (right)
    for k in ("stance_pct", "swing", "step_len", "cycle"):
        a, b = out.get("l_%s" % k), out.get("r_%s" % k)
        if a is not None and b is not None:
            out["asym_%s" % k] = a - b
            denom = 0.5 * (abs(a) + abs(b))
            out["ratio_%s" % k] = (a - b) / denom if denom else float("nan")
    return out


if __name__ == "__main__":
    import glob
    import json
    import os
    import sys

    RES = r"C:\Users\maurice\Documents\SCONE\results"
    GROUPS = {
        "HEALTHY": ["DHEALTHY_s1", "DHEALTHY_s2", "DHEALTHY_s3"],
        "PAR20": ["DPAR20_s1", "DPAR20_s2", "DPAR20_s3"],
        "PAR40": ["DPAR40_s1", "DPAR40_s2", "DPAR40_s3"],
        "PAR60": ["DPAR60_s1", "DPAR60_s2", "DPAR60_s3"],
        "SPAS005": ["SPAS005", "SPAS005_s2", "SPAS005_s3", "SPAS005_s4"],
        "SPAS01": ["SPAS01", "SPAS01_s2", "SPAS01_s3", "SPAS01_s4"],
    }

    def newest_sto(tag):
        ds = [x for x in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(x)]
        if not ds:
            return None
        dd = max(ds, key=os.path.getmtime)
        s = [x for x in glob.glob(os.path.join(dd, "*.sto")) if os.path.getsize(x) > 1000]
        return max(s, key=os.path.getmtime) if s else None

    res = {}
    print("%-10s %-7s %-10s %-11s %-11s %-11s" %
          ("group", "n", "asym_st%", "asym_swing", "asym_step", "dbl_supp%"))
    for g, tags in GROUPS.items():
        rows = []
        for tg in tags:
            p = newest_sto(tg)
            if not p:
                continue
            f = spatiotemporal(p)
            if f:
                rows.append(f)
                res["%s/%s" % (g, tg)] = f
        if not rows:
            print("%-10s  --" % g)
            continue

        def m(k):
            v = [r[k] for r in rows if k in r and np.isfinite(r[k])]
            return (float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0) if v else (float("nan"), 0.0)

        a, sa = m("asym_stance_pct")
        b, sb = m("asym_swing")
        c, sc = m("asym_step_len")
        e, se = m("double_support_pct")
        print("%-10s %-7d %+6.2f±%-4.2f %+6.3f±%-4.3f %+6.3f±%-4.3f %6.1f±%-4.1f"
              % (g, len(rows), a, sa, b, sb, c, sc, e, se))
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "scone_spatiotemporal.json"), "w"), indent=2)
