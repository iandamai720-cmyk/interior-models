"""Download interior-relevant Poly Haven models (CC0) as glTF (1k/2k) into staging/polyhaven/<id>/"""
import json, os, re, urllib.request, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = "/workspace/interior-lib"; UA = {"User-Agent": "interior-lib/1.0 (personal asset library)"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
d = json.loads(get("https://api.polyhaven.com/assets?t=models"))
want = {'furniture','decorative','seating','lighting','table','shelves','dishes','vases','wall decoration','flowers','potted plants','books','appliances','electronics','office','bed','food','plants','instrument','containers'}
bad = {'rocks','trees','ground cover','grass','ships','buildings','structures','rigged'}
BL = re.compile(r"barrel|cleaner|jerrycan|military|microscope|welding|generator|searchlight|toolbox|tool_cart|drill|oil_tin|can_rusted|lubricant|spray|bleach|compost|cigarette|circuit|megaphone|metal_detector|multimeter|spacecraft|fire_alarm|lifebuoy|cash_register|barber|wet_floor|street|security_light|aircon|modular_street|plastic_crate|plastic_bottle|plastic_jerrycan|industrial_pastic|medical_box|long_life|russian_food|thermos|seadogs|binocular|torch|flashlight|pull_chain|radio_transceiver|filmstrip|treasure|katana|gothic_statue|bronze_|bull_head|lion_head|horse_head|didelta|leipoldtia|stinkkruid|rooibos|fern_02|shrub_sorrel|anthurium|pachira|seeding|cheesebox|wooden_crate|wooden_bucket|wine_barrel|wooden_barrels|lantern_01$|lightbulb|sprinkler|garden_hose|mounted_fluorescent|worn_metal_rack|projector_screen|camera_01|vintage_stapler|clipboard|office_notepads|digital_wrist|cassette|boombox|vintage_video|portable_|old_military|metal_trash|metal_jug|scandinavian_masonry|chinese_screen|old_bed_frame|wooden_bookshelf_worn", re.I)
sel = {}
for k, v in d.items():
    c = set(v.get("categories", []))
    if c & want and not c & bad and not BL.search(k): sel[k] = v
have = set()
for f in ("appliances/_sources.json",):
    for r in json.load(open(f"{ROOT}/{f}")):
        if "polyhaven" in str(r.get("source", "")).lower() or "poly haven" in str(r.get("source", "")).lower():
            have.add(r.get("uid") or r.get("ph_id") or "")
print(len(sel), "selected; already used:", have)
BIG = {'furniture','seating','table','shelves','bed'}
def dl(k):
    v = sel[k]; res = "2k" if set(v["categories"]) & BIG else "1k"
    out = f"{ROOT}/staging/polyhaven/{k}"
    if os.path.exists(f"{out}/{k}.gltf"): return k, res, "cached"
    try:
        files = json.loads(get(f"https://api.polyhaven.com/files/{k}"))
        g = files["gltf"].get(res) or files["gltf"].get("1k") or next(iter(files["gltf"].values()))
        g = g["gltf"]; os.makedirs(out, exist_ok=True)
        for rel, inf in g.get("include", {}).items():
            p = f"{out}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(get(inf["url"]))
        open(f"{out}/{k}.gltf", "wb").write(get(g["url"]))
        return k, res, "ok"
    except Exception as e:
        return k, res, f"ERR {e}"
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(dl, sorted(sel)): print(*r, flush=True)
meta = {k: dict(name=v["name"], categories=v["categories"], tags=v.get("tags", []), authors=list(v.get("authors", {}).keys()), dimensions=v.get("dimensions")) for k, v in sel.items()}
json.dump(meta, open(f"{ROOT}/tmp/ph_meta.json", "w"), indent=1)
