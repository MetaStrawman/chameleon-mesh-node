# Power Design — Chameleon Mesh Node v1.2

## Summary

v1.2 is **USB-powered only**. The board takes 5 V from the USB-C port on the
Seeed XIAO ESP32-C5 (J1); the XIAO's onboard regulator supplies the 3.3 V rail
to the rest of the board. The earlier onboard Li-ion charger (TI BQ24074, U1) and
the LiPo battery connector (J2) were already populated DNP and were deleted in
v1.2 — their dead VBAT traces were shorting the relocated mounting hole, and
removing them cleared the short. There is no onboard battery charging, fuel gauge,
or solar input on this revision.

## Power tree

- 5 V enters at the USB-C receptacle (J1) and the XIAO ESP32-C5's VBUS pin.
- The XIAO's onboard 3.3 V regulator feeds the +3V3 rail.
- +3V3 supplies the Wio-WM1110 module (U3) and the BME280 sensor (U4) through
  their module-internal LDOs.

## What v1.2 does NOT have

Considered and deliberately left off this revision:

- Onboard Li-ion charging (the BQ24074 path) — removed; the board runs from USB.
- Battery connector / single-cell LiPo operation — removed with the charger.
- Solar / harvesting input.
- Coulomb-counting fuel gauge or input-current monitor.

## Battery operation (future revision)

A battery-capable revision would re-add a charger (e.g. BQ24074 or MCP73831) and a
JST-PH cell connector on a board outline that keeps the charger's VBAT traces clear
of the mounting holes. That is out of scope for this submission, which targets a
verified, fabbable USB-powered two-radio board.
