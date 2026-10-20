"""Normalise appliance/electronics models: join, fix orientation (front -Y), real-world scale (m),
origin bottom-centre, decimate >150k tris, textures <=2K, export GLB <=25 MB, render thumbnail.
blender -b --python scripts/normalize_appliances.py -- [key ...]"""
import bpy, json, math, os, sys
from mathutils import Vector, Matrix
ROOT = "/workspace/interior-lib"
SPEC = json.load(open(f"{ROOT}/tmp/appl_spec.json"))
FIX = json.load(open(f"{ROOT}/scripts/appliance_fixes.json")) if os.path.exists(f"{ROOT}/scripts/appliance_fixes.json") else {}
only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = f"{ROOT}/appliances"; TH = f"{ROOT}/previews/appliances"; os.makedirs(OUT, exist_ok=True); os.makedirs(TH, exist_ok=True)
res_path = f"{ROOT}/tmp/appl_norm.json"
RES = json.load(open(res_path)) if os.path.exists(res_path) else {}
MAX_TRIS = 150000

def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

for s in SPEC:
    k = s["key"]
    if only and k not in only: continue
    fx = FIX.get(k, {})
    if fx.get("drop"):
        RES.pop(k, None); print("DROP", k)
        if os.path.exists(f"{OUT}/{k}.glb"): os.remove(f"{OUT}/{k}.glb")
        if os.path.exists(f"{TH}/{k}.png"): os.remove(f"{TH}/{k}.png")
        json.dump(RES, open(res_path, "w"), indent=1); continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.gltf(filepath=s["src"])
    except Exception as e:
        print("IMPORT FAIL", k, e); continue
    sc = bpy.context.scene
    bpy.context.scene.frame_set(0)
    for o in list(sc.objects): o.animation_data_clear()
    meshes = [o for o in sc.objects if o.type == "MESH"]
    # drop helper meshes named like ground/floor/backdrop/shadow
    for o in list(meshes):
        if o.name in fx.get("remove_exact", []) or any(w in o.name.lower() for w in fx.get("remove", []) + ["shadow", "backdrop", "ground"]):
            bpy.data.objects.remove(o); meshes.remove(o)
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.convert(target="MESH")          # applies armature/shape modifiers
    meshes = [o for o in sc.objects if o.type == "MESH" and o.select_get()]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    for o in list(sc.objects):
        if o.type != "MESH": bpy.data.objects.remove(o)
    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(meshes) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    for mod in list(ob.modifiers): ob.modifiers.remove(mod)
    ob.shape_key_clear() if ob.data.shape_keys else None
    # orientation fixes: rx (tip upright), rz (turn so front faces -Y)
    M = Matrix.Rotation(math.radians(fx.get("rz", 0)), 4, "Z") @ Matrix.Rotation(math.radians(fx.get("ry", 0)), 4, "Y") @ Matrix.Rotation(math.radians(fx.get("rx", 0)), 4, "X")
    ob.data.transform(M)
    ob.data.update(); bpy.context.view_layer.update()
    mn, mx = bbox([ob]); size = mx - mn
    ax = fx.get("scale_axis", s["scale_axis"]); tgt = fx.get("target_m", s["target_m"])
    f = 1.0
    if ax and tgt:
        cur = {"x": size.x, "y": size.y, "z": size.z, "max": max(size)}[ax]
        f = tgt / cur
    ob.data.transform(Matrix.Scale(f, 4))
    ob.data.update(); bpy.context.view_layer.update()
    mn, mx = bbox([ob])
    ob.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    ob.data.update(); bpy.context.view_layer.update()
    ob.name = ob.data.name = k
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if tris > MAX_TRIS:
        d = ob.modifiers.new("dec", "DECIMATE"); d.ratio = MAX_TRIS / tris
        bpy.ops.object.modifier_apply(modifier="dec")
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    small = max(mx - mn) < 0.5
    lim = 1024 if small else 2048
    for im in bpy.data.images:
        if im.size[0] > lim or im.size[1] > lim:
            r = lim / max(im.size); im.scale(max(1, int(im.size[0] * r)), max(1, int(im.size[1] * r)))
    out = f"{OUT}/{k}.glb"
    def export(fmt):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format=fmt, export_animations=False,
                                  export_jpeg_quality=85, export_lights=False, export_cameras=False)
    export("AUTO")
    if os.path.getsize(out) > 8e6: export("JPEG")
    # re-import the exported file so the thumbnail shows exactly what ships
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=out)
    obs = [o for o in sc.objects if o.type == "MESH"]
    mn, mx = bbox(obs); size = mx - mn
    # thumbnail from front-left (camera on -Y side): verifies front faces -Y
    ctr = (mn + mx) / 2; r = size.length / 2
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = r * 2.15; cam.data.clip_end = 1000
    dv = Vector((-0.55, -1.4, 0.75)).normalized(); cam.location = ctr + dv * (r * 6 + 3)
    cam.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler(); sc.camera = cam
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30)); sc.collection.objects.link(sun)
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.92, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    sc.render.engine = "CYCLES"; sc.cycles.samples = 16; sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 480; sc.view_settings.view_transform = "AgX"
    sc.render.filepath = f"{TH}/{k}.png"; bpy.ops.render.render(write_still=True)
    RES[k] = dict(size=[round(v, 3) for v in size], tris=tris, scale_factor=f, bytes=os.path.getsize(out),
                  textures=len([i for i in bpy.data.images if i.size[0] > 0]), mount_offsets=fx.get("mount", {}), file=os.path.relpath(out, ROOT), preview=f"previews/appliances/{k}.png")
    print("N", k, RES[k]["size"], tris, RES[k]["bytes"] // 1024, "KB")
    json.dump(RES, open(res_path, "w"), indent=1)
