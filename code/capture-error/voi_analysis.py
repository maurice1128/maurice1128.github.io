"""Value of information by capture hardware — runs off the cached features (seconds, not minutes).

  L1  CAMERA        : sagittal kinematics of both limbs + spatiotemporal timing
                      (one phone filming from the side; a side view sees both legs)
  L2  + FORCE PLATE : adds body-weight-normalised GRF measures (frame-invariant only)

Scope limit stated honestly: a frontal-plane / 3D-markerless tier cannot be evaluated with this
planar model — every medio-lateral channel is identically zero (verified). That tier needs the 3D
H1922 model, which requires a Hyfydy licence.

Measurement noise is applied to the RAW joint signals before features are computed, so every level
is evaluated under capture error.
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
M = ['PF', 'DF', 'KE', 'KF', 'HF']
JOINTS = ['hip_flexion', 'knee_angle', 'ankle_angle']
LOG = None   # opened only under __main__ (see below); importing must not truncate


def say(m):
    print(m, flush=True); LOG.write(m + '\n'); LOG.flush()


det = pd.read_csv(os.path.join(HERE, 'features_det.csv'))
sig = pd.read_csv(os.path.join(HERE, 'signals_raw.csv')).set_index('tag')


def kinematic_features(tag, rng, noise):
    """Rebuild sagittal kinematic features from cached raw signals, with capture noise applied."""
    f = {}
    row = sig.loc[tag]
    for j in JOINTS:
        cl = [c for c in sig.columns if c.startswith(f'{j}_l_')]
        cr = [c for c in sig.columns if c.startswith(f'{j}_r_')]
        if not cl or not cr:
            continue
        l = row[cl].to_numpy(float); r = row[cr].to_numpy(float)
        if noise:
            l = l + rng.normal(0, noise, len(l)); r = r + rng.normal(0, noise, len(r))
        f[f'S::{j}_ROM_l'] = float(np.ptp(l)); f[f'S::{j}_min_l'] = float(l.min()); f[f'S::{j}_max_l'] = float(l.max())
        f[f'S::{j}_ROM_r'] = float(np.ptp(r)); f[f'S::{j}_min_r'] = float(r.min()); f[f'S::{j}_max_r'] = float(r.max())
        f[f'A::{j}_ROMd'] = float(np.ptp(l) - np.ptp(r))
        f[f'A::{j}_mind'] = float(l.min() - r.min())
        f[f'A::{j}_maxd'] = float(l.max() - r.max())
    return f


def build(n_rep=4, noise=2.0, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for _, d in det.iterrows():
        tag = d['tag']
        if tag not in sig.index:
            continue
        fixed = {k: d[k] for k in det.columns if k.startswith(('C::', 'G::'))}
        for _ in range(n_rep):
            f = kinematic_features(tag, rng, noise)
            # Measurement error must apply to EVERY capture tier, not just the kinematics, or the
            # comparison is unfair: force-plate and timing features were previously byte-identical
            # across replicates. 1.5% relative error is representative of force-plate/timing noise.
            if noise:
                # The force-plate and timing error MUST scale with the capture tier. Holding it at a
                # constant 1.5%% while the camera is degraded twelve-fold makes the force plate the only
                # undegraded tier, which manufactures a rising 'value of the force plate' that is an
                # artefact of unequal degradation rather than a property of the measurement.
                rel = 0.015 * (float(noise) / 2.0)
                f.update({k: float(v) * (1.0 + rng.normal(0, rel)) for k, v in fixed.items()})
            else:
                f.update(fixed)
            f['tag'] = tag; f['subj'] = d['subj']; f['mech'] = d['mech']; f['sev'] = int(d['sev'])
            rows.append(f)
    return pd.DataFrame(rows)


# Features that ARE terms of the CMA objective must be excluded: they encode how well the
# optimiser converged rather than biomechanics.
#   ReactionForceMeasure { max = 1.5 }  -> peak resultant GRF is penalised  => drop vgrf_peak*
#   GaitMeasure { min_velocity = 1.0 }  -> walking speed is constrained     => drop C::speed
# Verified contamination (Spearman rho vs the CMA objective / generation count):
#   G::vgrf_peak_l 0.665 | C::stance_frac_l 0.617 vs max_gen | C::step_time_r -0.573 vs max_gen
OBJECTIVE_TERMS = ('vgrf_peak', 'speed')
CONV_PROXIES = ('stance_frac_l', 'step_time_r')


def _clean(cols):
    return [c for c in cols if not any(k in c for k in OBJECTIVE_TERMS + CONV_PROXIES)]


def levels(df):
    S = _clean([c for c in df.columns if c.startswith('S::')])
    A = _clean([c for c in df.columns if c.startswith('A::')])
    C = _clean([c for c in df.columns if c.startswith('C::')])
    G = _clean([c for c in df.columns if c.startswith('G::')])
    return {
        'L1  camera (sagittal + timing)': S + A + C,
        'L2  camera + FORCE PLATE': S + A + C + G,
        '    - kinematics only (no timing)': S + A,
        '    - force plate alone': G,
    }


def loso(df, cols, seeds=2):
    subs = sorted(df.subj.unique())
    t1s, t3s, per = [], [], {}
    for sd in range(seeds):
        c1 = c3 = n = 0
        for ho in subs:
            tr, te = df[df.subj != ho], df[df.subj == ho]
            if not len(tr) or not len(te):
                continue
            Y = tr[[f'is_{m}' for m in M]].to_numpy(int)
            mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                            ('clf', MultiOutputClassifier(ExtraTreesClassifier(100, random_state=sd, n_jobs=1, class_weight='balanced')))])
            mdl.fit(tr[cols].to_numpy(float), Y)
            for tag in te.tag.unique():
                t = te[te.tag == tag]
                P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t)) for p in mdl.predict_proba(t[cols].to_numpy(float))]).T.mean(0)
                o = np.argsort(-P); ti = M.index(t.mech.iloc[0]); sev = int(t.sev.iloc[0]); n += 1
                h1 = int(o[0] == ti); h3 = int(ti in o[:3]); c1 += h1; c3 += h3
                if sd == 0:
                    per.setdefault(sev, [0, 0, 0]); per[sev][0] += h1; per[sev][1] += h3; per[sev][2] += 1
        if n:
            t1s.append(c1 / n); t3s.append(c3 / n)
    return float(np.mean(t1s)), float(np.std(t1s)), float(np.mean(t3s)), per


if __name__ == '__main__':
    LOG = open(os.path.join(HERE, 'voi_result.txt'), 'w')
    noise = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    df = build(n_rep=4, noise=noise, seed=0)
    for m in M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    say(f'=== VALUE OF INFORMATION BY CAPTURE HARDWARE ===')
    say(f'conditions={df.tag.nunique()}  bodies={sorted(df.subj.unique())}  capture noise={noise} deg')
    say(str(det.groupby(['subj', 'sev']).tag.nunique().unstack(fill_value=0)))
    say('')
    say(f'{"capture level":38}{"n_feat":>7}{"top-1":>13}{"top-3":>8}')
    res = {}
    for name, cols in levels(df).items():
        if not cols:
            continue
        t1, sd, t3, per = loso(df, cols)
        res[name] = (t1, t3, per)
        say(f'{name:38}{len(cols):7}   {t1:.3f}±{sd:.3f}{t3:8.3f}')
    # Baselines: uniform (1/5, 3/5) AND the majority-class baseline, which is the honest
    # reference when the mechanisms are not equally represented.
    cnt = det.mech.value_counts()
    maj1 = cnt.max() / cnt.sum()
    top3_counts = sorted(cnt.values, reverse=True)[:3]
    maj3 = sum(top3_counts) / cnt.sum()
    say(f'  baselines: uniform top-1 {1/len(M):.3f} / top-3 {3/len(M):.3f}'
        f'   |   majority-class top-1 {maj1:.3f} / top-3 {maj3:.3f}  <- the honest reference')
    k1, k2 = 'L1  camera (sagittal + timing)', 'L2  camera + FORCE PLATE'
    if k1 in res and k2 in res:
        say('')
        say('=== IS THE FORCE PLATE WORTH IT? ===')
        say(f'  camera alone    : top-1 {res[k1][0]:.3f}   top-3 {res[k1][1]:.3f}')
        say(f'  camera + plate  : top-1 {res[k2][0]:.3f}   top-3 {res[k2][1]:.3f}')
        say(f'  VALUE OF PLATE  : top-1 {res[k2][0]-res[k1][0]:+.3f}   top-3 {res[k2][1]-res[k1][1]:+.3f}')
    say('')
    say('=== per severity (seed 0) ===')
    for name, (t1, t3, per) in res.items():
        if per:
            say(f'  {name:38} ' + '  '.join(f'{s}%:{v[0]/v[2]:.2f}' for s, v in sorted(per.items()) if v[2]))
