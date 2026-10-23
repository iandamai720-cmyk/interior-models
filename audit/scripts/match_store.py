import json,os,sys,numpy as np,torch,open_clip
from PIL import Image
sys.path.insert(0,'/workspace/audit'); from groups import CG
torch.set_num_threads(6)
R='/workspace/audit'
A=json.load(open('/workspace/interior-lib/catalog.json'))['assets']
fc=json.load(open(f'{R}/fix_cat.json')); meta=json.load(open(f'{R}/store_meta.json'))
d=np.load(f'{R}/clip.npz',allow_pickle=True); ids=list(d['ids']); im=d['im']
drop={k for k,v in fc.items() if v.get('drop')}
mcat={a['id']:fc.get(a['id'],{}).get('category',a['category']) for a in A if a['id'] in set(ids)}
m,_,pre=open_clip.create_model_and_transforms('ViT-B-32',pretrained='laion2b_s34b_b79k'); m.eval(); tok=open_clip.get_tokenizer('ViT-B-32')
S=[a for a in A if a['type']=='store_product']
EN=dict(biały='white',czarny='black',grafitowy='graphite',antracytowy='anthracite',jasnoszary='light grey',ciemnoszary='dark grey',szary='grey',srebrny='silver',chrom='chrome',złoty='gold',beżowy='beige',brązowy='brown',ciemnozielony='dark green',zielony='green',turkusowy='turquoise',granatowy='navy blue',niebieski='blue',różowy='pink',żółty='yellow',czerwony='red',terakota='terracotta',dąb='oak wood',orzech='walnut wood',sosna='pine wood',brzoza='birch wood',buk='beech wood',naturalny='natural wood')
def en_col(c):
    if not c: return ''
    for k,v in EN.items():
        if k in c: return v
    return ''
emb={}
paths=[(a['id'],f'{R}/storeimg/{a["id"]}.img') for a in S if meta[a['id']]['image_verified']]
with torch.no_grad():
    for i in range(0,len(paths),32):
        ims=[];ok=[]
        for sid,p in paths[i:i+32]:
            try: ims.append(pre(Image.open(p).convert('RGB')));ok.append(sid)
            except Exception as e: print('bad',sid,e)
        e=torch.nn.functional.normalize(m.encode_image(torch.stack(ims)),dim=-1).numpy()
        for sid,v in zip(ok,e): emb[sid]=v
    txt={}
    for a in S:
        md=meta[a['id']]; q=f"a 3D render of a {en_col(md['colour'])} {md['category'].replace('_',' ')}".replace('  ',' ')
        txt[a['id']]=torch.nn.functional.normalize(m.encode_text(tok([q])),dim=-1).numpy()[0]
idx={k:i for i,k in enumerate(ids)}
res={}
for a in S:
    sid=a['id']; md=meta[sid]; c=md['category']; g=CG.get(c,'?')
    if c=='skirting_board': res[sid]=dict(mode=mode,cat=c,top=[],ncand=0); continue
    cand=[k for k in ids if k not in drop and mcat[k]==c]
    near=[]
    q=emb.get(sid); mode='image' if q is not None else 'text'
    if q is None: q=txt[sid]
    def sc(ks,pen): return [(float(im[idx[k]]@q)-pen,k) for k in ks]
    tq=txt[sid]
    allc=sorted(sc(cand,0),reverse=True)[:8]
    # rerank: image (or text) similarity + colour/type text prompt vs thumb
    rr_=sorted([(s+(0.5*float(im[idx[k]]@tq) if mode=='image' else 0),s,k) for s,k in allc],reverse=True)[:5]
    res[sid]=dict(mode=mode,cat=c,top=[(round(s,4),k,mcat[k],round(float(im[idx[k]]@tq),4),round(f,4)) for f,s,k in rr_],ncand=len(cand))
json.dump(res,open(f'{R}/match_res.json','w'),indent=0)
np.savez(f'{R}/store_emb.npz',sids=np.array(list(emb)),e=np.array(list(emb.values())))
import collections
for mode in ['image','text']:
    v=[r['top'][0][0] for r in res.values() if r['mode']==mode and r['top']]
    print(mode,len(v),np.percentile(v,[5,25,50,75,95]).round(3))
print('MATCHDONE')
