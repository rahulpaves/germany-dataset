#!/usr/bin/env python3
"""
Applies verified field values to data.json.

Each entry records what was checked, against which page, on what date. A record
only gets verified:true when every field below has been read off the
institution's own site. Anything unverified keeps verified:false, so the site
can never claim more than was actually checked.
"""
import json, sys, datetime

DATA = 'data.json'

def apply(patches, source_note, checked_on):
    d = json.load(open(DATA, encoding='utf-8'))
    idx = {}
    for r in d:
        idx.setdefault((r['country'], r['institution'], r['programme']), []).append(r)

    hit = miss = 0
    for p in patches:
        key = (p['country'], p['institution'], p['programme'])
        rows = idx.get(key)
        if not rows:
            print('  ! no record for', p['programme'][:48]); miss += 1; continue
        for r in rows:
            for k, v in p.items():
                if k in ('country', 'institution', 'programme'):
                    continue
                r[k] = v
            r['verified'] = True
            r['verifiedOn'] = checked_on
            r['verifiedFrom'] = p.get('verifiedFrom', source_note)
            r.pop('linkOk', None)
        hit += len(rows)
    json.dump(d, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'  verified {hit} record(s), {miss} unmatched')

def drop(country, institution, programme, reason):
    """Programme no longer offered — remove rather than ship a dead record."""
    d = json.load(open(DATA, encoding='utf-8'))
    before = len(d)
    d = [r for r in d if not (r['country'] == country and r['institution'] == institution
                              and r['programme'] == programme)]
    json.dump(d, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'  dropped {before-len(d)} record(s): {programme[:40]} — {reason}')
