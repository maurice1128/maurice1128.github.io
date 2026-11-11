"""Keyword screen for religion and stratified random sample (proportional by state).
Usage: python3 -I screen_sample.py WORK_DIR
Outputs: work/screen.csv, work/sample.csv, prints summary."""
import re, sys, os, json, csv, random, collections

SEED = 20261111
N_SAMPLE = 400

# Core religion terms (dialect spellings included). "Lord", "God" and secular "meeting" excluded
# from the core screen because they are frequent exclamations or secular words; reported separately.
CORE = {
    'church': r"\bch(?:u|o)'?r?ch|\bchurch",
    'preach': r"\bpreach",
    'pray': r"\bpray|\bprayer",
    'baptiz': r"\bbaptiz|\bbaptis|\bbaptiz",
    'convert': r"\bconvert",
    'religion': r"religi|'ligion|\bligion",
    'jesus': r"\bjesus|\bjesis|\bjedus",
    'camp_meeting': r"camp[- ]meet",
    'brush_arbor': r"(brush|bush)[- ]?(arbor|arbour|harbor|harbour)|hush[- ]?(arbor|harbor)",
    'pot_turned': r"turn(?:ed|in'?|ing)? (?:a |de |the |an |dat |that )?(?:big |iron |wash |old |black )*(?:wash)?(?:pot|kettle|tub)|(?:pot|kettle)s? (?:turned|turnt|upside)",
    'sermon': r"\bsermon",
    'bible': r"\bbible",
    'deacon': r"\bdeacon",
    'revival': r"\breviv",
    'mourner': r"mourner",
    'prayer_meeting': r"pray(?:er|in'?|ing)[- ]meet",
    'sunday_school': r"sunday[- ]school",
}
BROAD = {'lord': r"\blord\b|\blawd\b", 'god': r"\bgod\b", 'meeting': r"\bmeetin"}

def hits(text, pats):
    t = text.lower()
    # street/place names are not religion mentions
    t = re.sub(r"church\s+(st\.|street|ave\.|avenue|road|hill)", " ", t)
    return {k: len(re.findall(p, t)) for k, p in pats.items()}

def main(work):
    R = [json.loads(l) for l in open(os.path.join(work, 'segments.jsonl'))]
    rows = []
    for r in R:
        h = hits(r['text'], CORE); b = hits(r['text'], BROAD)
        core_total = sum(h.values())
        rows.append({'nid': r['nid'], 'state': r['state'], 'volume': r['volume'], 'pg_id': r['pg_id'],
                     'toc_name': r['toc_name'], 'start_line': r['start_line'], 'end_line': r['end_line'],
                     'n_chars': r['n_chars'], 'core_hits': core_total,
                     'religion_mention': int(core_total > 0),
                     'religion_strong': int(core_total >= 3),
                     **{'k_' + k: v for k, v in h.items()}, **{'b_' + k: v for k, v in b.items()}})
    keys = list(rows[0].keys())
    with open(os.path.join(work, 'screen.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    n = len(rows); m = sum(r['religion_mention'] for r in rows); s3 = sum(r['religion_strong'] for r in rows)
    broad_any = sum(1 for r in rows if r['religion_mention'] or r['b_lord'] or r['b_god'])
    print(f'narratives segmented: {n}; religion mention (>=1 core term): {m} ({m/n:.1%}); >=3 core hits: {s3}; core or Lord/God: {broad_any}')
    for k in CORE:
        print(f'  {k}: narratives with term = {sum(1 for r in rows if r["k_"+k] > 0)}')
    # by state
    bys = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        bys[r['state']][0] += 1; bys[r['state']][1] += r['religion_mention']
    # stratified proportional allocation, largest remainder
    frame = [r for r in rows if r['religion_mention']]
    strata = collections.defaultdict(list)
    for r in frame: strata[r['state']].append(r)
    M = len(frame)
    quota = {s: N_SAMPLE * len(v) / M for s, v in strata.items()}
    alloc = {s: int(q) for s, q in quota.items()}
    rem = N_SAMPLE - sum(alloc.values())
    for s in sorted(quota, key=lambda s: (-(quota[s] - alloc[s]), s))[:rem]:
        alloc[s] += 1
    rng = random.Random(SEED)
    sample = []
    for s in sorted(strata):
        pool = sorted(strata[s], key=lambda r: r['nid'])
        pick = rng.sample(pool, alloc[s])
        sample.extend(sorted(pick, key=lambda r: r['nid']))
    print('state  narratives  religion_mention  sample')
    for s in sorted(bys):
        print(f'{s:5} {bys[s][0]:6} {bys[s][1]:6} {alloc.get(s, 0):6}')
    order = list(range(len(sample)))
    rng2 = random.Random(SEED + 1)
    rng2.shuffle(order)  # coding order randomised so that coder drift is not confounded with state
    with open(os.path.join(work, 'sample.csv'), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['code_order', 'nid', 'state', 'volume', 'pg_id', 'toc_name', 'start_line', 'end_line', 'core_hits'])
        for pos, k in enumerate(order):
            r = sample[k]
            w.writerow([pos + 1, r['nid'], r['state'], r['volume'], r['pg_id'], r['toc_name'], r['start_line'], r['end_line'], r['core_hits']])
    # double-coding subsample: 10% (40), drawn with seed SEED+2
    dc = random.Random(SEED + 2).sample(sorted(r['nid'] for r in sample), 40)
    with open(os.path.join(work, 'double_code_ids.txt'), 'w') as fh:
        fh.write('\n'.join(sorted(dc)) + '\n')
    print('sample size', len(sample), 'double-code ids', len(dc))

if __name__ == '__main__':
    main(sys.argv[1])
