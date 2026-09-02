# -*- coding: utf-8 -*-
"""EXPLORATORY, EXPLICITLY NON-CONFIRMATORY endpoint scan (r367).

DISCOVERY HALF ONLY: seeds s101, s102, s103.
HELD-OUT HALF s104, s105, s106 IS NEVER GLOBBED, NEVER LOADED, NEVER PRINTED.

Cell selection and gating carried unaltered from scone/reflexgain_r366.py:
  rd(tag)  -> the one dir matching tag + ".*" whose history.txt has >= 91 lines
  the .sto -> sorted(glob("*.par.sto"))[-1]
  SETTLE 1.00 s, T1 9.73 s; cycles between heel strikes with t[start] >= SETTLE;
  keep cycles wholly inside the window; drop the LAST kept cycle;
  require t_end >= 9.73 and >= 5 cycles in window.
  stance = grf_norm_y > 0.05, the same threshold sto_utils.heel_strikes uses.

CLINICALLY OBSERVABLE CHANNELS ONLY. Allowed: joint kinematics, GRF, inverse-dynamics
joint torque, surface-EMG analogues (activation / excitation of soleus, gastroc, tib_ant).
FORBIDDEN and never read: fiber_length, fiber_velocity, mtu_force, tendon_length, any
*_norm muscle-internal channel, ce_vel, .input, and every controller parameter.

NOTHING IN THIS FILE IS CONFIRMATORY. It is a multiplicity-laden fishing expedition whose
only legitimate output is a shortlist to be pre-registered and tested on the held-out half.
"""
import glob
import io
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\EXPLORATORY_SCAN_r367.json"

SETTLE, T1 = 1.0, 9.73
MIN_CYCLES = 5
TAU_S = 0.020
MIN_SAMPLES = 30

DISCOVERY_SEEDS = ("s101", "s102", "s103")
HELD_OUT_SEEDS = ("s104", "s105", "s106")   # named only so the exclusion is auditable

SPASTIC = ["R289KV00625", "R289KV0125"]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]

MUSCLES = ("soleus", "gastroc", "tib_ant")
KINDS = ("activation", "excitation")
JOINTS = (("ankle", "ankle_angle"), ("knee", "knee_angle"), ("hip", "hip_flexion"))

FORBIDDEN_TOKENS = ("fiber_length", "fiber_velocity", "mtu_force", "tendon_length",
                    "_norm", "ce_vel", ".input")


# ---------------------------------------------------------------------------- selection

def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


def discovery_tags(fams):
    """Tags for the DISCOVERY half only. s104-s106 are never globbed."""
    out = []
    for f in fams:
        for sd in DISCOVERY_SEEDS:
            assert sd not in HELD_OUT_SEEDS
            seen = set()
            for d in sorted(glob.glob(os.path.join(RES, "%s_%s.*" % (f, sd)))):
                b = os.path.basename(d).split(".")[0]
                if b not in seen:
                    seen.add(b)
                    out.append(b)
    for t in out:
        assert not any(h in t for h in HELD_OUT_SEEDS), "HELD-OUT LEAK: " + t
    return out


# ---------------------------------------------------------------------------- helpers

def _safe(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if np.isfinite(f) else None


def _mean_cycles(vals):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    return float(np.mean(v)) if v else None


def pearson(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if len(x) < MIN_SAMPLES:
        return None
    vx, vy = x - x.mean(), y - y.mean()
    dx, dy = float((vx * vx).sum()), float((vy * vy).sum())
    if dx <= 0 or dy <= 0:
        return None
    return float((vx * vy).sum() / np.sqrt(dx * dy))


def ols_slope(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if len(x) < MIN_SAMPLES:
        return None
    vx, vy = x - x.mean(), y - y.mean()
    den = float((vx * vx).sum())
    if den <= 0:
        return None
    return float((vx * vy).sum() / den)


# ---------------------------------------------------------------------------- per side

def side_features(cols, dat, t, side, win, stance_on, dt):
    """All candidate quantities for one leg. Keys carry NO side suffix so that the
    left-minus-right asymmetry is a plain dict subtraction."""
    F = {}

    act = {}
    for m in MUSCLES:
        for k in KINDS:
            s = S.muscle_signal(cols, dat, m, side, k)
            act[(m, k)] = s

    ang = {}
    for jn, cn in JOINTS:
        a = S.col(cols, dat, "%s_%s" % (cn, side))
        ang[jn] = np.degrees(a) if a is not None else None

    tq = {}
    for jn, _ in JOINTS:
        tq[jn] = S.col(cols, dat, "%s_%s.torque" % (jn, side))

    grf_y, thr = S.grf_vertical(cols, dat, side)
    grf_x = None
    for i, c in enumerate(cols):
        if c.endswith("_%s.grf_norm_x" % side):
            grf_x = dat[:, i]
            break

    def masks(a, b):
        st = stance_on[a:b]
        return st, ~st

    # ---- activation summaries: mean / peak / integral over stance, swing, cycle -------
    for m in MUSCLES:
        for k in KINDS:
            s = act[(m, k)]
            if s is None:
                continue
            for ph in ("stance", "swing", "cycle"):
                mn, pk, ig = [], [], []
                for a, b in win:
                    st, sw = masks(a, b)
                    msk = st if ph == "stance" else (sw if ph == "swing"
                                                     else np.ones(b - a, bool))
                    if not msk.any():
                        continue
                    seg = s[a:b][msk]
                    mn.append(float(np.mean(seg)))
                    pk.append(float(np.max(seg)))
                    ig.append(float(np.sum(seg) * dt))
                F["%s_%s_%s_mean" % (m, k, ph)] = _mean_cycles(mn)
                F["%s_%s_%s_peak" % (m, k, ph)] = _mean_cycles(pk)
                F["%s_%s_%s_integral" % (m, k, ph)] = _mean_cycles(ig)

    # ---- PF/DF ratios and co-contraction indices ------------------------------------
    sol, gas, ta = act[("soleus", "activation")], act[("gastroc", "activation")], \
        act[("tib_ant", "activation")]
    if sol is not None and gas is not None and ta is not None:
        pf = 0.5 * (sol + gas)
        eps = 1e-9
        for ph in ("stance", "swing"):
            r_sol, r_gas, r_pf, cci = [], [], [], []
            for a, b in win:
                st, sw = masks(a, b)
                msk = st if ph == "stance" else sw
                if not msk.any():
                    continue
                S_, G_, T_, P_ = sol[a:b][msk], gas[a:b][msk], ta[a:b][msk], pf[a:b][msk]
                r_sol.append(float(np.mean(S_) / (np.mean(T_) + eps)))
                r_gas.append(float(np.mean(G_) / (np.mean(T_) + eps)))
                r_pf.append(float(np.mean(P_) / (np.mean(T_) + eps)))
                lo = np.minimum(P_, T_)
                hi = np.maximum(P_, T_)
                cci.append(float(np.mean(lo / (hi + eps))))
            F["ratio_soleus_over_tibant_%s" % ph] = _mean_cycles(r_sol)
            F["ratio_gastroc_over_tibant_%s" % ph] = _mean_cycles(r_gas)
            F["ratio_PF_over_DF_%s" % ph] = _mean_cycles(r_pf)
            F["cocontraction_minmax_%s" % ph] = _mean_cycles(cci)

    # ---- TIMING ---------------------------------------------------------------------
    for m in MUSCLES:
        s = act[(m, "activation")]
        if s is None:
            continue
        ph = []
        for a, b in win:
            if b - a < 2:
                continue
            ph.append(float(np.argmax(s[a:b])) / float(b - a))
        F["phase_of_peak_%s_activation" % m] = _mean_cycles(ph)
    for jn, _ in JOINTS:
        if tq[jn] is None:
            continue
        ph = []
        for a, b in win:
            if b - a < 2:
                continue
            ph.append(float(np.argmax(np.abs(tq[jn][a:b]))) / float(b - a))
        F["phase_of_peak_%s_torque" % jn] = _mean_cycles(ph)
    F["stance_fraction"] = _mean_cycles(
        [float(np.mean(stance_on[a:b])) for a, b in win if b > a])
    F["cycle_time_s"] = _mean_cycles([float(t[b] - t[a]) for a, b in win])

    # ---- DORSIFLEXION-ONLY (v > 0) stance regressions --------------------------------
    if ang["ankle"] is not None:
        v = np.gradient(ang["ankle"], t)          # deg/s, positive = dorsiflexion
        lag = int(round(TAU_S / dt))
        vlag = np.concatenate([np.zeros(lag), v[:-lag]]) if lag > 0 else v
        Xd, Xdl, Yd = [], [], {(m, k): [] for m in MUSCLES for k in KINDS}
        for a, b in win:
            st, _ = masks(a, b)
            sel = st & (v[a:b] > 0.0)
            if not sel.any():
                continue
            Xd.append(v[a:b][sel])
            Xdl.append(vlag[a:b][sel])
            for m in MUSCLES:
                for k in KINDS:
                    if act[(m, k)] is not None:
                        Yd[(m, k)].append(act[(m, k)][a:b][sel])
        if Xd:
            X = np.concatenate(Xd)
            XL = np.concatenate(Xdl)
            F["n_dorsiflexion_stance_samples"] = float(len(X))
            for m in MUSCLES:
                for k in KINDS:
                    if not Yd[(m, k)]:
                        continue
                    Y = np.concatenate(Yd[(m, k)])
                    F["dfonly_slope_%s_%s_vs_ankvel" % (m, k)] = ols_slope(X, Y)
                    F["dfonly_pearson_%s_%s_vs_ankvel" % (m, k)] = pearson(X, Y)
            Y = np.concatenate(Yd[("soleus", "activation")]) \
                if Yd[("soleus", "activation")] else None
            if Y is not None:
                F["dfonly_slope_soleus_activation_vs_ankvel_lag20ms"] = ols_slope(XL, Y)
                F["dfonly_pearson_soleus_activation_vs_ankvel_lag20ms"] = pearson(XL, Y)

    # ---- torques ---------------------------------------------------------------------
    for jn, cn in JOINTS:
        T_ = tq[jn]
        if T_ is None:
            continue
        pk, ms, mw, wk = [], [], [], []
        av = np.gradient(np.radians(ang[jn]), t) if ang[jn] is not None else None
        for a, b in win:
            st, sw = masks(a, b)
            pk.append(float(np.max(np.abs(T_[a:b]))))
            if st.any():
                ms.append(float(np.mean(T_[a:b][st])))
            if sw.any():
                mw.append(float(np.mean(T_[a:b][sw])))
            if av is not None:
                p = T_[a:b] * av[a:b]
                wk.append(float(np.sum(np.maximum(0.0, p)) * dt))
        F["%s_torque_peak_abs" % jn] = _mean_cycles(pk)
        F["%s_torque_stance_mean" % jn] = _mean_cycles(ms)
        F["%s_torque_swing_mean" % jn] = _mean_cycles(mw)
        F["%s_positive_work_per_cycle" % jn] = _mean_cycles(wk)

    # ---- kinematics -------------------------------------------------------------------
    A = ang["ankle"]
    if A is not None:
        rom, pdf, ppf, hsang, mcyc = [], [], [], [], []
        rom_st, rom_sw, pdf_st, pdf_sw, ppf_st, ppf_sw, m_st, m_sw = ([] for _ in range(8))
        for a, b in win:
            st, sw = masks(a, b)
            seg = A[a:b]
            rom.append(float(np.ptp(seg)))
            pdf.append(float(np.max(seg)))
            ppf.append(float(np.min(seg)))
            hsang.append(float(A[a]))
            mcyc.append(float(np.mean(seg)))
            if st.any():
                rom_st.append(float(np.ptp(seg[st])))
                pdf_st.append(float(np.max(seg[st])))
                ppf_st.append(float(np.min(seg[st])))
                m_st.append(float(np.mean(seg[st])))
            if sw.any():
                rom_sw.append(float(np.ptp(seg[sw])))
                pdf_sw.append(float(np.max(seg[sw])))
                ppf_sw.append(float(np.min(seg[sw])))
                m_sw.append(float(np.mean(seg[sw])))
        F["ankle_ROM_cycle_deg"] = _mean_cycles(rom)
        F["ankle_peak_dorsiflexion_cycle_deg"] = _mean_cycles(pdf)
        F["ankle_peak_plantarflexion_cycle_deg"] = _mean_cycles(ppf)
        F["ankle_angle_at_heelstrike_deg"] = _mean_cycles(hsang)
        F["ankle_mean_cycle_deg"] = _mean_cycles(mcyc)
        F["ankle_ROM_stance_deg"] = _mean_cycles(rom_st)
        F["ankle_ROM_swing_deg"] = _mean_cycles(rom_sw)
        F["ankle_peak_dorsiflexion_stance_deg"] = _mean_cycles(pdf_st)
        F["ankle_peak_dorsiflexion_swing_deg"] = _mean_cycles(pdf_sw)
        F["ankle_peak_plantarflexion_stance_deg"] = _mean_cycles(ppf_st)
        F["ankle_peak_plantarflexion_swing_deg"] = _mean_cycles(ppf_sw)
        F["ankle_mean_stance_deg"] = _mean_cycles(m_st)
        F["ankle_mean_swing_deg"] = _mean_cycles(m_sw)
        F["ankle_peak_dorsiflexion_velocity_stance_degps"] = _mean_cycles(
            [float(np.max(np.gradient(A[a:b], t[a:b])[stance_on[a:b]]))
             for a, b in win if stance_on[a:b].any() and b - a > 2])
    for jn in ("knee", "hip"):
        if ang[jn] is None:
            continue
        F["%s_ROM_cycle_deg" % jn] = _mean_cycles(
            [float(np.ptp(ang[jn][a:b])) for a, b in win])
        F["%s_ROM_stance_deg" % jn] = _mean_cycles(
            [float(np.ptp(ang[jn][a:b][stance_on[a:b]])) for a, b in win
             if stance_on[a:b].any()])
        F["%s_ROM_swing_deg" % jn] = _mean_cycles(
            [float(np.ptp(ang[jn][a:b][~stance_on[a:b]])) for a, b in win
             if (~stance_on[a:b]).any()])

    # ---- GRF -------------------------------------------------------------------------
    if grf_y is not None:
        F["grf_vertical_peak"] = _mean_cycles(
            [float(np.max(grf_y[a:b])) for a, b in win])
        F["grf_vertical_stance_mean"] = _mean_cycles(
            [float(np.mean(grf_y[a:b][stance_on[a:b]])) for a, b in win
             if stance_on[a:b].any()])
        F["grf_vertical_stance_impulse"] = _mean_cycles(
            [float(np.sum(grf_y[a:b][stance_on[a:b]]) * dt) for a, b in win
             if stance_on[a:b].any()])
    if grf_x is not None:
        F["grf_fore_aft_peak_propulsive"] = _mean_cycles(
            [float(np.max(grf_x[a:b])) for a, b in win])
        F["grf_fore_aft_peak_braking"] = _mean_cycles(
            [float(np.min(grf_x[a:b])) for a, b in win])

    return {k: _safe(v) for k, v in F.items()}


# ---------------------------------------------------------------------------- per cell

def window_for(t, grf, thr):
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    return win


def measure(tag):
    assert not any(h in tag for h in HELD_OUT_SEEDS), "HELD-OUT LEAK: " + tag
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        return rec
    rec["dir"] = os.path.basename(d)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        return rec
    rec["sto"] = os.path.basename(stos[-1])
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        return rec
    t = dat[:, 0]
    dt = float(np.median(np.diff(t)))
    rec["t_end_s"] = float(t[-1])

    grf_l, thr_l = S.grf_vertical(cols, dat, "l")
    win_l = window_for(t, grf_l, thr_l)
    rec["n_cycles_in_window"] = len(win_l)
    if rec["t_end_s"] < T1 or len(win_l) < MIN_CYCLES:
        rec["measured"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need %d" % (len(win_l), MIN_CYCLES))
        return rec
    rec["measured"] = True
    stance_l = grf_l > thr_l
    L = side_features(cols, dat, t, "l", win_l, stance_l, dt)

    grf_r, thr_r = S.grf_vertical(cols, dat, "r")
    R = None
    if grf_r is not None:
        win_r = window_for(t, grf_r, thr_r)
        rec["n_cycles_in_window_right"] = len(win_r)
        if len(win_r) >= MIN_CYCLES:
            R = side_features(cols, dat, t, "r", win_r, grf_r > thr_r, dt)
    rec["L"] = L
    rec["R"] = R
    if R is not None:
        rec["ASYM"] = {k: (None if (L.get(k) is None or R.get(k) is None)
                           else float(L[k] - R[k])) for k in L}
    else:
        rec["ASYM"] = None
    return rec


# ---------------------------------------------------------------------------- scan

def pooled_sd(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2:
        return None
    v = ((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)
    return float(np.sqrt(v)) if v > 0 else None


def family_of(tag):
    return tag.rsplit("_s", 1)[0]


def family_perm(sp_fam, wk_fam):
    """Exhaustive relabelling at the FAMILY level.

    The 6 SPASTIC discovery cells come from only 2 families and the 18 DFWEAK cells from 6,
    so the three seeds inside a family are not independent replicates of the arm contrast.
    Treating cells as exchangeable makes a clean split look like p ~ 1/134596; the honest
    unit is the family, where there are only C(8,2) = 28 labellings and the smallest
    attainable one-sided fraction is 1/28.
    """
    vals = list(sp_fam) + list(wk_fam)
    n1 = len(sp_fam)
    obs = max(min(wk_fam) - max(sp_fam), min(sp_fam) - max(wk_fam))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(vals)), n1):
        a = [vals[i] for i in comb]
        b = [vals[i] for i in range(len(vals)) if i not in comb]
        g = max(min(b) - max(a), min(a) - max(b))
        tot += 1
        if g >= obs - 1e-12:
            cnt += 1
    return {"n_labellings": tot, "n_at_least_as_extreme": cnt,
            "fraction": cnt / float(tot), "floor": "1/%d" % tot}


def main():
    # channel-hygiene guard: every channel name this module can reach must be observable
    for tok in FORBIDDEN_TOKENS:
        assert tok not in "".join([
            "%s_%s.torque" % (j, s) for j, _ in JOINTS for s in ("l", "r")] + [
            "%s_%s" % (c, s) for _, c in JOINTS for s in ("l", "r")] + [
            "%s_%s.%s" % (m, s, k) for m in MUSCLES for s in ("l", "r") for k in KINDS] + [
            "leg0_l.grf_norm_y", "leg1_r.grf_norm_y",
            "leg0_l.grf_norm_x", "leg1_r.grf_norm_x"]).replace("grf_norm", "GRFCH"), tok

    cells = {}
    arms = {"SPASTIC": [], "DFWEAK": []}
    for arm, fams in (("SPASTIC", SPASTIC), ("DFWEAK", DFWEAK)):
        print("=== %s ===" % arm)
        for tag in discovery_tags(fams):
            r = measure(tag)
            cells[tag] = r
            ok = r.get("measured")
            print("  %-20s %s" % (tag, ("OK  cycles=%d t_end=%.2f  nfeat=%d"
                                        % (r["n_cycles_in_window"], r["t_end_s"], len(r["L"])))
                                 if ok else r.get("guard", r.get("error", "?"))))
            if ok:
                arms[arm].append(tag)

    # candidate universe = union of keys actually present in every measured cell
    blocks = [("L", "L__"), ("ASYM", "ASYM__")]
    names = []
    for blk, pre in blocks:
        keys = None
        for tag in arms["SPASTIC"] + arms["DFWEAK"]:
            b = cells[tag].get(blk)
            k = set() if b is None else set(x for x in b if b[x] is not None)
            keys = k if keys is None else (keys & k)
        for k in sorted(keys or []):
            names.append((pre + k, blk, k))

    results = []
    for cname, blk, key in names:
        sp = [cells[t][blk][key] for t in arms["SPASTIC"]]
        wk = [cells[t][blk][key] for t in arms["DFWEAK"]]
        gap = max(min(wk) - max(sp), min(sp) - max(wk))
        sd = pooled_sd(sp, wk)

        spf, wkf = {}, {}
        for t_ in arms["SPASTIC"]:
            spf.setdefault(family_of(t_), []).append(cells[t_][blk][key])
        for t_ in arms["DFWEAK"]:
            wkf.setdefault(family_of(t_), []).append(cells[t_][blk][key])
        spfm = [float(np.mean(v)) for v in (spf[k] for k in sorted(spf))]
        wkfm = [float(np.mean(v)) for v in (wkf[k] for k in sorted(wkf))]
        fam_gap = max(min(wkfm) - max(spfm), min(spfm) - max(wkfm))

        results.append({
            "candidate": cname, "block": blk, "quantity": key,
            "n_spastic": len(sp), "n_weak": len(wk),
            "spastic_range": [float(min(sp)), float(max(sp))],
            "weak_range": [float(min(wk)), float(max(wk))],
            "spastic_mean": float(np.mean(sp)), "weak_mean": float(np.mean(wk)),
            "gap": float(gap), "separated": bool(gap > 0),
            "pooled_sd": sd,
            "effect_size_gap_over_pooled_sd": (float(gap / sd) if sd else None),
            "direction": (None if gap <= 0 else
                          ("SPASTIC HIGH" if min(sp) > max(wk) else "SPASTIC LOW")),
            "family_means_spastic": spfm,
            "family_means_weak": wkfm,
            "family_level_gap": float(fam_gap),
            "family_level_separated": bool(fam_gap > 0),
            "family_level_permutation": (family_perm(spfm, wkfm) if fam_gap > 0 else None),
        })

    by_gap = sorted(results, key=lambda r: -r["gap"])
    by_es = sorted([r for r in results if r["effect_size_gap_over_pooled_sd"] is not None],
                   key=lambda r: -r["effect_size_gap_over_pooled_sd"])
    n_sep = sum(1 for r in results if r["separated"])
    n_sep_fam = sum(1 for r in results if r["family_level_separated"])
    n_fam_floor = sum(1 for r in results if r["family_level_permutation"] and
                      r["family_level_permutation"]["n_at_least_as_extreme"] <= 2)

    N = len(results)
    out = {
        "STATUS_READ_THIS_FIRST":
            "THIS IS AN EXPLORATORY SCAN ON A DISCOVERY HALF. NO RESULT IN THIS FILE IS "
            "CONFIRMATORY. It was not pre-registered, it fixes no primary endpoint, and it "
            "must never be cited as evidence for or against any hypothesis. %d candidate "
            "endpoints were tried, so ANY single apparent separation must be read against "
            "that multiplicity: with %d candidates and only 6 spastic and 18 "
            "dorsiflexor-weak discovery cells, separations are expected by chance alone. "
            "The held-out seeds s104, s105 and s106 were NEVER globbed, NEVER loaded, NEVER "
            "computed and appear nowhere in this file; the only legitimate use of anything "
            "here is to pre-register a shortlist and test it there."
            % (N, N),
        "exploratory": True,
        "confirmatory": False,
        "n_candidates_tried": N,
        "multiplicity_warning":
            "%d candidates were scanned on the discovery half. No multiplicity correction "
            "is applied and none would rescue this design; treat every entry as a "
            "hypothesis, not a finding." % N,
        "discovery_seeds_used": list(DISCOVERY_SEEDS),
        "held_out_seeds_never_loaded": list(HELD_OUT_SEEDS),
        "held_out_assertion":
            "No directory whose name contains s104, s105 or s106 was globbed, opened, "
            "parsed, summarised, printed or deposited by this run.",
        "conventions_carried_from": "scone/reflexgain_r366.py (rd >= 91-line history.txt; "
                                    "sorted(*.par.sto)[-1]; SETTLE 1.00 s; T1 9.73 s; "
                                    ">=5 cycles in window; last kept cycle dropped; "
                                    "stance = grf_norm_y > 0.05)",
        "window_s": [SETTLE, T1],
        "observables_only": {
            "allowed": ["ankle_angle_l/r", "knee_angle_l/r", "hip_flexion_l/r",
                        "leg0_l.grf_norm_*", "leg1_r.grf_norm_*",
                        "ankle_l/r.torque", "knee_l/r.torque", "hip_l/r.torque",
                        "soleus/gastroc/tib_ant _l/_r .activation and .excitation"],
            "excluded_and_never_read": ["fiber_length", "fiber_velocity", "mtu_force",
                                        "tendon_length", "any *_norm muscle-internal channel",
                                        "ce_vel", "muscle .input", "all controller parameters"],
        },
        "arms": {"SPASTIC": {"families": SPASTIC, "cells": arms["SPASTIC"]},
                 "DFWEAK": {"families": DFWEAK, "cells": arms["DFWEAK"]}},
        "n_candidates_separating_at_all": n_sep,
        "any_clean_separation": bool(n_sep > 0),
        "n_candidates_separating_at_family_level": n_sep_fam,
        "n_candidates_at_family_permutation_floor": n_fam_floor,
        "CLUSTERING_CAVEAT":
            "The 6 SPASTIC discovery cells come from only 2 controller families "
            "(R289KV00625, R289KV0125) and the 18 DFWEAK cells from 6 families. The three "
            "seeds inside a family are NOT independent replicates of the arm contrast, so a "
            "cell-level clean split is worth far less than its 1/C(24,6) appearance. At the "
            "honest family level there are only C(8,2) = 28 labellings, so the smallest "
            "attainable one-sided fraction is 1/28 = 0.0357 and roughly 1/14 of candidates "
            "would separate by chance alone: with %d candidates that is about %.0f expected "
            "chance separations. %d candidates separate at the family level here."
            % (N, N / 14.0, n_sep_fam),
        "candidate_names_tried": [r["candidate"] for r in results],
        "SHORTLIST_for_possible_future_preregistration": {
            "criterion": "separates at the cell level AND at the family level AND has "
                         "effect size (gap / pooled SD) >= 1.0",
            "warning": "A shortlist is NOT a result. These candidates were chosen by looking "
                       "at the discovery data and are guaranteed to look good on it. They "
                       "have no evidential value until one of them is pre-registered and "
                       "tested on the untouched held-out half.",
            "members": [{"candidate": r["candidate"], "direction": r["direction"],
                         "gap": r["gap"],
                         "effect_size": r["effect_size_gap_over_pooled_sd"],
                         "family_perm_fraction": r["family_level_permutation"]["fraction"]}
                        for r in by_es
                        if r["separated"] and r["family_level_separated"]
                        and r["effect_size_gap_over_pooled_sd"] >= 1.0],
        },
        "ranked_by_gap_desc": by_gap,
        "ranked_by_effect_size_desc": by_es[:40],
        "note_on_ranking":
            "Gaps are in the native unit of each candidate and are therefore NOT comparable "
            "across candidates; the gap ranking is reported because it was requested, and "
            "the scale-free effect-size ranking is given alongside it. Only the sign of the "
            "gap (separated vs overlapping) is unit-free.",
        "per_cell_values": cells,
    }
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, indent=2, ensure_ascii=False, sort_keys=False, default=str))

    print()
    print("candidates tried: %d   separating (cell level): %d   separating (family level): %d"
          " (~%.0f expected by chance at 1/14 each)" % (N, n_sep, n_sep_fam, N / 14.0))
    print("at the family permutation floor (<=2 of 28 labellings as extreme): %d" % n_fam_floor)
    print()
    print("TOP 15 BY GAP (descending)")
    for i, r in enumerate(by_gap[:15], 1):
        print("%2d. %-58s gap=%+.6g  sp=[%.6g,%.6g] wk=[%.6g,%.6g] es=%s %s"
              % (i, r["candidate"], r["gap"], r["spastic_range"][0], r["spastic_range"][1],
                 r["weak_range"][0], r["weak_range"][1],
                 ("%+.3f" % r["effect_size_gap_over_pooled_sd"])
                 if r["effect_size_gap_over_pooled_sd"] is not None else "NA",
                 ("SEP(%s) famfrac=%s" % (r["direction"],
                  "%.4f" % r["family_level_permutation"]["fraction"]
                  if r["family_level_permutation"] else "OVERLAP@FAMILY"))
                 if r["separated"] else ""))
    print()
    print("TOP 15 BY EFFECT SIZE (descending)")
    for i, r in enumerate(by_es[:15], 1):
        print("%2d. %-58s es=%+.4f gap=%+.6g sp=[%.6g,%.6g] wk=[%.6g,%.6g] %s"
              % (i, r["candidate"], r["effect_size_gap_over_pooled_sd"], r["gap"],
                 r["spastic_range"][0], r["spastic_range"][1],
                 r["weak_range"][0], r["weak_range"][1],
                 ("SEP(%s) famfrac=%s" % (r["direction"],
                  "%.4f" % r["family_level_permutation"]["fraction"]
                  if r["family_level_permutation"] else "OVERLAP@FAMILY"))
                 if r["separated"] else ""))
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
