# -*- coding: utf-8 -*-
"""r518: how the separation behaves under stricter admissibility gates.

The gate is 9.73 s and the earliest admitted hyperreflexia cell ends at 9.81 s, so a referee asked
what a stricter gate does. A stricter gate drops the shortest-surviving cells, which are the deepest
gains, so this is also a direct probe of whether the result depends on the cells closest to failure.
Cells are re-admitted from CELL_CACHE_r501; no simulation and no .sto read.
"""
import io, json, itertools, math
import numpy as np

PAP = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
cache = json.load(io.open(PAP + r"\CELL_CACHE_r501.json", encoding="utf-8"))
HY = ["R151S", "R393SPg070", "R393SPg100", "R396SPg110", "R396SPg120"]
WK = ["R151W", "R174W870", "R174W892", "R169W090", "R174W915", "R169W095"]

print("%-7s %6s %6s %8s %9s %9s %10s %8s %8s"
      % ("gate", "nHy", "nWk", "famHy", "arm diff", "cell gap", "disjoint", "perm p", "LOFO"))
rows = []
for gate in (9.73, 10.0, 10.5, 11.0, 12.0, 13.0):
    hy = {f: [c["knee_ic_deg"] for c in cache[f]["cells"] if c["t_end_s"] >= gate] for f in HY}
    wk = {f: [c["knee_ic_deg"] for c in cache[f]["cells"] if c["t_end_s"] >= gate] for f in WK}
    hy = {f: v for f, v in hy.items() if len(v) >= 3}          # keep families with >= 3 cells
    wk = {f: v for f, v in wk.items() if len(v) >= 3}
    if len(hy) < 2 or len(wk) < 2:
        rows.append({"gate": gate, "note": "too few families survive"}); print("%-7.2f  -- too few families" % gate); continue
    ch = [x for v in hy.values() for x in v]; cw = [x for v in wk.values() for x in v]
    mh = [float(np.mean(v)) for v in hy.values()]; mw = [float(np.mean(v)) for v in wk.values()]
    diff = float(np.mean(mh) - np.mean(mw))
    gap = float(min(cw) - max(ch))
    disj = bool(max(ch) < min(cw))
    allm = mh + mw; obs = abs(np.mean(mh) - np.mean(mw)); tot = hit = 0
    for idx in itertools.combinations(range(len(allm)), len(mh)):
        g1 = [allm[i] for i in idx]; g2 = [allm[i] for i in range(len(allm)) if i not in idx]
        tot += 1
        if abs(np.mean(g1) - np.mean(g2)) >= obs - 1e-12: hit += 1
    ok = tot_c = 0
    for held, truth in [(f, True) for f in hy] + [(f, False) for f in wk]:
        trh = [np.mean(v) for f, v in hy.items() if f != held]
        trw = [np.mean(v) for f, v in wk.items() if f != held]
        if not trh or not trw: continue
        thr = 0.5 * (np.mean(trh) + np.mean(trw))
        v = hy[held] if truth else wk[held]
        ok += sum(1 for x in v if (x < thr) == truth); tot_c += len(v)
    rows.append({"gate": gate, "n_hy": len(ch), "n_wk": len(cw), "fam_hy": len(hy), "fam_wk": len(wk),
                 "arm_difference_deg": diff, "cell_gap_deg": gap, "cells_disjoint": disj,
                 "perm_p": hit / float(tot), "perm_splits": tot,
                 "lofo_accuracy": ok / float(tot_c) if tot_c else None})
    print("%-7.2f %6d %6d %8d %9.3f %9.3f %10s %8.4f %7.3f"
          % (gate, len(ch), len(cw), len(hy), diff, gap, disj, hit / float(tot),
             ok / float(tot_c) if tot_c else float("nan")))

io.open(PAP + r"\GATE_SENSITIVITY_r518.json", "w", encoding="utf-8", newline="").write(
    json.dumps({"id": "GATE_SENSITIVITY_r518",
                "why": ("the gate is 9.73 s and the earliest admitted hyperreflexia cell ends at "
                        "9.81 s; a stricter gate drops the shortest-surviving cells, which are the "
                        "deepest gains, so this probes whether the result depends on cells closest "
                        "to failure"),
                "families_kept_if": ">= 3 cells survive the gate",
                "rows": rows}, indent=1, ensure_ascii=False))
print("\n-> GATE_SENSITIVITY_r518.json")
