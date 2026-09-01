# -*- coding: utf-8 -*-
"""Bibliographic check on the references the supplementary sweep wants to ADD.

Every one of these arrives as a recommendation from a reading agent. Before any of them is written
into the supplementary, the printed fields are compared against the Crossref registry by DOI or by
title search - the same deterministic check the seventeen existing references pass. A recommendation
that cannot be matched to a registry record does not go in.
"""
import io, json, sys, time
import urllib.request, urllib.parse

MAIL = 'mauricewang1128@gmail.com'
CAND = [
    ('Stenum 2021', '10.1371/journal.pcbi.1008935',
     'Two-dimensional video-based analysis of human gait using pose estimation', 'PLoS Comput Biol', 2021),
    ('Wade 2023', '10.1371/journal.pone.0293917',
     'Examination of 2D frontal and sagittal markerless motion capture', 'PLoS ONE', 2023),
    ('Kanko 2021 (the one with 3.3 deg)', '10.1016/j.jbiomech.2021.110665',
     'Concurrent assessment of gait kinematics using marker-based and markerless motion capture', 'J Biomech', 2021),
    ('Keller 2022', '10.1016/j.jbiomech.2022.111182',
     'Clothing condition does not affect meaningful clinical interpretation in markerless motion capture', 'J Biomech', 2022),
    ('Augustine 2025', '10.7717/peerj.18613',
     'Markerless motion capture clothing', 'PeerJ', 2025),
    ('Baldinger 2025', '10.3390/s25030799',
     'Influence of the Camera Viewing Angle on OpenPose Validity in Motion Analysis', 'Sensors', 2025),
    ('Kwon 2015', None,
     'gait kinematics walking speed knee flexion young adults', None, 2015),
    ('Patathong 2023', None,
     'normal gait parameters Thai adults three-dimensional gait analysis', None, 2023),
]


def get(url):
    r = urllib.request.Request(url, headers={'User-Agent': f'ref-check (mailto:{MAIL})'})
    return json.load(urllib.request.urlopen(r, timeout=45))


for label, doi, title, jrnl, yr in CAND:
    print('=' * 76)
    print(label)
    try:
        if doi:
            m = get('https://api.crossref.org/works/' + urllib.parse.quote(doi))['message']
            how = 'by DOI ' + doi
        else:
            q = get('https://api.crossref.org/works?rows=1&query.bibliographic='
                    + urllib.parse.quote(title))['message']['items']
            if not q:
                print('   no Crossref hit for a title search - cannot verify, do NOT add')
                continue
            m, how = q[0], 'by title search'
        got_t = (m.get('title') or [''])[0]
        got_j = (m.get('container-title') or [''])[0]
        got_y = (m.get('issued', {}).get('date-parts') or [[None]])[0][0]
        auth = m.get('author') or []
        first = (auth[0].get('family', '') + ' ' + auth[0].get('given', '')) if auth else '?'
        print('   looked up ' + how)
        print('   registry : ' + got_t[:88])
        print('              ' + got_j[:52] + '  ' + str(got_y)
              + '  vol ' + str(m.get('volume', '')) + '  ' + str(m.get('page', '')))
        print('   first author: ' + first + '   (' + str(len(auth)) + ' authors)')
        if yr and got_y and int(got_y) != int(yr):
            print('   !! YEAR MISMATCH: we say ' + str(yr) + ', registry says ' + str(got_y))
        if title and title.lower()[:40] not in got_t.lower():
            print('   !! title differs from what we expected - read the registry line above')
    except Exception as e:
        print('   lookup failed: ' + str(e))
    time.sleep(0.4)
