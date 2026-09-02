"""Perturbation response: the one thing an adapted controller cannot pre-plan around.

WHY THIS, AFTER FIVE FAILED FEATURES.
Every previous attempt looked for a signature in STEADY adapted gait, and every one failed for the
same structural reason: the controller is re-optimized with the impairment in place, so it has an
entire optimization run in which to learn to avoid the impairment. Weakness and spasticity both
make dorsiflexion costly, both are answered by suppressing ankle excursion/velocity, and the two
converge on similar observable gaits. Adaptation is plausibly a many-to-one map, and no feature of
the adapted gait can invert it.

A perturbation bypasses that entirely. The controller here is optimized WITHOUT perturbation and
the push is applied only at REPLAY, so there is no opportunity to pre-adapt -- exactly as a patient
cannot rehearse an unexpected stumble. What the response reveals is the plant plus the reflex, not
the adaptation.

The two impairments should respond in OPPOSITE directions, which is what a discriminator needs:
  spasticity -> the push drives rapid ankle dorsiflexion, the velocity reflex FIRES, and the
                plantarflexors produce an involuntary burst: an EXCESSIVE, fast response
  weakness   -> recovery demands a rapid dorsiflexor response the weakened muscle cannot deliver:
                an ABSENT/sluggish response
Clinically this is the same logic as the Tardieu test (fast passive stretch), and it matches the
one variable that predicted nerve-block response in the literature (soleus co-contraction during
swing, OR 4.72) -- both are involuntary fast responses rather than steady-state postures.

Reported per condition: soleus/gastroc activation burst after the push, peak ankle angular
velocity during recovery, recovery time, and whether the model falls. Both limbs.
"""
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sto_utils import col, load_sto  # noqa: E402

RES = r"C:\Users\maurice\Documents\SCONE\results"
SCONECMD = r"C:\Program Files\SCONE\bin\sconecmd.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
PERT = os.path.join(HERE, "opt_pert")
GEN_CAP = 90

PUSH_T = 4.0        # single backward push, well into steady gait
PUSH_DUR = 0.1
PUSH_N = 100.0      # newtons, matching SCONE's own perturbation tutorial
WIN = 0.6           # seconds of response analysed after push onset

CONDS = {
    "HEALTHY": "DHEALTHY_s1", "PAR40": "DPAR40_s1", "PAR60": "DPAR60_s1",
    "SPAS005": "SPAS005", "SPAS01": "SPAS01", "MIX20S01": "MMIX20S01_s1",
}


def best_par(tag, gen_cap=GEN_CAP):
    ds = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)]
    if not ds:
        return None, None, None
    d = max(ds, key=os.path.getmtime)
    bp, bf, bg = None, 1e9, None
    for p in glob.glob(os.path.join(d, "0*.par")):
        b = os.path.basename(p)[:-4].split("_")
        try:
            g, f = int(b[0]), float(b[2])
        except Exception:
            continue
        if gen_cap is not None and g > gen_cap:
            continue
        if f < bf:
            bp, bf, bg = p, f, g
    return bp, bf, bg


def build(cond, src_scone, par):
    """Same scenario + same converged .par, with ONE unexpected push added at replay."""
    s = open(src_scone, encoding="utf-8", errors="ignore").read()
    pc = ('\n\t\t\tPerturbationController {\n'
          '\t\t\t\tname = Push\n'
          '\t\t\t\tstart_time = %.2f\n'
          '\t\t\t\tduration = %.2f\n'
          '\t\t\t\tinterval = 1000\n'          # once only, never repeats
          '\t\t\t\tforce = [ -%.1f 0 0 ]\n'
          '\t\t\t\tbody = torso\n'
          '\t\t\t\tposition_offset = [ 0 0.05 0 ]\n'
          '\t\t\t}\n' % (PUSH_T, PUSH_DUR, PUSH_N))
    if "CompositeController {" in s:
        s = s.replace("CompositeController {", "CompositeController {" + pc, 1)
    else:  # wrap a bare GaitStateController so the push can sit beside it
        s = s.replace("GaitStateController {",
                      "CompositeController {" + pc + "\n\t\t\tGaitStateController {", 1)
        # close the added CompositeController before the measure block
        i = s.rfind("}", 0, s.find("CompositeMeasure"))
        s = s[:i] + "}\n" + s[i:]
    s = re.sub(r"signature_prefix\s*=\s*\S+", "signature_prefix = P_" + cond, s, count=1)
    s = re.sub(r"init_file\s*=\s*\S+", "init_file = %s" % os.path.basename(par), s, count=1)
    p = os.path.join(PERT, "P_%s.scone" % cond)
    open(p, "w", encoding="utf-8").write(s)
    return p


def response(path):
    cols, d = load_sto(path)
    t = d[:, 0]
    out = {}
    i0 = int(np.searchsorted(t, PUSH_T))
    i1 = int(np.searchsorted(t, PUSH_T + WIN))
    if i1 <= i0 + 2:
        return None
    base0 = int(np.searchsorted(t, PUSH_T - 1.0))
    for side in ("l", "r"):
        ang = col(cols, d, "ankle_angle_%s" % side)
        if ang is None:
            return None
        ang = np.degrees(ang)
        vel = np.gradient(ang, t)
        seg, base = vel[i0:i1], vel[base0:i0]
        out["%s_vel_peak_post" % side] = float(np.max(np.abs(seg)))
        out["%s_vel_peak_base" % side] = float(np.max(np.abs(base))) if len(base) else float("nan")
        out["%s_ank_min_post" % side] = float(np.min(ang[i0:i1]))
        out["%s_ank_exc_post" % side] = float(np.max(ang[i0:i1]) - np.min(ang[i0:i1]))
        for mus in ("soleus", "gastroc", "tib_ant"):
            a = col(cols, d, "%s_%s.activation" % (mus, side))
            if a is None:
                continue
            out["%s_%s_post" % (mus, side)] = float(np.max(a[i0:i1]))
            out["%s_%s_base" % (mus, side)] = float(np.max(a[base0:i0])) if len(base) else float("nan")
    out["t_end"] = float(t[-1])
    out["fell"] = bool(t[-1] < PUSH_T + WIN)
    return out


def main():
    os.makedirs(PERT, exist_ok=True)
    out = {}
    for cond, tag in CONDS.items():
        par, fit, gen = best_par(tag)
        if par is None or fit >= 3.0:
            print("%-9s SKIP (fit=%s)" % (cond, fit))
            continue
        d = os.path.dirname(par)
        src = glob.glob(os.path.join(d, "*.scone"))
        if not src:
            print("%-9s no archived scenario" % cond)
            continue
        for aux in glob.glob(os.path.join(d, "*.osim")) + glob.glob(os.path.join(d, "*.zml")):
            dst = os.path.join(PERT, os.path.basename(aux))
            if not os.path.exists(dst):
                open(dst, "wb").write(open(aux, "rb").read())
        open(os.path.join(PERT, os.path.basename(par)), "wb").write(open(par, "rb").read())
        scen = build(cond, src[0], par)
        for old in glob.glob(os.path.join(PERT, "*.sto")):
            os.remove(old)
        try:
            subprocess.run([SCONECMD, "-e", scen], cwd=PERT, capture_output=True, timeout=600)
        except Exception:
            print("%-9s replay timeout" % cond)
            continue
        s = [x for x in glob.glob(os.path.join(PERT, "*.sto")) if os.path.getsize(x) > 1000]
        if len(s) != 1:
            print("%-9s %d sto files" % (cond, len(s)))
            continue
        r = response(s[0])
        if r is None:
            print("%-9s no usable response window" % cond)
            continue
        r.update(cond=cond, tag=tag, fitness=fit, gen=gen)
        out[cond] = r
        print("%-9s gen=%-3d  ankle vel peak: base %6.1f -> post-push %6.1f  "
              "soleus_l %.3f->%.3f  tib_ant_l %.3f->%.3f  %s"
              % (cond, gen, r.get("l_vel_peak_base", float('nan')),
                 r.get("l_vel_peak_post", float('nan')),
                 r.get("soleus_l_base", float('nan')), r.get("soleus_l_post", float('nan')),
                 r.get("tib_ant_l_base", float('nan')), r.get("tib_ant_l_post", float('nan')),
                 "FELL" if r["fell"] else ""))
    json.dump(out, open(os.path.join(HERE, "scone_perturbation.json"), "w"), indent=2)
    print("\nok %d / %d -> scone_perturbation.json" % (len(out), len(CONDS)))


if __name__ == "__main__":
    main()
