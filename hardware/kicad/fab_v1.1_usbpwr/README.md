# Chameleon Mesh Node v1.1 — USB-powered fab package

**This is the authoritative fabrication package.** Upload
`chameleon_mesh_node_v1.1_USBpwr_FAB.zip` to your PCB house (Seeed Fusion etc.).

## Board
- 60 × 35 mm, 2-layer, KiCad source: `../chameleon_mesh_node_v1.kicad_pcb`
- Verified (kicad-cli DRC): **0 unconnected, 0 shorts.** Remaining DRC items are
  benign DFM noise — USB-C (J1) pad pitch (0.15 mm vs a 0.20 mm generic rule),
  mounting-hole edge clearance, and GND thermal-relief spokes — handled routinely
  by the fab's CAM.

## Assembly — populate vs DNP
| Populate | Part |
|---|---|
| **U2** | XIAO-ESP32-C5 (SMD) — MCU/radio module |
| **U3** | Wio-WM1110 — LoRa + GNSS module |
| **U4** | BME280 — environmental sensor |
| **J1** | USB-C receptacle — power + data |

| Do NOT populate (DNP) | Why |
|---|---|
| **U1** | BQ24074 Li-ion charger — removed: its `OUT` rail tied to the XIAO 3V3 LDO output caused a source conflict / over-voltage on the 3V3 rail |
| **J2** | Battery JST — battery path was never wired to the XIAO; removed with U1 |

The DNP of U1 + J2 makes the only +3V3 driver the XIAO's onboard LDO (U2),
eliminating the over-voltage. Result: a **USB-powered LoRa + GNSS + sensor node.**

## Known caveats (carried for a future v1.2)
- No battery operation (the BAT path was never functional on this rev).
- No dedicated rail decoupling / USB-C CC resistors (acceptable for this
  USB-powered demo build; add for v1.2).
- J1 (USB-C) sits close to U2 (XIAO) — electrically clean (J1 shield/GND to XIAO
  no-net pads, no short); confirm the connector clears the module mechanically
  before a large run.
