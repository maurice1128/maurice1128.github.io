# Date classification rules for Westlake (1919) col. 2 date statements (see codebook.md, "Foundation date")
import re

def classify(raw, sub_raw_inherit=None):
    """Return dict(date_class, found_year, period_basis, note)."""
    r = raw.strip()
    lo = r.lower()
    out = {'date_class': '', 'found_year': '', 'tpq_year': '', 'period': '', 'date_note': ''}
    yrs = [int(y) for y in re.findall(r'\b(1[0-3]\d\d|10\d\d)\b', r)]

    def period_of(y):
        if y < 1300: return 'early'
        if y <= 1348: return 'pre'
        if y <= 1389: return 'post'
        return ''

    if 'pestilence' in lo:
        if 'before' in lo:
            out.update(date_class='rel_pestilence', period='pre', date_note='stated as before the great pestilence; no year')
        else:
            out.update(date_class='rel_pestilence', found_year=1349, period='post',
                       date_note="ordinances 'immediately after the first pestilence'; year is Westlake's gloss (c. 1349)")
        return out
    if 'mortmain' in lo:
        out.update(date_class='time_out_of_mind', period='early', date_note='"before the statute of Mortmain" (1279)')
        return out
    if any(k in lo for k in ['time without', 'old time', 'formerly', 'do not know the beginning']):
        out.update(date_class='time_out_of_mind')
        return out
    if any(k in lo for k in ['lately', 'newly', 'just begun']):
        out.update(date_class='recent', period='post', date_note='stated as recently begun in a 1388-9 return; period assigned post, no decade')
        return out
    if 'temp. ric' in lo:
        out.update(date_class='reign', period='post', date_note='temp. Ric. II (1377-89)')
        return out
    if 'temp. edw' in lo:
        out.update(date_class='reign', date_note='temp. Edw. III (1327-77); period indeterminate')
        return out
    if 'athelstan' in lo or 'hen. i.' in lo or 'henry ii' in lo or 'temp. john' in lo:
        out.update(date_class='document_or_tradition', period='early', date_note='pre-1300 charter/tradition')
        return out
    if 'date torn' in lo and '7 ed' in lo:
        out.update(date_class='document_or_tradition', period='pre', date_note='"7 Ed." = 1279, 1313 or 1333; pre-1349 in every reading')
        return out
    if "'37" in r or '’37' in r or 'year 37' in lo:
        out.update(date_class='approx', date_note="\"begun the year '37\": 1337 or 37 Edw. III (1363); indeterminate")
        return out
    # regnal-year licences / charters (Coventry)
    m = re.search(r'(\d+)\s+edw\.?\s*iii', lo)
    if m and ('licen' in lo or 'charter' in lo):
        y = 1326 + int(m.group(1))  # regnal year n of Edw. III begins 25 Jan 1326+n
        out.update(date_class='document_dated', tpq_year=y, period='pre' if y <= 1348 else '',
                   date_note='licence/charter %d Edw. III = %d-%d; terminus ante quem' % (int(m.group(1)), y, y + 1))
        return out
    if 'charter from ric' in lo:
        out.update(date_class='document_dated', date_note='charter of Ric. II (1377-89); terminus ante quem only')
        return out
    if any(k in lo for k in ['no date', '[none', 'unknown', 'obliterated', 'not stated']) and not yrs:
        out.update(date_class='not_stated')
        return out
    if 'founded on same day' in lo:
        out.update(date_class='exact', found_year=1378, period='post', date_note='same day as (i.), 1378')
        return out
    if lo.startswith('renewed'):
        y = yrs[0]
        out.update(date_class='document_dated', tpq_year=y, period='pre' if y <= 1349 else '',
                   date_note='"Renewed %d": gild existed before renewal; foundation date unknown' % y)
        return out
    if re.match(r'^(statutes|ordinances|deed|licen)', lo):
        y = yrs[0]
        out.update(date_class='document_dated', tpq_year=y, period='pre' if y <= 1348 else ('early' if y < 1300 else ''),
                   date_note='date of statutes/ordinances/deed/licence, not of foundation; terminus ante quem')
        if y < 1300: out['period'] = 'early'
        return out
    if yrs:
        y = yrs[0]
        approx = lo.startswith('c.') or lo.startswith('?') or '(?' in lo or lo.startswith('(?')
        if 'benefactors' in lo:  # Chesterfield "(? 1218.)"
            approx = True
        out.update(date_class='approx' if approx else 'exact', found_year=y, period=period_of(y))
        if 'century has been obliterated' in lo:
            out['date_class'] = 'approx'; out['date_note'] = 'century obliterated; Westlake conjectures 1385'
        if 'claim also' in lo:
            out['date_note'] = 'claimed date'
        return out
    out.update(date_class='not_stated', date_note='no date recognised')
    return out
