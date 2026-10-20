"""Merge appliance spec + normalisation results into tmp/appl_records.json (used by build_layout + make_catalog)."""
import json
ROOT = "/workspace/interior-lib"
spec = {s["key"]: s for s in json.load(open(f"{ROOT}/tmp/appl_spec.json"))}
norm = json.load(open(f"{ROOT}/tmp/appl_norm.json"))
LIC = {"by": "CC BY 4.0", "by-sa": "CC BY-SA 4.0", "by-nc": "CC BY-NC 4.0", "by-nc-sa": "CC BY-NC-SA 4.0", "by-nd": "CC BY-ND 4.0", "cc0": "CC0 1.0"}
COL = {"fridge_side_by_side": ["stainless steel"], "washing_machine": ["white"], "dryer": ["white"], "microwave_white": ["white"], "microwave_black": ["black"],
 "oven_builtin": ["stainless steel"], "dishwasher": ["white"], "extractor_hood_steel": ["stainless steel"], "extractor_hood_black": ["black"], "kitchen_sink_steel": ["stainless steel"],
 "kitchen_tap": ["chrome"], "coffee_machine_drip": ["black", "stainless steel"], "espresso_machine": ["cream"], "electric_kettle": ["black"], "toaster": ["stainless steel"],
 "tv_qled_65": ["black"], "tv_sony_55": ["black"], "soundbar": ["black"], "speakers_tower": ["walnut"], "speakers_bookshelf": ["grey", "walnut"], "smart_speaker_home": ["white", "grey"],
 "smart_speaker_dot": ["grey"], "console_ps5": ["white", "black"], "console_xbox": ["black"], "gamepad": ["white"], "pc_tower": ["black"], "monitor_27": ["black"], "keyboard": ["black"],
 "mouse": ["black"], "laptop": ["black"], "router": ["black"], "stick_vacuum": ["gold", "black"], "robot_vacuum": ["grey"], "air_conditioner": ["white"], "standing_fan": ["white"],
 "radiator_column": ["white"], "towel_radiator": ["chrome"], "toilet": ["white"], "bathtub_freestanding": ["white"], "shower_cabin": ["glass", "grey"], "bathroom_sink": ["white"],
 "bathroom_tap": ["chrome"], "ph_ceiling_fan": ["black"], "ph_desk_lamp_arm_01": ["orange"], "ph_modern_ceiling_lamp_01": ["white"], "ph_gaming_console": ["black"]}
recs = []
for k, n in norm.items():
    s = spec[k]; ik = s.get("ikea") or {}
    lic = LIC.get(s["license"], s["license"])
    name = s["name"] if s["source"] != "IKEA" else (ik.get("name") or s["name"])
    recs.append(dict(key=k, name=name, full_name=s["name"], category=s["category"], room=s["room"], style=s["style"],
        colour=", ".join(COL.get(k, [ik.get("colour")] if ik.get("colour") else [])) or None, colours=COL.get(k) or ik.get("colours") or [],
        material=ik.get("material"), width=ik.get("width"), depth=ik.get("depth"), height=ik.get("height"), dims_text=ik.get("dims_text"),
        file=n["file"], preview=n["preview"], size_m=n["size"], tris=n["tris"], size_bytes=n["bytes"], mount=n.get("mount_offsets") or {},
        source=s["source"], source_url=s["source_url"], author=s["author"], license=lic,
        license_note=("Personal/demo use only" if s["source"] == "IKEA" else ("Non-commercial only" if "NC" in lic else ("Attribution required" if "BY" in lic else "Public domain"))),
        article_number=s.get("article_number"), objaverse_uid=s.get("uid"), glb_url=ik.get("glb_url"), image=ik.get("image") if ik else None))
json.dump(recs, open(f"{ROOT}/tmp/appl_records.json", "w"), indent=1)
print(len(recs))
