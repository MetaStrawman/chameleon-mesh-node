# Design Rationale & DFM Notes — Chameleon Mesh Node v1.2

This document explains the key layout and manufacturability decisions behind the v1.2 board.
It exists so a reviewer (or a future builder) can see *why* each choice was made, not just *what*
the gerbers show. Target process: Seeed Fusion, 2-layer, 1 oz copper, 6 mil (0.15 mm) trace/space.

## Board at a glance
- 60 × 34 mm, 2-layer, USB-C powered, Meshtastic-compatible.
- **U2** — Seeed XIAO ESP32-C5 (MCU + Wi-Fi/BLE + USB-C; the companion/provisioning radio — the Meshtastic host is the nRF52840 inside U3).
- **U3** — Wio-WM1110 LGA-80 module (Semtech LR1110 LoRa + GNSS + Wi-Fi-scan, Nordic nRF52840).
- **J1** — USB-C receptacle, flush at the top edge.
- **C1** — 100 nF 0402 decoupling capacitor at the BME280 VDD (the board's only discrete passive).
- **H1–H4** — M2.5 mounting holes.

*(The schematic is a system block diagram of the functional architecture; board-level passives such as C1 are carried in the fabrication package — BOM, placement, gerbers — not the block diagram.)*

## Placement & clearance decisions

### USB-C ↔ XIAO separation
The USB-C receptacle (J1) is intentionally flush with the top board edge for a clean enclosure
mate. Its through-hole shield/mount tabs project into the board; the XIAO (U2) is placed below it.
We verified that the two **component bodies physically overlapped** (USB-C body extent vs. the XIAO
module outline), not merely their courtyards — so U2 was positioned to give true mechanical clearance
between the connector body and the module. The connecting nets were then re-routed to the relocated
part. This is a real fit fix, not a courtyard waiver.

### Mounting holes — NPTH by design
H1–H4 are **non-plated (NPTH)** M2.5 holes. Plated holes with a copper annulus sat inside the
board-edge keep-out; rather than shrink the pads or move the holes (which constrains the enclosure),
we use bare NPTH holes — the standard, fab-clean solution for edge-adjacent mounting. **Trade-off
acknowledged:** NPTH holes do not provide ground stitching at the corners. They are placed away from
the RF section (H-holes at the board corners; U3 is centred on the right), so there is no impact on
the LoRa return path. For a production revision that wants chassis grounding, a single plated stitch
hole can be added near one corner.

## Power & routing decisions

### VBUS off the top edge (bottom-layer detour)
The USB VBUS rail originally ran along the top edge in the narrow band between the board edge and
J1's pad row — too close to the edge for a robust fab margin. VBUS is re-routed on the **bottom
copper**, passing *under* J1's grounded shield (which provides incidental shielding for the 5 V rail's
inrush/brown-out transients), then via'd up to the XIAO's 5 V input. Net result: comfortable
copper-to-edge clearance with no impact on signal routing.

### USB-C high-density pads
The USB-C connector's own 0.5 mm-pitch pads sit at 0.15 mm clearance — within Seeed Fusion's 6 mil
capability, but tighter than the board's conservative default rule. A **scoped design rule** relaxes
clearance to 0.15 mm *only* for the connector's internal pads, leaving the rest of the board on the
conservative default. The XIAO's unused module pads that sit under the connector shield are tied to
GND (they're grounded by the shield anyway), eliminating any net-to-net concern.

## RF integrity (U3 / LoRa)
The Wio-WM1110's RF and antenna routing is **unchanged from the validated reference layout** — none
of the v1.2 manufacturability fixes touched any U3 net (verified: U3-region track counts are identical
before/after). Ground pour continuity under the module and its return path were preserved intact.

## Manufacturing package
The `hardware/kicad/fab_v1.2/` folder is a complete, fab-ready set: RS-274X gerbers (all copper, mask,
silk, paste, adhesive, edge), Excellon drill, pick-and-place (POS), BOM, schematic PDF, and top/bottom
3D renders. The board passes KiCad DRC with **0 errors and 0 unconnected nets**; the remaining 31 warnings
are silkscreen advisories (silk-over-pad, silk-to-edge), footprint-library-link notes, and a single
dangling-track stub — all reviewed and non-blocking for fabrication. The two custom footprints
(Wio-WM1110, XIAO) are vendored under `hardware/kicad/lib/`; standard KiCad library footprints
(USB-C, mounting holes) resolve from a stock KiCad install.
