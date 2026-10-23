"""Collect normalised turn-4 assets (IKEA PL, Poly Haven, Kenney) into tmp/new_assets.json."""
import json
out=[]
L={p['article_number']:p for p in json.load(open('tmp/ikea_pl.json'))}
r={}
for i in range(3): r.update(json.load(open(f'tmp/res_ikea_pl_{i}.json')))
for s in json.load(open('tmp/spec_ikea_pl.json')):
    a=s['key'].rsplit('_',1)[1]; p=L[a]; x=r[s['key']]
    out.append(dict(key=s['key'],file=x['file'],category=s['out'].split('/')[1],full_name=p['full_name'],article_number=a,size=x['size'],colour=p.get('colour',''),source='ikea_pl'))
for pref,n in (('ph',3),('kenney',2)):
    r={}
    for i in range(n): r.update(json.load(open(f'tmp/res_{pref}_{i}.json')))
    for s in json.load(open(f'tmp/spec_{pref}.json')):
        if s['key'] not in r: continue
        x=r[s['key']]; out.append(dict(key=s['key'],file=x['file'],category=s['category'],full_name=s['key'],article_number=None,size=x['size'],colour='',source=pref))
json.dump(out,open('tmp/new_assets.json','w'),indent=0); print(len(out))
