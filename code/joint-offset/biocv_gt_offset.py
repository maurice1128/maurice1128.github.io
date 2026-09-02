"""B14 — HOW MUCH OF THE ERROR IS A FIXED JOINT-CENTRE DEFINITION OFFSET?

Motivation: B7 measured detector pixel error scaling as d^(-1.04). A FIXED 3D offset
between the Vicon marker-derived joint centre and the detector's notion of that joint
projects to f*delta/Z pixels, i.e. exactly d^(-1). So the measured scaling law is what
a pure definitional offset alone would produce. If such an offset dominates the error
budget, NO triangulation change can remove it, which bounds the value of this entire
line of work.

Method: bias-variance decomposition of the 3D error vector e = X_est - X_gt, per
(subject, joint):
      MSE = ||mean(e)||^2  +  mean(||e - mean(e)||^2)
          =    bias^2      +        variance
A large bias fraction means the error is a systematic offset, not triangulation noise.

Computed in TWO frames, because a definitional offset is fixed in the BODY frame while
a calibration/registration error is fixed in the WORLD frame:
  - world frame (as-is)
  - body frame: x = right (hip-to-hip), z = up (world vertical), y = anterior (z cross x)
Bias that is large in the body frame but small in the world frame is anatomical
(definitional); the reverse indicates registration error.

Also reports the "ceiling": RMSE after removing the per-subject-per-joint bias — the
best any triangulation improvement could achieve on this data.
-> D:/BioCV/BIOCV_GT_OFFSET.txt
"""
import glob, os, pickle, numpy as np, sys
sys.path.insert(0, "D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras

MIN_CAM = 4; K_MAD = 3.0
CACHE = os.environ.get("BIOCV_CACHE", "D:/BioCV/_cache_undist")
OUTF = os.environ.get("BIOCV_OUT", "D:/BioCV/BIOCV_GT_OFFSET.txt")
JOINTS = {"L-shoulder":5,"R-shoulder":6,"L-elbow":7,"R-elbow":8,"L-wrist":9,"R-wrist":10,
          "L-hip":11,"R-hip":12,"L-knee":13,"R-knee":14,"L-ankle":15,"R-ankle":16}

def objd(cam, X, uv):
    dv = cam.ray_dir(uv); w = X - cam.C
    return np.linalg.norm(w - np.dot(w, dv) * dv)

def solve(cs, uvs, w):
    """Best arm from earlier work: object-space rejection + confidence weights."""
    idx = list(range(len(cs)))
    while len(idx) > MIN_CAM:
        CS = [cs[i] for i in idx]
        X = R.triangulate_wdlt(CS, uvs[idx], w[idx])
        e = np.array([objd(CS[k], X, uvs[idx][k]) for k in range(len(idx))])
        med = np.median(e); mad = np.median(np.abs(e - med)) * 1.4826
        worst = int(np.argmax(e))
        if mad < 1e-9 or e[worst] <= med + K_MAD * mad: break
        idx.pop(worst)
    return R.triangulate_wdlt([cs[i] for i in idx], uvs[idx], w[idx])

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

# err_world[(pid, joint)] -> list of 3-vectors ; err_body likewise
EW = {}; EB = {}
for f in sorted(glob.glob(f"{CACHE}/*.pkl")):
    D = pickle.load(open(f, "rb")); pid = D["pid"]; cams = cams_for(pid)
    for fr in D["frames"]:
        det = fr["det"]; gt = fr["gt"]
        # body frame from the GT hips (needs both hips present)
        if not (11 in gt and 12 in gt and np.any(gt[11]) and np.any(gt[12])): continue
        xr = gt[12] - gt[11]; xr = xr / (np.linalg.norm(xr) + 1e-9)   # left->right
        up = np.array([0.0, 0.0, 1.0])
        up = up - np.dot(up, xr) * xr; up /= (np.linalg.norm(up) + 1e-9)
        ant = np.cross(up, xr)
        Rb = np.vstack([xr, ant, up])                                 # world -> body
        for jn, cj in JOINTS.items():
            if cj not in gt or not np.any(gt[cj]): continue
            Xg = gt[cj]
            vi = [i for i, dd in enumerate(det)
                  if dd is not None and np.isfinite(dd[cj, 0]) and dd[cj, 2] > 0]
            if len(vi) < MIN_CAM: continue
            cs = [cams[i] for i in vi]
            uvs = np.array([det[i][cj, :2] for i in vi])
            w = np.array([det[i][cj, 2] for i in vi])
            e = solve(cs, uvs, w) - Xg
            EW.setdefault((pid, jn), []).append(e)
            EB.setdefault((pid, jn), []).append(Rb @ e)

lines = []
def out(s): print(s); lines.append(s)
out("B14 -- BIAS/VARIANCE DECOMPOSITION OF 3D JOINT ERROR")
out(f"Cache={CACHE}. Arm = object-space rejection + confidence weights.")
out("MSE = ||mean(e)||^2 (systematic offset) + mean(||e-mean(e)||^2) (random).")
out("")

def summarise(store, tag):
    out(f"=== {tag} FRAME ===")
    out(f"{'joint':>12}{'n':>8}{'RMSE':>9}{'bias':>9}{'resid':>9}{'bias%MSE':>10}")
    per_joint = {}
    tot_mse = tot_bias2 = 0.0; tot_n = 0
    for jn in JOINTS:
        vecs = []; biases = []
        for (pid, j), arr in store.items():
            if j != jn: continue
            A = np.array(arr)
            b = A.mean(0)
            biases.append(b)
            vecs.append(A)
        if not vecs: continue
        A = np.vstack(vecs)
        # per-subject bias removed (bias estimated within subject)
        mse = np.mean(np.sum(A**2, 1))
        b2 = np.mean([np.sum(b**2) for b in biases])
        resid = np.sqrt(max(mse - b2, 0))
        out(f"{jn:>12}{len(A):>8}{np.sqrt(mse):>9.1f}{np.sqrt(b2):>9.1f}{resid:>9.1f}"
            f"{100*b2/mse:>9.0f}%")
        per_joint[jn] = (np.sqrt(mse), np.sqrt(b2), resid, 100*b2/mse)
        tot_mse += mse * len(A); tot_bias2 += b2 * len(A); tot_n += len(A)
    # TWO SHARES, NOT ONE. The column above estimates the offset WITHIN each participant, so
    # between-participant scatter in the offset sits in the bias term. That is the right quantity
    # for this paper's contrasts, which are within-participant by construction. It is NOT the
    # quantity a validation study reports: pooling a cohort puts that scatter in the RANDOM term
    # and gives a materially smaller share. Reporting only the first reads as a claim about the
    # second, so both are printed.
    out("")
    out("THE SAME DECOMPOSITION WITH PARTICIPANTS POOLED, which is what a cohort-level validation")
    out("study measures. The common offset is the mean over participants of their mean error")
    out("vector; the between-participant scatter moves from the bias term into the random term.")
    out("")
    out(f"{'joint':>12}{'common':>9}{'scatter':>9}{'random':>9}"
        f"{'within-ppt share':>18}{'pooled share':>14}")
    for jn in JOINTS:
        bs = [np.array(arr).mean(0) for (pid, j), arr in store.items() if j == jn]
        if len(bs) < 2 or jn not in per_joint:
            continue
        B = np.vstack(bs)
        common2 = float(np.sum(B.mean(0) ** 2))
        scatter2 = float(np.sum(B.var(0, ddof=1)))
        rmse, bias, resid, share = per_joint[jn]
        resid2 = float(resid) ** 2
        pooled = 100 * common2 / (common2 + scatter2 + resid2)
        out(f"{jn:>12}{common2**0.5:>9.1f}{scatter2**0.5:>9.1f}{resid:>9.1f}"
            f"{share:>17.0f}%{pooled:>13.0f}%")
    out("")
    out("READ: the two columns answer different questions. The within-participant share is the one")
    out("this paper's contrasts live on, because every contrast is a difference within a participant")
    out("and that participant's own offset is common to both arms. The pooled share is the one a")
    out("cohort-level validation study would report. Any sentence about what 'the position metric'")
    out("measures for such a study must quote the pooled column.")
    out("")
    if tot_n:
        M = tot_mse / tot_n; Bq = tot_bias2 / tot_n
        out(f"{'ALL':>12}{tot_n:>8}{np.sqrt(M):>9.1f}{np.sqrt(Bq):>9.1f}"
            f"{np.sqrt(max(M-Bq,0)):>9.1f}{100*Bq/M:>9.0f}%")
    out("")
    return per_joint

pw = summarise(EW, "WORLD")
pb = summarise(EB, "BODY")

out("=== IS THE OFFSET CONSISTENT ACROSS SUBJECTS? (body frame) ===")
out("A definitional joint-centre offset should point the same way for every subject;")
out("a per-subject calibration error should not.")
out(f"{'joint':>12}{'mean offset (x=right,y=ant,z=up) mm':>40}{'across-subj SD':>16}")
for jn in JOINTS:
    bs = [np.array(a).mean(0) for (p, j), a in EB.items() if j == jn]
    if len(bs) < 3: continue
    bs = np.array(bs)
    m = bs.mean(0); sd = bs.std(0)
    out(f"{jn:>12}   [{m[0]:+7.1f},{m[1]:+7.1f},{m[2]:+7.1f}]{'':>8}"
        f"[{sd[0]:5.1f},{sd[1]:5.1f},{sd[2]:5.1f}]")
out("")
# The manuscript quoted the mediolateral share of the squared hip offset by dividing the
# ACROSS-PARTICIPANT MEAN mediolateral component by the MEAN OF PER-PARTICIPANT NORMS. Those are
# different objects, and with an across-participant SD of about 8 mm on that component they are
# not interchangeable. The ratio is formed per participant here and then averaged, which is what
# the sentence meant.
out("=== THE MEDIOLATERAL SHARE OF THE SQUARED HIP OFFSET, FORMED PER PARTICIPANT ===")
out("")
out("share = (mediolateral component)^2 / |offset|^2, computed for each participant and then")
out("averaged. The ratio of the across-participant means is given beside it; the two differ")
out("because the mediolateral component varies across participants by about 8 mm.")
out("")
out(f"{'joint':>12}{'per-participant':>18}{'ratio of means':>17}{'n':>5}")
for jn in ("L-hip", "R-hip", "L-knee", "R-knee"):
    vs = [np.array(a).mean(0) for (p, j), a in EB.items() if j == jn]
    if len(vs) < 3:
        continue
    vs = np.array(vs)
    per = np.array([(v[0] ** 2) / float(v @ v) for v in vs if float(v @ v) > 1e-12])
    mm = vs.mean(0)
    rat = (mm[0] ** 2) / float(mm @ mm)
    out(f"{jn:>12}{100 * per.mean():>17.1f}%{100 * rat:>16.1f}%{len(per):>5}")
out("")
out("")
out("READ: 'bias%MSE' is the share of squared error that is a FIXED per-subject-per-joint")
out("offset. Triangulation improvements can only act on the remaining 'resid' component,")
out("so a high bias share is a hard ceiling on this entire line of work.")
open(OUTF, "w", encoding="utf-8").write("\n".join(lines) + "\n")
