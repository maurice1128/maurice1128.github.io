# -*- coding: utf-8 -*-
"""r539: does the model's UNLESIONED ankle trajectory look like normal human gait?

The manuscript certifies the model's knee against normal adult values -- contact flexion 7.85 deg,
swing peak 64.6 deg -- and reports both as inside the normal range. It never does this for the
ankle. That was tolerable while the endpoint was a knee angle. It is not tolerable now that the
candidate readouts are phase-specific ANKLE angles, because a phase-specific readout is only
transferable if the model's 45 per cent of cycle is the same physiological event as a patient's 45
per cent of cycle.

Inspection of the control curve suggests it is not. The model appears to dorsiflex immediately after
contact and peak at about 15 per cent, whereas normal gait plantarflexes through loading response to
about -5 deg near 10 per cent and reaches its stance dorsiflexion peak near 45-50 per cent. If that
is right, the 40-50 per cent window is not measuring terminal stance as a clinician would recognise
it, and a stance-phase endpoint cannot be recommended from this model.

Reference landmarks are the textbook normal adult sagittal ankle pattern (Perry; Winter): about 0
deg at initial contact, a plantarflexion trough of roughly -3 to -7 deg during loading response
(5-12 per cent), a progressive rise to a stance peak of about +10 deg at 45-50 per cent, a rapid
fall to about -15 to -20 deg near toe-off (60-62 per cent), and a return to about 0 to +5 deg
through swing.
"""
import glob, io, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
P = r"C:\Users\maurice\Desktop\spasticity_paper\paper"
SETTLE, T1 = 1.0, 9.73


def curves(fam):
    out = {"ankle": [], "knee": []}
    for sd in range(101, 107):
        g = [d for d in glob.glob(os.path.join(RES, "%s_s%d.*" % (fam, sd))) if os.path.isdir(d)]
        if not g:
            continue
        g = [max(g, key=lambda d: len(glob.glob(os.path.join(d, "[0-9]*.par"))))]
        st = sorted(glob.glob(os.path.join(g[0], "*.par.sto")))
        if not st:
            continue
        c, dat = S.load_sto(st[-1])
        if dat.size == 0:
            continue
        t = dat[:, 0]
        grf, thr = S.grf_vertical(c, dat, "l")
        hs = S.heel_strikes(t, grf, thresh=thr)
        allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
        w = [x for x in allc if t[x[1]] <= T1]
        w = w[:-1] if len(w) >= 2 else w
        if float(t[-1]) < T1 or len(w) < 5:
            continue
        on = grf > thr
        for j, nm in (("ankle_angle_l", "ankle"), ("knee_angle_l", "knee")):
            y = np.degrees(S.col(c, dat, j))
            for a, b in w:
                out[nm].append(np.interp(np.linspace(0, 100, 101),
                                         np.linspace(0, 100, b - a), y[a:b]))
        # toe-off as a fraction of the cycle
        for a, b in w:
            idx = np.where(~on[a:b])[0]
            if idx.size:
                out.setdefault("toe_off_pct", []).append(100.0 * idx[0] / float(b - a))
    return out


C = curves("R151C")
an = np.mean(C["ankle"], axis=0)
kn = np.mean(C["knee"], axis=0)
tof = float(np.mean(C.get("toe_off_pct", [np.nan])))
print("control cycles pooled: %d   toe-off at %.1f%% of cycle (normal 60-62%%)"
      % (len(C["ankle"]), tof))

print("\nmodel unlesioned ankle, degrees (dorsiflexion positive):")
for p in range(0, 101, 5):
    print("   %3d%%  %+7.2f" % (p, an[p]))

# --- the four landmarks a clinician would recognise ---------------------------------------------
lr = int(np.argmin(an[:25]))                    # loading-response trough, searched over 0-25%
sp = int(np.argmax(an[25:60])) + 25             # stance dorsiflexion peak, searched over 25-60%
to = int(np.argmin(an[50:75])) + 50             # toe-off plantarflexion, 50-75%
sw = int(np.argmax(an[65:])) + 65               # swing dorsiflexion peak
REF = {
 "loading-response trough": {"model_pct": lr, "model_deg": float(an[lr]),
                             "normal_pct": "5-12", "normal_deg": "-3 to -7"},
 "stance dorsiflexion peak": {"model_pct": sp, "model_deg": float(an[sp]),
                              "normal_pct": "45-50", "normal_deg": "about +10"},
 "toe-off plantarflexion": {"model_pct": to, "model_deg": float(an[to]),
                            "normal_pct": "60-62", "normal_deg": "-15 to -20"},
 "swing dorsiflexion peak": {"model_pct": sw, "model_deg": float(an[sw]),
                             "normal_pct": "70-100", "normal_deg": "0 to +5"},
}
print("\n%-26s %-18s %-14s %-16s %s"
      % ("landmark", "model", "normal phase", "normal value", "verdict"))
verd = {}
for k, v in REF.items():
    lo, hi = [float(x) for x in v["normal_pct"].split("-")]
    inphase = lo <= v["model_pct"] <= hi
    verd[k] = inphase
    print("%-26s %5.0f%% %+7.2f     %-14s %-16s %s"
          % (k, v["model_pct"], v["model_deg"], v["normal_pct"] + "%", v["normal_deg"],
             "phase OK" if inphase else "PHASE WRONG"))

# --- does a loading-response plantarflexion wave exist at all? -----------------------------------
has_lr = bool(an[:20].min() < an[0] - 1.0)
print("\nloading-response plantarflexion wave present: %s "
      "(minimum over 0-20%% is %+.2f against %+.2f at contact)"
      % (has_lr, float(an[:20].min()), float(an[0])))

# --- the knee, for comparison, since the manuscript certifies it ---------------------------------
print("\nknee for comparison: contact %+.2f deg (manuscript: -7.85), swing peak %+.2f deg "
      "(manuscript: 64.6 flexion)" % (kn[0], float(np.min(kn))))

# --- what this does to each candidate readout ----------------------------------------------------
print("\nconsequence for each candidate:")
CAND = {"ankle at 45%": 45, "ankle 40-50% window": 45, "ankle at 85%": 85}
for nm, p in CAND.items():
    near_peak = abs(p - sp) <= 7
    print("   %-24s sits at %d%%; the model's stance peak is at %d%%  -> %s"
          % (nm, p, sp,
             "coincides with a recognisable landmark" if near_peak
             else "does NOT coincide with the model's own stance peak"))

dep = {
 "id": "ANKLESHAPE_r539",
 "why": ("The manuscript certifies the model's knee against normal adult values and never does so "
         "for the ankle. A phase-specific ankle readout is only transferable if the model's phase "
         "corresponds to the same physiological event in a patient."),
 "control_ankle_curve_deg": {str(p): float(an[p]) for p in range(0, 101, 5)},
 "toe_off_pct_of_cycle": tof,
 "landmarks": REF, "landmark_phase_correct": verd,
 "loading_response_wave_present": has_lr,
 "knee_contact_deg": float(kn[0]), "knee_peak_flexion_deg": float(np.min(kn)),
 "n_cycles_pooled": len(C["ankle"]),
}
io.open(os.path.join(P, "ANKLESHAPE_r539.json"), "w", encoding="utf-8",
        newline="").write(json.dumps(dep, indent=1, ensure_ascii=False))
print("\n-> ANKLESHAPE_r539.json")
