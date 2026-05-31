# Meshtastic Build-Off 2026 — Submission Readiness

Counsel-ratified (gpt5 + gem25, 2026-05-28). Contest = submit a **GitHub Issue**
with the template (name, email, **public repo link**, 200+ char description, tech
stack); repo must be **public** with a detailed README; **all work open-source**
(MIT/Apache/GPL/similar); deadline **Aug 2026**; judged on Innovation / Technical
Quality / Completeness / Impact / Presentation.

## ✅ Done (this pass)
- [x] Multi-license added — `LICENSE` map + `LICENSES/{CERN-OHL-S-2.0,GPL-3.0-or-later,MIT}.txt`.
- [x] `NOTICE.md` — third-party attribution (Seeed XIAO CC-BY-SA-4.0, Wio footprint, KiCad libs, Meshtastic GPL).
- [x] README rewritten — stale "awaiting routing/gerbers" status fixed → accurate fab-ready v1.0; added renders, "How it uses Meshtastic", design-state/DRC, roadmap, license sections.
- [x] Firmware proof-of-work — `firmware/variant.h` + `firmware/platformio.ini` (incremental variant on upstream Wio-WM1110 base; documents the 2 board deltas: BME280@0x76, C5-wake GPIO).
- [x] Gerbers extracted to browsable `hardware/gerbers/` (12 files, v1.0).
- [x] 3D renders generated headlessly → `assets/` (top + bottom).

## ⛔ Operator-only (cannot be done from here)
- [ ] **Create the PUBLIC GitHub repo** — extract `chameleon_mesh_node/` as a *standalone* repo. **Do NOT push the private monorepo.** Nothing outside this folder may ship.
- [ ] **Name + email + GitHub account** for the Issue submission template.
- [ ] **File the submission Issue** at `github.com/Seeed-Projects/meshtastic-build-off-2026` (Issue → submission template).
- [ ] Set the real copyright holder in `LICENSES/MIT.txt` (currently placeholder "Chameleon Mesh Node Project").

## ⚠️ Must-fix before publishing (gaps found, need a working session)
- [x] **Footprint libraries committed.** The `lib/` directory (custom Wio-WM1110 LGA-80 footprint + symbol, Seeed XIAO footprints/symbols, Seeed OPL license) is included under `hardware/kicad/lib/`; the project opens and regenerates standalone.
- [x] **OPSEC scrub complete.** Project-local custom library named `ChameleonMeshNode_Custom`; no internal program identifiers remain anywhere in the public tree.
- [ ] **BOM with real part numbers.** Build-guide BOM lists passives as TBD; `gerbers_v11.zip` is gerbers+drill only (no BOM/POS CSV, no schematic PDF). Re-export from KiCad and commit `hardware/bom/` + schematic PDF to assets.
- [ ] Verify + copy the upstream Seeed Wio-WM1110 KiCad library LICENSE into the vendored footprint dir (per `NOTICE.md`).
- [ ] Add `SPDX-License-Identifier:` headers to `hardware/scripts/*.py` (MIT).

## 💡 Nice-to-have (lifts Completeness / Impact / Presentation)
- [ ] **Order a first-article prototype now**; update the Issue later with "boards in fab, ETA …" — converts the no-physical-board risk into visible momentum.
- [ ] Power-budget calculation table in `docs/power-design.md` (justifies the <50 µA deep-sleep target ahead of measurement).
- [ ] Confirm the exact upstream PlatformIO env name (`wio-tracker-wm1110` vs current upstream) and fill `PIN_COMPANION_WAKE` in `variant.h`.
- [ ] Short 3D fly-by GIF/video for the README.
