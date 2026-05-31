// SPDX-License-Identifier: GPL-3.0-or-later
//
// Chameleon Mesh Node v1 — Meshtastic hardware variant (nRF52840 + LR1110)
// Host: Nordic nRF52840 core of the Seeed Wio-WM1110 (Semtech LR1110).
//
// STATUS: stub / work-in-progress. This board is electrically a close
// relative of the upstream Seeed Wio-WM1110 variant, so the LR1110 radio,
// GNSS, and SPI wiring are INHERITED from that upstream variant and are NOT
// redefined here. Only the two board-specific deviations are expressed below.
// Build by applying this variant on top of the upstream base env
// (see platformio.ini) — do not treat these defines as a complete pinmap.
//
// Upstream base:  meshtastic/firmware  variant  WM1110_GENERIC_LR1110
//                 (https://github.com/meshtastic/firmware)
//
// Board deviations from the upstream Wio-WM1110 reference:
//   1. On-board BME280 environmental sensor at I2C address 0x76 (not 0x77).
//   2. ESP32-C5 companion-wake GPIO (nRF drives this line to power the
//      XIAO ESP32-C5 only for provisioning / OTA / bulk offload).
//
// Pin facts confirmed from this board's netlist (nRF52840 P-port numbering):
//   I2C0  SDA = P0.26   SCL = P0.27   (BME280 + any expansion)
//   UART  TX  = P0.06   RX  = P0.08   (companion link to ESP32-C5)
// All LR1110 SPI / BUSY / RESET / DIO / GNSS / RF-switch lines: inherited
// from the upstream WM1110 variant (module-internal, fixed by the WM1110).

#pragma once

// --- Environmental sensor (board deviation #1) -----------------------------
#define HAS_BME280            1
#define BME_280_ADDR          0x76   // this board straps SDO low

// --- Companion ESP32-C5 wake line (board deviation #2) ----------------------
// Define to the actual nRF GPIO once the net is pulled from the schematic.
// #define PIN_COMPANION_WAKE  (0 + NN)

// --- Confirmed I2C / UART pins (see header note) ----------------------------
#define I2C_SDA               (0 + 26)   // P0.26
#define I2C_SCL               (0 + 27)   // P0.27
#define PIN_SERIAL2_TX        (0 + 6)    // P0.06  -> ESP32-C5
#define PIN_SERIAL2_RX        (0 + 8)    // P0.08  <- ESP32-C5

// NOTE: radio (LR1110), GNSS, button, LED, battery-sense, and SWD defines are
// supplied by the upstream WM1110_GENERIC_LR1110 variant and intentionally
// omitted here to avoid divergence. See SUBMISSION_CHECKLIST.md for the
// remaining bring-up tasks before this variant is upstreamed.
