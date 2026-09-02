# -*- coding: utf-8 -*-
"""r383 -- FREQUENCY-DOMAIN test of the half-wave-rectifier hypothesis.  EXPLORATORY.

FIRST PRINCIPLES.  The spastic lesion in this corpus is
    ReflexController name=SpasticL { MuscleReflex target=soleus KV=.. allow_neg_V=0
                                     MuscleReflex target=gastroc KV=.. allow_neg_V=0 }
i.e. the added drive is K*max(0, v): a HALF-WAVE RECTIFIER.  The dorsiflexor-weakness lesion
is a pure LINEAR scaling of tib_ant_l max_isometric_force.  Re-optimisation adjusts GAINS,
which are linear operators; a linear operator rescales a signal but cannot synthesise the
harmonic structure a rectifier injects into a near-periodic drive.

PREDICTION (fixed before measurement, recorded here verbatim):
    harmonic content of the spastic arm's signals, expressed as a RATIO to the fundamental
    (scale-free, hence immune to the amplitude suppression that defeated every previous
    endpoint), is HIGHER than the dorsiflexor-weakness arm's, and RISES WITH KV.

NO SINGLE MEASURE WAS NOMINATED IN ADVANCE.  6 signals x 5 harmonic measures x 4 rungs = 120
primary comparisons.  The whole deposit is therefore EXPLORATORY and NOTHING in it is
confirmatory.

CONVENTIONS CARRIED VERBATIM FROM scone/doseladder_r371.py:
    rd()   = the one directory per tag with history.txt >= 91 lines
    sto    = sorted(glob("*.par.sto"))[-1]
    SETTLE = 1.00, T1 = 9.73
    cycles between heel strikes with t[start] >= SETTLE, wholly inside the window,
           drop the LAST kept cycle, require >= 5
    stance = leg0_l.grf_norm_y > 0.05  (grf_vertical returns that threshold)
    seed unit = tag.split("_")[-1]; permutation over seed means only.
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
OUT = r"C:\Users\maurice\Desktop\spasticity_paper\paper\HARMONIC_r383.json"
SETTLE, T1 = 1.0, 9.73
NGRID = 128
NGRID_ALT = 64
KMAX = 8                      # THD sums bins 2..8

LADDER = [("0.00625", "R289KV00625"), ("0.0125", "R289KV0125"),
          ("0.035", "R291KV0035"), ("0.070", "R291KV0070")]
DFWEAK = ["R151W", "R169W090", "R169W095", "R174W870", "R174W892", "R174W915"]
CONTROL = ["R203V080C", "R203V105C", "R203V130C"]

SIGNALS = ["ankle_angle_l", "ankle_l.torque", "soleus_l.activation",
           "gastroc_l.activation", "ankle_vel_l", "ankle_angle_r"]
# ankle_angle_r is a WITHIN-SUBJECT NEGATIVE CONTROL: the lesion is left-sided, so the
# unlesioned right ankle should NOT carry the rectifier's harmonic signature.
RATIOS = ["THD_ratio", "H2_ratio", "H3_ratio", "H4_ratio", "phase2_rel"]
CIRCULAR = {"phase2_rel"}


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


def lesion_audit(fam):
    try:
        d = rd(tags_for([fam])[0])
    except Exception as e:
        return {"error": str(e)}
    a = {"dir": os.path.basename(d)}
    cfg = os.path.join(d, "config.scone")
    if not os.path.exists(cfg):
        return a
    txt = io.open(cfg, encoding="utf-8", errors="replace").read()
    m = re.search(r"min_velocity\s*=\s*([0-9.]+)", txt)
    a["min_velocity"] = float(m.group(1)) if m else None
    a["has_SpasticL"] = "SpasticL" in txt
    a["n_allow_neg_V_0"] = len(re.findall(r"allow_neg_V\s*=\s*0", txt))
    a["n_allow_neg_V_1"] = len(re.findall(r"allow_neg_V\s*=\s*1", txt))
    tg = []
    for m in re.finditer(r"allow_neg_V\s*=\s*0", txt):
        pre = re.findall(r"target\s*=\s*(\S+)", txt[max(0, m.start() - 400):m.start()])
        tg.append(pre[-1] if pre else "?")
    a["rectified_targets"] = tg
    m = re.search(r"name\s*=\s*SpasticL.*?KV\s*=\s*([0-9.]+)", txt, re.S)
    a["config_KV"] = float(m.group(1)) if m else None
    return a


# ---------------------------------------------------------------------------- spectrum core
def spectrum(mean_cycle):
    """rFFT of one phase-resampled mean cycle -> harmonic measures."""
    n = len(mean_cycle)
    X = np.fft.rfft(mean_cycle) / n
    a = np.abs(X)
    if a[1] <= 0 or not np.isfinite(a[1]):
        return None
    thd = float(np.sqrt(np.sum(a[2:KMAX + 1] ** 2)) / a[1])
    ph = float(np.angle(X[2]) - 2.0 * np.angle(X[1]))
    ph = float((ph + np.pi) % (2 * np.pi) - np.pi)     # invariant to phase-origin shift
    return {"A0_dc": float(a[0]), "A1": float(a[1]),
            "THD_ratio": thd,
            "THD_ratio_powerdenom": float(np.sqrt(np.sum(a[2:KMAX + 1] ** 2)) / (a[1] ** 2)),
            "H2_ratio": float(a[2] / a[1]), "H3_ratio": float(a[3] / a[1]),
            "H4_ratio": float(a[4] / a[1]), "phase2_rel": ph,
            "harm_abs": [float(x) for x in a[1:KMAX + 1]]}


def resample(t, y, a, b, ngrid):
    """Cycle [a,b] -> ngrid samples spanning 0..100% of the cycle, endpoint EXCLUDED so the
    grid is a proper periodic sampling for the FFT (including both 0% and 100% would duplicate
    one sample and inject a spurious DC/odd-harmonic step)."""
    tt = t[a:b + 1]
    yy = y[a:b + 1]
    grid = t[a] + (t[b] - t[a]) * np.linspace(0.0, 1.0, ngrid, endpoint=False)
    return np.interp(grid, tt, yy)


def get_signal(cols, dat, t, name):
    if name == "ankle_vel_l":
        ang = S.col(cols, dat, "ankle_angle_l")
        return None if ang is None else np.gradient(ang, t)
    if name.endswith(".activation"):
        mus = name.split("_")[0]
        side = name.split(".")[0].split("_")[-1]
        return S.muscle_signal(cols, dat, mus, side, "activation")
    if name in cols:
        return dat[:, cols.index(name)]
    return S.col(cols, dat, name)


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
    rec["t_end_s"] = float(t[-1])
    rec["dt_s"] = float(np.median(np.diff(t)))
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
    spc = [int(b - a) for a, b in win]
    rec["samples_per_cycle"] = {"min": min(spc), "median": float(np.median(spc)),
                                "max": max(spc), "all": spc}
    rec["cycle_time_s"] = [float(t[b] - t[a]) for a, b in win]
    # stance fraction, retained so the stance convention is visibly the registered one
    on = grf > thr
    rec["stance_frac"] = float(np.mean([np.mean(on[a:b]) for a, b in win]))

    rec["sig"] = {}
    for nm in SIGNALS:
        y = get_signal(cols, dat, t, nm)
        if y is None:
            rec["sig"][nm] = {"error": "column not found"}
            continue
        waves = np.array([resample(t, y, a, b, NGRID) for a, b in win])
        mean_cycle = waves.mean(axis=0)
        sp = spectrum(mean_cycle)
        if sp is None:
            rec["sig"][nm] = {"error": "zero fundamental"}
            continue
        # --- CHECK (a): per-cycle THD vs mean-cycle THD ------------------------------------
        per = [spectrum(w) for w in waves]
        per = [p for p in per if p is not None]
        sp["percycle_THD_mean"] = float(np.mean([p["THD_ratio"] for p in per])) if per else None
        sp["percycle_THD_sd"] = (float(np.std([p["THD_ratio"] for p in per], ddof=1))
                                 if len(per) > 1 else None)
        sp["n_percycle"] = len(per)
        # --- CHECK: 64-point grid (BELOW the raw samples/cycle -> pure downsampling) --------
        w64 = np.array([resample(t, y, a, b, NGRID_ALT) for a, b in win]).mean(axis=0)
        s64 = spectrum(w64)
        sp["THD_ratio_grid64"] = s64["THD_ratio"] if s64 else None
        sp["H2_ratio_grid64"] = s64["H2_ratio"] if s64 else None
        rec["sig"][nm] = sp

    # --- CHECK: interpolation harmonic FLOOR --------------------------------------------
    # A signal that is EXACTLY one sinusoid in cycle-phase, sampled at the true sample times
    # of each cycle, then pushed through the identical resample+average+FFT pipeline.  Any
    # harmonic content it shows is manufactured by linear interpolation / cycle jitter alone.
    synth_waves = []
    for a, b in win:
        tt = t[a:b + 1]
        ph = (tt - t[a]) / (t[b] - t[a])
        yy = np.sin(2 * np.pi * ph)
        grid = np.linspace(0.0, 1.0, NGRID, endpoint=False)
        synth_waves.append(np.interp(grid, ph, yy))
    ssp = spectrum(np.mean(synth_waves, axis=0))
    rec["interp_floor_synth"] = {"THD_ratio": ssp["THD_ratio"], "H2_ratio": ssp["H2_ratio"],
                                 "H3_ratio": ssp["H3_ratio"], "H4_ratio": ssp["H4_ratio"]}
    return rec


# ---------------------------------------------------------------------------- statistics
def seed_means(tags, cells, sig, meas):
    out = {}
    for tg in tags:
        r = cells.get(tg, {})
        if not r.get("gate_G"):
            continue
        s = r.get("sig", {}).get(sig, {})
        v = s.get(meas)
        if v is None or not np.isfinite(v):
            continue
        out.setdefault(tg.split("_")[-1], []).append(float(v))
    if meas in CIRCULAR:
        return {k: float(np.angle(np.mean(np.exp(1j * np.array(v))))) for k, v in out.items()}
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


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return None
    x, y = x[m], y[m]
    sx, sy = x.std(), y.std()
    if sx == 0 or sy == 0:
        return None
    return float(np.mean((x - x.mean()) * (y - y.mean())) / (sx * sy))


def spearman(x, y):
    def rk(v):
        v = np.asarray(v, float)
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v))
        r[o] = np.arange(len(v), dtype=float)
        return r
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return None
    return pearson(rk(x[m]), rk(y[m]))


# ---------------------------------------------------------------------------- main
def main():
    res = {
        "round": "r383",
        "status": "EXPLORATORY -- NO RESULT IN THIS DEPOSIT IS CONFIRMATORY",
        "why_exploratory": (
            "No single signal x measure was nominated in advance. The deposit runs 6 signals x "
            "5 harmonic measures x 4 KV rungs = 120 primary spastic-vs-DFweak comparisons, plus "
            "the same grid against the between-scenario control arm. There is no registration "
            "document for r383 and none was written before measurement, so every separation "
            "reported here is a HYPOTHESIS-GENERATING observation only."),
        "hypothesis": (
            "The spastic lesion is a HALF-WAVE RECTIFIED velocity feedback (MuscleReflex "
            "target=soleus/gastroc, allow_neg_V=0, drive = K*max(0,v)). The DF-weakness lesion "
            "is a linear scaling of tib_ant_l max_isometric_force. Re-optimisation adjusts "
            "gains = linear operators, which can rescale amplitude but cannot synthesise "
            "harmonic structure. So harmonic content RELATIVE to the fundamental should be "
            "higher in the spastic arm and rise with KV."),
        "prediction_fixed_before_measurement": (
            "spastic ratio-measures HIGHER than DF-weak, and MONOTONE INCREASING in KV"),
        "conventions": {
            "source": "scone/doseladder_r371.py (verbatim)",
            "rd": "the one dir per tag with history.txt >= 91 lines",
            "sto": 'sorted(glob("*.par.sto"))[-1]',
            "SETTLE": SETTLE, "T1": T1,
            "cycles": ("between heel strikes with t[start] >= SETTLE, wholly inside the window, "
                       "drop the LAST kept cycle, require >= 5"),
            "stance": "leg0_l.grf_norm_y > 0.05",
            "seed_unit": 'tag.split("_")[-1]',
        },
        "method": {
            "resampling": ("each admissible cycle linearly interpolated onto %d points spanning "
                           "0-100%% of that cycle, endpoint EXCLUDED (periodic grid); the "
                           "per-cycle waveforms are then AVERAGED to one mean cycle per cell"
                           % NGRID),
            "spectrum": "np.fft.rfft(mean_cycle)/N; bin k = k-th harmonic, bin 1 = one per stride",
            "THD_ratio": "sqrt(sum_{k=2..8} |X_k|^2) / |X_1|   (amplitude denominator, standard THD)",
            "THD_ratio_powerdenom": ("sqrt(sum_{k=2..8} |X_k|^2) / |X_1|^2 -- the literal reading "
                                     "of 'power in bin 1' as a denominator; recorded because the "
                                     "brief was ambiguous. NOT scale-free; do not use it."),
            "Hk_ratio": "|X_k| / |X_1|",
            "phase2_rel": ("arg(X_2) - 2*arg(X_1), wrapped to (-pi,pi]. This combination is "
                           "INVARIANT to where the cycle is cut, which arg(X_2)-arg(X_1) is not."),
            "signals": SIGNALS,
            "negative_control_signal": ("ankle_angle_r -- the RIGHT ankle. The lesion is "
                                        "left-sided, so a rectifier signature there is evidence "
                                        "of a pipeline artefact, not of the lesion."),
            "test": ("per rung: disjointness of the 6 spastic seed means against the 6 DF-weak "
                     "seed means; exhaustive permutation over C(12,6)=924. The 924 is reported "
                     "as a FLOOR, never as a p-value."),
        },
        "cells": {}, "lesion_audit": {}, "rungs": {}, "checks": {},
    }

    print("=== lesion audit ===")
    for f in [x[1] for x in LADDER] + DFWEAK + CONTROL:
        res["lesion_audit"][f] = lesion_audit(f)
    mv = {}
    for f, a in res["lesion_audit"].items():
        mv.setdefault(a.get("min_velocity"), []).append(f)
    res["lesion_audit"]["_min_velocity_groups"] = {str(k): sorted(v) for k, v in mv.items()}
    for k in sorted(mv, key=lambda x: (x is None, x)):
        print("  min_velocity=%-6s %s" % (k, ", ".join(sorted(mv[k]))))
    lad = res["lesion_audit"][LADDER[0][1]]
    dfw = res["lesion_audit"][DFWEAK[0]]
    print("  ladder rectified targets : %s" % lad.get("rectified_targets"))
    print("  DFweak rectified targets : %s" % dfw.get("rectified_targets"))
    res["lesion_audit"]["_premise_check"] = {
        "claim": "every velocity feedback other than the spastic one is linear (allow_neg_V=1)",
        "ladder_rectified_targets": lad.get("rectified_targets"),
        "dfweak_rectified_targets": dfw.get("rectified_targets"),
        "verdict": ("PARTLY TRUE: the BASELINE controller already contains one rectified "
                    "velocity feedback (target=vasti) present in ALL arms. The spastic lesion "
                    "ADDS two more (soleus, gastroc) on the left leg. The differential between "
                    "the arms is therefore exactly two added rectifiers, which is what the "
                    "hypothesis needs, but the claim 'every other velocity feedback is linear' "
                    "is not literally correct."),
    }

    print()
    print("=== measurement ===")
    ltags = {kv: tags_for([fam]) for kv, fam in LADDER}
    wtags = tags_for(DFWEAK)
    ctags = tags_for(CONTROL)
    allt = [x for v in ltags.values() for x in v] + wtags + ctags
    for i, tg in enumerate(allt):
        res["cells"][tg] = measure(tg)
        if (i + 1) % 12 == 0:
            print("  %d/%d" % (i + 1, len(allt)))
    ok = [t for t in allt if res["cells"][t].get("gate_G")]
    print("  gate_G pass %d / %d" % (len(ok), len(allt)))

    # ---------------------------------------------------------------- CHECK (b) sampling
    spc = [res["cells"][t]["samples_per_cycle"]["median"] for t in ok]
    spcmin = [res["cells"][t]["samples_per_cycle"]["min"] for t in ok]
    ct = [np.median(res["cells"][t]["cycle_time_s"]) for t in ok]
    nyq = int(np.floor(min(spcmin) / 2.0))
    res["checks"]["b_sampling"] = {
        "dt_s": float(np.median([res["cells"][t]["dt_s"] for t in ok])),
        "sampling_hz": float(1.0 / np.median([res["cells"][t]["dt_s"] for t in ok])),
        "cycle_time_s_median_over_cells": float(np.median(ct)),
        "cycle_time_s_range": [float(np.min(ct)), float(np.max(ct))],
        "raw_samples_per_cycle_median": float(np.median(spc)),
        "raw_samples_per_cycle_min": float(np.min(spcmin)),
        "raw_samples_per_cycle_max": float(np.max([res["cells"][t]["samples_per_cycle"]["max"]
                                                   for t in ok])),
        "grid_points": NGRID,
        "nyquist_harmonic_of_worst_cycle": nyq,
        "verdict": ("Interpolating to %d points is UPSAMPLING relative to the ~%.0f raw samples "
                    "in a typical cycle. Upsampling creates no information: harmonics above the "
                    "raw Nyquist (k = %d for the shortest cycle in the corpus) are pure "
                    "interpolation product. Harmonics 2..8 sit far below that limit and are "
                    "representable. What upsampling DOES do is spread the linear-interpolation "
                    "kink energy across all bins, which is why the synthetic interpolation "
                    "floor (per cell, key interp_floor_synth) must be compared against every "
                    "measured THD before any of it is believed."
                    % (NGRID, float(np.median(spc)), nyq)),
    }
    print("  samples/cycle median %.1f  min %.0f   -> raw Nyquist harmonic k=%d"
          % (np.median(spc), np.min(spcmin), nyq))

    # ---------------------------------------------------------------- CHECK (a) averaging
    ex = ok[0]
    ca = {"cell": ex, "n_cycles": res["cells"][ex]["n_cycles_in_window"], "per_signal": {}}
    for nm in SIGNALS:
        s = res["cells"][ex]["sig"].get(nm, {})
        if "THD_ratio" not in s:
            continue
        ca["per_signal"][nm] = {
            "THD_of_mean_cycle": s["THD_ratio"],
            "mean_of_percycle_THD": s["percycle_THD_mean"],
            "sd_of_percycle_THD": s["percycle_THD_sd"],
            "suppression_ratio_mean_over_percycle": (s["THD_ratio"] / s["percycle_THD_mean"]
                                                     if s["percycle_THD_mean"] else None),
        }
    sup = [v["suppression_ratio_mean_over_percycle"] for v in ca["per_signal"].values()
           if v["suppression_ratio_mean_over_percycle"]]
    ca["verdict"] = ("Mean-cycle THD / mean per-cycle THD ranges %.3f to %.3f across the six "
                     "signals of this cell. A value below 1 means the averaging DOES suppress "
                     "harmonics -- cycle-to-cycle phase jitter makes harmonic k of successive "
                     "cycles cancel k times faster than the fundamental does. The suppression "
                     "is applied identically to both arms, so it biases the measure toward the "
                     "NULL rather than toward a false separation, but it does shrink the effect."
                     % (min(sup), max(sup)) if sup else "no signal available")
    res["checks"]["a_mean_cycle_suppression"] = ca
    print("  check(a) suppression ratios: %s"
          % ", ".join("%s %.3f" % (k, v["suppression_ratio_mean_over_percycle"])
                      for k, v in ca["per_signal"].items()
                      if v["suppression_ratio_mean_over_percycle"]))

    # ---------------------------------------------------------------- interpolation floor
    fl = {}
    for nm in ["THD_ratio", "H2_ratio", "H3_ratio", "H4_ratio"]:
        v = [res["cells"][t]["interp_floor_synth"][nm] for t in ok]
        fl[nm] = {"median": float(np.median(v)), "max": float(np.max(v))}
    res["checks"]["interp_floor_synth"] = {
        "what": ("a pure sinusoid in cycle-phase, sampled at the real sample times of each "
                 "admissible cycle, pushed through the IDENTICAL resample+average+FFT pipeline. "
                 "Anything it shows is manufactured by the pipeline."),
        "floor": fl}
    print("  interpolation floor: THD median %.5f max %.5f"
          % (fl["THD_ratio"]["median"], fl["THD_ratio"]["max"]))

    # ---------------------------------------------------------------- CHECK (c) scale-free
    cc = {}
    for nm in SIGNALS:
        cc[nm] = {}
        A1 = []
        vals = {m: [] for m in RATIOS}
        for t_ in ok:
            s = res["cells"][t_]["sig"].get(nm, {})
            if "A1" not in s:
                continue
            A1.append(s["A1"])
            for m in RATIOS:
                vals[m].append(s.get(m, float("nan")))
        for m in RATIOS:
            cc[nm][m] = {"pearson_vs_A1": pearson(vals[m], A1),
                         "spearman_vs_A1": spearman(vals[m], A1), "n": len(A1)}
        cc[nm]["_A1_range"] = [float(np.min(A1)), float(np.max(A1))] if A1 else None
    res["checks"]["c_ratio_vs_amplitude"] = {
        "what": ("Pearson and Spearman of each ratio against the RAW fundamental amplitude |X_1| "
                 "across all %d gate-G cells of all three arms. A ratio that is genuinely "
                 "scale-free should show no systematic relation; a strong negative correlation "
                 "means the 'harmonic' measure is amplitude suppression wearing a disguise, "
                 "because a shrinking fundamental inflates every ratio that divides by it."
                 % len(ok)),
        "by_signal": cc}

    # ---------------------------------------------------------------- rung tests
    print()
    print("=== rung tests (EXPLORATORY, 120 comparisons) ===")
    ranked = []
    for kv, fam in LADDER:
        e = {"KV": float(kv), "family": fam, "by_signal": {}}
        for nm in SIGNALS:
            e["by_signal"][nm] = {}
            for m in RATIOS + ["A1"]:
                sm = seed_means(ltags[kv], res["cells"], nm, m)
                wm = seed_means(wtags, res["cells"], nm, m)
                cm = seed_means(ctags, res["cells"], nm, m)
                s, w = sorted(sm.values()), sorted(wm.values())
                d = {"n_spastic_seeds": len(s), "n_dfweak_seeds": len(w),
                     "spastic_seed_means": sm, "dfweak_seed_means": wm}
                if len(s) < 4 or len(w) < 4:
                    d["VERDICT"] = "UNINFORMATIVE"
                    e["by_signal"][nm][m] = d
                    continue
                d["spastic_range"] = [s[0], s[-1]]
                d["dfweak_range"] = [w[0], w[-1]]
                d["spastic_mean"] = float(np.mean(s))
                d["dfweak_mean"] = float(np.mean(w))
                gap = max(w[0] - s[-1], s[0] - w[-1])
                d["gap"] = float(gap)
                # scale-free effect size: gap normalised by the pooled spread
                pooled = float(np.std(list(s) + list(w), ddof=1))
                d["gap_over_pooled_sd"] = float(gap / pooled) if pooled > 0 else None
                d["separated"] = bool(gap > 0)
                if gap > 0:
                    d["direction"] = "SPASTIC HIGH" if s[0] > w[-1] else "SPASTIC LOW"
                    d["permutation"] = floor(s, w)
                if m in CIRCULAR:
                    d["CIRCULAR_CAVEAT"] = ("phase2_rel is an ANGLE. Min/max disjointness on a "
                                            "wrapped quantity is not a valid separation test "
                                            "unless both arms sit well away from +-pi. Treat any "
                                            "separation here as suggestive only.")
                if len(cm) >= 4:
                    c = list(cm.values())
                    d["control_mean_BETWEEN_SCENARIO"] = float(np.mean(c))
                    d["control_sd_BETWEEN_SCENARIO"] = float(np.std(c, ddof=1))
                e["by_signal"][nm][m] = d
                if m in RATIOS and d.get("separated"):
                    ranked.append({"KV": float(kv), "signal": nm, "measure": m,
                                   "gap": float(gap), "gap_over_pooled_sd": d["gap_over_pooled_sd"],
                                   "direction": d["direction"],
                                   "spastic_mean": d["spastic_mean"],
                                   "dfweak_mean": d["dfweak_mean"],
                                   "negative_control_signal": nm == "ankle_angle_r",
                                   "circular": m in CIRCULAR})
        res["rungs"][kv] = e
        nsep = sum(1 for nm in SIGNALS for m in RATIOS
                   if e["by_signal"][nm][m].get("separated"))
        print("  KV %-8s separations %d / %d" % (kv, nsep, len(SIGNALS) * len(RATIOS)))

    ranked.sort(key=lambda r: (r["KV"], -(r["gap_over_pooled_sd"] or 0)))
    res["RANKED_SEPARATIONS"] = ranked
    res["MULTIPLICITY"] = {
        "n_signals": len(SIGNALS), "n_ratio_measures": len(RATIOS), "n_rungs": len(LADDER),
        "n_primary_comparisons": len(SIGNALS) * len(RATIOS) * len(LADDER),
        "n_separated": len(ranked),
        "expected_separations_under_pure_noise": (
            "with 6 vs 6 seed means, the chance that two random draws are min/max disjoint is "
            "2/C(12,6) * (number of splits giving disjointness) = 2/924*1 per direction, i.e. "
            "2/924 = 0.00216 per comparison under exchangeability; over %d comparisons the "
            "expected count of chance separations is %.3f"
            % (len(SIGNALS) * len(RATIOS) * len(LADDER),
               2.0 / 924.0 * len(SIGNALS) * len(RATIOS) * len(LADDER))),
        "statement": ("This deposit is EXPLORATORY. 120 primary comparisons were run and no "
                      "single measure was nominated in advance. No result in this file is "
                      "confirmatory and none may be reported as a confirmed effect."),
    }

    # ---------------------------------------------------------------- monotonicity in KV
    mono = {}
    for nm in SIGNALS:
        mono[nm] = {}
        for m in RATIOS:
            seq = []
            for kv, _ in LADDER:
                d = res["rungs"][kv]["by_signal"][nm][m]
                if "spastic_mean" in d:
                    seq.append((float(kv), d["spastic_mean"]))
            seq.sort()
            mono[nm][m] = {
                "rung_means": {str(a): b for a, b in seq},
                "monotone_increasing": bool(all(seq[i][1] <= seq[i + 1][1] + 1e-12
                                                for i in range(len(seq) - 1))),
                "spearman_vs_KV": spearman([a for a, _ in seq], [b for _, b in seq]),
            }
    res["MONOTONICITY_IN_KV"] = mono

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(res, indent=2, ensure_ascii=False, sort_keys=False))
    print()
    print("ranked separations (smallest KV first):")
    for r in ranked[:40]:
        print("  KV %-8s %-22s %-12s gap %+.5f  %.2f pooled-sd  %s%s%s"
              % (r["KV"], r["signal"], r["measure"], r["gap"],
                 r["gap_over_pooled_sd"] or 0, r["direction"],
                 "  [NEGATIVE-CONTROL SIGNAL]" if r["negative_control_signal"] else "",
                 "  [CIRCULAR]" if r["circular"] else ""))
    if not ranked:
        print("  NONE. No signal x measure separates at any rung.")
    print()
    print("wrote %s (%d B)" % (OUT, os.path.getsize(OUT)))


main()
