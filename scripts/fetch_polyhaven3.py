"""Turn-6: remaining interior-relevant Poly Haven models (CC0) -> staging/polyhaven3/<id>/ (glTF 1k, 2k for furniture)"""
import json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT = "/workspace/interior-lib"; UA = {"User-Agent": "interior-lib/1.0 (personal asset library)"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
# (ph_id, category, room)
PICK = [("GothicBed_01","bed_double","bedroom"),("GothicCabinet_01","cabinet","living"),("old_bed_frame","bed_single","bedroom"),("wooden_bookshelf_worn","bookshelf","living"),
 ("chinese_screen_panels","room_divider","living"),("scandinavian_masonry_heater","fireplace","living"),("treasure_chest","storage_chest","living"),("spinning_wheel_01","decor","living"),
 ("Lantern_01","candle_holder","living"),("wooden_lantern_01","candle_holder","garden"),("lightbulb_led","lamp","living"),("lightbulb_01","lamp","living"),
 ("bronze_ray_statue","sculpture","living"),("bronze_shark_statue","sculpture","living"),("bronze_whale_statue","sculpture","living"),("gothic_statue","sculpture","living"),
 ("bull_head","wall_art","living"),("horse_head","sculpture","living"),("lion_head","wall_art","living"),("katana_stand_01","decor","living"),("kite_shield","wall_art","living"),
 ("decorative_book_set_01","books","living"),("postcard_set_01","decor","office"),("magnifying_glass_01","desk_accessory","office"),("round_spectacles","decor","bedroom"),
 ("pocket_watch","decor","bedroom"),("vintage_pocket_watch","decor","bedroom"),("digital_wrist_watch","decor","bedroom"),("vintage_lighter","decor","living"),
 ("vintage_binocular","decor","living"),("binoculars","decor","living"),("seadogs_compass","decor","office"),("vintage_microscope","decor","office"),("vintage_stapler","desk_accessory","office"),
 ("office_notepads","desk_accessory","office"),("clipboard","desk_accessory","office"),("Camera_01","electronics","living"),("vintage_video_camera","electronics","living"),
 ("boombox","speaker","living"),("cassette_player","electronics","living"),("portable_cassette_player","electronics","living"),("vintage_radio_transceiver","electronics","office"),
 ("gamepad","game_console","living"),("filmstrip_projector_8mm","electronics","living"),
 ("american_football","toy","kids"),("baseball_01","toy","kids"),("baseball_bat","toy","kids"),("football","toy","kids"),
 ("cardboard_box_01","storage_box","utility"),("plastic_crate_01","storage_box","utility"),("wooden_crate_01","storage_box","utility"),("wooden_crate_02","storage_box","utility"),
 ("wooden_bucket_01","basket","utility"),("wooden_bucket_02","basket","garden"),("metal_trash_can","bin","utility"),("dustpan","cleaning","utility"),("plastic_broom","cleaning","utility"),("wooden_broom","cleaning","utility"),
 ("rubber_boots","hallway_accessory","hallway"),("fishermans_hat","hallway_accessory","hallway"),("garden_gloves_01","garden_accessory","garden"),("trowel_01","garden_accessory","garden"),
 ("garden_sprinkler_01","garden_accessory","garden"),("seeding_tray_01","garden_accessory","garden"),("didelta_spinosa","plant","garden"),("leipoldtia_schultzei","plant","garden"),
 ("wine_barrel_01","decor","garden"),("modular_street_seating","garden_bench","garden"),("street_lamp_01","outdoor_lamp","garden"),("measuring_tape_01","tools","utility"),
 ("wheelchair_01","seating_misc","living"),("BarberShopChair_01","armchair","living"),("vintage_crutches_01","decor","hallway")]
BIG = {"bed_double","bed_single","cabinet","bookshelf","room_divider","fireplace","storage_chest","garden_bench","armchair"}
def dl(p):
    k, cat, room = p; res = "2k" if cat in BIG else "1k"; out = f"{ROOT}/staging/polyhaven3/{k}"
    if os.path.exists(f"{out}/{k}.gltf"): return k, "cached"
    try:
        files = json.loads(get(f"https://api.polyhaven.com/files/{k}"))
        g = (files["gltf"].get(res) or files["gltf"].get("1k") or next(iter(files["gltf"].values())))["gltf"]
        os.makedirs(out, exist_ok=True)
        for rel, inf in g.get("include", {}).items():
            q = f"{out}/{rel}"; os.makedirs(os.path.dirname(q), exist_ok=True); open(q, "wb").write(get(inf["url"]))
        open(f"{out}/{k}.gltf", "wb").write(get(g["url"])); return k, "ok"
    except Exception as e: return k, f"ERR {e}"
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(dl, PICK): print(*r, flush=True)
M = json.load(open(f"{ROOT}/tmp/ph_models_now.json"))
spec = []
for k, cat, room in PICK:
    if not os.path.exists(f"{ROOT}/staging/polyhaven3/{k}/{k}.gltf"): continue
    key = "ph_" + k.lower()
    spec.append(dict(key=key, src=f"{ROOT}/staging/polyhaven3/{k}/{k}.gltf", out=f"polyhaven/{cat}/{key}.glb", preview=f"previews/polyhaven/{key}.png",
                     max_tex=2048 if cat in BIG else 1024, category=cat, room=room, ph_id=k))
json.dump(spec, open(f"{ROOT}/tmp/spec_ph3.json", "w"), indent=1)
meta = json.load(open(f"{ROOT}/tmp/ph_meta.json"))
for k, *_ in PICK:
    v = M[k]; meta[k] = dict(name=v["name"], categories=v["categories"], tags=v.get("tags", []), authors=list(v.get("authors", {}).keys()), dimensions=v.get("dimensions"))
json.dump(meta, open(f"{ROOT}/tmp/ph_meta.json", "w"), indent=1)
print("SPEC", len(spec))
