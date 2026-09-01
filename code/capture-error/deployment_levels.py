"""Value of information across CAPTURE HARDWARE (the paper's deployment question).

Which motion-capture setup is sufficient to identify WHICH muscle group is weak?

  L1  CAMERA      : sagittal joint kinematics of BOTH limbs + spatiotemporal measures
                    -> one phone filming from the side (a side view sees both legs), ~free
  L2  + FORCE PLATE : adds ground-reaction-force derived measures
                    -> instrumented gait lab, $10k-50k

  (A frontal-plane / 3D-markerless tier is NOT evaluable here: the H0914 model is planar, so all
   medio-lateral channels are identically zero. That tier needs the 3D H1922 model, which is a
   Hyfydy model and requires a paid licence. This limitation is stated, not hidden.)

Design rules applied after an internal audit:
  * L1 includes BOTH limbs and spatiotemporal features - a side-view camera sees both legs, so
    "paretic only" vs "+asymmetry" is a processing choice, not a hardware tier.
  * Force-plate features are FRAME-INVARIANT. World-frame CoP_x and the moment about the origin
    are dominated by how far the model walked (CoP_x range ~= distance travelled) and would leak
    gait quality / optimiser convergence into the label. They are excluded.
  * Measurement noise is applied to the raw kinematics before features are computed, so every
    level is evaluated under capture error (the point of a deployment study).
"""
import warnings; warnings.filterwarnings('ignore')
import glob, os, re, numpy as np, pandas as pd
import scone_ident as si

import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
M = si.MECHS
BW = 9.81 * 70.0   # approximate body weight (N) for normalising GRF; H0914 ~70 kg


def spatiotemporal(cols, d, s):
    """Phone-observable timing measures from foot contact (derived from vertical GRF onset/offset,
    which a camera cannot measure directly BUT which is equivalent to visible foot-contact timing)."""
    f = {}
    for side, leg in [('l', 'leg0_l'), ('r', 'leg1_r')]:
        i = [k for k, c in enumerate(cols) if c == f'{leg}.grf_norm_y']
        if not i:
            continue
        v = d[s:, i[0]]
        contact = v > 0.05                      # foot on the ground
        f[f'C::stance_frac_{side}'] = float(contact.mean())
        # step timing from contact onsets
        on = np.where(np.diff(contact.astype(int)) == 1)[0]
        t = d[s:, 0]
        if len(on) > 1:
            st = np.diff(t[on])
            f[f'C::step_time_{side}'] = float(np.median(st))
            f[f'C::step_time_cv_{side}'] = float(np.std(st) / (np.mean(st) + 1e-9))
    if 'C::stance_frac_l' in f and 'C::stance_frac_r' in f:
        f['C::stance_asym'] = f['C::stance_frac_l'] - f['C::stance_frac_r']
    if 'C::step_time_l' in f and 'C::step_time_r' in f:
        f['C::step_time_asym'] = f['C::step_time_l'] - f['C::step_time_r']
    # walking speed (visible to a camera with a known scale)
    px = [k for k, c in enumerate(cols) if c == 'pelvis.com_pos_x']
    if px:
        x = d[s:, px[0]]; t = d[s:, 0]
        f['C::speed'] = float((x[-1] - x[0]) / (t[-1] - t[0] + 1e-9))
    return f


def grf_features(cols, d, s):
    """Frame-invariant force-plate measures (normalised to body weight, no world-frame terms)."""
    f = {}
    got = {}
    for side, leg in [('l', 'leg0_l'), ('r', 'leg1_r')]:
        iy = [k for k, c in enumerate(cols) if c == f'{leg}.grf_y']
        ix = [k for k, c in enumerate(cols) if c == f'{leg}.grf_x']
        if not iy or not ix:
            continue
        fy = d[s:, iy[0]] / BW      # vertical, body weights
        fx = d[s:, ix[0]] / BW      # fore-aft shear, body weights
        t = d[s:, 0]
        dt = float(np.median(np.diff(t)))
        stance = fy > 0.05
        f[f'G::vgrf_peak_{side}'] = float(np.max(fy))
        f[f'G::vgrf_mean_{side}'] = float(fy[stance].mean()) if stance.any() else 0.0
        # braking (negative fore-aft) and propulsive (positive) impulses, BW*s
        f[f'G::brake_imp_{side}'] = float(np.sum(np.clip(fx, None, 0)) * dt)
        f[f'G::prop_imp_{side}'] = float(np.sum(np.clip(fx, 0, None)) * dt)
        f[f'G::fx_peak_{side}'] = float(np.max(fx))
        f[f'G::fx_min_{side}'] = float(np.min(fx))
        # loading rate: max rise of vertical force
        f[f'G::load_rate_{side}'] = float(np.max(np.diff(fy)) / dt) if len(fy) > 1 else 0.0
        got[side] = True
    if got.get('l') and got.get('r'):
        for k in ['vgrf_peak', 'vgrf_mean', 'brake_imp', 'prop_imp', 'fx_peak', 'fx_min', 'load_rate']:
            f[f'G::{k}_asym'] = f[f'G::{k}_l'] - f[f'G::{k}_r']
    return f


def dataset(n_rep=6, noise=2.0, seed=0, accepted=None):
    rng = np.random.default_rng(seed)
    rows = []
    for folder in sorted(glob.glob(os.path.join(RES, '*.I'))):
        tag = os.path.basename(folder).split('.')[0]
        m = re.match(r'^(s\d)?(PF|DF|KE|KF|HF)(\d+)L$', tag)
        if not m:
            continue
        if accepted is not None and tag not in accepted:
            continue
        stos = glob.glob(os.path.join(folder, 'qc.sto*'))
        if not stos:
            continue
        sto = stos[0]
        try:
            cols, d = si.load_sto(sto)
        except Exception:
            continue
        s = int(len(d) * 0.4)
        st = spatiotemporal(cols, d, s)
        gr = grf_features(cols, d, s)
        for _ in range(n_rep):
            f = si.feats(sto, rng, noise)     # noise now reaches ROM/min/max too
            f.update(st); f.update(gr)
            f['mech'] = m.group(2); f['sev'] = int(m.group(3))
            f['subj'] = m.group(1) or 'base'; f['tag'] = tag
            rows.append(f)
    return pd.DataFrame(rows)


def levels(df):
    S = [c for c in df.columns if c.startswith('S::') and '_p' not in c]
    A = [c for c in df.columns if c.startswith('A::') and '_p' not in c]
    C = [c for c in df.columns if c.startswith('C::')]
    G = [c for c in df.columns if c.startswith('G::')]
    return {
        'L1  sagittal camera (both limbs + timing)': S + A + C,
        'L2  camera + FORCE PLATE': S + A + C + G,
        '     [kinematics only, no timing]': S + A,
        '     [force plate alone]': G,
    }


if __name__ == '__main__':
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.multioutput import MultiOutputClassifier

    acc = None
    qa = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qc_accepted.txt')
    if os.path.exists(qa):
        acc = set(open(qa).read().split())
    df = dataset(n_rep=6, noise=2.0, seed=0, accepted=acc)
    print(f'QC-accepted conditions used: {df.tag.nunique()}   subjects={sorted(df.subj.unique())}')
    print(df.groupby(["subj","sev"]).tag.nunique().unstack(fill_value=0), flush=True)
    for m in M:
        df[f'is_{m}'] = (df.mech == m).astype(int)
    subs = sorted(df.subj.unique())

    def loso(cols, seeds=3):
        t1s, t3s, per = [], [], {}
        for sd in range(seeds):
            c1 = c3 = n = 0
            for ho in subs:
                tr, te = df[df.subj != ho], df[df.subj == ho]
                if not len(tr) or not len(te):
                    continue
                Y = tr[[f'is_{m}' for m in M]].to_numpy(int)
                mdl = Pipeline([('imp', SimpleImputer(strategy='median')),
                                ('clf', MultiOutputClassifier(ExtraTreesClassifier(200, random_state=sd, n_jobs=3, class_weight='balanced')))])
                mdl.fit(tr[cols].to_numpy(float), Y)
                for tag in te.tag.unique():
                    t = te[te.tag == tag]
                    P = np.array([p[:, 1] if p.shape[1] == 2 else np.zeros(len(t)) for p in mdl.predict_proba(t[cols].to_numpy(float))]).T.mean(0)
                    o = np.argsort(-P); ti = M.index(t.mech.iloc[0]); sev = int(t.sev.iloc[0]); n += 1
                    h1 = int(o[0] == ti); h3 = int(ti in o[:3]); c1 += h1; c3 += h3
                    per.setdefault(sev, [0, 0, 0]); per[sev][0] += h1; per[sev][1] += h3; per[sev][2] += 1
            if n: t1s.append(c1/n); t3s.append(c3/n)
        return (np.mean(t1s), np.std(t1s), np.mean(t3s), per) if t1s else (0,0,0,{})

    print('\n=== VALUE OF INFORMATION BY CAPTURE HARDWARE (cross-subject LOSO, 2 deg capture noise) ===')
    print(f'{"capture level":45}{"n_feat":>7}{"top-1":>9}{"top-3":>8}')
    res = {}
    for name, cols in levels(df).items():
        if not cols: continue
        t1, sd, t3, per = loso(cols)
        res[name] = (t1, t3, per)
        print(f'{name:45}{len(cols):7}{t1:8.3f}±{sd:.2f}{t3:8.3f}', flush=True)
    print(f'  (chance top-1 0.20 / top-3 0.60)')

    k1 = 'L1  sagittal camera (both limbs + timing)'; k2 = 'L2  camera + FORCE PLATE'
    if k1 in res and k2 in res:
        print(f'\n=== IS THE FORCE PLATE WORTH IT? ===')
        print(f'  camera alone   : top-1 {res[k1][0]:.3f}  top-3 {res[k1][1]:.3f}')
        print(f'  camera + plate : top-1 {res[k2][0]:.3f}  top-3 {res[k2][1]:.3f}')
        print(f'  VALUE OF PLATE : top-1 {res[k2][0]-res[k1][0]:+.3f}  top-3 {res[k2][1]-res[k1][1]:+.3f}')

    print('\n=== per severity ===')
    for name, (t1, t3, per) in res.items():
        if not per: continue
        cells = '  '.join(f'{s}%:{v[0]/v[2]:.2f}' for s, v in sorted(per.items()) if v[2])
        print(f'  {name:45} {cells}')
