"""
ROWV: Robust Outlier removal by Weighted Voting for multi-view triangulation.

Core method (matches the paper's formulation):
  Given N camera observations of a 3D keypoint, enumerate all camera subsets
  of size N and N-1 (exhaustive leave-one-out). Triangulate each subset,
  find the observation with the MAXIMUM error within that subset (the subset's
  outlier candidate), then aggregate a SIZE-WEIGHTED vote across all subsets and
  take the mode (argmax weighted count) as the elected outlier, which is removed
  before a final refit.

Also implements:
  - weighted DLT (wDLT) triangulation using 2D-detector confidence.
  - distance error (metric, in mm) vs reprojection error (pixels) for quality.
  - baselines: naive DLT, wDLT (no removal), Pose2Sim-style greedy exclusion,
    RANSAC triangulation.

Pure numpy. No dataset needed; see rowv_sim.py for the controlled experiments.
"""
from __future__ import annotations
import itertools
import numpy as np


# --------------------------------------------------------------------------
# Camera model
# --------------------------------------------------------------------------
class Camera:
    """Pinhole camera. World point X (3,) -> pixel (2,)."""

    def __init__(self, K: np.ndarray, R: np.ndarray, C: np.ndarray):
        self.K = np.asarray(K, float)          # 3x3 intrinsics
        self.R = np.asarray(R, float)          # 3x3 world->cam rotation
        self.C = np.asarray(C, float).reshape(3)  # camera centre in world
        t = -self.R @ self.C
        self.P = self.K @ np.hstack([self.R, t.reshape(3, 1)])  # 3x4

    def project(self, X: np.ndarray) -> np.ndarray:
        Xh = np.append(np.asarray(X, float).reshape(3), 1.0)
        x = self.P @ Xh
        return x[:2] / x[2]

    def ray_dir(self, uv: np.ndarray) -> np.ndarray:
        """Unit ray direction in WORLD frame through pixel uv."""
        uvh = np.array([uv[0], uv[1], 1.0])
        d_cam = np.linalg.inv(self.K) @ uvh
        d_world = self.R.T @ d_cam
        return d_world / np.linalg.norm(d_world)


# --------------------------------------------------------------------------
# Triangulation
# --------------------------------------------------------------------------
def triangulate_wdlt(cams, uvs, weights=None):
    """Weighted linear DLT triangulation.

    cams: list of Camera; uvs: (M,2) observations; weights: (M,) or None.
    Returns X (3,).
    """
    M = len(cams)
    if weights is None:
        weights = np.ones(M)
    rows = []
    for cam, uv, w in zip(cams, uvs, weights):
        P = cam.P
        rows.append(w * (uv[0] * P[2] - P[0]))
        rows.append(w * (uv[1] * P[2] - P[1]))
    A = np.vstack(rows)
    _, _, Vt = np.linalg.svd(A)
    Xh = Vt[-1]
    return Xh[:3] / Xh[3]


def reproj_errors(cams, uvs, X):
    """Per-camera reprojection error in pixels."""
    return np.array([np.linalg.norm(cam.project(X) - uv) for cam, uv in zip(cams, uvs)])


def distance_errors(cams, uvs, X):
    """Per-camera metric error: perpendicular distance (mm) from X to the
    back-projected observation ray. Scale-consistent regardless of camera
    distance, unlike reprojection error."""
    errs = []
    for cam, uv in zip(cams, uvs):
        d = cam.ray_dir(uv)
        v = X - cam.C
        perp = v - np.dot(v, d) * d
        errs.append(np.linalg.norm(perp))
    return np.array(errs)


# --------------------------------------------------------------------------
# Methods under comparison
# --------------------------------------------------------------------------
def m_naive_dlt(cams, uvs, conf):
    return triangulate_wdlt(cams, uvs)


def m_wdlt(cams, uvs, conf):
    return triangulate_wdlt(cams, uvs, conf)


def m_greedy(cams, uvs, conf, thresh_px=8.0, min_cams=2):
    """Pose2Sim-style: iteratively drop the camera with the worst reprojection
    error until under threshold or min_cams reached."""
    idx = list(range(len(cams)))
    while True:
        cs = [cams[i] for i in idx]
        us = uvs[idx]
        ws = conf[idx]
        X = triangulate_wdlt(cs, us, ws)
        err = reproj_errors(cs, us, X)
        if err.max() <= thresh_px or len(idx) <= min_cams:
            return X
        drop = int(np.argmax(err))
        idx.pop(drop)


def m_ransac(cams, uvs, conf, thresh_px=8.0, iters=None, rng=None):
    """Classic RANSAC triangulation over minimal 2-camera samples."""
    rng = rng or np.random.default_rng(0)
    N = len(cams)
    pairs = list(itertools.combinations(range(N), 2))
    if iters is None or iters >= len(pairs):
        sample_pairs = pairs            # small N: enumerate all pairs
    else:
        sample_pairs = [pairs[i] for i in rng.choice(len(pairs), iters, replace=False)]
    best_inliers, best_X = None, None
    for (a, b) in sample_pairs:
        X = triangulate_wdlt([cams[a], cams[b]], uvs[[a, b]])
        err = reproj_errors(cams, uvs, X)
        inl = np.where(err <= thresh_px)[0]
        if best_inliers is None or len(inl) > len(best_inliers):
            best_inliers, best_X = inl, X
    if best_inliers is not None and len(best_inliers) >= 2:
        return triangulate_wdlt([cams[i] for i in best_inliers],
                                uvs[best_inliers], conf[best_inliers])
    return best_X


def rowv_vote(cams, uvs, conf, use_distance=True, return_elected=False):
    """ROWV: leave-one-out subset enumeration + size-weighted voting.

    Enumerate subsets of size N and N-1. For each subset triangulate (wDLT),
    find the max-error member (candidate outlier), and add a vote of weight
    |subset| to that ORIGINAL index. Elected outlier = argmax weighted votes.
    """
    N = len(cams)
    err_fn = distance_errors if use_distance else reproj_errors
    votes = np.zeros(N)
    for size in (N, N - 1):
        for subset in itertools.combinations(range(N), size):
            cs = [cams[i] for i in subset]
            us = uvs[list(subset)]
            ws = conf[list(subset)]
            X = triangulate_wdlt(cs, us, ws)
            err = err_fn(cs, us, X)
            worst_local = int(np.argmax(err))
            worst_global = subset[worst_local]
            votes[worst_global] += size          # size-weighted vote
    elected = int(np.argmax(votes))
    keep = [i for i in range(N) if i != elected]
    X = triangulate_wdlt([cams[i] for i in keep], uvs[keep], conf[keep])
    if return_elected:
        return X, elected, votes
    return X


def m_rowv(cams, uvs, conf):
    return rowv_vote(cams, uvs, conf, use_distance=True)


def rowv_iter(cams, uvs, conf, min_cams=2, k=3.0):
    """Iterative ROWV: repeatedly elect the worst camera by size-weighted voting
    and remove it *while* it is a statistical outlier (distance error above
    median + k*MAD of the current set). Threshold-free in scale (MAD adapts);
    removes MULTIPLE outliers, unlike single-shot ROWV."""
    idx = list(range(len(cams)))
    while len(idx) > min_cams:
        cs = [cams[i] for i in idx]
        us = uvs[idx]; cf = conf[idx]
        _, elected_local, _ = rowv_vote(cs, us, cf, use_distance=True, return_elected=True)
        X = triangulate_wdlt(cs, us, cf)
        d = distance_errors(cs, us, X)
        med = np.median(d)
        mad = np.median(np.abs(d - med)) * 1.4826
        if mad < 1e-6 or d[elected_local] <= med + k * mad:
            break                                     # remaining set is consistent
        idx.pop(elected_local)
    cs = [cams[i] for i in idx]
    return triangulate_wdlt(cs, uvs[idx], conf[idx])


def m_rowv_iter(cams, uvs, conf):
    return rowv_iter(cams, uvs, conf)


def m_rowv_reproj(cams, uvs, conf):
    """Ablation: ROWV voting but using reprojection error (no distance fix)."""
    return rowv_vote(cams, uvs, conf, use_distance=False)


METHODS = {
    "naive_DLT": m_naive_dlt,
    "wDLT": m_wdlt,
    "greedy_reproj": m_greedy,
    "RANSAC": m_ransac,
    "ROWV_reproj": m_rowv_reproj,
    "ROWV": m_rowv,
}
