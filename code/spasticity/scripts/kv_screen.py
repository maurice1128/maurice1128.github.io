"""Find the KV range where a UNILATERAL spastic reflex still permits walking.

Rationale: real spastic patients walk. A KV that makes the model fall in ~3 s is not a
spastic-gait model, it is a broken model -- and CMA-ES re-optimization starting from such a
state has no gradient to follow (fitness pinned at the fall penalty ~93). So screen with the
FIXED healthy controller first to bracket the survivable range, then re-optimize just inside
and just above it (re-optimization should extend the range, since an adapted controller can
cope with more than the healthy one).

Unilateral (left) here -- matching the clinical target -- unlike the earlier bilateral probe.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, numpy as np
sys.path.insert(0, r"C:\Program Files\SCONE\scone\scenarios\SconePy")
from sconetools import sconepy
sconepy.set_log_level(4)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data"
CTRL0 = DATA + "/ControllerGH2010v9.scone"


def model_text(kv, weak=0.0):
    L = ["ModelOpenSim3 {",
         f'\tmodel_file = "{DATA}/H0914M_osim3.osim"',
         f'\tstate_init_file = "{DATA}/InitStateGait10.zml"',
         "\tfixed_control_step_size = 0.005",
         "\tintegration_accuracy = 0.002"]
    if weak > 0:
        L += ["\tProperties {",
              f"\t\ttib_ant_l {{ max_isometric_force.factor = {1.0-weak:.3f} }}", "\t}"]
    L += ["\tCompositeController {", f'\t\t<< "{CTRL0}" >>']
    if kv > 0:  # UNILATERAL (left) spastic velocity reflex
        L += ["\t\tReflexController {"]
        for m in ("soleus_l", "gastroc_l"):
            L += [f"\t\t\tMuscleReflex {{ target = {m} delay = 0.020 "
                  f"KV = {kv:.3f} allow_neg_V = 0 }}"]
        L += ["\t\t}"]
    L += ["\t}", "}"]
    p = os.path.join(HERE, "kv_screen_run.scone")
    open(p, "w").write("\n".join(L))
    return p.replace("\\", "/")


def rollout(kv, weak=0.0, T=8.0):
    m = sconepy.load_model(model_text(kv, weak))
    m.reset(); m.init_state_from_dofs()
    dof = {d.name(): d for d in m.dofs()}
    ankL = dof["ankle_angle_l"]
    ank = []
    for t in np.arange(0, T, 0.01):
        m.advance_simulation_to(float(t))
        ank.append(np.degrees(ankL.pos()))
        if m.com_pos().y < 0.4:
            break
    fell = m.com_pos().y < 0.4
    return dict(fell=fell, t=round(m.time(), 2), dx=round(m.com_pos().x, 2),
                ank_min=round(float(np.min(ank)), 1))


def main():
    print("UNILATERAL spastic reflex, FIXED healthy controller (screening only)")
    print(f"{'KV':>6s} {'fell':>5s} {'t':>5s} {'dx':>6s} {'ank_min':>8s}   verdict")
    for kv in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0):
        r = rollout(kv)
        ok = (not r["fell"]) or r["t"] >= 7.0
        print(f"{kv:>6.2f} {str(r['fell']):>5s} {r['t']:>5} {r['dx']:>6} "
              f"{r['ank_min']:>8}   {'WALKS' if ok else 'falls'}")
    print("\nUse the largest KV that still WALKS as the top of the optimization grid;\n"
          "re-optimization should extend it somewhat above that.")


if __name__ == "__main__":
    main()
