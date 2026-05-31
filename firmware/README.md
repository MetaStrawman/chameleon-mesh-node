# Firmware

## Meshtastic on the nRF52840 (U3)

The Chameleon Mesh Node v1 hosts the Meshtastic stack on the nRF52840 core of the Wio-WM1110. Upstream:

- Project: https://meshtastic.org/
- Firmware repo: https://github.com/meshtastic/firmware

A hardware variant file specific to this board will be added here once submitted upstream. Until then, the upstream `WM1110_GENERIC_LR1110` variant is a near-fit; the only deviations are the BME280 I²C address (this board uses 0x76, not 0x77) and the ESP32-C5 companion-wake GPIO.

## ESP32-C5 companion firmware

The ESP32-C5 (U2) holds a small UART-bridge + provisioning helper. It is NOT continuously running. It powers on only when the operator presses the user button on the enclosure or when the nRF52840 explicitly toggles the companion-wake GPIO.

A reference companion-firmware build script (PlatformIO `platformio.ini`) will be added here.

## Programming interfaces

| Target | Interface | Connector |
|---|---|---|
| nRF52840 (U3) | SWD | TC2030 (Tag-Connect) footprint on PCB underside |
| ESP32-C5 (U2) | USB-Serial | Onboard via J1 USB-C |
| BME280 (U4) | I²C from U2 | No separate programming interface |

## Bootloader posture

The nRF52840 ships with the Adafruit nRF52 bootloader (DFU-over-USB) pre-installed by Seeed in factory-flashed Wio-WM1110 modules. First-time Meshtastic flash is via SWD using a programmer such as a Black Magic Probe, Segger J-Link EDU, or a generic CMSIS-DAP adapter. Subsequent firmware updates are via the standard Meshtastic OTA path over BLE.

The ESP32-C5 ships with the Espressif ROM bootloader; first flash and all subsequent updates are over USB-C.
