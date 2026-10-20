import objaverse, json
CATS = {"television_set":"tv","speaker_(stero_equipment)":"speaker","monitor_(computer_equipment) computer_monitor":"monitor","computer_keyboard":"keyboard",
 "mouse_(computer_equipment)":"mouse","laptop_computer":"laptop","router_(computer_equipment)":"router","refrigerator":"fridge","oven":"oven","stove":"stove",
 "microwave_oven":"microwave","dishwasher":"dishwasher","coffee_maker":"coffee_machine","kettle":"kettle","teakettle":"kettle","toaster":"toaster","toaster_oven":"toaster",
 "automatic_washer":"washing_machine","vacuum_cleaner":"vacuum","air_conditioner":"air_conditioner","fan":"fan","radiator":"radiator","heater":"heater",
 "toilet":"toilet","bathtub":"bathtub","sink":"sink","kitchen_sink":"kitchen_sink","faucet":"faucet","water_faucet":"faucet","shower_head":"shower","joystick":"console","table_lamp":"desk_lamp"}
lv = objaverse.load_lvis_annotations()
uids = sorted({u for k in CATS for u in lv[k]})
ann = objaverse.load_annotations(uids)
out = []
for k, c in CATS.items():
    for u in lv[k]:
        a = ann.get(u)
        if not a: continue
        th = sorted(a.get("thumbnails", {}).get("images", []), key=lambda i: -i.get("width", 0))
        th = [i for i in th if i.get("width", 0) <= 1100] or th
        out.append(dict(uid=u, lvis=k, cat=c, name=a["name"], likes=a.get("likeCount", 0), views=a.get("viewCount", 0), faces=a.get("faceCount"),
            verts=a.get("vertexCount"), textures=a.get("textureCount"), materials=a.get("materialCount"), license=a.get("license"),
            author=a.get("user", {}).get("displayName") or a.get("user", {}).get("username"), url=a.get("viewerUrl"),
            thumb=th[0]["url"] if th else None, animated=a.get("animationCount", 0), tags=[t["name"] for t in a.get("tags", [])]))
json.dump(out, open("/workspace/interior-lib/tmp/objaverse_cands.json", "w"), indent=1)
print(len(uids), len(out))
