"""Parse INFORMANTS lists from the Gutenberg WPA volumes."""
import re, sys, os, json

VOLS = {
 '36020': ('AL', 'I', 'Alabama'),
 '11255': ('AR', 'II-1', 'Arkansas pt 1'), '13700': ('AR', 'II-2', 'Arkansas pt 2'),
 '19446': ('AR', 'II-3', 'Arkansas pt 3'), '25154': ('AR', 'II-4', 'Arkansas pt 4'),
 '11544': ('AR', 'II-5', 'Arkansas pt 5'), '11709': ('AR', 'II-6', 'Arkansas pt 6'),
 '11422': ('AR', 'II-7', 'Arkansas pt 7'),
 '12297': ('FL', 'III', 'Florida'),
 '13602': ('GA', 'IV-1', 'Georgia pt 1'), '22166': ('GA', 'IV-2', 'Georgia pt 2'),
 '18484': ('GA', 'IV-3', 'Georgia pt 3'), '18485': ('GA', 'IV-4', 'Georgia pt 4'),
 '13579': ('IN', 'V', 'Indiana'), '11485': ('KS', 'VI', 'Kansas'),
 '11920': ('KY', 'VII', 'Kentucky'), '11552': ('MD', 'VIII', 'Maryland'),
 '12055': ('MS', 'IX', 'Mississippi'), '35379': ('MO', 'X', 'Missouri'),
 '22976': ('NC', 'XI-1', 'North Carolina pt 1'), '31219': ('NC', 'XI-2', 'North Carolina pt 2'),
 '13217': ('OH', 'XII', 'Ohio'), '20785': ('OK', 'XIII', 'Oklahoma'),
 '18912': ('SC', 'XIV-1', 'South Carolina pt 1'), '21508': ('SC', 'XIV-2', 'South Carolina pt 2'),
 '36022': ('SC', 'XIV-3', 'South Carolina pt 3'), '28170': ('SC', 'XIV-4', 'South Carolina pt 4'),
 '19932': ('TN', 'XV', 'Tennessee'),
 '30576': ('TX', 'XVI-1', 'Texas pt 1'), '30967': ('TX', 'XVI-2', 'Texas pt 2'),
 '35380': ('TX', 'XVI-3', 'Texas pt 3'), '35381': ('TX', 'XVI-4', 'Texas pt 4'),
 '28973': ('VA', 'XVII', 'Virginia'),
}

NAME_RE = re.compile(r"^\s*(?:-\s+)?([A-Z\[][^\d]{1,90}?)\s*([\d][\d,\s\-]*)?\s*$")
COUNTY_RE = re.compile(r"^\s*[A-Z][A-Z \.']+ CO[:\.]?\s*$|^\s*COMBINED INTERVIEWS\s*$")

def read(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        txt = fh.read()
    s = txt.find('*** START OF')
    e = txt.find('*** END OF')
    if s >= 0:
        s = txt.find('\n', s) + 1
    else:
        s = 0
    if e < 0: e = len(txt)
    return txt[s:e].replace('\r', '').split('\n')

def parse_toc(lines):
    i0 = next(i for i, l in enumerate(lines) if l.strip() == 'INFORMANTS')
    entries = []
    blank = 0
    i = i0 + 1
    cont = False
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            blank += 1
            if blank >= 3 and entries:
                break
            i += 1
            continue
        blank = 0
        st = l.strip()
        if cont:  # continuation of a [TR: ...] note
            if ']' in st: cont = False
            i += 1; continue
        if st in ('ILLUSTRATIONS',) or st.startswith('[Illustration') :
            break
        if COUNTY_RE.match(l):
            i += 1; continue
        if st.startswith('[TR:') :
            if ']' not in st: cont = True
            i += 1; continue
        m = NAME_RE.match(l)
        if not m or len(st) > 110:
            if entries: break
            i += 1; continue
        name = m.group(1).strip()
        if '[TR:' in name and ']' not in name:
            cont = True
        name = re.sub(r'\[TR:.*', '', name).strip()
        entries.append({'toc_raw': st, 'name': name, 'pages': (m.group(2) or '').strip(), 'toc_line': i})
        i += 1
    return i0, i, entries

if __name__ == '__main__':
    raw = sys.argv[1]
    for pid, (st, vol, lab) in VOLS.items():
        lines = read(os.path.join(raw, f'pg{pid}.txt'))
        i0, i1, ents = parse_toc(lines)
        print(pid, st, vol, len(ents), '| first:', ents[0]['name'], '| last:', ents[-1]['name'], '| end line:', i1, repr(lines[i1][:60]) if i1 < len(lines) else '')
