"""How big is the injected reflex WHEN IT FIRES? A mean cannot answer that.

Round 10 argued the injected spasticity is physiologically nil, using cycle-mean excitation:
"KV = 0.02 adds mean 0.0002 against soleus activation 0.123 -> 0.1-0.5 % of drive."

That reasoning has a known failure mode on this project. Watchdog defect #18 was logged for exactly
it: "an average over a window cannot test whether the window is empty." A velocity-gated reflex is
silent for most of the cycle BY DEFINITION -- `allow_neg_V = 0` means it contributes nothing while
the muscle shortens. Averaging over the whole cycle divides the reflex's contribution by the
fraction of time it is switched off, which understates it by construction.

The honest quantity is the contribution DURING the stretch events the reflex is defined to respond
to. This reports both, so the two numbers can never be quoted separately:

  cycle mean       -- what round 10 used; a lower bound
  during firing    -- restricted to frames where rectified fibre velocity is non-zero
  at peak stretch  -- the top 5 % of stretch-velocity frames, where a Tardieu catch would occur

If the reflex is still negligible at peak stretch, round 10's conclusion stands and the model does
not implement spasticity. If it is substantial at peak but negligible on average, the reflex is
real but PHASIC -- which is what velocity-dependent spasticity is supposed to be.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from replay_cache import replay  # noqa: E402
from sto_utils import grf_vertical, heel_strikes, load_sto, muscle_signal  # noqa: E402

RUNS = [("KV 0.02", "CMS020_s1", 0.02), ("KV 0.03", "CMS030_s1", 0.03),
        ("KV 0.05", "SPAS005_s2", 0.05), ("KV 0.10", "SPAS01_s2", 0.10)]


def main():
    print("Injected reflex excitation as a fraction of the muscle's own activation\n")
    print("%-8s %-8s %10s %10s %10s %9s" %
          ("cond", "muscle", "cycle_mean", "when_firing", "peak_5pct", "duty"))
    print("-" * 62)
    for name, tag, kv in RUNS:
        r = replay(tag, gen_cap=None)
        if "error" in r:
            print("%-8s %s" % (name, r["error"]))
            continue
        cols, d = load_sto(r["sto"])
        t = d[:, 0]
        grf, thr = grf_vertical(cols, d, "l")
        hs = [i for i in heel_strikes(t, grf, thresh=thr) if t[i] >= 1.0]
        if len(hs) < 3:
            continue
        a0, b0 = hs[0], hs[-1]
        for m in ("soleus", "gastroc"):
            act = muscle_signal(cols, d, m, "l", "activation")
            rv = None
            for cand in ("%s_l.RV" % m, "/forceset/%s_l/RV" % m):
                if cand in cols:
                    rv = d[:, cols.index(cand)]
                    break
            if act is None or rv is None:
                continue
            # `soleus_l.RV` IS ALREADY the reflex contribution KV*max(V_delayed,0) -- the raw
            # velocity is the separate `.V` channel. The original line was `kv * max(rv,0)`, i.e.
            # KV^2*V, understating the contribution by 1/KV = 10x at KV 0.10 and 20x at 0.05.
            # This is the same defect that voided tonic_swap_test.py, in the script that was used
            # to argue the reflex is physiologically negligible.
            add = np.maximum(rv[a0:b0], 0.0)
            A = act[a0:b0]
            fire = add > 0
            duty = float(np.mean(fire))
            cyc = float(np.mean(add) / max(np.mean(A), 1e-9))
            whenf = float(np.mean(add[fire]) / max(np.mean(A[fire]), 1e-9)) if fire.any() else 0.0
            if fire.any():
                thr95 = np.percentile(add[fire], 95)
                pk = add >= thr95
                peak = float(np.mean(add[pk]) / max(np.mean(A[pk]), 1e-9))
            else:
                peak = 0.0
            print("%-8s %-8s %9.2f%% %9.2f%% %9.2f%% %8.0f%%"
                  % (name, m, 100 * cyc, 100 * whenf, 100 * peak, 100 * duty))
    print("\nRead the 'peak_5pct' column, not 'cycle_mean': a velocity-gated reflex is silent")
    print("whenever the muscle shortens, so a cycle mean divides its effect by the duty cycle.")


if __name__ == "__main__":
    main()
