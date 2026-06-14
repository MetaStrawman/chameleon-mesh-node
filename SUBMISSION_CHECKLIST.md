# Meshtastic Build-Off 2026 — Submission Readiness

Requirements verified 2026-05-28. Contest = submit a **GitHub Issue**
with the template (name, email, **public repo link**, 200+ char description, tech
stack); repo must be **public** with a detailed README; **all work open-source**
(MIT/Apache/GPL/similar); deadline **Aug 2026**; judged on Innovation / Technical
Quality / Completeness / Impact / Presentation.

## ✅ Done (this pass)
- [x] Multi-license added — `LICENSE` map + `LICENSES/{CERN-OHL-S-2.0,GPL-3.0-or-later,MIT}.txt`.
- [x] `NOTICE.md` — third-party attribution (Seeed XIAO CC-BY-SA-4.0, Wio footprint, KiCad libs, Meshtastic GPL).
- [x] README rewritten — stale "awaiting routing/gerbers" status fixed → accurate fab-ready v1.2; added renders, "How it uses Meshtastic", design-state/DRC, roadmap, license sections.
- [x] Firmware proof-of-work — `firmware/variant.h` + `firmware/platformio.ini` (incremental variant on upstream Wio-WM1110 base; documents the 2 board deltas: BME280@0x76, C5-wake GPIO).
- [x] Gerbers extracted to browsable `hardware/gerbers/` (v1.2 set; canonical fab package at `hardware/kicad/fab_v1.2/`).
- [x] 3D renders generated headlessly → `assets/` (top + bottom).

## ⛔ Operator-only (cannot be done from here)
- [ ] **Create the PUBLIC GitHub repo** — extract `chameleon_mesh_node/` as a *standalone* repo. **Do NOT push the private monorepo.** Nothing outside this folder may ship.
- [ ] **Name + email + GitHub account** for the Issue submission template.
- [ ] **File the submission Issue** at `github.com/Seeed-Projects/meshtastic-build-off-2026` (Issue → submission template).
- [ ] Set the real copyright holder in `LICENSES/MIT.txt` (currently placeholder "Chameleon Mesh Node Project").

## ⚠️ Must-fix before publishing (gaps found, need a working session)
- [x] **Footprint libraries vendored.** `lib/ChameleonMeshNode_Custom.pretty` (Wio-WM1110 LGA-80 + MountingHole_M2.5) and `lib/Seeed_XIAO.pretty` + `lib/LICENSE_Seeed_OPL` are now committed under `hardware/kicad/lib/`; `fp-lib-table` points to `${KIPRJMOD}/lib/*.pretty`. Project is regenerable.
- [x] **OPSEC rename + scrub complete.** Custom footprint library renamed to `ChameleonMeshNode_Custom`; generator strings normalized to `kicad`; company set to `Chameleon Mesh Node Project`. No vendor/personal identifiers remain in the deliverable.
- [x] **DRC: 0 errors / 0 unconnected** on `chameleon_mesh_node_v1.2_FINAL.kicad_pcb` (kicad-cli json verified). USB-C J1 flush at top; U3 Wio-WM1110 RF routing untouched; full fab package exported to `hardware/kicad/fab_v1.2/`.
- [ ] **BOM with real part numbers.** Build-guide BOM lists passives as TBD; re-export from KiCad and commit `hardware/bom/` + schematic PDF to assets. (BOM CSV + schematic PDF now in `hardware/kicad/fab_v1.2/`.)
- [ ] Verify + copy the upstream Seeed Wio-WM1110 KiCad library LICENSE into the vendored footprint dir (per `NOTICE.md`).
- [ ] Add `SPDX-License-Identifier:` headers to `hardware/scripts/*.py` (MIT).

## 💡 Nice-to-have (lifts Completeness / Impact / Presentation)
- [ ] **Order a first-article prototype now**; update the Issue later with "boards in fab, ETA …" — converts the no-physical-board risk into visible momentum.
- [ ] Power-budget calculation table in `docs/power-design.md` (justifies the <50 µA deep-sleep target ahead of measurement).
- [ ] Confirm the exact upstream PlatformIO env name (`wio-tracker-wm1110` vs current upstream) and fill `PIN_COMPANION_WAKE` in `variant.h`.
- [ ] Short 3D fly-by GIF/video for the README.
