# Architecture — Chameleon Mesh Node v1

## Block diagram

```
              ┌─────────────────────────────────────────────────────────┐
              │                                                         │
   USB-C ─────┤ U1 BQ24074  ──(VSYS)──┬── U2 XIAO ESP32-C5 ──── ANT_24G │
   (5V in)    │ LiPo charger          │   Wi-Fi 6 / BLE 5 / 802.15.4    │
   J1         │ USB-priority,         │                                 │
              │ solar OK to 6 V       ├── U3 Wio-WM1110 ──┬── ANT_LORA  │
              │                       │  LR1110 + nRF52840 ├── ANT_GNSS │
              │                       │  (Meshtastic host) └── (Wi-Fi   │
              │                       │                       scan: shared
              │                       │                       with C5)  │
   LiPo  ─────┤ J2 JST-PH         (3.3V via internal LDOs in each module)
   battery    │                       │                                 │
              │                       └── U4 BME280 (I²C, addr 0x76)    │
              │                                                         │
              └─────────────────────────────────────────────────────────┘
```

## Why this topology

The nRF52840 inside the Wio-WM1110 hosts the Meshtastic stack. It owns the LoRa radio, the GNSS receiver (LR1110 has both on one die), and the Meshtastic mesh state machine. This is the "always-on" side of the board: it spends most of its life in deep sleep, wakes on radio events or scheduled transmissions, and goes back down.

The ESP32-C5 is the "burst-on" side. It stays unpowered (or in deep-sleep) by default. The operator wakes it intentionally during provisioning, OTA firmware updates, or bulk-data offload. Its Wi-Fi 6 / BLE / 802.15.4 stack consumes meaningful current and is gated behind explicit operator intent rather than running continuously.

## Radio zoning

The two antennas are placed at opposite edges of the board with the keep-out and ground pour separating them. The LoRa antenna is on a U.FL pigtail to allow the operator to mount a long whip externally to the enclosure; the 2.4 GHz Wi-Fi/BLE antenna uses a small PCB-trace antenna sized for the ESP32-C5's reference design (close-in coverage is the only requirement).

A shared GND pour on both copper layers provides the return path. Vias stitch the two pours together along the board midline, biased toward the LoRa antenna feed where the cleanest reference is most important.

## I²C bus

The BME280 is the only I²C peripheral in v1, on the ESP32-C5's bus at address 0x76. The bus is exposed at a 0.1" header pad pattern for future expansion (additional sensors, a real-time clock, an OLED display for field provisioning).

## Power tree summary

- Single 5 V input via USB-C (J1, 14-pin)
- BQ24074 charges a single-cell LiPo on J2 (JST-PH)
- VSYS feeds both U2 and U3 module-internal LDOs
- Battery monitoring is via the BQ24074's internal current sense (status only); no dedicated fuel gauge in v1 (planned for v2)

See `power-design.md` for the full power budget and sleep-current analysis.
