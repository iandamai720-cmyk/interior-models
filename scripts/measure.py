import bpy, json, sys, os
from mathutils import Vector
ROOT="/workspace/interior-lib"
cat=json.load(open(f"{ROOT}/tmp/fetched.json"))
res={}
for c in cat:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f"{ROOT}/{c['file']}")
    mn=Vector((1e9,)*3); mx=Vector((-1e9,)*3); tris=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH': continue
        for v in o.bound_box:
            w=o.matrix_world@Vector(v); mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
        tris+=sum(len(p.vertices)-2 for p in o.data.polygons)
    res[c['key']]=dict(min=list(mn),max=list(mx),size=list(mx-mn),tris=tris)
    print("M",c['key'],[round(x,3) for x in mx-mn],[round(x,3) for x in mn],tris)
json.dump(res,open(f"{ROOT}/tmp/bbox.json","w"),indent=1)
