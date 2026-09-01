"""Does each face-validity direction hold across ALL conditions, or only in the one we printed?

Table 1 of the manuscript prints one exemplar condition per mechanism, chosen by a mechanical rule
(base body, highest severity available), and §3.1 then says "all six deviations are in the expected
direction". An audit found that for plantarflexors the printed direction holds in a minority of the
fifteen PF conditions, and that the exemplar is one of the minority that agree.

This recomputes every check over every condition, and against two references:

  vs non-paretic   the contrast Table 1 actually prints
  vs own healthy   the contrast the mechanism is about - did the weakness change this limb at all,
                   compared with the same body's unimpaired solution

A direction that holds against the contralateral limb but not against the body's own healthy gait
means the asymmetry is a non-paretic-side effect, which is not what the clinical literature cited in
S1 describes.

Run:  python face_validity_all.py
"""
import warnings; warnings.filterwarnings('ignore')
import os, re, glob, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import os as _os
_FROZEN = r'C:\Users\maurice\Desktop\stroke_scone\results_frozen'
RES = _FROZEN if _os.path.isdir(_FROZEN) else r'C:\Users\maurice\Documents\SCONE\results'
JOINT = {'hip': 'hip_flexion', 'knee': 'knee_angle', 'ankle': 'ankle_angle'}


def read_sto(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        for ln in f:
            if ln.strip().lower() == 'endheader':
                break
        cols = f.readline().split()
        d = np.array([[float(x) for x in ln.split()] for ln in f if ln.strip()])
    return cols, d


def angles(path):
    """min / max / ROM per joint per side on the analysis window (last 60 %)."""
    cols, d = read_sto(path)
    s = int(len(d) * 0.4)
    out = {}
    for jn, key in JOINT.items():
        for side in ('l', 'r'):
            c = f'/jointset/{ "hip" if jn=="hip" else jn }_{side}/{key}_{side}/value'
            if c not in cols:
                continue
            v = d[s:, cols.index(c)]
            if np.abs(v).max() < 7:
                v = np.degrees(v)
            out[(jn, side)] = (float(v.min()), float(v.max()), float(np.ptp(v)))
    return out


def healthy_for(body):
    pat = 'HEALTHY.H0914M*.I' if body == 'base' else f'HEALTHY_{body}.*'
    for d in glob.glob(os.path.join(RES, pat)):
        for f in ('hq.sto.sto', 'qc.sto.sto'):
            p = os.path.join(d, f)
            if os.path.exists(p):
                return angles(p)
        s = glob.glob(os.path.join(d, '*.sto'))
        if s:
            return angles(s[0])
    return None


# (label, joint, which statistic, direction expected on the paretic side)
CHECK = {
    'PF': [('ankle excursion falls', 'ankle', 'rom', 'lower'),
           ('peak plantarflexion reduced', 'ankle', 'min', 'higher')],
    'DF': [('peak dorsiflexion reduced', 'ankle', 'max', 'lower')],
    'KE': [('knee flexes further under load', 'knee', 'min', 'lower')],
    'KF': [('knee hyperextends', 'knee', 'max', 'higher'),
           ('swing flexion little changed', 'knee', 'min', 'same')],
    'HF': [('peak hip flexion reduced', 'hip', 'max', 'lower')],
}
IDX = {'min': 0, 'max': 1, 'rom': 2}


def main():
    out = open(os.path.join(HERE, 'face_validity_all.txt'), 'w')

    def say(m):
        print(m, flush=True); out.write(m + '\n'); out.flush()

    acc = open(os.path.join(HERE, 'qc_accepted.txt')).read().split()
    HC = {}
    say('=== DOES EACH FACE-VALIDITY DIRECTION HOLD ACROSS ALL CONDITIONS? ===')
    say('"vs non-paretic" is the contrast Table 1 prints. "vs own healthy" asks whether the weakness')
    say('changed the paretic limb at all, against the same body\'s unimpaired solution.')
    say('')
    for mech, checks in CHECK.items():
        tags = [t for t in acc if re.match(r'^(s\d)?%s\d+L$' % mech, t)]
        for label, jn, stat, want in checks:
            rows = []
            for t in sorted(tags):
                body = (re.match(r'^(s\d)?', t).group(1) or 'base')
                ds = [d for d in glob.glob(os.path.join(RES, t + '.*')) if d.endswith('.I')]
                p = os.path.join(ds[0], 'qc.sto.sto') if ds else None
                if not p or not os.path.exists(p):
                    continue
                A = angles(p)
                if (jn, 'l') not in A:
                    continue
                lv, rv = A[(jn, 'l')][IDX[stat]], A[(jn, 'r')][IDX[stat]]
                if body not in HC:
                    HC[body] = healthy_for(body)
                hv = HC[body][(jn, 'l')][IDX[stat]] if HC.get(body) else None
                def ok(a, b):
                    if want == 'lower':  return a < b
                    if want == 'higher': return a > b
                    return abs(a - b) < 5.0
                rows.append((int(re.search(r'(\d+)L$', t).group(1)),
                             ok(lv, rv), ok(lv, hv) if hv is not None else None))
            if not rows:
                continue
            n = len(rows)
            vsn = sum(1 for _, a, _ in rows if a)
            vsh = sum(1 for _, _, b in rows if b)
            hn = sum(1 for _, _, b in rows if b is not None)
            bysev = {s: (sum(1 for x, a, _ in rows if x == s and a),
                         sum(1 for x, _, _ in rows if x == s)) for s in (20, 40, 60)}
            sev = '  '.join(f'{s}%:{a}/{b}' for s, (a, b) in bysev.items() if b)
            say(f'  {mech}  {label}')
            say(f'       vs non-paretic {vsn:2}/{n:2}   vs own healthy {vsh:2}/{hn:2}   [{sev}]')
    say('')
    say('READING: a row that holds in a minority cannot be reported as "the simulated deviation",')
    say('and a row that holds against the contralateral limb but not against the body\'s own healthy')
    say('gait is a non-paretic-side effect, not the mechanism the cited literature describes.')
    out.close()


if __name__ == '__main__':
    main()
