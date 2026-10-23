# copy re-rendered thumbs + fixed GLBs from main working tree into shard repos (idempotent, sha-verified)
import json,hashlib,shutil,os
L='/workspace/interior-lib'; S='/workspace/shards'
A={a['id']:a for a in json.load(open(f'{L}/catalog.json'))['assets']}
rr=json.load(open('/workspace/audit/rr/all.json'))
h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
n=dict(glb=0,thumb=0,ok=0,bad=0)
for i,e in rr.items():
    sh=A[i]['shard']
    if sh=='interior-models': continue
    for rel,key,kind in ((e['file'],'glb_sha256','glb'),(e['thumb'],'thumb_sha256','thumb')):
        src=f'{L}/{rel}'; dst=f'{S}/{sh}/{rel}'
        if h(src)!=e[key]: n['bad']+=1; print('SRC MISMATCH',i,rel); continue
        if os.path.exists(dst) and h(dst)==e[key]: n['ok']+=1; continue
        os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copyfile(src,dst); n[kind]+=1
print(n)
