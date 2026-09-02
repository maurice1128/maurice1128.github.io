# -*- coding: utf-8 -*-
"""Does warm-start chaining ITSELF move knee angle at heel strike?

The headline compares SPAS KV 0.110 (three chaining rounds) against WEAK x0.80 (unchained
root), edge gap 6.3919 deg. Severity and protocol are confounded there. r400 holds severity
FIXED and applies the same three rounds to both axes -- KV 0.050 -> 0.050 -> 0.050 -> 0.050
and x0.80 -> x0.80 -> x0.80 -> x0.80. If three rounds at unchanged severity leave knee-at-HS
where it was, protocol is not what produced the 6.39 deg.

Conventions carried unaltered: SETTLE 1.00, T1 9.73, cycles wholly inside the window, drop the
last kept cycle, require >= 5, stance = leg0_l.grf_norm_y > 0.05.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\SHAM_READOUT_r406.json"
SETTLE, T1 = 1.0, 9.73


def knee_hs(prefix):
    g = [d for d in glob.glob(os.path.join(RES, prefix + ".*")) if os.path.isdir(d)]
    if not g:
        return None
    if len(g) > 1:                      # a re-run leaves a " (1)" twin; take the real run
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
    kne = np.degrees(S.col(cols, dat, "knee_angle_l"))
    return float(np.mean([kne[a] for a, _ in win]))


SEEDS = range(101, 107)
LADDERS = [
    ("SPASTIC KV 0.050 (unchanged severity)",
     [("0 rounds  R151S", ["R151S_s%d" % s for s in SEEDS]),
      ("1 round   c1", ["R400SPgc1_s%d" % s for s in SEEDS]),
      ("2 rounds  c2", ["R400SPgc2_s%d" % s for s in SEEDS]),
      ("3 rounds  c3", ["R400SPgc3_s%d" % s for s in SEEDS])]),
    ("WEAK x0.80 (unchanged severity)",
     [("0 rounds  R151W", ["R151W_s%d" % s for s in SEEDS]),
      ("1 round   c1", ["R400WKc1_s%d" % s for s in SEEDS]),
      ("2 rounds  c2", ["R400WKc2_s%d" % s for s in SEEDS]),
      ("3 rounds  c3", ["R400WKc3_s%d" % s for s in SEEDS])]),
]

res = {"question": "does chaining itself move knee angle at heel strike, at unchanged severity?",
       "endpoint": "knee_angle_l at left heel strike, per-cycle mean, deg", "ladders": {}}

for title, rungs in LADDERS:
    print("=== %s" % title)
    print("  %-18s %-4s %-24s %-9s %s" % ("rounds of chaining", "n", "range", "mean", "shift vs 0"))
    base = None
    entries = {}
    for label, pres in rungs:
        v = sorted(x for x in (knee_hs(p) for p in pres) if x is not None)
        if not v:
            print("  %-18s %-4d %s" % (label, 0, "no Gate-G cell"))
            entries[label] = {"n": 0}
            continue
        m = float(np.mean(v))
        if base is None:
            base = m
        entries[label] = {"n": len(v), "range": [v[0], v[-1]], "mean": m,
                          "shift_vs_unchained": m - base}
        print("  %-18s %-4d [%+8.4f, %+8.4f]  %+9.4f  %+.4f"
              % (label, len(v), v[0], v[-1], m, m - base))
    res["ladders"][title] = entries
    print()

sp = res["ladders"][LADDERS[0][0]]
wk = res["ladders"][LADDERS[1][0]]
shifts = [e["shift_vs_unchained"] for d in (sp, wk) for e in d.values()
          if e.get("shift_vs_unchained") is not None]
worst = max(abs(x) for x in shifts) if shifts else None
res["largest_protocol_shift_deg"] = worst
res["headline_gap_deg"] = 6.391931677410274
res["verdict"] = (
    "protocol shift %.4f deg against a headline gap of 6.3919 deg -- %s"
    % (worst, "chaining cannot account for the gap" if worst is not None and worst < 1.0
       else "NOT negligible; the headline is partly protocol and must be re-read")
    if worst is not None else "UNINFORMATIVE")
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, indent=2, ensure_ascii=False))
print("largest protocol-only shift: %s deg" % ("%.4f" % worst if worst is not None else "n/a"))
print("headline gap              : 6.3919 deg")
print("VERDICT: %s" % res["verdict"])
print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))
