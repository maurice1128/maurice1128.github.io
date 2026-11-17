"""Figure 3: the confusion matrices as a colour map.

Every cell was checked against clinical_breakdown.txt, the source canonical_values.txt names for
confusion values. Red boxes mark the three most frequent misidentifications at 2 deg, ranked by share
of all conditions as in that file.

Run:  python make_figure3.py
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figure3.png')

GROUPS = ['plantarflexors', 'dorsiflexors', 'knee extensors', 'knee flexors', 'hip flexors']
SHORT = ['PF', 'DF', 'KE', 'KF', 'HF']

# clinical_breakdown.txt, rows are the imposed weakness, columns the identified group, in per cent
M2 = np.array([
    [90,  1,  6,  3,  0],
    [0,  84,  0,  2, 13],
    [22, 10, 60,  8,  0],
    [0,  14,  0, 69, 18],
    [0,   0,  0,  0, 100],
], float)

M8 = np.array([
    [90,  0,  9,  1,  0],
    [12, 50,  0, 17, 21],
    [39,  5, 38, 19,  0],
    [0,  23,  0, 57, 20],
    [21,  8,  0, 14, 57],
], float)

# the pairs the Discussion names as functional neighbours, (row, col) zero-indexed
NEIGHBOURS = [(2, 0), (3, 4), (1, 4)]

# white through a muted blue, so the diagonal reads as weight rather than as decoration
CMAP = LinearSegmentedColormap.from_list(
    'ident', ['#ffffff', '#dce6f1', '#9dbbd9', '#4a7fb5', '#1f4e79'])

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5))

for ax, M, title in zip(axes, (M2, M8), ('2° of capture error', '8° of capture error')):
    im = ax.imshow(M, cmap=CMAP, vmin=0, vmax=100)

    for i in range(5):
        for j in range(5):
            v = M[i, j]
            if v == 0:
                ax.text(j, i, '·', ha='center', va='center', color='#bbbbbb', fontsize=11)
                continue
            ax.text(j, i, '%d' % v, ha='center', va='center',
                    color='white' if v >= 55 else '#222222',
                    fontweight='bold' if i == j else 'normal', fontsize=9)

    # ring the three named confusions, inset so the box reads as a mark and not as a gridline
    for i, j in NEIGHBOURS:
        ax.add_patch(plt.Rectangle((j - .38, i - .38), .76, .76, fill=False,
                                   edgecolor='#c0392b', linewidth=2.0, zorder=3))

    ax.set_xticks(range(5), SHORT)
    ax.set_yticks(range(5), SHORT)
    ax.set_xlabel('identified as')
    ax.set_title(title, fontsize=9, pad=8)
    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 5, 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.5)
    ax.tick_params(which='minor', length=0)
    for s in ax.spines.values():
        s.set_visible(False)

axes[0].set_ylabel('imposed weakness')

cb = fig.colorbar(plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 100)),
                  ax=axes, fraction=0.025, pad=0.02)
cb.set_label('per cent of conditions in the row', fontsize=8)
cb.ax.tick_params(labelsize=8)

fig.savefig(OUT, dpi=300, bbox_inches='tight', facecolor='white')
print('wrote %s' % OUT)

# rows must still sum to 100 after transcription
for name, M in (('2 deg', M2), ('8 deg', M8)):
    print('  %s row sums: %s' % (name, M.sum(axis=1).astype(int).tolist()))
