"""sklepy.xlsx + assets.csv: every model / store product with store, price, links, model and preview URLs."""
import json, csv, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
ROOT = "/workspace/interior-lib"
A = json.load(open(f"{ROOT}/catalog.json"))["assets"]; BY = {a["id"]: a for a in A}
COLS = ["name", "category", "room", "store", "product_url", "price_pln", "model_file_url", "preview_url", "has_own_model", "similar_model_id",
        "id", "type", "style", "url_uk", "source", "license", "shard"]
rows = []
for a in A:
    if a["type"] == "layout": continue
    rows.append(dict(name=a.get("full_name") or a["name"], category=a["category"], room=a["room"], store=a.get("store") or a.get("source"),
        product_url=a.get("url_pl") or a.get("source_url"), price_pln=a.get("price_pln"), model_file_url=a.get("model_url") or a.get("url"),
        preview_url=a.get("preview_url"), has_own_model=bool(a.get("has_own_model", True)), similar_model_id=a.get("similar_model_id") or "",
        id=a["id"], type=a["type"], style=a["style"], url_uk=a.get("url_uk") or "", source=a.get("source"), license=a.get("license"), shard=a.get("shard") or ""))
with open(f"{ROOT}/assets.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(rows)
wb = Workbook(); hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor="0058A3")
def sheet(ws, rs, cols):
    ws.append(cols)
    for c in ws[1]: c.font, c.fill = hdr, fill
    for r in rs: ws.append([r.get(c) for c in cols])
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    for i, c in enumerate(cols, 1): ws.column_dimensions[get_column_letter(i)].width = {"name": 55, "product_url": 50, "model_file_url": 50, "preview_url": 40, "license": 40}.get(c, 16)
ws = wb.active; ws.title = "Wszystkie"; sheet(ws, rows, COLS)
by = collections.defaultdict(list)
for r in rows:
    if r["store"]: by[r["store"]].append(r)
for s, rs in sorted(by.items()):
    sheet(wb.create_sheet(s[:31].replace("/", "-")), rs, COLS)
ss = wb.create_sheet("Podsumowanie", 0); ss.append(["store/source", "items", "own 3D model", "similar model only", "with price PLN", "avg price PLN"])
for c in ss[1]: c.font, c.fill = hdr, fill
for s, rs in sorted(by.items()):
    pr = [r["price_pln"] for r in rs if r["price_pln"] is not None]
    ss.append([s, len(rs), sum(r["has_own_model"] for r in rs), sum(not r["has_own_model"] for r in rs), len(pr), round(sum(pr) / len(pr)) if pr else None])
ss.column_dimensions["A"].width = 28
wb.save(f"{ROOT}/sklepy.xlsx"); print(len(rows), {s: len(v) for s, v in by.items()})
