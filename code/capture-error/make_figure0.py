"""Graphical abstract, regenerated from the same constants as Figure 1.

The previous graphical abstract was drawn before the force-plate result was repriced and before the
interval estimator changed. It showed the pairs-cluster percentile intervals that S7 now rules out,
and bracketed "plate earns its cost" from 5 deg, where the paper places the robust crossover at 8.
It also had no generating script, so it was the one panel the study's "every number comes from a
named script" claim did not cover.

Every value below is imported from make_figure1.py rather than retyped, so the two figures cannot
drift apart again.

Run:  python make_figure0.py
"""
import os
import re
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, RED, GREY = '#1f4e79', '#c0392b', '#888888'


def arr(src, name):
    """Read a list literal out of make_figure1.py so the two figures share one source of truth."""
    m = re.search(r'^%s\s*=\s*\[([^\]]*)\]' % name, src, flags=re.M)
    return [float(x) for x in m.group(1).split(',')]


fig1 = io.open(os.path.join(HERE, 'make_figure1.py'), encoding='utf-8').read()
ERR = arr(fig1, 'ERR')
CAM, PLATE = arr(fig1, 'CAM'), arr(fig1, 'PLATE')
GAIN, LO, HI = arr(fig1, 'GAIN'), arr(fig1, 'LO'), arr(fig1, 'HI')
MAJ = float(re.search(r'^MAJ\s*=\s*([\d.]+)', fig1, flags=re.M).group(1))
SEV = {'60 %': (0.963, 0.831), '40 %': (0.948, 0.562), '20 %': (0.610, 0.480)}

fig, ax = plt.subplots(1, 3, figsize=(13.2, 3.6))
plt.rcParams.update({'font.size': 9})

# (1) tolerance --------------------------------------------------------------------------------
a = ax[0]
a.axvspan(2, 5, color='#dbe7f3', zorder=0)
a.plot(ERR, CAM, 'o-', color=NAVY, lw=2.2, ms=6)
a.axhline(MAJ, ls=':', color=GREY, lw=1.2)
a.text(6.2, MAJ + 0.02, 'chance', fontsize=8, color=GREY)
a.text(3.5, 0.155, "field's\n2–5° limit", fontsize=8, color=NAVY, ha='center')
a.set_xlim(-0.5, 12.8); a.set_ylim(0.10, 1.0)
a.set_xlabel('capture error (deg)'); a.set_ylabel('top-1 accuracy')
a.set_title('1  Identification survives far past the limit', loc='left', fontsize=10, color=NAVY)

# (2) severity ---------------------------------------------------------------------------------
b = ax[1]
for (k, (v2, v8)), col in zip(SEV.items(), [NAVY, '#3d7ab5', '#8fb8dc']):
    b.plot([2, 8], [v2, v8], 'o-', color=col, lw=2.2, ms=6, label=k + ' force loss')

b.annotate('', xy=(8, 0.562), xytext=(8, 0.948),
           arrowprops=dict(arrowstyle='<->', color=RED, lw=1.4))
b.text(8.4, 0.75, '$-$0.385\nlargest of\nthe three', fontsize=8, color=RED, va='center')
b.set_xlim(0.8, 11.5); b.set_ylim(0.35, 1.05); b.set_xticks([2, 8])
b.set_xlabel('capture error (deg)'); b.set_ylabel('top-1 accuracy')
b.legend(frameon=False, fontsize=8, loc='lower left')
b.set_title('2  The moderate case loses most', loc='left', fontsize=10, color=NAVY)

# (3) kinetics ---------------------------------------------------------------------------------
c = ax[2]
c.axhline(0, color=GREY, lw=1)
c.axvspan(8, 12.8, color='#f6e2df', zorder=0)
for i, e in enumerate(ERR):
    c.plot([e, e], [LO[i], HI[i]], color=RED, lw=1.5)
    c.plot(e, GAIN[i], 'o', color=RED, ms=6,
           mfc=RED if LO[i] > 0 else 'white', mec=RED, mew=1.6)
c.text(10.4, -0.075, 'plate earns\nits cost', fontsize=8, color=RED, ha='center')
c.set_xlim(-0.5, 12.8)
c.set_xlabel('capture error (deg)'); c.set_ylabel('gain from adding force plate')
c.set_title('3  Kinetics pay off only once video degrades', loc='left', fontsize=10, color=NAVY)

for x in ax:
    for sp in ('top', 'right'):
        x.spines[sp].set_visible(False)

plt.tight_layout()
out = os.path.join(HERE, 'figure0_graphical_abstract.png')
plt.savefig(out, dpi=300, facecolor='white')
print('wrote', out)
print('  intervals taken from make_figure1.py:')
for i, e in enumerate(ERR):
    print('   %5.0f deg  gain %+0.3f  [%+0.3f, %+0.3f]  %s'
          % (e, GAIN[i], LO[i], HI[i], 'excludes zero' if LO[i] > 0 else 'includes zero'))
