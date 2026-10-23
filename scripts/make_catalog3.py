"""Turn-6 catalog (extends turn-4 logic): adds IKEA PL batch 3 (ikea2/ikea3 shards), Poly Haven batch 3, curated Objaverse, materials, apt70/loft35 layouts.
Turn-4 catalog: keeps the turn-1..3 entries of catalog.json and adds the IKEA PL / Poly Haven / Kenney models,
the Polish store products (has_own_model=false -> similar_model_id) and the house1/house2 layouts.
Files of the new models live in shard repos (absolute URLs in `url`)."""
import json, os, re, glob, datetime, collections, hashlib
ROOT = "/workspace/interior-lib"
GH = "https://iandamai720-cmyk.github.io"
MAIN = f"{GH}/interior-models"
SHARDS = {"ikea/": "interior-models-ikea", "polyhaven/": "interior-models-extra", "kenney/": "interior-models-extra",
          "layouts/house1_": "interior-models-layouts", "layouts/house2_": "interior-models-layouts",
          "layouts/apt70_": "interior-models-layouts", "layouts/loft35_": "interior-models-layouts",
          "ikea2/": "interior-models-ikea-2", "ikea3/": "interior-models-ikea-3",
          "objaverse1/": "interior-models-objaverse", "objaverse2/": "interior-models-objaverse-2", "objaverse3/": "interior-models-objaverse-3", "materials/": "interior-models-materials"}
def url(p):
    if not p: return None
    for pre, repo in SHARDS.items():
        if p.startswith(pre): return f"{GH}/{repo}/{p}"
    return f"{MAIN}/{p}"
def shard(p):
    return next((r for pre, r in SHARDS.items() if p.startswith(pre)), "interior-models")
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower().translate(str.maketrans("ąćęłńóśźżäöåü", "acelnoszzaoau"))).strip("-")
old = json.load(open(f"{ROOT}/tmp/catalog_turn3.json"))  # frozen turn-3 catalog
OLD = [a for a in old["assets"] if a["type"] != "layout" and not a.get("turn4")]
OLDL = [a for a in old["assets"] if a["type"] == "layout" and a["layout"] in ("apartment", "house")]
for a in OLD:
    a.setdefault("store", "IKEA" if a.get("brand") == "IKEA" else None)
    a.setdefault("price_pln", None); a.setdefault("url_pl", None)
    a.setdefault("url_uk", a["source_url"] if a.get("brand") == "IKEA" and "/gb/" in (a.get("source_url") or "") else None)
    a["has_own_model"] = True; a["similar_model_id"] = None; a["shard"] = "interior-models"
APPL = {"fridge", "cooker", "microwave", "kettle", "coffee_machine", "washing_machine", "dryer", "cooker_hood", "kitchen_appliance_small", "tv", "electronics", "computer", "ceiling_fan",
        "oven", "dishwasher", "hob", "air_purifier", "air_conditioner", "kitchen_appliance", "toaster", "laptop", "monitor", "printer", "router", "headphones", "speaker", "hifi", "radio",
        "record_player", "projector", "phone", "camera", "keyboard", "vacuum", "heater", "fan", "water_cooler", "boiler", "sewing_machine", "grill"}
FIXT = {"toilet", "shower", "bathtub", "kitchen_sink", "window", "door", "stairs", "towel_rail", "bathroom_tap", "kitchen_tap", "radiator", "ventilation", "door_hardware",
        "curtain_rail", "decking", "fireplace", "bathroom_sink", "electrical"}
DARK = re.compile(r"czarn|antracyt|ciemn|brąz|grafit|black|dark|walnut|orzech|brown", re.I)
def style_of(txt): return "dark" if DARK.search(txt or "") else "scandi"
IK = {p["article_number"]: p for p in json.load(open(f"{ROOT}/tmp/ikea_pl.json"))}
RES = {}
for f in glob.glob(f"{ROOT}/tmp/res_*.json"): RES.update(json.load(open(f)))
SPEC = {}
for f in ("spec_ph", "spec_kenney", "spec_ikea_pl"):
    for s in json.load(open(f"{ROOT}/tmp/{f}.json")): SPEC[s["key"]] = s
PHM = json.load(open(f"{ROOT}/tmp/ph_meta.json"))
seen = {a["id"] for a in OLD}; new = []
for n in json.load(open(f"{ROOT}/tmp/new_assets.json")):
    k, s, r = n["key"], n["size"], RES.get(n["key"], {})
    sp = SPEC.get(k, {}); cat = n["category"]
    typ = "appliance" if cat in APPL else "fixture" if cat in FIXT else "furniture"
    d = dict(key=k, type=typ, category=cat, file=n["file"], file_size_bytes=os.path.getsize(f"{ROOT}/{n['file']}"), format="glb",
             dimensions_m={"x": s[0], "y": s[1], "z": s[2]}, triangles=r.get("tris"), preview=sp.get("preview") or r.get("preview"),
             orientation="Blender Z-up after glTF import; footprint centred on origin; floor z=0; front faces -Y, back +Y; real-world metres",
             has_own_model=True, similar_model_id=None, turn4=True)
    if n["source"] == "ikea_pl":
        p = IK[n["article_number"]]; aid = f"ikea-{p['article_number']}"
        if aid in seen: aid = f"ikea-pl-{p['article_number']}"
        cols = [c for c in (p.get("colours") or [p.get("colour")]) if c]
        d.update(id=aid, name=p["name"], full_name=p["full_name"], brand="IKEA", article_number=p["article_number"], room=p["room"],
                 style=style_of(p["full_name"]), colour=p.get("colour") or None, colours=cols, material=p.get("material"),
                 dimensions_listed={"width": p["width"], "depth": p["depth"], "height": p["height"], "text": p["dims_text"] or None},
                 store="IKEA", price_pln=p["price_pln"], price_gbp=p.get("price_gbp"), url_pl=p["url_pl"], url_uk=p["url_uk"],
                 source="IKEA", source_url=p["url_pl"], glb_source_url=p["glb_url"], image_url=p["image"], author="IKEA", license=p["license"],
                 ikea_category_path=p.get("ikea_category_path"), variant_group=slug(p["name"]))
    elif n["source"] == "ph":
        m = PHM.get(sp["ph_id"], {}); nm = m.get("name", k)
        d.update(id=f"polyhaven-{k.removeprefix('ph_').replace('_', '-')}", name=nm, full_name=nm, brand=None, article_number=None,
                 room=sp.get("room", "living"), style="scandi", colour=None, colours=[], material=None, dimensions_listed=None,
                 store=None, price_pln=None, url_pl=None, url_uk=None, source="Poly Haven", source_url=f"https://polyhaven.com/a/{sp['ph_id']}",
                 glb_source_url=f"https://dl.polyhaven.org/file/ph-assets/Models/gltf/1k/{sp['ph_id']}/{sp['ph_id']}_1k.gltf", image_url=f"https://cdn.polyhaven.com/asset_img/primary/{sp['ph_id']}.png",
                 author=", ".join(m.get("authors", [])) or "Poly Haven", license="CC0 1.0", ph_tags=m.get("tags"))
    else:
        nm = "Kenney " + re.sub(r"(?<!^)([A-Z])", r" \1", sp["kenney_id"]).lower()
        d.update(id=f"kenney-{k.removeprefix('kenney_').replace('_', '-')}", name=nm, full_name=nm, brand=None, article_number=None,
                 room=sp.get("room", "living"), style="lowpoly", colour=None, colours=[], material=None, dimensions_listed=None,
                 store=None, price_pln=None, url_pl=None, url_uk=None, source="Kenney", source_url="https://kenney.nl/assets/furniture-kit",
                 glb_source_url=None, image_url=None, author="Kenney (kenney.nl)", license="CC0 1.0",
                 license_note="Low-poly stylised kit; scaled x2 to approximate real size")
    assert d["id"] not in seen, d["id"]; seen.add(d["id"])
    d["tags"] = sorted({cat, d["room"], d["style"], typ, slug(d["source"]), *[slug(c) for c in d["colours"]]} | ({"kids"} if d["room"] == "kids" else set()))
    new.append(d)
# ---------- turn 6: IKEA PL batch 3, Poly Haven batch 3, Objaverse, materials
QA = json.load(open(f"{ROOT}/tmp/qa_drop.json"))
DROP = set(QA.get("ikea3", [])) | set(QA.get("obj3", [])) | set(QA.get("ph3", []))
MOVED = json.load(open(f"{ROOT}/tmp/moved_files.json")) if os.path.exists(f"{ROOT}/tmp/moved_files.json") else {}  # key -> file path after shard split
def t6(k, typ_cat, file, r, prev):
    cat = typ_cat; s = r["size"]
    typ = "appliance" if cat in APPL else "fixture" if cat in FIXT else "furniture"
    return dict(key=k, type=typ, category=cat, file=file, file_size_bytes=os.path.getsize(f"{ROOT}/{file}"), format="glb",
                dimensions_m={"x": s[0], "y": s[1], "z": s[2]}, triangles=r.get("tris"), preview=prev,
                orientation="Blender Z-up after glTF import; footprint centred on origin; floor z=0; front faces -Y, back +Y; real-world metres",
                has_own_model=True, similar_model_id=None, turn6=True)
def finish(d):
    assert d["id"] not in seen, d["id"]; seen.add(d["id"])
    d["tags"] = sorted({d["category"], d["room"], d["style"], d["type"], slug(d["source"]), *[slug(c) for c in d["colours"]]} | ({"kids"} if d["room"] == "kids" else set()))
    new.append(d)
IK3 = {f"{p['key']}_{p['article_number']}": p for p in json.load(open(f"{ROOT}/tmp/ikea_pl3.json"))}
ikea_arts = {a.get("article_number") for a in OLD + new if a.get("brand") == "IKEA"}
for k, p in IK3.items():
    r = RES.get(k)
    if not r or k in DROP or p["article_number"] in ikea_arts: continue
    f = MOVED.get(k, r["file"])
    if not os.path.exists(f"{ROOT}/{f}"): continue
    ikea_arts.add(p["article_number"])
    d = t6(k, p["category"], f, r, r["preview"]); aid = f"ikea-{p['article_number']}"
    if aid in seen: aid = f"ikea-pl-{p['article_number']}"
    cols = [c for c in (p.get("colours") or [p.get("colour")]) if c]
    d.update(id=aid, name=p["name"], full_name=p["full_name"], brand="IKEA", article_number=p["article_number"], room=p["room"],
             style=style_of(p["full_name"]), colour=p.get("colour") or None, colours=cols, material=p.get("material"),
             dimensions_listed={"width": p["width"], "depth": p["depth"], "height": p["height"], "text": p.get("dims_text") or None},
             store="IKEA", price_pln=p["price_pln"], price_gbp=p.get("price_gbp"), url_pl=p["url_pl"], url_uk=p.get("url_uk"),
             source="IKEA", source_url=p["url_pl"], glb_source_url=p["glb_url"], image_url=p["image"], author="IKEA", license=p["license"],
             ikea_category_path=p.get("ikea_category_path"), variant_group=slug(p["name"]))
    finish(d)
for sp in json.load(open(f"{ROOT}/tmp/spec_ph3.json")):
    k = sp["key"]; r = RES.get(k)
    if not r or k in DROP: continue
    m = PHM.get(sp["ph_id"], {}); nm = m.get("name", k)
    d = t6(k, sp["category"], r["file"], r, r["preview"])
    d.update(id=f"polyhaven-{k.removeprefix('ph_').replace('_', '-')}", name=nm, full_name=nm, brand=None, article_number=None,
             room=sp.get("room", "living"), style="scandi", colour=None, colours=[], material=None, dimensions_listed=None,
             store=None, price_pln=None, url_pl=None, url_uk=None, source="Poly Haven", source_url=f"https://polyhaven.com/a/{sp['ph_id']}",
             glb_source_url=f"https://dl.polyhaven.org/file/ph-assets/Models/gltf/2k/{sp['ph_id']}/{sp['ph_id']}_2k.gltf", image_url=f"https://cdn.polyhaven.com/asset_img/primary/{sp['ph_id']}.png",
             author=", ".join(m.get("authors", [])) or "Poly Haven", license="CC0 1.0", ph_tags=m.get("tags"))
    finish(d)
LIC = {"by": "CC BY 4.0", "by-sa": "CC BY-SA 4.0", "cc0": "CC0 1.0", "by-nc": "CC BY-NC 4.0"}
for c in json.load(open(f"{ROOT}/tmp/objav3_cands.json")):
    k = c["key"]; r = RES.get(k)
    f = MOVED.get(k, r["file"]) if r else None
    if not r or k in DROP or not os.path.exists(f"{ROOT}/{f}"): continue
    nm = re.sub(r"\s+", " ", re.sub(r"[_\-]+", " ", c["name"])).strip()
    nm = (nm[:1].upper() + nm[1:])[:80] if nm else c["cat"].replace("_", " ").title()
    d = t6(k, c["cat"], f, r, r["preview"])
    d.update(id=f"objaverse-{c['cat'].replace('_', '-')}-{c['uid'][:10]}", name=nm, full_name=nm, brand=None, article_number=None,
             room=c["room"], style=style_of(c["name"]), colour=None, colours=[], material=None, dimensions_listed=None,
             store=None, price_pln=None, url_pl=None, url_uk=None, source="Objaverse 1.0 (Sketchfab)", source_url=c["url"],
             glb_source_url=f"https://huggingface.co/datasets/allenai/objaverse/resolve/main/{c['path']}", image_url=None,
             author=c["author"], license=LIC.get(c["license"], c["license"]), objaverse_uid=c["uid"], lvis_category=c["lvis"],
             sketchfab_likes=c["likes"], license_note=f"{LIC.get(c['license'], c['license'])} – credit '{c['author']}' (Sketchfab) when used; rescaled to ~{c['target_m']} m ({c['scale_axis']} axis), textures max 1K")
    finish(d)
TILE = {"floor_tiles": 1.0, "wall_tiles": 1.0, "fabric": 0.5, "leather": 0.5, "countertop": 1.0, "wall_brick": 2.0}
SURF = lambda c: c.split("_")[0] if c.startswith(("floor", "wall")) else c
MATS = []
for m in json.load(open(f"{ROOT}/tmp/materials.json")):
    folder = f"materials/{m['cat']}/{m['slug']}"
    files = {mp: f"{folder}/{m['slug']}_{mp}.jpg" for mp in m["maps"] if os.path.exists(f"{ROOT}/{folder}/{m['slug']}_{mp}.jpg")}
    if not files or not os.path.exists(f"{ROOT}/previews/materials/{m['slug']}.png") or m["slug"] in set(QA.get("materials", [])): continue
    ph = m["src"] == "polyhaven"
    MATS.append(dict(id=f"material-{m['slug'].replace('_', '-')}", key=m["slug"], slug=m["slug"], type="material", name=m["name"], full_name=m["name"], category=m["cat"], room=SURF(m["cat"]),
        style=style_of(m["name"] + " " + " ".join(m["tags"])), colour=None, colours=[], resolution=m["res"], tile_m=TILE.get(m["cat"], 2.0), maps_available=sorted(files),
        files=files, folder=folder, file=None, file_size_bytes=sum(os.path.getsize(f"{ROOT}/{f}") for f in files.values()), format="jpg (PBR: color, normal-GL, roughness, ao[, displacement])",
        preview=f"previews/materials/{m['slug']}.png", has_own_model=False, similar_model_id=None, store=None, price_pln=None, url_pl=None, url_uk=None,
        source="Poly Haven" if ph else "ambientCG", source_url=m["page"], author=", ".join(m.get("authors", [])) if ph else "ambientCG (Lennart Demes)", license="CC0 1.0",
        blender="blender/load_material.py – loads api/materials/<id>.json into a Principled BSDF node tree",
        tags=sorted({m["cat"], SURF(m["cat"]), "material", "pbr", "ph" if ph else "ambientcg", *[slug(t) for t in m["tags"][:8]]}), turn6=True))

# colour variants: same IKEA product name, different article
grp = collections.defaultdict(list)
for a in new:
    if a.get("variant_group"): grp[a["variant_group"]].append(a["id"])
for a in new:
    if a.get("variant_group"): a["variants"] = [i for i in grp[a["variant_group"]] if i != a["id"]]
MODELS = OLD + new
# ---------- store products (no downloadable 3D -> similar model)
ALIAS = {"washbasin": ["bathroom_sink", "bathroom_vanity"], "radiator": ["radiator"], "kids_bed": ["kids_bed", "bed_single", "bunk_bed"],
         "kitchen_base_cabinet": ["kitchen_base_cabinet", "kitchen_cabinet", "kitchen"], "garden_chair": ["garden_chair", "balcony_furniture"],
         "garden_table": ["garden_table", "balcony_furniture"], "pendant_lamp": ["pendant_lamp", "ceiling_lamp", "lamp"], "mirror": ["mirror", "bathroom_mirror"],
         "shoe_cabinet": ["shoe_cabinet", "hallway_storage"], "sideboard": ["sideboard", "cabinet", "display_cabinet"], "pouffe": ["pouffe", "footstool"],
         "plant_pot": ["plant_pot", "plant"], "curtains": ["curtains"], "bed_double": ["bed_double", "bed"], "sofa": ["sofa", "sofa_corner", "sofa_bed"]}
bycat = collections.defaultdict(list)
for a in MODELS: bycat[a["category"]].append(a)
CW = ["biał", "czarn", "szar", "dąb", "dab", "orzech", "beż", "be", "zielon", "niebiesk", "grafit", "antracyt", "brąz", "złot", "zlot", "naturaln", "granat", "róż", "drewn", "metal", "szkł", "tkanin", "welur", "skór", "narożn", "rozkład", "lustr", "okrąg", "rattan"]
def toks(t): t = (t or "").lower(); return {w for w in CW if w in t}
def similar(p):
    cands = []
    for c in ALIAS.get(p["category"], [p["category"]]): cands += bycat.get(c, [])
    if not cands: return None, None
    pt = toks(p["name"]); st = style_of(p["name"])
    h = int(hashlib.md5(p["url"].encode()).hexdigest(), 16)
    best = max(cands, key=lambda a: (len(pt & toks(a["full_name"] + " " + (a.get("colour") or ""))) * 2 + (a["style"] == st) + (a.get("brand") == "IKEA") * 0.5 - (a["source"] == "Kenney") * 1.5, (h ^ int(hashlib.md5(a["id"].encode()).hexdigest()[:8], 16)) % 997))
    return best, len(pt & toks(best["full_name"]))
stores = json.load(open(f"{ROOT}/tmp/stores/products_clean.json")); SP = []; sids = set()
for p in stores:
    base = f"{p['store_key']}-{slug(p['name'])[:60]}"; sid = base; i = 2
    while sid in sids: sid = f"{base}-{i}"; i += 1
    sids.add(sid)
    sim, score = similar(p)
    SP.append(dict(id=sid, type="store_product", key=sid.replace("-", "_"), name=p["name"], full_name=p["name"], brand=p["store"], store=p["store"], store_key=p["store_key"],
        article_number=None, category=p["category"], room=p["room"], style=style_of(p["name"]), colour=None, colours=[], material=None,
        price_pln=p["price_pln"], url_pl=p["url"], url_uk=None, source_url=p["url"], image_url=p.get("image"), name_from=p.get("name_from", "page"),
        has_own_model=False, similar_model_id=sim["id"] if sim else None, similar_match="colour/material keywords + style" if score else "same category",
        file=None, file_size_bytes=0, format=None, preview=sim["preview"] if sim else None, dimensions_m=sim["dimensions_m"] if sim else None,
        source=p["store"], author=None, license="Product data only (no 3D model published by the store); geometry = similar_model_id",
        tags=sorted({p["category"], p["room"], "store-product", p["store_key"], style_of(p["name"])}), turn4=True))
# ---------- layouts
by_key = {a["key"]: a for a in MODELS}
LAY = []
for a in OLDL:
    a["storeys"] = 1; a["shard"] = "interior-models"; LAY.append(a)
for j in sorted(glob.glob(f"{ROOT}/layouts/house[12]_*.json") + glob.glob(f"{ROOT}/layouts/apt70_*.json") + glob.glob(f"{ROOT}/layouts/loft35_*.json")):
    L = json.load(open(j)); tag = os.path.basename(j)[:-5]
    used = sorted({p["key"] for p in L["placed"] if p["key"] in by_key})
    style = L["style"]
    cols = {"scandi": ["white", "light oak", "beige", "light grey"], "dark": ["anthracite", "dark walnut", "black", "brown leather"]}[style]
    two = L["floors"] == 2
    pv = {"top_gf": f"previews/{tag}_top_gf.png", "top_ff": f"previews/{tag}_top_ff.png", "iso": f"previews/{tag}_iso.png", "iso_gf": f"previews/{tag}_iso_gf.png"} if two else \
         {"top": f"previews/{tag}_top.png", "iso": f"previews/{tag}_iso.png"}
    title = {"apt70": "3-room apartment", "loft35": "Loft / studio"}.get(L["layout"]) or ("Two-storey house" if two else "Single-storey house")
    LAY.append(dict(id=tag.replace("_", "-"), type="layout", name=f"{title} {L['total_area_m2']:.0f} m² – {'furnished, ' + style if L['furnished'] else 'empty shell, ' + style}",
        layout=L["layout"], furnished=L["furnished"], style=style, colours=cols, area_m2=L["total_area_m2"], outdoor_area_m2=L.get("outdoor_area_m2"),
        footprint_m=L["footprint_m"], storeys=L["floors"], storey_height_m=L.get("storey_height_m"), wall_height_m=2.7,
        rooms=L["rooms"], room_count=len([r for r in L["rooms"] if not r.get("outdoor")]), bedrooms=sum(r["type"] == "bedroom" for r in L["rooms"]),
        tags=sorted({L["layout"], style, "furnished" if L["furnished"] else "shell", "two-storey" if two else "single-storey", "apartment" if L["layout"] in ("apt70", "loft35") else "house"}),
        files={"blend": f"layouts/{tag}.blend", "glb": f"layouts/{tag}.glb", "meta": f"layouts/{tag}.json"},
        file_size_bytes=os.path.getsize(f"{ROOT}/layouts/{tag}.glb") + os.path.getsize(f"{ROOT}/layouts/{tag}.blend"),
        preview=f"previews/{tag}_iso.png", previews=pv,
        furniture_used=[{"key": k, "id": by_key[k]["id"], "type": by_key[k]["type"], "count": sum(p["key"] == k for p in L["placed"])} for k in used],
        placeholders=sorted({p["key"] for p in L["placed"] if p["key"].startswith("placeholder")}),
        credits=sorted({f"{by_key[k]['name']} – {by_key[k]['author']} ({by_key[k]['license']})" for k in used if by_key[k].get("source") != "IKEA"}), turn4=not L["layout"] in ("apt70", "loft35"), turn6=L["layout"] in ("apt70", "loft35")))
PLURAL = {"material": "materials", "layout": "layouts", "furniture": "furniture", "appliance": "appliances", "fixture": "fixtures", "store_product": "store-products"}
ALL = LAY + MODELS + SP + MATS
for a in ALL:
    if a["type"] == "material":
        a["maps"] = {k: url(v) for k, v in a["files"].items()}; a["url"] = a["maps"].get("color") or next(iter(a["maps"].values()))
        a["shard"] = shard(a["folder"]); a["folder_url"] = url(a["folder"]) + "/"; a["model_url"] = None
    elif a["type"] == "layout":
        a["urls"] = {k: url(v) for k, v in a["files"].items()}; a["url"] = a["urls"]["glb"]
        a["preview_urls"] = {k: url(v) for k, v in a["previews"].items()}; a["shard"] = shard(a["files"]["glb"])
    else:
        a["url"] = url(a["file"]); a["model_url"] = a["url"]
        if a["file"]: a["shard"] = shard(a["file"])
    if a["type"] == "store_product": a["model_url"] = next((url(m["file"]) for m in MODELS if m["id"] == a["similar_model_id"]), None); a["shard"] = None
    a["preview_url"] = url(a["preview"]); a["api_url"] = f"{MAIN}/api/{PLURAL[a['type']]}/{a['id']}.json"
    a.setdefault("store", None); a.setdefault("price_pln", None)
import subprocess
TR = set(subprocess.run(["git", "-C", ROOT, "ls-files", "previews"], capture_output=True, text=True).stdout.split())
PS = {}  # previews not in the main repo (Pages 1 GB limit) are served from the asset's own shard
for a in ALL:
    p = a.get("preview")
    if a["type"] != "layout" and p and p not in TR and a.get("shard") and a["shard"] != "interior-models": PS.setdefault(p, a["shard"])
for a in ALL:
    if a.get("preview") in PS: a["preview_url"] = f"{GH}/{PS[a['preview']]}/{a['preview']}"
json.dump(PS, open(f"{ROOT}/tmp/preview_shards.json", "w"), indent=0)
cat = dict(version=3, generated=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), units="metres",
    license_note="Per-asset licence in `license`/`author`/`source_url`. IKEA models: personal/demo use only. Objaverse (Sketchfab): CC BY / BY-SA / BY-NC as listed. Poly Haven & Kenney: CC0. Materials (ambientCG / Poly Haven): CC0. Store products (Agata, JYSK, BRW, VOX, Bodzio, Komfort, Castorama, Leroy Merlin, Wójcik): product data only, geometry via similar_model_id.",
    base_url=MAIN, catalog_url=f"{MAIN}/catalog.json", shards={r: f"{GH}/{r}/" for r in ["interior-models", *dict.fromkeys(SHARDS.values())]}, assets=ALL)
for _a in cat["assets"]:
    if _a.get("room") == "hall": _a["room"] = "hallway"
json.dump(cat, open(f"{ROOT}/catalog.json", "w"), indent=1, ensure_ascii=False)
print(collections.Counter(a["type"] for a in ALL), len(ALL))
print(collections.Counter(a.get("source") for a in MODELS))
print("ids w/o similar:", [a["id"] for a in SP if not a["similar_model_id"]][:10])
