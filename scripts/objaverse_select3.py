"""Turn-6: pick curated interior Objaverse (Sketchfab) items from local LVIS + metadata cache.
Licence filter: CC-BY, CC-BY-SA, CC0 only. Ranked by likes; geometry/size sanity filters."""
import gzip, json, re
H = "/home/box/.objaverse/hf-objaverse-v1"
lv = json.load(gzip.open(f"{H}/lvis-annotations.json.gz")); paths = json.load(gzip.open(f"{H}/object-paths.json.gz"))
# lvis: (category, room, scale_axis, target_m, n)
C = {
 "armchair":("armchair","living","z",0.85,12),"sofa":("sofa","living","x",2.1,12),"loveseat":("sofa","living","x",1.6,6),"sofa_bed":("sofa_bed","living","x",2.0,5),
 "chaise_longue":("daybed","living","x",1.7,4),"recliner":("armchair","living","z",1.0,4),"rocking_chair":("armchair","living","z",1.0,5),"ottoman":("pouffe","living","z",0.45,5),
 "footstool":("footstool","living","z",0.42,5),"beanbag":("pouffe","living","z",0.7,4),"chair":("dining_chair","dining","z",0.85,25),"folding_chair":("dining_chair","dining","z",0.82,3),
 "stool":("stool","kitchen","z",0.65,8),"music_stool":("stool","living","z",0.5,3),"step_stool":("step_stool","utility","z",0.45,3),"bench":("bench","hallway","x",1.2,6),
 "coffee_table":("coffee_table","living","z",0.45,10),"table":("table","dining","z",0.75,10),"dining_table":("dining_table","dining","z",0.75,10),"kitchen_table":("dining_table","kitchen","z",0.75,5),
 "desk":("desk","office","z",0.75,10),"bookcase":("bookshelf","living","z",1.9,10),"cabinet":("cabinet","living","z",1.0,8),"cupboard":("cupboard","kitchen","z",1.8,6),
 "dresser":("chest_of_drawers","bedroom","z",0.9,8),"drawer":("chest_of_drawers","bedroom","z",0.8,4),"armoire":("wardrobe","bedroom","z",2.0,6),"wardrobe":("wardrobe","bedroom","z",2.0,6),
 "file_cabinet":("office_cabinet","office","z",1.0,4),"locker":("locker","hallway","z",1.8,2),"bed":("bed_double","bedroom","x",2.1,8),"bunk_bed":("bunk_bed","kids","z",1.6,4),
 "futon":("sofa_bed","living","x",1.9,3),"headboard":("headboard","bedroom","x",1.6,3),"mattress":("mattress","bedroom","x",2.0,3),"crib":("crib","kids","x",1.25,3),
 "highchair":("kids_chair","kids","z",1.0,3),"playpen":("playpen","kids","x",1.2,2),"coatrack":("coat_rack","hallway","z",1.8,4),"towel_rack":("towel_rail","bathroom","z",0.9,3),
 "fireplace":("fireplace","living","z",1.1,8),"piano":("piano","living","z",1.3,6),"pool_table":("pool_table","living","x",2.5,3),"table-tennis_table":("ping_pong_table","living","x",2.7,2),
 "lamp":("table_lamp","living","z",0.55,10),"table_lamp":("table_lamp","living","z",0.55,12),"chandelier":("chandelier","dining","z",0.8,12),"lampshade":("lamp_shade","living","z",0.35,4),
 "lantern":("candle_holder","living","z",0.35,5),"oil_lamp":("lamp","living","z",0.35,4),"candle":("candle","living","z",0.15,4),"candle_holder":("candle_holder","living","z",0.25,6),
 "spotlight":("spotlight","living","z",0.25,2),"lightbulb":("lamp","living","z",0.12,2),
 "television_set":("tv","living","x",1.2,6),"monitor_(computer_equipment) computer_monitor":("monitor","office","x",0.6,4),"computer_keyboard":("keyboard","office","x",0.44,3),
 "laptop_computer":("laptop","office","x",0.33,4),"speaker_(stero_equipment)":("speaker","living","z",0.4,4),"subwoofer":("speaker","living","z",0.45,2),"stereo_(sound_system)":("hifi","living","x",0.5,3),
 "record_player":("record_player","living","x",0.45,4),"radio_receiver":("radio","living","x",0.35,4),"telephone":("phone","living","x",0.22,4),"printer":("printer","office","x",0.45,3),
 "projector":("projector","living","x",0.3,2),"router_(computer_equipment)":("router","office","x",0.25,2),"headset":("headphones","office","z",0.2,3),"typewriter":("typewriter","office","x",0.45,4),
 "camera":("camera","living","x",0.14,3),"sewing_machine":("sewing_machine","utility","x",0.42,2),
 "refrigerator":("fridge","kitchen","z",1.85,4),"stove":("oven","kitchen","z",0.9,3),"microwave_oven":("microwave","kitchen","x",0.5,3),"toaster":("toaster","kitchen","x",0.3,3),
 "toaster_oven":("toaster","kitchen","x",0.45,2),"coffee_maker":("coffee_machine","kitchen","z",0.38,4),"kettle":("kettle","kitchen","z",0.25,3),"teakettle":("kettle","kitchen","z",0.22,3),
 "food_processor":("kitchen_appliance","kitchen","z",0.4,2),"mixer_(kitchen_tool)":("kitchen_appliance","kitchen","z",0.38,2),"blender":("kitchen_appliance","kitchen","z",0.4,2),
 "vacuum_cleaner":("vacuum","utility","z",1.1,2),"fan":("fan","living","z",1.1,4),"heater":("heater","living","z",0.6,2),"radiator":("radiator","living","x",0.8,3),"water_cooler":("water_cooler","office","z",1.1,2),
 "kitchen_sink":("kitchen_sink","kitchen","x",0.8,4),"faucet":("kitchen_tap","kitchen","z",0.3,3),"water_faucet":("bathroom_tap","bathroom","z",0.25,3),
 "pot":("cookware","kitchen","x",0.3,5),"saucepan":("cookware","kitchen","x",0.35,3),"frying_pan":("cookware","kitchen","x",0.45,3),"wok":("cookware","kitchen","x",0.45,2),"casserole":("cookware","kitchen","x",0.3,2),
 "chopping_board":("kitchen_accessory","kitchen","x",0.4,4),"knife":("cutlery","kitchen","x",0.3,3),"spice_rack":("kitchen_accessory","kitchen","x",0.35,3),"colander":("kitchen_accessory","kitchen","x",0.28,2),
 "rolling_pin":("kitchen_accessory","kitchen","x",0.4,2),"cooking_utensil":("kitchen_accessory","kitchen","z",0.32,3),"bread-bin":("kitchen_accessory","kitchen","x",0.4,2),
 "teapot":("tableware","dining","z",0.18,5),"mug":("tableware","kitchen","z",0.1,5),"cup":("tableware","dining","z",0.09,3),"teacup":("tableware","dining","z",0.07,2),"bowl":("tableware","dining","x",0.2,4),
 "plate":("tableware","dining","x",0.27,3),"platter":("tableware","dining","x",0.4,2),"wineglass":("glassware","dining","z",0.22,4),"glass_(drink_container)":("glassware","dining","z",0.12,3),
 "pitcher_(vessel_for_liquid)":("glassware","dining","z",0.25,3),"wine_bottle":("bottle","kitchen","z",0.3,3),"jar":("food_storage","kitchen","z",0.2,3),"chinaware":("tableware","dining","x",0.3,3),
 "tray":("tray","dining","x",0.45,3),"tablecloth":("tablecloth","dining","x",1.6,2),"wine_bucket":("tableware","dining","z",0.25,2),
 "toilet":("toilet","bathroom","z",0.8,5),"bathtub":("bathtub","bathroom","x",1.7,5),"sink":("bathroom_sink","bathroom","x",0.6,3),"washbasin":("bathroom_sink","bathroom","x",0.6,4),
 "shower_head":("shower","bathroom","z",0.3,2),"shower_curtain":("shower_curtain","bathroom","z",1.9,2),"towel":("towel","bathroom","x",0.6,2),"bath_towel":("towel","bathroom","x",0.7,2),
 "bath_mat":("bath_mat","bathroom","x",0.8,2),"toothbrush":("bathroom_accessory","bathroom","z",0.19,2),"soap":("bathroom_accessory","bathroom","x",0.09,2),"shampoo":("bathroom_accessory","bathroom","z",0.22,2),
 "toilet_tissue":("bathroom_accessory","bathroom","z",0.11,2),"hair_dryer":("bathroom_accessory","bathroom","x",0.25,2),"clothes_hamper":("laundry_basket","bathroom","z",0.6,3),"hamper":("laundry_basket","bathroom","z",0.6,2),
 "automatic_washer":("washing_machine","utility","z",0.85,3),"ironing_board":("utility","utility","x",1.2,2),"water_heater":("boiler","utility","z",0.8,2),
 "mirror":("mirror","hallway","z",1.0,8),"hand_glass":("mirror","bathroom","z",0.3,2),"painting":("wall_art","living","z",0.7,10),"poster":("wall_art","living","z",0.7,4),"tapestry":("wall_art","living","z",1.2,3),
 "wall_clock":("clock","living","z",0.35,5),"clock":("clock","living","z",0.3,4),"alarm_clock":("clock","bedroom","z",0.12,4),"vase":("vase","living","z",0.35,10),"pottery":("vase","living","z",0.3,5),
 "urn":("vase","living","z",0.5,3),"flowerpot":("plant","living","z",0.6,12),"flower_arrangement":("plant","living","z",0.45,6),"bouquet":("plant","dining","z",0.4,4),"window_box_(for_plants)":("plant_pot","balcony","x",0.6,3),
 "sculpture":("sculpture","living","z",0.45,8),"statue_(sculpture)":("sculpture","living","z",0.5,5),"figurine":("decor","living","z",0.2,6),"globe":("decor","office","z",0.45,4),"hourglass":("decor","living","z",0.2,2),
 "chessboard":("decor","living","x",0.4,3),"trophy_cup":("decor","living","z",0.3,2),"basket":("basket","living","x",0.4,5),"box":("storage_box","utility","x",0.4,4),"crate":("storage_box","utility","x",0.5,3),
 "trunk":("storage_chest","living","x",0.9,4),"suitcase":("suitcase","bedroom","z",0.7,3),"book":("books","living","z",0.24,5),"hardback_book":("books","living","z",0.24,4),"magazine":("books","living","x",0.3,2),
 "cushion":("cushion","living","x",0.5,6),"pillow":("pillow","bedroom","x",0.6,4),"blanket":("throw","living","x",1.5,2),"quilt":("bedspread","bedroom","x",2.0,2),"bedspread":("bedspread","bedroom","x",2.2,3),
 "curtain":("curtains","living","z",2.5,6),"runner_(carpet)":("runner_rug","hallway","x",2.5,3),"doormat":("doormat","hallway","x",0.75,3),"place_mat":("tableware","dining","x",0.45,2),
 "doorknob":("door_hardware","hallway","x",0.12,2),"knocker_(on_a_door)":("door_hardware","hallway","z",0.18,2),"wall_socket":("electrical","living","z",0.08,2),"thermostat":("electrical","living","z",0.12,2),
 "vent":("ventilation","living","x",0.3,1),"teddy_bear":("soft_toy","kids","z",0.4,6),"toy":("toy","kids","x",0.3,6),"doll":("toy","kids","z",0.35,3),"dollhouse":("toy","kids","x",0.7,3),
 "rag_doll":("soft_toy","kids","z",0.4,2),"Lego":("toy","kids","x",0.25,3),"rocking_horse":("toy","kids","x",0.9,0),"easel":("easel","kids","z",1.5,3),"blackboard":("wall_art","kids","x",1.0,2),
 "bulletin_board":("wall_art","office","x",0.9,2),"corkboard":("wall_art","office","x",0.8,2),"calendar":("decor","office","z",0.4,2),"notebook":("desk_accessory","office","x",0.3,2),
 "binder":("desk_accessory","office","z",0.32,2),"pen":("desk_accessory","office","x",0.14,2),"stapler_(stapling_machine)":("desk_accessory","office","x",0.15,2),"calculator":("desk_accessory","office","x",0.17,2),
 "guitar":("guitar","living","z",1.0,6),"violin":("instrument","living","z",0.6,3),"drum_(musical_instrument)":("instrument","living","z",0.6,3),"harmonium":("instrument","living","x",0.6,2),
 "birdcage":("decor","living","z",0.5,3),"aquarium":("aquarium","living","x",0.9,4),"fishbowl":("aquarium","living","z",0.25,2),"kennel":("pet","garden","x",0.9,2),
 "trash_can":("bin","kitchen","z",0.6,5),"watering_can":("garden_accessory","garden","x",0.45,3),"umbrella":("hallway_accessory","hallway","z",0.9,2),"parasol":("parasol","garden","z",2.4,3),
 "deck_chair":("sun_lounger","garden","x",1.5,4),"hammock":("garden_furniture","garden","x",2.5,2),"grill":("grill","garden","z",1.0,4),"birdhouse":("garden_accessory","garden","z",0.35,3),
 "birdbath":("garden_accessory","garden","z",0.7,2),"lamppost":("outdoor_lamp","garden","z",2.5,2),"mailbox_(at_home)":("garden_accessory","garden","z",1.2,2),"ladder":("step_stool","utility","z",1.6,2),
 "stepladder":("step_stool","utility","z",1.4,2),"broom":("cleaning","utility","z",1.3,2),"mop":("cleaning","utility","z",1.3,2),"dustpan":("cleaning","utility","x",0.3,2),"bucket":("cleaning","utility","z",0.3,2),
 "first-aid_kit":("utility","bathroom","x",0.3,1),"fire_extinguisher":("utility","kitchen","z",0.5,2),"toolbox":("tools","utility","x",0.45,2),"dartboard":("wall_art","living","z",0.45,2),
 "phonograph_record":("decor","living","x",0.31,2),"cassette":("decor","living","x",0.1,1),"telephone_booth":("decor","living","z",2.2,0),"wreath":("decor","hallway","z",0.4,2),"Christmas_tree":("decor","living","z",1.8,4),
 "gameboard":("toy","kids","x",0.4,2),"bottle":("bottle","kitchen","z",0.28,2),"water_jug":("glassware","kitchen","z",0.3,2),"sugar_bowl":("tableware","dining","z",0.1,2),
 "salad_plate":("tableware","dining","x",0.22,1),"saucer":("tableware","dining","x",0.15,1),"cream_pitcher":("tableware","dining","z",0.1,1),"coffeepot":("tableware","kitchen","z",0.22,2),
 "soup_bowl":("tableware","dining","x",0.2,2),"thermos_bottle":("tableware","kitchen","z",0.28,1),"pepper_mill":("kitchen_accessory","kitchen","z",0.2,2),"ice_maker":("kitchen_appliance","kitchen","z",0.4,1),
 "cooker":("oven","kitchen","z",0.9,2),"oven":("oven","kitchen","z",0.6,2),"dishwasher":("dishwasher","kitchen","z",0.85,2),"air_conditioner":("air_conditioner","living","x",0.9,2),
}
BAD = re.compile(r"\b(low ?poly|lowpoly|game ?ready|stylized|cartoon|toon|anime|voxel|minecraft|scan|photogrammetry|broken|destroyed|ruin|rusty|zombie|horror|blood|skull|nsfw|sci-?fi|fantasy|medieval|test|wip|untitled|sample|pack|set of|collection|kit|scene|room|interior|house|diorama|lowres)\b", re.I)
shards = {}
for k in C:
    for u in lv.get(k, []): shards.setdefault(paths[u].split("/")[1], set()).add(u)
meta = {}
for s, us in shards.items():
    m = json.load(gzip.open(f"{H}/metadata/{s}.json.gz"))
    for u in us: meta[u] = m.get(u)
used = {r.get("uid") for r in json.load(open("/workspace/interior-lib/tmp/objav_pick.json")).values()}
out, seen = [], set()
for k, (cat, room, ax, tm, n) in C.items():
    cands = []
    for u in lv.get(k, []):
        a = meta.get(u)
        if not a or u in used or u in seen: continue
        g = (a.get("archives") or {}).get("glb") or {}
        if a.get("license") not in ("by", "by-sa", "cc0"): continue
        if a.get("animationCount", 0) or a.get("isAgeRestricted"): continue
        f = g.get("faceCount") or a.get("faceCount") or 0
        if not (300 <= f <= 500000) or (g.get("size") or 0) > 45e6: continue
        if BAD.search(a["name"]) or (a.get("likeCount", 0) < 3): continue
        cands.append((a.get("likeCount", 0) + a.get("viewCount", 0) / 200, u, a, f, g))
    cands.sort(key=lambda t: -t[0])
    for sc, u, a, f, g in cands[: max(0, int(n * 1.5 + 0.99))]:  # over-pick 50%, QA trims
        seen.add(u); th = sorted(a.get("thumbnails", {}).get("images", []), key=lambda i: -i.get("width", 0))
        out.append(dict(uid=u, lvis=k, cat=cat, room=room, scale_axis=ax, target_m=tm, quota=n, name=a["name"], likes=a.get("likeCount", 0), views=a.get("viewCount", 0),
                        faces=f, size=g.get("size"), tex=g.get("textureMaxResolution"), license=a["license"], author=(a.get("user") or {}).get("displayName") or (a.get("user") or {}).get("username"),
                        url=a.get("viewerUrl"), path=paths[u]))
json.dump(out, open("/workspace/interior-lib/tmp/objav3_cands.json", "w"), indent=1)
print(len(out), "candidates", round(sum(o["size"] or 0 for o in out) / 1e9, 2), "GB")
