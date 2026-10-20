"""Replicates the userscript's goal without a browser: IKEA product pages (PIP) embed a
schema.org 3DModel JSON-LD block whose encoding[].contentUrl lists the same
web-api.ikea.com/dimma/assets/... .glb / glb_draco URLs the <model-viewer> loads."""
import json, re, os, sys, time, urllib.request, urllib.parse
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
CC = "gb/en"
ROOT = "/workspace/interior-lib"
OUT = f"{ROOT}/furniture"

# key, query, url-regex filter, category, room, style
TARGETS = [
 ("sofa_kivik", "kivik 3-seat sofa", r"kivik-3-seat-sofa-[a-z-]+-s?\d+/$", "sofa", "living", "scandi"),
 ("sofa_dark", "landskrona 3-seat sofa", r"landskrona-3-seat-sofa", "sofa", "living", "dark-industrial"),
 ("armchair_poang", "poang armchair", r"poang-armchair-", "armchair", "living", "wood-natural"),
 ("armchair_strandmon", "strandmon wing chair", r"strandmon-wing-chair", "armchair", "living", "classic"),
 ("coffee_table_lack", "lack coffee table", r"lack-coffee-table-(white|black)", "coffee_table", "living", "scandi"),
 ("coffee_table_listerby", "listerby coffee table", r"listerby-coffee-table", "coffee_table", "living", "wood-natural"),
 ("tv_bench_besta", "besta tv bench", r"besta-tv-bench", "tv_bench", "living", "scandi"),
 ("tv_bench_lack", "lack tv bench", r"lack-tv-bench", "tv_bench", "living", "dark-industrial"),
 ("bookcase_billy", "billy bookcase", r"billy-bookcase-white-\d+/$", "bookshelf", "living", "scandi"),
 ("shelf_kallax", "kallax shelving unit", r"kallax-shelving-unit-", "bookshelf", "living", "scandi"),
 ("floor_lamp_hektar", "hektar floor lamp", r"hektar-floor-lamp", "lamp", "living", "dark-industrial"),
 ("floor_lamp_hoglunda", "floor lamp", r"floor-lamp", "lamp", "living", "scandi"),
 ("table_lamp", "table lamp", r"table-lamp", "lamp", "bedroom", "scandi"),
 ("pendant_lamp", "pendant lamp", r"pendant-lamp", "lamp", "dining", "scandi"),
 ("rug_large", "rug low pile", r"rug-", "rug", "living", "scandi"),
 ("rug_dark", "rug dark grey", r"rug-.*(dark|anthracite|black)", "rug", "bedroom", "dark-industrial"),
 ("dining_table_ekedalen", "ekedalen extendable table", r"ekedalen-extendable-table", "dining_table", "dining", "wood-natural"),
 ("dining_table_lisabo", "lisabo table", r"lisabo-table", "dining_table", "dining", "scandi"),
 ("dining_chair_lisabo", "lisabo chair", r"lisabo-chair", "dining_chair", "dining", "wood-natural"),
 ("dining_chair_teodores", "teodores chair", r"teodores-chair", "dining_chair", "dining", "scandi"),
 ("bed_malm", "malm bed frame high", r"malm-bed-frame-high.*(160x200|white|oak)", "bed_double", "bedroom", "scandi"),
 ("bed_hemnes", "hemnes bed frame", r"hemnes-bed-frame.*160x200", "bed_double", "bedroom", "wood-natural"),
 ("bed_single", "malm bed frame 90x200", r"(malm|neiden|sniglar|tarva).*bed-frame.*90x200", "bed_single", "bedroom", "scandi"),
 ("wardrobe_pax", "pax wardrobe", r"pax-wardrobe", "wardrobe", "bedroom", "scandi"),
 ("wardrobe_kleppstad", "kleppstad wardrobe", r"kleppstad-wardrobe", "wardrobe", "bedroom", "scandi"),
 ("nightstand_malm", "malm chest of 2 drawers", r"malm-chest-of-2-drawers", "nightstand", "bedroom", "scandi"),
 ("nightstand_hemnes", "hemnes bedside table", r"hemnes-bedside-table", "nightstand", "bedroom", "wood-natural"),
 ("desk_micke", "micke desk", r"micke-desk", "desk", "office", "scandi"),
 ("desk_dark", "lagkapten alex desk", r"desk", "desk", "office", "dark-industrial"),
 ("office_chair_markus", "markus office chair", r"markus-office-chair", "office_chair", "office", "dark-industrial"),
 ("office_chair_light", "millberget swivel chair", r"(swivel|office)-chair", "office_chair", "office", "scandi"),
 ("kitchen_knoxhult", "knoxhult kitchen", r"knoxhult-kitchen", "kitchen", "kitchen", "scandi"),
 ("kitchen_island", "kitchen island", r"(island|kitchen-trolley|kitchen-cart)", "kitchen", "kitchen", "wood-natural"),
 ("kitchen_sunnersta", "sunnersta mini-kitchen", r"sunnersta", "kitchen", "kitchen", "scandi"),
 ("fridge", "fridge freezer", r"fridge", "appliance", "kitchen", "scandi"),
 ("wash_stand", "wash-stand with drawers", r"wash-stand", "bathroom_vanity", "bathroom", "scandi"),
 ("bathroom_mirror_cabinet", "mirror cabinet", r"mirror-cabinet", "bathroom_cabinet", "bathroom", "scandi"),
 ("bathroom_shelf", "bathroom shelving unit", r"(shelving-unit|high-cabinet|towel)", "bathroom_storage", "bathroom", "scandi"),
 ("hall_shoe_cabinet", "hemnes shoe cabinet", r"shoe-cabinet", "hallway_storage", "hallway", "scandi"),
 ("hall_coat_rack", "coat rack", r"(coat-rack|hat-and-coat|clothes-rack)", "hallway_storage", "hallway", "scandi"),
 ("plant_pot", "artificial potted plant", r"artificial-potted-plant", "decor", "living", "scandi"),
]


EXTRA = [
 ("bed_single", "single bed", r"(neiden-bed-frame-pine-luroey-s79248611|vihals-bed-frame-white-30602429|gullaberg-bed-frame-white-80608103|tarva-bed-frame)", "bed_single", "bedroom", "scandi"),
 ("bed_single2", "sniglar bed", r"sniglar-bed-frame", "bed_single", "bedroom", "wood-natural"),
]

def get(url, binary=False, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    raise err

def search(q, n=24):
    u = f"https://sik.search.blue.cdtapps.com/{CC}/search-result-page?" + urllib.parse.urlencode({"q": q, "size": n, "types": "PRODUCT"})
    d = json.loads(get(u))
    return [it["product"] for it in d["searchResultPage"]["products"]["main"]["items"] if "product" in it]

def ld(html):
    out = {}
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try: d = json.loads(m.group(1))
        except Exception: continue
        for x in (d if isinstance(d, list) else [d]):
            if isinstance(x, dict) and x.get("@type"): out[x["@type"]] = x
    return out

def pick_glb(model):
    urls = [e["contentUrl"] for e in model.get("encoding", []) if e.get("encodingFormat") == "model/gltf-binary"]
    for pat in ["/rqp3/glb/", "/rqp2/glb/", "/rqp1/glb/", "/glb/", "glb_draco"]:
        for u in urls:
            if pat in u and "geomagical" not in u: return u
    return urls[0] if urls else None

def main():
    cat = json.load(open(f'{ROOT}/tmp/fetched.json')) if len(sys.argv)>1 else []
    cat = [c for c in cat if 'error' not in c]
    targets = EXTRA if len(sys.argv)>1 else TARGETS
    done = set(json.load(open(f"{ROOT}/tmp/fetched.json"))["keys"]) if False else set()
    used_items = {c['article_number'] for c in cat}
    for key, q, rx, category, room, style in targets:
        try:
            prods = search(q)
        except Exception as e:
            print("SEARCH FAIL", key, e); cat.append({"key": key, "error": f"search: {e}"}); continue
        got = None
        for p in prods:
            url = p.get("pipUrl", "")
            if not re.search(rx, url) or p["itemNo"] in used_items: continue
            try: html = get(url)
            except Exception as e: print("  pip fail", url, e); continue
            L = ld(html)
            if "3DModel" not in L: continue
            glb = pick_glb(L["3DModel"])
            if not glb: continue
            got = (p, L, glb, url); break
        if not got:
            print("NO 3D", key); cat.append({"key": key, "error": "no product with 3D model found", "query": q}); continue
        p, L, glb, url = got
        used_items.add(p["itemNo"])
        pr = L.get("Product", {})
        fn = f"{OUT}/{key}_{p['itemNo']}.glb"
        if not os.path.exists(fn):
            data = get(glb, binary=True)
            open(fn, "wb").write(data)
        rec = dict(key=key, name=f"{p['name']} {p.get('typeName','')}".strip(), full_name=pr.get("name"),
                   article_number=p["itemNo"], article_number_dotted=pr.get("mpn"),
                   category=category, room=room, style=style,
                   colour=pr.get("color") or ", ".join(c.get("name","") for c in p.get("colors", [])),
                   colours=[c.get("name") for c in p.get("colors", [])],
                   material=pr.get("material"),
                   dims_text=p.get("itemMeasureReferenceText"),
                   width=pr.get("width"), depth=pr.get("depth"), height=pr.get("height"),
                   file=os.path.relpath(fn, ROOT), size_bytes=os.path.getsize(fn),
                   source_url=url, glb_url=glb.split("?")[0], image=p.get("mainImageUrl"))
        cat.append(rec)
        print("OK", key, rec["full_name"], rec["size_bytes"])
        time.sleep(0.5)
    json.dump(cat, open(f"{ROOT}/tmp/fetched.json", "w"), indent=1)

main()
