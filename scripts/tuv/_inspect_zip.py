"""Examine the Dshield SAC Transfer Package ZIP for TÜV form binaries."""
import os, sys, zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

zip_path = os.path.join(
    "C:\\Users\\eos\\AppData\\Local\\Microsoft\\Windows\\INetCache\\Content.Outlook",
    "Z98LJFU7", "Dshield SAC Transfer Package 22301.zip"
)

print(f"ZIP exists: {os.path.exists(zip_path)}")
print(f"ZIP size: {os.path.getsize(zip_path)}")

with zipfile.ZipFile(zip_path, "r") as z:
    names = z.namelist()
    print(f"Total entries: {len(names)}")
    print("\n=== All entries ===")
    for info in z.infolist():
        sz = info.file_size
        print(f"  {sz:>12}  {info.filename}")

    print("\n=== TÜV form candidates (FM-TAGMBH, .docx, .xlsx) ===")
    for info in z.infolist():
        fn = info.filename
        fl = fn.lower()
        if "FM-TAGMBH" in fn or "TAGMBH" in fn or fl.endswith((".docx", ".docm", ".xlsx")) or fl.endswith(".dotx"):
            print(f"  {info.file_size:>12}  {fn}")

    print("\n=== Directories (folder structure) ===")
    dirs = set()
    for fn in names:
        parts = fn.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    for d in sorted(dirs):
        print(f"  {d}")
