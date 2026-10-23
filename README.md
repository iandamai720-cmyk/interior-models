# interior-models

A static asset API, served from GitHub Pages, for an interior-architect demo app that imports models into Blender.

**Version 3 (turn 6):** 3817 catalog entries
* **3055 models with their own GLB file** (was 886): 1762 IKEA, 928 Objaverse, 236 Poly Haven and 129 Kenney.
  * Types: 2728 furniture/decor, 221 appliances/electronics, 106 sanitary/heating fixtures, in 229 categories.
  * IKEA items carry PLN prices, IKEA PL (and UK where available) links and colour variants.
  * Objaverse (Sketchfab) models were filtered by likes/name and every thumbnail was checked by eye; 370 broken/ugly ones were dropped. Each keeps its own licence, author and source link.
* **333 PBR materials** (`type: material`) from ambientCG and Poly Haven, CC0, 2K JPG maps: wood floors, tiles, fabric, countertops, plaster, brick, concrete, leather, carpet, wallpaper, metal. They are Blender-ready via `blender/load_material.py`.
* **411 Polish store products** from Agata, BRW, JYSK, VOX, Bodzio, Komfort, Meble Wójcik, Castorama and Leroy Merlin.
  * Each has a link and a price where the store publishes one.
  * They have no own 3D file (`has_own_model:false`). Each points to the closest library model via `similar_model_id`.
* **18 layouts**, each in three variants (scandi furnished, dark furnished, scandi shell):
  * a 50 m² apartment and a 100 m² house from v1;
  * a single-storey house of ~150 m² (`house1-*`);
  * a two-storey house of 175.75 m² with stairs and a terrace (`house2-*`);
  * **new:** a 70 m² 3-room apartment (`apt70-*`: living+kitchen, 2 bedrooms, bathroom, hall, utility, balcony);
  * **new:** a 35 m² loft studio (`loft35-*`: studio, sleeping niche, bathroom, hall).

> **Personal / demo use only.**
> * The IKEA 3D models are © Inter IKEA Systems B.V. They were downloaded from public IKEA product pages.
> * Objaverse items are under the CC licence recorded per asset (886 CC BY 4.0, 25 CC BY-SA 4.0, 2 CC BY-NC 4.0: `tv_qled_65` and `espresso_machine`). Attribution: `CREDITS.md` and `/api/credits.json`.
> * Poly Haven, Kenney and all materials are CC0.
> * Store names, prices and links were collected on 2026-10-23 and will go stale.

**Gallery:** https://iandamai720-cmyk.github.io/interior-models/
The gallery has filters for type, store, own/similar model, room, category, style, source, colour, PLN price and m², plus search. Materials and layouts have their own type filter. Each card shows its price and its PL and UK links.

**Spreadsheet:** `sklepy.xlsx` / `assets.csv` in this repo and [Google Sheet](https://docs.google.com/spreadsheets/d/1RidjlvMwOK9CLWBZbDtJHo1KykQIPCrOkTC6fg1vdEs/edit?usp=drivesdk).
Columns: name, category, room, store, product URL, price PLN, model file URL, preview URL, has_own_model, similar_model_id and more.

**Base URL:** `https://iandamai720-cmyk.github.io/interior-models`. GitHub Pages sends `Access-Control-Allow-Origin: *` on every repo below.

## Audit 2026-10-23
- Every own model's preview is now rendered from its own GLB (`<model_dir>/<id>.jpg`, sha256 in `preview_sha256`); 5 broken models dropped.
- Store products (`type=store_product`): `product_image_url` / `preview_url` = the real product photo from the store; they have **no own 3D file**.
  `similar_model_id` / `similar_model_url` point to a **podobny model (zastępczy)** picked by category + colour and checked with CLIP; empty when nothing fits.
- New column `opis` (Polish description). `assets_pl.csv` = `;`-separated variant for Polish Excel.
- Full change log: `audit/report.csv`; method & scripts: `audit/`.

## Storage: sharded GitHub Pages repos
Every repo is under 1 GB, with no file over 100 MB. Every URL in `catalog.json` is absolute, so clients don't need to care which shard holds a file.

| Repo | Pages base | Content |
|---|---|---|
| [interior-models](https://github.com/iandamai720-cmyk/interior-models) | https://iandamai720-cmyk.github.io/interior-models/ | catalog, API, gallery, v1–v2 previews and layout renders, v1 furniture/appliances/layouts, scripts, Blender helpers, sheet |
| [interior-models-ikea](https://github.com/iandamai720-cmyk/interior-models-ikea) | https://iandamai720-cmyk.github.io/interior-models-ikea/ | `ikea/<category>/*.glb`: 488 IKEA models from v2 (~640 MB) |
| [interior-models-ikea-2](https://github.com/iandamai720-cmyk/interior-models-ikea-2) | https://iandamai720-cmyk.github.io/interior-models-ikea-2/ | `ikea2/<category>/*.glb` + `previews/ikea/`: 620 new IKEA models (~860 MB) |
| [interior-models-ikea-3](https://github.com/iandamai720-cmyk/interior-models-ikea-3) | https://iandamai720-cmyk.github.io/interior-models-ikea-3/ | `ikea3/<category>/*.glb` + previews: 600 new IKEA models (~760 MB) |
| [interior-models-extra](https://github.com/iandamai720-cmyk/interior-models-extra) | https://iandamai720-cmyk.github.io/interior-models-extra/ | `polyhaven/**.glb` and `kenney/**.glb` + new Poly Haven previews (~615 MB) |
| [interior-models-objaverse](https://github.com/iandamai720-cmyk/interior-models-objaverse) | https://iandamai720-cmyk.github.io/interior-models-objaverse/ | `objaverse1/**.glb` + `previews/objaverse/`: 301 models (~840 MB) |
| [interior-models-objaverse-2](https://github.com/iandamai720-cmyk/interior-models-objaverse-2) | https://iandamai720-cmyk.github.io/interior-models-objaverse-2/ | `objaverse2/**.glb` + previews: 309 models (~840 MB) |
| [interior-models-objaverse-3](https://github.com/iandamai720-cmyk/interior-models-objaverse-3) | https://iandamai720-cmyk.github.io/interior-models-objaverse-3/ | `objaverse3/**.glb` + previews: 276 models (~845 MB) |
| [interior-models-materials](https://github.com/iandamai720-cmyk/interior-models-materials) | https://iandamai720-cmyk.github.io/interior-models-materials/ | `materials/<category>/<slug>/<slug>_{color,normal,roughness,ao,…}.jpg` + previews: 333 sets (~810 MB) |
| [interior-models-layouts](https://github.com/iandamai720-cmyk/interior-models-layouts) | https://iandamai720-cmyk.github.io/interior-models-layouts/ | `layouts/{house1,house2,apt70,loft35}_*` as .blend/.glb/.json (~860 MB) |

Thumbnails of the v3 additions live next to the models in their shard (the main Pages site must stay under 1 GB); `preview_url` is always absolute.
`catalog.json` → `shards`, and every asset has `shard` and `model_url`. `/api/shard/{repo}.json` lists the assets per shard.

### Local copy (e.g. drive D:)
* `download_all.ps1` (Windows PowerShell) downloads the `main.zip` archive of each repo and unpacks it into `D:\interior-models\`. Run it with `powershell -ExecutionPolicy Bypass -File download_all.ps1 [-Dest D:\interior-models]`.
* `download_all.sh` does the same on Linux/macOS.
* `urls.txt` lists every individual file URL, for incremental refreshes (`wget -x -nH -N -i urls.txt`).
* Zip archives (one per repo):
  * https://github.com/iandamai720-cmyk/interior-models/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-ikea/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-ikea-2/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-ikea-3/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-extra/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-objaverse/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-objaverse-2/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-objaverse-3/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-materials/archive/refs/heads/main.zip
  * https://github.com/iandamai720-cmyk/interior-models-layouts/archive/refs/heads/main.zip

## Endpoints (all GET, all static JSON)
| Endpoint | Content |
|---|---|
| `/catalog.json` | Full catalog: `{version:2, generated, base_url, shards, assets:[...]}` |
| `/api/index.json` | Lists the endpoints and counts, the categories, rooms, styles, colours, stores and shards, and the sheet links |
| `/api/assets.json`, `/api/models.json` | Summary of every asset / of every asset with its own model file |
| `/api/materials.json`, `/api/materials/{id}.json`, `/api/materials/category/{category}.json` | PBR materials: id, category, resolution, tile_m, `maps{color,normal,roughness,ao,…}`, folder_url, source, licence |
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
* `apt70-…` (70 m², 3 rooms) and `loft35-…` (35 m² studio loft); previews `top`, `iso`

### Asset fields
**Common to all assets:**
`id, type (layout|furniture|appliance|fixture|material|store_product), name, style, colours[], tags[], url, model_url, preview_url, api_url, shard, file_size_bytes`

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

## Blender helper: `blender/load_material.py`
```python
exec(open("load_material.py").read())
mat = load_material_from_catalog("material-acg-woodfloor051")        # downloads the maps, builds a Principled BSDF
# or a local copy:  mat = load_material("D:/interior-models/interior-models-materials/materials/floor_wood/acg_woodfloor051", tile_m=2.0)
bpy.context.object.data.materials.append(mat)
```
Box-projected object-space mapping, so no UVs are needed; `tile_m` (from the catalog) is the real-world size of one tile.

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
* `layouts/`: the v1 apartment and house layouts (house1/house2/apt70/loft35 live in the layouts shard).
* `previews/`: layout renders, plus `previews/{ikea,polyhaven,kenney,furniture,appliances}/` thumbnails.
* `research/sources.md`: research on sources and tools (X + GitHub) and the store findings.
* `scripts/`:
  * sourcing: `fetch_ikea_pl.py`, Poly Haven / Kenney import and normalisation, and the store scrapers;
  * `build_layout2.py`: house1/house2/apt70/loft35. Run it as `blender -b --python scripts/build_layout2.py -- <house2|house1|apt70|loft35> <scandi|dark> <furnished|shell>`;
  * `make_catalog3.py` → `build_api2.py` → `make_sheet.py` → `make_urls.py`: catalog, API + SQLite, xlsx/csv and urls.txt; `normalize_generic.py` (Blender normaliser) and `contact.py` (QA contact sheets).
* `index.html`: the gallery. `download_all.ps1` / `download_all.sh` / `urls.txt`: local mirror.

The layout .blend/.glb files use preview-grade copies of the models (textures ≤512 px). The individual GLBs are full quality (≤25 MB, textures ≤2K).

## Credits
Every non-IKEA model and material with author, licence and source link is listed in **[`CREDITS.md`](CREDITS.md)** and `/api/credits.json` (1626 entries). IKEA product models: © Inter IKEA Systems B.V., personal/demo use only; each links to its IKEA product page in `source_url` / `url_pl` / `url_uk`.
