# Power Design — Chameleon Mesh Node v1

## Goals

1. Operate indefinitely on a single LiPo cell topped up by a 5-6 V solar panel during daylight hours.
2. Reach < 50 µA in deep sleep so a 2000 mAh cell can carry the node through ≥ 7 cloudy days without solar.
3. Charge from a standard USB-C wall adapter when on-bench for provisioning and OTA work.
4. Survive a depleted battery + brownout → 5 V USB-C reconnect without operator intervention.

## Input + charger

Texas Instruments **BQ24074** is the regulator + linear charger. Selected over the more common MCP73831 for three reasons:

- **USB-priority logic.** When 5 V is present on VIN, the chip switches the system load from the battery to VIN and uses the residual current capacity to charge the battery. The MCP73831 cannot do this without external pass FETs.
- **Up to 6 V VIN tolerance.** Matches the Voc of a 5 V/1 W cell-phone-class solar panel under no-load conditions, which is the cheapest panel form factor the node is likely to be paired with.
- **Programmable charge current** via an external `ISET` resistor. The board ships with a 1.13 kΩ resistor giving 1.1 A nominal, which a 2000 mAh LiPo can accept safely (0.55 C).

## Sleep current target

| State | Estimated current | Source |
|---|---|---|
| nRF52840 deep sleep (RAM retain, RTC) | 1.5 µA | Nordic datasheet |
| LR1110 in OFF mode | < 1 µA | Semtech datasheet |
| ESP32-C5 not powered (gated) | 0 µA | gated by GPIO |
| BME280 in sleep | 0.1 µA | Bosch datasheet |
| BQ24074 quiescent (no charge) | ~20 µA | TI datasheet |
| 3.3 V LDO leak inside WM1110 | ~5 µA | inferred from module specs |
| **TOTAL** | **~28 µA** | — |

Margin to the 50 µA target is comfortable, but assumes the ESP32-C5 is fully off (not deep-sleep). v1 ships with a hard-gate via a GPIO + load switch; the ESP32-C5 supply is cut entirely between operator-initiated sessions.

## Solar panel sizing

A 5 V / 1 W panel produces ~ 200 mA at Pmax in full sun. With the BQ24074 charging at 1.1 A nominal, the panel will charge at panel-current-limited rate when sunlight is the only source. Realistic daily harvest from a 1 W panel placed in a moderately good outdoor location: ~ 200 mAh on a clear day, ~ 80 mAh on a heavily overcast day.

A node consuming an average ~5 mA (Meshtastic 1-minute interval, position + telemetry beacons) draws ~ 120 mAh per day. The energy budget closes positive in average-daylight conditions; the battery exists to ride through several cloudy days, not to do the daily lifting.

## Brownout + reconnect

If the LiPo drops below 3.0 V, the BQ24074 disconnects the system load to protect the cell. On the next USB-C connection, the chip enters PRECHARGE for a brief soft-start, and the nRF52840 boot will re-run cleanly. The Meshtastic firmware persists its mesh state to flash so the node rejoins the network without re-provisioning.

## What v1 does NOT have

These are planned for v2 (out of scope for this contest submission):

- Coulomb-counting fuel gauge (BQ27441 family) — v1 reports battery state via voltage approximation only
- INA219 input-current monitor — useful for diagnosing solar performance in the field
- Hard reset / wake button accessible from outside the enclosure
- USB-C data lines (v1 is power-only on the USB-C; data is via UART/SWD pads only)
