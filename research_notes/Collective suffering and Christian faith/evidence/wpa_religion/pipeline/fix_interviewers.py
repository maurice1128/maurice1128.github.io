"""Correct the interviewer columns of data.csv (interviewer, interviewer_race, interviewer_race_source).

Why: the first run segmented each narrative from its title line. In most volumes the credit line
("Interviewer:", "Worker:", "Prepared by", a field worker's name) sits in a header block a few lines
ABOVE the title, so (a) the coder's extract never showed it and (b) the last lines of each segment were
the NEXT narrative's header, which was sometimes recorded as this narrative's interviewer and was read
by merge.py as this narrative's footer when it assigned race.

What this script does, for every row of data.csv:
  1. finds the narrative's own text: the segment in `segment_lines`, extended up to the top of its
     header block and cut before the next narrative's header (segment.header_start), or the line range
     in OWN where the segment was checked by eye and holds other people's interviews as well;
  2. sets `interviewer` from IV (credit lines read by eye in the fresh Gutenberg text) and checks that
     the name really stands in the narrative's own header or footer;
  3. re-applies the documented race rules of codebook section 8 (merge.race_in_zone) to the narrative's
     own header (first 45 lines) and footer (last 20 lines);
  4. applies the two-interviewer rule of codebook section 8 to the entries in MULTI.
No other column is touched. Line numbers are 1-based line numbers in the downloaded pg<eBook>.txt.

Usage: python3 -I fix_interviewers.py RAW_DIR DATA_CSV [--write]
"""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segment import header_start
from merge import race_in_zone

NR = 'not recorded'

# ---------------------------------------------------------------------------------------------------
# Interviewer as given in the narrative's own header or footer. Only rows whose value changes are
# listed; every other row keeps its value (and is still checked against the text in step 2).
IV = {
    # Alabama: the segment started at an illustration inside the narrative; the header is at l. 2851
    'AL-I-025': 'G.L. Clark',
    # Arkansas
    'AR-II-1-024': 'Pernella Anderson',     # "Interviewer: Pernella Anderson, colored." l. 2230 (Cora Armstrong's own piece)
    'AR-II-1-067': 'Bernice Bowden',        # "NAME OF WORKER--Bernice Bowden" l. 6191 (Mal Boyd's own form)
    'AR-II-1-091': 'Samuel S. Taylor',      # l. 9060
    'AR-II-7-019': 'Samuel S. Taylor',      # "NAME OF WORKER--Samuel S. Taylor" l. 1930
    'AR-II-5-076': 'Samuel S. Taylor',      # l. 6904
    'AR-II-6-114': 'Watt McKinney',         # l. 10488 (Henry Turner's own piece)
    'AR-II-5-035': 'Bernice Bowden',        # l. 3381; "Martin - Barker" was the next narrative's header
    'AR-II-2-051': 'Pernella M. Anderson + Carol Graham',   # two interviews, l. 5697 and l. 5767
    'AR-II-7-065': 'Bernice Bowden + Martin - Barker',      # three pieces, l. 6044, 6123, 6153
    'AR-II-3-048': 'Bernice Bowden + Irene Robertson',      # two pieces, l. 4986 and l. 5057
    # Florida (header: "American Guide, (Negro Writers' Unit)" / "<name>, Field Worker")
    'FL-III-008': 'Alfred Farrell', 'FL-III-016': 'James Johnson', 'FL-III-023': 'Martin Richardson',
    'FL-III-027': 'Samuel Johnson', 'FL-III-031': 'Pearl Randolph', 'FL-III-032': 'Pearl Randolph',
    'FL-III-036': 'J.M. Johnson', 'FL-III-039': 'Rachel A. Austin', 'FL-III-041': 'Viola B. Muse',
    'FL-III-042': 'J.M. Johnson', 'FL-III-046': 'Pearl Randolph', 'FL-III-050': 'James Johnson',
    # Georgia
    'GA-IV-1-003': 'J.R. Jones',            # l. 411; "Henrietta Carlisle" was the next header
    'GA-IV-1-005': 'Minnie B. Ross',        # typed in her own header, l. 611; the HW "Ross" belongs to the next narrative
    'GA-IV-1-014': NR,                      # own header page is a placeholder; "Barragan-Harris" heads the next narrative
    'GA-IV-1-015': 'Maude Barragan',        # l. 3117-3118
    'GA-IV-1-034': 'Sadie B. Hornsby',      # "Written By: Mrs. Sadie B. Hornsby" l. 6974-6975
    'GA-IV-1-035': 'E. Driskell',           # l. 7280
    'GA-IV-1-037': 'Grace McCune',          # l. 7822; the HW "Driskell" heads the next narrative
    'GA-IV-1-038': 'Driskell (HW header)',  # l. 8144
    'GA-IV-3-001': 'Driskell',              # l. 174
    'GA-IV-3-004': 'Mary A. Crawford',      # l. 579
    'GA-IV-3-029': 'Minnie B. Ross',        # "Submitted by Minnie B. Ross" l. 4349-4350
    'GA-IV-3-037': 'Ruth Chitty',           # "Written by Ruth Chitty" l. 5461
    'GA-IV-4-002': 'Grace McCune',          # l. 412; "Alberta Minor" was the next header
    'GA-IV-4-007': 'Sadie B. Hornsby',      # l. 1941
    'GA-IV-4-014': 'Josephine Lowell',      # l. 4003
    'GA-IV-2-005': 'Corry Fowler + Sadie B. Hornsby',   # two interviews, l. 935 and l. 1092
    'GA-IV-2-012': 'Minnie B. Ross',        # l. 2462
    'GA-IV-2-039': 'Louise McKinney',       # l. 8126
    'GA-IV-2-046': 'Emily Powell',          # "Written By: Emily Powell" l. 9236; "Alberta Minor" was the next header
    # Indiana (header: name / district / county)
    'IN-V-009': 'Anna Pritchett', 'IN-V-021': 'Cecil C. Miller', 'IN-V-024': 'William Webb Tuttle',
    'IN-V-027': 'Grace Monroe', 'IN-V-030': 'Lauana Creel', 'IN-V-037': 'William R. Mays',
    'IN-V-039': 'Iris Cook', 'IN-V-056': 'William R. Mays', 'IN-V-057': 'Archie Koritz',
    'IN-V-060': 'Emily Hobson',
    # Maryland (header: "Maryland" / date / name)
    'MD-VIII-014': 'Rogers', 'MD-VIII-019': 'Stansbury',
    # Mississippi (header: informant, county / "FEC" / field worker / rewrite / editor)
    'MS-IX-001': 'Mrs. Ed Joiner', 'MS-IX-007': 'Esther de Sola', 'MS-IX-009': 'Mrs. Richard Kolb',
    'MS-IX-021': 'W.B. Allison',
    # North Carolina (header: "Worker:")
    'NC-XI-1-009': 'T. Pat Matthews', 'NC-XI-1-010': 'T. Pat Matthews', 'NC-XI-1-019': 'Mary A. Hicks',
    'NC-XI-1-025': 'T. Pat Matthews', 'NC-XI-1-035': 'T. Pat Matthews', 'NC-XI-1-038': 'T. Pat Matthews',
    'NC-XI-1-041': 'Mary Hicks', 'NC-XI-1-046': 'T. Pat Matthews', 'NC-XI-1-051': 'T. Pat Matthews',
    'NC-XI-1-054': 'Travis Jordan', 'NC-XI-1-057': 'Mrs. W. N. Harriss', 'NC-XI-1-058': 'Daisy Whaley',
    'NC-XI-1-070': 'T. Pat Matthews', 'NC-XI-1-074': 'Mary A. Hicks', 'NC-XI-2-001': 'Mrs. W.N. Harriss',
    'NC-XI-2-022': 'Mary Hicks', 'NC-XI-2-045': 'T. Pat Matthews', 'NC-XI-2-049': 'Nancy Watkins',
    'NC-XI-2-057': 'T. Pat Matthews', 'NC-XI-2-059': 'T. Pat Matthews', 'NC-XI-2-065': 'Mary A. Hicks',
    'NC-XI-2-068': 'T. Pat Matthews', 'NC-XI-2-076': 'Mary A. Hicks',
    # Ohio (header: "<name>, Reporter" or "Reporter: <name>")
    'OH-XII-012': 'Miriam Logan', 'OH-XII-014': 'Miriam Logan', 'OH-XII-020': 'Bishop',
    'OH-XII-022': 'Bishop', 'OH-XII-028': 'Miriam Logan', 'OH-XII-029': 'Ruth Thompson',
    # South Carolina (header: "Project" / name / place, or "Prepared by"; footer: "Interviewer:").
    # Where the header names only an editor and the footer names the interviewer, the interviewer is taken.
    'SC-XIV-1-017': 'Caldwell Sims', 'SC-XIV-1-023': 'W. W. Dixon',
    'SC-XIV-1-028': 'Jessie A. Butler + Augustus Ladson',   # two interviews, l. 3637 and l. 3739
    'SC-XIV-1-029': 'W. W. Dixon', 'SC-XIV-1-047': 'G. L. Summer', 'SC-XIV-1-064': 'Annie Ruth Davis',
    'SC-XIV-1-065': 'W. W. Dixon', 'SC-XIV-1-068': 'Caldwell Sims', 'SC-XIV-1-071': 'G. L. Summer',
    'SC-XIV-2-005': 'Annie Ruth Davis', 'SC-XIV-2-010': 'G.L. Summer', 'SC-XIV-2-014': 'F.S. DuPre',
    'SC-XIV-2-018': 'Martha S. Pinckney', 'SC-XIV-2-019': 'F.S. DuPre', 'SC-XIV-2-026': 'Phoebe Faucette',
    'SC-XIV-2-037': 'Annie Ruth Davis', 'SC-XIV-2-043': 'Phoebe Faucette', 'SC-XIV-2-044': 'Everett R. Pierce',
    'SC-XIV-2-045': 'G.L. Summer', 'SC-XIV-2-061': 'Mrs. Chlotilde R. Martin', 'SC-XIV-2-067': 'Everett R. Pierce',
    'SC-XIV-4-005': 'G. Leland Summer', 'SC-XIV-4-021': 'Genevieve W. Chandler', 'SC-XIV-4-022': 'G. Leland Summer',
    'SC-XIV-4-044': 'W.W. Dixon', 'SC-XIV-4-049': 'Annie Ruth Davis', 'SC-XIV-4-054': 'W.W. Dixon',
    'SC-XIV-4-056': 'Genevieve W. Chandler', 'SC-XIV-4-059': 'Annie Ruth Davis', 'SC-XIV-4-064': 'Annie Ruth Davis',
    'SC-XIV-3-060': 'Martha S. Pinckney',
}

# Rows whose "not recorded" was checked and stands (109): the header gives no worker's name. These are
# all sampled rows of Texas (61), Oklahoma (18) and Tennessee (6), the 12 Missouri and 3 Kentucky rows
# still so marked, and AR-II-6-106, GA-IV-1-014, GA-IV-1-023, GA-IV-2-020, GA-IV-2-035, GA-IV-2-041,
# GA-IV-3-032, MS-IX-014, MS-IX-015.

# The informant's own text, where the segment in `segment_lines` also holds other people's interviews
# (TOC entries that could not be segmented separately) or starts in the wrong place. Checked by eye.
OWN = {
    'AL-I-025': (2851, 2944),        # header "Interview with Wadley 'Shorty' Clemons / --G.L. Clark"
    'AR-II-1-024': (2230, 2276),     # the segment opens with Campbell Armstrong's interview (S. S. Taylor)
    'AR-II-1-067': (6187, 6295),     # between Jack Boyd and George Braddox (both Irene Robertson)
    'AR-II-1-091': (9060, 9275),
    'AR-II-2-018': (2080, 2159),     # followed by Albert Cummins (Mrs. W.M. Ball)
    'AR-II-2-042': (4529, 4592),     # followed by Alice Dixon (Pernella Anderson)
    'AR-II-3-064': (6817, 6900),     # followed by Annie Hill (Samuel S. Taylor)
    'AR-II-5-035': (3379, 3503),     # the forms begin 87 lines above the recorded segment start
    'AR-II-5-044': (4311, 4343),     # followed by Charity Morris (Pernella Anderson)
    'AR-II-6-024': (2348, 2455),     # followed by Amanda Rosa (Samuel S. Taylor)
    'AR-II-6-114': (10487, 10665),   # preceded by Emma Turner (Bernice Bowden)
    'GA-IV-1-014': (2925, 3116),     # "Barragan-Harris" (l. 3117) heads Nancy Boudry
    'GA-IV-1-015': (3117, 3273),
    'NC-XI-2-049': (5574, 5720),     # preceded by Catherine Scales
    'NC-XI-2-065': (7208, 7324),     # followed by Annie Tate
    'OH-XII-032': (4126, 4231),      # preceded by Reverend Williams (Miriam Logan), a separate TOC entry
    'SC-XIV-1-029': (3893, 4015),    # followed by Mary Frances Brown (two interviews)
    'SC-XIV-1-065': (8728, 8876),    # followed by Wallace Davis (two interviews)
    'SC-XIV-2-019': (2839, 2914),    # followed by Lucy and Simon Gallman
    'SC-XIV-2-028': (3593, 3709),
    'SC-XIV-2-037': (4948, 5102),    # followed by Rebecca Jane Grant (Phoebe Faucette)
    'SC-XIV-4-005': (474, 535),      # followed by Jesse Rice and Phillip Rice
    'SC-XIV-4-021': (2070, 2224),
    'SC-XIV-4-022': (2225, 2378),    # two pieces, both G. L. Summer (footers l. 2331 and l. 2374)
    'SC-XIV-4-054': (6228, 6345),    # followed by Mary Williams (F.S. DuPre)
    'SC-XIV-4-056': (6397, 6534),
}

# Entries that hold interviews of the same informant by different interviewers: (first line, last line,
# interviewer) per interview. Race is coded only if every interviewer has the same documented race.
MULTI = {
    'GA-IV-2-005': [(929, 1083, 'Corry Fowler'), (1084, 1326, 'Sadie B. Hornsby')],
    'SC-XIV-1-028': [(3636, 3737, 'Jessie A. Butler'), (3738, 3892, 'Augustus Ladson')],
    'AR-II-2-051': [(5697, 5766, 'Pernella M. Anderson'), (5767, 5813, 'Carol Graham')],
    'AR-II-7-065': [(6044, 6150, 'Bernice Bowden'), (6151, 6210, 'Martin - Barker')],
    'AR-II-3-048': [(4985, 5052, 'Bernice Bowden'), (5053, 5116, 'Irene Robertson')],
}

# ---------------------------------------------------------------------------------------------------
def read_raw(raw, pid, cache={}):
    if pid not in cache:
        txt = open(os.path.join(raw, f'pg{pid}.txt'), encoding='utf-8', errors='replace').read().replace('\r', '')
        cache[pid] = txt.split('\n')
    return cache[pid]

def own_bounds(L, r):
    """1-based first and last line of the narrative's own text."""
    if r['nid'] in OWN: return OWN[r['nid']]
    s, e = map(int, r['segment_lines'].split('-'))
    return header_start(L, s - 1, 0) + 1, header_start(L, e, 0)   # e (0-based) is the next segment's first line

def race_of(L, a, b):
    """merge.interviewer_race on lines a..b (1-based, inclusive); also returns the matching zone."""
    seg = L[a - 1:b]
    for zone in ('\n'.join(seg[:45]), '\n'.join(seg[-20:])):
        r = race_in_zone(zone)
        if r: return r
    return 'unknown', ''

def name_key(name):
    """Surname (last alphabetic token) used to check that a credit stands in the narrative's own text."""
    name = re.sub(r'\(.*?\)', ' ', name)
    toks = [t for t in re.findall(r"[A-Za-z][A-Za-z'\-]+", name) if t.lower() not in ('jr', 'sr', 'editor')]
    return toks[-1].lower() if toks else ''

def credit_line(L, a, b, name):
    seg = list(enumerate(L[a - 1:b], a))
    key = name_key(name)
    for ln, t in seg[:45] + seg[-20:]:
        if key and key in t.lower(): return ln
    return None

def main(raw, path, write):
    rows = list(csv.DictReader(open(path, encoding='utf-8', newline='')))
    fields = list(rows[0].keys())
    changed_iv = changed_race = 0; problems = []
    for r in rows:
        L = read_raw(raw, r['gutenberg_ebook'])
        a, b = own_bounds(L, r)
        old = (r['interviewer'], r['interviewer_race'], r['interviewer_race_source'])
        iv = IV.get(r['nid'], r['interviewer'])
        if r['nid'] in MULTI:
            parts = []
            for (pa, pb, name) in MULTI[r['nid']]:
                if credit_line(L, pa, pb, name) is None: problems.append(f"{r['nid']}: credit '{name}' not found in lines {pa}-{pb}")
                parts.append((name,) + race_of(L, pa, pb))
            races = {p[1] for p in parts}
            if races == {'unknown'}:
                race, src = 'unknown', ''
            elif len(races) == 1:
                race, src = parts[0][1], '; '.join(dict.fromkeys(p[2] for p in parts))
            else:
                race = 'unknown'
                src = 'two interviewers, not the same documented race: ' + '; '.join(
                    f"{n} {'undocumented' if rc == 'unknown' else rc + ' (' + s + ')'}" for n, rc, s in parts)
        else:
            race, src = race_of(L, a, b)
            if not iv.startswith(NR):
                for name in re.split(r'\s+(?:&|from FC by)\s+', iv):
                    if credit_line(L, a, b, name) is None:
                        problems.append(f"{r['nid']}: credit '{name}' not found in own text, lines {a}-{b}")
        r['interviewer'], r['interviewer_race'], r['interviewer_race_source'] = iv, race, src
        new = (iv, race, src)
        if new[0] != old[0]: changed_iv += 1
        if new[1] != old[1]: changed_race += 1
        if new != old:
            print(f"{r['nid']:13} {r['informant'][:26]:26} | {old[0]} -> {new[0]} | {old[1]} -> {new[1]} | {new[2][:70]}")
    import collections
    print(f"\nrows with interviewer changed: {changed_iv}; rows with interviewer_race changed: {changed_race}")
    print('interviewer_race:', dict(collections.Counter(r['interviewer_race'] for r in rows)))
    print('not recorded:', sum(r['interviewer'].startswith(NR) for r in rows))
    print(f'problems: {len(problems)}')
    for p in problems: print('  ', p)
    if write and not problems:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
        print('written', path)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--write' in sys.argv)
