"""Comprehensive search for real TÜV binaries."""
import os, sys

# 1. Check search_results.txt
desktop = "C:\\Users\\eos\\Desktop"
sr = os.path.join(desktop, "search_results.txt")
print(f"=== search_results.txt ===")
print(f"  exists={os.path.exists(sr)} size={os.path.getsize(sr) if os.path.exists(sr) else 'N/A'}")
if os.path.exists(sr):
    with open(sr, "rb") as f:
        raw = f.read()
    print(f"  raw bytes={len(raw)}")
    try:
        txt = raw.decode("utf-8")
        print(f"  content (utf-8):")
        for line in txt[:50].splitlines():
            print(f"    {line}")
    except:
        try:
            txt = raw.decode("cp1252")
            print(f"  content (cp1252):")
            for line in txt[:50].splitlines():
                print(f"    {line}")
        except Exception as e:
            print(f"  decode error: {e}")

# 2. List full Desktop contents
print(f"\n=== Desktop contents ===")
for f in sorted(os.listdir(desktop)):
    fp = os.path.join(desktop, f)
    sz = os.path.getsize(fp) if os.path.isfile(fp) else "<dir>"
    print(f"  {sz:>10}  {f}")

# 3. Check Desktop .pytest_cache
pc = os.path.join(desktop, ".pytest_cache")
if os.path.isdir(pc):
    print(f"\n=== Desktop .pytest_cache ===")
    for root, dirs, files in os.walk(pc):
        for fn in files:
            fp = os.path.join(root, fn)
            print(f"  {os.path.getsize(fp):>10}  {os.path.relpath(fp, pc)}")

# 4. Search INetCache for TÜV/audit-related files
inet = "C:\\Users\\eos\\AppData\\Local\\Microsoft\\Windows\\INetCache\\Content.Outlook"
print(f"\n=== Outlook INetCache TÜV-related files ===")
if os.path.isdir(inet):
    found = []
    for root, dirs, files in os.walk(inet):
        for f in files:
            fl = f.lower()
            if fl.endswith(('.docx','.docm','.pdf','.xlsx','.zip')) or 'audit' in fl or 'tüv' in fl or 'tu' in fl[:3] or 'certificate' in fl or 'cert' in fl or 'anlass' in fl or 'fm-' in fl:
                fp = os.path.join(root, f)
                try:
                    sz = os.path.getsize(fp)
                except:
                    continue
                found.append((sz, fp))
    found.sort(reverse=True)
    for sz, fp in found[:30]:
        rel = os.path.relpath(fp, inet)
        print(f"  {sz:>12}  {rel}")
    if not found:
        print("  (none found)")
else:
    print("  (INetCache not found)")

# 5. Check for .env file
env = os.path.join(desktop, "backend", ".env")
print(f"\n=== .env check ===")
print(f"  backend/.env exists: {os.path.exists(env)}")
if os.path.exists(env):
    with open(env) as f:
        for line in f:
            print(f"  {line.rstrip()}")

# 6. Search entire user profile for recently created large docx files
print(f"\n=== All .docx/.docx/.docm files > 30KB user profile (excluding backend/templates) ===")
hits = []
for root, dirs, files in os.walk("C:\\Users\\eos"):
    low = root.lower()
    if any(s in low for s in ["__pycache__", "inetcache", "node_modules", ".cache", "program files", ".git\\", "templates\\04_03_26"]):
        dirs[:] = []
        continue
    for f in files:
        fl = f.lower()
        if fl.endswith((".docx", ".docm")) and "templates" not in root:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
            except:
                continue
            if sz > 30000:
                hits.append((sz, fp))
hits.sort(reverse=True)
for sz, fp in hits[:30]:
    print(f"  {sz:>12}  {fp}")
if not hits:
    print("  (none found)")
