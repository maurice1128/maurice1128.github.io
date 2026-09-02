# -*- coding: utf-8 -*-
"""r437: independent re-derivation of every number in SUMMARY_FOR_ADVISOR.md.

Deliberately does NOT import any analysis script written today. It re-reads the .sto files,
re-detects heel strikes, re-applies the corpus window and recomputes each figure from scratch,
then compares against the value claimed in the summary. Anything that fails to reproduce is a
hallucination or a transcription error and is printed as MISMATCH.

The only shared code is sto_utils (the .sto reader), which is what the numbers were always
computed from.
"""
import glob
import io
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "VERIFY_SUMMARY_r437.json")
SETTLE, T1 = 1.0, 9.73

CHECKS = []


def check(name, claimed, got, tol=0.02, note=""):
    """tol is a RELATIVE tolerance unless claimed is 0."""
    if got is None:
        ok = False
        rel = None
    elif claimed == 0:
        rel = abs(got)
        ok = rel < 1e-6
    else:
        rel = abs(got - claimed) / abs(claimed)
        ok = rel <= tol
    CHECKS.append({"name": name, "claimed": claimed, "recomputed": got,
                   "relative_error": rel, "PASS": bool(ok), "note": note})
    print("  %-46s claimed %-12s got %-12s %s"
          % (name[:46],
             ("%.4f" % claimed) if isinstance(claimed, float) else str(claimed),
             ("%.4f" % got) if isinstance(got, float) else str(got),
             "PASS" if ok else "*** MISMATCH ***"))


def cell(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    if len(g) > 1:
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    cols, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    if float(t[-1]) < T1 or len(win) < 5:
        return None
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    return {"knee_ic": float(np.mean([kn[a] for a, _ in win])), "t_end": float(t[-1]),
            "n_cycles": len(win)}


def arm(prefixes):
    v = [cell(p) for p in prefixes]
    return [x for x in v if x]


print("=== 1. 頭條:痙攣 KV0.110 vs 無力 x0.80,膝角邊界差 ===")
SP = arm(["R396SPg110_s%d" % s for s in (101, 102, 105, 106)])
WK = arm(["R151W_s%d" % s for s in range(101, 107)])
sk = sorted(c["knee_ic"] for c in SP)
wk = sorted(c["knee_ic"] for c in WK)
edge = wk[0] - sk[-1]
check("headline edge gap (deg)", 6.3919, edge, tol=0.005)
check("headline n_spastic", 4, len(sk), tol=0)
check("headline n_weak", 6, len(wk), tol=0)
print("     spastic %s" % ["%.4f" % x for x in sk])
print("     weak    %s" % ["%.4f" % x for x in wk])

print()
print("=== 2. 置換檢定:10 個 cell 分成 4/6 的所有分法 ===")
allv = sk + wk
best = 0
tot = 0
for combo in itertools.combinations(range(10), 4):
    a = [allv[i] for i in combo]
    b = [allv[i] for i in range(10) if i not in combo]
    g = min(b) - max(a)
    tot += 1
    if g >= edge - 1e-9:
        best += 1
check("permutation: n_partitions", 210, tot, tol=0)
check("permutation: n_at_least_as_extreme", 1, best, tol=0)
print("     p = %d/%d = %.6f" % (best, tot, best / tot))

print()
print("=== 3. 同機制家族虛無(六個背屈無力家族)===")
FAMS = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
fam = {f: arm(["%s_s%d" % (f, s) for s in range(101, 107)]) for f in FAMS}
fam = {k: v for k, v in fam.items() if len(v) >= 4}
gaps = []
for a, b in itertools.combinations(sorted(fam), 2):
    va = sorted(c["knee_ic"] for c in fam[a])
    vb = sorted(c["knee_ic"] for c in fam[b])
    g = (vb[0] - va[-1]) if va[-1] < vb[0] else ((va[0] - vb[-1]) if vb[-1] < va[0] else 0.0)
    gaps.append(abs(g))
check("batch null: largest same-mechanism edge gap", 0.5697, max(gaps), tol=0.01)
check("batch null: headline / floor", 11.2, edge / max(gaps), tol=0.03)

print()
print("=== 4. 同格內 seed SD(正確的雜訊尺度)===")
sds = []
for pre in ("R424W1000125", "R424W0800125", "R424W0700125", "R424W1000500",
            "R424W0800500", "R424W0700500", "R151W", "R151C"):
    v = arm(["%s_s%d" % (pre, s) for s in range(101, 107)])
    if len(v) >= 4:
        sds.append(np.std([c["knee_ic"] for c in v], ddof=1))
sd_typ = float(np.mean(sds))
check("typical within-cell seed SD (deg)", 0.5114, sd_typ, tol=0.02)
check("headline / seed SD", 12.5, edge / sd_typ, tol=0.03)

print()
print("=== 5. 混合網格:痙攣軸與無力軸 ===")


def gmean(row, col):
    v = arm(["R424%s%s_s%d" % (row, col, s) for s in range(101, 107)])
    return (float(np.mean([c["knee_ic"] for c in v])), len(v)) if len(v) >= 4 else (None, len(v))


m = {}
for r in ("W100", "W080", "W070"):
    for c in ("0125", "0250", "0500", "1100"):
        m[(r, c)] = gmean(r, c)
check("spastic axis x1.00 (0.0125->0.050) deg", -4.270,
      m[("W100", "0500")][0] - m[("W100", "0125")][0], tol=0.02)
check("spastic axis x0.80 (0.0125->0.110) deg", -8.033,
      m[("W080", "1100")][0] - m[("W080", "0125")][0], tol=0.02)
check("weakness axis KV0.0125 (x1.00->x0.70) deg", 0.520,
      m[("W070", "0125")][0] - m[("W100", "0125")][0], tol=0.03)
check("weakness axis KV0.025 deg", 0.458,
      m[("W070", "0250")][0] - m[("W100", "0250")][0], tol=0.03)
check("weakness axis KV0.050 deg", 1.784,
      m[("W070", "0500")][0] - m[("W100", "0500")][0], tol=0.03)
check("weakness at KV0.0125 in seed SDs", 1.0,
      abs(m[("W070", "0125")][0] - m[("W100", "0125")][0]) / sd_typ, tol=0.10)
check("spastic x0.80 in seed SDs", 15.7,
      abs(m[("W080", "1100")][0] - m[("W080", "0125")][0]) / sd_typ, tol=0.05)

print()
print("=== 6. 最極端的抵消配對 ===")
d = abs(m[("W080", "0125")][0] - m[("W070", "0125")][0])
check("W080_0125 vs W070_0125 mean difference (deg)", 0.002, d, tol=0.60,
      note="claimed 0.002; tolerance is loose because the claim is 'essentially zero'")

print()
print("=== 7. 檔案存在性與大小 ===")
FILES = ["SUMMARY_FOR_ADVISOR.md", "MIXED_RESULT_r424.json", "MEDIATION_RESULT_r431.json",
         "SPANNING_RESULT_r421.json", "VIDEOKNEE_r422.json", "VIDEOMIXED_r435.json",
         "FLOOR_CORRECTION_r436.json", "STATIONARITY_r434.json",
         "MECHANISM_SCOREBOARD_r430.json", "KNEE_MDC_BATCHNULL_r399.json",
         "PREREG_mixed_r424.md", "PREREG_mediation_r431.md", "PREREG_spanning_r421.md"]
missing = [f for f in FILES if not os.path.exists(os.path.join(PAPER, f))]
check("all cited files exist", 0, len(missing), tol=0, note=str(missing))

print()
print("=== 8. 中介檢定的兩個力矩相關(獨立重算)===")
tsw_r = {}
for xk, yk, claimed, lab in ((("gastroc_l.activation"), ("knee_l.torque"), 0.0621, "GAS->KTQ"),
                             (("knee_l.torque"), ("knee_angle_l"), -0.0519, "KTQ->KNEE")):
    cx, cy = [], []
    for col in ("0125", "0250", "0500", "1100"):
        xs, ys = [], []
        for row in ("W100", "W080", "W070", "W060"):
            for s in range(101, 107):
                p = "R424%s%s_s%d" % (row, col, s)
                g = [dd for dd in glob.glob(os.path.join(RES, p + ".*")) if os.path.isdir(dd)]
                if not g:
                    continue
                if len(g) > 1:
                    g = [max(g, key=lambda dd: len(glob.glob(os.path.join(dd, "[0-9]*.par"))))]
                st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
                if not st:
                    continue
                cols, dat = S.load_sto(st[-1])
                t = dat[:, 0]
                grf, thr = S.grf_vertical(cols, dat, "l")
                hsx = S.heel_strikes(t, grf, thresh=thr)
                ac = [(hsx[k], hsx[k + 1]) for k in range(len(hsx) - 1) if t[hsx[k]] >= SETTLE]
                w = [c for c in ac if t[c[1]] <= T1]
                w = w[:-1] if len(w) >= 2 else w
                if float(t[-1]) < T1 or len(w) < 5:
                    continue
                tw = np.concatenate([np.arange(a + int(0.85 * (b - a)), b) for a, b in w])
                vx = S.col(cols, dat, xk)
                xs.append(float(np.mean(vx[tw])))
                if yk == "knee_angle_l":
                    vy = np.degrees(S.col(cols, dat, yk))
                    ys.append(float(np.mean([vy[a] for a, _ in w])))
                else:
                    ys.append(float(np.mean(S.col(cols, dat, yk)[tw])))
        if len(xs) >= 3:
            cx += list(np.array(xs) - np.mean(xs))
            cy += list(np.array(ys) - np.mean(ys))
    r = float(np.corrcoef(cx, cy)[0, 1])
    tsw_r[lab] = r
    check("mediation within-dose r %s" % lab, claimed, r, tol=0.15)
check("mediation n cells", 74, len(cx), tol=0)

n_pass = sum(1 for c in CHECKS if c["PASS"])
res = {"round": "VERIFY_SUMMARY_r437", "no_simulation_run": True,
       "what": "independent re-derivation of every number in SUMMARY_FOR_ADVISOR.md, from the "
               ".sto files, without importing any analysis script written this session",
       "n_checks": len(CHECKS), "n_pass": n_pass, "n_fail": len(CHECKS) - n_pass,
       "checks": CHECKS}
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print()
print("=========== %d / %d PASS ===========" % (n_pass, len(CHECKS)))
for c in CHECKS:
    if not c["PASS"]:
        print("  FAIL %-44s claimed %s got %s %s"
              % (c["name"][:44], c["claimed"], c["recomputed"], c["note"]))
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
