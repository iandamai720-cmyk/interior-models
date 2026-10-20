import bpy, json, math
from mathutils import Vector
ROOT="/workspace/interior-lib"
for c in json.load(open(f"{ROOT}/tmp/fetched.json")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{ROOT}/{c['file']}")
    sc=bpy.context.scene
    obs=[o for o in sc.objects if o.type=='MESH']
    if c['key']=="kitchen_wall_cabinet":
        for o in obs:
            if o.parent is None: o.rotation_mode='XYZ'; o.rotation_euler.x+=math.radians(90)
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(b) for o in obs for b in o.bound_box]
    mn=Vector([min(p[i] for p in pts) for i in range(3)]); mx=Vector([max(p[i] for p in pts) for i in range(3)])
    ctr=(mn+mx)/2; r=(mx-mn).length/2
    cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); sc.collection.objects.link(cam)
    cam.data.type='ORTHO'; cam.data.ortho_scale=r*2.1
    d=Vector((0.8,-1.4,0.9)).normalized(); cam.location=ctr+d*(r*6+5); cam.data.clip_end=1000
    cam.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
    sun=bpy.data.objects.new("s",bpy.data.lights.new("s",'SUN')); sun.data.energy=3; sun.rotation_euler=(0.7,0.2,0.6); sc.collection.objects.link(sun)
    w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.94,0.94,0.94,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
    sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.cycles.use_denoising=True
    sc.render.resolution_x=sc.render.resolution_y=480; sc.view_settings.view_transform='AgX'
    sc.render.filepath=f"{ROOT}/previews/furniture/{c['key']}.png"; bpy.ops.render.render(write_still=True)
    print("T",c['key'])
