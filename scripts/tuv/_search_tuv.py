"""Search for real TÜV form binaries across the filesystem."""
import os, zipfile

# 1. Examine current template to confirm it's a placeholder
tpl_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "04_03_26_consense_audit_documentation")
for f in sorted(os.listdir(tpl_dir)):
    fp = os.path.join(tpl_dir, f)
    sz = os.path.getsize(fp)
    kind = "?"
    if f.endswith(".docx"):
        try:
            with zipfile.ZipFile(fp, "r") as z:
                names = z.namelist()
                has_images = any(n.startswith("word/media/") for n in names)
                has_hdr = any(n.startswith("word/header") or n.startswith("word/footer") for n in names)
                nparts = len(names)
            kind = f"docx parts={nparts} images={has_images} hdrs={has_hdr}"
        except Exception as e:
            kind = f"docx-err:{e}"
    elif f.endswith(".xlsx"):
        try:
            with zipfile.ZipFile(fp, "r") as z:
                nparts = len(z.namelist())
            kind = f"xlsx parts={nparts}"
        except Exception as e:
            kind = f"xlsx-err:{e}"
    print(f"  {sz:>10}  {kind}  {f}")

# 2. Search for real TÜV binaries (large docx/xlsx with FM-TAGMBH names)
print("\n=== Searching filesystem for TÜV binaries ===")
hits = []
search_roots = [
    "C:\\Users\\eos\\Desktop",
    "C:\\Users\\eos\\Downloads",
    "C:\\Users\\eos\\Documents",
    "C:\\Users\\eos\\OneDrive",
]
for root_dir in search_roots:
    if not os.path.isdir(root_dir):
        continue
    for root, dirs, files in os.walk(root_dir):
        low = root.lower()
        if any(s in low for s in ["__pycache__", "inetcache", "node_modules", ".cache"]):
            dirs[:] = []
            continue
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
            except Exception:
                continue
            fl = f.lower()
            if "FM-TAGMBH" in f or "TAGMBH" in f:
                hits.append((sz, "TÜV-FORM", fp))
            elif sz > 100000 and fl.endswith((".docx", ".docm", ".xlsx")):
                hits.append((sz, "LARGE-FILE", fp))
hits.sort(reverse=True)
print(f"Found {len(hits)} candidates:")
for sz, kind, fp in hits[:40]:
    print(f"  {sz:>12}  [{kind}]  {fp}")
if not hits:
    print("  (none found)")
