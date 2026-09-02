# -*- coding: utf-8 -*-
"""r610: reconstruct sagittal joint centres from archived simulation output, for animation.

The .sto files report each body's centre of mass and its orientation quaternion, not its joint
centres. A joint centre is the one point that is fixed in the local frames of BOTH bodies it
connects, so it can be solved for from the trajectory alone without reading the model file: for
every frame, p_A + R_A a = p_B + R_B b, which is linear in the two local offsets a and b. This is
the SCoRE estimator. The residual it leaves is reported rather than assumed, because a large one
would mean the assumption of a fixed centre is wrong.

Nothing here is a new result. It reproduces the geometry already in the archived output so that the
gait can be drawn.
"""
import glob, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
SETTLE, T1 = 1.0, 9.73
CHAIN = [("pelvis", "femur_l", "hip"), ("femur_l", "tibia_l", "knee"),
         ("tibia_l", "calcn_l", "ankle"),
         ("pelvis", "femur_r", "hip_r"), ("femur_r", "tibia_r", "knee_r"),
         ("tibia_r", "calcn_r", "ankle_r")]


def quat_R(w, x, y, z):
    """Rotation matrices from quaternion arrays, shape (n, 3, 3)."""
    n = np.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / n, x / n, y / n, z / n
    R = np.empty((len(w), 3, 3))
    R[:, 0, 0] = 1 - 2 * (y * y + z * z); R[:, 0, 1] = 2 * (x * y - z * w); R[:, 0, 2] = 2 * (x * z + y * w)
    R[:, 1, 0] = 2 * (x * y + z * w); R[:, 1, 1] = 1 - 2 * (x * x + z * z); R[:, 1, 2] = 2 * (y * z - x * w)
    R[:, 2, 0] = 2 * (x * z - y * w); R[:, 2, 1] = 2 * (y * z + x * w); R[:, 2, 2] = 1 - 2 * (x * x + y * y)
    return R


def body(c, dat, b):
    p = np.c_[S.col(c, dat, b + ".pos.x"), S.col(c, dat, b + ".pos.y"), S.col(c, dat, b + ".pos.z")]
    R = quat_R(S.col(c, dat, b + ".ori.w"), S.col(c, dat, b + ".ori.x"),
               S.col(c, dat, b + ".ori.y"), S.col(c, dat, b + ".ori.z"))
    return p, R


def score(pA, RA, pB, RB):
    """Least-squares joint centre: returns local offsets and the RMS closure residual in metres."""
    n = len(pA)
    A = np.zeros((3 * n, 6)); y = np.zeros(3 * n)
    A[:, :3] = RA.reshape(3 * n, 3)
    A[:, 3:] = -RB.reshape(3 * n, 3)
    y[:] = (pB - pA).reshape(3 * n)
    sol, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = np.sqrt(np.mean((A @ sol - y) ** 2))
    return sol[:3], sol[3:], res


def latest_sto(fam, seed):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, seed))) if os.path.isdir(d)]
    if not g:
        return None
    g = max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))
    st = sorted(glob.glob(os.path.join(g, "*.par.sto")))
    return st[-1] if st else None


def skeleton(fam, seed=101):
    """Sagittal joint-centre trajectories plus the signals the animation annotates."""
    f = latest_sto(fam, seed)
    if f is None:
        return None
    c, dat = S.load_sto(f)
    t = dat[:, 0]
    m = (t >= SETTLE) & (t <= T1)
    if m.sum() < 50:
        return None
    bodies = {}
    for b in ["pelvis", "torso", "femur_l", "tibia_l", "calcn_l", "femur_r", "tibia_r", "calcn_r"]:
        p, R = body(c, dat, b)
        bodies[b] = (p[m], R[m])
    joints, resid = {}, {}
    for a, b, name in CHAIN:
        pA, RA = bodies[a]; pB, RB = bodies[b]
        oa, ob, r = score(pA, RA, pB, RB)
        joints[name] = pA + np.einsum("nij,j->ni", RA, oa)
        resid[name] = r
    # foot: heel and toe drawn from the calcaneus frame, so the ankle angle shown is the real one
    for side, cal in (("", "calcn_l"), ("_r", "calcn_r")):
        p, R = bodies[cal]
        joints["toe" + side] = p + np.einsum("nij,j->ni", R, np.array([0.16, -0.02, 0.0]))
        joints["heel" + side] = p + np.einsum("nij,j->ni", R, np.array([-0.06, -0.02, 0.0]))
    joints["pelvis"] = bodies["pelvis"][0]
    joints["neck"] = bodies["torso"][0] + np.einsum("nij,j->ni", bodies["torso"][1],
                                                    np.array([0.0, 0.25, 0.0]))
    out = {"t": t[m], "joints": joints, "residual_m": resid,
           "ankle_deg": np.degrees(S.col(c, dat, "ankle_angle_l")[m]),
           "knee_deg": np.degrees(S.col(c, dat, "knee_angle_l")[m]),
           "hip_deg": np.degrees(S.col(c, dat, "hip_flexion_l")[m]),
           "t_end": float(t[-1]), "sto": f}
    for mus in ["tib_ant_l", "soleus_l", "gastroc_l"]:
        out[mus] = S.col(c, dat, mus + ".activation")[m]
    out["act"] = {n[:-len(".activation")]: dat[m, i] for i, n in enumerate(c)
                  if n.endswith(".activation")}
    out["body"] = {}
    for b in ["pelvis", "torso", "femur_l", "tibia_l", "calcn_l",
              "femur_r", "tibia_r", "calcn_r"]:
        p, R = body(c, dat, b)
        out["body"][b] = (p[m], R[m])
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    out["heel_strikes_s"] = [float(t[i]) for i in hs if SETTLE <= t[i] <= T1]
    return out


if __name__ == "__main__":
    for fam in ["R151C", "R151S", "R396SPg120", "R151W", "R169W095"]:
        s = skeleton(fam)
        if s is None:
            print("%-12s no usable output" % fam); continue
        r = s["residual_m"]
        print("%-12s t_end %5.2f s  cycles %d  SCoRE residual hip %.1f mm knee %.1f mm ankle %.1f mm"
              % (fam, s["t_end"], len(s["heel_strikes_s"]) - 1,
                 1000 * r["hip"], 1000 * r["knee"], 1000 * r["ankle"]))
