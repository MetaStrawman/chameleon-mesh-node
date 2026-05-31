#!/usr/bin/env python3
"""Compose chameleon_mesh_node_v1.kicad_pcb with all 6 footprints
pre-placed inside the 60x40 mm outline + 4 corner M2.5 mounting holes.

Strategy mirrors build_schematic.py:
  * For each placement, read the source .kicad_mod, embed it inline
    inside a (footprint ...) block at (X, Y, rotation) on F.Cu.
  * Assign net numbers + net names to each pad by looking up the
    (ref, pad_number) tuple in the schematic's NETS table.
  * Build the net table at the top of the PCB so it agrees with the
    schematic's net list.

TWO KEY LESSONS from the 2026-05-16 debug session — both caused
silent "Failed to load board" without any parser diagnostic:

1. LAYER ORDER must be KiCad's functional grouping, NOT strict
   numeric-ascending by ID. The canonical sequence is:
     F.Cu, B.Cu  (copper, signal)
     F.Adhes, B.Adhes  (mechanical)
     F.Paste, B.Paste  (stencil)
     F.SilkS, B.SilkS  (silkscreen)
     F.Mask, B.Mask    (solder mask)  ← IDs 1/3 come AFTER 5/7
     Dwgs/Cmts/Eco1/Eco2.User
     Edge.Cuts, Margin
     F.CrtYd, B.CrtYd  ← F first (31 before 29)
     F.Fab, B.Fab      ← F first (35 before 33)

2. NO LISP-STYLE COMMENTS (`;` or `;;`) anywhere in the file. The
   .kicad_pcb parser silently crashes on the first one. The earlier
   `;; Board outline 60x40 mm` comment was the final smoking gun;
   removing it made the composer work after a 90-min hunt. Use
   `(comment N "...")` inside `(title_block ...)` for human notes
   instead, or just leave the section unannotated.

After opening in Pcbnew, the operator only needs to: route the ratlines,
add a GND pour, run DRC, export gerbers. No drag-from-origin pass needed.

Run:
  python3 scripts/build_pcb.py
  kicad-cli pcb drc chameleon_mesh_node_v1.kicad_pcb   # verification
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import NamedTuple

# Reuse the schematic's NETS + NO_CONNECT_PINS + Placement type so this
# composer never drifts from the schematic netlist.
import sys
sys.path.insert(0, str(Path(__file__).parent))
from build_schematic import NETS, PLACEMENTS as SCH_PLACEMENTS, NO_CONNECT_PINS

PROJ        = Path(__file__).resolve().parent.parent / "kicad"
KICAD_SHARE = Path("/usr/share/kicad/footprints")
OUT_PCB     = PROJ / "chameleon_mesh_node_v1.kicad_pcb"

# ── Footprint sources (must match the schematic placements' footprint field)
FP_SOURCES: dict[str, Path] = {
    "Connector_USB:USB_C_Receptacle_GCT_USB4085":
        KICAD_SHARE / "Connector_USB.pretty" / "USB_C_Receptacle_GCT_USB4085.kicad_mod",
    "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.675x1.675mm":
        KICAD_SHARE / "Package_DFN_QFN.pretty" / "QFN-16-1EP_3x3mm_P0.5mm_EP1.675x1.675mm.kicad_mod",
    "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal":
        KICAD_SHARE / "Connector_JST.pretty" / "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal.kicad_mod",
    "Seeed_XIAO:XIAO-ESP32-C5-SMD":
        PROJ / "lib" / "Seeed_XIAO.pretty" / "XIAO-ESP32-C5-SMD.kicad_mod",
    "ChameleonMeshNode_Custom:Wio_WM1110_LGA80":
        PROJ / "lib" / "ChameleonMeshNode_Custom.pretty" / "Wio_WM1110_LGA80.kicad_mod",
    "Package_LGA:Bosch_LGA-8_2.5x2.5mm_P0.65mm_ClockwisePinNumbering":
        KICAD_SHARE / "Package_LGA.pretty" / "Bosch_LGA-8_2.5x2.5mm_P0.65mm_ClockwisePinNumbering.kicad_mod",
}

# ── PCB placement coordinates (mm) — chosen for RF zoning:
#   Wio (LR1110/nRF) on right edge, antennas pointing to board right
#   BQ24074 switcher kept far from both radios
#   BME280 in bottom-right corner, away from RF + thermal sources
#   USB-C + LiPo on opposite vertical edges
class PCBPlacement(NamedTuple):
    ref: str
    x: float
    y: float
    rotation: int   # degrees, KiCad convention

PCB_PLACEMENTS: list[PCBPlacement] = [
    PCBPlacement("J1", 20.0,  7.0,    0),   # USB-C top edge, opening upward
    PCBPlacement("U1", 8.0,   8.0,    0),   # BQ24074 left of USB-C
    PCBPlacement("J2", 8.0,  22.0,   90),   # LiPo JST left edge, cable exits up
    PCBPlacement("U2", 26.0, 22.0,    0),   # XIAO center
    PCBPlacement("U3", 47.0, 22.0,   90),   # Wio LGA-80 right side, antennas → right edge
    PCBPlacement("U4", 50.0, 35.0,    0),   # BME280 bottom-right
]

# ── Mounting holes (M2.5, 3 mm from each corner)
MOUNTING_HOLES = [
    ("H1", 3.0,  3.0),
    ("H2", 57.0, 3.0),
    ("H3", 3.0,  37.0),
    ("H4", 57.0, 37.0),
]


# ── Helpers ───────────────────────────────────────────────────────────
def slurp(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def strip_footprint_wrapper(text: str) -> str:
    """Drop the outer `(footprint NAME ...)` wrapper, return the inner content.
    Lets us re-wrap at our chosen placement coordinates."""
    # Find the opening paren of `(footprint ...)`
    m = re.search(r'\(footprint\s+\S+[^\n]*', text)
    if not m:
        raise ValueError("no (footprint ...) wrapper found")
    start = m.end()
    # Walk balanced parens from the opening of (footprint to find its close.
    depth = 1   # we're inside the (footprint ...
    j = m.start() + len('(footprint')
    # Re-scan from start to count parens properly.
    depth = 0
    j = 0
    in_string = False
    fp_open = -1
    while j < len(text):
        c = text[j]
        if c == '"' and (j == 0 or text[j-1] != '\\'):
            in_string = not in_string
        elif not in_string:
            if c == '(':
                if depth == 0 and text[j:j+len('(footprint')] == '(footprint':
                    fp_open = j
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0 and fp_open >= 0:
                    inner = text[fp_open + len('(footprint'):j]
                    return inner
        j += 1
    raise ValueError("unbalanced parens")

def renumber_pad_nets(inner: str, ref: str, net_map: dict[str, tuple[int, str]]) -> str:
    """Rewrite each `(pad "PADNUM" ...)` block to include `(net N "name")`.
    Pad blocks that have no net mapping get `(net 0 "")` (unconnected)."""
    # Match a pad opening and find its closing paren.
    out: list[str] = []
    i = 0
    while i < len(inner):
        m = re.search(r'\(pad\s+"?([^\s")]+)"?', inner[i:])
        if not m:
            out.append(inner[i:])
            break
        rel = m.start()
        out.append(inner[i:i+rel])
        # Find matching close-paren for THIS (pad block.
        depth = 0
        j = i + rel
        in_string = False
        start = j
        pad_num = m.group(1).strip('"')
        while j < len(inner):
            c = inner[j]
            if c == '"' and (j == 0 or inner[j-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        # End of pad block at j (inclusive). Insert net just
                        # before the closing paren.
                        pad_body = inner[start:j]
                        net_idx, net_name = net_map.get(pad_num, (0, ""))
                        # Strip any existing (net ...) inside the pad body.
                        pad_body = re.sub(r'\(net\s+\d+\s+"[^"]*"\)\s*', '', pad_body)
                        # Append (net N "name") right before the close.
                        new_pad = pad_body + f'\n      (net {net_idx} "{net_name}")\n    )'
                        out.append(new_pad)
                        i = j + 1
                        break
            # j MUST increment outside the if/elif so quote chars + chars-inside-strings
            # also advance. (Earlier version had this inside the elif → infinite loop on
            # the first " encountered inside a pad block.)
            j += 1
        else:
            # Unterminated; bail.
            out.append(inner[i+rel:])
            break
    return "".join(out)


# ── Compose ───────────────────────────────────────────────────────────
def build():
    # 1. Build net table — gather all unique net names from NETS.
    net_names = sorted({net for _, _, net in NETS})
    # net 0 is the unconnected/default
    nets = ["(net 0 \"\")"] + [f'(net {i+1} "{name}")' for i, name in enumerate(net_names)]
    net_index = {name: i + 1 for i, name in enumerate(net_names)}

    # 2. Build per-ref pad→net mapping.
    per_ref_pad_nets: dict[str, dict[str, tuple[int, str]]] = {}
    for ref, pad_num, net_name in NETS:
        per_ref_pad_nets.setdefault(ref, {})[pad_num] = (net_index[net_name], net_name)

    # 3. For each placement, embed the footprint with patched pad nets.
    fp_blocks: list[str] = []
    sch_by_ref = {p.ref: p for p in SCH_PLACEMENTS}
    for pp in PCB_PLACEMENTS:
        sch = sch_by_ref[pp.ref]
        fp_lib_id = sch.footprint
        src = FP_SOURCES.get(fp_lib_id)
        if not src or not src.is_file():
            raise SystemExit(f"FATAL: footprint source missing for {fp_lib_id}: {src}")
        inner = strip_footprint_wrapper(slurp(src))
        # Strip leading footprint-name string (e.g. ' "Bosch_LGA-8..."') —
        # strip_footprint_wrapper kept everything after `(footprint`, including
        # the name token. Match optional whitespace + a quoted-or-unquoted name.
        inner = re.sub(r'^\s*"[^"]*"\s*', '', inner)         # quoted name
        inner = re.sub(r'^\s*[^\s()]+\s*',  '', inner)        # unquoted name (fallback)
        # Drop top-level wrapper metadata that ONLY belongs at the original
        # .kicad_mod root, not when embedded inline in a .kicad_pcb. Each
        # of these blocks is single-line so a non-greedy paren match is safe.
        for pat in (
            r'\(version\s+\d+\)\s*',
            r'\(generator\s+"[^"]*"\)\s*',
            r'\(generator_version\s+"[^"]*"\)\s*',
            r'\(layer\s+"[^"]*"\)\s*',
            r'\(tedit\s+\S+\)\s*',
        ):
            inner = re.sub(pat, '', inner, count=1)
        # Don't strip the source's (property "Reference"/"Value") blocks —
        # KiCad parser is order-sensitive and expects them BETWEEN
        # descr/tags and attr. Instead, in-place swap the value strings.
        # Bundled source default: "Reference" "REF**", "Value" "<footprint_name>"
        inner = re.sub(r'\(property\s+"Reference"\s+"[^"]*"',
                       f'(property "Reference" "{pp.ref}"', inner, count=1)
        inner = re.sub(r'\(property\s+"Value"\s+"[^"]*"',
                       f'(property "Value" "{sch.value}"', inner, count=1)
        # Rewrite pad nets.
        inner = renumber_pad_nets(inner, pp.ref, per_ref_pad_nets.get(pp.ref, {}))
        fp_uuid = str(uuid.uuid4())
        fp_blocks.append(
            f'(footprint "{fp_lib_id}"\n'
            f'  (layer "F.Cu")\n'
            f'  (uuid "{fp_uuid}")\n'
            f'  (at {pp.x} {pp.y} {pp.rotation})\n'
            f'{inner}\n'
            f')'
        )

    # 4. Mounting holes — hand-authored inline (avoids the broken
    #    KiCad-bundled MountingHole.pretty reference from my earlier
    #    attempt).
    for ref, mx, my in MOUNTING_HOLES:
        h_uuid = str(uuid.uuid4())
        fp_blocks.append(
            f'(footprint "ChameleonMeshNode_Custom:MountingHole_M2.5"\n'
            f'  (layer "F.Cu")\n'
            f'  (uuid "{h_uuid}")\n'
            f'  (at {mx} {my} 0)\n'
            f'  (attr through_hole)\n'
            f'  (property "Reference" "{ref}"\n'
            f'    (at 0 -3.5 0) (layer "F.SilkS")\n'
            f'    (uuid "{uuid.uuid4()}")\n'
            f'    (effects (font (size 1 1) (thickness 0.15)))\n'
            f'  )\n'
            f'  (property "Value" "M2.5"\n'
            f'    (at 0 3.5 0) (layer "F.Fab")\n'
            f'    (uuid "{uuid.uuid4()}")\n'
            f'    (effects (font (size 1 1) (thickness 0.15)))\n'
            f'  )\n'
            f'  (pad "" thru_hole circle\n'
            f'    (at 0 0)\n'
            f'    (size 5.5 5.5)\n'
            f'    (drill 2.7)\n'
            f'    (layers "*.Cu" "*.Mask")\n'
            f'    (uuid "{uuid.uuid4()}")\n'
            f'  )\n'
            f')'
        )

    # 5. Assemble the file.
    pcb = f'''(kicad_pcb
\t(version 20240108)
\t(generator "kicad-python")
\t(generator_version "10.0")
\t(general (thickness 1.6) (legacy_teardrops no))
\t(paper "A4")
\t(title_block
\t\t(title "Chameleon Mesh Node v1 — PCB")
\t\t(date "2026-05-16")
\t\t(rev "v1.0-DRAFT")
\t\t(company "Chameleon Mesh Node Project")
\t\t(comment 1 "Pre-placed: USB-C+BQ24074 top, LiPo left, XIAO center, Wio right (antennas to edge), BME280 bottom-right")
\t\t(comment 2 "Routing + GND pour pending operator GUI")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings")
\t\t(19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1")
\t\t(23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t)
\t(setup (pad_to_mask_clearance 0))

\t{chr(10).join(nets)}

\t(gr_line (start 0 0)   (end 60 0)  (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
\t(gr_line (start 60 0)  (end 60 40) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
\t(gr_line (start 60 40) (end 0 40)  (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))
\t(gr_line (start 0 40)  (end 0 0)   (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))

{chr(10).join(fp_blocks)}
)
'''
    OUT_PCB.write_text(pcb)
    print(f"wrote: {OUT_PCB}")
    print(f"  {len(PCB_PLACEMENTS)} components pre-placed")
    print(f"  {len(MOUNTING_HOLES)} mounting holes")
    print(f"  {len(net_names)} named nets + 1 unconnected")


if __name__ == "__main__":
    build()
