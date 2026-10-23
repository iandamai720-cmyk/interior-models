# Research – asset sources & tools (turn 4, 2026-10-23)

Research done via X (x MCP: recent search, interior design / 3D walkthrough / deweloperka / Blender / free 3D libraries)
and GitHub search (repos + topics). Raw search dumps: `tmp/research/` (not published).

Legend – **Used**: ✅ imported into this library · 🔶 partially / referenced · ❌ not used (reason given).

## 3D model libraries / datasets

| Source | Link | What it offers | Licence | Used |
|---|---|---|---|---|
| IKEA (PL + UK sites) | https://www.ikea.com/pl/pl/ | Official product GLB (rotera/“3D view”) for thousands of products, colour variants, PLN prices | © Inter IKEA Systems – personal/demo use only | ✅ 488 new models (+50 from turn 1) |
| Poly Haven | https://polyhaven.com/models | ~180 photoscanned/hand-made models (furniture, decor, food, plants, lamps), glTF 1k–8k | CC0 | ✅ 169 (+4 earlier) |
| Kenney – Furniture Kit | https://kenney.nl/assets/furniture-kit | 140 low-poly furniture/kitchen/bath models incl. **stairs, doorways, windows** | CC0 | ✅ 129 (gap-filler: stairs/doors/windows/kids) |
| ToxSam/open-source-3D-assets | https://github.com/ToxSam/open-source-3D-assets | Registry of ~1000 CC0 GLB models (mostly game props) | CC0 | 🔶 reviewed, low interior relevance |
| kimchistan – Daycare Everyday Interiors 240 | https://kimchistan.itch.io/daycare-everyday-interiors-240 | 240 CC0 GLB kids/daycare props (found on X) | CC0 | ❌ itch.io download flow needs a browser checkout ("$0 / name your price"); recommended for a manual download |
| Objaverse 1.0 | https://huggingface.co/datasets/allenai/objaverse | 800k Sketchfab CC models (mixed quality) | per-object CC-BY / CC0 etc. | 🔶 used in turn 3 (appliances); not expanded – Poly Haven/IKEA/Kenney covered the gaps |
| 3D-FUTURE / 3D-FRONT (Alibaba) | https://tianchi.aliyun.com/specials/promotion/alibaba-3d-future | 16k furniture CAD + 18k furnished rooms | research licence, **application form required** | ❌ needs form/approval |
| InteriorGS (manycore) | https://github.com/manycore-research/InteriorGS | 1000 Gaussian-splat indoor scenes w/ labels | non-commercial research | ❌ splats, not meshes |
| ambientCG | https://ambientcg.com | PBR materials (floors, walls, fabrics) | CC0 | 🔶 recommended for floor/wall materials (layouts use procedural materials) |
| BlenderKit (free tier) | https://www.blenderkit.com | Large furniture library inside Blender | Royalty-free / CC0 for free assets, account + addon needed | ❌ requires login/addon |
| Quaternius | https://quaternius.com | CC0 low-poly packs (furniture in "Ultimate House Interior") | CC0 | ❌ downloads via Google Drive/itch, Kenney covers same niche |
| Sketchfab | https://sketchfab.com | Huge library, many CC-BY | mixed | ❌ API download needs auth |

## Polish stores – results (see `sklepy.xlsx` / Google Sheet, `/api/stores.json`)

| Store | Products | With PLN price | Own 3D model | Notes |
|---|---|---|---|---|
| IKEA PL | 542 models (488 new) | 488 (all new ones) | ✅ 542 GLB | GLB from the product page JSON-LD `3DModel`; 347 also have an IKEA UK link; 72 have colour variants |
| Black Red White | 52 | 51 | ❌ | "Family Line 3D" planner works only in the browser; no product GLB |
| Castorama | 66 | 53 | ❌ | no 3D/AR on product pages |
| Leroy Merlin | 67 | 0 | ❌ | **HTTP 403 (bot protection)**: names come from URL slugs and there are no prices |
| Komfort | 58 | 58 | ❌ | – |
| JYSK | 48 | 48 | ❌ | – |
| VOX | 40 | 40 | ❌ | – |
| Agata Meble | 39 | 0 | ❌ | prices are rendered client-side (JS), so none were captured |
| Meble Wójcik | 27 | 27 | ❌ | – |
| Bodzio | 14 | 14 | ❌ | small online catalogue |

All 411 non-IKEA store products have `has_own_model=false` and a `similar_model_id`. It is picked by category, then colour/material keywords, then style, preferring IKEA models.

## Top findings
1. **IKEA is the only Polish-market store with downloadable 3D files.** Every other store either has no 3D at all or only an in-browser planner (BRW).
2. **The best gap-fillers are CC0:**
   * Poly Haven covers decor, plants, books, food and lamps at photoreal quality.
   * Kenney Furniture Kit is the only free source here for stairs, doors, windows and kids items. They are low-poly, so they are stand-ins.
3. **Not usable without manual steps:**
   * 3D-FUTURE/3D-FRONT needs an application form.
   * BlenderKit and Sketchfab need an account.
   * kimchistan's Daycare 240 pack (CC0 kids props, found on X) needs an itch.io checkout and is worth downloading manually.
4. **Useful tooling for the demo app:**
   * google/model-viewer for web/AR GLB viewing;
   * glTF-Transform for meshopt/KTX2 compression, which could roughly halve the shard sizes;
   * pascalorg/editor and blueprint-js as open-source floor-planner front-ends.
5. **On X:** many AI "floorplan → 3D → staging" projects (wy51ai/floorplan-3d, moodroom, roomsmith, walkmyplan-mcp). The Polish developer market uses "Spacer 3D" virtual tours. Both are competitive references.

## Tools / projects worth knowing (GitHub + X)

| Project | Link | Notes | Licence |
|---|---|---|---|
| pascalorg/editor (25k★) | https://github.com/pascalorg/editor | open-source 3D architectural editor with CLI + MCP tools | MIT |
| google/model-viewer | https://github.com/google/model-viewer | web/AR viewer for GLB/USDZ – good for the demo app | Apache-2.0 |
| glTF-Transform | https://github.com/donmccurdy/glTF-Transform | optimise/compress GLB (meshopt, KTX2, resize) | MIT |
| agmmnn/awesome-blender | https://github.com/agmmnn/awesome-blender | curated Blender addons/resources | CC0 |
| agmmnn/polydown | https://github.com/agmmnn/polydown | Poly Haven batch downloader | MIT |
| FloorplanToBlender3d | https://github.com/grebtsew/FloorplanToBlender3d | 2D plan image → Blender 3D | GPL-3.0 |
| blueprint-js / threejs-3d-room-designer | https://github.com/aalavandhaann/blueprint-js | three.js floor-planner (needs a model library like this one) | MIT |
| arcada | https://github.com/mehanix/arcada | react/pixi floor plan creator | Apache-2.0 |
| archilogic 3dio-js | https://github.com/archilogic-com/3dio-js | interior apps toolkit | MIT |
| Sweet Home 3D | https://www.sweethome3d.com | desktop planner, big free model catalogs | GPL |
| RoomFormer / FloorplanTransformation | https://github.com/ywyue/RoomFormer | floorplan reconstruction ML | MIT |
| IKEA downloaders | Tejay21/IKEA-Model-importer, Progxy/ikea-3d-scraper, sashkoangelov/ikea-bg-3d-downloader, "IKEA-3D-Model-Download-Button" userscript | same approach as `scripts/fetch_ikea_pl.py` | various |
| From X: wy51ai/floorplan-3d, OpenFabrica/moodroom, img2interior, walkmyplan-mcp, roomsmith, HousingWizard, archlang, cassandra/home-information | – | AI floorplan→3D / room-staging experiments | various |
| From X (commercial): Nolli, habita.design, homistry.ai, HomeStyler, naksa.cloud, Polish "Spacer 3D" virtual tours for developers | – | competitive reference for virtual staging / walkthroughs | commercial |

## Licence flags inside the library
* IKEA models: personal/demo use only – do not redistribute commercially.
* `tv_qled_65`, `espresso_machine` (Objaverse, turn 3): **CC BY-NC** – non-commercial only, attribution required.
* Poly Haven, Kenney: CC0.
