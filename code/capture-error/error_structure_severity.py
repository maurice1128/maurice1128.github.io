"""Read-only: do the severity and muscle-group patterns survive the other error structures?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from joblib import Parallel, delayed
import error_structure as C
T, V = C.T, C.V
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.multioutput import MultiOutputClassifier


def cell(kind, s, seed):
    df = C.build(kind, s, seed)
    cols = V.levels(df)['L1  camera (sagittal + timing)']
    rows = []
    for sd in range(2):
        for ho in sorted(df.subj.unique()):
            tr, te = df[df.subj != ho], df[df.subj == ho]
            Y = tr[[f'is_{m}' for m in V.M]].to_numpy(int)
            mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                            ('clf', MultiOutputClassifier(ExtraTreesClassifier(100, random_state=sd, n_jobs=1, class_weight='balanced')))])
            mdl.fit(tr[cols].to_numpy(float), Y)
            for tag in te.tag.unique():
                t = te[te.tag == tag]
                P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t)) for p in mdl.predict_proba(t[cols].to_numpy(float))]).T.mean(0)
                o = np.argsort(-P); ti = V.M.index(t.mech.iloc[0])
                rows.append((kind, s, seed, sd, t.mech.iloc[0], int(t.sev.iloc[0]), int(o[0] == ti)))
    return rows


if __name__ == '__main__':
    cells = [(k, s, sd) for k in ('white', 'structured_matched', 'offset') for s in (2.0, 8.0) for sd in (0, 1, 2)]
    res = Parallel(n_jobs=6)(delayed(cell)(*c) for c in cells)
    d = pd.DataFrame([r for x in res for r in x], columns='kind s seed sd mech sev ok'.split())
    print(d.groupby(['kind', 's', 'sev']).ok.mean().unstack().round(3).to_string())
    print(d.groupby(['kind', 's', 'mech']).ok.mean().unstack().round(2).to_string())
