"""Turn catalog.json into a static GitHub Pages API (absolute URLs + index files)."""
import json, os, re, shutil
ROOT = "/workspace/interior-lib"
BASE = "https://iandamai720-cmyk.github.io/interior-models"
u = lambda p: f"{BASE}/{p}" if p else None
cat = json.load(open(f"{ROOT}/catalog.json"))
cat["base_url"] = BASE
cat["catalog_url"] = f"{BASE}/catalog.json"
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
for a in cat["assets"]:
    if a["type"] == "furniture":
        a["url"] = u(a["file"]); a["preview_url"] = u(a["preview"])
    else:
        a["urls"] = {k: u(v) for k, v in a["files"].items()}
        a["url"] = a["urls"]["glb"]; a["preview_url"] = u(a["preview"])
        a["preview_urls"] = {k: u(v) for k, v in a["previews"].items()}
    a["api_url"] = f"{BASE}/api/{'layouts' if a['type']=='layout' else 'furniture'}/{a['id']}.json"
json.dump(cat, open(f"{ROOT}/catalog.json", "w"), indent=1, ensure_ascii=False)

shutil.rmtree(f"{ROOT}/api", ignore_errors=True)
def w(path, obj):
    p = f"{ROOT}/api/{path}"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=1, ensure_ascii=False)
def summary(a):
    keys = ["id", "type", "name", "style", "colours", "tags", "url", "preview_url", "api_url", "file_size_bytes"]
    keys += ["layout", "furnished", "area_m2", "room_count", "bedrooms"] if a["type"] == "layout" else ["category", "room", "article_number", "dimensions_m"]
    return {k: a[k] for k in keys}
L = [a for a in cat["assets"] if a["type"] == "layout"]; F = [a for a in cat["assets"] if a["type"] == "furniture"]
w("layouts.json", [summary(a) for a in L]); w("furniture.json", [summary(a) for a in F])
for a in L: w(f"layouts/{a['id']}.json", a)
for a in F: w(f"furniture/{a['id']}.json", a)
cats = sorted({a["category"] for a in F}); styles = sorted({a["style"] for a in cat["assets"]})
cols = sorted({slug(c) for a in cat["assets"] for c in a["colours"] if c})
rooms = sorted({a["room"] for a in F})
for c in cats: w(f"furniture/category/{c}.json", [summary(a) for a in F if a["category"] == c])
for r in rooms: w(f"furniture/room/{r}.json", [summary(a) for a in F if a["room"] == r])
for s in styles: w(f"styles/{s}.json", [summary(a) for a in cat["assets"] if a["style"] == s])
for c in cols: w(f"colours/{c}.json", [summary(a) for a in cat["assets"] if c in {slug(x) for x in a["colours"] if x}])
idx = dict(base_url=BASE, catalog=f"{BASE}/catalog.json", layouts=f"{BASE}/api/layouts.json", furniture=f"{BASE}/api/furniture.json",
    layout_detail=f"{BASE}/api/layouts/{{id}}.json", furniture_detail=f"{BASE}/api/furniture/{{id}}.json",
    furniture_by_category={c: f"{BASE}/api/furniture/category/{c}.json" for c in cats},
    furniture_by_room={r: f"{BASE}/api/furniture/room/{r}.json" for r in rooms},
    by_style={s: f"{BASE}/api/styles/{s}.json" for s in styles},
    by_colour={c: f"{BASE}/api/colours/{c}.json" for c in cols},
    sqlite=f"{BASE}/catalog.db", blender_helper=f"{BASE}/blender/import_from_catalog.py",
    counts={"layouts": len(L), "furniture": len(F)})
w("index.json", idx)
# keep this alias for the requested path api/furniture/<category>.json
for c in cats: w(f"furniture/{c}.json", [summary(a) for a in F if a["category"] == c])
print(json.dumps(idx["counts"]), cats, styles, cols, rooms)
import sqlite3
con = sqlite3.connect(f"{ROOT}/catalog.db")
cols_ = [r[1] for r in con.execute("PRAGMA table_info(assets)")]
for c in ("url", "preview_url", "api_url"):
    if c not in cols_: con.execute(f"ALTER TABLE assets ADD COLUMN {c} TEXT")
for a in cat["assets"]:
    con.execute("UPDATE assets SET url=?, preview_url=?, api_url=?, json=? WHERE id=?", (a["url"], a["preview_url"], a["api_url"], json.dumps(a, ensure_ascii=False), a["id"]))
con.commit(); con.execute("VACUUM"); con.close()
