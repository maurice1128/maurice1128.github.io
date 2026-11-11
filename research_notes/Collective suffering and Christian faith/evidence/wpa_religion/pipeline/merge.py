"""Merge coding batches into data.csv: derive categories, verify verbatim snippets against the
Gutenberg text, attach locators (eBook no., volume, informant, line numbers), and code interviewer race
by documented rules. Usage: python3 -I merge.py WORK_DIR OUT_CSV [codes_subdir]

NOTE (2026-11-11): the interviewer, interviewer_race and interviewer_race_source columns of the
published data.csv were corrected by hand after this script ran (codebook.md section 8,
interviewer_race_corrections.md, interviewer_name_corrections.csv). This script reads the coder's
"iv" field and scans the first 45 and last 20 lines of a segment, so it does not apply the rules for
two interviewers, appended interviews or surname-only credits. Re-running it would undo those
corrections; re-apply interviewer_name_corrections.csv afterwards. """
import re, sys, os, json, csv, glob

BLACK_NAMES = {  # documented Black interviewers / Negro-unit members (see codebook §8)
    'samuel s. taylor': 'Encyclopedia of Arkansas, "WPA Slave Narratives"',
    's. s. taylor': 'Encyclopedia of Arkansas, "WPA Slave Narratives"',
    's.s. taylor': 'Encyclopedia of Arkansas, "WPA Slave Narratives"',
    'pernella': 'in-text "colored"; Encyclopedia of Arkansas',
    'levi d. shelby': 'in-text "(Colored)" after his name, Vol. I header of W.E. Northcross',
    'minnie b. ross': 'Notable Folklorists of Color, Negro Units (GA)',
    'ross]': 'GA handwritten signature "Ross" = Minnie B. Ross (AccessGenealogy index lists her for Hannah Austin); Notable Folklorists of Color (GA)',
    'adella s. dixon': 'in-text [HW: (Colored)]; Notable Folklorists of Color (GA)',
    'ardella s. dixon': 'Notable Folklorists of Color (GA)',
    'edwin driskell': 'Notable Folklorists of Color (GA)',
    'louise oliphant': 'Notable Folklorists of Color (GA)',
    'willie h. cole': 'Notable Folklorists of Color (GA)',
    'augustus ladson': 'Notable Folklorists of Color (SC)',
    'augusta ladson': 'Notable Folklorists of Color (SC)',
    'laura lee middleton': 'Notable Folklorists of Color (SC)',
    'susie byrd': 'Notable Folklorists of Color (VA Negro Studies Project)',
    'susie r. c. byrd': 'Notable Folklorists of Color (VA)',
    'claude w. anderson': 'Notable Folklorists of Color (VA)',
    'claude anderson': 'Notable Folklorists of Color (VA)',
    'thelma dunston': 'Notable Folklorists of Color (VA)',
    'david hoggard': 'Notable Folklorists of Color (VA)',
    'pearl randolph': 'Notable Folklorists of Color (FL Negro unit)',
    'rachel a. austin': 'Notable Folklorists of Color (FL)',
    'rachel austin': 'Notable Folklorists of Color (FL)',
    'viola b. muse': 'Notable Folklorists of Color (FL)',
    'viola muse': 'Notable Folklorists of Color (FL)',
    'martin richardson': 'Notable Folklorists of Color (FL)',
    'martin d. richardson': 'Notable Folklorists of Color (FL)',
    'alfred farrell': 'Notable Folklorists of Color (FL)',
    'j. m. johnson': 'Notable Folklorists of Color (FL, "James Johnson")',
    'james johnson': 'Notable Folklorists of Color (FL)',
    'samuel johnson': 'Notable Folklorists of Color (FL)',
    'zora neale hurston': 'Notable Folklorists of Color (FL)',
}
WHITE_NAMES = {'sadie b. hornsby': 'in-text [HW: (White)]', 'grace mccune': 'in-text [HW: (White)]'}

def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('[...]', ' ')
    return re.sub(r'\s+', ' ', s).strip().lower()

def find_line(seg, snip):
    """Return absolute line number where snippet (or its first part before [...]) begins, else None."""
    parts = [p for p in snip.split('[...]') if p.strip()]
    lines = seg['text'].split('\n')
    flat, idx = '', []
    for i, l in enumerate(lines):
        t = norm(l)
        if not t: continue
        if flat: flat += ' '
        idx.append((len(flat), i)); flat += t
    ok = True; first = None
    for p in parts:
        q = norm(p)
        pos = flat.find(q)
        if pos < 0: ok = False; continue
        ln = max(i for (o, i) in idx if o <= pos)
        if first is None: first = ln
    return ok, (seg['start_line'] + first) if first is not None else None

def trailing_hw(lines):
    """Index where a trailing handwritten header block (e.g. '[HW: Dist. 5 / Ex Slave #1 / Ross]')
    begins; such blocks precede the NEXT narrative's title in the Georgia volumes."""
    idx = [i for i, l in enumerate(lines) if l.strip()]
    for i in idx[-8:]:
        if lines[i].strip().startswith('[HW:'):
            rest = [lines[j].strip() for j in idx if j >= i]
            if all(len(r) < 60 and not r.startswith('"') for r in rest):
                return i
    return len(lines)

PREV = {}

def race_in_zone(zone):
    zl = zone.lower()
    if re.search(r"negro writers'? unit|negro unit", zl):
        return 'Black', 'in-text: (Negro Writers\' Unit)'
    if re.search(r'interviewer[^\n]*\b(colored|negro)\b|\[hw:\s*\(colored\)\]', zl):
        return 'Black', 'in-text: interviewer marked colored'
    for n, src in BLACK_NAMES.items():
        if n in zl: return 'Black', f'{n}: {src}'
    if re.search(r'\[hw:\s*\(white\)\]', zl):
        return 'white', 'in-text: [HW: (White)]'
    for n, src in WHITE_NAMES.items():
        if n in zl: return 'white', f'{n}: {src}'
    return None


def interviewer_race(seg):
    L = seg['text'].split('\n')
    cut = len(L)  # GA handwritten signatures ('[HW: Dist. 5 / Ex Slave #1 / Ross]') belong to the narrative they follow
    pre = []
    for zone in ('\n'.join(pre + L[:45]), '\n'.join(L[:cut][-20:])):
        r = race_in_zone(zone)
        if r: return r
    return 'unknown', ''

def derive_wc(flags):
    f = set(flags)
    if not f: return 'not_stated'
    if f == {'S', 'F'}: return 'secret'
    if len(f) == 1:
        return {'W': 'white_supervised', 'B': 'black_led_permitted', 'S': 'secret', 'F': 'forbidden'}[f.pop()]
    return 'mixed'

def file_offsets(raw):
    """lines preceding the first content line (i.e. through the '*** START' line) in each raw file"""
    off = {}
    for fn in glob.glob(os.path.join(raw, 'pg*.txt')):
        txt = open(fn, encoding='utf-8', errors='replace').read().replace('\r', '')
        i = txt.find('*** START OF')
        off[os.path.basename(fn)[2:-4]] = txt[:txt.find('\n', i) + 1].count('\n') if i >= 0 else 0
    return off

def main(work, out_csv, sub='codes'):
    OFF = file_offsets(os.path.join(work, '..', 'raw'))
    segs = {}
    for l in open(os.path.join(work, 'segments.jsonl')):
        r = json.loads(l); segs[r['nid']] = r
    sample = {r['nid']: r for r in csv.DictReader(open(os.path.join(work, 'sample.csv')))}
    byend = {(r['pg_id'], r['end_line']): r for r in segs.values()}
    for r in segs.values():
        p = byend.get((r['pg_id'], r['start_line']))
        if p and r['state'] == 'GA':
            PL = p['text'].split('\n')
            PREV[r['nid']] = PL[trailing_hw(PL):]
    recs = []
    for fn in sorted(glob.glob(os.path.join(work, sub, 'batch_*.jsonl'))):
        for l in open(fn):
            if l.strip(): recs.append(json.loads(l))
    seen = set(); rows = []; problems = []
    for c in recs:
        nid = c['nid']
        if nid in seen: problems.append(f'duplicate {nid}'); continue
        seen.add(nid)
        seg = segs[nid]; smp = sample.get(nid, {})
        flags = [x for x in c.get('wc', '') if x in 'WBSF']
        wc = derive_wc(flags)
        bc = 'ns' if not flags else ('y' if ('B' in flags or 'S' in flags) else 'n')
        race, rsrc = interviewer_race(seg)
        row = {'nid': nid, 'code_order': smp.get('code_order', ''), 'state': seg['state'], 'volume': seg['volume'],
               'gutenberg_ebook': seg['pg_id'], 'informant': seg['toc_name'],
               'segment_lines': f"{seg['start_line'] + OFF[seg['pg_id']]}-{seg['end_line'] + OFF[seg['pg_id']]}",
               'interviewer': c.get('iv', ''), 'interviewer_race': race, 'interviewer_race_source': rsrc,
               'age_1937': c.get('age', ''), 'hearsay_only': c.get('hs', 'n'),
               'wc_white': 'y' if 'W' in flags else 'n', 'wc_blackled': 'y' if 'B' in flags else 'n',
               'wc_secret': 'y' if 'S' in flags else 'n', 'wc_forbidden': 'y' if 'F' in flags else 'n',
               'worship_control': wc, 'black_control_pre1865': bc,
               'obedience_preaching': c.get('obed', 'ns'), 'attitude_white_preachers': c.get('att', 'ns'),
               'conversion_timing': c.get('conv', 'ns'), 'faith_commitment_before_freedom': c.get('faith', 'ns'),
               'faith_subject': c.get('fsub', 'ns'), 'postwar_church_any': c.get('pany', 'ns'),
               'postwar_black_church': c.get('post', 'ns'), 'prayed_for_freedom': c.get('free', 'ns'),
               'notes': c.get('notes', '')}
        sn = c.get('s', {})
        for k in ['wc', 'obed', 'att', 'conv', 'faith', 'post', 'free']:
            s = sn.get(k, '')
            row[f'snip_{k}'] = s
            if s:
                ok, ln = find_line(seg, s)
                row[f'loc_{k}'] = f"pg{seg['pg_id']}.txt line {ln + OFF[seg['pg_id']]}; vol. {seg['volume']}, \"{seg['toc_name']}\"" if ln else ''
                if not ok: problems.append(f'{nid} snippet {k} not verbatim: {s[:80]}')
            else:
                row[f'loc_{k}'] = ''
        # consistency checks: non-ns code requires snippet
        need = {'wc': wc != 'not_stated', 'obed': row['obedience_preaching'] != 'ns',
                'att': row['attitude_white_preachers'] != 'ns', 'conv': row['conversion_timing'] != 'ns',
                'faith': row['faith_commitment_before_freedom'] != 'ns',
                'post': row['postwar_black_church'] != 'ns' or row['postwar_church_any'] != 'ns',
                'free': row['prayed_for_freedom'] != 'ns'}
        for k, v in need.items():
            if v and not sn.get(k): problems.append(f'{nid} missing snippet for {k}')
        rows.append(row)
    rows.sort(key=lambda r: int(r['code_order']) if r['code_order'] else 9999)
    if rows:
        with open(out_csv, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f'rows: {len(rows)}; problems: {len(problems)}')
    for p in problems: print('  ', p)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'codes')
