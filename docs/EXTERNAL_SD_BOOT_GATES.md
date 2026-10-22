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
