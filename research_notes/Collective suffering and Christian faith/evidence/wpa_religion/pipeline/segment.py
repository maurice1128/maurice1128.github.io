"""Segment the Gutenberg WPA volumes into individual narratives, guided by each
volume's INFORMANTS list. Output: work/segments.jsonl (one record per narrative).
Usage: python3 -I segment.py RAW_DIR OUT_DIR
"""
import re, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toc import VOLS, read, NAME_RE, COUNTY_RE

TITLES = {'rev', 'rev.', 'mrs', 'mrs.', 'mr', 'mr.', 'dr', 'dr.', 'uncle', 'aunt', 'aunty', 'auntie',
          'mammy', 'parson', 'miss', 'ms.', 'capt.', 'sister', 'brother', 'granny', 'daddy', 'mother',
          'father', 'old', 'and', 'jr.', 'sr.', 'jr', 'sr'}

def parse_toc2(lines, state):
    """Return (toc_end_line, entries). Handles continuation lines, county headers,
    COMBINED INTERVIEWS sections (kept for KY only)."""
    i0 = next(i for i, l in enumerate(lines) if l.strip() == 'INFORMANTS')
    entries, blank, i, cont, combined = [], 0, i0 + 1, False, False
    while i < len(lines):
        l = lines[i]; st = l.strip()
        if not st:
            blank += 1
            if blank >= 3 and entries: break
            i += 1; continue
        blank = 0
        if cont:
            if ']' in st: cont = False
            i += 1; continue
        if st.startswith('ILLUSTRATIONS') or st.startswith('*ILLUSTRATIONS') or st.startswith('[Illustration'):
            break
        if st.startswith('COMBINED INTERVIEWS'):
            combined = True
            i += 1; continue
        if COUNTY_RE.match(l) or re.match(r'^[A-Z ,\.]+(STORIES|FOLKLORE)\s*$', st) or st.startswith('[Excerpts'):
            i += 1; continue
        if st.startswith('[TR:'):
            if ']' not in st: cont = True
            i += 1; continue
        if re.match(r'^(and|\(|[a-z])', st) and entries:  # continuation of previous entry
            entries[-1]['toc_raw'] += ' ' + st
            i += 1; continue
        m = NAME_RE.match(l)
        if not m or len(st) > 110:
            if entries: break
            i += 1; continue
        name = re.sub(r'\[TR:.*', '', m.group(1)).strip()
        if '[TR:' in m.group(1) and ']' not in m.group(1): cont = True
        if combined and state != 'KY':
            i += 1; continue  # FL and GA-4 combined excerpt sections excluded
        if name.startswith('[') and re.search(r'Bill of Sale|WILL--', name):
            i += 1; continue
        entries.append({'toc_raw': st, 'name': name.strip('[] '), 'pages': (m.group(2) or '').strip(),
                        'combined': combined})
        i += 1
    return i, entries

def name_tokens(name):
    n = re.sub(r'\(.*?\)', ' ', name)
    n = re.sub(r'["\']', ' ', n)
    if ',' in n:
        sur, given = n.split(',', 1)
        sur_toks = [t for t in re.findall(r"[A-Za-z][A-Za-z\-]+", sur)]
        g = [t for t in re.findall(r"[A-Za-z][A-Za-z\-]*\.?", given) if t.lower() not in TITLES]
        surname = sur_toks[-1] if sur_toks else ''
        first = g[0].rstrip('.') if g else ''
    else:
        toks = [t for t in re.findall(r"[A-Za-z][A-Za-z\-]*\.?", n) if t.lower() not in TITLES]
        if len(toks) >= 2:
            surname, first = toks[-1].rstrip('.'), toks[0].rstrip('.')
        elif toks:
            surname, first = toks[0].rstrip('.'), ''
        else:
            surname, first = '', ''
    if len(first) <= 1: first = ''
    return surname, first

HDR_RE = re.compile(r'(person interviewed|interviewed|informant|subject|name of|ex-slave|ex slave|interview with|story of|age\b)', re.I)

def heading_like(line, sur, first):
    st = line.strip()
    if not st or len(st) > 130: return False
    if re.match(r'^[_\W]*(source|sources|page \d|interviewer|\[TR)', st, re.I): return False
    if not re.search(r'\b' + re.escape(sur) + r'\b', st, re.I): return False
    letters = [c for c in st if c.isalpha()]
    upfrac = sum(c.isupper() for c in letters) / max(1, len(letters))
    if upfrac >= 0.7: return True
    if re.search(r'\b' + re.escape(sur.upper()) + r'\b', st) and len(sur) > 2: return True
    if HDR_RE.search(st) and ':' in st and not st.startswith('"'): return True
    # short line that is basically the name (needs first name too, if known)
    if len(st) < 60 and st[0].isupper() and not st.endswith(('.', ',', ';', '!', '?', ':')) and not re.search(r'[!?"]', st):
        words = re.findall(r"[A-Za-z]+", st)
        if len(words) <= 5 and (not first or re.search(r'\b' + re.escape(first), st, re.I)): return True
    return False

def find_start(lines, cur, sur, first, limit):
    """first pass: surname + first name; second: surname only."""
    for need_first in ([True, False] if first else [False]):
        for j in range(cur, min(limit, len(lines))):
            l = lines[j]
            if not heading_like(l, sur, first): continue
            if need_first and not re.search(r'\b' + re.escape(first), l, re.I):
                # allow first name on next line(s) for split headings
                nxt = ' '.join(lines[j+1:j+3])
                if not re.search(r'\b' + re.escape(first), nxt, re.I): continue
            return j
    return None

WINDOW = 2500

def main(raw, out):
    os.makedirs(out, exist_ok=True)
    recs, problems = [], []
    for pid, (state, vol, lab) in VOLS.items():
        lines = read(os.path.join(raw, f'pg{pid}.txt'))
        tend, ents = parse_toc2(lines, state)
        # skip illustrations list if present
        cur = tend
        for k in range(tend, min(tend + 400, len(lines))):
            if 'ILLUSTRATIONS' in lines[k]:
                # skip until a run of 3 blank lines after list
                b = 0
                for m in range(k + 1, len(lines)):
                    if not lines[m].strip():
                        b += 1
                        if b >= 3:
                            cur = m; break
                    else: b = 0
                break
        starts, methods = [], []
        body0 = cur
        prev_sur, prev_j = None, None
        # end of individual narratives: a body-level COMBINED INTERVIEWS heading (FL, GA-4 excluded)
        vol_end = len(lines)
        if state in ('FL', 'GA'):
            for x in range(body0, len(lines)):
                if lines[x].strip().startswith('COMBINED INTERVIEWS'):
                    vol_end = x; break
        for e in ents:
            sur, first = name_tokens(e['name'])
            e['surname'], e['first'] = sur, first
            if not sur:
                starts.append(None); methods.append(None); continue
            c0 = cur
            if prev_sur and prev_sur.lower() == sur.lower() and prev_j is not None:
                c0 = max(cur, prev_j + 15)  # same surname as previous entry: skip its header block
            j = find_start(lines, c0, sur, first, c0 + WINDOW)
            prev_sur = sur
            if j is None:
                starts.append(None); methods.append(None); continue
            starts.append(j); methods.append('heading'); cur = j + 1; prev_j = j
        # pass 2: missing entries -> surname anywhere in the gap, back up to block gap
        for k, e in enumerate(ents):
            if starts[k] is not None or not e.get('surname'): continue
            a = max([s for s in starts[:k] if s is not None] or [body0])
            later = [s for s in starts[k+1:] if s is not None]
            b = min(later) if later else len(lines)
            pat = re.compile(r'\b' + re.escape(e['surname']) + r'\b', re.I)
            j = next((x for x in range(a + 1, b) if pat.search(lines[x])), None)
            if j is None:
                problems.append((pid, e['name'], 'not found')); continue
            st = None
            for x in range(j, a + 1, -1):
                if lines[x].strip() and all(not lines[x - y].strip() for y in (1, 2)):
                    st = x; break
            if st is None or st <= a:
                problems.append((pid, e['name'], 'no block start')); continue
            if any(s is not None and s == st for s in starts):
                problems.append((pid, e['name'], 'block start collides')); continue
            starts[k] = st; methods[k] = 'gap-fallback'
        # enforce monotonic order
        last = -1
        for k in range(len(starts)):
            if starts[k] is None: continue
            if starts[k] <= last:
                problems.append((pid, ents[k]['name'], 'out of order')); starts[k] = None; continue
            last = starts[k]
        # build segments
        idx = [(k, s) for k, s in enumerate(starts) if s is not None]
        for n, (k, s) in enumerate(idx):
            e = ents[k]
            end = idx[n + 1][1] if n + 1 < len(idx) else vol_end
            # back up over header lines just above the heading
            s0 = s
            for b in range(1, 9):
                if s - b <= tend: break
                pl = lines[s - b].strip()
                if not pl: continue
                if re.match(r'^(Interviewer|Interviewed by|Written by|Name of [Ii]nterviewer|By:|Field ?[Ww]orker|Reported by|Research Worker|\[HW|\[Date|District|Federal Writers|[A-Z][A-Z \-\',\.]{3,60}$)', pl) and not pl.startswith('"'):
                    s0 = s - b
                else:
                    break
            if n > 0 and s0 <= idx[n - 1][1]: s0 = s
            text = '\n'.join(lines[s0:end])
            recs.append({'nid': f'{state}-{vol}-{k+1:03d}', 'pg_id': pid, 'state': state, 'volume': vol,
                         'volume_label': lab, 'toc_name': e['name'], 'toc_pages': e['pages'],
                         'combined_section': e['combined'], 'seg_method': methods[k], 'start_line': s0 + 1, 'end_line': end,
                         'n_chars': len(text), 'text': text})
            # truncate previous record to s0
            if n > 0 and recs[-2]['pg_id'] == pid and recs[-2]['end_line'] > s0:
                prev = recs[-2]
                pl = lines[prev['start_line'] - 1:s0]
                prev['end_line'] = s0; prev['text'] = '\n'.join(pl); prev['n_chars'] = len(prev['text'])
        print(f'{pid} {state} {vol}: toc={len(ents)} segmented={len(idx)}')
    with open(os.path.join(out, 'segments.jsonl'), 'w') as fh:
        for r in recs: fh.write(json.dumps(r) + '\n')
    with open(os.path.join(out, 'segment_problems.txt'), 'w') as fh:
        for p in problems: fh.write('\t'.join(p) + '\n')
    print('TOTAL segments', len(recs), 'problems', len(problems))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
