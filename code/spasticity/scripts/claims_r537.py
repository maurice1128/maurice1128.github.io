# -*- coding: utf-8 -*-
"""r537: the three claims a clinician would care about, each scored clean and under motion capture.

A paper offering a gait readout to a clinic is making at most three separate claims, and they are
not equally supportable. They are separated here and each is measured on every candidate readout,
twice: on the noise-free simulation, and under the measurement error a gait laboratory brings.

  CLAIM 1  healthy from lesioned.        control cells against all lesion cells.
  CLAIM 2  hyperreflexia from weakness.  the two arms, leave-one-FAMILY-out so no family trains on
                                         itself.
  CLAIM 3  severity.                     the rank correlation of the readout with the dose actually
                                         delivered, computed inside each arm separately, because a
                                         readout can order one lesion and be blind to the other --
                                         and PAIR_r533 says that is exactly what happens.

The motion-capture model is VIDEOKNEE_r422's, unchanged: per-frame Gaussian jitter, frame-rate
resampling, out-of-plane yaw, and event-frame error. Peaks and points are affected differently -- a
mean over cycles divides zero-mean jitter by sqrt(n), a maximum rectifies it upward -- so the two
kinds are reported separately rather than pooled.
"""
import glob, io, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73
SEED, N_REP = 20260830, 60
SIGMAS = [0.0, 1.0, 2.0, 3.0]
FS, YAW, KMAX = 100, 10, 1
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
    on = grf > thr
    kn = np.degrees(S.col(c, dat, "knee_angle_l"))
    an = np.degrees(S.col(c, dat, "ankle_angle_l"))
    cy = []
    for a, b in w:
        idx = np.where(~on[a:b])[0]
        cy.append({"knee": kn[a:b], "ankle": an[a:b], "dur": float(t[b] - t[a]),
                   "swing": (int(idx[0]), int(idx[-1])) if idx.size else None})
    return cy


def pct(j, p):
    def f(nk, na, sw, ke):
        y = nk if j == "knee" else na
        return float(y[int(np.clip(round(p / 100.0 * (len(y) - 1)) + ke, 0, len(y) - 1))])
    return f


def win(j, lo, hi):
    def f(nk, na, sw, ke):
        y = nk if j == "knee" else na
        a = int(np.clip(round(lo / 100.0 * (len(y) - 1)) + ke, 0, len(y) - 2))
        b = int(np.clip(round(hi / 100.0 * (len(y) - 1)) + ke, a + 1, len(y) - 1))
        return float(np.mean(y[a:b + 1]))
    return f


def swpk(nk, na, sw, ke):
    if sw is None:
        return float("nan")
    a = int(np.clip(sw[0] + ke, 0, len(na) - 2))
    b = int(np.clip(sw[1] + ke, a + 1, len(na) - 1))
    return float(np.max(na[a:b]))


CANDS = [("knee at contact  [current]", pct("knee", 0), "point"),
         ("ankle at 45%", pct("ankle", 45), "point"),
         ("ankle 40-50% window", win("ankle", 40, 50), "window"),
         ("ankle at 85%", pct("ankle", 85), "point"),
         ("ankle peak in swing", swpk, "peak")]

print("loading ...")
DATA = []
for grp, fams in (("C", CTRL), ("H", HY), ("W", WK)):
    for f, dose in fams:
        for sd in range(101, 107):
            cy = load(f, sd)
            if cy:
                DATA.append({"fam": f, "arm": grp, "dose": dose, "cy": cy})
print("cells: %s" % {g: sum(1 for d in DATA if d["arm"] == g) for g in "CHW"})


def value(d, fn, sigma, rng):
    out = []
    for cy in d["cy"]:
        n = max(10, int(round(cy["dur"] * FS)))
        g = np.linspace(0, 1, n)
        s = np.linspace(0, 1, len(cy["knee"]))
        # NOTE: with a planar trace this is a uniform multiplicative scale, so it cannot change a
        # rank, a refitted threshold or a classification. It is retained for comparability with
        # VIDEOKNEE_r422 and is reported as inert rather than as a stressor.
        k = math.cos(math.radians(YAW))
        nk = np.interp(g, s, cy["knee"]) * k
        na = np.interp(g, s, cy["ankle"]) * k
        if sigma > 0:
            nk = nk + rng.normal(0, sigma, n)
            na = na + rng.normal(0, sigma, n)
        sw = None
        if cy["swing"]:
            sc = len(cy["knee"]) - 1.0
            sw = (int(cy["swing"][0] / sc * (n - 1)), int(cy["swing"][1] / sc * (n - 1)))
        ke = int(rng.integers(-KMAX, KMAX + 1)) if KMAX else 0
        out.append(fn(nk, na, sw, ke))
    v = [x for x in out if not math.isnan(x)]
    return float(np.mean(v)) if v else float("nan")


def loo1(pos, neg):
    """leave-one-out detection of a lesion, scored as balanced accuracy.

    As first written this used one threshold and a direction. That cannot work for a two-sided
    readout: on knee-at-contact the control sits BETWEEN the two arms, so no single cut separates it
    from both, and the test returned figures below chance for structural reasons rather than
    substantive ones. Detection asks whether a reading is FAR FROM normal, so the statistic is the
    distance from the control mean. Accuracy is balanced because 59 lesion cells against 6 controls
    would otherwise be won by always answering 'lesioned'.
    """
    lab = [(v, 1) for v in pos] + [(v, 0) for v in neg]
    tp = tn = np_ = nn = 0
    for i in range(len(lab)):
        r = lab[:i] + lab[i + 1:]
        c0 = float(np.mean([v for v, l in r if l == 0]))
        d = sorted(abs(v - c0) for v, l in r if l == 0)
        dl = sorted(abs(v - c0) for v, l in r if l == 1)
        th = 0.5 * (d[-1] + dl[0]) if dl[0] > d[-1] else 0.5 * (np.mean(d) + np.mean(dl))
        pred = 1 if abs(lab[i][0] - c0) > th else 0
        if lab[i][1] == 1:
            np_ += 1
            tp += (pred == 1)
        else:
            nn += 1
            tn += (pred == 0)
    return 0.5 * (tp / np_ + tn / nn) if np_ and nn else float("nan")


def loo1_by_arm(H, W, C):
    """detection scored separately for each arm, with the threshold HELD OUT.

    As first written this fitted the threshold on the same arm cells it then classified, so a
    separated arm scored 1.000 by construction. Each cell is now scored by a threshold built from
    the control cells and from the OTHER cells of its own arm, never from itself.
    """
    out = {}
    for nm, arm in (("hyper", H), ("weak", W)):
        hits = 0
        for i in range(len(arm)):
            rest = arm[:i] + arm[i + 1:]
            if not rest:
                continue
            c0 = float(np.mean(C))
            d = [abs(v - c0) for v in C]
            dl = [abs(v - c0) for v in rest]
            th = (0.5 * (max(d) + min(dl))) if min(dl) > max(d)                 else 0.5 * (float(np.mean(d)) + float(np.mean(dl)))
            hits += (abs(arm[i] - c0) > th)
        out[nm] = hits / float(len(arm)) if arm else float("nan")
    return out


def lofo(vals):
    """leave-one-FAMILY-out arm classification"""
    ok = tot = 0
    for f, _ in HY + WK:
        te = [(v, a) for v, a, g in vals if g == f]
        tr = [(v, a) for v, a, g in vals if g != f]
        if not te or len(set(a for _, a in tr)) < 2:
            continue
        mh = np.mean([v for v, a in tr if a == "H"])
        mw = np.mean([v for v, a in tr if a == "W"])
        th, sgn = 0.5 * (mh + mw), (1 if mh < mw else -1)
        for v, a in te:
            ok += ((("H" if sgn * v < sgn * th else "W")) == a)
            tot += 1
    return ok / tot if tot else float("nan")


def spear(x, y):
    if len(set(x)) < 2:
        return float("nan")
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


RES_ = {}
print("\n%-28s %-6s %-7s %-9s %-9s %-11s %s"
      % ("readout", "kind", "sigma", "C1 sick", "C2 arm", "C3 tone rho", "C3 weakness rho"))
for name, fn, kind in CANDS:
    RES_[name] = {"kind": kind, "by_sigma": {}}
    for sg in SIGMAS:
        rng = np.random.default_rng(SEED)
        reps = 1 if sg == 0 else N_REP
        c1, c2, r3h, r3w, c1h, c1w = [], [], [], [], [], []
        for _ in range(reps):
            vals = [(value(d, fn, sg, rng), d["arm"], d["fam"], d["dose"]) for d in DATA]
            vals = [v for v in vals if not math.isnan(v[0])]
            C = [v for v, a, f, dd in vals if a == "C"]
            L = [v for v, a, f, dd in vals if a != "C"]
            H = [(v, dd) for v, a, f, dd in vals if a == "H"]
            W = [(v, dd) for v, a, f, dd in vals if a == "W"]
            if not (C and L and H and W):
                continue
            c1.append(loo1(L, C))
            ba = loo1_by_arm([v for v, _ in H], [v for v, _ in W], C)
            c1h.append(ba["hyper"]); c1w.append(ba["weak"])
            c2.append(lofo([(v, a, f) for v, a, f, dd in vals if a != "C"]))
            # signed, not absolute: a reversal is not a success, and |rho| has a positive null
            # floor (E|rho| ~ 0.14 at n = 36) that reads as partial recovery when it is not
            r3h.append(spear([d for _, d in H], [v for v, _ in H]))
            r3w.append(spear([d for _, d in W], [v for v, _ in W]))
        RES_[name]["by_sigma"][str(sg)] = {
            "claim1_lesioned_vs_control_acc": float(np.mean(c1)),
            "claim1_detect_hyper": float(np.mean(c1h)),
            "claim1_detect_weak": float(np.mean(c1w)),
            "claim2_arm_lofo_acc": float(np.mean(c2)),
            "claim3_tone_severity_rho": float(np.mean(r3h)),
            "claim3_weakness_severity_rho": float(np.mean(r3w))}
        r = RES_[name]["by_sigma"][str(sg)]
        print("%-28s %-6s %-7g %-9.3f %-7.3f %-7.3f %-9.3f %-11.3f %.3f"
              % (name if sg == 0 else "", kind if sg == 0 else "", sg,
                 r["claim1_lesioned_vs_control_acc"], r["claim1_detect_hyper"],
                 r["claim1_detect_weak"], r["claim2_arm_lofo_acc"],
                 r["claim3_tone_severity_rho"], r["claim3_weakness_severity_rho"]))

print("\nat a realistic 3 deg of per-frame jitter, ranked by the weakest of the three claims:")
rank = sorted(RES_.items(),
              key=lambda kv: -min(kv[1]["by_sigma"]["3.0"]["claim1_lesioned_vs_control_acc"],
                                  kv[1]["by_sigma"]["3.0"]["claim2_arm_lofo_acc"],
                                  kv[1]["by_sigma"]["3.0"]["claim3_tone_severity_rho"]))
for n, v in rank:
    r = v["by_sigma"]["3.0"]
    print("   %-28s sick %.3f  arm %.3f  tone rho %.3f  |  weakness rho %.3f"
          % (n, r["claim1_lesioned_vs_control_acc"], r["claim2_arm_lofo_acc"],
             r["claim3_tone_severity_rho"], r["claim3_weakness_severity_rho"]))

io.open(os.path.join(P, "CLAIMS_r537.json"), "w", encoding="utf-8", newline="").write(json.dumps({
 "id": "CLAIMS_r537",
 "why": ("A paper offering a gait readout to a clinic makes at most three claims and they are not "
         "equally supportable. They are separated here and each is measured on every candidate, "
         "clean and under the measurement error a gait laboratory brings."),
 "claims": {"1": "lesioned distinguished from unimpaired control (leave-one-out)",
            "2": "hyperreflexia distinguished from weakness (leave-one-FAMILY-out)",
            "3": "severity ordered within each arm separately (Spearman against delivered dose)"},
 "motion_capture_model": {"from": "VIDEOKNEE_r422", "fs_hz": FS, "yaw_deg": YAW,
                          "event_error_frames": KMAX, "jitter_sigma_deg": SIGMAS,
                          "n_rep": N_REP, "rng_seed": SEED},
 "results": RES_}, indent=1, ensure_ascii=False))
print("\n-> CLAIMS_r537.json")
