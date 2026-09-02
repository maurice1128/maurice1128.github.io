"""Figure for the controlled outlier-injection result (real Vicon GT)."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# hard-coded from BIOCV_INJECT.txt (deterministic, SEED=2024)
rate = [0, 10, 20, 30, 40]
dp95 = [1.8, 24.7, 40.8, 43.9, 63.4]
rec_re = [78, 62, 42, 25, 13]
rec_di = [78, 65, 49, 33, 20]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
a1.plot(rate, dp95, 'D-', color='#37a'); a1.axhline(0, color='k', lw=.6)
a1.set_xlabel('injected 2D outlier rate (%)')
a1.set_ylabel('distance advantage on worst frames  dP95 (mm)')
a1.set_title('object-space benefit grows with outlier rate'); a1.grid(alpha=.3)
a2.plot(rate, rec_re, 'o-', color='#c44', label='reprojection removal')
a2.plot(rate, rec_di, 's-', color='#37a', label='distance (object-space) removal')
a2.set_xlabel('injected 2D outlier rate (%)')
a2.set_ylabel('usable reconstructions  (<50 mm, %)')
a2.set_title('distance recovers more usable frames under noise')
a2.legend(); a2.grid(alpha=.3)
fig.suptitle('BioCV real Vicon GT — controlled outlier injection (N=4800)', y=1.02)
fig.tight_layout(); fig.savefig("D:/BioCV/biocv_inject.png", dpi=140, bbox_inches='tight')
print("saved D:/BioCV/biocv_inject.png")
