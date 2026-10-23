"""Mass IKEA scrape from the Polish site (ikea.com/pl/pl): PLN price + PL link + UK link + GLB.
Same mechanism as fetch_ikea.py: PIP JSON-LD 3DModel encoding[].contentUrl."""
import json, os, re, sys, time, urllib.parse, threading
from concurrent.futures import ThreadPoolExecutor
src = open(os.path.join(os.path.dirname(__file__), "fetch_ikea.py")).read().split("def main")[0]
exec(src)
OUT = f"{ROOT}/staging/ikea"
# (query_pl, category, room, max_items)
Q = [
 ("sofa 3-osobowa","sofa","living",8),("sofa narożna","sofa_corner","living",5),("sofa 2-osobowa","sofa","living",5),("sofa rozkładana","sofa_bed","living",4),
 ("fotel","armchair","living",8),("podnóżek","footstool","living",4),("pufa","pouffe","living",4),
 ("stolik kawowy","coffee_table","living",8),("stolik boczny","side_table","living",6),("szafka pod tv","tv_bench","living",6),
 ("regał","bookshelf","living",8),("witryna","display_cabinet","living",5),("komoda","chest_of_drawers","bedroom",8),("kredens","sideboard","dining",5),
 ("lampa podłogowa","floor_lamp","living",8),("lampa stołowa","table_lamp","living",8),("lampa wisząca","pendant_lamp","dining",8),("lampa sufitowa","ceiling_lamp","living",5),("kinkiet","wall_lamp","bedroom",5),
 ("dywan","rug","living",8),("zasłony","curtains","living",4),("poduszka","cushion","living",4),("koc","throw","living",2),
 ("lustro","mirror","hallway",8),("roślina sztuczna","plant","living",8),("doniczka","plant_pot","living",6),("wazon","vase","living",5),("ramka na zdjęcia","picture_frame","living",4),("świecznik","candle_holder","living",4),("zegar","clock","living",3),("kosz","basket","living",4),
 ("stół do jadalni","dining_table","dining",8),("stół rozkładany","dining_table","dining",4),("krzesło","dining_chair","dining",10),("hoker","bar_stool","kitchen",5),("ławka","bench","dining",4),("stołek","stool","kitchen",3),
 ("rama łóżka 160x200","bed_double","bedroom",8),("rama łóżka 140x200","bed_double","bedroom",4),("łóżko 90x200","bed_single","bedroom",5),("łóżko piętrowe","bunk_bed","kids",3),("łóżko dziecięce","kids_bed","kids",5),("łóżeczko","crib","kids",4),
 ("szafka nocna","nightstand","bedroom",8),("szafa","wardrobe","bedroom",8),("toaletka","dressing_table","bedroom",3),("materac","mattress","bedroom",2),
 ("biurko dziecięce","kids_desk","kids",3),("krzesło dziecięce","kids_chair","kids",4),("zabawki","toy","kids",6),("przechowywanie zabawek","toy_storage","kids",5),("przewijak","changing_table","kids",3),("pluszak","soft_toy","kids",4),
 ("biurko","desk","office",8),("krzesło biurowe","office_chair","office",8),("kontener z szufladami","drawer_unit","office",4),("szafka biurowa","office_cabinet","office",3),("lampa biurkowa","desk_lamp","office",4),
 ("szafka kuchenna stojąca","kitchen_base_cabinet","kitchen",6),("szafka kuchenna wisząca","kitchen_wall_cabinet","kitchen",6),("szafka wysoka kuchnia","kitchen_tall_cabinet","kitchen",4),("wyspa kuchenna","kitchen_island","kitchen",4),("wózek kuchenny","kitchen_trolley","kitchen",4),("blat kuchenny","worktop","kitchen",2),("kuchnia","kitchen","kitchen",4),
 ("garnek","cookware","kitchen",4),("patelnia","cookware","kitchen",2),("deska do krojenia","kitchen_accessory","kitchen",3),("talerz","tableware","dining",3),("kubek","tableware","kitchen",3),("czajnik","kettle","kitchen",2),("pojemnik na żywność","food_storage","kitchen",3),("relingi kuchenne","kitchen_accessory","kitchen",3),
 ("szafka pod umywalkę","bathroom_vanity","bathroom",8),("szafka łazienkowa wysoka","bathroom_storage","bathroom",5),("szafka z lustrem","bathroom_cabinet","bathroom",4),("lustro łazienkowe","bathroom_mirror","bathroom",3),("wieszak na ręczniki","towel_rail","bathroom",3),("kosz na pranie","laundry_basket","bathroom",3),("akcesoria łazienkowe","bathroom_accessory","bathroom",4),
 ("szafka na buty","shoe_cabinet","hallway",6),("wieszak na ubrania","coat_rack","hallway",6),("garderoba","hallway_storage","hallway",4),("wieszak ścienny","wall_hook","hallway",3),
 ("meble ogrodowe","garden_furniture","garden",8),("stół ogrodowy","garden_table","garden",5),("krzesło ogrodowe","garden_chair","garden",6),("leżak","sun_lounger","garden",4),("sofa ogrodowa","garden_sofa","garden",4),("meble balkonowe","balcony_furniture","balcony",5),("parasol ogrodowy","parasol","garden",3),("doniczka zewnętrzna","plant_pot","garden",3),("oświetlenie zewnętrzne","outdoor_lamp","garden",3),
 ("regał na książki","bookshelf","living",4),("półka ścienna","wall_shelf","living",6),("regał metalowy","shelving_unit","utility",4),("pudełko","storage_box","utility",4),("szafka","cabinet","living",6),("system przechowywania","storage_system","utility",4),
 ("kosz na śmieci","bin","kitchen",3),("deska do prasowania","utility","utility",2),("suszarka na pranie","drying_rack","utility",3),("drabina","step_stool","utility",3),
]
lock = threading.Lock()
recs = {}
P = f"{ROOT}/tmp/ikea_pl.json"
if os.path.exists(P):
    recs = {r["article_number"]: r for r in json.load(open(P))}
existing = set()
for f in ("tmp/fetched.json", "tmp/appl_records.json"):
    try:
        for r in json.load(open(f"{ROOT}/{f}")):
            if r.get("article_number"): existing.add(r["article_number"])
    except Exception as e: print("warn", f, e)

def plsearch(q, n=60):
    u = "https://sik.search.blue.cdtapps.com/pl/pl/search-result-page?" + urllib.parse.urlencode({"q": q, "size": n, "types": "PRODUCT"})
    d = json.loads(get(u))
    return [it["product"] for it in d["searchResultPage"]["products"]["main"]["items"] if "product" in it]

def best_glb(model):
    urls = [e["contentUrl"].split("?")[0] for e in model.get("encoding", []) if e.get("encodingFormat") == "model/gltf-binary"]
    for test in (lambda u: "geomagical" not in u and "draco" not in u and "rqp3" in u,
                 lambda u: "geomagical" not in u and "draco" not in u,
                 lambda u: "draco" not in u,
                 lambda u: True):
        c = [u for u in urls if test(u)]
        if c: return c[0]
    return None

def uk_url(item):
    try:
        u = "https://sik.search.blue.cdtapps.com/gb/en/search-result-page?" + urllib.parse.urlencode({"q": item, "size": 5, "types": "PRODUCT"})
        d = json.loads(get(u, tries=2))
        for it in d["searchResultPage"]["products"]["main"]["items"]:
            p = it.get("product")
            if p and p["itemNo"] == item: return p["pipUrl"], (p.get("salesPrice") or {}).get("numeral")
    except Exception: pass
    return None, None

def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:40]

def process(p, category, room, q):
    item = p["itemNo"]
    try:
        L = ld(get(p["pipUrl"]))
    except Exception as e: return None
    if "3DModel" not in L: return None
    glb = best_glb(L["3DModel"])
    if not glb: return None
    pr = L.get("Product", {})
    key = f"{slug(p['name'])}_{slug(p.get('typeName',''))}"[:50].strip("_")
    fn = f"{OUT}/{item}.glb"
    if not os.path.exists(fn):
        try: open(fn, "wb").write(get(glb, binary=True))
        except Exception as e: print("dl fail", item, e); return None
    uk, gbp = uk_url(item)
    offers = pr.get("offers") or {}
    price = (p.get("salesPrice") or {}).get("numeral") or offers.get("price")
    cp = [c.get("name") for c in (p.get("categoryPath") or [])]
    return dict(key=key, article_number=item, name=f"{p['name']} {p.get('typeName','')}".strip(), full_name=pr.get("name"),
        category=category, room=room, query=q, ikea_category_path=cp,
        colour=pr.get("color") or ", ".join(c.get("name","") for c in p.get("colors", [])), colours=[c.get("name") for c in p.get("colors", [])],
        material=pr.get("material"), dims_text=p.get("itemMeasureReferenceText"), width=pr.get("width"), depth=pr.get("depth"), height=pr.get("height"),
        price_pln=float(price) if price else None, url_pl=p["pipUrl"], url_uk=uk, price_gbp=gbp,
        glb_url=glb, draco="draco" in glb, raw_file=os.path.relpath(fn, ROOT), raw_size=os.path.getsize(fn),
        image=p.get("mainImageUrl"), source="IKEA", author="IKEA", store="IKEA",
        license="IKEA product model – personal/demo use only (© Inter IKEA Systems B.V.)")

def run_query(args):
    q, category, room, nmax = args
    try: prods = plsearch(q)
    except Exception as e: print("SEARCH FAIL", q, e); return
    got = 0; names = {}
    for p in prods:
        if got >= nmax: break
        item = p["itemNo"]
        if p.get("itemType") not in (None, "ART", "SPR"): pass
        with lock:
            if item in recs or item in existing: 
                continue
            # variety: max 2 colour variants of same product name
            nm = p["name"] + p.get("typeName", "")
            if names.get(nm, 0) >= 2: continue
            recs[item] = None  # reserve
        r = process(p, category, room, q)
        with lock:
            if r: recs[item] = r; got += 1; names[nm] = names.get(nm, 0) + 1
            else: recs.pop(item, None)
    print(f"{q}: {got}", flush=True)

with ThreadPoolExecutor(6) as ex:
    list(ex.map(run_query, Q))
out = [r for r in recs.values() if r]
json.dump(out, open(P, "w"), indent=1, ensure_ascii=False)
print("TOTAL", len(out), "MB", sum(r["raw_size"] for r in out) / 1e6)
