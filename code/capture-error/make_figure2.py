"""Figure 2: one frame from each of the five simulated gaits.

Frames come from the rendered videos of the simulations. They share a frame number, not a gait
phase, so they show what each walker looks like and are not a matched comparison. Colour on the
muscles is activation for every muscle on both limbs, as defined in make_gait_video_pro.py; it does
not mark the weakened limb.

Run:  python make_figure2.py
"""
import os
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figure2.png')
TMP = os.path.join(HERE, '_frames')

# the weakened panel of the rendered comparison, measured on a 1466 x 824 frame
CROP = (935, 168, 1375, 548)     # below the clip's own caption, tight on the walker
FRAME = 92                                   # same frame number in every clip

CLIPS = [
    ('gait_PF60_pro.mp4', 'Plantarflexors', '60 %'),
    ('gait_DF60_pro.mp4', 'Dorsiflexors', '60 %'),
    ('gait_KE60_pro.mp4', 'Knee extensors', '60 %'),
    ('gait_KF40_pro.mp4', 'Knee flexors', '40 %'),
    ('gait_HF60_pro.mp4', 'Hip flexors', '60 %'),
]

os.makedirs(TMP, exist_ok=True)
exe = imageio_ffmpeg.get_ffmpeg_exe()

images = []
for clip, name, sev in CLIPS:
    src = os.path.join(HERE, clip)
    if not os.path.exists(src):
        print('  !! missing %s' % clip)
        continue
    png = os.path.join(TMP, clip.replace('.mp4', '.png'))
    subprocess.run([exe, '-y', '-loglevel', 'error', '-i', src,
                    '-vf', 'select=eq(n\\,%d)' % FRAME, '-vframes', '1', png], check=True)
    images.append((Image.open(png).crop(CROP), name, sev))

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, axes = plt.subplots(1, len(images), figsize=(7.2, 2.3))
for ax, (im, name, sev) in zip(axes, images):
    ax.imshow(im)
    ax.set_title('%s\n%s force loss' % (name, sev), fontsize=8.5, pad=5)
    ax.axis('off')

fig.subplots_adjust(bottom=0.02, top=0.82, wspace=0.04, left=0.01, right=0.99)
fig.savefig(OUT, dpi=300, facecolor='white')
print('wrote %s  (%d panels)' % (OUT, len(images)))
