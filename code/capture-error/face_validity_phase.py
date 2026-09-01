"""Face validity measured in the gait phase each mechanism actually belongs to.

`face_validity_all.py` took every extremum over the whole analysis window. That is the wrong
window for four of the six checks, and the error is not conservative:

  foot drop            is a SWING event. The whole-cycle maximum of ankle angle is usually
                       mid-stance tibial progression, which has nothing to do with the swing
                       clearance the dorsiflexors produce.
  quadriceps yield     is a LOADING-RESPONSE event. The whole-cycle knee minimum is peak swing
                       flexion, which is a different mechanism.
  genu recurvatum      is a TERMINAL-STANCE event.
  push-off             is a TERMINAL-STANCE event; the whole-cycle ankle minimum can also be the
                       small plantarflexion just after initial contact.

Phases are segmented per limb from the vertical ground reaction force (leg*.grf_norm_y > 0.05 body
weights). Each check is then evaluated only inside its own phase, against two references:

  vs non-paretic   the contralateral limb in the same trial (what Table 1 prints)
  vs own healthy   the same body's unimpaired solution, i.e. did the weakened limb itself move

Run:  python face_validity_phase.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, re, glob, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
LEG = {'l': 'leg0_l', 'r': 'leg1_r'}


def read_sto(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        for ln in f:
            if ln.strip().lower() == 'endheader':
                break
        cols = f.readline().split()
        d = np.array([[float(x) for x in ln.split()] for ln in f if ln.strip()])
    return cols, d


def deg(v):
    return np.degrees(v) if np.abs(v).max() < 7 else v


def phase_stats(path):
    """{(joint, side, phase): (min, max)} where phase is one of stance / swing / early / late.

    early = first 40 % of each stance, late = last 40 % of each stance. Statistics are taken per
    stride and then averaged, so a single outlier stride cannot set the value.
    """
    cols, d = read_sto(path)
    s = int(len(d) * 0.4)
    out = {}
    for side in ('l', 'r'):
        gy = None
        for nm in (f'{LEG[side]}.grf_norm_y', f'{LEG[side]}.grf_y'):
            if nm in cols:
                gy = d[s:, cols.index(nm)]
                break
        if gy is None:
            continue
        contact = gy > 0.05
        on = np.where(np.diff(contact.astype(int)) == 1)[0] + 1
        off = np.where(np.diff(contact.astype(int)) == -1)[0] + 1
        if len(on) < 2 or len(off) < 1:
            continue
        strides = []                                     # (stance slice, swing slice)
        for i in range(len(on) - 1):
            o = off[(off > on[i]) & (off < on[i + 1])]
            if len(o):
                strides.append((slice(on[i], o[0]), slice(o[0], on[i + 1])))
        if not strides:
            continue
        for jn, key in (('hip', 'hip_flexion'), ('knee', 'knee_angle'), ('ankle', 'ankle_angle')):
            c = f'/jointset/{jn}_{side}/{key}_{side}/value'
            if c not in cols:
                continue
            v = deg(d[s:, cols.index(c)])
            acc = {}
            for st, sw in strides:
                n = st.stop - st.start
                if n < 4 or sw.stop - sw.start < 3:
                    continue
                seg = {'stance': v[st], 'swing': v[sw],
                       'early': v[st.start:st.start + max(2, int(n * 0.4))],
                       'late': v[st.stop - max(2, int(n * 0.4)):st.stop]}
                for ph, w in seg.items():
                    acc.setdefault(ph, []).append((w.min(), w.max()))
            for ph, lst in acc.items():
                a = np.array(lst)
                out[(jn, side, ph)] = (float(a[:, 0].mean()), float(a[:, 1].mean()))
    return out


def healthy_for(body):
    pat = 'HEALTHY.H0914M*.I' if body == 'base' else f'HEALTHY_{body}.*'
    for d in glob.glob(os.path.join(RES, pat)):
        for f in ('hq.sto.sto', 'qc.sto.sto'):
            p = os.path.join(d, f)
            if os.path.exists(p):
                return phase_stats(p)
        s = glob.glob(os.path.join(d, '*.sto'))
        if s:
            return phase_stats(s[0])
    return None


# (label, joint, phase, statistic, expected direction on the paretic side, clinical anchor)
CHECK = {
    'HF': [('peak swing hip flexion reduced', 'hip', 'swing', 'max', 'lower', 'Carmo 2012')],
    # The naive expectation - the knee yields further under load - is NOT what vasti weakness does
    # here, and van der Krogt 2012 already reported that vasti tolerate ~80 % weakening with normal
    # kinematics. The two directions that are consistent are the ones the vasti actually control:
    # eccentric restraint of early-swing knee flexion, and knee extension in terminal stance.
    'KE': [('greater peak swing knee flexion', 'knee', 'swing', 'min', 'lower',
            'van der Krogt 2012 predicts loading response is spared'),
           ('reduced terminal-stance knee extension', 'knee', 'late', 'max', 'lower',
            'flexed-knee gait, Chen 2005'),
           ('knee yields further in loading response (NOT supported)', 'knee', 'early', 'min',
            'lower', 'naive expectation, reported as refuted')],
    'PF': [('peak plantarflexion at push-off reduced', 'ankle', 'late', 'min', 'higher',
            'Kesar 2009')],
    'DF': [('peak swing dorsiflexion reduced (foot drop)', 'ankle', 'swing', 'max', 'lower',
            'Szopa 2017')],
    'KF': [('genu recurvatum in terminal stance', 'knee', 'late', 'max', 'higher',
            'contested: Okada 2024 vs Cooper 2012'),
           ('peak swing knee flexion little changed', 'knee', 'swing', 'min', 'same',
            'Kerrigan 1991; Manikowska 2022')],
}
IDX = {'min': 0, 'max': 1}


def main():
    out = open(os.path.join(HERE, 'face_validity_phase.txt'), 'w', encoding='utf-8')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    acc = open(os.path.join(HERE, 'qc_accepted.txt')).read().split()
    HC, table = {}, []
    say('=== FACE VALIDITY, MEASURED IN THE CORRECT GAIT PHASE ===')
    say('Phases segmented per limb from vertical GRF. "early"/"late" are the first/last 40 % of')
    say('stance. Compare with face_validity_all.txt, which used whole-cycle extrema.')
    say('')
    for mech, checks in CHECK.items():
        tags = [t for t in acc if re.match(r'^(s\d)?%s\d+L$' % mech, t)]
        for label, jn, ph, stat, want, anchor in checks:
            rows = []
            for t in sorted(tags):
                body = re.match(r'^(s\d)?', t).group(1) or 'base'
                ds = [d for d in glob.glob(os.path.join(RES, t + '.*')) if d.endswith('.I')]
                p = os.path.join(ds[0], 'qc.sto.sto') if ds else None
                if not p or not os.path.exists(p):
                    continue
                A = phase_stats(p)
                if (jn, 'l', ph) not in A or (jn, 'r', ph) not in A:
                    continue
                lv, rv = A[(jn, 'l', ph)][IDX[stat]], A[(jn, 'r', ph)][IDX[stat]]
                if body not in HC:
                    HC[body] = healthy_for(body)
                H = HC.get(body)
                hv = H[(jn, 'l', ph)][IDX[stat]] if H and (jn, 'l', ph) in H else None

                def ok(a, b):
                    if want == 'lower':
                        return a < b
                    if want == 'higher':
                        return a > b
                    return abs(a - b) < 5.0

                rows.append((int(re.search(r'(\d+)L$', t).group(1)),
                             ok(lv, rv), (ok(lv, hv) if hv is not None else None),
                             lv - rv, (lv - hv) if hv is not None else np.nan))
            if not rows:
                continue
            n = len(rows)
            vsn = sum(1 for r in rows if r[1])
            hn = sum(1 for r in rows if r[2] is not None)
            vsh = sum(1 for r in rows if r[2])
            bysev = {s: (sum(1 for r in rows if r[0] == s and r[1]),
                         sum(1 for r in rows if r[0] == s)) for s in (20, 40, 60)}
            sev = '  '.join(f'{s}%:{a}/{b}' for s, (a, b) in bysev.items() if b)
            dn = np.nanmean([r[3] for r in rows])
            dh = np.nanmean([r[4] for r in rows])
            say(f'  {mech}  {label}   [{anchor}]')
            say(f'       vs non-paretic {vsn:2}/{n:2} (mean diff {dn:+6.1f} deg)   '
                f'vs own healthy {vsh:2}/{hn:2} (mean diff {dh:+6.1f} deg)')
            say(f'       by severity: {sev}')
            table.append((mech, label, vsn, n, vsh, hn))
    say('')
    say('--- summary for Table 1 ---')
    for mech, label, vsn, n, vsh, hn in table:
        v = 'holds' if vsn / n >= 0.8 and vsh / max(hn, 1) >= 0.8 else (
            'partial' if vsn / n >= 0.8 else 'does not generalise')
        say(f'  {mech:3} {label:46} {vsn:2}/{n:2}  {vsh:2}/{hn:2}   {v}')
    out.close()


if __name__ == '__main__':
    main()
