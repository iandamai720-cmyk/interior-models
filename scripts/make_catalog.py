import json, os, sqlite3, glob, datetime
ROOT = "/workspace/interior-lib"
fur = json.load(open(f"{ROOT}/tmp/fetched.json")); bb = json.load(open(f"{ROOT}/tmp/bbox.json"))
WALL_FIX = {"kitchen_wall_cabinet": lambda s: [s[0], s[2], s[1]]}
assets = []
for c in fur:
    s = bb[c["key"]]["size"]; s = WALL_FIX.get(c["key"], lambda s: s)(s)
    tags = sorted({c["category"], c["room"], c["style"], c["name"].split()[0].lower(), *[x.lower() for x in c["colours"] if x]} | ({"kids"} if "SNIGLAR" in c["name"] else set()))
    assets.append(dict(id=f"ikea-{c['article_number']}", key=c["key"], type="furniture", name=c["name"], full_name=c["full_name"],
        brand="IKEA", article_number=c["article_number"], article_number_dotted=c["article_number_dotted"],
        category=c["category"], room=c["room"], style=c["style"], colour=c["colour"], colours=c["colours"], material=c["material"],
        dimensions_listed={"width": c["width"], "depth": c["depth"], "height": c["height"], "text": c["dims_text"] or None},
        dimensions_m={"x": round(s[0], 3), "y": round(s[1], 3), "z": round(s[2], 3)},
        triangles=bb[c["key"]]["tris"], tags=tags, file=c["file"], file_size_bytes=os.path.getsize(f"{ROOT}/{c['file']}"),
        format="glb", preview=f"previews/furniture/{c['key']}.png", source_url=c["source_url"], glb_source_url=c["glb_url"], image_url=c["image"],
        orientation="Blender Z-up after glTF import; footprint centred on origin; floor z=0; front faces -Y, back +Y"))
by_key = {a["key"]: a for a in assets}
layouts = []
for j in sorted(glob.glob(f"{ROOT}/layouts/*.json")):
    L = json.load(open(j)); tag = os.path.basename(j)[:-5]
    used = sorted({p["key"] for p in L["placed"] if p["key"] in by_key})
    style = L["style"] if L["furnished"] else "neutral"
    cols = {"scandi": ["white", "light oak", "beige", "light grey"], "dark": ["anthracite", "dark walnut", "black", "brown leather"], "neutral": ["white", "light oak"]}[style]
    layouts.append(dict(id=tag.replace("_", "-"), type="layout", name=f"{L['layout'].title()} {L['total_area_m2']:.0f} m² – {'furnished, ' + L['style'] if L['furnished'] else 'empty shell'}",
        layout=L["layout"], furnished=L["furnished"], style=style, colours=cols,
        area_m2=L["total_area_m2"], footprint_m=L["footprint_m"], storeys=1, wall_height_m=2.7,
        rooms=L["rooms"], room_count=len(L["rooms"]),
        bedrooms=sum(r["type"] == "bedroom" for r in L["rooms"]),
        tags=sorted({L["layout"], style, "furnished" if L["furnished"] else "shell", "single-storey"}),
        files={"blend": f"layouts/{tag}.blend", "glb": f"layouts/{tag}.glb", "meta": f"layouts/{tag}.json"},
        file_size_bytes=os.path.getsize(f"{ROOT}/layouts/{tag}.glb") + os.path.getsize(f"{ROOT}/layouts/{tag}.blend"),
        preview=f"previews/{tag}_iso.png", previews={"top": f"previews/{tag}_top.png", "iso": f"previews/{tag}_iso.png"},
        furniture_used=[{"key": k, "id": by_key[k]["id"], "count": sum(p["key"] == k for p in L["placed"])} for k in used],
        placeholders=sorted({p["key"] for p in L["placed"] if p["key"].startswith("placeholder")})))
cat = dict(version=1, generated=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), units="metres",
           license_note="IKEA models: personal/demo use only.", assets=layouts + assets)
json.dump(cat, open(f"{ROOT}/catalog.json", "w"), indent=1, ensure_ascii=False)
db = f"{ROOT}/catalog.db"
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db)
con.executescript("""
CREATE TABLE assets(id TEXT PRIMARY KEY, type TEXT, name TEXT, style TEXT, colours TEXT, tags TEXT, preview TEXT,
  file TEXT, file_size_bytes INTEGER, area_m2 REAL, json TEXT);
CREATE TABLE furniture(id TEXT PRIMARY KEY REFERENCES assets(id), key TEXT, article_number TEXT, full_name TEXT, category TEXT, room TEXT,
  colour TEXT, material TEXT, width_m REAL, depth_m REAL, height_m REAL, dims_listed TEXT, source_url TEXT, glb_source_url TEXT);
CREATE TABLE layouts(id TEXT PRIMARY KEY REFERENCES assets(id), layout TEXT, furnished INTEGER, area_m2 REAL, room_count INTEGER, bedrooms INTEGER,
  blend_path TEXT, glb_path TEXT, preview_top TEXT, preview_iso TEXT);
CREATE TABLE rooms(layout_id TEXT REFERENCES layouts(id), name TEXT, type TEXT, area_m2 REAL, x0 REAL, y0 REAL, x1 REAL, y1 REAL);
CREATE TABLE layout_furniture(layout_id TEXT REFERENCES layouts(id), furniture_id TEXT REFERENCES furniture(id), count INTEGER);
CREATE TABLE tags(asset_id TEXT REFERENCES assets(id), tag TEXT);
CREATE INDEX tags_tag ON tags(tag);
""")
for a in cat["assets"]:
    f = a["files"]["glb"] if a["type"] == "layout" else a["file"]
    con.execute("INSERT INTO assets VALUES(?,?,?,?,?,?,?,?,?,?,?)", (a["id"], a["type"], a["name"], a["style"], ",".join(a["colours"]), ",".join(a["tags"]), a["preview"], f, a["file_size_bytes"], a.get("area_m2"), json.dumps(a, ensure_ascii=False)))
    con.executemany("INSERT INTO tags VALUES(?,?)", [(a["id"], t) for t in a["tags"]])
    if a["type"] == "furniture":
        d = a["dimensions_m"]
        con.execute("INSERT INTO furniture VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (a["id"], a["key"], a["article_number"], a["full_name"], a["category"], a["room"], a["colour"], a["material"], d["x"], d["y"], d["z"], json.dumps(a["dimensions_listed"]), a["source_url"], a["glb_source_url"]))
    else:
        con.execute("INSERT INTO layouts VALUES(?,?,?,?,?,?,?,?,?,?)", (a["id"], a["layout"], int(a["furnished"]), a["area_m2"], a["room_count"], a["bedrooms"], a["files"]["blend"], a["files"]["glb"], a["previews"]["top"], a["previews"]["iso"]))
        con.executemany("INSERT INTO rooms VALUES(?,?,?,?,?,?,?,?)", [(a["id"], r["name"], r["type"], r["area_m2"], *r["bounds"]) for r in a["rooms"]])
        con.executemany("INSERT INTO layout_furniture VALUES(?,?,?)", [(a["id"], u["id"], u["count"]) for u in a["furniture_used"]])
con.commit()
print(con.execute("select type,count(*) from assets group by type").fetchall())
print(con.execute("select id,area_m2,room_count,bedrooms from layouts").fetchall())
