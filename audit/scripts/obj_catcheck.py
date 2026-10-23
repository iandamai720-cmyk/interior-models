import json,re,numpy as np
d=np.load('clip.npz',allow_pickle=True); ids=list(d['ids']); cats=list(d['cats']); ct=d['cat_t']; im=d['im']; ix={k:i for i,k in enumerate(ids)}
on=json.load(open('obj_names.json')); A={a['id']:a for a in json.load(open('/workspace/interior-lib/catalog.json'))['assets']}; fc=json.load(open('fix_cat.json'))
SYN={'couch':'sofa','settee':'sofa','ottoman':'footstool','pouf':'pouffe','bookcase':'bookshelf','lantern':'lamp','closet':'wardrobe','stove':'cooker','trash':'bin','pillow':'cushion','easel':'easel','hanger':'coat_rack','globe':'decor','jug':'vase','pot':'plant_pot','locker':'locker','table':'table','chair':'chair','sofa':'sofa','rack':'coat_rack','shelf':'wall_shelf','lamp':'lamp','mirror':'mirror','stool':'stool','bench':'bench','desk':'desk','bed':'bed','clock':'clock','vase':'vase','rug':'rug','carpet':'rug','plant':'plant','flowers':'plant','tv':'tv','radio':'radio','fan':'fan','sink':'kitchen_sink','toilet':'toilet','bathtub':'bathtub','candle':'candle','basket':'basket','box':'storage_box','cabinet':'cabinet','dresser':'chest_of_drawers','wardrobe':'wardrobe','sideboard':'sideboard','piano':'piano','guitar':'guitar','book':'books','books':'books','frame':'picture_frame','painting':'wall_art','picture':'wall_art','statue':'sculpture','sculpture':'sculpture','kettle':'kettle','toaster':'toaster','microwave':'microwave','fridge':'fridge','refrigerator':'fridge','oven':'oven','heater':'heater','radiator':'radiator','curtain':'curtains','curtains':'curtains','armchair':'armchair','recliner':'armchair','tap':'bathroom_tap','faucet':'kitchen_tap','bowl':'tableware','plate':'tableware','cup':'tableware','mug':'tableware','dish':'tableware'}
ch={}
for k,v in on.items():
    if '–' not in v['after']: continue
    toks=re.findall(r'[a-z]+',v['before'].lower())
    cand={SYN[t] for t in toks if t in SYN}
    # expand generic to specific cats containing that word
    exp=set()
    for c in cand:
        exp|={x for x in cats if c==x or c in x.split('_')}
    exp&=set(cats)
    if not exp or k not in ix: continue
    cur=fc.get(k,{}).get('category',A[k]['category'])
    if cur in exp: continue
    s=im[ix[k]]@ct.T; sc={c:float(s[cats.index(c)]) for c in exp}; best=max(sc,key=sc.get)
    curs=float(s[cats.index(cur)]) if cur in cats else -1
    if sc[best]>curs: ch[k]=dict(before=cur,after=best,name=v['before'],s_new=round(sc[best],3),s_cur=round(curs,3))
json.dump(ch,open('obj_catfix.json','w'),indent=0,ensure_ascii=False)
print(len(ch))
for k,v in list(ch.items()): print(v['name'][:40],'|',v['before'],'->',v['after'],v['s_cur'],v['s_new'])
