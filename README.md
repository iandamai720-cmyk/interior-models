# interior-models

A static asset API, served from GitHub Pages, for an interior-architect demo app that imports models into Blender.

**Version 2 (turn 4):** 1309 catalog entries
* **886 models with their own GLB file:** 542 IKEA, 173 Poly Haven, 129 Kenney and 42 Objaverse.
  * IKEA items carry PLN prices, IKEA PL and UK links and colour variants.
  * The other sources fill gaps: decor, plants, books, kids, garden, stairs, doors, windows, curtains and kitchen accessories.
* **411 Polish store products** from Agata, BRW, JYSK, VOX, Bodzio, Komfort, Meble Wójcik, Castorama and Leroy Merlin.
  * Each has a link and a price where the store publishes one.
  * They have no own 3D file (`has_own_model:false`). Each points to the closest library model via `similar_model_id`.
* **12 layouts:**
  * a 50 m² apartment and a 100 m² house from v1;
  * a single-storey house of ~150 m² (`house1-*`);
  * a two-storey house of 175.75 m² with stairs and a terrace (`house2-*`).
  * Each comes in three variants: scandi furnished, dark furnished and scandi shell.

> **Personal / demo use only.**
> * The IKEA 3D models are © Inter IKEA Systems B.V. They were downloaded from public IKEA product pages.
> * Objaverse items are under the CC licence recorded per asset. `tv_qled_65` and `espresso_machine` are **CC BY-NC**.
> * Poly Haven and Kenney models are CC0.
> * Store names, prices and links were collected on 2026-10-23 and will go stale.

**Gallery:** https://iandamai720-cmyk.github.io/interior-models/
The gallery has filters for type, store, own/similar model, room, category, style, source, colour, PLN price and m², plus search. Each card shows its price and its PL and UK links.

**Spreadsheet:** `sklepy.xlsx` / `assets.csv` in this repo and [Google Sheet](https://docs.google.com/spreadsheets/d/1rqNTtskPRN7ftZ1w9KNB6eIjsTL1jFq6U17OSWNUyfE/edit?usp=drivesdk).
Columns: name, category, room, store, product URL, price PLN, model file URL, preview URL, has_own_model, similar_model_id and more.

**Base URL:** `https://iandamai720-cmyk.github.io/interior-models`. GitHub Pages sends `Access-Control-Allow-Origin: *` on every repo below.

## Storage: sharded GitHub Pages repos
Every repo is under 1 GB, with no file over 100 MB. Every URL in `catalog.json` is absolute, so clients don't need to care which shard holds a file.

| Repo | Pages base | Content |
|---|---|---|
| [interior-models](https://github.com/iandamai720-cmyk/interior-models) | https://iandamai720-cmyk.github.io/interior-models/ | catalog, API, gallery, previews/thumbnails, v1 furniture/appliances/layouts, scripts, Blender helper, sheet |
| [interior-models-ikea](https://github.com/iandamai720-cmyk/interior-models-ikea) | https://iandamai720-cmyk.github.io/interior-models-ikea/ | `ikea/<category>/*.glb`: 488 new IKEA models (~640 MB, each ≤25 MB, textures ≤2K) |
| [interior-models-extra](https://github.com/iandamai720-cmyk/interior-models-extra) | https://iandamai720-cmyk.github.io/interior-models-extra/ | `polyhaven/**.glb` and `kenney/**.glb` (~420 MB) |
| [interior-models-layouts](https://github.com/iandamai720-cmyk/interior-models-layouts) | https://iandamai720-cmyk.github.io/interior-models-layouts/ | `layouts/house1_*` and `layouts/house2_*` as .blend/.glb/.json (~550 MB) |

`catalog.json` → `shards`, and every asset has `shard` and `model_url`. `/api/shard/{repo}.json` lists the assets per shard.

### Local copy (e.g. drive D:)
* `download_all.ps1` (Windows PowerShell) downloads the `main.zip` archive of each repo and unpacks it into `D:\interior-models\`. Run it with `powershell -ExecutionPolicy Bypass -File download_all.ps1 [-Dest D:\interior-models]`.
* `download_all.sh` does the same on Linux/macOS.
* `urls.txt` lists every individual file URL, for incremental refreshes (`wget -x -nH -N -i urls.txt`).
* Zip archives:
  * https://github.com/iandamai720-cmyk/interior-models/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-ikea/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-extra/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-layouts/archive/refs/heads/main.zip

## Endpoints (all GET, all static JSON)
| Endpoint | Content |
|---|---|
| `/catalog.json` | Full catalog: `{version:2, generated, base_url, shards, assets:[...]}` |
| `/api/index.json` | Lists the endpoints and counts, the categories, rooms, styles, colours, stores and shards, and the sheet links |
| `/api/assets.json`, `/api/models.json` | Summary of every asset / of every asset with its own model file |
| `/api/layouts.json`, `/api/layouts/{id}.json` | Layouts: id, area_m2, floors, style, furnished, rooms, urls, preview_urls, furniture_used |
| `/api/furniture.json`, `/api/furniture/{id}.json`, `/api/furniture/{category}.json`, `/api/furniture/room/{room}.json` | Furniture (IKEA ids are `ikea-<article>`, e.g. `ikea-00263850`) |
| `/api/appliances…`, `/api/fixtures…` | Same structure for appliances/electronics and sanitary/heating |
| `/api/store-products.json`, `/api/store-products/{id}.json`, `/api/store-products/{category}.json` | Polish store products, each with `similar_model_id` |
| `/api/stores.json` | Stores with counts and price coverage |
| `/api/store/{store}.json`, `/api/store/{store}/{category}.json` | Products per store: `ikea`, `agata-meble`, `black-red-white`, `jysk`, `vox`, `bodzio`, `komfort`, `meble-wojcik`, `castorama`, `leroy-merlin` |
| `/api/category/{category}.json`, `/api/room/{room}.json` | Any type by category / room (`living`, `bedroom`, `kids`, `dining`, `kitchen`, `bathroom`, `hallway`, `office`, `garden`, …) |
| `/api/styles/{style}.json`, `/api/colours/{colour}.json` | By style (`scandi`, `dark`, …) and by colour |
| `/api/licenses/{licence}.json`, `/api/sources/{source}.json`, `/api/shard/{repo}.json` | By licence, by source (`ikea`, `poly-haven`, `kenney`, `objaverse-1-0-sketchfab`, store slugs) and by shard |
| `/api/variants.json` | IKEA colour-variant groups (`variant_group` → list of ids) |
| `/api/credits.json` | Attribution list for every non-IKEA model |
| `/catalog.db` | SQLite copy of the catalog: `assets`, `furniture`, `layouts`, `rooms`, `layout_furniture`, `tags`, plus store/price columns |

Layout ids:
* `apartment-{scandi-furnished,dark-furnished,scandi-shell}`
* `house-…`
* `house1-…` (~150 m², single storey)
* `house2-…` (175.75 m² over two storeys with stairs; previews `top_gf`, `top_ff`, `iso`, `iso_gf`)

### Asset fields
**Common to all assets:**
`id, type (layout|furniture|appliance|fixture|store_product), name, style, colours[], tags[], url, model_url, preview_url, api_url, shard, file_size_bytes`

**Commerce fields:**
* `store` and `price_pln` (null when the store doesn't publish one);
* `url_pl`, plus `url_uk` for IKEA;
* `has_own_model` and `similar_model_id`;
* `variant_group` and `variants[]` for IKEA colour variants.

**Models add:**
* `category, room, colour, material, dimensions_m{x,y,z}, triangles, source, source_url, author, license`;
* `article_number` for IKEA items.

Units are metres. Every model GLB is Z-up in Blender, with its footprint centred on the origin, the floor at z=0, and the front facing **−Y**.

## Query examples
```bash
B=https://iandamai720-cmyk.github.io/interior-models
curl -s $B/api/store/jysk/sofa.json | jq '.[] | {name, price_pln, url_pl, similar_model_id}'
curl -s $B/catalog.json | jq '.assets[] | select(.store=="IKEA" and .category=="sofa" and .price_pln < 1500) | {id,name,price_pln,url}'
curl -s $B/api/layouts/house2-scandi-furnished.json | jq '.rooms[] | {name, area_m2, floor}'
```
```js
const B = "https://iandamai720-cmyk.github.io/interior-models";
const { assets } = await (await fetch(`${B}/catalog.json`)).json();
const byId = Object.fromEntries(assets.map(a => [a.id, a]));
const p = assets.find(a => a.type === "store_product" && a.store === "VOX");
const glbUrl = byId[p.similar_model_id].url;   // the stand-in 3D model for a store product
```

## Blender helper: `blender/import_from_catalog.py`
Using the **Scripting tab:** open the file, set `RUN_ID` (or `RUN_FILTER`) in the CONFIG block, then press *Run Script*.
As a module:
```python
import sys; sys.path.append("/path/to/blender")
import import_from_catalog as ic
ic.list_assets(store="IKEA", category="sofa", max_price=2000)
ic.import_asset("ikea-00263850", location=(1, 0, 0), rotation_deg=90)
ic.import_asset("jysk-<slug>")                          # store product → imports its similar_model_id model
ic.import_filtered(type="furniture", style="scandi", room="bedroom", limit=6)
ic.import_asset("house2-scandi-furnished")              # whole layout GLB
ic.import_asset("house1-dark-furnished", fmt="blend")   # appends the original .blend collections
```
Every imported root object carries the custom props `catalog_id`, `ikea_article`, `store`, `price_pln`, `url_pl` and `similar_model_id`.

Headless:
```
blender -b --python import_from_catalog.py -- --store JYSK --category sofa --max-price 2500 --save sofy.blend
```
The other options are `--id`, `--type`, `--category`, `--room`, `--style`, `--colour`, `--min-price`, `--min-area`, `--max-area`, `--list` and `--format blend`.
Downloads are cached in `~/.cache/interior-models`; you can change this with `INTERIOR_MODELS_CACHE`.

## Repository layout (this repo)
* `furniture/` and `appliances/`: the v1/turn-3 GLBs.
* `layouts/`: the v1 apartment and house layouts (house1/house2 live in the layouts shard).
* `previews/`: layout renders, plus `previews/{ikea,polyhaven,kenney,furniture,appliances}/` thumbnails.
* `research/sources.md`: research on sources and tools (X + GitHub) and the store findings.
* `scripts/`:
  * sourcing: `fetch_ikea_pl.py`, Poly Haven / Kenney import and normalisation, and the store scrapers;
  * `build_layout2.py`: house1/house2. Run it as `blender -b --python scripts/build_layout2.py -- <house2|house1> <scandi|dark> <furnished|shell>`;
  * `make_catalog2.py` → `build_api2.py` → `make_sheet.py`: catalog, API + SQLite, and xlsx/csv.
* `index.html`: the gallery. `download_all.ps1` / `download_all.sh` / `urls.txt`: local mirror.

The layout .blend/.glb files use preview-grade copies of the models (textures ≤512 px). The individual GLBs are full quality (≤25 MB, textures ≤2K).

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

Plus 542 IKEA product models (© Inter IKEA Systems B.V., personal/demo use only); each links to its IKEA product page in `source_url` / `url_pl` / `url_uk`.
173 Poly Haven models (CC0, https://polyhaven.com) and 129 Kenney Furniture Kit models (CC0, https://kenney.nl/assets/furniture-kit) – the full list with authors is in `/api/credits.json`.
