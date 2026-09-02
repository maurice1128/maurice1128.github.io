"""Diagnose the video<->mocap alignment for one P06 walk trial (no RTMPose)."""
import glob, os, numpy as np, ezc3d, cv2
def ang(a,b,c):
    u=a-b; v=c-b; nu=np.linalg.norm(u); nv=np.linalg.norm(v)
    return np.nan if nu<1e-6 or nv<1e-6 else np.degrees(np.arccos(np.clip(u@v/(nu*nv),-1,1)))
root="D:/BioCV/P06"
trials=[t for t in sorted(glob.glob(f"{root}/*WALK*")) if 'ML' not in os.path.basename(t)
        and glob.glob(f"{t}/*marker*.c3d")]
print("valid WALK trials (own markers.c3d, non-ML):", [os.path.basename(t) for t in trials])
trial=trials[0]
print("trial:", os.path.basename(trial))
print("files:", sorted(os.listdir(trial)))
# video
v=sorted(glob.glob(f"{trial}/*.mp4"))[0]; cap=cv2.VideoCapture(v)
vfps=cap.get(cv2.CAP_PROP_FPS); vN=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.release()
print(f"video {os.path.basename(v)}: fps={vfps} frames={vN} dur={vN/vfps:.2f}s")
# mocap
mk=[c for c in glob.glob(f"{trial}/*.c3d") if 'marker' in os.path.basename(c).lower()]
d=ezc3d.c3d(mk[0]); lab=d["parameters"]["POINT"]["LABELS"]["value"]; rate=d["parameters"]["POINT"]["RATE"]["value"][0]
VP=np.transpose(d["data"]["points"][:3],(2,1,0))
print(f"markers.c3d rate={rate} frames={VP.shape[0]} dur={VP.shape[0]/rate:.2f}s")
li={k:lab.index(k) for k in ["LEFT_HIP","LEFT_KNEE","LEFT_ANKLE"] if k in lab}
print("has L hip/knee/ankle:", li)
kn=np.array([ang(VP[t][li['LEFT_HIP']],VP[t][li['LEFT_KNEE']],VP[t][li['LEFT_ANKLE']]) for t in range(VP.shape[0])])
kn=kn[np.isfinite(kn)]
print(f"Vicon LEFT knee angle over trial: min={kn.min():.1f} max={kn.max():.1f} mean={kn.mean():.1f} (walking flexion should swing ~0-70)")
print("first 10 vicon knee angles:", np.round(kn[:10],1))
# events files
for ev in glob.glob(f"{trial}/*events*"):
    print(f"--- {os.path.basename(ev)} ---");
    try: print(open(ev).read()[:400])
    except: print("(binary)")
# also check sample marker coords magnitude (units/frame)
print("sample LEFT_KNEE xyz frame0:", np.round(VP[0][li['LEFT_KNEE']],1))
