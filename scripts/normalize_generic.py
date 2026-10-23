"""Generic normaliser used for the turn-4 expansion (IKEA PL, Poly Haven, Objaverse, Kenney...).
blender -b --python scripts/normalize_generic.py -- <spec.json> <result.json> [shard_index shard_count]
spec: list of {key, src, out, preview, [rx,ry,rz, scale_axis, target_m, max_tex, remove]}
Imports, flattens, joins, applies orientation fix, optional scale to target, origin bottom-centre,
decimates >150k tris, textures <= max_tex (default 2048), exports non-Draco GLB, renders thumbnail
from the exported file."""
import bpy, json, math, os, sys
from mathutils import Vector, Matrix
ROOT = "/workspace/interior-lib"
a = sys.argv[sys.argv.index("--") + 1:]
SPEC = json.load(open(a[0])); RESP = a[1]
si, sn = (int(a[2]), int(a[3])) if len(a) > 3 else (0, 1)
RES = json.load(open(RESP)) if os.path.exists(RESP) else {}
MAX_TRIS = 150000

def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])

for n, s in enumerate(SPEC):
    if n % sn != si: continue
    k = s["key"]
    if k in RES and os.path.exists(f"{ROOT}/{s['out']}") and not s.get("force"): continue
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        src = s["src"]
        if src.endswith(".gltf") or src.endswith(".glb"): bpy.ops.import_scene.gltf(filepath=src)
        elif src.endswith(".fbx"): bpy.ops.import_scene.fbx(filepath=src)
        elif src.endswith(".obj"): bpy.ops.wm.obj_import(filepath=src)
        sc.frame_set(0)
        for o in list(sc.objects): o.animation_data_clear()
        meshes = [o for o in sc.objects if o.type == "MESH"]
        for o in list(meshes):
            if any(w in o.name.lower() for w in s.get("remove", []) + ["shadow", "backdrop"]):
                bpy.data.objects.remove(o); meshes.remove(o)
        if not meshes: print("NOMESH", k); continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in meshes: o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.convert(target="MESH")
        meshes = [o for o in sc.objects if o.type == "MESH" and o.select_get()]
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
        for o in list(sc.objects):
            if o.type != "MESH": bpy.data.objects.remove(o)
        bpy.ops.object.select_all(action="SELECT")
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if len(meshes) > 1: bpy.ops.object.join()
        ob = bpy.context.view_layer.objects.active
        for mod in list(ob.modifiers): ob.modifiers.remove(mod)
        if ob.data.shape_keys: ob.shape_key_clear()
        M = Matrix.Rotation(math.radians(s.get("rz", 0)), 4, "Z") @ Matrix.Rotation(math.radians(s.get("ry", 0)), 4, "Y") @ Matrix.Rotation(math.radians(s.get("rx", 0)), 4, "X")
        ob.data.transform(M); ob.data.update(); bpy.context.view_layer.update()
        mn, mx = bbox([ob]); size = mx - mn
        f = 1.0
        if s.get("scale_axis") and s.get("target_m"):
            cur = {"x": size.x, "y": size.y, "z": size.z, "max": max(size)}[s["scale_axis"]]
            f = s["target_m"] / cur
        elif s.get("scale"): f = s["scale"]
        ob.data.transform(Matrix.Scale(f, 4)); ob.data.update(); bpy.context.view_layer.update()
        mn, mx = bbox([ob])
        ob.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
        ob.data.update(); bpy.context.view_layer.update()
        ob.name = ob.data.name = k
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        if tris > MAX_TRIS:
            d = ob.modifiers.new("dec", "DECIMATE"); d.ratio = MAX_TRIS / tris
            bpy.ops.object.modifier_apply(modifier="dec")
            tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        lim = s.get("max_tex", 2048)
        for im in bpy.data.images:
            if im.size[0] > lim or im.size[1] > lim:
                r = lim / max(im.size); im.scale(max(1, int(im.size[0] * r)), max(1, int(im.size[1] * r)))
        out = f"{ROOT}/{s['out']}"; os.makedirs(os.path.dirname(out), exist_ok=True)
        def export(fmt):
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format=fmt, export_animations=False,
                                      export_jpeg_quality=85, export_lights=False, export_cameras=False)
        export("AUTO")
        if os.path.getsize(out) > 6e6: export("JPEG")
        bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
        bpy.ops.import_scene.gltf(filepath=out)
        obs = [o for o in sc.objects if o.type == "MESH"]
        mn, mx = bbox(obs); size = mx - mn
        ctr = (mn + mx) / 2; r = max(size.length / 2, 0.01)
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
        cam.data.type = "ORTHO"; cam.data.ortho_scale = r * 2.15; cam.data.clip_end = 1000; cam.data.clip_start = 0.001
        dv = Vector((-0.55, -1.4, 0.75)).normalized(); cam.location = ctr + dv * (r * 6 + 3)
        cam.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler(); sc.camera = cam
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
        sun.rotation_euler = (math.radians(50), 0, math.radians(-30)); sc.collection.objects.link(sun)
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.92, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
        sc.render.engine = "CYCLES"; sc.cycles.samples = 12; sc.cycles.use_denoising = True; sc.cycles.threads = 3
        sc.render.resolution_x = sc.render.resolution_y = 360; sc.view_settings.view_transform = "AgX"
        sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"; sc.render.image_settings.compression = 90
        pv = f"{ROOT}/{s['preview']}"; os.makedirs(os.path.dirname(pv), exist_ok=True)
        sc.render.filepath = pv; bpy.ops.render.render(write_still=True)
        RES[k] = dict(size=[round(v, 3) for v in size], tris=tris, scale_factor=round(f, 5), bytes=os.path.getsize(out), file=s["out"], preview=s["preview"])
        print("N", k, RES[k]["size"], tris, RES[k]["bytes"] // 1024, "KB", flush=True)
        json.dump(RES, open(RESP, "w"), indent=1)
    except Exception as e:
        print("FAIL", k, repr(e), flush=True)
