"""Is the severity x capture-quality interaction actually supported?

The manuscript argues that capture quality determines the moderate case because only the moderate
row's own two intervals fail to overlap between 2 and 8 degrees. That is a within-row test, and the
claim is a between-row difference: it is the difference-of-significance fallacy, raised by a cold
reader and correct.

The proper test is a paired bootstrap. The same conditions appear at both error levels, so each
condition supplies its own 2-degree-to-8-degree loss, and the quantity of interest is the difference
in mean loss between two severity strata, resampled over conditions within each stratum.

Two confounds are checked at the same time. Composition: the severity strata are not balanced across
muscle groups (the 60 % stratum has few knee-extensor and knee-flexor conditions), so part of any
between-stratum gap could be which mechanisms happen to sit in which row. Reweighting each stratum to
a common mechanism mix removes that.

Run:  python severity_interaction.py
"""
import warnings
warnings.filterwarnings('ignore')
import os
import collections
import numpy as np
import voi_analysis as V
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
NSEED, NBOOT = 8, 4000
RNG = np.random.default_rng(0)


def per_condition(nz):
    """{tag: (hit rate, severity, mechanism)} at one capture-error level."""
    df = V.build(n_rep=4, noise=nz, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    cols = V.levels(df)['L1  camera (sagittal + timing)']
    acc = {}
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
                a = acc.setdefault(tag, [0, 0, int(tt.sev.iloc[0]), tt.mech.iloc[0]])
                a[0] += int(np.argsort(-P)[0] == V.M.index(tt.mech.iloc[0]))
                a[1] += 1
    return {k: (v[0] / v[1], v[2], v[3]) for k, v in acc.items()}


def main():
    out = open(os.path.join(HERE, 'severity_interaction.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True)
        out.write(m + '\n')
        out.flush()

    say('=== IS THE SEVERITY x CAPTURE-QUALITY INTERACTION SUPPORTED? ===')
    say('Paired over conditions: each condition supplies its own 2 deg -> 8 deg loss.')
    say('')

    a2, a8 = per_condition(2.0), per_condition(8.0)
    shared = sorted(set(a2) & set(a8))
    loss = {t: a8[t][0] - a2[t][0] for t in shared}
    sev = {t: a2[t][1] for t in shared}
    mech = {t: a2[t][2] for t in shared}

    strata = {s: [t for t in shared if sev[t] == s] for s in (20, 40, 60)}
    say(f'{"severity":10}{"n":>4}{"acc 2deg":>10}{"acc 8deg":>10}{"mean loss":>11}   mechanism mix')
    for s, tags in strata.items():
        mix = collections.Counter(mech[t] for t in tags)
        say(f'{s:8} %{len(tags):4}{np.mean([a2[t][0] for t in tags]):10.3f}'
            f'{np.mean([a8[t][0] for t in tags]):10.3f}'
            f'{np.mean([loss[t] for t in tags]):+11.3f}   '
            + ' '.join(f'{k}:{v}' for k, v in sorted(mix.items())))
    say('')

    say('--- paired bootstrap on the DIFFERENCE IN LOSS between strata ---')
    say(f'{"comparison":18}{"difference":>12}{"95 % CI":>22}  excludes zero')
    for x, y in ((40, 20), (40, 60), (60, 20)):
        lx = np.array([loss[t] for t in strata[x]])
        ly = np.array([loss[t] for t in strata[y]])
        obs = lx.mean() - ly.mean()
        b = np.array([lx[RNG.integers(0, len(lx), len(lx))].mean()
                      - ly[RNG.integers(0, len(ly), len(ly))].mean() for _ in range(NBOOT)])
        lo, hi = np.percentile(b, [2.5, 97.5])
        say(f'  {x} % vs {y} %{"":6}{obs:+12.3f}   [{lo:+.3f}, {hi:+.3f}]{"":6}'
            f'{"YES" if lo > 0 or hi < 0 else "no"}')
    say('')

    say('--- composition: does the mechanism mix explain the gaps? ---')
    say('Each stratum reweighted so every mechanism carries the same weight in all three.')
    common = sorted(set(mech.values()))
    say(f'{"severity":10}{"raw loss":>11}{"reweighted":>12}{"shift":>9}')
    rw = {}
    for s, tags in strata.items():
        per_m = {m: np.mean([loss[t] for t in tags if mech[t] == m])
                 for m in common if any(mech[t] == m for t in tags)}
        rw[s] = float(np.mean(list(per_m.values())))
        say(f'{s:8} %{np.mean([loss[t] for t in tags]):+11.3f}{rw[s]:+12.3f}'
            f'{rw[s] - np.mean([loss[t] for t in tags]):+9.3f}')
    say('')
    for x, y in ((40, 20), (40, 60)):
        raw = np.mean([loss[t] for t in strata[x]]) - np.mean([loss[t] for t in strata[y]])
        say(f'  {x} % vs {y} %: raw gap {raw:+.3f}, gap after reweighting {rw[x] - rw[y]:+.3f}')
    say('')
    say('READING: if the paired intervals exclude zero the interaction is supported and the')
    say('manuscript should quote them instead of the non-overlap argument. If they do not, the')
    say('claim has to be rescoped to what the data show: that the moderate case has the largest')
    say('point loss, without a demonstrated difference from the other two.')
    out.close()


if __name__ == '__main__':
    main()
