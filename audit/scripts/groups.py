G = {
 "seating": "armchair bar_stool bench chair dining_chair footstool garden_bench garden_chair hallway_bench kids_chair office_chair pouffe stool step_stool bathroom_stool sun_lounger daybed",
 "sofa": "sofa sofa_bed sofa_corner sofa_modular garden_sofa",
 "bed": "bed bed_double bed_single bunk_bed crib kids_bed loft_bed headboard mattress playpen",
 "table": "bar_table coffee_table console_table desk dining_table dining_set garden_table kids_desk kids_table side_table table dressing_table kitchen_island pool_table balcony_furniture garden_furniture",
 "storage": "bookshelf cabinet chest_of_drawers cupboard display_cabinet drawer_unit hallway_storage kids_storage office_cabinet shelving_unit shoe_cabinet sideboard storage_system toy_storage tv_bench tv_storage wardrobe wall_cabinet wall_shelf nightstand changing_table locker storage_chest bathroom_cabinet bathroom_shelf bathroom_storage kitchen_base_cabinet kitchen_cabinet kitchen_corner_cabinet kitchen_oven_cabinet kitchen_shelf kitchen_sink_cabinet kitchen_tall_cabinet kitchen_wall_cabinet kitchen_front kitchen_trolley garden_storage clothes_rack coat_rack drying_rack room_divider kitchen worktop",
 "lamp": "ceiling_fan ceiling_lamp chandelier desk_lamp floor_lamp kids_lamp lamp lamp_shade outdoor_lamp pendant_lamp spotlight table_lamp wall_lamp",
 "textile": "bath_mat bedding bedspread curtains cushion doormat kids_rug pillow rug runner_rug shower_curtain tablecloth throw towel blinds",
 "decor": "basket books bottle candle candle_holder clock decor picture_frame plant plant_pot plant_stand sculpture vase wall_art mirror bathroom_mirror soft_toy toy garden_decor tray storage_box laundry_basket bin wall_hook hallway_accessory desk_accessory bathroom_accessory garden_accessory parasol easel suitcase pet",
 "kitchenware": "cookware cutlery food food_storage glassware kitchen_accessory tableware",
 "appliance": "air_conditioner air_purifier appliance boiler coffee_machine cooker cooker_hood dishwasher dryer extractor_hood fan fridge grill heater hob kettle kitchen_appliance kitchen_appliance_small microwave oven toaster vacuum washing_machine water_cooler sewing_machine cleaning tools utility",
 "electronics": "camera computer desktop_pc electronics game_console headphones hifi keyboard laptop monitor mouse phone printer projector radio record_player router smart_speaker soundbar speaker tv typewriter electrical",
 "instrument": "guitar instrument piano",
 "fixture": "bathroom_sink bathroom_tap bathroom_vanity bathtub curtain_rail decking door fireplace kitchen_sink kitchen_tap radiator shower stairs toilet towel_rail ventilation window",
}
CG = {c: g for g, s in G.items() for c in s.split()}
