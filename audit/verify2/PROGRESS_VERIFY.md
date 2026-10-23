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
