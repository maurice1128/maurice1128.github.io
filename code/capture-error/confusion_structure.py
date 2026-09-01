"""Is the classifier reading a biomechanical deviation, or a simulation fingerprint?

The strongest objection to an in-silico identification study is circularity: the pipeline may be
recovering whatever was injected through some artefact of the simulator, rather than through the
deviation a clinician would read. The objection is usually treated as unanswerable. It is not
entirely, because it has testable consequences.

If the classifier were reading an arbitrary fingerprint, the pattern of its mistakes would carry no
structure that survives perturbation: the confusion matrix at one capture-error level would not
predict the matrix at another, because a fingerprint is either present or destroyed, not gracefully
degraded. If instead it is reading a graded physical deviation, then the groups that are confused
are the groups whose deviations resemble each other, and that resemblance is a property of the
mechanics rather than of the noise level - so the confusion structure should persist as accuracy
falls.

This measures the persistence directly, against a permutation null.

Run:  python confusion_structure.py
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
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = (2.0, 5.0, 8.0, 12.0)
NSEED = 6
RNG = np.random.default_rng(0)


def confusion(nz):
    """Row-normalised confusion over the five groups, leave-one-body-out."""
    df = V.build(n_rep=4, noise=nz, seed=0)
    for m in V.M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    cols = V.levels(df)['L1  camera (sagittal + timing)']
    C = np.zeros((len(V.M), len(V.M)))
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
                C[V.M.index(tt.mech.iloc[0]), int(np.argsort(-P)[0])] += 1
    row = C.sum(1, keepdims=True)
    return np.divide(C, row, out=np.zeros_like(C), where=row > 0)


def offdiag(C):
    return np.array([C[i, j] for i in range(C.shape[0]) for j in range(C.shape[1]) if i != j])


def main():
    out = open(os.path.join(HERE, 'confusion_structure.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True)
        out.write(m + '\n')
        out.flush()

    say('=== DOES THE CONFUSION STRUCTURE PERSIST AS ACCURACY FALLS? ===')
    say('A simulation fingerprint would be present or destroyed. A graded physical deviation')
    say('produces confusions between groups whose deviations resemble each other, and that')
    say('resemblance is a property of the mechanics, so it should survive added error.')
    say('')

    mats = {}
    for nz in LEVELS:
        mats[nz] = confusion(nz)
        say(f'--- {nz:.0f} deg, rows = imposed, columns = predicted ---')
        say('        ' + ''.join(f'{x:>8}' for x in V.M))
        for i, mech in enumerate(V.M):
            say(f'  {mech:5} ' + ''.join(f'{mats[nz][i, j]:8.2f}' for j in range(len(V.M))))
        say('')

    say('=== PERSISTENCE OF THE OFF-DIAGONAL PATTERN ===')
    say('Spearman correlation between the off-diagonal cells of two error levels.')
    say('The null is the same correlation after independently permuting one matrix.')
    say('')
    base = offdiag(mats[LEVELS[0]])
    say(f'  {"comparison":18}{"rho":>8}{"p":>9}{"null rho (95th pct)":>22}')
    for nz in LEVELS[1:]:
        v = offdiag(mats[nz])
        r, p = spearmanr(base, v)
        null = []
        for _ in range(2000):
            null.append(spearmanr(base, RNG.permutation(v))[0])
        null = np.array(null)
        say(f'  2 deg vs {nz:4.0f} deg{r:8.3f}{p:9.4f}{np.nanpercentile(null, 95):22.3f}')

    say('')
    say('READING: if the observed correlations sit well above the permutation null, the pattern')
    say('of mistakes is a stable property of the mechanics rather than an artefact that appears')
    say('and disappears with the noise level. That does not remove the circularity objection -')
    say('only patient data can - but it does discriminate between the two explanations that')
    say('objection conflates.')
    out.close()


if __name__ == '__main__':
    main()
