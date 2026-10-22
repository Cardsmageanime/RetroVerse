# RetroVerse Systems Edition

**Status: Early development — not yet bootable or ready to flash.**

RetroVerse Systems Edition is a planned ARM64 Linux-based retro-gaming operating system for compatible Android TV boxes, HDMI gaming sticks, and other ARM-powered retro-gaming devices. The project aims to provide a lightweight, customizable frontend with RetroArch integration and bootable SD-card or USB distributions where supported.

## Current engineering priority

**Build and validate the ARM64 Linux boot foundation first.** Gameplay and network features are deferred until we have a verifiable booting system.

Initial reference hardware: **Vayava GameBox**, provisionally identified as **Amlogic G12A / S905X2, 2 GB RAM**. Board revision, boot method, driver compatibility, and SD-card boot behavior require verification.

The planned work is:
1. Obtain a complete Linux kernel source tree and ARM64 cross-compilation toolchain.
2. Compile the ARM64 kernel `Image` and kernel-matched device tree blobs (DTBs).
3. Build and package kernel modules and a minimal ARM64 root filesystem.
4. Determine the correct board-specific external boot chain and SD-card layout.
5. Assemble an SD-card image and perform non-destructive, controlled hardware boot testing.

**Important:** The kernel binary, bootloader configuration, and flashable RetroVerse operating-system image are **not complete**. Existing external DTB files are references and must not be assumed compatible with a newly compiled kernel.

## Hardware compatibility plan

The **Versus Tree** is a hardware-profile catalog intended to separate board-specific kernel, device tree, bootloader, and driver requirements from the shared operating-system userspace.

- First development family: Amlogic G12A / S905X2
- Additional reference families: Amlogic SM1 / S905X3 and G12B / S922X / A311D
- Longer-term candidates: compatible Rockchip and Allwinner ARM boards

Hardware support will be confirmed **per board**, not merely by CPU family or matching RAM size.

## Planned functionality (not yet implemented as a working OS)

- Offline retro gaming through RetroArch and compatible emulator cores
- Custom fullscreen frontend and game library management
- Wi-Fi and optional accounts for future RetroVerse Online features
- Online rooms, multiplayer, and spectating where compatible
- Preservation of saves, ROMs, configuration, and user data through future updates
- SD-card boot first; USB boot on verified supported hardware later

## Development safety

- Do not flash any work-in-progress package to your device.
- Do not overwrite the internal Android/eMMC installation.
- Do not substitute a legacy EmuELEC DTB for a kernel-built DTB without validation.
- No public release is planned until boot behavior and update safety are tested.

## Repository status

This repository is the development home for **RetroVerse Systems Edition**. It is distinct from **RetroRelay**, a separate PC application.

Kernel and OS source packages will be added as development progresses. A successful automated build does not, on its own, demonstrate hardware boot compatibility.

## License

Licensing for original RetroVerse material is pending. Upstream Linux, RetroArch, bootloaders, emulator cores, and other third-party components retain their respective licenses. Do not assume all components can be redistributed under a single license.
