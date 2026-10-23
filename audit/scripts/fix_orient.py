import bpy,json,sys,math,shutil,os
from mathutils import Matrix,Vector
a=sys.argv[sys.argv.index('--')+1:]; S=json.load(open(a[0])); R={}
for s in S:
    f='/workspace/interior-lib/'+s['file']
    bk='/workspace/audit/glb_backup/'+s['id']+'.glb'
    if not os.path.exists(bk): shutil.copy2(f,bk)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=bk)
    obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    M=Matrix.Rotation(math.radians(float(a[1])),4,'X')
    for o in obs: o.matrix_world=M@o.matrix_world
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(c) for o in obs for c in o.bound_box]
    mn=Vector([min(p[i] for p in pts) for i in range(3)]); mx=Vector([max(p[i] for p in pts) for i in range(3)])
    T=Matrix.Translation(Vector((-(mn.x+mx.x)/2,-(mn.y+mx.y)/2,-mn.z)))
    for o in obs: o.matrix_world=T@o.matrix_world
    bpy.ops.object.select_all(action='SELECT')
    for o in bpy.context.selected_objects: 
        if o.type=='MESH': bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    tmp=f+'.tmp.glb'
    bpy.ops.export_scene.gltf(filepath=tmp,export_format='GLB',use_selection=False,export_image_format='AUTO',export_animations=False,export_lights=False,export_cameras=False)
    os.replace(tmp,f)
    sz=mx-mn; R[s['id']]=[round(sz.x,3),round(sz.y,3),round(sz.z,3)]
    print('FIX',s['id'],R[s['id']],flush=True)
json.dump(R,open(a[2],'w'))
