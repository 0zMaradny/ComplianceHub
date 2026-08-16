"""TÜV branding scrub — red #C00000 + black only, no blue, no hardcoded hex.

Line-based replacement keyed on ASCII markers so umlauts/middledots need no match.
Applies to the synced OWL v4.2 files in Osama/.
"""
import pathlib
import re

ROOT = pathlib.Path("c:/Users/eos/ComplianceHub/Osama")

# (file, ascii_marker_found_in_line, replacement_whole_line)
EDITS = [
    # SOUL.md — ComplianceHub Platform Rules
    ("SOUL.md", "TUV_BLUE",
     "- TÜV branding: red #C00000 + black only — theme sourced from uploaded templates, never hardcode a hex, never blue."),
    # CONTEXT.md — Visual Identity Summary row
    ("CONTEXT.md", "#003D7A",
     "| TÜV Default | #C00000 (red) | black | Inter | Default |"),
    # AGENTS.md — Agent 4 Excel theme table row
    ("AGENTS.md", "#003D7A",
     "| TÜV | #C00000 | black | Default |"),
    # TOOLS.md — Design System
    ("TOOLS.md", "#003D7A",
     "| Design System | — | templates/DESIGN.md | red #C00000 + black — no blue, no hardcoded hex |"),
]

for rel, marker, new_line in EDITS:
    p = ROOT / rel
    if not p.exists():
        print(f"SKIP (missing): {rel}")
        continue
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = 0
    out = []
    for ln in lines:
        if marker in ln and changed == 0:
            out.append(new_line + "\n")
            changed += 1
        else:
            out.append(ln)
    if changed:
        p.write_text("".join(out), encoding="utf-8")
    print(f"{rel} [{marker}]: {changed} line(s) replaced")

# Verify: no blue hex/labels left in any Osama/*.md
print("=== verify no blue hex/labels left in Osama/*.md ===")
bad = []
for p in ROOT.glob("*.md"):
    for ln in p.read_text(encoding="utf-8").splitlines():
        if re.search(r"003D7A|4472C4|TV_BLUE|TUV_BLUE|professional blue", ln, re.I):
            bad.append(f"{p.name}: {ln.strip()}")
print("CLEAN" if not bad else "\n".join(bad))