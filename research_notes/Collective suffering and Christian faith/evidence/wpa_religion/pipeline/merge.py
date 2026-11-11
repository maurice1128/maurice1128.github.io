"""Merge coding batches into data.csv: derive categories, verify verbatim snippets against the
Gutenberg text, attach locators (eBook no., volume, informant, line numbers), and code interviewer race
by documented rules. Usage: python3 -I merge.py WORK_DIR OUT_CSV [codes_subdir] """
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
    'driskell': 'GA header credit "Driskell" / "E. Driskell" / "E.F. Driskell" = Edwin Driskell (typed in full above '
                'Isaiah Green; "By E. Driskell" above Lewis Favor); Notable Folklorists of Color (GA)',
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


# Entries whose segment holds more than the TOC-named informant's single interview. Ranges are 1-based
# line numbers in pg<eBook>.txt, inclusive, one per interview of the TOC-named informant, each starting
# at that interview's header block. Checked by eye against the Gutenberg text on 2026-11-11.
#   - same-surname neighbours whose own heading was not found, so the segment begins with the
#     neighbour's narrative (Armstrong, Boyd, Turner, Mitchell);
#   - two interviews of the same informant by different interviewers (Green, Douglas, Harris);
#   - narratives of other informants appended to the segment because their TOC entry could not be
#     located (the rest). Their credit lines are not this entry's interviewer (codebook section 8).
OWN_LINES = {
    'AR-II-1-024': [(2230, 2272)],                # Cora Armstrong; 1997-2225 is Campbell Armstrong (S.S. Taylor)
    'AR-II-1-067': [(6187, 6291)],                # Mal Boyd; 6128-6182 is Jack Boyd (Irene Robertson)
    'AR-II-6-114': [(10487, 10661)],              # Henry Turner; 10404-10482 is Emma Turner (Bernice Bowden)
    'AR-II-5-035': [(3379, 3499)],                # Moses Mitchell; his form begins in the 'Mitchell, Mary' segment
    'GA-IV-2-005': [(931, 1079), (1084, 1326)],   # Alice Green: Corry Fowler, then Sadie B. Hornsby
    'AR-II-2-051': [(5697, 5762), (5767, 5809)],  # Sarah Douglas: Pernella M. Anderson, then Carol Graham
    'AR-II-3-048': [(4985, 5048), (5053, 5112)],  # Rachel Harris: Bernice Bowden, then Irene Robertson
    'AR-II-2-018': [(2080, 2155)],                # Zenia Culp; 2160-2211 is Albert Cummins (Mrs. W.M. Ball)
    'AR-II-2-042': [(4529, 4588)],                # Katie Dillon; 4593-4720 is Alice Dixon (Pernella Anderson)
    'AR-II-3-064': [(6817, 6896)],                # Bert Higgins; 6901-7065 is Annie Hill (S.S. Taylor)
    'AR-II-5-044': [(4311, 4339)],                # Tom Morgan; 4344-4428 is Charity Morris (Pernella Anderson)
    'AR-II-6-024': [(2348, 2451)],                # William Henry Rooks; 2456-2630 is Amanda Rosa (S.S. Taylor)
    'AR-II-1-091': [(9060, 9275)],                # William Brown (N. Little Rock); header 9060-9064 is a stub segment
                                                  # because the INFORMANTS list has two 'Brown, William' entries
    'AR-II-7-065': [(6044, 6146), (6151, 6206)],  # Tom Windham: Bernice Bowden (two pieces), then Martin - Barker
    'GA-IV-2-006': [(1327, 1560), (1561, 1656)],  # Isaiah Green: Minnie B. Ross, then Edwin Driskell
    'SC-XIV-1-028': [(3636, 3737), (3738, 3892)], # Henry Brown: Jessie A. Butler, then Augustus Ladson
    'SC-XIV-4-056': [(6397, 6530)],               # Willis Williams; header 6397-6405 is in the 'Williams, Mary' stub
    'NC-XI-2-049': [(5574, 5720)],                # Porter Scales; 5389-5569 is Catherine Scales (same writer)
}

def own_text(nid, seg, off=0, file_lines=None):
    """Lines of each interview of the TOC-named informant, as a list of line lists.
    Default: the whole segment. For OWN_LINES entries the ranges are taken from the Gutenberg file
    (file_lines, needed where a header stands outside the segment) or else clipped to the segment."""
    L = seg['text'].split('\n')
    if nid not in OWN_LINES: return [L]
    if file_lines is not None:
        return [file_lines[a - 1:b] for a, b in OWN_LINES[nid]]
    base = seg['start_line'] + off          # file line of the segment's first line
    return [L[max(0, a - base):max(0, b - base + 1)] for a, b in OWN_LINES[nid]]

def interviewer_race(seg, nid=None, off=0, file_lines=None):
    """Documented race of the interviewer(s) of this entry (codebook section 8).

    Each interview of the TOC-named informant is searched in its first 45 and last 20 lines.
    Several interviewers (codebook section 8, rule added 2026-11-11): Black if any of them is
    documented Black, else white if any is documented white, else unknown."""
    found = []
    for own in own_text(nid, seg, off, file_lines):
        for zone in ('\n'.join(own[:45]), '\n'.join(own[-20:])):
            r = race_in_zone(zone)
            if r: found.append(r); break
    for want in ('Black', 'white'):
        src = [s for r, s in found if r == want]
        if src: return want, '; '.join(dict.fromkeys(src))
    return 'unknown', ''

def file_lines_of(raw, pg_id, _cache={}):
    if pg_id not in _cache:
        _cache[pg_id] = open(os.path.join(raw, f'pg{pg_id}.txt'), encoding='utf-8', errors='replace').read().replace('\r', '').split('\n')
    return _cache[pg_id]

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
    RAW = os.path.join(work, '..', 'raw')
    OFF = file_offsets(RAW)
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
        race, rsrc = interviewer_race(seg, nid, OFF[seg['pg_id']], file_lines_of(RAW, seg['pg_id']))
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
