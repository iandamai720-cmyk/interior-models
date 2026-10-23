import json
from PIL import Image,ImageDraw
R='/workspace/audit'; res=json.load(open(f'{R}/match_res.json')); rr=json.load(open(f'{R}/rr/all.json'))
import os
items=sorted([(r['top'][0][0],k) for k,r in res.items() if r['mode']=='image' and r['top']])
T=150
TH={}
for i,e in rr.items():
    TH[i]='/workspace/interior-lib/'+e['thumb']
os.makedirs(f'{R}/cs',exist_ok=True)
per=40
for si in range(0,len(items),per):
    ch=items[si:si+per]; W=Image.new('RGB',(5*2*T+40,8*(T+14)),'white'); d=ImageDraw.Draw(W)
    for j,(s,k) in enumerate(ch):
        x=(j%5)*(2*T+8); y=(j//5)*(T+14)
        a=Image.open(f'{R}/storeimg/{k}.img').convert('RGB'); a.thumbnail((T,T)); W.paste(a,(x,y))
        mk=res[k]['top'][0][1]; p=TH.get(mk)
        if p and os.path.exists(p): b=Image.open(p).convert('RGB'); b.thumbnail((T,T)); W.paste(b,(x+T,y))
        d.text((x,y+T),f"{si+j} {s:.3f} {res[k]['cat'][:12]}>{res[k]['top'][0][2][:10]}",fill='black')
    W.save(f'{R}/cs/x{si//per}.jpg',quality=80)
print(len(items))
