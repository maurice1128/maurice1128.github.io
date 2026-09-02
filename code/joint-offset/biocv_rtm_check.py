"""Per-camera: RTMPose detected knee/hip/ankle 2D vs projected-Vicon truth 2D,
with confidence. Determines whether confidence-filtering cleans the bad cameras."""
import glob, numpy as np, ezc3d, cv2, sys
sys.path.insert(0,"D:/ROWV_paper"); import rowv as R
from biocv_calib import load_biocv_cameras
from rtmlib import Body
trial="D:/BioCV/P06/P06_WALK_01"
cams,_=load_biocv_cameras("D:/BioCV/_calib/P06")
tv=sorted(glob.glob(f"{trial}/*.mp4")); n=len(cams)
d=ezc3d.c3d(f"{trial}/markers.c3d"); lab=d["parameters"]["POINT"]["LABELS"]["value"]
VP=np.transpose(d["data"]["points"][:3],(2,1,0)); li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"]}
fi=None
for t in range(400,VP.shape[0]):
    if all(np.any(VP[t][li[k]]) for k in li): fi=t; break
print("frame",fi)
body=Body(mode="balanced",backend="onnxruntime",device="cpu")
COCO={'hip':11,'knee':13,'ank':15}
gtK=VP[fi][li['LEFT_KNEE']]
print(f"{'cam':>4}{'inframe':>8}{'proj_knee_uv':>18}{'rtm_knee_uv':>18}{'err_px':>9}{'conf':>7}")
good=0
for i,(cam,v) in enumerate(zip(cams,tv)):
    projK=cam.project(gtK); inf=(0<=projK[0]<cam.w and 0<=projK[1]<cam.h)
    cap=cv2.VideoCapture(v); cap.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,fr=cap.read(); cap.release()
    k,s=body(fr)
    if len(k):
        p=int(np.argmax(s.mean(1))); rk=k[p][COCO['knee']]; cf=s[p][COCO['knee']]
        err=np.linalg.norm(rk-projK) if inf else float('nan')
        if inf and err<40 and cf>0.5: good+=1
        print(f"{i:>4}{str(inf):>8}{str(np.round(projK,0)):>18}{str(np.round(rk,0)):>18}{err:>9.0f}{cf:>7.2f}")
    else:
        print(f"{i:>4}{str(inf):>8}{str(np.round(projK,0)):>18}{'NO DET':>18}")
print(f"\ncameras with good knee (in-frame, err<40px, conf>0.5): {good}/{n}")
print("=> if >=4 good, confidence+inframe filtering should fix triangulation")
