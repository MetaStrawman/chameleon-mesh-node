# Build Guide — Chameleon Mesh Node v1.2

## BOM

| Ref | Part | Package | Manufacturer P/N | Source |
|---|---|---|---|---|
| U2 | ESP32-C5 SoM (Wi-Fi 6 / BLE / 802.15.4) | XIAO SMD | Seeed XIAO-ESP32-C5 | Seeed Studio |
| U3 | LR1110 LoRa+GNSS + nRF52840 module | LGA-80 | Seeed Wio-WM1110 | Seeed Studio |
| U4 | Environmental sensor (T/H/P) | LGA-8 | Bosch BME280 | DigiKey / Mouser |
| J1 | USB-C receptacle (power + data) | SMD | GCT USB4085 (or equiv.) | LCSC |
| C1 | 100 nF decoupling cap (BME280 VDD) | 0402 | generic X7R 16V | LCSC |
| (passives) | Caps, resistors, ferrite beads | 0402 / 0603 | various | — |
| Antennas | LoRa whip (U.FL pigtail) + on-board 2.4 GHz trace | — | varies | — |

A consolidated CSV BOM is in `hardware/bom/`. Power is module-integrated (the XIAO ESP32-C5 and Wio-WM1110 carry their own regulation and decoupling); the one discrete part is **C1, a 100 nF 0402 decoupling capacitor at the BME280 VDD** (Bosch datasheet). The schematic is a system block diagram and abstracts board-level passives — C1 appears in the BOM, placement, and gerbers.

## First power-on checklist

1. **Visual inspect** — verify no solder bridges around the LGA-80 (U3, Wio-WM1110) and the XIAO ESP32-C5 (U2). U3 is the densest package.
2. **Power smoke test** — apply 5 V via the USB-C port. Verify the +3V3 rail sits at 3.3 V ± 0.1 V (XIAO ESP32-C5 onboard regulator). Total current draw should be < 30 mA with both modules in their default boot state.
3. **First firmware** — flash the Meshtastic nRF52840 variant onto U3 via the SWD pads (a TC2030-style tag-connect footprint is on the PCB; no connector is populated — programming uses a pogo-pin clip). See `firmware/` for the device-specific configuration overlay.
4. **Companion** — flash the ESP32-C5 stub firmware via USB-C (no separate programmer needed; the C5 has built-in USB-Serial). See `firmware/`.
5. **Mesh join test** — provision the node onto a Meshtastic mesh via the official mobile app over BLE. Verify it announces itself and receives messages.

## Reflow profile

Standard lead-free reflow, peak 245 °C, 60-90 s above 217 °C. Pre-heat ramp 1.5 °C/s. The LR1110 inside the WM1110 has the usual ROHS reflow tolerance; do not exceed 250 °C peak.

## Assembly notes

- The Wio-WM1110 has a metal RF shield on the underside facing the PCB. Make sure your stencil aperture for the module's GND pad is correctly sized; under-paste here causes RF coupling issues.
- The XIAO ESP32-C5's USB-C testpoints under the module are NOT a programming interface — they are factory test only. Program through the J1 USB-C connector.
- BME280 is sensitive to airflow direction. Position the enclosure vent so airflow crosses the sensor's metal lid, not the side openings.
