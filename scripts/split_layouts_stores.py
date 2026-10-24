"""2026-10-24: main Pages site ~997 MB -> move v1 layouts to shard interior-models-layouts-2 and store-product detail/store API to shard interior-models-stores.
Idempotent: rewrites catalog.json (shards, layout urls/shard, store_product api_url) and writes tmp/old_urls_2026-10-24.txt."""
import json
L='/workspace/interior-lib'; GH='https://iandamai720-cmyk.github.io'
cat=json.load(open(f'{L}/catalog.json')); A=cat['assets']; MAIN=f'{GH}/interior-models'
LAY2=f'{GH}/interior-models-layouts-2'; ST=f'{GH}/interior-models-stores'
cat['shards']['interior-models-layouts-2']=LAY2+'/'; cat['shards']['interior-models-stores']=ST+'/'
old=[]; n=dict(layout=0,store=0)
for a in A:
    if a['type']=='layout' and a.get('shard')=='interior-models':
        for k,v in list(a['urls'].items()):
            if v.startswith(MAIN+'/layouts/'): old.append(v); a['urls'][k]=LAY2+v[len(MAIN):]
        if a['url'].startswith(MAIN+'/layouts/'): a['url']=LAY2+a['url'][len(MAIN):]
        a['shard']='interior-models-layouts-2'; n['layout']+=1
    if a['type']=='store_product' and a['api_url'].startswith(MAIN+'/api/store-products/'):
        a['api_url']=ST+a['api_url'][len(MAIN):]; n['store']+=1
cat['store_products_note']=cat['store_products_note'].split(' Dane szczegółowe')[0]+' Dane szczegółowe sklepów (api/store-products/{id}.json, api/store/…) serwuje shard interior-models-stores; api/country/* i catalog.json zostają w głównym repo.'
json.dump(cat,open(f'{L}/catalog.json','w'),indent=1,ensure_ascii=False)
if old: open(f'{L}/tmp/old_urls_2026-10-24.txt','w').write('\n'.join(sorted(set(old)))+'\n')
print(n,len(old))
