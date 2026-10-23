"""Turn-6: CC0 PBR material sets (ambientCG + Poly Haven) -> materials/<category>/<id>/<id>_{color,normal,roughness,ao,metalness,opacity}.jpg
2K for floors/walls/countertops/wood/metal, 1K for fabrics/leather/carpet. Normal = OpenGL convention (Blender)."""
import json, os, re, io, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
ROOT = "/workspace/interior-lib"; UA = {"User-Agent": "interior-lib/1.0 (personal asset library)"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300).read()
A = json.load(open(f"{ROOT}/tmp/acg_all.json"))
# ambientCG displayCategory -> (our category, n, res)
ACG = {"Wood Floor":("floor_wood",22,"2K"),"Tiles":("floor_tiles",24,"2K"),"Marble":("countertop",10,"2K"),"Terrazzo":("countertop",6,"2K"),"Granite":("countertop",5,"2K"),
 "Travertine":("countertop",3,"2K"),"Onyx":("countertop",2,"2K"),"Porcelain":("countertop",2,"2K"),"Concrete":("floor_concrete",8,"2K"),"Painted Plaster":("wall_plaster",8,"2K"),
 "Plaster":("wall_plaster",4,"2K"),"Paint":("wall_paint",5,"2K"),"Wallpaper":("wall_wallpaper",5,"2K"),"Bricks":("wall_brick",8,"2K"),"Painted Bricks":("wall_brick",3,"2K"),
 "Fabric":("fabric",14,"1K"),"Leather":("leather",6,"1K"),"Carpet":("floor_carpet",7,"1K"),"Wicker":("fabric",3,"1K"),"Wood":("wood",8,"2K"),"Painted Wood":("wood",3,"2K"),
 "Metal":("metal",5,"1K"),"Plastic":("plastic",2,"1K"),"Cork":("misc",2,"1K"),"Chipboard":("wood",1,"1K"),"Tatami":("floor_carpet",1,"1K"),"Facade":("wall_plaster",0,"2K")}
BAD = re.compile(r"dirty|damaged|broken|rust|moss|old|weather|cracked|grunge|scratch", re.I)
sel = []
for dc, (cat, n, res) in ACG.items():
    xs = sorted([a for a in A if a["displayCategory"] == dc and not BAD.search(" ".join(a.get("tags", [])) + a["assetId"])], key=lambda a: -(a.get("popularityScore") or 0))
    for a in xs[:n]:
        z = [d for d in a["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"] if d["attribute"] == f"{res}-JPG"]
        if z: sel.append(dict(src="ambientcg", id=a["assetId"], name=a["displayName"], cat=cat, res=res, zip=z[0]["downloadLink"], page=a["shortLink"], tags=a.get("tags", [])))
PH = json.load(open(f"{ROOT}/tmp/ph_tex.json"))
PHR = [(r"veneer|laminate_floor|parquet|plank_flooring|wood_floor$|oak_wood_planks|kitchen_wood|fine_grained_wood|wood_table", "floor_wood"),
       (r"interior_tiles|floor_tiles|terrazzo|terracotta_floor|granite_tile|grey_cartago|herringbone_concrete_tile|marble", "floor_tiles"),
       (r"^brushed_concrete|^concrete_floor$|^concrete_floor_0[23]$|polished_concrete|concrete_floor_painted", "floor_concrete"),
       (r"beige_wall|grey_plaster|clay_plaster|white_plaster|painted_plaster|plaster_wall|blue_plaster_wall|rough_plaster_0|plastered_wall", "wall_plaster"),
       (r"painted_brick$|^red_brick$|brick_wall_0(0[1-6]|2)$|white_brick|^brick_4$|mixed_brick_wall", "wall_brick")]
FAB = set(k for k, v in PH.items() if "fabric" in v["categories"]) - {"dirty_carpet"}
phsel = {}
for k, v in PH.items():
    if BAD.search(k): continue
    if k in FAB: phsel[k] = ("leather" if "leather" in k else "fabric"); continue
    for rx, c in PHR:
        if re.search(rx, k): phsel[k] = c; break
for k, c in sorted(phsel.items()):
    sel.append(dict(src="polyhaven", id=k, name=PH[k]["name"], cat=c, res="1K" if c in ("fabric", "leather") else "2K", page=f"https://polyhaven.com/a/{k}",
                    tags=PH[k].get("tags", []), authors=list(PH[k].get("authors", {}).keys())))
print(len(sel), "materials selected")
MAP = {"color": r"_Color\.|_diff_|_Diffuse", "normal": r"_NormalGL\.|_nor_gl_", "roughness": r"_Roughness\.|_rough_", "ao": r"_AmbientOcclusion\.|_ao_",
       "metalness": r"_Metalness\.|_metal_", "opacity": r"_Opacity\."}
def save(img_bytes, out, res):
    im = Image.open(io.BytesIO(img_bytes)); px = 2048 if res == "2K" else 1024
    if im.mode not in ("RGB", "L"): im = im.convert("RGB")
    if max(im.size) > px: im = im.resize((px, px * im.size[1] // im.size[0]), Image.LANCZOS)
    im.save(out, "JPEG", quality=88, optimize=True)
def do(m):
    slug = ("acg_" if m["src"] == "ambientcg" else "ph_") + m["id"].lower()
    d = f"{ROOT}/materials/{m['cat']}/{slug}"; m["slug"] = slug; m["dir"] = d
    if os.path.exists(f"{d}/{slug}_color.jpg"): return m, "cached"
    os.makedirs(d, exist_ok=True); maps = {}
    try:
        if m["src"] == "ambientcg":
            z = zipfile.ZipFile(io.BytesIO(get(m["zip"])))
            for n in z.namelist():
                for key, rx in MAP.items():
                    if re.search(rx, n) and key not in maps: maps[key] = z.read(n)
        else:
            f = json.loads(get(f"https://api.polyhaven.com/files/{m['id']}")); r = m["res"].lower()
            if "Diffuse" not in f:
                alt = sorted(k for k in f if re.match(r"col", k, re.I))
                if alt: f["Diffuse"] = f[alt[0]]
            for key, pk in (("color", "Diffuse"), ("normal", "nor_gl"), ("roughness", "Rough"), ("ao", "AO"), ("metalness", "Metal")):
                if pk in f and r in f[pk]: maps[key] = get(f[pk][r]["jpg"]["url"])
        for key, b in maps.items(): save(b, f"{d}/{slug}_{key}.jpg", m["res"])
        m["maps"] = sorted(maps); return m, "ok" if "color" in maps else "NOCOLOR"
    except Exception as e: return m, f"ERR {e}"
out = []
with ThreadPoolExecutor(6) as ex:
    for m, r in ex.map(do, sel):
        if "maps" not in m and os.path.isdir(m["dir"]): m["maps"] = sorted(f.rsplit("_", 1)[1][:-4] for f in os.listdir(m["dir"]) if f.endswith(".jpg"))
        print(m["slug"], r, flush=True); out.append(m)
json.dump(out, open(f"{ROOT}/tmp/materials.json", "w"), indent=1); print("DONE")
