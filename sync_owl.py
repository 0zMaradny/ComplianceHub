"""Sync OWL v4.2 workspace files into Osama/ (repo copy)."""
import pathlib
import shutil

SRC = pathlib.Path("g:/My Drive/Osama/Resources AI/OWL System/OWL-Complete-2026-08-09/workspace")
DST = pathlib.Path("c:/Users/eos/ComplianceHub/Osama")

FILES = [
    "SOUL.md",
    "AGENTS.md",
    "CONTEXT.md",
    "MEMORY.md",
    "SKILLS.md",
    "PLATFORMS.md",
    "TOOLS.md",
    "USER.md",
]

for name in FILES:
    src = SRC / name
    dst = DST / name
    if not src.exists():
        print(f"MISSING SOURCE: {src}")
        continue
    shutil.copy2(src, dst)
    print(f"COPIED: {name} ({src.stat().st_size} bytes)")

print("DONE")