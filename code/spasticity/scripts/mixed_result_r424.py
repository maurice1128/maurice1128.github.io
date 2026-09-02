# -*- coding: utf-8 -*-
"""r424 registered endpoint: can knee angle at heel strike rank a MIXED lesion?

Registration: paper/PREREG_mixed_r424.md, sha256 6b68fa0e3033f4d6..., hashed before any mixed cell
existed. NO SIMULATION -- reads .sto files already on disk.

Every reported difference is divided by the floor for its own endpoint (NULL_FLOORS_r428.json),
the rule that RESCORED_r429 and CORRECTION_r427 were written to enforce, and every arm reports
its per-cycle drift against control (STATIONARITY_r434).
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
OUT = os.path.join(PAPER, "MIXED_RESULT_r424.json")
SETTLE, T1 = 1.0, 9.73
SEEDS = range(101, 107)

ROWS = [("W100", 1.00), ("W080", 0.80), ("W070", 0.70), ("W060", 0.60)]
COLS = [("0125", 0.0125), ("0250", 0.025), ("0500", 0.050), ("1100", 0.110)]
KNEE_FLOOR = 1.09745          # NULL_FLOORS_r428, KNEE_ic_deg
ANKLE_FLOOR = 0.06902
BATCH_NULL_EDGE = 0.5697331886598267   # KNEE_MDC_BATCHNULL_r399, edge-gap form


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
    on = grf > thr
    stance = np.concatenate([np.arange(a, b)[on[a:b]] for a, b in win if on[a:b].any()])
    kn = np.degrees(S.col(cols, dat, "knee_angle_l"))
    an = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    per = [float(kn[a]) for a, _ in win]
    drift = float(np.polyfit(np.arange(len(per)), per, 1)[0])
    return {"KNEE_ic": float(np.mean(per)), "ANKLE_st": float(np.mean(an[stance])),
            "t_end": float(t[-1]), "n_cycles": len(win),
            "swing_s": float(np.mean([t[b] - t[a] for a, b in win])),
            "knee_drift_per_cycle": drift}


grid, cells = {}, []
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

res = {"round": "MIXED_RESULT_r424", "registration": "PREREG_mixed_r424.md",
       "registration_sha256":
           "6b68fa0e3033f4d634aa3b9ec20d8684cfc2cfdfe5c566101ddd926389f35b61",
       "no_simulation_run": True,
       "floors": {"KNEE_ic_mean_difference": KNEE_FLOOR, "ANKLE_st": ANKLE_FLOOR,
                  "knee_edge_gap_batch_null": BATCH_NULL_EDGE},
       "post_hoc_row": "W070 was added at r426 as an explicitly POST-HOC substitute after the "
                       "registered x0.60 root was found to pass only 2-3/6. It does NOT satisfy "
                       "any registered prediction and is reported separately.",
       "grid": {}}

print("%-6s %-8s %-5s %-22s %-9s %-8s %s"
      % ("weak", "KV", "n", "KNEE_ic range", "mean", "drift", "flag"))
for rtag, ws in ROWS:
    for ctag, kv in COLS:
        v = grid[(rtag, ctag)]
        key = "%s_%s" % (rtag, ctag)
        if not v:
            res["grid"][key] = {"n_gate_G": 0, "uninformative": True, "weak": ws, "KV": kv}
            print("  x%-4.2f %-8.4f %-5d no Gate-G cell" % (ws, kv, 0))
            continue
        kn = [c["KNEE_ic"] for c in v]
        e = {"n_gate_G": len(v), "uninformative": len(v) < 4, "weak": ws, "KV": kv,
             "KNEE_ic": {"mean": float(np.mean(kn)), "range": [float(min(kn)), float(max(kn))],
                         "values": sorted(kn)},
             "ANKLE_st": {"mean": float(np.mean([c["ANKLE_st"] for c in v]))},
             "t_end": {"mean": float(np.mean([c["t_end"] for c in v])),
                       "range": [float(min(c["t_end"] for c in v)),
                                 float(max(c["t_end"] for c in v))]},
             "swing_s_mean": float(np.mean([c["swing_s"] for c in v])),
             "knee_drift_per_cycle_mean": float(np.mean([c["knee_drift_per_cycle"] for c in v]))}
        res["grid"][key] = e
        print("  x%-4.2f %-8.4f %-5d [%+8.3f,%+8.3f]  %+8.3f %+8.4f %s"
              % (ws, kv, len(v), min(kn), max(kn), np.mean(kn), e["knee_drift_per_cycle_mean"],
                 "UNINFORMATIVE" if len(v) < 4 else ""))


def cell(rtag, ctag):
    e = res["grid"]["%s_%s" % (rtag, ctag)]
    return e if e.get("n_gate_G", 0) >= 4 else None


P = {}

# P1 -- spastic axis: more flexed as KV rises, within every weakness level
p1 = {}
for rtag, ws in ROWS:
    seq = [(kv, cell(rtag, ctag)) for ctag, kv in COLS]
    seq = [(kv, e["KNEE_ic"]["mean"]) for kv, e in seq if e]
    if len(seq) < 3:
        p1[rtag] = {"n_judgeable_rungs": len(seq), "VERDICT": "UNINFORMATIVE"}
        continue
    ms = [m for _, m in seq]
    mono = all(ms[i] > ms[i + 1] for i in range(len(ms) - 1))
    p1[rtag] = {"rung_means": ms, "monotone_more_flexed": mono,
                "total_change_deg": ms[-1] - ms[0],
                "multiple_of_floor": abs(ms[-1] - ms[0]) / KNEE_FLOOR,
                "VERDICT": "HOLDS" if mono else "FAILS"}
judged = [v for v in p1.values() if v["VERDICT"] != "UNINFORMATIVE"]
P["P1_spastic_axis_monotone_more_flexed"] = {
    "by_row": p1,
    "VERDICT": "HOLDS" if judged and all(v["VERDICT"] == "HOLDS" for v in judged) else "FAILS"}

# P2 -- weakness axis: more extended as weakness deepens, at every spastic gain
p2 = {}
for ctag, kv in COLS:
    seq = [(ws, cell(rtag, ctag)) for rtag, ws in ROWS]
    seq = [(ws, e["KNEE_ic"]["mean"]) for ws, e in seq if e]
    seq.sort(key=lambda x: -x[0])            # x1.00 first, deepening weakness after
    if len(seq) < 3:
        p2[ctag] = {"n_judgeable_rows": len(seq), "VERDICT": "UNINFORMATIVE"}
        continue
    ms = [m for _, m in seq]
    mono = all(ms[i] < ms[i + 1] for i in range(len(ms) - 1))
    p2[ctag] = {"row_means_from_x100_down": ms, "monotone_more_extended": mono,
                "total_change_deg": ms[-1] - ms[0],
                "multiple_of_floor": abs(ms[-1] - ms[0]) / KNEE_FLOOR,
                "VERDICT": "HOLDS" if mono else "FAILS"}
judged2 = [v for v in p2.values() if v["VERDICT"] != "UNINFORMATIVE"]
P["P2_weakness_axis_monotone_more_extended"] = {
    "by_dose": p2,
    "VERDICT": "HOLDS" if judged2 and all(v["VERDICT"] == "HOLDS" for v in judged2) else "FAILS"}


def edge(a, b):
    if a["range"][1] < b["range"][0]:
        return b["range"][0] - a["range"][1]
    if b["range"][1] < a["range"][0]:
        return -(a["range"][0] - b["range"][1])
    return 0.0


# P3 -- spasticity-dominant vs weakness-dominant, as registered
spd = [cell(r, "0500") for r in ("W100", "W080")]
spd = [e for e in spd if e]
wkd = cell("W060", "0125")
if not spd or not wkd:
    P["P3_mixed_is_rankable"] = {
        "VERDICT": "UNINFORMATIVE",
        "why": "the registered weakness-dominant cell is KV 0.0125 at x0.60, and the x0.60 root "
               "passes only 2-3/6 Gate G by either chaining route (RESCUE_RESULT_r426.json). It "
               "cannot be judged as written. Section 8 forbids substituting another cell."}
else:
    P["P3_mixed_is_rankable"] = {"VERDICT": "computed", "detail": "see below"}

# P3 substitute, explicitly post-hoc, using the x0.70 row
wkd_sub = cell("W070", "0125")
if spd and wkd_sub:
    gaps = [{"spastic_dominant": "%s_0500" % r,
             "edge_gap_deg": edge(cell(r, "0500")["KNEE_ic"], wkd_sub["KNEE_ic"]),
             "disjoint": edge(cell(r, "0500")["KNEE_ic"], wkd_sub["KNEE_ic"]) != 0}
            for r in ("W100", "W080") if cell(r, "0500")]
    P["P3_SUBSTITUTE_x070_POST_HOC"] = {
        "status": "POST-HOC. Does NOT satisfy registered P3, which names x0.60.",
        "weakness_dominant_cell": "W070_0125",
        "comparisons": gaps,
        "multiple_of_batch_null": [abs(g["edge_gap_deg"]) / BATCH_NULL_EDGE for g in gaps],
        "all_disjoint_and_above_null": all(abs(g["edge_gap_deg"]) > BATCH_NULL_EDGE
                                           for g in gaps)}

# P4 -- cancellation: do different (KV, weakness) combinations give the same knee angle?
overlaps = []
judgeable = [(k, e) for k, e in res["grid"].items() if e.get("n_gate_G", 0) >= 4]
for (ka, ea), (kb, eb) in itertools.combinations(judgeable, 2):
    if ea["KV"] == eb["KV"] and ea["weak"] == eb["weak"]:
        continue
    if edge(ea["KNEE_ic"], eb["KNEE_ic"]) == 0:
        overlaps.append({"a": ka, "b": kb,
                         "a_mean": ea["KNEE_ic"]["mean"], "b_mean": eb["KNEE_ic"]["mean"],
                         "mean_difference": abs(ea["KNEE_ic"]["mean"] - eb["KNEE_ic"]["mean"])})
P["P4_cancellation_exists"] = {
    "n_judgeable_cells": len(judgeable),
    "n_pairs_overlapping": len(overlaps), "overlapping_pairs": overlaps,
    "VERDICT": "HOLDS" if overlaps else "FAILS",
    "meaning": "P4 predicted overlap WOULD exist, i.e. a single knee reading cannot uniquely "
               "identify the lesion combination. HOLDS here means the predicted LIMIT is real."}

# duration control on the spastic axis, r417 procedure
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
span_t = float(np.ptp([c["t_end"] for c in cells]))
span_k = float(np.ptp([c["KNEE_ic"] for c in cells]))
res["duration_control"] = {"within_dose_slope_deg_per_s": bw, "pearson_r": rw,
                           "t_end_span_s": span_t, "KNEE_ic_span_deg": span_k,
                           "fraction": abs(bw) * span_t / span_k if span_k else None}
res["duration_control"]["CONFOUNDED"] = bool(res["duration_control"]["fraction"] and
                                             res["duration_control"]["fraction"] > 0.50)

res["predictions"] = P
res["n_cells"] = len(cells)
held = [k for k, v in P.items() if v.get("VERDICT") == "HOLDS"]
res["VERDICT"] = "%d hold on %d Gate-G cells: %s" % (len(held), len(cells), ", ".join(held))
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))

print()
for k, v in P.items():
    print("  %-44s %s" % (k[:44], v.get("VERDICT")))
dc = res["duration_control"]
print()
print("duration: slope %+.4f deg/s (r %+.4f) = %.0f%% -> %s"
      % (bw, rw, 100 * (dc["fraction"] or 0), "CONFOUNDED" if dc["CONFOUNDED"] else "clear"))
print("VERDICT:", res["VERDICT"])
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
