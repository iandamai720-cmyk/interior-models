"""urls.txt: every downloadable file URL (models, material maps, layouts, previews, catalog files)."""
import json
c = json.load(open("/workspace/interior-lib/catalog.json")); B = c["base_url"]; U = set()
for f in ("catalog.json", "catalog.db", "sklepy.xlsx", "assets.csv", "index.html", "README.md", "download_all.ps1", "download_all.sh",
          "blender/import_from_catalog.py", "blender/load_material.py", "api/index.json"): U.add(f"{B}/{f}")
for a in c["assets"]:
    if a["type"] == "store_product": continue
    for u in [a.get("url"), a.get("preview_url"), *(a.get("urls") or {}).values(), *(a.get("preview_urls") or {}).values(), *(a.get("maps") or {}).values()]:
        if u: U.add(u)
open("/workspace/interior-lib/urls.txt", "w").write("\n".join(sorted(U)) + "\n"); print(len(U))
