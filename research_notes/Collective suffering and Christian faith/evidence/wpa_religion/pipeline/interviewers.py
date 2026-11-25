"""Best-effort extraction of interviewer names and in-text race markers from segments.
Usage: python3 -I interviewers.py WORK_DIR"""
import re, sys, json, os, collections

PATS = [
    r'Interviewer[s]?\s*[:\-]\s*(.+)',
    r'Interviewed by\s*[:\-]?\s*(.+)',
    r'Written by\s*[:\-]?\s*(.+)?',
    r'Name of (?:interviewer|worker|field worker)\s*[:\-]\s*(.+)',
    r'Field ?[Ww]orker\s*[:\-]\s*(.+)',
    r'Research [Ww]orker\s*[:\-]\s*(.+)',
    r'Reported by\s*[:\-]?\s*(.+)',
    r'^\s*BY\s*:\s*(.+)',
    r'^\s*By\s*:\s*(.+)',
    r'Writer\s*[:\-]\s*(.+)',
    r'Story [Tt]eller.*\n(?:.*\n)?\s*(?:Editor)\s*:\s*(.+)',
    r'--_?Written by ([^_\n]+)',
]

def extract(text):
    head = '\n'.join(text.split('\n')[:40])
    tail = '\n'.join(text.split('\n')[-15:])
    found = []
    for zone in (head, tail):
        for p in PATS:
            for m in re.finditer(p, zone, re.M):
                g = (m.group(1) or '').strip()
                if not g:  # name on next line ("Written by:\nSadie B. Hornsby")
                    rest = zone[m.end():].lstrip('\n').split('\n')
                    g = rest[0].strip() if rest else ''
                g = re.sub(r'\s{2,}.*', '', g).strip(' ,.;*_')
                if g and len(g) < 80:
                    found.append(g)
    return found

def markers(text):
    head = '\n'.join(text.split('\n')[:45]) + '\n' + '\n'.join(text.split('\n')[-15:])
    out = []
    for p in [r'\[HW:\s*\(?(White|Negro|Colored)\)?\]', r'Negro Writers[\'’]? Unit', r'Interviewer:[^\n]*\b(colored|negro)\b',
              r'Negro (?:Writers|Studies|unit|Unit)']:
        for m in re.finditer(p, head, re.I):
            out.append(m.group(0))
    return out

if __name__ == '__main__':
    work = sys.argv[1]
    R = [json.loads(l) for l in open(os.path.join(work, 'segments.jsonl'))]
    cnt = collections.Counter()
    with open(os.path.join(work, 'interviewers.jsonl'), 'w') as fh:
        for r in R:
            iv = extract(r['text']); mk = markers(r['text'])
            fh.write(json.dumps({'nid': r['nid'], 'interviewer_raw': iv, 'race_markers': mk}) + '\n')
            key = (r['state'], iv[0] if iv else '(none)')
            cnt[key] += 1
    for (st, nm), c in sorted(cnt.items()):
        print(st, c, nm, sep='\t')
