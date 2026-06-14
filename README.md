# Chameleon Mesh Node

> A rugged, dual-radio environmental telemetry node built on the Meshtastic + LoRa stack.

**Submission:** Seeed Studio Meshtastic Build-Off 2026
**Status:** Design complete & verified — routed, DRC-clean (0 errors / 0 unconnected; 31 cosmetic silkscreen/DFM warnings), Gerbers exported. **Pre-fabrication** (first article not yet ordered).
**Hardware revision:** v1.2
**License:** Multi-license open source — CERN-OHL-S-2.0 (hardware), GPL-3.0-or-later (Meshtastic firmware variant), MIT (tooling). See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).

![Chameleon Mesh Node v1.2 — top](assets/chameleon_mesh_node_v1_top.png)

*3D render (top). Bottom: [`assets/chameleon_mesh_node_v1_bottom.png`](assets/chameleon_mesh_node_v1_bottom.png).*

## What it is

The Chameleon Mesh Node is a single-board, USB-powered field appliance for Meshtastic telemetry. It joins a Meshtastic mesh on sub-GHz LoRa for resilient long-range messaging, reads local environment with an on-board sensor, and exposes a Wi-Fi / BLE side-channel for short-range provisioning and bulk-data offload.

Designed as a compact, regenerable two-radio Meshtastic reference board.

## Why dual radio

Most off-the-shelf Meshtastic nodes pick one path: a LoRa-only board that needs a phone to provision, or a Wi-Fi-only "smart sensor" that needs an AP within range. Neither survives a real off-grid deployment where the closest infrastructure is hours away.

This board pairs **two complementary radio subsystems on one PCB**:

| Subsystem | Role | Module |
|---|---|---|
| Long-range mesh | Meshtastic LoRa + GNSS time-sync + Wi-Fi scan for opportunistic uplink | Seeed **Wio-WM1110** (Semtech LR1110 + Nordic nRF52840) |
| Local-area + provisioning | Wi-Fi 6 / BLE 5 / 802.15.4 for setup, OTA, and bulk data offload to a passing operator's phone | Seeed **XIAO ESP32-C5** |

Both radios cohabit one 60×34 mm 2-layer board, with explicit RF zoning and a shared ground pour designed to keep mutual desense within acceptable limits for an environmental-sensing-class duty cycle.

## Top-level specs

| | |
|---|---|
| Dimensions | 60 × 34 mm, 2-layer FR-4 |
| MCU | Nordic nRF52840 (Meshtastic firmware host) + Espressif ESP32-C5 (companion) |
| Radios | Semtech LR1110 (sub-GHz LoRa, GNSS, passive Wi-Fi scan); Wi-Fi 6 / BLE 5 / 802.15.4 |
| Power input | USB-C 5 V (XIAO ESP32-C5 onboard port) |
| Environmental sensor | Bosch BME280 (temperature, humidity, barometric pressure, I²C) |
| Operating temperature | -20 °C to +60 °C (designed; pending environmental test) |

## Repository layout

```
chameleon_mesh_node/
├── README.md                — this file
├── LICENSE                  — multi-license map (see also LICENSES/, NOTICE.md)
├── LICENSES/                — full license texts (CERN-OHL-S-2.0, GPL-3.0, MIT)
├── NOTICE.md                — third-party attribution
├── SUBMISSION_CHECKLIST.md  — Build-Off submission readiness gate
├── assets/                  — 3D renders
├── docs/
│   ├── architecture.md      — block diagram, radio zoning, antenna feeds
│   ├── build-guide.md       — BOM, assembly notes, first-power-on checklist
│   └── power-design.md      — USB-C power input and module power tree
├── hardware/
│   ├── kicad/               — KiCad 10 project (schematic, PCB, footprints, gerber zips)
│   ├── gerbers/             — extracted v1.2 Gerbers + Excellon drill (fab-ready)
│   └── scripts/             — Python composers that regenerate schematic + PCB from source
├── firmware/                — Meshtastic nRF52840 variant (variant.h + platformio.ini) + ESP32-C5 stub
└── enclosure/cad/           — 3D-printable case (planned, post-fab)
```

The KiCad project is fully regenerable: `python3 hardware/scripts/build_schematic.py` rebuilds the schematic from the Python composer, and `python3 hardware/scripts/build_pcb.py` rebuilds the pre-placed PCB. You can wipe the `.kicad_*` files and reproduce the design from source.

## How it uses Meshtastic

The Chameleon Mesh Node **is a Meshtastic node.** The Nordic nRF52840 core of the
Wio-WM1110 runs the [Meshtastic firmware](https://github.com/meshtastic/firmware);
the Semtech LR1110 is its sub-GHz LoRa radio (plus GNSS time-sync and passive
Wi-Fi scan). It joins a Meshtastic mesh, announces itself, relays messages, and
publishes its BME280 environmental readings as Meshtastic telemetry — provisioned
over BLE with the standard Meshtastic mobile app.

Because the base board (Seeed Wio-WM1110 / nRF52840 + LR1110) is already supported
upstream, this project ships as an **incremental hardware variant**, not a new port.
The board-specific deltas (BME280 at I²C `0x76`, an ESP32-C5 companion-wake GPIO)
are captured in [`firmware/variant.h`](firmware/variant.h) +
[`firmware/platformio.ini`](firmware/platformio.ini), layered on the upstream
Wio-WM1110 build environment. See [`firmware/README.md`](firmware/README.md).

## Design state & verification

- Schematic ERC: **0 errors / 0 warnings** (KiCad 10).
- PCB: 2-layer routed (top-copper signal, bottom-copper VBUS detour with vias), 3 GND zones poured, RF-zoned placement.
- Post-route DRC: **0 errors / 0 unconnected / 31 warnings** (cosmetic silkscreen-over-pad, silk-to-edge, library-footprint, and one dangling-track advisory; non-blocking for fabrication — see `docs/design-rationale.md`).
- Gerbers + Excellon drill exported (`hardware/gerbers/`).
- v1.1 → v1.2: top edge truncated 60×40 → 60×34 mm so the USB-C mouth is flush with the board edge (the earlier board had the connector inset and the cable could not seat); the DNP BQ24074 charger (U1) and the LiPo connector (J2) were deleted (their dead VBAT traces shorted the relocated mounting hole), leaving the board USB-powered only; mounting holes relocated, routing and GND zones refilled.

## Status

The board is **design-complete and verified** — schematic + ERC clean, RF-zoned
placement, routing and ground pour done, DRC clean (0 errors / 0 unconnected), and
the full fabrication package (gerbers, drill, BOM, placement, schematic PDF, 3D
renders) is exported and committed. This revision is fab-ready.

**Next:** first-article prototype, board bring-up (power smoke test, Meshtastic
flash over SWD, mesh-join test), deep-sleep current measurement, upstreaming the
Meshtastic variant, and an enclosure design.

## License

Multi-license open source — see [`LICENSE`](LICENSE) for the per-component map and
[`LICENSES/`](LICENSES/) for full texts. Hardware: **CERN-OHL-S-2.0**. Meshtastic
firmware variant: **GPL-3.0-or-later**. Tooling/generators: **MIT**. Third-party
components retain their upstream licenses ([`NOTICE.md`](NOTICE.md)).

## Acknowledgments

- **Seeed Studio** for the Wio-WM1110 module, the XIAO ESP32-C5, and the Meshtastic Build-Off platform
- The **Meshtastic** project for the firmware and the mesh protocol
- **Semtech**, **Nordic**, **Espressif**, **Bosch** for the silicon
- **KiCad** for the EDA toolchain (v10.0.3 used)

## Contact

See repository issues for design questions, build reports, or fork notifications.
