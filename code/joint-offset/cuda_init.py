"""Import this FIRST (before onnxruntime/rtmlib) to enable the CUDA execution
provider on this machine. onnxruntime-gpu 1.27 needs CUDA-13 + cuDNN-9 runtime
DLLs (nvidia-cublas / nvidia-cuda-runtime / nvidia-cufft / nvidia-cudnn-cu13
pip wheels); they must be on BOTH os.add_dll_directory AND PATH or the CUDA EP
silently falls back to CPU. Usage:  import cuda_init  # noqa
"""
import os, glob, site

def _register():
    dirs = []
    for base in site.getsitepackages():
        dirs += glob.glob(os.path.join(base, "nvidia", "cu13", "bin", "x86_64"))
        dirs += glob.glob(os.path.join(base, "nvidia", "cudnn", "bin"))
        dirs += glob.glob(os.path.join(base, "nvidia", "*", "bin"))  # fallback layouts
    seen = set()
    for d in dirs:
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        try:
            os.add_dll_directory(d)
        except Exception:
            pass
        os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
    return sorted(seen)

REGISTERED = _register()
