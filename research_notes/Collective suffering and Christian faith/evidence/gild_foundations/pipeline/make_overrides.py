# Manual (model-read) codes that replace rule-based output; each records the justifying text in check_note.
import json, csv, re, sys
coded = {(x['cert'] + ('.' + x['sub'] if x['sub'] else '')): x for x in csv.DictReader(open(sys.argv[1]))}
F = {  # founders, manual reading of founding statements in Westlake cols 3/5
 '7':'craft','21':'mixed','36':'mixed','54':'parishioners','73':'parishioners','79':'parishioners','93':'parishioners',
 '109':'parishioners','110':'parishioners','111':'parishioners','112':'parishioners','117':'craft','119':'parishioners',
 '120':'craft','122':'parishioners','123':'parishioners','140.ii':'parishioners','166':'parishioners','167':'parishioners',
 '175':'parishioners','176':'parishioners','180':'mixed','184.i':'parishioners','184.ii':'parishioners','184.iii':'parishioners','184.iv':'parishioners',
 '189':'parishioners','191':'parishioners','199':'parishioners','201':'parishioners','203':'parishioners','205':'mixed','207':'parishioners',
 '208.i':'parishioners','208.ii':'parishioners','233':'parishioners','235':'parishioners','255':'craft','272':'parishioners',
 '279':'parishioners','291':'clergy','292':'parishioners','301':'craft','304':'craft','318':'parishioners','333.i':'parishioners',
 '339':'parishioners','340':'parishioners','342':'parishioners','348':'parishioners','355':'parishioners','358':'parishioners',
 '367':'parishioners','373':'craft','378':'parishioners','380':'parishioners','386':'parishioners','391':'parishioners',
 '400':'parishioners','415':'clergy','426':'parishioners','435':'mixed','436':'parishioners','448':'mixed','469':'parishioners',
 '470':'craft','471':'parishioners','253':'clergy','417':'clergy',
 '169':'parishioners','61':'not_stated','209':'not_stated','213':'not_stated','234':'not_stated','274':'not_stated',
}
FN = {'36':'chaplain + "Nicholas, Clerk" (clerk may be surname); others then associated','21':'"Sir Robert Aylsham, monk, and others"',
      '180':'a monk founded chapel/chaplaincy; after his death "certain men" continued it','205':'"Master Piers de Berkhampstede, Vicar, and others (named)"',
      '471':'John Enefeld, brewer, with an attorney, a chandler and a whittawyer (lay, mixed trades)','253':"Clerk's Gild (clerks)",'417':'Clerks of Glemsford',
      '184.ii':'"Mutatis mutandis as in (i.)" -> devotion of the parishioners'}
G = {'6':1,'9':1,'10':1,'77':1,'205':1,'234':1,'236':1,'385':1,'386':1,'387':1,'404':1,
     '69':0,'103':0,'124':0,'163':0,'180':0,'182':0,'203':0,'213':0,'402':0,'436':0,'437':0,'466':0}
GN = {'404':'"Governed by a prior (or cantor)": title may be a gild office, ambiguous','402':'gild "consists of a master and 12 priests, also laymen and women": clergy members, no governing role stated',
      '124':'lay alderman directs the chaplain (lay control)','180':'alderman collects chaplain\'s salary (lay control)','182':'chaplain elected by the brethren (lay control)',
      '213':'wardens pay the priest (lay control)','437':'gild ordinances form a rule for the chaplains (lay control)'}
E = {'417':0}
out = {}
def sent(key, pat):
    x = coded[key]; t = ' '.join([x['date_raw'], x['text_purpose'], x['text_benefits'], x['text_remarks']])
    ss = [s for s in re.split(r'(?<=[.;])\s+', t) if re.search(pat, s, re.I)]
    return ' | '.join(ss)[:300]
for k, v in F.items():
    o = out.setdefault(k, {})
    o['founders'] = v
    o['founders_snip'] = sent(k, r'found|begun|began|beginning|formed|devotion|caused|joined|clerk|monk|vicar|rector|chaplains') or coded[k]['dedication']
    if k in FN: o['check_note'] = (o.get('check_note', '') + ' founders: ' + FN[k]).strip()
for k, v in G.items():
    o = out.setdefault(k, {})
    o['clergy_gov'] = v
    o['clergy_snip'] = sent(k, r'bishop|vicar|prior|archbishop|abbot|priest|chaplain|rector|parson|convent')
    if k in GN: o['check_note'] = (o.get('check_note', '') + ' clergy: ' + GN[k]).strip()
for k, v in E.items():
    out.setdefault(k, {})['clergy_excluded'] = v
out.setdefault('222', {}).update({'content_free': 0, 'lights': 1, 'lights_snip': 'Yearly a candle.', 'check_note': 'short entry "Yearly a candle." read as content'})
out.setdefault('459', {}).update({'inherit_from': '458', 'check_note': 'OCR "As in 459" corrected to 458 from page image context (Worton)'})
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(len(out), 'overrides')
