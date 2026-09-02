"""Parse BioCV .mp4-mocAligned2.calib files -> rowv.Camera, and read MarkerNames.
Calib format: width, height, 3x3 K, 4x4 [R|t] (world->cam), distortion (k1 k2 p1 p2 k3).
Coordinates in mm, same frame as the Vicon markers (mocAligned)."""
import glob, os, re
import numpy as np
import sys
sys.path.insert(0, "D:/ROWV_paper")
import rowv as R

def parse_calib(path):
    nums = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        nums.append([float(x) for x in line.split()])
    w, h = int(nums[0][0]), int(nums[1][0])
    K = np.array(nums[2:5], float)                       # 3x3
    ext = np.array(nums[5:9], float)                     # 4x4 world->cam
    Rmat = ext[:3, :3]; t = ext[:3, 3]                   # x_cam = R x_world + t
    dist = np.array(nums[9], float) if len(nums) > 9 else np.zeros(5)
    C = -Rmat.T @ t                                      # camera centre (mm)
    cam = R.Camera(K, Rmat, C)
    cam.dist = dist; cam.w = w; cam.h = h
    return cam

def load_biocv_cameras(calib_dir):
    """calib_dir e.g. D:/BioCV/_calib/P06 -> list of 9 cameras by node 00..08."""
    files = sorted(glob.glob(os.path.join(calib_dir, "*.calib")))
    return [parse_calib(f) for f in files], files

if __name__ == "__main__":
    cams, files = load_biocv_cameras("D:/BioCV/_calib/P06")
    print(f"Parsed {len(cams)} cameras for P06")
    C = np.array([c.C for c in cams])
    ctr = C.mean(0)
    print(f"camera centres (mm), distance to centroid:")
    for i, c in enumerate(cams):
        d = np.linalg.norm(c.C - ctr)
        print(f"  cam{i:02d}: C={np.round(c.C,0)}  f={c.K[0,0]:.0f}  dist2ctr={d:.0f}")
    print(f"\ncentroid {np.round(ctr,0)} mm; camera ring radius ~{np.median(np.linalg.norm(C-ctr,axis=1)):.0f} mm")
    # sanity: reproject the centroid into each camera, check it lands in-image
    inview = 0
    for c in cams:
        uv = c.project(ctr)
        if 0 <= uv[0] < c.w and 0 <= uv[1] < c.h:
            inview += 1
    print(f"centroid projects in-frame for {inview}/{len(cams)} cameras (sanity)")
