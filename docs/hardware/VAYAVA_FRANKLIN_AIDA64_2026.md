# Vayava GameBox — observed AIDA64 hardware data

Status: **user-provided screen observations, not independent board identification or boot verification.**

## AIDA64 observations (October 2026)
- Manufacturer/hardware family shown: Amlogic
- Model shown: `TVBOX-GAME`
- Android brand, board, device or product fields: `franklin` (labels visible in photographs)
- Installed RAM: **2 GB**; reported memory total **2007 MB**; available at capture **1252 MB**
- Internal storage total shown: **3445 MB**, free **1083 MB** (reported Android-accessible storage, not necessarily full physical eMMC)
- CPU: **4 × ARM Cortex-A53**, up to **1800 MHz**
- CPU ISA: **ARMv8-A 64-bit capable**, while current Android is reported running in **32-bit mode**
- Supported Android ABIs shown: `armeabi-v7a`, `armeabi`
- Bluetooth version reported: 4+
- Android lists Ethernet, Bluetooth, low-latency audio, HDMI among reported device features; capabilities need actual driver/hardware testing

## Engineering implications
- An **AArch64 Linux kernel remains possible**, because the CPU is 64-bit capable; the 32-bit Android installation is not proof that the bootloader supports starting a 64-bit Linux kernel.
- The processor's exact **SoC revision is NOT confirmed** by these screenshots. The earlier S905X2 / G12A candidate remains provisional; do not select a DTB based solely on A53 cores or product name `franklin`.
- Treat the supplied legacy `g12a_s905x2_2g.dtb` as a hardware-reference candidate, not a kernel-matched or verified boot DTB.
- The photos do not establish SD boot support, U-Boot variant, PCB revision, Mali GPU model, Wi-Fi chipset, or removable-media boot method.

## Next evidence to collect
- AIDA64 **System** / **Android** build identifiers and **CPU** SoC identification, if shown.
- `/proc/device-tree/model` and `/proc/device-tree/compatible` via optional read-only ADB board probe.
- Exact external bootloader behavior from a known working removable boot setup.

No Android modification, eMMC write, or flashing is authorized by this profile.
