# Audit progress (preview/item mismatch) — updated 2026-10-23 22:20 (UTC+7)

## Root cause (established)
1. Store products (411) carried the *substitute* model's preview/model_url/dimensions → CSV preview showed a different item.
2. Store categories derived from URL-slug regex (e.g. witryna→sideboard, narożnik→sofa, łóżeczko→kids_bed, umywalka→washbasin).
3. Objaverse names = raw Sketchfab titles (junk tokens, codes).
4. IKEA category errors (~107 fixes in fix_cat.json), 5 broken models (drops).
5. 44 models with wrong orientation (28 flat + 16 flipped) → fixed GLBs.
6. Old previews were shared per-family PNGs (previews/furniture/<family>.png), not per-GLB.
CSV structure itself was fine.

## DONE
- [x] Stage 1: 3055 thumbs re-rendered from each own GLB → `<model_dir>/<id>.jpg`, sha256 in audit/rr/all.json
- [x] 44 orientation fixes (GLB backups in audit/glb_backup)
- [x] main commit 0c11d23 (100 thumbs + scripts/rerender_thumbs.py); shards synced (scripts/sync_shards.py, sha-verified, 44 GLB + 2955 thumbs) and committed locally in 7 shards — NOT pushed yet
- [x] CLIP flagging + manual view: 150 random (1 error), 191 non-IKEA + 140 IKEA flagged → fix_cat.json (~107 cat/name fixes, 5 drops), dims_fix.json (44)
- [x] store_meta.py → store_meta.json: real names (JYSK h1), categories by earliest-match rules on name (51 changed), colour/material/dims, product_image_url (351 verified images; 52 BRW = store URL unverified (403), 8 others missing)
- [x] match_store.py → match_res.json: CLIP image(product photo)→thumb within exact category (+colour text rerank); 60 text-only
- [x] contact sheets reviewed (audit/cs/x*.jpg, t0.jpg); threshold image ≥0.50, manual rejects listed in accept_similar.py

## NEXT
- [x] accept_similar.py → similar.json: 385 with similar (331 image-verified, 54 text-only), 26 empty
- [x] Objaverse names: obj_names.json (424 renamed) + obj_catfix.json (38 category fixes via name+CLIP)
- [x] opis column (PL) built in scripts/audit_fix.py
- [x] scripts/audit_fix.py applied (catalog_before.json snapshot; audit/report.csv 6317 rows). [ ] make_sheet (CSV BOM + ; variant + xlsx), build_api2, make_urls, gallery
- [ ] commit, push main + shards, verify URLs 200, Google Sheet upload, report.csv

## Update 2026-10-23 22:20 (UTC+7)
- DONE: build_api2 (api/ rebuilt from scratch), index.html gallery (podobny model (zastępczy) label + preview, opis, GLB zastępczy link), make_urls (7831 URLs).
- DONE: main committed 1b1dda6 + 464f342, pushed; 7 shards pushed (normal fast-forward pushes, no history rewrite).
- DONE: new Google Sheet https://docs.google.com/spreadsheets/d/1sPE9N7sV9ewqaHAqXRBwfWkL-VeYulbSzqj7grKDEiY/edit (A1:AA3795 verified), link in README/api/index.json.
- NEXT: wait for Pages builds, run scripts/verify_urls.sh, final report.

## Update 22:45 (UTC+7)
- DONE: all 8 Pages builds built; verify_urls.sh 13096 URLs -> 13095 OK, 1 transient 503 (ikea-60224078.jpg) re-checked = 200. ALL DONE.
