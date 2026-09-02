# -*- coding: utf-8 -*-
"""Round 146. Re-derive the P3D-2 ankle deltas two ways, and say which window each used.

The coordinator's re-measurement does not reproduce mine. Two candidate causes:
  (i)  WINDOW  -- I compared each run over a window ending at min(dur_inj, dur_base),
                  which is 11.84 / 12.16 / 12.16 s, so the windows differ BETWEEN rungs.
  (ii) METRIC  -- I used the GLOBAL RANGE (max-min) of ankle_angle over the whole
                  window. r141 and the coordinator use MEAN PER-CYCLE ROM.

A global range is set by the single most extreme excursion anywhere in the window;
a per-cycle mean is not. This script computes BOTH metrics under BOTH windows and
prints the calibration that decides which decomposition is the registered one:
r141 independently measured baseline L ROM = 30.963 deg.

Cycle decomposition is the project's own: sto_utils.heel_strikes on vertical GRF,
settle = 1.0 s, last cycle dropped.
"""
import io, os, sys, math, json

sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import sto_utils as S

BASE = r"C:\Users\maurice\Desktop\spasticity_paper\scone\probe3d_r141"
PAR = "230119.H1922v7b3.D20.par.sto"
REF = os.path.join(BASE, "bench_D20", PAR)
RUNGS = [("0.0125", "bench_D20_kv0p0125"),
         ("0.00625", "bench_D20_kv0p00625"),
         ("0.003125", "bench_D20_kv0p003125")]
SETTLE = 1.0


def load(p):
    cols, dat = S.load_sto(p)
    return cols, dat


def series(cols, dat, name):
    return list(S.col(cols, dat, name))


def global_range(cols, dat, side, t0, t1):
    t = series(cols, dat, "time")
    a = series(cols, dat, "ankle_angle_" + side)
    v = [a[i] for i in range(len(t)) if t0 <= t[i] <= t1]
    return math.degrees(max(v) - min(v)) if v else None


def per_cycle_rom(cols, dat, side, t0, t1):
    """Mean per-cycle ROM, project decomposition: heel strikes on vertical GRF
    (grf_vertical returns (signal, threshold); heel_strikes returns INDICES),
    last cycle dropped, cycles must lie wholly inside [t0, t1]."""
    t = series(cols, dat, "time")
    grf, thresh = S.grf_vertical(cols, dat, side)
    if grf is None:
        return None, 0
    idx = S.heel_strikes(t, grf, thresh=thresh)
    if idx is None or len(idx) < 3:
        return None, 0
    ang = series(cols, dat, "ankle_angle_" + side)
    cyc = []
    for k in range(len(idx) - 1):
        i0, i1 = idx[k], idx[k + 1]
        if t[i0] < t0 or t[i1] > t1:
            continue
        v = ang[i0:i1 + 1]
        if len(v):
            cyc.append(math.degrees(max(v) - min(v)))
    if len(cyc) >= 2:
        cyc = cyc[:-1]          # drop last, per cycle_features
    return (sum(cyc) / len(cyc) if cyc else None), len(cyc)


def dur(cols, dat):
    return series(cols, dat, "time")[-1]


rc, rd = load(REF)
BDUR = dur(rc, rd)
print("baseline duration %.4f s" % BDUR)
print()
print("CALIBRATION -- r141 independently measured baseline L per-cycle ROM = 30.963 deg")
for t1, lbl in ((BDUR, "full 1.0-%.2f" % BDUR), (11.84, "fixed 1.0-11.84")):
    v, n = per_cycle_rom(rc, rd, "l", SETTLE, t1)
    g = global_range(rc, rd, "l", SETTLE, t1)
    print("  window %-18s per-cycle ROM_l = %s (%d cycles)   global range = %.3f"
          % (lbl, ("%.3f" % v) if v else "n/a", n, g))

out = {}
for kv, d in RUNGS:
    ic, idd = load(os.path.join(BASE, d, PAR))
    idur = dur(ic, idd)
    W = {"per-rung  1.0-%.2f" % min(idur, BDUR): min(idur, BDUR),
         "fixed     1.0-11.84": 11.84}
    print()
    print("=" * 74)
    print("KV %s   injected duration %.2f s" % (kv, idur))
    print("=" * 74)
    rec = {}
    for wname, t1 in W.items():
        row = {}
        for metric, fn in (("global range", global_range), ("per-cycle ROM", per_cycle_rom)):
            vals = {}
            for side in ("l", "r"):
                b = fn(rc, rd, side, SETTLE, t1)
                i = fn(ic, idd, side, SETTLE, t1)
                if isinstance(b, tuple):
                    b, i = b[0], i[0]
                vals[side] = (b, i)
            bl, il = vals["l"]
            br, ir = vals["r"]
            if None in (bl, il, br, ir):
                print("  %-22s %-14s UNEVALUABLE" % (wname, metric))
                continue
            dl, dr = il - bl, ir - br
            ratio = abs(dr) / abs(dl) if dl else None
            print("  %-22s %-14s baseL %7.3f baseR %7.3f  injL %7.3f injR %7.3f"
                  % (wname, metric, bl, br, il, ir))
            print("  %-22s %-14s signed dL %+7.3f  dR %+7.3f   |dR|/|dL| = %s"
                  % ("", "", dl, dr, ("%.2f" % ratio) if ratio else "n/a"))
            row[metric] = {"baseL": bl, "baseR": br, "injL": il, "injR": ir,
                           "dL": dl, "dR": dr, "ratio": ratio}
        rec[wname] = row
    out[kv] = rec

json.dump(out, io.open(r"C:\Users\maurice\Desktop\spasticity_paper\paper\P3D2_REDERIVE_r146.json",
                       "w", encoding="utf-8"), indent=1)
print()
print("wrote paper/P3D2_REDERIVE_r146.json")
