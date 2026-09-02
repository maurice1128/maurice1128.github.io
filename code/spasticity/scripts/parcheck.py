"""EXTERNAL POSITIVE CONTROL.

The oracle's channel semantics (which .sto channel is the contribution, which is the plant
sensor, what the delay does) are validated against a file the oracle never reads: the .par
that SCONE wrote for the same run. The base GaitStateController's soleus/gastroc KF gains are
free parameters whose converged values appear in the .par. Recovering them from the .sto alone
tests the reading, not the reflex under audit.
"""
import numpy as np, sys, os, glob

def load_sto(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    hi = [i for i, l in enumerate(lines) if l.strip().lower() == "endheader"][0] + 1
    cols = [c.strip() for c in lines[hi].split("\t")]
    body = [r for r in lines[hi + 1:] if r.strip()]
    return cols, np.array([[float(x) for x in r.split("\t")] for r in body])

for run in sys.argv[1:]:
    par = sorted(glob.glob(os.path.join(run, "0*.par")))[-1]
    sto = glob.glob(os.path.join(run, "*.sto"))[0]
    truth = {}
    for l in open(par, encoding="utf-8"):
        p = l.split("\t")
        if len(p) >= 2:
            truth[p[0].strip()] = float(p[1])
    cols, d = load_sto(sto); t = d[:, 0]; dt = np.median(np.diff(t))
    C = lambda n: d[:, cols.index(n)] if n in cols else None
    print("== %s  (par: %s)" % (os.path.basename(run), os.path.basename(par)))
    for mus, key in (("soleus", "S00111.soleus.KF"), ("gastroc", "S00111.gastroc.KF")):
        if key not in truth:
            continue
        for side in ("_l", "_r"):
            RF = C(mus + side + ".RF"); F = C(mus + side + ".mtu_force_norm")
            if RF is None:
                print("   %-10s no RF channel" % (mus + side)); continue
            best = None
            for k in range(0, 7):
                Fd = np.concatenate([np.full(k, F[0]), F[:len(F) - k]]) if k else F
                act = RF != 0
                if act.sum() < 50:
                    continue
                r = RF[act] / np.maximum(Fd[act], 1e-12)
                sc = np.percentile(np.abs(r - np.median(r)), 75)
                if best is None or sc < best[0]:
                    best = (sc, k, float(np.median(r)))
            print("   %-10s .par KF = %.6f   recovered from .sto = %.6f  (ratio %.4f, lag %d samples)"
                  % (mus + side, truth[key], best[2], best[2] / truth[key], best[1]))
