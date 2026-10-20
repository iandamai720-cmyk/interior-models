"""Import interior-models assets into Blender straight from the GitHub Pages catalog.

Use from Blender's Scripting tab: open this file, edit the CONFIG block below, press Run Script.
Or from the Python console / another script:
    exec(open("/path/import_from_catalog.py").read())   # or: import import_from_catalog as ic
    ic.list_assets(type="furniture", category="sofa")
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
           min_area=None, max_area=None, furnished=None, text=None):
    if type and a["type"] != type: return False
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
    """Return assets matching filters: type, style, category, room, colour, tag, min_area, max_area, furnished, text."""
    res = [a for a in catalog()["assets"] if _match(a, **flt)]
    for a in res:
        extra = f"{a['area_m2']} m²" if a["type"] == "layout" else a.get("category", "")
        print(f"{a['id']:32s} {a['type']:9s} {a.get('style',''):16s} {extra:16s} {a['name']}")
    return res

def get_asset(asset_id):
    for a in catalog()["assets"]:
        if a["id"] == asset_id or a.get("key") == asset_id or a.get("article_number") == asset_id:
            return a
    raise KeyError(f"asset {asset_id!r} not in catalog")

def download(asset_id, fmt="glb"):
    """Download an asset file into the cache (skipped if already cached with matching size)."""
    a = get_asset(asset_id)
    url = a["urls"][fmt] if a["type"] == "layout" else a["url"]
    path = os.path.join(CACHE, a["type"], os.path.basename(url))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    expected = a.get("file_size_bytes") if a["type"] == "furniture" else None
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
    p.add_argument("--save")
    a = p.parse_args(argv)
    flt = {k: v for k, v in dict(type=a.type, style=a.style, category=a.category, colour=a.colour, min_area=a.min_area, max_area=a.max_area).items() if v is not None}
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
