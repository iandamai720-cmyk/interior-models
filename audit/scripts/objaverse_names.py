import json,re
CF=json.load(open('obj_catfix.json'))
A=json.load(open('/workspace/interior-lib/catalog.json'))['assets'];fc=json.load(open('fix_cat.json'))
JUNK=[r'\(free\)',r'\[free\]',r'\bfree\b(?= *(download|model|3d|low))',r'\bdownload\b',r'\blow[- ]?poly\b',r'\blowpoly\b',r'\bgame[- ]ready\b',r'#\w+',r'\[smk\]',r'\.unity\b',r'\b3d ?model\b',r'freepoly\.org',r'\bpbr\b',r'\bsketchfab\b',r'\bfbx\b',r'\bobj\b',r'\bblender\b',r'\bhigh[- ]?poly\b',r'\brealistic\b(?= *$)',r'\b\d+k\b(?= *(textures?)?$)',r'\btextured?\b(?= *$)']
SYN={'sofa':'couch settee','armchair':'chair recliner','dining_chair':'chair','office_chair':'chair','bin':'trash can garbage','tv':'television','plant':'flower flowers cactus succulent','books':'book magazine magazines','decor':'statue vase sculpture','cookware':'pot pan','tableware':'bowl plate cup mug','cushion':'pillow','pouffe':'pouf ottoman bag','wardrobe':'closet','oven':'stove cooker','lamp':'light','fan':'','bookshelf':'shelf bookcase'}
def label(c): return c.replace('_',' ').capitalize()
out={}
for a in A:
    if not a['id'].startswith('objaverse') or a['type'] not in ('furniture','appliance','fixture'): continue
    f=fc.get(a['id'],{});
    if f.get('drop'): continue
    c=CF.get(a["id"],{}).get("after") or f.get("category",a["category"]); n0=f.get('name',a['name']); n=n0
    for j in JUNK: n=re.sub(j,' ',n,flags=re.I)
    n=re.sub(r'\s*\|\s*',' ',n); n=re.sub(r'[_]+',' ',n); n=re.sub(r'\s+',' ',n).strip(' -–,.:')
    words=[w for w in re.findall(r'[A-Za-zÀ-ž]+',n) if len(w)>=3 and re.search(r'[aeiouy]',w.lower()) and not w.isupper()]
    lab=label(c)
    if not words: new=f'{lab} (Objaverse)'
    else:
        toks=set(re.findall(r'[a-z]+',n.lower())); lt=set(c.split('_'))|set(SYN.get(c,'').split())|{t+'s' for t in c.split('_')}
        new=n if toks&lt else f'{lab} – {n}'
    if new!=n0: out[a['id']]=dict(before=n0,after=new,source_title=a.get('source_title') or n0)
json.dump(out,open('obj_names.json','w'),indent=0,ensure_ascii=False)
print(len(out))
import random;random.seed(3)
for k in random.sample(list(out),30): print(out[k]['before'],' => ',out[k]['after'])
