import csv,json,collections,re,openpyxl,sys
L='live/'
raw=open(L+'assets.csv','rb').read(3);print('BOM',raw==b'\xef\xbb\xbf')
R=list(csv.reader(open(L+'assets.csv',encoding='utf-8-sig')));H=R[0];rows=[dict(zip(H,r)) for r in R[1:]]
print('rows',len(rows),'cols',len(H),'bad width',sum(len(r)!=len(H) for r in R))
P=list(csv.reader(open(L+'assets_pl.csv',encoding='utf-8-sig'),delimiter=';'))
print('pl rows',len(P)-1,'bad width',sum(len(r)!=len(P[0]) for r in P),'same header',P[0]==H)
prow=[dict(zip(P[0],r)) for r in P[1:]]
diff=collections.Counter()
for a,b in zip(rows,prow):
    for k in H:
        if a[k]!=b[k]:
            if k=='price_pln' and a[k].replace('.',',')==b[k]: continue
            diff[k]+=1
print('pl vs csv diffs',dict(diff))
ids=[r['id'] for r in rows];print('dup ids',[i for i,c in collections.Counter(ids).items() if c>1])
cat={a['id']:a for a in json.load(open(L+'catalog.json'))['assets']}
shards=json.load(open(L+'catalog.json')).get('shards')
prob=collections.defaultdict(list)
glb=collections.defaultdict(list);pv=collections.defaultdict(list)
VALID_T={'furniture','appliance','fixture','store_product'}
for r in rows:
    i=r['id'];a=cat.get(i)
    if not a: prob['not in catalog'].append(i);continue
    if r['type'] not in VALID_T: prob['bad type'].append(i)
    if r['name']!=(a.get('name') or ''): prob['name != catalog'].append(i)
    if r['category']!=a.get('category'): prob['cat != catalog'].append(i)
    if r['opis']!=(a.get('opis') or ''): prob['opis != catalog'].append(i)
    if r['type']=='store_product':
        if r['model_file_url']: prob['store has glb'].append(i)
        if r['preview_url']!=r['product_image_url']: prob['store preview != product img'].append(i)
        if r['similar_model_id'] and r['similar_label']!='podobny model (zastępczy)': prob['sim no label'].append(i)
        if r['similar_model_id'] and r['similar_model_id'] not in cat: prob['sim missing'].append(i)
        if r['similar_model_id']:
            s=cat[r['similar_model_id']]
            if r['similar_model_url']!=s.get('url') or r['similar_preview_url']!=s.get('preview_url'): prob['sim url mismatch'].append(i)
            if s['category']!=r['category']: prob['sim other category'].append(i)
        if r['product_image_url']: pv[r['product_image_url']].append(i)
        continue
    u=r['model_file_url'];p=r['preview_url']
    if not u: prob['no glb'].append(i);continue
    if u!=a.get('url'): prob['glb != catalog'].append(i)
    m=re.match(r'(https://[^/]+/[^/]+/)(.*)/([^/]+)\.glb$',u)
    if not m: prob['glb url form'].append(i);continue
    base,d,fn=m.groups()
    if fn!=i and not fn.startswith(i): prob['glb name != id'].append((i,fn))
    if p!=f'{base}{d}/{i}.jpg': prob['preview not <id>.jpg next to glb'].append((i,p,u))
    if r['shard'] and shards and not base.startswith(shards.get(r['shard'],'#')): prob['shard mismatch'].append(i)
    glb[u].append(i);pv[p].append(i)
    if r['category'] and r['category'].replace('_',' ')[:4].lower() not in (r['opis'] or '').lower() and False: pass
print('shared glb',[v for v in glb.values() if len(v)>1][:5],sum(len(v)>1 for v in glb.values()))
print('shared preview',[v for v in pv.values() if len(v)>1][:5],sum(len(v)>1 for v in pv.values()))
for k,v in prob.items(): print(k,len(v),v[:3])
# xlsx
wb=openpyxl.load_workbook(L+'sklepy.xlsx',read_only=True);print(wb.sheetnames)
ws=wb['Wszystkie'];X=[[('' if c is None else str(c)) for c in r] for r in ws.iter_rows(values_only=True)]
print('xlsx rows',len(X)-1,'hdr same',X[0]==H)
xd=collections.Counter()
for a,b in zip(R[1:],X[1:]):
    for k,(u,v) in enumerate(zip(a,b)):
        if u!=v:
            try:
                if float(u)==float(v): continue
            except: pass
            xd[H[k]]+=1
print('xlsx diffs',dict(xd))
json.dump({k:v for k,v in prob.items()},open('integrity_prob.json','w'),default=str)
json.dump(rows,open('rows.json','w'))
