"""Import interior-models assets into Blender straight from the GitHub Pages catalog.

Use from Blender's Scripting tab: open this file, edit the CONFIG block below, press Run Script.
Or from the Python console / another script:
    exec(open("/path/import_from_catalog.py").read())   # or: import import_from_catalog as ic
    ic.list_assets(type="furniture", category="sofa")
    ic.list_assets(type="appliance", category="tv")      # types: layout, furniture, appliance, fixture, store_product
    ic.list_assets(store="JYSK", category="sofa", max_price=2500)   # Polish store products (geometry = similar_model_id)
    ic.import_asset("jysk-...")                          # store product -> imports its similar model, named after the product
    ic.import_asset("ikea-00263850", location=(1, 0, 0), rotation_deg=90)
    ic.import_filtered(type="layout", style="scandi", min_area=40, max_area=60, furnished=True)
Headless:  blender -b --python import_from_catalog.py -- --id house-scandi-furnished --save out.blend

Assets are cached in ~/.cache/interior-models (override with env INTERIOR_MODELS_CACHE).
Furniture convention: Z-up, footprint centred on origin, z=0 is the floor, front faces -Y.
"""
import json, os, sys, math, urllib.request

# ----------------------------------------------------------------- CONFIG (Scripting tab)
CATALOG_URL = "https://iandamai720-cmyk.github.io/interior-models/catalog.json"
RUN_ID = None                 # e.g. "ikea-00263850" or "apartment-scandi-furnished"
RUN_FILTER = None             # e.g. dict(type="furniture", category="sofa", style="scandi")
RUN_LIMIT = 10                # max assets imported by RUN_FILTER (laid out in a row)
RUN_FORMAT = "glb"            # layouts only: "glb" (import) or "blend" (append all collections)
# -----------------------------------------------------------------------------------------

CACHE = os.environ.get("INTERIOR_MODELS_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "interior-models"))
_catalog = None

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "interior-models-blender/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

def catalog(refresh=False):
    """Fetch (and cache) catalog.json. Falls back to the cached copy when offline."""
    global _catalog
    if _catalog is not None and not refresh:
        return _catalog
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "catalog.json")
    try:
        data = _get(CATALOG_URL)
        open(path, "wb").write(data)
    except Exception as e:
        if not os.path.exists(path):
            raise
        print("[interior-models] offline, using cached catalog:", e)
        data = open(path, "rb").read()
    _catalog = json.loads(data)
    return _catalog

def _match(a, type=None, style=None, category=None, room=None, colour=None, tag=None,
           min_area=None, max_area=None, furnished=None, text=None, store=None, min_price=None, max_price=None, own_model=None, shard=None):
    if type and a["type"] != type: return False
    if store and (a.get("store") or "").lower() != store.lower(): return False
    if shard and a.get("shard") != shard: return False
    if own_model is not None and a["type"] != "layout" and bool(a.get("has_own_model", True)) != own_model: return False
    if min_price is not None and (a.get("price_pln") is None or a["price_pln"] < min_price): return False
    if max_price is not None and (a.get("price_pln") is None or a["price_pln"] > max_price): return False
    if style and a.get("style") != style: return False
    if category and a.get("category") != category: return False
    if room and a.get("room") != room: return False
    if colour and colour.lower() not in [c.lower() for c in a.get("colours", []) if c]: return False
    if tag and tag not in a.get("tags", []): return False
    if furnished is not None and a["type"] == "layout" and a.get("furnished") != furnished: return False
    if min_area is not None and (a.get("area_m2") or 0) < min_area: return False
    if max_area is not None and (a.get("area_m2") or 1e9) > max_area: return False
    if text and text.lower() not in (a.get("name", "") + " " + a.get("full_name", "")).lower(): return False
    return True

def list_assets(**flt):
    """Filters: type, style, category, room, colour, tag, min_area, max_area, furnished, text, store, min_price, max_price, own_model, shard."""
    res = [a for a in catalog()["assets"] if _match(a, **flt)]
    for a in res:
        extra = f"{a['area_m2']} m²" if a["type"] == "layout" else a.get("category", "")
        price = f"{a['price_pln']:.0f} zł" if a.get("price_pln") is not None else ""
        print(f"{a['id']:40s} {a['type']:13s} {a.get('style',''):10s} {extra:18s} {(a.get('store') or ''):16s} {price:>9s}  {a['name']}")
    return res

def get_asset(asset_id):
    for a in catalog()["assets"]:
        if a["id"] == asset_id or a.get("key") == asset_id or a.get("article_number") == asset_id:
            return a
    raise KeyError(f"asset {asset_id!r} not in catalog")

def download(asset_id, fmt="glb"):
    """Download an asset file into the cache (skipped if already cached with matching size)."""
    a = get_asset(asset_id)
    if a["type"] == "store_product":            # no own 3D model: fetch the similar model's file
        return download(a["similar_model_id"], fmt)
    url = a["urls"][fmt] if a["type"] == "layout" else a["url"]
    path = os.path.join(CACHE, a["type"], os.path.basename(url))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    expected = a.get("file_size_bytes") if a["type"] != "layout" else None
    if not os.path.exists(path) or (expected and os.path.getsize(path) != expected):
        print("[interior-models] downloading", url)
        tmp = path + ".part"
        open(tmp, "wb").write(_get(url))
        os.replace(tmp, path)
    return path

def import_asset(asset_id, location=(0, 0, 0), rotation_deg=0.0, fmt="glb", collection_name=None):
    """Download + import one asset. Returns the list of new top-level objects."""
    import bpy
    a = get_asset(asset_id)
    path = download(asset_id, fmt)
    before = set(bpy.data.objects)
    if fmt == "blend":
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.collections = [c for c in src.collections if not c.startswith("_")]
        coll = bpy.data.collections.new(collection_name or a["id"])
        bpy.context.scene.collection.children.link(coll)
        for c in dst.collections:
            coll.children.link(c)
    else:
        bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in new if o.parent is None or o.parent not in new]
    if fmt != "blend":
        coll = bpy.data.collections.get(collection_name or a["id"]) or bpy.data.collections.new(collection_name or a["id"])
        if coll.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(coll)
        for o in new:
            for c in list(o.users_collection): c.objects.unlink(o)
            coll.objects.link(o)
    # move/rotate via a parent empty so the asset's internal transforms stay intact
    root = bpy.data.objects.new(f"{a['id']}_root", None)
    coll.objects.link(root)
    for o in roots: o.parent = root
    root.location = location
    root.rotation_euler = (0, 0, math.radians(rotation_deg))
    root["catalog_id"] = a["id"]
    if a.get("article_number"): root["ikea_article"] = a["article_number"]
    for k in ("store", "price_pln", "url_pl", "similar_model_id"):
        if a.get(k) is not None: root[k] = a[k]
    print(f"[interior-models] imported {a['id']} ({a['name']}) from {path}")
    return [root]

def import_filtered(limit=10, spacing=0.5, fmt="glb", **flt):
    """Import every match (up to limit), laid out in a row along +X."""
    x = 0.0; out = []
    for a in [a for a in catalog()["assets"] if _match(a, **flt)][:limit]:
        w = (a.get("dimensions_m") or {}).get("x") or (a.get("footprint_m") or [2])[0]
        out += import_asset(a["id"], location=(x + w / 2, 0, 0), fmt=fmt)
        x += w + spacing
    return out

def _cli():
    import argparse, bpy
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv: return False
    p = argparse.ArgumentParser()
    p.add_argument("--id"); p.add_argument("--type"); p.add_argument("--style"); p.add_argument("--category")
    p.add_argument("--colour"); p.add_argument("--min-area", type=float); p.add_argument("--max-area", type=float)
    p.add_argument("--limit", type=int, default=10); p.add_argument("--format", default="glb"); p.add_argument("--list", action="store_true")
    p.add_argument("--store"); p.add_argument("--room"); p.add_argument("--min-price", type=float); p.add_argument("--max-price", type=float)
    p.add_argument("--save")
    a = p.parse_args(argv)
    flt = {k: v for k, v in dict(type=a.type, style=a.style, category=a.category, colour=a.colour, min_area=a.min_area, max_area=a.max_area, store=a.store, room=a.room, min_price=a.min_price, max_price=a.max_price).items() if v is not None}
    if a.list: list_assets(**flt)
    elif a.id: import_asset(a.id, fmt=a.format)
    elif flt: import_filtered(limit=a.limit, fmt=a.format, **flt)
    if a.save: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.save))
    return True

if __name__ == "__main__":
    if not _cli():
        if RUN_ID: import_asset(RUN_ID, fmt=RUN_FORMAT)
        elif RUN_FILTER: import_filtered(limit=RUN_LIMIT, fmt=RUN_FORMAT, **RUN_FILTER)
        else: list_assets()
