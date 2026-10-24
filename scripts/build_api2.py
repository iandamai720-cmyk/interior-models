"""Static JSON API from catalog.json (v2: shards, stores, store products). Writes api/ and refreshes catalog.db."""
import json, os, re, shutil, sqlite3, collections
ROOT = "/workspace/interior-lib"
cat = json.load(open(f"{ROOT}/catalog.json")); BASE = cat["base_url"]; A = cat["assets"]
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower().translate(str.maketrans("ąćęłńóśźżäöåü", "acelnoszzaoau"))).strip("-")
PLURAL = {"material": "materials", "layout": "layouts", "furniture": "furniture", "appliance": "appliances", "fixture": "fixtures", "store_product": "store-products"}
shutil.rmtree(f"{ROOT}/api", ignore_errors=True)
def w(path, obj):
    p = f"{ROOT}/api/{path}"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=1, ensure_ascii=False)
    return f"{BASE}/api/{path}"
def summary(a):
    k = ["id", "type", "name", "style", "colours", "tags", "url", "preview_url", "api_url", "file_size_bytes", "shard"]
    if a["type"] == "material": return {x: a.get(x) for x in k + ["category", "room", "resolution", "tile_m", "maps", "folder_url", "source", "source_url", "author", "license"]}
    k += ["layout", "furnished", "area_m2", "storeys", "room_count", "bedrooms"] if a["type"] == "layout" else \
         ["category", "room", "store", "price_pln", "url_pl", "url_uk", "has_own_model", "similar_model_id", "model_url", "article_number", "dimensions_m", "dimensions_cm", "source", "author", "license",
          "opis", "product_image_url", "country", "price", "currency", "product_url", "similar_label", "similar_model_name", "similar_model_url", "similar_preview_url", "source_title"]
    return {x: a.get(x) for x in k}
idx = dict(base_url=BASE, catalog=f"{BASE}/catalog.json", shards=cat["shards"], sqlite=f"{BASE}/catalog.db", blender_helper=f"{BASE}/blender/import_from_catalog.py", blender_material_helper=f"{BASE}/blender/load_material.py",
           spreadsheet_xlsx=f"{BASE}/sklepy.xlsx", spreadsheet_csv=f"{BASE}/assets.csv", google_sheet="https://docs.google.com/spreadsheets/d/1RidjlvMwOK9CLWBZbDtJHo1KykQIPCrOkTC6fg1vdEs/edit")
idx["assets"] = w("assets.json", [summary(a) for a in A])
idx["models"] = w("models.json", [summary(a) for a in A if a["type"] not in ("layout", "store_product", "material")])
for t, pl in PLURAL.items():
    G = [a for a in A if a["type"] == t]; idx[pl.replace("-", "_")] = w(f"{pl}.json", [summary(a) for a in G])
    idx[f"{t}_detail"] = f"{BASE}/api/{pl}/{{id}}.json"
    for a in G: w(f"{pl}/{a['id']}.json", a)
    if t == "layout": continue
    for c in sorted({a["category"] for a in G}):
        w(f"{pl}/category/{c}.json", [summary(a) for a in G if a["category"] == c]); w(f"{pl}/{c}.json", [summary(a) for a in G if a["category"] == c])
    for r in sorted({a["room"] for a in G}): w(f"{pl}/room/{r}.json", [summary(a) for a in G if a["room"] == r])
O = [a for a in A if a["type"] not in ("layout",)]
def group(name, keyf, pool):
    g = collections.defaultdict(list)
    for a in pool:
        for k in keyf(a):
            if k: g[k].append(summary(a))
    idx[f"by_{name}"] = {k: w(f"{name}/{slug(k)}.json", v) for k, v in sorted(g.items())}
    return g
group("category", lambda a: [a["category"]], O)
group("room", lambda a: [a["room"]], O)
group("styles", lambda a: [a["style"]], A)
group("colours", lambda a: a.get("colours") or [], A)
group("licenses", lambda a: [a.get("license")], O)
group("sources", lambda a: [a.get("source")], O)
st = group("store", lambda a: [a.get("store")], O)
group("country", lambda a: [a.get("country")], O)
group("shard", lambda a: [a.get("shard")], A)
# store x category
for s_, items in st.items():
    for c in sorted({x["category"] for x in items}): w(f"store/{slug(s_)}/{c}.json", [x for x in items if x["category"] == c])
# colour-variant groups (IKEA)
vg = collections.defaultdict(list)
for a in A:
    if a.get("variant_group"): vg[a["variant_group"]].append(summary(a))
vg = {k: v for k, v in vg.items() if len(v) > 1}
idx["variants"] = w("variants.json", {k: [x["id"] for x in v] for k, v in sorted(vg.items())})
idx["stores_summary"] = w("stores.json", [{"store": s_, "products": len(v), "own_models": sum(x["has_own_model"] for x in v),
    "country": sorted({x["country"] for x in v if x.get("country")}), "with_price": sum((x.get("price") if x.get("price") is not None else x["price_pln"]) is not None for x in v), "url": f"{BASE}/api/store/{slug(s_)}.json"} for s_, v in sorted(st.items())])
idx["credits"] = w("credits.json", [{k: a.get(k) for k in ("id", "name", "source", "source_url", "author", "license", "license_note")} for a in O if a.get("source") not in ("IKEA",) and a["type"] != "store_product"])
idx["counts"] = {**{PLURAL[t]: sum(a["type"] == t for a in A) for t in PLURAL}, "models_with_files": len([a for a in O if a["has_own_model"]]), "total": len(A)}
w("index.json", idx); print(json.dumps(idx["counts"]), len(idx["by_store"]), len(idx["by_category"]))
# sqlite
db = f"{ROOT}/catalog.db"
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db)
con.executescript("""CREATE TABLE assets(id TEXT PRIMARY KEY, type TEXT, name TEXT, category TEXT, room TEXT, style TEXT, store TEXT, price_pln REAL,
 url_pl TEXT, url_uk TEXT, has_own_model INTEGER, similar_model_id TEXT, shard TEXT, url TEXT, model_url TEXT, preview_url TEXT, api_url TEXT,
 source TEXT, author TEXT, license TEXT, file_size_bytes INTEGER, area_m2 REAL, tags TEXT, json TEXT, country TEXT, price REAL, currency TEXT);
CREATE TABLE tags(asset_id TEXT, tag TEXT); CREATE INDEX tags_tag ON tags(tag);
CREATE TABLE rooms(layout_id TEXT, name TEXT, type TEXT, floor INTEGER, area_m2 REAL, x0 REAL, y0 REAL, x1 REAL, y1 REAL);
CREATE TABLE layout_furniture(layout_id TEXT, asset_id TEXT, count INTEGER);
CREATE VIEW store_products AS SELECT * FROM assets WHERE type='store_product';
CREATE VIEW layouts AS SELECT * FROM assets WHERE type='layout';""")
for a in A:
    con.execute("INSERT INTO assets VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (a["id"], a["type"], a["name"], a.get("category"), a.get("room"), a["style"], a.get("store"), a.get("price_pln"),
        a.get("url_pl"), a.get("url_uk"), int(a.get("has_own_model", True)), a.get("similar_model_id"), a.get("shard"), a.get("url"), a.get("model_url", a.get("url")), a.get("preview_url"), a["api_url"],
        a.get("source"), a.get("author"), a.get("license"), a.get("file_size_bytes"), a.get("area_m2"), ",".join(a["tags"]), json.dumps(a, ensure_ascii=False), a.get("country"), a.get("price"), a.get("currency")))
    con.executemany("INSERT INTO tags VALUES(?,?)", [(a["id"], t) for t in a["tags"]])
    if a["type"] == "layout":
        con.executemany("INSERT INTO rooms VALUES(?,?,?,?,?,?,?,?,?)", [(a["id"], r["name"], r["type"], r.get("floor", 0), r["area_m2"], *r["bounds"]) for r in a["rooms"]])
        con.executemany("INSERT INTO layout_furniture VALUES(?,?,?)", [(a["id"], u["id"], u["count"]) for u in a["furniture_used"]])
con.commit(); con.execute("VACUUM"); con.close()
