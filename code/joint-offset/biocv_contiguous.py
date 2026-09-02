"""Does filtering move the offset share? The one re-analysis the reviews asked for.

Every error in this paper is an UNFILTERED markerless estimate against a 12 Hz-filtered
marker-based reference, because trials are sampled every ninth frame and 45 ms between retained
frames admits no temporal filter. The manuscript states the direction of that bias -- filtering
would shrink the random half and so RAISE the offset share, making the reported figure
conservative -- but states it as an argument, not a measurement. The sampling was a compute choice
and not a property of the data, so the measurement is available.

This re-detects a CONTIGUOUS window for a subset of participants, applies the reference's own
filter to the markerless trajectories, and recomputes the bias/variance split both ways.

================================================================================================
THE READING IS FIXED HERE, BEFORE THE NUMBERS EXIST.
================================================================================================

  (1) DIRECTION. If filtering RAISES the offset share at hip and knee, the manuscript's stated
      direction is confirmed and may be quoted as measured rather than argued.
      If it LOWERS the share, the Limitations statement is WRONG and must be reversed: the
      reported share would then be optimistic, not conservative, and the headline figure would
      need restating against the filtered value.

  (2) SIZE. Report the shift in percentage points whichever way it falls. A shift under 5 points
      leaves the manuscript's numbers usable as they stand; 5 points or more must be carried into
      Section 3.1 and the abstract, as the timing bracket already is.

  (3) SCOPE. This is a subset, not the whole dataset, so it settles the DIRECTION of the bias and
      bounds its size on these participants. It does not replace the headline figure, and the
      manuscript must not quote it as if it did.

  (5) THE ANGLE HALF. The share is only one of the two things the sampling can bias, and it is
      the one that favours nothing. The paper's deployable ANGLE finding is that discarding
      cameras costs 0.14-0.19 deg of the thigh-shank angle. Discarding adds high-frequency
      jitter and a temporal filter removes it, so an unfiltered estimate scored against a
      12 Hz-filtered reference attributes to discarding an error no deployed pipeline would
      report. That bias runs IN THE PAPER'S FAVOUR, so arguing its direction is not a
      defence. It is measured here.

      The rejection cost is MAE(object-space rejection) - MAE(no rejection) on the
      thigh-shank angle, computed per participant, raw and with the reference's own filter
      applied to the markerless joint positions before the angle is formed.

        - If the filtered cost keeps its sign and at least HALF its raw magnitude, the
          manuscript's angle conclusion stands and may be quoted as filter-robust.
        - If it falls below half, Section 3.2 and the Conclusion must say the cost is
          substantially an artefact of unfiltered estimates.
        - If it REVERSES, the angle conclusion is wrong and must be withdrawn.

  (4) A NULL IS REPORTABLE. If the share moves by less than a point in either direction, that is
      the finding: the sampling choice did not matter, and the Limitations caveat can be retired
      rather than restated.

-> D:/BioCV/_cache_contig/*.pkl   and   D:/BioCV/BIOCV_CONTIGUOUS.txt
"""
import glob
import io
import os
import pickle
import sys

import cv2
import numpy as np
from scipy.signal import butter, filtfilt

sys.path.insert(0, "D:/ROWV_paper")
DEVICE = os.environ.get("BIOCV_DEVICE", "cuda")
if DEVICE == "cuda":
    import cuda_init  # noqa  (must precede rtmlib/onnxruntime import)
import ezc3d
from rtmlib import Body

import rowv as R
from biocv_calib import load_biocv_cameras

PIDS = os.environ.get("BIOCV_CONTIG_PIDS",
                      "P03,P04,P06,P08,P09,P10,P13,P16,P17,P26,P28").split(",")
# Trials per participant. Re-detecting a whole contiguous window across nine views costs about
# 35 minutes a trial, against 60 sampled frames in the main analysis, so all 11 per participant
# would take half a day. This is a COMPUTE bound and is declared as one, the same kind of bound
# as the 60-frame sampling it exists to test; the pre-registered reading above asks only for the
# DIRECTION of the filtering bias, which does not need every trial. Completed trials are cached
# per trial, so raising this later resumes rather than restarts.
# One trial per participant across all eleven, which is the configuration this file's artefact
# reports. A four-trial budget was launched to give the post-hoc filtered test more than eleven
# differences and was stopped before it completed; the budget is returned to the published one
# so that the script and its artefact agree.
MAXTR = int(os.environ.get("BIOCV_CONTIG_MAX", "1"))
NFRAMES = int(os.environ.get("BIOCV_CONTIG_N", "600"))       # 3.0 s at 200 Hz
DST = "D:/BioCV/_cache_contig"
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_CONTIGUOUS.txt")
FS, FC, ORDER = 200.0, 12.0, 4
MIN_CAM = 4
K_MAD = 3.0                       # the adaptive rule of Section 2.2
SIDES = {"L": (11, 13, 15), "R": (12, 14, 16)}   # hip, knee, ankle -> the thigh-shank angle
ASSOC_MAXPX = 80.0
os.makedirs(DST, exist_ok=True)

COCO2VIC = {5: "LEFT_SHO", 6: "RIGHT_SHO", 7: "LEFT_ELBOW", 8: "RIGHT_ELBOW",
            9: "LEFT_WRIST", 10: "RIGHT_WRIST", 11: "LEFT_HIP", 12: "RIGHT_HIP",
            13: "LEFT_KNEE", 14: "RIGHT_KNEE", 15: "LEFT_ANKLE", 16: "RIGHT_ANKLE"}
JN = {11: "L-hip", 12: "R-hip", 13: "L-knee", 14: "R-knee", 15: "L-ankle", 16: "R-ankle"}

L = []


def out(s):
    print(s, flush=True)
    L.append(s)


def associate(kps, scs, gt_uv, valid):
    if len(kps) == 0 or valid.sum() < 4:
        return None
    best, bestd = None, 1e18
    for kp, sc in zip(kps, scs):
        d = np.median(np.linalg.norm(kp[valid] - gt_uv[valid], axis=1))
        if d < bestd:
            bestd, best = d, np.concatenate([kp, sc[:, None]], 1)
    return best if bestd <= ASSOC_MAXPX else None


CAMS = {}


def cams_for(pid):
    if pid not in CAMS:
        CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]


def detect_contiguous(body, pid, trial):
    outp = f"{DST}/{pid}_{os.path.basename(trial)}.pkl"
    if os.path.exists(outp):
        return outp
    c3dp = f"{trial}/markers.c3d"
    if not os.path.exists(c3dp):
        return None
    try:
        d = ezc3d.c3d(c3dp)
    except Exception:
        return None
    lab = d["parameters"]["POINT"]["LABELS"]["value"]
    if not all(v in lab for v in COCO2VIC.values()):
        return None
    VP = np.transpose(d["data"]["points"][:3], (2, 1, 0))
    vidx = {c: lab.index(v) for c, v in COCO2VIC.items()}
    cams = cams_for(pid)
    vids = sorted(glob.glob(f"{trial}/*.mp4"))[:len(cams)]
    if not vids:
        return None
    caps = [cv2.VideoCapture(v) for v in vids]
    F = min(int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT)), VP.shape[0])
    ok_frames = [fi for fi in range(F) if all(np.any(VP[fi][vidx[c]]) for c in COCO2VIC)]
    if len(ok_frames) < 50:
        for c in caps:
            c.release()
        return None
    # the longest contiguous run, centred, capped at NFRAMES
    runs, cur = [], [ok_frames[0]]
    for a, b in zip(ok_frames[:-1], ok_frames[1:]):
        if b == a + 1:
            cur.append(b)
        else:
            runs.append(cur); cur = [b]
    runs.append(cur)
    run = max(runs, key=len)
    if len(run) > NFRAMES:
        s0 = (len(run) - NFRAMES) // 2
        run = run[s0:s0 + NFRAMES]
    sel = set(run)
    frames, fi = [], -1
    while fi < run[-1]:
        grabbed = [c.grab() for c in caps]
        fi += 1
        if not all(grabbed):
            break
        if fi not in sel:
            continue
        gtw = {c: VP[fi][vidx[c]] for c in COCO2VIC}
        det = []
        for i, cap in enumerate(caps):
            okr, fr = cap.retrieve()
            if not okr:
                det.append(None); continue
            gt_uv = np.zeros((17, 2)); valid = np.zeros(17, bool)
            for c in COCO2VIC:
                try:
                    gt_uv[c] = cams[i].project(gtw[c]); valid[c] = True
                except Exception:
                    pass
            kp, sc = body(fr)
            det.append(associate(np.asarray(kp), np.asarray(sc), gt_uv, valid))
        frames.append({"fi": fi, "gt": {c: gtw[c].copy() for c in gtw}, "det": det})
    for c in caps:
        c.release()
    pickle.dump({"pid": pid, "trial": os.path.basename(trial), "frames": frames},
                open(outp, "wb"))
    return outp


def undistort(det, cams):
    for i, dd in enumerate(det):
        if dd is None:
            continue
        uv = dd[:, :2]
        ok = np.isfinite(uv[:, 0]) & np.isfinite(uv[:, 1])
        if not ok.any():
            continue
        pts = uv[ok].astype(np.float64).reshape(-1, 1, 2)
        dist = np.asarray(cams[i].dist, float).reshape(1, -1)
        uv[ok] = cv2.undistortPoints(pts, cams[i].K, dist, P=cams[i].K).reshape(-1, 2)


def share(err_by_pid_joint):
    rows = {}
    for j in sorted(JN):
        bias, resid, sh = [], [], []
        for (p, jj), arr in err_by_pid_joint.items():
            if jj != j or len(arr) < 20:
                continue
            e = np.asarray(arr, float)
            m = e.mean(axis=0)
            mse = (e ** 2).sum(axis=1).mean()
            bias.append(float(np.linalg.norm(m)))
            resid.append(float(np.sqrt(((e - m) ** 2).sum(axis=1).mean())))
            sh.append(100 * float((m @ m) / mse) if mse > 0 else np.nan)
        if bias:
            rows[j] = (np.mean(bias), np.mean(resid), np.nanmean(sh), len(bias))
    return rows


def _objd(cam, X, uv):
    """Object-space residual: the perpendicular distance from X to the camera ray through uv."""
    dv = cam.ray_dir(uv)
    w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)


def _reject(cs, uvs, w):
    """Adaptive object-space rejection, the deployable rule of Section 2.2: drop the worst camera
    while it exceeds median + 3 MAD, never going below MIN_CAM."""
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([_objd(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e)
        mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K_MAD * mad:
            break
        idx.pop(worst)
    return idx


def _angle(h, k, an):
    """Three-point included angle at the knee, in degrees. The same definition as the manuscript."""
    u, v = h - k, an - k
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if nu < 1e-9 or nv < 1e-9:
        return np.nan
    return float(np.degrees(np.arccos(np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0))))


def main():
    body = Body(mode="balanced", backend="onnxruntime", device=DEVICE)   # same two-stage default as biocv_detect.py
    paths = []
    for pid in PIDS:
        # "*WALK*" also matches the pipeline output directory {pid}_ML_WALK_01, which holds no
        # markers.c3d and sorts first. Every other script here excludes it; this one did not, so
        # it silently spent one slot per participant on a directory that can never yield a window.
        trials = [t for t in sorted(glob.glob(f"D:/BioCV/{pid}/*WALK*"))
                  if "ML" not in os.path.basename(t)]
        for t in trials[:MAXTR]:
            if os.path.isdir(t):
                r = detect_contiguous(body, pid, t)
                if r:
                    paths.append(r)
    if not paths:
        out("No contiguous windows detected. Nothing to compare.")
        io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
        return

    b, a = butter(ORDER, FC / (FS / 2.0), btype="low")
    raw, filt, ANG = {}, {}, {}
    for f in paths:
        D = pickle.load(open(f, "rb"))
        pid = D["pid"]
        cams = cams_for(pid)
        series = {}
        apos, agt = {"none": {}, "objd": {}}, {}
        for fr in D["frames"]:
            undistort(fr["det"], cams)
            for j in JN:
                if j not in fr["gt"] or not np.any(fr["gt"][j]):
                    continue
                vi = [i for i, dd in enumerate(fr["det"])
                      if dd is not None and np.isfinite(dd[j, 0]) and dd[j, 2] > 0]
                if len(vi) < MIN_CAM:
                    continue
                uvs = np.array([fr["det"][i][j, :2] for i in vi])
                w = np.array([fr["det"][i][j, 2] for i in vi])
                X = R.triangulate_wdlt([cams[i] for i in vi], uvs, w)
                series.setdefault(j, []).append((fr["fi"], X, fr["gt"][j].copy()))
                # the same frame under the deployable rejection rule, for the angle half
                keep = _reject([cams[i] for i in vi], uvs, w)
                Xr = R.triangulate_wdlt([cams[vi[i]] for i in keep], uvs[keep], w[keep])
                apos["none"].setdefault(j, {})[fr["fi"]] = X
                apos["objd"].setdefault(j, {})[fr["fi"]] = Xr
                agt.setdefault(j, {})[fr["fi"]] = fr["gt"][j].copy()
        for j, seq in series.items():
            seq.sort(key=lambda r: r[0])
            if len(seq) < 4 * ORDER + 1:
                continue
            Xs = np.array([x for _, x, _ in seq])
            Gs = np.array([g for _, _, g in seq])
            raw.setdefault((pid, j), []).extend(list(Xs - Gs))
            Xf = filtfilt(b, a, Xs, axis=0)
            filt.setdefault((pid, j), []).extend(list(Xf - Gs))

        # --- the angle half -------------------------------------------------------------
        # Filtering is applied to the JOINT POSITIONS and the angle formed afterwards, which
        # is what a deployed pipeline does; filtering the angle series instead would smooth a
        # quantity the reference never filtered.
        for sd, (jh, jk, ja) in SIDES.items():
            fis = sorted(set(agt.get(jh, {})) & set(agt.get(jk, {})) & set(agt.get(ja, {}))
                         & set(apos["objd"].get(jh, {})) & set(apos["objd"].get(jk, {}))
                         & set(apos["objd"].get(ja, {})))
            if len(fis) < 4 * ORDER + 1:
                continue
            gtA = np.array([_angle(agt[jh][i], agt[jk][i], agt[ja][i]) for i in fis])
            for arm in ("none", "objd"):
                P = {j: np.array([apos[arm][j][i] for i in fis]) for j in (jh, jk, ja)}
                rawA = np.array([_angle(P[jh][t], P[jk][t], P[ja][t]) for t in range(len(fis))])
                Pf = {j: filtfilt(b, a, P[j], axis=0) for j in (jh, jk, ja)}
                filA = np.array([_angle(Pf[jh][t], Pf[jk][t], Pf[ja][t]) for t in range(len(fis))])
                ok = np.isfinite(rawA) & np.isfinite(filA) & np.isfinite(gtA)
                if ok.sum() < 10:
                    continue
                ANG.setdefault((pid, arm, "raw"), []).extend(np.abs(rawA[ok] - gtA[ok]))
                ANG.setdefault((pid, arm, "filt"), []).extend(np.abs(filA[ok] - gtA[ok]))

    ru, rf = share(raw), share(filt)
    out("DOES FILTERING MOVE THE OFFSET SHARE?")
    out("")
    out(f"{len(paths)} trials from {len(PIDS)} participant(s), contiguous windows of up to "
        f"{NFRAMES} frames.")
    out(f"Markerless trajectories filtered with the reference's own filter: Butterworth, order "
        f"{ORDER}, {FC:.0f} Hz, zero-phase.")
    out("")
    out(f"{'joint':>9}{'bias raw':>10}{'bias filt':>11}{'rand raw':>10}{'rand filt':>11}"
        f"{'share raw':>11}{'share filt':>12}{'shift':>8}")
    shifts = []
    for j in sorted(JN):
        if j not in ru or j not in rf:
            continue
        out(f"{JN[j]:>9}{ru[j][0]:>10.1f}{rf[j][0]:>11.1f}{ru[j][1]:>10.1f}{rf[j][1]:>11.1f}"
            f"{ru[j][2]:>10.1f}%{rf[j][2]:>11.1f}%{rf[j][2]-ru[j][2]:>+8.2f}")
        if "ankle" not in JN[j]:
            shifts.append(rf[j][2] - ru[j][2])
    out("")
    if shifts:
        m = float(np.mean(shifts))
        out("=== VERDICTS, against the rule fixed in this file's header ===")
        out(f"(1) DIRECTION: filtering moves the hip/knee share by {m:+.1f} points  ->  "
            + ("the manuscript's stated direction is CONFIRMED and may be quoted as measured"
               if m > 0 else
               "the manuscript's stated direction is WRONG and the Limitations must be reversed"))
        out(f"(2) SIZE: {abs(m):.1f} points  ->  "
            + ("under one point; the sampling choice did not matter and the caveat can be retired"
               if abs(m) < 1 else
               "under 5 points; the manuscript's numbers stand as they are"
               if abs(m) < 5 else
               "5 points or more; this must be carried into Section 3.1 and the abstract"))
        out("(3) SCOPE: a subset, so this settles the direction and bounds the size on these")
        out("    participants. It does not replace the headline figure.")

    # === (5) THE ANGLE HALF =============================================================
    pids = sorted({k[0] for k in ANG})
    rows_a = []
    for pid in pids:
        g = {}
        for sc in ("raw", "filt"):
            n0, o0 = ANG.get((pid, "none", sc)), ANG.get((pid, "objd", sc))
            if not n0 or not o0:
                break
            g[sc] = (float(np.mean(n0)), float(np.mean(o0)))
        if len(g) == 2:
            rows_a.append((pid, g["raw"][0], g["raw"][1], g["filt"][0], g["filt"][1]))
    out("")
    out("DOES THE REJECTION COST TO THE ANGLE SURVIVE FILTERING?")
    out("")
    out("Thigh-shank angle, mean absolute error in degrees against the filtered reference.")
    out("COST = rejection minus no rejection; positive means rejection is worse, which is the")
    out("direction the manuscript reports. Filtering is applied to the joint POSITIONS and the")
    out("angle formed afterwards.")
    out("")
    out(f"{'pid':>6}{'none raw':>10}{'objd raw':>10}{'cost raw':>10}"
        f"{'none filt':>11}{'objd filt':>11}{'cost filt':>11}")
    for pid, nr, orr, nf, of in rows_a:
        out(f"{pid:>6}{nr:>10.3f}{orr:>10.3f}{orr - nr:>+10.3f}{nf:>11.3f}{of:>11.3f}{of - nf:>+11.3f}")
    if rows_a:
        cr = float(np.mean([r[2] - r[1] for r in rows_a]))
        cf = float(np.mean([r[4] - r[3] for r in rows_a]))
        out("")
        out(f"Mean cost raw {cr:+.3f} deg, filtered {cf:+.3f} deg "
            f"({len(rows_a)} participant(s)).")
        out("")
        out("=== VERDICT (5), against the rule fixed in this file's header ===")
        if cr <= 0:
            out("The raw cost is not positive in this subset, so the pre-registered comparison has")
            out("no cost to test. Report that and nothing more: it does not confirm or refute the")
            out("manuscript's figure, which is computed on the full sampled dataset.")
        elif cf < 0:
            out("REVERSES: filtering turns the rejection cost into a gain. The manuscript's angle")
            out("conclusion is an artefact of unfiltered estimates and must be WITHDRAWN.")
        elif cf < 0.5 * cr:
            out(f"FALLS BELOW HALF ({cf:.3f} against {cr:.3f}). Section 3.2 and the Conclusion must")
            out("say the rejection cost to the angle is substantially an artefact of unfiltered")
            out("estimates, and the quoted magnitude must not be presented as filter-robust.")
        else:
            out(f"HOLDS ({cf:.3f} against {cr:.3f}, at least half). The angle conclusion stands and")
            out("may be quoted as robust to the absence of temporal filtering, on this subset.")
        out("")
        out("SCOPE: a subset of participants and trials. It settles the DIRECTION and bounds")
        out("the size of the filtering bias on the angle; it does not replace the headline")
        out("figure.")
        # --- POST HOC -----------------------------------------------------------------
        # Added AFTER the eleven-participant numbers existed, and labelled as such. The
        # pre-registered rule compares two means and says nothing about dispersion; with
        # eleven participants the per-participant costs can be tested directly, and three
        # of them reverse under filtering. Reporting only the mean would hide that.
        out("")
        out("=== POST HOC: is the filtered cost distinguishable from zero? ===")
        out("Declared post hoc. This test was added after the per-participant numbers were")
        out("seen; it is not part of the rule fixed in this file's header, and it is not")
        out("carried into any declared family.")
        _cf = np.array([r[4] - r[3] for r in rows_a], float)
        _cr = np.array([r[2] - r[1] for r in rows_a], float)
        for _lab, _v in (("raw", _cr), ("filtered", _cf)):
            _n = len(_v)
            if _n > 20:
                out(f"  {_lab}: n = {_n}, too many for exact enumeration here")
                continue
            _obs = abs(float(np.mean(_v)))
            _hit = 0
            for _m in range(1 << _n):
                _sg = np.array([1.0 if (_m >> _b) & 1 else -1.0 for _b in range(_n)])
                if abs(float(np.mean(_sg * _v))) >= _obs - 1e-12:
                    _hit += 1
            _p = _hit / float(1 << _n)
            _neg = int((_v < 0).sum())
            out(f"  {_lab}: mean {float(np.mean(_v)):+.3f} deg, {_neg} of {_n} participants "
                f"negative, exact sign-flip p = {_p:.4f}")
    # A timestamp cannot tell "written by the current code" from "written by older code that
    # happened to finish later". A long run launched before an edit overwrote this artefact once,
    # and check_stale.py passed it because the file was newer than the script; only check_drift.py
    # caught it, downstream, after the numbers had reached the manuscript. Stamping the source
    # hash of this file moves that check upstream.
    import hashlib
    L.append("")
    L.append("source-sha256: " + hashlib.sha256(io.open(__file__, "rb").read()).hexdigest())
    io.open(OUTF, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nWROTE", OUTF)


if __name__ == "__main__":
    main()
