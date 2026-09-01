"""How degraded can motion capture be before the weak muscle group can no longer be identified?

This replaces the earlier framing. The earlier experiment asked "is a force plate worth adding?" and
answered "+0.000", which is a null at a ceiling (top-3 = 1.000) and therefore uninformative: nothing
*could* have added value there.

The question here has no ceiling by construction, because capture quality is degraded until the task
breaks. It is also the question a clinic actually faces. Laboratory markerless capture is not what
gets deployed: deployment happens in a large room, with other people moving, with occlusion, with the
camera further away and off-axis. All of that shows up as capture error, and the deployable claim is
a tolerance:

    identification survives up to E degrees of capture error; beyond that it degrades / fails.

NOISE MODEL. Independent per-frame Gaussian error is the optimistic case and would overstate
tolerance, because averaging over a trial removes it. Real markerless error is dominated by
components that do NOT average out:

  offset  a constant per-joint, per-trial bias from model scaling and calibration
  drift   a slow wander over the trial from soft-tissue artefact and tracking bias
  white   per-frame jitter from keypoint detection

The three are applied together, scaled by one deployment-quality parameter, so a single axis maps to
conditions a clinician can recognise. `--white-only` reproduces the optimistic model for comparison,
which is itself a result worth reporting: the gap between the two is how much of the earlier
robustness was an artefact of assuming benign noise.

Run:  python tolerance.py                  (structured noise, default sweep)
      python tolerance.py --white-only     (optimistic comparison)
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
WHITE_ONLY = '--white-only' in sys.argv
LEVELS = [0.0, 1.0, 2.0, 3.0, 4.5, 6.0, 8.0, 11.0, 15.0, 20.0]

# proportion of the total error budget carried by each component (structured model)
MIX = dict(offset=0.55, drift=0.30, white=0.15)


def noisy_signals(tag, rng, scale, white_only):
    """Return per-joint left/right waveforms with deployment-realistic error applied."""
    row = V.sig.loc[tag]
    out = {}
    for j in V.JOINTS:
        for side in ('l', 'r'):
            cols = [c for c in V.sig.columns if c.startswith(f'{j}_{side}_')]
            if not cols:
                continue
            x = row[cols].to_numpy(float)
            n = len(x)
            if scale > 0:
                if white_only:
                    x = x + rng.normal(0, scale, n)
                else:
                    # offset: one constant per joint per side per trial - does not average out
                    x = x + rng.normal(0, scale * MIX['offset'])
                    # drift: a slow wander across the trial, random phase
                    ph = rng.uniform(0, 2 * np.pi)
                    x = x + scale * MIX['drift'] * np.sqrt(2) * np.sin(
                        np.linspace(0, np.pi, n) + ph)
                    # white: per-frame jitter
                    x = x + rng.normal(0, scale * MIX['white'], n)
            out[(j, side)] = x
    return out


def features(tag, rng, scale, white_only):
    w = noisy_signals(tag, rng, scale, white_only)
    f = {}
    for j in V.JOINTS:
        if (j, 'l') not in w or (j, 'r') not in w:
            continue
        l, r = w[(j, 'l')], w[(j, 'r')]
        f[f'S::{j}_ROM_l'] = float(np.ptp(l)); f[f'S::{j}_min_l'] = float(l.min()); f[f'S::{j}_max_l'] = float(l.max())
        f[f'S::{j}_ROM_r'] = float(np.ptp(r)); f[f'S::{j}_min_r'] = float(r.min()); f[f'S::{j}_max_r'] = float(r.max())
        f[f'A::{j}_ROMd'] = float(np.ptp(l) - np.ptp(r))
        f[f'A::{j}_mind'] = float(l.min() - r.min())
        f[f'A::{j}_maxd'] = float(l.max() - r.max())
    return f


def build(scale, white_only, n_rep=4, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for _, d in V.det.iterrows():
        tag = d['tag']
        if tag not in V.sig.index:
            continue
        fixed = {k: d[k] for k in V.det.columns if k.startswith(('C::', 'G::'))}
        for _ in range(n_rep):
            f = features(tag, rng, scale, white_only)
            rel = 0.015 * (scale / 2.0) if scale > 0 else 0.0    # force/timing error scales with tier quality
            f.update({k: float(v) * (1.0 + rng.normal(0, rel)) if rel else float(v)
                      for k, v in fixed.items()})
            f['tag'] = tag; f['subj'] = d['subj']; f['mech'] = d['mech']; f['sev'] = int(d['sev'])
            rows.append(f)
    df = pd.DataFrame(rows)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    return df


def evaluate(df, cols, seeds=4):
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
    return float(np.mean(t1s)), float(np.std(t1s)), float(np.mean(t3s))


def main():
    name = 'tolerance_whiteonly.txt' if WHITE_ONLY else 'tolerance.txt'
    out = open(os.path.join(HERE, name), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    say('=== CAPTURE-QUALITY TOLERANCE ===')
    say(f'noise model: {"WHITE ONLY (optimistic)" if WHITE_ONLY else "STRUCTURED (offset 55% / drift 30% / white 15%)"}')
    say(f'conditions {len(V.det)} | the scale is the total per-joint error SD in degrees')
    say('')
    say(f'{"error":>7}  {"camera t1":>10}{"+-":>7}{"camera t3":>10}   {"+plate t1":>10}{"+plate t3":>10}   {"plate value":>12}')

    K1 = 'L1  camera (sagittal + timing)'
    K2 = 'L2  camera + FORCE PLATE'
    rows = []
    for s in LEVELS:
        df = build(s, WHITE_ONLY)
        lv = V.levels(df)
        a1, asd, a3 = evaluate(df, lv[K1])
        b1, _, b3 = evaluate(df, lv[K2])
        rows.append((s, a1, asd, a3, b1, b3))
        say(f'{s:7.1f}  {a1:10.3f}{asd:7.3f}{a3:10.3f}   {b1:10.3f}{b3:10.3f}   {b1-a1:+12.3f}')

    # majority-class baseline is the level the task is "broken" at
    cnt = V.det.mech.value_counts()
    maj1, maj3 = cnt.max() / cnt.sum(), sum(sorted(cnt.values, reverse=True)[:3]) / cnt.sum()
    say('')
    say(f'majority-class baseline: top-1 {maj1:.3f}  top-3 {maj3:.3f}   (the task is dead at this level)')
    say('')
    say('=== tolerance thresholds (camera tier) ===')
    base = rows[0][1]
    for drop, tag in ((0.05, '5 % relative'), (0.10, '10 % relative')):
        over = [s for s, a1, *_ in rows if a1 < base * (1 - drop)]
        say(f'  first error level where top-1 falls more than {tag}: '
            + (f'{min(over):.1f} deg' if over else 'never in the swept range'))
    dead = [s for s, a1, *_ in rows if a1 <= maj1]
    say(f'  first error level at or below the majority-class baseline: '
        + (f'{min(dead):.1f} deg' if dead else 'never in the swept range'))
    say('')
    say('=== does the force plate rescue a degraded camera? ===')
    say('  (if the plate\'s value grows with capture error, kinetics earn their keep exactly where')
    say('   video is unreliable - that is a far more useful claim than a flat "+0.000")')
    for s, a1, _, _, b1, _ in rows:
        say(f'  {s:5.1f} deg : {b1-a1:+.3f}')
    out.close()


if __name__ == '__main__':
    main()
