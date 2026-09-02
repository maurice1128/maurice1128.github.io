"""DOES `ank_rom` SURVIVE A CAMERA?  A 2D video-degradation study of the ROM discriminator.

WHY THIS EXISTS
---------------
`ank_rom` (sagittal ankle range of motion over GRF-delimited gait cycles, 1.0 s settle) separates
the SPASTIC arm from the WEAK arm completely at condition level in noiseless simulated joint
angles, and 39/40 at seed level with a fitted threshold (paper/ROM_REANALYSIS.json). The
unlesioned reference is 20.0134 deg; spastic runs sit below it, weak runs above.

`scone/video_observable.py` records why that is not enough. Five earlier candidate features in
this project failed for one shared reason: every one was a MAGNITUDE of a joint angle, and the
surviving margin sat below the post-stroke ankle minimal detectable change (MDC) of 3.8-11.5 deg.
`ank_rom` has exactly that shape again. Against the 20.0134 deg reference only three of five
spastic rungs clear 3.8 deg, none by more than 0.4 deg, and BOTH MILD rungs fall far short. The
intended use is mass screening from a cheap 2D sagittal phone video with no EMG, so the question
that decides the paper is not whether ROM separates in clean data -- it does -- but whether it
still separates after being observed through a camera, AT THE MILD DOSES A SCREENING TOOL EXISTS
TO SERVE. Severe cases are clinically obvious; a tool that only works on them is close to useless.
That is why every result below is SPLIT INTO MILD AND SEVERE RUNGS. The split is the study.

NO SIMULATION IS RUN. All 48 trajectories already exist under scone/replay_crossed/.

THE OBSERVATION MODEL, AND EVERY ASSUMPTION IN IT
-------------------------------------------------
The pipeline mimics the real order of operations in a markerless 2D pipeline:

  clean 100 Hz joint angles
    -> (1) reconstruct absolute sagittal SEGMENT orientations (shank, foot)
    -> (2) FRAME CAPTURE: resample to the video frame rate fs (30 Hz primary, 60 Hz sensitivity)
    -> (3) OUT-OF-PLANE ROTATION: orthographic projection of each segment at yaw theta
    -> (4) POSE-ESTIMATOR NOISE: i.i.d. per-frame Gaussian on the observed ankle angle
    -> (5) 6 Hz 4th-order zero-phase Butterworth low-pass (what a gait lab does)
    -> (6) `ank_rom` = mean over complete gait cycles of the per-cycle peak-to-peak angle

A1  SEGMENT RECONSTRUCTION.  A camera does not see a joint angle; it sees two segments. The
    H0914M model is planar and every joint rotates about the same lateral axis, so absolute
    sagittal rotations chain by addition:
        q_shank = pelvis_tilt + hip_flexion_l + knee_angle_l
        q_foot  = q_shank + ankle_angle_l
    Verified against the data: knee_angle_l is negative in flexion (-73..+1 deg) and
    ankle_angle_l positive in dorsiflexion (-14..+11 deg), which is the sign pattern this sum
    requires. In the sagittal plane the shank unit vector (knee -> ankle) is
        v_shank = ( sin q_shank, -cos q_shank )        [neutral = straight down]
    and the foot unit vector (ankle -> toe) is
        v_foot  = ( cos q_foot,   sin q_foot )         [neutral = straight forward]
    ASSUMED: the foot's visual long axis is perpendicular to the shank at ankle_angle = 0, i.e.
    the model's calcaneus long axis is taken as the segment a pose estimator would see. A real
    foot keypoint set (ankle-heel-toe) has a small fixed pitch offset; it is a CONSTANT and
    therefore cancels out of a range of motion, so it is not modelled.

A2  OUT-OF-PLANE ROTATION (yaw theta).  ASSUMED CAMERA GEOMETRY: orthographic (weak-perspective)
    projection, optical axis horizontal, subject's progression direction rotated by theta about
    the VERTICAL axis relative to the image plane. Weak perspective is the standard assumption
    when subject depth is small against camera distance; it is stated, not proven, and it is
    OPTIMISTIC (true perspective adds scale drift across the frame).
    Under that geometry the image horizontal axis is u = (cos theta, 0, -sin theta) and the image
    vertical axis is w = (0, 1, 0), so for any sagittal-plane vector (x, y) the observed image
    vector is (x * cos theta, y): THE ANTERIOR COMPONENT IS FORESHORTENED BY cos theta AND THE
    VERTICAL COMPONENT IS PRESERVED. Applied to each segment separately:
        q_shank' = atan2( sin q_shank * cos theta,  cos q_shank )
        q_foot'  = atan2( sin q_foot,   cos q_foot * cos theta )
        observed ankle angle = q_foot' - q_shank'
    NOTE THE ASYMMETRY, which is a real consequence and not a modelling choice: the near-VERTICAL
    shank is angularly COMPRESSED by yaw (q' ~ q cos theta) while the near-HORIZONTAL foot is
    angularly EXPANDED (q' ~ q / cos theta). The observed ankle angle is therefore NOT a simple
    rescaling of the true one. At theta = 0 the identity q_foot' - q_shank' = ankle_angle holds
    exactly, which is the built-in check of this code.
    Yaw is swept, both as a FIXED value (one camera setup, same error for everybody) and as a
    RANDOM per-subject draw theta ~ U(0, theta_max) (a screening clinic, every subject filmed at
    a different angle), because the second is the deployment case and is strictly harder.

A3  POSE-ESTIMATOR NOISE.  Modelled as i.i.d. per-frame additive Gaussian of standard deviation
    SIGMA_DEG on the observed ankle angle. i.i.d. is the OPTIMISTIC case: real markerless error
    is temporally correlated and carries a per-limb bias, and correlated error survives a 6 Hz
    low-pass far better than white noise does.
    MAPPING FROM PIXELS TO DEGREES, with the limb-length assumption stated. Three keypoints:
    knee K, ankle A, toe T, each with i.i.d. isotropic error of SIGMA_PX pixels. Shank
    orientation alpha comes from (K - A), foot orientation beta from (A - T). For small errors a
    perpendicular displacement e of an endpoint of a segment of pixel length L rotates it by e/L,
    so Var(alpha) = 2 SIGMA_PX^2 / L_shank^2 and Var(beta) = 2 SIGMA_PX^2 / L_foot^2. The shared
    ankle point A contributes to both, but through PERPENDICULAR directions (shank and foot are
    ~90 deg apart), so that covariance is ~0 and is dropped. Hence
        SIGMA_DEG ~ SIGMA_PX * sqrt( 2/L_shank^2 + 2/L_foot^2 )   [radians, then to degrees]
    ASSUMED ANTHROPOMETRY AND FRAMING: subject height 1.70 m; Winter segment ratios give
    shank (knee->ankle) 0.246*H = 0.418 m and ankle->toe 0.112*H = 0.190 m; the subject occupies
    900 px of height in a 1080p frame, i.e. 529 px/m. Because SIGMA_PX and the framing are BOTH
    uncertain, the swept quantity is SIGMA_DEG itself and the px equivalents are reported for
    1080p AND 720p framing, rather than one px value being picked.

A4  FRAME RATE.  Linear interpolation onto a uniform fs grid. Motion blur, rolling shutter and
    compression artefacts are NOT modelled -- another way this study is optimistic.

A5  GAIT-CYCLE SEGMENTATION IS TAKEN FROM THE CLEAN GROUND-REACTION FORCE and held FIXED across
    every noise level and repetition. A video pipeline has no force plate and must detect
    contacts from the noisy kinematics, which adds a second, independent failure mode. Holding
    the cycles clean isolates the effect of noise on the ANGLE alone and makes every number
    below an UPPER BOUND on real-world performance. If a feature fails here it fails in the
    clinic; the converse does not follow.

A6  `ank_rom` is a peak-to-peak, i.e. a max-minus-min. Additive noise can only INFLATE it, so
    noise imposes a POSITIVE BIAS on every run. That bias is roughly common to both arms, so a
    threshold FITTED under noise partly absorbs it, while a FIXED threshold calibrated on clean
    data cannot. This is predicted (PR4) rather than discovered.

CLASSIFICATION -- THREE RULES, ONLY ONE OF WHICH INVOLVES ANY FITTING
--------------------------------------------------------------------
  LOSO       leave-one-seed-out cross-validation. Seeds s1..s4; for each held-out seed the
             threshold is fitted on the OTHER THREE seeds only and applied to the held-out one.
             The DIRECTION is FIXED A PRIORI (spastic = below threshold), never fitted, so a
             collapsed feature scores 50% rather than being rescued by a sign flip. Chance = 50%.
  REF        the fixed clean-data reference threshold 20.0134 deg. No fitting whatsoever.
  REFCAL     the mean `ank_rom` of the 8 unlesioned reference runs (HEALTHY, DR2K000) MEASURED
             THROUGH THE SAME DEGRADED PIPELINE in the same repetition. Still no fitting on
             labelled patient data -- healthy controls are trivial to film -- so this is the
             fair no-fit rule a real deployment would actually use.

PREDICTED OUTCOME IS REGISTERED IN paper/VIDEO_DEGRADATION_REGISTRATION.txt WITH THE SHA-256 OF
THIS FILE, WRITTEN BEFORE THE SCRIPT WAS EVER EXECUTED.
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sto_utils as S  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPLAY = os.path.join(HERE, "replay_crossed")
OUT = os.path.abspath(os.path.join(HERE, "..", "paper", "VIDEO_DEGRADATION.json"))

# ---------------------------------------------------------------------------------------------
# EVERY CHOSEN PARAMETER, IN ONE PLACE. Each is flagged in the registration file.
# ---------------------------------------------------------------------------------------------
SETTLE = 1.0            # s, discarded transient -- inherited from the registered feature
FC = 6.0                # Hz low-pass cutoff, 4th order, zero-phase (filtfilt) -- CHOSEN, standard
BUTTER_ORDER = 4        # CHOSEN, standard for clinical gait kinematics
N_REP = 200             # random-noise repetitions per run per cell -- CHOSEN
FS_LIST = [30.0, 60.0]  # Hz, phone video primary / sensitivity
SIGMA_DEG = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]   # swept, CHOSEN range
YAW_FIXED = [0.0, 10.0, 20.0, 30.0]     # deg, CHOSEN sweep
YAW_RANDOM = [15.0, 30.0]               # theta ~ U(0, max), CHOSEN sweep
REF_THRESHOLD = 20.013352185604393      # paper/ROM_REANALYSIS.json, clean unlesioned reference
MDC_DEG = 3.8                           # lowest published post-stroke ankle MDC (3.8-11.5)
SEED = 20260803                         # RNG seed, fixed for reproducibility

# anthropometry / framing for the px <-> deg mapping (A3)
HEIGHT_M = 1.70
L_SHANK_M = 0.246 * HEIGHT_M
L_FOOT_M = 0.112 * HEIGHT_M
PX_PER_M_1080 = 900.0 / HEIGHT_M        # subject fills 900 px of a 1080p frame
PX_PER_M_720 = 600.0 / HEIGHT_M         # same framing at 720p

SPASTIC = ["DR2K050", "DR2K075", "DR2K100", "DR2K150", "DR2K200"]
WEAK = ["PAR20", "PAR40", "PAR60", "CMW70", "CMW80"]
REFERENCE = ["HEALTHY", "DR2K000"]
SPLITS = {
    "MILD": (["DR2K050", "DR2K075"], ["PAR20", "PAR40"]),
    "SEVERE": (["DR2K150", "DR2K200"], ["CMW70", "CMW80"]),
    "ALL": (SPASTIC, WEAK),
}


def deg_per_px(px_per_m):
    """A3: angular sd (deg) produced by 1 px of i.i.d. keypoint error."""
    ls, lf = L_SHANK_M * px_per_m, L_FOOT_M * px_per_m
    return float(np.degrees(np.sqrt(2.0 / ls ** 2 + 2.0 / lf ** 2)))


# ---------------------------------------------------------------------------------------------
def load_runs():
    """-> list of dicts: tag, cond, seed, q_shank, q_foot (rad, 100 Hz), t, cycle time windows."""
    runs = []
    for d in sorted(glob.glob(os.path.join(REPLAY, "*"))):
        if not os.path.isdir(d):
            continue
        tag = os.path.basename(d)
        cond = tag.rsplit("_s", 1)[0]
        if cond not in SPASTIC + WEAK + REFERENCE:
            continue
        st = [x for x in glob.glob(os.path.join(d, "*.sto")) if os.path.getsize(x) > 1000]
        if len(st) != 1:
            raise RuntimeError("expected exactly one .sto in %s, found %d" % (d, len(st)))
        cols, data = S.load_sto(st[0])
        t = np.asarray(data[:, 0], float)
        pel = np.asarray(S.col(cols, data, "pelvis_tilt"), float)
        hip = np.asarray(S.col(cols, data, "hip_flexion_l"), float)
        kne = np.asarray(S.col(cols, data, "knee_angle_l"), float)
        ank = np.asarray(S.col(cols, data, "ankle_angle_l"), float)
        q_shank = pel + hip + kne                       # A1
        q_foot = q_shank + ank                          # A1
        grf, thr = S.grf_vertical(cols, data, "l")
        hs = [i for i in S.heel_strikes(t, grf, thresh=thr) if t[i] >= SETTLE]
        cyc = [(hs[i], hs[i + 1]) for i in range(len(hs) - 1)][:-1]   # A5, drop last cycle
        if len(cyc) < 2:
            raise RuntimeError("fewer than 2 complete cycles in %s" % tag)
        runs.append({
            "tag": tag, "cond": cond, "seed": int(tag.rsplit("_s", 1)[1]),
            "t": t, "q_shank": q_shank, "q_foot": q_foot, "ank_clean": np.degrees(ank),
            "cyc_t": [(float(t[a]), float(t[b])) for a, b in cyc],
            "clean_rom": float(np.mean([np.ptp(np.degrees(ank)[a:b]) for a, b in cyc])),
            "n_cycles": len(cyc),
        })
    return runs


def prepare(run, fs):
    """A4 frame capture: segment orientations and cycle index windows on the fs grid."""
    t = run["t"]
    grid = np.arange(t[0], t[-1] + 1e-12, 1.0 / fs)
    qs = np.interp(grid, t, run["q_shank"])
    qf = np.interp(grid, t, run["q_foot"])
    wins = []
    for a, b in run["cyc_t"]:
        i = int(np.searchsorted(grid, a))
        j = int(np.searchsorted(grid, b))
        if j - i >= 3:
            wins.append((i, j))
    return grid, qs, qf, wins


def project(qs, qf, cos_t):
    """A2: orthographic sagittal projection at yaw. cos_t broadcasts over repetitions."""
    qs_o = np.arctan2(np.sin(qs) * cos_t, np.cos(qs))
    qf_o = np.arctan2(np.sin(qf), np.cos(qf) * cos_t)
    return np.degrees(qf_o - qs_o)


def rom_matrix(ang, wins, b, a):
    """A6: 6 Hz zero-phase low-pass, then mean per-cycle peak-to-peak. ang is (nrep, nsamp)."""
    y = signal.filtfilt(b, a, ang, axis=-1)
    return np.mean([np.ptp(y[:, i:j], axis=-1) for i, j in wins], axis=0)


# ---------------------------------------------------------------------------------------------
def fit_threshold(vals, lab):
    """Threshold maximising training accuracy with the DIRECTION FIXED (spastic = below).

    lab: 1 = spastic. Candidates are midpoints of the sorted training values plus the two
    open ends; ties are broken by the median candidate, which is deterministic and does not
    look at the test set.
    """
    v = np.sort(np.unique(vals))
    cand = np.concatenate(([v[0] - 1.0], (v[:-1] + v[1:]) / 2.0, [v[-1] + 1.0]))
    acc = np.array([np.mean((vals < c).astype(int) == lab) for c in cand])
    best = cand[acc == acc.max()]
    return float(np.median(best))


def loso_accuracy(vals, lab, seeds):
    correct = n = 0
    for k in sorted(set(seeds)):
        tr = seeds != k
        te = ~tr
        if tr.sum() < 2 or te.sum() == 0 or len(set(lab[tr])) < 2:
            continue
        thr = fit_threshold(vals[tr], lab[tr])
        correct += int(np.sum((vals[te] < thr).astype(int) == lab[te]))
        n += int(te.sum())
    return correct / n if n else np.nan


def evaluate(rom, runs, ridx):
    """rom: (nrep, nrun). -> per-split per-rep accuracies and margins."""
    out = {}
    ref_rom = rom[:, ridx["_REF_"]].mean(axis=1)                    # REFCAL, per repetition
    for name, (sp_c, wk_c) in SPLITS.items():
        idx = np.array([i for i, r in enumerate(runs) if r["cond"] in sp_c + wk_c])
        lab = np.array([1 if runs[i]["cond"] in sp_c else 0 for i in idx])
        seeds = np.array([runs[i]["seed"] for i in idx])
        V = rom[:, idx]
        nrep = V.shape[0]
        loso = np.array([loso_accuracy(V[r], lab, seeds) for r in range(nrep)])
        ref = np.mean((V < REF_THRESHOLD).astype(int) == lab, axis=1)
        refcal = np.mean((V < ref_rom[:, None]).astype(int) == lab, axis=1)
        gm_sp = V[:, lab == 1].mean(axis=1)
        gm_wk = V[:, lab == 0].mean(axis=1)
        # condition-mean gap: worst spastic rung vs worst weak rung (the margin that must
        # exceed the MDC for the sign to be clinically detectable)
        cs = [np.mean([V[:, j] for j, i in enumerate(idx) if runs[i]["cond"] == c], axis=0)
              for c in sp_c]
        cw = [np.mean([V[:, j] for j, i in enumerate(idx) if runs[i]["cond"] == c], axis=0)
              for c in wk_c]
        gap = np.min(cw, axis=0) - np.max(cs, axis=0)
        out[name] = {
            "n_runs": int(len(idx)),
            "loso_mean": float(np.mean(loso)), "loso_sd": float(np.std(loso)),
            "loso_p05": float(np.percentile(loso, 5)),
            "loso_p025": float(np.percentile(loso, 2.5)),
            "loso_p975": float(np.percentile(loso, 97.5)),
            "ref_mean": float(np.mean(ref)), "ref_sd": float(np.std(ref)),
            "refcal_mean": float(np.mean(refcal)), "refcal_sd": float(np.std(refcal)),
            "margin_groupmean": float(np.mean(gm_wk - gm_sp)),
            "margin_groupmean_sd": float(np.std(gm_wk - gm_sp)),
            "margin_gap": float(np.mean(gap)), "margin_gap_sd": float(np.std(gap)),
            "rom_spastic": float(np.mean(gm_sp)), "rom_weak": float(np.mean(gm_wk)),
        }
    out["_ref_rom"] = float(np.mean(ref_rom))
    return out


def main():
    rng = np.random.default_rng(SEED)
    runs = load_runs()
    ridx = {"_REF_": np.array([i for i, r in enumerate(runs) if r["cond"] in REFERENCE])}
    print("loaded %d runs (%d spastic-arm, %d weak-arm, %d reference)"
          % (len(runs),
             sum(r["cond"] in SPASTIC for r in runs), sum(r["cond"] in WEAK for r in runs),
             len(ridx["_REF_"])))
    dpp_1080, dpp_720 = deg_per_px(PX_PER_M_1080), deg_per_px(PX_PER_M_720)
    print("px->deg mapping: 1080p %.4f deg/px   720p %.4f deg/px" % (dpp_1080, dpp_720))

    prep = {}
    for fs in FS_LIST:
        b, a = signal.butter(BUTTER_ORDER, FC / (fs / 2.0), btype="low")
        prep[fs] = (b, a, [prepare(r, fs) for r in runs])

    cells = []
    yaws = [("fixed", y) for y in YAW_FIXED] + [("random", y) for y in YAW_RANDOM]
    for fs in FS_LIST:
        b, a, pr = prep[fs]
        for ymode, ymax in yaws:
            for sd in SIGMA_DEG:
                nrep = 1 if (sd == 0.0 and ymode == "fixed") else N_REP
                rom = np.empty((nrep, len(runs)))
                for k, (grid, qs, qf, wins) in enumerate(pr):
                    if ymode == "fixed":
                        cos_t = np.cos(np.radians(ymax))
                        ang = project(qs, qf, cos_t)[None, :]
                        ang = np.repeat(ang, nrep, axis=0) if nrep > 1 else ang
                    else:
                        th = rng.uniform(0.0, ymax, size=nrep)     # A2 per-subject random yaw
                        ang = project(qs[None, :], qf[None, :], np.cos(np.radians(th))[:, None])
                    if sd > 0:
                        ang = ang + rng.normal(0.0, sd, size=ang.shape)
                    rom[:, k] = rom_matrix(ang, wins, b, a)
                res = evaluate(rom, runs, ridx)
                cells.append({"fs": fs, "yaw_mode": ymode, "yaw_deg": ymax, "sigma_deg": sd,
                              "sigma_px_1080p": sd / dpp_1080, "sigma_px_720p": sd / dpp_720,
                              "n_rep": nrep, "splits": res})
        print("  fs=%g done" % fs)

    # ---- baseline: what the pipeline alone does with NO noise and NO yaw --------------------
    base = {}
    for fs in FS_LIST:
        b, a, pr = prep[fs]
        v = {}
        for r, (grid, qs, qf, wins) in zip(runs, pr):
            v[r["tag"]] = float(rom_matrix(project(qs, qf, 1.0)[None, :], wins, b, a)[0])
        base["fs%g" % fs] = v
    clean = {r["tag"]: r["clean_rom"] for r in runs}

    def condmean(dd, c):
        return float(np.mean([x for k, x in dd.items() if k.rsplit("_s", 1)[0] == c]))

    print("\n--- pipeline bias at zero noise, zero yaw (deg) ---")
    print("%-9s %9s %9s %9s" % ("cond", "clean100", "30Hz+6Hz", "delta"))
    for c in SPASTIC + WEAK + REFERENCE:
        print("%-9s %9.3f %9.3f %+9.3f"
              % (c, condmean(clean, c), condmean(base["fs30"], c),
                 condmean(base["fs30"], c) - condmean(clean, c)))

    # ---- headline table ---------------------------------------------------------------------
    def show(fs, ymode, ymax):
        print("\n=== fs=%g Hz, yaw %s %g deg  (LOSO / REF / REFCAL accuracy, margin vs MDC %.1f) ==="
              % (fs, ymode, ymax, MDC_DEG))
        print("%6s %7s | %-22s | %-22s | %8s %8s"
              % ("sd_deg", "sd_px", "MILD loso ref refcal", "SEVERE loso ref refcal",
                 "MILDmarg", "SEVmarg"))
        for c in cells:
            if c["fs"] != fs or c["yaw_mode"] != ymode or c["yaw_deg"] != ymax:
                continue
            m, s = c["splits"]["MILD"], c["splits"]["SEVERE"]
            print("%6.1f %7.2f | %.3f%s %.3f %.3f | %.3f %.3f %.3f | %+8.2f %+8.2f"
                  % (c["sigma_deg"], c["sigma_px_1080p"],
                     m["loso_mean"], "*" if m["loso_p05"] <= 0.5 else " ",
                     m["ref_mean"], m["refcal_mean"],
                     s["loso_mean"], s["ref_mean"], s["refcal_mean"],
                     m["margin_gap"], s["margin_gap"]))
        print("  * = 5th percentile of the per-repetition LOSO accuracy has reached chance (0.50)")

    for ymode, ymax in yaws:
        show(30.0, ymode, ymax)
    show(60.0, "fixed", 0.0)

    # ---- registered summary numbers ---------------------------------------------------------
    def crossing(fs, ymode, ymax, split, key, rule):
        cs = sorted([c for c in cells
                     if c["fs"] == fs and c["yaw_mode"] == ymode and c["yaw_deg"] == ymax],
                    key=lambda c: c["sigma_deg"])
        for c in cs:
            if rule(c["splits"][split][key]):
                return c["sigma_deg"]
        return None

    summary = {}
    for ymode, ymax in yaws:
        tagn = "fs30_yaw_%s_%g" % (ymode, ymax)
        summary[tagn] = {
            "mild_chance_sigma_deg": crossing(30.0, ymode, ymax, "MILD", "loso_p05",
                                              lambda x: x <= 0.5),
            "mild_useless_sigma_deg": crossing(30.0, ymode, ymax, "MILD", "loso_mean",
                                               lambda x: x < 0.60),
            "severe_chance_sigma_deg": crossing(30.0, ymode, ymax, "SEVERE", "loso_p05",
                                                lambda x: x <= 0.5),
            "mild_ref_useless_sigma_deg": crossing(30.0, ymode, ymax, "MILD", "ref_mean",
                                                   lambda x: x < 0.60),
            "mild_margin_below_mdc_sigma_deg": crossing(30.0, ymode, ymax, "MILD", "margin_gap",
                                                        lambda x: x < MDC_DEG),
        }

    print("\n=== REGISTERED SUMMARY (fs = 30 Hz) ===")
    for k, v in summary.items():
        print("  %-22s mild->chance at sd=%s ; mild<60%% at sd=%s ; severe->chance at sd=%s ; "
              "mild REF<60%% at sd=%s ; mild gap<MDC at sd=%s"
              % (k, v["mild_chance_sigma_deg"], v["mild_useless_sigma_deg"],
                 v["severe_chance_sigma_deg"], v["mild_ref_useless_sigma_deg"],
                 v["mild_margin_below_mdc_sigma_deg"]))

    out = {
        "what": "2D video-degradation study of the ank_rom spastic-vs-weak discriminator",
        "no_simulation_run": True,
        "source": os.path.abspath(REPLAY),
        "n_runs": len(runs),
        "parameters": {
            "settle_s": SETTLE, "lowpass_hz": FC, "butter_order": BUTTER_ORDER,
            "n_rep": N_REP, "fs_list": FS_LIST, "sigma_deg": SIGMA_DEG,
            "yaw_fixed_deg": YAW_FIXED, "yaw_random_max_deg": YAW_RANDOM,
            "ref_threshold_deg": REF_THRESHOLD, "mdc_deg": MDC_DEG, "rng_seed": SEED,
            "height_m": HEIGHT_M, "l_shank_m": L_SHANK_M, "l_foot_m": L_FOOT_M,
            "deg_per_px_1080p": dpp_1080, "deg_per_px_720p": dpp_720,
        },
        "clean_rom_per_run": clean,
        "pipeline_baseline_rom": base,
        "cells": cells,
        "summary": summary,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("\nwrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
