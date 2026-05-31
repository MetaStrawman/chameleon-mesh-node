#!/usr/bin/env python3
"""Generate the Wio_WM1110 symbol from the official Seeed datasheet pinout.

Source: Wio_WM1110_Module_Datasheet_V1.3.pdf, Table 1 (pages 7-9), sha256
65f80b1347fabb6f12c44156bb6dae875c8be4be534c2f8dce69b7b71fdc18f2.

Replaces the prior 21-pin placeholder. The real module is LGA-80 with
pins around the perimeter; this symbol mirrors that physical layout:
  - Top edge      pins 1-20   (GND ×8 + GPIOs 9-20)
  - Right edge    pins 21-40  (power, LoRa I/O, USB, more GPIOs)
  - Bottom edge   pins 41-60  (GPIOs + SWD + GND 44/62)
  - Left edge     pins 61-80  (RF antennas + GND ×8)

Note: I²C / UART / SPI are NOT dedicated pins on the WM1110 — they are
software-assigned to nRF52840 GPIO via the SDK pin matrix. Common SDK
defaults that the schematic now wires to:
  I²C0 SDA  = P0.26 (module pin 18)
  I²C0 SCL  = P0.27 (module pin 16)
  UART  TX  = P0.06 (module pin 32)
  UART  RX  = P0.08 (module pin 33)
"""
from __future__ import annotations
from pathlib import Path

# ── Pin table (verbatim from datasheet pp. 7-9) ───────────────────────
# Each entry: (number, name, type, description)
# Pin types map to KiCad electrical types:
#   GND       -> power_in
#   VDD_*     -> power_in
#   VBUS      -> power_in   (USB host supply)
#   DN/DP     -> bidirectional
#   LR_DIO*   -> output     (per datasheet "O")
#   ANT_*     -> passive    (RF, not electrically modelled by ERC)
#   P0.xx/P1.xx GPIO -> bidirectional (I/O per datasheet)
#   SWDIO     -> bidirectional
#   SWDCLK    -> input
PINS: list[tuple[int, str, str, str]] = [
    (1,  "GND",      "power_in",      "Ground"),
    (2,  "GND",      "power_in",      "Ground"),
    (3,  "GND",      "power_in",      "Ground"),
    (4,  "GND",      "power_in",      "Ground"),
    (5,  "GND",      "power_in",      "Ground"),
    (6,  "GND",      "power_in",      "Ground"),
    (7,  "GND",      "power_in",      "Ground"),
    (8,  "GND",      "power_in",      "Ground"),
    (9,  "P0.29",    "bidirectional", "MCU GPIO P0.29"),
    (10, "P0.31",    "bidirectional", "MCU GPIO P0.31"),
    (11, "LR_DIO9",  "output",        "LR1110 DOUT (interrupt)"),
    (12, "P0.02",    "bidirectional", "MCU GPIO P0.02"),
    (13, "P0.03",    "bidirectional", "MCU GPIO P0.03"),
    (14, "P0.28",    "bidirectional", "MCU GPIO P0.28"),
    (15, "P0.30",    "bidirectional", "MCU GPIO P0.30"),
    (16, "P0.27",    "bidirectional", "MCU GPIO P0.27 — default I2C0 SCL"),
    (17, "P0.05",    "bidirectional", "MCU GPIO P0.05"),
    (18, "P0.26",    "bidirectional", "MCU GPIO P0.26 — default I2C0 SDA"),
    (19, "P0.07",    "bidirectional", "MCU GPIO P0.07"),
    (20, "P1.08",    "bidirectional", "MCU GPIO P1.08"),
    (21, "VDD_LR",   "power_in",      "Supply voltage for LoRa (1.8-3.7V)"),
    (22, "VDD_LR",   "power_in",      "Supply voltage for LoRa (1.8-3.7V)"),
    (23, "LR_DIO8",  "output",        "LR1110 DOUT"),
    (24, "LR_DIO7",  "output",        "LR1110 DOUT"),
    (25, "P0.11",    "bidirectional", "MCU GPIO P0.11"),
    (26, "P0.16",    "bidirectional", "MCU GPIO P0.16"),
    (27, "VDD_NRF",  "power_in",      "Supply voltage for Bluetooth/nRF (1.7-3.6V)"),
    (28, "VDD_NRF",  "power_in",      "Supply voltage for Bluetooth/nRF (1.7-3.6V)"),
    (29, "P0.00",    "bidirectional", "MCU GPIO P0.00"),
    (30, "P0.01",    "bidirectional", "MCU GPIO P0.01"),
    (31, "P0.04",    "bidirectional", "MCU GPIO P0.04"),
    (32, "P0.06",    "bidirectional", "MCU GPIO P0.06 — default UART TX"),
    (33, "P0.08",    "bidirectional", "MCU GPIO P0.08 — default UART RX"),
    (34, "P1.09",    "bidirectional", "MCU GPIO P1.09"),
    (35, "P0.12",    "bidirectional", "MCU GPIO P0.12"),
    (36, "P0.18",    "bidirectional", "MCU GPIO P0.18"),
    (37, "VBUS",     "power_in",      "USB VBUS (4.35-5.5V)"),
    (38, "P0.14",    "bidirectional", "MCU GPIO P0.14"),
    (39, "P0.13",    "bidirectional", "MCU GPIO P0.13"),
    (40, "DN",       "bidirectional", "USB D-"),
    (41, "DP",       "bidirectional", "USB D+"),
    (42, "P0.15",    "bidirectional", "MCU GPIO P0.15"),
    (43, "P0.17",    "bidirectional", "MCU GPIO P0.17"),
    (44, "GND",      "power_in",      "Ground"),
    (45, "P0.20",    "bidirectional", "MCU GPIO P0.20"),
    (46, "P0.22",    "bidirectional", "MCU GPIO P0.22"),
    (47, "P0.24",    "bidirectional", "MCU GPIO P0.24"),
    (48, "P1.00",    "bidirectional", "MCU GPIO P1.00"),
    (49, "P0.21",    "bidirectional", "MCU GPIO P0.21"),
    (50, "SWDIO",    "bidirectional", "nRF SWD data"),
    (51, "SWDCLK",   "input",         "nRF SWD clock"),
    (52, "P0.25",    "bidirectional", "MCU GPIO P0.25"),
    (53, "P0.23",    "bidirectional", "MCU GPIO P0.23"),
    (54, "P1.01",    "bidirectional", "MCU GPIO P1.01"),
    (55, "P1.02",    "bidirectional", "MCU GPIO P1.02"),
    (56, "P1.03",    "bidirectional", "MCU GPIO P1.03"),
    (57, "P1.05",    "bidirectional", "MCU GPIO P1.05"),
    (58, "P1.04",    "bidirectional", "MCU GPIO P1.04"),
    (59, "P0.09",    "bidirectional", "MCU GPIO P0.09 (NFC1)"),
    (60, "P0.10",    "bidirectional", "MCU GPIO P0.10 (NFC2)"),
    (61, "P0.19",    "bidirectional", "MCU GPIO P0.19"),
    (62, "GND",      "power_in",      "Ground"),
    (63, "ANT_NRF",  "passive",       "Bluetooth Antenna"),
    (64, "GND",      "power_in",      "Ground"),
    (65, "ANT_WIFI", "passive",       "Wi-Fi Scan Antenna"),
    (66, "GND",      "power_in",      "Ground"),
    (67, "ANT_GNSS", "passive",       "GNSS Antenna"),
    (68, "GND",      "power_in",      "Ground"),
    (69, "GND",      "power_in",      "Ground"),
    (70, "GND",      "power_in",      "Ground"),
    (71, "GND",      "power_in",      "Ground"),
    (72, "ANT_LoRa", "passive",       "LoRa Antenna"),
    (73, "GND",      "power_in",      "Ground"),
    (74, "GND",      "power_in",      "Ground"),
    (75, "GND",      "power_in",      "Ground"),
    (76, "GND",      "power_in",      "Ground"),
    (77, "GND",      "power_in",      "Ground"),
    (78, "GND",      "power_in",      "Ground"),
    (79, "GND",      "power_in",      "Ground"),
    (80, "GND",      "power_in",      "Ground"),
]

assert len(PINS) == 80, f"expected 80 pins, got {len(PINS)}"

# ── Perimeter geometry ────────────────────────────────────────────────
# LGA-80 perimeter: 20 pins per side. Body 60×60 mm (rectangle from
# -27.94 to +27.94 each axis). Pins on a 2.54mm pitch around the outside,
# connect-points at ±30.48 (2.54mm clear of the body edge).
BODY  = 27.94    # half-body in mm
PIN_X = 30.48    # connect-point offset
PITCH = 2.54
PIN_LEN = 2.54
SIDE_RANGE_HALF = (20 - 1) * PITCH / 2.0   # 24.13

def pin_position(num: int) -> tuple[float, float, int]:
    """Return (x, y, angle_into_body) for pin number 1..80.
    Pin 1 starts at top-left corner; numbering goes clockwise around
    the package perimeter (top → right → bottom → left)."""
    side, idx = divmod(num - 1, 20)   # side 0..3, idx 0..19
    pos = -SIDE_RANGE_HALF + idx * PITCH
    if side == 0:   # top edge — pins lay left-to-right, extend DOWN (angle 270)
        return (pos, +PIN_X, 270)
    if side == 1:   # right edge — pins lay top-to-bottom, extend LEFT (180)
        return (+PIN_X, +SIDE_RANGE_HALF - idx * PITCH, 180)
    if side == 2:   # bottom edge — pins lay right-to-left, extend UP (90)
        return (+SIDE_RANGE_HALF - idx * PITCH, -PIN_X, 90)
    # side == 3: left edge — pins lay bottom-to-top, extend RIGHT (0)
    return (-PIN_X, -SIDE_RANGE_HALF + idx * PITCH, 0)

# ── Compose the .kicad_sym file ───────────────────────────────────────
header = '''(kicad_symbol_lib
\t(version 20251024)
\t(generator "kicad-python")
\t(generator_version "10.0")
\t(symbol "Wio_WM1110"
\t\t(pin_names
\t\t\t(offset 1.016)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(property "Reference" "U"
\t\t\t(at -27.94 33.02 0)
\t\t\t(effects (font (size 1.524 1.524)))
\t\t)
\t\t(property "Value" "Wio-WM1110"
\t\t\t(at 0 -33.02 0)
\t\t\t(effects (font (size 1.524 1.524)))
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Datasheet" "https://files.seeedstudio.com/products/SenseCAP/Wio-WM1110/Wio-WM1110_Module_Datasheet_V1.3.pdf"
\t\t\t(at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Description" "Wio-WM1110 LGA-80 module: Semtech LR1110 (LoRa + GNSS + Wi-Fi scan) + Nordic nRF52840 (BLE/Thread/Zigbee). Datasheet V1.3, authored against Table 1 pinout. I2C/UART/SPI are not dedicated pins — assigned via the nRF GPIO matrix; this design uses Nordic SDK defaults (I2C0 SDA=P0.26 pin18, SCL=P0.27 pin16; UART TX=P0.06 pin32, RX=P0.08 pin33)."
\t\t\t(at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "Manufacturer" "Seeed Studio"
\t\t\t(at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(property "MPN" "Wio-WM1110"
\t\t\t(at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) (hide yes))
\t\t)
\t\t(symbol "Wio_WM1110_0_1"
\t\t\t(rectangle
\t\t\t\t(start -{B} {B})
\t\t\t\t(end {B} -{B})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)
'''.format(B=BODY)

pin_blocks = []
for num, name, etype, _desc in PINS:
    x, y, ang = pin_position(num)
    pin_blocks.append(
        f'\t\t\t(pin {etype} line\n'
        f'\t\t\t\t(at {x:.2f} {y:.2f} {ang})\n'
        f'\t\t\t\t(length {PIN_LEN})\n'
        f'\t\t\t\t(name "{name}" (effects (font (size 1.016 1.016))))\n'
        f'\t\t\t\t(number "{num}" (effects (font (size 1.016 1.016))))\n'
        f'\t\t\t)'
    )

footer = '\t\t)\n\t)\n)\n'

content = header + "\n".join(pin_blocks) + "\n" + footer

# Write next to the placeholder, ready to swap.
out = Path("./lib/ChameleonMeshNode_Custom.kicad_symdir/Wio_WM1110.kicad_sym")
out.write_text(content)
print(f"wrote: {out}  ({len(PINS)} pins, {out.stat().st_size} bytes)")
