# PROGRESS – turn 6 (v3 expansion, updated 2026-10-23)

- [x] IKEA PL: +1220 new GLB models (1762 total) with PLN price, url_pl and colour variants. 1 of 1226 failed normalisation; 5 dropped in QA (4 near-invisible mirrors, 1 glass).
- [x] Poly Haven: +63 interior models (236 total). 9 dropped in QA.
- [x] Objaverse 1.0 (Sketchfab): 1256 candidates filtered by likes/name and normalised, all thumbnails checked by eye; 886 kept, 370 dropped (928 total). Licence/author/source kept per asset.
- [x] Materials: 333 PBR sets (ambientCG 158, Poly Haven 175, CC0, 2K). New `material` type, /api/materials*, blender/load_material.py. 1 dropped.
- [x] Layouts: apt70 (70 m², 3 rooms) and loft35 (35 m² loft) × scandi/dark furnished + scandi shell. Previews rendered and checked.
- [x] Quaternius skipped: only Google Drive / itch.io downloads, no stable direct URLs.
- [x] catalog.json v3 (3817 entries, 3055 models with own GLB), api/, catalog.db, gallery, CREDITS.md, README
- [x] sklepy.xlsx + assets.csv. The new Google Sheet 1pXMH_1O5brYE4_K3pZfvjZ95s2XnLJUN7228FeqaGew replaces 1rqNTtsk… (the Drive connector can't overwrite it in place).
- [x] New shard repos: interior-models-ikea-2, -ikea-3, -objaverse, -objaverse-2, -objaverse-3, -materials. Added to -extra and -layouts as normal commits (no history rewrites). All are under 900 MB, every file is under 100 MB, and Pages is built on all 10 repos.
- [x] v3 thumbnails are served from their shard, so the main Pages site stays under 1 GB (856 MB).
- [x] download_all.ps1/.sh (10 repos, ~7.9 GB), urls.txt (7839 URLs)
- [x] URL verification: 12980/12980 return 200 with ACAO * (tmp/verify.txt; 24 transient 503s/404s during Pages builds passed on retry)
- [x] Cleanup: staging/ (6.4 GB), dropped Objaverse files (1.1 GB), ikea_new/, /tmp QA dirs, normalisation logs

## Earlier (turn 4/5)
- [x] Research → research/sources.md (X + GitHub, store results, top findings)
- [x] IKEA PL: 488 new GLB models (542 total), PLN price, url_pl, url_uk (347), colour variants (72)
- [x] Polish stores: 411 products / 9 stores, similar_model_id for all (no store publishes 3D)
- [x] Gap fillers: Poly Haven 169 new, Kenney 129 (stairs/doors/windows/kids/garden/decor)
- [x] Layouts: house1 (~150 m²) + house2 (175.75 m², 2 floors) × scandi/dark furnished + shell, previews rendered & checked
- [x] catalog.json v2 (1309), api/ v2, catalog.db, index.html gallery, Blender helper
- [x] sklepy.xlsx + assets.csv + Google Sheet (1rqNTtskPRN7ftZ1w9KNB6eIjsTL1jFq6U17OSWNUyfE)
- [x] Shard repos pushed + Pages enabled: interior-models-ikea, -extra, -layouts (/workspace/shards, hardlinks)
- [x] Main repo committed & pushed in stages (scripts, previews, catalog/api/gallery/sheet)
- [x] README, download_all.ps1/.sh, urls.txt
- [x] URL verification: 4107/4107 URLs 200 + ACAO * (tmp/verify.txt; 40 transient 503s passed on retry)
- [x] Cleanup: removed staging/ (1.25 GB), tmp/stores cache+sitemaps, tmp view/thumb/raw dirs, old /workspace/interior-lib.zip

- [x] 2026-10-23 audit: see audit/PROGRESS_AUDIT.md and audit/report.csv. New Google Sheet: https://docs.google.com/spreadsheets/d/1sPE9N7sV9ewqaHAqXRBwfWkL-VeYulbSzqj7grKDEiY/edit
