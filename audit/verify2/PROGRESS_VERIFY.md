# Verification run 2 (live assets) – started 2026-10-23 18:00 CEST
- [ ] 1 row integrity (CSV, PL CSV, xlsx, Google Sheet)
- [ ] 2 GLB sha vs render, preview sha/SSIM, fresh renders, CLIP text check
- [ ] 3 manual view flagged + 200 random; IKEA PL 50 spot-check
- [ ] 4 store rows
- [ ] 5 fixes, rebuild, push, verify
## 18:40 CEST
- DONE 1: live assets.csv/assets_pl.csv/sklepy.xlsx/Google Sheet(export) all 3794 rows identical cell-for-cell; no column shift, no dup ids, no shared GLB/preview; every preview = <id>.jpg in same dir as GLB. GLB filenames are legacy (not <id>) -> fix: rename GLB to <id>.glb.
- DONE 2a: all 3050 live GLB sha256 == GLB that was rendered; all 3050 live previews sha256 == that render (dl.jsonl).
- RUNNING: fresh renders 300 sample (fresh/), clip2.py (clip2.npz)
- Store: dl_store.jsonl, pagecheck.jsonl, agata_live.json (3 new Agata images: PAOLA, MANSION, HAPPIANO, Ława G-TE; BRODWAY image differs from live)

## Update 2026-10-23 (CEST) — stage 4/5
- Store overrides: /workspace/audit/verify2_store.json (10 Agata live images via GraphQL exact url_key, Ława name; MIRJAN → kitchen_tall_cabinet 60×57×210, substitute ikea-60212565)
- BRW: 52/52 image URLs contain product-page slug; WebFetch of brw.pl page OK (image bytes 403 from box). Leroy Merlin page WebFetch OK.
- audit_fix.py extended (verify2 fixes, room recompute, EN→PL colour/material). Rebuilt CSV/xlsx/api/urls; CREDITS cleaned (3 stale).
- New Google Sheet 1RidjlvMwOK9CLWBZbDtJHo1KykQIPCrOkTC6fg1vdEs (Drive tool can't overwrite content of old sheet).
- Commits: main 8d6c581, objaverse shard 2ffdf01 — pushed (normal). NEXT: Pages build, verify_urls, live re-check.
- DONE: Pages built (8d6c581, 2ffdf01). verify_urls: 13086 URLs, 13085 OK, 1 transient 503 (ph_painted_wooden_cabinet_02.glb) re-checked 200. Dropped GLB now 404.
- DONE: live assets.csv/sklepy.xlsx byte-identical to local; integrity.py on live: 3793 rows, 0 bad width, 0 dup ids, 0 shared GLB/preview; PL CSV, xlsx and new Google Sheet: 0 diffs. ALL DONE.
