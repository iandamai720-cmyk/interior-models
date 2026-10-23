"""Mass IKEA scrape from the Polish site (ikea.com/pl/pl): PLN price + PL link + UK link + GLB.
Same mechanism as fetch_ikea.py: PIP JSON-LD 3DModel encoding[].contentUrl."""
import json, os, re, sys, time, urllib.parse, threading
from concurrent.futures import ThreadPoolExecutor
src = open(os.path.join(os.path.dirname(__file__), "fetch_ikea.py")).read().split("def main")[0]
exec(src)
OUT = f"{ROOT}/staging/ikea3"
# (query_pl, category, room, max_items)
Q = [
 ("sofa modułowa","sofa_modular","living",10),("sofa narożna","sofa_corner","living",10),("sofa 3-osobowa","sofa","living",10),("sofa 2-osobowa","sofa","living",8),("sofa rozkładana","sofa_bed","living",8),("sofa z szezlongiem","sofa_corner","living",8),
 ("SÖDERHAMN","sofa_modular","living",6),("VIMLE","sofa_modular","living",8),("KIVIK","sofa","living",6),("FRIHETEN","sofa_bed","living",4),("EKTORP","sofa","living",5),("GRÖNLID","sofa_modular","living",5),("HYLTARP","sofa","living",4),("LANDSKRONA","sofa","living",4),("UPPLAND","sofa","living",4),("JÄTTEBO","sofa_modular","living",5),("KLIPPAN","sofa","living",4),("GLOSTAD","sofa","living",3),("LINANÄS","sofa","living",3),("PÄRUP","sofa","living",3),
 ("fotel","armchair","living",12),("fotel bujany","armchair","living",4),("fotel uszak","armchair","living",4),("POÄNG","armchair","living",5),("STRANDMON","armchair","living",3),("podnóżek","footstool","living",6),("pufa","pouffe","living",6),
 ("stolik kawowy","coffee_table","living",12),("stolik boczny","side_table","living",10),("szafka pod tv","tv_bench","living",10),("BESTÅ","tv_bench","living",8),("zestaw mebli tv","tv_storage","living",6),("regał","bookshelf","living",10),("KALLAX","bookshelf","living",6),("BILLY","bookshelf","living",6),("HEMNES","cabinet","living",8),("witryna","display_cabinet","living",8),("kredens","sideboard","dining",8),("komoda","chest_of_drawers","bedroom",12),("MALM","chest_of_drawers","bedroom",6),
 ("rama łóżka 160x200","bed_double","bedroom",12),("rama łóżka 180x200","bed_double","bedroom",8),("rama łóżka 140x200","bed_double","bedroom",8),("łóżko kontynentalne","bed_double","bedroom",4),("łóżko z pojemnikiem","bed_double","bedroom",6),("łóżko tapicerowane","bed_double","bedroom",6),("łóżko 90x200","bed_single","bedroom",8),("łóżko rozkładane","bed_single","bedroom",4),("leżanka","daybed","bedroom",5),("zagłówek","headboard","bedroom",3),
 ("szafka nocna","nightstand","bedroom",12),("PAX szafa","wardrobe","bedroom",14),("PAX kombinacja","wardrobe","bedroom",10),("szafa z drzwiami przesuwnymi","wardrobe","bedroom",6),("szafa otwarta","wardrobe","bedroom",5),("szafa 2-drzwiowa","wardrobe","bedroom",6),("toaletka","dressing_table","bedroom",5),("wieszak na ubrania stojący","clothes_rack","bedroom",5),("lustro stojące","mirror","bedroom",5),
 ("stół do jadalni","dining_table","dining",12),("stół rozkładany","dining_table","dining",8),("stół okrągły","dining_table","dining",6),("stół barowy","bar_table","dining",5),("zestaw stół i krzesła","dining_set","dining",6),("krzesło","dining_chair","dining",14),("krzesło tapicerowane","dining_chair","dining",6),("krzesło składane","dining_chair","dining",5),("hoker","bar_stool","kitchen",8),("ławka","bench","dining",6),("stołek","stool","kitchen",6),
 ("biurko","desk","office",12),("biurko z regulacją wysokości","desk","office",6),("biurko narożne","desk","office",4),("krzesło biurowe","office_chair","office",10),("krzesło gamingowe","office_chair","office",5),("kontener z szufladami","drawer_unit","office",5),("szafka na dokumenty","office_cabinet","office",5),("lampa biurkowa","desk_lamp","office",6),("organizer biurowy","desk_accessory","office",4),
 ("METOD szafka stojąca","kitchen_base_cabinet","kitchen",12),("METOD szafka wisząca","kitchen_wall_cabinet","kitchen",10),("METOD szafka wysoka","kitchen_tall_cabinet","kitchen",8),("METOD szafka pod zlewozmywak","kitchen_sink_cabinet","kitchen",5),("METOD szafka narożna","kitchen_corner_cabinet","kitchen",5),("METOD szafka na piekarnik","kitchen_oven_cabinet","kitchen",5),("front szafki","kitchen_front","kitchen",6),("wyspa kuchenna","kitchen_island","kitchen",6),("wózek kuchenny","kitchen_trolley","kitchen",6),("ENHET","kitchen_cabinet","kitchen",8),("KNOXHULT","kitchen","kitchen",6),("półka kuchenna","kitchen_shelf","kitchen",5),("zlewozmywak","kitchen_sink","kitchen",5),("bateria kuchenna","kitchen_tap","kitchen",5),("okap","cooker_hood","kitchen",4),("płyta indukcyjna","hob","kitchen",4),("piekarnik","oven","kitchen",4),("lodówka","fridge","kitchen",4),("zmywarka","dishwasher","kitchen",3),("mikrofalówka","microwave","kitchen",3),
 ("garnek","cookware","kitchen",6),("patelnia","cookware","kitchen",4),("deska do krojenia","kitchen_accessory","kitchen",4),("talerz","tableware","dining",5),("miska","tableware","dining",5),("kubek","tableware","kitchen",5),("szklanka","glassware","dining",5),("karafka","glassware","dining",3),("sztućce","cutlery","dining",3),("czajnik","kettle","kitchen",3),("pojemnik na żywność","food_storage","kitchen",5),("relingi kuchenne","kitchen_accessory","kitchen",4),("suszarka do naczyń","kitchen_accessory","kitchen",4),("przyprawy","kitchen_accessory","kitchen",3),("taca","tray","dining",4),
 ("szafka pod umywalkę","bathroom_vanity","bathroom",12),("umywalka","bathroom_sink","bathroom",6),("szafka łazienkowa wysoka","bathroom_storage","bathroom",8),("szafka z lustrem","bathroom_cabinet","bathroom",6),("lustro łazienkowe","bathroom_mirror","bathroom",5),("regał łazienkowy","bathroom_shelf","bathroom",5),("wieszak na ręczniki","towel_rail","bathroom",4),("kosz na pranie","laundry_basket","bathroom",5),("dozownik do mydła","bathroom_accessory","bathroom",5),("bateria umywalkowa","bathroom_tap","bathroom",4),("taboret łazienkowy","bathroom_stool","bathroom",3),("ręcznik","towel","bathroom",3),
 ("szafka na buty","shoe_cabinet","hallway",10),("wieszak na ubrania","coat_rack","hallway",8),("garderoba","hallway_storage","hallway",6),("wieszak ścienny","wall_hook","hallway",5),("ławka do przedpokoju","hallway_bench","hallway",5),("lustro ścienne","mirror","hallway",8),("wycieraczka","doormat","hallway",3),("parasol stojak","hallway_accessory","hallway",2),
 ("biurko dziecięce","kids_desk","kids",5),("krzesło dziecięce","kids_chair","kids",6),("łóżko dziecięce","kids_bed","kids",8),("łóżko piętrowe","bunk_bed","kids",5),("łóżko na antresoli","loft_bed","kids",4),("łóżeczko","crib","kids",6),("przewijak","changing_table","kids",4),("zabawki","toy","kids",10),("przechowywanie zabawek","toy_storage","kids",8),("pluszak","soft_toy","kids",8),("namiot dziecięcy","toy","kids",3),("lampa dziecięca","kids_lamp","kids",5),("dywan dziecięcy","kids_rug","kids",4),("stolik dziecięcy","kids_table","kids",4),("TROFAST","toy_storage","kids",5),("SMÅSTAD","kids_storage","kids",6),
 ("meble ogrodowe","garden_furniture","garden",10),("stół ogrodowy","garden_table","garden",8),("krzesło ogrodowe","garden_chair","garden",8),("leżak","sun_lounger","garden",6),("sofa ogrodowa","garden_sofa","garden",6),("meble balkonowe","balcony_furniture","balcony",8),("stolik balkonowy","balcony_furniture","balcony",5),("parasol ogrodowy","parasol","garden",4),("doniczka zewnętrzna","plant_pot","garden",5),("oświetlenie zewnętrzne","outdoor_lamp","garden",5),("hamak","garden_furniture","garden",3),("skrzynia ogrodowa","garden_storage","garden",4),("płytki tarasowe","decking","garden",3),("ławka ogrodowa","garden_bench","garden",4),
 ("lampa podłogowa","floor_lamp","living",12),("lampa stołowa","table_lamp","living",12),("lampa wisząca","pendant_lamp","dining",12),("lampa sufitowa","ceiling_lamp","living",8),("kinkiet","wall_lamp","bedroom",8),("listwa oświetleniowa","spotlight","living",4),("reflektor","spotlight","living",4),("lampa LED","lamp","living",5),("lampka nocna","table_lamp","bedroom",5),("abażur","lamp_shade","living",4),
 ("dywan","rug","living",12),("dywan okrągły","rug","living",6),("dywan z długim włosiem","rug","living",5),("chodnik","runner_rug","hallway",4),("zasłony","curtains","living",8),("firanka","curtains","living",4),("rolety","blinds","living",6),("karnisz","curtain_rail","living",3),("poduszka","cushion","living",8),("koc","throw","living",5),("narzuta","bedspread","bedroom",4),("pościel","bedding","bedroom",4),
 ("lustro","mirror","hallway",10),("roślina sztuczna","plant","living",12),("roślina doniczkowa","plant","living",8),("osłonka na doniczkę","plant_pot","living",8),("stojak na rośliny","plant_stand","living",5),("wazon","vase","living",8),("ramka na zdjęcia","picture_frame","living",6),("obraz","wall_art","living",6),("plakat","wall_art","living",4),("świecznik","candle_holder","living",6),("lampion","candle_holder","living",4),("zegar","clock","living",5),("kosz","basket","living",6),("dekoracja","decor","living",6),("figurka","decor","living",4),("misa dekoracyjna","decor","living",4),
 ("regał na książki","bookshelf","living",6),("półka ścienna","wall_shelf","living",8),("regał metalowy","shelving_unit","utility",6),("pudełko","storage_box","utility",8),("pudełko z pokrywą","storage_box","utility",6),("kosz do przechowywania","basket","utility",6),("szafka","cabinet","living",8),("system przechowywania","storage_system","utility",6),("BOAXEL","storage_system","utility",4),("IVAR","shelving_unit","utility",5),("PLATSA","wardrobe","bedroom",6),("ELVARLI","storage_system","bedroom",4),("szafka ścienna","wall_cabinet","living",5),("gablota","display_cabinet","living",4),
 ("kosz na śmieci","bin","kitchen",4),("deska do prasowania","utility","utility",3),("suszarka na pranie","drying_rack","utility",3),("drabina","step_stool","utility",3),("odkurzacz","vacuum","utility",2),("oczyszczacz powietrza","air_purifier","living",3),("wentylator","fan","living",3),("głośnik","speaker","living",4),
]
lock = threading.Lock()
recs = {}
P = f"{ROOT}/tmp/ikea_pl3.json"
if os.path.exists(P):
    recs = {r["article_number"]: r for r in json.load(open(P))}
existing = set()
for f in ("tmp/fetched.json", "tmp/appl_records.json", "tmp/ikea_pl.json"):
    try:
        for r in json.load(open(f"{ROOT}/{f}")):
            if r.get("article_number"): existing.add(r["article_number"])
    except Exception as e: print("warn", f, e)

def plsearch(q, n=100):
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
            if names.get(nm, 0) >= 3: continue
            recs[item] = None  # reserve
        r = process(p, category, room, q)
        with lock:
            if r: recs[item] = r; got += 1; names[nm] = names.get(nm, 0) + 1
            else: recs.pop(item, None)
    print(f"{q}: {got}", flush=True)
    with lock: json.dump([r for r in recs.values() if r], open(P, "w"), ensure_ascii=False)

with ThreadPoolExecutor(6) as ex:
    list(ex.map(run_query, Q))
out = [r for r in recs.values() if r]
json.dump(out, open(P, "w"), indent=1, ensure_ascii=False)
print("TOTAL", len(out), "MB", sum(r["raw_size"] for r in out) / 1e6)
