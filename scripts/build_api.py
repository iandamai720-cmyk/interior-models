"""Turn catalog.json into a static GitHub Pages API (absolute URLs + index files)."""
import json, os, re, shutil
ROOT = "/workspace/interior-lib"
BASE = "https://iandamai720-cmyk.github.io/interior-models"
u = lambda p: f"{BASE}/{p}" if p else None
cat = json.load(open(f"{ROOT}/catalog.json"))
cat["base_url"] = BASE
cat["catalog_url"] = f"{BASE}/catalog.json"
PLURAL = {"layout": "layouts", "furniture": "furniture", "appliance": "appliances", "fixture": "fixtures"}
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
for a in cat["assets"]:
    if a["type"] != "layout":
        a["url"] = u(a["file"]); a["preview_url"] = u(a["preview"])
    else:
        a["urls"] = {k: u(v) for k, v in a["files"].items()}
        a["url"] = a["urls"]["glb"]; a["preview_url"] = u(a["preview"])
        a["preview_urls"] = {k: u(v) for k, v in a["previews"].items()}
    a["api_url"] = f"{BASE}/api/{PLURAL[a['type']]}/{a['id']}.json"
json.dump(cat, open(f"{ROOT}/catalog.json", "w"), indent=1, ensure_ascii=False)

shutil.rmtree(f"{ROOT}/api", ignore_errors=True)
def w(path, obj):
    p = f"{ROOT}/api/{path}"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=1, ensure_ascii=False)
def summary(a):
    keys = ["id", "type", "name", "style", "colours", "tags", "url", "preview_url", "api_url", "file_size_bytes"]
    keys += ["layout", "furnished", "area_m2", "room_count", "bedrooms"] if a["type"] == "layout" else ["category", "room", "article_number", "dimensions_m", "source", "author", "license"]
    return {k: a.get(k) for k in keys}
L = [a for a in cat["assets"] if a["type"] == "layout"]; F = [a for a in cat["assets"] if a["type"] == "furniture"]
OBJ = [a for a in cat["assets"] if a["type"] != "layout"]          # every placeable model
w("layouts.json", [summary(a) for a in L]); w("assets.json", [summary(a) for a in cat["assets"]])
for a in L: w(f"layouts/{a['id']}.json", a)
groups = {}
for t in ("furniture", "appliance", "fixture"):
    G = [a for a in OBJ if a["type"] == t]; pl = PLURAL[t]; groups[pl] = G
    w(f"{pl}.json", [summary(a) for a in G])
    for a in G: w(f"{pl}/{a['id']}.json", a)
    for c in sorted({a["category"] for a in G}):
        w(f"{pl}/category/{c}.json", [summary(a) for a in G if a["category"] == c])
        w(f"{pl}/{c}.json", [summary(a) for a in G if a["category"] == c])     # short alias api/<type>/<category>.json
    for r in sorted({a["room"] for a in G}): w(f"{pl}/room/{r}.json", [summary(a) for a in G if a["room"] == r])
cats = sorted({a["category"] for a in OBJ}); rooms = sorted({a["room"] for a in OBJ}); styles = sorted({a["style"] for a in cat["assets"]})
cols = sorted({slug(c) for a in cat["assets"] for c in a["colours"] if c})
lics = sorted({a["license"] for a in OBJ}); srcs = sorted({a["source"] for a in OBJ})
for c in cats: w(f"category/{c}.json", [summary(a) for a in OBJ if a["category"] == c])
for r in rooms: w(f"room/{r}.json", [summary(a) for a in OBJ if a["room"] == r])
for s_ in styles: w(f"styles/{s_}.json", [summary(a) for a in cat["assets"] if a["style"] == s_])
for c in cols: w(f"colours/{c}.json", [summary(a) for a in cat["assets"] if c in {slug(x) for x in a["colours"] if x}])
for l in lics: w(f"licenses/{slug(l)}.json", [summary(a) for a in OBJ if a["license"] == l])
for s_ in srcs: w(f"sources/{slug(s_)}.json", [summary(a) for a in OBJ if a["source"] == s_])
w("credits.json", [{k: a.get(k) for k in ("id", "name", "source_title", "source", "source_url", "author", "license", "license_note")} for a in OBJ if a["source"] != "IKEA"])
idx = dict(base_url=BASE, catalog=f"{BASE}/catalog.json", assets=f"{BASE}/api/assets.json", layouts=f"{BASE}/api/layouts.json",
    furniture=f"{BASE}/api/furniture.json", appliances=f"{BASE}/api/appliances.json", fixtures=f"{BASE}/api/fixtures.json",
    credits=f"{BASE}/api/credits.json",
    layout_detail=f"{BASE}/api/layouts/{{id}}.json", furniture_detail=f"{BASE}/api/furniture/{{id}}.json",
    appliance_detail=f"{BASE}/api/appliances/{{id}}.json", fixture_detail=f"{BASE}/api/fixtures/{{id}}.json",
    furniture_by_category={c: f"{BASE}/api/furniture/category/{c}.json" for c in sorted({a["category"] for a in groups["furniture"]})},
    furniture_by_room={r: f"{BASE}/api/furniture/room/{r}.json" for r in sorted({a["room"] for a in groups["furniture"]})},
    appliances_by_category={c: f"{BASE}/api/appliances/category/{c}.json" for c in sorted({a["category"] for a in groups["appliances"]})},
    appliances_by_room={r: f"{BASE}/api/appliances/room/{r}.json" for r in sorted({a["room"] for a in groups["appliances"]})},
    fixtures_by_category={c: f"{BASE}/api/fixtures/category/{c}.json" for c in sorted({a["category"] for a in groups["fixtures"]})},
    by_category={c: f"{BASE}/api/category/{c}.json" for c in cats}, by_room={r: f"{BASE}/api/room/{r}.json" for r in rooms},
    by_style={s_: f"{BASE}/api/styles/{s_}.json" for s_ in styles},
    by_colour={c: f"{BASE}/api/colours/{c}.json" for c in cols},
    by_license={l: f"{BASE}/api/licenses/{slug(l)}.json" for l in lics}, by_source={s_: f"{BASE}/api/sources/{slug(s_)}.json" for s_ in srcs},
    sqlite=f"{BASE}/catalog.db", blender_helper=f"{BASE}/blender/import_from_catalog.py",
    counts={"layouts": len(L), **{k: len(v) for k, v in groups.items()}, "total": len(cat["assets"])})
w("index.json", idx)
print(json.dumps(idx["counts"]), cats, styles, lics, srcs)
import sqlite3
con = sqlite3.connect(f"{ROOT}/catalog.db")
cols_ = [r[1] for r in con.execute("PRAGMA table_info(assets)")]
for c in ("url", "preview_url", "api_url"):
    if c not in cols_: con.execute(f"ALTER TABLE assets ADD COLUMN {c} TEXT")
for a in cat["assets"]:
    con.execute("UPDATE assets SET url=?, preview_url=?, api_url=?, json=? WHERE id=?", (a["url"], a["preview_url"], a["api_url"], json.dumps(a, ensure_ascii=False), a["id"]))
con.commit(); con.execute("VACUUM"); con.close()
