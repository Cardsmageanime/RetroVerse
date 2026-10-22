# External SD boot — next engineering gate

## Confirmed build outputs
- ARM64 kernel and G12A DTBs: GitHub Actions run 39717680785
- ARM64 diagnostic initramfs: run 39745766212
- Combined diagnostic boot directory: run 39752968846
- Debian ARM64 rootfs tar: run 39753280095
- ext4 rootfs partition image (structurally checked): run 39758465329

## Important hardware distinction
A GPT/MBR layout and an ext4 root partition **do not guarantee boot** on an Amlogic Android TV box. The early-stage boot ROM may expect signed or vendor-specific U-Boot components at precise sectors; an existing vendor U-Boot may or may not support loading an external extlinux configuration.

The Vayava GameBox label is not enough to confirm the board revision, DRAM initialization, bootloader, device tree, or SD boot procedure. Legacy EmuELEC DTBs are reference material, not a drop-in match for mainline Linux.

## Next gates
1. Record evidence from the exact Vayava GameBox: SoC, RAM, board revision, firmware/U-Boot version, Wi-Fi chip and removable boot capability.
2. Select and verify a mainline G12A DTB **for this specific board**.
3. Confirm existing U-Boot can load a kernel + DTB + initramfs from external media, without modifying eMMC.
4. Check the rootfs's init/kernel module version and boot-time mounts; generate UUID-based root= settings.
5. Assemble SD-card image **only after** boot-chain assumptions are verified; never write an internal storage device.

## Safety
Do not flash existing GitHub artifact ZIPs or the ext4 partition image as a complete SD card. Until the boot chain is verified, build only read-only manifests and inspection tooling.


## 2026-10-22 GameBox evidence and inspector

- Android firmware-selected board profile: `g12a_u212_2g`; G12A platform, 2 GiB RAM, 4-bit SD controller with 100 MHz *configured maximum*.
- Android vendor kernel logs recorded SD CMD18 CRC communication errors. Windows exFAT filesystem check was clean, and a 256 MiB Windows write/read SHA-256 comparison matched. **Neither verifies GameBox-side card reliability.**
- Existing U-Boot 2015.01 vendor firmware external SD boot sequence remains unknown. Internal eMMC must stay unchanged.
- Check evidence: `python boot/tools/check_external_boot_readiness.py`.
- Examine **existing local boot files** without touching disks: `python boot/tools/inspect_boot_artifacts.py --kernel path/to/Image --dtb path/to/board.dtb --initramfs path/to/initramfs.cpio.gz`.
- The artifact checker accepts an uncompressed ARM64 Image, a structurally plausible FDT header, and a gzip/newc initramfs signature. It does **not** validate the entire DTB, kernel version, initramfs integrity, bootloader acceptance, or whether this DTB belongs to the GameBox. Header acceptance must never be interpreted as permission to flash.
- CI runs both sets of tests; a green workflow confirms only automated software checks, not a physical boot.

## Vendor U-Boot compatibility investigation (2026-10-22)

**Observed on user hardware:** `franklin` Android board, `g12a_u212_2g` DT selection, and vendor U-Boot `2015.01-g51e6fd64e9-dirty`. These facts do not expose the installed U-Boot environment.

**Relevant source-code leads (NOT verified on this exact device):**
- https://github.com/Amlogic-Lineage/u-boot/blob/khadas-vims-pie_lpddr/board/amlogic/configs/g12a_u212_v1.h describes `CONFIG_DEVICE_PRODUCT "franklin"`; recovery routines may look for `aml_autoscript` via `fatload mmc 0` and `fatload usb 0`, then invoke `autoscr`.
- https://android.googlesource.com/platform/external/u-boot/+/refs/heads/android-tv-9.0.0_r1/board/amlogic/configs/g12a_u212_v1.h is another related U-Boot tree with `aml_autoscript` recovery logic.
- https://github-wiki-see.page/m/EmuELEC/EmuELEC/wiki/How-to-Install documents a common Amlogic G12A external-media installation path, but explicitly warns against cross-distro DTBs.

**Critical caveats:**
1. The installed vendor environment and its actual recovery triggers are unobserved. `aml_autoscript` in source does NOT prove external boot support.
2. Scripts have U-Boot privileges and can flash/erase internal eMMC. Do NOT execute a generic internet `aml_autoscript` or a recovery update package without auditing every command.
3. `mmc 0` in U-Boot is a controller/device index, not Android's `/dev/mmcblk0`; never equate the two.
4. Recovery-to-external-media may require a firmware-specific key/button sequence. Do not trigger factory reset, wipe, erase, store, upgrade, or firmware flashing workflows.
5. Successful kernel artifact inspection, mounted Android SD, and matching hashes do not validate the board-specific DTB, SD signal integrity, or a physical Linux boot.

**Safest next experiment:** Obtain passive UART boot logs from the existing firmware **only if a documented, non-invasive connector exists**; otherwise find an exact factory firmware release/configuration matching this board/version and inspect its U-Boot environment offline. Collect only redacted command names, boot-source decisions, and SD probing results. Do not change any internal partition or U-Boot environment.

**Status:** external boot candidate only; `external_uboot_boot_path_verified = false`. No RetroVerse `aml_autoscript` or bootable SD image is published until the chain and rollback are understood.

## Offline U-Boot script preflight (2026-10-22)

New: `boot/tools/lint_uboot_script.py` performs a **text-only, nonexecuting** heuristic review of candidate U-Boot commands. Example: `python boot/tools/lint_uboot_script.py path/to/candidate.txt`. It flags firmware/environment writes, boot transfers, unknown commands, variable expansion, chaining, and other non-allowlisted text. The intentionally tiny observational allowlist includes `version`, `mmc list`, and simple `echo`.

**Do not feed it binary `aml_autoscript` images or treat passing as proof of safety.** It is not a parser for the full U-Boot language; unexpected features and platform-specific side effects remain possible. Inspect any candidate manually with exact board firmware documentation. The tool never approves execution, writes to media, changes environment variables, or marks `external_uboot_boot_path_verified` true.

The CI suite now includes its regression tests. Only user-device evidence or exact vendor boot-chain verification can resolve the physical external boot gate.
