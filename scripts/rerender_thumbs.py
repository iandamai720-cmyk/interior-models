"""Re-render a thumbnail from the exact published GLB of each asset.
blender -b --python scripts/rerender_thumbs.py -- <spec.json> <result.json> <i> <n>
spec: list of {id, file, thumb}. Output JPEG 320px named <id>.jpg next to the model.
World: camera rays see flat light grey; reflection/refraction rays see a sky gradient so mirrors/glass stay visible."""
import bpy, json, math, os, sys, hashlib
from mathutils import Vector
ROOT = "/workspace/interior-lib"
a = sys.argv[sys.argv.index("--") + 1:]
SPEC = json.load(open(a[0])); RESP = a[1]; si, sn = int(a[2]), int(a[3])
RES = json.load(open(RESP)) if os.path.exists(RESP) else {}
for n, s in enumerate(SPEC):
    if n % sn != si or s["id"] in RES: continue
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
        g = f"{ROOT}/{s['file']}"
        bpy.ops.import_scene.gltf(filepath=g)
        obs = [o for o in sc.objects if o.type == "MESH"]
        if not obs: RES[s["id"]] = dict(error="nomesh"); continue
        pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
        mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
        size = mx - mn; ctr = (mn + mx) / 2; r = max(size.length / 2, 0.01)
        tris = sum(len(p.vertices) - 2 for o in obs for p in o.data.polygons)
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
        cam.data.type = "ORTHO"; cam.data.ortho_scale = r * 2.15; cam.data.clip_end = 1000; cam.data.clip_start = 0.001
        dv = Vector((-0.55, -1.4, 0.75)).normalized(); cam.location = ctr + dv * (r * 6 + 3)
        cam.rotation_euler = (-dv).to_track_quat("-Z", "Y").to_euler(); sc.camera = cam
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
        sun.rotation_euler = (math.radians(50), 0, math.radians(-30)); sc.collection.objects.link(sun)
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; nt = w.node_tree; N = nt.nodes
        bg = N["Background"]; bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1); bg.inputs[1].default_value = 0.9
        # sky gradient for non-camera rays
        tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); ramp = N.new("ShaderNodeValToRGB")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs[1].default_value = -1; mr.inputs[2].default_value = 1
        nt.links.new(sep.outputs[2], mr.inputs[0]); nt.links.new(mr.outputs[0], ramp.inputs[0])
        ramp.color_ramp.elements[0].color = (0.08, 0.08, 0.09, 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[1].position = 0.62
        bg2 = N.new("ShaderNodeBackground"); nt.links.new(ramp.outputs[0], bg2.inputs[0]); bg2.inputs[1].default_value = 1.0
        lp = N.new("ShaderNodeLightPath"); mix = N.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0]); nt.links.new(bg2.outputs[0], mix.inputs[1]); nt.links.new(bg.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], N["World Output"].inputs[0])
        sc.render.engine = "CYCLES"; sc.cycles.samples = 10; sc.cycles.use_denoising = True; sc.cycles.threads = 1
        sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 8
        sc.render.resolution_x = sc.render.resolution_y = 320; sc.view_settings.view_transform = "AgX"
        sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 86
        out = f"{ROOT}/{s['thumb']}"; os.makedirs(os.path.dirname(out), exist_ok=True)
        sc.render.filepath = out; bpy.ops.render.render(write_still=True)
        RES[s["id"]] = dict(thumb=s["thumb"], file=s["file"], glb_sha256=hashlib.sha256(open(g, "rb").read()).hexdigest(),
                            thumb_sha256=hashlib.sha256(open(out, "rb").read()).hexdigest(), size=[round(v, 3) for v in size], tris=tris)
        print("N", s["id"], flush=True)
    except Exception as e:
        RES[s["id"]] = dict(error=repr(e)); print("FAIL", s["id"], repr(e), flush=True)
    json.dump(RES, open(RESP, "w"))
