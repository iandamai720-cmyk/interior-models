"""Procedural apartment/house builder for Blender (headless).
Usage: blender -b --python build_layout.py -- <apartment|house> <scandi|dark>
Coordinates: metres, X east, Y north, interior faces of exterior walls at 0..W / 0..D.
IKEA GLBs (after glTF import): footprint centred at origin, z=0 floor, BACK faces +Y, FRONT faces -Y."""
import bpy, bmesh, json, math, sys, os
from mathutils import Vector, Matrix
ROOT = "/workspace/interior-lib"
argv = sys.argv[sys.argv.index("--") + 1:]
LAYOUT, STYLE = argv[0], argv[1]
CAT = {c["key"]: c for c in json.load(open(f"{ROOT}/tmp/fetched.json"))}
CAT.update({c["key"]: c for c in json.load(open(f"{ROOT}/tmp/appl_records.json"))})   # appliances & electronics
H = 2.7          # wall height
TE, TI = 0.25, 0.12   # exterior / interior wall thickness
hi = TI / 2

PAL = {
 "scandi": dict(wall=(0.93, 0.92, 0.89), wall_ext=(0.85, 0.84, 0.82), wood=(0.72, 0.56, 0.38), tile=(0.86, 0.86, 0.84), bath_tile=(0.80, 0.84, 0.86), world=(0.95, 0.97, 1.0)),
 "dark":   dict(wall=(0.20, 0.21, 0.22), wall_ext=(0.15, 0.15, 0.16), wood=(0.25, 0.16, 0.10), tile=(0.30, 0.30, 0.31), bath_tile=(0.12, 0.12, 0.13), world=(0.85, 0.88, 0.95)),
}[STYLE]

# ---------------------------------------------------------------- materials
def mat(name, col, rough=0.6, metal=0.0, alpha=1.0, transmission=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
        b.inputs["IOR"].default_value = 1.45
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND"
    m.diffuse_color = (*col, alpha)
    return m

def floor_mat(kind):
    col = {"wood": PAL["wood"], "tile": PAL["tile"], "bath": PAL["bath_tile"]}[kind]
    name = f"Floor_{kind}_{STYLE}"
    m = bpy.data.materials.get(name)
    if m: return m
    m = mat(name, col, rough=0.45 if kind == "wood" else 0.3)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    c1 = Vector(col); 
    br.inputs["Color1"].default_value = (*c1, 1)
    br.inputs["Color2"].default_value = (*(c1 * 0.85), 1)
    br.inputs["Mortar"].default_value = (*(c1 * 0.7), 1)
    if kind == "wood":
        br.inputs["Scale"].default_value = 1.0; br.inputs["Brick Width"].default_value = 1.2
        br.inputs["Row Height"].default_value = 0.18; br.inputs["Mortar Size"].default_value = 0.003
    else:
        br.inputs["Scale"].default_value = 1.0; br.inputs["Brick Width"].default_value = 0.3
        br.inputs["Row Height"].default_value = 0.3; br.inputs["Mortar Size"].default_value = 0.004; br.offset = 0.0
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    return m

M_WALL = mat(f"Wall_{STYLE}", PAL["wall"], 0.8)
M_WALL_TOP = mat("WallCut", (0.1, 0.1, 0.1), 0.9)
M_GLASS = mat("Glass", (0.8, 0.9, 1.0), 0.02, alpha=0.25, transmission=1.0)
M_FRAME = mat("Frame", (0.95, 0.95, 0.95) if STYLE == "scandi" else (0.08, 0.08, 0.08), 0.4)
M_DOOR = mat("DoorLeaf", (0.9, 0.88, 0.84) if STYLE == "scandi" else (0.12, 0.11, 0.10), 0.5)
M_PORC = mat("Porcelain", (0.97, 0.97, 0.97), 0.15)
M_TOP = mat("Worktop", (0.75, 0.62, 0.45) if STYLE == "scandi" else (0.10, 0.10, 0.10), 0.35)
M_CHROME = mat("Chrome", (0.9, 0.9, 0.9), 0.15, metal=1.0)

# ---------------------------------------------------------------- collections
def coll(name):
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c
C_SHELL, C_FURN = coll("Shell"), coll("Furniture")
C_LIB = coll("_IKEA_library"); C_LIB.hide_render = True
bpy.context.view_layer.layer_collection.children["_IKEA_library"].exclude = True

def box(name, x0, y0, z0, x1, y1, z1, m, c=None, props=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
    bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); (c or C_SHELL).objects.link(o)
    for k, v in (props or {}).items(): o[k] = v
    return o

# ---------------------------------------------------------------- walls
def wall(name, a, b, t, ops=(), axis=None):
    """Axis-aligned wall centreline a->b (x,y). ops: (kind, centre_along, width). kind door|window|open|hiwin."""
    (x1, y1), (x2, y2) = a, b
    horiz = abs(y1 - y2) < 1e-6
    lo, hi_ = (min(x1, x2), max(x1, x2)) if horiz else (min(y1, y2), max(y1, y2))
    c = y1 if horiz else x1
    def seg(s0, s1, z0, z1, m=M_WALL, nm=name):
        if s1 - s0 < 1e-4 or z1 - z0 < 1e-4: return
        if horiz: box(nm, s0, c - t / 2, z0, s1, c + t / 2, z1, m)
        else:     box(nm, c - t / 2, s0, z0, c + t / 2, s1, z1, m)
    cur = lo
    for kind, cen, w in sorted(ops, key=lambda o: o[1]):
        s0, s1 = cen - w / 2, cen + w / 2
        seg(cur, s0, 0, H)
        if kind == "door":   seg(s0, s1, 2.1, H); frame(horiz, c, t, s0, s1, 0, 2.1, door=True)
        elif kind == "entry": seg(s0, s1, 2.1, H); frame(horiz, c, t, s0, s1, 0, 2.1, door=True); leaf(horiz, c, t, s0, s1)
        elif kind == "window": seg(s0, s1, 0, 0.9); seg(s0, s1, 2.2, H); frame(horiz, c, t, s0, s1, 0.9, 2.2)
        elif kind == "hiwin":  seg(s0, s1, 0, 1.5); seg(s0, s1, 2.1, H); frame(horiz, c, t, s0, s1, 1.5, 2.1)
        elif kind == "open":   seg(s0, s1, 2.4, H)
        cur = s1
    seg(cur, hi_, 0, H)

def frame(horiz, c, t, s0, s1, z0, z1, door=False):
    f = 0.05
    def b(a0, a1, zz0, zz1, m, th):
        if horiz: box("Frame", a0, c - th / 2, zz0, a1, c + th / 2, zz1, m)
        else:     box("Frame", c - th / 2, a0, zz0, c + th / 2, a1, zz1, m)
    b(s0, s0 + f, z0, z1, M_FRAME, t + 0.02); b(s1 - f, s1, z0, z1, M_FRAME, t + 0.02)
    b(s0, s1, z1 - f, z1, M_FRAME, t + 0.02)
    if not door:
        b(s0, s1, z0, z0 + f, M_FRAME, t + 0.04)
        b(s0 + f, s1 - f, z0 + f, z1 - f, M_GLASS, 0.02)
        b((s0 + s1) / 2 - 0.02, (s0 + s1) / 2 + 0.02, z0 + f, z1 - f, M_FRAME, 0.06)

def leaf(horiz, c, t, s0, s1):
    if horiz: box("EntranceDoor", s0 + 0.05, c - 0.02, 0, s1 - 0.05, c + 0.02, 2.05, M_DOOR)
    else:     box("EntranceDoor", c - 0.02, s0 + 0.05, 0, c + 0.02, s1 - 0.05, 2.05, M_DOOR)

def exterior(W, D, south=(), north=(), west=(), east=()):
    e = TE / 2
    wall("Ext_S", (-TE, -e), (W + TE, -e), TE, south)
    wall("Ext_N", (-TE, D + e), (W + TE, D + e), TE, north)
    wall("Ext_W", (-e, 0), (-e, D), TE, west)
    wall("Ext_E", (W + e, 0), (W + e, D), TE, east)
    box("Slab", -TE, -TE, -0.2, W + TE, D + TE, -0.01, mat("Slab", (0.5, 0.5, 0.5)))

ROOMS = []
def room(name, kind, x0, y0, x1, y1, floor="wood"):
    o = box(f"Floor_{name}", x0, y0, -0.01, x1, y1, 0.0, floor_mat(floor), props={"room": name, "room_type": kind, "area_m2": round((x1 - x0) * (y1 - y0), 2)})
    ROOMS.append(dict(name=name, type=kind, area_m2=round((x1 - x0) * (y1 - y0), 2), bounds=[x0, y0, x1, y1]))

# ---------------------------------------------------------------- furniture
LIB = {}
def asset(key):
    if key in LIB: return LIB[key]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{ROOT}/{CAT[key]['file']}")
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    others = [o.name for o in new if o.type != "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(meshes) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    for n in others:
        if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
    if key == "kitchen_wall_cabinet":       # model lies on its back (open side +Z) -> stand it up, front -Y
        ob.data.transform(Matrix.Rotation(math.radians(90), 4, "X"))
    ntri = sum(len(pl.vertices) - 2 for pl in ob.data.polygons)
    if ntri > 20000:                        # layout copies only need preview-grade geometry
        md = ob.modifiers.new("dec", "DECIMATE"); md.ratio = 20000 / ntri
        bpy.ops.object.modifier_apply(modifier=md.name)
    vs = [v.co for v in ob.data.vertices]
    mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    ob.data.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    ob.data.name = ob.name = f"IKEA_{key}"
    for c in ob.users_collection: c.objects.unlink(ob)
    C_LIB.objects.link(ob)
    if CAT[key].get("article_number"): ob["ikea_article"] = CAT[key]["article_number"]
    ob["asset_name"] = CAT[key]["full_name"] or key
    LIB[key] = (ob, mx - mn)
    return LIB[key]

PLACED = []
def put(key, x, y, rot=0.0, z=0.0, room=None, scale=None, ceiling=False):
    src, size = asset(key)
    o = src.copy(); o.name = f"{key}.{len(PLACED):02d}"
    o.rotation_mode = "XYZ"
    o.location = (x, y, z); o.rotation_euler = (0, 0, math.radians(rot))
    if scale: o.scale = scale
    C_FURN.objects.link(o)
    if CAT[key].get("article_number"): o["ikea_article"] = CAT[key]["article_number"]
    o["room"] = room or ""; o["asset_key"] = key
    if ceiling: o["ceiling"] = 1
    PLACED.append(dict(key=key, article_number=CAT[key].get("article_number"), room=room, x=round(x, 3), y=round(y, 3), z=round(z, 3), rot_deg=round(rot, 1),
                       **({"scale": list(scale)} if scale else {})))
    if CAT[key]["category"].startswith("bed"): mattress(o, src, size)
    return o

M_BED = None
def mattress(o, src, size):
    """IKEA bed-frame models ship without mattress: add a mattress + duvet resting on the slats."""
    global M_BED
    vs = [v.co for v in src.data.vertices if abs(v.co.x) < size.x * 0.2 and abs(v.co.y) < size.y * 0.2]
    zs = sorted(v.z for v in vs if v.z < 0.6) if vs else [0.3]
    top = zs[-1] if zs else 0.3
    wi, le = size.x - 0.12, min(size.y - 0.14, 2.0)
    M_BED = M_BED or mat("Bedding", (0.93, 0.92, 0.9) if STYLE == "scandi" else (0.35, 0.36, 0.38), 0.9)
    m = box(o.name + "_mattress", -wi / 2, -le / 2 - 0.02, top, wi / 2, le / 2 - 0.02, top + 0.18, mat("Mattress", (0.97, 0.97, 0.97), 0.9), C_FURN)
    d = box(o.name + "_duvet", -wi / 2 - 0.01, -le / 2 - 0.04, top + 0.18, wi / 2 + 0.01, le * 0.25, top + 0.24, M_BED, C_FURN)
    pw = box(o.name + "_pillows", -wi / 2 + 0.06, le * 0.28, top + 0.18, wi / 2 - 0.06, le / 2 - 0.08, top + 0.30, mat("Pillow", (1, 1, 1), 0.9), C_FURN)
    for p in (m, d, pw): p.parent = o

def against(key, side, face, along, room=None, z=0.0, gap=0.01, scale=None):
    """Back of object against a wall face. side=N/S/E/W (which wall), face=coordinate of wall face."""
    _, s = asset(key); d = s.y * (scale[1] if scale else 1) / 2 + gap
    if side == "N": return put(key, along, face - d, 0, z, room, scale)
    if side == "S": return put(key, along, face + d, 180, z, room, scale)
    if side == "W": return put(key, face + d, along, 90, z, room, scale)
    if side == "E": return put(key, face - d, along, -90, z, room, scale)

def depth(key): return asset(key)[1].y
def height(key): return asset(key)[1].z

def facing(key, x, y, tx, ty, room=None):
    return put(key, x, y, math.degrees(math.atan2(tx - x, -(ty - y))), 0, room)

def pendant(key, x, y, room=None):
    _, s = asset(key); return put(key, x, y, 0, H - s.z, room, ceiling=True)

# procedural placeholders for items IKEA does not sell
def toilet(x, y, side, room):
    o = []
    rot = {"N": 0, "S": 180, "W": 90, "E": -90}[side]
    parts = [box("Toilet_bowl", -0.18, -0.35, 0, 0.18, 0.05, 0.42, M_PORC, C_FURN), box("Toilet_tank", -0.19, 0.05, 0.3, 0.19, 0.22, 0.8, M_PORC, C_FURN)]
    e = bpy.data.objects.new("Placeholder_toilet", None); C_FURN.objects.link(e)
    for p in parts: p.parent = e
    e.location = (x, y, 0); e.rotation_euler = (0, 0, math.radians(rot)); e["placeholder"] = "toilet"
    PLACED.append(dict(key="placeholder_toilet", room=room, x=x, y=y, rot_deg=rot))
def shower(x0, y0, x1, y1, room):
    box("Shower_tray", x0, y0, 0, x1, y1, 0.06, M_PORC, C_FURN, {"placeholder": "shower"})
    box("Shower_glass", x0, y0, 0.06, x1, y0 + 0.01, 2.0, M_GLASS, C_FURN)
    box("Shower_head", (x0 + x1) / 2 - 0.1, y1 - 0.2, 1.95, (x0 + x1) / 2 + 0.1, y1 - 0.05, 1.97, M_CHROME, C_FURN)
    PLACED.append(dict(key="placeholder_shower", room=room, bounds=[x0, y0, x1, y1]))
def bathtub(x0, y0, x1, y1, room):
    box("Bathtub", x0, y0, 0, x1, y1, 0.55, M_PORC, C_FURN, {"placeholder": "bathtub"})
    box("Bathtub_inner", x0 + 0.07, y0 + 0.07, 0.15, x1 - 0.07, y1 - 0.07, 0.56, mat("Water", (0.75, 0.85, 0.9), 0.05), C_FURN)
    PLACED.append(dict(key="placeholder_bathtub", room=room, bounds=[x0, y0, x1, y1]))
def worktop(x0, y0, x1, y1, z=0.8, room=None):
    box("Worktop", x0, y0, z, x1, y1, z + 0.035, M_TOP, C_FURN, {"placeholder": "worktop"})
    PLACED.append(dict(key="placeholder_worktop", room=room, bounds=[x0, y0, x1, y1]))
def bed_cover(o, key):
    pass

S = (lambda scandi, dark: scandi if STYLE == "scandi" else dark)

# ================================================================= APARTMENT ~50 m2
def apartment():
    W, D = 8.0, 6.25
    exterior(W, D,
        south=[("window", 1.3, 1.4), ("window", 3.7, 1.4), ("window", 6.6, 1.4)],
        north=[("entry", 2.9, 1.0)],
        west=[("window", 2.0, 1.2)],
        east=[("hiwin", 5.3, 0.6)])
    # interior walls
    wall("Int_living_hall", (2.0, 4.2), (5.0, 4.2), TI, [("door", 4.3, 0.9)])
    wall("Int_bed_N", (5.0, 4.2), (8.0, 4.2), TI, [("door", 5.45, 0.8)])
    wall("Int_living_bed", (5.0, 0), (5.0, 4.2), TI)
    wall("Int_kitch_hall", (2.0, 4.2), (2.0, D), TI)
    wall("Int_hall_bath", (5.9, 4.2), (5.9, D), TI, [("door", 5.4, 0.8)])
    room("Living_kitchenette", "living_kitchen", 0, 0, 5.0, 4.2, "wood")
    room("Kitchenette", "kitchen", 0, 4.2, 2.0, D, "tile")
    room("Hallway", "hallway", 2.0, 4.2, 5.9, D, "wood")
    room("Bedroom", "bedroom", 5.0, 0, 8.0, 4.2, "wood")
    room("Bathroom", "bathroom", 5.9, 4.2, 8.0, D, "bath")
    if not FURNISH: return
    L = "Living_kitchenette"
    # living zone
    put(S("rug_large", "rug_large"), 2.45, 1.6, 90, room=L)
    against(S("sofa_kivik", "sofa_dark"), "W", 0.55, 1.6, L)
    ct = S("coffee_table_lack", "coffee_table_listerby")
    put(ct, 2.45, 1.6, 90 if STYLE == "dark" else 0, room=L)
    put("gamepad", 2.35, 1.45, 25, height(ct), L)
    facing(S("armchair_light", "armchair_strandmon"), 3.8, 0.6, 2.45, 1.6, L)
    put(S("floor_lamp_hoglunda", "floor_lamp_hektar"), 0.35, 0.35, 45, room=L)
    against(S("bookcase_billy", "shelf_kallax"), "W", 0, 3.6, L)
    put("plant_pot", 4.6, 3.8, room=L)
    # media wall: TV bench on the bedroom wall, TV + soundbar + console + smart speaker
    bench = S("tv_bench_besta", "ikea_tv_bench_wall"); face = 5.0 - hi
    against(bench, "E", face, 1.7, L); bz = height(bench); bx = face - depth(bench) / 2 - 0.01
    against(S("tv_qled_65", "tv_sony_55"), "E", face, 1.7, L, z=bz)
    put("soundbar", bx - 0.13, 1.7, -90, bz, L)
    put(S("console_ps5", "console_xbox"), bx, 2.52, -90, bz, L)
    put("smart_speaker_home", bx, 0.9, -90, bz, L)
    put("robot_vacuum", 4.2, 2.95, 20, room=L)
    against("radiator_column", "S", 0, 1.3, L, z=0.12)
    against("air_conditioner", "W", 0, 3.45, L, z=2.25)
    # dining
    put(S("dining_table_lisabo", "dining_table_lisabo"), 2.6, 3.35, 0, room=L)
    ch = S("dining_chair_teodores", "dining_chair_lisabo")
    facing(ch, 2.25, 2.72, 2.25, 3.35, L); facing(ch, 2.95, 2.72, 2.95, 3.35, L)
    facing(ch, 1.6, 3.35, 2.6, 3.35, L); facing(ch, 3.6, 3.35, 2.6, 3.35, L)
    pendant("pendant_lamp", 2.6, 3.35, L)
    # kitchenette
    K = "Kitchenette"
    for yy in (4.6, 5.2): against("kitchen_base_cabinet", "W", 0, yy, K)
    worktop(0, 4.28, 0.63, 5.5, 0.81, K)
    against(S("microwave_white", "microwave_black"), "W", 0, 4.55, K, z=0.845)
    put("ikea_hob", 0.31, 5.2, 90, 0.80, K)
    against(S("extractor_hood_steel", "extractor_hood_black"), "W", 0, 5.2, K, z=1.5, scale=S(None, (0.667, 1, 1)))
    against("kitchen_sunnersta", "N", D, 1.25, K)
    against("fridge", "W", 0, 5.85, K)
    # hallway
    Hh = "Hallway"
    against("hall_shoe_cabinet", "W", 2.0 + hi, 5.2, Hh)
    put("router", 2.26, 5.55, 90, height("hall_shoe_cabinet"), Hh)
    put("hall_coat_rack", 5.45, 5.9, room=Hh)
    put(S("rug_dark", "rug_dark"), 3.3, 5.2, 90, room=Hh)
    against("stick_vacuum", "N", D, 4.0, Hh)
    pendant("ph_modern_ceiling_lamp_01", 3.9, 5.2, Hh)
    # bedroom
    B = "Bedroom"
    against(S("bed_malm", "bed_double_dark"), "E", W, 2.2, B)
    ns = S("nightstand_malm", "nightstand_hemnes")
    against(ns, "E", W, 1.2, B); against(ns, "E", W, 3.2, B)
    _, nss = asset(ns)
    for yy in (1.2, 3.2): put("table_lamp", W - 0.25, yy, 0, nss.z, B)
    if STYLE == "scandi": put("smart_speaker_dot", W - 0.42, 3.2, -90, nss.z, B)
    for xx in (6.5, 7.5): against(S("wardrobe_pax", "wardrobe_pax"), "N", 4.2 - hi, xx, B)
    dk = S("desk_micke", "desk_dark"); dy = S(1.0, 1.25); dz = height(dk); df = 5.0 + hi
    against(dk, "W", df, dy, B)
    facing(S("office_chair_light", "office_chair_markus"), S(5.75, 5.95), dy, 5.0, dy, B)
    if STYLE == "scandi":
        put("laptop", df + 0.27, dy, 90, dz, B)
        put("ikea_desk_lamp2", df + 0.18, dy + 0.4, 90, dz, B)
    else:
        put("monitor_27", df + 0.14, dy, 90, dz, B)
        put("keyboard", df + 0.42, dy, 90, dz, B)
        put("mouse", df + 0.42, dy - 0.36, 90, dz, B)
        put("pc_tower", df + 0.22, 0.36, 90, 0, B)
        put("ikea_desk_lamp", df + 0.30, dy + 0.52, 0, dz, B)
    put("standing_fan", 5.45, 3.0, 60, room=B)
    against("radiator_column", "S", 0, 6.6, B, z=0.12)
    pendant("ikea_ceiling_lamp", 6.5, 1.9, B)
    # bathroom (real models replace the old placeholders)
    Bt = "Bathroom"
    against("ikea_basin", "N", D, 6.47, Bt)
    against("bathroom_mirror_cabinet", "N", D, 6.27, Bt, z=1.15)
    against("washing_machine", "N", D, 7.32, Bt)
    against("toilet", "E", W, 5.42, Bt)
    put("shower_cabin", 7.55, 4.26 + 0.46, 180, 0, Bt, scale=(0.9 / 1.181, 0.9 / 0.95, 1.0))
    against("towel_radiator", "S", 4.2 + hi, 6.65, Bt, z=0.3)
    against("bathroom_shelf", "S", 4.2 + hi, 6.15, Bt)

# ================================================================= HOUSE ~100 m2
def house():
    W, D = 12.5, 8.0
    exterior(W, D,
        south=[("window", 1.5, 1.6), ("window", 4.0, 1.6), ("window", 6.25, 0.8), ("window", 8.5, 1.4), ("window", 11.25, 1.2)],
        north=[("window", 3.6, 1.4), ("entry", 6.25, 1.0), ("hiwin", 8.0, 0.8), ("window", 10.75, 1.4)],
        west=[("window", 6.2, 1.2)],
        east=[("window", 1.7, 1.0)])
    wall("Int_living_kitchen", (0, 4.4), (5.5, 4.4), TI, [("open", 2.2, 2.6)])
    wall("Int_hall_W", (5.5, 0), (5.5, D), TI, [("open", 2.5, 1.2), ("door", 6.8, 0.9)])
    wall("Int_hall_E_S", (7.0, 0), (7.0, 3.4), TI)
    wall("Int_hall_E_N", (7.0, 4.6), (7.0, D), TI)
    wall("Int_corr_S", (7.0, 3.4), (W, 3.4), TI, [("door", 7.6, 0.8), ("door", 10.6, 0.8)])
    wall("Int_corr_N", (7.0, 4.6), (W, 4.6), TI, [("door", 8.0, 0.8), ("door", 9.6, 0.8)])
    wall("Int_bed2_bed3", (10.0, 0), (10.0, 3.4), TI)
    wall("Int_bath_master", (9.0, 4.6), (9.0, D), TI)
    room("Living_room", "living", 0, 0, 5.5, 4.4, "wood")
    room("Kitchen_dining", "kitchen", 0, 4.4, 5.5, D, "tile")
    room("Hallway", "hallway", 5.5, 0, 7.0, D, "wood")
    room("Corridor", "hallway", 7.0, 3.4, W, 4.6, "wood")
    room("Bedroom_2", "bedroom", 7.0, 0, 10.0, 3.4, "wood")
    room("Bedroom_3_office", "bedroom", 10.0, 0, W, 3.4, "wood")
    room("Master_bedroom", "bedroom", 9.0, 4.6, W, D, "wood")
    room("Bathroom", "bathroom", 7.0, 4.6, 9.0, D, "bath")
    if not FURNISH: return
    L = "Living_room"
    put("rug_large", 2.0, 2.2, 0, room=L)
    bench = S("tv_bench_besta", "ikea_tv_bench_wall")
    against(bench, "W", 0, 2.2, L); bz = height(bench); bx = depth(bench) / 2 + 0.01
    against(S("tv_qled_65", "tv_sony_55"), "W", 0, 2.2, L, z=bz)
    put("soundbar", bx + 0.13, 2.2, 90, bz, L)
    put(S("console_ps5", "console_xbox"), bx, 3.02, 90, bz, L)
    put("smart_speaker_home", bx, 1.38, 90, bz, L)
    put(S("sofa_kivik", "sofa_dark"), 3.55, 2.2, -90, room=L)
    ct = S("coffee_table_lack", "coffee_table_listerby")
    put(ct, 2.0, 2.2, 0 if STYLE == "scandi" else 90, room=L)
    put("gamepad", 2.1, 2.35, 200, height(ct), L)
    facing(S("armchair_light", "armchair_strandmon"), 1.0, 0.65, 2.0, 2.2, L)
    facing("armchair_strandmon" if STYLE == "scandi" else "armchair_light", 1.0, 3.75, 2.0, 2.2, L)
    put(S("floor_lamp_hoglunda", "floor_lamp_hektar"), 4.25, 0.45, 200, room=L)
    for xx in (4.15, 4.95): against(S("bookcase_billy", "bookcase_billy"), "N", 4.4 - hi, xx, L)
    against("shelf_kallax", "E", 5.5 - hi, 0.6, L)
    put("plant_pot", 0.4, 0.4, room=L)
    put("robot_vacuum", 4.7, 3.65, -30, room=L)
    against("air_conditioner", "N", 4.4 - hi, 4.55, L, z=2.2)
    for xx in (1.5, 4.0): against("radiator_column", "S", 0, xx, L, z=0.12)
    pendant("ph_ceiling_fan", 2.0, 2.2, L)
    K = "Kitchen_dining"
    # north wall run: cabinet | oven+hob+hood | microwave | sink | dishwasher
    for xx in (0.3, 1.5, 2.1): against("kitchen_base_cabinet", "N", D, xx, K)
    against("oven_builtin", "N", D, 0.9, K, z=0.17)
    against("dishwasher", "N", D, 3.06, K)
    worktop(0, D - 0.66, 3.39, D, 0.81, K)
    put("ikea_hob", 0.9, D - 0.31, 0, 0.795, K)
    against(S("extractor_hood_steel", "extractor_hood_black"), "N", D, 0.9, K, z=1.55, scale=S(None, (0.667, 1, 1)))
    for xx in (0.3, 1.5, 2.1): against("kitchen_wall_cabinet", "N", D, xx, K, z=1.45)
    against(S("microwave_white", "microwave_black"), "N", D, 1.5, K, z=0.845)
    put("kitchen_sink_steel", 2.2, D - 0.31, 0, 0.845 - CAT["kitchen_sink_steel"]["mount"].get("rim_z", 0.3), K)
    against("electric_kettle", "N", D, 0.22, K, z=0.845)
    against("fridge_side_by_side", "W", 0, 4.95, K)
    put("kitchen_island", 1.5, 6.15, 0, room=K)
    put("toaster", 1.05, 6.15, 0, height("kitchen_island"), K)
    put(S("espresso_machine", "coffee_machine_drip"), 1.95, 6.2, 0, height("kitchen_island"), K)
    put(S("kitchen_cart", "kitchen_cart"), 5.15, 7.6, -90, room=K)
    put(S("dining_table_wood", "dining_table_lisabo"), 3.95, 5.7, 0, room=K)
    ch = S("dining_chair_lisabo", "dining_chair_teodores")
    for xx in (3.55, 4.35):
        facing(ch, xx, 5.05, xx, 5.7, K); facing(ch, xx, 6.35, xx, 5.7, K)
    pendant("pendant_lamp", 3.95, 5.7, K); pendant("pendant_lamp", 1.5, 6.15, K)
    Hh = "Hallway"
    against("hall_shoe_cabinet", "E", 7.0 - hi, 7.1, Hh)
    put("router", 6.76, 7.35, -90, height("hall_shoe_cabinet"), Hh)
    put("hall_coat_rack", 5.85, 7.6, room=Hh)
    put("rug_dark", 6.25, 2.0, 0, room=Hh)
    against("stick_vacuum", "W", 5.5 + hi, 5.2, Hh)
    pendant("ph_modern_ceiling_lamp_01", 6.25, 4.0, Hh)
    B2 = "Bedroom_2"
    against(S("bed_double_dark", "bed_double_dark"), "E", 10.0 - hi, 1.65, B2)
    for yy in (0.62, 2.68): against("nightstand_hemnes", "E", 10.0 - hi, yy, B2)
    _, nh = asset("nightstand_hemnes"); put("table_lamp", 9.72, 0.62, 0, nh.z, B2)
    put("smart_speaker_dot", 9.77, 2.68, -90, nh.z, B2)
    against(S("wardrobe_kleppstad", "wardrobe_kleppstad"), "W", 7.0 + hi, 1.2, B2)
    against("air_conditioner", "E", 10.0 - hi, 1.65, B2, z=2.2)
    put("standing_fan", 7.4, 2.15, 120, room=B2)
    against("radiator_column", "S", 0, 8.5, B2, z=0.12)
    B3 = "Bedroom_3_office"
    against("bed_single", "N", 3.4 - hi, 11.95, B3)
    dk = S("desk_micke", "desk_dark"); df = 10.0 + hi; dz = height(dk); half = asset(dk)[1].x / 2
    against(dk, "W", df, 1.0, B3)
    facing(S("office_chair_light", "office_chair_markus"), 10.85, 1.0, 10.0, 1.0, B3)
    put("monitor_27", df + 0.14, 1.0, 90, dz, B3)
    put("keyboard", df + 0.40, 1.0, 90, dz, B3)
    put("mouse", df + 0.40, 0.66, 90, dz, B3)
    put("pc_tower", df + 0.22, 1.0 + half + 0.13, 90, 0, B3)
    if STYLE == "scandi": put("ikea_desk_lamp2", df + 0.18, 1.38, 90, dz, B3)
    else: put("ikea_desk_lamp", df + 0.30, 1.52, 0, dz, B3)
    against(S("shelf_kallax", "bookcase_billy"), "S", 0, 12.05, B3)
    against("radiator_column", "S", 0, 11.0, B3, z=0.12)
    M = "Master_bedroom"
    put(S("rug_large", "rug_dark"), 11.0, 6.3, 90, room=M)
    against(S("bed_malm", "bed_malm"), "E", W, 6.3, M)
    ns = S("nightstand_malm", "nightstand_hemnes")
    for yy in (5.3, 7.3):
        against(ns, "E", W, yy, M); put("table_lamp", W - 0.25, yy, 0, asset(ns)[1].z, M)
    if STYLE == "scandi": put("smart_speaker_dot", W - 0.43, 7.3, -90, asset(ns)[1].z, M)
    for yy in (6.0, 7.0): against("wardrobe_pax", "W", 9.0 + hi, yy, M)
    put("plant_pot", 9.45, 5.0, room=M)
    against("air_conditioner", "N", D, 9.75, M, z=2.3)
    against("radiator_column", "N", D, 10.75, M, z=0.12)
    pendant("ikea_ceiling_lamp", 10.75, 6.3, M)
    Bt = "Bathroom"
    put("bathtub_freestanding", 7.95, 7.5, 0, room=Bt)
    against("ikea_basin", "W", 7.0 + hi, 6.1, Bt)
    against("bathroom_mirror_cabinet", "W", 7.0 + hi, 5.85, Bt, z=1.15)
    against("toilet", "E", 9.0 - hi, 5.3, Bt)
    against("washing_machine", "E", 9.0 - hi, 5.95, Bt)
    against("dryer", "E", 9.0 - hi, 5.95, Bt, z=height("washing_machine") + 0.005)
    against("bathroom_shelf", "E", 9.0 - hi, 6.6, Bt)
    against("towel_radiator", "S", 4.6 + hi, 7.3, Bt, z=0.3)

# ================================================================= scene, export, render
def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 24
    sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1100
    sc.view_settings.view_transform = "AgX"
    w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*PAL["world"], 1); bg.inputs[1].default_value = 0.6
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.5; sun.data.angle = math.radians(8); sun.rotation_euler = (math.radians(30), math.radians(12), math.radians(35))
    sc.collection.objects.link(sun)

def camera(kind, W, D):
    sc = bpy.context.scene
    cam = bpy.data.objects.get("Cam") or bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.clip_end = 200
    c = Vector((W / 2, D / 2, 0.8))
    if kind == "top":
        cam.location = (W / 2, D / 2, 30); cam.rotation_euler = (0, 0, 0)
        cam.data.ortho_scale = max(W, D * 1600 / 1100) + 1.2
    else:
        d = Vector((1.0, -1.25, 1.35)).normalized()
        cam.location = c + d * 40
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        cam.data.ortho_scale = max(W, D) * 1.32 + 1.0
    sc.camera = cam

def render(path):
    bpy.context.scene.render.filepath = path; bpy.ops.render.render(write_still=True)

def export_glb(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_visible=True, export_image_format="JPEG", export_jpeg_quality=82, export_lights=False, export_cameras=False, export_apply=False)

MODE = argv[2] if len(argv) > 2 else "both"
bpy.ops.wm.read_factory_settings(use_empty=True)
FURNISH = MODE == "furnished"
C_SHELL, C_FURN = coll("Shell"), coll("Furniture")
C_LIB = coll("_IKEA_library"); bpy.context.view_layer.layer_collection.children["_IKEA_library"].exclude = True
M_WALL = mat(f"Wall_{STYLE}", PAL["wall"], 0.8); M_GLASS = mat("Glass", (0.8, 0.9, 1.0), 0.02, alpha=0.25, transmission=1.0)
M_FRAME = mat("Frame", (0.95, 0.95, 0.95) if STYLE == "scandi" else (0.08, 0.08, 0.08), 0.4)
M_DOOR = mat("DoorLeaf", (0.9, 0.88, 0.84) if STYLE == "scandi" else (0.12, 0.11, 0.10), 0.5)
M_PORC = mat("Porcelain", (0.97, 0.97, 0.97), 0.15); M_TOP = mat("Worktop", (0.75, 0.62, 0.45) if STYLE == "scandi" else (0.10, 0.10, 0.10), 0.35)
M_CHROME = mat("Chrome", (0.9, 0.9, 0.9), 0.15, metal=1.0)
(apartment if LAYOUT == "apartment" else house)()
W, D = (8.0, 6.25) if LAYOUT == "apartment" else (12.5, 8.0)
setup_render()
tag = f"{LAYOUT}_{STYLE}_{'furnished' if FURNISH else 'shell'}"
bpy.context.scene["layout"] = LAYOUT; bpy.context.scene["style"] = STYLE
# layout files only need preview-grade textures: cap at 512px (the per-asset GLBs keep 2K)
for im in bpy.data.images:
    if im.size[0] > 512 or im.size[1] > 512:
        r = 512 / max(im.size); im.scale(max(1, int(im.size[0] * r)), max(1, int(im.size[1] * r)))
        if im.packed_file:
            import numpy as np
            px = np.empty(im.size[0] * im.size[1] * 4, dtype=np.float32); im.pixels.foreach_get(px)
            if im.channels < 4 or px[3::4].min() > 0.99: im.file_format = "JPEG"
            im.pack()
bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/layouts/{tag}.blend", compress=True)
export_glb(f"{ROOT}/layouts/{tag}.glb")
json.dump(dict(layout=LAYOUT, style=STYLE, furnished=FURNISH, footprint_m=[W, D], rooms=ROOMS, placed=PLACED,
               total_area_m2=round(sum(r["area_m2"] for r in ROOMS), 2)), open(f"{ROOT}/layouts/{tag}.json", "w"), indent=1)
for kind in ("top", "iso"):
    for o in C_FURN.all_objects:
        top_hidden = kind == "top" and (o.get("ceiling") or (o.parent is not None and o.parent.get("ceiling")))
        o.hide_render = bool(top_hidden)
    camera(kind, W, D); render(f"{ROOT}/previews/{tag}_{kind}.png")
print("DONE", tag)
