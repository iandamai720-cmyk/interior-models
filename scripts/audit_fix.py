"""Audit fix (turn 8): apply verified corrections to catalog.json. Idempotent: always starts from audit/catalog_before.json.
Inputs (audit/): rr_all.json (per-GLB thumbs+sha), fix_cat.json, dims_fix.json, obj_catfix.json, obj_names.json, store_meta.json, similar.json
Output: catalog.json, audit/report.csv"""
import json,csv,os,shutil,sys,re
L='/workspace/interior-lib'; AU='/workspace/audit'
sys.path.insert(0,AU); from cat_pl import PL
if not os.path.exists(f'{AU}/catalog_before.json'): shutil.copyfile(f'{L}/catalog.json',f'{AU}/catalog_before.json')
cat=json.load(open(f'{AU}/catalog_before.json')); A=cat['assets']; SH=cat['shards']
J=lambda n:json.load(open(f'{AU}/{n}'))
rr=J('rr/all.json'); fc=J('fix_cat.json'); dims=J('dims_fix.json'); ocf=J('obj_catfix.json'); onm=J('obj_names.json'); sm=J('store_meta.json'); sim=J('similar.json')
# verify2 (turn 10): live end-to-end verification fixes
v2=J('verify2_fixes.json') if os.path.exists(f'{AU}/verify2_fixes.json') else {}
vs=J('verify2_store.json') if os.path.exists(f'{AU}/verify2_store.json') else {}
for k,v in vs.items():
    sm[k]=dict(sm[k],**v.get('meta',{}))
    if v.get('similar'): sim[k]=dict(similar=v['similar'],mode='manual',score=1.0,reason=None)
import collections as _c
_rc=_c.defaultdict(_c.Counter)
for _a in json.load(open(f'{AU}/catalog_before.json'))['assets']:
    if _a.get('room') and _a['type'] not in ('layout','material','store_product'): _rc[_a['category']][_a['room']]+=1
exec(re.search(r'^ROOM=dict\(.*?\)\n',open(f'{AU}/store_meta.py').read(),re.S|re.M).group(0))
LABEL='podobny model (zastępczy)'
rep=[]
def ch(i,f,b,a):
    if b!=a: rep.append(dict(id=i,change=f,before='' if b is None else (json.dumps(b,ensure_ascii=False) if not isinstance(b,str) else b),after='' if a is None else (json.dumps(a,ensure_ascii=False) if not isinstance(a,str) else a)))
def setf(a,f,v,log=True):
    if log: ch(a['id'],f,a.get(f),v)
    a[f]=v
CPL={'white':'biały','black':'czarny','grey':'szary','beige':'beżowy','brown':'brązowy','green':'zielony','blue':'niebieski','yellow':'żółty','red':'czerwony','pink':'różowy','orange':'pomarańczowy','gold':'złoty','cream':'kremowy','walnut':'orzech','chrome':'chrom','stainless steel':'stal nierdzewna','multicolour':'wielobarwny','glass':'szkło','turquoise':'turkusowy'}
def cm(v): return f'{v:.0f}' if v>=10 else f'{v:.1f}'.replace('.',',')
def opis(a,store=None):
    typ=PL.get(a['category'],a['category'].replace('_',' ')); p=[typ[0].upper()+typ[1:]]
    cols=[CPL.get(c,c) for c in (a.get('colours') or ([a['colour']] if a.get('colour') else []))]
    if cols: p.append('kolor: '+', '.join(dict.fromkeys(cols)))
    if a.get('material'): p.append('materiał: '+a['material'])
    if store:
        d=store.get('dims_cm')
        if d and any(d.get(k) for k in ('w','d','h')):
            ks=[k for k in ('w','d','h') if d.get(k)]; nm=dict(w='szer.',d='gł.',h='wys.')
            p.append('wym.: '+' × '.join(cm(d[k]) for k in ks)+' cm ('+' × '.join(nm[k] for k in ks)+')')
        p.append('sklep: '+a['store']+(f", cena {a['price_pln']:.0f} zł" if a.get('price_pln') else ''))
        p.append('zdjęcie: produkt ze sklepu' if a.get('product_image_url') else 'brak zdjęcia produktu')
        if a.get('similar_model_id'): p.append(f"{LABEL}: {a['similar_model_name']}")
        else: p.append('brak dobrego modelu zastępczego')
    else:
        d=a.get('dimensions_m')
        if d: p.append('wym.: '+' × '.join(cm(d[k]*100) for k in ('x','y','z'))+' cm (szer. × gł. × wys.)')
        p.append('źródło: '+(a.get('source') or '')+('; własny model 3D (GLB)' if a.get('file') else ''))
    return '; '.join(p)+'.'
drops={k for k,v in fc.items() if v.get('drop')}|{k for k,v in v2.items() if v.get('drop')}
out=[]
for a in A:
    i=a['id']
    if i in drops: ch(i,'dropped (broken model)',a['name'],None); continue
    if i in rr:
        e=rr[i]; base=SH[a['shard']].rstrip('/')
        setf(a,'preview',e['thumb'],False); ch(i,'preview_url',a.get('preview_url'),f"{base}/{e['thumb']}"); a['preview_url']=f"{base}/{e['thumb']}"
        a['preview_sha256']=e['thumb_sha256']
        if a.get('sha256')!=e['glb_sha256']: setf(a,'sha256',e['glb_sha256'], a.get('sha256') is not None)
        a['file_size_bytes']=os.path.getsize(f"{L}/{e['file']}")
        a['triangles']=e.get('tris',a.get('triangles'))
    if i in dims:
        x,y,z=dims[i]; setf(a,'dimensions_m',dict(x=round(x,3),y=round(y,3),z=round(z,3)))
    f=fc.get(i,{})
    if f.get('category'): setf(a,'category',f['category'])
    if i in ocf: setf(a,'category',ocf[i]['after'])
    if f.get('name'): setf(a,'name',f['name'])
    if i in onm:
        a.setdefault('source_title',onm[i]['source_title']); setf(a,'name',onm[i]['after'])
        if a.get('full_name') and a['full_name']==onm[i]['before']: a['full_name']=onm[i]['after']
    g=v2.get(i,{})
    if g.get('category'): setf(a,'category',g['category'])
    if g.get('name'): setf(a,'name',g['name']); a['full_name']=g['name'] if a.get('full_name') else a.get('full_name')
    if f.get('category') or i in ocf or g.get('category'):
        r=ROOM.get(a['category']) or (_rc[a['category']].most_common(1)[0][0] if _rc[a['category']] else None)
        if r: setf(a,'room',r)
    if a['type']=='store_product':
        m=sm[i]; s=sim[i]
        for k in ('name','category','room'):
            if m.get(k) and m[k]!=a.get(k): setf(a,k,m[k])
        if m.get('name'): a['full_name']=m['name']
        if m.get('colour'): setf(a,'colour',m['colour']); a['colours']=[m['colour']]
        if m.get('material'): setf(a,'material',m['material'])
        if m.get('price_pln') and not a.get('price_pln'): setf(a,'price_pln',m['price_pln'])
        ch(i,'dimensions_m (copied from substitute model) removed',a.pop('dimensions_m',None),None)
        a['dimensions_cm']=m.get('dims_cm')
        setf(a,'product_image_url',m.get('product_image_url')); a['image_url']=m.get('product_image_url'); a['product_image_verified']=m['image_verified']; a['product_image_source']=m.get('image_src')
        setf(a,'preview',m.get('product_image_url')); setf(a,'preview_url',m.get('product_image_url'))
        old=a.get('similar_model_id'); new=s['similar']
        setf(a,'similar_model_id',new); a['similar_label']=LABEL if new else ''
        a['similar_match']=('wybrany ręcznie (weryfikacja 2026-10-23)' if s['mode']=='manual' else f"CLIP {'zdjęcie produktu' if s['mode']=='image' else 'opis tekstowy'} vs miniatura, ta sama kategoria, wynik {s['score']:.3f}; sprawdzone wizualnie") if new else ('brak: '+(s['reason'] or ''))
        a.pop('model_url',None); a['url']=None
        a['license']='Product data/image © store (link only); no 3D model published by the store'+(f'; {LABEL} = similar_model_id' if new else '')
        out.append(a); continue
    out.append(a)
CPL.update({'anthracite':'antracytowy','dark walnut':'ciemny orzech','brown leather':'brązowa skóra','light oak':'jasny dąb','light grey':'jasnoszary'})
MPL={'Fabric':'Tkanina','Leather':'Skóra','Coated fabric':'Tkanina powlekana','Wood (including board)':'Drewno (łacznie z płytą)','Plastic':'Tworzywo sztuczne','Textile':'Tekstylia','Synthetic fibres':'Włókna syntetyczne','Solid wood':'lite drewno','Wood veneer':'Okleina drewniana','Glass':'Szkło','Bamboo':'Bambus','Rattan':'Wiklina i ratan','Steel':'Stal','Stainless steel':'Stal nierdzewna','Cotton':'Bawełna','Polyester':'Poliester','Paper':'Papier','Ceramic':'Ceramiczny','Wool':'Wełna','Jute':'Juta','Cork':'Korek','Stone':'Kamień','Marble':'Marmur','Porcelain':'Porcelana','Stoneware':'Kamionka','Aluminium':'Aluminium','Natural fibres':'Włókna naturalne'}
for a in out:
    if a.get('colour') in CPL: setf(a,'colour',CPL[a['colour']])
    if a.get('colours'): a['colours']=[CPL.get(c,c) for c in a['colours']]
    if a.get('material'):
        m2=', '.join(MPL.get(t.strip(),t.strip()) for t in a['material'].split(','))
        if m2!=a['material']: setf(a,'material',m2)
BY={a['id']:a for a in out}
for a in out:
    if a['type']=='store_product':
        t=BY.get(a['similar_model_id']) if a['similar_model_id'] else None
        a['similar_model_name']=(t.get('full_name') or t['name']) if t else None
        a['similar_model_url']=(t.get('model_url') or t.get('url')) if t else None
        a['similar_preview_url']=t['preview_url'] if t else None
        a['tags']=sorted(set([x for x in a.get('tags',[]) if x not in ROOM.values() and x not in PL])|{a['category'],a['room'],a['store_key'],'store-product'})
    if a['type'] not in ('layout','material'): a['opis']=opis(a,sm.get(a['id']) if a['type']=='store_product' else None)
cat['assets']=out; cat['audit']=dict(date='2026-10-23',report='audit/report.csv',note='per-GLB previews; store products show real product image; similar models re-picked (CLIP + visual check)')
json.dump(cat,open(f'{L}/catalog.json','w'),indent=1,ensure_ascii=False)
os.makedirs(f'{L}/audit',exist_ok=True)
with open(f'{L}/audit/report.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,['id','change','before','after']); w.writeheader(); w.writerows(rep)
import collections; print(len(out),'assets;',len(rep),'changes', collections.Counter(r['change'] for r in rep).most_common(20))
