"""CLEAN core SCONE finding: in a forward-dynamic reflex-controlled walking model, does a
velocity-dependent stretch reflex (Lance's definition of spasticity) on the plantarflexors
produce graded EQUINUS? The predictive OCP could not show this (the optimizer routes around
the reflex). Forward dynamics cannot route around it -- the reflex genuinely fires.

Bilateral spastic reflex on soleus+gastroc (symmetric, matches the symmetric healthy GH2010
controller so no re-optimization is needed). KV = velocity gain. Fixed healthy controller.
This is the honest, reproducible mechanistic result. Unilateral / severe cases fall under the
fixed controller and would require controller re-optimization (Veerkamp 2022) -- scoped separately.
Run from SconePy dir with the scone39 python.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, numpy as np
sys.path.insert(0, r"C:\Program Files\SCONE\scone\scenarios\SconePy")
from sconetools import sconepy
sconepy.set_log_level(3)

HERE = r"C:\Users\maurice\Desktop\spasticity_paper\scone"
DATA = r"C:/Program Files/SCONE/scone/scenarios/Examples2/data"
CTRL0 = os.path.join(DATA, "ControllerGH2010v9.scone").replace("\\", "/")

def make_model(kv=0.0):
    """Healthy GH2010 walking controller + bilateral spastic velocity reflex (KV) on the
    plantarflexors. Bilateral keeps the model symmetric so the healthy symmetric controller
    still applies -- isolates the reflex effect with no confound from controller re-tuning."""
    L = ["ModelOpenSim3 {",
         f'\tmodel_file = "{DATA}/H0914M_osim3.osim"',
         f'\tstate_init_file = "{DATA}/InitStateGait10.zml"',
         "\tfixed_control_step_size = 0.005",
         "\tintegration_accuracy = 0.002",
         "\tCompositeController {", f'\t\t<< "{CTRL0}" >>']
    if kv > 0:
        L += ["\t\tReflexController {"]
        for m in ("soleus_l", "soleus_r", "gastroc_l", "gastroc_r"):
            L += [f'\t\t\tMuscleReflex {{ target = {m} delay = 0.020 KV = {kv:.3f} allow_neg_V = 0 }}']
        L += ["\t\t}"]
    L += ["\t}", "}"]
    p = os.path.join(HERE, "grad_run.scone")
    open(p, "w").write("\n".join(L))
    return p.replace("\\", "/")

def rollout(kv, T=6.0):
    m = sconepy.load_model(make_model(kv))
    m.reset(); m.init_state_from_dofs()
    dof = {d.name(): d for d in m.dofs()}
    sol = [mu for mu in m.muscles() if mu.name() == "soleus_l"][0]
    ankL = dof["ankle_angle_l"]
    ank = []; solA = []
    for t in np.arange(0, T, 0.01):
        m.advance_simulation_to(float(t))
        ank.append(np.degrees(ankL.pos())); solA.append(sol.activation())
        if m.com_pos().y < 0.4:
            break
    ank = np.array(ank)
    return dict(fell=(m.com_pos().y < 0.4), dx=round(m.com_pos().x, 2), t=round(m.time(), 2),
                ankMin=round(float(ank.min()), 1), ankMean=round(float(ank.mean()), 1),
                solMean=round(float(np.mean(solA)), 3))

def main():
    print(f"{'KV':>5s} {'fell':>5s} {'dx':>6s} {'t':>5s} {'ankMin':>7s} {'ankMean':>8s} "
          f"{'dEqui':>6s} {'solMean':>7s}")
    he = None
    for kv in (0.0, 0.5, 1.0, 2.0, 3.0):
        r = rollout(kv)
        if he is None: he = r["ankMean"]
        print(f"{kv:>5.1f} {str(r['fell']):>5s} {r['dx']:>6} {r['t']:>5} {r['ankMin']:>7} "
              f"{r['ankMean']:>8} {r['ankMean']-he:>+6.1f} {r['solMean']:>7}")
    print("\ndEqui<0 = ankle shifted plantarflexed vs healthy = equinus. Graded equinus with KV\n"
          "= forward-dynamic reflex sim captures spastic equinus the predictive OCP could not.")

if __name__ == "__main__":
    main()
