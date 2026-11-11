"""Parse BHO Husting calendar roll pages (downloaded HTML) into one record per entry.
Usage: python3 -I parse.py RAW_DIR PAGES_TSV OUT_JSON
"""
import sys, re, json, html

RAW, PAGES, OUT = sys.argv[1:4]

# regnal year start (month, day) and first calendar year
REIGN = {
    'Edward II': (1307, 7, 8),
    'Edward III': (1327, 1, 25),
    'Richard II': (1377, 6, 22),
    'Henry IV': (1399, 9, 30),
}
MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7,
          'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}


def cal_year(reign, n, m, d):
    y0, m0, d0 = REIGN[reign]
    first = y0 + n - 1
    return first if (m, d) >= (m0, d0) else first + 1


def bracket_date(s):
    # e.g. "[2 Feb.]", "[12 March]", "[23 April]"
    for m in re.finditer(r'\[(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?\]', s):
        mon = MONTHS.get(m.group(2).lower()[:3])
        if mon:
            return mon, int(m.group(1))
    return None


def clean(s):
    s = re.sub(r'<a [^>]*>\(fn\. \d+\)</a>', '', s)
    s = re.sub(r'<tr class="page-row">.*?\[Page (\d+)\].*?</tr>', r' @@PAGE\1@@ ', s)
    s = re.sub(r'<br\s*/?>', ' ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return s


records = []
for line in open(PAGES):
    vol, pg, title = line.rstrip('\n').split('\t')
    h = open(f'{RAW}/{vol}_{pg}.html', encoding='utf-8').read()
    a = h.find('<div class="inner">')
    b = h.find('<footer class="footnotes">')
    body = h[a:b if b > 0 else len(h)]
    tm = re.match(r'(\d+) (Edward III|Edward II|Richard II|Henry IV)', title)
    reign, n = tm.group(2), int(tm.group(1))
    page = int(re.search(r'pp?(\d+)', pg).group(1))
    # tokenise into blocks: page markers, h2, p, blockquote
    tokens = re.findall(r'(<tr class="page-row">.*?</tr>|<h2[^>]*>.*?</h2>|<p[^>]*>.*?</p>)', body, re.S)
    cur = None
    md = None  # reset per page; current (month, day) from date heading
    heading = ''
    for t in tokens:
        pm = re.search(r'\[Page (\d+)\]', t)
        if t.startswith('<tr'):
            if pm:
                page = int(pm.group(1))
            continue
        if t.startswith('<h2'):
            continue
        inner = re.sub(r'^<p[^>]*>|</p>$', '', t.strip(), flags=re.S).strip()
        # page markers inside a paragraph
        txt = clean(inner).strip()
        stripped = re.sub(r'\s*@@PAGE\d+@@\s*', ' ', txt).strip()
        # date heading = paragraph wholly in <em>
        if re.fullmatch(r'<em>.*</em>\.?', inner, re.S) and not re.search(r'Roll \d', stripped):
            heading = stripped
            bd = bracket_date(stripped)
            if bd:
                md = bd
            cur = None
            continue
        is_entry = re.match(r'^"?\s*<strong>', inner) is not None
        if is_entry:
            cur = {'vol': 1 if vol == 'vol1' else 2, 'page_url': pg, 'page': page,
                   'roll_title': title, 'reign': reign, 'regnal_year': n,
                   'heading': heading, 'md': md, 'text': ''}
            records.append(cur)
        if cur is None:
            continue
        # update page tracker for text inside
        for p in re.findall(r'@@PAGE(\d+)@@', txt):
            page = int(p)
        cur['text'] = (cur['text'] + ' ' + stripped).strip()

for r in records:
    r['text'] = re.sub(r'\s+', ' ', r['text'])
    m = re.findall(r'Roll ([\d.]+)\s*\((\d+\*?)\)', r['text'])
    r['roll'] = f'{m[-1][0]}({m[-1][1]})' if m else ''
    if r['md']:
        r['enrol_year'] = cal_year(r['reign'], r['regnal_year'], *r['md'])
        r['enrol_year_basis'] = 'heading date'
    else:
        y0, m0, d0 = REIGN[r['reign']]
        r['enrol_year'] = y0 + r['regnal_year'] - 1
        r['enrol_year_basis'] = 'regnal year start (no heading date)'
    del r['md']
json.dump(records, open(OUT, 'w'), ensure_ascii=False, indent=0)
print(len(records))
