# Third-Party Notices & Attribution

The Chameleon Mesh Node design incorporates the following third-party
components. Each retains its upstream license; inclusion here does not imply
endorsement by the respective vendors. Trademarks are property of their owners.

## KiCad footprint libraries

| Library (as referenced in `hardware/kicad/fp-lib-table`) | Source | License | Notes |
|---|---|---|---|
| `Seeed_XIAO` (XIAO ESP32-C5 footprint) | Seeed Studio Open Parts Library | CC-BY-SA 4.0 | See `hardware/kicad/lib/LICENSE_Seeed_OPL` once the `lib/` directory is committed (see `SUBMISSION_CHECKLIST.md`). |
| `ChameleonMeshNode_Custom` (Wio-WM1110 LGA-80 footprint) | Derived from the official Seeed Wio-WM1110 KiCad library (`MODULE72_0D9_20X20X2MM.kicad_mod`), vendored and renamed `Wio_WM1110_LGA80.kicad_mod` | Per Seeed Wio-WM1110 KiCad library terms | Verify and copy the upstream LICENSE into the vendored footprint directory before publishing. |
| `Connector_USB`, `Connector_JST`, `Package_DFN_QFN`, `Package_LGA` | KiCad standard footprint libraries (v10.0.3) | CC-BY-SA 4.0 with exception | Bundled with KiCad; redistributed under the KiCad library license. |

## Software / firmware

| Component | Source | License |
|---|---|---|
| Meshtastic firmware (host stack on the nRF52840) | https://github.com/meshtastic/firmware | GPL-3.0-or-later |
| Meshtastic project / protocol | https://meshtastic.org/ | — |

## Silicon datasheets / reference designs

Layout follows the manufacturer reference-design and layout guidelines for:
Semtech LR1110, Nordic nRF52840, Espressif ESP32-C5, Bosch BME280, and
Texas Instruments BQ24074. Datasheets are © their respective manufacturers
and are **not** redistributed in this repository.
