# -*- coding: utf-8 -*-
"""r431: mediation test for mechanism hypothesis 4, on the r424 mixed-lesion grid.

Registration: paper/PREREG_mediation_r431.md, sha256 21cc6a4a90b67a0d..., hashed before any
kinematic or muscle endpoint of the r424 grid had been computed.

NO SIMULATION. Reads .sto files already on disk.

The judging statistic is the WITHIN-DOSE CENTRED correlation, fixed by section 6. A pooled
correlation across doses is reported but may not be used to judge: SLACK_RESULT_r418's P5 passed
on a pooled rho of -0.90 while the within-rung correlation flipped sign from -0.77 to +0.64.
"""
import glob
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
OUT = os.path.join(PAPER, "MEDIATION_RESULT_r431.json")
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

ROWS = [("W100", 1.00), ("W080", 0.80), ("W070", 0.70), ("W060", 0.60)]
COLS = [("0125", 0.0125), ("0250", 0.025), ("0500", 0.050), ("1100", 0.110)]

FLOORS = {"GASDRIVE": 0.00258, "SOLDRIVE": 0.00689, "KNEE_ic": 1.09745, "KTQ": 0.06841}


def measure(prefix):
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
    tsw = np.concatenate([np.arange(a + int(0.85 * (b - a)), b) for a, b in win])
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    return {"GASDRIVE": float(np.mean(S.col(cols, dat, "gastroc_l.activation")[tsw])),
            "SOLDRIVE": float(np.mean(S.col(cols, dat, "soleus_l.activation")[tsw])),
            "KTQ": float(np.mean(S.col(cols, dat, "knee_l.torque")[tsw])),
            "KNEE_ic": float(np.mean([kn[a] for a, _ in win])),
            "t_end": float(t[-1]), "n_cycles": len(win)}


def within_dose_r(cells, xk, yk):
    """Centre within each spastic dose, then correlate. Section 6's judging statistic."""
    cx, cy, per = [], [], {}
    for ctag, kv in COLS:
        v = [c for c in cells if c["col"] == ctag]
        if len(v) < 3:
            continue
        x = np.array([c[xk] for c in v])
        y = np.array([c[yk] for c in v])
        if len(set(x.tolist())) > 1:
            per[ctag] = {"n": len(v), "r": float(np.corrcoef(x, y)[0, 1])}
        cx += list(x - x.mean())
        cy += list(y - y.mean())
    if len(set(cx)) < 2:
        return None, per, 0
    return float(np.corrcoef(cx, cy)[0, 1]), per, len(cx)


cells = []
grid = {}
for rtag, ws in ROWS:
    for ctag, kv in COLS:
        got = []
        for s in SEEDS:
            m = measure("R424%s%s_s%d" % (rtag, ctag, s))
            if m:
                m.update(row=rtag, col=ctag, weak=ws, KV=kv, seed=s)
                got.append(m)
        grid[(rtag, ctag)] = got
        cells += got

res = {"round": "MEDIATION_RESULT_r431", "registration": "PREREG_mediation_r431.md",
       "registration_sha256":
           "21cc6a4a90b67a0d2fda29759d7f2ed359ebb2bb56d8cc8636eb58a26e41a928",
       "no_simulation_run": True, "floors_used": FLOORS, "grid": {}}

print("%-6s %-8s %-5s %-10s %-10s %-10s %s"
      % ("weak", "KV", "n", "GASDRIVE", "SOLDRIVE", "KTQ", "KNEE_ic"))
for rtag, ws in ROWS:
    for ctag, kv in COLS:
        v = grid[(rtag, ctag)]
        key = "%s_%s" % (rtag, ctag)
        if not v:
            res["grid"][key] = {"n_gate_G": 0, "uninformative": True}
            print("  x%-4.2f %-8.4f %-5d no Gate-G cell" % (ws, kv, 0))
            continue
        e = {"n_gate_G": len(v), "uninformative": len(v) < 4, "weak": ws, "KV": kv}
        for k in ("GASDRIVE", "SOLDRIVE", "KTQ", "KNEE_ic", "t_end"):
            a = [c[k] for c in v]
            e[k] = {"mean": float(np.mean(a)), "range": [float(min(a)), float(max(a))]}
        res["grid"][key] = e
        print("  x%-4.2f %-8.4f %-5d %-10.5f %-10.5f %-10.4f %+.4f%s"
              % (ws, kv, len(v), e["GASDRIVE"]["mean"], e["SOLDRIVE"]["mean"],
                 e["KTQ"]["mean"], e["KNEE_ic"]["mean"], "  UNINFORMATIVE" if len(v) < 4 else ""))

P = {}

# P1 -- dose to mediator, monotone within every weakness level
p1 = {}
for rtag, ws in ROWS:
    seq = [(kv, res["grid"]["%s_%s" % (rtag, ctag)].get("GASDRIVE", {}).get("mean"))
           for ctag, kv in COLS]
    seq = [(kv, m) for kv, m in seq if m is not None]
    if len(seq) < 2:
        p1[rtag] = {"n_rungs": len(seq), "VERDICT": "UNINFORMATIVE"}
        continue
    ms = [m for _, m in seq]
    mono = all(ms[i] < ms[i + 1] for i in range(len(ms) - 1))
    p1[rtag] = {"rung_means": ms, "monotone_increasing": mono,
                "total_rise": ms[-1] - ms[0],
                "multiple_of_floor": abs(ms[-1] - ms[0]) / FLOORS["GASDRIVE"],
                "VERDICT": "HOLDS" if mono else "FAILS"}
rows_judged = [v for v in p1.values() if v["VERDICT"] != "UNINFORMATIVE"]
P["P1_dose_raises_GASDRIVE_monotonically_in_every_row"] = {
    "by_row": p1,
    "VERDICT": "HOLDS" if rows_judged and all(v["VERDICT"] == "HOLDS" for v in rows_judged)
               else "FAILS"}

# P2 -- the key one: mediator to outcome, dose controlled
r2, per2, n2 = within_dose_r(cells, "GASDRIVE", "KNEE_ic")
pooled2 = float(np.corrcoef([c["GASDRIVE"] for c in cells],
                            [c["KNEE_ic"] for c in cells])[0, 1]) if len(cells) > 2 else None
P["P2_within_dose_GASDRIVE_predicts_KNEE_ic"] = {
    "within_dose_r": r2, "n": n2, "per_dose": per2, "threshold": -0.5,
    "pooled_r_REPORTED_BUT_NOT_JUDGING": pooled2,
    "VERDICT": "HOLDS" if (r2 is not None and r2 <= -0.5) else "FAILS"}

# P3 -- negative control
r3, per3, n3 = within_dose_r(cells, "SOLDRIVE", "KNEE_ic")
P["P3_SOLDRIVE_negative_control"] = {
    "within_dose_r": r3, "n": n3, "per_dose": per3, "threshold_abs": 0.3,
    "smaller_than_P2": (abs(r3) < abs(r2)) if (r2 is not None and r3 is not None) else None,
    "VERDICT": "HOLDS" if (r3 is not None and abs(r3) < 0.3
                           and (r2 is None or abs(r3) < abs(r2))) else "FAILS"}

# P4 -- torque sits in the middle
r4a, _, _ = within_dose_r(cells, "GASDRIVE", "KTQ")
r4b, _, _ = within_dose_r(cells, "KTQ", "KNEE_ic")
P["P4_KTQ_mediates"] = {
    "within_dose_r_GASDRIVE_vs_KTQ": r4a, "expected": "negative",
    "within_dose_r_KTQ_vs_KNEE_ic": r4b, "expected2": "positive",
    "VERDICT": "HOLDS" if (r4a is not None and r4b is not None and r4a < 0 and r4b > 0)
               else "FAILS"}

# P5 -- weakness must not drive the mediator
p5 = {}
for ctag, kv in COLS:
    ms = [res["grid"]["%s_%s" % (rtag, ctag)].get("GASDRIVE", {}).get("mean") for rtag, _ in ROWS]
    ms = [m for m in ms if m is not None]
    if len(ms) < 2:
        continue
    p5[ctag] = {"spread": max(ms) - min(ms),
                "multiple_of_floor": (max(ms) - min(ms)) / FLOORS["GASDRIVE"]}
worst = max((v["multiple_of_floor"] for v in p5.values()), default=None)
P["P5_weakness_does_not_drive_GASDRIVE"] = {
    "by_dose": p5, "largest_multiple_of_floor": worst,
    "VERDICT": "HOLDS" if (worst is not None and worst < 1.0) else "FAILS"}

# section 6 duration control on P2
ct, ck = [], []
for ctag, kv in COLS:
    v = [c for c in cells if c["col"] == ctag]
    if len(v) < 3:
        continue
    tt = np.array([c["t_end"] for c in v])
    kk = np.array([c["KNEE_ic"] for c in v])
    ct += list(tt - tt.mean())
    ck += list(kk - kk.mean())
bw = float(np.polyfit(ct, ck, 1)[0]) if len(set(ct)) > 1 else 0.0
rw = float(np.corrcoef(ct, ck)[0, 1]) if len(set(ct)) > 1 else 0.0
tspan = float(np.ptp([c["t_end"] for c in cells])) if cells else 0.0
eff = float(np.ptp([c["KNEE_ic"] for c in cells])) if cells else 0.0
frac = (abs(bw) * tspan / eff) if eff else None
res["duration_control"] = {"within_dose_pooled_slope_deg_per_s": bw, "pearson_r": rw,
                           "t_end_span_s": tspan, "KNEE_ic_span_deg": eff,
                           "fraction_attributable": frac, "threshold": 0.50,
                           "CONFOUNDED": bool(frac is not None and frac > 0.50)}
if res["duration_control"]["CONFOUNDED"] and \
        P["P2_within_dose_GASDRIVE_predicts_KNEE_ic"]["VERDICT"] == "HOLDS":
    P["P2_within_dose_GASDRIVE_predicts_KNEE_ic"]["VERDICT"] = \
        "CONFOUNDED (section 6); not counted as holding"

res["predictions"] = P
res["n_cells_used"] = len(cells)
held = [k for k, v in P.items() if v["VERDICT"] == "HOLDS"]
res["VERDICT"] = "%d of %d hold on %d Gate-G cells: %s" % (len(held), len(P), len(cells),
                                                           ", ".join(held) or "none")
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))

print()
for k, v in P.items():
    print("  %-52s %s" % (k[:52], v["VERDICT"]))
print()
print("P2 within-dose r = %s   (pooled %s, NOT judging)"
      % ("%.4f" % r2 if r2 is not None else "n/a",
         "%.4f" % pooled2 if pooled2 is not None else "n/a"))
print("P3 within-dose r = %s" % ("%.4f" % r3 if r3 is not None else "n/a"))
dc = res["duration_control"]
print("duration: slope %+.4f deg/s (r %+.4f), %.0f%% of the span -> %s"
      % (dc["within_dose_pooled_slope_deg_per_s"], dc["pearson_r"],
         100 * (dc["fraction_attributable"] or 0),
         "CONFOUNDED" if dc["CONFOUNDED"] else "clear"))
print()
print("VERDICT:", res["VERDICT"])
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
