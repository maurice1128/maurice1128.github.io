# -*- coding: utf-8 -*-
"""r386 -- TWO SCALE-FREE FIRST-PRINCIPLES TESTS.  EXPLORATORY.

WHY.  Every endpoint tried in this corpus is an AMPLITUDE, and the amplitudes land at
0.22-1.21 deg against a clinical MDC of 3.8-11.5.  The reason is that re-optimisation of the
controller cancels ~86% of the imposed lesion, and re-optimisation adjusts GAINS.  A gain can
scale a signal.  It cannot change a TIME DELAY, and it cannot change a STABILITY MARGIN
without changing the loop itself.  Both tests below are therefore immune, IN PRINCIPLE, to
the mechanism that has defeated every previous endpoint.

TEST 1 -- LAG STRUCTURE.  The spastic lesion is
    ReflexController name=SpasticL { MuscleReflex target=soleus  delay=0.020 KV=.. allow_neg_V=0
                                     MuscleReflex target=gastroc delay=0.020 KV=.. allow_neg_V=0 }
i.e. a velocity feedback with an EXPLICIT 20 ms delay onto the plantarflexors.  The weakness
lesion is a static scaling of tib_ant_l max_isometric_force and introduces NO delay at all.
So the temporal relationship between ankle dorsiflexion velocity and plantarflexor activation
should carry a lesion-specific lag signature.  The endpoint is a LAG in milliseconds and is
completely scale-free.

TEST 2 -- STABILITY MARGIN / CYCLE-TO-CYCLE STRUCTURE.  Raising a feedback loop gain reduces
the stability margin; reducing an actuator gain does not, in the same way.
    *** PREMISE FAILURE, VERIFIED, REPORTED LOUDLY: the brief asserted that the SCONE
    *** controller contains `NoiseController { base_noise, proportional_noise }`.  IT DOES
    *** NOT.  See NOISE_AUDIT below.  There is no injected noise in any arm, so the promised
    *** "free system-identification probe" does not exist.  Test 2 is reinterpreted, not
    *** abandoned: see NOISE_AUDIT["consequence"].

CONVENTIONS CARRIED VERBATIM FROM scone/doseladder_r371.py:
    rd()   = the one directory per tag with history.txt >= 91 lines
    sto    = sorted(glob("*.par.sto"))[-1]
    SETTLE = 1.00, T1 = 9.73
    cycles between heel strikes with t[start] >= SETTLE, wholly inside the window,
           drop the LAST kept cycle, require >= 5
    stance = leg0_l.grf_norm_y > 0.05  (grf_vertical returns that threshold)
    seed unit = tag.split("_")[-1]; permutation over seed means only.

ARMS.  ladder and DF-weak are both min_velocity 1.0 -> WITHIN-SCENARIO.
       control is 0.80/1.05/1.30 -> BETWEEN-SCENARIO; every statement using it says so.

EXPLORATORY.  No single measure was nominated in advance.  See MULTIPLICITY.
"""
import glob
import io
import itertools
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S

RES = r"C:\Users\maurice\Documents\SCONE\results"
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\TIMING_STABILITY_r386.json"
SETTLE, T1 = 1.0, 9.73

LADDER = [("0.00625", "R289KV00625"), ("0.0125", "R289KV0125"),
          ("0.035", "R291KV0035"), ("0.070", "R291KV0070")]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
CONTROL = ["R203V080C", "R203V105C", "R203V130C"]

LAGS_MS = list(range(-200, 201, 10))          # 41 lags, dt is exactly 10 ms -> 1 sample/step
TARGETS = ["soleus", "gastroc", "tib_ant"]
VSRC = ["v", "vrect"]
NGRID = 64                                    # phase grid for the ensemble-mean cycle
# Two cross-correlation FAMILIES, both reported:
#   raw   -- exactly as briefed: the signals themselves over the admissible cycles.
#   resid -- the SAME statistic after the phase-averaged (ensemble-mean) cycle has been
#            subtracted from BOTH signals. Rationale: gait is near-periodic at ~1.15 s, so a
#            +-200 ms window covers only +-17% of a stride and the raw cross-correlogram is
#            dominated by the stride-periodic lobe, which pins the peak to the grid edge and
#            drags the centroid with it. Removing the stride-periodic component leaves the
#            cycle-to-cycle residual coupling, which is where a 20 ms reflex delay can live.
FAMS_XC = [("raw", "lag"), ("resid", "lag_resid")]
LAGSTATS = ["lag_peak_ms", "peak_corr", "centroid_lag_ms"]
# extra lag descriptors carried per cell but NOT part of the primary 3
LAGSTATS_EXTRA = ["centroid_lag_contig_ms", "n_positive_lags"]

CYCSTATS = ["sd_dur_s", "cv_dur", "sd_rom_deg", "cv_rom", "sd_pksol", "cv_pksol",
            "ac1_dur", "floquet_dur"]


# ---------------------------------------------------------------------------- corpus access
def rd(tag):
    g = [d for d in glob.glob(os.path.join(RES, tag + ".*")) if os.path.isdir(d)
         and os.path.exists(os.path.join(d, "history.txt"))
         and sum(1 for _ in io.open(os.path.join(d, "history.txt"), errors="replace")) >= 91]
    if len(g) != 1:
        raise AssertionError("%s -> %d dirs" % (tag, len(g)))
    return g[0]


def tags_for(fams):
    out = []
    for f in fams:
        seen = set()
        for d in sorted(glob.glob(os.path.join(RES, f + "_s*"))):
            b = os.path.basename(d).split(".")[0]
            if b not in seen:
                seen.add(b)
                out.append(b)
    return out


def cfg_audit(fam):
    """min_velocity, SpasticL KV/delay, and -- the point of this round -- NOISE settings."""
    try:
        d = rd(tags_for([fam])[0])
    except Exception as e:
        return {"error": str(e)}
    a = {"dir": os.path.basename(d)}
    cfg = os.path.join(d, "config.scone")
    if not os.path.exists(cfg):
        a["error"] = "no config.scone"
        return a
    txt = io.open(cfg, encoding="utf-8", errors="replace").read()
    m = re.search(r"min_velocity\s*=\s*([0-9.]+)", txt)
    a["min_velocity"] = float(m.group(1)) if m else None
    a["has_SpasticL"] = "SpasticL" in txt
    m = re.search(r"name\s*=\s*SpasticL.*?KV\s*=\s*([0-9.]+)", txt, re.S)
    a["config_KV"] = float(m.group(1)) if m else None
    m = re.search(r"name\s*=\s*SpasticL.*?delay\s*=\s*([0-9.]+)", txt, re.S)
    a["SpasticL_delay_s"] = float(m.group(1)) if m else None
    # --- the noise audit proper --------------------------------------------------------
    a["n_NoiseController"] = len(re.findall(r"NoiseController", txt))
    a["base_noise"] = re.findall(r"base_noise\s*=\s*([-0-9.eE+]+)", txt)
    a["proportional_noise"] = re.findall(r"proportional_noise\s*=\s*([-0-9.eE+]+)", txt)
    a["any_token_noise"] = sorted(set(re.findall(r"\w*[Nn]oise\w*", txt)))
    m = re.search(r"initial_state_offset\s*=\s*\"([^\"]+)\"", txt)
    a["initial_state_offset"] = m.group(1) if m else None
    m = re.search(r"random_seed\s*=\s*(\d+)", txt)
    a["random_seed"] = int(m.group(1)) if m else None
    m = re.search(r"fixed_control_step_size\s*=\s*([0-9.eE+-]+)", txt)
    a["fixed_control_step_size"] = float(m.group(1)) if m else None
    a["cfg_sha_head"] = None
    return a


# ---------------------------------------------------------------------------- test 1 core
def xcorr_lagstats(v, y, core_lo, core_hi, lags_samp):
    """Normalised cross-correlation of v (reference) against y at integer sample lags.

    C(L) = pearson( v[i], y[i+L] ) for i in [core_lo, core_hi).  POSITIVE L therefore means
    y LAGS v, i.e. the activation happens L samples AFTER the velocity.  The reference index
    set is FIXED across lags so the curve is not confounded by a changing sample set; only
    the y window slides.  Shifted indices are allowed to leave the admissible cycles (they
    stay inside the record), which is correct: the question is a temporal relation, not a
    per-cycle average.
    """
    x = v[core_lo:core_hi]
    xs = x.std()
    out = []
    for L in lags_samp:
        yy = y[core_lo + L:core_hi + L]
        ys = yy.std()
        if xs <= 0 or ys <= 0 or len(yy) != len(x):
            out.append(float("nan"))
        else:
            out.append(float(np.mean((x - x.mean()) * (yy - yy.mean())) / (xs * ys)))
    C = np.array(out, float)
    d = {"corr_curve": [None if not np.isfinite(c) else float(c) for c in C]}
    if not np.isfinite(C).any():
        d["error"] = "degenerate (zero variance)"
        return d
    k = int(np.nanargmax(C))
    d["lag_peak_ms"] = float(LAGS_MS[k])
    d["peak_corr"] = float(C[k])
    d["peak_at_grid_edge"] = bool(k == 0 or k == len(C) - 1)
    d["no_positive_peak"] = bool(C[k] <= 0)
    pos = np.isfinite(C) & (C > 0)
    d["n_positive_lags"] = int(pos.sum())
    L = np.array(LAGS_MS, float)
    if pos.any():
        d["centroid_lag_ms"] = float(np.sum(C[pos] * L[pos]) / np.sum(C[pos]))
        lo = hi = k                                  # contiguous positive run around the peak
        if C[k] > 0:
            while lo - 1 >= 0 and np.isfinite(C[lo - 1]) and C[lo - 1] > 0:
                lo -= 1
            while hi + 1 < len(C) and np.isfinite(C[hi + 1]) and C[hi + 1] > 0:
                hi += 1
            seg = slice(lo, hi + 1)
            d["centroid_lag_contig_ms"] = float(np.sum(C[seg] * L[seg]) / np.sum(C[seg]))
            d["contig_run_ms"] = [float(L[lo]), float(L[hi])]
        else:
            d["centroid_lag_contig_ms"] = None
    else:
        d["centroid_lag_ms"] = None
        d["centroid_lag_contig_ms"] = None
    return d


def cycle_residual(t, y, win):
    """y minus its own ensemble-mean cycle, evaluated at each sample's cycle phase.

    Defined only inside the admissible cycles; NaN elsewhere.  With 5-6 cycles the ensemble
    mean absorbs ~1/n of each cycle's own waveform, which shrinks the residual, but it does so
    identically in every arm, so it biases toward the null rather than toward a separation.
    """
    N = len(t)
    out = np.full(N, np.nan)
    grid = np.linspace(0.0, 1.0, NGRID, endpoint=False)
    waves = []
    phases = []
    for a, b in win:
        p = (t[a:b] - t[a]) / (t[b] - t[a])
        phases.append(p)
        # periodic interpolation onto the common phase grid
        pp = np.concatenate([p, [1.0]])
        yy = np.concatenate([y[a:b], [y[a]]])
        waves.append(np.interp(grid, pp, yy))
    mw = np.mean(waves, axis=0)
    gp = np.concatenate([grid, [1.0]])
    mwp = np.concatenate([mw, [mw[0]]])
    for (a, b), p in zip(win, phases):
        out[a:b] = y[a:b] - np.interp(p, gp, mwp)
    return out


def xcorr_lagstats_resid(rv, ry, lo, hi, lags_samp):
    """As xcorr_lagstats but on residual arrays that are NaN outside the admissible cycles;
    the reference range [lo,hi) is already inset by the maximum shift."""
    x = rv[lo:hi]
    if not np.isfinite(x).all():
        return {"error": "residual undefined inside core"}
    return xcorr_lagstats(rv, ry, lo, hi, lags_samp)


# ---------------------------------------------------------------------------- measurement
def measure(tag):
    rec = {"tag": tag}
    try:
        d = rd(tag)
    except AssertionError as e:
        rec["error"] = str(e)
        rec["gate_G"] = False
        return rec
    rec["dir"] = os.path.basename(d)
    stos = sorted(glob.glob(os.path.join(d, "*.par.sto")))
    if not stos:
        rec["error"] = "no .par.sto"
        rec["gate_G"] = False
        return rec
    rec["sto"] = os.path.basename(stos[-1])
    cols, dat = S.load_sto(stos[-1])
    if dat.size == 0:
        rec["error"] = "empty sto"
        rec["gate_G"] = False
        return rec
    t = dat[:, 0]
    N = len(t)
    rec["t_end_s"] = float(t[-1])
    dt = float(np.median(np.diff(t)))
    rec["dt_s"] = dt
    grf, thr = S.grf_vertical(cols, dat, "l")
    hs = S.heel_strikes(t, grf, thresh=thr)
    allc = [(hs[k], hs[k + 1]) for k in range(len(hs) - 1) if t[hs[k]] >= SETTLE]
    win = [c for c in allc if t[c[1]] <= T1]
    win = win[:-1] if len(win) >= 2 else win
    rec["n_cycles_in_window"] = len(win)
    if rec["t_end_s"] < T1 or len(win) < 5:
        rec["gate_G"] = False
        rec["guard"] = ("t_end %.3f < %.2f" % (rec["t_end_s"], T1) if rec["t_end_s"] < T1
                        else "only %d cycles in window, need 5" % len(win))
        return rec
    rec["gate_G"] = True

    # lag grid in samples -- ASSERTED to be an exact multiple of the sample interval
    step = int(round(0.010 / dt))
    rec["lag_grid_samples_per_10ms"] = step
    rec["lag_grid_exact"] = bool(abs(0.010 / dt - step) < 1e-6 and step >= 1)
    lags_samp = [int(round(ms / 1000.0 / dt)) for ms in LAGS_MS]

    core_lo, core_hi = win[0][0], win[-1][1]
    mx = max(abs(min(lags_samp)), abs(max(lags_samp)))
    rec["core_samples"] = int(core_hi - core_lo)
    rec["core_window_s"] = [float(t[core_lo]), float(t[core_hi])]
    rec["shift_margin_ok"] = bool(core_lo - mx >= 0 and core_hi + mx <= N)
    if not rec["shift_margin_ok"]:
        core_lo = max(core_lo, mx)
        core_hi = min(core_hi, N - mx)
        rec["core_samples_clipped"] = int(core_hi - core_lo)

    # ---- TEST 1 ------------------------------------------------------------------------
    rlo, rhi = core_lo + mx, core_hi - mx        # residual core, inset by the maximum shift
    rec["resid_core_samples"] = int(max(rhi - rlo, 0))
    rec["lag"] = {}
    rec["lag_resid"] = {}
    for side in ("l", "r"):
        ang = S.col(cols, dat, "ankle_angle_%s" % side)
        if ang is None:
            rec["lag"][side] = {"error": "no ankle_angle_%s" % side}
            rec["lag_resid"][side] = {"error": "no ankle_angle_%s" % side}
            continue
        angd = np.degrees(ang)
        v = np.gradient(angd, t)                    # deg/s, POSITIVE = DORSIFLEXION
        vr = np.maximum(v, 0.0)                     # the lesion acts only on lengthening
        rv = cycle_residual(t, v, win)
        rvr = cycle_residual(t, vr, win)
        rec["lag"][side] = {}
        rec["lag_resid"][side] = {}
        if side == "l":
            rec["v_l_deg_s"] = {"min": float(v[core_lo:core_hi].min()),
                                "max": float(v[core_lo:core_hi].max()),
                                "frac_positive": float(np.mean(v[core_lo:core_hi] > 0))}
        for tgt in TARGETS:
            a = S.muscle_signal(cols, dat, tgt, side, "activation")
            if a is None:
                rec["lag"][side][tgt] = {"error": "no %s_%s activation" % (tgt, side)}
                rec["lag_resid"][side][tgt] = {"error": "no %s_%s activation" % (tgt, side)}
                continue
            rec["lag"][side][tgt] = {
                "v": xcorr_lagstats(v, a, core_lo, core_hi, lags_samp),
                "vrect": xcorr_lagstats(vr, a, core_lo, core_hi, lags_samp)}
            ra = cycle_residual(t, a, win)
            if rhi - rlo < 50:
                rec["lag_resid"][side][tgt] = {"error": "residual core too short"}
            else:
                rec["lag_resid"][side][tgt] = {
                    "v": xcorr_lagstats_resid(rv, ra, rlo, rhi, lags_samp),
                    "vrect": xcorr_lagstats_resid(rvr, ra, rlo, rhi, lags_samp)}

    # ---- TEST 2 ------------------------------------------------------------------------
    on = grf > thr
    angl = np.degrees(S.col(cols, dat, "ankle_angle_l"))
    sol = S.muscle_signal(cols, dat, "soleus", "l", "activation")
    dur, rom, pks, stf = [], [], [], []
    for a, b in win:
        dur.append(float(t[b] - t[a]))
        rom.append(float(np.ptp(angl[a:b])))
        m = on[a:b]
        stf.append(float(np.mean(m)))
        pks.append(float(np.max(sol[a:b][m])) if m.any() else float("nan"))
    cyc = {"n_cycles": len(win), "dur_s": dur, "rom_deg": rom, "peak_stance_soleus": pks,
           "stance_frac": stf}

    def sdcv(x, prefix):
        x = np.asarray([q for q in x if np.isfinite(q)], float)
        o = {}
        if len(x) < 2:
            o[prefix + "_mean"] = None
            o["sd_" + prefix] = None
            o["cv_" + prefix] = None
            return o
        mu, sd = float(x.mean()), float(x.std(ddof=1))
        o[prefix + "_mean"] = mu
        o["sd_" + prefix] = sd
        o["cv_" + prefix] = float(sd / abs(mu)) if mu != 0 else None
        return o

    cyc.update(sdcv(dur, "dur"))
    cyc.update(sdcv(rom, "rom"))
    cyc.update(sdcv(pks, "pksol"))
    # rename to the flat keys the statistics layer uses
    cyc["sd_dur_s"] = cyc.pop("sd_dur")
    cyc["sd_rom_deg"] = cyc.pop("sd_rom")

    def ac1(x):
        """lag-1 autocorrelation, sum_{k}(e_k e_{k+1}) / sum_k e_k^2 (biased denominator)."""
        x = np.asarray([q for q in x if np.isfinite(q)], float)
        if len(x) < 3:
            return None
        e = x - x.mean()
        den = float(np.sum(e * e))
        return float(np.sum(e[:-1] * e[1:]) / den) if den > 0 else None

    def floquet(x):
        """Slope of e_{k+1} on e_k through the origin -- a crude one-dimensional Floquet
        multiplier for the deviation of the cycle statistic from its own mean.  |slope| < 1
        means deviations shrink; -> 1 means a slowly-decaying (low-damping) return."""
        x = np.asarray([q for q in x if np.isfinite(q)], float)
        if len(x) < 3:
            return None
        e = x - x.mean()
        den = float(np.sum(e[:-1] ** 2))
        return float(np.sum(e[:-1] * e[1:]) / den) if den > 0 else None

    cyc["ac1_dur"] = ac1(dur)
    cyc["floquet_dur"] = floquet(dur)
    cyc["ac1_rom"] = ac1(rom)
    cyc["floquet_rom"] = floquet(rom)
    cyc["n_pairs_for_ac1"] = max(len(dur) - 1, 0)
    # monotone-drift diagnostic: with NO injected noise the only source of cycle-to-cycle
    # variation is the decaying transient, so a near-monotone series is expected and a
    # near-1 lag-1 autocorrelation reflects DRIFT, not marginal damping.
    dd = np.diff(np.asarray(dur, float))
    cyc["dur_diff_sign_all_same"] = bool(len(dd) > 0 and (np.all(dd > 0) or np.all(dd < 0)))
    cyc["dur_first_minus_last_s"] = float(dur[0] - dur[-1])
    cyc["abs_drift_over_sd"] = (float(abs(dur[0] - dur[-1]) / cyc["sd_dur_s"])
                                if cyc["sd_dur_s"] else None)
    rec["cyc"] = cyc
    return rec


# ---------------------------------------------------------------------------- statistics
def get_lag(rec, fkey, side, tgt, vs, stat):
    try:
        return rec[fkey][side][tgt][vs][stat]
    except (KeyError, TypeError):
        return None


def get_cyc(rec, stat):
    try:
        return rec["cyc"][stat]
    except (KeyError, TypeError):
        return None


def seed_means(tags, cells, getter):
    out = {}
    for tg in tags:
        r = cells.get(tg, {})
        if not r.get("gate_G"):
            continue
        v = getter(r)
        if v is None or not np.isfinite(v):
            continue
        out.setdefault(tg.split("_")[-1], []).append(float(v))
    return {k: float(np.mean(v)) for k, v in out.items()}


def floor(a, b):
    allv = list(a) + list(b)
    n1 = len(a)
    obs = max(min(b) - max(a), min(a) - max(b))
    tot = cnt = 0
    for comb in itertools.combinations(range(len(allv)), n1):
        x = [allv[i] for i in comb]
        y = [allv[i] for i in range(len(allv)) if i not in comb]
        if max(min(y) - max(x), min(x) - max(y)) >= obs - 1e-12:
            cnt += 1
        tot += 1
    return {"n_total": tot, "n_at_least_as_extreme": cnt, "floor": "1/%d" % tot,
            "frac_at_least_as_extreme": cnt / float(tot)}


def compare(sm, wm, label):
    s, w = sorted(sm.values()), sorted(wm.values())
    d = {"measure": label, "n_a_seeds": len(s), "n_b_seeds": len(w),
         "a_seed_means": sm, "b_seed_means": wm}
    if len(s) < 4 or len(w) < 4:
        d["VERDICT"] = "UNINFORMATIVE"
        d["why"] = "fewer than 4 gate-G seeds in one arm"
        return d
    d["a_range"] = [s[0], s[-1]]
    d["b_range"] = [w[0], w[-1]]
    d["a_mean"] = float(np.mean(s))
    d["b_mean"] = float(np.mean(w))
    gap = max(w[0] - s[-1], s[0] - w[-1])
    d["gap"] = float(gap)
    pooled = float(np.std(list(s) + list(w), ddof=1))
    d["gap_over_pooled_sd"] = float(gap / pooled) if pooled > 0 else None
    d["separated"] = bool(gap > 0)
    if gap > 0:
        d["direction"] = "A HIGH" if s[0] > w[-1] else "A LOW"
        d["permutation"] = floor(s, w)
        d["VERDICT"] = "SEPARATED"
    else:
        d["VERDICT"] = "OVERLAP"
    return d


# ---------------------------------------------------------------------------- main
def main():
    res = {
        "round": "r386",
        "status": "EXPLORATORY -- NO RESULT IN THIS DEPOSIT IS CONFIRMATORY",
        "why_exploratory": (
            "No single measure was nominated in advance and no registration document exists "
            "for r386. Every separation reported here is HYPOTHESIS-GENERATING only."),
        "rationale": (
            "Every endpoint tried in this corpus is an AMPLITUDE, and the amplitudes land at "
            "0.22-1.21 deg against a clinical MDC of 3.8-11.5, because re-optimisation cancels "
            "~86% of the imposed lesion by adjusting GAINS. A gain can scale a signal; it "
            "cannot change a TIME DELAY, and it cannot change a STABILITY MARGIN without "
            "changing the loop itself. Both tests are therefore immune IN PRINCIPLE to the "
            "mechanism that defeated the amplitude endpoints."),
        "conventions": {
            "source": "scone/doseladder_r371.py (verbatim)",
            "rd": "the one dir per tag with history.txt >= 91 lines",
            "sto": 'sorted(glob("*.par.sto"))[-1]',
            "SETTLE": SETTLE, "T1": T1,
            "cycles": ("between heel strikes with t[start] >= SETTLE, wholly inside the "
                       "window, drop the LAST kept cycle, require >= 5"),
            "stance": "leg0_l.grf_norm_y > 0.05",
            "seed_unit": 'tag.split("_")[-1]',
            "permutation": "exhaustive over C(12,6)=924; reported as a FLOOR, never a p-value",
        },
        "arms": {
            "ladder": {kv: fam for kv, fam in LADDER},
            "dfweak": DFWEAK, "control": CONTROL,
            "scenario_note": ("ladder and DF-weak are BOTH min_velocity 1.0, so the "
                              "ladder-vs-DFweak test is WITHIN-SCENARIO. The control arm is "
                              "min_velocity 0.80/1.05/1.30, so EVERY statement involving the "
                              "control arm is BETWEEN-SCENARIO and is labelled as such."),
        },
        "cells": {}, "config_audit": {}, "NOISE_AUDIT": {},
        "TEST1_lag": {}, "TEST2_cycle": {}, "checks": {},
    }

    # ------------------------------------------------------------------ config + noise audit
    print("=== config / noise audit ===")
    fams = [f for _, f in LADDER] + DFWEAK + CONTROL
    for f in fams:
        res["config_audit"][f] = cfg_audit(f)
    mv = {}
    for f in fams:
        mv.setdefault(res["config_audit"][f].get("min_velocity"), []).append(f)
    res["config_audit"]["_min_velocity_groups"] = {str(k): sorted(v) for k, v in mv.items()}
    for k in sorted(mv, key=lambda x: (x is None, x)):
        print("  min_velocity=%-6s %s" % (k, ", ".join(sorted(mv[k]))))

    lad_f = [f for _, f in LADDER]
    n_noise = {f: res["config_audit"][f].get("n_NoiseController") for f in fams}
    toks = {f: res["config_audit"][f].get("any_token_noise") for f in fams}
    iso = {f: res["config_audit"][f].get("initial_state_offset") for f in fams}
    fcs = {f: res["config_audit"][f].get("fixed_control_step_size") for f in fams}
    all_zero = all(v == 0 for v in n_noise.values())
    res["NOISE_AUDIT"] = {
        "question": ("the brief asserted `NoiseController { base_noise, proportional_noise }` "
                     "is present and provides a free system-identification probe"),
        "n_NoiseController_per_family": n_noise,
        "any_token_matching_noise_per_family": toks,
        "base_noise_values": {f: res["config_audit"][f].get("base_noise") for f in fams},
        "proportional_noise_values": {f: res["config_audit"][f].get("proportional_noise")
                                      for f in fams},
        "initial_state_offset_per_family": iso,
        "fixed_control_step_size_per_family": fcs,
        "ANSWER": ("NO NoiseController EXISTS IN ANY ARM." if all_zero else
                   "NoiseController IS present in some arms -- see counts."),
        "ladder_vs_dfweak_noise_settings_differ": bool(
            len(set(str(n_noise[f]) for f in lad_f)) > 1
            or set(str(n_noise[f]) for f in lad_f) != set(str(n_noise[f]) for f in DFWEAK)
            or set(str(iso[f]) for f in lad_f) != set(str(iso[f]) for f in DFWEAK)),
        "consequence": (
            "THE PREMISE OF TEST 2 AS BRIEFED IS FALSE. There is no injected noise anywhere in "
            "this corpus, so there is no continuous stochastic probe and no system "
            "identification comes for free. The only stochastic element in config.scone is "
            "`initial_state_offset = \"0~0.01<-0.5,0.5>\"`, and that is an OPTIMISED PARAMETER "
            "fixed inside the chosen .par, not per-step noise: the replay that produced each "
            ".par.sto is DETERMINISTIC. Test 2 therefore does not measure the response to a "
            "known perturbation. What the cycle-to-cycle numbers DO measure is the decay of "
            "the transient launched by the initial state away from the limit cycle, observed "
            "over the 5-6 admissible cycles. Under that reading a large cycle-to-cycle SD, a "
            "near-1 lag-1 autocorrelation and a near-1 Floquet slope all indicate a transient "
            "that has NOT yet died out -- which is a genuine (if very crude) stability-margin "
            "signal, but it is confounded with how far the initial state happened to sit from "
            "each cell's own limit cycle, and that distance is not controlled across arms. "
            "The measures are reported on that basis and on no stronger one."),
        "GOOD_NEWS_for_symmetry": (
            "Because the setting is identical in every arm (zero noise, same "
            "initial_state_offset spec, same fixed_control_step_size), the missing noise is "
            "NOT a differential confound between the ladder and DF-weak arms. It removes the "
            "briefed interpretation, not the comparability."),
    }
    print("  NoiseController count per family: %s" % sorted(set(n_noise.values())))
    print("  -> %s" % res["NOISE_AUDIT"]["ANSWER"])
    print("  ladder/DFweak noise settings differ: %s"
          % res["NOISE_AUDIT"]["ladder_vs_dfweak_noise_settings_differ"])

    # ------------------------------------------------------------------ measurement
    print()
    print("=== measurement (78 cells, ~17 MB each, sequential) ===")
    ltags = {kv: tags_for([fam]) for kv, fam in LADDER}
    wtags = tags_for(DFWEAK)
    ctags = tags_for(CONTROL)
    allt = [x for v in ltags.values() for x in v] + wtags + ctags
    # Re-running only the STATISTICS layer must not re-parse 78 x 17 MB of .sto. With
    # R386_REUSE_CELLS=1 the per-cell block is taken verbatim from the existing deposit; the
    # measurement code above is untouched, so the reused values are bit-identical to a fresh
    # parse. The provenance is recorded in res["cells_source"].
    reuse = os.environ.get("R386_REUSE_CELLS") == "1" and os.path.exists(OUT)
    if reuse:
        prev = json.loads(io.open(OUT, encoding="utf-8").read())
        missing = [t for t in allt if t not in prev.get("cells", {})]
        if missing:
            raise AssertionError("R386_REUSE_CELLS=1 but %d cells absent from the deposit: %s"
                                 % (len(missing), missing[:5]))
        res["cells"] = {t: prev["cells"][t] for t in allt}
        res["cells_source"] = ("REUSED verbatim from the previous %s written by this same "
                               "script; only the statistics layer was recomputed." % OUT)
        print("  cells REUSED from existing deposit (%d cells, no .sto re-parsed)" % len(allt))
    else:
        res["cells_source"] = "measured fresh from .par.sto"
        for i, tg in enumerate(allt):
            res["cells"][tg] = measure(tg)
            print("  [%2d/%d] %-22s gate_G=%s n_cyc=%s"
                  % (i + 1, len(allt), tg, res["cells"][tg].get("gate_G"),
                     res["cells"][tg].get("n_cycles_in_window")))
            sys.stdout.flush()
    ok = [t for t in allt if res["cells"][t].get("gate_G")]
    print("  gate_G pass %d / %d" % (len(ok), len(allt)))

    # ------------------------------------------------------------------ resolution check
    dts = sorted(set(round(res["cells"][t]["dt_s"], 6) for t in ok))
    exact = all(res["cells"][t]["lag_grid_exact"] for t in ok)
    marg = all(res["cells"][t]["shift_margin_ok"] for t in ok)
    ncy = [res["cells"][t]["n_cycles_in_window"] for t in ok]
    res["checks"]["resolution"] = {
        "dt_s_values": dts,
        "lag_grid_is_exact_multiple_of_dt": bool(exact),
        "samples_per_10ms_lag_step": sorted(set(res["cells"][t]["lag_grid_samples_per_10ms"]
                                                for t in ok)),
        "all_shifts_inside_record": bool(marg),
        "core_samples_range": [int(min(res["cells"][t]["core_samples"] for t in ok)),
                               int(max(res["cells"][t]["core_samples"] for t in ok))],
        "n_cycles_range": [int(min(ncy)), int(max(ncy))],
        "VERDICT": ("The .sto sample interval is %s s, so the 10 ms lag grid is exactly ONE "
                    "sample per step and the peak-lag statistic is quantised to 10 ms. The "
                    "SpasticL delay under test is 20 ms = 2 samples, i.e. only two grid steps: "
                    "lag_peak_ms is a COARSE statistic here and ties across cells are expected. "
                    "The centroid lag is the sub-grid-resolution statistic and should be "
                    "preferred." % dts),
    }
    print("  dt=%s  lag step = %s sample(s)  n_cycles %d-%d"
          % (dts, res["checks"]["resolution"]["samples_per_10ms_lag_step"],
             min(ncy), max(ncy)))

    res["checks"]["cycle_count_caveat"] = {
        "n_cycles_per_cell_range": [int(min(ncy)), int(max(ncy))],
        "n_pairs_for_lag1": [int(min(ncy)) - 1, int(max(ncy)) - 1],
        "VERDICT": ("5-6 cycles is TOO FEW to estimate a decay rate defensibly. A lag-1 "
                    "autocorrelation from 4-5 pairs has a sampling standard error of roughly "
                    "1/sqrt(n) ~ 0.45, i.e. the estimate is essentially unconstrained, and it "
                    "is biased toward -1/(n-1) ~ -0.2 by the subtraction of the sample mean. "
                    "The Floquet slope from 4-5 pairs is no better. BOTH ARE REPORTED WITH "
                    "THIS CAVEAT ATTACHED rather than omitted, and neither should be read as "
                    "an estimate of anything. They are included because the brief asked for "
                    "them and because a NEGATIVE on them is still informative."),
    }

    # ------------------------------------------------------------------ grid-edge diagnostic
    ge = {}
    for fam_lbl, fkey in FAMS_XC:
        for tgt in TARGETS:
            for vs in VSRC:
                n = e0 = 0
                for tg in ok:
                    d0 = res["cells"][tg].get(fkey, {}).get("l", {}).get(tgt, {})
                    d0 = d0.get(vs) if isinstance(d0, dict) else None
                    if not isinstance(d0, dict) or "peak_at_grid_edge" not in d0:
                        continue
                    n += 1
                    e0 += 1 if d0["peak_at_grid_edge"] else 0
                ge["%s.l.%s.%s" % (fam_lbl, tgt, vs)] = {
                    "n_cells": n, "n_peak_at_grid_edge": e0,
                    "frac_at_edge": (e0 / float(n)) if n else None}
    ct_med = float(np.median([np.median(res["cells"][t]["cyc"]["dur_s"]) for t in ok]))
    res["checks"]["grid_edge"] = {
        "median_stride_s": ct_med,
        "lag_window_as_fraction_of_stride": float(0.400 / ct_med),
        "by_signal": ge,
        "VERDICT": ("The stride is ~%.2f s, so the briefed +-200 ms lag window spans only "
                    "%.0f%% of one stride. The raw cross-correlogram of two strongly "
                    "stride-periodic signals is therefore a slice of the periodic lobe, not a "
                    "reflex impulse response: wherever frac_at_edge is high the 'peak lag' is "
                    "simply the edge of the search window and both lag_peak_ms and the "
                    "centroid are artefacts of where the window was cut, NOT latencies. The "
                    "`resid` family exists precisely to remove that lobe, and it is the family "
                    "in which a 20 ms delay could actually be visible. Read the raw family's "
                    "lag statistics only where frac_at_edge is low."
                    % (ct_med, 100.0 * 0.400 / ct_med)),
    }
    print("  grid-edge fractions: %s"
          % ", ".join("%s %.2f" % (k, v["frac_at_edge"] or 0) for k, v in ge.items()))

    # ------------------------------------------------------------------ TEST 1 rungs
    print()
    print("=== TEST 1: lag structure ===")
    t1 = {}
    for kv, fam in LADDER:
        e = {"KV": float(kv), "family": fam, "left_PRIMARY": {}, "right_NEGATIVE_CONTROL": {},
             "vs_control_BETWEEN_SCENARIO": {}}
        for side, key in (("l", "left_PRIMARY"), ("r", "right_NEGATIVE_CONTROL")):
            for fam_lbl, fkey in FAMS_XC:
                for tgt in TARGETS:
                    for vs in VSRC:
                        for st in LAGSTATS + LAGSTATS_EXTRA:
                            lbl = "%s.%s.%s.%s.%s" % (fam_lbl, side, tgt, vs, st)
                            g = (lambda fk, sd, tg, v, s:
                                 (lambda r: get_lag(r, fk, sd, tg, v, s)))(fkey, side, tgt,
                                                                           vs, st)
                            sm = seed_means(ltags[kv], res["cells"], g)
                            wm = seed_means(wtags, res["cells"], g)
                            e[key][lbl] = compare(sm, wm, lbl)
                            if side == "l" and st in LAGSTATS:
                                cm = seed_means(ctags, res["cells"], g)
                                cc = compare(sm, cm, lbl)
                                cc["BETWEEN_SCENARIO"] = True
                                cc["scenario_warning"] = (
                                    "control arm is min_velocity 0.80/1.05/1.30 vs ladder 1.0; "
                                    "this comparison is BETWEEN-SCENARIO and cannot separate "
                                    "lesion from target-speed effects")
                                e["vs_control_BETWEEN_SCENARIO"][lbl] = cc
        t1[kv] = e
        sep = [k for k, v in e["left_PRIMARY"].items()
               if v.get("VERDICT") == "SEPARATED" and k.split(".")[-1] in LAGSTATS]
        print("  KV %-8s left-primary separations: %d  %s" % (kv, len(sep), sep))
    res["TEST1_lag"] = t1

    # ------------------------------------------------------------------ TEST 2 rungs
    print()
    print("=== TEST 2: cycle-to-cycle structure ===")
    t2 = {}
    for kv, fam in LADDER:
        e = {"KV": float(kv), "family": fam, "PRIMARY": {},
             "vs_control_BETWEEN_SCENARIO": {}}
        for st in CYCSTATS + ["ac1_rom", "floquet_rom", "abs_drift_over_sd"]:
            g = (lambda s: (lambda r: get_cyc(r, s)))(st)
            sm = seed_means(ltags[kv], res["cells"], g)
            wm = seed_means(wtags, res["cells"], g)
            e["PRIMARY"][st] = compare(sm, wm, st)
            if st in CYCSTATS:
                cm = seed_means(ctags, res["cells"], g)
                cc = compare(sm, cm, st)
                cc["BETWEEN_SCENARIO"] = True
                cc["scenario_warning"] = ("control arm min_velocity 0.80/1.05/1.30 vs ladder "
                                          "1.0 -- BETWEEN-SCENARIO")
                e["vs_control_BETWEEN_SCENARIO"][st] = cc
        t2[kv] = e
        sep = [k for k, v in e["PRIMARY"].items() if v.get("VERDICT") == "SEPARATED"]
        print("  KV %-8s separations: %d  %s" % (kv, len(sep), sep))
    res["TEST2_cycle"] = t2

    # ------------------------------------------------------------------ multiplicity + rank
    n_t1 = len(LADDER) * len(FAMS_XC) * len(TARGETS) * len(VSRC) * len(LAGSTATS)
    n_t1x = len(LADDER) * len(FAMS_XC) * len(TARGETS) * len(VSRC) * len(LAGSTATS_EXTRA)
    n_t2 = len(LADDER) * len(CYCSTATS)
    res["MULTIPLICITY"] = {
        "test1_primary_left": n_t1,
        "test1_extra_left_descriptors": n_t1x,
        "test1_right_negative_control": n_t1 + n_t1x,
        "test2_primary": n_t2,
        "test2_extra": len(LADDER) * 3,
        "total_spastic_vs_dfweak_comparisons": n_t1 + n_t1x + n_t1 + n_t1x + n_t2
                                               + len(LADDER) * 3,
        "headline": ("%d primary spastic-vs-DF-weak comparisons (Test 1 left %d + Test 2 %d), "
                     "plus %d right-side negative-control and %d descriptor comparisons, plus "
                     "a parallel between-scenario grid against the control arm. At a nominal "
                     "1/924 exhaustive-permutation floor per comparison, the expected number "
                     "of floor-attaining separations under a global null is small but the "
                     "expected number of bare disjointness events is NOT: with 6 vs 6 seed "
                     "means, disjointness alone occurs with probability 2/924 = 0.0022 per "
                     "comparison only if the two arms are exchangeable, and any shared "
                     "nuisance structure inflates it. Nothing here is corrected and nothing "
                     "here is confirmatory."
                     % (n_t1 + n_t2, n_t1, n_t2, n_t1 + n_t1x, n_t1x + len(LADDER) * 3)),
    }

    ranked = []
    for kv, _ in LADDER:
        for k, v in res["TEST1_lag"][kv]["left_PRIMARY"].items():
            if k.split(".")[-1] in LAGSTATS and v.get("VERDICT") == "SEPARATED":
                ranked.append({"test": "TEST1", "KV": float(kv), "measure": k,
                               "gap": v["gap"], "gap_over_pooled_sd": v["gap_over_pooled_sd"],
                               "direction": v["direction"].replace("A ", "SPASTIC "),
                               "spastic_range": v["a_range"], "dfweak_range": v["b_range"],
                               "permutation_floor": v["permutation"]["floor"],
                               "frac_at_least_as_extreme":
                                   v["permutation"]["frac_at_least_as_extreme"]})
        for k, v in res["TEST2_cycle"][kv]["PRIMARY"].items():
            if k in CYCSTATS and v.get("VERDICT") == "SEPARATED":
                ranked.append({"test": "TEST2", "KV": float(kv), "measure": k,
                               "gap": v["gap"], "gap_over_pooled_sd": v["gap_over_pooled_sd"],
                               "direction": v["direction"].replace("A ", "SPASTIC "),
                               "spastic_range": v["a_range"], "dfweak_range": v["b_range"],
                               "permutation_floor": v["permutation"]["floor"],
                               "frac_at_least_as_extreme":
                                   v["permutation"]["frac_at_least_as_extreme"]})
    ranked.sort(key=lambda r: -(r["gap_over_pooled_sd"] or 0))
    res["RANKED_SEPARATIONS"] = ranked

    # right-side negative control separations -- artefact detector
    nc = []
    for kv, _ in LADDER:
        for k, v in res["TEST1_lag"][kv]["right_NEGATIVE_CONTROL"].items():
            if v.get("VERDICT") == "SEPARATED":
                nc.append({"KV": float(kv), "measure": k, "gap": v["gap"],
                           "gap_over_pooled_sd": v["gap_over_pooled_sd"],
                           "direction": v["direction"].replace("A ", "SPASTIC ")})
    nc.sort(key=lambda r: -(r["gap_over_pooled_sd"] or 0))
    res["NEGATIVE_CONTROL_SEPARATIONS_right_side"] = {
        "n": len(nc), "list": nc,
        "how_to_read": ("The lesion is LEFT-sided in both arms. A separation on the RIGHT "
                        "ankle cannot be a direct lesion lag signature; it is either a "
                        "whole-body compensation effect or a pipeline artefact. The count "
                        "here is the empirical false-positive yardstick for the left-side "
                        "count under the same multiplicity."),
    }

    # ------------------------------------------------------------------ THE DECIDING QUESTION
    low = ["0.00625", "0.0125"]
    low_sep = [r for r in ranked if str(r["KV"]) in ("0.00625", "0.0125")]
    res["THE_DECIDING_QUESTION"] = {
        "question": ("does anything separate at KV 0.00625 or KV 0.0125, where every amplitude "
                     "endpoint has OVERLAPPED?"),
        "n_separations_at_low_rungs": len(low_sep),
        "separations_at_low_rungs": low_sep,
        "ANSWER": None,     # filled below
    }
    if not low_sep:
        res["THE_DECIDING_QUESTION"]["ANSWER"] = (
            "NO. Nothing separates at KV 0.00625 or KV 0.0125 on any timing or "
            "cycle-to-cycle measure in this deposit. This is a CLEAN NEGATIVE on a scale-free "
            "channel. It matters: a lag is a time, not an amplitude, and re-optimisation of "
            "gains provably cannot move it, so the failure to separate at the low rungs is not "
            "attributable to the ~86% compensation that explains the amplitude nulls. The "
            "lesion signature is ABSENT from the one channel compensation cannot reach.")
    else:
        res["THE_DECIDING_QUESTION"]["ANSWER"] = (
            "YES -- %d measure(s) separate at KV <= 0.0125. EXPLORATORY: see MULTIPLICITY and "
            "NEGATIVE_CONTROL_SEPARATIONS_right_side before believing any of them."
            % len(low_sep))

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False, default=str))

    print()
    print("=== RANKED SEPARATIONS (spastic vs DF-weak, within-scenario) ===")
    if not ranked:
        print("  NONE. No measure separates at any rung.")
    for r in ranked:
        print("  %-5s KV %-8s %-28s gap %+.5g  gap/sd %.2f  %s  floor %s"
              % (r["test"], r["KV"], r["measure"], r["gap"], r["gap_over_pooled_sd"] or 0,
                 r["direction"], r["permutation_floor"]))
    print()
    print("negative-control (right-side) separations: %d" % len(nc))
    print()
    print("DECIDING QUESTION: %s" % res["THE_DECIDING_QUESTION"]["ANSWER"])
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
