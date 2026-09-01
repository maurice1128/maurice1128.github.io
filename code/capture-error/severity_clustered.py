"""Does the severity x capture-quality interaction survive the paper's own stricter resampling?

severity_interaction.py resamples CONDITIONS within each severity stratum. But the paper insists
elsewhere (S7, clustered_ci.py) that the 66 conditions are not 66 independent units: they come from
five bodies, and the body is also the cross-validation fold. Applying the loose standard to the
severity claim and the strict standard to the kinetics claim is an inconsistency a reviewer can see,
and the severity intervals stop only -0.010 and -0.007 short of zero, so it is not academic.

This repeats the interaction test resampling BODIES with replacement. Both are printed side by side.

A note on multiplicity, because it comes up: the claim is a CONJUNCTION - the moderate case loses
more than the mild case AND more than the severe case. A conjunction is an intersection-union test,
whose size is controlled at alpha by requiring every component to reject, so no Bonferroni widening
is required. The 60-vs-20 contrast is not part of the claim and is reported only for completeness.
What is NOT excused by that argument is the resampling unit, which is what this script tests.

Run:  python severity_clustered.py [n_seeds] [n_boot]
"""
import warnings; warnings.filterwarnings('ignore')
import os, sys
import numpy as np
import voi_analysis as V
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 8
NBOOT = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
RNG = np.random.default_rng(0)


def per_condition(nz):
    """{tag: (hit rate, severity, mechanism, body)} at one capture-error level."""
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
                a = acc.setdefault(tag, [0, 0, int(tt.sev.iloc[0]), tt.mech.iloc[0], tt.subj.iloc[0]])
                a[0] += int(np.argsort(-P)[0] == V.M.index(tt.mech.iloc[0]))
                a[1] += 1
    return {k: (v[0] / v[1], v[2], v[3], v[4]) for k, v in acc.items()}


def main():
    out = open(os.path.join(HERE, 'severity_clustered.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True)
        out.write(m + '\n'); out.flush()

    say('=== SEVERITY INTERACTION UNDER BOTH RESAMPLING UNITS ===')
    say(f'seeds {NSEED}, bootstrap draws {NBOOT}')
    say('')

    a2, a8 = per_condition(2.0), per_condition(8.0)
    shared = sorted(set(a2) & set(a8))
    loss = {t: a8[t][0] - a2[t][0] for t in shared}
    sev = {t: a2[t][1] for t in shared}
    body = {t: a2[t][3] for t in shared}
    mech = {t: a2[t][2] for t in shared}
    bodies = sorted(set(body.values()))
    import json
    json.dump({t: [loss[t], sev[t], mech[t], str(body[t])] for t in shared},
              open(os.path.join(HERE, 'severity_losses.json'), 'w'), indent=1)
    strata = {s: [t for t in shared if sev[t] == s] for s in (20, 40, 60)}

    say(f'{"body":12}' + ''.join(f'{s:>10} %' for s in (20, 40, 60)) + '   (mean 2->8 loss)')
    for b in bodies:
        row = []
        for s in (20, 40, 60):
            v = [loss[t] for t in strata[s] if body[t] == b]
            row.append(f'{np.mean(v):+11.3f}' if v else f'{"-":>11}')
        say(f'  {str(b):10}' + ''.join(row))
    say('')

    say(f'{"comparison":16}{"difference":>12}{"95 % over conditions":>26}{"95 % over bodies":>24}')
    verdict = {}
    for x, y in ((40, 20), (40, 60), (60, 20)):
        lx = np.array([loss[t] for t in strata[x]])
        ly = np.array([loss[t] for t in strata[y]])
        obs = lx.mean() - ly.mean()

        # loose: resample conditions independently within each stratum
        bc = np.array([lx[RNG.integers(0, len(lx), len(lx))].mean()
                       - ly[RNG.integers(0, len(ly), len(ly))].mean() for _ in range(NBOOT)])
        cl, ch = np.percentile(bc, [2.5, 97.5])

        # strict: resample the five bodies with replacement, carrying every condition each owns,
        # so conditions sharing a model and a held-out fold move together as they must
        bx = {b: np.array([loss[t] for t in strata[x] if body[t] == b]) for b in bodies}
        by = {b: np.array([loss[t] for t in strata[y] if body[t] == b]) for b in bodies}
        bb = []
        for _ in range(NBOOT):
            pick = [bodies[i] for i in RNG.integers(0, len(bodies), len(bodies))]
            vx = np.concatenate([bx[b] for b in pick if len(bx[b])])
            vy = np.concatenate([by[b] for b in pick if len(by[b])])
            if len(vx) and len(vy):
                bb.append(vx.mean() - vy.mean())
        bl, bh = np.percentile(bb, [2.5, 97.5])
        verdict[(x, y)] = (obs, (cl, ch), (bl, bh))
        say(f'  {x} % vs {y} %{"":4}{obs:+12.3f}   [{cl:+.3f}, {ch:+.3f}] {"YES" if cl > 0 or ch < 0 else "no ":>4}'
            f'   [{bl:+.3f}, {bh:+.3f}] {"YES" if bl > 0 or bh < 0 else "no "}')
    say('')

    say('--- the same two contrasts after equalising the mechanism mix ---')
    say('Each stratum reweighted so every mechanism carries equal weight, then bootstrapped.')
    common = sorted(set(mech.values()))

    def rw_mean(tags):
        per_m = [np.mean([loss[t] for t in tags if mech[t] == m])
                 for m in common if any(mech[t] == m for t in tags)]
        return float(np.mean(per_m)) if per_m else np.nan

    say(f'{"comparison":16}{"reweighted":>12}{"95 % over conditions":>26}{"95 % over bodies":>24}')
    for x, y in ((40, 20), (40, 60)):
        obs = rw_mean(strata[x]) - rw_mean(strata[y])
        bc = []
        for _ in range(NBOOT):
            rx = [strata[x][i] for i in RNG.integers(0, len(strata[x]), len(strata[x]))]
            ry = [strata[y][i] for i in RNG.integers(0, len(strata[y]), len(strata[y]))]
            v = rw_mean(rx) - rw_mean(ry)
            if v == v:
                bc.append(v)
        cl, ch = np.percentile(bc, [2.5, 97.5])
        bb = []
        for _ in range(NBOOT):
            pick = [bodies[i] for i in RNG.integers(0, len(bodies), len(bodies))]
            rx = [t for b in pick for t in strata[x] if body[t] == b]
            ry = [t for b in pick for t in strata[y] if body[t] == b]
            v = rw_mean(rx) - rw_mean(ry)
            if v == v:
                bb.append(v)
        bl, bh = np.percentile(bb, [2.5, 97.5])
        say(f'  {x} % vs {y} %{"":4}{obs:+12.3f}   [{cl:+.3f}, {ch:+.3f}] {"YES" if cl > 0 or ch < 0 else "no ":>4}'
            f'   [{bl:+.3f}, {bh:+.3f}] {"YES" if bl > 0 or bh < 0 else "no "}')
    say('')

    say('--- the same two contrasts as a t interval on the five per-body losses ---')
    say('At five clusters a percentile bootstrap is confined to the convex hull of the five body')
    say('means, so when they agree in sign it cannot cross zero whatever the true uncertainty')
    say('(cluster_degeneracy.py). The t interval can fail, so it is the one the paper reports.')
    say(f'{"comparison":16}{"per-body losses":>44}{"mean":>9}{"t(4) 95 % CI":>22}')
    T4 = 2.776           # t(0.975, df = 4), five bodies
    tver = {}
    for x, y in ((40, 20), (40, 60)):
        v = np.array([np.mean([loss[t] for t in strata[x] if body[t] == b])
                      - np.mean([loss[t] for t in strata[y] if body[t] == b]) for b in bodies])
        se = v.std(ddof=1) / np.sqrt(len(v))
        lo, hi = v.mean() - T4 * se, v.mean() + T4 * se
        tver[(x, y)] = (lo, hi)
        say(f'  {x} % vs {y} %{"":4}' + ' '.join(f'{q:+7.3f}' for q in v)
            + f'{v.mean():+9.3f}   [{lo:+.3f}, {hi:+.3f}]  '
            + ('excludes zero' if lo > 0 or hi < 0 else 'INCLUDES ZERO'))
    say('')

    a = verdict[(40, 20)][2]; b = verdict[(40, 60)][2]
    both = (a[1] < 0 or a[0] > 0) and (b[1] < 0 or b[0] > 0)
    say('READING: the claim is the conjunction "the moderate case loses more than the mild case AND')
    say('more than the severe case". As an intersection-union test it needs both components to')
    say('reject and needs no multiplicity widening. Under the strict unit that conjunction is')
    ta, tb = tver[(40, 20)], tver[(40, 60)]
    tboth = (ta[1] < 0 or ta[0] > 0) and (tb[1] < 0 or tb[0] > 0)
    say('  under the percentile bootstrap : ' + ('supported' if both else 'not supported'))
    say('  under the t interval           : ' + ('supported' if tboth else 'NOT SUPPORTED'))
    say('')
    say('The t interval is the one to report: it is the estimator used for Table 4, and it is the')
    say('one that can fail at five clusters. The claim is rescoped to the observation - the moderate')
    say('case shows the largest loss, in four bodies of five, without a separable difference.')
    out.close()


if __name__ == '__main__':
    main()
