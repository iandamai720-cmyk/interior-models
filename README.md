# interior-models

A static asset API, served from GitHub Pages, for an interior-architect demo app that imports models into Blender.
It contains two procedurally built layouts (an apartment of about 50 m² and a single-storey house of about 100 m²)
plus 44 IKEA furniture models in GLB format.

> **Personal / demo use only.** The IKEA 3D models are © Inter IKEA Systems B.V. They were downloaded from public IKEA product pages.

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
| `/api/furniture.json` | Summary of each furniture item |
| `/api/furniture/{id}.json` | One furniture item in full (the id is `ikea-<article number>`, e.g. `ikea-00263850`) |
| `/api/furniture/{category}.json` | Furniture in one category, e.g. `sofa`, `bed_double`, `lamp`, `kitchen` (same data as `/api/furniture/category/{category}.json`) |
| `/api/furniture/room/{room}.json` | Furniture for one room type: `living`, `bedroom`, `dining`, `kitchen`, `bathroom`, `hallway`, `office` |
| `/api/styles/{style}.json` | Layouts and furniture in one style: `scandi`, `dark`, `dark-industrial`, `wood-natural`, `neutral` |
| `/api/colours/{colour}.json` | Assets in one colour (slugified), e.g. `white`, `black`, `beige`, `light-oak` |
| `/catalog.db` | SQLite copy of the catalog. Tables: `assets`, `furniture`, `layouts`, `rooms`, `layout_furniture`, `tags` |
| `/furniture/*.glb`, `/layouts/*.glb|.blend`, `/previews/**.png` | The asset files themselves (each asset's `url` / `urls` / `preview_url` field points here) |
| `/blender/import_from_catalog.py` | Blender helper script (see below) |

Layout ids: `apartment-scandi-furnished`, `apartment-dark-furnished`, `apartment-scandi-shell`,
`house-scandi-furnished`, `house-dark-furnished`, `house-scandi-shell`.

### Asset fields
Common to all assets: `id, type (layout|furniture), name, style, colours[], tags[], url, preview_url, api_url, file_size_bytes`.
Layouts add: `area_m2, footprint_m, rooms[{name,type,area_m2,bounds}], bedrooms, furnished, urls{glb,blend,meta}, preview_urls{top,iso}, furniture_used[]`.
Furniture adds: `article_number, full_name, category, room, colour, material, dimensions_m{x,y,z}, dimensions_listed, source_url, triangles`.
Units are metres. Every furniture GLB is Z-up in Blender, with its footprint centred on the origin, the floor at z=0, and the front facing **−Y**.

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
- `layouts/`: for each layout variant, a `.blend`, a `.glb` and a `.json` file with rooms and furniture placements.
- `previews/`: top-down and isometric renders of each layout, and `previews/furniture/` thumbnails.
- `scripts/`:
  - `fetch_ikea.py`: IKEA search, then the product page's JSON-LD `3DModel` block, then the GLB download.
  - `build_layout.py`: the procedural shell and furniture placement. Run it as `blender -b --python scripts/build_layout.py -- <apartment|house> <scandi|dark> <furnished|shell>`.
  - `make_catalog.py`, then `build_api.py`: rebuild the catalog, the API files and the SQLite db.
- `index.html`: a gallery with filters for type, category, style, colour, area and text.

Bathroom fixtures (toilet, shower, bathtub), kitchen worktops and mattresses/bedding are simple procedural placeholders,
because IKEA has no 3D models for them.
