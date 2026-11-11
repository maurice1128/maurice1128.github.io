"""Correction of 2026-11-11: interviewer credit lines that stand above the segment start.

The first segmentation started each narrative at the informant's name, so a credit line in the
header block above the name ("Interviewer: ...", "Worker: ...", "NAME OF WORKER--...", "Prepared by
...", "X, Field Worker", "[HW: Dist. 5 ... Driskell]") fell into the tail of the PREVIOUS segment.
Two errors followed in data.csv:
  - `interviewer` = "not recorded" although the header names the worker, and
  - `interviewer` taken from the tail of the segment, which is the NEXT narrative's header.
`interviewer_race` was wrong wherever the name concerned is a documented one.

This script
  1. reads the segments made by the corrected segment.py (WORK_DIR/segments.jsonl),
  2. sets `interviewer` from the table IV below, which was filled by eye from the header and footer
     of every sampled narrative; each entry carries the Gutenberg line that shows the credit, and
     the script refuses to run unless that line contains the name,
  3. re-applies the race rules of codebook section 8 through merge.interviewer_race(), and
  4. rewrites `interviewer`, `interviewer_race`, `interviewer_race_source` and `segment_lines` in
     data.csv, the locator columns of corpus_screen.csv, and writes interviewer_corrections.csv
     (one row per changed narrative, old and new values, evidence line).
No code column is touched.

Usage: python3 -I interviewer_fix.py WORK_DIR RAW_DIR PROJECT_DIR [--dry]
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge

NR = 'not recorded'

# nid: (interviewer, evidence line in pg<eBook>.txt [or None when the point is that no credit exists], note)
IV = {
    # ---- Arkansas
    'AR-II-1-024': ('Pernella Anderson', 2230, "own interview starts l. 2230; the 'Interviewer: Samuel S. Taylor' line at l. 1997 heads Campbell Armstrong's narrative, which fills the first part of this segment"),
    'AR-II-1-067': ('Bernice Bowden', 6191, "own interview starts l. 6187; l. 6128-6182 is Jack Boyd (Irene Robertson)"),
    'AR-II-1-091': ('Samuel S. Taylor', 9060, "header l. 9060-9064 stands in a stub segment (two 'Brown, William' entries in the INFORMANTS list)"),
    'AR-II-2-051': ('Pernella M. Anderson; Carol Graham', 5767, "two interviews of Sarah Douglas: Anderson l. 5697, Graham l. 5767"),
    'AR-II-3-048': ('Bernice Bowden; Irene Robertson', 5057, "two interviews of Rachel Harris: Bowden l. 4986, Robertson l. 5057"),
    'AR-II-5-035': ('Bernice Bowden', 3381, "his form header stands in the 'Mitchell, Mary' segment; 'Martin - Barker' (l. 3506) heads the next narrative, Ben Moon"),
    'AR-II-5-076': ('Samuel S. Taylor', 6904, ''),
    'AR-II-6-114': ('Watt McKinney', 10488, "own interview starts l. 10487; l. 10404-10482 is Emma Turner (Bernice Bowden)"),
    'AR-II-7-019': ('Samuel S. Taylor', 1930, ''),
    'AR-II-7-065': ('Bernice Bowden; Martin - Barker', 6153, "three pieces on Tom Windham: Bowden l. 6044 and l. 6123, Martin - Barker l. 6153"),
    # ---- Florida (all "American Guide, (Negro Writers' Unit)" headers)
    'FL-III-008': ('Alfred Farrell', 1372, ''),
    'FL-III-016': ('James Johnson', 2353, "'Martin Richardson' heads the next narrative"),
    'FL-III-023': ('Martin Richardson', 3506, ''),
    'FL-III-027': ('Samuel Johnson', 4234, ''),
    'FL-III-031': ('Pearl Randolph', 4896, ''),
    'FL-III-032': ('Pearl Randolph', 5091, ''),
    'FL-III-036': ('J.M. Johnson', 5455, ''),
    'FL-III-039': ('Rachel A. Austin', 5995, ''),
    'FL-III-041': ('Viola B. Muse', 6503, ''),
    'FL-III-042': ('J.M. Johnson', 6675, ''),
    'FL-III-046': ('Pearl Randolph', 7909, ''),
    'FL-III-050': ('James Johnson', 8652, ''),
    # ---- Georgia
    'GA-IV-1-003': ('J.R. Jones', None, "name line directly above 'REV. W.B. ALLEN, EX-SLAVE'; 'Henrietta Carlisle' heads the next narrative"),
    'GA-IV-1-005': ('Minnie B. Ross', 611, "typed in her own header; the handwritten 'Ross' block (l. 716-718) heads the next narrative, Celestia Avery"),
    'GA-IV-1-014': (NR, None, "own header page is a placeholder ([TR] note l. 2932); 'Barragan-Harris' heads the next narrative, Nancy Boudry"),
    'GA-IV-1-015': ('Maude Barragan', 3118, "'Barragan-Harris', [TR: Miss Maude Barragan (interviewer)]"),
    'GA-IV-1-034': ('Sadie B. Hornsby', 6975, "'E. Driskell' (l. 7280) heads the next narrative, Mose Davis"),
    'GA-IV-1-035': ('Edwin Driskell ("E. Driskell" in header)', 7280, ''),
    'GA-IV-1-037': ('Grace McCune', 7822, "'Driskell' (l. 8144) heads the next narrative, George Eason"),
    'GA-IV-1-038': ('Edwin Driskell ("Driskell" in header)', 8144, ''),
    'GA-IV-2-005': ('Corry Fowler; Sadie B. Hornsby', 1092, "two interviews of Alice Green: Fowler l. 937, Hornsby l. 1092"),
    'GA-IV-2-006': ('Minnie B. Ross; Edwin Driskell', 1563, "two interviews of Isaiah Green: Ross l. 1332, Driskell l. 1563"),
    'GA-IV-2-012': ('Minnie B. Ross', 2462, ''),
    'GA-IV-2-039': ('Louise McKinney (name in header line, role not stated)', 8126, ''),
    'GA-IV-2-046': ('Emily Powell', None, "'Written By: / Emily Powell'; 'Alberta Minor' heads the next narrative"),
    'GA-IV-3-001': ('Edwin Driskell ("Driskell" in header)', 174, 'first narrative of the volume, so the block cannot be a footer'),
    'GA-IV-3-004': ('Mary A. Crawford', 579, ''),
    'GA-IV-3-029': ('Minnie B. Ross', 4350, ''),
    'GA-IV-3-037': ('Ruth Chitty', 5461, 'rewritten by Velma Bell'),
    'GA-IV-4-002': ('Grace McCune', 412, "'Alberta Minor' heads the next narrative"),
    'GA-IV-4-007': ('Sadie B. Hornsby', 1941, ''),
    'GA-IV-4-014': ('Josephine Lowell', 4003, ''),
    # ---- Indiana (worker's name and district stand above the title)
    'IN-V-009': ('Anna Pritchett', None, "'Lauana Creel' heads the next narrative"),
    'IN-V-021': ('Cecil C. Miller', None, "'Lauana Creel' heads the next narrative"),
    'IN-V-024': ('William Webb Tuttle', 3119, ''),
    'IN-V-027': ('Grace Monroe', 3320, ''),
    'IN-V-030': ('Lauana Creel', None, "'Anna Pritchett' heads the next narrative"),
    'IN-V-037': ('William R. Mays', None, "'Anna Pritchett' heads the next narrative"),
    'IN-V-039': ('Iris Cook', None, "'Lauana Creel' heads the next narrative"),
    'IN-V-056': ('William R. Mays', 5974, ''),
    'IN-V-057': ('Archie Koritz', None, "'Lauana Creel' heads the next narrative"),
    'IN-V-060': ('Emily Hobson', 6420, ''),
    # ---- Maryland (surname line in the header)
    'MD-VIII-014': ('Rogers', None, "'Ellen B. Warfield' heads the next narrative"),
    'MD-VIII-019': ('Stansbury', None, "'Rogers' heads the next narrative"),
    # ---- Mississippi (field worker's name after 'FEC', before 'Rewrite, ...' and 'Edited, ...')
    'MS-IX-001': ('Mrs. Ed Joiner', 141, ''),
    'MS-IX-007': ('Esther de Sola', 1319, ''),
    'MS-IX-009': ('Mrs. Richard Kolb', 1639, ''),
    'MS-IX-021': ('W.B. Allison', 3790, ''),
    # ---- North Carolina ("Worker:" line of the narrative's own header)
    'NC-XI-1-009': ('T. Pat Matthews', 1320, ''),
    'NC-XI-1-010': ('T. Pat Matthews', None, "'Mary A. Hicks' heads the next narrative"),
    'NC-XI-1-019': ('Mary A. Hicks', None, "'T. Pat Matthews' heads the next narrative"),
    'NC-XI-1-035': ('T. Pat Matthews', 4245, ''),
    'NC-XI-1-038': ('T. Pat Matthews', None, "'Mary A. Hicks' heads the next narrative"),
    'NC-XI-1-041': ('Mary Hicks', 4824, ''),
    'NC-XI-1-046': ('T. Pat Matthews', None, "'Travis Jordan' heads the next narrative"),
    'NC-XI-1-051': ('T. Pat Matthews', None, "'Mary A. Hicks' heads the next narrative"),
    'NC-XI-1-054': ('Travis Jordan', 6248, ''),
    'NC-XI-1-058': ('Daisy Whaley', 6617, ''),
    'NC-XI-1-070': ('T. Pat Matthews', 8066, ''),
    'NC-XI-1-074': ('Mary A. Hicks', None, "'Mrs. Edith S. Hibbs' heads the next narrative"),
    'NC-XI-2-001': ('Mrs. W.N. Harriss', 231, ''),
    'NC-XI-2-022': ('Mary Hicks', 2552, ''),
    'NC-XI-2-045': ('T. Pat Matthews', None, "'Mary A. Hicks' heads the next narrative"),
    'NC-XI-2-049': ('Miss Nancy Watkins', 5574, "'By Miss Nancy Watkins, volunteer'; 'T. Pat Matthews' heads the next narrative"),
    'NC-XI-2-057': ('T. Pat Matthews', 6431, ''),
    'NC-XI-2-059': ('T. Pat Matthews', 6588, ''),
    'NC-XI-2-065': ('Mary A. Hicks', None, "'T. Pat Matthews' heads the next narrative"),
    'NC-XI-2-068': ('T. Pat Matthews', 7552, ''),
    'NC-XI-2-076': ('Mary A. Hicks', None, "'T. Pat Matthews' heads the next narrative"),
    # ---- Ohio
    'OH-XII-012': ('Miriam Logan', 1405, ''),
    'OH-XII-014': ('Miriam Logan', 1588, ''),
    'OH-XII-020': ('Bishop', 2507, "'Bishop & Isleman / Reporter: Bishop'"),
    'OH-XII-022': ('Bishop', 2672, "'Bishop & Isleman / Reporter: Bishop'"),
    'OH-XII-028': ('Miriam Logan', 3330, ''),
    'OH-XII-029': ('Ruth Thompson', 3525, "'Ruth Thompson, Interviewing / Graff, Editing'"),
    # ---- South Carolina (writer's name in the header, or 'Interviewer:' in the footer after 'Source: <informant>')
    'SC-XIV-1-017': ('Caldwell Sims', None, 'own footer'),
    'SC-XIV-1-023': ('W. W. Dixon', None, "'Elmer Turnage' (editor) heads the next narrative"),
    'SC-XIV-1-028': ('Jessie A. Butler; Augustus Ladson', 3739, "two pieces on Henry Brown: Butler l. 3637, Ladson l. 3739; 'W. W. Dixon' heads the next narrative"),
    'SC-XIV-1-029': ('W. W. Dixon', 3894, ''),
    'SC-XIV-1-047': ('G. L. Summer', None, 'own footer'),
    'SC-XIV-1-064': ('Annie Ruth Davis', 8446, ''),
    'SC-XIV-1-065': ('W. W. Dixon', 8729, ''),
    'SC-XIV-1-068': ('Caldwell Sims', 9309, 'own footer; Elmer Turnage is the editor'),
    'SC-XIV-1-071': ('G. L. Summer', 9651, 'own footer; Elmer Turnage is the editor'),
    'SC-XIV-2-005': ('Annie Ruth Davis', 512, ''),
    'SC-XIV-2-010': ('G.L. Summer', 1356, 'own footer; Elmer Turnage is the editor'),
    'SC-XIV-2-014': ('F.S. DuPre', None, "own footer; 'Stiles M. Scruggs' heads the next narrative"),
    'SC-XIV-2-018': ('Martha S. Pinckney', 2692, ''),
    'SC-XIV-2-019': ('F.S. DuPre', 2910, "own footer ('Source: Aunt Janie Gallman'); the later pieces are Lucy and Simon Gallman (G.L. Summer)"),
    'SC-XIV-2-026': ('Phoebe Faucette', None, "'Elmer Turnage' (editor) heads the next narrative"),
    'SC-XIV-2-037': ('Annie Ruth Davis', None, "'Phoebe Faucette' (l. 5104) heads the appended piece on Rebecca Jane Grant"),
    'SC-XIV-2-043': ('Phoebe Faucette', None, "'Everett R. Pierce' heads the next narrative"),
    'SC-XIV-2-044': ('Everett R. Pierce', None, "'Elmer Turnage' (editor) heads the next narrative"),
    'SC-XIV-2-045': ('G.L. Summer', 6175, 'own footer; Elmer Turnage is the editor'),
    'SC-XIV-2-061': ('Mrs. Chlotilde R. Martin', 7996, ''),
    'SC-XIV-2-067': ('Everett R. Pierce', 9335, ''),
    'SC-XIV-3-060': ('Martha S. Pinckney', None, "'--_Martha S. Pinckney, Charleston, S.C._'"),
    'SC-XIV-4-005': ('G. Leland Summer', 530, "own footer ('SOURCE: Anne Rice'); the later pieces are Jesse and Phillip Rice (Caldwell Sims)"),
    'SC-XIV-4-021': ('Genevieve W. Chandler', None, ''),
    'SC-XIV-4-022': ('G. Leland Summer', 2331, "own footers l. 2331 and l. 2374; the last piece is Emoline Satterwhite"),
    'SC-XIV-4-044': ('W.W. Dixon', 5078, ''),
    'SC-XIV-4-049': ('Annie Ruth Davis', None, "'W.W. Dixon' heads the next narrative"),
    'SC-XIV-4-054': ('W.W. Dixon', 6229, ''),
    'SC-XIV-4-056': ('Genevieve W. Chandler', 6398, "header l. 6397-6405 stands in the 'Williams, Mary' stub segment; 'Elmer Turnage' (editor) heads the next narrative"),
    'SC-XIV-4-059': ('Annie Ruth Davis', 6719, ''),
    'SC-XIV-4-064': ('Annie Ruth Davis', 7767, ''),
}

# rows whose name stays but whose race changes: why
RACE_NOTES = {
    'AR-II-5-044': "'Name of Interviewer: Pernella Anderson' (l. 4346) heads the appended Charity Morris interview "
                   "(l. 4344-4428), not Tom Morgan's own (Irene Robertson, l. 4311-4339). The old code Black came from "
                   "the next narrative's header in the segment tail. Note: this row's snippets (l. 4367, 4371) are "
                   "from the appended interview.",
}

def surname(name):
    n = re.sub(r'\(.*?\)', ' ', name.split(';')[-1])
    toks = re.findall(r"[A-Za-z][A-Za-z'\-]+", n)
    return toks[-1].lower() if toks else ''

def find_evidence(lines, a, b, key):
    """first short line in file lines a..b (1-based, inclusive) that contains key"""
    for i in range(a - 1, min(b, len(lines))):
        t = lines[i].strip()
        if key in t.lower() and len(t) < 110: return i + 1
    return None

def main(work, raw, proj, dry=False):
    OFF = merge.file_offsets(raw)
    segs = {}
    for l in open(os.path.join(work, 'segments.jsonl')):
        r = json.loads(l); segs[r['nid']] = r
    dpath = os.path.join(proj, 'data.csv')
    rows = list(csv.DictReader(open(dpath, encoding='utf-8', newline='')))
    fields = list(rows[0].keys())
    audit, problems = [], []
    for r in rows:
        nid = r['nid']; seg = segs[nid]; off = OFF[seg['pg_id']]
        fl = merge.file_lines_of(raw, seg['pg_id'])
        old = (r['interviewer'], r['interviewer_race'], r['interviewer_race_source'], r['segment_lines'])
        a, b = seg['start_line'] + off, seg['end_line'] + off
        ev_line, note = '', RACE_NOTES.get(nid, '')
        if nid in IV:
            name, ev, note = IV[nid]
            lo = min([a] + [x for x, _ in merge.OWN_LINES.get(nid, [])])
            if name != NR:
                key = surname(name)
                if ev is None: ev = find_evidence(fl, lo, b, key)
                if ev is None or key not in fl[ev - 1].lower() or not (lo <= ev <= b):
                    problems.append(f'{nid}: no evidence line for {name!r} (line {ev})'); continue
                ev_line = ev
            r['interviewer'] = name
        elif not r['interviewer'].startswith(NR):
            # unchanged name: it must still be found in the informant's own text
            key = surname(re.split(r'[;/&]| and ', r['interviewer'])[0])
            own = '\n'.join('\n'.join(x) for x in merge.own_text(nid, seg, off, fl)).lower()
            if key and key not in own: problems.append(f'{nid}: recorded interviewer {r["interviewer"]!r} not in own text')
        race, src = merge.interviewer_race(seg, nid, off, fl)
        r['interviewer_race'], r['interviewer_race_source'] = race, src
        r['segment_lines'] = f'{a}-{b}'
        new = (r['interviewer'], race, src, r['segment_lines'])
        if new[:3] != old[:3]:
            audit.append({'nid': nid, 'informant': r['informant'], 'gutenberg_ebook': r['gutenberg_ebook'],
                          'segment_lines_old': old[3], 'segment_lines_new': new[3],
                          'interviewer_old': old[0], 'interviewer_new': new[0],
                          'interviewer_race_old': old[1], 'interviewer_race_new': new[1],
                          'interviewer_race_source_new': new[2],
                          'evidence_line': ev_line,
                          'evidence_text': fl[ev_line - 1].strip() if ev_line else '',
                          'note': note})
    for p in problems: print('PROBLEM', p)
    if problems: sys.exit(1)
    import collections
    print('rows', len(rows), '| rows with a changed interviewer column:', len(audit))
    print('  interviewer changed:', sum(x['interviewer_old'] != x['interviewer_new'] for x in audit),
          '| of these, was "not recorded":', sum(x['interviewer_old'].startswith(NR) and not x['interviewer_new'].startswith(NR) for x in audit),
          '| was another narrative\'s credit:', sum(not x['interviewer_old'].startswith(NR) and x['interviewer_old'] != x['interviewer_new'] for x in audit))
    print('  race changed:', [(x['nid'], x['interviewer_race_old'] + '->' + x['interviewer_race_new']) for x in audit if x['interviewer_race_old'] != x['interviewer_race_new']])
    print('  interviewer_race:', dict(collections.Counter(r['interviewer_race'] for r in rows)))
    print('  still "not recorded":', sum(r['interviewer'].startswith(NR) for r in rows))
    if dry: return audit
    with open(dpath, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    audit.sort(key=lambda x: x['nid'])
    with open(os.path.join(proj, 'interviewer_corrections.csv'), 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(audit[0].keys())); w.writeheader(); w.writerows(audit)
    # locator columns of corpus_screen.csv follow the corrected segmentation (flags and sample unchanged)
    cpath = os.path.join(proj, 'corpus_screen.csv')
    crow = list(csv.DictReader(open(cpath, encoding='utf-8', newline='')))
    cf = list(crow[0].keys())
    for c in crow:
        s = segs[c['nid']]; off = OFF[s['pg_id']]
        c['start_line'], c['end_line'], c['n_chars'] = s['start_line'] + off, s['end_line'] + off, s['n_chars']
    with open(cpath, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cf); w.writeheader(); w.writerows(crow)
    return audit

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], '--dry' in sys.argv)
