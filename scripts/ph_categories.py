import re
SKIP={"CashRegister_01","WetFloorSign_01","cardboard_box_01","plastic_container","industrial_storage_cart","ceiling_fan","modern_ceiling_lamp_01","gaming_console","desk_lamp_arm_01","GothicBed_01","GothicCabinet_01"}
RULES=[  # (regex on id, category, room)
(r"chandelier",'pendant_lamp','living'),(r"hanging_industrial_lamp|caged_hanging",'pendant_lamp','kitchen'),(r"sconce|wall_lamp",'wall_lamp','living'),
(r"pipe_lamp|oil_lamp|diya",'table_lamp','living'),(r"candle",'candle_holder','living'),
(r"sofa|day_bed",'sofa','living'),(r"arm_?chair|lounge_chair|GreenChair|Rockingchair",'armchair','living'),(r"Ottoman",'pouffe','living'),
(r"bar_chair|metal_stool_0[13]",'bar_stool','kitchen'),(r"stool",'stool','living'),(r"monobloc|outdoor_table|picnic",'garden_furniture','garden'),
(r"SchoolChair|SchoolDesk",'kids_desk','kids'),(r"chair",'dining_chair','dining'),(r"bench",'bench','hallway'),
(r"Nightstand|nightstand",'nightstand','bedroom'),(r"coffee_table|CoffeeTable|tea_table",'coffee_table','living'),(r"side_table|WoodenTable_02",'side_table','living'),
(r"office_desk",'desk','office'),(r"console",'console_table','hallway'),(r"dining_table|round_wooden_table_01|painted_wooden_table|WoodenTable_01|wooden_table_02|WoodenTable_03|gallinera_table|round_wooden_table_02",'dining_table','dining'),
(r"small_wooden_table",'side_table','living'),(r"CoffeeCart",'kitchen_trolley','kitchen'),
(r"shelves|Shelf_01",'shelving_unit','living'),(r"commode|Commode|drawer",'chest_of_drawers','bedroom'),(r"cabinet",'cabinet','living'),
(r"mirror",'mirror','hallway'),(r"picture_frame",'picture_frame','living'),(r"clock",'clock','living'),(r"dartboard|chalkboard",'decor','kids'),
(r"vase",'vase','living'),(r"planter|potted|pot_clay",'plant_pot','living'),(r"potted_plant",'plant','living'),
(r"book|binder|stationery",'books','office'),(r"pillow",'cushion','living'),(r"basket",'basket','living'),
(r"duck|chess|sungka|Ukulele",'toy','kids'),(r"gnome",'garden_decor','garden'),(r"watering",'garden_decor','garden'),
(r"statue|bust|elephant|shell",'decor','living'),(r"suitcase",'decor','bedroom'),
(r"laptop",'electronics','office'),(r"[Tt]elevision",'tv','living'),(r"microwave|kettle",'kitchen_appliance_small','kitchen'),
(r"food_|banana|lemon|onion|potato|cake|croissant|buns",'food','kitchen'),
(r"tea_set|goblet|jug|bowl|plate|pan|pot_|cutting|spoon|wine",'tableware','kitchen'),(r"brass_pot|ceramic_pot",'decor','living'),
]
def classify(k):
    if k in SKIP: return None
    for rx,c,r in RULES:
        if re.search(rx,k): return c,r
    return 'decor','living'
