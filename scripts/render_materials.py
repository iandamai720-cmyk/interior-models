"""blender -b --python scripts/render_materials.py -- tmp/materials.json  -> previews/materials/<slug>.png (rounded cube + sphere, 360px)"""
import bpy, sys, json, os, math
ROOT = "/workspace/interior-lib"; exec(open(f"{ROOT}/blender/load_material.py").read())
M = json.load(open(sys.argv[sys.argv.index("--") + 1]))
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = 24; sc.cycles.use_denoising = True; sc.render.resolution_x = sc.render.resolution_y = 360
sc.render.film_transparent = False; sc.view_settings.view_transform = "AgX"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.82, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
bpy.ops.mesh.primitive_plane_add(size=1.6, location=(0, 0, 0)); pl = bpy.context.object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(0, 0, 0.42), segments=64, ring_count=32); sp = bpy.context.object; bpy.ops.object.shade_smooth()
bpy.ops.object.light_add(type="AREA", location=(1.5, -1.5, 2.5)); L = bpy.context.object; L.data.energy = 250; L.data.size = 2; L.rotation_euler = (math.radians(40), 0, math.radians(45))
bpy.ops.object.camera_add(location=(1.55, -1.55, 1.25)); cam = bpy.context.object; sc.camera = cam
c = cam.constraints.new("TRACK_TO"); c.target = sp; cam.data.lens = 50
os.makedirs(f"{ROOT}/previews/materials", exist_ok=True)
for r in M:
    out = f"{ROOT}/previews/materials/{r['slug']}.png"
    if os.path.exists(out) or "color" not in r.get("maps", []): continue
    tile = 1.0 if r["cat"] in ("fabric", "leather", "floor_carpet") else 1.6
    m = load_material(r["dir"], tile_m=tile)
    for o in (pl, sp): o.data.materials.clear(); o.data.materials.append(m)
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    bpy.data.materials.remove(m)
    for im in list(bpy.data.images):
        if im.users == 0: bpy.data.images.remove(im)
print("RENDER DONE")
