"""Blender helper: build a Principled-BSDF material from an interior-models material set.
Usage inside Blender (Scripting tab):
    exec(open("load_material.py").read())
    mat = load_material("/path/to/materials/floor_wood/acg_woodfloor051", tile_m=2.0)   # local folder
    # or from the web catalog:  mat = load_material_from_catalog("material-acg-woodfloor051")
    obj.data.materials.append(mat)
Maps: <slug>_color.jpg (sRGB), _normal.jpg (OpenGL), _roughness.jpg, _ao.jpg, _metalness.jpg, _opacity.jpg (Non-Color).
Texture coordinates use Object space scaled by 1/tile_m, so one texture tile covers tile_m metres (no UVs needed)."""
import bpy, os, glob, json, urllib.request, tempfile
API = "https://iandamai720-cmyk.github.io/interior-models/api"
def load_material(folder, name=None, tile_m=2.0):
    slug = os.path.basename(folder.rstrip("/")); name = name or slug
    maps = {os.path.basename(p)[len(slug) + 1:-4]: p for p in glob.glob(os.path.join(folder, f"{slug}_*.jpg"))}
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N.get("Principled BSDF")
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / tile_m,) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def tex(k, nc=True):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(maps[k], check_existing=True)
        t.projection = "BOX"; t.projection_blend = 0.2
        if nc: t.image.colorspace_settings.name = "Non-Color"
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    if "color" in maps:
        c = tex("color", False)
        if "ao" in maps:
            mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = 0.6
            L.new(c.outputs["Color"], mix.inputs[6]); L.new(tex("ao").outputs["Color"], mix.inputs[7]); L.new(mix.outputs[2], bsdf.inputs["Base Color"])
        else: L.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    if "roughness" in maps: L.new(tex("roughness").outputs["Color"], bsdf.inputs["Roughness"])
    if "metalness" in maps: L.new(tex("metalness").outputs["Color"], bsdf.inputs["Metallic"])
    if "opacity" in maps: L.new(tex("opacity").outputs["Color"], bsdf.inputs["Alpha"])
    if "normal" in maps:
        nm = N.new("ShaderNodeNormalMap"); L.new(tex("normal").outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    m["catalog_folder"] = folder; m["tile_m"] = tile_m
    return m
def load_material_from_catalog(material_id, cache=None):
    rec = json.load(urllib.request.urlopen(f"{API}/materials/{material_id}.json"))
    d = os.path.join(cache or tempfile.gettempdir(), "interior-materials", rec["slug"]); os.makedirs(d, exist_ok=True)
    for k, u in rec["maps"].items():
        p = os.path.join(d, f"{rec['slug']}_{k}.jpg")
        if not os.path.exists(p): open(p, "wb").write(urllib.request.urlopen(u).read())
    m = load_material(d, rec["name"], rec.get("tile_m", 2.0)); m["catalog_id"] = material_id; return m
