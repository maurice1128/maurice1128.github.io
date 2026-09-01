"""The two results a physiotherapist actually wants, neither of which the manuscript reports.

A cold reviewer put it plainly: a therapist cares much more about *which groups get confused with
which* than about an aggregate accuracy, and cares most about mild weakness, which is where
identification would change management. Both are recoverable from the existing runs; they were
simply never printed.

  1. CONFUSION MATRIX - when identification is wrong, what does it say instead? A system that
     confuses knee extensors with plantarflexors misleads treatment in a specific, describable way.
     "0.84 accurate" tells a clinician nothing about that.

  2. ACCURACY BY SEVERITY - 20 / 40 / 60 % imposed force loss, reported separately. The hostile
     reading of an aggregate number is that all of it comes from the 60 % cells and mild weakness is
     invisible. Mild weakness is the clinically decisive case, so this cannot be left out.

Both are reported at two capture-error levels: laboratory quality and the degraded end, so the
reader can see whether the confusion structure is stable or whether error changes what the system
gets wrong.

Run:  python clinical_breakdown.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier

import voi_analysis as V

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = [2.0, 8.0]
NSEED = 8
FULL = {'PF': 'plantarflexors', 'DF': 'dorsiflexors', 'KE': 'knee extensors',
        'KF': 'knee flexors', 'HF': 'hip flexors'}


def predictions(df, cols, seeds):
    """(true, predicted, severity) for every condition x seed."""
    out = []
    subs = sorted(df.subj.unique())
    for sd in range(seeds):
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
                o = np.argsort(-P)
                out.append((t.mech.iloc[0], V.M[o[0]], int(t.sev.iloc[0]),
                            int(V.M.index(t.mech.iloc[0]) in o[:3])))
    return out


def main():
    out = open(os.path.join(HERE, 'clinical_breakdown.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    K1 = 'L1  camera (sagittal + timing)'
    for nz in LEVELS:
        df = V.build(n_rep=4, noise=nz, seed=0)
        for m in V.M:
            df[f'is_{m}'] = (df.mech == m).astype(int)
        pr = predictions(df, V.levels(df)[K1], NSEED)

        say('=' * 74)
        say(f'CAPTURE ERROR {nz:.0f} deg   (camera tier, {NSEED} seeds, leave-one-body-out)')
        say('=' * 74)

        # ---- confusion matrix, row-normalised: given the truth, what was said? ----------------
        say('')
        say('CONFUSION: rows = imposed weakness, columns = what the system said (%)')
        say(f'{"imposed":>16} | ' + ''.join(f'{m:>7}' for m in V.M) + f'{"  n":>6}')
        say(' ' * 17 + '+' + '-' * (7 * len(V.M) + 7))
        for t in V.M:
            rows = [p for p in pr if p[0] == t]
            n = len(rows)
            cells = []
            for c in V.M:
                pct = 100.0 * sum(1 for p in rows if p[1] == c) / n if n else 0
                cells.append(f'{pct:6.0f} ' if pct >= 0.5 else '     . ')
            say(f'{FULL[t]:>16} | ' + ''.join(cells) + f'{n:6}')

        # ---- where the confusion actually costs a clinician -----------------------------------
        say('')
        wrong = [(p[0], p[1]) for p in pr if p[0] != p[1]]
        if wrong:
            from collections import Counter
            cc = Counter(wrong).most_common(4)
            tot = len(pr)
            say('Most frequent misidentifications (share of all conditions):')
            for (t, c), k in cc:
                say(f'  {FULL[t]:>16} called {FULL[c]:<16} {100.0*k/tot:5.1f} %')

        # ---- accuracy by imposed severity -----------------------------------------------------
        say('')
        say('ACCURACY BY IMPOSED SEVERITY (the clinically decisive breakdown)')
        say(f'{"force loss":>12}{"top-1":>9}{"top-3":>9}{"n":>7}')
        for s in (20, 40, 60):
            rows = [p for p in pr if p[2] == s]
            if not rows:
                continue
            t1 = sum(1 for p in rows if p[0] == p[1]) / len(rows)
            t3 = sum(p[3] for p in rows) / len(rows)
            say(f'{s:11} %{t1:9.3f}{t3:9.3f}{len(rows):7}')
        say('  baselines: majority-class top-1 0.227 / top-3 0.667')  # 15/66, 44/66 on the frozen set
        say('')

    say('READING GUIDE')
    say('  If accuracy at 20 % force loss is near baseline, the aggregate number is carried by the')
    say('  severe cells and the method does not address the case where it would change management.')
    say('  If the confusion matrix is concentrated in one or two off-diagonal cells, those specific')
    say('  substitutions - not the aggregate - are what a clinician must be warned about.')
    out.close()


if __name__ == '__main__':
    main()
