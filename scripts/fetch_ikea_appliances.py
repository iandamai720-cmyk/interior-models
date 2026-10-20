"""IKEA appliances/fixtures via the same PIP JSON-LD 3DModel method as fetch_ikea.py."""
import json, os, re, time, sys
src = open(os.path.join(os.path.dirname(__file__), "fetch_ikea.py")).read().split("def main")[0]
exec(src)
OUT = f"{ROOT}/appliances"
T = [
 ("ikea_oven", "built-in oven", r"oven", "oven", "kitchen", "modern"),
 ("ikea_oven2", "oven stainless steel", r"oven", "oven", "kitchen", "dark-industrial"),
 ("ikea_hob", "induction hob", r"induction-hob", "hob", "kitchen", "modern"),
 ("ikea_microwave", "microwave oven", r"microwave", "microwave", "kitchen", "modern"),
 ("ikea_dishwasher", "integrated dishwasher", r"dishwasher", "dishwasher", "kitchen", "modern"),
 ("ikea_hood_wall", "wall mounted extractor hood", r"extractor-hood", "extractor_hood", "kitchen", "modern"),
 ("ikea_hood2", "extractor hood", r"extractor-hood", "extractor_hood", "kitchen", "dark-industrial"),
 ("ikea_fridge_int", "integrated fridge freezer", r"fridge", "fridge", "kitchen", "modern"),
 ("ikea_freezer", "freezer", r"(freezer|fridge)", "fridge", "kitchen", "modern"),
 ("ikea_sink", "inset sink 1 bowl", r"sink", "kitchen_sink", "kitchen", "modern"),
 ("ikea_tap", "kitchen mixer tap", r"kitchen-mixer-tap", "kitchen_tap", "kitchen", "modern"),
 ("ikea_basin", "countertop wash-basin", r"wash-basin", "bathroom_sink", "bathroom", "scandi"),
 ("ikea_bath_tap", "wash-basin mixer tap", r"wash-basin-mixer-tap|basin-mixer", "bathroom_tap", "bathroom", "modern"),
 ("ikea_shower", "shower set with thermostatic mixer", r"shower", "shower", "bathroom", "modern"),
 ("ikea_speaker_shelf", "symfonisk bookshelf speaker", r"symfonisk", "speaker", "living", "scandi"),
 ("ikea_speaker_lamp", "symfonisk speaker lamp", r"symfonisk.*lamp", "speaker", "living", "scandi"),
 ("ikea_speaker_frame", "symfonisk picture frame speaker", r"symfonisk-picture-frame", "speaker", "living", "scandi"),
 ("ikea_vappeby", "vappeby bluetooth speaker", r"vappeby", "speaker", "living", "scandi"),
 ("ikea_desk_lamp", "forsa work lamp", r"(forsa|work-lamp)", "desk_lamp", "office", "dark-industrial"),
 ("ikea_desk_lamp2", "led work lamp", r"work-lamp|desk-lamp", "desk_lamp", "office", "scandi"),
 ("ikea_air_purifier", "starkvind air purifier", r"starkvind|air-purifier", "air_purifier", "living", "scandi"),
 ("ikea_fan", "fan", r"-fan-", "fan", "bedroom", "scandi"),
 ("ikea_ceiling_lamp", "ceiling lamp", r"ceiling-lamp|pendant", "lamp", "living", "scandi"),
 ("ikea_kettle", "kettle", r"kettle", "kettle", "kitchen", "scandi"),
 ("ikea_coffee", "coffee maker", r"coffee", "coffee_machine", "kitchen", "scandi"),
 ("ikea_tv_bench_wall", "wall-mounted tv bench", r"tv-bench|media", "tv_bench", "living", "scandi"),
 ("ikea_charger", "wireless charger", r"charger", "electronics", "office", "scandi"),
]
cat = []
used = set()
for key, q, rx, category, room, style in T:
    try: prods = search(q)
    except Exception as e: print("SEARCH FAIL", key, e); continue
    got = None
    for p in prods:
        url = p.get("pipUrl", "")
        if not re.search(rx, url) or p["itemNo"] in used: continue
        try: html = get(url)
        except Exception: continue
        L = ld(html)
        if "3DModel" not in L: continue
        glb = pick_glb(L["3DModel"])
        if glb: got = (p, L, glb, url); break
    if not got: print("NO 3D", key); continue
    p, L, glb, url = got; used.add(p["itemNo"]); pr = L.get("Product", {})
    fn = f"{OUT}/{key}_{p['itemNo']}.glb"
    if not os.path.exists(fn): open(fn, "wb").write(get(glb, binary=True))
    cat.append(dict(key=key, name=f"{p['name']} {p.get('typeName','')}".strip(), full_name=pr.get("name"), article_number=p["itemNo"],
        category=category, room=room, style=style, colour=pr.get("color") or ", ".join(c.get("name","") for c in p.get("colors", [])),
        colours=[c.get("name") for c in p.get("colors", [])], material=pr.get("material"), dims_text=p.get("itemMeasureReferenceText"),
        width=pr.get("width"), depth=pr.get("depth"), height=pr.get("height"), file=os.path.relpath(fn, ROOT), source="IKEA", source_url=url,
        glb_url=glb.split("?")[0], author="IKEA", license="IKEA product model – personal/demo use only (© Inter IKEA Systems B.V.)"))
    print("OK", key, pr.get("name"), os.path.getsize(fn)); time.sleep(0.4)
json.dump(cat, open(f"{ROOT}/tmp/appl_ikea.json", "w"), indent=1)
