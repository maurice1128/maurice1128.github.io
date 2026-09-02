# -*- coding: utf-8 -*-
"""r555: permutation and leave-one-family-out that account for the 81-candidate selection.

The manuscript reports p = 1/462 and 59 of 59 for one readout chosen as the maximum of a scan over
81 candidates, and conditions neither statistic on that scan. Both remedies are cheap on this design
and neither was run.

  max-T permutation.  For each of the C(11,5) = 462 label assignments, recompute the standardised
  arm separation for ALL 81 candidates and take the maximum. Comparing the observed maximum against
  that null distribution gives a p that is valid over the whole scan rather than for a readout picked
  after looking.

  nested leave-one-family-out.  Inside each of the 11 folds, choose the winning candidate from the 81
  using only the ten training families, then classify the held-out family's cells with a threshold
  fitted on those ten. Selection then sits inside the fold instead of outside it.

Both use the same corpus, gate and conventions as the rest of the paper.
"""
import glob, io, itertools, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
JOINTS = [("knee_angle_l", "knee"), ("ankle_angle_l", "ankle"), ("hip_flexion_l", "hip")]
GRID = list(range(0, 101, 5))
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]


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
    out = {}
    for col, nm in JOINTS:
        try:
            y = np.degrees(S.col(c, dat, col))
        except Exception:
            continue
        cur, sw, stn, tof = [], [], [], []
        for a, b in w:
            seg = y[a:b]
            cur.append(np.interp(np.linspace(0, 100, 101), np.linspace(0, 100, b - a), seg))
            m = on[a:b]
            i0 = np.where(~m)[0]
            if i0.size:
                sw.append((float(np.max(seg[i0])), float(np.min(seg[i0]))))
                tof.append(float(seg[i0[0]]))
            i1 = np.where(m)[0]
            if i1.size:
                stn.append((float(np.max(seg[i1])), float(np.min(seg[i1]))))
        out[nm] = {"curve": np.mean(cur, axis=0),
                   "swing_max": np.mean([x[0] for x in sw]) if sw else None,
                   "swing_min": np.mean([x[1] for x in sw]) if sw else None,
                   "stance_max": np.mean([x[0] for x in stn]) if stn else None,
                   "stance_min": np.mean([x[1] for x in stn]) if stn else None,
                   "toe_off": np.mean(tof) if tof else None,
                   "rom": float(np.mean([c.max() - c.min() for c in cur]))}
    return out


print("loading ...")
CELLS = {f: [d for d in (load(f, s) for s in range(101, 107)) if d] for f in HY + WK}
FAMS = [f for f in HY + WK if CELLS[f]]
print("   %d families, %d cells" % (len(FAMS), sum(len(CELLS[f]) for f in FAMS)))

CAND = []
for col, nm in JOINTS:
    for p in GRID:
        CAND.append(("%s at %d%% of cycle" % (nm, p), lambda d, nm=nm, p=p: d[nm]["curve"][p]))
    for k, lab in (("swing_max", "peak in swing"), ("swing_min", "trough in swing"),
                   ("stance_max", "peak in stance"), ("stance_min", "trough in stance"),
                   ("toe_off", "at toe-off"), ("rom", "range of motion")):
        CAND.append(("%s %s" % (nm, lab), lambda d, nm=nm, k=k: d[nm][k]))

# V[c][f] = array of cell values for candidate c, family f
NAMES = [nm for nm, _ in CAND]
V = np.full((len(CAND), len(FAMS), 6), np.nan)
for ci, (nm, fn) in enumerate(CAND):
    for fi, f in enumerate(FAMS):
        for si, d in enumerate(CELLS[f]):
            try:
                x = fn(d)
            except Exception:
                x = None
            if x is not None:
                V[ci, fi, si] = float(x)
FMEAN = np.nanmean(V, axis=2)                                    # (81, 11)
SD = np.nanmean(np.nanstd(V, axis=2, ddof=1), axis=1)            # (81,) mean within-family seed SD
SD = np.where(SD > 1e-9, SD, np.nan)
ok = ~np.isnan(SD) & ~np.isnan(FMEAN).any(axis=1)
print("   candidates usable for the permutation: %d of %d" % (ok.sum(), len(CAND)))

IDX = list(range(len(FAMS)))
TRUE_H = set(range(len(HY)))
splits = list(itertools.combinations(IDX, len(HY)))
print("   arrangements: %d" % len(splits))


def stat_all(hset):
    h = list(hset)
    w = [i for i in IDX if i not in hset]
    return np.abs(FMEAN[:, w].mean(axis=1) - FMEAN[:, h].mean(axis=1)) / SD


obs_all = stat_all(TRUE_H)
obs_max = np.nanmax(obs_all[ok])
win = NAMES[int(np.nanargmax(np.where(ok, obs_all, np.nan)))]
print("\nmax-T permutation")
print("   observed maximum over the scan: %.2f seed SD, at '%s'" % (obs_max, win))
null = np.array([np.nanmax(stat_all(set(sp))[ok]) for sp in splits])
ge = int((null >= obs_max - 1e-12).sum())
print("   arrangements whose maximum is at least as large: %d of %d" % (ge, len(splits)))
print("   selection-valid p = %.5f   (the naive single-readout p is %.5f)"
      % (ge / float(len(splits)), 1.0 / len(splits)))
print("   null maximum: median %.2f, 95th centile %.2f, largest %.2f"
      % (np.median(null), np.percentile(null, 95), null.max()))

print("\nnested leave-one-family-out: the readout is chosen inside each fold")
nested_ok = nested_n = 0
picks = {}
for fo in IDX:
    tr = [i for i in IDX if i != fo]
    trh = [i for i in tr if i in TRUE_H]
    trw = [i for i in tr if i not in TRUE_H]
    sc = np.abs(FMEAN[:, trw].mean(axis=1) - FMEAN[:, trh].mean(axis=1)) / SD
    sc = np.where(ok, sc, -np.inf)
    ci = int(np.nanargmax(sc))
    picks[NAMES[ci]] = picks.get(NAMES[ci], 0) + 1
    th = 0.5 * (FMEAN[ci, trh].mean() + FMEAN[ci, trw].mean())
    hi_is_weak = FMEAN[ci, trw].mean() > FMEAN[ci, trh].mean()
    for v in V[ci, fo]:
        if np.isnan(v):
            continue
        pred_w = (v > th) if hi_is_weak else (v < th)
        nested_n += 1
        nested_ok += int(pred_w == (fo not in TRUE_H))
print("   candidate chosen in each fold: %s"
      % ", ".join("%s x%d" % (k, v) for k, v in sorted(picks.items(), key=lambda x: -x[1])))
print("   nested accuracy: %d of %d = %.3f" % (nested_ok, nested_n, nested_ok / float(nested_n)))

io.open(os.path.join(P, "MAXT_r555.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "MAXT_r555",
 "why": ("The reported permutation p and leave-one-family-out accuracy are computed for a readout "
         "selected as the maximum of an 81-candidate scan, and neither is conditioned on that scan. "
         "This runs the max-T permutation and the nested-selection LOFO, which are."),
 "statistic": "family-level |mean(weakness) - mean(hyperreflexia)| divided by the mean within-family seed SD",
 "n_candidates_usable": int(ok.sum()), "n_arrangements": len(splits),
 "observed_max_seed_SD": float(obs_max), "winner": win,
 "n_arrangements_ge_observed": ge,
 "p_selection_valid": ge / float(len(splits)),
 "p_naive_single_readout": 1.0 / len(splits),
 "null_max_median": float(np.median(null)), "null_max_p95": float(np.percentile(null, 95)),
 "null_max_largest": float(null.max()),
 "nested_lofo": {"correct": nested_ok, "n": nested_n,
                 "accuracy": nested_ok / float(nested_n), "candidate_per_fold": picks},
}, indent=1, ensure_ascii=False, default=float))
print("\n-> MAXT_r555.json")
