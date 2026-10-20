# interior-models

A static asset API, served from GitHub Pages, for an interior-architect demo app that imports models into Blender.
It contains two procedurally built layouts (an apartment of about 50 m² and a single-storey house of about 100 m²)
plus 50 IKEA furniture models, 40 home appliances / electronics (AGD/RTV) and 10 sanitary/heating fixtures in GLB format.
The furnished layouts use all of these (TV wall, kitchen appliances, washer/dryer, PC desk, real toilet/shower/bathtub…).

> **Personal / demo use only.** The IKEA 3D models are © Inter IKEA Systems B.V. They were downloaded from public IKEA product pages.
> Appliance/fixture models from **Objaverse 1.0** (Sketchfab uploads) are under the Creative Commons licence recorded per asset
> (`license`, `author`, `source_url`): CC BY / CC BY-SA require attribution, and **CC BY-NC** items (`tv_qled_65`, `espresso_machine`) are non-commercial only.
> **Poly Haven** models are CC0. See the [Credits](#credits) table and `/api/credits.json`.

**Gallery:** https://iandamai720-cmyk.github.io/interior-models/
**Base URL:** `https://iandamai720-cmyk.github.io/interior-models`

GitHub Pages sends `Access-Control-Allow-Origin: *`, so your app can call every endpoint directly from a browser.

## Endpoints (all GET, all static JSON)
| Endpoint | Content |
|---|---|
| `/catalog.json` | Full catalog: `{version, generated, base_url, assets:[...]}` with every layout and every furniture item |
| `/api/index.json` | Lists all endpoints below, with the available categories, rooms, styles and colours |
| `/api/layouts.json` | Summary of each layout (id, area_m2, style, furnished, rooms, url, preview_url) |
| `/api/layouts/{id}.json` | One layout in full: rooms with their bounds, furniture used, and the GLB, .blend, metadata and preview URLs |
| `/api/assets.json` | Summary of every asset (all types) |
| `/api/furniture.json` | Summary of each furniture item |
| `/api/furniture/{id}.json` | One furniture item in full (the id is `ikea-<article number>`, e.g. `ikea-00263850`) |
| `/api/furniture/{category}.json` | Furniture in one category, e.g. `sofa`, `bed_double`, `lamp`, `kitchen` (same data as `/api/furniture/category/{category}.json`) |
| `/api/furniture/room/{room}.json` | Furniture for one room type: `living`, `bedroom`, `dining`, `kitchen`, `bathroom`, `hallway`, `office` |
| `/api/appliances.json`, `/api/appliances/{id}.json` | Appliances & electronics (id e.g. `objaverse-tv-sony-55`, `polyhaven-ceiling-fan`, `ikea-10467093`) |
| `/api/appliances/{category}.json` | e.g. `tv`, `fridge`, `oven`, `hob`, `microwave`, `dishwasher`, `extractor_hood`, `washing_machine`, `dryer`, `coffee_machine`, `kettle`, `toaster`, `soundbar`, `speaker`, `smart_speaker`, `game_console`, `desktop_pc`, `monitor`, `keyboard`, `mouse`, `laptop`, `router`, `vacuum`, `air_conditioner`, `fan`, `air_purifier` (also `/api/appliances/category/…`, `/api/appliances/room/{room}.json`) |
| `/api/fixtures.json`, `/api/fixtures/{id}.json`, `/api/fixtures/{category}.json` | Sanitary & heating: `toilet`, `bathtub`, `shower`, `bathroom_sink`, `bathroom_tap`, `kitchen_sink`, `kitchen_tap`, `radiator` |
| `/api/category/{category}.json`, `/api/room/{room}.json` | Any type of model by category / room |
| `/api/licenses/{licence}.json`, `/api/sources/{source}.json` | Models by licence (`cc-by-4-0`, `cc-by-nc-4-0`, `cc0-1-0`, …) or source (`ikea`, `objaverse-1-0-sketchfab`, `poly-haven`) |
| `/api/credits.json` | Attribution list for all non-IKEA models |
| `/api/styles/{style}.json` | Layouts and furniture in one style: `scandi`, `dark`, `dark-industrial`, `wood-natural`, `neutral` |
| `/api/colours/{colour}.json` | Assets in one colour (slugified), e.g. `white`, `black`, `beige`, `light-oak` |
| `/catalog.db` | SQLite copy of the catalog. Tables: `assets`, `furniture` (all placeable models, with `type`, `source`, `author`, `license`), `layouts`, `rooms`, `layout_furniture`, `tags`; views `appliances`, `fixtures` |
| `/furniture/*.glb`, `/appliances/*.glb`, `/layouts/*.glb|.blend`, `/previews/**.png` | The asset files themselves (each asset's `url` / `urls` / `preview_url` field points here) |
| `/blender/import_from_catalog.py` | Blender helper script (see below) |

Layout ids: `apartment-scandi-furnished`, `apartment-dark-furnished`, `apartment-scandi-shell`,
`house-scandi-furnished`, `house-dark-furnished`, `house-scandi-shell`.

### Asset fields
Common to all assets: `id, type (layout|furniture|appliance|fixture), name, style, colours[], tags[], url, preview_url, api_url, file_size_bytes`.
Layouts add: `area_m2, footprint_m, rooms[{name,type,area_m2,bounds}], bedrooms, furnished, urls{glb,blend,meta}, preview_urls{top,iso}, furniture_used[]`.
Furniture / appliances / fixtures add: `category, room, colour, material, dimensions_m{x,y,z}, triangles, source, source_url, author, license, license_note`,
plus `article_number, full_name, dimensions_listed` for IKEA items, `objaverse_uid` for Objaverse items and `mount` (e.g. sink rim height) where relevant.
Layouts also list `credits[]` for the non-IKEA models they use.
Units are metres. Every model GLB is Z-up in Blender, with its footprint centred on the origin, the floor at z=0, and the front facing **−Y**.

## Query examples
Static hosting can't filter on the server. Either use one of the pre-built index files above, or filter `catalog.json` on the client.

```bash
B=https://iandamai720-cmyk.github.io/interior-models
curl -s $B/api/layouts.json | jq '.[] | select(.area_m2 >= 40 and .area_m2 <= 60 and .furnished) | {id, url}'
curl -s $B/api/furniture/sofa.json | jq '.[] | {id, name, url}'
curl -s $B/api/styles/scandi.json | jq '[.[] | select(.type=="furniture")] | length'
curl -s $B/catalog.json | jq '.assets[] | select(.type=="furniture" and (.colours|index("white"))) | .id'
curl -sO $B/catalog.db && sqlite3 catalog.db "select f.full_name, a.url from furniture f join assets a using(id) where f.category='desk'"
```
```js
const B = "https://iandamai720-cmyk.github.io/interior-models";
const { assets } = await (await fetch(`${B}/catalog.json`)).json();
const beds = assets.filter(a => a.type === "furniture" && a.category.startsWith("bed") && a.style === "scandi");
const glb = await (await fetch(beds[0].url)).arrayBuffer();     // e.g. hand to three.js GLTFLoader.parse
```
```python
import json, urllib.request
B = "https://iandamai720-cmyk.github.io/interior-models"
layouts = json.load(urllib.request.urlopen(f"{B}/api/layouts.json"))
house = json.load(urllib.request.urlopen(f"{B}/api/layouts/house-scandi-furnished.json"))
print([r["name"] for r in house["rooms"]], house["urls"]["glb"])
```

## Blender helper: `blender/import_from_catalog.py`
Using the **Scripting tab:** open the file, set `RUN_ID` (or `RUN_FILTER`) in the CONFIG block, then press *Run Script*.
With no setting it just prints the asset list to the system console.
To use it as a module from the Python console:
```python
import sys; sys.path.append("/path/to/blender")       # folder that contains the script
import import_from_catalog as ic
ic.list_assets(type="furniture", category="sofa")
ic.list_assets(type="appliance", category="tv")
ic.import_asset("objaverse-washing-machine", location=(2, 0, 0))
ic.import_asset("ikea-00263850", location=(1, 0, 0), rotation_deg=90)            # BILLY
ic.import_filtered(type="furniture", style="scandi", room="bedroom", limit=6)     # lays matches out in a row
ic.import_asset("apartment-scandi-furnished")                                    # whole layout as GLB
ic.import_asset("house-dark-furnished", fmt="blend")                             # appends the original .blend collections
```
Headless:
`blender -b --python import_from_catalog.py -- --type furniture --category lamp --save lamps.blend`
(other options: `--id`, `--style`, `--colour`, `--min-area`, `--max-area`, `--list`, `--format blend`).
Downloads are cached in `~/.cache/interior-models`; you can change this with `INTERIOR_MODELS_CACHE`.

## Repository layout
- `furniture/`: 44 IKEA GLBs. `_fetch_log.json` records the source URLs.
- `appliances/`: 56 appliance / electronics / fixture / lamp GLBs (≤11 MB each, textures ≤2K, real scale). `_sources.json` and `_records.json` record source, author and licence. Thumbnails in `previews/appliances/`.
- `layouts/`: for each layout variant, a `.blend`, a `.glb` and a `.json` file with rooms and furniture placements.
- `previews/`: top-down and isometric renders of each layout, and `previews/furniture/` thumbnails.
- `scripts/`:
  - `fetch_ikea.py`: IKEA search, then the product page's JSON-LD `3DModel` block, then the GLB download.
  - `build_layout.py`: the procedural shell and furniture placement. Run it as `blender -b --python scripts/build_layout.py -- <apartment|house> <scandi|dark> <furnished|shell>`.
  - `fetch_ikea_appliances.py`, `objaverse_candidates.py`: appliance sourcing (IKEA + Objaverse LVIS/name search); `normalize_appliances.py` (+ `appliance_fixes.json`): Blender normalisation (metres, origin bottom-centre, front −Y, decimation, 2K textures, thumbnails); `appliance_records.py`: metadata.
  - `make_catalog.py`, then `build_api.py`: rebuild the catalog, the API files and the SQLite db.
- `index.html`: a gallery with filters for type, category, room, source, style, colour, area and text; shows source/author/licence per model.

Kitchen worktops are still simple procedural boxes. The layout .blend/.glb files use preview-grade copies of the models
(textures ≤512 px, meshes ≤20k triangles); the individual GLBs in `furniture/` and `appliances/` are full quality.

## Credits
| Model | Source title | Author | Licence | Link |
|---|---|---|---|---|

| `objaverse-fridge-side-by-side` French-door fridge freezer (stainless) | French Door Refrigerator - Stainless | Smokahontas | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/ebe62ed6dd9b446a9c9b7d7d6a8086e7) |
| `objaverse-washing-machine` Front-load washing machine (Whirlpool-style) | Washing Machine Whirpool | Francesco Coldesina | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/0e0f28026fec40da8c0f1dfd7a8dd45f) |
| `objaverse-dryer` Tumble dryer | Washer Dryer Machine | rhcreations | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/8358b47f171d43e98f473083ce55b36e) |
| `objaverse-microwave-white` Microwave oven (white) | Microwave Rigged (Free - NonCommercial) | 3DHaupt | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/951cea7c961541d6a27a9d1abca27ee9) |
| `objaverse-microwave-black` Microwave oven (black, Samsung-style) | SamMicroWm | anybody | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/69a33a97aa884e98be90b1cf87715cc2) |
| `objaverse-oven-builtin` Built-in oven 60 cm | Built-in oven | 3DDomino | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/50be70931dcb4a838b906382233a28f1) |
| `objaverse-dishwasher` Freestanding dishwasher 60 cm | Dishwasher 411 | 1-3D.com | CC BY-SA 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/42493d4758bb4f128168ea9cc09f3266) |
| `objaverse-extractor-hood-steel` Chimney extractor hood (stainless) | Kitchen Hood Model 3D fbx | GLOBALO | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/f2de7240cfe64ebebff8f6d78f7f7879) |
| `objaverse-extractor-hood-black` Chimney extractor hood (black) | Kitchen Hood Model 3D fbx | GLOBALO | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/731339229a10410b9a530cb8c647cd27) |
| `objaverse-kitchen-sink-steel` Stainless inset kitchen sink | Kitchen Sink | HippoStance | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/504248ed68e3480a807aced6f002b2d5) |
| `objaverse-kitchen-tap` Kitchen mixer tap | Kitchen Tap | ethan_garden | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/21d028dd26434c7c848260a9574b4517) |
| `objaverse-coffee-machine-drip` Drip coffee maker | Coffee Maker | Ryan_Nein | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/383923d4412f4b66937d9c1779a9a0a2) |
| `objaverse-espresso-machine` Espresso machine (cream) | Coffee machine | DailyArt | CC BY-NC 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/a6e19d641a2642b4b9ddb68b0c5f3c56) |
| `objaverse-electric-kettle` Electric kettle (Electrolux) | Electrolux electric kettle | gorzi | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/0445b3baee4b4a6fb40d7e03be4e8550) |
| `objaverse-toaster` 2-slice toaster | Toaster | Artem P | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/0dd620043178479db6752ab103b1e04e) |
| `objaverse-tv-qled-65` Samsung QLED TV 65" | Samsung TV | cgwings | CC BY-NC 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/46a391dea9af479b97dd60fd59323318) |
| `objaverse-tv-sony-55` Sony Bravia X900C TV 55" | SONY Bravia X900C 4K TV | 3D Share | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/c78af37dc5364be2a31d1a2c7cc1edc3) |
| `objaverse-soundbar` Q Acoustics M3 soundbar | Q-Acoustics M3 Soundbar | Q-Acoustics | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/7cf33febf603401586ffa5e18c312d31) |
| `objaverse-speakers-tower` Floor-standing speaker pair | Sound system | yryabchenko | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/725273fbdde54a1babaf6ce1c95b96b4) |
| `objaverse-speakers-bookshelf` Jamo S803 bookshelf speakers | Jamo S803 speakers | gorzi | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/47c1da3925ee41a39befc061997d8291) |
| `objaverse-smart-speaker-home` Google Home smart speaker | Google Home | koss2712 | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/5388f20d16064e1fae2741e1c26c9fa3) |
| `objaverse-smart-speaker-dot` Amazon Echo Spot smart speaker | Amazon Alexa Echo Spot Animated Low Poly | layne | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/10949d794d9a436ca46b88fa9ce6279e) |
| `objaverse-console-ps5` PlayStation 5 console | PS5 | rtql8d | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/d788de3735964151a3e24fd59c0f1956) |
| `objaverse-console-xbox` Xbox Series X console | XBOX SERIES X | Abdurhman Aljakthami | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/29460c063c7b4046aea8be633f90210e) |
| `objaverse-gamepad` DualSense controller | Playstation 5 Dualsense | AHarmlessPotato | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/878c1f882808477ab81c2fe86d5a3936) |
| `objaverse-pc-tower` Fractal Design Meshify C PC | Fractal Design. Meshify C  -  PC Case | MUSHROOM_BUILDS | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/a46526af2ac84fa098edc3f01c012450) |
| `objaverse-monitor-27` Acer 27" monitor | Acer K222HQL Model Monitor | bahayalniz | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/864c7f9afa2e49e1a64ad05b2a29f66a) |
| `objaverse-keyboard` Mechanical keyboard | Keyboards | 3D Share | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/a25c537932e84ef693de2cdbfc9dd22d) |
| `objaverse-mouse` Computer mouse | Lowpoly Mouse | khanhnguyen1189 | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/e0bc8c1d5c8f4be0af37ea852d42d6d9) |
| `objaverse-laptop` Lenovo laptop | lenovo | elyas_baloch | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/565aea3028e54b4883e89577c971a43c) |
| `objaverse-router` Wi-Fi router | Router | va3dmodels | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/1a5a5dbdb6de43f7aa9dfa2f31b326b9) |
| `objaverse-stick-vacuum` Cordless stick vacuum | Vacuum Cleaner | Nommoc | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/bc4f9e3319ec4a2f8fc6d0b5aa99b4cb) |
| `objaverse-robot-vacuum` Robot vacuum cleaner | Robot vacuum Cleaner Rob-vac | darkfrei | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/7d904c05d4204d19a2940d9d6f21ef8d) |
| `objaverse-air-conditioner` Daikin wall-mounted AC split unit | Air condition Daikin | maxsbond.work | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/26b0f7c8472741f4b85b889cf3b1d870) |
| `objaverse-standing-fan` Pedestal fan | Electric Fan | Lillya | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/c27f71e432b84353a245fb9b65dcdbf2) |
| `objaverse-radiator-column` Column radiator (cast iron) | Old Radiator | thethieme | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/8a1a2e0263aa401591c1e87d824a79ef) |
| `objaverse-towel-radiator` Heated towel rail (chrome) | Heated towel rail | nester1279 | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/b3636221263546c4ae457b54de6e5d39) |
| `objaverse-toilet` Wall-hung toilet with cistern | Toilet | HippoStance | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/132a8ee2af3a40d39d270fbed3d3666c) |
| `objaverse-bathtub-freestanding` Freestanding bathtub (Angelo) | Angelo Freestanding Bath | tissinouk | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/dcd691724f6b4d29a6d16def24d14e6e) |
| `objaverse-shower-cabin` Corner shower cabin | Shower Cabin | Heliona | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/e2c6a8dd490e4e4398378e1f6c9121a8) |
| `objaverse-bathroom-sink` Bathroom basin | Simple Sink | Andrew.Mischenko | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/73bda35b6e7a499a80427fc1b049b192) |
| `objaverse-bathroom-tap` Basin mixer tap | Washbasin mixer | nester1279 | CC BY 4.0 | [Objaverse 1.0 (Sketchfab)](https://sketchfab.com/3d-models/64e227842c254a2a81f6f9930b7d791f) |
| `polyhaven-ceiling-fan` Ceiling fan | Ceiling Fan | Ulan Cabanilla | CC0 1.0 | [Poly Haven](https://polyhaven.com/a/ceiling_fan) |
| `polyhaven-desk-lamp-arm-01` Desk lamp (arm) | Desk Lamp Arm 01 | Yann Kervran, Kuutti Siitonen | CC0 1.0 | [Poly Haven](https://polyhaven.com/a/desk_lamp_arm_01) |
| `polyhaven-modern-ceiling-lamp-01` Modern ceiling pendant | Modern Ceiling Lamp 01 | James Ray Cock | CC0 1.0 | [Poly Haven](https://polyhaven.com/a/modern_ceiling_lamp_01) |
| `polyhaven-gaming-console` Retro gaming console | Gaming Console | Sean Buckley | CC0 1.0 | [Poly Haven](https://polyhaven.com/a/gaming_console) |

Plus 54 IKEA product models (© Inter IKEA Systems B.V., personal/demo use only); each links to its IKEA product page in `source_url`.
