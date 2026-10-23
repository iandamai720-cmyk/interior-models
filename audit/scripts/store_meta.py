import json,re,os,unicodedata,html
R='/workspace/audit'
A=json.load(open('/workspace/interior-lib/catalog.json'))['assets']
S=[a for a in A if a['type']=='store_product']
sp=json.load(open(f'{R}/store_parsed.json')); ag=json.load(open(f'{R}/agata_gql.json'))
si=json.load(open(f'{R}/store_img.json')); lm=json.load(open(f'{R}/lm_fetch.json'))
def nd(s): return ''.join(c for c in unicodedata.normalize('NFKD',s.lower().replace('ł','l')) if not unicodedata.combining(c))
CAT=[ # (regex on normalized name, category)
 (r'naroznik (zewnetrzn|wewnetrzn)|listw\w* przypodlog|^listwa',"skirting_board"),
 (r'poduszk[ai] na krzesl|poduszk[ai] ogrod',"cushion"),
 (r'fotel\w* ogrod',"garden_chair"),
 (r'fotel biurow|krzeslo biurow|fotel gaming|krzeslo obrotow',"office_chair"),
 (r'\blezak',"sun_lounger"),
 (r'\bnaroznik',"sofa_corner"),
 (r'\bsofa|\bkanapa',"sofa"),
 (r'\bhoker',"bar_stool"),
 (r'\bpuf[ae]?\b',"pouffe"),
 (r'\bfotel',"armchair"),
 (r'krzeslo ogrod|krzesla ogrod',"garden_chair"),
 (r'\bkrzesl',"dining_chair"),
 (r'(stol|stolik)\w* ogrod|stolik balkon',"garden_table"),
 (r'stolik nocny|szafka nocna',"nightstand"),
 (r'stolik|\blawa\b',"coffee_table"),
 (r'\bstol\b|\bstol ',"dining_table"),
 (r'pietrow',"bunk_bed"),
 (r'lozeczko',"crib"),
 (r'lozko dziec|lozko mlodziez',"kids_bed"),
 (r'\blozko',"bed_double"),
 (r'szafka rtv|mebloscianka|szafka pod tv|stolik rtv',"tv_bench"),
 (r'(szafka|regal|szafa)[\w ]{0,10}na buty|szafka na obuwie',"shoe_cabinet"),
 (r'szafk\w* pod umywalk|pod umywalk|szafka lazienk',"bathroom_vanity"),
 (r'szafka kuchenn|szafka (\d+ )?dolna',"kitchen_base_cabinet"),
 (r'\bwitryn|gablot',"display_cabinet"),
 (r'\bszaf[ay]\b|\bszafa',"wardrobe"),
 (r'\bkomod',"chest_of_drawers"),
 (r'regal',"bookshelf"),
 (r'biurk',"desk"),
 (r'lustr',"mirror"),
 (r'lampa wiszaca|lampa wisz|zyrandol',"pendant_lamp"),
 (r'lampa podlog',"floor_lamp"),
 (r'lampa stolow|lampka|lampa biurk',"table_lamp"),
 (r'dywanik lazienk',"bath_mat"),
 (r'dywan',"rug"),
 (r'firan|zaslon',"curtains"),
 (r'poduszk',"cushion"),
 (r'doniczk|oslonk|donic|kwietnik',"plant_pot"),
 (r'\bwc\b|miska',"toilet"),
 (r'umywalk',"bathroom_sink"),
 (r'\bwanna',"bathtub"),
 (r'kabina prysz|prysznic|brodzik',"shower"),
 (r'grzejnik (na podczerwien|konwektor)|podczerwien|konwektor|termofol|promiennik',"heater"),
 (r'grzejnik',"radiator"),
 (r'^drzwi|skrzydlo drzwiowe',"door"),
 (r'\bszafk',"cabinet"),
]
ROOM=dict(sofa='living',sofa_corner='living',armchair='living',pouffe='living',coffee_table='living',tv_bench='living',display_cabinet='living',bookshelf='living',rug='living',curtains='living',cushion='living',plant_pot='living',floor_lamp='living',pendant_lamp='living',table_lamp='living',mirror='hallway',shoe_cabinet='hallway',
 dining_chair='dining',dining_table='dining',bar_stool='kitchen',kitchen_base_cabinet='kitchen',bed_double='bedroom',nightstand='bedroom',wardrobe='bedroom',chest_of_drawers='bedroom',kids_bed='kids',bunk_bed='kids',crib='kids',desk='office',office_chair='office',
 garden_chair='garden',garden_table='garden',sun_lounger='garden',toilet='bathroom',bathroom_sink='bathroom',bathtub='bathroom',shower='bathroom',bathroom_vanity='bathroom',bath_mat='bathroom',radiator='bathroom',heater='living',door='hallway')
COL=[(r'bial','biały'),(r'czarn','czarny'),(r'grafit','grafitowy'),(r'antracyt','antracytowy'),(r'jasnoszar|jasny szar','jasnoszary'),(r'ciemnoszar','ciemnoszary'),(r'szar|popiel','szary'),(r'srebr','srebrny'),(r'chrom','chrom'),(r'zlot|gold','złoty'),(r'bez\b|bezow|kaszmir|cream|kremow','beżowy'),
 (r'braz|cognac|koniak','brązowy'),(r'ciemnozielon','ciemnozielony'),(r'zielon|szalwi|oliwk','zielony'),(r'turkus|lazur','turkusowy'),(r'granat','granatowy'),(r'niebiesk','niebieski'),(r'roz\b|rozow|pudrow','różowy'),(r'zolt|musztard','żółty'),(r'czerwon|bordow','czerwony'),(r'terakot|rdzaw','terakota'),
 (r'dab|debow|debu','dąb'),(r'orzech','orzech'),(r'sosn','sosna'),(r'brzoz','brzoza'),(r'buk','buk'),(r'sonoma','dąb sonoma'),(r'natur','naturalny'),(r'trawertyn|marmur','marmur/trawertyn')]
MAT=[(r'welur|velvet|aksamit','welur'),(r'sztruks','sztruks'),(r'boucle','boucle'),(r'skora eko|ekoskor|skora ekolog','skóra ekologiczna'),(r'\bskor','skóra'),(r'tkanin','tkanina'),(r'lity dab|litego deb|lite drewno|litego drewna|drewno lite|z litego','lite drewno'),(r'fornir','fornir'),(r'drewnian|drewn','drewno'),
 (r'rattan|technorattan','rattan'),(r'alumin','aluminium'),(r'stal|metal|metalow','metal'),(r'szkl|szyb','szkło'),(r'ceram|spiek','ceramika/spiek'),(r'marmur','marmur'),(r'tworzywo mineral|konglomerat','konglomerat mineralny'),(r'akryl','akryl'),(r'juta|jutow','juta'),(r'bawel','bawełna'),(r'poliest','poliester'),(r'beton','beton'),(r'plyt|laminat|mdf','płyta meblowa')]
def picks(rules,t,multi=True):
    out=[]
    for r,v in rules:
        if re.search(r,t) and v not in out: out.append(v)
        if out and not multi: break
    return out
def dims(t):
    t=t.replace(',','.')
    m=re.search(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(cm|mm)?',t)
    if m:
        f=0.1 if m.group(4)=='mm' else 1; return dict(w=float(m.group(1))*f,d=float(m.group(2))*f,h=float(m.group(3))*f,src='nazwa')
    m=re.search(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(cm)?',t)
    if m: return dict(w=float(m.group(1)),d=float(m.group(2)),h=None,src='nazwa')
    m=re.search(r'(?:sr\.?|srednica|o)\s*(\d+(?:\.\d+)?)\s*cm',t)
    if m: return dict(w=float(m.group(1)),d=float(m.group(1)),h=None,src='nazwa (średnica)')
    m=re.search(r'\b(\d{2,3}(?:\.\d+)?)\s*cm',t)
    if m: return dict(w=float(m.group(1)),d=None,h=None,src='nazwa (szerokość)')
    return None
out={}
for a in S:
    i=a['id']; p=sp.get(i,{}); st=a['store']; name=a['name']; nfrom='catalog'
    if st=='JYSK' and p.get('h1'):
        h=p['h1']; ser=p.get('ld_name') or ''
        if ser and h.startswith(ser) and len(h)>len(ser)+3: h=h[len(ser):]
        else: h=re.sub(r'^[A-ZÆØÅ +]+(?=[A-ZŁŚŻ][a-ząćęłńóśźż])','',h)
        h=re.sub(r'^basic','',h); name=h.strip(); nfrom='h1 (bez prefiksu serii)'
    elif st=='Bodzio' and p.get('og_title'): name=re.sub(r'\s*-\s*BODZIO\s*$','',p['og_title']).strip(); nfrom='og:title'
    elif st=='Komfort' and p.get('ld_name'): name=p['ld_name']; nfrom='JSON-LD'
    name=re.sub(r'\s*-\s*BODZIO\s*$','',name); name=re.sub(r'\s+1\s*szt\.?$','',name.strip()); name=re.sub(r'\s{2,}',' ',name).strip()
    if st=='Leroy Merlin': name=name[:1].upper()+name[1:]
    t=nd(name+' '+(a.get('url_pl') or '').split('/')[-1].replace('-',' '))
    tn=nd(name)
    best=None
    for o,(r,c) in enumerate(CAT):
        m=re.search(r,tn)
        if m and (best is None or (m.start(),o)<best[0]): best=((m.start(),o),c)
    cat=best[1] if best else None
    # image
    img=None; isrc=None
    g=ag.get(i)
    if g and g.get('image',{}).get('url'): img,isrc=g['image']['url'],'Agata GraphQL'
    elif i in lm: img,isrc=lm[i]['img'],'strona produktu LM'
    elif p.get('og_image'): img,isrc=html.unescape(p['og_image']),'og:image'
    elif p.get('ld_image'): img,isrc=html.unescape(p['ld_image']),'JSON-LD image'
    elif si.get(i,{}).get('url'): img,isrc=si[i]['url'],si[i].get('src')
    elif a.get('image_url'): img,isrc=a['image_url'],'BRW listing (niezweryfikowany)'
    has=os.path.exists(f'{R}/storeimg/{i}.img') and os.path.getsize(f'{R}/storeimg/{i}.img')>2000
    col=picks(COL,tn); mat=picks(MAT,tn)
    D=None
    if i in lm:
        L=lm[i]; D=dict(w=L['w'],d=L['d'],h=L['h'],src='tabela cech LM')
        if L.get('colour'): col=[L['colour']]
        if L.get('material'): mat=[L['material']]
    elif p.get('ld_width') or p.get('ld_height'):
        f=lambda x: float(re.sub(r'[^\d.]','',str(x).replace(',','.'))) if x and re.search(r'\d',str(x)) else None
        D=dict(w=f(p.get('ld_width')),d=f(p.get('ld_depth')),h=f(p.get('ld_height')),src='JSON-LD')
    if not D: D=dims(tn)
    if p.get('ld_color') and not col: col=[p['ld_color']]
    price=a.get('price_pln')
    if not price and g: 
        try: price=g['price_range']['minimum_price']['final_price']['value']
        except Exception: pass
    out[i]=dict(name=name,name_from=nfrom,category=cat or a['category'],cat_rule=bool(cat),room=ROOM.get(cat or a['category'],a.get('room')),colour=', '.join(col[:2]) or None,material=', '.join(mat[:2]) or None,dims_cm=D,
               product_image_url=img,image_src=isrc,image_verified=has,price_pln=price)
json.dump(out,open(f'{R}/store_meta.json','w'),ensure_ascii=False,indent=0)
from collections import Counter
print(Counter(v['category'] for v in out.values()).most_common())
print('no rule',[ (k,v['name']) for k,v in out.items() if not v['cat_rule']])
print('img',sum(1 for v in out.values() if v['product_image_url']),'verified',sum(v['image_verified'] for v in out.values()))
print('dims',sum(1 for v in out.values() if v['dims_cm']),'colour',sum(1 for v in out.values() if v['colour']),'mat',sum(1 for v in out.values() if v['material']))
old={a['id']:a['category'] for a in S}
ch=[(k,old[k],v['category'],v['name']) for k,v in out.items() if old[k]!=v['category']]
print(len(ch))
for c in ch: print(c)
