# RetroVerse Systems Edition — Development Roadmap
**Baseline:** October 25, 2026 | **Scope:** removable-media ARM retro-gaming operating system, not the separate RetroRelay PC app.

## Vision and non-negotiable rules
- Boot RetroVerse from **external SD or USB** on supported ARM-based game consoles, game sticks, and Android TV boxes; never install or flash internal Android/eMMC.
- **Any brand** of technically compatible SD/microSD card is eligible; support cards up to **1,000,000,000,000 bytes (1 TB)**, subject to individual device/firmware compatibility, reliability and sufficient space.
- Games, ROMs, saves, settings and themes persist through safe updates. Offline use never requires Wi-Fi or a RetroVerse account.
- No public release until successfully tested on physical devices with recovery procedures.
- Do not begin multiplayer/netplay until a successful local hardware boot and offline baseline.

## Evidence-based progress
| Milestone | Work | Current state | Exit condition |
|---|---|---|---|
| 1–8 | G12A platform research; ARM64 kernel and experimental Franklin DTB structural gate | Offline development performed; Franklin DTB **research-only** | Board matched DTB requires real evidence |
| 9 | Static ARM64 BusyBox early userspace / initramfs | Built and validated on Linux Mint | Real boot still pending |
| 10 | Offline review bundle with kernel and initramfs SHA256 checks | User-confirmed checksums OK | Complete for offline purpose only |
| 11–12 | Inspect EmuELEC boot scripts, G12A identity, SD GPIO and power references | Reference inspection done; U-Boot `saveenv` hazard documented, board wiring unknown | GPIO/CD polarity, regulators, DRAM and boot chain verified |
| 13 | Brand-neutral SD-card policy and eligibility-check logic | 6/6 unit tests passed on Mint; not a physical installer | Validate live inventory and reliability before any write |
| 14 | Read-only lsblk JSON storage inventory | 6/6 unit tests passed on Mint; saved real report **not yet reviewed** | Validate against user report, improve system disk and nested mount protection |
| 15 | Storage reliability/read-only diagnostics | Planned | Evidence-based card/reader assessment; no destructive probing of reference card |
| 16 | Board DTB reconciliation and G12A GPIO mapping | Planned; research-only DTB remains disabled | Board-specific supplies/pins/capabilities verified |
| 17 | Nonpersistent U-Boot boot-chain verification | Planned | External MMC/USB indices, `booti`/`bootm`, address map and recovery path demonstrated without writes to eMMC |
| 18 | Minimal external SD/USB test image | **Blocked** until 15–17 pass | Explicit removable target + safe image/layout, readback, rollback |
| 19 | First supervised physical boot on Vayava GameBox | Not yet attempted | Serial/visual logs prove ARM64 kernel + initramfs boots; Android recovery confirmed |
| 20 | Offline RetroVerse OS foundation | Planned | Reliable storage, controllers, boot UI, RetroArch startup and saves |
| 21 | Additional ARM hardware profiles | Planned | Per-board DTB/bootloader validation; shared RetroVerse userspace |
| 22 | Robust offline experience | Planned | Game library, metadata, local saves, cheats for solo only, controller mapping, settings and themes |
| 23 | Safe update mechanism | Planned | Atomic/non-destructive update with rollback preserving ROMs/saves/configuration |
| 24 | RetroVerse Online | Later (after boot) | Account/security, friends, public/private lobbies and compatible cross-platform netplay; cheats blocked in **all** multiplayer |
| 25 | Community and polish | Later | Spectator/creator lobbies, chat and platform badges; continuous/shuffle music; optional backgrounds and theme palettes |
| 26 | Release qualification | Later | Multi-board boot matrix, SD/USB brands/capacities, regression tests and signed release artifacts |

## Near-term sprint: focus on milestone 14 then one gate at a time
1. **Validate real storage inventory**: inspect `~/Downloads/RetroVerse-Storage-Report.json`, confirm the internal SATA SSD remains excluded and the mounted EmuELEC reference card is never an installer target.
2. Harden read-only inventory: nested partitions/mountpoints, ambiguous/unknown fields, symlink safety, transport uncertainty, units and device renumbering, all fail-closed.
3. Extend offline capacity preflight with a full 1 TB exact-boundary test matrix, brand neutrality, write-protect and CRC warnings.
4. Finalize Franklin GPIO evidence collection; map vendor `gpio_cd` only with independent validation (no speculative pin substitution).
5. Gather U-Boot console evidence and SD signal reliability data when user can access hardware.

## Progress/status meanings
- **Tested offline:** automated checks pass on development host; not proof of board boot.
- **Hardware verified:** confirmed on target device with captured evidence.
- **Blocked:** must not create/use a deployable image until prerequisites are satisfied.
- **Planned:** roadmap feature, not implemented or guaranteed.

## Safety gates
- Do not run the copied EmuELEC `aml_autoscript`: it contains `defenv`, `saveenv`, and bootcmd changes.
- Never treat `mmcblk1` as proof of U-Boot `mmc 0` numbering.
- No default enabling of `&sd_emmc_b`, board regulators or eMMC nodes in experimental DTB.
- Existing EmuELEC reference SD card and Linux system SSD must remain untouched.
- Never promise compatibility with **every** physical card/board merely based on brand or capacity.

## Long-term feature outline
**First usable offline system:** RetroArch cores/launching, artwork and library browser, configurable controllers, local saves, offline first-use, accessibility and game-compatible performance.

**Networking after reliable offline boots:** optional RetroVerse Online accounts, MFA, friends, online/friends/spectator/creator lobbies; public/private rooms; platform badges (RetroVerse, EmuELEC, Windows, Linux, etc.); netplay where emulator core/version/network compatibility actually permits; strict no-cheats policy in every multiplayer mode.

**Customization and updates:** original game/anime-inspired palette themes, optional generated artwork, background music/shuffle/continuous playback; safe firmware-style updates and rollback without overwriting ROMs, save data or user settings.

## Working agreement
GitHub development and offline tests can proceed without connected GameBox. Physical verification needs user-provided logs and deliberate supervised tests. No autonomous background work is implied.
