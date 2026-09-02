"""Build distortion-CORRECTED detection caches once, vectorized, so every downstream
analysis can be re-run on undistorted detections cheaply.

Reads  D:/BioCV/_cache_balanced/*.pkl   (detections in DISTORTED pixel coords)
Writes D:/BioCV/_cache_undist/*.pkl     (same structure, detections mapped to the
                                         ideal pinhole frame via cv2.undistortPoints)

BIOCV_UNDIST_SRC and BIOCV_UNDIST_DST override the two paths. Every alternative-detector cache
must be passed through this before it is compared with _cache_undist: the published results use
corrected detections, and comparing a corrected cache with a raw one puts the distortion
difference into the detector contrast, at exactly the near-camera residuals distortion moves
most.
Only the (u,v) of each keypoint is changed; confidence and GT are untouched.
"""
import glob, os, pickle, numpy as np, sys, cv2
sys.path.insert(0, "D:/ROWV_paper")
from biocv_calib import load_biocv_cameras

SRC = os.environ.get("BIOCV_UNDIST_SRC", "D:/BioCV/_cache_balanced")
DST = os.environ.get("BIOCV_UNDIST_DST", "D:/BioCV/_cache_undist")
os.makedirs(DST, exist_ok=True)

CAMS = {}
def cams_for(pid):
    if pid not in CAMS: CAMS[pid], _ = load_biocv_cameras(f"D:/BioCV/_calib/{pid}")
    return CAMS[pid]

n_files = 0; n_pts = 0
for f in sorted(glob.glob(f"{SRC}/*.pkl")):
    D = pickle.load(open(f, "rb")); cams = cams_for(D["pid"])
    for fr in D["frames"]:
        det = fr["det"]
        for i, dd in enumerate(det):
            if dd is None: continue
            uv = dd[:, :2]
            ok = np.isfinite(uv[:, 0]) & np.isfinite(uv[:, 1])
            if not ok.any(): continue
            cam = cams[i]
            pts = uv[ok].astype(np.float64).reshape(-1, 1, 2)
            dist = np.asarray(cam.dist, float).reshape(1, -1)
            und = cv2.undistortPoints(pts, cam.K, dist, P=cam.K).reshape(-1, 2)
            uv[ok] = und                      # in-place on the array inside dd
            n_pts += ok.sum()
    out = os.path.join(DST, os.path.basename(f))
    pickle.dump(D, open(out, "wb"))
    n_files += 1
print(f"wrote {n_files} undistorted caches to {DST}; {n_pts} keypoints corrected")
