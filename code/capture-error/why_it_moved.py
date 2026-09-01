"""Why did the numbers move when ten cells were added? Test the explanation instead of asserting it.

When the dataset went from 61 to 71 conditions, mild-severity accuracy fell (0.799 -> 0.580 at 20 %)
and the force plate became statistically detectable at 8 deg. The explanation offered was that the
added cells were concentrated in s2, the weakest body, and that a harder body both depresses
mild-weakness identification and raises the relative value of kinetics.

That is a plausible story, and it was asserted without evidence. It makes three predictions that can
be checked:

  P1  s2 conditions are identified less accurately than other bodies.
  P2  Removing s2 from the analysis restores something close to the old numbers.
  P3  The force plate's marginal value is larger within s2 than within the other bodies.

If P1-P3 hold, the explanation stands. If they do not, the movement has some other cause and the
explanation must be withdrawn rather than repeated.

Run:  python why_it_moved.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
NSEED = 6
K1 = 'L1  camera (sagittal + timing)'
K2 = 'L2  camera + FORCE PLATE'


def per_condition(df, cols, seeds, subset=None):
    """top-1 correctness per condition; folds are always over the full body set."""
    acc = {}
    subs = sorted(df.subj.unique())
    for sd in range(seeds):
        for ho in subs:
            tr, te = df[df.subj != ho], df[df.subj == ho]
            if subset is not None:
                te = te[te.subj.isin(subset)]
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
                a = acc.setdefault(tag, [0, 0])
                a[0] += int(np.argsort(-P)[0] == V.M.index(t.mech.iloc[0])); a[1] += 1
    return {k: v[0] / v[1] for k, v in acc.items()}


def loso(df, cols, drop=None, seeds=NSEED):
    d = df if drop is None else df[df.subj != drop]
    subs = sorted(d.subj.unique()); t1 = []
    for sd in range(seeds):
        c = n = 0
        for ho in subs:
            tr, te = d[d.subj != ho], d[d.subj == ho]
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
                n += 1
                c += int(np.argsort(-P)[0] == V.M.index(t.mech.iloc[0]))
        if n:
            t1.append(c / n)
    return float(np.mean(t1)) if t1 else float('nan')


def main():
    out = open(os.path.join(HERE, 'why_it_moved.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    df = V.build(n_rep=4, noise=2.0, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    lv = V.levels(df)

    say('=== WHY DID THE NUMBERS MOVE? ===')
    say(f'conditions {df.tag.nunique()}   capture error 2 deg   seeds {NSEED}')
    say(str(V.det.groupby(['subj', 'sev']).tag.nunique().unstack(fill_value=0)))
    say('')

    # ---- P1: is s2 harder than the other bodies? ------------------------------------------
    say('--- P1: accuracy of each body when it is the held-out body ---')
    h1 = per_condition(df, lv[K1], NSEED)
    h2 = per_condition(df, lv[K2], NSEED)
    tagsub = V.det.set_index('tag').subj.to_dict()
    tagsev = V.det.set_index('tag').sev.to_dict()
    say(f'{"body":>6}{"n":>5}{"camera":>9}{"+plate":>9}{"plate value":>13}')
    per_body = {}
    for b in sorted(set(tagsub.values())):
        ts = [t for t in h1 if tagsub.get(t) == b]
        if not ts:
            continue
        a = np.mean([h1[t] for t in ts]); c = np.mean([h2[t] for t in ts])
        per_body[b] = (a, c, len(ts))
        say(f'{b:>6}{len(ts):5}{a:9.3f}{c:9.3f}{c-a:+13.3f}')
    say('')
    if 's2' in per_body:
        others = [v[0] for k, v in per_body.items() if k != 's2']
        say(f'  s2 camera accuracy {per_body["s2"][0]:.3f} vs mean of the others {np.mean(others):.3f}')
        say('  P1 ' + ('SUPPORTED: s2 is the hardest body' if per_body['s2'][0] < min(others)
                       else 'NOT SUPPORTED: s2 is not the hardest body'))
    say('')

    # ---- P2: does removing s2 restore the earlier picture? ---------------------------------
    say('--- P2: mild-severity accuracy with and without s2 ---')
    say(f'{"severity":>9}{"all bodies":>12}{"without s2":>12}{"difference":>12}')
    for sev in (20, 40, 60):
        ts = [t for t in h1 if tagsev.get(t) == sev]
        allb = np.mean([h1[t] for t in ts]) if ts else float('nan')
        ns = [t for t in ts if tagsub.get(t) != 's2']
        nos2 = np.mean([h1[t] for t in ns]) if ns else float('nan')
        say(f'{sev:8}%{allb:12.3f}{nos2:12.3f}{nos2-allb:+12.3f}')
    say('')
    say('  (these are the same folds; only which conditions are SCORED differs, so this isolates')
    say('   "s2 conditions are harder" from "training on s2 changes the model")')
    say('')

    # retrain without s2 entirely, which is the other half of the question
    say('--- P2b: retrained with s2 removed from training as well ---')
    a_all = loso(df, lv[K1])
    a_nos2 = loso(df, lv[K1], drop='s2')
    say(f'  overall top-1 all bodies {a_all:.3f}   |   s2 removed entirely {a_nos2:.3f}   '
        f'difference {a_nos2-a_all:+.3f}')
    say('')

    # ---- P3: is the force plate worth more inside s2? --------------------------------------
    say('--- P3: marginal value of the force plate, by body ---')
    vals = {b: v[1] - v[0] for b, v in per_body.items()}
    for b in sorted(vals):
        say(f'  {b:>6}  {vals[b]:+.3f}')
    if 's2' in vals:
        others = [v for k, v in vals.items() if k != 's2']
        say('')
        say(f'  s2 {vals["s2"]:+.3f} vs mean of the others {np.mean(others):+.3f}')
        say('  P3 ' + ('SUPPORTED: kinetics are worth more on the hardest body'
                       if vals['s2'] > max(others) else
                       'NOT SUPPORTED: kinetics are not worth more on s2 than elsewhere'))
    say('')
    say('VERDICT: the explanation stands only if P1, P2 and P3 all hold. Any that fails must be')
    say('withdrawn rather than repeated, and the movement attributed to something else.')
    out.close()


if __name__ == '__main__':
    main()
