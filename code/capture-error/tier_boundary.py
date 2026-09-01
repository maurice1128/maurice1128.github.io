"""Where does the camera tier end? Report the comparison under every defensible tier assignment.

An audit found that the spatiotemporal features assigned to the CAMERA tier (`C::stance_frac`,
`C::step_time`, ...) are computed from vertical ground reaction force. `deployment_levels.py:32` says
so in its own docstring and argues that GRF onset/offset is equivalent to visible foot contact. That
argument is reasonable — a camera really can see heel strike and toe off — but it cannot be left
implicit, because the whole paper is a comparison between a camera and a camera-plus-force-plate, and
the answer moves if these nine features sit on the wrong side of the line.

Rather than pick an assignment and hope a reviewer agrees, this reports all three:

  A  TIMING IS CAMERA-OBSERVABLE, at force-plate precision.
     The original assumption. Indefensible on its own: it gives contact timing the precision of a
     force transducer while the camera's joint angles are being degraded.

  B  TIMING IS CAMERA-OBSERVABLE, at video precision.  <-- the defensible reading
     A camera detects contact events to within a frame or two. At 60 fps that is 17-33 ms against a
     step time near 0.55 s, i.e. roughly 3-6 % — several times worse than force-plate precision, and
     it should degrade further as capture quality falls (motion blur, occlusion, oblique view).

  C  TIMING REQUIRES THE FORCE PLATE.
     The conservative reading: if you do not trust video event detection, these features belong to
     the instrumented tier and the camera tier is kinematics only.

If the conclusion is the same under B and C, it is robust to the boundary. If it flips, the paper
must argue the boundary explicitly, and say so.

Run:  python tier_boundary.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = [0.0, 2.0, 5.0, 8.0, 12.0]

# Video contact-event detection error, as a fraction of the measured interval, at the reference
# capture quality (2 deg). One to two frames at 60 fps against a ~0.55 s step time.
VIDEO_TIMING_ERR = 0.045
PLATE_ERR = 0.015


def build(noise, timing_err, n_rep=4, seed=0):
    """Same features as voi_analysis, but timing and force error are specified separately."""
    rng = np.random.default_rng(seed)
    rows = []
    for _, d in V.det.iterrows():
        tag = d['tag']
        if tag not in V.sig.index:
            continue
        Ccols = {k: d[k] for k in V.det.columns if k.startswith('C::')}
        Gcols = {k: d[k] for k in V.det.columns if k.startswith('G::')}
        for _ in range(n_rep):
            f = V.kinematic_features(tag, rng, noise)
            scale = (noise / 2.0) if noise > 0 else 0.0
            te = timing_err * scale
            pe = PLATE_ERR * scale
            f.update({k: float(v) * (1.0 + rng.normal(0, te)) if te else float(v)
                      for k, v in Ccols.items()})
            f.update({k: float(v) * (1.0 + rng.normal(0, pe)) if pe else float(v)
                      for k, v in Gcols.items()})
            f['tag'] = tag; f['subj'] = d['subj']; f['mech'] = d['mech']
            rows.append(f)
    df = pd.DataFrame(rows)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    return df


def loso(df, cols, seeds=4):
    subs = sorted(df.subj.unique()); t1s, t3s = [], []
    for sd in range(seeds):
        c1 = c3 = n = 0
        for ho in subs:
            tr, te = df[df.subj != ho], df[df.subj == ho]
            if not len(tr) or not len(te):
                continue
            Y = tr[[f'is_{m}' for m in V.M]].to_numpy(int)
            mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                            ('clf', MultiOutputClassifier(ExtraTreesClassifier(
                                100, random_state=sd, n_jobs=1, class_weight='balanced')))])
            mdl.fit(tr[cols].to_numpy(float), Y)
            for tag in te.tag.unique():
                t = te[te.tag == tag]
                P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t))
                              for p in mdl.predict_proba(t[cols].to_numpy(float))]).T.mean(0)
                o = np.argsort(-P); ti = V.M.index(t.mech.iloc[0]); n += 1
                c1 += int(o[0] == ti); c3 += int(ti in o[:3])
        if n:
            t1s.append(c1 / n); t3s.append(c3 / n)
    return float(np.mean(t1s)), float(np.mean(t3s))


def main():
    out = open(os.path.join(HERE, 'tier_boundary.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== WHERE DOES THE CAMERA TIER END? ===')
    say('The spatiotemporal features are computed from vertical GRF but argued to be camera-observable.')
    say('Every defensible assignment is reported, because the paper compares exactly these two tiers.')
    say('')

    for label, timing_err, cam_has_timing in [
            ('A  timing = camera, force-plate precision (original)', PLATE_ERR, True),
            ('B  timing = camera, VIDEO precision (defensible)', VIDEO_TIMING_ERR, True),
            ('C  timing = force-plate tier (conservative)', PLATE_ERR, False)]:
        say(f'--- {label} ---')
        say(f'{"error":>7}{"camera t1":>11}{"camera t3":>11}{"+plate t1":>11}{"+plate t3":>11}{"plate value":>13}')
        for nz in LEVELS:
            df = build(nz, timing_err)
            S = [c for c in df.columns if c.startswith('S::')]
            A = [c for c in df.columns if c.startswith('A::')]
            C = V._clean([c for c in df.columns if c.startswith('C::')])
            G = V._clean([c for c in df.columns if c.startswith('G::')])
            cam = S + A + C if cam_has_timing else S + A
            both = S + A + C + G
            a1, a3 = loso(df, cam)
            b1, b3 = loso(df, both)
            say(f'{nz:7.1f}{a1:11.3f}{a3:11.3f}{b1:11.3f}{b3:11.3f}{b1-a1:+13.3f}')
        say('')

    say('=== READING ===')
    say('  If B and C give the same sign for the plate value at every error level, the conclusion is')
    say('  robust to where the boundary is drawn and the paper can state it plainly.')
    say('  If they disagree, the boundary is load-bearing and must be argued explicitly in Methods -')
    say('  and the honest report is BOTH columns, not the one that suits the argument.')
    out.close()


if __name__ == '__main__':
    main()
