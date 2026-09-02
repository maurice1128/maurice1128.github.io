"""Main paper figure: object-space advantage vs camera-distance asymmetry, on two
legs — real BioCV Vicon-GT data (natural outliers, to asym~3.8) and the controlled
realistic-geometry experiment (guaranteed outlier, isolates mechanism, to asym~31)."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

# real BioCV (BIOCV_CLUSTERED.txt), asym bin midpoints
b_as = [1.25, 1.75, 2.5, 3.5]
b_dm = [0.11, 0.11, 0.41, 3.61]
b_lo = [0.04, 0.06, 0.28, 2.32]; b_hi = [0.17, 0.15, 0.55, 5.25]
# controlled sim (BIOCV_SIM.txt) realA vs dMEAN
s_as = [3.15, 4.72, 6.30, 9.45, 12.59, 18.89, 25.19, 31.49]
s_dm = [3.01, 11.95, 37.03, 99.97, 172.95, 381.90, 652.64, 865.74]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
# left: real data, linear
a1.errorbar(b_as, b_dm, yerr=[np.array(b_dm)-b_lo, np.array(b_hi)-np.array(b_dm)],
            fmt='o-', color='#2a7', capsize=4, label='BioCV real Vicon GT')
a1.axhline(0, color='k', lw=.6)
a1.set_xlabel('camera-distance asymmetry (max/min)')
a1.set_ylabel('object-space advantage  dMEAN (mm)')
a1.set_title('Real gait data (natural outliers)\n95% trial-cluster CI'); a1.grid(alpha=.3); a1.legend()
# right: sim, log-y to show super-linear growth
a2.semilogy(s_as, s_dm, 's-', color='#37a', label='controlled (realistic geometry)')
a2.semilogy(b_as, np.maximum(b_dm, 0.05), 'o', color='#2a7', label='BioCV real (overlap region)')
a2.set_xlabel('camera-distance asymmetry (max/min)')
a2.set_ylabel('object-space advantage  dMEAN (mm, log)')
a2.set_title('Advantage grows super-linearly with asymmetry\n(controlled, guaranteed outlier)')
a2.grid(alpha=.3, which='both'); a2.legend()
fig.suptitle('Object-space outlier removal: benefit grows with camera-distance asymmetry', y=1.02)
fig.tight_layout(); fig.savefig("D:/BioCV/fig_asymmetry.png", dpi=140, bbox_inches='tight')
print("saved D:/BioCV/fig_asymmetry.png")
