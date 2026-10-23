# Franklin vendor U-Boot external-boot evidence packet

**Milestone:** B — establish an evidence-based external boot path before building a RetroVerse image.
**Status (2026-10-23): REFERENCE BOOT CONFIRMED / RETROVERSE BOOT PENDING.**
**Scope:** Vayava GameBox, Android board `franklin`, firmware DT selector `g12a_u212_2g`, observed U-Boot `2015.01-g51e6fd64e9-dirty`.

The owner physically booted the existing EmuELEC installation from external removable media using the recovery/reset trigger. This establishes that the installed firmware can start a compatible external ARM system. Exact U-Boot commands and a RetroVerse-built boot remain unverified.

## Evidence ledger

| Fact or gate | Current observation | Status |
| --- | --- | --- |
| Android board name | `franklin` | Observed in prior device evidence |
| Android DT selector | `g12a_u212_2g` | Observed; not a mainline DTB compatibility proof |
| SoC/RAM compatibility | EmuELEC booted with `g12a_s905x2_2g.dtb` active | Physically supported for this reference image |
| Vendor U-Boot | `2015.01-g51e6fd64e9-dirty` | Version observed; build configuration and environment unknown |
| External boot route | Recovery/reset trigger followed by successful EmuELEC boot | Physically verified at a high level |
| U-Boot commands/MMC mapping | Not captured | Unknown |
| Reference DTB | `dtb.img` SHA-256 equals `g12a_s905x2_2g.dtb`: `66f024a72e9e9c6efcf2e1e61ea6338afb29be12ff2b0da41d1b792b38d17966` | Host-side verified |
| Reference kernel | `kernel.img` MD5 `505156cb65832bcfbeeb2db3a56c5120` | Matches supplied checksum |
| Reference system | `SYSTEM` MD5 `23c4fd1c5bb43cb4099107e24ed60fd0` | Matches supplied checksum |
| HDMI video | EmuELEC splash and EmulationStation rendered | Physically verified |
| Userspace | Collections loaded; frontend reached | Physically verified |
| RetroArch launch path | EmuELEC 4.3 launched RetroArch 1.9.8 (Git `37aa13bb47`, built 2021-10-04), found the `udev` input driver, and loaded `cannonball_libretro.so` | Core loaded and Cannonball display-calibration UI rendered; gameplay and audio not yet observed |
| Game application | Abuse reached its title screen and responded during active play | Gameplay and controller input verified by owner observation |
| Controller | Game control responded during the test | Functional input verified by owner observation |
| HDMI audio | Sound heard through the TV during the game test | Verified by owner observation |
| Network | Not tested | Unknown |
| Repeat boot | Not tested | Unknown |
| Android fallback with media removed | Not tested | Unknown |
| SD read quality | Earlier Android logs showed CMD18 CRC errors; one full boot later succeeded | Reliability still unverified |
| RetroVerse kernel/DTB/rootfs | Not physically booted | Pending |

## Interpretation

The test closes the earlier high-level question of whether this hardware and installed firmware can boot a compatible external Linux gaming system. It does not expose the precise U-Boot command sequence, memory layout, or controller numbering. It also does not establish compatibility between the legacy EmuELEC DTB and a new RetroVerse kernel.

No room photographs are committed to this public repository. The record retains only technical observations and hashes needed for review.

## Remaining non-destructive checks

1. Reboot with the external media still inserted and determine whether Reset is required again.
2. Shut down, remove the media, and verify that Android starts normally.
3. In the running reference system, capture sanitized kernel, DTB model, memory, storage, and network-interface information.
4. Verify clean game exit and system shutdown.
5. Investigate the earlier CMD18 CRC errors before treating long-duration media access as reliable.
6. Keep all identifiers such as MAC addresses, serial numbers, account tokens, and Wi-Fi credentials out of committed logs.

## Required reviewer questions

- Which parts of the successful reference boot are reusable for RetroVerse, and which are tied to EmuELEC's kernel and boot files?
- What exact external-media path does the installed U-Boot execute?
- Which U-Boot MMC controller corresponds to the external media?
- Does the installed bootloader support the load commands and image formats selected for the RetroVerse candidate?
- Does the candidate kernel/DTB/initramfs layout avoid overlap and match the observed DRAM?
- Does Android boot normally after the external media is removed?
- Are the earlier device-side SD CRC failures resolved or acceptably bounded?

## Stop conditions

Do not copy the legacy EmuELEC DTB into a differently built RetroVerse kernel without validation. Do not write eMMC, alter the U-Boot environment, run internal-install options, or claim a RetroVerse boot until the exact RetroVerse candidate reaches userspace on the physical box.

## Artifact checklist for review

- [x] Active reference DTB identified and hashed
- [x] Reference kernel and system checksum match recorded
- [x] External reference OS reached HDMI userspace
- [ ] Exact U-Boot command path and MMC mapping captured
- [ ] Repeat external boot documented
- [ ] Known-good Android fallback documented
- [x] RetroArch/libretro core loaded and Cannonball calibration UI rendered
- [x] Abuse game application reached its title screen
- [x] Live gameplay, controller input, and HDMI audio tested
- [ ] Clean game exit and shutdown tested
- [ ] SD CRC/reliability diagnosis recorded
- [ ] RetroVerse candidate contents independently reviewed
- [ ] Physical RetroVerse boot completed
- [ ] Independent review completed

**Acceptance for this checkpoint:** the repository may set `external_uboot_boot_path_verified=true` only with scope limited to the observed EmuELEC reference boot. `board_dtb_matches_compiled_kernel=false`, `gamebox_sd_link_reliability_verified=false`, `android_internal_storage_untouched=false`, and `can_flash=false` remain until their separate gates are satisfied.
