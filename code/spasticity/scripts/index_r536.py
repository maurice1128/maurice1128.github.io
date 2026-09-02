# -*- coding: utf-8 -*-
"""r536: define the two-readout index, and test it rather than assert it.

What the corpus permits and forbids is now known. Plantarflexor overactivity is gradeable from gait:
peak swing dorsiflexion recovers delivered reflex gain with R2 0.946 (PAIR_r533, step 1). Dorsiflexor
weakness is not: no single readout and no combination recovers its magnitude, every leave-one-level-out
R2 being negative (PAIR_r533). An index that claims to return both numbers would be claiming
something this corpus says is false.

So the index returns one graded number and one categorical statement, and this script measures both:

  T, a tone score          = control mean minus the patient's peak swing dorsiflexion.
  D, a direction call      = which side of the control mean the knee at contact sits on.

Three things are tested, all leave-one-FAMILY-out so a family never trains on itself:

  (a) does T rank tone severity? Spearman against delivered gain, and the residual scatter in
      degrees, which is what sets a usable threshold.
  (b) does adding the second reading improve CLASSIFICATION? PAIR_r533 showed the pair fails to
      recover weakness MAGNITUDE by regression. Classification is a different question and has not
      been asked. One dimension is compared with two.
  (c) what threshold on T separates the arms, and how far is it from the measurement error a real
      laboratory brings (ref [15], ICC 0.941, MDC 4.9 deg on treadmill, implying SEM 1.77 deg)?
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEM_LAB = 4.9 / (1.96 * math.sqrt(2.0))          # ref [15], peak ankle angle in swing
CTRL = [("R151C", None)]
HY = [("R151S", 0.100), ("R393SPg070", 0.140), ("R393SPg100", 0.200),
      ("R396SPg110", 0.220), ("R396SPg120", 0.240)]
WK = [("R151W", 0.80), ("R174W870", 0.87), ("R174W892", 0.892),
      ("R169W090", 0.90), ("R174W915", 0.915), ("R169W095", 0.95)]


def load(fam, sd):
    g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
    if not g:
        return None
    g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
    st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
    if not st:
        return None
    c, dat = S.load_sto(st[-1])
    if dat.size == 0:
        return None
    t = dat[:, 0]
    grf, thr = S.grf_vertical(c, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    w = [x for x in allc if t[x[1]] <= T1]
    w = w[:-1] if len(w) >= 2 else w
    if float(t[-1]) < T1 or len(w) < 5:
        return None
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    on = grf > thr
    pk = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        if idx.size:
            pk.append(float(np.max(an[a:b][idx])))
    if not pk:
        return None
    return {"A": float(np.mean(pk)), "B": float(np.mean([kn[a] for a, _ in w]))}


cells = []
for grp, fams in (("C", CTRL), ("H", HY), ("W", WK)):
    for f, dose in fams:
        for sd in range(101, 107):
            r = load(f, sd)
            if r:
                r.update({"fam": f, "arm": grp, "dose": dose, "seed": sd})
                cells.append(r)
print("cells: %s" % {g: sum(1 for c in cells if c["arm"] == g) for g in "CHW"})

C = [c for c in cells if c["arm"] == "C"]
H = [c for c in cells if c["arm"] == "H"]
W = [c for c in cells if c["arm"] == "W"]
A0 = float(np.mean([c["A"] for c in C]))
B0 = float(np.mean([c["B"] for c in C]))
print("control reference: A0 = %.3f deg (peak swing dorsiflexion), B0 = %.3f deg (knee at contact)"
      % (A0, B0))

# ---- (a) does T rank tone severity? ------------------------------------------------------------
print("\n(a) tone score T = A0 - A, against delivered reflex gain")
T = [(c["dose"], A0 - c["A"]) for c in H]


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


rho = spearman([x for x, _ in T], [y for _, y in T])
fit = np.polyfit([y for _, y in T], [x for x, _ in T], 1)
pred = np.polyval(fit, [y for _, y in T])
resid = np.array([x for x, _ in T]) - pred
print("   Spearman rho = %+.4f over %d hyperreflexia cells" % (rho, len(T)))
for f, dose in HY:
    v = [A0 - c["A"] for c in H if c["fam"] == f]
    if v:
        print("   KV %.3f   T = %6.3f +- %.3f deg" % (dose, np.mean(v), np.std(v, ddof=1) if len(v) > 1 else 0))
# leave-one-family-out calibration error, in gain units and in degrees of T
lofo_res = []
for f, dose in HY:
    tr = [(c["dose"], A0 - c["A"]) for c in H if c["fam"] != f]
    te = [(c["dose"], A0 - c["A"]) for c in H if c["fam"] == f]
    if len(set(d for d, _ in tr)) < 2 or not te:
        continue
    ff = np.polyfit([y for _, y in tr], [x for x, _ in tr], 1)
    lofo_res += [x - np.polyval(ff, y) for x, y in te]
print("   leave-one-family-out gain error: RMSE %.4f over a %.3f-wide ladder (%.1f%% of the range)"
      % (float(np.sqrt(np.mean(np.square(lofo_res)))), 0.240 - 0.100,
         100 * float(np.sqrt(np.mean(np.square(lofo_res)))) / (0.240 - 0.100)))

# ---- (b) one reading or two, for CLASSIFICATION ------------------------------------------------
print("\n(b) classification of the arm, leave-one-family-out; PAIR_r533 showed two readings fail to")
print("    recover weakness MAGNITUDE, which is a different question from this one")
FEATS = {"A only (peak swing dorsiflexion)": lambda c: [c["A"]],
         "B only (knee at contact)": lambda c: [c["B"]],
         "A and B": lambda c: [c["A"], c["B"]]}
lab = {"H": 0, "W": 1}
res_b = {}
for nm, g in FEATS.items():
    ok = 0
    tot = 0
    for f, _ in HY + WK:
        te = [c for c in H + W if c["fam"] == f]
        tr = [c for c in H + W if c["fam"] != f]
        if not te or len(set(c["arm"] for c in tr)) < 2:
            continue
        X = np.array([g(c) for c in tr])
        y = np.array([lab[c["arm"]] for c in tr])
        m0, m1 = X[y == 0].mean(axis=0), X[y == 1].mean(axis=0)
        cov = np.cov(X.T).reshape(len(m0), len(m0)) + 1e-9 * np.eye(len(m0))
        wv = np.linalg.solve(cov, m1 - m0)
        thr = 0.5 * (m0 + m1).dot(wv)
        for c in te:
            ok += ((np.array(g(c)).dot(wv) > thr) == (lab[c["arm"]] == 1))
            tot += 1
    res_b[nm] = ok / tot
    print("   %-34s %d of %d = %.1f%%" % (nm, ok, tot, 100 * ok / tot))
base = max(len(H), len(W)) / float(len(H) + len(W))
print("   %-34s %.1f%%" % ("majority-class baseline", 100 * base))

# ---- (c) the threshold, against a real laboratory's error ---------------------------------------
print("\n(c) the threshold on T, and what a laboratory's measurement error does to it")
Th = [A0 - c["A"] for c in H]
Tw = [A0 - c["A"] for c in W]
thr = 0.5 * (max(Tw) + min(Th))
print("   weakness cells   T in [%.3f, %.3f]" % (min(Tw), max(Tw)))
print("   hyperreflexia    T in [%.3f, %.3f]" % (min(Th), max(Th)))
print("   separating threshold T = %.3f deg, margin to the nearer arm %.3f deg" % (thr, min(Th) - thr))
print("   one laboratory session's SEM on this variable is %.3f deg (ref [15]); the margin is "
      "%.2f SEM" % (SEM_LAB, (min(Th) - thr) / SEM_LAB))
print("   NOTE the margin is between SIMULATED lesion arms with no between-patient variance in it. "
      "Against the spread a stroke population presents this is the 22.7%% figure of SWINGDF_r525, "
      "not this margin.")

dep = {
 "id": "INDEX_r536",
 "why": ("The corpus permits a graded tone readout and forbids a graded weakness readout. This "
         "defines an index that returns only what is permitted, and measures it rather than "
         "asserting it."),
 "definition": {
    "inputs": "one instrumented gait recording of the paretic side, at least five clean cycles",
    "A": "peak ankle dorsiflexion during swing, mean over cycles, degrees, dorsiflexion positive",
    "B": "knee flexion angle at initial contact, mean over cycles, degrees",
    "reference": "A0 and B0 from the laboratory's own unimpaired controls",
    "tone_score_T": "A0 - A; larger means more plantarflexor overactivity",
    "direction_call_D": "only interpreted when T is below the tone threshold: knee extended "
                        "relative to B0 indicates the weakness pattern",
    "what_it_does_NOT_return": "a graded weakness magnitude. No readout or combination in this "
                               "corpus recovers it (PAIR_r533: every leave-one-level-out R2 "
                               "negative). A strength measurement is required and cannot be "
                               "substituted by gait"},
 "control_reference_deg": {"A0": A0, "B0": B0},
 "tone_score": {"spearman_rho_vs_delivered_gain": rho,
                "lofo_gain_RMSE": float(np.sqrt(np.mean(np.square(lofo_res)))),
                "ladder_width": 0.240 - 0.100,
                "by_dose": {str(d): float(np.mean([A0 - c["A"] for c in H if c["fam"] == f]))
                            for f, d in HY if [c for c in H if c["fam"] == f]}},
 "classification_lofo": res_b, "majority_baseline": base,
 "threshold": {"T_threshold_deg": thr, "margin_deg": min(Th) - thr,
               "laboratory_SEM_deg": SEM_LAB, "margin_in_SEM": (min(Th) - thr) / SEM_LAB,
               "CAVEAT": "this margin contains no between-patient variance. Against the spread a "
                         "stroke population presents, the relevant figure is the 22.7 per cent "
                         "misclassification of SWINGDF_r525"},
}
io.open(os.path.join(P, "INDEX_r536.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> INDEX_r536.json")
