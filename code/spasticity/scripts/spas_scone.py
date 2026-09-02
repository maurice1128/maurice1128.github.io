"""SCONE forward-dynamics spasticity: does adding a velocity stretch-reflex to the
plantarflexors produce equinus in a reflex-controlled WALKING model? (Forward dynamics =
the reflex genuinely fires; the OCP could not do this.)
Builds controller variants (healthy / spastic KV / ...) + records affected ankle.
Run from SconePy dir with the scone39 python.
"""
import warnings; warnings.filterwarnings("ignore")
import os, re, sys, numpy as np
sys.path.insert(0, r"C:\Program Files\SCONE\scone\scenarios\SconePy")
from sconetools import sconepy
sconepy.set_log_level(5)

HERE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
DATA = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data"
CTRL0 = os.path.join(DATA, "ControllerGH2010v9.scone").replace("\\", "/")

def make_model(kv=0.0, weak=0.0):
    """Model .scone: healthy GH2010 walking controller (symmetric) + optional UNILATERAL
    left-side spastic velocity reflex (KV on soleus_l/gastroc_l) + optional left dorsiflexor
    weakness (tib_ant_l force factor). Affected side = left (stroke)."""
    L = ["ModelOpenSim3 {",
         f'\tmodel_file = "{DATA}/H0914M_osim3.osim"',
         f'\tstate_init_file = "{DATA}/InitStateGait10.zml"',
         "\tfixed_control_step_size = 0.005",
         "\tintegration_accuracy = 0.002"]
    if weak > 0:
        L += ["\tProperties {", f'\t\ttib_ant_l {{ max_isometric_force.factor = {1.0-weak:.3f} }}', "\t}"]
    # controller: composite of the healthy GH2010 + (optional) unilateral spastic reflex
    L += ["\tCompositeController {", f'\t\t<< "{CTRL0}" >>']
    if kv > 0:
        L += ["\t\tReflexController {",
              f'\t\t\tMuscleReflex {{ target = soleus_l delay = 0.020 KV = {kv:.3f} allow_neg_V = 0 }}',
              f'\t\t\tMuscleReflex {{ target = gastroc_l delay = 0.020 KV = {kv:.3f} allow_neg_V = 0 }}',
              "\t\t}"]
    L += ["\t}", "}"]
    p = os.path.join(HERE, "model_run.scone")
    open(p, "w").write("\n".join(L))
    return p.replace("\\", "/")

def rollout(model_scone, T=4.0):
    m = sconepy.load_model(model_scone)
    m.reset(); m.init_state_from_dofs()
    dof = {d.name(): d for d in m.dofs()}
    sol = [mu for mu in m.muscles() if mu.name() == "soleus_l"][0]
    ankL = dof["ankle_angle_l"]
    ank = []; solA = []
    for t in np.arange(0, T, 0.01):
        m.advance_simulation_to(t)
        ank.append(np.degrees(ankL.pos())); solA.append(sol.activation())
        if m.com_pos().y < 0.4:
            break
    ank = np.array(ank)
    return dict(fell=(m.com_pos().y < 0.4), dx=round(m.com_pos().x, 2), t=round(m.time(), 2),
                ankMin=round(float(ank.min()), 1), ankMax=round(float(ank.max()), 1),
                ankMean=round(float(ank.mean()), 1), solMean=round(float(np.mean(solA)), 3))

def main():
    print(f"{'cond':16s} {'fell':>5s} {'dx':>5s} {'t':>4s} {'ankMin':>7s} {'ankMean':>8s} {'dMean':>6s} {'solMean':>7s}")
    he = None
    for name, kv, w in [("healthy", 0, 0), ("spastic_kv1", 1, 0), ("spastic_kv2", 2, 0),
                        ("weak0.5", 0, 0.5), ("weak0.7", 0, 0.7), ("mixed", 1, 0.5)]:
        mdl = make_model(kv, w)
        r = rollout(mdl)
        if he is None: he = r["ankMean"]
        print(f"{name:16s} {str(r['fell']):>5s} {r['dx']:>5} {r['t']:>4} "
              f"{r['ankMin']:>7} {r['ankMean']:>8} {r['ankMean']-he:>+6.1f} {r['solMean']:>7}")
    print("\n(equinus = lower/more-negative ankle. If spastic shifts the ankle plantarflexed vs\n"
          " healthy in this forward reflex gait, SCONE captured what the OCP could not.)")

if __name__ == "__main__":
    main()
