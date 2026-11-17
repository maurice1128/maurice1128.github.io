"""The tolerance curve for a tier that a camera alone could actually deliver.

A cold reader pointed out that the paper's "camera" tier includes nine spatiotemporal features, and
that in this model those are derived from the vertical ground reaction force - so the tier a camera
could deliver on its own is the 27 kinematic and asymmetry features, not the 33 reported. S3 already
tests three tier assignments, but only for the kinetic delta; the kinematics-only tolerance curve is
never reported.

It should be, because it is the honest headline: a clinic with a camera and no force plate cannot
obtain step timing the way this model obtains it.

Run:  python kinematics_only.py
"""
import warnings
warnings.filterwarnings('ignore')
import os
import numpy as np
import voi_analysis as V
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = (0.0, 2.0, 5.0, 8.0, 12.0)
NSEED = 8
MAJ = 0.227


def curve(key):
    out = []
    for nz in LEVELS:
        df = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            df[f'is_{m}'] = (df.mech == m).astype(int)
        cols = V.levels(df)[key]
        hit = tot = 0
        for sd in range(NSEED):
            for ho in sorted(df.subj.unique()):
                tr, te = df[df.subj != ho], df[df.subj == ho]
                if not len(tr) or not len(te):
                    continue
                mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                                ('clf', MultiOutputClassifier(ExtraTreesClassifier(
                                    100, random_state=sd, n_jobs=1, class_weight='balanced')))])
                mdl.fit(tr[cols].to_numpy(float), tr[[f'is_{x}' for x in V.M]].to_numpy(int))
                for tag in te.tag.unique():
                    tt = te[te.tag == tag]
                    P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(tt))
                                  for p in mdl.predict_proba(tt[cols].to_numpy(float))]).T.mean(0)
                    hit += int(np.argsort(-P)[0] == V.M.index(tt.mech.iloc[0]))
                    tot += 1
        out.append(hit / tot)
    return out


def main():
    f = open(os.path.join(HERE, 'kinematics_only.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True)
        f.write(m + '\n')
        f.flush()

    say('=== WHAT A CAMERA ALONE DELIVERS ===')
    say('The reported "camera" tier is 33 features: 18 sagittal kinematics, 9 asymmetry, 9')
    say('spatiotemporal minus exclusions. In this model the spatiotemporal features are derived from')
    say('vertical ground reaction force, so a camera without a force plate would not have them.')
    say('The kinematics-only tier is the 27 kinematic and asymmetry features.')
    say('')

    k33 = curve('L1  camera (sagittal + timing)')
    k27 = curve('    - kinematics only (no timing)')

    say(f'{"capture error":>14}{"33-feature":>12}{"27-feature":>12}{"difference":>12}')
    for i, nz in enumerate(LEVELS):
        say(f'{nz:12.0f} deg{k33[i]:12.3f}{k27[i]:12.3f}{k27[i] - k33[i]:+12.3f}')
    say('')
    say(f'  33-feature: {k33[0]:.3f} at {LEVELS[0]:.0f} deg -> {k33[-1]:.3f} at {LEVELS[-1]:.0f} deg, '
        f'{k33[-1] / MAJ:.1f}x the {MAJ} baseline at the end')
    say(f'  27-feature: {k27[0]:.3f} at {LEVELS[0]:.0f} deg -> {k27[-1]:.3f} at {LEVELS[-1]:.0f} deg, '
        f'{k27[-1] / MAJ:.1f}x')
    d = np.array(k27) - np.array(k33)
    say(f'  mean cost of dropping the force-derived timing features: {d.mean():+.3f}')
    say('')
    say('READING: if the 27-feature curve stays well above baseline the tolerance claim holds for a')
    say('camera on its own, and the paper should report this curve as its headline. If it collapses,')
    say('the reported curve describes an instrumented setup and the claim has to say so.')
    f.close()


if __name__ == '__main__':
    main()
