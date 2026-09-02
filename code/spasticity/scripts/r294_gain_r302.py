# -*- coding: utf-8 -*-
"""The registered failure criterion of r294 is a SPEED gain, not a fitness gain.

`PREREG_faststart_r294.md` fails the arm only when achieved speed is <= 1.30 m/s AND the gain
over the final 100 generations is < 0.02 m/s. `verify_r294.py` supplied the speeds and the
FITNESS gain; fitness is in objective units and cannot stand in for m/s. This evaluates the par
nearest 100 generations before the last one and measures the speed gain directly.

The distinction decides the rung:
  gain < 0.02 m/s  -> FAILURE, the model is at its asymptote and the axis is closed for it
  gain >= 0.02 m/s -> PARTIAL, the arm is budget-bound and a model bound has NOT been shown

Read-only apart from `sconecmd -e`, which writes only `.sto`.
"""
import io, os, re, sys, glob, json, subprocess
sys.path.insert(0, r"C:\Users\maurice\Desktop\spasticity_paper\scone")
import numpy as np, sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
PAPER = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
SETTLE, T1 = 1.00, 13.58
SUCCESS, FAIL_GAIN = 1.30, 0.02


def speed_of(d, par):
    sto = os.path.join(d, par + ".sto")
    if not os.path.exists(sto):
        subprocess.run([SCONECMD, "-e", par], cwd=d, capture_output=True, timeout=1800)
    if not os.path.exists(sto):
        return None
    cols, dat = S.load_sto(sto)
    t = np.asarray(S.col(cols, dat, "time"), dtype=float)
    grf, thr = S.grf_vertical(cols, dat, "l")
    idx = S.heel_strikes(t, grf, thresh=thr)
    cyc = [(a, b) for a, b in zip(idx[:-1], idx[1:]) if t[a] >= SETTLE and t[b] <= T1]
    cyc = cyc[:-1] if len(cyc) >= 2 else cyc
    if not cyc:
        return None
    px = np.asarray(S.col(cols, dat, "pelvis_tx"), dtype=float)
    a, b = cyc[0][0], cyc[-1][1]
    return float((px[b - 1] - px[a]) / (t[b - 1] - t[a]))


cells = []
for p in sorted(glob.glob(os.path.join(PAPER, "RUN_FASTSTART_r294_cell*.json"))):
    dep = json.load(open(p))
    d = os.path.join(RES, dep["result_dir"])
    warm = dep["warm_start"]
    pars = sorted((int(m.group(1)), f) for f in os.listdir(d)
                  for m in [re.match(r"^(\d{4})_[\d.]+_[\d.]+\.par$", f)] if m and f != warm)
    gen_last, par_last = pars[-1]
    target = gen_last - 100
    gen_prev, par_prev = min(pars, key=lambda x: abs(x[0] - target))

    s_last = speed_of(d, par_last)
    s_prev = speed_of(d, par_prev)
    gain = (s_last - s_prev) if (s_last is not None and s_prev is not None) else None
    span = gen_last - gen_prev
    cells.append({"cell": dep["cell"], "seed": dep["seed"],
                  "par_prev": par_prev, "gen_prev": gen_prev, "speed_prev_mps": s_prev,
                  "par_last": par_last, "gen_last": gen_last, "speed_last_mps": s_last,
                  "generations_spanned": span, "speed_gain_mps": gain,
                  "gain_per_100_gen": (gain * 100.0 / span) if (gain is not None and span) else None})
    print("cell %d seed %d: gen %d %.4f  ->  gen %d %.4f   gain %+.4f over %d gens (%+.4f per 100)"
          % (dep["cell"], dep["seed"], gen_prev, s_prev, gen_last, s_last,
             gain, span, gain * 100.0 / span))

sp = [c["speed_last_mps"] for c in cells if c["speed_last_mps"] is not None]
gn = [c["gain_per_100_gen"] for c in cells if c["gain_per_100_gen"] is not None]
mx = max(sp)
mg = max(gn)
if mx > SUCCESS:
    rung, verdict = "SUCCESS", "a warm start above 1.30 m/s exists; the velocity axis is deliverable"
elif mg < FAIL_GAIN:
    rung, verdict = "FAILURE", ("<= 1.30 m/s and the final-100-generation speed gain is below "
                                "0.02 m/s: the model is at its asymptote and the axis is closed "
                                "for this MODEL, not merely for the tool")
else:
    rung, verdict = "PARTIAL", ("<= 1.30 m/s but the final-100-generation speed gain is at or "
                                "above 0.02 m/s, so the arm is BUDGET-BOUND. A model bound has "
                                "NOT been shown and the registered failure rung does not fire")

out = {"what": "registered failure criterion of r294 evaluated as a SPEED gain",
       "success_threshold_mps": SUCCESS, "failure_gain_threshold_mps_per_100gen": FAIL_GAIN,
       "cells": cells, "max_achieved_speed_mps": mx, "max_gain_per_100_gen": mg,
       "RUNG": rung, "VERDICT": verdict,
       "context": ("SPEED_CLOSURE_r208.md measured a ceiling of ~1.13 m/s at 270 generations "
                   "from this warm start; 600 generations reach %.4f m/s, so that figure was a "
                   "budget bound rather than a ceiling" % mx)}
q = os.path.join(PAPER, "R294_GAIN_r302.json")
json.dump(out, io.open(q, "w", encoding="utf-8"), indent=1)

print()
print("max achieved            %.4f m/s   (success needs > %.2f)" % (mx, SUCCESS))
print("max gain per 100 gens   %+.4f m/s   (failure needs < %.2f)" % (mg, FAIL_GAIN))
print("RUNG %s -- %s" % (rung, verdict))
print("\nwrote %s (%d bytes)" % (q, os.path.getsize(q)))
