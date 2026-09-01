"""Figure 1, in a 2x2 layout.

The previous version placed four panels in a single row, giving a 4.2:1 strip that renders at about
1.7 inches per panel once fitted to a manuscript column - too small to read the axis labels. A 2x2
arrangement roughly doubles the panel size at the same page width.

Every number here is transcribed from an analysis output file, named in the comment above it, so the
figure can be checked against the same sources as the text.

Run:  python make_figure1.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figure1.png')

NAVY, RED, GREY = '#1f4e79', '#c0392b', '#888888'
MAJ = 0.227                              # 15/66, the frozen dataset

# crossover_ci.txt
ERR = [0, 2, 5, 8, 12]
CAM = [0.845, 0.824, 0.659, 0.600, 0.549]
PLATE = [0.877, 0.822, 0.775, 0.759, 0.731]
GAIN = [0.032, -0.002, 0.116, 0.159, 0.182]
# cluster_degeneracy.txt - t interval on the five per-body gains, the unit Table 4 reports
LO = [-0.068, -0.101, 0.018, 0.035, 0.075]
HI = [0.134, 0.096, 0.223, 0.293, 0.300]

# remaining_checks.txt
SEV = {'60 % force loss': (0.963, 0.831), '40 %': (0.948, 0.562), '20 % (mild)': (0.610, 0.480)}
SEVCI = {'60 % force loss': ((0.897, 1.000), (0.654, 0.978)),
         '40 %': ((0.870, 1.000), (0.380, 0.740)),
         '20 % (mild)': ((0.425, 0.785), (0.290, 0.665))}

# clinical_breakdown.txt, diagonal of the confusion matrix
GROUPS = ['plantar-\nflexors', 'dorsi-\nflexors', 'knee\nextensors', 'knee\nflexors', 'hip\nflexors']
G2 = [0.90, 0.84, 0.60, 0.69, 1.00]
G8 = [0.90, 0.50, 0.38, 0.57, 0.57]

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(2, 2, figsize=(7.2, 6.0))
(a, b), (c, d) = ax

# (a) tolerance -----------------------------------------------------------------------------------
a.axvspan(2, 5, color=GREY, alpha=0.15, lw=0)
a.text(3.5, 0.97, "field's\nconvention", ha='center', va='top', fontsize=7, color=GREY)
a.axhline(MAJ, ls=':', color=GREY, lw=1.2)
a.text(12.4, MAJ + 0.022, 'chance', ha='right', fontsize=7, color=GREY)
a.plot(ERR, CAM, 'o-', color=NAVY, lw=2, ms=5, label='camera (sagittal)')
a.plot(ERR, PLATE, 's--', color=RED, lw=1.8, ms=5, label='+ force plate')
a.set_ylim(0.10, 1.04); a.set_xlim(-0.4, 12.8)
a.set_xlabel('capture error (deg)'); a.set_ylabel('top-1 accuracy')
a.set_title('(a)  identification tolerates large capture error', loc='left', fontsize=9.5)
a.legend(frameon=False, fontsize=8, loc='lower left')

# (b) marginal value of kinetics --------------------------------------------------------------------
b.axhline(0, color=GREY, lw=1)
for i, e in enumerate(ERR):
    b.plot([e, e], [LO[i], HI[i]], color=RED, lw=1.4)
    b.plot(e, GAIN[i], 'o', color=RED, ms=6,
           mfc=RED if LO[i] > 0 else 'white', mec=RED, mew=1.6)
b.set_xlim(-0.4, 12.6)
b.set_xlabel('capture error (deg)'); b.set_ylabel('gain from adding force plate')
b.set_title('(b)  kinetics pay off once video degrades', loc='left', fontsize=9.5)
b.text(0.4, 0.285, 'filled = 95 % CI excludes zero', fontsize=7.5, color=RED, ha='left')

# (c) severity ----------------------------------------------------------------------------------
shades = [NAVY, '#3d7ab5', '#8fb8dc']
for (k, (v2, v8)), col in zip(SEV.items(), shades):
    (l2, h2), (l8, h8) = SEVCI[k]
    c.plot([2, 2], [l2, h2], color=col, lw=1.2, alpha=0.5)
    c.plot([8, 8], [l8, h8], color=col, lw=1.2, alpha=0.5)
    c.plot([2, 8], [v2, v8], 'o-', color=col, lw=2, ms=6, label=k)
c.axhline(MAJ, ls=':', color=GREY, lw=1.2)
c.set_xlim(0.5, 9.5); c.set_ylim(0.10, 1.07); c.set_xticks([2, 8])
c.set_xlabel('capture error (deg)'); c.set_ylabel('top-1 accuracy')
c.set_title('(c)  the moderate case loses most between 2 and 8 deg', loc='left', fontsize=9.5)
c.legend(frameon=False, fontsize=8, loc='lower left', bbox_to_anchor=(0.0, 0.02))

# (d) by muscle group ---------------------------------------------------------------------------
x = np.arange(len(GROUPS))
d.bar(x - 0.2, G2, 0.38, color=NAVY, label='2 deg')
d.bar(x + 0.2, G8, 0.38, color='#8fb8dc', label='8 deg')
d.axhline(MAJ, ls=':', color=GREY, lw=1.2)
d.set_xticks(x); d.set_xticklabels(GROUPS, fontsize=7.5)
d.set_ylim(0, 1.22); d.set_ylabel('correctly identified')
d.set_title('(d)  which groups survive degraded capture', loc='left', fontsize=9.5, pad=14)
d.legend(frameon=False, fontsize=8, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.03))

fig.tight_layout(pad=1.1)
fig.savefig(OUT, dpi=600, facecolor='white')
print('wrote', OUT)
from PIL import Image
im = Image.open(OUT)
print(f'  {im.width} x {im.height} px, {im.width / 7.0:.0f} dpi at a 7-inch column')
