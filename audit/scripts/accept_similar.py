import json
res=json.load(open('match_res.json'))
img=sorted([(r['top'][0][0],k) for k,r in res.items() if r['mode']=='image' and r['top']])
txt=sorted([(r['top'][0][0],k) for k,r in res.items() if r['mode']=='text' and r['top']])
REJ_IMG={18,21,33,40,44}   # visually wrong type despite score>=0.50 (cs/x0,x1)
REJ_TXT={0,3,4,18,26,35}   # cs/t0: wrong type/colour
out={}
for i,(s,k) in enumerate(img):
    ok=s>=0.50 and i not in REJ_IMG
    out[k]=dict(similar=res[k]['top'][0][1] if ok else None,score=s,mode='image',reason=None if ok else ('score<0.50' if s<0.5 else 'visual reject'))
for i,(s,k) in enumerate(txt):
    ok=i not in REJ_TXT
    out[k]=dict(similar=res[k]['top'][0][1] if ok else None,score=s,mode='text',reason=None if ok else 'visual reject')
for k,r in res.items():
    if not r['top']: out[k]=dict(similar=None,score=None,mode=r['mode'],reason='no comparable model ('+r['cat']+')')
json.dump(out,open('similar.json','w'),indent=0,ensure_ascii=False)
import collections;print(len(out),collections.Counter((v['mode'],v['similar'] is not None) for v in out.values()))
