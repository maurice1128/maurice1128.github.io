"""Rule-based coder for Husting will entries (project husting_wills).
Implements codebook.md. Deterministic: same input -> same output.
Usage: python3 -I code_wills.py wills.json out.csv [--with-text]

Amended 2026-11-11 after the independent audit (see results.md, change log):
  (1) the burial-clause rule now also matches "TO be buried" and the misprint "To he buried"
      (five entries were missed);
  (2) two descriptive columns were added for wills with a chantry or obit: holder_private_named
      (a wife, heir, executor or other private person is named in the chantry/obit sentence)
      and parish_body_kind (rector_only / lay_only / both). No other rule was changed.
"""
import sys, re, json, csv

VARS = ['parish', 'chantry', 'obit', 'masses', 'lights', 'fraternity', 'friars', 'monastic',
        'hospital', 'charity', 'cathedral', 'named_chaplain', 'pious_uses', 'pestilence']

# ---------------------------------------------------------------- text helpers
ABBR = re.compile(r'\b(SS|S|St|V|H|Knt|co|viz|Ed|Dr|fn|temp|vol|No|Bp|[A-Z])\.(?=\s|,|\))')


def protect(t):
    t = t.replace('A.D.', 'A§D§').replace('&c.', '&c§')
    t = ABBR.sub(lambda m: m.group(1) + '§', t)
    return t


def unprotect(t):
    return t.replace('§', '.')


def sentences(t):
    """Split protected text into sentences; '&c§' followed by capital also ends a sentence."""
    t = re.sub(r'&c§(\s+)(?=["(\[]?[A-Z])', r'&c§.\1', t)
    parts = re.split(r'(?:(?<=[.?!])|(?<=[.?!]["\')\]]))\s+(?=["(\[]?[A-Z0-9])', t)
    return [p for p in parts if p.strip()]


def snip(s, a, b, w=70):
    return unprotect(s[max(0, a - w):min(len(s), b + w)]).strip()


# ---------------------------------------------------------------- church referents
RELIGIOUS_HOUSE = re.compile(
    r"Christ ?Church|Cristchirche|H§ Trinity(?! the Less)(?! the Little)(?! de Kyrion)|Holy Trinity(?! the Less)|"
    r"S§ Mary Over|S§ Mary de Overe|Overhee|Overey|S§ Elen|S§ Helen|Clerkenwell|Clerconwell|Clerkenewell|Clerkenwelle|"
    r"S§ Bartholomew(?! the L)[^,;]{0,25}Sm[ey]the?feld|"
    r"\b(?:Haliwell|Halywell|Westminster|Bermundes\w*|Bermondes\w*|Charterhous\w*|Charturhous\w*|Chartrehous\w*|Minoress\w*|"
    r"Kilburn|Kelleburn\w*|Kellebourn\w*|Merton|Graces|Eastminster)\b|S§ Clare|S§ Martin le Gran[dt]|S§ Thomas (?:de )?Ac(?:on|res)|"
    r"(?<!S§ )(?<!S§ [A-Z][a-z]{2})(?<!S§ [A-Z][a-z]{3})(?<!S§ [A-Z][a-z]{4})(?<!S§ [A-Z][a-z]{5})(?<!S§ [A-Z][a-z]{6})(?<!S§ [A-Z][a-z]{7})"
    r"(?<!S§ [A-Z][a-z]{8})(?<!de )\b(?:Stratford\w*|Berkyng\w*|Barking)\b|"
    r"\b(?:abbey|priory|Abbey|Priory|convent|Convent|monastery|nunnery)\b",
)
HOSPITAL_NAME = re.compile(
    r"hospital|Hospital|spital|Spital|spitel|Spitel|Elsyng|Elsing|S§ Mary without Biss?hop|S§ Mary without Bisshop|"
    r"Bedlem|Bethlem|le lok|le loke|Meselcot|S§ Giles(?: without| in| de)? (?:the fields|Holbourne|Holeburne|Holborne|Holburn)|"
    r"S§ Katherine (?:near|by) the Tower|S§ Anthon|S§ Antony(?! near)|S§ Thomas (?:of|in|de) Suthwerk")
FRIARS_NAME = re.compile(r"[Ff]riars?|[Ff]reres|Minors|Preachers|Carmelite|Crutched|Crouched|Crossed Friars|Pied|Fratrum")
STPAULS = re.compile(r"S§ Paul(?!'s (?:Gate|Wharf|Chain|Cross|Brewhouse|Bakehouse))|Paul's (?:Church|church|cathedral)|cathedral church|Pouls")


def classify_church(name):
    if STPAULS.search(name):
        return 'st_pauls'
    if FRIARS_NAME.search(name):
        return 'friars'
    if HOSPITAL_NAME.search(name):
        return 'hospital'
    if RELIGIOUS_HOUSE.search(name):
        return 'religious_house'
    return 'parish'


CHURCH_REF = re.compile(
    r"(?P<anaph>(?:the |its )?(?:said |same |aforesaid |above-mentioned |above |last-mentioned )(?:parish )?(?:church|chapel)(?: of [^,;]{1,50}?)?(?= aforesaid|[,;.]| and | for | in | to | with | wherein| where| as )|"
    r"the (?:parish )?church aforesaid|the same church|the church(?= and | for |,)|(?:thereof|therein|of the same)(?=[,;. ])|(?<=of )which\b|(?<=to )which\b|(?<=to )whom\b)"
    r"|(?P<named>(?:the )?(?:parish |conventual |priory |abbey |collegiate |cathedral )?(?:church|chapel)(?:es)? of (?:the )?[^,;()]{1,70}?(?=[,;()]| and | for | in | to | with | wherein| where| as | near| without| within| at |\.(?:\s|$)))"
    r"|(?P<named2>Christ ?Church|S§ Paul's(?: Church| church)?|(?:the )?(?:new |old )?work of S§ Paul'?s?)")

GIFT_TAIL = re.compile(
    r"(?:\bto|\bunto|\bamong|\bbetween)\s+(?:the\s+)?(?:said\s+)?$|"
    r"\b(?:fabric|work|works|repair|repairs|rebuilding|building|rector|rectors|vicar|parson|ministers?|chaplains?|clerks?|"
    r"churchwardens?|wardens|parishioners|high altar|altars?|rood|ornaments?|bells?|belfry|steeple|tower|chancel|nave|roof|font|"
    r"image|crucifix|fermer|use|uses|benefit|keeper|keepers|masters|procurators|curate|priests?|almonry|treasury|"
    r"Prior|Prioress|Abbot|Abbess|Convent|convent|Dean|Chapter|canons|nuns|monks|brethren|sisters)\b"
    r"[^;]{0,45}?\b(?:of|to|in aid of|towards|for)\s+(?:the\s+)?(?:said\s+)?$", re.I)
LOC_TAIL = re.compile(
    r"(?:\bburied|\bnear|\bnigh|\bnext|\bopposite|\bagainst|\btowards the|\badjoining|\bbeside|\bwithout|\bwithin|\bat|\bupon|"
    r"\bparish of|\bparishes of|\bheld of|\bheld under|\bholden of|\bfee of|\bpayable to|\bpaid to|\bdue to|\bin|\bfrom|"
    r"\bchantr(?:y|ies)|\blight|\blights|\blamp|\btaper|\btapers|\bcalled|\bstreet|\blane|\bclose of)\s+(?:the\s+)?(?:said\s+)?$", re.I)
LIST_START = re.compile(r"(?:Bequests?(?: also)?(?: of [^,;]{0,40})? to|[Ll]eaves (?:sums of money|bequests|money|legacies) to|"
                        r"\bTo\b|\bto\b(?: each of)?|divided (?:equally )?(?:among|between)|[Bb]equeaths?|gives)\b")


def gift_context(clause_before):
    """Decide whether a referent at the end of clause_before is a beneficiary."""
    tail = clause_before[-90:]
    if re.search(r"(?:pious|charitable) (?:and charitable )?(?:uses|purposes) (?:in|of|at)\s+(?:the\s+)?(?:said\s+)?$", tail):
        return True
    if re.search(r"advowson|a certain\s+$", tail):
        return False
    if LOC_TAIL.search(tail):
        return False
    if GIFT_TAIL.search(tail):
        return True
    # list continuation: "..., the church of X" / "and the church of X" after a gift marker in the same clause
    if re.search(r"(?:,|\band|\bas also|\balso)\s+(?:to\s+)?(?:the\s+)?$", tail) and LIST_START.search(clause_before):
        # make sure no location word governs the list
        last = re.split(r"[,]", clause_before)
        return True
    return False


# ---------------------------------------------------------------- other detectors
ADDR_BEFORE = re.compile(
    r"(?:\bnear|\bnigh|\bnext|\bopposite|\bagainst|\btowards|\badjoining|\bbeside|\bby|\bwithout|\bwithin|\bat|\bupon|\bin|"
    r"\bparish of|\bparishes of|\bheld of|\bheld under|\bholden of|\bfee of|\bpayable to|\bpaid to|\bdue to|\bpaying to|\bfrom|"
    r"\bstreet|\blane|\bgate|\bcalled|\bbetween|\bof the|\bwharf|\bburied)\s+(?:the\s+)?(?:house of\s+)?(?:the\s+)?(?:church of\s+)?(?:the\s+)?$", re.I)

FRIARS_PAT = re.compile(
    r"(?<!Friar )(?:(?:four|five|several|divers|various|principal|mendicant|the|each)\s+)?(?:orders? of (?:mendicant )?friars|"
    r"(?:Friars? )?(?:Minors|Preachers)|Preaching Friars|Carmelite Friars|Carmelites|Augustinian Friars|Austin Friars|Friars Augustin\w*|"
    r"Crutched Friars|Crouched Friars|Crossed Friars|Pied Friars|Friars of the Sack|friars(?! Minor)|Friars(?! Minor)|Friars Minors|Fratrum)")
MONASTIC_PAT = re.compile(
    r"\b(?:Prior(?:ess)?|Abbot|Abbess|Master)s? and (?:Convent|Canons|Nuns|Monks|Brethren|Sisters|Chapter)|"
    r"(?<!Minor )\b(?:the |each )?(?:convents?|nuns|monks|canons(?! of S§ Paul)|religious (?:orders|houses|men|women)|monastic orders|religious|"
    r"abbey|priory|nunnery|Charterhouse|Charturhous\w*|Chartrehous\w*|Minoresses|Sisters Minor\w*|recluses?|anchoress|anchorite|"
    r"S§ Thomas (?:de )?Ac(?:on|res))\b", re.I)
HOSPITAL_PAT = re.compile(
    r"\bhospitals?\b|\bspital\w*|\bspitel\w*|Elsyng\w*|\blepers?\b|\blazar|\ble lok\w*|Meselcot\w*|Bedlem|Bethlem|"
    r"S§ Mary without Biss?h?op\w*gate", re.I)
CHARITY_PAT = re.compile(
    r"\bpoor\b|\bpoorest\b|\bpaupers?\b|\bneedy\b|\bindigent|\bbedridden|\bbedrid\b|\bprisoners?\b|\bprisons?\b|\binmates of Neugate|\bNeugate\b(?! Street)|"
    r"\bhighways?\b|\broads?\b|\bcauseway|\bcauce\w*|\bpavement|\bbridges?\b|\bBrigge\b|\bbrugge\b|\balmshouse|"
    r"marriage of poor|maidens", re.I)
CHARITY_BRIDGE_ADDR = re.compile(r"(?:near|by|at|upon|of the|without|beyond|on|Ward|Street|street|towards|held (?:of|under)(?: the)? (?:Wardens of)?|Wardens of)\s+(?:the\s+)?(?:London\s+)?$")
CATHEDRAL_PAT = re.compile(
    r"(?:Dean and Chapter|fabric|work|works|new work|old work|shrine|chaplains|minor canons|almonry|indulgence|pardon|altar|"
    r"chantry|crucifix|image|church|cathedral church|treasury|college|canons)[^;.]{0,25}?S§ Paul|"
    r"\b(?:to|for) (?:the )?(?:church of )?S§ Paul(?:'s)?(?! (?:Gate|Wharf|Chain|Cross))|S§ Paul's (?:Church|church|cathedral)(?! ?yard)")

CHANTRY_PAT = re.compile(
    r"chantr(?:y|ies)|chauntr\w*|cantar\w*|(?:chaplains?|priests?)[^.;]{0,40}?\b(?:to (?:celebrate|pray|sing|say)|celebrating|to be maintained|to be found)|"
    r"(?:maintenance|maintain|maintaining|support|supporting|find|finding|provide|providing|sustentation|stipend|salary) (?:of )?(?:a |one |two |three |four |five |six |\w+ )?(?:honest |fit |suitable )?(?:chaplains?|priests?)\b|"
    r"\bcelebrat\w+ (?:divine service|masses|for (?:the good of )?(?:his|her|the) souls?)|divine service", re.I)
OBIT_PAT = re.compile(r"\bobits?\b|anniversar\w*|year'?s mind|\bobitus", re.I)
MASSES_PAT = re.compile(r"\bmasses\b|\btrentals?\b|\btrigintals?\b|\brequiem\b|\bPlacebo\b|\bDirige\b|\bmass\b(?! of (?:silver|gold))", re.I)
LIGHTS_PAT = re.compile(r"\blights?\b|\blighting\b|\blamps?\b|\btapers?\b|\btorch(?:es)?\b|\bcandles?\b|\bcandelabr\w*|\bwax\b(?![- ]?chandler)|\bcierges?\b|\bcerges?\b|\bmortars\b", re.I)
FRAT_PAT = re.compile(r"\bfraternit(?:y|ies)\b|\bbrotherhoods?\b|\bconfraternit\w*|\bgilds?\b|\bguilds?\b(?!hall)|\bGild\b(?!hall)|\bfraternitas", re.I)
PIOUS_PAT = re.compile(r"pious (?:and charitable )?(?:uses|purposes|works)|charitable (?:uses|purposes|works)|works of (?:piety|charity|mercy)", re.I)
PEST_PAT = re.compile(r"pestilen\w*|\bplague\w*|mortalit\w*|epidemic\w*|\bpestis\b|\bmorina\b", re.I)
NAMED_CHAP = re.compile(r"(?:\bSir [A-Z][a-z]+(?: (?:de )?[A-Z][a-z]+)?|[A-Z][a-z]+ (?:de )?[A-Z][a-z]+, (?:a |the )?(?:chaplain|priest))", )
PRAYER = re.compile(r"celebrat\w*|\bpray\w*|\bmass(?:es)?\b|chantr\w*|divine service|trental|soul", re.I)

PERPETUAL = re.compile(r"perpetu\w*|for ever|for evermore|in mortmain|their successors|his successors|amortis|mortmain", re.I)
TEMPORARY = re.compile(r"for (?:the (?:first|space of|term of) )?(?:a term of )?(?:\w+|\d+) (?:whole )?years|for (?:one|a) year|for the term of|during the (?:life|lifetime)|for life|for (?:his|her|their) lives|years next", re.I)

TRUSTEE = {
    'lay_corporate': re.compile(r"Mayor|Commonalty|Aldermen|Chamberlain(?: of (?:the City|London|the Guildhall))|Wardens of (?:the )?(?:London )?Bridge|"
                                r"mistery|craft of|wardens of the (?:mistery|craft|trade|company|art)|Fraternit\w+|fraternit\w+|Gild\b|gild\b|"
                                r"Goldsmithery|Company of"),
    'parish_body': re.compile(r"churchwardens?|parishioners|wardens of the (?:said |same )?(?:church|fabric|works?)|\brector and\b|\brectors? (?:of the said church )?and (?:churchwardens|parishioners|wardens)|good men of the parish", re.I),
    'church_corporate': re.compile(r"Dean and Chapter|Prior(?:ess)? and (?:Convent|Canons|Nuns)|Abbot and Convent|Abbess and Convent|Master and Brethren|Warden and Brethren|"
                                   r"Master and (?:Chaplains|Fellows)|Minor Canons|college of|College of|their successors", re.I),
}
SOULS = re.compile(r"(?:for (?:the )?(?:good|welfare|health|benefit) of )?(?:(?:his|her|their|the|my) )?(?:own )?souls?\b[^;.]*", re.I)
PRIVATE_HOLDER = re.compile(r"\b(?:wife|husband|sons?|daughters?|heirs?|executors?|brothers?|sisters?|kinsm[ae]n|kinswom[ae]n|nephews?|"
                            r"nieces?|mother|father|apprentices?|servants?|feoffees?|assigns)\b", re.I)
PB_RECTOR = re.compile(r"\b(?:rectors?|vicars?|parsons?)\b", re.I)
PB_LAY = re.compile(r"churchwardens?|parishioners|wardens of the (?:said |same )?(?:church|fabric|works?)|good men of the parish", re.I)
LAY_EXCL = re.compile(r"(?:held (?:of|under)|by grant of|holden of|leasehold)[^.;]{0,40}(?:Mayor|Commonalty|Wardens)", re.I)


def header(text):
    m = re.match(r'^"?\s*([^(—]{1,60}?)"?\s*\(([^)]*)\)\s*"?([^—]{0,200}?)\s*—', text)
    if m:
        return m.group(1).strip(' "'), m.group(2).strip(), m.group(3).strip(' ,."')
    m = re.match(r'^([^—.]{1,120})[—.]', text)
    return (m.group(1).strip() if m else text[:60]), '', ''


FEMALE_NAMES = set('''Agnes Alice Alicia Amicia Amisia Anabilla Anne Avice Beatrice Basilia Cecilia Cecily Christina Cristina Clarice Constance
Dionisia Denise Edith Eleanor Elena Elianora Elienora Elizabeth Ellen Emma Felicia Floria Gena Godiva Helen Idonea Isabella Isabel Isolda Ismania
Johanna Joan Juliana Katherine Leticia Lettice Lucy Lucia Mabel Mabilia Margaret Margery Mariota Mary Matilda Maud Muriel Nichola Petronilla
Philippa Rose Roesia Sabine Sarah Sibil Sibilla Tiffany Thomasina Agatha Athelina Alienora Amy Avelina Benedicta Clemence Desiderata Egidia
Gonnora Hawisia Ida Joyce Laura Lora Mabil Mathilda Massilia Olive Sabina Sibyl Susanna Alianora Aleyse Helewisa Rohesia Wymarca Grace Elisabeth
Agnete Emota Annora Leuota Leticia Alina Alianor Avis Mariona Christiana Dulcia Eva Felicity Iseult Joan Juette Mazeline'''.split())


def sex_of(name_paren, text):
    p = name_paren
    if re.search(r'\b(wife|relict|widow|daughter|Dame|Lady|Prioress|Abbess)\b', p):
        if not re.search(r'\bson\b', p.split(',')[0]):
            return 'F'
    first = re.split(r'[ ,]', p.strip())[0] if p else ''
    if first in FEMALE_NAMES:
        return 'F'
    her = len(re.findall(r'\b(?:her|she)\b', text[:600]))
    his = len(re.findall(r'\b(?:his|he|him)\b', text[:600]))
    if her > his and her >= 2:
        return 'F'
    return 'M'


def code(r):
    text = r['text']
    out = {}
    name, paren, occ = header(text)
    out['testator'] = (name + (' (' + paren + ')' if paren else '')).strip()
    if not occ and paren:
        mm = re.search(r',\s*(late\s+)?([a-z"][^,]*)$', paren)
        occ = ''
        mm2 = re.search(r'(?:late |, )([a-z"][\w" -]+)$', paren)
        if mm2 and re.search(r'relict|wife|widow', paren):
            occ = 'relict of ' + mm2.group(1).strip()
    out['occupation'] = occ
    out['sex'] = sex_of(paren, text)
    cl = re.search(r'chaplain|clerk|rector|vicar|parson|canon|priest|prebendary|dean|archdeacon|minister of the church|Rector|Parson|Canon|Vicar', occ + ' ' + name + ' ' + paren)
    sir = paren.startswith('Sir') and 'Knt' not in occ and 'knight' not in occ.lower()
    out['cleric'] = 1 if (cl or sir) else 0
    m = re.search(r'Dated[^.]*?A\.D\. (\d{4})', text) or re.search(r'A\.D\. (\d{4})\.?\s*(?:Roll|$)', text)
    out['will_year'] = m.group(1) if m else ''
    out['empty_entry'] = 1 if re.search(r'Vacant space|\[No will\]', text) or len(text) < 60 else 0

    P = protect(text)
    # strip the header (name and occupation) from coded text
    body_start = P.find('—')
    if body_start < 0 or body_start > 300:
        body_start = 0
    B = P[body_start + 1:] if body_start else P
    # drop trailing roll locator and later court notes are kept
    snips = {v: [] for v in VARS}
    flags = {v: 0 for v in VARS}

    def hit(v, s, a, b):
        flags[v] = 1
        if len(snips[v]) < 3:
            snips[v].append(snip(s, a, b))

    burial_site = 'none_stated'
    last_church_type = None
    sents = sentences(B)
    chantry_sents = []
    for s in sents:
        work = s
        # ---- burial clause
        bm = re.search(r"(?:If (?:he|she) die[^,]*,\s*)?(?:desires? |wills? |directs? )?(?:[Tt][Oo] [bh]e buried|[Bb]ody to be buried|desires? burial|[Hh]is burial (?:to be )?(?:in|at))[^;]*?(?=;|, to (?:the|which|whose)|, and (?:he |she )?leaves|$)", work)
        if bm:
            bt = bm.group(0)
            if burial_site == 'none_stated':
                if STPAULS.search(bt) or re.search(r"Pardon|Pardoun", bt):
                    burial_site = 'st_pauls'
                elif FRIARS_NAME.search(bt):
                    burial_site = 'friars'
                elif HOSPITAL_NAME.search(bt):
                    burial_site = 'hospital'
                elif RELIGIOUS_HOUSE.search(bt):
                    burial_site = 'religious_house'
                elif re.search(r"church|chapel|churchyard|cemetery|chancel", bt):
                    burial_site = 'parish'
                else:
                    burial_site = 'other_or_unspecified'
            # referent for "said church"
            cm = re.search(r"(?:church|chapel|churchyard)(?:yard)? of [^,;]+|Christ ?Church|S§ Paul's|[A-Z][^,;]{0,40} church", bt)
            if cm:
                last_church_type = classify_church(bt[max(0, cm.start() - 25):cm.end()])
            elif burial_site != 'none_stated':
                last_church_type = {'st_pauls': 'st_pauls', 'friars': 'friars', 'hospital': 'hospital',
                                    'religious_house': 'religious_house'}.get(burial_site, 'parish')
            work = work[:bm.start()] + ' ' * len(bt) + work[bm.end():]

        # ---- church referents (parish / cathedral / religious / friars / hospital)
        for cm in CHURCH_REF.finditer(work):
            reftext = cm.group(0)
            if cm.group('named') or cm.group('named2'):
                ctype = classify_church(reftext)
            else:
                ctype = last_church_type or 'parish'
            before = work[:cm.start()]
            clause_before = re.split(r';', before)[-1]
            is_gift = gift_context(clause_before)
            if is_gift:
                v = {'parish': 'parish', 'st_pauls': 'cathedral', 'friars': 'friars', 'hospital': 'hospital',
                     'religious_house': 'monastic'}[ctype]
                hit(v, work, cm.start(), cm.end())
                if re.match(r"(?:the )?(?:\w+ )?churches of", reftext):
                    # plural list: classify each listed dedication up to the end of the clause
                    rest = work[cm.start():]
                    rest = re.split(r";|\balso\b|(?<=[a-z])\.\s", rest)[0]
                    for item in re.split(r",|\band\b", rest[len(reftext):]):
                        it = item.strip()
                        if re.match(r"(?:of )?(?:the )?(?:S§|SS§|H§|All|St§|Christ|Holy|Our)", it):
                            t2 = classify_church(it)
                            v2 = {'parish': 'parish', 'st_pauls': 'cathedral', 'friars': 'friars', 'hospital': 'hospital',
                                  'religious_house': 'monastic'}[t2]
                            hit(v2, work, cm.start(), cm.start() + len(reftext) + 40)
            if cm.group('named') or cm.group('named2'):
                last_church_type = ctype
        # high altar / tithes -> parish (unless cathedral or religious named next to it)
        for m in re.finditer(r"high altar|tithes|oblations (?:forgotten|omitted|withheld)|forgotten tithes", work, re.I):
            nxt = work[m.end():m.end() + 70]
            if re.search(r"S§ Paul|Friars|Christ ?Church|Prior|convent", nxt):
                continue
            pre = work[max(0, m.start() - 40):m.start()]
            if re.search(r"\b(?:before|near|at|beside|towards|opposite)\s+(?:the\s+)?$", pre):
                continue
            ref = last_church_type or 'parish'
            hit('parish' if ref == 'parish' else {'st_pauls': 'cathedral', 'friars': 'friars', 'hospital': 'hospital', 'religious_house': 'monastic'}[ref], work, m.start(), m.end())
        for m in re.finditer(r"\b(?:rector|vicar|parson|churchwardens?|parishioners|parish chaplains?|parish clerk)\b", work, re.I):
            pre = work[max(0, m.start() - 60):m.start()]
            if re.search(r"\b(?:to|To|Bequests? to|leaves to|remainder to|go to|,|and)\s+(?:the\s+)?(?:said\s+)?(?:Sir [A-Z]\w+(?: [A-Z]\w+)?,?\s*)?$", pre) and \
                    not re.search(r"(?:held of|patron|presentation|by|of|parish of)\s+(?:the\s+)?$", pre):
                if not re.search(r"Rector of the church|Parson of the church", unprotect(r['text'][:150])) or m.start() > 0:
                    hit('parish', work, m.start(), m.end())

        # ---- friars
        for m in FRIARS_PAT.finditer(work):
            pre = work[max(0, m.start() - 60):m.start()]
            seg = m.group(0)
            if re.search(r"Friar [A-Z]", work[max(0, m.start() - 1):m.end() + 3]) and not re.search(r"Friars", seg):
                continue
            if ADDR_BEFORE.search(pre) and not re.search(r"\bto (?:the |each of the |each )?$", pre):
                continue
            if re.search(r"(?:of|in) the (?:Order|order) of (?:the )?$", pre) or re.search(r"(?:his|her) (?:son|brother|sister|kinsman|nephew|confessor|uncle)[^.;]{0,30}$", pre):
                continue
            if re.search(r"(?:a|one|the) friar(?! of)", seg):
                continue
            hit('friars', work, m.start(), m.end())
        # ---- monastic
        for m in MONASTIC_PAT.finditer(work):
            pre = work[max(0, m.start() - 60):m.start()]
            if ADDR_BEFORE.search(pre) and not re.search(r"\bto (?:the |each )?$", pre):
                continue
            if re.search(r"held (?:of|under)|rent (?:due|payable|paid)|quitrent[^.;]{0,30}$|(?:his|her) (?:son|daughter|sister|brother|kinsman|niece)[^.;]{0,40}$|\ba (?:sister|nun|monk|canon) (?:in|of)\s+(?:the\s+)?$|seised|feoffment|by deed", pre, re.I):
                continue
            if re.search(r"^(?:religious)$", m.group(0), re.I) and not re.search(r"religious (?:orders|houses|men|women)", work[m.start():m.end() + 10], re.I):
                continue
            after = work[m.end():m.end() + 45]
            if re.search(r"^[^;]{0,12}\b(?:of )?the (?:New )?(?:Hospital|hospital|spital)|^[^;]{0,25}(?:Elsyng|spitel|Spitel|spital)", after) and not re.search(r"S§ John of Jerusalem|S§ John de Clerk", after):
                continue
            hit('monastic', work, m.start(), m.end())
        # ---- hospitals
        for m in HOSPITAL_PAT.finditer(work):
            pre = work[max(0, m.start() - 60):m.start()]
            if ADDR_BEFORE.search(pre) and not re.search(r"\bto (?:the |each )?$|\b(?:the )?(?:poor|inmates|sick|brethren|sisters|lazars|lepers|Master|Prior|Warden|Keeper|Custos|work|fabric|chapel|church|chaplains|priests)\b[^;]{0,30}\b(?:in|of|at)\s+(?:the\s+)?(?:said\s+)?(?:New\s+)?$", pre):
                continue
            if re.search(r"held (?:of|under)|rent (?:due|payable)|by demise of", pre, re.I):
                continue
            if re.search(r"^Hospital of S§ John (?:of Jerusalem|de Clerk)", work[m.start():m.start() + 40], re.I):
                hit('monastic', work, m.start(), m.end())
                continue
            hit('hospital', work, m.start(), m.end())
        # ---- charity
        for m in CHARITY_PAT.finditer(work):
            pre = work[max(0, m.start() - 40):m.start()]
            w = m.group(0).lower()
            if w in ('bridge', 'bridges', 'brigge', 'brugge'):
                if CHARITY_BRIDGE_ADDR.search(pre) and not re.search(r"(?:work|works|repair|maintenance|fabric|amendment|building)\b[^;]{0,45}$|\bto (?:the )?(?:London )?$", pre):
                    continue
                if re.search(r"^\s*(?:Street|street|Ward|ward|House|house|Gate)", work[m.end():m.end() + 8]):
                    continue
            if w in ('neugate',) and not re.search(r"prisoners|inmates|poor", work[max(0, m.start() - 40):m.end() + 20], re.I):
                continue
            if w in ('poor',) and re.search(r"poor (?:clares|Clares)", work[m.start():m.end() + 8]):
                continue
            if w in ('road', 'roads', 'highway', 'highways', 'pavement') and not re.search(r"repair|amend|mend|maintenance|making|work|to the", work[max(0, m.start() - 50):m.end() + 30], re.I):
                continue
            hit('charity', work, m.start(), m.end())
        # ---- cathedral
        for m in CATHEDRAL_PAT.finditer(work):
            pre = work[max(0, m.start() - 40):m.start()]
            if re.search(r"(?:Canon|canon|Prebendary|prebendary|Dean|Treasurer|Archdeacon|chaplain) of\s+$", pre + work[m.start():m.start() + 15][:0]):
                continue
            if re.search(r"^(?:canons|chaplains)", m.group(0)) and re.search(r"Sir [A-Z]\w+[^;]{0,30}$", pre):
                continue
            if ADDR_BEFORE.search(pre) and not re.search(r"\bto (?:the )?$", pre) and not re.match(r"(?:Dean|fabric|work|new|old|shrine)", m.group(0)):
                continue
            hit('cathedral', work, m.start(), m.end())

        # ---- intercession and others
        for v, pat in (('chantry', CHANTRY_PAT), ('obit', OBIT_PAT), ('masses', MASSES_PAT), ('lights', LIGHTS_PAT),
                       ('fraternity', FRAT_PAT), ('pious_uses', PIOUS_PAT), ('pestilence', PEST_PAT)):
            for m in pat.finditer(work):
                if v == 'chantry':
                    ctx = work[max(0, m.start() - 70):m.end() + 40]
                    if re.search(r"(?:chaplain|priest|warden|custos|keeper) of (?:the )?chantr", ctx, re.I) and not re.search(r"maintenance|provide|found|support|aid|charged|devoted|celebrat", ctx, re.I):
                        continue
                    if re.search(r"Lord|lord|King|Bishop|Earl", ctx) and re.search(r"souls of", ctx) is None and False:
                        continue
                if v == 'masses':
                    ctx = work[max(0, m.start() - 30):m.end() + 30]
                    if re.search(r"mass(?:es)? (?:book|of silver|of gold)|mass-book|Michaelmas|Christmas|Candlemas|Lammas", ctx, re.I):
                        continue
                    if re.search(r"Christ|Michael|Candle|Lam", work[max(0, m.start() - 8):m.start()]):
                        continue
                if v == 'lights':
                    ctx = work[max(0, m.start() - 30):m.end() + 30]
                    if re.search(r"ancient lights|light(?:s)? of (?:the|his) (?:house|window)|daylight|lighter", ctx, re.I):
                        continue
                if v == 'fraternity':
                    ctx = work[max(0, m.start() - 40):m.end() + 5]
                    if re.search(r"Guildhall|Gildhall|Yeldehall", ctx, re.I):
                        continue
                if v == 'pestilence':
                    pass
                hit(v, work, m.start(), m.end())
                if v in ('chantry', 'obit'):
                    chantry_sents.append(work)
        # ---- named chaplain to pray
        for m in NAMED_CHAP.finditer(work):
            if not re.search(r"chaplain|priest|Sir ", m.group(0)):
                continue
            if re.search(r"Knt|knight|kt\b", work[m.end():m.end() + 12], re.I):
                continue
            role = work[max(0, m.start() - 10):m.end() + 50]
            if not re.search(r"chaplain|priest", role, re.I):
                continue
            window = re.split(r";", work[m.start():m.end() + 130])[0]
            if re.search(r"celebrat\w*|\bpray\w*|\bmass(?:es)?\b|chantr\w*|divine service|trental|for (?:the good of )?(?:his|her|their|the) souls?|souls of|in remembrance|(?:to be|be) (?:the )?(?:first )?chaplain|to sing", window, re.I):
                hit('named_chaplain', work, m.start(), m.end())

    # chantry sub-codes and trustee
    perp = temp = 0
    trustees = []
    if flags['chantry'] or flags['obit']:
        for s in chantry_sents:
            if flags['chantry'] and re.search(r"chantr|chauntr|celebrat|divine service", s, re.I):
                if PERPETUAL.search(s):
                    perp = 1
                if TEMPORARY.search(s):
                    temp = 1
            for k, pat in TRUSTEE.items():
                if pat.search(s) and not (k == 'lay_corporate' and LAY_EXCL.search(s)):
                    if k not in trustees:
                        trustees.append(k)
        if not trustees:
            trustees = ['private']
    # ---- holder detail (added after the audit; descriptive, not double-coded)
    private_named = ''
    pb_kind = ''
    if flags['chantry'] or flags['obit']:
        named = 0
        has_rector = has_lay = 0
        for s in chantry_sents:
            # drop "for the good of his soul and the souls of ..." so that kin named as souls are not read as holders
            t = SOULS.sub(' ', s)
            if PRIVATE_HOLDER.search(t):
                named = 1
            if TRUSTEE['parish_body'].search(s):
                if PB_RECTOR.search(s):
                    has_rector = 1
                if PB_LAY.search(s):
                    has_lay = 1
        private_named = named
        if 'parish_body' in trustees:
            pb_kind = 'both' if (has_rector and has_lay) else 'lay_only' if has_lay else 'rector_only'
    out['holder_private_named'] = private_named
    out['parish_body_kind'] = pb_kind
    out['chantry_perpetual'] = perp
    out['chantry_temporary'] = temp
    out['chantry_trustee'] = ';'.join(trustees)
    out['burial_site'] = burial_site
    for v in VARS:
        out[v] = flags[v]
        out[v + '_snip'] = ' || '.join(snips[v])
    return out


def main():
    R = json.load(open(sys.argv[1]))
    rows = []
    for r in R:
        c = code(r)
        period = ('P1' if r['enrol_year'] <= 1348 else 'P2' if r['enrol_year'] <= 1360 else
                  'P3' if r['enrol_year'] <= 1375 else 'P4')
        row = {'will_id': r['will_id'], 'vol': r['vol'], 'page': r['page'], 'bho_page': r['page_url'],
               'roll': r['roll'], 'regnal_heading': r['roll_title'], 'court_heading': r['heading'],
               'enrol_year': r['enrol_year'], 'will_year': c['will_year'], 'period': period,
               'testator': c['testator'], 'sex': c['sex'], 'occupation': c['occupation'], 'cleric': c['cleric'],
               'empty_entry': c['empty_entry'], 'burial_site': c['burial_site']}
        for v in VARS:
            row[v] = c[v]
        row['chantry_perpetual'] = c['chantry_perpetual']
        row['chantry_temporary'] = c['chantry_temporary']
        row['chantry_trustee'] = c['chantry_trustee']
        row['holder_private_named'] = c['holder_private_named']
        row['parish_body_kind'] = c['parish_body_kind']
        for v in VARS:
            row[v + '_snip'] = c[v + '_snip']
        row['entry_words'] = len(re.sub(r'Roll [\d.]+\s*\([^)]*\)\.?', '', r['text']).split())
        if '--with-text' in sys.argv:
            row['entry_text'] = r['text']
        rows.append(row)
    with open(sys.argv[2], 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(len(rows))


if __name__ == '__main__':
    main()
