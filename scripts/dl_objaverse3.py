import json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
C = json.load(open("/workspace/interior-lib/tmp/objav3_cands.json")); D = "/workspace/interior-lib/staging/objaverse3"
def dl(c):
    p = f"{D}/{c['uid']}.glb"
    if os.path.exists(p): return "cached"
    loc = f"/home/box/.objaverse/hf-objaverse-v1/{c['path']}"
    if os.path.exists(loc): os.link(loc, p) if False else open(p, "wb").write(open(loc, "rb").read()); return "local"
    try:
        d = urllib.request.urlopen(f"https://huggingface.co/datasets/allenai/objaverse/resolve/main/{c['path']}", timeout=300).read()
        open(p + ".part", "wb").write(d); os.rename(p + ".part", p); return "ok"
    except Exception as e: return f"ERR {e}"
with ThreadPoolExecutor(10) as ex:
    for c, r in zip(C, ex.map(dl, C)): print(c["uid"], r, flush=True)
print("DONE")
