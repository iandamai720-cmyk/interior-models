import json,os,sys,numpy as np,torch,open_clip
from PIL import Image
torch.set_num_threads(int(sys.argv[1]) if len(sys.argv)>1 else 4)
ROOT='/workspace/interior-lib'
A=json.load(open(f'{ROOT}/catalog.json'))['assets']
M=[a for a in A if a['type'] in('furniture','appliance','fixture')]
S=[a for a in A if a['type']=='store_product']
m,_,pre=open_clip.create_model_and_transforms('ViT-B-32',pretrained='laion2b_s34b_b79k'); m.eval(); tok=open_clip.get_tokenizer('ViT-B-32')
CATS=sorted({a['category'] for a in M+S})
def T(xs):
    out=[]
    with torch.no_grad():
        for i in range(0,len(xs),128):
            e=m.encode_text(tok(xs[i:i+128])); out.append(torch.nn.functional.normalize(e,dim=-1))
    return torch.cat(out).numpy()
def I(paths):
    out=[]
    with torch.no_grad():
        for i in range(0,len(paths),32):
            ims=[]
            for p in paths[i:i+32]:
                try: ims.append(pre(Image.open(p).convert('RGB')))
                except Exception: ims.append(torch.zeros(3,224,224))
            e=m.encode_image(torch.stack(ims)); out.append(torch.nn.functional.normalize(e,dim=-1))
            print('img',i,flush=True)
    return torch.cat(out).numpy()
cat_t=T([f"a 3D render of a {c.replace('_',' ')}" for c in CATS])
name_t=T([f"a 3D render of {a['name']}, a {a['category'].replace('_',' ')}" for a in M])
thumbs=[f"{ROOT}/{os.path.dirname(a['file'])}/{a['id']}.jpg" for a in M]
im=I(thumbs)
simg=[f"/workspace/audit/storeimg/{a['id']}.img" for a in S]
sim_img=I(simg)
sname_t=T([f"a photo of {a['name']}" for a in S])
np.savez('/workspace/audit/clip.npz',cats=np.array(CATS),cat_t=cat_t,name_t=name_t,im=im,ids=np.array([a['id'] for a in M]),sids=np.array([a['id'] for a in S]),sim_img=sim_img,sname_t=sname_t)
print('CLIPDONE')
