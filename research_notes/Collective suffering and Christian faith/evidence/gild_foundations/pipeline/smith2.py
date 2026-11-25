import re, sys
L=open(sys.argv[1],encoding='utf-8',errors='replace').read().split('\n')
heads=[(i,l.strip()) for i,l in enumerate(L) if re.match(r'\s*(\[|\([a-z]{1,2}\s*\)\s*)?(The\s+)?(Great\s+)?Gild\s+of',l) and 11000<i<24500]
for k,(i,h) in enumerate(heads):
    end=heads[k+1][0] if k+1<len(heads) else i+400
    print('#### %d %s' % (i,h))
    for j in range(i,end):
        l=L[j]
        if re.search(r'begun|be-gunne|begonne|bigunne|M\s*[\.,]?\s*CCC|mccc|yere? of|3ere|ȝere|tyme|mynde|memorie|pestil|deth|dethe|1[23]\d\d',l,re.I):
            print('   %d: %s' % (j,l.strip()[:150]))
