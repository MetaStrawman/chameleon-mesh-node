# Build Guide — Chameleon Mesh Node v1

## BOM

| Ref | Part | Package | Manufacturer P/N | Source |
|---|---|---|---|---|
| U1 | Single-cell LiPo charger, USB priority | QFN-10 | TI BQ24074RGT | DigiKey / Mouser |
| U2 | ESP32-C5 SoM (Wi-Fi 6 / BLE / 802.15.4) | XIAO SMD | Seeed XIAO-ESP32-C5 | Seeed Studio |
| U3 | LR1110 LoRa+GNSS + nRF52840 module | LGA-80 | Seeed Wio-WM1110 | Seeed Studio |
| U4 | Environmental sensor (T/H/P) | LGA-8 | Bosch BME280 | DigiKey / Mouser |
| J1 | USB-C receptacle, 14-pin | SMD | Generic | LCSC |
| J2 | LiPo battery connector | JST-PH 2-pin SMD | Generic | DigiKey |
| (passives) | Caps, resistors, ferrite beads | 0402 / 0603 | various | — |
| Antennas | LoRa whip (U.FL pigtail) + on-board 2.4 GHz trace | — | varies | — |
| Battery | LiPo single cell, ≥ 1000 mAh recommended | — | varies | — |

A consolidated CSV BOM with LCSC/Mouser part numbers will be added before Gerber export.

## First power-on checklist

1. **Visual inspect** — verify no solder bridges around the QFN-10 (U1) and LGA-80 (U3). These are the densest packages.
2. **Power smoke test** — apply 5 V via USB-C with no battery connected. Verify VSYS sits at 4.4 V ± 0.1 V (BQ24074 internal regulator). Total current draw should be < 30 mA with both modules in their default boot state.
3. **Battery attach** — plug in the LiPo battery. Verify the BQ24074 enters CHARGE state (CHRG pin low if a status LED is fitted).
4. **First firmware** — flash the Meshtastic nRF52840 variant onto U3 via SWD (TC2030 footprint included). See `firmware/` for the device-specific configuration overlay.
5. **Companion** — flash the ESP32-C5 stub firmware via USB-C (no separate programmer needed; the C5 has built-in USB-Serial). See `firmware/`.
6. **Mesh join test** — provision the node onto a Meshtastic mesh via the official mobile app over BLE. Verify it announces itself and receives messages.

## Reflow profile

Standard lead-free reflow, peak 245 °C, 60-90 s above 217 °C. Pre-heat ramp 1.5 °C/s. The LR1110 inside the WM1110 has the usual ROHS reflow tolerance; do not exceed 250 °C peak.

## Assembly notes

- The Wio-WM1110 has a metal RF shield on the underside facing the PCB. Make sure your stencil aperture for the module's GND pad is correctly sized; under-paste here causes RF coupling issues.
- The XIAO ESP32-C5's USB-C testpoints under the module are NOT a programming interface — they are factory test only. Program through the J1 USB-C connector.
- BME280 is sensitive to airflow direction. Position the enclosure vent so airflow crosses the sensor's metal lid, not the side openings.
