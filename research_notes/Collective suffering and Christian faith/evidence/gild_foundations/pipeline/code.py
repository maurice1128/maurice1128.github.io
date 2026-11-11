# Rule-based coding of purposes / founders / clergy role from OCR'd Westlake columns 3-5.
# Usage: python3 -I code.py <scriptsdir> ident.tsv unit_text.json overrides.json out.csv
import sys, csv, json, re
sys.path.insert(0, sys.argv[1])
from dates import classify

ident = list(csv.DictReader(open(sys.argv[2]), delimiter='\t'))
TXT = json.load(open(sys.argv[3]))          # key "cert.sub" -> {"purpose":..,"benefits":..,"remarks":..,"rows":[..]}
try:
    OVR = json.load(open(sys.argv[4]))      # key -> {var: value, var_snip: text, check_note: ..}
except FileNotFoundError:
    OVR = {}

HDR = re.compile(r'^\W*(Friendly Benefits|to Members,?|[ia]f any\.?|Origin, Purpose,? and Religious Provisions\.?|Remarks\.?|Certificate|Place, Dedi\S*,?|and Da[ti]e of|Fou\S*ation\.?|No\.? and|Lan[gq]uage\.?)\W*$', re.I)
def norm(s):
    s = '\n'.join(l for l in s.split('\n') if not HDR.match(l.strip()))
    s = re.sub(r'(Friendly Benefits to Members, if any\.?|Origin, Purpose, and Religious Provisions\.?)', ' ', s)
    s = s.replace('\n', ' ')
    s = re.sub(r'(\w)- (\w)', r'\1\2', s)       # de-hyphenate line breaks
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def sentences(s):
    return [x.strip() for x in re.split(r'(?<=[.;])\s+', s) if x.strip()]

RULES = {
 'funeral': r'funeral|burial|\bbur(y|ied|ying|ies)\b|corpse|\bhea?rse\b|by the body|round the body|about the body|round the dead|about the dead|round the corpse|accompany (a|the) dead|to the grave|obsequ|interment',
 'masses':  r'requiem|trental|\bobit|anniversar|dirige|dirge|\b(masse?s?|masa)\b[^.;]{0,40}\b(dead|souls?|departed|deceased)\b|\b(dead|souls?)\b[^.;]{0,25}\bmasse?s?\b|pray(ers?|ing)? for [^.;]{0,30}(dead|souls?|departed)|quick and dead|living and dead|faithful departed|for (the )?souls?\b|for the soul\b|offer[^.;]{0,20}for the soul|(thirty|forty|hundred|\d+) masses|masses for',
 'chaplain': r'chaplain|\bpriest\b[^.;]{0,40}(celebrat|sing|say|maintain|found|find|hire)|(maintain|find|found|hire|keep|have)[^.;]{0,30}\bpriests?\b|chantry',
 'lights':  r'candle|taper|torch|\blights?\b|\blighta\b|lamp|\bwax\b|cierge|gild-light|candlestick|\bherse of',
 'aid':     r'poverty|poor (brethren|brothers?|sisters?|members?)|(brethren|brother|sister|member)s?[^.;,]{0,40}\b(fall|falls|fallen|become|becomes|be|are|is|in|being|grow|wax|waxes|come|comes|by)\b[^.;,]{0,20}\b(poor|sick|want|need|distress|decay|mischief|mischance|misfortune|robbed|imprison|prison|fire|shipwreck|blind|lame|aged|old age)|\bsick (brethren|brothers?|sisters?|members?)|(\d|pence|penny|d\.|shillings?|s\.)[^.;]{0,20}(weekly|a week|every week|in the week)|\bloan|\blend|relie[fv]|help[^.;]{0,30}(brethren|brother|members|fall)|bur(ial|ied|y)[^.;]{0,30}gild.?s expense|in need|accidental',
 'alms_general': r'soul-?alm|(in|for|give|gives|giving|distribute[ds]?|distributed in|as) alms|alms (to|for|among) (the )?poor|almsgiving|feed[^.;]{0,30}poor|poor of the|to the poor|\bdole|(to|for|among|feed|feeds|clothe|gives?|any|many|as|bring|by) (any |the |a |as many |certain )?poor (man|men|person|persons|people|folk|woman|women|strangers)?\b|bread[^.;]{0,30}poor|beggars|lepers|prisoners',
 'feast':   r'\b(a|one|two|their|annual|yearly|common|general|gild|great) feasts?\b(?! (of|day))|gild[- ]feast|\bfeast (together|of the gild)|common feast|\bale\b|drink|\bdine\b|dinner|\beat(s|ing)?\b|breakfast|banquet|potation|\bmeal\b|general day|morn-?speech|morrow-?speech',
 'other':   r'fabric|repair|roof|steeple|ornament|vestment|procession|pilgrim|\bplay\b|pageant|bridge|road|highway|hospital|school|teach|letters|peace|charity|love|discord|quarrel|dispute|craft|trade|mystery|workm|apprentice|wages|weights|bell',
}
# 'feast' rule includes Lynn-type 'morn-speech'/'general day' meetings ONLY together with drink/ale; see below.
OTHER_TAGS = {'fabric|repair|roof|steeple|ornament|vestment': 'church fabric/ornaments', 'procession': 'procession',
              'pilgrim': 'pilgrimage', r'\bplay\b|pageant': 'plays', 'bridge|road|highway': 'roads/bridges',
              'hospital': 'hospital', 'school': 'school', 'peace|charity|love|discord|quarrel|dispute': 'peace/charity among members',
              'craft|trade|mystery|workm|apprentice|wages|weights': 'craft regulation', 'bell': 'bells'}

CLERIC = r'\b(rector|vicar|parson|chaplains?|priests?|bishop|archdeacon|official|prior|abbot|curate|clergy|holy orders|monks?|friars?|archbishop|dean and chapter|chapter)\b'
GOV = r'punish|jurisdiction|consent|assent|keeper|\bkeep[s]? the|chest|account|elect|alderman|warden|admi(t|ssion)|officer|correct|censure|authority|oversight|audit|ordinance|rule|govern|custos|master|supervis|counsel|advice|approv|seal|key'
EXCL = r'\bno (chaplain|priest|clerk|one in holy orders|cleric)|not be (admitted|an officer)[^.;]{0,40}' + CLERIC + r'|' + CLERIC + r'[^.;]{0,40}(shall not|may not|cannot) be (admitted|a member|an officer)|in holy orders may'
FOUNDV = r'found(ed|ing)?|begun|began|formed|ordained|instituted|established|started|associated|set up|caused'
CRAFT_WORDS = r'tilers|sailors|tailors|cordwainers|barbers|masons|fullers|weavers|mercers|minstrels|actors|archers|coifmakers|cobblers|tanners|carpenters|peltyers|saddlers|spurriers|painters|pouchmakers|girdlers|brewers|cutlers|glovers|whittawyers|candlemakers|artificers|shipman|shipmen|smiths|shepherds|merchants|gild merchant|young merchants'

def find(rule, text):
    hits = []
    for s in sentences(text):
        if re.search(rule, s, re.I):
            hits.append(s)
    return hits

out = []
prev_by_cert = {}
for k, x in enumerate(ident):
    key = x['cert'] + ('.' + x['sub'] if x['sub'] else '')
    t = TXT.get(key, {'purpose': '', 'benefits': '', 'remarks': '', 'rows': []})
    P, B, R = norm(t.get('purpose', '')), norm(t.get('benefits', '')), norm(t.get('remarks', ''))
    inherit = ''
    m = re.search(r'(general purpose|regulations?|ordinances?|word for word|same|purpose|mutatis mutandis)\s+(as|is )?\s*in (\(([a-z]|[ivx]+)\.?\)|(no\.\s*)?(\d+))', P, re.I) or re.search(r'^\W*as in (\(([a-z]|[ivx]+)\.?\)|(no\.\s*)?(\d+))', P, re.I)
    if m:
        ref = m.group(0)
        n = re.search(r'\d+', ref)
        l = re.search(r'\(([a-z]|[ivx]+)\.?\)', ref)
        if l:
            inherit = x['cert'] + '.' + l.group(1)
        elif n:
            inherit = n.group(0)
    BODYC = r'body (and blood )?of (our lord |jesus |)christ|body of our lord|body of god|precious body|the body of the lord'
    P = re.sub(BODYC, 'CORPUSXP', P, flags=re.I); R = re.sub(BODYC, 'CORPUSXP', R, flags=re.I)
    if key in OVR and 'inherit_from' in OVR[key]:
        inherit = OVR[key]['inherit_from']
    full = ' '.join([P, R])
    base = full
    if inherit:
        src = TXT.get(inherit) or TXT.get(inherit + '.a') or TXT.get(inherit + '.i') or {}
        base = full + ' ' + norm(src.get('purpose', ''))
    base = re.sub(r'no craft statutes', '', base, flags=re.I)
    row = {'unit_id': 'G%04d' % (k + 1)}
    row.update({c: x[c] for c in ['cert', 'sub', 'lang', 'county', 'place', 'dedication', 'church_note', 'page']})
    row['pdf_page'] = int(x['page']) + 24
    row['ocr_rows'] = ';'.join(t.get('rows', []))
    row['date_raw'] = x['date_raw']
    row.update(classify(x['date_raw']))
    row['decade'] = (int(row['found_year']) // 10 * 10) if row['found_year'] != '' else ''
    # pestilence mention anywhere in the unit
    pest = find(r'pestilen|plague|mortalit|great death|qualm|estilen|pestil|lague\b', ' '.join([x['date_raw'], P, B, R]))
    row['pest_mention'] = 1 if pest else 0
    row['pest_snippet'] = ' | '.join(pest)[:400]
    content = len(re.findall(r'[A-Za-z]{3,}', P + ' ' + B)) >= 3 or bool(inherit)
    row['content_free'] = 0 if content else 1
    for v, rule in RULES.items():
        if v == 'aid':
            hits = find(rule, base)
            if len(re.findall(r'[A-Za-z]{3,}', B)) >= 2 and not re.match(r'^\W*(none|nil|no\b)', B, re.I):
                hits = ['[benefits col.] ' + B] + hits
        elif v == 'feast':
            LCF = r'(?i:(?<!on )(?<!after )(?<!before )(?<!of )(?<!within )(?<!at )(?<!said )(?<!until )(?<!till )(?<!from )(?<!in )(?<!for ))\b(to|the|re|their|a|one|two) feasts?\b(?!\s*(of|day|-day|days)\b)'
            hits = [h for h in find(rule + '|' + LCF, base + ' ' + B) if re.search(LCF, h) or not re.search(r'^(?!.*(ale|drink|dine|dinner|eat|breakfast|banquet|potation|meal|gild[- ]feast|feast together|common feast|(a|one|two|their|annual|yearly|common|general|gild|great) feasts?\b(?! (of|day)))).*$', h, re.I)]
        else:
            hits = find(rule, base + (' ' + B if v in ('funeral', 'masses', 'alms_general') else ''))
        if v == 'chaplain':
            hits = [h for h in hits if not re.search(r'\bno (chaplain|priest)|chaplains? (shall|may) not|not[^.;]{0,20}chaplain', h, re.I) or re.search(r'maintain|find|celebrat', h, re.I)]
        row[v] = 1 if hits else 0
        row[v + '_snip'] = (' | '.join(hits))[:300]
    tags = sorted(set(lab for pat, lab in OTHER_TAGS.items() if re.search(pat, base, re.I)))
    row['other_text'] = '; '.join(tags)
    # founders
    ftxt = ' '.join([x['date_raw'], P, R])
    CLW = r'((?i:priests?|chaplains?|rector|vicar|parson|monk|clerks?|prior|abbot|bishop|friars?|canons?|curate)|[Ss]ir [A-Z][a-z]+)'
    LAYW = r'((?i:parishioners|men|women|persons|people|burgesses|citizens|townsmen|brethren|brothers|sisters|neighbours|inhabitants|merchants|scholars|minstrels|commonalty|commons)|[A-Z][a-z]+ (de |le |atte |of )?[A-Z][a-z]+(,)? (and|with) (others|certain|\d+ others|other))'
    FV = r'(?i:(found(ed|ing)?|begun|began|beginning|formed|ordained|instituted|established|started|set up|caused|associated|devised|made (this|the) (gild|fraternity)))'
    cl, lay = [], []
    for s_ in sentences(ftxt):
        c1 = re.search(FV + r'[^.;]{0,15}\bby\b[^.;]{0,50}\b' + CLW + r'\b', s_) or re.search(r'\b' + CLW + r'\b[^.;]{0,40}\b' + FV + r'\b[^.;]{0,20}\b(gild|fraternity|brotherhood)', s_) or re.search(r'(?i:devotion of (the|certain)) ' + CLW, s_)
        l1 = re.search(FV + r'[^.;]{0,15}\bby\b[^.;]{0,50}\b' + LAYW, s_) or re.search(r'\b(certain|devout|good|poor|young|the|some|\d+|twenty|six|five|ten|nine) ?(devout |good |poor |young )?' + LAYW + r'\b[^.;]{0,80}\b' + FV, s_) or re.search(r'[A-Z][a-z]+ (de |le |atte |of )?[A-Z][a-z]+[^.;]{0,30}(and|with) (others|certain|other)[^.;]{0,80}' + FV, s_) or re.search(r'(?i:devotion of the (townsmen|parishioners|people|men))', s_)
        if c1: cl.append(s_)
        if l1 and not (c1 and not re.search(r'\band\b', s_)): lay.append(s_)
    craft = bool(re.search(CRAFT_WORDS, x['dedication'], re.I)) or bool(re.search(r'\b(craft|mystery)\b', P, re.I))
    clerk = bool(re.search(r"clerk'?s'? gild|clerks of", x['dedication'] + ' ' + P, re.I))
    if clerk:
        f, fs = 'clergy', 'clerks\' gild: ' + x['dedication']
    elif cl and lay:
        f, fs = 'mixed', ' | '.join(cl + [l for l in lay if l not in cl])
    elif cl:
        f, fs = 'clergy', ' | '.join(cl)
    elif craft:
        f, fs = 'craft', x['dedication']
    elif lay:
        f, fs = 'parishioners', ' | '.join(lay)
    else:
        f, fs = 'not_stated', ''
    if 'parishioners of st. magnus' in x['date_raw'].lower():
        f, fs = 'parishioners', x['date_raw']
    row['founders'] = f
    row['founders_snip'] = fs[:300]
    gov = [s for s in sentences(' '.join([P, B, R])) if re.search(CLERIC, s, re.I) and re.search(GOV, s, re.I) and not re.search(EXCL, s, re.I)]
    exc = [s for s in sentences(' '.join([P, B, R])) if re.search(EXCL, s, re.I)]
    row['clergy_gov'] = 1 if gov else 0
    row['clergy_excluded'] = 1 if exc else 0
    row['clergy_snip'] = ' | '.join(gov + ['[excl] ' + e for e in exc])[:300]
    row['inherit_from'] = inherit
    row['text_purpose'] = P
    row['text_benefits'] = B
    row['text_remarks'] = R
    row['check_note'] = ''
    o = OVR.get(key)
    if o:
        for kk, vv in o.items():
            row[kk] = vv
        if 'found_year' in o or 'date_class' in o:
            row['decade'] = (int(row['found_year']) // 10 * 10) if row['found_year'] not in ('', None) else ''
    out.append(row)

fields = list(out[0].keys())
w = csv.DictWriter(open(sys.argv[5], 'w', newline=''), fieldnames=fields)
w.writeheader(); w.writerows(out)
print(len(out), 'units written')
