#!/usr/bin/env python3
"""Compose chameleon_mesh_node_v1.kicad_sch from bundled symbols + project libs.

Strategy:
  * For each component: read its source .kicad_sym, extract the (symbol ...)
    block, re-emit it under a Library:Name prefix into the schematic's
    (lib_symbols ...) block.
  * Place each component at a chosen (x, y) on the A3 sheet.
  * For each pin we want connected: compute its world-coordinate connect
    point (symbol_pos + pin_relpos) and emit a (global_label ...) at
    that exact point with the chosen net name.
  * Add power:PWR_FLAG symbols on nets that have no power_out driver
    (GND, VBUS, VBAT) so ERC accepts them.

Output: ../chameleon_mesh_node_v1.kicad_sch (overwrites).
"""
from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import NamedTuple

KICAD_SHARE = Path("/usr/share/kicad/symbols")
PROJ        = Path(__file__).resolve().parent.parent / "kicad"
OUT_SCH     = PROJ / "chameleon_mesh_node_v1.kicad_sch"
SHEET_UUID  = "08bddda4-777a-4465-8af5-7e5907361ace"

# ── Sources for each symbol we need ──────────────────────────────────
SOURCES: dict[tuple[str, str], Path] = {
    ("ChameleonMeshNode_Custom",       "Wio_WM1110"):                 PROJ / "lib" / "ChameleonMeshNode_Custom.kicad_symdir" / "Wio_WM1110.kicad_sym",
    ("Seeed_XIAO_Series",  "XIAO-ESP32-C5-SMD"):          PROJ / "lib" / "Seeed_XIAO_Series.kicad_sym",
    ("Battery_Management", "BQ24074RGT"):                 KICAD_SHARE / "Battery_Management.kicad_symdir" / "BQ24074RGT.kicad_sym",
    ("Sensor",             "BME280"):                     KICAD_SHARE / "Sensor.kicad_symdir" / "BME280.kicad_sym",
    ("Connector",          "USB_C_Receptacle_USB2.0_14P"):KICAD_SHARE / "Connector.kicad_symdir" / "USB_C_Receptacle_USB2.0_14P.kicad_sym",
    ("Connector",          "Conn_01x02_Pin"):             KICAD_SHARE / "Connector.kicad_symdir" / "Conn_01x02_Pin.kicad_sym",
    ("power",              "PWR_FLAG"):                   KICAD_SHARE / "power.kicad_symdir" / "PWR_FLAG.kicad_sym",
}

# ── Placements (mm on the A3 sheet) ─────────────────────────────────
class Placement(NamedTuple):
    lib: str       # symbol library namespace
    name: str      # symbol name
    ref: str       # reference designator (U1, J1, etc.)
    value: str     # human label
    x: float       # sheet x (mm)
    y: float       # sheet y (mm)
    footprint: str # "FootprintLib:FootprintName" — fp-lib-table reference

PLACEMENTS = [
    Placement("Connector",          "USB_C_Receptacle_USB2.0_14P", "J1", "USB-C Power+Data",    50.0,  60.0,
              "Connector_USB:USB_C_Receptacle_GCT_USB4085"),
    Placement("Battery_Management", "BQ24074RGT",                  "U1", "BQ24074RGT",          130.0, 80.0,
              "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.675x1.675mm"),
    Placement("Connector",          "Conn_01x02_Pin",              "J2", "LiPo JST (PH 2.0)",   50.0,  140.0,
              "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal"),
    Placement("Seeed_XIAO_Series",  "XIAO-ESP32-C5-SMD",           "U2", "XIAO-ESP32-C5-SMD",   220.0, 90.0,
              "Seeed_XIAO:XIAO-ESP32-C5-SMD"),
    # U3 (Wio-WM1110) is LGA-80 (60mm body) — bumped to x=340 for clearance from XIAO.
    Placement("ChameleonMeshNode_Custom",       "Wio_WM1110",                  "U3", "Wio-WM1110",          340.0, 100.0,
              "ChameleonMeshNode_Custom:Wio_WM1110_LGA80"),
    # U4 (BME280) moved down + right to clear the larger Wio body.
    Placement("Sensor",             "BME280",                      "U4", "BME280",              420.0, 200.0,
              "Package_LGA:Bosch_LGA-8_2.5x2.5mm_P0.65mm_ClockwisePinNumbering"),
]

# ── Net assignments — (ref, pin_number, net_name) ────────────────────
# Pin numbers come from the pin-map extraction; verified against the
# bundled .kicad_sym sources.
NETS: list[tuple[str, str, str]] = [
    # USB-C J1: 4× VBUS + 4× GND + shield
    ("J1", "A4",  "VBUS"), ("J1", "A9",  "VBUS"),
    ("J1", "B4",  "VBUS"), ("J1", "B9",  "VBUS"),
    ("J1", "A1",  "GND"),  ("J1", "A12", "GND"),
    ("J1", "B1",  "GND"),  ("J1", "B12", "GND"),
    ("J1", "SH",  "GND"),
    # CC1/CC2 to GND via 5.1k typical — for logical netlist, just label as CC1/CC2 (no-connect handled by GUI later)
    ("J1", "A5",  "CC1"),  ("J1", "B5",  "CC2"),

    # BQ24074 U1
    ("U1", "13",  "VBUS"),                  # IN <- USB-C VBUS
    ("U1", "8",   "GND"), ("U1", "17", "GND"),  # VSS x2
    ("U1", "2",   "VBAT"), ("U1", "3", "VBAT"),  # BAT x2
    ("U1", "10",  "+3V3"), ("U1", "11", "+3V3"),  # OUT x2 — operator-stated LDO assumption
    # Control-pin defaults (USB-priority charging, internally regulated):
    ("U1", "4",   "GND"),                   # ~CE = LOW -> charger enabled
    ("U1", "5",   "GND"),                   # EN2 = LOW \  EN1=LOW + EN2=LOW
    ("U1", "6",   "GND"),                   # EN1 = LOW /  -> USB100mA mode default
    # ITERM, TMR, ISET, ILIM, TS, ~PGOOD, ~CHG are NC for this logical draft —
    # the BQ24074 needs external resistors + thermistor + LED indicators that
    # belong in the PCB-routing phase, not the netlist phase.

    # LiPo JST J2
    ("J2", "1",   "VBAT"),
    ("J2", "2",   "GND"),

    # XIAO ESP32-C5-SMD U2
    ("U2", "12",  "+3V3"),                  # 3V3 (top side)
    ("U2", "31",  "+3V3"),                  # 3V3 (bottom-pad mirror)
    ("U2", "13",  "GND"), ("U2", "27", "GND"), ("U2", "33", "GND"),  # GND x3
    ("U2", "34",  "GND"),                   # PAD (thermal pad to GND)
    ("U2", "14",  "VBUS"),                  # VBUS (5V from USB)
    ("U2", "32",  "VBAT"),                  # BAT
    ("U2", "5",   "I2C_SDA"),               # D4_SDA
    ("U2", "6",   "I2C_SCL"),               # D5_SCL
    ("U2", "7",   "UART_BRIDGE_TX"),        # D6_TX -> Wio RX
    ("U2", "8",   "UART_BRIDGE_RX"),        # D7_RX <- Wio TX

    # Wio-WM1110 U3 (datasheet V1.3 pinout — LGA-80, perimeter)
    # Power rails (both LoRa and BLE/MCU sides on the +3V3 rail):
    ("U3", "21",  "+3V3"), ("U3", "22", "+3V3"),       # VDD_LR (LoRa side, 1.8-3.7V)
    ("U3", "27",  "+3V3"), ("U3", "28", "+3V3"),       # VDD_NRF (BLE/MCU side, 1.7-3.6V)
    # All 25 module GND pads tied to GND:
    ("U3", "1",   "GND"), ("U3", "2",  "GND"), ("U3", "3",  "GND"), ("U3", "4",  "GND"),
    ("U3", "5",   "GND"), ("U3", "6",  "GND"), ("U3", "7",  "GND"), ("U3", "8",  "GND"),
    ("U3", "44",  "GND"), ("U3", "62", "GND"), ("U3", "64", "GND"), ("U3", "66", "GND"),
    ("U3", "68",  "GND"), ("U3", "69", "GND"), ("U3", "70", "GND"), ("U3", "71", "GND"),
    ("U3", "73",  "GND"), ("U3", "74", "GND"), ("U3", "75", "GND"), ("U3", "76", "GND"),
    ("U3", "77",  "GND"), ("U3", "78", "GND"), ("U3", "79", "GND"), ("U3", "80", "GND"),
    # I2C / UART mapped to Nordic SDK defaults on the nRF52840 GPIO matrix
    # (firmware-configurable; chosen here to match the SDK convention so
    # operator's first-flash firmware "just works" without pin remapping):
    ("U3", "18",  "I2C_SDA"),               # P0.26 — I2C0 SDA
    ("U3", "16",  "I2C_SCL"),               # P0.27 — I2C0 SCL
    ("U3", "33",  "UART_BRIDGE_TX"),        # P0.08 — UART RX  <- XIAO TX
    ("U3", "32",  "UART_BRIDGE_RX"),        # P0.06 — UART TX  -> XIAO RX

    # BME280 U4
    ("U4", "8",   "+3V3"),                  # VDD
    ("U4", "6",   "+3V3"),                  # VDDIO (single-rail tie)
    ("U4", "2",   "+3V3"),                  # CSB tied HIGH -> I2C mode
    ("U4", "1",   "GND"), ("U4", "7", "GND"),
    ("U4", "5",   "GND"),                   # SDO tied to GND -> I2C addr 0x76
    ("U4", "3",   "I2C_SDA"),               # SDI = SDA in I2C mode
    ("U4", "4",   "I2C_SCL"),               # SCK = SCL in I2C mode
]

# ── PWR_FLAG anchors (net_name, x, y) — satisfies ERC for nets w/o power_out.
# Skip nets that ALREADY have a power_out driver in the placed symbols:
#   +3V3 -> driven by BQ24074 pin 10 (power_out)
#   VBAT -> driven by BQ24074 pin 2  (power_out)
# Only VBUS, GND need flags.
PWR_FLAGS = [
    ("VBUS", 70.0, 50.0),
    ("GND",  100.0, 240.0),
]

# ── Pins intentionally left unconnected — emits (no_connect ...) at each.
# Documents intent so ERC doesn't flag them. (ref, pin_number)
NO_CONNECT_PINS: list[tuple[str, str]] = [
    # USB-C: D+/D- + CC1/CC2 left for PCB-phase refinement
    ("J1", "A6"), ("J1", "A7"), ("J1", "B6"), ("J1", "B7"),
    ("J1", "A5"), ("J1", "B5"),
    # BQ24074 analog control pins (need external Rs in PCB phase)
    ("U1", "1"),  ("U1", "7"),  ("U1", "9"),  ("U1", "12"),
    ("U1", "14"), ("U1", "15"), ("U1", "16"),
    # XIAO ESP32-C5 unused GPIOs (logical draft uses only TX/RX/SDA/SCL)
    ("U2", "1"), ("U2", "2"), ("U2", "3"), ("U2", "4"),
    ("U2", "9"), ("U2", "10"), ("U2", "11"),
    ("U2", "24"), ("U2", "25"), ("U2", "26"),
    ("U2", "28"), ("U2", "29"), ("U2", "30"),
    # Wio-WM1110 (LGA-80) — all module pins NOT in NETS above are NC for
    # this draft. RF antennas (63/65/67/72), USB (37/40/41), SWD (50/51),
    # LR_DIO (11/23/24), and most MCU GPIOs are left unwired pending PCB
    # routing phase + firmware-assignment refinement.
    ("U3", "9"),  ("U3", "10"), ("U3", "11"), ("U3", "12"), ("U3", "13"), ("U3", "14"), ("U3", "15"),
    ("U3", "17"), ("U3", "19"), ("U3", "20"),
    ("U3", "23"), ("U3", "24"), ("U3", "25"), ("U3", "26"),
    ("U3", "29"), ("U3", "30"), ("U3", "31"),
    ("U3", "34"), ("U3", "35"), ("U3", "36"), ("U3", "37"),  # VBUS NC (USB through XIAO only)
    ("U3", "38"), ("U3", "39"), ("U3", "40"), ("U3", "41"),  # DN/DP unconnected (USB on XIAO)
    ("U3", "42"), ("U3", "43"), ("U3", "45"), ("U3", "46"), ("U3", "47"), ("U3", "48"), ("U3", "49"),
    ("U3", "50"), ("U3", "51"),                              # SWD (route to debug header in PCB phase)
    ("U3", "52"), ("U3", "53"), ("U3", "54"), ("U3", "55"), ("U3", "56"), ("U3", "57"), ("U3", "58"),
    ("U3", "59"), ("U3", "60"), ("U3", "61"),                # NFC1, NFC2, GPIO P0.19
    ("U3", "63"), ("U3", "65"), ("U3", "67"), ("U3", "72"),  # ANT_NRF, ANT_WIFI, ANT_GNSS, ANT_LoRa
]


# ── Symbol-source parsing helpers ────────────────────────────────────
def slurp(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def extract_symbol_block(text: str, name: str) -> str:
    """Pull a top-level (symbol "<name>" ...) block from a .kicad_sym source.
    Returns the s-expression text with matched parens, trimmed of outer parens."""
    needle = f'(symbol "{name}"'
    i = text.find(needle)
    if i < 0:
        raise KeyError(f"symbol {name!r} not found in source")
    # Walk paren-matched to find the end of this block.
    depth = 0
    j = i
    in_string = False
    while j < len(text):
        c = text[j]
        if c == '"' and (j == 0 or text[j-1] != '\\'):
            in_string = not in_string
        elif not in_string:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return text[i:j+1]
        j += 1
    raise ValueError("unbalanced parens")

def extract_pin_map(symbol_block: str) -> dict[str, tuple[float, float, int]]:
    """Return {pin_number: (rel_x, rel_y, angle_deg)}.
    angle is the direction the pin extends INTO the body; the connect point is at (rel_x, rel_y)."""
    pins = {}
    # Match (pin <type> <shape> (at X Y A) (length L) ... (number "N" ...))
    pat = re.compile(
        r'\(pin\s+\w+\s+\w+\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)\)\s*\(length\s+[\d.]+\).*?\(number\s+"([^"]+)"',
        re.S,
    )
    for m in pat.finditer(symbol_block):
        x, y, a, num = float(m.group(1)), float(m.group(2)), int(m.group(3)), m.group(4)
        pins[num] = (x, y, a)
    return pins


# ── Composer ────────────────────────────────────────────────────────
def build():
    # 1. Load each source symbol block, re-prefix as "Lib:Name".
    lib_symbol_blocks: list[str] = []
    pin_maps: dict[str, dict[str, tuple[float, float, int]]] = {}  # keyed "Lib:Name"
    for (lib, name), src_path in SOURCES.items():
        src_text = slurp(src_path)
        try:
            block = extract_symbol_block(src_text, name)
        except KeyError as e:
            raise SystemExit(f"FATAL: {e} in {src_path}")
        # Re-prefix:  (symbol "X"  ->  (symbol "Lib:X"
        prefixed = block.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
        lib_symbol_blocks.append(prefixed)
        pin_maps[f"{lib}:{name}"] = extract_pin_map(block)

    # 2. Compose lib_symbols section.
    lib_symbols_sxp = "(lib_symbols\n\t\t" + "\n\t\t".join(
        ln for blk in lib_symbol_blocks for ln in blk.splitlines()
    ) + "\n\t)"

    # 3. Compose symbol placements + per-pin global_labels.
    placements_sxp: list[str] = []
    labels_sxp:     list[str] = []

    placement_by_ref = {p.ref: p for p in PLACEMENTS}
    for p in PLACEMENTS:
        sym_uuid = str(uuid.uuid4())
        lib_id   = f"{p.lib}:{p.name}"
        placements_sxp.append(f'''\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {p.x:.2f} {p.y:.2f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{sym_uuid}")
\t\t(property "Reference" "{p.ref}"
\t\t\t(at {p.x:.2f} {p.y - 18.0:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "{p.value}"
\t\t\t(at {p.x:.2f} {p.y + 18.0:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "{p.footprint}"
\t\t\t(at {p.x:.2f} {p.y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at {p.x:.2f} {p.y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(instances
\t\t\t(project ""
\t\t\t\t(path "/{SHEET_UUID}"
\t\t\t\t\t(reference "{p.ref}") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)''')

    # 4. For each (ref, pin, net) emit a global_label at the pin's world coord.
    #    The label's orientation points AWAY from the symbol body.
    seen_pinrefs: set[tuple[str, str]] = set()
    for ref, pin_num, net in NETS:
        p = placement_by_ref.get(ref)
        if p is None:
            raise SystemExit(f"FATAL: NETS references unknown ref {ref}")
        lib_id = f"{p.lib}:{p.name}"
        pm = pin_maps.get(lib_id, {})
        rel = pm.get(pin_num)
        if rel is None:
            raise SystemExit(f"FATAL: {lib_id} has no pin numbered {pin_num!r}")
        rx, ry, ang_into = rel
        # Pin direction `ang_into` is the direction the pin LINE extends from
        # the connect point into the symbol body. The label should point in the
        # OPPOSITE direction (away from the body).
        ang_away = (ang_into + 180) % 360
        wx, wy = p.x + rx, p.y - ry  # KiCad schematic Y is inverted vs. symbol-local
        label_uuid = str(uuid.uuid4())
        seen_pinrefs.add((ref, pin_num))
        labels_sxp.append(f'''\t(global_label "{net}"
\t\t(shape input)
\t\t(at {wx:.2f} {wy:.2f} {ang_away})
\t\t(effects (font (size 1.27 1.27)))
\t\t(uuid "{label_uuid}")
\t)''')

    # 4b. Emit (no_connect ...) markers for every intentionally-unused pin.
    no_connects_sxp: list[str] = []
    for ref, pin_num in NO_CONNECT_PINS:
        p = placement_by_ref.get(ref)
        if p is None:
            raise SystemExit(f"FATAL: NO_CONNECT_PINS references unknown ref {ref}")
        lib_id = f"{p.lib}:{p.name}"
        rel = pin_maps.get(lib_id, {}).get(pin_num)
        if rel is None:
            raise SystemExit(f"FATAL: {lib_id} has no pin numbered {pin_num!r} (NO_CONNECT)")
        rx, ry, _ang = rel
        wx, wy = p.x + rx, p.y - ry
        nc_uuid = str(uuid.uuid4())
        no_connects_sxp.append(f'\t(no_connect (at {wx:.2f} {wy:.2f}) (uuid "{nc_uuid}"))')

    # 5. Place a PWR_FLAG on each net needing a power_out driver.
    pwr_flag_pin = pin_maps.get("power:PWR_FLAG", {})
    # PWR_FLAG has a single pin numbered "1" at known offset.
    pf_rel = pwr_flag_pin.get("1", (0.0, 0.0, 270))
    for net, fx, fy in PWR_FLAGS:
        sym_uuid = str(uuid.uuid4())
        # Place PWR_FLAG symbol so its pin connect point is at (fx, fy).
        # symbol world = pin_world - rel_pin_offset (with Y inversion).
        sym_x = fx - pf_rel[0]
        sym_y = fy + pf_rel[1]
        placements_sxp.append(f'''\t(symbol
\t\t(lib_id "power:PWR_FLAG")
\t\t(at {sym_x:.2f} {sym_y:.2f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{sym_uuid}")
\t\t(property "Reference" "#FLG{abs(hash((net, fx, fy))) % 100:02d}"
\t\t\t(at {sym_x:.2f} {sym_y - 5.0:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Value" "PWR_FLAG"
\t\t\t(at {sym_x:.2f} {sym_y + 5.0:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {sym_x:.2f} {sym_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at {sym_x:.2f} {sym_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(instances
\t\t\t(project ""
\t\t\t\t(path "/{SHEET_UUID}"
\t\t\t\t\t(reference "#FLG{abs(hash((net, fx, fy))) % 100:02d}") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)''')
        # Attach a global_label at the flag's pin to bind it to the net.
        lbl_uuid = str(uuid.uuid4())
        labels_sxp.append(f'''\t(global_label "{net}"
\t\t(shape output)
\t\t(at {fx:.2f} {fy:.2f} 0)
\t\t(effects (font (size 1.27 1.27)))
\t\t(uuid "{lbl_uuid}")
\t)''')

    # 6. Stitch the whole file.
    schematic = f'''(kicad_sch
\t(version 20240329)
\t(generator "kicad-python")
\t(generator_version "10.0")
\t(uuid "{SHEET_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "Chameleon Mesh Node v1")
\t\t(date "2026-05-16")
\t\t(rev "v1.0-DRAFT")
\t\t(company "Chameleon Mesh Node Project")
\t\t(comment 1 "Dual-radio telemetry motherboard")
\t\t(comment 2 "Seeed Meshtastic Build-Off entry — dual-radio mesh node")
\t\t(comment 3 "Wio-WM1110 + XIAO ESP32-C5 + BQ24074 + BME280")
\t\t(comment 4 "Logical net mapping; PCB routing deferred")
\t)
\t{lib_symbols_sxp}
{chr(10).join(placements_sxp)}
{chr(10).join(labels_sxp)}
{chr(10).join(no_connects_sxp)}
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)
'''
    OUT_SCH.write_text(schematic)
    print(f"wrote: {OUT_SCH}")
    print(f"  {len(PLACEMENTS)} core components placed")
    print(f"  {len(PWR_FLAGS)} PWR_FLAG drivers placed")
    print(f"  {len(NETS)} pin-to-net labels emitted")
    print(f"  {len(NO_CONNECT_PINS)} no_connect markers")
    print(f"  {len(lib_symbol_blocks)} embedded lib_symbols")


if __name__ == "__main__":
    build()
