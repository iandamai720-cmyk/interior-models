"""Houses for turn 4: two-storey (house2, 180 m2) and single-storey (house1, 150 m2).
Usage: blender -b --python build_layout2.py -- <house2|house1> <scandi|dark> <furnished|shell>
Reuses helpers from build_layout.py (exec'd up to the APARTMENT marker) and adds floors (Z0), stairs, terraces."""
import sys, json, math
ROOT = "/workspace/interior-lib"
_full = open(f"{ROOT}/scripts/build_layout.py").read()
_src = _full.split("# ================================================================= APARTMENT")[0] + \
       _full.split("# ================================================================= scene, export, render")[1].split("MODE = argv[2]")[0]
FURNISH = False
exec(compile(_src, "build_layout.py", "exec"))
for a in json.load(open(f"{ROOT}/tmp/new_assets.json")):
    CAT[a["key"]] = a
MODE = argv[2]
from mathutils import Euler
def camera_fit(kind, bb):
    """Ortho camera that frames bounding box bb=(x0,y0,z0,x1,y1,z1) for 'top' or 'iso'."""
    sc = bpy.context.scene
    cam = bpy.data.objects.get("Cam") or bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.clip_end = 300
    d = Vector((0, 0, 1)) if kind == "top" else Vector((1.0, -1.25, 1.35)).normalized()
    q = (-d).to_track_quat("-Z", "Y") if kind != "top" else Euler((0, 0, 0)).to_quaternion()
    right, up = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0))
    x0, y0, z0, x1, y1, z1 = bb
    pts = [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    us = [p.dot(right) for p in pts]; vs = [p.dot(up) for p in pts]
    cu, cv = (min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2
    asp = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(max(us) - min(us), (max(vs) - min(vs)) * asp) * 1.06
    cen = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    cen = cen + right * (cu - cen.dot(right)) + up * (cv - cen.dot(up))
    cam.location = cen + d * 80
    cam.rotation_euler = q.to_euler()
    sc.camera = cam

# ---------------------------------------------------------------- floor-aware wrappers
Z0, FLOOR = 0.0, 0
_IN_PUT = [False]
_box0, _put0, _room0 = box, put, room
def box(name, x0, y0, z0, x1, y1, z1, m, c=None, props=None):
    dz = 0.0 if _IN_PUT[0] else Z0
    o = _box0(name, x0, y0, z0 + dz, x1, y1, z1 + dz, m, c, props); o["floor"] = FLOOR; return o
def put(key, x, y, rot=0.0, z=0.0, room=None, scale=None, ceiling=False):
    _IN_PUT[0] = True
    try: o = _put0(key, x, y, rot, z + Z0, room, scale, ceiling)
    finally: _IN_PUT[0] = False
    o["floor"] = FLOOR; PLACED[-1]["floor"] = FLOOR; PLACED[-1]["z"] = round(z + Z0, 3); return o
def room(name, kind, x0, y0, x1, y1, floor="wood", hole=None):
    if hole is None:
        _room0(name, kind, x0, y0, x1, y1, floor)
    else:   # floor plate with a rectangular opening (stairwell)
        hx0, hy0, hx1, hy1 = hole; fm = floor_mat(floor)
        for (a, b, c, d) in ((x0, y0, x1, hy0), (x0, hy1, x1, y1), (x0, hy0, hx0, hy1), (hx1, hy0, x1, hy1)):
            if c - a > 1e-3 and d - b > 1e-3: box(f"Floor_{name}", a, b, -0.01, c, d, 0.0, fm, props={"room": name, "room_type": kind})
        ar = round((x1 - x0) * (y1 - y0) - (hx1 - hx0) * (hy1 - hy0), 2)
        ROOMS.append(dict(name=name, type=kind, area_m2=ar, bounds=[x0, y0, x1, y1], opening=list(hole)))
    ROOMS[-1]["floor"] = FLOOR

def wall(name, a, b, t, ops=(), axis=None):
    """as build_layout.wall + 'patio' (full-height glazed door 0..2.2 m)."""
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
        if kind == "door":    seg(s0, s1, 2.1, H); frame(horiz, c, t, s0, s1, 0, 2.1, door=True)
        elif kind == "entry": seg(s0, s1, 2.1, H); frame(horiz, c, t, s0, s1, 0, 2.1, door=True); leaf(horiz, c, t, s0, s1)
        elif kind == "window": seg(s0, s1, 0, 0.9); seg(s0, s1, 2.2, H); frame(horiz, c, t, s0, s1, 0.9, 2.2)
        elif kind == "hiwin":  seg(s0, s1, 0, 1.5); seg(s0, s1, 2.1, H); frame(horiz, c, t, s0, s1, 1.5, 2.1)
        elif kind == "patio":  seg(s0, s1, 2.25, H); frame(horiz, c, t, s0, s1, 0.0, 2.25)
        elif kind == "open":   seg(s0, s1, 2.4, H)
        cur = s1
    seg(cur, hi_, 0, H)

def exterior2(W, D, south=(), north=(), west=(), east=(), hole=None):
    e = TE / 2
    wall("Ext_S", (-TE, -e), (W + TE, -e), TE, south)
    wall("Ext_N", (-TE, D + e), (W + TE, D + e), TE, north)
    wall("Ext_W", (-e, 0), (-e, D), TE, west)
    wall("Ext_E", (W + e, 0), (W + e, D), TE, east)
    ms = mat("Slab", (0.5, 0.5, 0.5)); z0 = -0.3 if FLOOR else -0.2
    if hole is None:
        box("Slab", -TE, -TE, z0, W + TE, D + TE, -0.01, ms)
    else:
        hx0, hy0, hx1, hy1 = hole
        for (a, b, c, d) in ((-TE, -TE, W + TE, hy0), (-TE, hy1, W + TE, D + TE), (-TE, hy0, hx0, hy1), (hx1, hy0, W + TE, hy1)):
            if c - a > 1e-3 and d - b > 1e-3: box("Slab", a, b, z0, c, d, -0.01, ms)

M_STAIR = None
def stairs(x0, y0, y1, n=16, rise=3.0, run=0.27, glass_side="S"):
    """Straight flight rising towards +X from (x0, y0..y1); n risers to the next floor at local z=rise."""
    global M_STAIR
    M_STAIR = M_STAIR or mat("StairTread", (0.70, 0.55, 0.38) if STYLE == "scandi" else (0.10, 0.09, 0.08), 0.45)
    h = rise / n
    for i in range(n - 1):
        xa, xb, zt = x0 + i * run, x0 + (i + 1) * run, (i + 1) * h
        box("Stair_tread", xa, y0, zt - 0.05, xb + 0.02, y1, zt, M_STAIR, C_SHELL, {"stairs": 1})
        box("Stair_body", xa, y0, max(0.0, zt - 0.30), xb, y1, zt - 0.05, M_WALL, C_SHELL)
        yg = y0 + 0.02 if glass_side == "S" else y1 - 0.02
        box("Stair_glass", xa, yg - 0.01, zt, xb, yg + 0.01, zt + 0.9, M_GLASS, C_SHELL)
    yr = y0 + 0.02 if glass_side == "S" else y1 - 0.02
    for i in range(n - 1):
        box("Stair_rail", x0 + i * run, yr - 0.025, (i + 1) * h + 0.9, x0 + (i + 1) * run, yr + 0.025, (i + 1) * h + 0.94, M_FRAME, C_SHELL)
    return (x0, y0, x0 + (n - 1) * run, y1)

def railing(x0, y0, x1, y1, hgt=1.0):
    box("Railing_glass", x0, y0, 0.0, x1, y1, hgt, M_GLASS, C_SHELL)
    box("Railing_top", x0 - 0.01, y0 - 0.015, hgt, x1 + 0.01, y1 + 0.015, hgt + 0.04, M_FRAME, C_SHELL)

def deck(name, x0, y0, x1, y1, z=0.0):
    m = mat("Deck", (0.55, 0.42, 0.30) if STYLE == "scandi" else (0.18, 0.15, 0.13), 0.7)
    box(name, x0, y0, z - 0.15, x1, y1, z - 0.02, m, C_SHELL, {"room": name, "room_type": "terrace"})
    ROOMS.append(dict(name=name, type="terrace", area_m2=round((x1 - x0) * (y1 - y0), 2), bounds=[x0, y0, x1, y1], floor=FLOOR, outdoor=True))

def curtain(side, face, along, rm):
    k = S("majgull_zasony_zaciemniajace_para_30586033", "haggveckmal_zasony_zacieniajace_1_para_20569029")
    against(k, side, face, along, rm, z=0.0, gap=0.06, scale=(1.0, 1.0, 2.6 / height(k)))

def on_wall(key, side, face, along, z, rm):
    return against(key, side, face, along, rm, z=z, gap=0.005)

def kitchen_run(side, face, s, rm, sign=1):
    """Base cabinets/oven/sink/dishwasher + wall cabinets along one wall, starting at 'along'=s, going +sign."""
    a = lambda d: s + sign * d
    for d in (0.3, 1.5, 2.1): against("kitchen_base_cabinet", side, face, a(d), rm)
    against("oven_builtin", side, face, a(0.9), rm, z=0.17)
    against("dishwasher", side, face, a(2.72), rm)
    dd = 0.66
    lo, hi2 = sorted((a(0), a(3.03)))
    if side == "N":   worktop(lo, face - dd, hi2, face, 0.81, rm)
    elif side == "S": worktop(lo, face, hi2, face + dd, 0.81, rm)
    elif side == "W": worktop(face, lo, face + dd, hi2, 0.81, rm)
    else:             worktop(face - dd, lo, face, hi2, 0.81, rm)
    off = {"N": (0, -0.31), "S": (0, 0.31), "W": (0.31, 0), "E": (-0.31, 0)}[side]
    rot = {"N": 0, "S": 180, "W": 90, "E": -90}[side]
    def at(d):
        al = a(d)
        return (al + off[0], face + off[1]) if side in "NS" else (face + off[0], al + off[1])
    x, y = at(0.9); put("ikea_hob", x, y, rot, 0.795, rm)
    against(S("extractor_hood_steel", "extractor_hood_black"), side, face, a(0.9), rm, z=1.55, scale=S(None, (0.667, 1, 1)))
    for d in (0.3, 1.5, 2.1, 2.7): against("kitchen_wall_cabinet", side, face, a(d), rm, z=1.45)
    against(S("microwave_white", "microwave_black"), side, face, a(1.5), rm, z=0.845)
    x, y = at(2.15); put("kitchen_sink_steel", x, y, rot, 0.845 - CAT["kitchen_sink_steel"]["mount"].get("rim_z", 0.3), rm)
    against("electric_kettle", side, face, a(0.22), rm, z=0.845)
    against(S("espresso_machine", "coffee_machine_drip"), side, face, a(1.25), rm, z=0.845)
    x, y = at(1.85); put("aptitlig_deska_do_krojenia_80233430", x, y, rot, 0.845, rm)
    x, y = at(0.9); put("ikea_365_garnek_z_pokrywka_90484244", x - 0.1 * (side in "NS"), y - 0.1 * (side in "WE"), rot, 0.80, rm)

def bed_with_ns(bed, ns, lamp, side, face, along, rm):
    o = against(bed, side, face, along, rm)
    bw = asset(bed)[1].x; nw = asset(ns)[1].x; nz = asset(ns)[1].z
    for sg in (-1, 1):
        al = along + sg * (bw / 2 + nw / 2 + 0.04)
        against(ns, side, face, al, rm)
        against(lamp, side, face, al, rm, z=nz, gap=0.12)
    return o

def check_keys(keys):
    miss = [k for k in keys if k not in CAT]
    if miss: raise SystemExit(f"missing assets: {miss}")

# ================================================================= TWO-STOREY HOUSE 10 x 9 m (2 x 90 m2)
def house2():
    global Z0, FLOOR
    W, D = 10.0, 9.0
    SX0, SY0, SY1 = 5.4, 7.95, 9.0          # staircase: 16 risers x 0.1875, 15 treads x 0.27 -> x 5.4..9.45
    SX1 = SX0 + 15 * 0.27
    # ---------------- ground floor
    Z0, FLOOR = 0.0, 0
    exterior2(W, D,
        south=[("window", 2.0, 1.4), ("patio", 6.0, 2.4), ("window", 8.6, 1.4)],
        north=[("hiwin", 1.1, 0.6), ("hiwin", 2.9, 0.5), ("entry", 4.5, 1.0)],
        west=[("window", 0.9, 1.0), ("window", 7.0, 0.8)],
        east=[("window", 0.9, 0.8), ("window", 4.3, 0.8), ("window", 6.4, 1.0)])
    wall("GF_y5_W", (0, 5), (3.6, 5), TI, [("door", 1.1, 0.8)])
    wall("GF_y5_E", (3.6, 5), (W, 5), TI, [("open", 4.9, 1.4)])
    wall("GF_x4", (4, 0), (4, 5), TI, [("open", 2.6, 3.0)])
    wall("GF_x22", (2.2, 5), (2.2, D), TI)
    wall("GF_x36", (3.6, 5), (3.6, D), TI, [("door", 5.9, 0.7), ("door", 7.9, 0.7)])
    wall("GF_y68", (2.2, 6.8), (3.6, 6.8), TI)
    room("GF_Kitchen_dining", "kitchen", 0, 0, 4, 5, "tile")
    room("GF_Living_room", "living", 4, 0, W, 5, "wood")
    room("GF_Utility", "utility", 0, 5, 2.2, D, "tile")
    room("GF_WC", "bathroom", 2.2, 5, 3.6, 6.8, "bath")
    room("GF_Wardrobe", "wardrobe", 2.2, 6.8, 3.6, D, "wood")
    room("GF_Hall", "hallway", 3.6, 5, W, D, "wood")
    stairs(SX0, SY0, SY1, glass_side="S")
    deck("GF_Terrace", 3.0, -3.2, W + 0.25, -0.13)
    if FURNISH: furnish_house2_gf(W, D)
    # ---------------- first floor
    Z0, FLOOR = 3.0, 1
    hole = (SX0, SY0, SX1, D)
    exterior2(W, D,
        south=[("window", 2.2, 1.6), ("patio", 5.9, 1.8), ("window", 8.65, 1.4)],
        north=[("window", 1.3, 1.0), ("hiwin", 4.0, 0.8), ("window", 7.4, 1.6)],
        west=[("window", 0.9, 0.8), ("window", 6.4, 1.0)],
        east=[("window", 1.2, 1.0), ("window", 6.3, 1.2)], hole=hole)
    wall("FF_y46", (0, 4.6), (W, 4.6), TI, [("door", 3.8, 0.8), ("door", 6.6, 0.8), ("door", 8.2, 0.8)])
    wall("FF_x45", (4.5, 0), (4.5, 4.6), TI)
    wall("FF_x73", (7.3, 0), (7.3, 4.6), TI)
    wall("FF_y56", (0, 5.6), (5.4, 5.6), TI, [("door", 1.3, 0.8), ("door", 4.0, 0.8)])
    wall("FF_x26", (2.6, 5.6), (2.6, D), TI)
    wall("FF_x54", (5.4, 5.6), (5.4, D), TI)
    room("FF_Master_bedroom", "bedroom", 0, 0, 4.5, 4.6, "wood")
    room("FF_Bedroom_2", "bedroom", 4.5, 0, 7.3, 4.6, "wood")
    room("FF_Kids_room", "kids", 7.3, 0, W, 4.6, "wood")
    room("FF_Corridor", "hallway", 0, 4.6, 5.4, 5.6, "wood")
    room("FF_Office", "office", 0, 5.6, 2.6, D, "wood")
    room("FF_Bathroom", "bathroom", 2.6, 5.6, 5.4, D, "bath")
    room("FF_Landing", "hallway", 5.4, 5.6 - 1.0, W, D, "wood", hole=hole)
    ROOMS[-1]["area_m2"] = round((W - 5.4) * (D - 4.6) - (SX1 - SX0) * (D - SY0), 2)
    railing(SX0, SY0 - 0.02, SX1, SY0 + 0.0)
    deck("FF_Balcony", 4.5, -1.6, 7.3, -0.13)
    railing(4.5, -1.62, 7.3, -1.58); railing(4.48, -1.6, 4.52, -0.13); railing(7.28, -1.6, 7.32, -0.13)
    if FURNISH: furnish_house2_ff(W, D)
    return W, D

def furnish_house2_gf(W, D):
    K = "GF_Kitchen_dining"
    kitchen_run("W", 0, 1.9, K, sign=1)              # west wall, y 1.9..4.93
    against(S("fridge_side_by_side", "fridge"), "N", 5 - hi, 3.4, K)
    tb = S("tonstad_sto_rozkadany_40593882", "stornas_sto_rozkadany_40176846")
    put(tb, 2.3, 1.3, 0, room=K)
    ch = S("sandsberg_krzeso_40605253", "skogsta_krzeso_70544866")
    for xx in (1.95, 2.65):
        facing(ch, xx, 0.6, xx, 1.3, K); facing(ch, xx, 2.0, xx, 1.3, K)
    put("ikea_365_kubek_80278367", 2.0, 1.2, 0, height(tb), K); put("stilren_wazon_10442045", 2.4, 1.3, 0, height(tb), K)
    pendant(S("stockholm_2025_lampa_wiszaca_90585988", "skurup_lampa_wiszaca_80407114"), 2.3, 1.3, K)
    put("fejka_sztuczna_roslina_doniczkowa_00615249", 3.7, 0.3, room=K)
    curtain("S", 0, 2.0, K); against("radiator_column", "S", 0, 2.0, K, z=0.12)
    L = "GF_Living_room"
    put(S("lokaltag_dywan_z_krotkim_wosiem_10623220", "jarnvag_dywan_z_krotkim_wosiem_20595698"), 8.0, 2.4, 90, room=L)
    put(S("soderhamn_sofa_narozna_4_osobowa_89305842", "vimle_sofa_narozna_5_osobowa_99399581"), 6.4, 2.4, 90, room=L)
    ct = S("vittsjo_stolik_kawowy_80213309", "tonstad_stolik_kawowy_10489311")
    put(ct, 8.25, 2.4, 0, room=L); put("kenney_books", 8.2, 2.4, 20, height(ct), L)
    tvb = S("hemnes_szafka_pod_tv_50413526", "stockholm_2025_awa_tv_z_drzwiami_przesuwnymi_40586508")
    against(tvb, "E", W, 2.4, L); bz = height(tvb)
    against(S("tv_qled_65", "tv_sony_55"), "E", W, 2.4, L, z=bz)
    put("soundbar", W - 0.3, 2.4, -90, bz, L)
    facing(S("poang_fotel_59514385", "strandmon_fotel_uszak_20343224"), 8.6, 4.3, 8.25, 2.4, L)
    put(S("arstid_lampa_podogowa_00321317", "barlast_lampa_podogowa_10430368"), 4.5, 0.5, room=L)
    for xx in (6.2, 6.6): against("billy_rega_50263838", "N", 5 - hi, xx, L)
    put("fejka_sztuczna_roslina_doniczkowa_00600894", 7.6, 4.5, room=L)
    put("fejka_sztuczna_roslina_doniczkowa_00615249", 9.7, 4.6, room=L)
    on_wall("bondis_zegar_scienny_10543092", "W", 4 + hi, 4.55, 1.7, L)
    curtain("S", 0, 8.6, L); against("radiator_column", "S", 0, 8.6, L, z=0.12)
    pendant("ph_ceiling_fan", 8.0, 2.4, L)
    Hh = "GF_Hall"
    against(S("gullaberg_szafka_na_buty_4_przegrody_10587707", "bissa_szafka_na_buty_3_przegrody_10530259"), "S", 5 + hi, 6.6, Hh)
    against("hovet_lustro_70515915", "S", 5 + hi, 7.6, Hh)
    against(S("tolkning_awka_z_pojemnikiem_80512657", "gullaberg_awka_ze_schowkiem_80573957"), "S", 5 + hi, 8.8, Hh)
    against("mulig_wieszak_na_ubrania_60179434", "W", 3.6 + hi, 6.9, Hh)
    put(S("tiphede_dywan_tkany_na_pasko_40456757", "lohals_dywan_tkany_na_pasko_30511288"), 4.7, 7.0, 0, room=Hh)
    put("kenney_plant_small2", 9.75, 7.6, room=Hh)
    pendant("ph_modern_ceiling_lamp_01", 7.0, 6.5, Hh)
    U = "GF_Utility"
    against("washing_machine", "W", 0, 8.35, U); against("dryer", "W", 0, 8.35, U, z=height("washing_machine") + 0.005)
    against("hyllis_rega_00278578", "N", D, 1.6, U)
    against("danka_deska_do_prasowania_20471612", "E", 2.2 - hi, 7.0, U)
    put("branas_kosz_na_bielizne_20214731", 0.35, 5.4, room=U)
    put("jall_suszarka_na_pranie_80242892", 0.5, 6.4, 90, room=U)
    put("stick_vacuum", 1.95, 5.35, 180, room=U)
    Wc = "GF_WC"
    against("toilet", "N", 6.8 - hi, 2.9, Wc)
    against("ikea_basin", "W", 2.2 + hi, 5.55, Wc)
    on_wall("larbro_lustro_40601778", "W", 2.2 + hi, 5.55, 1.25, Wc)
    against("pax_flisberget_szafa_39304128", "W", 2.2 + hi, 7.9, "GF_Wardrobe", scale=(0.9, 1, 1))

def furnish_house2_ff(W, D):
    M = "FF_Master_bedroom"
    put(S("lokaltag_dywan_z_krotkim_wosiem_10623220", "jarnvag_dywan_z_krotkim_wosiem_20595698"), 2.3, 2.6, 90, room=M)
    bed_with_ns(S("tonstad_rama_ozka_89577729", "idanas_rama_ozka_40458898"), S("tonstad_stolik_nocny_80489322", "hemnes_komoda_2_szuflady_80242627"),
                S("blidvader_lampa_stoowa_80501258", "arstid_lampa_stoowa_30321373"), "W", 0, 2.6, M)
    against("pax_forsand_szafa_49494335", "N", 4.6 - hi, 1.75, M)
    against(S("malm_toaletka_70620346", "storklinta_komoda_6_szuflad_70627550"), "E", 4.5 - hi, 1.4, M)
    on_wall("rodalm_ramka_70548925", "E", 4.5 - hi, 3.2, 1.3, M)
    put("fejka_sztuczna_roslina_doniczkowa_00615249", 4.2, 0.3, room=M)
    curtain("S", 0, 2.2, M); against("radiator_column", "S", 0, 2.2, M, z=0.12)
    pendant("ikea_ceiling_lamp", 2.6, 2.6, M)
    B2 = "FF_Bedroom_2"
    against(S("vihals_rama_ozka_20602439", "tarva_rama_ozka_29553972"), "W", 4.5 + hi, 2.8, B2)
    against(S("knarrevik_stolik_nocny_00576318", "gullaberg_stolik_nocny_20561740"), "W", 4.5 + hi, 1.65, B2)
    against("brimnes_szafa_2_drzwi_40400478", "E", 7.3 - hi, 3.6, B2)
    put(S("strandmon_fotel_uszak_20343224", "oskarshamn_fotel_uszak_20523611"), 6.8, 1.45, -120, room=B2)
    curtain("S", 0, 5.9, B2)
    pendant("pendant_lamp", 5.9, 2.4, B2)
    KD = "FF_Kids_room"
    put("kenney_rug_round", 8.4, 2.3, 0, room=KD)
    against("mydal_rama_ozka_pietrowego_00102452", "E", W, 3.45, KD)
    against("trofast_rega_z_pojemnikami_39574865", "W", 7.3 + hi, 3.7, KD)
    against("piplarka_biurko_20579943", "W", 7.3 + hi, 1.3, KD)
    facing("ingolf_krzeso_dzieciece_60353838", 8.25, 1.3, 7.3, 1.3, KD)
    put("mala_sztaluga_30488966", 9.4, 0.6, -150, room=KD)
    put("djungelskog_pluszak_00402808", 8.0, 3.1, 30, room=KD)
    put("lillabo_garaz_z_samochodem_i_helikopterem_80589350", 8.7, 2.0, 10, room=KD)
    curtain("S", 0, 8.65, KD)
    pendant("ikea_ceiling_lamp", 8.65, 2.3, KD)
    O = "FF_Office"
    dk = S("malm_biurko_60214159", "lagkapten_alex_biurko_09521604")
    against(dk, "W", 0, 8.1, O); dz = height(dk)
    facing(S("alefjall_krzeso_biurowe_40419982", "markus_krzeso_biurowe_30588800"), 1.05, 8.1, 0.0, 8.1, O)
    put("monitor_27", 0.16, 8.1, 90, dz, O); put("keyboard", 0.42, 8.1, 90, dz, O)
    put(S("forsa_lampa_biurkowa_30439117", "skurup_lampa_biurkowa_80516778"), 0.2, 8.65, 90, dz, O)
    for xx in (0.25, 2.35): against("billy_rega_50263838", "S", 5.6 + hi, xx, O)
    put("ph_book_encyclopedia_set_01", 0.25, 5.8, 180, height("billy_rega_50263838"), O, scale=(0.7, 1, 1))
    against(S("alex_komoda_na_kokach_59422220", "helmer_komoda_na_kokach_70625023"), "E", 2.6 - hi, 6.3, O)
    pendant("ikea_ceiling_lamp", 1.3, 7.3, O)
    Bt = "FF_Bathroom"
    put("bathtub_freestanding", 4.4, 8.4, 0, room=Bt)
    against(S("havback_szafka_umywalkowa_z_szufladami_90535069", "tannforsen_szafka_umywalkowa_z_szufladami_30535114"), "W", 2.6 + hi, 7.0, Bt, z=0.38)
    on_wall("faxalven_lustro_z_wbudowanym_oswietleniem_29516705", "W", 2.6 + hi, 7.0, 1.3, Bt)
    against("toilet", "E", 5.4 - hi, 6.3, Bt)
    against("towel_radiator", "E", 5.4 - hi, 7.3, Bt, z=0.3)
    against(S("havback_szafka_wysoka_drzwi_40535000", "angsjon_szafka_wysoka_drzwi_40535081"), "S", 5.6 + hi, 3.0, Bt)
    put("kenney_plant_small1", 5.2, 7.7, room=Bt)
    Ln = "FF_Landing"
    against(S("kallax_rega_80275887", "kallax_rega_80275887"), "W", 5.4 + hi, 6.6, Ln)
    facing(S("strandmon_fotel_uszak_20343224", "oskarshamn_fotel_uszak_20523611"), 9.35, 6.3, 7.6, 6.3, Ln)
    put(S("tagarp_lampa_podogowa_do_czytania_40486387", "barlast_lampa_podogowa_10430368"), 9.7, 5.3, room=Ln)
    put("fejka_sztuczna_roslina_doniczkowa_00615249", 5.65, 7.6, room=Ln)
    put(S("tiphede_dywan_tkany_na_pasko_40456757", "lohals_dywan_tkany_na_pasko_30511288"), 7.6, 6.2, 90, room=Ln)
    pendant("ph_modern_ceiling_lamp_01", 7.6, 6.3, Ln)
    Bl = "FF_Balcony"
    put("tarno_sto_2_krzesa_na_zewnatrz_69898415", 5.9, -0.85, 90, room=Bl)
    put("kenney_plant_small3", 7.0, -1.35, room=Bl)

def furnish_terrace2():
    T = "GF_Terrace"
    put(S("norrmanso_sto_ogrodowy_30500794", "segeron_sto_ogrodowy_10510812"), 8.3, -1.6, 0, room=T)
    gc = S("lacko_krzeso_ogrodowe_60151840", "torparo_krzeso_z_podokietnikami_ogr_60595408")
    for xx in (7.75, 8.85):
        facing(gc, xx, -2.45, xx, -1.6, T); facing(gc, xx, -0.75, xx, -1.6, T)
    put("tveto_parasol_80468857", 8.3, -1.6, 0, room=T)
    put("segeron_lezak_79494857", 3.7, -1.7, 0, room=T)
    put("ph_planter_box_01", 9.7, -0.5, 90, room=T)
    put("ph_garden_gnome", 9.8, -2.9, -150, room=T)

_h2 = house2
def house2():
    global Z0, FLOOR
    W, D = _h2()
    if FURNISH:
        Z0, FLOOR = 0.0, 0; furnish_terrace2()
    return W, D

# ================================================================= SINGLE-STOREY HOUSE 15 x 10 m (150 m2)
def house1():
    W, D = 15.0, 10.0
    exterior2(W, D,
        south=[("window", 1.5, 1.6), ("patio", 4.5, 2.4), ("window", 8.75, 1.6), ("window", 13.0, 1.6)],
        north=[("window", 1.8, 1.2), ("window", 5.3, 1.2), ("hiwin", 8.2, 0.8), ("entry", 10.5, 1.0), ("hiwin", 12.3, 0.6), ("window", 14.0, 1.0)],
        west=[("window", 1.0, 1.0)],
        east=[("window", 4.8, 0.8), ("window", 9.3, 0.8)])
    wall("y55", (0, 5.5), (W, 5.5), TI, [("open", 3.2, 2.0), ("open", 10.4, 1.0), ("door", 12.0, 0.8)])
    wall("x65", (6.5, 0), (6.5, 5.5), TI, [("open", 2.75, 3.0)])
    wall("x11", (11, 0), (11, 5.5), TI)
    wall("y67", (0, 6.7), (W, 6.7), TI, [("door", 2.8, 0.8), ("door", 4.4, 0.8), ("door", 8.2, 0.8), ("open", 10.5, 1.8), ("door", 12.3, 0.8), ("door", 14.0, 0.8)])
    for x in (3.6, 7.0, 9.4, 11.6, 13.0): wall(f"x{x}", (x, 6.7), (x, D), TI)
    room("Living_room", "living", 0, 0, 6.5, 5.5, "wood")
    room("Kitchen_dining", "kitchen", 6.5, 0, 11, 5.5, "tile")
    room("Master_bedroom", "bedroom", 11, 0, W, 5.5, "wood")
    room("Corridor", "hallway", 0, 5.5, W, 6.7, "wood")
    room("Bedroom_2", "bedroom", 0, 6.7, 3.6, D, "wood")
    room("Kids_room", "kids", 3.6, 6.7, 7.0, D, "wood")
    room("Bathroom", "bathroom", 7.0, 6.7, 9.4, D, "bath")
    room("Hall", "hallway", 9.4, 6.7, 11.6, D, "wood")
    room("Utility", "utility", 11.6, 6.7, 13.0, D, "tile")
    room("Office", "office", 13.0, 6.7, W, D, "wood")
    deck("Terrace", -0.25, -3.4, 8.0, -0.13)
    if FURNISH: furnish_house1(W, D)
    return W, D

def furnish_house1(W, D):
    L = "Living_room"
    put(S("lokaltag_dywan_z_krotkim_wosiem_10623220", "jarnvag_dywan_z_krotkim_wosiem_20595698"), 2.9, 2.8, 90, room=L)
    put(S("kivik_sofa_3_osobowa_49440597", "landskrona_sofa_3_osobowa_29435337"), 4.4, 2.8, -90, room=L)
    tvb = S("fjallbo_szafka_pod_tv_90339290", "stockholm_2025_awa_tv_z_drzwiami_przesuwnymi_40586508")
    against(tvb, "W", 0, 2.8, L); bz = height(tvb)
    against(S("tv_sony_55", "tv_qled_65"), "W", 0, 2.8, L, z=bz)
    put(S("console_ps5", "console_xbox"), 0.2, 3.4, 90, bz, L)
    ct = S("borgeby_stolik_kawowy_70389356", "ph_industrial_coffee_table")
    put(ct, 2.9, 2.8, 0, room=L); put("ph_ceramic_vase_01", 2.9, 2.8, 0, height(ct), L)
    facing(S("dyvlinge_fotel_obrotowy_00581918", "havberg_fotel_obrotowy_70515109"), 2.6, 1.0, 2.9, 2.8, L)
    facing(S("lillesater_fotel_obrotowy_00618686", "ph_mid_century_lounge_chair"), 2.6, 4.6, 2.9, 2.8, L)
    put(S("lauters_lampa_podogowa_30405042", "sjomakt_lampa_podogowa_2_punktowa_70595667"), 5.0, 4.9, room=L)
    against(S("hemnes_witryna_z_3_szufladami_00596161", "billy_oxberg_witryna_79398832"), "E", 6.5 - hi, 4.85, L)
    put("fejka_sztuczna_roslina_doniczkowa_00600894", 0.5, 4.95, room=L)
    put("ph_potted_plant_01", 6.05, 0.4, room=L)
    on_wall(S("rodalm_ramka_70548925", "fiskbo_ramka_50297961"), "N", 5.5 - hi, 1.2, 1.4, L)
    curtain("S", 0, 1.5, L); against("radiator_column", "W", 0, 1.0, L, z=0.12)
    pendant(S("narrkolv_lampa_wiszaca_00594341", "ph_hanging_industrial_lamp"), 2.9, 2.8, L)
    K = "Kitchen_dining"
    kitchen_run("N", 5.5 - hi, 6.65, K, sign=1)       # y=5.5 wall, x 6.65..9.68
    against(S("fridge_side_by_side", "fridge"), "E", 11 - hi, 3.6, K)
    isl = S("vadholma_wyspa_kuchenna_20359154", "forhoja_barek_kuchenny_80035920")
    put(isl, 8.2, 3.55, 0, room=K)
    for xx in (7.85, 8.55): facing(S("rosentorp_stoek_barowy_z_oparciem_50618194", "ph_metal_stool_01"), xx, 2.95, xx, 3.55, K)
    put("ph_bananas", 8.3, 3.55, 30, height(isl), K)
    tb = S("tarsele_sto_rozkadany_70581359", "skogsta_sto_70419264")
    put(tb, 8.6, 1.35, 0, room=K)
    ch = S("lisabo_krzeso_00457235", "krylbo_krzeso_60566745")
    for xx in (7.9, 8.6, 9.3):
        facing(ch, xx, 0.55 if STYLE == "scandi" else 0.45, xx, 1.35, K); facing(ch, xx, 2.15 if STYLE == "scandi" else 2.25, xx, 1.35, K)
    put("ph_wooden_bowl_01", 8.6, 1.35, 0, height(tb), K)
    for xx in (7.9, 9.3): pendant(S("stockholm_2025_lampa_wiszaca_90585988", "skurup_lampa_wiszaca_80407114"), xx, 1.35, K)
    curtain("S", 0, 8.75, K); against("radiator_column", "S", 0, 10.4, K, z=0.12)
    M = "Master_bedroom"
    put(S("jarnvag_dywan_z_krotkim_wosiem_20595698", "lokaltag_dywan_z_krotkim_wosiem_10623220"), 13.2, 2.6, 90, room=M)
    bed_with_ns(S("tarnkullen_tapicerowana_rama_ozka_99569205", "tonstad_rama_ozka_89577729"), S("fagelfjallet_stolik_nocny_40627684", "gullaberg_stolik_nocny_20561740"),
                S("snobyar_lampa_stoowa_50450401", "blidvader_lampa_stoowa_80501258"), "E", W, 2.6, M)
    against(S("pax_flisberget_szafa_39304128", "pax_bergsbo_szafa_19127297"), "W", 11 + hi, 4.3, M)
    against(S("hemnes_komoda_8_szuflad_10239280", "storklinta_komoda_6_szuflad_70627550"), "W", 11 + hi, 1.6, M)
    put("fejka_sztuczna_roslina_doniczkowa_00615249", 14.6, 0.35, room=M)
    curtain("S", 0, 13.0, M); against("radiator_column", "S", 0, 13.0, M, z=0.12)
    pendant("ikea_ceiling_lamp", 13.0, 2.6, M)
    C = "Corridor"
    put(S("tiphede_dywan_tkany_na_pasko_40456757", "lohals_dywan_tkany_na_pasko_30511288"), 6.0, 6.1, 90, room=C)
    for xx in (2.0, 6.0, 13.5): pendant("ph_modern_ceiling_lamp_01", xx, 6.1, C)
    B2 = "Bedroom_2"
    put("kenney_rug_rectangle", 1.6, 8.4, 90, room=B2)
    against(S("vihals_rama_ozka_40602424", "neiden_rama_ozka_40395245"), "W", 0, 8.6, B2)
    against(S("knarrevik_stolik_nocny_00576318", "gullaberg_stolik_nocny_20561740"), "W", 0, 7.55, B2)
    against(S("brimnes_szafa_2_drzwi_40400478", "kleppstad_szafa_3_drzwi_00441758"), "E", 3.6 - hi, 8.9, B2)
    curtain("N", D, 1.8, B2)
    pendant("ikea_ceiling_lamp", 1.8, 8.35, B2)
    KD = "Kids_room"
    put(S("lokaltag_dywan_z_krotkim_wosiem_10623220", "jarnvag_dywan_z_krotkim_wosiem_20595698"), 5.4, 8.3, 0, room=KD, scale=(0.7, 0.7, 1))
    against(S("kura_dwustronne_ozko_80253809", "slakt_rama_ozka_z_3_poj_na_posciel_89386070"), "W", 3.6 + hi, 8.9, KD)
    against("trofast_rega_z_pojemnikami_89574467", "E", 7.0 - hi, 9.3, KD)
    against("flisat_biurko_dla_dziecka_30609181", "E", 7.0 - hi, 7.8, KD)
    facing("mammut_krzeseko_dzieciece_40365371", 6.05, 7.8, 7.0, 7.8, KD)
    put("djungelskog_pluszak_00402808", 4.9, 7.3, 30, room=KD)
    put("duktig_kosz_warzyw_14_szt_10185748", 5.6, 7.5, 0, room=KD)
    put("ph_rubber_duck_toy", 5.2, 8.6, 40, room=KD)
    pendant("ikea_ceiling_lamp", 5.3, 8.3, KD)
    Bt = "Bathroom"
    put("shower_cabin", 7.06 + 0.45, D - 0.48, 0, 0, Bt, scale=(0.9 / 1.181, 0.9 / 0.95, 1.0))
    against("toilet", "E", 9.4 - hi, 9.4, Bt)
    against(S("angsjon_szafka_umywalkowa_z_szufladami_30535086", "enhet_szafka_umywalkowa_z_szufladami_50623020"), "E", 9.4 - hi, 7.6, Bt, z=0.38)
    on_wall(S("nysjon_poka_z_lustrem_60470837", "faxalven_lustro_z_wbudowanym_oswietleniem_29516705"), "E", 9.4 - hi, 7.6, 1.3, Bt)
    against("towel_radiator", "W", 7.0 + hi, 7.7, Bt, z=0.3)
    Hh = "Hall"
    against(S("gullaberg_szafka_na_buty_2_przegrody_40587697", "brusali_szafka_na_buty_3_przegrody_80480393"), "W", 9.4 + hi, 8.6, Hh)
    against("jonaxel_kombinacja_szafy_49297660", "E", 11.6 - hi, 8.6, Hh)
    on_wall("hovet_lustro_70515915", "W", 9.4 + hi, 7.4, 0.02, Hh)
    put("kenney_rug_doormat", 10.5, 9.6, 0, room=Hh)
    U = "Utility"
    against("washing_machine", "W", 11.6 + hi, 9.4, U); against("dryer", "W", 11.6 + hi, 9.4, U, z=height("washing_machine") + 0.005)
    against("hyllis_rega_00278578", "E", 13.0 - hi, 8.3, U)
    put("nattgibba_kosz_na_pranie_30531936", 12.6, 9.7, 0, room=U, scale=(0.6, 0.6, 1))
    O = "Office"
    dk = S("micke_biurko_90214308", "lagkapten_alex_biurko_69416817")
    against(dk, "E", W, 7.7, O); dz = height(dk)
    facing(S("millberget_krzeso_obrotowe_70489394", "jarvfjallet_krzeso_biurowe_z_podokietnikami_10605570"), 14.1, 7.7, W, 7.7, O)
    put("laptop", W - 0.3, 7.7, -90, dz, O)
    put(S("navlinge_lampa_biurkowa_led_50404918", "skurup_lampa_biurkowa_80516778"), W - 0.2, 8.25, -90, dz, O)
    against(S("gersby_rega_70261131", "baggebo_rega_20436713"), "W", 13.0 + hi, 8.8, O)
    pendant("ikea_ceiling_lamp", 14.0, 8.35, O)
    Tz = "Terrace"
    put(S("nammaro_sofa_narozna_3_osobowa_09575215", "revskar_3_osobowy_zestaw_mebli_19544624"), 1.4, -1.8, 0, room=Tz)
    put("krokholmen_stolik_kawowy_ogrodowy_80336466", 1.4, -2.9, 0, room=Tz)
    put(S("askholmen_sto_ogrodowy_50535679", "nammaro_sto_ogrodowy_20510307"), 5.6, -1.7, 0, room=Tz)
    gc = S("askholmen_krzeso_ogrodowe_20557502", "nammaro_krzeso_z_podokietnikami_ogr_90511105")
    for xx in (5.2, 6.0):
        facing(gc, xx, -2.45, xx, -1.7, Tz); facing(gc, xx, -0.95, xx, -1.7, Tz)
    put("tveto_parasol_80468857", 5.6, -1.7, 0, room=Tz)
    put("ph_planter_box_02", 7.3, -3.0, 0, room=Tz)
    put("ph_watering_can_metal_01", 7.6, -2.5, 30, room=Tz)

# ================================================================= scene, export, render
bpy.ops.wm.read_factory_settings(use_empty=True)
FURNISH = MODE == "furnished"
C_SHELL, C_FURN = coll("Shell"), coll("Furniture")
C_LIB = coll("_IKEA_library"); bpy.context.view_layer.layer_collection.children["_IKEA_library"].exclude = True
M_WALL = mat(f"Wall_{STYLE}", PAL["wall"], 0.8); M_GLASS = mat("Glass", (0.8, 0.9, 1.0), 0.02, alpha=0.25, transmission=1.0)
M_FRAME = mat("Frame", (0.95, 0.95, 0.95) if STYLE == "scandi" else (0.08, 0.08, 0.08), 0.4)
M_DOOR = mat("DoorLeaf", (0.9, 0.88, 0.84) if STYLE == "scandi" else (0.12, 0.11, 0.10), 0.5)
M_PORC = mat("Porcelain", (0.97, 0.97, 0.97), 0.15); M_TOP = mat("Worktop", (0.75, 0.62, 0.45) if STYLE == "scandi" else (0.10, 0.10, 0.10), 0.35)
M_CHROME = mat("Chrome", (0.9, 0.9, 0.9), 0.15, metal=1.0)
W, D = {"house2": house2, "house1": house1}[LAYOUT]()
setup_render()
tag = f"{LAYOUT}_{STYLE}_{'furnished' if FURNISH else 'shell'}"
sc = bpy.context.scene; sc["layout"] = LAYOUT; sc["style"] = STYLE
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
floors = 2 if LAYOUT == "house2" else 1
Z_TOP = (floors - 1) * 3.0 + H
indoor = [r for r in ROOMS if not r.get("outdoor")]
json.dump(dict(layout=LAYOUT, style=STYLE, furnished=FURNISH, footprint_m=[W, D], floors=floors, storey_height_m=3.0 if floors == 2 else None,
               rooms=ROOMS, placed=PLACED, total_area_m2=round(sum(r["area_m2"] for r in indoor), 2),
               outdoor_area_m2=round(sum(r["area_m2"] for r in ROOMS if r.get("outdoor")), 2)),
          open(f"{ROOT}/layouts/{tag}.json", "w"), indent=1)
def fl(o):
    while o is not None:
        if "floor" in o: return o["floor"]
        o = o.parent
    return 0
def is_ceiling(o): return bool(o.get("ceiling") or (o.parent is not None and o.parent.get("ceiling")))
views = [("top", None, "top"), ("iso", None, "iso")] if floors == 1 else [("top_gf", 0, "top"), ("top_ff", 1, "top"), ("iso", None, "iso"), ("iso_gf", 0, "iso")]
for name, only, kind in views:
    for o in list(C_FURN.all_objects) + list(C_SHELL.all_objects):
        hide = False
        if only is not None and fl(o) > only: hide = True
        if only is not None and only == 1 and fl(o) < 1 and kind == "top": hide = True
        if kind == "top" and is_ceiling(o): hide = True
        o.hide_render = hide
    ys = min([-0.3] + [r["bounds"][1] for r in ROOMS if r.get("outdoor") and (only is None or r["floor"] <= only)])
    ztop = (Z_TOP if only is None else (only * 3.0 + H)) if kind == "iso" else 0.0
    camera_fit(kind, (-0.3, ys if kind == "iso" else -0.3, -0.2, W + 0.3, D + 0.3, ztop) if kind == "iso" else (-0.3, min(ys, -0.3), 0, W + 0.3, D + 0.3, 0))
    render(f"{ROOT}/previews/{tag}_{name}.png")
print("DONE", tag)
